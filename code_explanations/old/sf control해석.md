# SF Control 줄별 해석

> **대상 코드** : `fwu_v2/Logic/SF Control.py` (현재 jh 작업 코드, 196 줄)  
> **행** = 코드 줄 번호 (빈 줄은 생략)  
> **표기** : `→` 들여쓰기 단계 · *[주석]* 코드 안 주석 · **[신규]** 이번에 새로 들어간 동작 · **※** 검토할 점

**목차**

- [1~13행 · 머리말, 안내 주석, 상수](#113행--머리말-안내-주석-상수)
- [15~35행 · 운전 모드 판단](#1535행--운전-모드-판단)
- [37~44행 · PI 게인 읽기](#3744행--pi-게인-읽기)
- [46~57행 · 비상 해제 (P1 해제)](#4657행--비상-해제-p1-해제)
- [58~115행 · 자동 운전](#58115행--자동-운전)
- [116~122행 · 수동 운전](#116122행--수동-운전)
- [123~145행 · 비상](#123145행--비상)
- [147~164행 · 팬 운전 명령 (Run Command)](#147164행--팬-운전-명령-run-command)
- [166~196행 · 속도 출력 (5 초마다)](#166196행--속도-출력-5-초마다)

## 1~13행 · 머리말, 안내 주석, 상수

> 타이머·PI 루프 번호

| 행 | 해석 |
|---:|---|
| 1 | *[주석] LJH 2026-11-17 수정 구간 시작. 주제 = 온도센서 고장 시 대체운전 + 네 밸브 닫힘과 팬 정지 연계* |
| 2 | 상수: 속도 출력 주기 타이머 번호 = 1 |
| 3 | *[주석] 모드 선택 UI 는 정수 0\~4 만 보냄. 다른 경로로 직접 쓰게 하면 값 검증 필요* |
| 4 | *[주석] 수동 속도는 코드에서 제한 안 함. HMI 에서 정지 0 또는 최소\~최대 속도만 입력되게 할 것* |
| 5 | *[주석] HMI 에서 최소 ≤ 최대 확인. 최소속도 30 % 유지, QTS 요구 20 % 는 코드 리뷰 시 확인 필요* |
| 6 | *[주석] ΔT 목표 -2℃ 는 SMX01 기준 임시값. RAT-SAT 가 양수인 실제 운전에서는 최대속도에 머물 수 있어 재확인 필요* |
| 7 | *[주석] 정상 정지 시 네 밸브가 닫힐 때까지 팬을 안 멈춤. 밸브가 안 닫힐 때 제한시간·대체 정지 방법은 추후 검토* |
| 8 | *[주석] 팬 통신 이상 시 전체를 아날로그 AO 로 전환. 새 팬의 Run·AO/RPM 우선권, 환산, 복구 동작 확인 필요* |
| 9 | 상수: RAT 제어 PI 루프 번호 = 1 |
| 10 | 상수: RDP 제어 PI 루프 번호 = 2 |
| 11 | 상수: ΔT 제어 PI 루프 번호 = 3 |
| 12 | 상수: CZT 제어 PI 루프 번호 = 4 |
| 13 | DDC 로직 엔진 객체 생성 |

## 15~35행 · 운전 모드 판단

> 고정속도로 대체할지, BMS 통신 장애 운전을 할지 결정

| 행 | 해석 |
|---:|---|
| 15 | 팬 제어 모드 선택 읽기 (`VP_FWU_SF_Control_Select` : 0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT) |
| 16 | "고정속도로 운전" 변수 초기화 (0 = 아니오) |
| 17 | 모드 0(고정속도) (`0 <= sf_select < 1`) 이면 |
| 18 | &emsp;→&nbsp;고정속도 운전 |
| 19 | 모드 2(RDP) (`2 <= sf_select < 3`) 인데 RDP PV 가 유효하지 않으면 (센서 모두 고장 / 개수 0 / 상위 통신 장애) |
| 20 | &emsp;→&nbsp;고정속도로 대체 |
| 21 | 모드 4(CZT) (`4 <= sf_select < 5`) 인데 CZT PV 가 유효하지 않으면 |
| 22 | &emsp;→&nbsp;고정속도로 대체 |
| 24 | **[신규]** 모드 1(RAT) (`1 <= sf_select < 2`) 인데 RAT 센서 고장 알람이 1 이면 |
| 25 | &emsp;→&nbsp;고정속도로 대체 (고장 센서로 PI 제어하지 않게) |
| 26 | **[신규]** 모드 3(ΔT) (`3 <= sf_select < 4`) 인데 RAT 또는 SAT 센서 고장이면 (ΔT = RAT-SAT 계산 불가) |
| 27 | &emsp;→&nbsp;고정속도로 대체 |
| 28 | "BMS 통신 장애 운전" 변수 초기화 (0 = 아니오) |
| 29 | 상위 통신 사용 중(Upper Comm Enable=1) 이고 BMS PLC 통신 장애이면 :<br>**※** 상위 미사용 모델은 이 운전을 안 함 |
| 30 | &emsp;→&nbsp;모드 2(RDP) 또는 4(CZT) (`2 <= sf_select < 3 또는 4 <= sf_select < 5`) 이면 (BMS 가 주는 구역 센서값을 쓰는 모드) |
| 31 | &emsp;&emsp;→&nbsp;BMS 통신 장애 운전 |
| 32 | &emsp;→&nbsp;모드 0(고정속도) (`0 <= sf_select < 1`) 이고 Remote 이면 (Speed SP 를 BMS 가 써 주는 경우) |
| 33 | &emsp;&emsp;→&nbsp;BMS 통신 장애 운전 |
| 34 | BMS 통신 장애 운전이면 |
| 35 | &emsp;→&nbsp;고정속도 대체는 취소 (아래 90행의 장애 운전이 대신 처리) |

## 37~44행 · PI 게인 읽기

| 행 | 해석 |
|---:|---|
| 37 | RDP 제어 P 게인 읽기 |
| 38 | RDP 제어 I 게인 읽기 |
| 39 | RAT 제어 P 게인 읽기 |
| 40 | RAT 제어 I 게인 읽기 |
| 41 | ΔT 제어 P 게인 읽기 |
| 42 | ΔT 제어 I 게인 읽기 |
| 43 | CZT 제어 P 게인 읽기 |
| 44 | CZT 제어 I 게인 읽기 |

## 46~57행 · 비상 해제 (P1 해제)

| 행 | 해석 |
|---:|---|
| 46 | 비상 DI = 0 (평상시) 이면 : |
| 47 | &emsp;→&nbsp;팬 아날로그 속도 AO (SF-1\~4) 의 비상 P1 해제<br>*[주석] FWU_SF-1_8_SPEED_CONTROL로 합쳐도 됨. 기존 배선은 1~4, 5~8로 나뉘어 있음* |
| 48 | &emsp;→&nbsp;팬 아날로그 속도 AO (SF-5\~8) 의 비상 P1 해제 |
| 49 | &emsp;→&nbsp;SF-1 Modbus 목표 RPM 의 비상 P1 해제 |
| 50 | &emsp;→&nbsp;SF-2 Modbus 목표 RPM 의 비상 P1 해제 |
| 51 | &emsp;→&nbsp;SF-3 Modbus 목표 RPM 의 비상 P1 해제 |
| 52 | &emsp;→&nbsp;SF-4 Modbus 목표 RPM 의 비상 P1 해제 |
| 53 | &emsp;→&nbsp;SF-5 Modbus 목표 RPM 의 비상 P1 해제 |
| 54 | &emsp;→&nbsp;SF-6 Modbus 목표 RPM 의 비상 P1 해제 |
| 55 | &emsp;→&nbsp;SF-7 Modbus 목표 RPM 의 비상 P1 해제 |
| 56 | &emsp;→&nbsp;SF-8 Modbus 목표 RPM 의 비상 P1 해제 |
| 57 | &emsp;→&nbsp;급기 댐퍼 명령(SAD-1\~4 공통 DO) 의 비상 P1 해제 |

## 58~115행 · 자동 운전

> 댐퍼 열림 확인 후 모드별 속도 결정, 정지 시 밸브 닫힘 →&nbsp;팬 정지 →&nbsp;댐퍼 닫힘

| 행 | 해석 |
|---:|---|
| 58 | &emsp;→&nbsp;운전 모드가 자동(1) 이면 : |
| 59 | &emsp;&emsp;→&nbsp;Command = 1 (운전) 이면 : |
| 60 | &emsp;&emsp;&emsp;→&nbsp;급기 댐퍼 4개 열기 명령 (P5) |
| 61 | &emsp;&emsp;&emsp;→&nbsp;댐퍼 4개의 열림 상태 DI 가 모두 1 이면 (다 열렸으면) 팬 제어 시작 : |
| 62 | &emsp;&emsp;&emsp;&emsp;→&nbsp;고정속도 운전이면 : |
| 63 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;속도 = MAX(Speed SP, 최소속도) : 최소속도보다 낮지 않게 |
| 64 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;속도 = MIN(속도, 최대속도) : 최대속도보다 높지 않게 |
| 65 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;팬 속도값(`VP_FWU_SF_Speed_Value`, %) 에 기록 |
| 66 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;RAT 루프 초기화 (안 쓰는 루프 누적값 정리) |
| 67 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;RDP 루프 초기화 |
| 68 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;ΔT 루프 초기화 |
| 69 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;CZT 루프 초기화 |
| 70 | &emsp;&emsp;&emsp;&emsp;→&nbsp;`b_fixed == 0`이고 모드 1(RAT) (`1 <= sf_select < 2`) 이면 : |
| 71 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 제어: 제어 방향 1(RAT &gt; 설정 →&nbsp;속도 증가), PV=`FWU_RAT`, 출력=Speed Value, SP=RAT SP, D=0, 샘플링 0, 시작값 60, 범위 최소\~최대, 루프 1 |
| 72 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;RDP 루프 초기화 |
| 73 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;ΔT 루프 초기화 |
| 74 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;CZT 루프 초기화 |
| 75 | &emsp;&emsp;&emsp;&emsp;→&nbsp;`b_fixed == 0`이고 모드 2(RDP) (`2 <= sf_select < 3`) 이고 BMS 통신 장애 운전이 아니면 : |
| 76 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 제어: 제어 방향 0(RDP &lt; 설정 →&nbsp;속도 증가), PV=RDP PV, SP=RDP SP, 시작값 60, 범위 최소\~최대, 루프 2 |
| 77 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;RAT 루프 초기화 |
| 78 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;ΔT 루프 초기화 |
| 79 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;CZT 루프 초기화 |
| 80 | &emsp;&emsp;&emsp;&emsp;→&nbsp;`b_fixed == 0`이고 모드 3(ΔT) (`3 <= sf_select < 4`) 이면 : |
| 81 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 제어: 제어 방향 1(ΔT &gt; 설정 →&nbsp;속도 증가), PV=ΔT PV(RAT-SAT), SP=ΔT SP, 루프 3 |
| 82 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;RAT 루프 초기화 |
| 83 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;RDP 루프 초기화 |
| 84 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;CZT 루프 초기화 |
| 85 | &emsp;&emsp;&emsp;&emsp;→&nbsp;`b_fixed == 0`이고 모드 4(CZT) (`4 <= sf_select < 5`) 이고 BMS 통신 장애 운전이 아니면 : |
| 86 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 제어: 제어 방향 1(CZT &gt; 설정 →&nbsp;속도 증가), PV=CZT PV, SP=CZT SP, 루프 4 |
| 87 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;RAT 루프 초기화 |
| 88 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;RDP 루프 초기화 |
| 89 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;ΔT 루프 초기화 |
| 90 | &emsp;&emsp;&emsp;&emsp;→&nbsp;BMS 통신 장애 운전이면 (QTS 129\~131) : |
| 91 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;장애 모드가 1(최대속도) 이거나, 유지할 속도가 없으면 (현재 속도 &lt; 최소속도, 예: 기동 직후 0)<br>*[주석] VP_FWU_BMS_Comm_Fail_Mode = 1: 팬 최대 속도 운전, 0: 마지막 팬 속도 유지* |
| 92 | &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;팬 속도 = 최대속도. |
| 93 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;RAT 루프 초기화 |
| 94 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;RDP 루프 초기화 |
| 95 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;ΔT 루프 초기화 |
| 96 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;CZT 루프 초기화 |
| 98 | &emsp;&emsp;&emsp;→&nbsp;댐퍼 4개의 닫힘 상태 DI 가 모두 1 이면 (운전 명령 중인데 다 닫혀 있음) : |
| 99 | &emsp;&emsp;&emsp;&emsp;→&nbsp;RAT 루프 초기화 |
| 100 | &emsp;&emsp;&emsp;&emsp;→&nbsp;RDP 루프 초기화 |
| 101 | &emsp;&emsp;&emsp;&emsp;→&nbsp;ΔT 루프 초기화 |
| 102 | &emsp;&emsp;&emsp;&emsp;→&nbsp;CZT 루프 초기화 |
| 103 | &emsp;&emsp;&emsp;&emsp;→&nbsp;팬 속도 0 (닫힌 댐퍼에 대고 팬을 돌리지 않음). 댐퍼가 다시 열리면 재기동 |
| 105 | &emsp;&emsp;→&nbsp;`VP_FWU_Command`가 1이 아니면 : |
| 106 | &emsp;&emsp;&emsp;→&nbsp;RAT 루프 초기화 |
| 107 | &emsp;&emsp;&emsp;→&nbsp;RDP 루프 초기화 |
| 108 | &emsp;&emsp;&emsp;→&nbsp;ΔT 루프 초기화 |
| 109 | &emsp;&emsp;&emsp;→&nbsp;CZT 루프 초기화 |
| 110 | &emsp;&emsp;&emsp;→&nbsp;네 밸브가 모두 닫혔으면 (`VP_FWU_PICV_All_Closed` = 1, PICV Feedback 에서 만듦)<br>&emsp;&emsp;&emsp;**※** 밸브 1대라도 통신 이상이면 0 → 팬이 안 멈춤 (7행 주석) |
| 111 | &emsp;&emsp;&emsp;&emsp;→&nbsp;팬 속도 0 |
| 112 | &emsp;&emsp;&emsp;→&nbsp;팬이 모두 멈췄으면 (SF Status = 0) |
| 113 | &emsp;&emsp;&emsp;&emsp;→&nbsp;급기 댐퍼 닫기 |
| 114 | &emsp;&emsp;→&nbsp;지금 팬 속도값을 P11 에도 기록 (수동 전환 시 유지) |
| 115 | &emsp;&emsp;→&nbsp;지금 댐퍼 명령을 P11 에도 기록 |

## 116~122행 · 수동 운전

> P5 해제

| 행 | 해석 |
|---:|---|
| 116 | &emsp;→&nbsp;운전 모드가 자동(1)이 아니면 : |
| 117 | &emsp;&emsp;→&nbsp;RAT 루프 초기화 |
| 118 | &emsp;&emsp;→&nbsp;RDP 루프 초기화 |
| 119 | &emsp;&emsp;→&nbsp;ΔT 루프 초기화 |
| 120 | &emsp;&emsp;→&nbsp;CZT 루프 초기화 |
| 121 | &emsp;&emsp;→&nbsp;팬 속도의 자동 쓰기 P5 해제 (운전원 값 P11 이 살아남) |
| 122 | &emsp;&emsp;→&nbsp;댐퍼 명령의 자동 쓰기 P5 해제 |

## 123~145행 · 비상

> Command 0, 팬 0, 댐퍼 닫힘을 P1 로 강제

| 행 | 해석 |
|---:|---|
| 123 | 비상 DI가 0이 아니면 : |
| 124 | &emsp;→&nbsp;BMS 운전 명령을 P11 에 0 으로 (비상이 풀려도 자동 재기동 안 함) |
| 125 | &emsp;→&nbsp;터치스크린 운전 명령도 P11 에 0 |
| 126 | &emsp;→&nbsp;RAT 루프 초기화 |
| 127 | &emsp;→&nbsp;RDP 루프 초기화 |
| 128 | &emsp;→&nbsp;ΔT 루프 초기화 |
| 129 | &emsp;→&nbsp;CZT 루프 초기화 |
| 130 | &emsp;→&nbsp;팬 속도값 0 (P5) |
| 131 | &emsp;→&nbsp;팬 속도값 P11 도 0 |
| 132 | &emsp;→&nbsp;팬이 모두 멈췄으면 : |
| 133 | &emsp;&emsp;→&nbsp;댐퍼 닫기 (P5) |
| 134 | &emsp;&emsp;→&nbsp;댐퍼 닫기 P11 |
| 135 | &emsp;&emsp;→&nbsp;댐퍼 닫기를 비상 P1 로 강제 |
| 136 | &emsp;→&nbsp;팬 아날로그 AO (SF-1\~4) 0 을 P1 로 강제 |
| 137 | &emsp;→&nbsp;팬 아날로그 AO (SF-5\~8) 0 을 P1 로 강제 |
| 138 | &emsp;→&nbsp;SF-1 목표 RPM 0 을 P1 로 강제 |
| 139 | &emsp;→&nbsp;SF-2 목표 RPM 0 을 P1 로 강제 |
| 140 | &emsp;→&nbsp;SF-3 목표 RPM 0 을 P1 로 강제 |
| 141 | &emsp;→&nbsp;SF-4 목표 RPM 0 을 P1 로 강제 |
| 142 | &emsp;→&nbsp;SF-5 목표 RPM 0 을 P1 로 강제 |
| 143 | &emsp;→&nbsp;SF-6 목표 RPM 0 을 P1 로 강제 |
| 144 | &emsp;→&nbsp;SF-7 목표 RPM 0 을 P1 로 강제 |
| 145 | &emsp;→&nbsp;SF-8 목표 RPM 0 을 P1 로 강제 |

## 147~164행 · 팬 운전 명령 (Run Command)

> 속도값 &gt; 0 이면 8 대 모두 1

| 행 | 해석 |
|---:|---|
| 147 | 팬 속도값이 0 보다 크면 : |
| 148 | &emsp;→&nbsp;SF-1 운전 명령(Run Command) = 1 |
| 149 | &emsp;→&nbsp;SF-2 운전 명령(Run Command) = 1 |
| 150 | &emsp;→&nbsp;SF-3 운전 명령(Run Command) = 1 |
| 151 | &emsp;→&nbsp;SF-4 운전 명령(Run Command) = 1 |
| 152 | &emsp;→&nbsp;SF-5 운전 명령(Run Command) = 1 |
| 153 | &emsp;→&nbsp;SF-6 운전 명령(Run Command) = 1 |
| 154 | &emsp;→&nbsp;SF-7 운전 명령(Run Command) = 1 |
| 155 | &emsp;→&nbsp;SF-8 운전 명령(Run Command) = 1 |
| 156 | 팬 속도값이 0 이하이면 : |
| 157 | &emsp;→&nbsp;SF-1 운전 명령 = 0 |
| 158 | &emsp;→&nbsp;SF-2 운전 명령 = 0 |
| 159 | &emsp;→&nbsp;SF-3 운전 명령 = 0 |
| 160 | &emsp;→&nbsp;SF-4 운전 명령 = 0 |
| 161 | &emsp;→&nbsp;SF-5 운전 명령 = 0 |
| 162 | &emsp;→&nbsp;SF-6 운전 명령 = 0 |
| 163 | &emsp;→&nbsp;SF-7 운전 명령 = 0 |
| 164 | &emsp;→&nbsp;SF-8 운전 명령 = 0 |

## 166~196행 · 속도 출력 (5 초마다)

> 통신 정상이면 Modbus 목표 RPM, 통신 장애면 아날로그 AO

| 행 | 해석 |
|---:|---|
| 166 | 속도 출력 타이머(1) 가 5 초를 넘으면 (5 초마다 한 번 출력) : |
| 167 | &emsp;→&nbsp;팬 속도값(%) 읽기 |
| 168 | &emsp;→&nbsp;팬 최대 RPM 읽기 (Initialization 에서 계산한 값) |
| 169 | &emsp;→&nbsp;Modbus 목표 RPM = MIN(속도% x 최대RPM / 100, 최대RPM) |
| 170 | &emsp;→&nbsp;아날로그 AO 값(%) = 속도% x 최대RPM / 정격최대RPM (정격 0 오입력 시 나눗셈 오류 방지로 최소 1) |
| 172 | &emsp;→&nbsp;팬 통신 장애 요약(8대 중 1대라도 통신 장애) 이 1 이면 : 전부 아날로그 출력으로 |
| 173 | &emsp;&emsp;→&nbsp;AO (SF-1\~4) = 아날로그 값 |
| 174 | &emsp;&emsp;→&nbsp;AO (SF-5\~8) = 아날로그 값 |
| 175 | &emsp;&emsp;→&nbsp;SF-1 목표 RPM = 0 |
| 176 | &emsp;&emsp;→&nbsp;SF-2 목표 RPM = 0 |
| 177 | &emsp;&emsp;→&nbsp;SF-3 목표 RPM = 0 |
| 178 | &emsp;&emsp;→&nbsp;SF-4 목표 RPM = 0 |
| 179 | &emsp;&emsp;→&nbsp;SF-5 목표 RPM = 0 |
| 180 | &emsp;&emsp;→&nbsp;SF-6 목표 RPM = 0 |
| 181 | &emsp;&emsp;→&nbsp;SF-7 목표 RPM = 0 |
| 182 | &emsp;&emsp;→&nbsp;SF-8 목표 RPM = 0 |
| 183 | &emsp;→&nbsp;팬 통신이 모두 정상이면 : Modbus 출력으로 |
| 184 | &emsp;&emsp;→&nbsp;AO (SF-1\~4) = 0 |
| 185 | &emsp;&emsp;→&nbsp;AO (SF-5\~8) = 0 |
| 186 | &emsp;&emsp;→&nbsp;SF-1 목표 RPM = 계산한 RPM |
| 187 | &emsp;&emsp;→&nbsp;SF-2 목표 RPM = 계산한 RPM |
| 188 | &emsp;&emsp;→&nbsp;SF-3 목표 RPM = 계산한 RPM |
| 189 | &emsp;&emsp;→&nbsp;SF-4 목표 RPM = 계산한 RPM |
| 190 | &emsp;&emsp;→&nbsp;SF-5 목표 RPM = 계산한 RPM |
| 191 | &emsp;&emsp;→&nbsp;SF-6 목표 RPM = 계산한 RPM |
| 192 | &emsp;&emsp;→&nbsp;SF-7 목표 RPM = 계산한 RPM |
| 193 | &emsp;&emsp;→&nbsp;SF-8 목표 RPM = 계산한 RPM |
| 195 | &emsp;→&nbsp;출력 타이머(1) 초기화 (다시 5 초 세기) |
| 196 | *[주석] LJH 2026-11-17 수정 구간 끝* |
