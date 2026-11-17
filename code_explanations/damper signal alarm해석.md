# Damper Signal Alarm 줄별 해석

> **대상 코드** : `fwu_v2/Logic/Damper Signal Alarm.py`  
> **기준 커밋** : `0e0a374d983bf194220e75da79b28598673bc0fa` (`jh`)  
> **행** = 코드 줄 번호 (빈 줄은 생략)  
> **표기** : `→` 들여쓰기 단계 · *[주석]* 코드 안 주석 · **※** 읽을 때 주의할 점

댐퍼별 열림·닫힘 접점이 둘 다 0이거나 둘 다 1인 상태를 감시한다.

**목차**

- [1~1행 · 로직 엔진](#section-1)
- [3~16행 · 댐퍼 1번 접점 감시](#section-2)
- [17~30행 · 댐퍼 2번 접점 감시](#section-3)
- [31~44행 · 댐퍼 3번 접점 감시](#section-4)
- [45~59행 · 댐퍼 4번 접점 감시](#section-5)

**※ 공통 표기**: 알람 1=발생, 0=해제. 조건이 거짓이라고 모든 관제점이 자동으로 0이 되지는 않는다. 해당 분기에 쓰기 명령이 없으면 이전 값이 남는다. `SECTIMER(..., 0)`은 타이머 초기화, `SECTIMER(..., 1)`은 경과시간 확인이다. 명시적 P번호가 없는 쓰기는 `WRITEPOINT` 기본 우선순위를 사용한다.

<a id="section-1"></a>

## 1~1행 · 로직 엔진

> 4개 댐퍼를 각각 확인

| 행 | 해석 |
|---:|---|
| 1 | DDC 로직 엔진 객체 생성 (이후 engine.xxx로 관제점을 읽고 씀) |

<a id="section-2"></a>

## 3~16행 · 댐퍼 1번 접점 감시

> 0·0은 위치 미확인, 1·1은 접점 모순

| 행 | 해석 |
|---:|---|
| 3 | 상수: 댐퍼 1번 위치 미확인 확인 타이머 번호 = 0 (`SAD_1_UNKNOWN_TIMER`) |
| 4 | 팬 운전 상태 (`VP_FWU_SF_Status`) = 1 **그리고** 댐퍼 4대 공통 명령(1=열기, 0=닫기) (`FWU_SAD-1_4_COMMAND`) = 1 **그리고** 댐퍼 1번 열림 접점 (`FWU_SAD-1_OPEN_STATUS`) = 0 **그리고** 댐퍼 1번 닫힘 접점 (`FWU_SAD-1_CLOSE_STATUS`) = 0이면 : |
| 5 | &emsp;→&nbsp;댐퍼 1번 위치 미확인 확인 타이머(번호 0) 경과시간이 댐퍼 위치 미확인 확인시간(초) (`VP_FWU_SAD_Unknown_Delay`) 초과하면 : |
| 6 | &emsp;&emsp;→&nbsp;댐퍼 1번 위치 미확인 알람 (`VP_FWU_SAD-1_Position_Unknown_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 7 | 4행 조건이 성립하지 않으면 : |
| 8 | &emsp;→&nbsp;댐퍼 1번 위치 미확인 확인 타이머(번호 0)를 0초로 초기화 |
| 9 | &emsp;→&nbsp;댐퍼 1번 위치 미확인 알람 (`VP_FWU_SAD-1_Position_Unknown_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 10 | 상수: 댐퍼 1번 접점 모순 확인 타이머 번호 = 4 (`SAD_1_CONFLICT_TIMER`) |
| 11 | 댐퍼 1번 열림 접점 (`FWU_SAD-1_OPEN_STATUS`) = 1 **그리고** 댐퍼 1번 닫힘 접점 (`FWU_SAD-1_CLOSE_STATUS`) = 1이면 : |
| 12 | &emsp;→&nbsp;댐퍼 1번 접점 모순 확인 타이머(번호 4) 경과시간이 댐퍼 접점 모순 확인시간(초) (`VP_FWU_SAD_Conflict_Delay`) 초과하면 : |
| 13 | &emsp;&emsp;→&nbsp;댐퍼 1번 접점 모순 알람 (`VP_FWU_SAD-1_Signal_Conflict_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 14 | 11행 조건이 성립하지 않으면 : |
| 15 | &emsp;→&nbsp;댐퍼 1번 접점 모순 확인 타이머(번호 4)를 0초로 초기화 |
| 16 | &emsp;→&nbsp;댐퍼 1번 접점 모순 알람 (`VP_FWU_SAD-1_Signal_Conflict_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |

<a id="section-3"></a>

## 17~30행 · 댐퍼 2번 접점 감시

> 0·0은 위치 미확인, 1·1은 접점 모순

| 행 | 해석 |
|---:|---|
| 17 | 상수: 댐퍼 2번 위치 미확인 확인 타이머 번호 = 1 (`SAD_2_UNKNOWN_TIMER`) |
| 18 | 팬 운전 상태 (`VP_FWU_SF_Status`) = 1 **그리고** 댐퍼 4대 공통 명령(1=열기, 0=닫기) (`FWU_SAD-1_4_COMMAND`) = 1 **그리고** 댐퍼 2번 열림 접점 (`FWU_SAD-2_OPEN_STATUS`) = 0 **그리고** 댐퍼 2번 닫힘 접점 (`FWU_SAD-2_CLOSE_STATUS`) = 0이면 : |
| 19 | &emsp;→&nbsp;댐퍼 2번 위치 미확인 확인 타이머(번호 1) 경과시간이 댐퍼 위치 미확인 확인시간(초) (`VP_FWU_SAD_Unknown_Delay`) 초과하면 : |
| 20 | &emsp;&emsp;→&nbsp;댐퍼 2번 위치 미확인 알람 (`VP_FWU_SAD-2_Position_Unknown_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 21 | 18행 조건이 성립하지 않으면 : |
| 22 | &emsp;→&nbsp;댐퍼 2번 위치 미확인 확인 타이머(번호 1)를 0초로 초기화 |
| 23 | &emsp;→&nbsp;댐퍼 2번 위치 미확인 알람 (`VP_FWU_SAD-2_Position_Unknown_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 24 | 상수: 댐퍼 2번 접점 모순 확인 타이머 번호 = 5 (`SAD_2_CONFLICT_TIMER`) |
| 25 | 댐퍼 2번 열림 접점 (`FWU_SAD-2_OPEN_STATUS`) = 1 **그리고** 댐퍼 2번 닫힘 접점 (`FWU_SAD-2_CLOSE_STATUS`) = 1이면 : |
| 26 | &emsp;→&nbsp;댐퍼 2번 접점 모순 확인 타이머(번호 5) 경과시간이 댐퍼 접점 모순 확인시간(초) (`VP_FWU_SAD_Conflict_Delay`) 초과하면 : |
| 27 | &emsp;&emsp;→&nbsp;댐퍼 2번 접점 모순 알람 (`VP_FWU_SAD-2_Signal_Conflict_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 28 | 25행 조건이 성립하지 않으면 : |
| 29 | &emsp;→&nbsp;댐퍼 2번 접점 모순 확인 타이머(번호 5)를 0초로 초기화 |
| 30 | &emsp;→&nbsp;댐퍼 2번 접점 모순 알람 (`VP_FWU_SAD-2_Signal_Conflict_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |

<a id="section-4"></a>

## 31~44행 · 댐퍼 3번 접점 감시

> 0·0은 위치 미확인, 1·1은 접점 모순

| 행 | 해석 |
|---:|---|
| 31 | 상수: 댐퍼 3번 위치 미확인 확인 타이머 번호 = 2 (`SAD_3_UNKNOWN_TIMER`) |
| 32 | 팬 운전 상태 (`VP_FWU_SF_Status`) = 1 **그리고** 댐퍼 4대 공통 명령(1=열기, 0=닫기) (`FWU_SAD-1_4_COMMAND`) = 1 **그리고** 댐퍼 3번 열림 접점 (`FWU_SAD-3_OPEN_STATUS`) = 0 **그리고** 댐퍼 3번 닫힘 접점 (`FWU_SAD-3_CLOSE_STATUS`) = 0이면 : |
| 33 | &emsp;→&nbsp;댐퍼 3번 위치 미확인 확인 타이머(번호 2) 경과시간이 댐퍼 위치 미확인 확인시간(초) (`VP_FWU_SAD_Unknown_Delay`) 초과하면 : |
| 34 | &emsp;&emsp;→&nbsp;댐퍼 3번 위치 미확인 알람 (`VP_FWU_SAD-3_Position_Unknown_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 35 | 32행 조건이 성립하지 않으면 : |
| 36 | &emsp;→&nbsp;댐퍼 3번 위치 미확인 확인 타이머(번호 2)를 0초로 초기화 |
| 37 | &emsp;→&nbsp;댐퍼 3번 위치 미확인 알람 (`VP_FWU_SAD-3_Position_Unknown_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 38 | 상수: 댐퍼 3번 접점 모순 확인 타이머 번호 = 6 (`SAD_3_CONFLICT_TIMER`) |
| 39 | 댐퍼 3번 열림 접점 (`FWU_SAD-3_OPEN_STATUS`) = 1 **그리고** 댐퍼 3번 닫힘 접점 (`FWU_SAD-3_CLOSE_STATUS`) = 1이면 : |
| 40 | &emsp;→&nbsp;댐퍼 3번 접점 모순 확인 타이머(번호 6) 경과시간이 댐퍼 접점 모순 확인시간(초) (`VP_FWU_SAD_Conflict_Delay`) 초과하면 : |
| 41 | &emsp;&emsp;→&nbsp;댐퍼 3번 접점 모순 알람 (`VP_FWU_SAD-3_Signal_Conflict_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 42 | 39행 조건이 성립하지 않으면 : |
| 43 | &emsp;→&nbsp;댐퍼 3번 접점 모순 확인 타이머(번호 6)를 0초로 초기화 |
| 44 | &emsp;→&nbsp;댐퍼 3번 접점 모순 알람 (`VP_FWU_SAD-3_Signal_Conflict_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |

<a id="section-5"></a>

## 45~59행 · 댐퍼 4번 접점 감시

> 0·0은 위치 미확인, 1·1은 접점 모순

| 행 | 해석 |
|---:|---|
| 45 | 상수: 댐퍼 4번 위치 미확인 확인 타이머 번호 = 3 (`SAD_4_UNKNOWN_TIMER`) |
| 46 | 팬 운전 상태 (`VP_FWU_SF_Status`) = 1 **그리고** 댐퍼 4대 공통 명령(1=열기, 0=닫기) (`FWU_SAD-1_4_COMMAND`) = 1 **그리고** 댐퍼 4번 열림 접점 (`FWU_SAD-4_OPEN_STATUS`) = 0 **그리고** 댐퍼 4번 닫힘 접점 (`FWU_SAD-4_CLOSE_STATUS`) = 0이면 : |
| 47 | &emsp;→&nbsp;댐퍼 4번 위치 미확인 확인 타이머(번호 3) 경과시간이 댐퍼 위치 미확인 확인시간(초) (`VP_FWU_SAD_Unknown_Delay`) 초과하면 : |
| 48 | &emsp;&emsp;→&nbsp;댐퍼 4번 위치 미확인 알람 (`VP_FWU_SAD-4_Position_Unknown_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 49 | 46행 조건이 성립하지 않으면 : |
| 50 | &emsp;→&nbsp;댐퍼 4번 위치 미확인 확인 타이머(번호 3)를 0초로 초기화 |
| 51 | &emsp;→&nbsp;댐퍼 4번 위치 미확인 알람 (`VP_FWU_SAD-4_Position_Unknown_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 52 | 상수: 댐퍼 4번 접점 모순 확인 타이머 번호 = 7 (`SAD_4_CONFLICT_TIMER`) |
| 53 | 댐퍼 4번 열림 접점 (`FWU_SAD-4_OPEN_STATUS`) = 1 **그리고** 댐퍼 4번 닫힘 접점 (`FWU_SAD-4_CLOSE_STATUS`) = 1이면 : |
| 54 | &emsp;→&nbsp;댐퍼 4번 접점 모순 확인 타이머(번호 7) 경과시간이 댐퍼 접점 모순 확인시간(초) (`VP_FWU_SAD_Conflict_Delay`) 초과하면 : |
| 55 | &emsp;&emsp;→&nbsp;댐퍼 4번 접점 모순 알람 (`VP_FWU_SAD-4_Signal_Conflict_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 56 | 53행 조건이 성립하지 않으면 : |
| 57 | &emsp;→&nbsp;댐퍼 4번 접점 모순 확인 타이머(번호 7)를 0초로 초기화 |
| 58 | &emsp;→&nbsp;댐퍼 4번 접점 모순 알람 (`VP_FWU_SAD-4_Signal_Conflict_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 59 | *[주석] LJH[2026.1117]댐퍼 위치 미확인 및 접점 모순 감시* |

## 읽을 때 짚어둘 점

- **※** 0·0 감시는 팬 운전 중이고 댐퍼 열기 명령이 있을 때만 적용한다. 모든 0·0 상태를 곧바로 고장으로 보지는 않는다.
- **※** 1·1 감시는 팬 상태와 무관하게 수행한다. 실제 댐퍼가 동시에 열리고 닫혔다는 뜻이 아니라 두 끝단 신호가 모순된다는 뜻이다.
- **※** 여기서는 알람만 쓴다. 이 추가 알람들은 현재 Failover의 세 가지 원인에 포함되지 않는다.
