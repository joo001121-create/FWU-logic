# Comm Fault Alarm 줄별 해석

> **대상 코드** : `fwu_v3/Logic/Comm Fault Alarm.py` (117 줄)  
> **기준** : `sy 브랜치 2026-11-23 (naming rule·관제점 이름 변경 반영)`  
> **행** = 코드 줄 번호 (빈 줄은 생략)  
> **표기** : `→` 들여쓰기 단계 · *[주석]* 코드 안 주석 · `이름` 코드 안 상수·변수 · **※** 읽을 때 주의할 점

팬 8대와 ATS의 통신 이상을 감시한다. 기존 Alarm-3에서 이름만 바꾼 파일이다.

**목차**

- [1~25행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수](#section-1)
- [27~98행 · 팬 1~8 통신 이상: 각 팬의 Current_RPM 점에 통신 경보(8)가 떠 있는지로 본다](#section-2)
- [100~104행 · 팬 통신 종합: 한 대라도 이상이면 TRUE (SF Control이 이 값을 보고 AO 출력으로 바꾼다)](#section-3)
- [106~117행 · ATS 통신 이상](#section-4)

**※ 공통 표기**: 매크로 상수 TRUE·ON·SET·TMR_READ·DEC = 1, FALSE·OFF·CLEAR·TMR_CLEAR·INC = 0. `SECTIMER(타이머, TMR_CLEAR)`는 타이머를 0초로 초기화, `SECTIMER(타이머, TMR_READ)`는 경과시간 확인이다. P번호가 없는 쓰기(`WRITEPOINT`)는 기본 우선순위 P5를 쓴다. 조건이 거짓이라고 관제점이 저절로 0이 되지는 않는다. 해당 분기에 쓰기가 없으면 이전 값이 남는다. 대문자 이름은 상수, `m`으로 시작하는 이름은 이 파일의 전역변수, `b`가 붙은 이름은 참/거짓 값이다.

<a id="section-1"></a>

## 1~25행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수

| 행 | 해석 |
|---:|---|
| 1 | *[주석] JSY 2026-11-23 수정 구간 시작. 주제 = Alarm-3에서 이름 변경(팬·ATS 통신 이상 알람만 남아 내용에 맞춤), Coding Rule 적용* |
| 3 | *[주석] 로직엔진 loading* |
| 4 | DDC 로직 엔진 객체 생성 (이후 engine.xxx로 관제점을 읽고 씀) |
| 6 | *[주석] Macro상수 정의* |
| 7 | 매크로 상수 정의: TMR_READ, SET, ON, TRUE, DEC = 1 (긍정의 의미 또는 1인 인자) |
| 8 | 매크로 상수 정의: TMR_CLEAR, CLEAR, OFF, FALSE, INC = 0 (부정의 의미 또는 0인 인자) |
| 9 | 상수 `COMM_FAULT_CODE` = 8<br>*[주석] READPOINT_ALARM 결과 8 = 통신 경보 (LDPL 가이드 4.10)* |
| 10 | 상수 `FAN_COMM_CONFIRM_SECONDS` = 10<br>*[주석] 팬 통신 이상이 10초 넘게 이어지면 알람* |
| 11 | 상수 `ATS_COMM_CONFIRM_SECONDS` = 10<br>*[주석] ATS 통신 이상이 10초 넘게 이어지면 알람* |
| 13 | *[주석] 타이머 정의 (번호는 Alarm-3에서 쓰던 그대로)* |
| 14 | 타이머 번호 상수 `SF_1_COMM_TIMER` = 0번<br>*[주석] 팬1 통신 이상이 이어진 시간* |
| 15 | 타이머 번호 상수 `SF_2_COMM_TIMER` = 1번<br>*[주석] 팬2 통신 이상이 이어진 시간* |
| 16 | 타이머 번호 상수 `SF_3_COMM_TIMER` = 2번<br>*[주석] 팬3 통신 이상이 이어진 시간* |
| 17 | 타이머 번호 상수 `SF_4_COMM_TIMER` = 3번<br>*[주석] 팬4 통신 이상이 이어진 시간* |
| 18 | 타이머 번호 상수 `SF_5_COMM_TIMER` = 4번<br>*[주석] 팬5 통신 이상이 이어진 시간* |
| 19 | 타이머 번호 상수 `SF_6_COMM_TIMER` = 5번<br>*[주석] 팬6 통신 이상이 이어진 시간* |
| 20 | 타이머 번호 상수 `SF_7_COMM_TIMER` = 6번<br>*[주석] 팬7 통신 이상이 이어진 시간* |
| 21 | 타이머 번호 상수 `SF_8_COMM_TIMER` = 7번<br>*[주석] 팬8 통신 이상이 이어진 시간* |
| 22 | 타이머 번호 상수 `ATS_COMM_TIMER` = 8번<br>*[주석] ATS 통신 이상이 이어진 시간* |
| 24 | *[주석] ATS는 CH2 RS485(Modbus2.xml, 포트 2)로 연결한다. DI 입력 표기와 실제 HW 구성을 대조한다.* |
| 25 | *[주석] XML 통신 포트 배치는 v2에서 확인된 CH2 구성으로 반영함. 장치 주소·통신 설정은 실장 시 확인.* |

<a id="section-2"></a>

## 27~98행 · 팬 1~8 통신 이상: 각 팬의 Current_RPM 점에 통신 경보(8)가 떠 있는지로 본다

| 행 | 해석 |
|---:|---|
| 27 | *[주석] 팬 1~8 통신 이상: 각 팬의 Current_RPM 점에 통신 경보(8)가 떠 있는지로 본다* |
| 28 | 팬 1번 현재 RPM (`FWU_SF-1.Current_RPM`)의 알람 코드 = `COMM_FAULT_CODE`(8) 이면 : |
| 29 | &emsp;→&nbsp;타이머 `SF_1_COMM_TIMER`(0번: 팬1 통신 이상이 이어진 시간) 경과시간 > `FAN_COMM_CONFIRM_SECONDS`(10) 이면 : |
| 30 | &emsp;&emsp;→&nbsp;팬 1번 통신 이상 (`VP_FWU_SF-1_Comm_Fault`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 31 | &emsp;→&nbsp;29행 조건이 성립하지 않으면 : |
| 32 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 33 | 28행 조건이 성립하지 않으면 : |
| 34 | &emsp;→&nbsp;팬 1번 통신 이상 (`VP_FWU_SF-1_Comm_Fault`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 35 | &emsp;→&nbsp;타이머 `SF_1_COMM_TIMER`(0번: 팬1 통신 이상이 이어진 시간)를 0초로 초기화 |
| 37 | 팬 2번 현재 RPM (`FWU_SF-2.Current_RPM`)의 알람 코드 = `COMM_FAULT_CODE`(8) 이면 : |
| 38 | &emsp;→&nbsp;타이머 `SF_2_COMM_TIMER`(1번: 팬2 통신 이상이 이어진 시간) 경과시간 > `FAN_COMM_CONFIRM_SECONDS`(10) 이면 : |
| 39 | &emsp;&emsp;→&nbsp;팬 2번 통신 이상 (`VP_FWU_SF-2_Comm_Fault`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 40 | &emsp;→&nbsp;38행 조건이 성립하지 않으면 : |
| 41 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 42 | 37행 조건이 성립하지 않으면 : |
| 43 | &emsp;→&nbsp;팬 2번 통신 이상 (`VP_FWU_SF-2_Comm_Fault`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 44 | &emsp;→&nbsp;타이머 `SF_2_COMM_TIMER`(1번: 팬2 통신 이상이 이어진 시간)를 0초로 초기화 |
| 46 | 팬 3번 현재 RPM (`FWU_SF-3.Current_RPM`)의 알람 코드 = `COMM_FAULT_CODE`(8) 이면 : |
| 47 | &emsp;→&nbsp;타이머 `SF_3_COMM_TIMER`(2번: 팬3 통신 이상이 이어진 시간) 경과시간 > `FAN_COMM_CONFIRM_SECONDS`(10) 이면 : |
| 48 | &emsp;&emsp;→&nbsp;팬 3번 통신 이상 (`VP_FWU_SF-3_Comm_Fault`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 49 | &emsp;→&nbsp;47행 조건이 성립하지 않으면 : |
| 50 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 51 | 46행 조건이 성립하지 않으면 : |
| 52 | &emsp;→&nbsp;팬 3번 통신 이상 (`VP_FWU_SF-3_Comm_Fault`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 53 | &emsp;→&nbsp;타이머 `SF_3_COMM_TIMER`(2번: 팬3 통신 이상이 이어진 시간)를 0초로 초기화 |
| 55 | 팬 4번 현재 RPM (`FWU_SF-4.Current_RPM`)의 알람 코드 = `COMM_FAULT_CODE`(8) 이면 : |
| 56 | &emsp;→&nbsp;타이머 `SF_4_COMM_TIMER`(3번: 팬4 통신 이상이 이어진 시간) 경과시간 > `FAN_COMM_CONFIRM_SECONDS`(10) 이면 : |
| 57 | &emsp;&emsp;→&nbsp;팬 4번 통신 이상 (`VP_FWU_SF-4_Comm_Fault`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 58 | &emsp;→&nbsp;56행 조건이 성립하지 않으면 : |
| 59 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 60 | 55행 조건이 성립하지 않으면 : |
| 61 | &emsp;→&nbsp;팬 4번 통신 이상 (`VP_FWU_SF-4_Comm_Fault`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 62 | &emsp;→&nbsp;타이머 `SF_4_COMM_TIMER`(3번: 팬4 통신 이상이 이어진 시간)를 0초로 초기화 |
| 64 | 팬 5번 현재 RPM (`FWU_SF-5.Current_RPM`)의 알람 코드 = `COMM_FAULT_CODE`(8) 이면 : |
| 65 | &emsp;→&nbsp;타이머 `SF_5_COMM_TIMER`(4번: 팬5 통신 이상이 이어진 시간) 경과시간 > `FAN_COMM_CONFIRM_SECONDS`(10) 이면 : |
| 66 | &emsp;&emsp;→&nbsp;팬 5번 통신 이상 (`VP_FWU_SF-5_Comm_Fault`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 67 | &emsp;→&nbsp;65행 조건이 성립하지 않으면 : |
| 68 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 69 | 64행 조건이 성립하지 않으면 : |
| 70 | &emsp;→&nbsp;팬 5번 통신 이상 (`VP_FWU_SF-5_Comm_Fault`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 71 | &emsp;→&nbsp;타이머 `SF_5_COMM_TIMER`(4번: 팬5 통신 이상이 이어진 시간)를 0초로 초기화 |
| 73 | 팬 6번 현재 RPM (`FWU_SF-6.Current_RPM`)의 알람 코드 = `COMM_FAULT_CODE`(8) 이면 : |
| 74 | &emsp;→&nbsp;타이머 `SF_6_COMM_TIMER`(5번: 팬6 통신 이상이 이어진 시간) 경과시간 > `FAN_COMM_CONFIRM_SECONDS`(10) 이면 : |
| 75 | &emsp;&emsp;→&nbsp;팬 6번 통신 이상 (`VP_FWU_SF-6_Comm_Fault`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 76 | &emsp;→&nbsp;74행 조건이 성립하지 않으면 : |
| 77 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 78 | 73행 조건이 성립하지 않으면 : |
| 79 | &emsp;→&nbsp;팬 6번 통신 이상 (`VP_FWU_SF-6_Comm_Fault`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 80 | &emsp;→&nbsp;타이머 `SF_6_COMM_TIMER`(5번: 팬6 통신 이상이 이어진 시간)를 0초로 초기화 |
| 82 | 팬 7번 현재 RPM (`FWU_SF-7.Current_RPM`)의 알람 코드 = `COMM_FAULT_CODE`(8) 이면 : |
| 83 | &emsp;→&nbsp;타이머 `SF_7_COMM_TIMER`(6번: 팬7 통신 이상이 이어진 시간) 경과시간 > `FAN_COMM_CONFIRM_SECONDS`(10) 이면 : |
| 84 | &emsp;&emsp;→&nbsp;팬 7번 통신 이상 (`VP_FWU_SF-7_Comm_Fault`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 85 | &emsp;→&nbsp;83행 조건이 성립하지 않으면 : |
| 86 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 87 | 82행 조건이 성립하지 않으면 : |
| 88 | &emsp;→&nbsp;팬 7번 통신 이상 (`VP_FWU_SF-7_Comm_Fault`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 89 | &emsp;→&nbsp;타이머 `SF_7_COMM_TIMER`(6번: 팬7 통신 이상이 이어진 시간)를 0초로 초기화 |
| 91 | 팬 8번 현재 RPM (`FWU_SF-8.Current_RPM`)의 알람 코드 = `COMM_FAULT_CODE`(8) 이면 : |
| 92 | &emsp;→&nbsp;타이머 `SF_8_COMM_TIMER`(7번: 팬8 통신 이상이 이어진 시간) 경과시간 > `FAN_COMM_CONFIRM_SECONDS`(10) 이면 : |
| 93 | &emsp;&emsp;→&nbsp;팬 8번 통신 이상 (`VP_FWU_SF-8_Comm_Fault`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 94 | &emsp;→&nbsp;92행 조건이 성립하지 않으면 : |
| 95 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 96 | 91행 조건이 성립하지 않으면 : |
| 97 | &emsp;→&nbsp;팬 8번 통신 이상 (`VP_FWU_SF-8_Comm_Fault`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 98 | &emsp;→&nbsp;타이머 `SF_8_COMM_TIMER`(7번: 팬8 통신 이상이 이어진 시간)를 0초로 초기화 |

<a id="section-3"></a>

## 100~104행 · 팬 통신 종합: 한 대라도 이상이면 TRUE (SF Control이 이 값을 보고 AO 출력으로 바꾼다)

| 행 | 해석 |
|---:|---|
| 100 | *[주석] 팬 통신 종합: 한 대라도 이상이면 TRUE (SF Control이 이 값을 보고 AO 출력으로 바꾼다)* |
| 101 | 팬 1번 통신 이상 (`VP_FWU_SF-1_Comm_Fault`) = TRUE(1) **또는** 팬 2번 통신 이상 (`VP_FWU_SF-2_Comm_Fault`) = TRUE(1) **또는** 팬 3번 통신 이상 (`VP_FWU_SF-3_Comm_Fault`) = TRUE(1) **또는** 팬 4번 통신 이상 (`VP_FWU_SF-4_Comm_Fault`) = TRUE(1) **또는** 팬 5번 통신 이상 (`VP_FWU_SF-5_Comm_Fault`) = TRUE(1) **또는** 팬 6번 통신 이상 (`VP_FWU_SF-6_Comm_Fault`) = TRUE(1) **또는** 팬 7번 통신 이상 (`VP_FWU_SF-7_Comm_Fault`) = TRUE(1) **또는** 팬 8번 통신 이상 (`VP_FWU_SF-8_Comm_Fault`) = TRUE(1) 이면 : |
| 102 | &emsp;→&nbsp;팬 통신 이상 종합 (`VP_FWU_SF_Comm_Fault`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 103 | 101행 조건이 성립하지 않으면 : |
| 104 | &emsp;→&nbsp;팬 통신 이상 종합 (`VP_FWU_SF_Comm_Fault`)에 FALSE(0) 기록 — 기본 우선순위(P5) |

<a id="section-4"></a>

## 106~117행 · ATS 통신 이상

| 행 | 해석 |
|---:|---|
| 106 | *[주석] ATS 통신 이상* |
| 107 | ATS 현재 전원 통신점 (`FWU_ATS.Current_Power`)의 알람 코드 = `COMM_FAULT_CODE`(8) 이면 : |
| 108 | &emsp;→&nbsp;타이머 `ATS_COMM_TIMER`(8번: ATS 통신 이상이 이어진 시간) 경과시간 > `ATS_COMM_CONFIRM_SECONDS`(10) 이면 : |
| 109 | &emsp;&emsp;→&nbsp;ATS 통신 이상 (`VP_FWU_ATS_Comm_Fault`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 110 | &emsp;→&nbsp;108행 조건이 성립하지 않으면 : |
| 111 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 112 | 107행 조건이 성립하지 않으면 : |
| 113 | &emsp;→&nbsp;ATS 통신 이상 (`VP_FWU_ATS_Comm_Fault`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 114 | &emsp;→&nbsp;타이머 `ATS_COMM_TIMER`(8번: ATS 통신 이상이 이어진 시간)를 0초로 초기화 |
| 116 | *[주석] JSY 2026-11-23 수정 구간 끝. 주제 = Alarm-3에서 이름 변경(팬·ATS 통신 이상 알람만 남아 내용에 맞춤), Coding Rule 적용* |
| 117 | *[주석] LJH 2026-11-17 수정 표시. 주제 = 기존 단일 유량계 감시 분리* |
