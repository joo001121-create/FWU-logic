# Initialization 줄별 해석

> **대상 코드** : `fwu_v3/Logic/Initialization.py` (674 줄)  
> **기준** : `sy 브랜치 2026-11-23 (naming rule·관제점 이름 변경 반영)`  
> **행** = 코드 줄 번호 (빈 줄은 생략)  
> **표기** : `→` 들여쓰기 단계 · *[주석]* 코드 안 주석 · `이름` 코드 안 상수·변수 · **※** 읽을 때 주의할 점

상위(BMS/PLC) 통신을 감시하고, 외부 센서(냉복도·열복도 온도, 룸 차압, 냉복도 습도) 값을 모아 평균·최대·최소와 제어용 값을 만든다. 팬 운전 상태 판단, 급기 풍량 계산, 운전 명령 동기화, 팬 최대 RPM 계산도 여기서 한다.

**목차**

- [1~56행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수](#section-1)
- [58~81행 · 상위 통신(heartbeat) 감시](#section-2)
- [83~84행 · 다음 실행에서 '감시를 막 켰는지' 알 수 있도록 지금 상태를 남긴다](#section-3)
- [86~98행 · 통신 이상 Reset: heartbeat가 살아 있을 때만 알람을 풀고, Reset 입력은 5초 뒤 스스로 되돌린다](#section-4)
- [100~101행 · 상위 통신이 정상일 때만 외부 센서(CZT/HZT/RDP)값을 쓴다](#section-5)
- [103~194행 · CZT(냉복도 온도) 집계](#section-6)
- [196~206행 · 쓸 수 있는 센서가 하나라도 있으면 평균·최대·최소를 내보내고, 없으면 0과 '무효'로 표시](#section-7)
- [208~215행 · 제어에 쓸 CZT 값 (Select 0 = 평균, 1 = 최대)](#section-8)
- [217~307행 · HZT(열복도 온도) 집계](#section-9)
- [309~319행 · 쓸 수 있는 센서가 하나라도 있으면 평균·최대·최소를 내보내고, 없으면 0과 '무효'로 표시](#section-10)
- [321~328행 · 제어에 쓸 HZT 값 (Select 0 = 평균, 1 = 최대)](#section-11)
- [330~420행 · RDP(룸 차압) 집계](#section-12)
- [422~432행 · 쓸 수 있는 센서가 하나라도 있으면 평균·최대·최소를 내보내고, 없으면 0과 '무효'로 표시](#section-13)
- [434~441행 · 제어에 쓸 RDP 값 (Select 0 = 평균, 1 = 최소)](#section-14)
- [443~546행 · CZH(냉복도 습도) 집계: 표시용이라 상위 통신·고장 조건 없이 사용 개수만 본다](#section-15)
- [548~549행 · ΔT = RAT - SAT (SF Control의 ΔT 모드에서 쓴다)](#section-16)
- [551~639행 · 팬 운전 판단: 한 대라도 돌고 있으면 운전 중으로 본다](#section-17)
- [641~649행 · 판단이 바뀐 채로 5초가 지나야 VP_FWU_SF_Status에 반영한다 (순간적인 흔들림 무시)](#section-18)
- [651~658행 · 급기 풍량 계산: 팬이 돌고 차압이 5Pa 이상일 때만 계산한다](#section-19)
- [660~668행 · 운전 명령 맞추기: 원격(BMS) 선택이면 BMS 명령을 HMI 쪽에, 로컬이면 HMI 명령을 BMS 쪽에 따라 쓴다](#section-20)
- [670~674행 · 팬 최대 RPM = 설계 RPM × 비율(%). 단 정격 최대 RPM은 넘지 않게 한다 (SF Control이 이 값을 쓴다)](#section-21)

**※ 공통 표기**: 매크로 상수 TRUE·ON·SET·TMR_READ·DEC = 1, FALSE·OFF·CLEAR·TMR_CLEAR·INC = 0. `SECTIMER(타이머, TMR_CLEAR)`는 타이머를 0초로 초기화, `SECTIMER(타이머, TMR_READ)`는 경과시간 확인이다. P번호가 없는 쓰기(`WRITEPOINT`)는 기본 우선순위 P5를 쓴다. 조건이 거짓이라고 관제점이 저절로 0이 되지는 않는다. 해당 분기에 쓰기가 없으면 이전 값이 남는다. 대문자 이름은 상수, `m`으로 시작하는 이름은 이 파일의 전역변수, `b`가 붙은 이름은 참/거짓 값이다.

<a id="section-1"></a>

## 1~56행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수

| 행 | 해석 |
|---:|---|
| 1 | *[주석] LJH 2026-11-17 수정 구간 시작. 주제 = 상위 감시와 외부 센서 집계* |
| 2 | *[주석] JSY 2026-11-23 수정 구간 시작. 주제 = Coding Rule 적용(매크로 상수, 설정값 상수, 변수명, if-else 짝 맞춤, 주석)* |
| 4 | *[주석] 로직엔진 loading* |
| 5 | DDC 로직 엔진 객체 생성 (이후 engine.xxx로 관제점을 읽고 씀) |
| 7 | *[주석] Macro상수 정의* |
| 8 | 매크로 상수 정의: TMR_READ, SET, ON, TRUE, DEC = 1 (긍정의 의미 또는 1인 인자) |
| 9 | 매크로 상수 정의: TMR_CLEAR, CLEAR, OFF, FALSE, INC = 0 (부정의 의미 또는 0인 인자) |
| 10 | 설정값 상수 `FAIL_RPM`: 팬 운전 판단 RPM 설정 (`VP_FWU_SF_Failure_RPM_Set`) 값을 읽어 둠<br>*[주석] 팬 RPM이 이 값 이상이면 도는 것으로 봄* |
| 11 | 설정값 상수 `RUN_DP`: 팬 운전 판단 차압 설정 (`VP_FWU_SF_Run_DP_Set`) 값을 읽어 둠<br>*[주석] 팬 통신이 끊겼을 때 급기 차압이 이 값보다 높으면 도는 것으로 봄* |
| 13 | *[주석] 타이머 정의* |
| 14 | 타이머 번호 상수 `SF_STATUS_TIMER` = 5번<br>*[주석] 팬 운전 판단이 VP_FWU_SF_Status와 다르게 이어진 시간* |
| 15 | 타이머 번호 상수 `UPPER_HEARTBEAT_TIMER` = 6번<br>*[주석] 상위 heartbeat 값이 마지막으로 바뀐 뒤 지난 시간* |
| 16 | 타이머 번호 상수 `UPPER_RESET_TIMER` = 7번<br>*[주석] 상위 통신 Reset 입력이 켜져 있던 시간* |
| 18 | *[주석] 전역변수 선언* |
| 19 | 전역변수 `mbUpperEnabled` ← 상위 통신 감시 사용 설정 (`VP_FWU_Upper_Comm_Enable`) = TRUE(1) 이면 TRUE, 아니면 FALSE<br>*[주석] 상위(BMS/PLC) 통신 감시를 쓰는지 (HMI 설정)* |
| 20 | `mHeartbeat` ← 상위 heartbeat 값 (`VP_FWU_BMS_PLC_Heartbeat`) 값 읽기<br>*[주석] 상위가 주기적으로 바꿔 주는 값* |
| 21 | 전역변수 `mbHBOk` 선언, 처음 값 = FALSE(0)<br>*[주석] 이번 실행에서 heartbeat가 살아 있다고 확인되면 TRUE* |
| 22 | 전역변수 `mbUpperOk` 선언, 처음 값 = FALSE(0)<br>*[주석] 상위 통신이 정상이라 외부 센서값을 써도 되면 TRUE (heartbeat 확인 뒤에 계산)* |
| 24 | *[주석] 외부 센서 집계값. 최대·최소는 어떤 센서값보다도 작게/크게 잡고 시작한다* |
| 25 | 전역변수 `mCZTCount` 선언, 처음 값 = 0 |
| 26 | 전역변수 `mCZTSum` 선언, 처음 값 = 0 |
| 27 | 전역변수 `mCZTMax` 선언, 처음 값 = -1000 |
| 28 | 전역변수 `mCZTMin` 선언, 처음 값 = 1000 |
| 29 | 전역변수 `mHZTCount` 선언, 처음 값 = 0 |
| 30 | 전역변수 `mHZTSum` 선언, 처음 값 = 0 |
| 31 | 전역변수 `mHZTMax` 선언, 처음 값 = -1000 |
| 32 | 전역변수 `mHZTMin` 선언, 처음 값 = 1000 |
| 33 | 전역변수 `mRDPCount` 선언, 처음 값 = 0 |
| 34 | 전역변수 `mRDPSum` 선언, 처음 값 = 0 |
| 35 | 전역변수 `mRDPMax` 선언, 처음 값 = -1000 |
| 36 | 전역변수 `mRDPMin` 선언, 처음 값 = 1000 |
| 37 | 전역변수 `mCZHCount` 선언, 처음 값 = 0 |
| 38 | 전역변수 `mCZHSum` 선언, 처음 값 = 0 |
| 39 | 전역변수 `mCZHMax` 선언, 처음 값 = -1000 |
| 40 | 전역변수 `mCZHMin` 선언, 처음 값 = 1000 |
| 42 | *[주석] 팬 8대의 통신 이상 상태 (Comm Fault Alarm이 판단해 둔 값)* |
| 43 | `mbSF1CommFault` ← 팬 1번 통신 이상 (`VP_FWU_SF-1_Comm_Fault`) 값 읽기 |
| 44 | `mbSF2CommFault` ← 팬 2번 통신 이상 (`VP_FWU_SF-2_Comm_Fault`) 값 읽기 |
| 45 | `mbSF3CommFault` ← 팬 3번 통신 이상 (`VP_FWU_SF-3_Comm_Fault`) 값 읽기 |
| 46 | `mbSF4CommFault` ← 팬 4번 통신 이상 (`VP_FWU_SF-4_Comm_Fault`) 값 읽기 |
| 47 | `mbSF5CommFault` ← 팬 5번 통신 이상 (`VP_FWU_SF-5_Comm_Fault`) 값 읽기 |
| 48 | `mbSF6CommFault` ← 팬 6번 통신 이상 (`VP_FWU_SF-6_Comm_Fault`) 값 읽기 |
| 49 | `mbSF7CommFault` ← 팬 7번 통신 이상 (`VP_FWU_SF-7_Comm_Fault`) 값 읽기 |
| 50 | `mbSF8CommFault` ← 팬 8번 통신 이상 (`VP_FWU_SF-8_Comm_Fault`) 값 읽기 |
| 52 | `mSAFlowDP` ← 급기 풍량 차압(FMS) (`FWU_SAFLOW_DP`) 값 읽기<br>*[주석] 급기 차압(Pa)* |
| 53 | 전역변수 `mbSFRun` 선언, 처음 값 = FALSE(0)<br>*[주석] 팬이 한 대라도 돌고 있다고 판단되면 TRUE* |
| 55 | *[주석] 상위가 없는 모델은 감시를 끄고 고정속도/RAT/ΔT를 사용한다.* |
| 56 | *[주석] 감시를 끄면 외부 온도·차압은 제어 입력으로 쓰지 않는다.* |

<a id="section-2"></a>

## 58~81행 · 상위 통신(heartbeat) 감시

> 상위가 heartbeat 값을 계속 바꿔 주는지 본다. Upper_Comm_Timeout 동안 그대로면 통신 이상으로 잡아 둔다

| 행 | 해석 |
|---:|---|
| 58 | *[주석] 상위 통신(heartbeat) 감시* |
| 59 | *[주석] 상위가 heartbeat 값을 계속 바꿔 주는지 본다. Upper_Comm_Timeout 동안 그대로면 통신 이상으로 잡아 둔다* |
| 60 | `mbUpperEnabled` = TRUE(1) 이면 : |
| 61 | &emsp;→&nbsp;*[주석] 감시를 막 켰으면(이전 실행에서는 꺼져 있었으면) 지금 값을 기준으로 새로 잰다* |
| 62 | &emsp;→&nbsp;직전 감시 사용 상태(기억용) (`VP_FWU_Upper_Comm_Enable_Prev`) = TRUE(1) 이면 : |
| 63 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) — 이전 실행에서도 켜져 있었음. 하던 대로 잰다 |
| 64 | &emsp;→&nbsp;62행 조건이 성립하지 않으면 : |
| 65 | &emsp;&emsp;→&nbsp;타이머 `UPPER_HEARTBEAT_TIMER`(6번: 상위 heartbeat 값이 마지막으로 바뀐 뒤 지난 시간)를 0초로 초기화 |
| 66 | &emsp;&emsp;→&nbsp;직전 heartbeat 값(기억용) (`VP_FWU_BMS_PLC_Heartbeat_Prev`)에 `mHeartbeat` 기록 — 기본 우선순위(P5) |
| 67 | &emsp;→&nbsp;`mHeartbeat` = 직전 heartbeat 값(기억용) (`VP_FWU_BMS_PLC_Heartbeat_Prev`) 이면 :<br>*[주석] 값이 그대로면 Timeout을 넘었는지 본다* |
| 68 | &emsp;&emsp;→&nbsp;타이머 `UPPER_HEARTBEAT_TIMER`(6번: 상위 heartbeat 값이 마지막으로 바뀐 뒤 지난 시간) 경과시간 > 상위 통신 끊김 판정 시간 설정(초) (`VP_FWU_Upper_Comm_Timeout`) 이면 : |
| 69 | &emsp;&emsp;&emsp;→&nbsp;상위(BMS/PLC) 통신 이상 (`VP_FWU_BMS_PLC_Comm_Fault`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 70 | &emsp;&emsp;→&nbsp;68행 조건이 성립하지 않으면 : |
| 71 | &emsp;&emsp;&emsp;→&nbsp;`mbHBOk` ← TRUE(1) |
| 72 | &emsp;→&nbsp;67행 조건이 성립하지 않으면 : |
| 73 | &emsp;&emsp;→&nbsp;*[주석] 값이 바뀌었으면 살아 있는 것. 기준값을 새로 남기고 시간을 다시 잰다* |
| 74 | &emsp;&emsp;→&nbsp;직전 heartbeat 값(기억용) (`VP_FWU_BMS_PLC_Heartbeat_Prev`)에 `mHeartbeat` 기록 — 기본 우선순위(P5) |
| 75 | &emsp;&emsp;→&nbsp;타이머 `UPPER_HEARTBEAT_TIMER`(6번: 상위 heartbeat 값이 마지막으로 바뀐 뒤 지난 시간)를 0초로 초기화 |
| 76 | &emsp;&emsp;→&nbsp;`mbHBOk` ← TRUE(1) |
| 77 | 60행 조건이 성립하지 않으면 : |
| 78 | &emsp;→&nbsp;*[주석] 감시를 안 쓰면 타이머와 통신 이상을 풀어 둔다* |
| 79 | &emsp;→&nbsp;타이머 `UPPER_HEARTBEAT_TIMER`(6번: 상위 heartbeat 값이 마지막으로 바뀐 뒤 지난 시간)를 0초로 초기화 |
| 80 | &emsp;→&nbsp;직전 heartbeat 값(기억용) (`VP_FWU_BMS_PLC_Heartbeat_Prev`)에 `mHeartbeat` 기록 — 기본 우선순위(P5) |
| 81 | &emsp;→&nbsp;상위(BMS/PLC) 통신 이상 (`VP_FWU_BMS_PLC_Comm_Fault`)에 FALSE(0) 기록 — 기본 우선순위(P5) |

<a id="section-3"></a>

## 83~84행 · 다음 실행에서 '감시를 막 켰는지' 알 수 있도록 지금 상태를 남긴다

| 행 | 해석 |
|---:|---|
| 83 | *[주석] 다음 실행에서 '감시를 막 켰는지' 알 수 있도록 지금 상태를 남긴다* |
| 84 | 직전 감시 사용 상태(기억용) (`VP_FWU_Upper_Comm_Enable_Prev`)에 `mbUpperEnabled` 기록 — 기본 우선순위(P5) |

<a id="section-4"></a>

## 86~98행 · 통신 이상 Reset: heartbeat가 살아 있을 때만 알람을 풀고, Reset 입력은 5초 뒤 스스로 되돌린다

| 행 | 해석 |
|---:|---|
| 86 | *[주석] 통신 이상 Reset: heartbeat가 살아 있을 때만 알람을 풀고, Reset 입력은 5초 뒤 스스로 되돌린다* |
| 87 | 상위 통신 이상 Reset 입력 (`VP_FWU_BMS_PLC_Comm_Reset`) = TRUE(1) 이면 : |
| 88 | &emsp;→&nbsp;`mbHBOk` = TRUE(1) 이면 : |
| 89 | &emsp;&emsp;→&nbsp;상위(BMS/PLC) 통신 이상 (`VP_FWU_BMS_PLC_Comm_Fault`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 90 | &emsp;→&nbsp;88행 조건이 성립하지 않으면 : |
| 91 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 92 | &emsp;→&nbsp;타이머 `UPPER_RESET_TIMER`(7번: 상위 통신 Reset 입력이 켜져 있던 시간) 경과시간 > 5 이면 :<br>*[주석] 5초* |
| 93 | &emsp;&emsp;→&nbsp;상위 통신 이상 Reset 입력 (`VP_FWU_BMS_PLC_Comm_Reset`)에 FALSE(0) 기록 — 우선순위 P11 |
| 94 | &emsp;&emsp;→&nbsp;타이머 `UPPER_RESET_TIMER`(7번: 상위 통신 Reset 입력이 켜져 있던 시간)를 0초로 초기화 |
| 95 | &emsp;→&nbsp;92행 조건이 성립하지 않으면 : |
| 96 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 97 | 87행 조건이 성립하지 않으면 : |
| 98 | &emsp;→&nbsp;타이머 `UPPER_RESET_TIMER`(7번: 상위 통신 Reset 입력이 켜져 있던 시간)를 0초로 초기화 |

<a id="section-5"></a>

## 100~101행 · 상위 통신이 정상일 때만 외부 센서(CZT/HZT/RDP)값을 쓴다

| 행 | 해석 |
|---:|---|
| 100 | *[주석] 상위 통신이 정상일 때만 외부 센서(CZT/HZT/RDP)값을 쓴다* |
| 101 | `mbUpperOk` ← `mbUpperEnabled` = TRUE **그리고** 상위(BMS/PLC) 통신 이상 (`VP_FWU_BMS_PLC_Comm_Fault`) = FALSE(0) 이면 TRUE, 아니면 FALSE |

<a id="section-6"></a>

## 103~194행 · CZT(냉복도 온도) 집계

> 사용 개수(CZT_Count) 안의 센서 중, 상위 통신이 정상이고 고장 알람이 없는 것만 평균·최대·최소에 넣는다 사용 개수는 0~10 정수. 상위에서 대표값 하나만 받으면 사용 개수를 1로 설정한다

| 행 | 해석 |
|---:|---|
| 103 | *[주석] CZT(냉복도 온도) 집계* |
| 104 | *[주석] 사용 개수(CZT_Count) 안의 센서 중, 상위 통신이 정상이고 고장 알람이 없는 것만 평균·최대·최소에 넣는다* |
| 105 | *[주석] 사용 개수는 0~10 정수. 상위에서 대표값 하나만 받으면 사용 개수를 1로 설정한다* |
| 106 | 냉복도 온도 사용 센서 수 설정 (`VP_FWU_CZT_Count`) ≥ 1 **그리고** `mbUpperOk` = TRUE(1) **그리고** 냉복도 온도 1번 센서 고장 알람 (`VP_FWU_CZT-1_Failure_Alarm`) = FALSE(0) 이면 : |
| 107 | &emsp;→&nbsp;`SensorValue` ← 냉복도 온도 1번 값 (`VP_FWU_CZT-1`) 값 읽기 |
| 108 | &emsp;→&nbsp;`mCZTCount`에 1을(를) 더함 |
| 109 | &emsp;→&nbsp;`mCZTSum`에 `SensorValue`을(를) 더함 |
| 110 | &emsp;→&nbsp;`mCZTMax` ← [`mCZTMax`, `SensorValue`] 중 최댓값 |
| 111 | &emsp;→&nbsp;`mCZTMin` ← [`mCZTMin`, `SensorValue`] 중 최솟값 |
| 112 | 106행 조건이 성립하지 않으면 : |
| 113 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 115 | 냉복도 온도 사용 센서 수 설정 (`VP_FWU_CZT_Count`) ≥ 2 **그리고** `mbUpperOk` = TRUE(1) **그리고** 냉복도 온도 2번 센서 고장 알람 (`VP_FWU_CZT-2_Failure_Alarm`) = FALSE(0) 이면 : |
| 116 | &emsp;→&nbsp;`SensorValue` ← 냉복도 온도 2번 값 (`VP_FWU_CZT-2`) 값 읽기 |
| 117 | &emsp;→&nbsp;`mCZTCount`에 1을(를) 더함 |
| 118 | &emsp;→&nbsp;`mCZTSum`에 `SensorValue`을(를) 더함 |
| 119 | &emsp;→&nbsp;`mCZTMax` ← [`mCZTMax`, `SensorValue`] 중 최댓값 |
| 120 | &emsp;→&nbsp;`mCZTMin` ← [`mCZTMin`, `SensorValue`] 중 최솟값 |
| 121 | 115행 조건이 성립하지 않으면 : |
| 122 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 124 | 냉복도 온도 사용 센서 수 설정 (`VP_FWU_CZT_Count`) ≥ 3 **그리고** `mbUpperOk` = TRUE(1) **그리고** 냉복도 온도 3번 센서 고장 알람 (`VP_FWU_CZT-3_Failure_Alarm`) = FALSE(0) 이면 : |
| 125 | &emsp;→&nbsp;`SensorValue` ← 냉복도 온도 3번 값 (`VP_FWU_CZT-3`) 값 읽기 |
| 126 | &emsp;→&nbsp;`mCZTCount`에 1을(를) 더함 |
| 127 | &emsp;→&nbsp;`mCZTSum`에 `SensorValue`을(를) 더함 |
| 128 | &emsp;→&nbsp;`mCZTMax` ← [`mCZTMax`, `SensorValue`] 중 최댓값 |
| 129 | &emsp;→&nbsp;`mCZTMin` ← [`mCZTMin`, `SensorValue`] 중 최솟값 |
| 130 | 124행 조건이 성립하지 않으면 : |
| 131 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 133 | 냉복도 온도 사용 센서 수 설정 (`VP_FWU_CZT_Count`) ≥ 4 **그리고** `mbUpperOk` = TRUE(1) **그리고** 냉복도 온도 4번 센서 고장 알람 (`VP_FWU_CZT-4_Failure_Alarm`) = FALSE(0) 이면 : |
| 134 | &emsp;→&nbsp;`SensorValue` ← 냉복도 온도 4번 값 (`VP_FWU_CZT-4`) 값 읽기 |
| 135 | &emsp;→&nbsp;`mCZTCount`에 1을(를) 더함 |
| 136 | &emsp;→&nbsp;`mCZTSum`에 `SensorValue`을(를) 더함 |
| 137 | &emsp;→&nbsp;`mCZTMax` ← [`mCZTMax`, `SensorValue`] 중 최댓값 |
| 138 | &emsp;→&nbsp;`mCZTMin` ← [`mCZTMin`, `SensorValue`] 중 최솟값 |
| 139 | 133행 조건이 성립하지 않으면 : |
| 140 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 142 | 냉복도 온도 사용 센서 수 설정 (`VP_FWU_CZT_Count`) ≥ 5 **그리고** `mbUpperOk` = TRUE(1) **그리고** 냉복도 온도 5번 센서 고장 알람 (`VP_FWU_CZT-5_Failure_Alarm`) = FALSE(0) 이면 : |
| 143 | &emsp;→&nbsp;`SensorValue` ← 냉복도 온도 5번 값 (`VP_FWU_CZT-5`) 값 읽기 |
| 144 | &emsp;→&nbsp;`mCZTCount`에 1을(를) 더함 |
| 145 | &emsp;→&nbsp;`mCZTSum`에 `SensorValue`을(를) 더함 |
| 146 | &emsp;→&nbsp;`mCZTMax` ← [`mCZTMax`, `SensorValue`] 중 최댓값 |
| 147 | &emsp;→&nbsp;`mCZTMin` ← [`mCZTMin`, `SensorValue`] 중 최솟값 |
| 148 | 142행 조건이 성립하지 않으면 : |
| 149 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 151 | 냉복도 온도 사용 센서 수 설정 (`VP_FWU_CZT_Count`) ≥ 6 **그리고** `mbUpperOk` = TRUE(1) **그리고** 냉복도 온도 6번 센서 고장 알람 (`VP_FWU_CZT-6_Failure_Alarm`) = FALSE(0) 이면 : |
| 152 | &emsp;→&nbsp;`SensorValue` ← 냉복도 온도 6번 값 (`VP_FWU_CZT-6`) 값 읽기 |
| 153 | &emsp;→&nbsp;`mCZTCount`에 1을(를) 더함 |
| 154 | &emsp;→&nbsp;`mCZTSum`에 `SensorValue`을(를) 더함 |
| 155 | &emsp;→&nbsp;`mCZTMax` ← [`mCZTMax`, `SensorValue`] 중 최댓값 |
| 156 | &emsp;→&nbsp;`mCZTMin` ← [`mCZTMin`, `SensorValue`] 중 최솟값 |
| 157 | 151행 조건이 성립하지 않으면 : |
| 158 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 160 | 냉복도 온도 사용 센서 수 설정 (`VP_FWU_CZT_Count`) ≥ 7 **그리고** `mbUpperOk` = TRUE(1) **그리고** 냉복도 온도 7번 센서 고장 알람 (`VP_FWU_CZT-7_Failure_Alarm`) = FALSE(0) 이면 : |
| 161 | &emsp;→&nbsp;`SensorValue` ← 냉복도 온도 7번 값 (`VP_FWU_CZT-7`) 값 읽기 |
| 162 | &emsp;→&nbsp;`mCZTCount`에 1을(를) 더함 |
| 163 | &emsp;→&nbsp;`mCZTSum`에 `SensorValue`을(를) 더함 |
| 164 | &emsp;→&nbsp;`mCZTMax` ← [`mCZTMax`, `SensorValue`] 중 최댓값 |
| 165 | &emsp;→&nbsp;`mCZTMin` ← [`mCZTMin`, `SensorValue`] 중 최솟값 |
| 166 | 160행 조건이 성립하지 않으면 : |
| 167 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 169 | 냉복도 온도 사용 센서 수 설정 (`VP_FWU_CZT_Count`) ≥ 8 **그리고** `mbUpperOk` = TRUE(1) **그리고** 냉복도 온도 8번 센서 고장 알람 (`VP_FWU_CZT-8_Failure_Alarm`) = FALSE(0) 이면 : |
| 170 | &emsp;→&nbsp;`SensorValue` ← 냉복도 온도 8번 값 (`VP_FWU_CZT-8`) 값 읽기 |
| 171 | &emsp;→&nbsp;`mCZTCount`에 1을(를) 더함 |
| 172 | &emsp;→&nbsp;`mCZTSum`에 `SensorValue`을(를) 더함 |
| 173 | &emsp;→&nbsp;`mCZTMax` ← [`mCZTMax`, `SensorValue`] 중 최댓값 |
| 174 | &emsp;→&nbsp;`mCZTMin` ← [`mCZTMin`, `SensorValue`] 중 최솟값 |
| 175 | 169행 조건이 성립하지 않으면 : |
| 176 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 178 | 냉복도 온도 사용 센서 수 설정 (`VP_FWU_CZT_Count`) ≥ 9 **그리고** `mbUpperOk` = TRUE(1) **그리고** 냉복도 온도 9번 센서 고장 알람 (`VP_FWU_CZT-9_Failure_Alarm`) = FALSE(0) 이면 : |
| 179 | &emsp;→&nbsp;`SensorValue` ← 냉복도 온도 9번 값 (`VP_FWU_CZT-9`) 값 읽기 |
| 180 | &emsp;→&nbsp;`mCZTCount`에 1을(를) 더함 |
| 181 | &emsp;→&nbsp;`mCZTSum`에 `SensorValue`을(를) 더함 |
| 182 | &emsp;→&nbsp;`mCZTMax` ← [`mCZTMax`, `SensorValue`] 중 최댓값 |
| 183 | &emsp;→&nbsp;`mCZTMin` ← [`mCZTMin`, `SensorValue`] 중 최솟값 |
| 184 | 178행 조건이 성립하지 않으면 : |
| 185 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 187 | 냉복도 온도 사용 센서 수 설정 (`VP_FWU_CZT_Count`) ≥ 10 **그리고** `mbUpperOk` = TRUE(1) **그리고** 냉복도 온도 10번 센서 고장 알람 (`VP_FWU_CZT-10_Failure_Alarm`) = FALSE(0) 이면 : |
| 188 | &emsp;→&nbsp;`SensorValue` ← 냉복도 온도 10번 값 (`VP_FWU_CZT-10`) 값 읽기 |
| 189 | &emsp;→&nbsp;`mCZTCount`에 1을(를) 더함 |
| 190 | &emsp;→&nbsp;`mCZTSum`에 `SensorValue`을(를) 더함 |
| 191 | &emsp;→&nbsp;`mCZTMax` ← [`mCZTMax`, `SensorValue`] 중 최댓값 |
| 192 | &emsp;→&nbsp;`mCZTMin` ← [`mCZTMin`, `SensorValue`] 중 최솟값 |
| 193 | 187행 조건이 성립하지 않으면 : |
| 194 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |

<a id="section-7"></a>

## 196~206행 · 쓸 수 있는 센서가 하나라도 있으면 평균·최대·최소를 내보내고, 없으면 0과 '무효'로 표시

| 행 | 해석 |
|---:|---|
| 196 | *[주석] 쓸 수 있는 센서가 하나라도 있으면 평균·최대·최소를 내보내고, 없으면 0과 '무효'로 표시* |
| 197 | `mCZTCount` > 0 이면 : |
| 198 | &emsp;→&nbsp;냉복도 온도 평균 (`VP_FWU_CZT_Avg`)에 `mCZTSum` ÷ `mCZTCount` 기록 — 기본 우선순위(P5) |
| 199 | &emsp;→&nbsp;냉복도 온도 최대값 (`VP_FWU_CZT_Max`)에 `mCZTMax` 기록 — 기본 우선순위(P5) |
| 200 | &emsp;→&nbsp;냉복도 온도 최소값 (`VP_FWU_CZT_Min`)에 `mCZTMin` 기록 — 기본 우선순위(P5) |
| 201 | &emsp;→&nbsp;냉복도 온도 제어용 값 유효 표시 (`VP_FWU_CZT_PV_Valid`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 202 | 197행 조건이 성립하지 않으면 : |
| 203 | &emsp;→&nbsp;냉복도 온도 평균 (`VP_FWU_CZT_Avg`)에 0 기록 — 기본 우선순위(P5) |
| 204 | &emsp;→&nbsp;냉복도 온도 최대값 (`VP_FWU_CZT_Max`)에 0 기록 — 기본 우선순위(P5) |
| 205 | &emsp;→&nbsp;냉복도 온도 최소값 (`VP_FWU_CZT_Min`)에 0 기록 — 기본 우선순위(P5) |
| 206 | &emsp;→&nbsp;냉복도 온도 제어용 값 유효 표시 (`VP_FWU_CZT_PV_Valid`)에 FALSE(0) 기록 — 기본 우선순위(P5) |

<a id="section-8"></a>

## 208~215행 · 제어에 쓸 CZT 값 (Select 0 = 평균, 1 = 최대)

| 행 | 해석 |
|---:|---|
| 208 | *[주석] 제어에 쓸 CZT 값 (Select 0 = 평균, 1 = 최대)* |
| 209 | 냉복도 온도 제어용 값 유효 표시 (`VP_FWU_CZT_PV_Valid`) = TRUE(1) 이면 : |
| 210 | &emsp;→&nbsp;냉복도 온도 제어값 선택 설정 (`VP_FWU_CZT_Select`) = FALSE(0) 이면 : |
| 211 | &emsp;&emsp;→&nbsp;냉복도 온도 제어용 값(PV) (`VP_FWU_CZT_PV`)에 냉복도 온도 평균 (`VP_FWU_CZT_Avg`) 값을 그대로 복사 — 기본 우선순위(P5) |
| 212 | &emsp;→&nbsp;210행 조건이 성립하지 않으면 : |
| 213 | &emsp;&emsp;→&nbsp;냉복도 온도 제어용 값(PV) (`VP_FWU_CZT_PV`)에 냉복도 온도 최대값 (`VP_FWU_CZT_Max`) 값을 그대로 복사 — 기본 우선순위(P5) |
| 214 | 209행 조건이 성립하지 않으면 : |
| 215 | &emsp;→&nbsp;냉복도 온도 제어용 값(PV) (`VP_FWU_CZT_PV`)에 0 기록 — 기본 우선순위(P5) |

<a id="section-9"></a>

## 217~307행 · HZT(열복도 온도) 집계

> 사용 개수(HZT_Count) 안의 센서 중, 상위 통신이 정상이고 고장 알람이 없는 것만 평균·최대·최소에 넣는다

| 행 | 해석 |
|---:|---|
| 217 | *[주석] HZT(열복도 온도) 집계* |
| 218 | *[주석] 사용 개수(HZT_Count) 안의 센서 중, 상위 통신이 정상이고 고장 알람이 없는 것만 평균·최대·최소에 넣는다* |
| 219 | 열복도 온도 사용 센서 수 설정 (`VP_FWU_HZT_Count`) ≥ 1 **그리고** `mbUpperOk` = TRUE(1) **그리고** 열복도 온도 1번 센서 고장 알람 (`VP_FWU_HZT-1_Failure_Alarm`) = FALSE(0) 이면 : |
| 220 | &emsp;→&nbsp;`SensorValue` ← 열복도 온도 1번 값 (`VP_FWU_HZT-1`) 값 읽기 |
| 221 | &emsp;→&nbsp;`mHZTCount`에 1을(를) 더함 |
| 222 | &emsp;→&nbsp;`mHZTSum`에 `SensorValue`을(를) 더함 |
| 223 | &emsp;→&nbsp;`mHZTMax` ← [`mHZTMax`, `SensorValue`] 중 최댓값 |
| 224 | &emsp;→&nbsp;`mHZTMin` ← [`mHZTMin`, `SensorValue`] 중 최솟값 |
| 225 | 219행 조건이 성립하지 않으면 : |
| 226 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 228 | 열복도 온도 사용 센서 수 설정 (`VP_FWU_HZT_Count`) ≥ 2 **그리고** `mbUpperOk` = TRUE(1) **그리고** 열복도 온도 2번 센서 고장 알람 (`VP_FWU_HZT-2_Failure_Alarm`) = FALSE(0) 이면 : |
| 229 | &emsp;→&nbsp;`SensorValue` ← 열복도 온도 2번 값 (`VP_FWU_HZT-2`) 값 읽기 |
| 230 | &emsp;→&nbsp;`mHZTCount`에 1을(를) 더함 |
| 231 | &emsp;→&nbsp;`mHZTSum`에 `SensorValue`을(를) 더함 |
| 232 | &emsp;→&nbsp;`mHZTMax` ← [`mHZTMax`, `SensorValue`] 중 최댓값 |
| 233 | &emsp;→&nbsp;`mHZTMin` ← [`mHZTMin`, `SensorValue`] 중 최솟값 |
| 234 | 228행 조건이 성립하지 않으면 : |
| 235 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 237 | 열복도 온도 사용 센서 수 설정 (`VP_FWU_HZT_Count`) ≥ 3 **그리고** `mbUpperOk` = TRUE(1) **그리고** 열복도 온도 3번 센서 고장 알람 (`VP_FWU_HZT-3_Failure_Alarm`) = FALSE(0) 이면 : |
| 238 | &emsp;→&nbsp;`SensorValue` ← 열복도 온도 3번 값 (`VP_FWU_HZT-3`) 값 읽기 |
| 239 | &emsp;→&nbsp;`mHZTCount`에 1을(를) 더함 |
| 240 | &emsp;→&nbsp;`mHZTSum`에 `SensorValue`을(를) 더함 |
| 241 | &emsp;→&nbsp;`mHZTMax` ← [`mHZTMax`, `SensorValue`] 중 최댓값 |
| 242 | &emsp;→&nbsp;`mHZTMin` ← [`mHZTMin`, `SensorValue`] 중 최솟값 |
| 243 | 237행 조건이 성립하지 않으면 : |
| 244 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 246 | 열복도 온도 사용 센서 수 설정 (`VP_FWU_HZT_Count`) ≥ 4 **그리고** `mbUpperOk` = TRUE(1) **그리고** 열복도 온도 4번 센서 고장 알람 (`VP_FWU_HZT-4_Failure_Alarm`) = FALSE(0) 이면 : |
| 247 | &emsp;→&nbsp;`SensorValue` ← 열복도 온도 4번 값 (`VP_FWU_HZT-4`) 값 읽기 |
| 248 | &emsp;→&nbsp;`mHZTCount`에 1을(를) 더함 |
| 249 | &emsp;→&nbsp;`mHZTSum`에 `SensorValue`을(를) 더함 |
| 250 | &emsp;→&nbsp;`mHZTMax` ← [`mHZTMax`, `SensorValue`] 중 최댓값 |
| 251 | &emsp;→&nbsp;`mHZTMin` ← [`mHZTMin`, `SensorValue`] 중 최솟값 |
| 252 | 246행 조건이 성립하지 않으면 : |
| 253 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 255 | 열복도 온도 사용 센서 수 설정 (`VP_FWU_HZT_Count`) ≥ 5 **그리고** `mbUpperOk` = TRUE(1) **그리고** 열복도 온도 5번 센서 고장 알람 (`VP_FWU_HZT-5_Failure_Alarm`) = FALSE(0) 이면 : |
| 256 | &emsp;→&nbsp;`SensorValue` ← 열복도 온도 5번 값 (`VP_FWU_HZT-5`) 값 읽기 |
| 257 | &emsp;→&nbsp;`mHZTCount`에 1을(를) 더함 |
| 258 | &emsp;→&nbsp;`mHZTSum`에 `SensorValue`을(를) 더함 |
| 259 | &emsp;→&nbsp;`mHZTMax` ← [`mHZTMax`, `SensorValue`] 중 최댓값 |
| 260 | &emsp;→&nbsp;`mHZTMin` ← [`mHZTMin`, `SensorValue`] 중 최솟값 |
| 261 | 255행 조건이 성립하지 않으면 : |
| 262 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 264 | 열복도 온도 사용 센서 수 설정 (`VP_FWU_HZT_Count`) ≥ 6 **그리고** `mbUpperOk` = TRUE(1) **그리고** 열복도 온도 6번 센서 고장 알람 (`VP_FWU_HZT-6_Failure_Alarm`) = FALSE(0) 이면 : |
| 265 | &emsp;→&nbsp;`SensorValue` ← 열복도 온도 6번 값 (`VP_FWU_HZT-6`) 값 읽기 |
| 266 | &emsp;→&nbsp;`mHZTCount`에 1을(를) 더함 |
| 267 | &emsp;→&nbsp;`mHZTSum`에 `SensorValue`을(를) 더함 |
| 268 | &emsp;→&nbsp;`mHZTMax` ← [`mHZTMax`, `SensorValue`] 중 최댓값 |
| 269 | &emsp;→&nbsp;`mHZTMin` ← [`mHZTMin`, `SensorValue`] 중 최솟값 |
| 270 | 264행 조건이 성립하지 않으면 : |
| 271 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 273 | 열복도 온도 사용 센서 수 설정 (`VP_FWU_HZT_Count`) ≥ 7 **그리고** `mbUpperOk` = TRUE(1) **그리고** 열복도 온도 7번 센서 고장 알람 (`VP_FWU_HZT-7_Failure_Alarm`) = FALSE(0) 이면 : |
| 274 | &emsp;→&nbsp;`SensorValue` ← 열복도 온도 7번 값 (`VP_FWU_HZT-7`) 값 읽기 |
| 275 | &emsp;→&nbsp;`mHZTCount`에 1을(를) 더함 |
| 276 | &emsp;→&nbsp;`mHZTSum`에 `SensorValue`을(를) 더함 |
| 277 | &emsp;→&nbsp;`mHZTMax` ← [`mHZTMax`, `SensorValue`] 중 최댓값 |
| 278 | &emsp;→&nbsp;`mHZTMin` ← [`mHZTMin`, `SensorValue`] 중 최솟값 |
| 279 | 273행 조건이 성립하지 않으면 : |
| 280 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 282 | 열복도 온도 사용 센서 수 설정 (`VP_FWU_HZT_Count`) ≥ 8 **그리고** `mbUpperOk` = TRUE(1) **그리고** 열복도 온도 8번 센서 고장 알람 (`VP_FWU_HZT-8_Failure_Alarm`) = FALSE(0) 이면 : |
| 283 | &emsp;→&nbsp;`SensorValue` ← 열복도 온도 8번 값 (`VP_FWU_HZT-8`) 값 읽기 |
| 284 | &emsp;→&nbsp;`mHZTCount`에 1을(를) 더함 |
| 285 | &emsp;→&nbsp;`mHZTSum`에 `SensorValue`을(를) 더함 |
| 286 | &emsp;→&nbsp;`mHZTMax` ← [`mHZTMax`, `SensorValue`] 중 최댓값 |
| 287 | &emsp;→&nbsp;`mHZTMin` ← [`mHZTMin`, `SensorValue`] 중 최솟값 |
| 288 | 282행 조건이 성립하지 않으면 : |
| 289 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 291 | 열복도 온도 사용 센서 수 설정 (`VP_FWU_HZT_Count`) ≥ 9 **그리고** `mbUpperOk` = TRUE(1) **그리고** 열복도 온도 9번 센서 고장 알람 (`VP_FWU_HZT-9_Failure_Alarm`) = FALSE(0) 이면 : |
| 292 | &emsp;→&nbsp;`SensorValue` ← 열복도 온도 9번 값 (`VP_FWU_HZT-9`) 값 읽기 |
| 293 | &emsp;→&nbsp;`mHZTCount`에 1을(를) 더함 |
| 294 | &emsp;→&nbsp;`mHZTSum`에 `SensorValue`을(를) 더함 |
| 295 | &emsp;→&nbsp;`mHZTMax` ← [`mHZTMax`, `SensorValue`] 중 최댓값 |
| 296 | &emsp;→&nbsp;`mHZTMin` ← [`mHZTMin`, `SensorValue`] 중 최솟값 |
| 297 | 291행 조건이 성립하지 않으면 : |
| 298 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 300 | 열복도 온도 사용 센서 수 설정 (`VP_FWU_HZT_Count`) ≥ 10 **그리고** `mbUpperOk` = TRUE(1) **그리고** 열복도 온도 10번 센서 고장 알람 (`VP_FWU_HZT-10_Failure_Alarm`) = FALSE(0) 이면 : |
| 301 | &emsp;→&nbsp;`SensorValue` ← 열복도 온도 10번 값 (`VP_FWU_HZT-10`) 값 읽기 |
| 302 | &emsp;→&nbsp;`mHZTCount`에 1을(를) 더함 |
| 303 | &emsp;→&nbsp;`mHZTSum`에 `SensorValue`을(를) 더함 |
| 304 | &emsp;→&nbsp;`mHZTMax` ← [`mHZTMax`, `SensorValue`] 중 최댓값 |
| 305 | &emsp;→&nbsp;`mHZTMin` ← [`mHZTMin`, `SensorValue`] 중 최솟값 |
| 306 | 300행 조건이 성립하지 않으면 : |
| 307 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |

<a id="section-10"></a>

## 309~319행 · 쓸 수 있는 센서가 하나라도 있으면 평균·최대·최소를 내보내고, 없으면 0과 '무효'로 표시

| 행 | 해석 |
|---:|---|
| 309 | *[주석] 쓸 수 있는 센서가 하나라도 있으면 평균·최대·최소를 내보내고, 없으면 0과 '무효'로 표시* |
| 310 | `mHZTCount` > 0 이면 : |
| 311 | &emsp;→&nbsp;열복도 온도 평균 (`VP_FWU_HZT_Avg`)에 `mHZTSum` ÷ `mHZTCount` 기록 — 기본 우선순위(P5) |
| 312 | &emsp;→&nbsp;열복도 온도 최대값 (`VP_FWU_HZT_Max`)에 `mHZTMax` 기록 — 기본 우선순위(P5) |
| 313 | &emsp;→&nbsp;열복도 온도 최소값 (`VP_FWU_HZT_Min`)에 `mHZTMin` 기록 — 기본 우선순위(P5) |
| 314 | &emsp;→&nbsp;열복도 온도 제어용 값 유효 표시 (`VP_FWU_HZT_PV_Valid`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 315 | 310행 조건이 성립하지 않으면 : |
| 316 | &emsp;→&nbsp;열복도 온도 평균 (`VP_FWU_HZT_Avg`)에 0 기록 — 기본 우선순위(P5) |
| 317 | &emsp;→&nbsp;열복도 온도 최대값 (`VP_FWU_HZT_Max`)에 0 기록 — 기본 우선순위(P5) |
| 318 | &emsp;→&nbsp;열복도 온도 최소값 (`VP_FWU_HZT_Min`)에 0 기록 — 기본 우선순위(P5) |
| 319 | &emsp;→&nbsp;열복도 온도 제어용 값 유효 표시 (`VP_FWU_HZT_PV_Valid`)에 FALSE(0) 기록 — 기본 우선순위(P5) |

<a id="section-11"></a>

## 321~328행 · 제어에 쓸 HZT 값 (Select 0 = 평균, 1 = 최대)

| 행 | 해석 |
|---:|---|
| 321 | *[주석] 제어에 쓸 HZT 값 (Select 0 = 평균, 1 = 최대)* |
| 322 | 열복도 온도 제어용 값 유효 표시 (`VP_FWU_HZT_PV_Valid`) = TRUE(1) 이면 : |
| 323 | &emsp;→&nbsp;열복도 온도 제어값 선택 설정 (`VP_FWU_HZT_Select`) = FALSE(0) 이면 : |
| 324 | &emsp;&emsp;→&nbsp;열복도 온도 제어용 값(PV) (`VP_FWU_HZT_PV`)에 열복도 온도 평균 (`VP_FWU_HZT_Avg`) 값을 그대로 복사 — 기본 우선순위(P5) |
| 325 | &emsp;→&nbsp;323행 조건이 성립하지 않으면 : |
| 326 | &emsp;&emsp;→&nbsp;열복도 온도 제어용 값(PV) (`VP_FWU_HZT_PV`)에 열복도 온도 최대값 (`VP_FWU_HZT_Max`) 값을 그대로 복사 — 기본 우선순위(P5) |
| 327 | 322행 조건이 성립하지 않으면 : |
| 328 | &emsp;→&nbsp;열복도 온도 제어용 값(PV) (`VP_FWU_HZT_PV`)에 0 기록 — 기본 우선순위(P5) |

<a id="section-12"></a>

## 330~420행 · RDP(룸 차압) 집계

> 사용 개수(RDP_Count) 안의 센서 중, 상위 통신이 정상이고 고장 알람이 없는 것만 평균·최대·최소에 넣는다

| 행 | 해석 |
|---:|---|
| 330 | *[주석] RDP(룸 차압) 집계* |
| 331 | *[주석] 사용 개수(RDP_Count) 안의 센서 중, 상위 통신이 정상이고 고장 알람이 없는 것만 평균·최대·최소에 넣는다* |
| 332 | 룸 차압 사용 센서 수 설정 (`VP_FWU_RDP_Count`) ≥ 1 **그리고** `mbUpperOk` = TRUE(1) **그리고** 룸 차압 1번 센서 고장 알람 (`VP_FWU_RDP-1_Failure_Alarm`) = FALSE(0) 이면 : |
| 333 | &emsp;→&nbsp;`SensorValue` ← 룸 차압 1번 값 (`VP_FWU_RDP-1`) 값 읽기 |
| 334 | &emsp;→&nbsp;`mRDPCount`에 1을(를) 더함 |
| 335 | &emsp;→&nbsp;`mRDPSum`에 `SensorValue`을(를) 더함 |
| 336 | &emsp;→&nbsp;`mRDPMax` ← [`mRDPMax`, `SensorValue`] 중 최댓값 |
| 337 | &emsp;→&nbsp;`mRDPMin` ← [`mRDPMin`, `SensorValue`] 중 최솟값 |
| 338 | 332행 조건이 성립하지 않으면 : |
| 339 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 341 | 룸 차압 사용 센서 수 설정 (`VP_FWU_RDP_Count`) ≥ 2 **그리고** `mbUpperOk` = TRUE(1) **그리고** 룸 차압 2번 센서 고장 알람 (`VP_FWU_RDP-2_Failure_Alarm`) = FALSE(0) 이면 : |
| 342 | &emsp;→&nbsp;`SensorValue` ← 룸 차압 2번 값 (`VP_FWU_RDP-2`) 값 읽기 |
| 343 | &emsp;→&nbsp;`mRDPCount`에 1을(를) 더함 |
| 344 | &emsp;→&nbsp;`mRDPSum`에 `SensorValue`을(를) 더함 |
| 345 | &emsp;→&nbsp;`mRDPMax` ← [`mRDPMax`, `SensorValue`] 중 최댓값 |
| 346 | &emsp;→&nbsp;`mRDPMin` ← [`mRDPMin`, `SensorValue`] 중 최솟값 |
| 347 | 341행 조건이 성립하지 않으면 : |
| 348 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 350 | 룸 차압 사용 센서 수 설정 (`VP_FWU_RDP_Count`) ≥ 3 **그리고** `mbUpperOk` = TRUE(1) **그리고** 룸 차압 3번 센서 고장 알람 (`VP_FWU_RDP-3_Failure_Alarm`) = FALSE(0) 이면 : |
| 351 | &emsp;→&nbsp;`SensorValue` ← 룸 차압 3번 값 (`VP_FWU_RDP-3`) 값 읽기 |
| 352 | &emsp;→&nbsp;`mRDPCount`에 1을(를) 더함 |
| 353 | &emsp;→&nbsp;`mRDPSum`에 `SensorValue`을(를) 더함 |
| 354 | &emsp;→&nbsp;`mRDPMax` ← [`mRDPMax`, `SensorValue`] 중 최댓값 |
| 355 | &emsp;→&nbsp;`mRDPMin` ← [`mRDPMin`, `SensorValue`] 중 최솟값 |
| 356 | 350행 조건이 성립하지 않으면 : |
| 357 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 359 | 룸 차압 사용 센서 수 설정 (`VP_FWU_RDP_Count`) ≥ 4 **그리고** `mbUpperOk` = TRUE(1) **그리고** 룸 차압 4번 센서 고장 알람 (`VP_FWU_RDP-4_Failure_Alarm`) = FALSE(0) 이면 : |
| 360 | &emsp;→&nbsp;`SensorValue` ← 룸 차압 4번 값 (`VP_FWU_RDP-4`) 값 읽기 |
| 361 | &emsp;→&nbsp;`mRDPCount`에 1을(를) 더함 |
| 362 | &emsp;→&nbsp;`mRDPSum`에 `SensorValue`을(를) 더함 |
| 363 | &emsp;→&nbsp;`mRDPMax` ← [`mRDPMax`, `SensorValue`] 중 최댓값 |
| 364 | &emsp;→&nbsp;`mRDPMin` ← [`mRDPMin`, `SensorValue`] 중 최솟값 |
| 365 | 359행 조건이 성립하지 않으면 : |
| 366 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 368 | 룸 차압 사용 센서 수 설정 (`VP_FWU_RDP_Count`) ≥ 5 **그리고** `mbUpperOk` = TRUE(1) **그리고** 룸 차압 5번 센서 고장 알람 (`VP_FWU_RDP-5_Failure_Alarm`) = FALSE(0) 이면 : |
| 369 | &emsp;→&nbsp;`SensorValue` ← 룸 차압 5번 값 (`VP_FWU_RDP-5`) 값 읽기 |
| 370 | &emsp;→&nbsp;`mRDPCount`에 1을(를) 더함 |
| 371 | &emsp;→&nbsp;`mRDPSum`에 `SensorValue`을(를) 더함 |
| 372 | &emsp;→&nbsp;`mRDPMax` ← [`mRDPMax`, `SensorValue`] 중 최댓값 |
| 373 | &emsp;→&nbsp;`mRDPMin` ← [`mRDPMin`, `SensorValue`] 중 최솟값 |
| 374 | 368행 조건이 성립하지 않으면 : |
| 375 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 377 | 룸 차압 사용 센서 수 설정 (`VP_FWU_RDP_Count`) ≥ 6 **그리고** `mbUpperOk` = TRUE(1) **그리고** 룸 차압 6번 센서 고장 알람 (`VP_FWU_RDP-6_Failure_Alarm`) = FALSE(0) 이면 : |
| 378 | &emsp;→&nbsp;`SensorValue` ← 룸 차압 6번 값 (`VP_FWU_RDP-6`) 값 읽기 |
| 379 | &emsp;→&nbsp;`mRDPCount`에 1을(를) 더함 |
| 380 | &emsp;→&nbsp;`mRDPSum`에 `SensorValue`을(를) 더함 |
| 381 | &emsp;→&nbsp;`mRDPMax` ← [`mRDPMax`, `SensorValue`] 중 최댓값 |
| 382 | &emsp;→&nbsp;`mRDPMin` ← [`mRDPMin`, `SensorValue`] 중 최솟값 |
| 383 | 377행 조건이 성립하지 않으면 : |
| 384 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 386 | 룸 차압 사용 센서 수 설정 (`VP_FWU_RDP_Count`) ≥ 7 **그리고** `mbUpperOk` = TRUE(1) **그리고** 룸 차압 7번 센서 고장 알람 (`VP_FWU_RDP-7_Failure_Alarm`) = FALSE(0) 이면 : |
| 387 | &emsp;→&nbsp;`SensorValue` ← 룸 차압 7번 값 (`VP_FWU_RDP-7`) 값 읽기 |
| 388 | &emsp;→&nbsp;`mRDPCount`에 1을(를) 더함 |
| 389 | &emsp;→&nbsp;`mRDPSum`에 `SensorValue`을(를) 더함 |
| 390 | &emsp;→&nbsp;`mRDPMax` ← [`mRDPMax`, `SensorValue`] 중 최댓값 |
| 391 | &emsp;→&nbsp;`mRDPMin` ← [`mRDPMin`, `SensorValue`] 중 최솟값 |
| 392 | 386행 조건이 성립하지 않으면 : |
| 393 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 395 | 룸 차압 사용 센서 수 설정 (`VP_FWU_RDP_Count`) ≥ 8 **그리고** `mbUpperOk` = TRUE(1) **그리고** 룸 차압 8번 센서 고장 알람 (`VP_FWU_RDP-8_Failure_Alarm`) = FALSE(0) 이면 : |
| 396 | &emsp;→&nbsp;`SensorValue` ← 룸 차압 8번 값 (`VP_FWU_RDP-8`) 값 읽기 |
| 397 | &emsp;→&nbsp;`mRDPCount`에 1을(를) 더함 |
| 398 | &emsp;→&nbsp;`mRDPSum`에 `SensorValue`을(를) 더함 |
| 399 | &emsp;→&nbsp;`mRDPMax` ← [`mRDPMax`, `SensorValue`] 중 최댓값 |
| 400 | &emsp;→&nbsp;`mRDPMin` ← [`mRDPMin`, `SensorValue`] 중 최솟값 |
| 401 | 395행 조건이 성립하지 않으면 : |
| 402 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 404 | 룸 차압 사용 센서 수 설정 (`VP_FWU_RDP_Count`) ≥ 9 **그리고** `mbUpperOk` = TRUE(1) **그리고** 룸 차압 9번 센서 고장 알람 (`VP_FWU_RDP-9_Failure_Alarm`) = FALSE(0) 이면 : |
| 405 | &emsp;→&nbsp;`SensorValue` ← 룸 차압 9번 값 (`VP_FWU_RDP-9`) 값 읽기 |
| 406 | &emsp;→&nbsp;`mRDPCount`에 1을(를) 더함 |
| 407 | &emsp;→&nbsp;`mRDPSum`에 `SensorValue`을(를) 더함 |
| 408 | &emsp;→&nbsp;`mRDPMax` ← [`mRDPMax`, `SensorValue`] 중 최댓값 |
| 409 | &emsp;→&nbsp;`mRDPMin` ← [`mRDPMin`, `SensorValue`] 중 최솟값 |
| 410 | 404행 조건이 성립하지 않으면 : |
| 411 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 413 | 룸 차압 사용 센서 수 설정 (`VP_FWU_RDP_Count`) ≥ 10 **그리고** `mbUpperOk` = TRUE(1) **그리고** 룸 차압 10번 센서 고장 알람 (`VP_FWU_RDP-10_Failure_Alarm`) = FALSE(0) 이면 : |
| 414 | &emsp;→&nbsp;`SensorValue` ← 룸 차압 10번 값 (`VP_FWU_RDP-10`) 값 읽기 |
| 415 | &emsp;→&nbsp;`mRDPCount`에 1을(를) 더함 |
| 416 | &emsp;→&nbsp;`mRDPSum`에 `SensorValue`을(를) 더함 |
| 417 | &emsp;→&nbsp;`mRDPMax` ← [`mRDPMax`, `SensorValue`] 중 최댓값 |
| 418 | &emsp;→&nbsp;`mRDPMin` ← [`mRDPMin`, `SensorValue`] 중 최솟값 |
| 419 | 413행 조건이 성립하지 않으면 : |
| 420 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |

<a id="section-13"></a>

## 422~432행 · 쓸 수 있는 센서가 하나라도 있으면 평균·최대·최소를 내보내고, 없으면 0과 '무효'로 표시

| 행 | 해석 |
|---:|---|
| 422 | *[주석] 쓸 수 있는 센서가 하나라도 있으면 평균·최대·최소를 내보내고, 없으면 0과 '무효'로 표시* |
| 423 | `mRDPCount` > 0 이면 : |
| 424 | &emsp;→&nbsp;룸 차압 평균 (`VP_FWU_RDP_Avg`)에 `mRDPSum` ÷ `mRDPCount` 기록 — 기본 우선순위(P5) |
| 425 | &emsp;→&nbsp;룸 차압 최대값 (`VP_FWU_RDP_Max`)에 `mRDPMax` 기록 — 기본 우선순위(P5) |
| 426 | &emsp;→&nbsp;룸 차압 최소값 (`VP_FWU_RDP_Min`)에 `mRDPMin` 기록 — 기본 우선순위(P5) |
| 427 | &emsp;→&nbsp;룸 차압 제어용 값 유효 표시 (`VP_FWU_RDP_PV_Valid`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 428 | 423행 조건이 성립하지 않으면 : |
| 429 | &emsp;→&nbsp;룸 차압 평균 (`VP_FWU_RDP_Avg`)에 0 기록 — 기본 우선순위(P5) |
| 430 | &emsp;→&nbsp;룸 차압 최대값 (`VP_FWU_RDP_Max`)에 0 기록 — 기본 우선순위(P5) |
| 431 | &emsp;→&nbsp;룸 차압 최소값 (`VP_FWU_RDP_Min`)에 0 기록 — 기본 우선순위(P5) |
| 432 | &emsp;→&nbsp;룸 차압 제어용 값 유효 표시 (`VP_FWU_RDP_PV_Valid`)에 FALSE(0) 기록 — 기본 우선순위(P5) |

<a id="section-14"></a>

## 434~441행 · 제어에 쓸 RDP 값 (Select 0 = 평균, 1 = 최소)

| 행 | 해석 |
|---:|---|
| 434 | *[주석] 제어에 쓸 RDP 값 (Select 0 = 평균, 1 = 최소)* |
| 435 | 룸 차압 제어용 값 유효 표시 (`VP_FWU_RDP_PV_Valid`) = TRUE(1) 이면 : |
| 436 | &emsp;→&nbsp;룸 차압 제어값 선택 설정 (`VP_FWU_RDP_Select`) = FALSE(0) 이면 : |
| 437 | &emsp;&emsp;→&nbsp;룸 차압 제어용 값(PV) (`VP_FWU_RDP_PV`)에 룸 차압 평균 (`VP_FWU_RDP_Avg`) 값을 그대로 복사 — 기본 우선순위(P5) |
| 438 | &emsp;→&nbsp;436행 조건이 성립하지 않으면 : |
| 439 | &emsp;&emsp;→&nbsp;룸 차압 제어용 값(PV) (`VP_FWU_RDP_PV`)에 룸 차압 최소값 (`VP_FWU_RDP_Min`) 값을 그대로 복사 — 기본 우선순위(P5) |
| 440 | 435행 조건이 성립하지 않으면 : |
| 441 | &emsp;→&nbsp;룸 차압 제어용 값(PV) (`VP_FWU_RDP_PV`)에 0 기록 — 기본 우선순위(P5) |

<a id="section-15"></a>

## 443~546행 · CZH(냉복도 습도) 집계: 표시용이라 상위 통신·고장 조건 없이 사용 개수만 본다

| 행 | 해석 |
|---:|---|
| 443 | *[주석] CZH(냉복도 습도) 집계: 표시용이라 상위 통신·고장 조건 없이 사용 개수만 본다* |
| 444 | 냉복도 습도 사용 센서 수 설정 (`VP_FWU_CZH_Count`) ≥ 1 이면 : |
| 445 | &emsp;→&nbsp;`SensorValue` ← 냉복도 습도 1번 값 (`VP_FWU_CZH-1`) 값 읽기 |
| 446 | &emsp;→&nbsp;`mCZHCount`에 1을(를) 더함 |
| 447 | &emsp;→&nbsp;`mCZHSum`에 `SensorValue`을(를) 더함 |
| 448 | &emsp;→&nbsp;`mCZHMax` ← [`mCZHMax`, `SensorValue`] 중 최댓값 |
| 449 | &emsp;→&nbsp;`mCZHMin` ← [`mCZHMin`, `SensorValue`] 중 최솟값 |
| 450 | 444행 조건이 성립하지 않으면 : |
| 451 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 453 | 냉복도 습도 사용 센서 수 설정 (`VP_FWU_CZH_Count`) ≥ 2 이면 : |
| 454 | &emsp;→&nbsp;`SensorValue` ← 냉복도 습도 2번 값 (`VP_FWU_CZH-2`) 값 읽기 |
| 455 | &emsp;→&nbsp;`mCZHCount`에 1을(를) 더함 |
| 456 | &emsp;→&nbsp;`mCZHSum`에 `SensorValue`을(를) 더함 |
| 457 | &emsp;→&nbsp;`mCZHMax` ← [`mCZHMax`, `SensorValue`] 중 최댓값 |
| 458 | &emsp;→&nbsp;`mCZHMin` ← [`mCZHMin`, `SensorValue`] 중 최솟값 |
| 459 | 453행 조건이 성립하지 않으면 : |
| 460 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 462 | 냉복도 습도 사용 센서 수 설정 (`VP_FWU_CZH_Count`) ≥ 3 이면 : |
| 463 | &emsp;→&nbsp;`SensorValue` ← 냉복도 습도 3번 값 (`VP_FWU_CZH-3`) 값 읽기 |
| 464 | &emsp;→&nbsp;`mCZHCount`에 1을(를) 더함 |
| 465 | &emsp;→&nbsp;`mCZHSum`에 `SensorValue`을(를) 더함 |
| 466 | &emsp;→&nbsp;`mCZHMax` ← [`mCZHMax`, `SensorValue`] 중 최댓값 |
| 467 | &emsp;→&nbsp;`mCZHMin` ← [`mCZHMin`, `SensorValue`] 중 최솟값 |
| 468 | 462행 조건이 성립하지 않으면 : |
| 469 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 471 | 냉복도 습도 사용 센서 수 설정 (`VP_FWU_CZH_Count`) ≥ 4 이면 : |
| 472 | &emsp;→&nbsp;`SensorValue` ← 냉복도 습도 4번 값 (`VP_FWU_CZH-4`) 값 읽기 |
| 473 | &emsp;→&nbsp;`mCZHCount`에 1을(를) 더함 |
| 474 | &emsp;→&nbsp;`mCZHSum`에 `SensorValue`을(를) 더함 |
| 475 | &emsp;→&nbsp;`mCZHMax` ← [`mCZHMax`, `SensorValue`] 중 최댓값 |
| 476 | &emsp;→&nbsp;`mCZHMin` ← [`mCZHMin`, `SensorValue`] 중 최솟값 |
| 477 | 471행 조건이 성립하지 않으면 : |
| 478 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 480 | 냉복도 습도 사용 센서 수 설정 (`VP_FWU_CZH_Count`) ≥ 5 이면 : |
| 481 | &emsp;→&nbsp;`SensorValue` ← 냉복도 습도 5번 값 (`VP_FWU_CZH-5`) 값 읽기 |
| 482 | &emsp;→&nbsp;`mCZHCount`에 1을(를) 더함 |
| 483 | &emsp;→&nbsp;`mCZHSum`에 `SensorValue`을(를) 더함 |
| 484 | &emsp;→&nbsp;`mCZHMax` ← [`mCZHMax`, `SensorValue`] 중 최댓값 |
| 485 | &emsp;→&nbsp;`mCZHMin` ← [`mCZHMin`, `SensorValue`] 중 최솟값 |
| 486 | 480행 조건이 성립하지 않으면 : |
| 487 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 489 | 냉복도 습도 사용 센서 수 설정 (`VP_FWU_CZH_Count`) ≥ 6 이면 : |
| 490 | &emsp;→&nbsp;`SensorValue` ← 냉복도 습도 6번 값 (`VP_FWU_CZH-6`) 값 읽기 |
| 491 | &emsp;→&nbsp;`mCZHCount`에 1을(를) 더함 |
| 492 | &emsp;→&nbsp;`mCZHSum`에 `SensorValue`을(를) 더함 |
| 493 | &emsp;→&nbsp;`mCZHMax` ← [`mCZHMax`, `SensorValue`] 중 최댓값 |
| 494 | &emsp;→&nbsp;`mCZHMin` ← [`mCZHMin`, `SensorValue`] 중 최솟값 |
| 495 | 489행 조건이 성립하지 않으면 : |
| 496 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 498 | 냉복도 습도 사용 센서 수 설정 (`VP_FWU_CZH_Count`) ≥ 7 이면 : |
| 499 | &emsp;→&nbsp;`SensorValue` ← 냉복도 습도 7번 값 (`VP_FWU_CZH-7`) 값 읽기 |
| 500 | &emsp;→&nbsp;`mCZHCount`에 1을(를) 더함 |
| 501 | &emsp;→&nbsp;`mCZHSum`에 `SensorValue`을(를) 더함 |
| 502 | &emsp;→&nbsp;`mCZHMax` ← [`mCZHMax`, `SensorValue`] 중 최댓값 |
| 503 | &emsp;→&nbsp;`mCZHMin` ← [`mCZHMin`, `SensorValue`] 중 최솟값 |
| 504 | 498행 조건이 성립하지 않으면 : |
| 505 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 507 | 냉복도 습도 사용 센서 수 설정 (`VP_FWU_CZH_Count`) ≥ 8 이면 : |
| 508 | &emsp;→&nbsp;`SensorValue` ← 냉복도 습도 8번 값 (`VP_FWU_CZH-8`) 값 읽기 |
| 509 | &emsp;→&nbsp;`mCZHCount`에 1을(를) 더함 |
| 510 | &emsp;→&nbsp;`mCZHSum`에 `SensorValue`을(를) 더함 |
| 511 | &emsp;→&nbsp;`mCZHMax` ← [`mCZHMax`, `SensorValue`] 중 최댓값 |
| 512 | &emsp;→&nbsp;`mCZHMin` ← [`mCZHMin`, `SensorValue`] 중 최솟값 |
| 513 | 507행 조건이 성립하지 않으면 : |
| 514 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 516 | 냉복도 습도 사용 센서 수 설정 (`VP_FWU_CZH_Count`) ≥ 9 이면 : |
| 517 | &emsp;→&nbsp;`SensorValue` ← 냉복도 습도 9번 값 (`VP_FWU_CZH-9`) 값 읽기 |
| 518 | &emsp;→&nbsp;`mCZHCount`에 1을(를) 더함 |
| 519 | &emsp;→&nbsp;`mCZHSum`에 `SensorValue`을(를) 더함 |
| 520 | &emsp;→&nbsp;`mCZHMax` ← [`mCZHMax`, `SensorValue`] 중 최댓값 |
| 521 | &emsp;→&nbsp;`mCZHMin` ← [`mCZHMin`, `SensorValue`] 중 최솟값 |
| 522 | 516행 조건이 성립하지 않으면 : |
| 523 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 525 | 냉복도 습도 사용 센서 수 설정 (`VP_FWU_CZH_Count`) ≥ 10 이면 : |
| 526 | &emsp;→&nbsp;`SensorValue` ← 냉복도 습도 10번 값 (`VP_FWU_CZH-10`) 값 읽기 |
| 527 | &emsp;→&nbsp;`mCZHCount`에 1을(를) 더함 |
| 528 | &emsp;→&nbsp;`mCZHSum`에 `SensorValue`을(를) 더함 |
| 529 | &emsp;→&nbsp;`mCZHMax` ← [`mCZHMax`, `SensorValue`] 중 최댓값 |
| 530 | &emsp;→&nbsp;`mCZHMin` ← [`mCZHMin`, `SensorValue`] 중 최솟값 |
| 531 | 525행 조건이 성립하지 않으면 : |
| 532 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 534 | `mCZHCount` > 0 이면 : |
| 535 | &emsp;→&nbsp;냉복도 습도 평균 (`VP_FWU_CZH_Avg`)에 `mCZHSum` ÷ `mCZHCount` 기록 — 기본 우선순위(P5) |
| 536 | &emsp;→&nbsp;냉복도 습도 최대값 (`VP_FWU_CZH_Max`)에 `mCZHMax` 기록 — 기본 우선순위(P5) |
| 537 | &emsp;→&nbsp;냉복도 습도 최소값 (`VP_FWU_CZH_Min`)에 `mCZHMin` 기록 — 기본 우선순위(P5) |
| 538 | 534행 조건이 성립하지 않으면 : |
| 539 | &emsp;→&nbsp;냉복도 습도 평균 (`VP_FWU_CZH_Avg`)에 0 기록 — 기본 우선순위(P5) |
| 540 | &emsp;→&nbsp;냉복도 습도 최대값 (`VP_FWU_CZH_Max`)에 0 기록 — 기본 우선순위(P5) |
| 541 | &emsp;→&nbsp;냉복도 습도 최소값 (`VP_FWU_CZH_Min`)에 0 기록 — 기본 우선순위(P5) |
| 543 | *[주석] 팬 수는 F8 기준 고정. F4/F6는 팬별 입출력과 고장 집계를 함께 변경한다.* |
| 544 | *[주석] 풍량 계수·정격 RPM·운전 차압은 새 팬 제원으로 팬 개발팀 확인 필요.* |
| 545 | *[주석] FMS 1대로 개별 팬 풍량은 확인할 수 없다. QTS 수준은 팬별 감지 입력 추가 검토.* |
| 546 | *[주석] 공통 차압 대체 판정은 다른 팬이 만든 차압으로 정지 팬을 구분하지 못할 수 있다.* |

<a id="section-16"></a>

## 548~549행 · ΔT = RAT - SAT (SF Control의 ΔT 모드에서 쓴다)

| 행 | 해석 |
|---:|---|
| 548 | *[주석] ΔT = RAT - SAT (SF Control의 ΔT 모드에서 쓴다)* |
| 549 | ΔT(RAT-SAT) 현재값 (`VP_FWU_DeltaT_PV`)에 환기 온도(RAT) 센서값 (`FWU_RAT`) - 급기 온도(SAT) 센서값 (`FWU_SAT`) 기록 — 기본 우선순위(P5) |

<a id="section-17"></a>

## 551~639행 · 팬 운전 판단: 한 대라도 돌고 있으면 운전 중으로 본다

> 통신이 되는 팬은 RPM으로, 통신이 끊긴 팬은 급기 차압으로 판단한다

| 행 | 해석 |
|---:|---|
| 551 | *[주석] 팬 운전 판단: 한 대라도 돌고 있으면 운전 중으로 본다* |
| 552 | *[주석] 통신이 되는 팬은 RPM으로, 통신이 끊긴 팬은 급기 차압으로 판단한다* |
| 553 | `mbSF1CommFault` = TRUE(1) 이면 : |
| 554 | &emsp;→&nbsp;`mSAFlowDP` > `RUN_DP`(설정값) 이면 : |
| 555 | &emsp;&emsp;→&nbsp;`mbSFRun` ← TRUE(1) |
| 556 | &emsp;→&nbsp;554행 조건이 성립하지 않으면 : |
| 557 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 558 | 553행 조건이 성립하지 않으면 : |
| 559 | &emsp;→&nbsp;팬 1번 현재 RPM (`FWU_SF-1.Current_RPM`) ≥ `FAIL_RPM`(설정값) 이면 : |
| 560 | &emsp;&emsp;→&nbsp;`mbSFRun` ← TRUE(1) |
| 561 | &emsp;→&nbsp;559행 조건이 성립하지 않으면 : |
| 562 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 564 | `mbSF2CommFault` = TRUE(1) 이면 : |
| 565 | &emsp;→&nbsp;`mSAFlowDP` > `RUN_DP`(설정값) 이면 : |
| 566 | &emsp;&emsp;→&nbsp;`mbSFRun` ← TRUE(1) |
| 567 | &emsp;→&nbsp;565행 조건이 성립하지 않으면 : |
| 568 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 569 | 564행 조건이 성립하지 않으면 : |
| 570 | &emsp;→&nbsp;팬 2번 현재 RPM (`FWU_SF-2.Current_RPM`) ≥ `FAIL_RPM`(설정값) 이면 : |
| 571 | &emsp;&emsp;→&nbsp;`mbSFRun` ← TRUE(1) |
| 572 | &emsp;→&nbsp;570행 조건이 성립하지 않으면 : |
| 573 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 575 | `mbSF3CommFault` = TRUE(1) 이면 : |
| 576 | &emsp;→&nbsp;`mSAFlowDP` > `RUN_DP`(설정값) 이면 : |
| 577 | &emsp;&emsp;→&nbsp;`mbSFRun` ← TRUE(1) |
| 578 | &emsp;→&nbsp;576행 조건이 성립하지 않으면 : |
| 579 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 580 | 575행 조건이 성립하지 않으면 : |
| 581 | &emsp;→&nbsp;팬 3번 현재 RPM (`FWU_SF-3.Current_RPM`) ≥ `FAIL_RPM`(설정값) 이면 : |
| 582 | &emsp;&emsp;→&nbsp;`mbSFRun` ← TRUE(1) |
| 583 | &emsp;→&nbsp;581행 조건이 성립하지 않으면 : |
| 584 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 586 | `mbSF4CommFault` = TRUE(1) 이면 : |
| 587 | &emsp;→&nbsp;`mSAFlowDP` > `RUN_DP`(설정값) 이면 : |
| 588 | &emsp;&emsp;→&nbsp;`mbSFRun` ← TRUE(1) |
| 589 | &emsp;→&nbsp;587행 조건이 성립하지 않으면 : |
| 590 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 591 | 586행 조건이 성립하지 않으면 : |
| 592 | &emsp;→&nbsp;팬 4번 현재 RPM (`FWU_SF-4.Current_RPM`) ≥ `FAIL_RPM`(설정값) 이면 : |
| 593 | &emsp;&emsp;→&nbsp;`mbSFRun` ← TRUE(1) |
| 594 | &emsp;→&nbsp;592행 조건이 성립하지 않으면 : |
| 595 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 597 | `mbSF5CommFault` = TRUE(1) 이면 : |
| 598 | &emsp;→&nbsp;`mSAFlowDP` > `RUN_DP`(설정값) 이면 : |
| 599 | &emsp;&emsp;→&nbsp;`mbSFRun` ← TRUE(1) |
| 600 | &emsp;→&nbsp;598행 조건이 성립하지 않으면 : |
| 601 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 602 | 597행 조건이 성립하지 않으면 : |
| 603 | &emsp;→&nbsp;팬 5번 현재 RPM (`FWU_SF-5.Current_RPM`) ≥ `FAIL_RPM`(설정값) 이면 : |
| 604 | &emsp;&emsp;→&nbsp;`mbSFRun` ← TRUE(1) |
| 605 | &emsp;→&nbsp;603행 조건이 성립하지 않으면 : |
| 606 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 608 | `mbSF6CommFault` = TRUE(1) 이면 : |
| 609 | &emsp;→&nbsp;`mSAFlowDP` > `RUN_DP`(설정값) 이면 : |
| 610 | &emsp;&emsp;→&nbsp;`mbSFRun` ← TRUE(1) |
| 611 | &emsp;→&nbsp;609행 조건이 성립하지 않으면 : |
| 612 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 613 | 608행 조건이 성립하지 않으면 : |
| 614 | &emsp;→&nbsp;팬 6번 현재 RPM (`FWU_SF-6.Current_RPM`) ≥ `FAIL_RPM`(설정값) 이면 : |
| 615 | &emsp;&emsp;→&nbsp;`mbSFRun` ← TRUE(1) |
| 616 | &emsp;→&nbsp;614행 조건이 성립하지 않으면 : |
| 617 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 619 | `mbSF7CommFault` = TRUE(1) 이면 : |
| 620 | &emsp;→&nbsp;`mSAFlowDP` > `RUN_DP`(설정값) 이면 : |
| 621 | &emsp;&emsp;→&nbsp;`mbSFRun` ← TRUE(1) |
| 622 | &emsp;→&nbsp;620행 조건이 성립하지 않으면 : |
| 623 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 624 | 619행 조건이 성립하지 않으면 : |
| 625 | &emsp;→&nbsp;팬 7번 현재 RPM (`FWU_SF-7.Current_RPM`) ≥ `FAIL_RPM`(설정값) 이면 : |
| 626 | &emsp;&emsp;→&nbsp;`mbSFRun` ← TRUE(1) |
| 627 | &emsp;→&nbsp;625행 조건이 성립하지 않으면 : |
| 628 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 630 | `mbSF8CommFault` = TRUE(1) 이면 : |
| 631 | &emsp;→&nbsp;`mSAFlowDP` > `RUN_DP`(설정값) 이면 : |
| 632 | &emsp;&emsp;→&nbsp;`mbSFRun` ← TRUE(1) |
| 633 | &emsp;→&nbsp;631행 조건이 성립하지 않으면 : |
| 634 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 635 | 630행 조건이 성립하지 않으면 : |
| 636 | &emsp;→&nbsp;팬 8번 현재 RPM (`FWU_SF-8.Current_RPM`) ≥ `FAIL_RPM`(설정값) 이면 : |
| 637 | &emsp;&emsp;→&nbsp;`mbSFRun` ← TRUE(1) |
| 638 | &emsp;→&nbsp;636행 조건이 성립하지 않으면 : |
| 639 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |

<a id="section-18"></a>

## 641~649행 · 판단이 바뀐 채로 5초가 지나야 VP_FWU_SF_Status에 반영한다 (순간적인 흔들림 무시)

| 행 | 해석 |
|---:|---|
| 641 | *[주석] 판단이 바뀐 채로 5초가 지나야 VP_FWU_SF_Status에 반영한다 (순간적인 흔들림 무시)* |
| 642 | `mbSFRun` = 팬 운전 상태 (`VP_FWU_SF_Status`) 이면 : |
| 643 | &emsp;→&nbsp;타이머 `SF_STATUS_TIMER`(5번: 팬 운전 판단이 VP_FWU_SF_Status와 다르게 이어진 시간)를 0초로 초기화<br>*[주석] 판단이 지금 상태와 같으면 시간을 다시 잰다* |
| 644 | 642행 조건이 성립하지 않으면 : |
| 645 | &emsp;→&nbsp;타이머 `SF_STATUS_TIMER`(5번: 팬 운전 판단이 VP_FWU_SF_Status와 다르게 이어진 시간) 경과시간 > 5 이면 :<br>*[주석] 5초* |
| 646 | &emsp;&emsp;→&nbsp;팬 운전 상태 (`VP_FWU_SF_Status`)에 `mbSFRun` 기록 — 기본 우선순위(P5) |
| 647 | &emsp;&emsp;→&nbsp;타이머 `SF_STATUS_TIMER`(5번: 팬 운전 판단이 VP_FWU_SF_Status와 다르게 이어진 시간)를 0초로 초기화 |
| 648 | &emsp;→&nbsp;645행 조건이 성립하지 않으면 : |
| 649 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |

<a id="section-19"></a>

## 651~658행 · 급기 풍량 계산: 팬이 돌고 차압이 5Pa 이상일 때만 계산한다

> 차압은 위에서 읽어 둔 mSAFlowDP를 쓴다 (FWU_SAFLOW_DP를 다시 읽는 것과 같은 값) VP_FWU_SAF_VA-2(기본값 9)가 어떤 값인지는 아직 확인하지 못했다

| 행 | 해석 |
|---:|---|
| 651 | *[주석] 급기 풍량 계산: 팬이 돌고 차압이 5Pa 이상일 때만 계산한다* |
| 652 | *[주석] 차압은 위에서 읽어 둔 mSAFlowDP를 쓴다 (FWU_SAFLOW_DP를 다시 읽는 것과 같은 값)* |
| 653 | *[주석] VP_FWU_SAF_VA-2(기본값 9)가 어떤 값인지는 아직 확인하지 못했다* |
| 654 | 팬 운전 상태 (`VP_FWU_SF_Status`) = ON(1) **그리고** `mSAFlowDP` ≥ 5 이면 : |
| 655 | &emsp;→&nbsp;`SAFlow` ← (급기 풍량 계수 (`VP_FWU_SA_Flow_Coef`) × (√(`mSAFlowDP`))) × 급기 풍량 계수 VA-2 (`VP_FWU_SAF_VA-2`) |
| 656 | &emsp;→&nbsp;급기 풍량 계산값 (`VP_FWU_SA_Flow`)에 `SAFlow` 기록 — 기본 우선순위(P5) |
| 657 | 654행 조건이 성립하지 않으면 : |
| 658 | &emsp;→&nbsp;급기 풍량 계산값 (`VP_FWU_SA_Flow`)에 0 기록 — 기본 우선순위(P5) |

<a id="section-20"></a>

## 660~668행 · 운전 명령 맞추기: 원격(BMS) 선택이면 BMS 명령을 HMI 쪽에, 로컬이면 HMI 명령을 BMS 쪽에 따라 쓴다

| 행 | 해석 |
|---:|---|
| 660 | *[주석] 운전 명령 맞추기: 원격(BMS) 선택이면 BMS 명령을 HMI 쪽에, 로컬이면 HMI 명령을 BMS 쪽에 따라 쓴다* |
| 661 | 원격(BMS) 선택 입력(DI) (`REMOTE_SELECTION`) = TRUE(1) 이면 : |
| 662 | &emsp;→&nbsp;운전 명령(BMS) (`VP_FWU_Command`)의 P5 쓰기 해제 |
| 663 | &emsp;→&nbsp;운전 명령(HMI) (`VP_FWU_Command_HMI`)에 운전 명령(BMS) (`VP_FWU_Command`) 값을 그대로 복사 — 기본 우선순위(P5) |
| 664 | &emsp;→&nbsp;운전 명령(HMI) (`VP_FWU_Command_HMI`)에 운전 명령(BMS) (`VP_FWU_Command`) 값을 그대로 기록 — 우선순위 P11 |
| 665 | 661행 조건이 성립하지 않으면 : |
| 666 | &emsp;→&nbsp;운전 명령(HMI) (`VP_FWU_Command_HMI`)의 P5 쓰기 해제 |
| 667 | &emsp;→&nbsp;운전 명령(BMS) (`VP_FWU_Command`)에 운전 명령(HMI) (`VP_FWU_Command_HMI`) 값을 그대로 복사 — 기본 우선순위(P5) |
| 668 | &emsp;→&nbsp;운전 명령(BMS) (`VP_FWU_Command`)에 운전 명령(HMI) (`VP_FWU_Command_HMI`) 값을 그대로 기록 — 우선순위 P11 |

<a id="section-21"></a>

## 670~674행 · 팬 최대 RPM = 설계 RPM × 비율(%). 단 정격 최대 RPM은 넘지 않게 한다 (SF Control이 이 값을 쓴다)

| 행 | 해석 |
|---:|---|
| 670 | *[주석] 팬 최대 RPM = 설계 RPM × 비율(%). 단 정격 최대 RPM은 넘지 않게 한다 (SF Control이 이 값을 쓴다)* |
| 671 | 팬 최대 RPM(계산값) (`VP_FWU_SF_Max_RPM`)에 [(팬 설계 RPM (`VP_FWU_SF_Design_RPM`) × 팬 최대 RPM 비율(%) (`VP_FWU_SF_Max_RPM_Ratio`)) ÷ 100, 팬 정격 최대 RPM (`VP_FWU_SF_Rated_Max_RPM`)] 중 최솟값 기록 — 기본 우선순위(P5) |
| 673 | *[주석] JSY 2026-11-23 수정 구간 끝. 주제 = Coding Rule 적용(매크로 상수, 설정값 상수, 변수명, if-else 짝 맞춤, 주석)* |
| 674 | *[주석] LJH 2026-11-17 수정 구간 끝. 주제 = 상위 감시와 외부 센서 집계* |
