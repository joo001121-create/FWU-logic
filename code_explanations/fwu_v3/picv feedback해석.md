# PICV Feedback 줄별 해석

> **대상 코드** : `fwu_v3/Logic/PICV Feedback.py` (320 줄, refac 예제 원본)  
> **기준** : `sy 브랜치 2026-11-23 (naming rule·관제점 이름 변경 반영)`  
> **행** = 코드 줄 번호 (빈 줄은 생략)  
> **표기** : `→` 들여쓰기 단계 · *[주석]* 코드 안 주석 · `이름` 코드 안 상수·변수 · **※** 읽을 때 주의할 점

PICV 4대의 개도·유량·온도 수신값을 확인하고, 닫힘 여부·명령-개도 차이·유량 이상을 판단해 밸브별 알람과 종합 상태를 낸다. refac 예제 원본 파일이다.

**※** 이 파일(refac 예제 원본)은 탭과 스페이스가 섞여 있어 Python에서 TabError가 난다. 원본을 그대로 두었으며, 아래 들여쓰기 단계는 탭을 4칸으로 보고 표시했다.

**목차**

- [1~33행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수](#section-1)
- [35~51행 · PICV1(1/2): valid check(개도, 유량, 온도에서 alarm 없음)](#section-2)
- [53~102행 · PICV1(2/2): 개도 및 유량 범위 확인](#section-3)
- [104~120행 · PICV2(1/2): valid check(개도, 유량, 온도에서 alarm 없음)](#section-4)
- [122~171행 · PICV2(2/2): 개도 및 유량 범위 확인](#section-5)
- [173~189행 · PICV3(1/2): valid check(개도, 유량, 온도에서 alarm 없음)](#section-6)
- [191~238행 · PICV3(2/2): 개도 및 유량 범위 확인](#section-7)
- [240~256행 · PICV4(1/2): valid check(개도, 유량, 온도에서 alarm 없음)](#section-8)
- [258~307행 · PICV4(2/2): 개도 및 유량 범위 확인](#section-9)
- [309~313행 · 모니터링 flag setting](#section-10)
- [315~320행 · PICV 상태, 유량 등의 정보를 VP_...에 업데이트](#section-11)

**※ 공통 표기**: 매크로 상수 TRUE·ON·SET·TMR_READ·DEC = 1, FALSE·OFF·CLEAR·TMR_CLEAR·INC = 0. `SECTIMER(타이머, TMR_CLEAR)`는 타이머를 0초로 초기화, `SECTIMER(타이머, TMR_READ)`는 경과시간 확인이다. P번호가 없는 쓰기(`WRITEPOINT`)는 기본 우선순위 P5를 쓴다. 조건이 거짓이라고 관제점이 저절로 0이 되지는 않는다. 해당 분기에 쓰기가 없으면 이전 값이 남는다. 대문자 이름은 상수, `m`으로 시작하는 이름은 이 파일의 전역변수, `b`가 붙은 이름은 참/거짓 값이다.

<a id="section-1"></a>

## 1~33행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수

| 행 | 해석 |
|---:|---|
| 1 | *[주석] LJH 2026-11-17 수정 구간 시작. 주제 = 밸브별 수신 유효성 및 닫힘 확인* |
| 3 | *[주석] 로직엔진 loading* |
| 4 | DDC 로직 엔진 객체 생성 (이후 engine.xxx로 관제점을 읽고 씀) |
| 6 | *[주석] Macro상수 정의* |
| 7 | 매크로 상수 정의: TMR_READ, SET, ON, TRUE, DEC = 1 (긍정의 의미 또는 1인 인자) |
| 8 | 매크로 상수 정의: TMR_CLEAR, CLEAR, OFF, FALSE, INC = 0 (부정의 의미 또는 0인 인자) |
| 9 | 상수 `DEV_TIME_OUT` = 40<br>*[주석] deviation timer는 40초 까지* |
| 10 | 상수 `POS_HYST` = 30<br>*[주석] 개도의 히스테리시스는 +/-30% 까지* |
| 11 | 상수 `POS_OPEN` = 30<br>*[주석] 30% 이상 열리면 PICV가 "충분히" 열린 것으로 판단* |
| 12 | 설정값 상수 `NO_FLOW`: 유량 없음 판단 유량 설정 (`VP_FWU_PICV_No_Flow_Set`) 값을 읽어 둠<br>*[주석] '유량없음'으로 판단하는 최소 유량* |
| 13 | 설정값 상수 `LEAK_FLOW`: 누설 판단 유량 설정 (`VP_FWU_PICV_Leak_Flow_Set`) 값을 읽어 둠<br>*[주석] leak로 판단하는 유량 (?)* |
| 15 | *[주석] 타이머 정의: PICV의 현재 개도가 tolerance를 벗어난 경우* |
| 16 | 타이머 번호 상수 `PICV_1_DEVIATION_TIMER` = 4번 |
| 17 | 타이머 번호 상수 `PICV_2_DEVIATION_TIMER` = 5번 |
| 18 | 타이머 번호 상수 `PICV_3_DEVIATION_TIMER` = 6번 |
| 19 | 타이머 번호 상수 `PICV_4_DEVIATION_TIMER` = 7번 |
| 21 | *[주석] CH3에 FWU_PICV-1~4의 Position, Flow, Temperature 통신점을 등록한 뒤 Input_Enable=1로 설정* |
| 22 | *[주석] 개도는 %, 유량은 L/min, 온도는 냉수 출구 온도(℃)로 환산* |
| 24 | *[주석] 전역변수 선언* |
| 25 | 전역변수 `mbAllClosed` 선언, 처음 값 = TRUE(1) |
| 26 | 전역변수 `mbMonitorReady` 선언, 처음 값 = TRUE(1) |
| 27 | 전역변수 `mbAnyFault` 선언, 처음 값 = FALSE(0) |
| 28 | 전역변수 `mbAnyCommFault` 선언, 처음 값 = FALSE(0) |
| 29 | 전역변수 `mbPICVValid` 선언, 처음 값 = FALSE(0) |
| 30 | 전역변수 `mbPICVInputEnable` ← PICV 통신 입력 사용 설정 (`VP_FWU_PICV_Input_Enable`) = 1 이면 TRUE, 아니면 FALSE |
| 31 | 전역변수 `mbPICVFlowChkEnable` ← 밸브 유량 감시 사용 설정 (`VP_FWU_PICV_Flow_Check_Enable`) = 1 이면 TRUE, 아니면 FALSE |
| 32 | 전역변수 `mbCHWSCondi` ← 냉수 공급 조건 성립 표시 (`VP_FWU_Chilled_Water_Supply_Condition`) = 1 이면 TRUE, 아니면 FALSE |
| 33 | 전역변수 `mPICVCurrPos` 선언, 처음 값 = 0<br>*[주석] PICV의 현재 개도값* |

<a id="section-2"></a>

## 35~51행 · PICV1(1/2): valid check(개도, 유량, 온도에서 alarm 없음)

| 행 | 해석 |
|---:|---|
| 35 | *[주석] PICV1(1/2): valid check(개도, 유량, 온도에서 alarm 없음)* |
| 36 | `mbPICVValid` ← FALSE(0)<br>*[주석] 초기화* |
| 37 | `mbPICVInputEnable` = TRUE 이면 : |
| 38 | &emsp;→&nbsp;PICV 1번 개도 통신점 (`FWU_PICV-1.Position`)의 알람 코드 = 0 **그리고** PICV 1번 유량 통신점 (`FWU_PICV-1.Flow`)의 알람 코드 = 0 **그리고** PICV 1번 온도 통신점 (`FWU_PICV-1.Temperature`)의 알람 코드 = 0 이면 : |
| 39 | &emsp;&emsp;→&nbsp;PICV 1번 개도 표시값 (`VP_FWU_PICV-1_Position`)에 PICV 1번 개도 통신점 (`FWU_PICV-1.Position`) 값을 그대로 복사 — 기본 우선순위(P5) |
| 40 | &emsp;&emsp;→&nbsp;PICV 1번 유량 표시값 (`VP_FWU_PICV-1_Flow`)에 PICV 1번 유량 통신점 (`FWU_PICV-1.Flow`) 값을 그대로 복사 — 기본 우선순위(P5) |
| 41 | &emsp;&emsp;→&nbsp;PICV 1번 온도 표시값 (`VP_FWU_PICV-1_Temperature`)에 PICV 1번 온도 통신점 (`FWU_PICV-1.Temperature`) 값을 그대로 복사 — 기본 우선순위(P5) |
| 42 | &emsp;&emsp;→&nbsp;`mbPICVValid` ← TRUE(1) |
| 43 | &emsp;→&nbsp;38행 조건이 성립하지 않으면 : |
| 44 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 46 | `mPICVCurrPos` ← PICV 1번 개도 표시값 (`VP_FWU_PICV-1_Position`) 값 읽기 |
| 47 | 0 ≤ `mPICVCurrPos` ≤ 100 이면 : |
| 48 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 49 | 47행 조건이 성립하지 않으면 : |
| 50 | &emsp;→&nbsp;`mbPICVValid` ← FALSE(0) |
| 51 | PICV 1번 수신값 유효 표시 (`VP_FWU_PICV-1_Feedback_Valid`)에 `mbPICVValid` 기록 — 기본 우선순위(P5) |

<a id="section-3"></a>

## 53~102행 · PICV1(2/2): 개도 및 유량 범위 확인

| 행 | 해석 |
|---:|---|
| 53 | *[주석] PICV1(2/2): 개도 및 유량 범위 확인* |
| 54 | `mbPICVValid` = TRUE 이면 : |
| 55 | &emsp;→&nbsp;PICV 1번 수신 이상 (`VP_FWU_PICV-1_Comm_Fault`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 57 | &emsp;→&nbsp;`mPICVCurrPos` ≥ 5 이면 : |
| 58 | &emsp;&emsp;→&nbsp;`mbAllClosed` ← FALSE(0) |
| 59 | &emsp;→&nbsp;57행 조건이 성립하지 않으면 : |
| 60 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 62 | &emsp;→&nbsp;*[주석] 위치 제어 모드에서만 명령과 실제 개도를 비교한다.* |
| 63 | &emsp;→&nbsp;`bValveFault` ← FALSE(0) |
| 64 | &emsp;→&nbsp;밸브 제어 모드(0 미확정, 1 위치, 2 유량) (`VP_FWU_PICV_Control_Mode`) = 1 이면 :<br>*[주석] 좌변이 boolean인가? (?)* |
| 65 | &emsp;&emsp;→&nbsp;`mPICVCurrPos` - `POS_HYST`(30) < PICV 공통 개도 명령(AO) (`FWU_PICV_CONTROL`) < `mPICVCurrPos` + `POS_HYST`(30) 이면 : |
| 66 | &emsp;&emsp;&emsp;→&nbsp;타이머 `PICV_1_DEVIATION_TIMER`(4번: PICV 1번 명령-개도 차이 확인)를 0초로 초기화 |
| 67 | &emsp;&emsp;→&nbsp;65행 조건이 성립하지 않으면 : |
| 68 | &emsp;&emsp;&emsp;→&nbsp;타이머 `PICV_1_DEVIATION_TIMER`(4번: PICV 1번 명령-개도 차이 확인) 경과시간 > `DEV_TIME_OUT`(40) 이면 : |
| 69 | &emsp;&emsp;&emsp;&emsp;→&nbsp;`bValveFault` ← TRUE(1) |
| 70 | &emsp;&emsp;&emsp;→&nbsp;68행 조건이 성립하지 않으면 : |
| 71 | &emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 72 | &emsp;→&nbsp;64행 조건이 성립하지 않으면 : |
| 73 | &emsp;&emsp;→&nbsp;타이머 `PICV_1_DEVIATION_TIMER`(4번: PICV 1번 명령-개도 차이 확인)를 0초로 초기화 |
| 75 | &emsp;→&nbsp;*[주석] 유량 기준 30/10 LPM은 밸브별 설계 유량 확인 후 감시를 켤 것.* |
| 76 | &emsp;→&nbsp;`mbPICVFlowChkEnable` = TRUE 이면 : |
| 77 | &emsp;&emsp;→&nbsp;`PICVCurrFlow` ← PICV 1번 유량 표시값 (`VP_FWU_PICV-1_Flow`) 값 읽기 |
| 78 | &emsp;&emsp;→&nbsp;`mbCHWSCondi` = TRUE **그리고** `mPICVCurrPos` > `POS_OPEN`(30) **그리고** `PICVCurrFlow` < `NO_FLOW`(설정값) 이면 : |
| 79 | &emsp;&emsp;&emsp;→&nbsp;`bValveFault` ← TRUE(1) |
| 80 | &emsp;&emsp;→&nbsp;78행 조건이 성립하지 않으면 : |
| 81 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 83 | &emsp;&emsp;→&nbsp;`mPICVCurrPos` < 1 **그리고** `PICVCurrFlow` > `LEAK_FLOW`(설정값) 이면 : |
| 84 | &emsp;&emsp;&emsp;→&nbsp;`bValveFault` ← TRUE(1) |
| 85 | &emsp;&emsp;→&nbsp;83행 조건이 성립하지 않으면 : |
| 86 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 87 | &emsp;→&nbsp;76행 조건이 성립하지 않으면 : |
| 88 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 90 | &emsp;→&nbsp;PICV 1번 밸브 알람 (`VP_FWU_PICV-1_Alarm`)에 `bValveFault` 기록 — 기본 우선순위(P5) |
| 91 | 54행 조건이 성립하지 않으면 : |
| 92 | &emsp;→&nbsp;`mbAllClosed` ← FALSE(0) |
| 93 | &emsp;→&nbsp;`mbMonitorReady` ← FALSE(0) |
| 94 | &emsp;→&nbsp;`mbAnyCommFault` ← TRUE(1) |
| 95 | &emsp;→&nbsp;PICV 1번 수신 이상 (`VP_FWU_PICV-1_Comm_Fault`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 96 | &emsp;→&nbsp;PICV 1번 밸브 알람 (`VP_FWU_PICV-1_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 97 | &emsp;→&nbsp;타이머 `PICV_1_DEVIATION_TIMER`(4번: PICV 1번 명령-개도 차이 확인)를 0초로 초기화 |
| 99 | PICV 1번 밸브 알람 (`VP_FWU_PICV-1_Alarm`) = TRUE(1) 이면 : |
| 100 | &emsp;→&nbsp;`mbAnyFault` ← TRUE(1) |
| 101 | 99행 조건이 성립하지 않으면 : |
| 102 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |

<a id="section-4"></a>

## 104~120행 · PICV2(1/2): valid check(개도, 유량, 온도에서 alarm 없음)

| 행 | 해석 |
|---:|---|
| 104 | *[주석] PICV2(1/2): valid check(개도, 유량, 온도에서 alarm 없음)* |
| 105 | `mbPICVValid` ← FALSE(0)<br>*[주석] 초기화* |
| 106 | `mbPICVInputEnable` = TRUE 이면 : |
| 107 | &emsp;→&nbsp;PICV 2번 개도 통신점 (`FWU_PICV-2.Position`)의 알람 코드 = 0 **그리고** PICV 2번 유량 통신점 (`FWU_PICV-2.Flow`)의 알람 코드 = 0 **그리고** PICV 2번 온도 통신점 (`FWU_PICV-2.Temperature`)의 알람 코드 = 0 이면 : |
| 108 | &emsp;&emsp;→&nbsp;PICV 2번 개도 표시값 (`VP_FWU_PICV-2_Position`)에 PICV 2번 개도 통신점 (`FWU_PICV-2.Position`) 값을 그대로 복사 — 기본 우선순위(P5) |
| 109 | &emsp;&emsp;→&nbsp;PICV 2번 유량 표시값 (`VP_FWU_PICV-2_Flow`)에 PICV 2번 유량 통신점 (`FWU_PICV-2.Flow`) 값을 그대로 복사 — 기본 우선순위(P5) |
| 110 | &emsp;&emsp;→&nbsp;PICV 2번 온도 표시값 (`VP_FWU_PICV-2_Temperature`)에 PICV 2번 온도 통신점 (`FWU_PICV-2.Temperature`) 값을 그대로 복사 — 기본 우선순위(P5) |
| 111 | &emsp;&emsp;→&nbsp;`mbPICVValid` ← TRUE(1) |
| 112 | &emsp;→&nbsp;107행 조건이 성립하지 않으면 : |
| 113 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 115 | `mPICVCurrPos` ← PICV 2번 개도 표시값 (`VP_FWU_PICV-2_Position`) 값 읽기 |
| 116 | 0 ≤ `mPICVCurrPos` ≤ 100 이면 : |
| 117 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 118 | 116행 조건이 성립하지 않으면 : |
| 119 | &emsp;→&nbsp;`mbPICVValid` ← FALSE(0) |
| 120 | PICV 2번 수신값 유효 표시 (`VP_FWU_PICV-2_Feedback_Valid`)에 `mbPICVValid` 기록 — 기본 우선순위(P5) |

<a id="section-5"></a>

## 122~171행 · PICV2(2/2): 개도 및 유량 범위 확인

| 행 | 해석 |
|---:|---|
| 122 | *[주석] PICV2(2/2): 개도 및 유량 범위 확인* |
| 123 | `mbPICVValid` = TRUE 이면 : |
| 124 | &emsp;→&nbsp;PICV 2번 수신 이상 (`VP_FWU_PICV-2_Comm_Fault`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 126 | &emsp;→&nbsp;`mPICVCurrPos` ≥ 5 이면 : |
| 127 | &emsp;&emsp;→&nbsp;`mbAllClosed` ← FALSE(0) |
| 128 | &emsp;→&nbsp;126행 조건이 성립하지 않으면 : |
| 129 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 131 | &emsp;→&nbsp;*[주석] 위치 제어 모드에서만 명령과 실제 개도를 비교한다.* |
| 132 | &emsp;→&nbsp;`bValveFault` ← FALSE(0) |
| 133 | &emsp;→&nbsp;밸브 제어 모드(0 미확정, 1 위치, 2 유량) (`VP_FWU_PICV_Control_Mode`) = 1 이면 :<br>*[주석] 좌변이 boolean인가? (?)* |
| 134 | &emsp;&emsp;→&nbsp;`mPICVCurrPos` - `POS_HYST`(30) < PICV 공통 개도 명령(AO) (`FWU_PICV_CONTROL`) < `mPICVCurrPos` + `POS_HYST`(30) 이면 : |
| 135 | &emsp;&emsp;&emsp;→&nbsp;타이머 `PICV_2_DEVIATION_TIMER`(5번: PICV 2번 명령-개도 차이 확인)를 0초로 초기화 |
| 136 | &emsp;&emsp;→&nbsp;134행 조건이 성립하지 않으면 : |
| 137 | &emsp;&emsp;&emsp;→&nbsp;타이머 `PICV_2_DEVIATION_TIMER`(5번: PICV 2번 명령-개도 차이 확인) 경과시간 > `DEV_TIME_OUT`(40) 이면 : |
| 138 | &emsp;&emsp;&emsp;&emsp;→&nbsp;`bValveFault` ← TRUE(1) |
| 139 | &emsp;&emsp;&emsp;→&nbsp;137행 조건이 성립하지 않으면 : |
| 140 | &emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 141 | &emsp;→&nbsp;133행 조건이 성립하지 않으면 : |
| 142 | &emsp;&emsp;→&nbsp;타이머 `PICV_2_DEVIATION_TIMER`(5번: PICV 2번 명령-개도 차이 확인)를 0초로 초기화 |
| 144 | &emsp;→&nbsp;*[주석] 유량 기준 30/10 LPM은 밸브별 설계 유량 확인 후 감시를 켤 것.* |
| 145 | &emsp;→&nbsp;`mbPICVFlowChkEnable` = TRUE 이면 : |
| 146 | &emsp;&emsp;→&nbsp;`PICVCurrFlow` ← PICV 2번 유량 표시값 (`VP_FWU_PICV-2_Flow`) 값 읽기 |
| 147 | &emsp;&emsp;→&nbsp;`mbCHWSCondi` = TRUE **그리고** `mPICVCurrPos` > `POS_OPEN`(30) **그리고** `PICVCurrFlow` < `NO_FLOW`(설정값) 이면 : |
| 148 | &emsp;&emsp;&emsp;→&nbsp;`bValveFault` ← TRUE(1) |
| 149 | &emsp;&emsp;→&nbsp;147행 조건이 성립하지 않으면 : |
| 150 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 152 | &emsp;&emsp;→&nbsp;`mPICVCurrPos` < 1 **그리고** `PICVCurrFlow` > `LEAK_FLOW`(설정값) 이면 : |
| 153 | &emsp;&emsp;&emsp;→&nbsp;`bValveFault` ← TRUE(1) |
| 154 | &emsp;&emsp;→&nbsp;152행 조건이 성립하지 않으면 : |
| 155 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 156 | &emsp;→&nbsp;145행 조건이 성립하지 않으면 : |
| 157 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 159 | &emsp;→&nbsp;PICV 2번 밸브 알람 (`VP_FWU_PICV-2_Alarm`)에 `bValveFault` 기록 — 기본 우선순위(P5) |
| 160 | 123행 조건이 성립하지 않으면 : |
| 161 | &emsp;→&nbsp;`mbAllClosed` ← FALSE(0) |
| 162 | &emsp;→&nbsp;`mbMonitorReady` ← FALSE(0) |
| 163 | &emsp;→&nbsp;`mbAnyCommFault` ← TRUE(1) |
| 164 | &emsp;→&nbsp;PICV 2번 수신 이상 (`VP_FWU_PICV-2_Comm_Fault`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 165 | &emsp;→&nbsp;PICV 2번 밸브 알람 (`VP_FWU_PICV-2_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 166 | &emsp;→&nbsp;타이머 `PICV_2_DEVIATION_TIMER`(5번: PICV 2번 명령-개도 차이 확인)를 0초로 초기화 |
| 168 | PICV 2번 밸브 알람 (`VP_FWU_PICV-2_Alarm`) = TRUE(1) 이면 : |
| 169 | &emsp;→&nbsp;`mbAnyFault` ← TRUE(1) |
| 170 | 168행 조건이 성립하지 않으면 : |
| 171 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |

<a id="section-6"></a>

## 173~189행 · PICV3(1/2): valid check(개도, 유량, 온도에서 alarm 없음)

| 행 | 해석 |
|---:|---|
| 173 | *[주석] PICV3(1/2): valid check(개도, 유량, 온도에서 alarm 없음)* |
| 174 | `mbPICVValid` ← FALSE(0)<br>*[주석] 초기화* |
| 175 | `mbPICVInputEnable` = TRUE 이면 : |
| 176 | &emsp;→&nbsp;PICV 3번 개도 통신점 (`FWU_PICV-3.Position`)의 알람 코드 = 0 **그리고** PICV 3번 유량 통신점 (`FWU_PICV-3.Flow`)의 알람 코드 = 0 **그리고** PICV 3번 온도 통신점 (`FWU_PICV-3.Temperature`)의 알람 코드 = 0 이면 : |
| 177 | &emsp;&emsp;→&nbsp;PICV 3번 개도 표시값 (`VP_FWU_PICV-3_Position`)에 PICV 3번 개도 통신점 (`FWU_PICV-3.Position`) 값을 그대로 복사 — 기본 우선순위(P5) |
| 178 | &emsp;&emsp;→&nbsp;PICV 3번 유량 표시값 (`VP_FWU_PICV-3_Flow`)에 PICV 3번 유량 통신점 (`FWU_PICV-3.Flow`) 값을 그대로 복사 — 기본 우선순위(P5) |
| 179 | &emsp;&emsp;→&nbsp;PICV 3번 온도 표시값 (`VP_FWU_PICV-3_Temperature`)에 PICV 3번 온도 통신점 (`FWU_PICV-3.Temperature`) 값을 그대로 복사 — 기본 우선순위(P5) |
| 180 | &emsp;&emsp;→&nbsp;`mbPICVValid` ← TRUE(1) |
| 181 | &emsp;→&nbsp;176행 조건이 성립하지 않으면 : |
| 182 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 184 | `mPICVCurrPos` ← PICV 3번 개도 표시값 (`VP_FWU_PICV-3_Position`) 값 읽기 |
| 185 | 0 ≤ `mPICVCurrPos` ≤ 100 이면 : |
| 186 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 187 | 185행 조건이 성립하지 않으면 : |
| 188 | &emsp;→&nbsp;`mbPICVValid` ← FALSE(0) |
| 189 | PICV 3번 수신값 유효 표시 (`VP_FWU_PICV-3_Feedback_Valid`)에 `mbPICVValid` 기록 — 기본 우선순위(P5) |

<a id="section-7"></a>

## 191~238행 · PICV3(2/2): 개도 및 유량 범위 확인

| 행 | 해석 |
|---:|---|
| 191 | *[주석] PICV3(2/2): 개도 및 유량 범위 확인* |
| 192 | `mbPICVValid` = TRUE 이면 : |
| 193 | &emsp;→&nbsp;PICV 3번 수신 이상 (`VP_FWU_PICV-3_Comm_Fault`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 195 | &emsp;→&nbsp;`mPICVCurrPos` ≥ 5 이면 : |
| 196 | &emsp;&emsp;→&nbsp;`mbAllClosed` ← FALSE(0) |
| 197 | &emsp;→&nbsp;195행 조건이 성립하지 않으면 : |
| 198 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 200 | *[주석] 위치 제어 모드에서만 명령과 실제 개도를 비교한다.* |
| 201 | &emsp;→&nbsp;`bValveFault` ← FALSE(0) |
| 202 | &emsp;→&nbsp;밸브 제어 모드(0 미확정, 1 위치, 2 유량) (`VP_FWU_PICV_Control_Mode`) = 1 이면 :<br>*[주석] 좌변이 boolean인가? (?)* |
| 203 | &emsp;&emsp;→&nbsp;`mPICVCurrPos` - `POS_HYST`(30) < PICV 공통 개도 명령(AO) (`FWU_PICV_CONTROL`) < `mPICVCurrPos` + `POS_HYST`(30) 이면 : |
| 204 | &emsp;&emsp;&emsp;→&nbsp;타이머 `PICV_3_DEVIATION_TIMER`(6번: PICV 3번 명령-개도 차이 확인)를 0초로 초기화 |
| 205 | &emsp;&emsp;→&nbsp;203행 조건이 성립하지 않으면 : |
| 206 | &emsp;&emsp;&emsp;→&nbsp;타이머 `PICV_3_DEVIATION_TIMER`(6번: PICV 3번 명령-개도 차이 확인) 경과시간 > `DEV_TIME_OUT`(40) 이면 : |
| 207 | &emsp;&emsp;&emsp;&emsp;→&nbsp;`bValveFault` ← TRUE(1) |
| 208 | &emsp;&emsp;&emsp;→&nbsp;206행 조건이 성립하지 않으면 : |
| 209 | &emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 210 | &emsp;→&nbsp;202행 조건이 성립하지 않으면 : |
| 211 | &emsp;&emsp;→&nbsp;타이머 `PICV_3_DEVIATION_TIMER`(6번: PICV 3번 명령-개도 차이 확인)를 0초로 초기화 |
| 212 | &emsp;→&nbsp;*[주석] 유량 기준 30/10 LPM은 밸브별 설계 유량 확인 후 감시를 켤 것.* |
| 213 | &emsp;→&nbsp;`mbPICVFlowChkEnable` = TRUE 이면 : |
| 214 | &emsp;&emsp;→&nbsp;`PICVCurrFlow` ← PICV 3번 유량 표시값 (`VP_FWU_PICV-3_Flow`) 값 읽기 |
| 215 | &emsp;&emsp;→&nbsp;`mbCHWSCondi` = TRUE **그리고** `mPICVCurrPos` > `POS_OPEN`(30) **그리고** `PICVCurrFlow` < `NO_FLOW`(설정값) 이면 : |
| 216 | &emsp;&emsp;&emsp;→&nbsp;`bValveFault` ← TRUE(1) |
| 217 | &emsp;&emsp;→&nbsp;215행 조건이 성립하지 않으면 : |
| 218 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 220 | &emsp;&emsp;→&nbsp;`mPICVCurrPos` < 1 **그리고** `PICVCurrFlow` > `LEAK_FLOW`(설정값) 이면 : |
| 221 | &emsp;&emsp;&emsp;→&nbsp;`bValveFault` ← TRUE(1) |
| 222 | &emsp;&emsp;→&nbsp;220행 조건이 성립하지 않으면 : |
| 223 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 224 | &emsp;→&nbsp;213행 조건이 성립하지 않으면 : |
| 225 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 226 | &emsp;→&nbsp;PICV 3번 밸브 알람 (`VP_FWU_PICV-3_Alarm`)에 `bValveFault` 기록 — 기본 우선순위(P5) |
| 227 | 192행 조건이 성립하지 않으면 : |
| 228 | &emsp;→&nbsp;`mbAllClosed` ← FALSE(0) |
| 229 | &emsp;→&nbsp;`mbMonitorReady` ← FALSE(0) |
| 230 | &emsp;→&nbsp;`mbAnyCommFault` ← TRUE(1) |
| 231 | &emsp;→&nbsp;PICV 3번 수신 이상 (`VP_FWU_PICV-3_Comm_Fault`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 232 | &emsp;→&nbsp;PICV 3번 밸브 알람 (`VP_FWU_PICV-3_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 233 | &emsp;→&nbsp;타이머 `PICV_3_DEVIATION_TIMER`(6번: PICV 3번 명령-개도 차이 확인)를 0초로 초기화 |
| 235 | PICV 3번 밸브 알람 (`VP_FWU_PICV-3_Alarm`) = TRUE(1) 이면 : |
| 236 | &emsp;→&nbsp;`mbAnyFault` ← TRUE(1) |
| 237 | 235행 조건이 성립하지 않으면 : |
| 238 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |

<a id="section-8"></a>

## 240~256행 · PICV4(1/2): valid check(개도, 유량, 온도에서 alarm 없음)

| 행 | 해석 |
|---:|---|
| 240 | *[주석] PICV4(1/2): valid check(개도, 유량, 온도에서 alarm 없음)* |
| 241 | `mbPICVValid` ← FALSE(0)<br>*[주석] 초기화* |
| 242 | `mbPICVInputEnable` = TRUE 이면 : |
| 243 | &emsp;→&nbsp;PICV 4번 개도 통신점 (`FWU_PICV-4.Position`)의 알람 코드 = 0 **그리고** PICV 4번 유량 통신점 (`FWU_PICV-4.Flow`)의 알람 코드 = 0 **그리고** PICV 4번 온도 통신점 (`FWU_PICV-4.Temperature`)의 알람 코드 = 0 이면 : |
| 244 | &emsp;&emsp;→&nbsp;PICV 4번 개도 표시값 (`VP_FWU_PICV-4_Position`)에 PICV 4번 개도 통신점 (`FWU_PICV-4.Position`) 값을 그대로 복사 — 기본 우선순위(P5) |
| 245 | &emsp;&emsp;→&nbsp;PICV 4번 유량 표시값 (`VP_FWU_PICV-4_Flow`)에 PICV 4번 유량 통신점 (`FWU_PICV-4.Flow`) 값을 그대로 복사 — 기본 우선순위(P5) |
| 246 | &emsp;&emsp;→&nbsp;PICV 4번 온도 표시값 (`VP_FWU_PICV-4_Temperature`)에 PICV 4번 온도 통신점 (`FWU_PICV-4.Temperature`) 값을 그대로 복사 — 기본 우선순위(P5) |
| 247 | &emsp;&emsp;→&nbsp;`mbPICVValid` ← TRUE(1) |
| 248 | &emsp;→&nbsp;243행 조건이 성립하지 않으면 : |
| 249 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 251 | `mPICVCurrPos` ← PICV 4번 개도 표시값 (`VP_FWU_PICV-4_Position`) 값 읽기 |
| 252 | 0 ≤ `mPICVCurrPos` ≤ 100 이면 : |
| 253 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 254 | 252행 조건이 성립하지 않으면 : |
| 255 | &emsp;→&nbsp;`mbPICVValid` ← FALSE(0) |
| 256 | PICV 4번 수신값 유효 표시 (`VP_FWU_PICV-4_Feedback_Valid`)에 `mbPICVValid` 기록 — 기본 우선순위(P5) |

<a id="section-9"></a>

## 258~307행 · PICV4(2/2): 개도 및 유량 범위 확인

| 행 | 해석 |
|---:|---|
| 258 | *[주석] PICV4(2/2): 개도 및 유량 범위 확인* |
| 259 | `mbPICVValid` = TRUE 이면 : |
| 260 | &emsp;→&nbsp;PICV 4번 수신 이상 (`VP_FWU_PICV-4_Comm_Fault`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 262 | &emsp;→&nbsp;`mPICVCurrPos` ≥ 5 이면 : |
| 263 | &emsp;&emsp;→&nbsp;`mbAllClosed` ← FALSE(0) |
| 264 | &emsp;→&nbsp;262행 조건이 성립하지 않으면 : |
| 265 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 267 | &emsp;→&nbsp;*[주석] 위치 제어 모드에서만 명령과 실제 개도를 비교한다.* |
| 268 | &emsp;→&nbsp;`bValveFault` ← FALSE(0) |
| 269 | &emsp;→&nbsp;밸브 제어 모드(0 미확정, 1 위치, 2 유량) (`VP_FWU_PICV_Control_Mode`) = 1 이면 :<br>*[주석] 좌변이 boolean인가? (?)* |
| 270 | &emsp;&emsp;→&nbsp;`mPICVCurrPos` - `POS_HYST`(30) < PICV 공통 개도 명령(AO) (`FWU_PICV_CONTROL`) < `mPICVCurrPos` + `POS_HYST`(30) 이면 : |
| 271 | &emsp;&emsp;&emsp;→&nbsp;타이머 `PICV_4_DEVIATION_TIMER`(7번: PICV 4번 명령-개도 차이 확인)를 0초로 초기화 |
| 272 | &emsp;&emsp;→&nbsp;270행 조건이 성립하지 않으면 : |
| 273 | &emsp;&emsp;&emsp;→&nbsp;타이머 `PICV_4_DEVIATION_TIMER`(7번: PICV 4번 명령-개도 차이 확인) 경과시간 > `DEV_TIME_OUT`(40) 이면 : |
| 274 | &emsp;&emsp;&emsp;&emsp;→&nbsp;`bValveFault` ← TRUE(1) |
| 275 | &emsp;&emsp;&emsp;→&nbsp;273행 조건이 성립하지 않으면 : |
| 276 | &emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 277 | &emsp;→&nbsp;269행 조건이 성립하지 않으면 : |
| 278 | &emsp;&emsp;→&nbsp;타이머 `PICV_4_DEVIATION_TIMER`(7번: PICV 4번 명령-개도 차이 확인)를 0초로 초기화 |
| 280 | &emsp;→&nbsp;*[주석] 유량 기준 30/10 LPM은 밸브별 설계 유량 확인 후 감시를 켤 것.* |
| 281 | &emsp;→&nbsp;`mbPICVFlowChkEnable` = TRUE 이면 : |
| 282 | &emsp;&emsp;→&nbsp;`PICVCurrFlow` ← PICV 4번 유량 표시값 (`VP_FWU_PICV-4_Flow`) 값 읽기 |
| 283 | &emsp;&emsp;→&nbsp;`mbCHWSCondi` = TRUE **그리고** `mPICVCurrPos` > `POS_OPEN`(30) **그리고** `PICVCurrFlow` < `NO_FLOW`(설정값) 이면 : |
| 284 | &emsp;&emsp;&emsp;→&nbsp;`bValveFault` ← TRUE(1) |
| 285 | &emsp;&emsp;→&nbsp;283행 조건이 성립하지 않으면 : |
| 286 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 288 | &emsp;&emsp;→&nbsp;`mPICVCurrPos` < 1 **그리고** `PICVCurrFlow` > `LEAK_FLOW`(설정값) 이면 : |
| 289 | &emsp;&emsp;&emsp;→&nbsp;`bValveFault` ← TRUE(1) |
| 290 | &emsp;&emsp;→&nbsp;288행 조건이 성립하지 않으면 : |
| 291 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 292 | &emsp;→&nbsp;281행 조건이 성립하지 않으면 : |
| 293 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 295 | &emsp;→&nbsp;PICV 4번 밸브 알람 (`VP_FWU_PICV-4_Alarm`)에 `bValveFault` 기록 — 기본 우선순위(P5) |
| 296 | 259행 조건이 성립하지 않으면 : |
| 297 | &emsp;→&nbsp;`mbAllClosed` ← FALSE(0) |
| 298 | &emsp;→&nbsp;`mbMonitorReady` ← FALSE(0) |
| 299 | &emsp;→&nbsp;`mbAnyCommFault` ← TRUE(1) |
| 300 | &emsp;→&nbsp;PICV 4번 수신 이상 (`VP_FWU_PICV-4_Comm_Fault`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 301 | &emsp;→&nbsp;PICV 4번 밸브 알람 (`VP_FWU_PICV-4_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 302 | &emsp;→&nbsp;타이머 `PICV_4_DEVIATION_TIMER`(7번: PICV 4번 명령-개도 차이 확인)를 0초로 초기화 |
| 304 | PICV 4번 밸브 알람 (`VP_FWU_PICV-4_Alarm`) = TRUE(1) 이면 : |
| 305 | &emsp;→&nbsp;`mbAnyFault` ← TRUE(1) |
| 306 | 304행 조건이 성립하지 않으면 : |
| 307 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |

<a id="section-10"></a>

## 309~313행 · 모니터링 flag setting

| 행 | 해석 |
|---:|---|
| 309 | *[주석] 모니터링 flag setting* |
| 310 | 밸브 제어 모드(0 미확정, 1 위치, 2 유량) (`VP_FWU_PICV_Control_Mode`) = 0 **또는** `mbPICVFlowChkEnable` = FALSE(0) 이면 :<br>*[주석] 좌변의 첫번째 term이 boolean인가? (?)* |
| 311 | &emsp;→&nbsp;`mbMonitorReady` ← 0 |
| 312 | 310행 조건이 성립하지 않으면 : |
| 313 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |

<a id="section-11"></a>

## 315~320행 · PICV 상태, 유량 등의 정보를 VP_...에 업데이트

| 행 | 해석 |
|---:|---|
| 315 | *[주석] PICV 상태, 유량 등의 정보를 VP_...에 업데이트* |
| 316 | 네 밸브 모두 닫힘 표시 (`VP_FWU_PICV_All_Closed`)에 `mbAllClosed` 기록 — 기본 우선순위(P5) |
| 317 | 밸브 감시 준비 표시 (`VP_FWU_PICV_Monitor_Ready`)에 `mbMonitorReady` 기록 — 기본 우선순위(P5) |
| 318 | PICV 알람 종합 (`VP_FWU_PICV_Alarm`)에 `mbAnyFault` 기록 — 기본 우선순위(P5) |
| 319 | PICV 수신 이상 종합 (`VP_FWU_Flow_Comm_Fault`)에 `mbAnyCommFault` 기록 — 기본 우선순위(P5) |
| 320 | *[주석] LJH 2026-11-17 수정 구간 끝. 주제 = 밸브별 수신 유효성 및 닫힘 확인* |
