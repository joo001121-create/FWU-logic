# PICV Feedback.py 해석

> 대상: 이 압축에 포함된 LDPL 재검토 수정 코드. 이전 Input_OK·Sample_Seq 설명을 대체한다. 행 번호는 `Logic/PICV Feedback.py` 기준이다.

이 블록은 DDC가 읽어 둔 네 밸브의 개도·유량·온도와 통신점 알람을 확인한다. 별도 수신 프로그램을 만들지 않는다. 밸브에 명령을 내리는 코드는 PICV Control에 그대로 있다.

## 1~8행 · 시작 및 전체 판정 초기화

| 행 | 해석 |
|---:|---|
| 1 | *[주석] LJH[2026.1117]밸브별 수신 유효성 및 닫힘 확인: S ----* |
| 2 | DDC 로직 엔진 객체 생성 (이후 engine.xxx로 관제점을 읽고 씀) |
| 3 | *[주석] CH3에 FWU_PICV-1~4의 Position, Flow, Temperature 통신점을 등록한 뒤 Input_Enable=1로 설정* |
| 4 | *[주석] 개도는 %, 유량은 L/min, 온도는 냉수 출구 온도(℃)로 환산* |
| 5 | 전체 밸브 닫힘 판정 (`b_all_closed`) = 1 (예) |
| 6 | 전체 밸브 감시 준비 판정 (`b_monitor_ready`) = 1 (예) |
| 7 | 밸브 중 하나라도 알람이 있는지 여부 (`b_any_fault`) = 0 (아니오) |
| 8 | 밸브 중 하나라도 수신 이상이 있는지 여부 (`b_any_comm_fault`) = 0 (아니오) |

## 9~50행 · 밸브 1번 입력·닫힘·동작 감시

| 행 | 해석 |
|---:|---|
| 9 | 상수: 밸브 1번 명령·개도 편차 확인 타이머 번호 = 4 (`PICV_1_DEVIATION_TIMER`) |
| 10 | 현재 밸브 피드백을 우선 유효하지 않은 상태(0)로 둔다. |
| 11 | PICV 입력 사용 설정 (`VP_FWU_PICV_Input_Enable`)이 1이면 : |
| 12 | &emsp;→&nbsp;밸브 1번 실제 통신점의 개도·유량·온도 알람 값이 **모두 0**이면 : |
| 13 | &emsp;&emsp;→&nbsp;실제 통신점 `FWU_PICV-1.Position`에서 실제 개도(%)를 읽어 기존 표시용 관제점 `VP_FWU_PICV-1_Position`에 기록한다. |
| 14 | &emsp;&emsp;→&nbsp;실제 통신점 `FWU_PICV-1.Flow`에서 실제 유량(L/min)를 읽어 기존 표시용 관제점 `VP_FWU_PICV-1_Flow`에 기록한다. |
| 15 | &emsp;&emsp;→&nbsp;실제 통신점 `FWU_PICV-1.Temperature`에서 냉수 출구 온도(℃)를 읽어 기존 표시용 관제점 `VP_FWU_PICV-1_Temperature`에 기록한다. |
| 16 | &emsp;&emsp;→&nbsp;현재 밸브 피드백을 사용할 수 있는 상태(1)로 둔다. |
| 17 | 현재 밸브 실제 개도(%) (`position`) = 밸브 1번 실제 개도(%) (`VP_FWU_PICV-1_Position`) |
| 18 | 실제 개도가 0% 미만 또는 100% 초과하면 : |
| 19 | &emsp;→&nbsp;현재 밸브 피드백 유효 여부 (`b_valid`) = 0 (아니오) |
| 20 | 관제점 `VP_FWU_PICV-1_Feedback_Valid`에 현재 밸브 입력을 사용할 수 있는지(1/0) 기록한다. |
| 21 | 현재 밸브 피드백 유효 여부 = 거짓이면 : |
| 22 | &emsp;→&nbsp;전체 밸브 닫힘 판정 (`b_all_closed`) = 0 (아니오) |
| 23 | &emsp;→&nbsp;전체 밸브 감시 준비 판정 (`b_monitor_ready`) = 0 (아니오) |
| 24 | &emsp;→&nbsp;밸브 중 하나라도 수신 이상이 있는지 여부 (`b_any_comm_fault`) = 1 (예) |
| 25 | &emsp;→&nbsp;밸브 1번 수신 이상 알람 (`VP_FWU_PICV-1_Comm_Fault`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 26 | &emsp;→&nbsp;밸브 1번 개별 종합 알람 (`VP_FWU_PICV-1_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 27 | &emsp;→&nbsp;밸브 1번 명령·개도 편차 확인 타이머(번호 4)를 0초로 초기화 |
| 28 | 21행 조건이 성립하지 않으면 : |
| 29 | &emsp;→&nbsp;밸브 1번 수신 이상 알람 (`VP_FWU_PICV-1_Comm_Fault`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 30 | &emsp;→&nbsp;현재 밸브 실제 개도(%)이 5 이상이면 : |
| 31 | &emsp;&emsp;→&nbsp;전체 밸브 닫힘 판정 (`b_all_closed`) = 0 (아니오) |
| 32 | &emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 0 (아니오) |
| 33 | &emsp;→&nbsp;*[주석] 위치 제어 모드에서만 명령과 실제 개도를 비교한다.* |
| 34 | &emsp;→&nbsp;밸브 제어 모드 (`VP_FWU_PICV_Control_Mode`) = 1이면 : |
| 35 | &emsp;&emsp;→&nbsp;공통 명령과 실제 개도 차이가 30%p 이상이면 : |
| 36 | &emsp;&emsp;&emsp;→&nbsp;밸브 1번 명령·개도 편차 확인 타이머(번호 4) 경과시간이 40 초과하면 : |
| 37 | &emsp;&emsp;&emsp;&emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 1 (예) |
| 38 | &emsp;&emsp;→&nbsp;35행 조건이 성립하지 않으면 : |
| 39 | &emsp;&emsp;&emsp;→&nbsp;밸브 1번 명령·개도 편차 확인 타이머(번호 4)를 0초로 초기화 |
| 40 | &emsp;→&nbsp;34행 조건이 성립하지 않으면 : |
| 41 | &emsp;&emsp;→&nbsp;밸브 1번 명령·개도 편차 확인 타이머(번호 4)를 0초로 초기화 |
| 42 | &emsp;→&nbsp;*[주석] 유량 기준 30/10 LPM은 밸브별 설계 유량 확인 후 감시를 켤 것.* |
| 43 | &emsp;→&nbsp;밸브 유량 감시 사용 설정 (`VP_FWU_PICV_Flow_Check_Enable`) = 1이면 : |
| 44 | &emsp;&emsp;→&nbsp;냉수 공급 조건 성립 표시 (`VP_FWU_Chilled_Water_Supply_Condition`) = 1 **그리고** 현재 밸브 실제 개도(%)이 30 초과 **그리고** 밸브 1번 실제 유량 (`VP_FWU_PICV-1_Flow`)이 밸브 유량 부족 판정 설정값 (`VP_FWU_PICV_No_Flow_Set`) 미만이면 : |
| 45 | &emsp;&emsp;&emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 1 (예) |
| 46 | &emsp;&emsp;→&nbsp;현재 밸브 실제 개도(%)이 1 미만 **그리고** 밸브 1번 실제 유량 (`VP_FWU_PICV-1_Flow`)이 닫힌 밸브의 잔류 유량 판정 설정값 (`VP_FWU_PICV_Leak_Flow_Set`) 초과하면 : |
| 47 | &emsp;&emsp;&emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 1 (예) |
| 48 | &emsp;→&nbsp;밸브 1번 개별 종합 알람 (`VP_FWU_PICV-1_Alarm`)에 현재 밸브 동작 이상 판정 기록 — 기본 쓰기 우선순위 |
| 49 | 밸브 1번 개별 종합 알람 (`VP_FWU_PICV-1_Alarm`) = 1이면 : |
| 50 | &emsp;→&nbsp;밸브 중 하나라도 알람이 있는지 여부 (`b_any_fault`) = 1 (예) |

## 51~92행 · 밸브 2번 입력·닫힘·동작 감시

| 행 | 해석 |
|---:|---|
| 51 | 상수: 밸브 2번 명령·개도 편차 확인 타이머 번호 = 5 (`PICV_2_DEVIATION_TIMER`) |
| 52 | 현재 밸브 피드백을 우선 유효하지 않은 상태(0)로 둔다. |
| 53 | PICV 입력 사용 설정 (`VP_FWU_PICV_Input_Enable`)이 1이면 : |
| 54 | &emsp;→&nbsp;밸브 2번 실제 통신점의 개도·유량·온도 알람 값이 **모두 0**이면 : |
| 55 | &emsp;&emsp;→&nbsp;실제 통신점 `FWU_PICV-2.Position`에서 실제 개도(%)를 읽어 기존 표시용 관제점 `VP_FWU_PICV-2_Position`에 기록한다. |
| 56 | &emsp;&emsp;→&nbsp;실제 통신점 `FWU_PICV-2.Flow`에서 실제 유량(L/min)를 읽어 기존 표시용 관제점 `VP_FWU_PICV-2_Flow`에 기록한다. |
| 57 | &emsp;&emsp;→&nbsp;실제 통신점 `FWU_PICV-2.Temperature`에서 냉수 출구 온도(℃)를 읽어 기존 표시용 관제점 `VP_FWU_PICV-2_Temperature`에 기록한다. |
| 58 | &emsp;&emsp;→&nbsp;현재 밸브 피드백을 사용할 수 있는 상태(1)로 둔다. |
| 59 | 현재 밸브 실제 개도(%) (`position`) = 밸브 2번 실제 개도(%) (`VP_FWU_PICV-2_Position`) |
| 60 | 실제 개도가 0% 미만 또는 100% 초과하면 : |
| 61 | &emsp;→&nbsp;현재 밸브 피드백 유효 여부 (`b_valid`) = 0 (아니오) |
| 62 | 관제점 `VP_FWU_PICV-2_Feedback_Valid`에 현재 밸브 입력을 사용할 수 있는지(1/0) 기록한다. |
| 63 | 현재 밸브 피드백 유효 여부 = 거짓이면 : |
| 64 | &emsp;→&nbsp;전체 밸브 닫힘 판정 (`b_all_closed`) = 0 (아니오) |
| 65 | &emsp;→&nbsp;전체 밸브 감시 준비 판정 (`b_monitor_ready`) = 0 (아니오) |
| 66 | &emsp;→&nbsp;밸브 중 하나라도 수신 이상이 있는지 여부 (`b_any_comm_fault`) = 1 (예) |
| 67 | &emsp;→&nbsp;밸브 2번 수신 이상 알람 (`VP_FWU_PICV-2_Comm_Fault`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 68 | &emsp;→&nbsp;밸브 2번 개별 종합 알람 (`VP_FWU_PICV-2_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 69 | &emsp;→&nbsp;밸브 2번 명령·개도 편차 확인 타이머(번호 5)를 0초로 초기화 |
| 70 | 63행 조건이 성립하지 않으면 : |
| 71 | &emsp;→&nbsp;밸브 2번 수신 이상 알람 (`VP_FWU_PICV-2_Comm_Fault`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 72 | &emsp;→&nbsp;현재 밸브 실제 개도(%)이 5 이상이면 : |
| 73 | &emsp;&emsp;→&nbsp;전체 밸브 닫힘 판정 (`b_all_closed`) = 0 (아니오) |
| 74 | &emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 0 (아니오) |
| 75 | &emsp;→&nbsp;*[주석] 위치 제어 모드에서만 명령과 실제 개도를 비교한다.* |
| 76 | &emsp;→&nbsp;밸브 제어 모드 (`VP_FWU_PICV_Control_Mode`) = 1이면 : |
| 77 | &emsp;&emsp;→&nbsp;공통 명령과 실제 개도 차이가 30%p 이상이면 : |
| 78 | &emsp;&emsp;&emsp;→&nbsp;밸브 2번 명령·개도 편차 확인 타이머(번호 5) 경과시간이 40 초과하면 : |
| 79 | &emsp;&emsp;&emsp;&emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 1 (예) |
| 80 | &emsp;&emsp;→&nbsp;77행 조건이 성립하지 않으면 : |
| 81 | &emsp;&emsp;&emsp;→&nbsp;밸브 2번 명령·개도 편차 확인 타이머(번호 5)를 0초로 초기화 |
| 82 | &emsp;→&nbsp;76행 조건이 성립하지 않으면 : |
| 83 | &emsp;&emsp;→&nbsp;밸브 2번 명령·개도 편차 확인 타이머(번호 5)를 0초로 초기화 |
| 84 | &emsp;→&nbsp;*[주석] 유량 기준 30/10 LPM은 밸브별 설계 유량 확인 후 감시를 켤 것.* |
| 85 | &emsp;→&nbsp;밸브 유량 감시 사용 설정 (`VP_FWU_PICV_Flow_Check_Enable`) = 1이면 : |
| 86 | &emsp;&emsp;→&nbsp;냉수 공급 조건 성립 표시 (`VP_FWU_Chilled_Water_Supply_Condition`) = 1 **그리고** 현재 밸브 실제 개도(%)이 30 초과 **그리고** 밸브 2번 실제 유량 (`VP_FWU_PICV-2_Flow`)이 밸브 유량 부족 판정 설정값 (`VP_FWU_PICV_No_Flow_Set`) 미만이면 : |
| 87 | &emsp;&emsp;&emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 1 (예) |
| 88 | &emsp;&emsp;→&nbsp;현재 밸브 실제 개도(%)이 1 미만 **그리고** 밸브 2번 실제 유량 (`VP_FWU_PICV-2_Flow`)이 닫힌 밸브의 잔류 유량 판정 설정값 (`VP_FWU_PICV_Leak_Flow_Set`) 초과하면 : |
| 89 | &emsp;&emsp;&emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 1 (예) |
| 90 | &emsp;→&nbsp;밸브 2번 개별 종합 알람 (`VP_FWU_PICV-2_Alarm`)에 현재 밸브 동작 이상 판정 기록 — 기본 쓰기 우선순위 |
| 91 | 밸브 2번 개별 종합 알람 (`VP_FWU_PICV-2_Alarm`) = 1이면 : |
| 92 | &emsp;→&nbsp;밸브 중 하나라도 알람이 있는지 여부 (`b_any_fault`) = 1 (예) |

## 93~134행 · 밸브 3번 입력·닫힘·동작 감시

| 행 | 해석 |
|---:|---|
| 93 | 상수: 밸브 3번 명령·개도 편차 확인 타이머 번호 = 6 (`PICV_3_DEVIATION_TIMER`) |
| 94 | 현재 밸브 피드백을 우선 유효하지 않은 상태(0)로 둔다. |
| 95 | PICV 입력 사용 설정 (`VP_FWU_PICV_Input_Enable`)이 1이면 : |
| 96 | &emsp;→&nbsp;밸브 3번 실제 통신점의 개도·유량·온도 알람 값이 **모두 0**이면 : |
| 97 | &emsp;&emsp;→&nbsp;실제 통신점 `FWU_PICV-3.Position`에서 실제 개도(%)를 읽어 기존 표시용 관제점 `VP_FWU_PICV-3_Position`에 기록한다. |
| 98 | &emsp;&emsp;→&nbsp;실제 통신점 `FWU_PICV-3.Flow`에서 실제 유량(L/min)를 읽어 기존 표시용 관제점 `VP_FWU_PICV-3_Flow`에 기록한다. |
| 99 | &emsp;&emsp;→&nbsp;실제 통신점 `FWU_PICV-3.Temperature`에서 냉수 출구 온도(℃)를 읽어 기존 표시용 관제점 `VP_FWU_PICV-3_Temperature`에 기록한다. |
| 100 | &emsp;&emsp;→&nbsp;현재 밸브 피드백을 사용할 수 있는 상태(1)로 둔다. |
| 101 | 현재 밸브 실제 개도(%) (`position`) = 밸브 3번 실제 개도(%) (`VP_FWU_PICV-3_Position`) |
| 102 | 실제 개도가 0% 미만 또는 100% 초과하면 : |
| 103 | &emsp;→&nbsp;현재 밸브 피드백 유효 여부 (`b_valid`) = 0 (아니오) |
| 104 | 관제점 `VP_FWU_PICV-3_Feedback_Valid`에 현재 밸브 입력을 사용할 수 있는지(1/0) 기록한다. |
| 105 | 현재 밸브 피드백 유효 여부 = 거짓이면 : |
| 106 | &emsp;→&nbsp;전체 밸브 닫힘 판정 (`b_all_closed`) = 0 (아니오) |
| 107 | &emsp;→&nbsp;전체 밸브 감시 준비 판정 (`b_monitor_ready`) = 0 (아니오) |
| 108 | &emsp;→&nbsp;밸브 중 하나라도 수신 이상이 있는지 여부 (`b_any_comm_fault`) = 1 (예) |
| 109 | &emsp;→&nbsp;밸브 3번 수신 이상 알람 (`VP_FWU_PICV-3_Comm_Fault`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 110 | &emsp;→&nbsp;밸브 3번 개별 종합 알람 (`VP_FWU_PICV-3_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 111 | &emsp;→&nbsp;밸브 3번 명령·개도 편차 확인 타이머(번호 6)를 0초로 초기화 |
| 112 | 105행 조건이 성립하지 않으면 : |
| 113 | &emsp;→&nbsp;밸브 3번 수신 이상 알람 (`VP_FWU_PICV-3_Comm_Fault`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 114 | &emsp;→&nbsp;현재 밸브 실제 개도(%)이 5 이상이면 : |
| 115 | &emsp;&emsp;→&nbsp;전체 밸브 닫힘 판정 (`b_all_closed`) = 0 (아니오) |
| 116 | &emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 0 (아니오) |
| 117 | &emsp;→&nbsp;*[주석] 위치 제어 모드에서만 명령과 실제 개도를 비교한다.* |
| 118 | &emsp;→&nbsp;밸브 제어 모드 (`VP_FWU_PICV_Control_Mode`) = 1이면 : |
| 119 | &emsp;&emsp;→&nbsp;공통 명령과 실제 개도 차이가 30%p 이상이면 : |
| 120 | &emsp;&emsp;&emsp;→&nbsp;밸브 3번 명령·개도 편차 확인 타이머(번호 6) 경과시간이 40 초과하면 : |
| 121 | &emsp;&emsp;&emsp;&emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 1 (예) |
| 122 | &emsp;&emsp;→&nbsp;119행 조건이 성립하지 않으면 : |
| 123 | &emsp;&emsp;&emsp;→&nbsp;밸브 3번 명령·개도 편차 확인 타이머(번호 6)를 0초로 초기화 |
| 124 | &emsp;→&nbsp;118행 조건이 성립하지 않으면 : |
| 125 | &emsp;&emsp;→&nbsp;밸브 3번 명령·개도 편차 확인 타이머(번호 6)를 0초로 초기화 |
| 126 | &emsp;→&nbsp;*[주석] 유량 기준 30/10 LPM은 밸브별 설계 유량 확인 후 감시를 켤 것.* |
| 127 | &emsp;→&nbsp;밸브 유량 감시 사용 설정 (`VP_FWU_PICV_Flow_Check_Enable`) = 1이면 : |
| 128 | &emsp;&emsp;→&nbsp;냉수 공급 조건 성립 표시 (`VP_FWU_Chilled_Water_Supply_Condition`) = 1 **그리고** 현재 밸브 실제 개도(%)이 30 초과 **그리고** 밸브 3번 실제 유량 (`VP_FWU_PICV-3_Flow`)이 밸브 유량 부족 판정 설정값 (`VP_FWU_PICV_No_Flow_Set`) 미만이면 : |
| 129 | &emsp;&emsp;&emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 1 (예) |
| 130 | &emsp;&emsp;→&nbsp;현재 밸브 실제 개도(%)이 1 미만 **그리고** 밸브 3번 실제 유량 (`VP_FWU_PICV-3_Flow`)이 닫힌 밸브의 잔류 유량 판정 설정값 (`VP_FWU_PICV_Leak_Flow_Set`) 초과하면 : |
| 131 | &emsp;&emsp;&emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 1 (예) |
| 132 | &emsp;→&nbsp;밸브 3번 개별 종합 알람 (`VP_FWU_PICV-3_Alarm`)에 현재 밸브 동작 이상 판정 기록 — 기본 쓰기 우선순위 |
| 133 | 밸브 3번 개별 종합 알람 (`VP_FWU_PICV-3_Alarm`) = 1이면 : |
| 134 | &emsp;→&nbsp;밸브 중 하나라도 알람이 있는지 여부 (`b_any_fault`) = 1 (예) |

## 135~176행 · 밸브 4번 입력·닫힘·동작 감시

| 행 | 해석 |
|---:|---|
| 135 | 상수: 밸브 4번 명령·개도 편차 확인 타이머 번호 = 7 (`PICV_4_DEVIATION_TIMER`) |
| 136 | 현재 밸브 피드백을 우선 유효하지 않은 상태(0)로 둔다. |
| 137 | PICV 입력 사용 설정 (`VP_FWU_PICV_Input_Enable`)이 1이면 : |
| 138 | &emsp;→&nbsp;밸브 4번 실제 통신점의 개도·유량·온도 알람 값이 **모두 0**이면 : |
| 139 | &emsp;&emsp;→&nbsp;실제 통신점 `FWU_PICV-4.Position`에서 실제 개도(%)를 읽어 기존 표시용 관제점 `VP_FWU_PICV-4_Position`에 기록한다. |
| 140 | &emsp;&emsp;→&nbsp;실제 통신점 `FWU_PICV-4.Flow`에서 실제 유량(L/min)를 읽어 기존 표시용 관제점 `VP_FWU_PICV-4_Flow`에 기록한다. |
| 141 | &emsp;&emsp;→&nbsp;실제 통신점 `FWU_PICV-4.Temperature`에서 냉수 출구 온도(℃)를 읽어 기존 표시용 관제점 `VP_FWU_PICV-4_Temperature`에 기록한다. |
| 142 | &emsp;&emsp;→&nbsp;현재 밸브 피드백을 사용할 수 있는 상태(1)로 둔다. |
| 143 | 현재 밸브 실제 개도(%) (`position`) = 밸브 4번 실제 개도(%) (`VP_FWU_PICV-4_Position`) |
| 144 | 실제 개도가 0% 미만 또는 100% 초과하면 : |
| 145 | &emsp;→&nbsp;현재 밸브 피드백 유효 여부 (`b_valid`) = 0 (아니오) |
| 146 | 관제점 `VP_FWU_PICV-4_Feedback_Valid`에 현재 밸브 입력을 사용할 수 있는지(1/0) 기록한다. |
| 147 | 현재 밸브 피드백 유효 여부 = 거짓이면 : |
| 148 | &emsp;→&nbsp;전체 밸브 닫힘 판정 (`b_all_closed`) = 0 (아니오) |
| 149 | &emsp;→&nbsp;전체 밸브 감시 준비 판정 (`b_monitor_ready`) = 0 (아니오) |
| 150 | &emsp;→&nbsp;밸브 중 하나라도 수신 이상이 있는지 여부 (`b_any_comm_fault`) = 1 (예) |
| 151 | &emsp;→&nbsp;밸브 4번 수신 이상 알람 (`VP_FWU_PICV-4_Comm_Fault`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 152 | &emsp;→&nbsp;밸브 4번 개별 종합 알람 (`VP_FWU_PICV-4_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 153 | &emsp;→&nbsp;밸브 4번 명령·개도 편차 확인 타이머(번호 7)를 0초로 초기화 |
| 154 | 147행 조건이 성립하지 않으면 : |
| 155 | &emsp;→&nbsp;밸브 4번 수신 이상 알람 (`VP_FWU_PICV-4_Comm_Fault`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 156 | &emsp;→&nbsp;현재 밸브 실제 개도(%)이 5 이상이면 : |
| 157 | &emsp;&emsp;→&nbsp;전체 밸브 닫힘 판정 (`b_all_closed`) = 0 (아니오) |
| 158 | &emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 0 (아니오) |
| 159 | &emsp;→&nbsp;*[주석] 위치 제어 모드에서만 명령과 실제 개도를 비교한다.* |
| 160 | &emsp;→&nbsp;밸브 제어 모드 (`VP_FWU_PICV_Control_Mode`) = 1이면 : |
| 161 | &emsp;&emsp;→&nbsp;공통 명령과 실제 개도 차이가 30%p 이상이면 : |
| 162 | &emsp;&emsp;&emsp;→&nbsp;밸브 4번 명령·개도 편차 확인 타이머(번호 7) 경과시간이 40 초과하면 : |
| 163 | &emsp;&emsp;&emsp;&emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 1 (예) |
| 164 | &emsp;&emsp;→&nbsp;161행 조건이 성립하지 않으면 : |
| 165 | &emsp;&emsp;&emsp;→&nbsp;밸브 4번 명령·개도 편차 확인 타이머(번호 7)를 0초로 초기화 |
| 166 | &emsp;→&nbsp;160행 조건이 성립하지 않으면 : |
| 167 | &emsp;&emsp;→&nbsp;밸브 4번 명령·개도 편차 확인 타이머(번호 7)를 0초로 초기화 |
| 168 | &emsp;→&nbsp;*[주석] 유량 기준 30/10 LPM은 밸브별 설계 유량 확인 후 감시를 켤 것.* |
| 169 | &emsp;→&nbsp;밸브 유량 감시 사용 설정 (`VP_FWU_PICV_Flow_Check_Enable`) = 1이면 : |
| 170 | &emsp;&emsp;→&nbsp;냉수 공급 조건 성립 표시 (`VP_FWU_Chilled_Water_Supply_Condition`) = 1 **그리고** 현재 밸브 실제 개도(%)이 30 초과 **그리고** 밸브 4번 실제 유량 (`VP_FWU_PICV-4_Flow`)이 밸브 유량 부족 판정 설정값 (`VP_FWU_PICV_No_Flow_Set`) 미만이면 : |
| 171 | &emsp;&emsp;&emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 1 (예) |
| 172 | &emsp;&emsp;→&nbsp;현재 밸브 실제 개도(%)이 1 미만 **그리고** 밸브 4번 실제 유량 (`VP_FWU_PICV-4_Flow`)이 닫힌 밸브의 잔류 유량 판정 설정값 (`VP_FWU_PICV_Leak_Flow_Set`) 초과하면 : |
| 173 | &emsp;&emsp;&emsp;→&nbsp;현재 밸브 동작 이상 판정 (`b_valve_fault`) = 1 (예) |
| 174 | &emsp;→&nbsp;밸브 4번 개별 종합 알람 (`VP_FWU_PICV-4_Alarm`)에 현재 밸브 동작 이상 판정 기록 — 기본 쓰기 우선순위 |
| 175 | 밸브 4번 개별 종합 알람 (`VP_FWU_PICV-4_Alarm`) = 1이면 : |
| 176 | &emsp;→&nbsp;밸브 중 하나라도 알람이 있는지 여부 (`b_any_fault`) = 1 (예) |

## 177~183행 · 전체 결과 기록

| 행 | 해석 |
|---:|---|
| 177 | 밸브 제어 모드 (`VP_FWU_PICV_Control_Mode`) = 0 **또는** 밸브 유량 감시 사용 설정 (`VP_FWU_PICV_Flow_Check_Enable`) ≠ 1이면 : |
| 178 | &emsp;→&nbsp;전체 밸브 감시 준비 판정 (`b_monitor_ready`) = 0 (아니오) |
| 179 | 밸브 4대 모두 닫힘 표시 (`VP_FWU_PICV_All_Closed`)에 전체 밸브 닫힘 판정 기록 — 기본 쓰기 우선순위 |
| 180 | 밸브 감시 준비 표시 (`VP_FWU_PICV_Monitor_Ready`)에 전체 밸브 감시 준비 판정 기록 — 기본 쓰기 우선순위 |
| 181 | 밸브 종합 알람 (`VP_FWU_PICV_Alarm`)에 밸브 중 하나라도 알람이 있는지 여부 기록 — 기본 쓰기 우선순위 |
| 182 | 밸브 수신 종합 이상 알람 (`VP_FWU_Flow_Comm_Fault`)에 밸브 중 하나라도 수신 이상이 있는지 여부 기록 — 기본 쓰기 우선순위 |
| 183 | *[주석] LJH[2026.1117]밸브별 수신 유효성 및 닫힘 확인: E ----* |

## 읽을 때 짚어둘 점

- `FWU_PICV-n.Position/Flow/Temperature`는 엔지니어가 DDC에 등록할 실제 Modbus 점이다. `VP_FWU_...`는 코드가 값을 복사해 두는 기존 표시용 점이다. 통신 경보는 실제 통신점에서 읽는다.
- Input_Enable은 HMI 등의 서비스 설정으로 엔지니어가 0/1을 넣는 값이다. Input_OK와 수신 순번을 따로 만들어 주지 않는다.
- 알람 값 0일 때 입력을 읽지만, 이것만으로 새로운 응답을 받았다는 별도 증거가 생기는 것은 아니다. 재부팅 직후 첫 응답 전의 DDC 상태는 실기 확인이 남았다.
- 세 입력 중 하나라도 경보가 있으면 그 밸브 입력 전체를 유효하지 않게 본다. 기존 표시값이 남아 있어도 Feedback_Valid=0이면 현재 정상값으로 보면 안 된다.
- All_Closed=1은 네 밸브 입력이 유효하고 개도가 모두 5% 미만이라는 뜻이다. 유량 0이나 완전 밀폐를 보증하는 뜻은 아니다.
- 위치 모드의 명령·실제 개도 차이 30%p 이상, 40초 초과 조건과 선택적 유량 검사는 그대로다. 밸브 2~4도 같은 순서로 반복한다.
- Input_Timeout은 더 이상 사용하지 않는다. 통신 경보가 올라오는 시간은 DDC 설정과 실제 폴링 상태에 달려 있다.
