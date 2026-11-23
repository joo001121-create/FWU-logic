# Fan Damper Alarm 줄별 해석

> **대상 코드** : `fwu_v3/Logic/Fan Damper Alarm.py` (179 줄)  
> **기준** : `sy 브랜치 2026-11-23 (naming rule·관제점 이름 변경 반영)`  
> **행** = 코드 줄 번호 (빈 줄은 생략)  
> **표기** : `→` 들여쓰기 단계 · *[주석]* 코드 안 주석 · `이름` 코드 안 상수·변수 · **※** 읽을 때 주의할 점

팬 8대의 운전 고장과 종합 팬 고장, 댐퍼 보호 알람(일부 닫힘·전폐·미개방·미폐쇄)을 판단한다. 기존 Alarm-1에서 떼어 만든 파일이다.

**목차**

- [1~22행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수](#section-1)
- [24~133행 · 팬 운전 고장: 운전 명령이 있고 속도가 최소 이상인데 60초가 지나도 안 돌면 고장](#section-2)
- [135~142행 · 댐퍼 일부 닫힘: 팬이 도는데 네 댐퍼 중 일부만 닫혀 있음](#section-3)
- [144~148행 · 댐퍼 전폐: 열림 명령인데 네 댐퍼가 모두 닫혀 있음. 팬이 서도 한 번 걸린 알람은 닫힘이 풀릴 때까지 유지](#section-4)
- [150~162행 · 댐퍼 미개방: 열림 명령을 내고 팬이 아직 안 돌 때, 120초가 지나도 네 댐퍼가 다 안 열리면 알람](#section-5)
- [164~179행 · 댐퍼 미폐쇄: 닫힘 명령 뒤 120초가 지나도 네 댐퍼가 다 안 닫히면 알람](#section-6)

**※ 공통 표기**: 매크로 상수 TRUE·ON·SET·TMR_READ·DEC = 1, FALSE·OFF·CLEAR·TMR_CLEAR·INC = 0. `SECTIMER(타이머, TMR_CLEAR)`는 타이머를 0초로 초기화, `SECTIMER(타이머, TMR_READ)`는 경과시간 확인이다. P번호가 없는 쓰기(`WRITEPOINT`)는 기본 우선순위 P5를 쓴다. 조건이 거짓이라고 관제점이 저절로 0이 되지는 않는다. 해당 분기에 쓰기가 없으면 이전 값이 남는다. 대문자 이름은 상수, `m`으로 시작하는 이름은 이 파일의 전역변수, `b`가 붙은 이름은 참/거짓 값이다.

<a id="section-1"></a>

## 1~22행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수

| 행 | 해석 |
|---:|---|
| 1 | *[주석] JSY 2026-11-23 수정 구간 시작. 주제 = Alarm-1에서 팬 운전 고장 알람과 댐퍼 보호 알람을 떼어 만듦, Coding Rule 적용* |
| 3 | *[주석] 로직엔진 loading* |
| 4 | DDC 로직 엔진 객체 생성 (이후 engine.xxx로 관제점을 읽고 씀) |
| 6 | *[주석] Macro상수 정의* |
| 7 | 매크로 상수 정의: TMR_READ, SET, ON, TRUE, DEC = 1 (긍정의 의미 또는 1인 인자) |
| 8 | 매크로 상수 정의: TMR_CLEAR, CLEAR, OFF, FALSE, INC = 0 (부정의 의미 또는 0인 인자) |
| 9 | 상수 `FAN_COUNT` = 8<br>*[주석] 팬 대수 (F8 모델 기준)* |
| 10 | 상수 `FAN_FAIL_CONFIRM_SECONDS` = 60<br>*[주석] 운전 명령 후 60초가 지나야 팬 고장을 본다* |
| 11 | 상수 `DAMPER_TRAVEL_SECONDS` = 120<br>*[주석] 댐퍼가 끝까지 움직이는 데 주는 시간* |
| 12 | 설정값 상수 `FAIL_RPM`: 팬 운전 판단 RPM 설정 (`VP_FWU_SF_Failure_RPM_Set`) 값을 읽어 둠<br>*[주석] 팬 RPM이 이 값보다 낮으면 고장 후보로 봄* |
| 13 | *[주석] F4/F6는 개별 팬 판정과 입출력을 함께 변경. Count VP로 모델을 전환하지 않는다.* |
| 15 | *[주석] 타이머 정의 (번호는 Alarm-1에서 쓰던 그대로)* |
| 16 | 타이머 번호 상수 `FAN_FAIL_TIMER` = 1번<br>*[주석] 운전 명령이 들어간 뒤 지난 시간 (팬 고장 판단 시작 지연)* |
| 17 | 타이머 번호 상수 `SAD_OPEN_TIMER` = 7번<br>*[주석] 댐퍼 열림 명령 뒤 지난 시간* |
| 18 | 타이머 번호 상수 `SAD_CLOSE_TIMER` = 8번<br>*[주석] 댐퍼 닫힘 명령 뒤 지난 시간* |
| 20 | *[주석] 전역변수 선언: 댐퍼 닫힘 접점 상태* |
| 21 | 전역변수 `mbSADAllClose` ← 댐퍼 1번 닫힘 접점 (`FWU_SAD-1_CLOSE_STATUS`) = TRUE(1) **그리고** 댐퍼 2번 닫힘 접점 (`FWU_SAD-2_CLOSE_STATUS`) = TRUE(1) **그리고** 댐퍼 3번 닫힘 접점 (`FWU_SAD-3_CLOSE_STATUS`) = TRUE(1) **그리고** 댐퍼 4번 닫힘 접점 (`FWU_SAD-4_CLOSE_STATUS`) = TRUE(1) 이면 TRUE, 아니면 FALSE<br>*[주석] 네 댐퍼가 모두 닫힘* |
| 22 | 전역변수 `mbSADAnyClose` ← 댐퍼 1번 닫힘 접점 (`FWU_SAD-1_CLOSE_STATUS`) = TRUE(1) **또는** 댐퍼 2번 닫힘 접점 (`FWU_SAD-2_CLOSE_STATUS`) = TRUE(1) **또는** 댐퍼 3번 닫힘 접점 (`FWU_SAD-3_CLOSE_STATUS`) = TRUE(1) **또는** 댐퍼 4번 닫힘 접점 (`FWU_SAD-4_CLOSE_STATUS`) = TRUE(1) 이면 TRUE, 아니면 FALSE<br>*[주석] 하나라도 닫힘* |

<a id="section-2"></a>

## 24~133행 · 팬 운전 고장: 운전 명령이 있고 속도가 최소 이상인데 60초가 지나도 안 돌면 고장

| 행 | 해석 |
|---:|---|
| 24 | *[주석] 팬 운전 고장: 운전 명령이 있고 속도가 최소 이상인데 60초가 지나도 안 돌면 고장* |
| 25 | 운전 명령(BMS) (`VP_FWU_Command`) = ON(1) **그리고** 팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`) ≥ 팬 최소 속도(%) (`VP_FWU_SF_Speed_Min`) 이면 : |
| 26 | &emsp;→&nbsp;타이머 `FAN_FAIL_TIMER`(1번: 운전 명령이 들어간 뒤 지난 시간 (팬 고장 판단 시작 지연)) 경과시간 > `FAN_FAIL_CONFIRM_SECONDS`(60) 이면 : |
| 27 | &emsp;&emsp;→&nbsp;`bSFDPLow` ← 급기 풍량 차압(FMS) (`FWU_SAFLOW_DP`) ≤ 팬 운전 판단 차압 설정 (`VP_FWU_SF_Run_DP_Set`) 이면 TRUE, 아니면 FALSE<br>*[주석] 급기 차압이 운전 기준 이하* |
| 29 | &emsp;&emsp;→&nbsp;*[주석] 통신이 되는 팬은 RPM으로, 통신이 끊긴 팬은 급기 차압으로 판단한다* |
| 30 | &emsp;&emsp;→&nbsp;팬 1번 통신 이상 (`VP_FWU_SF-1_Comm_Fault`) = FALSE(0) 이면 : |
| 31 | &emsp;&emsp;&emsp;→&nbsp;`bSF1Fail` ← 팬 1번 현재 RPM (`FWU_SF-1.Current_RPM`) < `FAIL_RPM`(설정값) 이면 TRUE, 아니면 FALSE |
| 32 | &emsp;&emsp;→&nbsp;30행 조건이 성립하지 않으면 : |
| 33 | &emsp;&emsp;&emsp;→&nbsp;`bSF1Fail` ← `bSFDPLow` |
| 35 | &emsp;&emsp;→&nbsp;팬 2번 통신 이상 (`VP_FWU_SF-2_Comm_Fault`) = FALSE(0) 이면 : |
| 36 | &emsp;&emsp;&emsp;→&nbsp;`bSF2Fail` ← 팬 2번 현재 RPM (`FWU_SF-2.Current_RPM`) < `FAIL_RPM`(설정값) 이면 TRUE, 아니면 FALSE |
| 37 | &emsp;&emsp;→&nbsp;35행 조건이 성립하지 않으면 : |
| 38 | &emsp;&emsp;&emsp;→&nbsp;`bSF2Fail` ← `bSFDPLow` |
| 40 | &emsp;&emsp;→&nbsp;팬 3번 통신 이상 (`VP_FWU_SF-3_Comm_Fault`) = FALSE(0) 이면 : |
| 41 | &emsp;&emsp;&emsp;→&nbsp;`bSF3Fail` ← 팬 3번 현재 RPM (`FWU_SF-3.Current_RPM`) < `FAIL_RPM`(설정값) 이면 TRUE, 아니면 FALSE |
| 42 | &emsp;&emsp;→&nbsp;40행 조건이 성립하지 않으면 : |
| 43 | &emsp;&emsp;&emsp;→&nbsp;`bSF3Fail` ← `bSFDPLow` |
| 45 | &emsp;&emsp;→&nbsp;팬 4번 통신 이상 (`VP_FWU_SF-4_Comm_Fault`) = FALSE(0) 이면 : |
| 46 | &emsp;&emsp;&emsp;→&nbsp;`bSF4Fail` ← 팬 4번 현재 RPM (`FWU_SF-4.Current_RPM`) < `FAIL_RPM`(설정값) 이면 TRUE, 아니면 FALSE |
| 47 | &emsp;&emsp;→&nbsp;45행 조건이 성립하지 않으면 : |
| 48 | &emsp;&emsp;&emsp;→&nbsp;`bSF4Fail` ← `bSFDPLow` |
| 50 | &emsp;&emsp;→&nbsp;팬 5번 통신 이상 (`VP_FWU_SF-5_Comm_Fault`) = FALSE(0) 이면 : |
| 51 | &emsp;&emsp;&emsp;→&nbsp;`bSF5Fail` ← 팬 5번 현재 RPM (`FWU_SF-5.Current_RPM`) < `FAIL_RPM`(설정값) 이면 TRUE, 아니면 FALSE |
| 52 | &emsp;&emsp;→&nbsp;50행 조건이 성립하지 않으면 : |
| 53 | &emsp;&emsp;&emsp;→&nbsp;`bSF5Fail` ← `bSFDPLow` |
| 55 | &emsp;&emsp;→&nbsp;팬 6번 통신 이상 (`VP_FWU_SF-6_Comm_Fault`) = FALSE(0) 이면 : |
| 56 | &emsp;&emsp;&emsp;→&nbsp;`bSF6Fail` ← 팬 6번 현재 RPM (`FWU_SF-6.Current_RPM`) < `FAIL_RPM`(설정값) 이면 TRUE, 아니면 FALSE |
| 57 | &emsp;&emsp;→&nbsp;55행 조건이 성립하지 않으면 : |
| 58 | &emsp;&emsp;&emsp;→&nbsp;`bSF6Fail` ← `bSFDPLow` |
| 60 | &emsp;&emsp;→&nbsp;팬 7번 통신 이상 (`VP_FWU_SF-7_Comm_Fault`) = FALSE(0) 이면 : |
| 61 | &emsp;&emsp;&emsp;→&nbsp;`bSF7Fail` ← 팬 7번 현재 RPM (`FWU_SF-7.Current_RPM`) < `FAIL_RPM`(설정값) 이면 TRUE, 아니면 FALSE |
| 62 | &emsp;&emsp;→&nbsp;60행 조건이 성립하지 않으면 : |
| 63 | &emsp;&emsp;&emsp;→&nbsp;`bSF7Fail` ← `bSFDPLow` |
| 65 | &emsp;&emsp;→&nbsp;팬 8번 통신 이상 (`VP_FWU_SF-8_Comm_Fault`) = FALSE(0) 이면 : |
| 66 | &emsp;&emsp;&emsp;→&nbsp;`bSF8Fail` ← 팬 8번 현재 RPM (`FWU_SF-8.Current_RPM`) < `FAIL_RPM`(설정값) 이면 TRUE, 아니면 FALSE |
| 67 | &emsp;&emsp;→&nbsp;65행 조건이 성립하지 않으면 : |
| 68 | &emsp;&emsp;&emsp;→&nbsp;`bSF8Fail` ← `bSFDPLow` |
| 70 | &emsp;&emsp;→&nbsp;*[주석] 팬별 알람을 내고 고장 대수를 센다* |
| 71 | &emsp;&emsp;→&nbsp;`SFFailCount` ← 0 |
| 72 | &emsp;&emsp;→&nbsp;`bSF1Fail` = TRUE(1) 이면 : |
| 73 | &emsp;&emsp;&emsp;→&nbsp;`SFFailCount`에 1을(를) 더함 |
| 74 | &emsp;&emsp;&emsp;→&nbsp;팬 1번 운전 고장 알람 (`VP_FWU_SF-1_Run_Fail_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 75 | &emsp;&emsp;→&nbsp;72행 조건이 성립하지 않으면 : |
| 76 | &emsp;&emsp;&emsp;→&nbsp;팬 1번 운전 고장 알람 (`VP_FWU_SF-1_Run_Fail_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 77 | &emsp;&emsp;→&nbsp;`bSF2Fail` = TRUE(1) 이면 : |
| 78 | &emsp;&emsp;&emsp;→&nbsp;`SFFailCount`에 1을(를) 더함 |
| 79 | &emsp;&emsp;&emsp;→&nbsp;팬 2번 운전 고장 알람 (`VP_FWU_SF-2_Run_Fail_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 80 | &emsp;&emsp;→&nbsp;77행 조건이 성립하지 않으면 : |
| 81 | &emsp;&emsp;&emsp;→&nbsp;팬 2번 운전 고장 알람 (`VP_FWU_SF-2_Run_Fail_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 82 | &emsp;&emsp;→&nbsp;`bSF3Fail` = TRUE(1) 이면 : |
| 83 | &emsp;&emsp;&emsp;→&nbsp;`SFFailCount`에 1을(를) 더함 |
| 84 | &emsp;&emsp;&emsp;→&nbsp;팬 3번 운전 고장 알람 (`VP_FWU_SF-3_Run_Fail_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 85 | &emsp;&emsp;→&nbsp;82행 조건이 성립하지 않으면 : |
| 86 | &emsp;&emsp;&emsp;→&nbsp;팬 3번 운전 고장 알람 (`VP_FWU_SF-3_Run_Fail_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 87 | &emsp;&emsp;→&nbsp;`bSF4Fail` = TRUE(1) 이면 : |
| 88 | &emsp;&emsp;&emsp;→&nbsp;`SFFailCount`에 1을(를) 더함 |
| 89 | &emsp;&emsp;&emsp;→&nbsp;팬 4번 운전 고장 알람 (`VP_FWU_SF-4_Run_Fail_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 90 | &emsp;&emsp;→&nbsp;87행 조건이 성립하지 않으면 : |
| 91 | &emsp;&emsp;&emsp;→&nbsp;팬 4번 운전 고장 알람 (`VP_FWU_SF-4_Run_Fail_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 92 | &emsp;&emsp;→&nbsp;`bSF5Fail` = TRUE(1) 이면 : |
| 93 | &emsp;&emsp;&emsp;→&nbsp;`SFFailCount`에 1을(를) 더함 |
| 94 | &emsp;&emsp;&emsp;→&nbsp;팬 5번 운전 고장 알람 (`VP_FWU_SF-5_Run_Fail_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 95 | &emsp;&emsp;→&nbsp;92행 조건이 성립하지 않으면 : |
| 96 | &emsp;&emsp;&emsp;→&nbsp;팬 5번 운전 고장 알람 (`VP_FWU_SF-5_Run_Fail_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 97 | &emsp;&emsp;→&nbsp;`bSF6Fail` = TRUE(1) 이면 : |
| 98 | &emsp;&emsp;&emsp;→&nbsp;`SFFailCount`에 1을(를) 더함 |
| 99 | &emsp;&emsp;&emsp;→&nbsp;팬 6번 운전 고장 알람 (`VP_FWU_SF-6_Run_Fail_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 100 | &emsp;&emsp;→&nbsp;97행 조건이 성립하지 않으면 : |
| 101 | &emsp;&emsp;&emsp;→&nbsp;팬 6번 운전 고장 알람 (`VP_FWU_SF-6_Run_Fail_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 102 | &emsp;&emsp;→&nbsp;`bSF7Fail` = TRUE(1) 이면 : |
| 103 | &emsp;&emsp;&emsp;→&nbsp;`SFFailCount`에 1을(를) 더함 |
| 104 | &emsp;&emsp;&emsp;→&nbsp;팬 7번 운전 고장 알람 (`VP_FWU_SF-7_Run_Fail_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 105 | &emsp;&emsp;→&nbsp;102행 조건이 성립하지 않으면 : |
| 106 | &emsp;&emsp;&emsp;→&nbsp;팬 7번 운전 고장 알람 (`VP_FWU_SF-7_Run_Fail_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 107 | &emsp;&emsp;→&nbsp;`bSF8Fail` = TRUE(1) 이면 : |
| 108 | &emsp;&emsp;&emsp;→&nbsp;`SFFailCount`에 1을(를) 더함 |
| 109 | &emsp;&emsp;&emsp;→&nbsp;팬 8번 운전 고장 알람 (`VP_FWU_SF-8_Run_Fail_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 110 | &emsp;&emsp;→&nbsp;107행 조건이 성립하지 않으면 : |
| 111 | &emsp;&emsp;&emsp;→&nbsp;팬 8번 운전 고장 알람 (`VP_FWU_SF-8_Run_Fail_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 113 | &emsp;&emsp;→&nbsp;*[주석] 종합 팬 고장 기준은 SMX01의 절반 이상 고장을 임시로 유지한다.* |
| 114 | &emsp;&emsp;→&nbsp;*[주석] 신규 팬의 정압-풍량 곡선과 허용 최대속도를 기준으로, 팬 고장 시에도* |
| 115 | &emsp;&emsp;→&nbsp;*[주석] 요구 정압에서 목표 풍량을 확보할 수 있는 고장 허용 대수를 확인할 것.* |
| 116 | &emsp;&emsp;→&nbsp;*[주석] 확인 결과에 맞춰 아래 종합 고장 대수 기준과 Failover 정지 연계를 재검토한다.* |
| 117 | &emsp;&emsp;→&nbsp;`SFFailCount` × 2 ≥ `FAN_COUNT`(8) 이면 :<br>*[주석] 절반 이상 고장이면 종합 알람 (팬·모델이 바뀌면 기준을 다시 정해야 할 수 있음)* |
| 118 | &emsp;&emsp;&emsp;→&nbsp;팬 종합 고장 알람 (`VP_FWU_SF_Failure_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 119 | &emsp;&emsp;→&nbsp;117행 조건이 성립하지 않으면 : |
| 120 | &emsp;&emsp;&emsp;→&nbsp;팬 종합 고장 알람 (`VP_FWU_SF_Failure_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 121 | &emsp;→&nbsp;26행 조건이 성립하지 않으면 : |
| 122 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 123 | 25행 조건이 성립하지 않으면 : |
| 124 | &emsp;→&nbsp;타이머 `FAN_FAIL_TIMER`(1번: 운전 명령이 들어간 뒤 지난 시간 (팬 고장 판단 시작 지연))를 0초로 초기화 |
| 125 | &emsp;→&nbsp;팬 종합 고장 알람 (`VP_FWU_SF_Failure_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 126 | &emsp;→&nbsp;팬 1번 운전 고장 알람 (`VP_FWU_SF-1_Run_Fail_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 127 | &emsp;→&nbsp;팬 2번 운전 고장 알람 (`VP_FWU_SF-2_Run_Fail_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 128 | &emsp;→&nbsp;팬 3번 운전 고장 알람 (`VP_FWU_SF-3_Run_Fail_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 129 | &emsp;→&nbsp;팬 4번 운전 고장 알람 (`VP_FWU_SF-4_Run_Fail_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 130 | &emsp;→&nbsp;팬 5번 운전 고장 알람 (`VP_FWU_SF-5_Run_Fail_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 131 | &emsp;→&nbsp;팬 6번 운전 고장 알람 (`VP_FWU_SF-6_Run_Fail_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 132 | &emsp;→&nbsp;팬 7번 운전 고장 알람 (`VP_FWU_SF-7_Run_Fail_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 133 | &emsp;→&nbsp;팬 8번 운전 고장 알람 (`VP_FWU_SF-8_Run_Fail_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |

<a id="section-3"></a>

## 135~142행 · 댐퍼 일부 닫힘: 팬이 도는데 네 댐퍼 중 일부만 닫혀 있음

| 행 | 해석 |
|---:|---|
| 135 | *[주석] 댐퍼 일부 닫힘: 팬이 도는데 네 댐퍼 중 일부만 닫혀 있음* |
| 136 | 팬 운전 상태 (`VP_FWU_SF_Status`) = ON(1) 이면 : |
| 137 | &emsp;→&nbsp;`mbSADAnyClose` = TRUE(1) **그리고** `mbSADAllClose` = FALSE(0) 이면 : |
| 138 | &emsp;&emsp;→&nbsp;댐퍼 일부 닫힘 알람 (`VP_FWU_SAD_Partial_Close_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 139 | &emsp;→&nbsp;137행 조건이 성립하지 않으면 : |
| 140 | &emsp;&emsp;→&nbsp;댐퍼 일부 닫힘 알람 (`VP_FWU_SAD_Partial_Close_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 141 | 136행 조건이 성립하지 않으면 : |
| 142 | &emsp;→&nbsp;댐퍼 일부 닫힘 알람 (`VP_FWU_SAD_Partial_Close_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |

<a id="section-4"></a>

## 144~148행 · 댐퍼 전폐: 열림 명령인데 네 댐퍼가 모두 닫혀 있음. 팬이 서도 한 번 걸린 알람은 닫힘이 풀릴 때까지 유지

| 행 | 해석 |
|---:|---|
| 144 | *[주석] 댐퍼 전폐: 열림 명령인데 네 댐퍼가 모두 닫혀 있음. 팬이 서도 한 번 걸린 알람은 닫힘이 풀릴 때까지 유지* |
| 145 | `mbSADAllClose` = TRUE(1) **그리고** 댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`) = ON(1) **그리고** (팬 운전 상태 (`VP_FWU_SF_Status`) = ON(1) **또는** 댐퍼 전폐 알람 (`VP_FWU_SAD_Full_Close_Alarm`) = TRUE(1)) 이면 : |
| 146 | &emsp;→&nbsp;댐퍼 전폐 알람 (`VP_FWU_SAD_Full_Close_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 147 | 145행 조건이 성립하지 않으면 : |
| 148 | &emsp;→&nbsp;댐퍼 전폐 알람 (`VP_FWU_SAD_Full_Close_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |

<a id="section-5"></a>

## 150~162행 · 댐퍼 미개방: 열림 명령을 내고 팬이 아직 안 돌 때, 120초가 지나도 네 댐퍼가 다 안 열리면 알람

| 행 | 해석 |
|---:|---|
| 150 | *[주석] 댐퍼 미개방: 열림 명령을 내고 팬이 아직 안 돌 때, 120초가 지나도 네 댐퍼가 다 안 열리면 알람* |
| 151 | 댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`) = ON(1) **그리고** 팬 운전 상태 (`VP_FWU_SF_Status`) = OFF(0) 이면 : |
| 152 | &emsp;→&nbsp;타이머 `SAD_CLOSE_TIMER`(8번: 댐퍼 닫힘 명령 뒤 지난 시간)를 0초로 초기화 |
| 153 | &emsp;→&nbsp;타이머 `SAD_OPEN_TIMER`(7번: 댐퍼 열림 명령 뒤 지난 시간) 경과시간 > `DAMPER_TRAVEL_SECONDS`(120) 이면 : |
| 154 | &emsp;&emsp;→&nbsp;댐퍼 1번 열림 접점 (`FWU_SAD-1_OPEN_STATUS`) ≠ TRUE(1) **또는** 댐퍼 2번 열림 접점 (`FWU_SAD-2_OPEN_STATUS`) ≠ TRUE(1) **또는** 댐퍼 3번 열림 접점 (`FWU_SAD-3_OPEN_STATUS`) ≠ TRUE(1) **또는** 댐퍼 4번 열림 접점 (`FWU_SAD-4_OPEN_STATUS`) ≠ TRUE(1) 이면 : |
| 155 | &emsp;&emsp;&emsp;→&nbsp;댐퍼 미개방 알람 (`VP_FWU_SAD_Not_Open_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 156 | &emsp;&emsp;→&nbsp;154행 조건이 성립하지 않으면 : |
| 157 | &emsp;&emsp;&emsp;→&nbsp;댐퍼 미개방 알람 (`VP_FWU_SAD_Not_Open_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 158 | &emsp;→&nbsp;153행 조건이 성립하지 않으면 : |
| 159 | &emsp;&emsp;→&nbsp;댐퍼 미개방 알람 (`VP_FWU_SAD_Not_Open_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 160 | 151행 조건이 성립하지 않으면 : |
| 161 | &emsp;→&nbsp;댐퍼 미개방 알람 (`VP_FWU_SAD_Not_Open_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 162 | &emsp;→&nbsp;타이머 `SAD_OPEN_TIMER`(7번: 댐퍼 열림 명령 뒤 지난 시간)를 0초로 초기화 |

<a id="section-6"></a>

## 164~179행 · 댐퍼 미폐쇄: 닫힘 명령 뒤 120초가 지나도 네 댐퍼가 다 안 닫히면 알람

| 행 | 해석 |
|---:|---|
| 164 | *[주석] 댐퍼 미폐쇄: 닫힘 명령 뒤 120초가 지나도 네 댐퍼가 다 안 닫히면 알람* |
| 165 | 댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`) = OFF(0) 이면 : |
| 166 | &emsp;→&nbsp;타이머 `SAD_OPEN_TIMER`(7번: 댐퍼 열림 명령 뒤 지난 시간)를 0초로 초기화 |
| 167 | &emsp;→&nbsp;타이머 `SAD_CLOSE_TIMER`(8번: 댐퍼 닫힘 명령 뒤 지난 시간) 경과시간 > `DAMPER_TRAVEL_SECONDS`(120) 이면 : |
| 168 | &emsp;&emsp;→&nbsp;댐퍼 1번 닫힘 접점 (`FWU_SAD-1_CLOSE_STATUS`) ≠ TRUE(1) **또는** 댐퍼 2번 닫힘 접점 (`FWU_SAD-2_CLOSE_STATUS`) ≠ TRUE(1) **또는** 댐퍼 3번 닫힘 접점 (`FWU_SAD-3_CLOSE_STATUS`) ≠ TRUE(1) **또는** 댐퍼 4번 닫힘 접점 (`FWU_SAD-4_CLOSE_STATUS`) ≠ TRUE(1) 이면 : |
| 169 | &emsp;&emsp;&emsp;→&nbsp;댐퍼 미폐쇄 알람 (`VP_FWU_SAD_Not_Close_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 170 | &emsp;&emsp;→&nbsp;168행 조건이 성립하지 않으면 : |
| 171 | &emsp;&emsp;&emsp;→&nbsp;댐퍼 미폐쇄 알람 (`VP_FWU_SAD_Not_Close_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 172 | &emsp;→&nbsp;167행 조건이 성립하지 않으면 : |
| 173 | &emsp;&emsp;→&nbsp;댐퍼 미폐쇄 알람 (`VP_FWU_SAD_Not_Close_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 174 | 165행 조건이 성립하지 않으면 : |
| 175 | &emsp;→&nbsp;댐퍼 미폐쇄 알람 (`VP_FWU_SAD_Not_Close_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 176 | &emsp;→&nbsp;타이머 `SAD_CLOSE_TIMER`(8번: 댐퍼 닫힘 명령 뒤 지난 시간)를 0초로 초기화 |
| 178 | *[주석] JSY 2026-11-23 수정 구간 끝. 주제 = Alarm-1에서 팬 운전 고장 알람과 댐퍼 보호 알람을 떼어 만듦, Coding Rule 적용* |
| 179 | *[주석] LJH 2026-11-17 수정 표시. 주제 = 내부 센서 유효성 및 팬·댐퍼 알람* |
