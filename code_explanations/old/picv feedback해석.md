# PICV Feedback 줄별 해석

> **대상 코드** : `fwu_v2/Logic/PICV Feedback.py`  
> **기준 커밋** : `0e0a374d983bf194220e75da79b28598673bc0fa` (`jh`)  
> **행** = 코드 줄 번호 (빈 줄은 생략)  
> **표기** : `→` 들여쓰기 단계 · *[주석]* 코드 안 주석 · **※** 읽을 때 주의할 점

밸브 4대의 수신 갱신, 개도 범위, 명령 편차 및 유량을 확인하고 결과를 모은다.

**목차**

- [1~9행 · 준비와 집계값 초기화](#section-1)
- [10~59행 · 밸브 1번 피드백 감시](#section-2)
- [60~109행 · 밸브 2번 피드백 감시](#section-3)
- [110~159행 · 밸브 3번 피드백 감시](#section-4)
- [160~209행 · 밸브 4번 피드백 감시](#section-5)
- [210~216행 · 전체 결과 기록](#section-6)

**※ 공통 표기**: 알람 1=발생, 0=해제. 조건이 거짓이라고 모든 관제점이 자동으로 0이 되지는 않는다. 해당 분기에 쓰기 명령이 없으면 이전 값이 남는다. `SECTIMER(..., 0)`은 타이머 초기화, `SECTIMER(..., 1)`은 경과시간 확인이다. 명시적 P번호가 없는 쓰기는 `WRITEPOINT` 기본 우선순위를 사용한다.

<a id="section-1"></a>

## 1~9행 · 준비와 집계값 초기화

> 이번 실행의 전체 판정값을 먼저 준비

| 행 | 해석 |
|---:|---|
| 1 | *[주석] LJH[2026.1117]밸브별 수신 유효성 및 닫힘 확인: S ----* |
| 2 | DDC 로직 엔진 객체 생성 (이후 engine.xxx로 관제점을 읽고 씀) |
| 3 | *[주석] 수신 어댑터가 실제 값과 Input OK를 기록한 뒤 Sample Seq를 갱신해야 한다.* |
| 4 | *[주석] 같은 값을 재수신해도 Seq는 갱신한다. 주소 미연결 상태에서는 Input Enable=0 유지.* |
| 5 | *[주석] 통신 10초는 기존 유량계 감시 기준의 임시값. CH3 폴링 주기에 맞춰 확인.* |
| 6 | 전체 밸브 닫힘 판정 (`b_all_closed`) = 1 (예) |
| 7 | 전체 밸브 감시 준비 판정 (`b_monitor_ready`) = 1 (예) |
| 8 | 밸브 중 하나라도 알람이 있는지 여부 (`b_any_fault`) = 0 (아니오) |
| 9 | 밸브 중 하나라도 수신 이상이 있는지 여부 (`b_any_comm_fault`) = 0 (아니오) |

<a id="section-2"></a>

## 10~59행 · 밸브 1번 피드백 감시

> 수신 갱신 → 개도 범위 → 닫힘 판정 → 동작 이상 → 개별 알람

| 행 | 해석 |
|---:|---|
| 10 | 상수: 밸브 1번 수신 갱신 확인 타이머 번호 = 0 (`PICV_1_INPUT_TIMER`) |
| 11 | 상수: 밸브 1번 명령·개도 편차 확인 타이머 번호 = 4 (`PICV_1_DEVIATION_TIMER`) |
| 12 | 현재 밸브 수신 사용 및 정상 조건 (`b_input_ok`)에 판정 결과 저장: 밸브 수신 사용 설정 (`VP_FWU_PICV_Input_Enable`) = 1 **그리고** 밸브 1번 수신 정상 표시 (`VP_FWU_PICV-1_Input_OK`) = 1, `VP_FWU_PICV_Input_Enable`는 HMI UI로 만들어서 엔지니어가 picv 연결 확인 후 write 해줘야 함, `VP_FWU_PICV-1_Input_OK`는 RS485로 개도율, 유량 정보를 정상적으로 받으면 1 써줘야 함|
| 13 | 현재 밸브 수신 사용 및 정상 조건 = 거짓이면 : |
| 14 | &emsp;→&nbsp;밸브 1번 피드백 유효 표시 (`VP_FWU_PICV-1_Feedback_Valid`)에 0 (아니오) 기록 — 기본 쓰기 우선순위 |
| 15 | &emsp;→&nbsp;밸브 1번 이전 수신 순번 (`VP_FWU_PICV-1_Sample_Prev`)(이전 순번)에 밸브 1번 현재 수신 순번 (`VP_FWU_PICV-1_Sample_Seq`)(Sequence, 현재 순번) 기록 — 기본 쓰기 우선순위 |
| 16 | &emsp;→&nbsp;밸브 1번 수신 갱신 확인 타이머(번호 0)를 0초로 초기화 |
| 17 | 13행 조건이 성립하지 않으면 : |
| 18 | &emsp;→&nbsp;밸브 1번 현재 수신 순번 (`VP_FWU_PICV-1_Sample_Seq`) ≠ 밸브 1번 이전 수신 순번 (`VP_FWU_PICV-1_Sample_Prev`)이면 : |
| 19 | &emsp;&emsp;→&nbsp;밸브 1번 이전 수신 순번 (`VP_FWU_PICV-1_Sample_Prev`)에 밸브 1번 현재 수신 순번 (`VP_FWU_PICV-1_Sample_Seq`) 기록 — 기본 쓰기 우선순위 |
| 20 | &emsp;&emsp;→&nbsp;밸브 1번 피드백 유효 표시 (`VP_FWU_PICV-1_Feedback_Valid`)에 1 (예) 기록 — 기본 쓰기 우선순위 |
| 21 | &emsp;&emsp;→&nbsp;밸브 1번 수신 갱신 확인 타이머(번호 0)를 0초로 초기화 |
| 22 | &emsp;→&nbsp;18행 조건이 성립하지 않으면 : |
| 23 | &emsp;&emsp;→&nbsp;밸브 1번 수신 갱신 확인 타이머(번호 0) 경과시간이 밸브 수신 갱신 제한시간(초) (`VP_FWU_PICV_Input_Timeout`) 초과하면 : |
| 24 | &emsp;&emsp;&emsp;→&nbsp;밸브 1번 피드백 유효 표시 (`VP_FWU_PICV-1_Feedback_Valid`)에 0 (아니오) 기록 — 기본 쓰기 우선순위 |
| 25 | 현재 밸브 피드백 유효 여부 (`b_valid`)에 판정 결과 저장: 밸브 1번 피드백 유효 표시 (`VP_FWU_PICV-1_Feedback_Valid`) = 1 |
| 26 | 현재 밸브 실제 개도(%) (`position`) = 밸브 1번 실제 개도(%) (`VP_FWU_PICV-1_Position`) |
| 27 | 실제 개도가 0% 미만 또는 100% 초과하면 : |
| 28 | &emsp;→&nbsp;현재 밸브 피드백 유효 여부 (`b_valid`) = 0 (아니오) |
| 29 | &emsp;→&nbsp;밸브 1번 피드백 유효 표시 (`VP_FWU_PICV-1_Feedback_Valid`)에 0 (아니오) 기록 — 기본 쓰기 우선순위 |
| 30 | 현재 밸브 피드백 유효 여부 = 거짓이면 : |
| 31 | &emsp;→&nbsp;전체 밸브 닫힘 판정 (`b_all_closed`) = 0 (아니오) |
| 32 | &emsp;→&nbsp;전체 밸브 감시 준비 판정 (`b_monitor_ready`) = 0 (아니오) |
| 33 | &emsp;→&nbsp;밸브 중 하나라도 수신 이상이 있는지 여부 (`b_any_comm_fault`) = 1 (예) |
| 34 | &emsp;→&nbsp;밸브 1번 수신 이상 알람 (`VP_FWU_PICV-1_Comm_Fault`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 35 | &emsp;→&nbsp;밸브 1번 개별 종합 알람 (`VP_FWU_PICV-1_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 36 | &emsp;→&nbsp;밸브 1번 명령·개도 편차 확인 타이머(번호 4)를 0초로 초기화 |
| 37 | 30행 조건이 성립하지 않으면 : |
| 38 | &emsp;→&nbsp;밸브 1번 수신 이상 알람 (`VP_FWU_PICV-1_Comm_Fault`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 39 | &emsp;→&nbsp;현재 밸브 실제 개도(%)이 5 이상이면 : |
| 40 | &emsp;&emsp;→&nbsp;전체 밸브 닫힘 판정 (`b_all_closed`) = 0 (아니오) |
| 41 | &emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 0 (아니오) |
| 42 | &emsp;→&nbsp;*[주석] 위치 제어 모드에서만 명령과 실제 개도를 비교한다.* |
| 43 | &emsp;→&nbsp;밸브 제어 모드 (`VP_FWU_PICV_Control_Mode`) = 1이면 : |
| 44 | &emsp;&emsp;→&nbsp;공통 명령과 실제 개도 차이가 30%p 이상이면 : |
| 45 | &emsp;&emsp;&emsp;→&nbsp;밸브 1번 명령·개도 편차 확인 타이머(번호 4) 경과시간이 40 초과하면 : |
| 46 | &emsp;&emsp;&emsp;&emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 1 (예) |
| 47 | &emsp;&emsp;→&nbsp;44행 조건이 성립하지 않으면 : |
| 48 | &emsp;&emsp;&emsp;→&nbsp;밸브 1번 명령·개도 편차 확인 타이머(번호 4)를 0초로 초기화 |
| 49 | &emsp;→&nbsp;43행 조건이 성립하지 않으면 : |
| 50 | &emsp;&emsp;→&nbsp;밸브 1번 명령·개도 편차 확인 타이머(번호 4)를 0초로 초기화 |
| 51 | &emsp;→&nbsp;*[주석] 유량 기준 30/10 LPM은 밸브별 설계 유량 확인 후 감시를 켤 것.* |
| 52 | &emsp;→&nbsp;밸브 유량 감시 사용 설정 (`VP_FWU_PICV_Flow_Check_Enable`) = 1이면 : |
| 53 | &emsp;&emsp;→&nbsp;냉수 공급 조건 성립 표시 (`VP_FWU_Chilled_Water_Supply_Condition`) = 1 **그리고** 현재 밸브 실제 개도(%)이 30 초과 **그리고** 밸브 1번 실제 유량 (`VP_FWU_PICV-1_Flow`)이 밸브 유량 부족 판정 설정값 (`VP_FWU_PICV_No_Flow_Set`) 미만이면 : |
| 54 | &emsp;&emsp;&emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 1 (예) |
| 55 | &emsp;&emsp;→&nbsp;현재 밸브 실제 개도(%)이 1 미만 **그리고** 밸브 1번 실제 유량 (`VP_FWU_PICV-1_Flow`)이 닫힌 밸브의 잔류 유량 판정 설정값 (`VP_FWU_PICV_Leak_Flow_Set`) 초과하면 : |
| 56 | &emsp;&emsp;&emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 1 (예) |
| 57 | &emsp;→&nbsp;밸브 1번 개별 종합 알람 (`VP_FWU_PICV-1_Alarm`)에 현재 밸브 동작 이상 판정 기록 — 기본 쓰기 우선순위 |
| 58 | 밸브 1번 개별 종합 알람 (`VP_FWU_PICV-1_Alarm`) = 1이면 : |
| 59 | &emsp;→&nbsp;밸브 중 하나라도 알람이 있는지 여부 (`b_any_fault`) = 1 (예) |

<a id="section-3"></a>

## 60~109행 · 밸브 2번 피드백 감시

> 수신 갱신 → 개도 범위 → 닫힘 판정 → 동작 이상 → 개별 알람

| 행 | 해석 |
|---:|---|
| 60 | 상수: 밸브 2번 수신 갱신 확인 타이머 번호 = 1 (`PICV_2_INPUT_TIMER`) |
| 61 | 상수: 밸브 2번 명령·개도 편차 확인 타이머 번호 = 5 (`PICV_2_DEVIATION_TIMER`) |
| 62 | 현재 밸브 수신 사용 및 정상 조건 (`b_input_ok`)에 판정 결과 저장: 밸브 수신 사용 설정 (`VP_FWU_PICV_Input_Enable`) = 1 **그리고** 밸브 2번 수신 정상 표시 (`VP_FWU_PICV-2_Input_OK`) = 1 |
| 63 | 현재 밸브 수신 사용 및 정상 조건 = 거짓이면 : |
| 64 | &emsp;→&nbsp;밸브 2번 피드백 유효 표시 (`VP_FWU_PICV-2_Feedback_Valid`)에 0 (아니오) 기록 — 기본 쓰기 우선순위 |
| 65 | &emsp;→&nbsp;밸브 2번 이전 수신 순번 (`VP_FWU_PICV-2_Sample_Prev`)에 밸브 2번 현재 수신 순번 (`VP_FWU_PICV-2_Sample_Seq`) 기록 — 기본 쓰기 우선순위 |
| 66 | &emsp;→&nbsp;밸브 2번 수신 갱신 확인 타이머(번호 1)를 0초로 초기화 |
| 67 | 63행 조건이 성립하지 않으면 : |
| 68 | &emsp;→&nbsp;밸브 2번 현재 수신 순번 (`VP_FWU_PICV-2_Sample_Seq`) ≠ 밸브 2번 이전 수신 순번 (`VP_FWU_PICV-2_Sample_Prev`)이면 : |
| 69 | &emsp;&emsp;→&nbsp;밸브 2번 이전 수신 순번 (`VP_FWU_PICV-2_Sample_Prev`)에 밸브 2번 현재 수신 순번 (`VP_FWU_PICV-2_Sample_Seq`) 기록 — 기본 쓰기 우선순위 |
| 70 | &emsp;&emsp;→&nbsp;밸브 2번 피드백 유효 표시 (`VP_FWU_PICV-2_Feedback_Valid`)에 1 (예) 기록 — 기본 쓰기 우선순위 |
| 71 | &emsp;&emsp;→&nbsp;밸브 2번 수신 갱신 확인 타이머(번호 1)를 0초로 초기화 |
| 72 | &emsp;→&nbsp;68행 조건이 성립하지 않으면 : |
| 73 | &emsp;&emsp;→&nbsp;밸브 2번 수신 갱신 확인 타이머(번호 1) 경과시간이 밸브 수신 갱신 제한시간(초) (`VP_FWU_PICV_Input_Timeout`) 초과하면 : |
| 74 | &emsp;&emsp;&emsp;→&nbsp;밸브 2번 피드백 유효 표시 (`VP_FWU_PICV-2_Feedback_Valid`)에 0 (아니오) 기록 — 기본 쓰기 우선순위 |
| 75 | 현재 밸브 피드백 유효 여부 (`b_valid`)에 판정 결과 저장: 밸브 2번 피드백 유효 표시 (`VP_FWU_PICV-2_Feedback_Valid`) = 1 |
| 76 | 현재 밸브 실제 개도(%) (`position`) = 밸브 2번 실제 개도(%) (`VP_FWU_PICV-2_Position`) |
| 77 | 실제 개도가 0% 미만 또는 100% 초과하면 : |
| 78 | &emsp;→&nbsp;현재 밸브 피드백 유효 여부 (`b_valid`) = 0 (아니오) |
| 79 | &emsp;→&nbsp;밸브 2번 피드백 유효 표시 (`VP_FWU_PICV-2_Feedback_Valid`)에 0 (아니오) 기록 — 기본 쓰기 우선순위 |
| 80 | 현재 밸브 피드백 유효 여부 = 거짓이면 : |
| 81 | &emsp;→&nbsp;전체 밸브 닫힘 판정 (`b_all_closed`) = 0 (아니오) |
| 82 | &emsp;→&nbsp;전체 밸브 감시 준비 판정 (`b_monitor_ready`) = 0 (아니오) |
| 83 | &emsp;→&nbsp;밸브 중 하나라도 수신 이상이 있는지 여부 (`b_any_comm_fault`) = 1 (예) |
| 84 | &emsp;→&nbsp;밸브 2번 수신 이상 알람 (`VP_FWU_PICV-2_Comm_Fault`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 85 | &emsp;→&nbsp;밸브 2번 개별 종합 알람 (`VP_FWU_PICV-2_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 86 | &emsp;→&nbsp;밸브 2번 명령·개도 편차 확인 타이머(번호 5)를 0초로 초기화 |
| 87 | 80행 조건이 성립하지 않으면 : |
| 88 | &emsp;→&nbsp;밸브 2번 수신 이상 알람 (`VP_FWU_PICV-2_Comm_Fault`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 89 | &emsp;→&nbsp;현재 밸브 실제 개도(%)이 5 이상이면 : |
| 90 | &emsp;&emsp;→&nbsp;전체 밸브 닫힘 판정 (`b_all_closed`) = 0 (아니오) |
| 91 | &emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 0 (아니오) |
| 92 | &emsp;→&nbsp;*[주석] 위치 제어 모드에서만 명령과 실제 개도를 비교한다.* |
| 93 | &emsp;→&nbsp;밸브 제어 모드 (`VP_FWU_PICV_Control_Mode`) = 1이면 : |
| 94 | &emsp;&emsp;→&nbsp;공통 명령과 실제 개도 차이가 30%p 이상이면 : |
| 95 | &emsp;&emsp;&emsp;→&nbsp;밸브 2번 명령·개도 편차 확인 타이머(번호 5) 경과시간이 40 초과하면 : |
| 96 | &emsp;&emsp;&emsp;&emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 1 (예) |
| 97 | &emsp;&emsp;→&nbsp;94행 조건이 성립하지 않으면 : |
| 98 | &emsp;&emsp;&emsp;→&nbsp;밸브 2번 명령·개도 편차 확인 타이머(번호 5)를 0초로 초기화 |
| 99 | &emsp;→&nbsp;93행 조건이 성립하지 않으면 : |
| 100 | &emsp;&emsp;→&nbsp;밸브 2번 명령·개도 편차 확인 타이머(번호 5)를 0초로 초기화 |
| 101 | &emsp;→&nbsp;*[주석] 유량 기준 30/10 LPM은 밸브별 설계 유량 확인 후 감시를 켤 것.* |
| 102 | &emsp;→&nbsp;밸브 유량 감시 사용 설정 (`VP_FWU_PICV_Flow_Check_Enable`) = 1이면 : |
| 103 | &emsp;&emsp;→&nbsp;냉수 공급 조건 성립 표시 (`VP_FWU_Chilled_Water_Supply_Condition`) = 1 **그리고** 현재 밸브 실제 개도(%)이 30 초과 **그리고** 밸브 2번 실제 유량 (`VP_FWU_PICV-2_Flow`)이 밸브 유량 부족 판정 설정값 (`VP_FWU_PICV_No_Flow_Set`) 미만이면 : |
| 104 | &emsp;&emsp;&emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 1 (예) |
| 105 | &emsp;&emsp;→&nbsp;현재 밸브 실제 개도(%)이 1 미만 **그리고** 밸브 2번 실제 유량 (`VP_FWU_PICV-2_Flow`)이 닫힌 밸브의 잔류 유량 판정 설정값 (`VP_FWU_PICV_Leak_Flow_Set`) 초과하면 : |
| 106 | &emsp;&emsp;&emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 1 (예) |
| 107 | &emsp;→&nbsp;밸브 2번 개별 종합 알람 (`VP_FWU_PICV-2_Alarm`)에 현재 밸브 동작 이상 판정 기록 — 기본 쓰기 우선순위 |
| 108 | 밸브 2번 개별 종합 알람 (`VP_FWU_PICV-2_Alarm`) = 1이면 : |
| 109 | &emsp;→&nbsp;밸브 중 하나라도 알람이 있는지 여부 (`b_any_fault`) = 1 (예) |

<a id="section-4"></a>

## 110~159행 · 밸브 3번 피드백 감시

> 수신 갱신 → 개도 범위 → 닫힘 판정 → 동작 이상 → 개별 알람

| 행 | 해석 |
|---:|---|
| 110 | 상수: 밸브 3번 수신 갱신 확인 타이머 번호 = 2 (`PICV_3_INPUT_TIMER`) |
| 111 | 상수: 밸브 3번 명령·개도 편차 확인 타이머 번호 = 6 (`PICV_3_DEVIATION_TIMER`) |
| 112 | 현재 밸브 수신 사용 및 정상 조건 (`b_input_ok`)에 판정 결과 저장: 밸브 수신 사용 설정 (`VP_FWU_PICV_Input_Enable`) = 1 **그리고** 밸브 3번 수신 정상 표시 (`VP_FWU_PICV-3_Input_OK`) = 1 |
| 113 | 현재 밸브 수신 사용 및 정상 조건 = 거짓이면 : |
| 114 | &emsp;→&nbsp;밸브 3번 피드백 유효 표시 (`VP_FWU_PICV-3_Feedback_Valid`)에 0 (아니오) 기록 — 기본 쓰기 우선순위 |
| 115 | &emsp;→&nbsp;밸브 3번 이전 수신 순번 (`VP_FWU_PICV-3_Sample_Prev`)에 밸브 3번 현재 수신 순번 (`VP_FWU_PICV-3_Sample_Seq`) 기록 — 기본 쓰기 우선순위 |
| 116 | &emsp;→&nbsp;밸브 3번 수신 갱신 확인 타이머(번호 2)를 0초로 초기화 |
| 117 | 113행 조건이 성립하지 않으면 : |
| 118 | &emsp;→&nbsp;밸브 3번 현재 수신 순번 (`VP_FWU_PICV-3_Sample_Seq`) ≠ 밸브 3번 이전 수신 순번 (`VP_FWU_PICV-3_Sample_Prev`)이면 : |
| 119 | &emsp;&emsp;→&nbsp;밸브 3번 이전 수신 순번 (`VP_FWU_PICV-3_Sample_Prev`)에 밸브 3번 현재 수신 순번 (`VP_FWU_PICV-3_Sample_Seq`) 기록 — 기본 쓰기 우선순위 |
| 120 | &emsp;&emsp;→&nbsp;밸브 3번 피드백 유효 표시 (`VP_FWU_PICV-3_Feedback_Valid`)에 1 (예) 기록 — 기본 쓰기 우선순위 |
| 121 | &emsp;&emsp;→&nbsp;밸브 3번 수신 갱신 확인 타이머(번호 2)를 0초로 초기화 |
| 122 | &emsp;→&nbsp;118행 조건이 성립하지 않으면 : |
| 123 | &emsp;&emsp;→&nbsp;밸브 3번 수신 갱신 확인 타이머(번호 2) 경과시간이 밸브 수신 갱신 제한시간(초) (`VP_FWU_PICV_Input_Timeout`) 초과하면 : |
| 124 | &emsp;&emsp;&emsp;→&nbsp;밸브 3번 피드백 유효 표시 (`VP_FWU_PICV-3_Feedback_Valid`)에 0 (아니오) 기록 — 기본 쓰기 우선순위 |
| 125 | 현재 밸브 피드백 유효 여부 (`b_valid`)에 판정 결과 저장: 밸브 3번 피드백 유효 표시 (`VP_FWU_PICV-3_Feedback_Valid`) = 1 |
| 126 | 현재 밸브 실제 개도(%) (`position`) = 밸브 3번 실제 개도(%) (`VP_FWU_PICV-3_Position`) |
| 127 | 실제 개도가 0% 미만 또는 100% 초과하면 : |
| 128 | &emsp;→&nbsp;현재 밸브 피드백 유효 여부 (`b_valid`) = 0 (아니오) |
| 129 | &emsp;→&nbsp;밸브 3번 피드백 유효 표시 (`VP_FWU_PICV-3_Feedback_Valid`)에 0 (아니오) 기록 — 기본 쓰기 우선순위 |
| 130 | 현재 밸브 피드백 유효 여부 = 거짓이면 : |
| 131 | &emsp;→&nbsp;전체 밸브 닫힘 판정 (`b_all_closed`) = 0 (아니오) |
| 132 | &emsp;→&nbsp;전체 밸브 감시 준비 판정 (`b_monitor_ready`) = 0 (아니오) |
| 133 | &emsp;→&nbsp;밸브 중 하나라도 수신 이상이 있는지 여부 (`b_any_comm_fault`) = 1 (예) |
| 134 | &emsp;→&nbsp;밸브 3번 수신 이상 알람 (`VP_FWU_PICV-3_Comm_Fault`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 135 | &emsp;→&nbsp;밸브 3번 개별 종합 알람 (`VP_FWU_PICV-3_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 136 | &emsp;→&nbsp;밸브 3번 명령·개도 편차 확인 타이머(번호 6)를 0초로 초기화 |
| 137 | 130행 조건이 성립하지 않으면 : |
| 138 | &emsp;→&nbsp;밸브 3번 수신 이상 알람 (`VP_FWU_PICV-3_Comm_Fault`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 139 | &emsp;→&nbsp;현재 밸브 실제 개도(%)이 5 이상이면 : |
| 140 | &emsp;&emsp;→&nbsp;전체 밸브 닫힘 판정 (`b_all_closed`) = 0 (아니오) |
| 141 | &emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 0 (아니오) |
| 142 | &emsp;→&nbsp;*[주석] 위치 제어 모드에서만 명령과 실제 개도를 비교한다.* |
| 143 | &emsp;→&nbsp;밸브 제어 모드 (`VP_FWU_PICV_Control_Mode`) = 1이면 : |
| 144 | &emsp;&emsp;→&nbsp;공통 명령과 실제 개도 차이가 30%p 이상이면 : |
| 145 | &emsp;&emsp;&emsp;→&nbsp;밸브 3번 명령·개도 편차 확인 타이머(번호 6) 경과시간이 40 초과하면 : |
| 146 | &emsp;&emsp;&emsp;&emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 1 (예) |
| 147 | &emsp;&emsp;→&nbsp;144행 조건이 성립하지 않으면 : |
| 148 | &emsp;&emsp;&emsp;→&nbsp;밸브 3번 명령·개도 편차 확인 타이머(번호 6)를 0초로 초기화 |
| 149 | &emsp;→&nbsp;143행 조건이 성립하지 않으면 : |
| 150 | &emsp;&emsp;→&nbsp;밸브 3번 명령·개도 편차 확인 타이머(번호 6)를 0초로 초기화 |
| 151 | &emsp;→&nbsp;*[주석] 유량 기준 30/10 LPM은 밸브별 설계 유량 확인 후 감시를 켤 것.* |
| 152 | &emsp;→&nbsp;밸브 유량 감시 사용 설정 (`VP_FWU_PICV_Flow_Check_Enable`) = 1이면 : |
| 153 | &emsp;&emsp;→&nbsp;냉수 공급 조건 성립 표시 (`VP_FWU_Chilled_Water_Supply_Condition`) = 1 **그리고** 현재 밸브 실제 개도(%)이 30 초과 **그리고** 밸브 3번 실제 유량 (`VP_FWU_PICV-3_Flow`)이 밸브 유량 부족 판정 설정값 (`VP_FWU_PICV_No_Flow_Set`) 미만이면 : |
| 154 | &emsp;&emsp;&emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 1 (예) |
| 155 | &emsp;&emsp;→&nbsp;현재 밸브 실제 개도(%)이 1 미만 **그리고** 밸브 3번 실제 유량 (`VP_FWU_PICV-3_Flow`)이 닫힌 밸브의 잔류 유량 판정 설정값 (`VP_FWU_PICV_Leak_Flow_Set`) 초과하면 : |
| 156 | &emsp;&emsp;&emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 1 (예) |
| 157 | &emsp;→&nbsp;밸브 3번 개별 종합 알람 (`VP_FWU_PICV-3_Alarm`)에 현재 밸브 동작 이상 판정 기록 — 기본 쓰기 우선순위 |
| 158 | 밸브 3번 개별 종합 알람 (`VP_FWU_PICV-3_Alarm`) = 1이면 : |
| 159 | &emsp;→&nbsp;밸브 중 하나라도 알람이 있는지 여부 (`b_any_fault`) = 1 (예) |

<a id="section-5"></a>

## 160~209행 · 밸브 4번 피드백 감시

> 수신 갱신 → 개도 범위 → 닫힘 판정 → 동작 이상 → 개별 알람

| 행 | 해석 |
|---:|---|
| 160 | 상수: 밸브 4번 수신 갱신 확인 타이머 번호 = 3 (`PICV_4_INPUT_TIMER`) |
| 161 | 상수: 밸브 4번 명령·개도 편차 확인 타이머 번호 = 7 (`PICV_4_DEVIATION_TIMER`) |
| 162 | 현재 밸브 수신 사용 및 정상 조건 (`b_input_ok`)에 판정 결과 저장: 밸브 수신 사용 설정 (`VP_FWU_PICV_Input_Enable`) = 1 **그리고** 밸브 4번 수신 정상 표시 (`VP_FWU_PICV-4_Input_OK`) = 1 |
| 163 | 현재 밸브 수신 사용 및 정상 조건 = 거짓이면 : |
| 164 | &emsp;→&nbsp;밸브 4번 피드백 유효 표시 (`VP_FWU_PICV-4_Feedback_Valid`)에 0 (아니오) 기록 — 기본 쓰기 우선순위 |
| 165 | &emsp;→&nbsp;밸브 4번 이전 수신 순번 (`VP_FWU_PICV-4_Sample_Prev`)에 밸브 4번 현재 수신 순번 (`VP_FWU_PICV-4_Sample_Seq`) 기록 — 기본 쓰기 우선순위 |
| 166 | &emsp;→&nbsp;밸브 4번 수신 갱신 확인 타이머(번호 3)를 0초로 초기화 |
| 167 | 163행 조건이 성립하지 않으면 : |
| 168 | &emsp;→&nbsp;밸브 4번 현재 수신 순번 (`VP_FWU_PICV-4_Sample_Seq`) ≠ 밸브 4번 이전 수신 순번 (`VP_FWU_PICV-4_Sample_Prev`)이면 : |
| 169 | &emsp;&emsp;→&nbsp;밸브 4번 이전 수신 순번 (`VP_FWU_PICV-4_Sample_Prev`)에 밸브 4번 현재 수신 순번 (`VP_FWU_PICV-4_Sample_Seq`) 기록 — 기본 쓰기 우선순위 |
| 170 | &emsp;&emsp;→&nbsp;밸브 4번 피드백 유효 표시 (`VP_FWU_PICV-4_Feedback_Valid`)에 1 (예) 기록 — 기본 쓰기 우선순위 |
| 171 | &emsp;&emsp;→&nbsp;밸브 4번 수신 갱신 확인 타이머(번호 3)를 0초로 초기화 |
| 172 | &emsp;→&nbsp;168행 조건이 성립하지 않으면 : |
| 173 | &emsp;&emsp;→&nbsp;밸브 4번 수신 갱신 확인 타이머(번호 3) 경과시간이 밸브 수신 갱신 제한시간(초) (`VP_FWU_PICV_Input_Timeout`) 초과하면 : |
| 174 | &emsp;&emsp;&emsp;→&nbsp;밸브 4번 피드백 유효 표시 (`VP_FWU_PICV-4_Feedback_Valid`)에 0 (아니오) 기록 — 기본 쓰기 우선순위 |
| 175 | 현재 밸브 피드백 유효 여부 (`b_valid`)에 판정 결과 저장: 밸브 4번 피드백 유효 표시 (`VP_FWU_PICV-4_Feedback_Valid`) = 1 |
| 176 | 현재 밸브 실제 개도(%) (`position`) = 밸브 4번 실제 개도(%) (`VP_FWU_PICV-4_Position`) |
| 177 | 실제 개도가 0% 미만 또는 100% 초과하면 : |
| 178 | &emsp;→&nbsp;현재 밸브 피드백 유효 여부 (`b_valid`) = 0 (아니오) |
| 179 | &emsp;→&nbsp;밸브 4번 피드백 유효 표시 (`VP_FWU_PICV-4_Feedback_Valid`)에 0 (아니오) 기록 — 기본 쓰기 우선순위 |
| 180 | 현재 밸브 피드백 유효 여부 = 거짓이면 : |
| 181 | &emsp;→&nbsp;전체 밸브 닫힘 판정 (`b_all_closed`) = 0 (아니오) |
| 182 | &emsp;→&nbsp;전체 밸브 감시 준비 판정 (`b_monitor_ready`) = 0 (아니오) |
| 183 | &emsp;→&nbsp;밸브 중 하나라도 수신 이상이 있는지 여부 (`b_any_comm_fault`) = 1 (예) |
| 184 | &emsp;→&nbsp;밸브 4번 수신 이상 알람 (`VP_FWU_PICV-4_Comm_Fault`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 185 | &emsp;→&nbsp;밸브 4번 개별 종합 알람 (`VP_FWU_PICV-4_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 186 | &emsp;→&nbsp;밸브 4번 명령·개도 편차 확인 타이머(번호 7)를 0초로 초기화 |
| 187 | 180행 조건이 성립하지 않으면 : |
| 188 | &emsp;→&nbsp;밸브 4번 수신 이상 알람 (`VP_FWU_PICV-4_Comm_Fault`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 189 | &emsp;→&nbsp;현재 밸브 실제 개도(%)이 5 이상이면 : |
| 190 | &emsp;&emsp;→&nbsp;전체 밸브 닫힘 판정 (`b_all_closed`) = 0 (아니오) |
| 191 | &emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 0 (아니오) |
| 192 | &emsp;→&nbsp;*[주석] 위치 제어 모드에서만 명령과 실제 개도를 비교한다.* |
| 193 | &emsp;→&nbsp;밸브 제어 모드 (`VP_FWU_PICV_Control_Mode`) = 1이면 : |
| 194 | &emsp;&emsp;→&nbsp;공통 명령과 실제 개도 차이가 30%p 이상이면 : |
| 195 | &emsp;&emsp;&emsp;→&nbsp;밸브 4번 명령·개도 편차 확인 타이머(번호 7) 경과시간이 40 초과하면 : |
| 196 | &emsp;&emsp;&emsp;&emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 1 (예) |
| 197 | &emsp;&emsp;→&nbsp;194행 조건이 성립하지 않으면 : |
| 198 | &emsp;&emsp;&emsp;→&nbsp;밸브 4번 명령·개도 편차 확인 타이머(번호 7)를 0초로 초기화 |
| 199 | &emsp;→&nbsp;193행 조건이 성립하지 않으면 : |
| 200 | &emsp;&emsp;→&nbsp;밸브 4번 명령·개도 편차 확인 타이머(번호 7)를 0초로 초기화 |
| 201 | &emsp;→&nbsp;*[주석] 유량 기준 30/10 LPM은 밸브별 설계 유량 확인 후 감시를 켤 것.* |
| 202 | &emsp;→&nbsp;밸브 유량 감시 사용 설정 (`VP_FWU_PICV_Flow_Check_Enable`) = 1이면 : |
| 203 | &emsp;&emsp;→&nbsp;냉수 공급 조건 성립 표시 (`VP_FWU_Chilled_Water_Supply_Condition`) = 1 **그리고** 현재 밸브 실제 개도(%)이 30 초과 **그리고** 밸브 4번 실제 유량 (`VP_FWU_PICV-4_Flow`)이 밸브 유량 부족 판정 설정값 (`VP_FWU_PICV_No_Flow_Set`) 미만이면 : |
| 204 | &emsp;&emsp;&emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 1 (예) |
| 205 | &emsp;&emsp;→&nbsp;현재 밸브 실제 개도(%)이 1 미만 **그리고** 밸브 4번 실제 유량 (`VP_FWU_PICV-4_Flow`)이 닫힌 밸브의 잔류 유량 판정 설정값 (`VP_FWU_PICV_Leak_Flow_Set`) 초과하면 : |
| 206 | &emsp;&emsp;&emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 1 (예) |
| 207 | &emsp;→&nbsp;밸브 4번 개별 종합 알람 (`VP_FWU_PICV-4_Alarm`)에 현재 밸브 동작 이상 판정 기록 — 기본 쓰기 우선순위 |
| 208 | 밸브 4번 개별 종합 알람 (`VP_FWU_PICV-4_Alarm`) = 1이면 : |
| 209 | &emsp;→&nbsp;밸브 중 하나라도 알람이 있는지 여부 (`b_any_fault`) = 1 (예) |

<a id="section-6"></a>

## 210~216행 · 전체 결과 기록

> 4대의 판정 결과를 공통 관제점에 기록

| 행 | 해석 |
|---:|---|
| 210 | 밸브 제어 모드 (`VP_FWU_PICV_Control_Mode`) = 0 **또는** 밸브 유량 감시 사용 설정 (`VP_FWU_PICV_Flow_Check_Enable`) ≠ 1이면 : |
| 211 | &emsp;→&nbsp;전체 밸브 감시 준비 판정 (`b_monitor_ready`) = 0 (아니오) |
| 212 | 밸브 4대 모두 닫힘 표시 (`VP_FWU_PICV_All_Closed`)에 전체 밸브 닫힘 판정 기록 — 기본 쓰기 우선순위 |
| 213 | 밸브 감시 준비 표시 (`VP_FWU_PICV_Monitor_Ready`)에 전체 밸브 감시 준비 판정 기록 — 기본 쓰기 우선순위 |
| 214 | 밸브 종합 알람 (`VP_FWU_PICV_Alarm`)에 밸브 중 하나라도 알람이 있는지 여부 기록 — 기본 쓰기 우선순위 |
| 215 | 밸브 수신 종합 이상 알람 (`VP_FWU_Flow_Comm_Fault`)에 밸브 중 하나라도 수신 이상이 있는지 여부 기록 — 기본 쓰기 우선순위 |
| 216 | *[주석] LJH[2026.1117]밸브별 수신 유효성 및 닫힘 확인: E ----* |

## 읽을 때 짚어둘 점

- **※** 이 코드는 RS485 통신을 직접 수행하지 않는다. 수신 어댑터가 값·Input_OK·Sample_Seq를 기록해 줘야 한다. 같은 측정값을 다시 받아도 순번은 바뀌어야 갱신으로 인정한다.
- **※** 개도는 0~100%를 포함한 범위를 유효하게 본다. 수신 이상뿐 아니라 개도 범위 오류도 Comm_Fault로 표시하므로 원인을 단선으로 단정할 수 없다.
- **※** 위치 모드(1)에서는 명령과 실제 개도의 차이가 30%p 이상인 상태가 40초 초과 지속되면 이상이다. 유량 제어에서는 같은 비교를 하지 않는다.
- **※** All_Closed=1은 네 밸브의 피드백이 모두 유효하고 개도가 각각 5% 미만이라는 뜻이다. 실제 유량 0을 확인했다는 뜻은 아니다.
- **※** Monitor_Ready는 감시를 위한 조건 표시다. 개별 밸브 동작 알람이 없다는 보증은 아니다. 유량 감시 조건에는 별도 지연 타이머가 없다.
