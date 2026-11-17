# Alarm-1 줄별 해석

> **대상 코드** : `fwu_v2/Logic/Alarm-1.py`  
> **기준 커밋** : `0e0a374d983bf194220e75da79b28598673bc0fa` (`jh`)  
> **행** = 코드 줄 번호 (빈 줄은 생략)  
> **표기** : `→` 들여쓰기 단계 · *[주석]* 코드 안 주석 · **※** 읽을 때 주의할 점

내부·외부 센서의 상하한, 팬 고장, FMS 및 댐퍼 동작을 감시한다.

**목차**

- [1~25행 · 상수와 로직 엔진](#section-1)
- [26~41행 · 내부 센서 유효성](#section-2)
- [43~125행 · 운전 중 상하한 알람](#section-3)
- [127~142행 · 팬 정지 시 상하한 알람 정리](#section-4)
- [144~249행 · 팬별 고장 및 종합 고장](#section-5)
- [251~277행 · 내부 센서 고장 확정](#section-6)
- [279~285행 · FMS 고장 추정](#section-7)
- [287~300행 · 운전 중 댐퍼 닫힘](#section-8)
- [302~313행 · 댐퍼 열림 실패](#section-9)
- [315~328행 · 댐퍼 닫힘 실패](#section-10)

**※ 공통 표기**: 알람 1=발생, 0=해제. 조건이 거짓이라고 모든 관제점이 자동으로 0이 되지는 않는다. 해당 분기에 쓰기 명령이 없으면 이전 값이 남는다. `SECTIMER(..., 0)`은 타이머 초기화, `SECTIMER(..., 1)`은 경과시간 확인이다. 명시적 P번호가 없는 쓰기는 `WRITEPOINT` 기본 우선순위를 사용한다.

<a id="section-1"></a>

## 1~25행 · 상수와 로직 엔진

> 시간·판정 기준과 팬 8대 모델을 지정

| 행 | 해석 |
|---:|---|
| 1 | 상수: 상하한 알람 시작 대기 타이머 번호 = 0 (`LIMIT_TIMER`) |
| 2 | 상수: 팬 고장 감시 시작 대기 타이머 번호 = 1 (`FAN_FAIL_TIMER`) |
| 3 | 상수: 급기온도 고장 확인 타이머 번호 = 2 (`SAT_FAIL_TIMER`) |
| 4 | 상수: 급기습도 고장 확인 타이머 번호 = 3 (`SAH_FAIL_TIMER`) |
| 5 | 상수: 환기온도 고장 확인 타이머 번호 = 4 (`RAT_FAIL_TIMER`) |
| 6 | 상수: 환기습도 고장 확인 타이머 번호 = 5 (`RAH_FAIL_TIMER`) |
| 7 | 상수: FMS 고장 확인 타이머 번호 = 6 (`SAF_FAIL_TIMER`) |
| 8 | 상수: 댐퍼 열림 대기 타이머 번호 = 7 (`SAD_OPEN_TIMER`) |
| 9 | 상수: 댐퍼 닫힘 대기 타이머 번호 = 8 (`SAD_CLOSE_TIMER`) |
| 10 | 상수: 모델의 팬 대수 = 8 (`FAN_COUNT`) |
| 11 | 상수: 상하한 알람 시작 대기시간(초) = 300 (`LIMIT_START_SECONDS`) |
| 12 | 상수: 팬 고장 감시 시작 대기시간(초) = 60 (`FAN_FAIL_CONFIRM_SECONDS`) |
| 13 | 상수: 내부 센서 고장 확인시간(초) = 20 (`SENSOR_FAIL_CONFIRM_SECONDS`) |
| 14 | 상수: FMS 고장 확인시간(초) = 20 (`FMS_FAIL_CONFIRM_SECONDS`) |
| 15 | 상수: 댐퍼 동작 대기시간(초) = 120 (`DAMPER_TRAVEL_SECONDS`) |
| 16 | 상수: 온도 유효 판정 하한(℃) = 0 (`TEMPERATURE_VALID_MIN`) |
| 17 | 상수: 습도 유효 판정 하한(%RH) = 5 (`HUMIDITY_VALID_MIN`) |
| 18 | 상수: 차압 알람 복귀 여유값 = 0.5 (`PRESSURE_HYSTERESIS`) |
| 19 | 상수: 온도 알람 복귀 여유값(℃) = 0.5 (`TEMPERATURE_HYSTERESIS`) |
| 20 | 상수: 습도 알람 복귀 여유값(%RH) = 5 (`HUMIDITY_HYSTERESIS`) |
| 21 | *[주석] F4/F6는 개별 팬 판정과 입출력을 함께 변경. Count VP로 모델을 전환하지 않는다.* |
| 22 | DDC 로직 엔진 객체 생성 (이후 engine.xxx로 관제점을 읽고 씀) |
| 24 | *[주석] 고장 확정 전이라도 무효 측정값으로 고온·저온/고습·저습을 판정하지 않는다.* |
| 25 | *[주석] HMI에서는 이 구간을 정상 측정으로 표시하지 말 것.* |

<a id="section-2"></a>

## 26~41행 · 내부 센서 유효성

> 고장 알람 확정 전이라도 무효값으로 상하한 알람을 만들지 않음

| 행 | 해석 |
|---:|---|
| 26 | 환기온도 유효 여부 (`b_rat_valid`)에 판정 결과 저장: 환기온도 (`FWU_RAT`)이 0 이상 |
| 27 | 환기온도 유효 여부 = 거짓이면 : |
| 28 | &emsp;→&nbsp;환기온도 상한 알람 (`VP_FWU_RAT_High_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 29 | &emsp;→&nbsp;환기온도 하한 알람 (`VP_FWU_RAT_Low_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 30 | 환기습도 유효 여부 (`b_rah_valid`)에 판정 결과 저장: 환기습도 (`FWU_RAH`)이 5 이상 |
| 31 | 환기습도 유효 여부 = 거짓이면 : |
| 32 | &emsp;→&nbsp;환기습도 상한 알람 (`VP_FWU_RAH_High_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 33 | &emsp;→&nbsp;환기습도 하한 알람 (`VP_FWU_RAH_Low_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 34 | 급기온도 유효 여부 (`b_sat_valid`)에 판정 결과 저장: 급기온도 (`FWU_SAT`)이 0 이상 |
| 35 | 급기온도 유효 여부 = 거짓이면 : |
| 36 | &emsp;→&nbsp;급기온도 상한 알람 (`VP_FWU_SAT_High_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 37 | &emsp;→&nbsp;급기온도 하한 알람 (`VP_FWU_SAT_Low_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 38 | 급기습도 유효 여부 (`b_sah_valid`)에 판정 결과 저장: 급기습도 (`FWU_SAH`)이 5 이상 |
| 39 | 급기습도 유효 여부 = 거짓이면 : |
| 40 | &emsp;→&nbsp;급기습도 상한 알람 (`VP_FWU_SAH_High_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 41 | &emsp;→&nbsp;급기습도 하한 알람 (`VP_FWU_SAH_Low_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |

<a id="section-3"></a>

## 43~125행 · 운전 중 상하한 알람

> 팬 운전 후 300초 초과부터 감시. 발생 기준과 복귀 기준 사이에서는 이전 알람 상태 유지

| 행 | 해석 |
|---:|---|
| 43 | 팬 운전 상태 (`VP_FWU_SF_Status`) = 1 **그리고** 상하한 알람 시작 대기 타이머(번호 0) 경과시간이 300초 초과하면 : |
| 44 | &emsp;→&nbsp;환기온도 유효 여부 = 참이면 : |
| 45 | &emsp;&emsp;→&nbsp;환기온도 (`FWU_RAT`)이 환기온도 상한 알람 설정값 (`VP_FWU_RAT_High_Alarm_SP`) 초과하면 : |
| 46 | &emsp;&emsp;&emsp;→&nbsp;환기온도 상한 알람 (`VP_FWU_RAT_High_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 47 | &emsp;&emsp;→&nbsp;환기온도 (`FWU_RAT`)이 (환기온도 상한 알람 설정값 (`VP_FWU_RAT_High_Alarm_SP`) − 온도 알람 복귀 여유값(℃) 0.5) 미만이면 : |
| 48 | &emsp;&emsp;&emsp;→&nbsp;환기온도 상한 알람 (`VP_FWU_RAT_High_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 50 | &emsp;&emsp;→&nbsp;환기온도 (`FWU_RAT`)이 환기온도 하한 알람 설정값 (`VP_FWU_RAT_Low_Alarm_SP`) 미만이면 : |
| 51 | &emsp;&emsp;&emsp;→&nbsp;환기온도 하한 알람 (`VP_FWU_RAT_Low_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 52 | &emsp;&emsp;→&nbsp;환기온도 (`FWU_RAT`)이 (환기온도 하한 알람 설정값 (`VP_FWU_RAT_Low_Alarm_SP`) + 온도 알람 복귀 여유값(℃) 0.5) 초과하면 : |
| 53 | &emsp;&emsp;&emsp;→&nbsp;환기온도 하한 알람 (`VP_FWU_RAT_Low_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 55 | &emsp;→&nbsp;환기습도 유효 여부 = 참이면 : |
| 56 | &emsp;&emsp;→&nbsp;환기습도 (`FWU_RAH`)이 환기습도 상한 알람 설정값 (`VP_FWU_RAH_High_Alarm_SP`) 초과하면 : |
| 57 | &emsp;&emsp;&emsp;→&nbsp;환기습도 상한 알람 (`VP_FWU_RAH_High_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 58 | &emsp;&emsp;→&nbsp;환기습도 (`FWU_RAH`)이 (환기습도 상한 알람 설정값 (`VP_FWU_RAH_High_Alarm_SP`) − 습도 알람 복귀 여유값(%RH) 5) 미만이면 : |
| 59 | &emsp;&emsp;&emsp;→&nbsp;환기습도 상한 알람 (`VP_FWU_RAH_High_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 61 | &emsp;&emsp;→&nbsp;환기습도 (`FWU_RAH`)이 환기습도 하한 알람 설정값 (`VP_FWU_RAH_Low_Alarm_SP`) 미만이면 : |
| 62 | &emsp;&emsp;&emsp;→&nbsp;환기습도 하한 알람 (`VP_FWU_RAH_Low_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 63 | &emsp;&emsp;→&nbsp;환기습도 (`FWU_RAH`)이 (환기습도 하한 알람 설정값 (`VP_FWU_RAH_Low_Alarm_SP`) + 습도 알람 복귀 여유값(%RH) 5) 초과하면 : |
| 64 | &emsp;&emsp;&emsp;→&nbsp;환기습도 하한 알람 (`VP_FWU_RAH_Low_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 66 | &emsp;→&nbsp;급기온도 유효 여부 = 참이면 : |
| 67 | &emsp;&emsp;→&nbsp;급기온도 (`FWU_SAT`)이 급기온도 상한 알람 설정값 (`VP_FWU_SAT_High_Alarm_SP`) 초과하면 : |
| 68 | &emsp;&emsp;&emsp;→&nbsp;급기온도 상한 알람 (`VP_FWU_SAT_High_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 69 | &emsp;&emsp;→&nbsp;급기온도 (`FWU_SAT`)이 (급기온도 상한 알람 설정값 (`VP_FWU_SAT_High_Alarm_SP`) − 온도 알람 복귀 여유값(℃) 0.5) 미만이면 : |
| 70 | &emsp;&emsp;&emsp;→&nbsp;급기온도 상한 알람 (`VP_FWU_SAT_High_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 72 | &emsp;&emsp;→&nbsp;급기온도 (`FWU_SAT`)이 급기온도 하한 알람 설정값 (`VP_FWU_SAT_Low_Alarm_SP`) 미만이면 : |
| 73 | &emsp;&emsp;&emsp;→&nbsp;급기온도 하한 알람 (`VP_FWU_SAT_Low_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 74 | &emsp;&emsp;→&nbsp;급기온도 (`FWU_SAT`)이 (급기온도 하한 알람 설정값 (`VP_FWU_SAT_Low_Alarm_SP`) + 온도 알람 복귀 여유값(℃) 0.5) 초과하면 : |
| 75 | &emsp;&emsp;&emsp;→&nbsp;급기온도 하한 알람 (`VP_FWU_SAT_Low_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 77 | &emsp;→&nbsp;급기습도 유효 여부 = 참이면 : |
| 78 | &emsp;&emsp;→&nbsp;급기습도 (`FWU_SAH`)이 급기습도 상한 알람 설정값 (`VP_FWU_SAH_High_Alarm_SP`) 초과하면 : |
| 79 | &emsp;&emsp;&emsp;→&nbsp;급기습도 상한 알람 (`VP_FWU_SAH_High_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 80 | &emsp;&emsp;→&nbsp;급기습도 (`FWU_SAH`)이 (급기습도 상한 알람 설정값 (`VP_FWU_SAH_High_Alarm_SP`) − 습도 알람 복귀 여유값(%RH) 5) 미만이면 : |
| 81 | &emsp;&emsp;&emsp;→&nbsp;급기습도 상한 알람 (`VP_FWU_SAH_High_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 83 | &emsp;&emsp;→&nbsp;급기습도 (`FWU_SAH`)이 급기습도 하한 알람 설정값 (`VP_FWU_SAH_Low_Alarm_SP`) 미만이면 : |
| 84 | &emsp;&emsp;&emsp;→&nbsp;급기습도 하한 알람 (`VP_FWU_SAH_Low_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 85 | &emsp;&emsp;→&nbsp;급기습도 (`FWU_SAH`)이 (급기습도 하한 알람 설정값 (`VP_FWU_SAH_Low_Alarm_SP`) + 습도 알람 복귀 여유값(%RH) 5) 초과하면 : |
| 86 | &emsp;&emsp;&emsp;→&nbsp;급기습도 하한 알람 (`VP_FWU_SAH_Low_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 88 | &emsp;→&nbsp;냉복도 온도 제어 입력 유효 표시 (`VP_FWU_CZT_PV_Valid`) = 1이면 : |
| 89 | &emsp;&emsp;→&nbsp;냉복도 온도 최댓값 (`VP_FWU_CZT_Max`)이 냉복도 온도 상한 알람 설정값 (`VP_FWU_CZT_High_Alarm_SP`) 초과하면 : |
| 90 | &emsp;&emsp;&emsp;→&nbsp;냉복도 온도 상한 알람 (`VP_FWU_CZT_High_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 91 | &emsp;&emsp;→&nbsp;냉복도 온도 최댓값 (`VP_FWU_CZT_Max`)이 (냉복도 온도 상한 알람 설정값 (`VP_FWU_CZT_High_Alarm_SP`) − 온도 알람 복귀 여유값(℃) 0.5) 미만이면 : |
| 92 | &emsp;&emsp;&emsp;→&nbsp;냉복도 온도 상한 알람 (`VP_FWU_CZT_High_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 93 | &emsp;&emsp;→&nbsp;냉복도 온도 최솟값 (`VP_FWU_CZT_Min`)이 냉복도 온도 하한 알람 설정값 (`VP_FWU_CZT_Low_Alarm_SP`) 미만이면 : |
| 94 | &emsp;&emsp;&emsp;→&nbsp;냉복도 온도 하한 알람 (`VP_FWU_CZT_Low_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 95 | &emsp;&emsp;→&nbsp;냉복도 온도 최솟값 (`VP_FWU_CZT_Min`)이 (냉복도 온도 하한 알람 설정값 (`VP_FWU_CZT_Low_Alarm_SP`) + 온도 알람 복귀 여유값(℃) 0.5) 초과하면 : |
| 96 | &emsp;&emsp;&emsp;→&nbsp;냉복도 온도 하한 알람 (`VP_FWU_CZT_Low_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 97 | &emsp;→&nbsp;88행 조건이 성립하지 않으면 : |
| 98 | &emsp;&emsp;→&nbsp;냉복도 온도 상한 알람 (`VP_FWU_CZT_High_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 99 | &emsp;&emsp;→&nbsp;냉복도 온도 하한 알람 (`VP_FWU_CZT_Low_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 101 | &emsp;→&nbsp;열복도 온도 제어 입력 유효 표시 (`VP_FWU_HZT_PV_Valid`) = 1이면 : |
| 102 | &emsp;&emsp;→&nbsp;열복도 온도 최댓값 (`VP_FWU_HZT_Max`)이 열복도 온도 상한 알람 설정값 (`VP_FWU_HZT_High_Alarm_SP`) 초과하면 : |
| 103 | &emsp;&emsp;&emsp;→&nbsp;열복도 온도 상한 알람 (`VP_FWU_HZT_High_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 104 | &emsp;&emsp;→&nbsp;열복도 온도 최댓값 (`VP_FWU_HZT_Max`)이 (열복도 온도 상한 알람 설정값 (`VP_FWU_HZT_High_Alarm_SP`) − 온도 알람 복귀 여유값(℃) 0.5) 미만이면 : |
| 105 | &emsp;&emsp;&emsp;→&nbsp;열복도 온도 상한 알람 (`VP_FWU_HZT_High_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 106 | &emsp;&emsp;→&nbsp;열복도 온도 최솟값 (`VP_FWU_HZT_Min`)이 열복도 온도 하한 알람 설정값 (`VP_FWU_HZT_Low_Alarm_SP`) 미만이면 : |
| 107 | &emsp;&emsp;&emsp;→&nbsp;열복도 온도 하한 알람 (`VP_FWU_HZT_Low_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 108 | &emsp;&emsp;→&nbsp;열복도 온도 최솟값 (`VP_FWU_HZT_Min`)이 (열복도 온도 하한 알람 설정값 (`VP_FWU_HZT_Low_Alarm_SP`) + 온도 알람 복귀 여유값(℃) 0.5) 초과하면 : |
| 109 | &emsp;&emsp;&emsp;→&nbsp;열복도 온도 하한 알람 (`VP_FWU_HZT_Low_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 110 | &emsp;→&nbsp;101행 조건이 성립하지 않으면 : |
| 111 | &emsp;&emsp;→&nbsp;열복도 온도 상한 알람 (`VP_FWU_HZT_High_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 112 | &emsp;&emsp;→&nbsp;열복도 온도 하한 알람 (`VP_FWU_HZT_Low_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 114 | &emsp;→&nbsp;룸 차압 제어 입력 유효 표시 (`VP_FWU_RDP_PV_Valid`) = 1이면 : |
| 115 | &emsp;&emsp;→&nbsp;룸 차압 최댓값 (`VP_FWU_RDP_Max`)이 룸 차압 상한 알람 설정값 (`VP_FWU_RDP_High_Alarm_SP`) 초과하면 : |
| 116 | &emsp;&emsp;&emsp;→&nbsp;룸 차압 상한 알람 (`VP_FWU_RDP_High_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 117 | &emsp;&emsp;→&nbsp;룸 차압 최댓값 (`VP_FWU_RDP_Max`)이 (룸 차압 상한 알람 설정값 (`VP_FWU_RDP_High_Alarm_SP`) − 차압 알람 복귀 여유값 0.5) 미만이면 : |
| 118 | &emsp;&emsp;&emsp;→&nbsp;룸 차압 상한 알람 (`VP_FWU_RDP_High_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 119 | &emsp;&emsp;→&nbsp;룸 차압 최솟값 (`VP_FWU_RDP_Min`)이 룸 차압 하한 알람 설정값 (`VP_FWU_RDP_Low_Alarm_SP`) 미만이면 : |
| 120 | &emsp;&emsp;&emsp;→&nbsp;룸 차압 하한 알람 (`VP_FWU_RDP_Low_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 121 | &emsp;&emsp;→&nbsp;룸 차압 최솟값 (`VP_FWU_RDP_Min`)이 (룸 차압 하한 알람 설정값 (`VP_FWU_RDP_Low_Alarm_SP`) + 차압 알람 복귀 여유값 0.5) 초과하면 : |
| 122 | &emsp;&emsp;&emsp;→&nbsp;룸 차압 하한 알람 (`VP_FWU_RDP_Low_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 123 | &emsp;→&nbsp;114행 조건이 성립하지 않으면 : |
| 124 | &emsp;&emsp;→&nbsp;룸 차압 상한 알람 (`VP_FWU_RDP_High_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 125 | &emsp;&emsp;→&nbsp;룸 차압 하한 알람 (`VP_FWU_RDP_Low_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |

<a id="section-4"></a>

## 127~142행 · 팬 정지 시 상하한 알람 정리

> 시작 타이머와 상하한 알람을 초기화

| 행 | 해석 |
|---:|---|
| 127 | 팬 운전 상태 (`VP_FWU_SF_Status`) = 0이면 : |
| 128 | &emsp;→&nbsp;상하한 알람 시작 대기 타이머(번호 0)를 0초로 초기화 |
| 129 | &emsp;→&nbsp;환기온도 상한 알람 (`VP_FWU_RAT_High_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 130 | &emsp;→&nbsp;환기온도 하한 알람 (`VP_FWU_RAT_Low_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 131 | &emsp;→&nbsp;환기습도 상한 알람 (`VP_FWU_RAH_High_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 132 | &emsp;→&nbsp;환기습도 하한 알람 (`VP_FWU_RAH_Low_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 133 | &emsp;→&nbsp;급기온도 상한 알람 (`VP_FWU_SAT_High_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 134 | &emsp;→&nbsp;급기온도 하한 알람 (`VP_FWU_SAT_Low_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 135 | &emsp;→&nbsp;급기습도 상한 알람 (`VP_FWU_SAH_High_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 136 | &emsp;→&nbsp;급기습도 하한 알람 (`VP_FWU_SAH_Low_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 137 | &emsp;→&nbsp;냉복도 온도 상한 알람 (`VP_FWU_CZT_High_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 138 | &emsp;→&nbsp;냉복도 온도 하한 알람 (`VP_FWU_CZT_Low_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 139 | &emsp;→&nbsp;열복도 온도 상한 알람 (`VP_FWU_HZT_High_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 140 | &emsp;→&nbsp;열복도 온도 하한 알람 (`VP_FWU_HZT_Low_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 141 | &emsp;→&nbsp;룸 차압 상한 알람 (`VP_FWU_RDP_High_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 142 | &emsp;→&nbsp;룸 차압 하한 알람 (`VP_FWU_RDP_Low_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |

<a id="section-5"></a>

## 144~249행 · 팬별 고장 및 종합 고장

> 운전 명령·최소 속도 조건 성립 후 60초 초과부터 판정

| 행 | 해석 |
|---:|---|
| 144 | FWU 운전 명령 (`VP_FWU_Command`) = 1 **그리고** 팬 속도 요구값 (`VP_FWU_SF_Speed_Value`)이 팬 최소 속도 (`VP_FWU_SF_Speed_Min`) 이상이면 : |
| 145 | &emsp;→&nbsp;팬 고장 감시 시작 대기 타이머(번호 1) 경과시간이 60초 초과하면 : |
| 146 | &emsp;&emsp;→&nbsp;팬 고장 판정 회전수 (`fail_rpm`) = 팬 고장 판정 회전수 설정값 (`VP_FWU_SF_Failure_RPM_Set`) |
| 147 | &emsp;&emsp;→&nbsp;공통 차압이 낮은지 여부 (`b_sf_dp_low`)에 판정 결과 저장: 팬 공통 차압 (`FWU_SAFLOW_DP`)이 팬 운전 판정 차압 설정값 (`VP_FWU_SF_Run_DP_Set`) 이하 |
| 149 | &emsp;&emsp;→&nbsp;팬 1번 통신 이상 알람 (`VP_FWU_SF-1_Comm_Fault`) = 0이면 : |
| 150 | &emsp;&emsp;&emsp;→&nbsp;팬 1번 고장 여부 (`b_sf_1_fail`)에 판정 결과 저장: 팬 1번 현재 회전수 (`FWU_SF-1.Current_RPM`)이 팬 고장 판정 회전수 미만 |
| 151 | &emsp;&emsp;→&nbsp;149행 조건이 성립하지 않으면 : |
| 152 | &emsp;&emsp;&emsp;→&nbsp;팬 1번 고장 여부 (`b_sf_1_fail`) = 공통 차압이 낮은지 여부 |
| 154 | &emsp;&emsp;→&nbsp;팬 2번 통신 이상 알람 (`VP_FWU_SF-2_Comm_Fault`) = 0이면 : |
| 155 | &emsp;&emsp;&emsp;→&nbsp;팬 2번 고장 여부 (`b_sf_2_fail`)에 판정 결과 저장: 팬 2번 현재 회전수 (`FWU_SF-2.Current_RPM`)이 팬 고장 판정 회전수 미만 |
| 156 | &emsp;&emsp;→&nbsp;154행 조건이 성립하지 않으면 : |
| 157 | &emsp;&emsp;&emsp;→&nbsp;팬 2번 고장 여부 (`b_sf_2_fail`) = 공통 차압이 낮은지 여부 |
| 159 | &emsp;&emsp;→&nbsp;팬 3번 통신 이상 알람 (`VP_FWU_SF-3_Comm_Fault`) = 0이면 : |
| 160 | &emsp;&emsp;&emsp;→&nbsp;팬 3번 고장 여부 (`b_sf_3_fail`)에 판정 결과 저장: 팬 3번 현재 회전수 (`FWU_SF-3.Current_RPM`)이 팬 고장 판정 회전수 미만 |
| 161 | &emsp;&emsp;→&nbsp;159행 조건이 성립하지 않으면 : |
| 162 | &emsp;&emsp;&emsp;→&nbsp;팬 3번 고장 여부 (`b_sf_3_fail`) = 공통 차압이 낮은지 여부 |
| 164 | &emsp;&emsp;→&nbsp;팬 4번 통신 이상 알람 (`VP_FWU_SF-4_Comm_Fault`) = 0이면 : |
| 165 | &emsp;&emsp;&emsp;→&nbsp;팬 4번 고장 여부 (`b_sf_4_fail`)에 판정 결과 저장: 팬 4번 현재 회전수 (`FWU_SF-4.Current_RPM`)이 팬 고장 판정 회전수 미만 |
| 166 | &emsp;&emsp;→&nbsp;164행 조건이 성립하지 않으면 : |
| 167 | &emsp;&emsp;&emsp;→&nbsp;팬 4번 고장 여부 (`b_sf_4_fail`) = 공통 차압이 낮은지 여부 |
| 169 | &emsp;&emsp;→&nbsp;팬 5번 통신 이상 알람 (`VP_FWU_SF-5_Comm_Fault`) = 0이면 : |
| 170 | &emsp;&emsp;&emsp;→&nbsp;팬 5번 고장 여부 (`b_sf_5_fail`)에 판정 결과 저장: 팬 5번 현재 회전수 (`FWU_SF-5.Current_RPM`)이 팬 고장 판정 회전수 미만 |
| 171 | &emsp;&emsp;→&nbsp;169행 조건이 성립하지 않으면 : |
| 172 | &emsp;&emsp;&emsp;→&nbsp;팬 5번 고장 여부 (`b_sf_5_fail`) = 공통 차압이 낮은지 여부 |
| 174 | &emsp;&emsp;→&nbsp;팬 6번 통신 이상 알람 (`VP_FWU_SF-6_Comm_Fault`) = 0이면 : |
| 175 | &emsp;&emsp;&emsp;→&nbsp;팬 6번 고장 여부 (`b_sf_6_fail`)에 판정 결과 저장: 팬 6번 현재 회전수 (`FWU_SF-6.Current_RPM`)이 팬 고장 판정 회전수 미만 |
| 176 | &emsp;&emsp;→&nbsp;174행 조건이 성립하지 않으면 : |
| 177 | &emsp;&emsp;&emsp;→&nbsp;팬 6번 고장 여부 (`b_sf_6_fail`) = 공통 차압이 낮은지 여부 |
| 179 | &emsp;&emsp;→&nbsp;팬 7번 통신 이상 알람 (`VP_FWU_SF-7_Comm_Fault`) = 0이면 : |
| 180 | &emsp;&emsp;&emsp;→&nbsp;팬 7번 고장 여부 (`b_sf_7_fail`)에 판정 결과 저장: 팬 7번 현재 회전수 (`FWU_SF-7.Current_RPM`)이 팬 고장 판정 회전수 미만 |
| 181 | &emsp;&emsp;→&nbsp;179행 조건이 성립하지 않으면 : |
| 182 | &emsp;&emsp;&emsp;→&nbsp;팬 7번 고장 여부 (`b_sf_7_fail`) = 공통 차압이 낮은지 여부 |
| 184 | &emsp;&emsp;→&nbsp;팬 8번 통신 이상 알람 (`VP_FWU_SF-8_Comm_Fault`) = 0이면 : |
| 185 | &emsp;&emsp;&emsp;→&nbsp;팬 8번 고장 여부 (`b_sf_8_fail`)에 판정 결과 저장: 팬 8번 현재 회전수 (`FWU_SF-8.Current_RPM`)이 팬 고장 판정 회전수 미만 |
| 186 | &emsp;&emsp;→&nbsp;184행 조건이 성립하지 않으면 : |
| 187 | &emsp;&emsp;&emsp;→&nbsp;팬 8번 고장 여부 (`b_sf_8_fail`) = 공통 차압이 낮은지 여부 |
| 189 | &emsp;&emsp;→&nbsp;고장 팬 수 (`sf_fail_count`) = 0 |
| 190 | &emsp;&emsp;→&nbsp;팬 1번 고장 여부 = 참이면 : |
| 191 | &emsp;&emsp;&emsp;→&nbsp;고장 팬 수에 1대를 더함 |
| 192 | &emsp;&emsp;&emsp;→&nbsp;팬 1번 운전 실패 알람 (`VP_FWU_SF-1_Run_Fail_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 193 | &emsp;&emsp;→&nbsp;190행 조건이 성립하지 않으면 : |
| 194 | &emsp;&emsp;&emsp;→&nbsp;팬 1번 운전 실패 알람 (`VP_FWU_SF-1_Run_Fail_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 195 | &emsp;&emsp;→&nbsp;팬 2번 고장 여부 = 참이면 : |
| 196 | &emsp;&emsp;&emsp;→&nbsp;고장 팬 수에 1대를 더함 |
| 197 | &emsp;&emsp;&emsp;→&nbsp;팬 2번 운전 실패 알람 (`VP_FWU_SF-2_Run_Fail_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 198 | &emsp;&emsp;→&nbsp;195행 조건이 성립하지 않으면 : |
| 199 | &emsp;&emsp;&emsp;→&nbsp;팬 2번 운전 실패 알람 (`VP_FWU_SF-2_Run_Fail_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 200 | &emsp;&emsp;→&nbsp;팬 3번 고장 여부 = 참이면 : |
| 201 | &emsp;&emsp;&emsp;→&nbsp;고장 팬 수에 1대를 더함 |
| 202 | &emsp;&emsp;&emsp;→&nbsp;팬 3번 운전 실패 알람 (`VP_FWU_SF-3_Run_Fail_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 203 | &emsp;&emsp;→&nbsp;200행 조건이 성립하지 않으면 : |
| 204 | &emsp;&emsp;&emsp;→&nbsp;팬 3번 운전 실패 알람 (`VP_FWU_SF-3_Run_Fail_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 205 | &emsp;&emsp;→&nbsp;팬 4번 고장 여부 = 참이면 : |
| 206 | &emsp;&emsp;&emsp;→&nbsp;고장 팬 수에 1대를 더함 |
| 207 | &emsp;&emsp;&emsp;→&nbsp;팬 4번 운전 실패 알람 (`VP_FWU_SF-4_Run_Fail_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 208 | &emsp;&emsp;→&nbsp;205행 조건이 성립하지 않으면 : |
| 209 | &emsp;&emsp;&emsp;→&nbsp;팬 4번 운전 실패 알람 (`VP_FWU_SF-4_Run_Fail_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 210 | &emsp;&emsp;→&nbsp;팬 5번 고장 여부 = 참이면 : |
| 211 | &emsp;&emsp;&emsp;→&nbsp;고장 팬 수에 1대를 더함 |
| 212 | &emsp;&emsp;&emsp;→&nbsp;팬 5번 운전 실패 알람 (`VP_FWU_SF-5_Run_Fail_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 213 | &emsp;&emsp;→&nbsp;210행 조건이 성립하지 않으면 : |
| 214 | &emsp;&emsp;&emsp;→&nbsp;팬 5번 운전 실패 알람 (`VP_FWU_SF-5_Run_Fail_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 215 | &emsp;&emsp;→&nbsp;팬 6번 고장 여부 = 참이면 : |
| 216 | &emsp;&emsp;&emsp;→&nbsp;고장 팬 수에 1대를 더함 |
| 217 | &emsp;&emsp;&emsp;→&nbsp;팬 6번 운전 실패 알람 (`VP_FWU_SF-6_Run_Fail_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 218 | &emsp;&emsp;→&nbsp;215행 조건이 성립하지 않으면 : |
| 219 | &emsp;&emsp;&emsp;→&nbsp;팬 6번 운전 실패 알람 (`VP_FWU_SF-6_Run_Fail_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 220 | &emsp;&emsp;→&nbsp;팬 7번 고장 여부 = 참이면 : |
| 221 | &emsp;&emsp;&emsp;→&nbsp;고장 팬 수에 1대를 더함 |
| 222 | &emsp;&emsp;&emsp;→&nbsp;팬 7번 운전 실패 알람 (`VP_FWU_SF-7_Run_Fail_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 223 | &emsp;&emsp;→&nbsp;220행 조건이 성립하지 않으면 : |
| 224 | &emsp;&emsp;&emsp;→&nbsp;팬 7번 운전 실패 알람 (`VP_FWU_SF-7_Run_Fail_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 225 | &emsp;&emsp;→&nbsp;팬 8번 고장 여부 = 참이면 : |
| 226 | &emsp;&emsp;&emsp;→&nbsp;고장 팬 수에 1대를 더함 |
| 227 | &emsp;&emsp;&emsp;→&nbsp;팬 8번 운전 실패 알람 (`VP_FWU_SF-8_Run_Fail_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 228 | &emsp;&emsp;→&nbsp;225행 조건이 성립하지 않으면 : |
| 229 | &emsp;&emsp;&emsp;→&nbsp;팬 8번 운전 실패 알람 (`VP_FWU_SF-8_Run_Fail_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 231 | &emsp;&emsp;→&nbsp;*[주석] 종합 팬 고장 기준은 SMX01의 절반 이상 고장을 임시로 유지한다.* |
| 232 | &emsp;&emsp;→&nbsp;*[주석] 신규 팬의 정압-풍량 곡선과 허용 최대속도를 기준으로, 팬 고장 시에도* |
| 233 | &emsp;&emsp;→&nbsp;*[주석] 요구 정압에서 목표 풍량을 확보할 수 있는 고장 허용 대수를 확인할 것.* |
| 234 | &emsp;&emsp;→&nbsp;*[주석] 확인 결과에 맞춰 아래 종합 고장 대수 기준과 Failover 정지 연계를 재검토한다.* |
| 235 | &emsp;&emsp;→&nbsp;고장 팬 수가 전체 팬 수의 절반 이상이면 (현재 8대 중 4대 이상) : |
| 236 | &emsp;&emsp;&emsp;→&nbsp;팬 종합 고장 알람 (`VP_FWU_SF_Failure_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 237 | &emsp;&emsp;→&nbsp;235행 조건이 성립하지 않으면 : |
| 238 | &emsp;&emsp;&emsp;→&nbsp;팬 종합 고장 알람 (`VP_FWU_SF_Failure_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 239 | 144행 조건이 성립하지 않으면 : |
| 240 | &emsp;→&nbsp;팬 고장 감시 시작 대기 타이머(번호 1)를 0초로 초기화 |
| 241 | &emsp;→&nbsp;팬 종합 고장 알람 (`VP_FWU_SF_Failure_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 242 | &emsp;→&nbsp;팬 1번 운전 실패 알람 (`VP_FWU_SF-1_Run_Fail_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 243 | &emsp;→&nbsp;팬 2번 운전 실패 알람 (`VP_FWU_SF-2_Run_Fail_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 244 | &emsp;→&nbsp;팬 3번 운전 실패 알람 (`VP_FWU_SF-3_Run_Fail_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 245 | &emsp;→&nbsp;팬 4번 운전 실패 알람 (`VP_FWU_SF-4_Run_Fail_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 246 | &emsp;→&nbsp;팬 5번 운전 실패 알람 (`VP_FWU_SF-5_Run_Fail_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 247 | &emsp;→&nbsp;팬 6번 운전 실패 알람 (`VP_FWU_SF-6_Run_Fail_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 248 | &emsp;→&nbsp;팬 7번 운전 실패 알람 (`VP_FWU_SF-7_Run_Fail_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 249 | &emsp;→&nbsp;팬 8번 운전 실패 알람 (`VP_FWU_SF-8_Run_Fail_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |

<a id="section-6"></a>

## 251~277행 · 내부 센서 고장 확정

> 무효 측정 상태가 20초를 넘으면 고장 알람

| 행 | 해석 |
|---:|---|
| 251 | 급기온도 유효 여부 = 거짓이면 : |
| 252 | &emsp;→&nbsp;급기온도 고장 확인 타이머(번호 2) 경과시간이 20초 초과하면 : |
| 253 | &emsp;&emsp;→&nbsp;급기온도 센서 고장 알람 (`VP_FWU_SAT_Failure_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 254 | 251행 조건이 성립하지 않으면 : |
| 255 | &emsp;→&nbsp;급기온도 고장 확인 타이머(번호 2)를 0초로 초기화 |
| 256 | &emsp;→&nbsp;급기온도 센서 고장 알람 (`VP_FWU_SAT_Failure_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 258 | 급기습도 유효 여부 = 거짓이면 : |
| 259 | &emsp;→&nbsp;급기습도 고장 확인 타이머(번호 3) 경과시간이 20초 초과하면 : |
| 260 | &emsp;&emsp;→&nbsp;급기습도 센서 고장 알람 (`VP_FWU_SAH_Failure_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 261 | 258행 조건이 성립하지 않으면 : |
| 262 | &emsp;→&nbsp;급기습도 고장 확인 타이머(번호 3)를 0초로 초기화 |
| 263 | &emsp;→&nbsp;급기습도 센서 고장 알람 (`VP_FWU_SAH_Failure_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 265 | 환기온도 유효 여부 = 거짓이면 : |
| 266 | &emsp;→&nbsp;환기온도 고장 확인 타이머(번호 4) 경과시간이 20초 초과하면 : |
| 267 | &emsp;&emsp;→&nbsp;환기온도 센서 고장 알람 (`VP_FWU_RAT_Failure_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 268 | 265행 조건이 성립하지 않으면 : |
| 269 | &emsp;→&nbsp;환기온도 고장 확인 타이머(번호 4)를 0초로 초기화 |
| 270 | &emsp;→&nbsp;환기온도 센서 고장 알람 (`VP_FWU_RAT_Failure_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 272 | 환기습도 유효 여부 = 거짓이면 : |
| 273 | &emsp;→&nbsp;환기습도 고장 확인 타이머(번호 5) 경과시간이 20초 초과하면 : |
| 274 | &emsp;&emsp;→&nbsp;환기습도 센서 고장 알람 (`VP_FWU_RAH_Failure_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 275 | 272행 조건이 성립하지 않으면 : |
| 276 | &emsp;→&nbsp;환기습도 고장 확인 타이머(번호 5)를 0초로 초기화 |
| 277 | &emsp;→&nbsp;환기습도 센서 고장 알람 (`VP_FWU_RAH_Failure_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |

<a id="section-7"></a>

## 279~285행 · FMS 고장 추정

> 팬은 빠르게 도는데 공통 차압이 낮은 상태를 감시

| 행 | 해석 |
|---:|---|
| 279 | *[주석] FMS 고장은 RPM과 차압의 불일치로 추정한다. 실제 풍량 부족과 센서·배선 이상은 구분하지 못한다.* |
| 280 | 공통 차압이 FMS 고장 차압 설정값보다 낮고, 팬 1~8번 중 최고 회전수가 FMS 고장 회전수 설정값보다 높으면 : |
| 281 | &emsp;→&nbsp;FMS 고장 확인 타이머(번호 6) 경과시간이 20초 초과하면 : |
| 282 | &emsp;&emsp;→&nbsp;FMS 고장 알람 (`VP_FWU_SAF_Failure_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 283 | 280행 조건이 성립하지 않으면 : |
| 284 | &emsp;→&nbsp;FMS 고장 확인 타이머(번호 6)를 0초로 초기화 |
| 285 | &emsp;→&nbsp;FMS 고장 알람 (`VP_FWU_SAF_Failure_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |

<a id="section-8"></a>

## 287~300행 · 운전 중 댐퍼 닫힘

> 일부 닫힘과 전체 닫힘을 구분

| 행 | 해석 |
|---:|---|
| 287 | 댐퍼 4대가 모두 닫혔는지 여부 (`b_sad_all_close`)에 판정 결과 저장: 댐퍼 1~4번의 닫힘 접점이 모두 1 |
| 288 | 닫힌 댐퍼가 하나라도 있는지 여부 (`b_sad_any_close`)에 판정 결과 저장: 댐퍼 1~4번의 닫힘 접점이 하나라도 1 |
| 289 | 팬 운전 상태 (`VP_FWU_SF_Status`) = 1이면 : |
| 290 | &emsp;→&nbsp;닫힌 댐퍼가 하나라도 있는지 여부 = 참 **그리고** 댐퍼 4대가 모두 닫혔는지 여부 = 거짓이면 : |
| 291 | &emsp;&emsp;→&nbsp;댐퍼 일부 닫힘 알람 (`VP_FWU_SAD_Partial_Close_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 292 | &emsp;→&nbsp;290행 조건이 성립하지 않으면 : |
| 293 | &emsp;&emsp;→&nbsp;댐퍼 일부 닫힘 알람 (`VP_FWU_SAD_Partial_Close_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 294 | 289행 조건이 성립하지 않으면 : |
| 295 | &emsp;→&nbsp;댐퍼 일부 닫힘 알람 (`VP_FWU_SAD_Partial_Close_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 297 | 댐퍼 4대가 모두 닫혔는지 여부 = 참 **그리고** 댐퍼 4대 공통 명령(1=열기, 0=닫기) (`FWU_SAD-1_4_COMMAND`) = 1 **그리고** (팬 운전 상태 (`VP_FWU_SF_Status`) = 1 **또는** 댐퍼 전체 닫힘 알람 (`VP_FWU_SAD_Full_Close_Alarm`) = 1)이면 : |
| 298 | &emsp;→&nbsp;댐퍼 전체 닫힘 알람 (`VP_FWU_SAD_Full_Close_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 299 | 297행 조건이 성립하지 않으면 : |
| 300 | &emsp;→&nbsp;댐퍼 전체 닫힘 알람 (`VP_FWU_SAD_Full_Close_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |

<a id="section-9"></a>

## 302~313행 · 댐퍼 열림 실패

> 팬 정지·열기 명령 상태에서 120초 초과 후 확인

| 행 | 해석 |
|---:|---|
| 302 | 댐퍼 4대 공통 명령(1=열기, 0=닫기) (`FWU_SAD-1_4_COMMAND`) = 1 **그리고** 팬 운전 상태 (`VP_FWU_SF_Status`) = 0이면 : |
| 303 | &emsp;→&nbsp;댐퍼 닫힘 대기 타이머(번호 8)를 0초로 초기화 |
| 304 | &emsp;→&nbsp;댐퍼 열림 대기 타이머(번호 7) 경과시간이 120초 초과하면 : |
| 305 | &emsp;&emsp;→&nbsp;댐퍼 1~4번 중 열림 접점이 1이 아닌 것이 하나라도 있으면 : |
| 306 | &emsp;&emsp;&emsp;→&nbsp;댐퍼 열림 실패 알람 (`VP_FWU_SAD_Not_Open_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 307 | &emsp;&emsp;→&nbsp;305행 조건이 성립하지 않으면 : |
| 308 | &emsp;&emsp;&emsp;→&nbsp;댐퍼 열림 실패 알람 (`VP_FWU_SAD_Not_Open_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 309 | &emsp;→&nbsp;304행 조건이 성립하지 않으면 : |
| 310 | &emsp;&emsp;→&nbsp;댐퍼 열림 실패 알람 (`VP_FWU_SAD_Not_Open_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 311 | 302행 조건이 성립하지 않으면 : |
| 312 | &emsp;→&nbsp;댐퍼 열림 실패 알람 (`VP_FWU_SAD_Not_Open_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 313 | &emsp;→&nbsp;댐퍼 열림 대기 타이머(번호 7)를 0초로 초기화 |

<a id="section-10"></a>

## 315~328행 · 댐퍼 닫힘 실패

> 닫기 명령 후 120초 초과해도 닫힘 접점이 안 들어오면 알람

| 행 | 해석 |
|---:|---|
| 315 | 댐퍼 4대 공통 명령(1=열기, 0=닫기) (`FWU_SAD-1_4_COMMAND`) = 0이면 : |
| 316 | &emsp;→&nbsp;댐퍼 열림 대기 타이머(번호 7)를 0초로 초기화 |
| 317 | &emsp;→&nbsp;댐퍼 닫힘 대기 타이머(번호 8) 경과시간이 120초 초과하면 : |
| 318 | &emsp;&emsp;→&nbsp;댐퍼 1~4번 중 닫힘 접점이 1이 아닌 것이 하나라도 있으면 : |
| 319 | &emsp;&emsp;&emsp;→&nbsp;댐퍼 닫힘 실패 알람 (`VP_FWU_SAD_Not_Close_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 320 | &emsp;&emsp;→&nbsp;318행 조건이 성립하지 않으면 : |
| 321 | &emsp;&emsp;&emsp;→&nbsp;댐퍼 닫힘 실패 알람 (`VP_FWU_SAD_Not_Close_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 322 | &emsp;→&nbsp;317행 조건이 성립하지 않으면 : |
| 323 | &emsp;&emsp;→&nbsp;댐퍼 닫힘 실패 알람 (`VP_FWU_SAD_Not_Close_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 324 | 315행 조건이 성립하지 않으면 : |
| 325 | &emsp;→&nbsp;댐퍼 닫힘 실패 알람 (`VP_FWU_SAD_Not_Close_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |
| 326 | &emsp;→&nbsp;댐퍼 닫힘 대기 타이머(번호 8)를 0초로 초기화 |
| 328 | *[주석] LJH[2026.1117]내부 센서 유효성 및 팬·댐퍼 알람* |

## 읽을 때 짚어둘 점

- **※** 팬 고장 60초는 각 팬의 이상이 60초 지속됐다는 뜻이 아니다. 운전 명령과 최소 속도 조건으로 감시 시작을 지연한다.
- **※** 통신이 끊긴 팬은 공통 차압으로 대체 판정한다. 공통 차압 하나만으로 개별 팬 상태를 정확히 구분할 수는 없다.
- **※** 현재 FAN_COUNT=8이므로 4대 이상 고장이면 종합 고장이다. 알람을 만드는 블록이며 Failover 정지 명령은 별도 블록에서 처리한다.
- **※** 온도는 0℃ 이상, 습도는 5%RH 이상이면 여기서는 유효로 본다. 실제 센서의 모든 고장 형태를 판별한다는 뜻은 아니다.
