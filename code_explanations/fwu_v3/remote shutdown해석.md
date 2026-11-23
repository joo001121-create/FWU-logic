# Remote Shutdown 줄별 해석

> **대상 코드** : `fwu_v3/Logic/Remote Shutdown.py` (99 줄)  
> **기준** : `sy 브랜치 2026-11-23 (naming rule·관제점 이름 변경 반영)`  
> **행** = 코드 줄 번호 (빈 줄은 생략)  
> **표기** : `→` 들여쓰기 단계 · *[주석]* 코드 안 주석 · `이름` 코드 안 상수·변수 · **※** 읽을 때 주의할 점

연기감지기 신호를 확인해 화재 알람을 내고, 원격 정지 명령이 있거나 화재 시 정지 설정이면 운전 명령과 출력을 0으로 누른다.

**목차**

- [1~16행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수](#section-1)
- [18~26행 · 연기감지기 신호 확인 → 화재 알람](#section-2)
- [28~40행 · 정지 조건 확인](#section-3)
- [42~99행 · 강제 정지: 운전 명령과 출력을 0으로 누른다 (P2·P11)](#section-4)

**※ 공통 표기**: 매크로 상수 TRUE·ON·SET·TMR_READ·DEC = 1, FALSE·OFF·CLEAR·TMR_CLEAR·INC = 0. `SECTIMER(타이머, TMR_CLEAR)`는 타이머를 0초로 초기화, `SECTIMER(타이머, TMR_READ)`는 경과시간 확인이다. P번호가 없는 쓰기(`WRITEPOINT`)는 기본 우선순위 P5를 쓴다. 조건이 거짓이라고 관제점이 저절로 0이 되지는 않는다. 해당 분기에 쓰기가 없으면 이전 값이 남는다. 대문자 이름은 상수, `m`으로 시작하는 이름은 이 파일의 전역변수, `b`가 붙은 이름은 참/거짓 값이다.

<a id="section-1"></a>

## 1~16행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수

| 행 | 해석 |
|---:|---|
| 1 | *[주석] LJH 2026-11-17 수정 구간 시작. 주제 = 원격 및 연기 정지 우선순위 유지* |
| 2 | *[주석] JSY 2026-11-23 수정 구간 시작. 주제 = Coding Rule 적용(매크로 상수, 변수명, if-else 짝 맞춤, 주석)* |
| 4 | *[주석] 로직엔진 loading* |
| 5 | DDC 로직 엔진 객체 생성 (이후 engine.xxx로 관제점을 읽고 씀) |
| 7 | *[주석] Macro상수 정의* |
| 8 | 매크로 상수 정의: TMR_READ, SET, ON, TRUE, DEC = 1 (긍정의 의미 또는 1인 인자) |
| 9 | 매크로 상수 정의: TMR_CLEAR, CLEAR, OFF, FALSE, INC = 0 (부정의 의미 또는 0인 인자) |
| 10 | 상수 `FIRE_CONFIRM_SECONDS` = 3<br>*[주석] 감지기 신호가 잠깐 튀는 걸 화재로 보지 않도록, 3초 넘게 이어질 때만 알람* |
| 12 | *[주석] 타이머 정의* |
| 13 | 타이머 번호 상수 `FIRE_CONFIRM_TIMER` = 0번<br>*[주석] 연기감지기 신호가 이어진 시간* |
| 15 | *[주석] 전역변수 선언* |
| 16 | 전역변수 `mbShutdown` 선언, 처음 값 = FALSE(0)<br>*[주석] 원격 정지나 화재 정지 중 하나라도 걸리면 TRUE* |

<a id="section-2"></a>

## 18~26행 · 연기감지기 신호 확인 → 화재 알람

| 행 | 해석 |
|---:|---|
| 18 | *[주석] 연기감지기 신호 확인 → 화재 알람* |
| 19 | 연기감지기 입력(DI) (`FWU_FIRE_ALARM`) = TRUE(1) 이면 : |
| 20 | &emsp;→&nbsp;타이머 `FIRE_CONFIRM_TIMER`(0번: 연기감지기 신호가 이어진 시간) 경과시간 > `FIRE_CONFIRM_SECONDS`(3) 이면 : |
| 21 | &emsp;&emsp;→&nbsp;화재 알람 (`VP_FWU_Fire_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 22 | &emsp;→&nbsp;20행 조건이 성립하지 않으면 : |
| 23 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 24 | 19행 조건이 성립하지 않으면 : |
| 25 | &emsp;→&nbsp;타이머 `FIRE_CONFIRM_TIMER`(0번: 연기감지기 신호가 이어진 시간)를 0초로 초기화 |
| 26 | &emsp;→&nbsp;화재 알람 (`VP_FWU_Fire_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |

<a id="section-3"></a>

## 28~40행 · 정지 조건 확인

> 화재 때 정지할지는 HMI의 Smoke_Action_Set으로 고른다. 일반 운전 ON/OFF와 별개인 강제 정지라서 로컬·수동 운전 중에도 걸린다. 하드웨어 화재 차단 회로는 이 설정과 상관없이 따로 동작한다.

| 행 | 해석 |
|---:|---|
| 28 | *[주석] 정지 조건 확인* |
| 29 | *[주석] 화재 때 정지할지는 HMI의 Smoke_Action_Set으로 고른다.* |
| 30 | *[주석] 일반 운전 ON/OFF와 별개인 강제 정지라서 로컬·수동 운전 중에도 걸린다.* |
| 31 | *[주석] 하드웨어 화재 차단 회로는 이 설정과 상관없이 따로 동작한다.* |
| 32 | 원격 정지 명령 (`VP_FWU_Remote_Shutdown_Command`) = TRUE(1) 이면 :<br>*[주석] 사용자(HMI/BMS)가 원격 정지를 걸면 1* |
| 33 | &emsp;→&nbsp;`mbShutdown` ← TRUE(1) |
| 34 | 32행 조건이 성립하지 않으면 : |
| 35 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 37 | 화재 알람 (`VP_FWU_Fire_Alarm`) = TRUE(1) **그리고** 화재 시 동작 설정(1 정지, 0 알람만) (`VP_FWU_Smoke_Action_Set`) = TRUE(1) 이면 :<br>*[주석] Smoke_Action_Set 1 = 정지, 0 = 알람만* |
| 38 | &emsp;→&nbsp;`mbShutdown` ← TRUE(1) |
| 39 | 37행 조건이 성립하지 않으면 : |
| 40 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |

<a id="section-4"></a>

## 42~99행 · 강제 정지: 운전 명령과 출력을 0으로 누른다 (P2·P11)

| 행 | 해석 |
|---:|---|
| 42 | *[주석] 강제 정지: 운전 명령과 출력을 0으로 누른다 (P2·P11)* |
| 43 | `mbShutdown` = TRUE(1) 이면 : |
| 44 | &emsp;→&nbsp;운전 명령(BMS) (`VP_FWU_Command`)에 OFF(0) 기록 — 우선순위 P11 |
| 45 | &emsp;→&nbsp;운전 명령(HMI) (`VP_FWU_Command_HMI`)에 OFF(0) 기록 — 우선순위 P11 |
| 46 | &emsp;→&nbsp;PICV 공통 개도 명령(AO) (`FWU_PICV_CONTROL`)에 0 기록 — 우선순위 P2 |
| 47 | &emsp;→&nbsp;PICV 공통 개도 명령(AO) (`FWU_PICV_CONTROL`)에 0 기록 — 우선순위 P11 |
| 48 | &emsp;→&nbsp;팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`)에 0 기록 — 우선순위 P11 |
| 49 | &emsp;→&nbsp;팬 1~4번 속도 AO 출력 (`FWU_SF-1_4_SPEED_CONTROL`)에 0 기록 — 우선순위 P2 |
| 50 | &emsp;→&nbsp;팬 5~8번 속도 AO 출력 (`FWU_SF-5_8_SPEED_CONTROL`)에 0 기록 — 우선순위 P2 |
| 51 | &emsp;→&nbsp;팬 1번 목표 RPM (`FWU_SF-1.Target_RPM_Set`)에 0 기록 — 우선순위 P2 |
| 52 | &emsp;→&nbsp;팬 2번 목표 RPM (`FWU_SF-2.Target_RPM_Set`)에 0 기록 — 우선순위 P2 |
| 53 | &emsp;→&nbsp;팬 3번 목표 RPM (`FWU_SF-3.Target_RPM_Set`)에 0 기록 — 우선순위 P2 |
| 54 | &emsp;→&nbsp;팬 4번 목표 RPM (`FWU_SF-4.Target_RPM_Set`)에 0 기록 — 우선순위 P2 |
| 55 | &emsp;→&nbsp;팬 5번 목표 RPM (`FWU_SF-5.Target_RPM_Set`)에 0 기록 — 우선순위 P2 |
| 56 | &emsp;→&nbsp;팬 6번 목표 RPM (`FWU_SF-6.Target_RPM_Set`)에 0 기록 — 우선순위 P2 |
| 57 | &emsp;→&nbsp;팬 7번 목표 RPM (`FWU_SF-7.Target_RPM_Set`)에 0 기록 — 우선순위 P2 |
| 58 | &emsp;→&nbsp;팬 8번 목표 RPM (`FWU_SF-8.Target_RPM_Set`)에 0 기록 — 우선순위 P2 |
| 59 | &emsp;→&nbsp;팬 1번 운전 명령 (`FWU_SF-1.Run_Command`)에 OFF(0) 기록 — 우선순위 P2 |
| 60 | &emsp;→&nbsp;팬 2번 운전 명령 (`FWU_SF-2.Run_Command`)에 OFF(0) 기록 — 우선순위 P2 |
| 61 | &emsp;→&nbsp;팬 3번 운전 명령 (`FWU_SF-3.Run_Command`)에 OFF(0) 기록 — 우선순위 P2 |
| 62 | &emsp;→&nbsp;팬 4번 운전 명령 (`FWU_SF-4.Run_Command`)에 OFF(0) 기록 — 우선순위 P2 |
| 63 | &emsp;→&nbsp;팬 5번 운전 명령 (`FWU_SF-5.Run_Command`)에 OFF(0) 기록 — 우선순위 P2 |
| 64 | &emsp;→&nbsp;팬 6번 운전 명령 (`FWU_SF-6.Run_Command`)에 OFF(0) 기록 — 우선순위 P2 |
| 65 | &emsp;→&nbsp;팬 7번 운전 명령 (`FWU_SF-7.Run_Command`)에 OFF(0) 기록 — 우선순위 P2 |
| 66 | &emsp;→&nbsp;팬 8번 운전 명령 (`FWU_SF-8.Run_Command`)에 OFF(0) 기록 — 우선순위 P2 |
| 68 | &emsp;→&nbsp;*[주석] 댐퍼는 팬이 다 멈춘 걸 확인한 뒤에 닫는다* |
| 69 | &emsp;→&nbsp;팬 운전 상태 (`VP_FWU_SF_Status`) = OFF(0) 이면 : |
| 70 | &emsp;&emsp;→&nbsp;댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`)에 OFF(0) 기록 — 우선순위 P2 |
| 71 | &emsp;&emsp;→&nbsp;댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`)에 OFF(0) 기록 — 우선순위 P11 |
| 72 | &emsp;→&nbsp;69행 조건이 성립하지 않으면 : |
| 73 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 74 | 43행 조건이 성립하지 않으면 : |
| 75 | &emsp;→&nbsp;*[주석] 정지 해제: P2만 풀어 준다.* |
| 76 | &emsp;→&nbsp;*[주석] P11에 남은 OFF는 재기동을 막는 래치가 아니어서, 더 높은 우선순위에 운전 명령이 남아 있으면 다시 돈다.* |
| 77 | &emsp;→&nbsp;PICV 공통 개도 명령(AO) (`FWU_PICV_CONTROL`)의 P2 쓰기 해제 |
| 78 | &emsp;→&nbsp;팬 1~4번 속도 AO 출력 (`FWU_SF-1_4_SPEED_CONTROL`)의 P2 쓰기 해제 |
| 79 | &emsp;→&nbsp;팬 5~8번 속도 AO 출력 (`FWU_SF-5_8_SPEED_CONTROL`)의 P2 쓰기 해제 |
| 80 | &emsp;→&nbsp;팬 1번 목표 RPM (`FWU_SF-1.Target_RPM_Set`)의 P2 쓰기 해제 |
| 81 | &emsp;→&nbsp;팬 2번 목표 RPM (`FWU_SF-2.Target_RPM_Set`)의 P2 쓰기 해제 |
| 82 | &emsp;→&nbsp;팬 3번 목표 RPM (`FWU_SF-3.Target_RPM_Set`)의 P2 쓰기 해제 |
| 83 | &emsp;→&nbsp;팬 4번 목표 RPM (`FWU_SF-4.Target_RPM_Set`)의 P2 쓰기 해제 |
| 84 | &emsp;→&nbsp;팬 5번 목표 RPM (`FWU_SF-5.Target_RPM_Set`)의 P2 쓰기 해제 |
| 85 | &emsp;→&nbsp;팬 6번 목표 RPM (`FWU_SF-6.Target_RPM_Set`)의 P2 쓰기 해제 |
| 86 | &emsp;→&nbsp;팬 7번 목표 RPM (`FWU_SF-7.Target_RPM_Set`)의 P2 쓰기 해제 |
| 87 | &emsp;→&nbsp;팬 8번 목표 RPM (`FWU_SF-8.Target_RPM_Set`)의 P2 쓰기 해제 |
| 88 | &emsp;→&nbsp;팬 1번 운전 명령 (`FWU_SF-1.Run_Command`)의 P2 쓰기 해제 |
| 89 | &emsp;→&nbsp;팬 2번 운전 명령 (`FWU_SF-2.Run_Command`)의 P2 쓰기 해제 |
| 90 | &emsp;→&nbsp;팬 3번 운전 명령 (`FWU_SF-3.Run_Command`)의 P2 쓰기 해제 |
| 91 | &emsp;→&nbsp;팬 4번 운전 명령 (`FWU_SF-4.Run_Command`)의 P2 쓰기 해제 |
| 92 | &emsp;→&nbsp;팬 5번 운전 명령 (`FWU_SF-5.Run_Command`)의 P2 쓰기 해제 |
| 93 | &emsp;→&nbsp;팬 6번 운전 명령 (`FWU_SF-6.Run_Command`)의 P2 쓰기 해제 |
| 94 | &emsp;→&nbsp;팬 7번 운전 명령 (`FWU_SF-7.Run_Command`)의 P2 쓰기 해제 |
| 95 | &emsp;→&nbsp;팬 8번 운전 명령 (`FWU_SF-8.Run_Command`)의 P2 쓰기 해제 |
| 96 | &emsp;→&nbsp;댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`)의 P2 쓰기 해제 |
| 98 | *[주석] JSY 2026-11-23 수정 구간 끝. 주제 = Coding Rule 적용(매크로 상수, 변수명, if-else 짝 맞춤, 주석)* |
| 99 | *[주석] LJH 2026-11-17 수정 구간 끝. 주제 = 원격 및 연기 정지 우선순위 유지* |
