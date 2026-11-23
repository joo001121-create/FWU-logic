# Zone RDP Alarm 줄별 해석

> **대상 코드** : `fwu_v3/Logic/Zone RDP Alarm.py` (104 줄, refac 예제 원본)  
> **기준** : `sy 브랜치 2026-11-23 (naming rule·관제점 이름 변경 반영)`  
> **행** = 코드 줄 번호 (빈 줄은 생략)  
> **표기** : `→` 들여쓰기 단계 · *[주석]* 코드 안 주석 · `이름` 코드 안 상수·변수 · **※** 읽을 때 주의할 점

사용하도록 설정한 룸 차압 센서의 값이 0 이하인 상태가 20초를 넘으면 센서 고장 알람을 낸다. refac 예제 원본 파일이다.

**※** refac 예제 원본이라 일부 if에 짝이 되는 else가 없다(원본 그대로 해석).

**목차**

- [1~23행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수](#section-1)
- [25~31행 · RDP-1 check](#section-2)
- [33~39행 · RDP-2 check](#section-3)
- [41~47행 · RDP-3 check](#section-4)
- [49~55행 · RDP-4 check](#section-5)
- [57~63행 · RDP-5 check](#section-6)
- [65~71행 · RDP-6 check](#section-7)
- [73~79행 · RDP-7 check](#section-8)
- [81~87행 · RDP-8 check](#section-9)
- [89~95행 · RDP-9 check](#section-10)
- [97~104행 · RDP-10 check](#section-11)

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
| 7 | 상수 `RDP_FAIL_TIME_OUT` = 20<br>*[주석] RDP Timer는 20초 까지* |
| 8 | 상수 `RDP_FAIL_DP` = 0<br>*[주석] RDP차압이 0Pa 이하이면 fail로 간주* |
| 9 | 설정값 상수 `INST_RDP_QTY`: 룸 차압 사용 센서 수 설정 (`VP_FWU_RDP_Count`) 값을 읽어 둠<br>*[주석] 설치된 RDP차압센서 갯수(Quantity)* |
| 11 | *[주석] 타이머 정의* |
| 12 | 타이머 번호 상수 `RDP_1_FAIL_TIMER` = 0번 |
| 13 | 타이머 번호 상수 `RDP_2_FAIL_TIMER` = 1번 |
| 14 | 타이머 번호 상수 `RDP_3_FAIL_TIMER` = 2번 |
| 15 | 타이머 번호 상수 `RDP_4_FAIL_TIMER` = 3번 |
| 16 | 타이머 번호 상수 `RDP_5_FAIL_TIMER` = 4번 |
| 17 | 타이머 번호 상수 `RDP_6_FAIL_TIMER` = 5번 |
| 18 | 타이머 번호 상수 `RDP_7_FAIL_TIMER` = 6번 |
| 19 | 타이머 번호 상수 `RDP_8_FAIL_TIMER` = 7번 |
| 20 | 타이머 번호 상수 `RDP_9_FAIL_TIMER` = 8번 |
| 21 | 타이머 번호 상수 `RDP_10_FAIL_TIMER` = 9번 |
| 23 | *[주석] 미사용 센서는 알람과 타이머를 해제한다. 기존 20초 판정 유지.* |

<a id="section-2"></a>

## 25~31행 · RDP-1 check

| 행 | 해석 |
|---:|---|
| 25 | *[주석] RDP-1 check* |
| 26 | `INST_RDP_QTY`(설정값) ≥ 1 **그리고** 룸 차압 1번 값 (`VP_FWU_RDP-1`) ≤ `RDP_FAIL_DP`(0) 이면 : |
| 27 | &emsp;→&nbsp;타이머 `RDP_1_FAIL_TIMER`(0번: 룸 차압 1번 고장 확인) 경과시간 > `RDP_FAIL_TIME_OUT`(20) 이면 : |
| 28 | &emsp;&emsp;→&nbsp;룸 차압 1번 센서 고장 알람 (`VP_FWU_RDP-1_Failure_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 29 | 26행 조건이 성립하지 않으면 : |
| 30 | &emsp;→&nbsp;타이머 `RDP_1_FAIL_TIMER`(0번: 룸 차압 1번 고장 확인)를 0초로 초기화 |
| 31 | &emsp;→&nbsp;룸 차압 1번 센서 고장 알람 (`VP_FWU_RDP-1_Failure_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |

<a id="section-3"></a>

## 33~39행 · RDP-2 check

| 행 | 해석 |
|---:|---|
| 33 | *[주석] RDP-2 check* |
| 34 | `INST_RDP_QTY`(설정값) ≥ 2 **그리고** 룸 차압 2번 값 (`VP_FWU_RDP-2`) ≤ `RDP_FAIL_DP`(0) 이면 : |
| 35 | &emsp;→&nbsp;타이머 `RDP_2_FAIL_TIMER`(1번: 룸 차압 2번 고장 확인) 경과시간 > `RDP_FAIL_TIME_OUT`(20) 이면 : |
| 36 | &emsp;&emsp;→&nbsp;룸 차압 2번 센서 고장 알람 (`VP_FWU_RDP-2_Failure_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 37 | 34행 조건이 성립하지 않으면 : |
| 38 | &emsp;→&nbsp;타이머 `RDP_2_FAIL_TIMER`(1번: 룸 차압 2번 고장 확인)를 0초로 초기화 |
| 39 | &emsp;→&nbsp;룸 차압 2번 센서 고장 알람 (`VP_FWU_RDP-2_Failure_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |

<a id="section-4"></a>

## 41~47행 · RDP-3 check

| 행 | 해석 |
|---:|---|
| 41 | *[주석] RDP-3 check* |
| 42 | `INST_RDP_QTY`(설정값) ≥ 3 **그리고** 룸 차압 3번 값 (`VP_FWU_RDP-3`) ≤ `RDP_FAIL_DP`(0) 이면 : |
| 43 | &emsp;→&nbsp;타이머 `RDP_3_FAIL_TIMER`(2번: 룸 차압 3번 고장 확인) 경과시간 > `RDP_FAIL_TIME_OUT`(20) 이면 : |
| 44 | &emsp;&emsp;→&nbsp;룸 차압 3번 센서 고장 알람 (`VP_FWU_RDP-3_Failure_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 45 | 42행 조건이 성립하지 않으면 : |
| 46 | &emsp;→&nbsp;타이머 `RDP_3_FAIL_TIMER`(2번: 룸 차압 3번 고장 확인)를 0초로 초기화 |
| 47 | &emsp;→&nbsp;룸 차압 3번 센서 고장 알람 (`VP_FWU_RDP-3_Failure_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |

<a id="section-5"></a>

## 49~55행 · RDP-4 check

| 행 | 해석 |
|---:|---|
| 49 | *[주석] RDP-4 check* |
| 50 | `INST_RDP_QTY`(설정값) ≥ 4 **그리고** 룸 차압 4번 값 (`VP_FWU_RDP-4`) ≤ `RDP_FAIL_DP`(0) 이면 : |
| 51 | &emsp;→&nbsp;타이머 `RDP_4_FAIL_TIMER`(3번: 룸 차압 4번 고장 확인) 경과시간 > `RDP_FAIL_TIME_OUT`(20) 이면 : |
| 52 | &emsp;&emsp;→&nbsp;룸 차압 4번 센서 고장 알람 (`VP_FWU_RDP-4_Failure_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 53 | 50행 조건이 성립하지 않으면 : |
| 54 | &emsp;→&nbsp;타이머 `RDP_4_FAIL_TIMER`(3번: 룸 차압 4번 고장 확인)를 0초로 초기화 |
| 55 | &emsp;→&nbsp;룸 차압 4번 센서 고장 알람 (`VP_FWU_RDP-4_Failure_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |

<a id="section-6"></a>

## 57~63행 · RDP-5 check

| 행 | 해석 |
|---:|---|
| 57 | *[주석] RDP-5 check* |
| 58 | `INST_RDP_QTY`(설정값) ≥ 5 **그리고** 룸 차압 5번 값 (`VP_FWU_RDP-5`) ≤ `RDP_FAIL_DP`(0) 이면 : |
| 59 | &emsp;→&nbsp;타이머 `RDP_5_FAIL_TIMER`(4번: 룸 차압 5번 고장 확인) 경과시간 > `RDP_FAIL_TIME_OUT`(20) 이면 : |
| 60 | &emsp;&emsp;→&nbsp;룸 차압 5번 센서 고장 알람 (`VP_FWU_RDP-5_Failure_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 61 | 58행 조건이 성립하지 않으면 : |
| 62 | &emsp;→&nbsp;타이머 `RDP_5_FAIL_TIMER`(4번: 룸 차압 5번 고장 확인)를 0초로 초기화 |
| 63 | &emsp;→&nbsp;룸 차압 5번 센서 고장 알람 (`VP_FWU_RDP-5_Failure_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |

<a id="section-7"></a>

## 65~71행 · RDP-6 check

| 행 | 해석 |
|---:|---|
| 65 | *[주석] RDP-6 check* |
| 66 | `INST_RDP_QTY`(설정값) ≥ 6 **그리고** 룸 차압 6번 값 (`VP_FWU_RDP-6`) ≤ `RDP_FAIL_DP`(0) 이면 : |
| 67 | &emsp;→&nbsp;타이머 `RDP_6_FAIL_TIMER`(5번: 룸 차압 6번 고장 확인) 경과시간 > `RDP_FAIL_TIME_OUT`(20) 이면 : |
| 68 | &emsp;&emsp;→&nbsp;룸 차압 6번 센서 고장 알람 (`VP_FWU_RDP-6_Failure_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 69 | 66행 조건이 성립하지 않으면 : |
| 70 | &emsp;→&nbsp;타이머 `RDP_6_FAIL_TIMER`(5번: 룸 차압 6번 고장 확인)를 0초로 초기화 |
| 71 | &emsp;→&nbsp;룸 차압 6번 센서 고장 알람 (`VP_FWU_RDP-6_Failure_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |

<a id="section-8"></a>

## 73~79행 · RDP-7 check

| 행 | 해석 |
|---:|---|
| 73 | *[주석] RDP-7 check* |
| 74 | `INST_RDP_QTY`(설정값) ≥ 7 **그리고** 룸 차압 7번 값 (`VP_FWU_RDP-7`) ≤ `RDP_FAIL_DP`(0) 이면 : |
| 75 | &emsp;→&nbsp;타이머 `RDP_7_FAIL_TIMER`(6번: 룸 차압 7번 고장 확인) 경과시간 > `RDP_FAIL_TIME_OUT`(20) 이면 : |
| 76 | &emsp;&emsp;→&nbsp;룸 차압 7번 센서 고장 알람 (`VP_FWU_RDP-7_Failure_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 77 | 74행 조건이 성립하지 않으면 : |
| 78 | &emsp;→&nbsp;타이머 `RDP_7_FAIL_TIMER`(6번: 룸 차압 7번 고장 확인)를 0초로 초기화 |
| 79 | &emsp;→&nbsp;룸 차압 7번 센서 고장 알람 (`VP_FWU_RDP-7_Failure_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |

<a id="section-9"></a>

## 81~87행 · RDP-8 check

| 행 | 해석 |
|---:|---|
| 81 | *[주석] RDP-8 check* |
| 82 | `INST_RDP_QTY`(설정값) ≥ 8 **그리고** 룸 차압 8번 값 (`VP_FWU_RDP-8`) ≤ `RDP_FAIL_DP`(0) 이면 : |
| 83 | &emsp;→&nbsp;타이머 `RDP_8_FAIL_TIMER`(7번: 룸 차압 8번 고장 확인) 경과시간 > `RDP_FAIL_TIME_OUT`(20) 이면 : |
| 84 | &emsp;&emsp;→&nbsp;룸 차압 8번 센서 고장 알람 (`VP_FWU_RDP-8_Failure_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 85 | 82행 조건이 성립하지 않으면 : |
| 86 | &emsp;→&nbsp;타이머 `RDP_8_FAIL_TIMER`(7번: 룸 차압 8번 고장 확인)를 0초로 초기화 |
| 87 | &emsp;→&nbsp;룸 차압 8번 센서 고장 알람 (`VP_FWU_RDP-8_Failure_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |

<a id="section-10"></a>

## 89~95행 · RDP-9 check

| 행 | 해석 |
|---:|---|
| 89 | *[주석] RDP-9 check* |
| 90 | `INST_RDP_QTY`(설정값) ≥ 9 **그리고** 룸 차압 9번 값 (`VP_FWU_RDP-9`) ≤ `RDP_FAIL_DP`(0) 이면 : |
| 91 | &emsp;→&nbsp;타이머 `RDP_9_FAIL_TIMER`(8번: 룸 차압 9번 고장 확인) 경과시간 > `RDP_FAIL_TIME_OUT`(20) 이면 : |
| 92 | &emsp;&emsp;→&nbsp;룸 차압 9번 센서 고장 알람 (`VP_FWU_RDP-9_Failure_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 93 | 90행 조건이 성립하지 않으면 : |
| 94 | &emsp;→&nbsp;타이머 `RDP_9_FAIL_TIMER`(8번: 룸 차압 9번 고장 확인)를 0초로 초기화 |
| 95 | &emsp;→&nbsp;룸 차압 9번 센서 고장 알람 (`VP_FWU_RDP-9_Failure_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |

<a id="section-11"></a>

## 97~104행 · RDP-10 check

| 행 | 해석 |
|---:|---|
| 97 | *[주석] RDP-10 check* |
| 98 | `INST_RDP_QTY`(설정값) ≥ 10 **그리고** 룸 차압 10번 값 (`VP_FWU_RDP-10`) ≤ `RDP_FAIL_DP`(0) 이면 : |
| 99 | &emsp;→&nbsp;타이머 `RDP_10_FAIL_TIMER`(9번: 룸 차압 10번 고장 확인) 경과시간 > `RDP_FAIL_TIME_OUT`(20) 이면 : |
| 100 | &emsp;&emsp;→&nbsp;룸 차압 10번 센서 고장 알람 (`VP_FWU_RDP-10_Failure_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 101 | 98행 조건이 성립하지 않으면 : |
| 102 | &emsp;→&nbsp;타이머 `RDP_10_FAIL_TIMER`(9번: 룸 차압 10번 고장 확인)를 0초로 초기화 |
| 103 | &emsp;→&nbsp;룸 차압 10번 센서 고장 알람 (`VP_FWU_RDP-10_Failure_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 104 | *[주석] LJH 2026-11-17 수정 표시. 주제 = RDP 센서 10개 고장 감시* |
