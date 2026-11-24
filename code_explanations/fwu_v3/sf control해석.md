# SF Control 줄별 해석

> **대상 코드** : `fwu_v3/Logic/SF Control.py` (288 줄)  
> **기준** : `sy 브랜치 2026-11-23 (naming rule·관제점 이름 변경 반영)`  
> **행** = 코드 줄 번호 (빈 줄은 생략)  
> **표기** : `→` 들여쓰기 단계 · *[주석]* 코드 안 주석 · `이름` 코드 안 상수·변수 · **※** 읽을 때 주의할 점

팬 제어 기준(고정속도·RAT·RDP·ΔT·CZT)에 따라 팬 속도를 정하고, 댐퍼·밸브와 연계해 기동과 정지를 한다. 5초마다 팬 목표 RPM(팬 통신 이상 시 AO)을 내보낸다.

**목차**

- [1~38행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수](#section-1)
- [40~55행 · 고정속도로 돌릴지 판단](#section-2)
- [57~66행 · 온도 센서 고장 시 대체 운전: RAT 모드는 RAT 고장, ΔT 모드는 RAT·SAT 중 하나라도 고장이면 고정속도](#section-3)
- [68~85행 · 상위(BMS/PLC) 통신이 끊겼을 때](#section-4)
- [87~230행 · 비상정지가 아닐 때](#section-5)
- [232~250행 · 팬 운전 명령: 속도 값이 있으면 8대 모두 운전](#section-6)
- [252~288행 · 팬 속도 출력 (5초마다)](#section-7)

**※ 공통 표기**: 매크로 상수 TRUE·ON·SET·TMR_READ·DEC = 1, FALSE·OFF·CLEAR·TMR_CLEAR·INC = 0. `SECTIMER(타이머, TMR_CLEAR)`는 타이머를 0초로 초기화, `SECTIMER(타이머, TMR_READ)`는 경과시간 확인이다. P번호가 없는 쓰기(`WRITEPOINT`)는 기본 우선순위 P5를 쓴다. 조건이 거짓이라고 관제점이 저절로 0이 되지는 않는다. 해당 분기에 쓰기가 없으면 이전 값이 남는다. 대문자 이름은 상수, `m`으로 시작하는 이름은 이 파일의 전역변수, `b`가 붙은 이름은 참/거짓 값이다.

<a id="section-1"></a>

## 1~38행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수

| 행 | 해석 |
|---:|---|
| 1 | *[주석] LJH 2026-11-17 수정 구간 시작. 주제 = 온도 센서 고장 시 대체운전, 네 밸브 닫힘과 팬 정지 연계* |
| 2 | *[주석] JSY 2026-11-23 수정 구간 시작. 주제 = Coding Rule 적용(매크로 상수, 설정값 상수, 변수명, if-else 짝 맞춤, 주석)* |
| 4 | *[주석] 로직엔진 loading* |
| 5 | DDC 로직 엔진 객체 생성 (이후 engine.xxx로 관제점을 읽고 씀) |
| 7 | *[주석] Macro상수 정의* |
| 8 | 매크로 상수 정의: TMR_READ, SET, ON, TRUE, DEC = 1 (긍정의 의미 또는 1인 인자) |
| 9 | 매크로 상수 정의: TMR_CLEAR, CLEAR, OFF, FALSE, INC = 0 (부정의 의미 또는 0인 인자) |
| 11 | *[주석] DEC/INC는 LOOP2 제어 방향 (DEC: 현재값을 내리는 제어, INC: 현재값을 올리는 제어)* |
| 12 | 상수 `RAT_LOOP` = 1<br>*[주석] LOOP2 번호: RAT 기준 제어* |
| 13 | 상수 `RDP_LOOP` = 2<br>*[주석] LOOP2 번호: RDP 기준 제어* |
| 14 | 상수 `DELTA_T_LOOP` = 3<br>*[주석] LOOP2 번호: ΔT(RAT-SAT) 기준 제어* |
| 15 | 상수 `CZT_LOOP` = 4<br>*[주석] LOOP2 번호: CZT 기준 제어* |
| 16 | 설정값 상수 `SF_CONTROL_SELECT`: 팬 제어 기준 선택(0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT) (`VP_FWU_SF_Control_Select`) 값을 읽어 둠<br>*[주석] 팬 제어 기준. 0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT* |
| 17 | 설정값 상수 `RAT_PGAIN`: 팬 RAT 기준 제어 P 게인 (`VP_FWU_SF_RAT_PGain`) 값을 읽어 둠<br>*[주석] RAT 기준 팬 제어 P 게인* |
| 18 | 설정값 상수 `RAT_IGAIN`: 팬 RAT 기준 제어 I 게인 (`VP_FWU_SF_RAT_IGain`) 값을 읽어 둠<br>*[주석] RAT 기준 팬 제어 I 게인* |
| 19 | 설정값 상수 `RDP_PGAIN`: 팬 RDP 기준 제어 P 게인 (`VP_FWU_SF_RDP_PGain`) 값을 읽어 둠<br>*[주석] RDP 기준 팬 제어 P 게인* |
| 20 | 설정값 상수 `RDP_IGAIN`: 팬 RDP 기준 제어 I 게인 (`VP_FWU_SF_RDP_IGain`) 값을 읽어 둠<br>*[주석] RDP 기준 팬 제어 I 게인* |
| 21 | 설정값 상수 `DELTAT_PGAIN`: 팬 ΔT 기준 제어 P 게인 (`VP_FWU_SF_DeltaT_PGain`) 값을 읽어 둠<br>*[주석] ΔT 기준 팬 제어 P 게인* |
| 22 | 설정값 상수 `DELTAT_IGAIN`: 팬 ΔT 기준 제어 I 게인 (`VP_FWU_SF_DeltaT_IGain`) 값을 읽어 둠<br>*[주석] ΔT 기준 팬 제어 I 게인* |
| 23 | 설정값 상수 `CZT_PGAIN`: 팬 CZT 기준 제어 P 게인 (`VP_FWU_SF_CZT_PGain`) 값을 읽어 둠<br>*[주석] CZT 기준 팬 제어 P 게인* |
| 24 | 설정값 상수 `CZT_IGAIN`: 팬 CZT 기준 제어 I 게인 (`VP_FWU_SF_CZT_IGain`) 값을 읽어 둠<br>*[주석] CZT 기준 팬 제어 I 게인* |
| 26 | *[주석] 타이머 정의* |
| 27 | 타이머 번호 상수 `SPEED_OUTPUT_TIMER` = 1번<br>*[주석] 팬 속도를 마지막으로 내보낸 뒤 지난 시간* |
| 29 | *[주석] 전역변수 선언* |
| 30 | 전역변수 `mbFixed` 선언, 처음 값 = FALSE(0)<br>*[주석] TRUE면 PI 제어 대신 고정속도(Speed_SP)로 돈다* |
| 31 | 전역변수 `mbBMSFail` 선언, 처음 값 = FALSE(0)<br>*[주석] TRUE면 상위 통신이 끊겨 Comm_Fail_Mode 설정대로 돈다* |
| 33 | *[주석] 모드 UI는 정수 0~4만 전송. 직접 쓰기를 허용하면 별도 값 검증 필요.* |
| 34 | *[주석] 수동 속도는 코드 제한 없음. HMI에서 정지 0 또는 최소~최대 속도만 허용.* |
| 35 | *[주석] HMI에서 최소 <= 최대를 확인할 것. 최소 속도 기본값 20% (QTS RFP 2.3.D.3, JSY 2026-11-24 30%→20%).* |
| 36 | *[주석] ΔT 목표 -2℃는 SMX01 기준 임시값. 양의 RAT-SAT 운전에서 최대속도에 머물 수 있어 재확인.* |
| 37 | *[주석] 정상 정지는 네 밸브 닫힘까지 대기. 미폐쇄 제한시간/대체 정지 정책은 추후 검토.* |
| 38 | *[주석] 팬 통신 이상 시 전체 AO 전환. 새 팬의 Run·AO/RPM 우선권·환산·복구 동작 확인.* |

<a id="section-2"></a>

## 40~55행 · 고정속도로 돌릴지 판단

> 고정속도(0)를 골랐거나, 고른 제어 기준의 센서값을 쓸 수 없으면 고정속도로 돈다

| 행 | 해석 |
|---:|---|
| 40 | *[주석] 고정속도로 돌릴지 판단* |
| 41 | *[주석] 고정속도(0)를 골랐거나, 고른 제어 기준의 센서값을 쓸 수 없으면 고정속도로 돈다* |
| 42 | 0 ≤ `SF_CONTROL_SELECT`(설정값) < 1 이면 : |
| 43 | &emsp;→&nbsp;`mbFixed` ← TRUE(1) |
| 44 | 42행 조건이 성립하지 않으면 : |
| 45 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 47 | 2 ≤ `SF_CONTROL_SELECT`(설정값) < 3 **그리고** 룸 차압 제어용 값 유효 표시 (`VP_FWU_RDP_PV_Valid`) ≠ TRUE(1) 이면 : |
| 48 | &emsp;→&nbsp;`mbFixed` ← TRUE(1) |
| 49 | 47행 조건이 성립하지 않으면 : |
| 50 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 52 | 4 ≤ `SF_CONTROL_SELECT`(설정값) < 5 **그리고** 냉복도 온도 제어용 값 유효 표시 (`VP_FWU_CZT_PV_Valid`) ≠ TRUE(1) 이면 : |
| 53 | &emsp;→&nbsp;`mbFixed` ← TRUE(1) |
| 54 | 52행 조건이 성립하지 않으면 : |
| 55 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |

<a id="section-3"></a>

## 57~66행 · 온도 센서 고장 시 대체 운전: RAT 모드는 RAT 고장, ΔT 모드는 RAT·SAT 중 하나라도 고장이면 고정속도

| 행 | 해석 |
|---:|---|
| 57 | *[주석] 온도 센서 고장 시 대체 운전: RAT 모드는 RAT 고장, ΔT 모드는 RAT·SAT 중 하나라도 고장이면 고정속도* |
| 58 | 1 ≤ `SF_CONTROL_SELECT`(설정값) < 2 **그리고** 환기 온도(RAT) 센서 고장 알람 (`VP_FWU_RAT_Failure_Alarm`) = TRUE(1) 이면 : |
| 59 | &emsp;→&nbsp;`mbFixed` ← TRUE(1) |
| 60 | 58행 조건이 성립하지 않으면 : |
| 61 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 63 | 3 ≤ `SF_CONTROL_SELECT`(설정값) < 4 **그리고** (환기 온도(RAT) 센서 고장 알람 (`VP_FWU_RAT_Failure_Alarm`) = TRUE(1) **또는** 급기 온도(SAT) 센서 고장 알람 (`VP_FWU_SAT_Failure_Alarm`) = TRUE(1)) 이면 : |
| 64 | &emsp;→&nbsp;`mbFixed` ← TRUE(1) |
| 65 | 63행 조건이 성립하지 않으면 : |
| 66 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |

<a id="section-4"></a>

## 68~85행 · 상위(BMS/PLC) 통신이 끊겼을 때

> 상위 값을 쓰는 RDP·CZT 모드, 또는 원격 선택 상태의 고정속도 모드는 Comm_Fail_Mode 설정을 따른다

| 행 | 해석 |
|---:|---|
| 68 | *[주석] 상위(BMS/PLC) 통신이 끊겼을 때* |
| 69 | *[주석] 상위 값을 쓰는 RDP·CZT 모드, 또는 원격 선택 상태의 고정속도 모드는 Comm_Fail_Mode 설정을 따른다* |
| 70 | 상위 통신 감시 사용 설정 (`VP_FWU_Upper_Comm_Enable`) = TRUE(1) **그리고** 상위(BMS/PLC) 통신 이상 (`VP_FWU_BMS_PLC_Comm_Fault`) = TRUE(1) 이면 : |
| 71 | &emsp;→&nbsp;2 ≤ `SF_CONTROL_SELECT`(설정값) < 3 **또는** 4 ≤ `SF_CONTROL_SELECT`(설정값) < 5 이면 : |
| 72 | &emsp;&emsp;→&nbsp;`mbBMSFail` ← TRUE(1) |
| 73 | &emsp;→&nbsp;71행 조건이 성립하지 않으면 : |
| 74 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 75 | &emsp;→&nbsp;0 ≤ `SF_CONTROL_SELECT`(설정값) < 1 **그리고** 원격(BMS) 선택 입력(DI) (`REMOTE_SELECTION`) = TRUE(1) 이면 : |
| 76 | &emsp;&emsp;→&nbsp;`mbBMSFail` ← TRUE(1) |
| 77 | &emsp;→&nbsp;75행 조건이 성립하지 않으면 : |
| 78 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 79 | 70행 조건이 성립하지 않으면 : |
| 80 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 82 | `mbBMSFail` = TRUE(1) 이면 : |
| 83 | &emsp;→&nbsp;`mbFixed` ← FALSE(0) |
| 84 | 82행 조건이 성립하지 않으면 : |
| 85 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |

<a id="section-5"></a>

## 87~230행 · 비상정지가 아닐 때

| 행 | 해석 |
|---:|---|
| 87 | *[주석] 비상정지가 아닐 때* |
| 88 | 비상정지 입력(DI) (`FWU_EMERGENCY`) = FALSE(0) 이면 : |
| 89 | &emsp;→&nbsp;*[주석] 비상정지 때 걸어 둔 P1 해제* |
| 90 | &emsp;→&nbsp;팬 1~4번 속도 AO 출력 (`FWU_SF-1_4_SPEED_CONTROL`)의 P1 쓰기 해제<br>*[주석] FWU_SF-1_8_SPEED_CONTROL로 합쳐도 됨 (기존 배선이 1~4, 5~8로 나뉘어 있음)* |
| 91 | &emsp;→&nbsp;팬 5~8번 속도 AO 출력 (`FWU_SF-5_8_SPEED_CONTROL`)의 P1 쓰기 해제 |
| 92 | &emsp;→&nbsp;팬 1번 목표 RPM (`FWU_SF-1.Target_RPM_Set`)의 P1 쓰기 해제 |
| 93 | &emsp;→&nbsp;팬 2번 목표 RPM (`FWU_SF-2.Target_RPM_Set`)의 P1 쓰기 해제 |
| 94 | &emsp;→&nbsp;팬 3번 목표 RPM (`FWU_SF-3.Target_RPM_Set`)의 P1 쓰기 해제 |
| 95 | &emsp;→&nbsp;팬 4번 목표 RPM (`FWU_SF-4.Target_RPM_Set`)의 P1 쓰기 해제 |
| 96 | &emsp;→&nbsp;팬 5번 목표 RPM (`FWU_SF-5.Target_RPM_Set`)의 P1 쓰기 해제 |
| 97 | &emsp;→&nbsp;팬 6번 목표 RPM (`FWU_SF-6.Target_RPM_Set`)의 P1 쓰기 해제 |
| 98 | &emsp;→&nbsp;팬 7번 목표 RPM (`FWU_SF-7.Target_RPM_Set`)의 P1 쓰기 해제 |
| 99 | &emsp;→&nbsp;팬 8번 목표 RPM (`FWU_SF-8.Target_RPM_Set`)의 P1 쓰기 해제 |
| 100 | &emsp;→&nbsp;댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`)의 P1 쓰기 해제 |
| 102 | &emsp;→&nbsp;운전 모드(1 자동, 0 수동) (`VP_FWU_Operation_Mode`) = TRUE(1) 이면 :<br>*[주석] Operation_Mode 1 = 자동, 0 = 수동* |
| 103 | &emsp;&emsp;→&nbsp;운전 명령(BMS) (`VP_FWU_Command`) = ON(1) 이면 : |
| 104 | &emsp;&emsp;&emsp;→&nbsp;*[주석] 운전: 댐퍼부터 열고, 네 댐퍼가 모두 열린 뒤에 팬 속도를 정한다* |
| 105 | &emsp;&emsp;&emsp;→&nbsp;댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`)에 ON(1) 기록 — 기본 우선순위(P5) |
| 106 | &emsp;&emsp;&emsp;→&nbsp;댐퍼 1번 열림 접점 (`FWU_SAD-1_OPEN_STATUS`) = TRUE(1) **그리고** 댐퍼 2번 열림 접점 (`FWU_SAD-2_OPEN_STATUS`) = TRUE(1) **그리고** 댐퍼 3번 열림 접점 (`FWU_SAD-3_OPEN_STATUS`) = TRUE(1) **그리고** 댐퍼 4번 열림 접점 (`FWU_SAD-4_OPEN_STATUS`) = TRUE(1) 이면 : |
| 107 | &emsp;&emsp;&emsp;&emsp;→&nbsp;*[주석] 고정속도: Speed_SP를 최소~최대 속도 안으로 맞춰서 쓴다* |
| 108 | &emsp;&emsp;&emsp;&emsp;→&nbsp;`mbFixed` = TRUE(1) 이면 : |
| 109 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;`Speed` ← [고정속도 설정값(%) (`VP_FWU_Speed_SP`), 팬 최소 속도(%) (`VP_FWU_SF_Speed_Min`)] 중 최댓값 |
| 110 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;`Speed` ← [`Speed`, 팬 최대 속도(%) (`VP_FWU_SF_Speed_Max`)] 중 최솟값 |
| 111 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`)에 `Speed` 기록 — 기본 우선순위(P5) |
| 112 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RAT_LOOP`(1) 누적값 초기화 |
| 113 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RDP_LOOP`(2) 누적값 초기화 |
| 114 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `DELTA_T_LOOP`(3) 누적값 초기화 |
| 115 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `CZT_LOOP`(4) 누적값 초기화 |
| 116 | &emsp;&emsp;&emsp;&emsp;→&nbsp;108행 조건이 성립하지 않으면 : |
| 117 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 119 | &emsp;&emsp;&emsp;&emsp;→&nbsp;*[주석] LOOP2(방향, 현재값, 출력, 목표값, P, I, D, 샘플링(초), 시작 출력, 최소, 최대, 루프 번호, 데드밴드)* |
| 120 | &emsp;&emsp;&emsp;&emsp;→&nbsp;*[주석] RAT 기준: RAT가 목표보다 높으면 팬을 올린다 (DEC)* |
| 121 | &emsp;&emsp;&emsp;&emsp;→&nbsp;`mbFixed` = FALSE(0) **그리고** 1 ≤ `SF_CONTROL_SELECT`(설정값) < 2 이면 : |
| 122 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 제어(LOOP2) — 방향 DEC: 현재값이 목표보다 높으면 출력을 올리는 방향. 현재값 = 환기 온도(RAT) 센서값 (`FWU_RAT`), 출력 = 팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`), 목표값 = 환기 온도 목표값 (`VP_FWU_RAT_SP`), P = `RAT_PGAIN`(설정값), I = `RAT_IGAIN`(설정값), D = 0, 샘플링 = 0, 시작 출력 = 60, 출력 범위 = 팬 최소 속도(%) (`VP_FWU_SF_Speed_Min`) ~ 팬 최대 속도(%) (`VP_FWU_SF_Speed_Max`), 루프 번호 = `RAT_LOOP`(1), 데드밴드 = 0 |
| 123 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RDP_LOOP`(2) 누적값 초기화 |
| 124 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `DELTA_T_LOOP`(3) 누적값 초기화 |
| 125 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `CZT_LOOP`(4) 누적값 초기화 |
| 126 | &emsp;&emsp;&emsp;&emsp;→&nbsp;121행 조건이 성립하지 않으면 : |
| 127 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 129 | &emsp;&emsp;&emsp;&emsp;→&nbsp;*[주석] RDP 기준: 차압이 목표보다 낮으면 팬을 올린다 (INC)* |
| 130 | &emsp;&emsp;&emsp;&emsp;→&nbsp;`mbFixed` = FALSE(0) **그리고** `mbBMSFail` = FALSE(0) **그리고** 2 ≤ `SF_CONTROL_SELECT`(설정값) < 3 이면 : |
| 131 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 제어(LOOP2) — 방향 INC: 현재값이 목표보다 낮으면 출력을 올리는 방향. 현재값 = 룸 차압 제어용 값(PV) (`VP_FWU_RDP_PV`), 출력 = 팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`), 목표값 = 룸 차압 목표값 (`VP_FWU_RDP_SP`), P = `RDP_PGAIN`(설정값), I = `RDP_IGAIN`(설정값), D = 0, 샘플링 = 0, 시작 출력 = 60, 출력 범위 = 팬 최소 속도(%) (`VP_FWU_SF_Speed_Min`) ~ 팬 최대 속도(%) (`VP_FWU_SF_Speed_Max`), 루프 번호 = `RDP_LOOP`(2), 데드밴드 = 0 |
| 132 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RAT_LOOP`(1) 누적값 초기화 |
| 133 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `DELTA_T_LOOP`(3) 누적값 초기화 |
| 134 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `CZT_LOOP`(4) 누적값 초기화 |
| 135 | &emsp;&emsp;&emsp;&emsp;→&nbsp;130행 조건이 성립하지 않으면 : |
| 136 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 138 | &emsp;&emsp;&emsp;&emsp;→&nbsp;*[주석] ΔT 기준* |
| 139 | &emsp;&emsp;&emsp;&emsp;→&nbsp;`mbFixed` = FALSE(0) **그리고** 3 ≤ `SF_CONTROL_SELECT`(설정값) < 4 이면 : |
| 140 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 제어(LOOP2) — 방향 DEC: 현재값이 목표보다 높으면 출력을 올리는 방향. 현재값 = ΔT(RAT-SAT) 현재값 (`VP_FWU_DeltaT_PV`), 출력 = 팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`), 목표값 = ΔT 목표값 (`VP_FWU_DeltaT_SP`), P = `DELTAT_PGAIN`(설정값), I = `DELTAT_IGAIN`(설정값), D = 0, 샘플링 = 0, 시작 출력 = 60, 출력 범위 = 팬 최소 속도(%) (`VP_FWU_SF_Speed_Min`) ~ 팬 최대 속도(%) (`VP_FWU_SF_Speed_Max`), 루프 번호 = `DELTA_T_LOOP`(3), 데드밴드 = 0 |
| 141 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RAT_LOOP`(1) 누적값 초기화 |
| 142 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RDP_LOOP`(2) 누적값 초기화 |
| 143 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `CZT_LOOP`(4) 누적값 초기화 |
| 144 | &emsp;&emsp;&emsp;&emsp;→&nbsp;139행 조건이 성립하지 않으면 : |
| 145 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 147 | &emsp;&emsp;&emsp;&emsp;→&nbsp;*[주석] CZT 기준: 존 온도가 목표보다 높으면 팬을 올린다 (DEC)* |
| 148 | &emsp;&emsp;&emsp;&emsp;→&nbsp;`mbFixed` = FALSE(0) **그리고** `mbBMSFail` = FALSE(0) **그리고** 4 ≤ `SF_CONTROL_SELECT`(설정값) < 5 이면 : |
| 149 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 제어(LOOP2) — 방향 DEC: 현재값이 목표보다 높으면 출력을 올리는 방향. 현재값 = 냉복도 온도 제어용 값(PV) (`VP_FWU_CZT_PV`), 출력 = 팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`), 목표값 = 냉복도 온도 목표값 (`VP_FWU_CZT_SP`), P = `CZT_PGAIN`(설정값), I = `CZT_IGAIN`(설정값), D = 0, 샘플링 = 0, 시작 출력 = 60, 출력 범위 = 팬 최소 속도(%) (`VP_FWU_SF_Speed_Min`) ~ 팬 최대 속도(%) (`VP_FWU_SF_Speed_Max`), 루프 번호 = `CZT_LOOP`(4), 데드밴드 = 0 |
| 150 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RAT_LOOP`(1) 누적값 초기화 |
| 151 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RDP_LOOP`(2) 누적값 초기화 |
| 152 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `DELTA_T_LOOP`(3) 누적값 초기화 |
| 153 | &emsp;&emsp;&emsp;&emsp;→&nbsp;148행 조건이 성립하지 않으면 : |
| 154 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 156 | &emsp;&emsp;&emsp;&emsp;→&nbsp;*[주석] 상위 통신 끊김: 설정이 '최대 속도'이거나 지금 속도가 최소보다 낮으면 최대 속도로 올린다* |
| 157 | &emsp;&emsp;&emsp;&emsp;→&nbsp;`mbBMSFail` = TRUE(1) 이면 : |
| 158 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;상위 통신 끊김 시 운전 방식 설정(1 최대 속도, 0 마지막 속도) (`VP_FWU_BMS_Comm_Fail_Mode`) = TRUE(1) **또는** 팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`) < 팬 최소 속도(%) (`VP_FWU_SF_Speed_Min`) 이면 :<br>*[주석] Comm_Fail_Mode 1 = 최대 속도, 0 = 마지막 속도 유지* |
| 159 | &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`)에 팬 최대 속도(%) (`VP_FWU_SF_Speed_Max`) 값을 그대로 복사 — 기본 우선순위(P5) |
| 160 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;158행 조건이 성립하지 않으면 : |
| 161 | &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) — 마지막 팬 속도 유지 |
| 162 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RAT_LOOP`(1) 누적값 초기화 |
| 163 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RDP_LOOP`(2) 누적값 초기화 |
| 164 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `DELTA_T_LOOP`(3) 누적값 초기화 |
| 165 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `CZT_LOOP`(4) 누적값 초기화 |
| 166 | &emsp;&emsp;&emsp;&emsp;→&nbsp;157행 조건이 성립하지 않으면 : |
| 167 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 168 | &emsp;&emsp;&emsp;→&nbsp;106행 조건이 성립하지 않으면 : |
| 169 | &emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) — 댐퍼가 다 열릴 때까지 팬 속도는 그대로 둔다 |
| 171 | &emsp;&emsp;&emsp;→&nbsp;*[주석] 운전 명령 중인데 네 댐퍼가 모두 닫혀 있으면 PI를 초기화하고 속도를 0으로* |
| 172 | &emsp;&emsp;&emsp;→&nbsp;댐퍼 1번 닫힘 접점 (`FWU_SAD-1_CLOSE_STATUS`) = TRUE(1) **그리고** 댐퍼 2번 닫힘 접점 (`FWU_SAD-2_CLOSE_STATUS`) = TRUE(1) **그리고** 댐퍼 3번 닫힘 접점 (`FWU_SAD-3_CLOSE_STATUS`) = TRUE(1) **그리고** 댐퍼 4번 닫힘 접점 (`FWU_SAD-4_CLOSE_STATUS`) = TRUE(1) 이면 : |
| 173 | &emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RAT_LOOP`(1) 누적값 초기화 |
| 174 | &emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RDP_LOOP`(2) 누적값 초기화 |
| 175 | &emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `DELTA_T_LOOP`(3) 누적값 초기화 |
| 176 | &emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `CZT_LOOP`(4) 누적값 초기화 |
| 177 | &emsp;&emsp;&emsp;&emsp;→&nbsp;팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`)에 0 기록 — 기본 우선순위(P5) |
| 178 | &emsp;&emsp;&emsp;→&nbsp;172행 조건이 성립하지 않으면 : |
| 179 | &emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 181 | &emsp;&emsp;→&nbsp;103행 조건이 성립하지 않으면 : |
| 182 | &emsp;&emsp;&emsp;→&nbsp;*[주석] 정지 명령: 밸브가 다 닫힌 뒤 팬을 세우고, 팬이 멈춘 뒤 댐퍼를 닫는다* |
| 183 | &emsp;&emsp;&emsp;→&nbsp;PI 루프 `RAT_LOOP`(1) 누적값 초기화 |
| 184 | &emsp;&emsp;&emsp;→&nbsp;PI 루프 `RDP_LOOP`(2) 누적값 초기화 |
| 185 | &emsp;&emsp;&emsp;→&nbsp;PI 루프 `DELTA_T_LOOP`(3) 누적값 초기화 |
| 186 | &emsp;&emsp;&emsp;→&nbsp;PI 루프 `CZT_LOOP`(4) 누적값 초기화 |
| 187 | &emsp;&emsp;&emsp;→&nbsp;네 밸브 모두 닫힘 표시 (`VP_FWU_PICV_All_Closed`) = TRUE(1) 이면 : |
| 188 | &emsp;&emsp;&emsp;&emsp;→&nbsp;팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`)에 0 기록 — 기본 우선순위(P5) |
| 189 | &emsp;&emsp;&emsp;→&nbsp;187행 조건이 성립하지 않으면 : |
| 190 | &emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 191 | &emsp;&emsp;&emsp;→&nbsp;팬 운전 상태 (`VP_FWU_SF_Status`) = OFF(0) 이면 : |
| 192 | &emsp;&emsp;&emsp;&emsp;→&nbsp;댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`)에 OFF(0) 기록 — 기본 우선순위(P5) |
| 193 | &emsp;&emsp;&emsp;→&nbsp;191행 조건이 성립하지 않으면 : |
| 194 | &emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 195 | &emsp;&emsp;→&nbsp;팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`)에 현재 값을 그대로 기록 — 우선순위 P11 |
| 196 | &emsp;&emsp;→&nbsp;댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`)에 현재 값을 그대로 기록 — 우선순위 P11 |
| 197 | &emsp;→&nbsp;102행 조건이 성립하지 않으면 : |
| 198 | &emsp;&emsp;→&nbsp;*[주석] 수동 모드: 로직이 쓴 P5를 내려놓아 사람이 넣은 값이 적용되게 한다* |
| 199 | &emsp;&emsp;→&nbsp;PI 루프 `RAT_LOOP`(1) 누적값 초기화 |
| 200 | &emsp;&emsp;→&nbsp;PI 루프 `RDP_LOOP`(2) 누적값 초기화 |
| 201 | &emsp;&emsp;→&nbsp;PI 루프 `DELTA_T_LOOP`(3) 누적값 초기화 |
| 202 | &emsp;&emsp;→&nbsp;PI 루프 `CZT_LOOP`(4) 누적값 초기화 |
| 203 | &emsp;&emsp;→&nbsp;팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`)의 P5 쓰기 해제 |
| 204 | &emsp;&emsp;→&nbsp;댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`)의 P5 쓰기 해제 |
| 205 | 88행 조건이 성립하지 않으면 : |
| 206 | &emsp;→&nbsp;*[주석] 비상정지: 운전 명령을 끄고 팬 출력을 P1으로 0으로 누른다. 댐퍼는 팬이 멈춘 뒤 닫는다* |
| 207 | &emsp;→&nbsp;운전 명령(BMS) (`VP_FWU_Command`)에 OFF(0) 기록 — 우선순위 P11 |
| 208 | &emsp;→&nbsp;운전 명령(HMI) (`VP_FWU_Command_HMI`)에 OFF(0) 기록 — 우선순위 P11 |
| 209 | &emsp;→&nbsp;PI 루프 `RAT_LOOP`(1) 누적값 초기화 |
| 210 | &emsp;→&nbsp;PI 루프 `RDP_LOOP`(2) 누적값 초기화 |
| 211 | &emsp;→&nbsp;PI 루프 `DELTA_T_LOOP`(3) 누적값 초기화 |
| 212 | &emsp;→&nbsp;PI 루프 `CZT_LOOP`(4) 누적값 초기화 |
| 213 | &emsp;→&nbsp;팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`)에 0 기록 — 기본 우선순위(P5) |
| 214 | &emsp;→&nbsp;팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`)에 0 기록 — 우선순위 P11 |
| 215 | &emsp;→&nbsp;팬 운전 상태 (`VP_FWU_SF_Status`) = OFF(0) 이면 : |
| 216 | &emsp;&emsp;→&nbsp;댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`)에 OFF(0) 기록 — 기본 우선순위(P5) |
| 217 | &emsp;&emsp;→&nbsp;댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`)에 OFF(0) 기록 — 우선순위 P11 |
| 218 | &emsp;&emsp;→&nbsp;댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`)에 OFF(0) 기록 — 우선순위 P1 |
| 219 | &emsp;→&nbsp;215행 조건이 성립하지 않으면 : |
| 220 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 221 | &emsp;→&nbsp;팬 1~4번 속도 AO 출력 (`FWU_SF-1_4_SPEED_CONTROL`)에 0 기록 — 우선순위 P1 |
| 222 | &emsp;→&nbsp;팬 5~8번 속도 AO 출력 (`FWU_SF-5_8_SPEED_CONTROL`)에 0 기록 — 우선순위 P1 |
| 223 | &emsp;→&nbsp;팬 1번 목표 RPM (`FWU_SF-1.Target_RPM_Set`)에 0 기록 — 우선순위 P1 |
| 224 | &emsp;→&nbsp;팬 2번 목표 RPM (`FWU_SF-2.Target_RPM_Set`)에 0 기록 — 우선순위 P1 |
| 225 | &emsp;→&nbsp;팬 3번 목표 RPM (`FWU_SF-3.Target_RPM_Set`)에 0 기록 — 우선순위 P1 |
| 226 | &emsp;→&nbsp;팬 4번 목표 RPM (`FWU_SF-4.Target_RPM_Set`)에 0 기록 — 우선순위 P1 |
| 227 | &emsp;→&nbsp;팬 5번 목표 RPM (`FWU_SF-5.Target_RPM_Set`)에 0 기록 — 우선순위 P1 |
| 228 | &emsp;→&nbsp;팬 6번 목표 RPM (`FWU_SF-6.Target_RPM_Set`)에 0 기록 — 우선순위 P1 |
| 229 | &emsp;→&nbsp;팬 7번 목표 RPM (`FWU_SF-7.Target_RPM_Set`)에 0 기록 — 우선순위 P1 |
| 230 | &emsp;→&nbsp;팬 8번 목표 RPM (`FWU_SF-8.Target_RPM_Set`)에 0 기록 — 우선순위 P1 |

<a id="section-6"></a>

## 232~250행 · 팬 운전 명령: 속도 값이 있으면 8대 모두 운전

| 행 | 해석 |
|---:|---|
| 232 | *[주석] 팬 운전 명령: 속도 값이 있으면 8대 모두 운전* |
| 233 | 팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`) > 0 이면 : |
| 234 | &emsp;→&nbsp;팬 1번 운전 명령 (`FWU_SF-1.Run_Command`)에 ON(1) 기록 — 기본 우선순위(P5) |
| 235 | &emsp;→&nbsp;팬 2번 운전 명령 (`FWU_SF-2.Run_Command`)에 ON(1) 기록 — 기본 우선순위(P5) |
| 236 | &emsp;→&nbsp;팬 3번 운전 명령 (`FWU_SF-3.Run_Command`)에 ON(1) 기록 — 기본 우선순위(P5) |
| 237 | &emsp;→&nbsp;팬 4번 운전 명령 (`FWU_SF-4.Run_Command`)에 ON(1) 기록 — 기본 우선순위(P5) |
| 238 | &emsp;→&nbsp;팬 5번 운전 명령 (`FWU_SF-5.Run_Command`)에 ON(1) 기록 — 기본 우선순위(P5) |
| 239 | &emsp;→&nbsp;팬 6번 운전 명령 (`FWU_SF-6.Run_Command`)에 ON(1) 기록 — 기본 우선순위(P5) |
| 240 | &emsp;→&nbsp;팬 7번 운전 명령 (`FWU_SF-7.Run_Command`)에 ON(1) 기록 — 기본 우선순위(P5) |
| 241 | &emsp;→&nbsp;팬 8번 운전 명령 (`FWU_SF-8.Run_Command`)에 ON(1) 기록 — 기본 우선순위(P5) |
| 242 | 233행 조건이 성립하지 않으면 : |
| 243 | &emsp;→&nbsp;팬 1번 운전 명령 (`FWU_SF-1.Run_Command`)에 OFF(0) 기록 — 기본 우선순위(P5) |
| 244 | &emsp;→&nbsp;팬 2번 운전 명령 (`FWU_SF-2.Run_Command`)에 OFF(0) 기록 — 기본 우선순위(P5) |
| 245 | &emsp;→&nbsp;팬 3번 운전 명령 (`FWU_SF-3.Run_Command`)에 OFF(0) 기록 — 기본 우선순위(P5) |
| 246 | &emsp;→&nbsp;팬 4번 운전 명령 (`FWU_SF-4.Run_Command`)에 OFF(0) 기록 — 기본 우선순위(P5) |
| 247 | &emsp;→&nbsp;팬 5번 운전 명령 (`FWU_SF-5.Run_Command`)에 OFF(0) 기록 — 기본 우선순위(P5) |
| 248 | &emsp;→&nbsp;팬 6번 운전 명령 (`FWU_SF-6.Run_Command`)에 OFF(0) 기록 — 기본 우선순위(P5) |
| 249 | &emsp;→&nbsp;팬 7번 운전 명령 (`FWU_SF-7.Run_Command`)에 OFF(0) 기록 — 기본 우선순위(P5) |
| 250 | &emsp;→&nbsp;팬 8번 운전 명령 (`FWU_SF-8.Run_Command`)에 OFF(0) 기록 — 기본 우선순위(P5) |

<a id="section-7"></a>

## 252~288행 · 팬 속도 출력 (5초마다)

> 평소에는 Modbus로 목표 RPM을 보내고, 팬 통신이 끊기면 AO(아날로그)로 바꿔 보낸다

| 행 | 해석 |
|---:|---|
| 252 | *[주석] 팬 속도 출력 (5초마다)* |
| 253 | *[주석] 평소에는 Modbus로 목표 RPM을 보내고, 팬 통신이 끊기면 AO(아날로그)로 바꿔 보낸다* |
| 254 | 타이머 `SPEED_OUTPUT_TIMER`(1번: 팬 속도를 마지막으로 내보낸 뒤 지난 시간) 경과시간 > 5 이면 :<br>*[주석] 5초* |
| 255 | &emsp;→&nbsp;`SFSpeed` ← 팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`) 값 읽기 |
| 256 | &emsp;→&nbsp;`SFMaxRPM` ← 팬 최대 RPM(계산값) (`VP_FWU_SF_Max_RPM`) 값 읽기<br>*[주석] Initialization이 설계 RPM과 비율로 계산해 둔 값* |
| 257 | &emsp;→&nbsp;`SFRPMSet` ← [(`SFSpeed` × `SFMaxRPM`) ÷ 100, `SFMaxRPM`] 중 최솟값 |
| 258 | &emsp;→&nbsp;`SFAOSet` ← (`SFSpeed` × `SFMaxRPM`) ÷ [팬 정격 최대 RPM (`VP_FWU_SF_Rated_Max_RPM`), 1] 중 최댓값 |
| 260 | &emsp;→&nbsp;팬 통신 이상 종합 (`VP_FWU_SF_Comm_Fault`) = TRUE(1) 이면 : |
| 261 | &emsp;&emsp;→&nbsp;팬 1~4번 속도 AO 출력 (`FWU_SF-1_4_SPEED_CONTROL`)에 `SFAOSet` 기록 — 기본 우선순위(P5) |
| 262 | &emsp;&emsp;→&nbsp;팬 5~8번 속도 AO 출력 (`FWU_SF-5_8_SPEED_CONTROL`)에 `SFAOSet` 기록 — 기본 우선순위(P5) |
| 263 | &emsp;&emsp;→&nbsp;팬 1번 목표 RPM (`FWU_SF-1.Target_RPM_Set`)에 0 기록 — 기본 우선순위(P5) |
| 264 | &emsp;&emsp;→&nbsp;팬 2번 목표 RPM (`FWU_SF-2.Target_RPM_Set`)에 0 기록 — 기본 우선순위(P5) |
| 265 | &emsp;&emsp;→&nbsp;팬 3번 목표 RPM (`FWU_SF-3.Target_RPM_Set`)에 0 기록 — 기본 우선순위(P5) |
| 266 | &emsp;&emsp;→&nbsp;팬 4번 목표 RPM (`FWU_SF-4.Target_RPM_Set`)에 0 기록 — 기본 우선순위(P5) |
| 267 | &emsp;&emsp;→&nbsp;팬 5번 목표 RPM (`FWU_SF-5.Target_RPM_Set`)에 0 기록 — 기본 우선순위(P5) |
| 268 | &emsp;&emsp;→&nbsp;팬 6번 목표 RPM (`FWU_SF-6.Target_RPM_Set`)에 0 기록 — 기본 우선순위(P5) |
| 269 | &emsp;&emsp;→&nbsp;팬 7번 목표 RPM (`FWU_SF-7.Target_RPM_Set`)에 0 기록 — 기본 우선순위(P5) |
| 270 | &emsp;&emsp;→&nbsp;팬 8번 목표 RPM (`FWU_SF-8.Target_RPM_Set`)에 0 기록 — 기본 우선순위(P5) |
| 271 | &emsp;→&nbsp;260행 조건이 성립하지 않으면 : |
| 272 | &emsp;&emsp;→&nbsp;팬 1~4번 속도 AO 출력 (`FWU_SF-1_4_SPEED_CONTROL`)에 0 기록 — 기본 우선순위(P5) |
| 273 | &emsp;&emsp;→&nbsp;팬 5~8번 속도 AO 출력 (`FWU_SF-5_8_SPEED_CONTROL`)에 0 기록 — 기본 우선순위(P5) |
| 274 | &emsp;&emsp;→&nbsp;팬 1번 목표 RPM (`FWU_SF-1.Target_RPM_Set`)에 `SFRPMSet` 기록 — 기본 우선순위(P5) |
| 275 | &emsp;&emsp;→&nbsp;팬 2번 목표 RPM (`FWU_SF-2.Target_RPM_Set`)에 `SFRPMSet` 기록 — 기본 우선순위(P5) |
| 276 | &emsp;&emsp;→&nbsp;팬 3번 목표 RPM (`FWU_SF-3.Target_RPM_Set`)에 `SFRPMSet` 기록 — 기본 우선순위(P5) |
| 277 | &emsp;&emsp;→&nbsp;팬 4번 목표 RPM (`FWU_SF-4.Target_RPM_Set`)에 `SFRPMSet` 기록 — 기본 우선순위(P5) |
| 278 | &emsp;&emsp;→&nbsp;팬 5번 목표 RPM (`FWU_SF-5.Target_RPM_Set`)에 `SFRPMSet` 기록 — 기본 우선순위(P5) |
| 279 | &emsp;&emsp;→&nbsp;팬 6번 목표 RPM (`FWU_SF-6.Target_RPM_Set`)에 `SFRPMSet` 기록 — 기본 우선순위(P5) |
| 280 | &emsp;&emsp;→&nbsp;팬 7번 목표 RPM (`FWU_SF-7.Target_RPM_Set`)에 `SFRPMSet` 기록 — 기본 우선순위(P5) |
| 281 | &emsp;&emsp;→&nbsp;팬 8번 목표 RPM (`FWU_SF-8.Target_RPM_Set`)에 `SFRPMSet` 기록 — 기본 우선순위(P5) |
| 283 | &emsp;→&nbsp;타이머 `SPEED_OUTPUT_TIMER`(1번: 팬 속도를 마지막으로 내보낸 뒤 지난 시간)를 0초로 초기화 |
| 284 | 254행 조건이 성립하지 않으면 : |
| 285 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 287 | *[주석] JSY 2026-11-23 수정 구간 끝. 주제 = Coding Rule 적용(매크로 상수, 설정값 상수, 변수명, if-else 짝 맞춤, 주석)* |
| 288 | *[주석] LJH 2026-11-17 수정 구간 끝. 주제 = 온도 고장 대체운전과 네 밸브 정지 연계* |
