# SF Control 줄별 해석

> **대상 코드** : `fwu_v3/Logic/SF Control.py` (297 줄)  
> **기준** : `sy 브랜치 2026-11-23 (naming rule·관제점 이름 변경 반영)`  
> **행** = 코드 줄 번호 (빈 줄은 생략)  
> **표기** : `→` 들여쓰기 단계 · *[주석]* 코드 안 주석 · `이름` 코드 안 상수·변수 · **※** 읽을 때 주의할 점

팬 제어 기준(고정속도·RAT·RDP·ΔT·CZT)에 따라 팬 속도를 정하고, 댐퍼·밸브와 연계해 기동과 정지를 한다. 5초마다 팬 목표 RPM(팬 통신 이상 시 AO)을 내보낸다.

**목차**

- [1~39행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수](#section-1)
- [41~56행 · 고정속도로 돌릴지 판단](#section-2)
- [58~67행 · 온도 센서 고장 시 대체 운전: RAT 모드는 RAT 고장, ΔT 모드는 RAT·SAT 중 하나라도 고장이면 고정속도](#section-3)
- [69~86행 · 상위(BMS/PLC) 통신이 끊겼을 때](#section-4)
- [88~239행 · 비상정지가 아닐 때](#section-5)
- [241~259행 · 팬 운전 명령: 속도 값이 있으면 8대 모두 운전](#section-6)
- [261~297행 · 팬 속도 출력 (5초마다)](#section-7)

**※ 공통 표기**: 매크로 상수 TRUE·ON·SET·TMR_READ·DEC = 1, FALSE·OFF·CLEAR·TMR_CLEAR·INC = 0. `SECTIMER(타이머, TMR_CLEAR)`는 타이머를 0초로 초기화, `SECTIMER(타이머, TMR_READ)`는 경과시간 확인이다. P번호가 없는 쓰기(`WRITEPOINT`)는 기본 우선순위 P5를 쓴다. 조건이 거짓이라고 관제점이 저절로 0이 되지는 않는다. 해당 분기에 쓰기가 없으면 이전 값이 남는다. 대문자 이름은 상수, `m`으로 시작하는 이름은 이 파일의 전역변수, `b`가 붙은 이름은 참/거짓 값이다.

<a id="section-1"></a>

## 1~39행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수

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
| 25 | 설정값 상수 `SAD_INSTALLED`: 댐퍼 설치 여부 설정(0 없음, 1 있음) (`VP_FWU_SAD_Installed`) 값을 읽어 둠<br>*[주석] 댐퍼 설치 여부 (옵션 부품). 0 = 없음, 1 = 있음* |
| 27 | *[주석] 타이머 정의* |
| 28 | 타이머 번호 상수 `SPEED_OUTPUT_TIMER` = 1번<br>*[주석] 팬 속도를 마지막으로 내보낸 뒤 지난 시간* |
| 30 | *[주석] 전역변수 선언* |
| 31 | 전역변수 `mbFixed` 선언, 처음 값 = FALSE(0)<br>*[주석] TRUE면 PI 제어 대신 고정속도(Speed_SP)로 돈다* |
| 32 | 전역변수 `mbBMSFail` 선언, 처음 값 = FALSE(0)<br>*[주석] TRUE면 상위 통신이 끊겨 Comm_Fail_Mode 설정대로 돈다* |
| 34 | *[주석] 모드 UI는 정수 0~4만 전송. 직접 쓰기를 허용하면 별도 값 검증 필요.* |
| 35 | *[주석] 수동 속도는 코드 제한 없음. HMI에서 정지 0 또는 최소~최대 속도만 허용.* |
| 36 | *[주석] HMI에서 최소 <= 최대를 확인할 것. 최소 속도 기본값 20% (QTS RFP 2.3.D.3, JSY 2026-11-24 30%→20%).* |
| 37 | *[주석] ΔT 목표 -2℃는 SMX01 기준 임시값. 양의 RAT-SAT 운전에서 최대속도에 머물 수 있어 재확인.* |
| 38 | *[주석] 정상 정지는 네 밸브 닫힘까지 대기. 미폐쇄 제한시간/대체 정지 정책은 추후 검토.* |
| 39 | *[주석] 팬 통신 이상 시 전체 AO 전환. 새 팬의 Run·AO/RPM 우선권·환산·복구 동작 확인.* |

<a id="section-2"></a>

## 41~56행 · 고정속도로 돌릴지 판단

> 고정속도(0)를 골랐거나, 고른 제어 기준의 센서값을 쓸 수 없으면 고정속도로 돈다

| 행 | 해석 |
|---:|---|
| 41 | *[주석] 고정속도로 돌릴지 판단* |
| 42 | *[주석] 고정속도(0)를 골랐거나, 고른 제어 기준의 센서값을 쓸 수 없으면 고정속도로 돈다* |
| 43 | 0 ≤ `SF_CONTROL_SELECT`(설정값) < 1 이면 : |
| 44 | &emsp;→&nbsp;`mbFixed` ← TRUE(1) |
| 45 | 43행 조건이 성립하지 않으면 : |
| 46 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 48 | 2 ≤ `SF_CONTROL_SELECT`(설정값) < 3 **그리고** 룸 차압 제어용 값 유효 표시 (`VP_FWU_RDP_PV_Valid`) = FALSE(0) 이면 : |
| 49 | &emsp;→&nbsp;`mbFixed` ← TRUE(1) |
| 50 | 48행 조건이 성립하지 않으면 : |
| 51 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 53 | 4 ≤ `SF_CONTROL_SELECT`(설정값) < 5 **그리고** 냉복도 온도 제어용 값 유효 표시 (`VP_FWU_CZT_PV_Valid`) = FALSE(0) 이면 : |
| 54 | &emsp;→&nbsp;`mbFixed` ← TRUE(1) |
| 55 | 53행 조건이 성립하지 않으면 : |
| 56 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |

<a id="section-3"></a>

## 58~67행 · 온도 센서 고장 시 대체 운전: RAT 모드는 RAT 고장, ΔT 모드는 RAT·SAT 중 하나라도 고장이면 고정속도

| 행 | 해석 |
|---:|---|
| 58 | *[주석] 온도 센서 고장 시 대체 운전: RAT 모드는 RAT 고장, ΔT 모드는 RAT·SAT 중 하나라도 고장이면 고정속도* |
| 59 | 1 ≤ `SF_CONTROL_SELECT`(설정값) < 2 **그리고** 환기 온도(RAT) 센서 고장 알람 (`VP_FWU_RAT_Failure_Alarm`) = TRUE(1) 이면 : |
| 60 | &emsp;→&nbsp;`mbFixed` ← TRUE(1) |
| 61 | 59행 조건이 성립하지 않으면 : |
| 62 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 64 | 3 ≤ `SF_CONTROL_SELECT`(설정값) < 4 **그리고** (환기 온도(RAT) 센서 고장 알람 (`VP_FWU_RAT_Failure_Alarm`) = TRUE(1) **또는** 급기 온도(SAT) 센서 고장 알람 (`VP_FWU_SAT_Failure_Alarm`) = TRUE(1)) 이면 : |
| 65 | &emsp;→&nbsp;`mbFixed` ← TRUE(1) |
| 66 | 64행 조건이 성립하지 않으면 : |
| 67 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |

<a id="section-4"></a>

## 69~86행 · 상위(BMS/PLC) 통신이 끊겼을 때

> 상위 값을 쓰는 RDP·CZT 모드, 또는 원격 선택 상태의 고정속도 모드는 Comm_Fail_Mode 설정을 따른다

| 행 | 해석 |
|---:|---|
| 69 | *[주석] 상위(BMS/PLC) 통신이 끊겼을 때* |
| 70 | *[주석] 상위 값을 쓰는 RDP·CZT 모드, 또는 원격 선택 상태의 고정속도 모드는 Comm_Fail_Mode 설정을 따른다* |
| 71 | 상위 통신 감시 사용 설정 (`VP_FWU_Upper_Comm_Enable`) = TRUE(1) **그리고** 상위(BMS/PLC) 통신 이상 (`VP_FWU_BMS_PLC_Comm_Fault`) = TRUE(1) 이면 : |
| 72 | &emsp;→&nbsp;2 ≤ `SF_CONTROL_SELECT`(설정값) < 3 **또는** 4 ≤ `SF_CONTROL_SELECT`(설정값) < 5 이면 : |
| 73 | &emsp;&emsp;→&nbsp;`mbBMSFail` ← TRUE(1) |
| 74 | &emsp;→&nbsp;72행 조건이 성립하지 않으면 : |
| 75 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 76 | &emsp;→&nbsp;0 ≤ `SF_CONTROL_SELECT`(설정값) < 1 **그리고** 원격(BMS) 선택 입력(DI) (`REMOTE_SELECTION`) = TRUE(1) 이면 : |
| 77 | &emsp;&emsp;→&nbsp;`mbBMSFail` ← TRUE(1) |
| 78 | &emsp;→&nbsp;76행 조건이 성립하지 않으면 : |
| 79 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 80 | 71행 조건이 성립하지 않으면 : |
| 81 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 83 | `mbBMSFail` = TRUE(1) 이면 : |
| 84 | &emsp;→&nbsp;`mbFixed` ← FALSE(0) |
| 85 | 83행 조건이 성립하지 않으면 : |
| 86 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |

<a id="section-5"></a>

## 88~239행 · 비상정지가 아닐 때

| 행 | 해석 |
|---:|---|
| 88 | *[주석] 비상정지가 아닐 때* |
| 89 | 비상정지 입력(DI) (`FWU_EMERGENCY`) = FALSE(0) 이면 : |
| 90 | &emsp;→&nbsp;*[주석] 비상정지 때 걸어 둔 P1 해제* |
| 91 | &emsp;→&nbsp;팬 1~4번 속도 AO 출력 (`FWU_SF-1_4_SPEED_CONTROL`)의 P1 쓰기 해제<br>*[주석] FWU_SF-1_8_SPEED_CONTROL로 합쳐도 됨 (기존 배선이 1~4, 5~8로 나뉘어 있음)* |
| 92 | &emsp;→&nbsp;팬 5~8번 속도 AO 출력 (`FWU_SF-5_8_SPEED_CONTROL`)의 P1 쓰기 해제 |
| 93 | &emsp;→&nbsp;팬 1번 목표 RPM (`FWU_SF-1.Target_RPM_Set`)의 P1 쓰기 해제 |
| 94 | &emsp;→&nbsp;팬 2번 목표 RPM (`FWU_SF-2.Target_RPM_Set`)의 P1 쓰기 해제 |
| 95 | &emsp;→&nbsp;팬 3번 목표 RPM (`FWU_SF-3.Target_RPM_Set`)의 P1 쓰기 해제 |
| 96 | &emsp;→&nbsp;팬 4번 목표 RPM (`FWU_SF-4.Target_RPM_Set`)의 P1 쓰기 해제 |
| 97 | &emsp;→&nbsp;팬 5번 목표 RPM (`FWU_SF-5.Target_RPM_Set`)의 P1 쓰기 해제 |
| 98 | &emsp;→&nbsp;팬 6번 목표 RPM (`FWU_SF-6.Target_RPM_Set`)의 P1 쓰기 해제 |
| 99 | &emsp;→&nbsp;팬 7번 목표 RPM (`FWU_SF-7.Target_RPM_Set`)의 P1 쓰기 해제 |
| 100 | &emsp;→&nbsp;팬 8번 목표 RPM (`FWU_SF-8.Target_RPM_Set`)의 P1 쓰기 해제 |
| 101 | &emsp;→&nbsp;댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`)의 P1 쓰기 해제 |
| 103 | &emsp;→&nbsp;운전 모드(1 자동, 0 수동) (`VP_FWU_Operation_Mode`) = TRUE(1) 이면 :<br>*[주석] Operation_Mode 1 = 자동, 0 = 수동* |
| 104 | &emsp;&emsp;→&nbsp;운전 명령(BMS) (`VP_FWU_Command`) = ON(1) 이면 : |
| 105 | &emsp;&emsp;&emsp;→&nbsp;*[주석] JSY 2026-11-24 수정 구간 시작. 주제 = 댐퍼 설치 여부(옵션 부품) 반영* |
| 106 | &emsp;&emsp;&emsp;→&nbsp;*[주석] 운전: 댐퍼가 있으면 댐퍼부터 열고, 네 댐퍼가 모두 열린 뒤에 팬 속도를 정한다* |
| 107 | &emsp;&emsp;&emsp;→&nbsp;*[주석] 댐퍼가 없으면 댐퍼 명령을 내지 않고(OFF), 열림을 기다리지 않고 바로 팬 속도를 정한다* |
| 108 | &emsp;&emsp;&emsp;→&nbsp;`SAD_INSTALLED`(설정값) = TRUE(1) 이면 : |
| 109 | &emsp;&emsp;&emsp;&emsp;→&nbsp;댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`)에 ON(1) 기록 — 기본 우선순위(P5) |
| 110 | &emsp;&emsp;&emsp;&emsp;→&nbsp;`bSADReady` ← 댐퍼 1번 열림 접점 (`FWU_SAD-1_OPEN_STATUS`) = TRUE(1) **그리고** 댐퍼 2번 열림 접점 (`FWU_SAD-2_OPEN_STATUS`) = TRUE(1) **그리고** 댐퍼 3번 열림 접점 (`FWU_SAD-3_OPEN_STATUS`) = TRUE(1) **그리고** 댐퍼 4번 열림 접점 (`FWU_SAD-4_OPEN_STATUS`) = TRUE(1) 이면 TRUE, 아니면 FALSE<br>*[주석] 네 댐퍼가 모두 열림* |
| 111 | &emsp;&emsp;&emsp;→&nbsp;108행 조건이 성립하지 않으면 : |
| 112 | &emsp;&emsp;&emsp;&emsp;→&nbsp;댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`)에 OFF(0) 기록 — 기본 우선순위(P5) |
| 113 | &emsp;&emsp;&emsp;&emsp;→&nbsp;`bSADReady` ← TRUE(1) |
| 114 | &emsp;&emsp;&emsp;→&nbsp;*[주석] JSY 2026-11-24 수정 구간 끝. 주제 = 댐퍼 설치 여부(옵션 부품) 반영* |
| 115 | &emsp;&emsp;&emsp;→&nbsp;`bSADReady` = TRUE(1) 이면 : |
| 116 | &emsp;&emsp;&emsp;&emsp;→&nbsp;*[주석] 고정속도: Speed_SP를 최소~최대 속도 안으로 맞춰서 쓴다* |
| 117 | &emsp;&emsp;&emsp;&emsp;→&nbsp;`mbFixed` = TRUE(1) 이면 : |
| 118 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;`Speed` ← [고정속도 설정값(%) (`VP_FWU_Speed_SP`), 팬 최소 속도(%) (`VP_FWU_SF_Speed_Min`)] 중 최댓값 |
| 119 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;`Speed` ← [`Speed`, 팬 최대 속도(%) (`VP_FWU_SF_Speed_Max`)] 중 최솟값 |
| 120 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`)에 `Speed` 기록 — 기본 우선순위(P5) |
| 121 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RAT_LOOP`(1) 누적값 초기화 |
| 122 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RDP_LOOP`(2) 누적값 초기화 |
| 123 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `DELTA_T_LOOP`(3) 누적값 초기화 |
| 124 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `CZT_LOOP`(4) 누적값 초기화 |
| 125 | &emsp;&emsp;&emsp;&emsp;→&nbsp;117행 조건이 성립하지 않으면 : |
| 126 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 128 | &emsp;&emsp;&emsp;&emsp;→&nbsp;*[주석] LOOP2(방향, 현재값, 출력, 목표값, P, I, D, 샘플링(초), 시작 출력, 최소, 최대, 루프 번호, 데드밴드)* |
| 129 | &emsp;&emsp;&emsp;&emsp;→&nbsp;*[주석] RAT 기준: RAT가 목표보다 높으면 팬을 올린다 (DEC)* |
| 130 | &emsp;&emsp;&emsp;&emsp;→&nbsp;`mbFixed` = FALSE(0) **그리고** 1 ≤ `SF_CONTROL_SELECT`(설정값) < 2 이면 : |
| 131 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 제어(LOOP2) — 방향 DEC: 현재값이 목표보다 높으면 출력을 올리는 방향. 현재값 = 환기 온도(RAT) 센서값 (`FWU_RAT`), 출력 = 팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`), 목표값 = 환기 온도 목표값 (`VP_FWU_RAT_SP`), P = `RAT_PGAIN`(설정값), I = `RAT_IGAIN`(설정값), D = 0, 샘플링 = 0, 시작 출력 = 60, 출력 범위 = 팬 최소 속도(%) (`VP_FWU_SF_Speed_Min`) ~ 팬 최대 속도(%) (`VP_FWU_SF_Speed_Max`), 루프 번호 = `RAT_LOOP`(1), 데드밴드 = 0 |
| 132 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RDP_LOOP`(2) 누적값 초기화 |
| 133 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `DELTA_T_LOOP`(3) 누적값 초기화 |
| 134 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `CZT_LOOP`(4) 누적값 초기화 |
| 135 | &emsp;&emsp;&emsp;&emsp;→&nbsp;130행 조건이 성립하지 않으면 : |
| 136 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 138 | &emsp;&emsp;&emsp;&emsp;→&nbsp;*[주석] RDP 기준: 차압이 목표보다 낮으면 팬을 올린다 (INC)* |
| 139 | &emsp;&emsp;&emsp;&emsp;→&nbsp;`mbFixed` = FALSE(0) **그리고** `mbBMSFail` = FALSE(0) **그리고** 2 ≤ `SF_CONTROL_SELECT`(설정값) < 3 이면 : |
| 140 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 제어(LOOP2) — 방향 INC: 현재값이 목표보다 낮으면 출력을 올리는 방향. 현재값 = 룸 차압 제어용 값(PV) (`VP_FWU_RDP_PV`), 출력 = 팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`), 목표값 = 룸 차압 목표값 (`VP_FWU_RDP_SP`), P = `RDP_PGAIN`(설정값), I = `RDP_IGAIN`(설정값), D = 0, 샘플링 = 0, 시작 출력 = 60, 출력 범위 = 팬 최소 속도(%) (`VP_FWU_SF_Speed_Min`) ~ 팬 최대 속도(%) (`VP_FWU_SF_Speed_Max`), 루프 번호 = `RDP_LOOP`(2), 데드밴드 = 0 |
| 141 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RAT_LOOP`(1) 누적값 초기화 |
| 142 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `DELTA_T_LOOP`(3) 누적값 초기화 |
| 143 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `CZT_LOOP`(4) 누적값 초기화 |
| 144 | &emsp;&emsp;&emsp;&emsp;→&nbsp;139행 조건이 성립하지 않으면 : |
| 145 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 147 | &emsp;&emsp;&emsp;&emsp;→&nbsp;*[주석] ΔT 기준* |
| 148 | &emsp;&emsp;&emsp;&emsp;→&nbsp;`mbFixed` = FALSE(0) **그리고** 3 ≤ `SF_CONTROL_SELECT`(설정값) < 4 이면 : |
| 149 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 제어(LOOP2) — 방향 DEC: 현재값이 목표보다 높으면 출력을 올리는 방향. 현재값 = ΔT(RAT-SAT) 현재값 (`VP_FWU_DeltaT_PV`), 출력 = 팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`), 목표값 = ΔT 목표값 (`VP_FWU_DeltaT_SP`), P = `DELTAT_PGAIN`(설정값), I = `DELTAT_IGAIN`(설정값), D = 0, 샘플링 = 0, 시작 출력 = 60, 출력 범위 = 팬 최소 속도(%) (`VP_FWU_SF_Speed_Min`) ~ 팬 최대 속도(%) (`VP_FWU_SF_Speed_Max`), 루프 번호 = `DELTA_T_LOOP`(3), 데드밴드 = 0 |
| 150 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RAT_LOOP`(1) 누적값 초기화 |
| 151 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RDP_LOOP`(2) 누적값 초기화 |
| 152 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `CZT_LOOP`(4) 누적값 초기화 |
| 153 | &emsp;&emsp;&emsp;&emsp;→&nbsp;148행 조건이 성립하지 않으면 : |
| 154 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 156 | &emsp;&emsp;&emsp;&emsp;→&nbsp;*[주석] CZT 기준: 존 온도가 목표보다 높으면 팬을 올린다 (DEC)* |
| 157 | &emsp;&emsp;&emsp;&emsp;→&nbsp;`mbFixed` = FALSE(0) **그리고** `mbBMSFail` = FALSE(0) **그리고** 4 ≤ `SF_CONTROL_SELECT`(설정값) < 5 이면 : |
| 158 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 제어(LOOP2) — 방향 DEC: 현재값이 목표보다 높으면 출력을 올리는 방향. 현재값 = 냉복도 온도 제어용 값(PV) (`VP_FWU_CZT_PV`), 출력 = 팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`), 목표값 = 냉복도 온도 목표값 (`VP_FWU_CZT_SP`), P = `CZT_PGAIN`(설정값), I = `CZT_IGAIN`(설정값), D = 0, 샘플링 = 0, 시작 출력 = 60, 출력 범위 = 팬 최소 속도(%) (`VP_FWU_SF_Speed_Min`) ~ 팬 최대 속도(%) (`VP_FWU_SF_Speed_Max`), 루프 번호 = `CZT_LOOP`(4), 데드밴드 = 0 |
| 159 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RAT_LOOP`(1) 누적값 초기화 |
| 160 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RDP_LOOP`(2) 누적값 초기화 |
| 161 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `DELTA_T_LOOP`(3) 누적값 초기화 |
| 162 | &emsp;&emsp;&emsp;&emsp;→&nbsp;157행 조건이 성립하지 않으면 : |
| 163 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 165 | &emsp;&emsp;&emsp;&emsp;→&nbsp;*[주석] 상위 통신 끊김: 설정이 '최대 속도'이거나 지금 속도가 최소보다 낮으면 최대 속도로 올린다* |
| 166 | &emsp;&emsp;&emsp;&emsp;→&nbsp;`mbBMSFail` = TRUE(1) 이면 : |
| 167 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;상위 통신 끊김 시 운전 방식 설정(1 최대 속도, 0 마지막 속도) (`VP_FWU_BMS_Comm_Fail_Mode`) = TRUE(1) **또는** 팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`) < 팬 최소 속도(%) (`VP_FWU_SF_Speed_Min`) 이면 :<br>*[주석] Comm_Fail_Mode 1 = 최대 속도, 0 = 마지막 속도 유지* |
| 168 | &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`)에 팬 최대 속도(%) (`VP_FWU_SF_Speed_Max`) 값을 그대로 복사 — 기본 우선순위(P5) |
| 169 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;167행 조건이 성립하지 않으면 : |
| 170 | &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) — 마지막 팬 속도 유지 |
| 171 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RAT_LOOP`(1) 누적값 초기화 |
| 172 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RDP_LOOP`(2) 누적값 초기화 |
| 173 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `DELTA_T_LOOP`(3) 누적값 초기화 |
| 174 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `CZT_LOOP`(4) 누적값 초기화 |
| 175 | &emsp;&emsp;&emsp;&emsp;→&nbsp;166행 조건이 성립하지 않으면 : |
| 176 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 177 | &emsp;&emsp;&emsp;→&nbsp;115행 조건이 성립하지 않으면 : |
| 178 | &emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) — 댐퍼가 다 열릴 때까지 팬 속도는 그대로 둔다 |
| 180 | &emsp;&emsp;&emsp;→&nbsp;*[주석] 운전 명령 중인데 네 댐퍼가 모두 닫혀 있으면 PI를 초기화하고 속도를 0으로 (댐퍼가 있을 때만)* |
| 181 | &emsp;&emsp;&emsp;→&nbsp;`SAD_INSTALLED`(설정값) = TRUE(1) **그리고** 댐퍼 1번 닫힘 접점 (`FWU_SAD-1_CLOSE_STATUS`) = TRUE(1) **그리고** 댐퍼 2번 닫힘 접점 (`FWU_SAD-2_CLOSE_STATUS`) = TRUE(1) **그리고** 댐퍼 3번 닫힘 접점 (`FWU_SAD-3_CLOSE_STATUS`) = TRUE(1) **그리고** 댐퍼 4번 닫힘 접점 (`FWU_SAD-4_CLOSE_STATUS`) = TRUE(1) 이면 : |
| 182 | &emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RAT_LOOP`(1) 누적값 초기화 |
| 183 | &emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RDP_LOOP`(2) 누적값 초기화 |
| 184 | &emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `DELTA_T_LOOP`(3) 누적값 초기화 |
| 185 | &emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `CZT_LOOP`(4) 누적값 초기화 |
| 186 | &emsp;&emsp;&emsp;&emsp;→&nbsp;팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`)에 0 기록 — 기본 우선순위(P5) |
| 187 | &emsp;&emsp;&emsp;→&nbsp;181행 조건이 성립하지 않으면 : |
| 188 | &emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 190 | &emsp;&emsp;→&nbsp;104행 조건이 성립하지 않으면 : |
| 191 | &emsp;&emsp;&emsp;→&nbsp;*[주석] 정지 명령: 밸브가 다 닫힌 뒤 팬을 세우고, 팬이 멈춘 뒤 댐퍼를 닫는다* |
| 192 | &emsp;&emsp;&emsp;→&nbsp;PI 루프 `RAT_LOOP`(1) 누적값 초기화 |
| 193 | &emsp;&emsp;&emsp;→&nbsp;PI 루프 `RDP_LOOP`(2) 누적값 초기화 |
| 194 | &emsp;&emsp;&emsp;→&nbsp;PI 루프 `DELTA_T_LOOP`(3) 누적값 초기화 |
| 195 | &emsp;&emsp;&emsp;→&nbsp;PI 루프 `CZT_LOOP`(4) 누적값 초기화 |
| 196 | &emsp;&emsp;&emsp;→&nbsp;네 밸브 모두 닫힘 표시 (`VP_FWU_PICV_All_Closed`) = TRUE(1) 이면 : |
| 197 | &emsp;&emsp;&emsp;&emsp;→&nbsp;팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`)에 0 기록 — 기본 우선순위(P5) |
| 198 | &emsp;&emsp;&emsp;→&nbsp;196행 조건이 성립하지 않으면 : |
| 199 | &emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 200 | &emsp;&emsp;&emsp;→&nbsp;팬 운전 상태 (`VP_FWU_SF_Status`) = OFF(0) 이면 : |
| 201 | &emsp;&emsp;&emsp;&emsp;→&nbsp;댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`)에 OFF(0) 기록 — 기본 우선순위(P5) |
| 202 | &emsp;&emsp;&emsp;→&nbsp;200행 조건이 성립하지 않으면 : |
| 203 | &emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 204 | &emsp;&emsp;→&nbsp;팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`)에 현재 값을 그대로 기록 — 우선순위 P11 |
| 205 | &emsp;&emsp;→&nbsp;댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`)에 현재 값을 그대로 기록 — 우선순위 P11 |
| 206 | &emsp;→&nbsp;103행 조건이 성립하지 않으면 : |
| 207 | &emsp;&emsp;→&nbsp;*[주석] 수동 모드: 로직이 쓴 P5를 내려놓아 사람이 넣은 값이 적용되게 한다* |
| 208 | &emsp;&emsp;→&nbsp;PI 루프 `RAT_LOOP`(1) 누적값 초기화 |
| 209 | &emsp;&emsp;→&nbsp;PI 루프 `RDP_LOOP`(2) 누적값 초기화 |
| 210 | &emsp;&emsp;→&nbsp;PI 루프 `DELTA_T_LOOP`(3) 누적값 초기화 |
| 211 | &emsp;&emsp;→&nbsp;PI 루프 `CZT_LOOP`(4) 누적값 초기화 |
| 212 | &emsp;&emsp;→&nbsp;팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`)의 P5 쓰기 해제 |
| 213 | &emsp;&emsp;→&nbsp;댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`)의 P5 쓰기 해제 |
| 214 | 89행 조건이 성립하지 않으면 : |
| 215 | &emsp;→&nbsp;*[주석] 비상정지: 운전 명령을 끄고 팬 출력을 P1으로 0으로 누른다. 댐퍼는 팬이 멈춘 뒤 닫는다* |
| 216 | &emsp;→&nbsp;운전 명령(BMS) (`VP_FWU_Command`)에 OFF(0) 기록 — 우선순위 P11 |
| 217 | &emsp;→&nbsp;운전 명령(HMI) (`VP_FWU_Command_HMI`)에 OFF(0) 기록 — 우선순위 P11 |
| 218 | &emsp;→&nbsp;PI 루프 `RAT_LOOP`(1) 누적값 초기화 |
| 219 | &emsp;→&nbsp;PI 루프 `RDP_LOOP`(2) 누적값 초기화 |
| 220 | &emsp;→&nbsp;PI 루프 `DELTA_T_LOOP`(3) 누적값 초기화 |
| 221 | &emsp;→&nbsp;PI 루프 `CZT_LOOP`(4) 누적값 초기화 |
| 222 | &emsp;→&nbsp;팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`)에 0 기록 — 기본 우선순위(P5) |
| 223 | &emsp;→&nbsp;팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`)에 0 기록 — 우선순위 P11 |
| 224 | &emsp;→&nbsp;팬 운전 상태 (`VP_FWU_SF_Status`) = OFF(0) 이면 : |
| 225 | &emsp;&emsp;→&nbsp;댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`)에 OFF(0) 기록 — 기본 우선순위(P5) |
| 226 | &emsp;&emsp;→&nbsp;댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`)에 OFF(0) 기록 — 우선순위 P11 |
| 227 | &emsp;&emsp;→&nbsp;댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`)에 OFF(0) 기록 — 우선순위 P1 |
| 228 | &emsp;→&nbsp;224행 조건이 성립하지 않으면 : |
| 229 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 230 | &emsp;→&nbsp;팬 1~4번 속도 AO 출력 (`FWU_SF-1_4_SPEED_CONTROL`)에 0 기록 — 우선순위 P1 |
| 231 | &emsp;→&nbsp;팬 5~8번 속도 AO 출력 (`FWU_SF-5_8_SPEED_CONTROL`)에 0 기록 — 우선순위 P1 |
| 232 | &emsp;→&nbsp;팬 1번 목표 RPM (`FWU_SF-1.Target_RPM_Set`)에 0 기록 — 우선순위 P1 |
| 233 | &emsp;→&nbsp;팬 2번 목표 RPM (`FWU_SF-2.Target_RPM_Set`)에 0 기록 — 우선순위 P1 |
| 234 | &emsp;→&nbsp;팬 3번 목표 RPM (`FWU_SF-3.Target_RPM_Set`)에 0 기록 — 우선순위 P1 |
| 235 | &emsp;→&nbsp;팬 4번 목표 RPM (`FWU_SF-4.Target_RPM_Set`)에 0 기록 — 우선순위 P1 |
| 236 | &emsp;→&nbsp;팬 5번 목표 RPM (`FWU_SF-5.Target_RPM_Set`)에 0 기록 — 우선순위 P1 |
| 237 | &emsp;→&nbsp;팬 6번 목표 RPM (`FWU_SF-6.Target_RPM_Set`)에 0 기록 — 우선순위 P1 |
| 238 | &emsp;→&nbsp;팬 7번 목표 RPM (`FWU_SF-7.Target_RPM_Set`)에 0 기록 — 우선순위 P1 |
| 239 | &emsp;→&nbsp;팬 8번 목표 RPM (`FWU_SF-8.Target_RPM_Set`)에 0 기록 — 우선순위 P1 |

<a id="section-6"></a>

## 241~259행 · 팬 운전 명령: 속도 값이 있으면 8대 모두 운전

| 행 | 해석 |
|---:|---|
| 241 | *[주석] 팬 운전 명령: 속도 값이 있으면 8대 모두 운전* |
| 242 | 팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`) > 0 이면 : |
| 243 | &emsp;→&nbsp;팬 1번 운전 명령 (`FWU_SF-1.Run_Command`)에 ON(1) 기록 — 기본 우선순위(P5) |
| 244 | &emsp;→&nbsp;팬 2번 운전 명령 (`FWU_SF-2.Run_Command`)에 ON(1) 기록 — 기본 우선순위(P5) |
| 245 | &emsp;→&nbsp;팬 3번 운전 명령 (`FWU_SF-3.Run_Command`)에 ON(1) 기록 — 기본 우선순위(P5) |
| 246 | &emsp;→&nbsp;팬 4번 운전 명령 (`FWU_SF-4.Run_Command`)에 ON(1) 기록 — 기본 우선순위(P5) |
| 247 | &emsp;→&nbsp;팬 5번 운전 명령 (`FWU_SF-5.Run_Command`)에 ON(1) 기록 — 기본 우선순위(P5) |
| 248 | &emsp;→&nbsp;팬 6번 운전 명령 (`FWU_SF-6.Run_Command`)에 ON(1) 기록 — 기본 우선순위(P5) |
| 249 | &emsp;→&nbsp;팬 7번 운전 명령 (`FWU_SF-7.Run_Command`)에 ON(1) 기록 — 기본 우선순위(P5) |
| 250 | &emsp;→&nbsp;팬 8번 운전 명령 (`FWU_SF-8.Run_Command`)에 ON(1) 기록 — 기본 우선순위(P5) |
| 251 | 242행 조건이 성립하지 않으면 : |
| 252 | &emsp;→&nbsp;팬 1번 운전 명령 (`FWU_SF-1.Run_Command`)에 OFF(0) 기록 — 기본 우선순위(P5) |
| 253 | &emsp;→&nbsp;팬 2번 운전 명령 (`FWU_SF-2.Run_Command`)에 OFF(0) 기록 — 기본 우선순위(P5) |
| 254 | &emsp;→&nbsp;팬 3번 운전 명령 (`FWU_SF-3.Run_Command`)에 OFF(0) 기록 — 기본 우선순위(P5) |
| 255 | &emsp;→&nbsp;팬 4번 운전 명령 (`FWU_SF-4.Run_Command`)에 OFF(0) 기록 — 기본 우선순위(P5) |
| 256 | &emsp;→&nbsp;팬 5번 운전 명령 (`FWU_SF-5.Run_Command`)에 OFF(0) 기록 — 기본 우선순위(P5) |
| 257 | &emsp;→&nbsp;팬 6번 운전 명령 (`FWU_SF-6.Run_Command`)에 OFF(0) 기록 — 기본 우선순위(P5) |
| 258 | &emsp;→&nbsp;팬 7번 운전 명령 (`FWU_SF-7.Run_Command`)에 OFF(0) 기록 — 기본 우선순위(P5) |
| 259 | &emsp;→&nbsp;팬 8번 운전 명령 (`FWU_SF-8.Run_Command`)에 OFF(0) 기록 — 기본 우선순위(P5) |

<a id="section-7"></a>

## 261~297행 · 팬 속도 출력 (5초마다)

> 평소에는 Modbus로 목표 RPM을 보내고, 팬 통신이 끊기면 AO(아날로그)로 바꿔 보낸다

| 행 | 해석 |
|---:|---|
| 261 | *[주석] 팬 속도 출력 (5초마다)* |
| 262 | *[주석] 평소에는 Modbus로 목표 RPM을 보내고, 팬 통신이 끊기면 AO(아날로그)로 바꿔 보낸다* |
| 263 | 타이머 `SPEED_OUTPUT_TIMER`(1번: 팬 속도를 마지막으로 내보낸 뒤 지난 시간) 경과시간 > 5 이면 :<br>*[주석] 5초* |
| 264 | &emsp;→&nbsp;`SFSpeed` ← 팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`) 값 읽기 |
| 265 | &emsp;→&nbsp;`SFMaxRPM` ← 팬 최대 RPM(계산값) (`VP_FWU_SF_Max_RPM`) 값 읽기<br>*[주석] Initialization이 설계 RPM과 비율로 계산해 둔 값* |
| 266 | &emsp;→&nbsp;`SFRPMSet` ← [(`SFSpeed` × `SFMaxRPM`) ÷ 100, `SFMaxRPM`] 중 최솟값 |
| 267 | &emsp;→&nbsp;`SFAOSet` ← (`SFSpeed` × `SFMaxRPM`) ÷ [팬 정격 최대 RPM (`VP_FWU_SF_Rated_Max_RPM`), 1] 중 최댓값 |
| 269 | &emsp;→&nbsp;팬 통신 이상 종합 (`VP_FWU_SF_Comm_Fault`) = TRUE(1) 이면 : |
| 270 | &emsp;&emsp;→&nbsp;팬 1~4번 속도 AO 출력 (`FWU_SF-1_4_SPEED_CONTROL`)에 `SFAOSet` 기록 — 기본 우선순위(P5) |
| 271 | &emsp;&emsp;→&nbsp;팬 5~8번 속도 AO 출력 (`FWU_SF-5_8_SPEED_CONTROL`)에 `SFAOSet` 기록 — 기본 우선순위(P5) |
| 272 | &emsp;&emsp;→&nbsp;팬 1번 목표 RPM (`FWU_SF-1.Target_RPM_Set`)에 0 기록 — 기본 우선순위(P5) |
| 273 | &emsp;&emsp;→&nbsp;팬 2번 목표 RPM (`FWU_SF-2.Target_RPM_Set`)에 0 기록 — 기본 우선순위(P5) |
| 274 | &emsp;&emsp;→&nbsp;팬 3번 목표 RPM (`FWU_SF-3.Target_RPM_Set`)에 0 기록 — 기본 우선순위(P5) |
| 275 | &emsp;&emsp;→&nbsp;팬 4번 목표 RPM (`FWU_SF-4.Target_RPM_Set`)에 0 기록 — 기본 우선순위(P5) |
| 276 | &emsp;&emsp;→&nbsp;팬 5번 목표 RPM (`FWU_SF-5.Target_RPM_Set`)에 0 기록 — 기본 우선순위(P5) |
| 277 | &emsp;&emsp;→&nbsp;팬 6번 목표 RPM (`FWU_SF-6.Target_RPM_Set`)에 0 기록 — 기본 우선순위(P5) |
| 278 | &emsp;&emsp;→&nbsp;팬 7번 목표 RPM (`FWU_SF-7.Target_RPM_Set`)에 0 기록 — 기본 우선순위(P5) |
| 279 | &emsp;&emsp;→&nbsp;팬 8번 목표 RPM (`FWU_SF-8.Target_RPM_Set`)에 0 기록 — 기본 우선순위(P5) |
| 280 | &emsp;→&nbsp;269행 조건이 성립하지 않으면 : |
| 281 | &emsp;&emsp;→&nbsp;팬 1~4번 속도 AO 출력 (`FWU_SF-1_4_SPEED_CONTROL`)에 0 기록 — 기본 우선순위(P5) |
| 282 | &emsp;&emsp;→&nbsp;팬 5~8번 속도 AO 출력 (`FWU_SF-5_8_SPEED_CONTROL`)에 0 기록 — 기본 우선순위(P5) |
| 283 | &emsp;&emsp;→&nbsp;팬 1번 목표 RPM (`FWU_SF-1.Target_RPM_Set`)에 `SFRPMSet` 기록 — 기본 우선순위(P5) |
| 284 | &emsp;&emsp;→&nbsp;팬 2번 목표 RPM (`FWU_SF-2.Target_RPM_Set`)에 `SFRPMSet` 기록 — 기본 우선순위(P5) |
| 285 | &emsp;&emsp;→&nbsp;팬 3번 목표 RPM (`FWU_SF-3.Target_RPM_Set`)에 `SFRPMSet` 기록 — 기본 우선순위(P5) |
| 286 | &emsp;&emsp;→&nbsp;팬 4번 목표 RPM (`FWU_SF-4.Target_RPM_Set`)에 `SFRPMSet` 기록 — 기본 우선순위(P5) |
| 287 | &emsp;&emsp;→&nbsp;팬 5번 목표 RPM (`FWU_SF-5.Target_RPM_Set`)에 `SFRPMSet` 기록 — 기본 우선순위(P5) |
| 288 | &emsp;&emsp;→&nbsp;팬 6번 목표 RPM (`FWU_SF-6.Target_RPM_Set`)에 `SFRPMSet` 기록 — 기본 우선순위(P5) |
| 289 | &emsp;&emsp;→&nbsp;팬 7번 목표 RPM (`FWU_SF-7.Target_RPM_Set`)에 `SFRPMSet` 기록 — 기본 우선순위(P5) |
| 290 | &emsp;&emsp;→&nbsp;팬 8번 목표 RPM (`FWU_SF-8.Target_RPM_Set`)에 `SFRPMSet` 기록 — 기본 우선순위(P5) |
| 292 | &emsp;→&nbsp;타이머 `SPEED_OUTPUT_TIMER`(1번: 팬 속도를 마지막으로 내보낸 뒤 지난 시간)를 0초로 초기화 |
| 293 | 263행 조건이 성립하지 않으면 : |
| 294 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 296 | *[주석] JSY 2026-11-23 수정 구간 끝. 주제 = Coding Rule 적용(매크로 상수, 설정값 상수, 변수명, if-else 짝 맞춤, 주석)* |
| 297 | *[주석] LJH 2026-11-17 수정 구간 끝. 주제 = 온도 고장 대체운전과 네 밸브 정지 연계* |
