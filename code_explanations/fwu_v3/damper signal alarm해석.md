# Damper Signal Alarm 줄별 해석

> **대상 코드** : `fwu_v3/Logic/Damper Signal Alarm.py` (100 줄, refac 예제 원본)  
> **기준** : `sy 브랜치 2026-11-23 (naming rule·관제점 이름 변경 반영)`  
> **행** = 코드 줄 번호 (빈 줄은 생략)  
> **표기** : `→` 들여쓰기 단계 · *[주석]* 코드 안 주석 · `이름` 코드 안 상수·변수 · **※** 읽을 때 주의할 점

댐퍼 4개의 열림·닫힘 접점이 둘 다 꺼져 있거나(위치 미확인) 둘 다 켜져 있는(접점 모순) 상태를 감시한다. refac 예제 원본 파일이다.

**목차**

- [1~23행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수](#section-1)
- [25~42행 · 댐퍼1의 unknown 및 conflict alarm 처리](#section-2)
- [44~61행 · 댐퍼2의 unknown 및 conflict alarm 처리](#section-3)
- [63~80행 · 댐퍼3의 unknown 및 conflict alarm 처리](#section-4)
- [82~100행 · 댐퍼4의 unknown 및 conflict alarm 처리](#section-5)

**※ 공통 표기**: 매크로 상수 TRUE·ON·SET·TMR_READ·DEC = 1, FALSE·OFF·CLEAR·TMR_CLEAR·INC = 0. `SECTIMER(타이머, TMR_CLEAR)`는 타이머를 0초로 초기화, `SECTIMER(타이머, TMR_READ)`는 경과시간 확인이다. P번호가 없는 쓰기(`WRITEPOINT`)는 기본 우선순위 P5를 쓴다. 조건이 거짓이라고 관제점이 저절로 0이 되지는 않는다. 해당 분기에 쓰기가 없으면 이전 값이 남는다. 대문자 이름은 상수, `m`으로 시작하는 이름은 이 파일의 전역변수, `b`가 붙은 이름은 참/거짓 값이다.

<a id="section-1"></a>

## 1~23행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수

| 행 | 해석 |
|---:|---|
| 1 | *[주석] 로직엔진 loading* |
| 2 | DDC 로직 엔진 객체 생성 (이후 engine.xxx로 관제점을 읽고 씀) |
| 4 | *[주석] Macro상수 정의:* |
| 5 | 매크로 상수 정의: TMR_READ, SET, ON, TRUE, DEC = 1 (긍정의 의미 또는 1인 인자) |
| 6 | 매크로 상수 정의: TMR_CLEAR, CLEAR, OFF, FALSE, INC = 0 (부정의 의미 또는 0인 인자) |
| 8 | *[주석] 타이머 정의: 댐퍼의 unknown delay 대응용* |
| 9 | 타이머 번호 상수 `SAD_1_UNKNOWN_TIMER` = 0번 |
| 10 | 타이머 번호 상수 `SAD_2_UNKNOWN_TIMER` = 1번 |
| 11 | 타이머 번호 상수 `SAD_3_UNKNOWN_TIMER` = 2번 |
| 12 | 타이머 번호 상수 `SAD_4_UNKNOWN_TIMER` = 3번 |
| 14 | *[주석] 타이머 정의: 댐퍼 상태의 conflict(open과 closed가 동시에 만족) 대응용* |
| 15 | 타이머 번호 상수 `SAD_1_CONFLICT_TIMER` = 4번 |
| 16 | 타이머 번호 상수 `SAD_2_CONFLICT_TIMER` = 5번 |
| 17 | 타이머 번호 상수 `SAD_3_CONFLICT_TIMER` = 6번 |
| 18 | 타이머 번호 상수 `SAD_4_CONFLICT_TIMER` = 7번 |
| 21 | *[주석] 전역변수 선언* |
| 22 | 전역변수 `mbSFstat` ← 팬 운전 상태 (`VP_FWU_SF_Status`) = 1 이면 TRUE, 아니면 FALSE<br>*[주석] 모든 SF의 상태가 정상이면 TRUE, 아니면 FALSE (?)* |
| 23 | 전역변수 `mbSADcmd` ← 댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`) = 1 이면 TRUE, 아니면 FALSE<br>*[주석] SAD CMD가 정상이면 TRUE, 아니면 FALSE (?)* |

<a id="section-2"></a>

## 25~42행 · 댐퍼1의 unknown 및 conflict alarm 처리

| 행 | 해석 |
|---:|---|
| 25 | *[주석] 댐퍼1의 unknown 및 conflict alarm 처리* |
| 26 | `mbSFstat` = TRUE **그리고** `mbSADcmd` = TRUE **그리고** 댐퍼 1번 열림 접점 (`FWU_SAD-1_OPEN_STATUS`) = FALSE(0) **그리고** 댐퍼 1번 닫힘 접점 (`FWU_SAD-1_CLOSE_STATUS`) = FALSE(0) 이면 : |
| 27 | &emsp;→&nbsp;타이머 `SAD_1_UNKNOWN_TIMER`(0번: 댐퍼 1번 위치 미확인 확인) 경과시간 > 댐퍼 위치 미확인 판정 시간 설정 (`VP_FWU_SAD_Unknown_Delay`) 이면 : |
| 28 | &emsp;&emsp;→&nbsp;댐퍼 1번 위치 미확인 알람 (`VP_FWU_SAD-1_Position_Unknown_Alarm`)에 SET(1) 기록 — 기본 우선순위(P5) |
| 29 | &emsp;→&nbsp;27행 조건이 성립하지 않으면 : |
| 30 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 31 | 26행 조건이 성립하지 않으면 : |
| 32 | &emsp;→&nbsp;타이머 `SAD_1_UNKNOWN_TIMER`(0번: 댐퍼 1번 위치 미확인 확인)를 0초로 초기화 |
| 33 | &emsp;→&nbsp;댐퍼 1번 위치 미확인 알람 (`VP_FWU_SAD-1_Position_Unknown_Alarm`)에 CLEAR(0) 기록 — 기본 우선순위(P5) |
| 35 | 댐퍼 1번 열림 접점 (`FWU_SAD-1_OPEN_STATUS`) = TRUE(1) **그리고** 댐퍼 1번 닫힘 접점 (`FWU_SAD-1_CLOSE_STATUS`) = TRUE(1) 이면 : |
| 36 | &emsp;→&nbsp;타이머 `SAD_1_CONFLICT_TIMER`(4번: 댐퍼 1번 접점 모순 확인) 경과시간 > 댐퍼 접점 모순 판정 시간 설정 (`VP_FWU_SAD_Conflict_Delay`) 이면 : |
| 37 | &emsp;&emsp;→&nbsp;댐퍼 1번 접점 모순 알람 (`VP_FWU_SAD-1_Signal_Conflict_Alarm`)에 SET(1) 기록 — 기본 우선순위(P5) |
| 38 | &emsp;→&nbsp;36행 조건이 성립하지 않으면 : |
| 39 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 40 | 35행 조건이 성립하지 않으면 : |
| 41 | &emsp;→&nbsp;타이머 `SAD_1_CONFLICT_TIMER`(4번: 댐퍼 1번 접점 모순 확인)를 0초로 초기화 |
| 42 | &emsp;→&nbsp;댐퍼 1번 접점 모순 알람 (`VP_FWU_SAD-1_Signal_Conflict_Alarm`)에 CLEAR(0) 기록 — 기본 우선순위(P5) |

<a id="section-3"></a>

## 44~61행 · 댐퍼2의 unknown 및 conflict alarm 처리

| 행 | 해석 |
|---:|---|
| 44 | *[주석] 댐퍼2의 unknown 및 conflict alarm 처리* |
| 45 | `mbSFstat` = TRUE **그리고** `mbSADcmd` = TRUE **그리고** 댐퍼 2번 열림 접점 (`FWU_SAD-2_OPEN_STATUS`) = FALSE(0) **그리고** 댐퍼 2번 닫힘 접점 (`FWU_SAD-2_CLOSE_STATUS`) = FALSE(0) 이면 : |
| 46 | &emsp;→&nbsp;타이머 `SAD_2_UNKNOWN_TIMER`(1번: 댐퍼 2번 위치 미확인 확인) 경과시간 > 댐퍼 위치 미확인 판정 시간 설정 (`VP_FWU_SAD_Unknown_Delay`) 이면 : |
| 47 | &emsp;&emsp;→&nbsp;댐퍼 2번 위치 미확인 알람 (`VP_FWU_SAD-2_Position_Unknown_Alarm`)에 SET(1) 기록 — 기본 우선순위(P5) |
| 48 | &emsp;→&nbsp;46행 조건이 성립하지 않으면 : |
| 49 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 50 | 45행 조건이 성립하지 않으면 : |
| 51 | &emsp;→&nbsp;타이머 `SAD_2_UNKNOWN_TIMER`(1번: 댐퍼 2번 위치 미확인 확인)를 0초로 초기화 |
| 52 | &emsp;→&nbsp;댐퍼 2번 위치 미확인 알람 (`VP_FWU_SAD-2_Position_Unknown_Alarm`)에 CLEAR(0) 기록 — 기본 우선순위(P5) |
| 54 | 댐퍼 2번 열림 접점 (`FWU_SAD-2_OPEN_STATUS`) = TRUE(1) **그리고** 댐퍼 2번 닫힘 접점 (`FWU_SAD-2_CLOSE_STATUS`) = TRUE(1) 이면 : |
| 55 | &emsp;→&nbsp;타이머 `SAD_2_CONFLICT_TIMER`(5번: 댐퍼 2번 접점 모순 확인) 경과시간 > 댐퍼 접점 모순 판정 시간 설정 (`VP_FWU_SAD_Conflict_Delay`) 이면 : |
| 56 | &emsp;&emsp;→&nbsp;댐퍼 2번 접점 모순 알람 (`VP_FWU_SAD-2_Signal_Conflict_Alarm`)에 SET(1) 기록 — 기본 우선순위(P5) |
| 57 | &emsp;→&nbsp;55행 조건이 성립하지 않으면 : |
| 58 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 59 | 54행 조건이 성립하지 않으면 : |
| 60 | &emsp;→&nbsp;타이머 `SAD_2_CONFLICT_TIMER`(5번: 댐퍼 2번 접점 모순 확인)를 0초로 초기화 |
| 61 | &emsp;→&nbsp;댐퍼 2번 접점 모순 알람 (`VP_FWU_SAD-2_Signal_Conflict_Alarm`)에 CLEAR(0) 기록 — 기본 우선순위(P5) |

<a id="section-4"></a>

## 63~80행 · 댐퍼3의 unknown 및 conflict alarm 처리

| 행 | 해석 |
|---:|---|
| 63 | *[주석] 댐퍼3의 unknown 및 conflict alarm 처리* |
| 64 | `mbSFstat` = TRUE **그리고** `mbSADcmd` = TRUE **그리고** 댐퍼 3번 열림 접점 (`FWU_SAD-3_OPEN_STATUS`) = FALSE(0) **그리고** 댐퍼 3번 닫힘 접점 (`FWU_SAD-3_CLOSE_STATUS`) = FALSE(0) 이면 : |
| 65 | &emsp;→&nbsp;타이머 `SAD_3_UNKNOWN_TIMER`(2번: 댐퍼 3번 위치 미확인 확인) 경과시간 > 댐퍼 위치 미확인 판정 시간 설정 (`VP_FWU_SAD_Unknown_Delay`) 이면 : |
| 66 | &emsp;&emsp;→&nbsp;댐퍼 3번 위치 미확인 알람 (`VP_FWU_SAD-3_Position_Unknown_Alarm`)에 SET(1) 기록 — 기본 우선순위(P5) |
| 67 | &emsp;→&nbsp;65행 조건이 성립하지 않으면 : |
| 68 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 69 | 64행 조건이 성립하지 않으면 : |
| 70 | &emsp;→&nbsp;타이머 `SAD_3_UNKNOWN_TIMER`(2번: 댐퍼 3번 위치 미확인 확인)를 0초로 초기화 |
| 71 | &emsp;→&nbsp;댐퍼 3번 위치 미확인 알람 (`VP_FWU_SAD-3_Position_Unknown_Alarm`)에 CLEAR(0) 기록 — 기본 우선순위(P5) |
| 73 | 댐퍼 3번 열림 접점 (`FWU_SAD-3_OPEN_STATUS`) = TRUE(1) **그리고** 댐퍼 3번 닫힘 접점 (`FWU_SAD-3_CLOSE_STATUS`) = TRUE(1) 이면 : |
| 74 | &emsp;→&nbsp;타이머 `SAD_3_CONFLICT_TIMER`(6번: 댐퍼 3번 접점 모순 확인) 경과시간 > 댐퍼 접점 모순 판정 시간 설정 (`VP_FWU_SAD_Conflict_Delay`) 이면 : |
| 75 | &emsp;&emsp;→&nbsp;댐퍼 3번 접점 모순 알람 (`VP_FWU_SAD-3_Signal_Conflict_Alarm`)에 SET(1) 기록 — 기본 우선순위(P5) |
| 76 | &emsp;→&nbsp;74행 조건이 성립하지 않으면 : |
| 77 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 78 | 73행 조건이 성립하지 않으면 : |
| 79 | &emsp;→&nbsp;타이머 `SAD_3_CONFLICT_TIMER`(6번: 댐퍼 3번 접점 모순 확인)를 0초로 초기화 |
| 80 | &emsp;→&nbsp;댐퍼 3번 접점 모순 알람 (`VP_FWU_SAD-3_Signal_Conflict_Alarm`)에 CLEAR(0) 기록 — 기본 우선순위(P5) |

<a id="section-5"></a>

## 82~100행 · 댐퍼4의 unknown 및 conflict alarm 처리

| 행 | 해석 |
|---:|---|
| 82 | *[주석] 댐퍼4의 unknown 및 conflict alarm 처리* |
| 83 | `mbSFstat` = TRUE **그리고** `mbSADcmd` = TRUE **그리고** 댐퍼 4번 열림 접점 (`FWU_SAD-4_OPEN_STATUS`) = FALSE(0) **그리고** 댐퍼 4번 닫힘 접점 (`FWU_SAD-4_CLOSE_STATUS`) = FALSE(0) 이면 : |
| 84 | &emsp;→&nbsp;타이머 `SAD_4_UNKNOWN_TIMER`(3번: 댐퍼 4번 위치 미확인 확인) 경과시간 > 댐퍼 위치 미확인 판정 시간 설정 (`VP_FWU_SAD_Unknown_Delay`) 이면 : |
| 85 | &emsp;&emsp;→&nbsp;댐퍼 4번 위치 미확인 알람 (`VP_FWU_SAD-4_Position_Unknown_Alarm`)에 SET(1) 기록 — 기본 우선순위(P5) |
| 86 | &emsp;→&nbsp;84행 조건이 성립하지 않으면 : |
| 87 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 88 | 83행 조건이 성립하지 않으면 : |
| 89 | &emsp;→&nbsp;타이머 `SAD_4_UNKNOWN_TIMER`(3번: 댐퍼 4번 위치 미확인 확인)를 0초로 초기화 |
| 90 | &emsp;→&nbsp;댐퍼 4번 위치 미확인 알람 (`VP_FWU_SAD-4_Position_Unknown_Alarm`)에 CLEAR(0) 기록 — 기본 우선순위(P5) |
| 92 | 댐퍼 4번 열림 접점 (`FWU_SAD-4_OPEN_STATUS`) = TRUE(1) **그리고** 댐퍼 4번 닫힘 접점 (`FWU_SAD-4_CLOSE_STATUS`) = TRUE(1) 이면 : |
| 93 | &emsp;→&nbsp;타이머 `SAD_4_CONFLICT_TIMER`(7번: 댐퍼 4번 접점 모순 확인) 경과시간 > 댐퍼 접점 모순 판정 시간 설정 (`VP_FWU_SAD_Conflict_Delay`) 이면 : |
| 94 | &emsp;&emsp;→&nbsp;댐퍼 4번 접점 모순 알람 (`VP_FWU_SAD-4_Signal_Conflict_Alarm`)에 SET(1) 기록 — 기본 우선순위(P5) |
| 95 | &emsp;→&nbsp;93행 조건이 성립하지 않으면 : |
| 96 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 97 | 92행 조건이 성립하지 않으면 : |
| 98 | &emsp;→&nbsp;타이머 `SAD_4_CONFLICT_TIMER`(7번: 댐퍼 4번 접점 모순 확인)를 0초로 초기화 |
| 99 | &emsp;→&nbsp;댐퍼 4번 접점 모순 알람 (`VP_FWU_SAD-4_Signal_Conflict_Alarm`)에 CLEAR(0) 기록 — 기본 우선순위(P5) |
| 100 | *[주석] LJH 2026-11-17 수정 표시. 주제 = 댐퍼 위치 미확인 및 접점 모순 감시* |
