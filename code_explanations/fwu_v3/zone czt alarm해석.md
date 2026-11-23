# Zone CZT Alarm 줄별 해석

> **대상 코드** : `fwu_v3/Logic/Zone CZT Alarm.py` (124 줄, refac 예제 원본)  
> **기준** : `sy 브랜치 2026-11-23 (naming rule·관제점 이름 변경 반영)`  
> **행** = 코드 줄 번호 (빈 줄은 생략)  
> **표기** : `→` 들여쓰기 단계 · *[주석]* 코드 안 주석 · `이름` 코드 안 상수·변수 · **※** 읽을 때 주의할 점

사용하도록 설정한 냉복도 온도 센서의 값이 0℃ 미만인 상태가 20초를 넘으면 센서 고장 알람을 낸다. refac 예제 원본 파일이다.

**목차**

- [1~23행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수](#section-1)
- [25~33행 · CZT-1 check](#section-2)
- [35~43행 · CZT-2 check](#section-3)
- [45~53행 · CZT-3 check](#section-4)
- [55~63행 · CZT-4 check](#section-5)
- [65~73행 · CZT-5 check](#section-6)
- [75~83행 · CZT-6 check](#section-7)
- [85~93행 · CZT-7 check](#section-8)
- [95~103행 · CZT-8 check](#section-9)
- [105~113행 · CZT-9 check](#section-10)
- [115~124행 · CZT-10 check](#section-11)

**※ 공통 표기**: 매크로 상수 TRUE·ON·SET·TMR_READ·DEC = 1, FALSE·OFF·CLEAR·TMR_CLEAR·INC = 0. `SECTIMER(타이머, TMR_CLEAR)`는 타이머를 0초로 초기화, `SECTIMER(타이머, TMR_READ)`는 경과시간 확인이다. P번호가 없는 쓰기(`WRITEPOINT`)는 기본 우선순위 P5를 쓴다. 조건이 거짓이라고 관제점이 저절로 0이 되지는 않는다. 해당 분기에 쓰기가 없으면 이전 값이 남는다. 대문자 이름은 상수, `m`으로 시작하는 이름은 이 파일의 전역변수, `b`가 붙은 이름은 참/거짓 값이다.

<a id="section-1"></a>

## 1~23행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수

| 행 | 해석 |
|---:|---|
| 1 | *[주석] 로직엔진 loading* |
| 2 | DDC 로직 엔진 객체 생성 (이후 engine.xxx로 관제점을 읽고 씀) |
| 4 | *[주석] Macro상수 정의* |
| 5 | 매크로 상수 정의: TMR_READ, SET, ON, TRUE, DEC = 1 (긍정의 의미 또는 1인 인자) |
| 6 | 매크로 상수 정의: TMR_CLEAR, CLEAR, OFF, FALSE, INC = 0 (부정의 의미 또는 0인 인자) |
| 7 | 상수 `CZT_FAIL_TIME_OUT` = 20<br>*[주석] CZT Timer는 20초 까지* |
| 8 | 상수 `CZT_FAIL_TEMP` = 0<br>*[주석] CZT온도가 0도 미만이면 fail로 간주* |
| 9 | 설정값 상수 `INST_CZT_QTY`: 냉복도 온도 사용 센서 수 설정 (`VP_FWU_CZT_Count`) 값을 읽어 둠<br>*[주석] 설치된 CZT온도센서 갯수(Quantity)* |
| 11 | *[주석] 타이머 정의* |
| 12 | 타이머 번호 상수 `CZT_1_FAIL_TIMER` = 0번 |
| 13 | 타이머 번호 상수 `CZT_2_FAIL_TIMER` = 1번 |
| 14 | 타이머 번호 상수 `CZT_3_FAIL_TIMER` = 2번 |
| 15 | 타이머 번호 상수 `CZT_4_FAIL_TIMER` = 3번 |
| 16 | 타이머 번호 상수 `CZT_5_FAIL_TIMER` = 4번 |
| 17 | 타이머 번호 상수 `CZT_6_FAIL_TIMER` = 5번 |
| 18 | 타이머 번호 상수 `CZT_7_FAIL_TIMER` = 6번 |
| 19 | 타이머 번호 상수 `CZT_8_FAIL_TIMER` = 7번 |
| 20 | 타이머 번호 상수 `CZT_9_FAIL_TIMER` = 8번 |
| 21 | 타이머 번호 상수 `CZT_10_FAIL_TIMER` = 9번 |
| 23 | *[주석] 미사용 센서는 알람과 타이머를 해제한다. 기존 20초 판정 유지.* |

<a id="section-2"></a>

## 25~33행 · CZT-1 check

| 행 | 해석 |
|---:|---|
| 25 | *[주석] CZT-1 check* |
| 26 | `INST_CZT_QTY`(설정값) ≥ 1 **그리고** 냉복도 온도 1번 값 (`VP_FWU_CZT-1`) < `CZT_FAIL_TEMP`(0) 이면 : |
| 27 | &emsp;→&nbsp;타이머 `CZT_1_FAIL_TIMER`(0번: 냉복도 온도 1번 고장 확인) 경과시간 > `CZT_FAIL_TIME_OUT`(20) 이면 : |
| 28 | &emsp;&emsp;→&nbsp;냉복도 온도 1번 센서 고장 알람 (`VP_FWU_CZT-1_Failure_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 29 | &emsp;→&nbsp;27행 조건이 성립하지 않으면 : |
| 30 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 31 | 26행 조건이 성립하지 않으면 : |
| 32 | &emsp;→&nbsp;타이머 `CZT_1_FAIL_TIMER`(0번: 냉복도 온도 1번 고장 확인)를 0초로 초기화 |
| 33 | &emsp;→&nbsp;냉복도 온도 1번 센서 고장 알람 (`VP_FWU_CZT-1_Failure_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |

<a id="section-3"></a>

## 35~43행 · CZT-2 check

| 행 | 해석 |
|---:|---|
| 35 | *[주석] CZT-2 check* |
| 36 | `INST_CZT_QTY`(설정값) ≥ 2 **그리고** 냉복도 온도 2번 값 (`VP_FWU_CZT-2`) < `CZT_FAIL_TEMP`(0) 이면 : |
| 37 | &emsp;→&nbsp;타이머 `CZT_2_FAIL_TIMER`(1번: 냉복도 온도 2번 고장 확인) 경과시간 > `CZT_FAIL_TIME_OUT`(20) 이면 : |
| 38 | &emsp;&emsp;→&nbsp;냉복도 온도 2번 센서 고장 알람 (`VP_FWU_CZT-2_Failure_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 39 | &emsp;→&nbsp;37행 조건이 성립하지 않으면 : |
| 40 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 41 | 36행 조건이 성립하지 않으면 : |
| 42 | &emsp;→&nbsp;타이머 `CZT_2_FAIL_TIMER`(1번: 냉복도 온도 2번 고장 확인)를 0초로 초기화 |
| 43 | &emsp;→&nbsp;냉복도 온도 2번 센서 고장 알람 (`VP_FWU_CZT-2_Failure_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |

<a id="section-4"></a>

## 45~53행 · CZT-3 check

| 행 | 해석 |
|---:|---|
| 45 | *[주석] CZT-3 check* |
| 46 | `INST_CZT_QTY`(설정값) ≥ 3 **그리고** 냉복도 온도 3번 값 (`VP_FWU_CZT-3`) < `CZT_FAIL_TEMP`(0) 이면 : |
| 47 | &emsp;→&nbsp;타이머 `CZT_3_FAIL_TIMER`(2번: 냉복도 온도 3번 고장 확인) 경과시간 > `CZT_FAIL_TIME_OUT`(20) 이면 : |
| 48 | &emsp;&emsp;→&nbsp;냉복도 온도 3번 센서 고장 알람 (`VP_FWU_CZT-3_Failure_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 49 | &emsp;→&nbsp;47행 조건이 성립하지 않으면 : |
| 50 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 51 | 46행 조건이 성립하지 않으면 : |
| 52 | &emsp;→&nbsp;타이머 `CZT_3_FAIL_TIMER`(2번: 냉복도 온도 3번 고장 확인)를 0초로 초기화 |
| 53 | &emsp;→&nbsp;냉복도 온도 3번 센서 고장 알람 (`VP_FWU_CZT-3_Failure_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |

<a id="section-5"></a>

## 55~63행 · CZT-4 check

| 행 | 해석 |
|---:|---|
| 55 | *[주석] CZT-4 check* |
| 56 | `INST_CZT_QTY`(설정값) ≥ 4 **그리고** 냉복도 온도 4번 값 (`VP_FWU_CZT-4`) < `CZT_FAIL_TEMP`(0) 이면 : |
| 57 | &emsp;→&nbsp;타이머 `CZT_4_FAIL_TIMER`(3번: 냉복도 온도 4번 고장 확인) 경과시간 > `CZT_FAIL_TIME_OUT`(20) 이면 : |
| 58 | &emsp;&emsp;→&nbsp;냉복도 온도 4번 센서 고장 알람 (`VP_FWU_CZT-4_Failure_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 59 | &emsp;→&nbsp;57행 조건이 성립하지 않으면 : |
| 60 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 61 | 56행 조건이 성립하지 않으면 : |
| 62 | &emsp;→&nbsp;타이머 `CZT_4_FAIL_TIMER`(3번: 냉복도 온도 4번 고장 확인)를 0초로 초기화 |
| 63 | &emsp;→&nbsp;냉복도 온도 4번 센서 고장 알람 (`VP_FWU_CZT-4_Failure_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |

<a id="section-6"></a>

## 65~73행 · CZT-5 check

| 행 | 해석 |
|---:|---|
| 65 | *[주석] CZT-5 check* |
| 66 | `INST_CZT_QTY`(설정값) ≥ 5 **그리고** 냉복도 온도 5번 값 (`VP_FWU_CZT-5`) < `CZT_FAIL_TEMP`(0) 이면 : |
| 67 | &emsp;→&nbsp;타이머 `CZT_5_FAIL_TIMER`(4번: 냉복도 온도 5번 고장 확인) 경과시간 > `CZT_FAIL_TIME_OUT`(20) 이면 : |
| 68 | &emsp;&emsp;→&nbsp;냉복도 온도 5번 센서 고장 알람 (`VP_FWU_CZT-5_Failure_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 69 | &emsp;→&nbsp;67행 조건이 성립하지 않으면 : |
| 70 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 71 | 66행 조건이 성립하지 않으면 : |
| 72 | &emsp;→&nbsp;타이머 `CZT_5_FAIL_TIMER`(4번: 냉복도 온도 5번 고장 확인)를 0초로 초기화 |
| 73 | &emsp;→&nbsp;냉복도 온도 5번 센서 고장 알람 (`VP_FWU_CZT-5_Failure_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |

<a id="section-7"></a>

## 75~83행 · CZT-6 check

| 행 | 해석 |
|---:|---|
| 75 | *[주석] CZT-6 check* |
| 76 | `INST_CZT_QTY`(설정값) ≥ 6 **그리고** 냉복도 온도 6번 값 (`VP_FWU_CZT-6`) < `CZT_FAIL_TEMP`(0) 이면 : |
| 77 | &emsp;→&nbsp;타이머 `CZT_6_FAIL_TIMER`(5번: 냉복도 온도 6번 고장 확인) 경과시간 > `CZT_FAIL_TIME_OUT`(20) 이면 : |
| 78 | &emsp;&emsp;→&nbsp;냉복도 온도 6번 센서 고장 알람 (`VP_FWU_CZT-6_Failure_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 79 | &emsp;→&nbsp;77행 조건이 성립하지 않으면 : |
| 80 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 81 | 76행 조건이 성립하지 않으면 : |
| 82 | &emsp;→&nbsp;타이머 `CZT_6_FAIL_TIMER`(5번: 냉복도 온도 6번 고장 확인)를 0초로 초기화 |
| 83 | &emsp;→&nbsp;냉복도 온도 6번 센서 고장 알람 (`VP_FWU_CZT-6_Failure_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |

<a id="section-8"></a>

## 85~93행 · CZT-7 check

| 행 | 해석 |
|---:|---|
| 85 | *[주석] CZT-7 check* |
| 86 | `INST_CZT_QTY`(설정값) ≥ 7 **그리고** 냉복도 온도 7번 값 (`VP_FWU_CZT-7`) < `CZT_FAIL_TEMP`(0) 이면 : |
| 87 | &emsp;→&nbsp;타이머 `CZT_7_FAIL_TIMER`(6번: 냉복도 온도 7번 고장 확인) 경과시간 > `CZT_FAIL_TIME_OUT`(20) 이면 : |
| 88 | &emsp;&emsp;→&nbsp;냉복도 온도 7번 센서 고장 알람 (`VP_FWU_CZT-7_Failure_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 89 | &emsp;→&nbsp;87행 조건이 성립하지 않으면 : |
| 90 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 91 | 86행 조건이 성립하지 않으면 : |
| 92 | &emsp;→&nbsp;타이머 `CZT_7_FAIL_TIMER`(6번: 냉복도 온도 7번 고장 확인)를 0초로 초기화 |
| 93 | &emsp;→&nbsp;냉복도 온도 7번 센서 고장 알람 (`VP_FWU_CZT-7_Failure_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |

<a id="section-9"></a>

## 95~103행 · CZT-8 check

| 행 | 해석 |
|---:|---|
| 95 | *[주석] CZT-8 check* |
| 96 | `INST_CZT_QTY`(설정값) ≥ 8 **그리고** 냉복도 온도 8번 값 (`VP_FWU_CZT-8`) < `CZT_FAIL_TEMP`(0) 이면 : |
| 97 | &emsp;→&nbsp;타이머 `CZT_8_FAIL_TIMER`(7번: 냉복도 온도 8번 고장 확인) 경과시간 > `CZT_FAIL_TIME_OUT`(20) 이면 : |
| 98 | &emsp;&emsp;→&nbsp;냉복도 온도 8번 센서 고장 알람 (`VP_FWU_CZT-8_Failure_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 99 | &emsp;→&nbsp;97행 조건이 성립하지 않으면 : |
| 100 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 101 | 96행 조건이 성립하지 않으면 : |
| 102 | &emsp;→&nbsp;타이머 `CZT_8_FAIL_TIMER`(7번: 냉복도 온도 8번 고장 확인)를 0초로 초기화 |
| 103 | &emsp;→&nbsp;냉복도 온도 8번 센서 고장 알람 (`VP_FWU_CZT-8_Failure_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |

<a id="section-10"></a>

## 105~113행 · CZT-9 check

| 행 | 해석 |
|---:|---|
| 105 | *[주석] CZT-9 check* |
| 106 | `INST_CZT_QTY`(설정값) ≥ 9 **그리고** 냉복도 온도 9번 값 (`VP_FWU_CZT-9`) < `CZT_FAIL_TEMP`(0) 이면 : |
| 107 | &emsp;→&nbsp;타이머 `CZT_9_FAIL_TIMER`(8번: 냉복도 온도 9번 고장 확인) 경과시간 > `CZT_FAIL_TIME_OUT`(20) 이면 : |
| 108 | &emsp;&emsp;→&nbsp;냉복도 온도 9번 센서 고장 알람 (`VP_FWU_CZT-9_Failure_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 109 | &emsp;→&nbsp;107행 조건이 성립하지 않으면 : |
| 110 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 111 | 106행 조건이 성립하지 않으면 : |
| 112 | &emsp;→&nbsp;타이머 `CZT_9_FAIL_TIMER`(8번: 냉복도 온도 9번 고장 확인)를 0초로 초기화 |
| 113 | &emsp;→&nbsp;냉복도 온도 9번 센서 고장 알람 (`VP_FWU_CZT-9_Failure_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |

<a id="section-11"></a>

## 115~124행 · CZT-10 check

| 행 | 해석 |
|---:|---|
| 115 | *[주석] CZT-10 check* |
| 116 | `INST_CZT_QTY`(설정값) ≥ 10 **그리고** 냉복도 온도 10번 값 (`VP_FWU_CZT-10`) < `CZT_FAIL_TEMP`(0) 이면 : |
| 117 | &emsp;→&nbsp;타이머 `CZT_10_FAIL_TIMER`(9번: 냉복도 온도 10번 고장 확인) 경과시간 > `CZT_FAIL_TIME_OUT`(20) 이면 : |
| 118 | &emsp;&emsp;→&nbsp;냉복도 온도 10번 센서 고장 알람 (`VP_FWU_CZT-10_Failure_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 119 | &emsp;→&nbsp;117행 조건이 성립하지 않으면 : |
| 120 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 121 | 116행 조건이 성립하지 않으면 : |
| 122 | &emsp;→&nbsp;타이머 `CZT_10_FAIL_TIMER`(9번: 냉복도 온도 10번 고장 확인)를 0초로 초기화 |
| 123 | &emsp;→&nbsp;냉복도 온도 10번 센서 고장 알람 (`VP_FWU_CZT-10_Failure_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 124 | *[주석] LJH 2026-11-17 수정 표시. 주제 = CZT 센서 10개 고장 감시* |
