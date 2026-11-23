# Sensor Limit Alarm 줄별 해석

> **대상 코드** : `fwu_v3/Logic/Sensor Limit Alarm.py` (283 줄)  
> **기준** : `sy 브랜치 2026-11-23 (naming rule·관제점 이름 변경 반영)`  
> **행** = 코드 줄 번호 (빈 줄은 생략)  
> **표기** : `→` 들여쓰기 단계 · *[주석]* 코드 안 주석 · `이름` 코드 안 상수·변수 · **※** 읽을 때 주의할 점

내부 센서(RAT·RAH·SAT·SAH)와 외부 센서 집계값(CZT·HZT·RDP)의 상·하한 알람, 내부 센서 고장, FMS 고장을 판단한다. 기존 Alarm-1에서 떼어 만든 파일이다.

**목차**

- [1~30행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수](#section-1)
- [32~56행 · 측정값을 믿을 수 없으면 고장으로 확정되기 전이라도 상·하한 알람은 바로 끈다](#section-2)
- [58~211행 · 상·하한 알람: 팬이 돌고 300초가 지난 뒤부터 본다. 해제는 히스테리시스만큼 돌아와야 한다](#section-3)
- [213~231행 · 팬이 서면 시작 지연 타이머와 상·하한 알람을 모두 푼다](#section-4)
- [233~268행 · 내부 센서 고장: 측정값이 유효 범위 밖에 20초 넘게 있으면 고장](#section-5)
- [270~283행 · FMS(풍량 차압 센서) 고장: 팬은 충분히 도는데(최대 RPM > 기준) 급기 차압이 기준보다 낮으면 고장으로 본다](#section-6)

**※ 공통 표기**: 매크로 상수 TRUE·ON·SET·TMR_READ·DEC = 1, FALSE·OFF·CLEAR·TMR_CLEAR·INC = 0. `SECTIMER(타이머, TMR_CLEAR)`는 타이머를 0초로 초기화, `SECTIMER(타이머, TMR_READ)`는 경과시간 확인이다. P번호가 없는 쓰기(`WRITEPOINT`)는 기본 우선순위 P5를 쓴다. 조건이 거짓이라고 관제점이 저절로 0이 되지는 않는다. 해당 분기에 쓰기가 없으면 이전 값이 남는다. 대문자 이름은 상수, `m`으로 시작하는 이름은 이 파일의 전역변수, `b`가 붙은 이름은 참/거짓 값이다.

<a id="section-1"></a>

## 1~30행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수

| 행 | 해석 |
|---:|---|
| 1 | *[주석] JSY 2026-11-23 수정 구간 시작. 주제 = Alarm-1에서 상·하한 알람과 센서 고장 알람을 떼어 만듦, Coding Rule 적용* |
| 3 | *[주석] 로직엔진 loading* |
| 4 | DDC 로직 엔진 객체 생성 (이후 engine.xxx로 관제점을 읽고 씀) |
| 6 | *[주석] Macro상수 정의* |
| 7 | 매크로 상수 정의: TMR_READ, SET, ON, TRUE, DEC = 1 (긍정의 의미 또는 1인 인자) |
| 8 | 매크로 상수 정의: TMR_CLEAR, CLEAR, OFF, FALSE, INC = 0 (부정의 의미 또는 0인 인자) |
| 9 | 상수 `LIMIT_START_SECONDS` = 300<br>*[주석] 팬이 돈 뒤 300초 동안은 상·하한 알람을 보지 않는다 (기동 직후 흔들림)* |
| 10 | 상수 `SENSOR_FAIL_CONFIRM_SECONDS` = 20<br>*[주석] 센서값이 유효 범위 밖으로 20초 넘게 있으면 센서 고장* |
| 11 | 상수 `FMS_FAIL_CONFIRM_SECONDS` = 20<br>*[주석] 팬은 도는데 차압이 낮은 상태가 20초 넘게 이어지면 FMS 고장* |
| 12 | 상수 `TEMPERATURE_VALID_MIN` = 0<br>*[주석] 온도가 0℃ 미만이면 측정값을 믿지 않는다* |
| 13 | 상수 `HUMIDITY_VALID_MIN` = 5<br>*[주석] 습도가 5% 미만이면 측정값을 믿지 않는다* |
| 14 | 상수 `PRESSURE_HYSTERESIS` = 0.5<br>*[주석] 차압 알람 해제 폭 (Pa)* |
| 15 | 상수 `TEMPERATURE_HYSTERESIS` = 0.5<br>*[주석] 온도 알람 해제 폭 (℃)* |
| 16 | 상수 `HUMIDITY_HYSTERESIS` = 5<br>*[주석] 습도 알람 해제 폭 (%)* |
| 18 | *[주석] 타이머 정의 (번호는 Alarm-1에서 쓰던 그대로)* |
| 19 | 타이머 번호 상수 `LIMIT_TIMER` = 0번<br>*[주석] 팬이 돌기 시작한 뒤 지난 시간 (상·하한 알람 시작 지연)* |
| 20 | 타이머 번호 상수 `SAT_FAIL_TIMER` = 2번<br>*[주석] SAT 값이 유효 범위 밖에 있던 시간* |
| 21 | 타이머 번호 상수 `SAH_FAIL_TIMER` = 3번<br>*[주석] SAH 값이 유효 범위 밖에 있던 시간* |
| 22 | 타이머 번호 상수 `RAT_FAIL_TIMER` = 4번<br>*[주석] RAT 값이 유효 범위 밖에 있던 시간* |
| 23 | 타이머 번호 상수 `RAH_FAIL_TIMER` = 5번<br>*[주석] RAH 값이 유효 범위 밖에 있던 시간* |
| 24 | 타이머 번호 상수 `SAF_FAIL_TIMER` = 6번<br>*[주석] 팬은 도는데 급기 차압이 낮았던 시간 (FMS 고장 판단)* |
| 26 | *[주석] 전역변수 선언: 내부 센서값을 믿을 수 있는지* |
| 27 | 전역변수 `mbRATValid` ← 환기 온도(RAT) 센서값 (`FWU_RAT`) ≥ `TEMPERATURE_VALID_MIN`(0) 이면 TRUE, 아니면 FALSE |
| 28 | 전역변수 `mbRAHValid` ← 환기 습도(RAH) 센서값 (`FWU_RAH`) ≥ `HUMIDITY_VALID_MIN`(5) 이면 TRUE, 아니면 FALSE |
| 29 | 전역변수 `mbSATValid` ← 급기 온도(SAT) 센서값 (`FWU_SAT`) ≥ `TEMPERATURE_VALID_MIN`(0) 이면 TRUE, 아니면 FALSE |
| 30 | 전역변수 `mbSAHValid` ← 급기 습도(SAH) 센서값 (`FWU_SAH`) ≥ `HUMIDITY_VALID_MIN`(5) 이면 TRUE, 아니면 FALSE |

<a id="section-2"></a>

## 32~56행 · 측정값을 믿을 수 없으면 고장으로 확정되기 전이라도 상·하한 알람은 바로 끈다

> HMI에서도 이 구간은 정상 측정으로 보이지 않게 할 것

| 행 | 해석 |
|---:|---|
| 32 | *[주석] 측정값을 믿을 수 없으면 고장으로 확정되기 전이라도 상·하한 알람은 바로 끈다* |
| 33 | *[주석] HMI에서도 이 구간은 정상 측정으로 보이지 않게 할 것* |
| 34 | `mbRATValid` = TRUE(1) 이면 : |
| 35 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 36 | 34행 조건이 성립하지 않으면 : |
| 37 | &emsp;→&nbsp;환기 온도(RAT) 상한 알람 (`VP_FWU_RAT_High_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 38 | &emsp;→&nbsp;환기 온도(RAT) 하한 알람 (`VP_FWU_RAT_Low_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 40 | `mbRAHValid` = TRUE(1) 이면 : |
| 41 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 42 | 40행 조건이 성립하지 않으면 : |
| 43 | &emsp;→&nbsp;환기 습도(RAH) 상한 알람 (`VP_FWU_RAH_High_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 44 | &emsp;→&nbsp;환기 습도(RAH) 하한 알람 (`VP_FWU_RAH_Low_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 46 | `mbSATValid` = TRUE(1) 이면 : |
| 47 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 48 | 46행 조건이 성립하지 않으면 : |
| 49 | &emsp;→&nbsp;급기 온도(SAT) 상한 알람 (`VP_FWU_SAT_High_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 50 | &emsp;→&nbsp;급기 온도(SAT) 하한 알람 (`VP_FWU_SAT_Low_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 52 | `mbSAHValid` = TRUE(1) 이면 : |
| 53 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 54 | 52행 조건이 성립하지 않으면 : |
| 55 | &emsp;→&nbsp;급기 습도(SAH) 상한 알람 (`VP_FWU_SAH_High_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 56 | &emsp;→&nbsp;급기 습도(SAH) 하한 알람 (`VP_FWU_SAH_Low_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |

<a id="section-3"></a>

## 58~211행 · 상·하한 알람: 팬이 돌고 300초가 지난 뒤부터 본다. 해제는 히스테리시스만큼 돌아와야 한다

| 행 | 해석 |
|---:|---|
| 58 | *[주석] 상·하한 알람: 팬이 돌고 300초가 지난 뒤부터 본다. 해제는 히스테리시스만큼 돌아와야 한다* |
| 59 | 팬 운전 상태 (`VP_FWU_SF_Status`) = ON(1) **그리고** 타이머 `LIMIT_TIMER`(0번: 팬이 돌기 시작한 뒤 지난 시간 (상·하한 알람 시작 지연)) 경과시간 > `LIMIT_START_SECONDS`(300) 이면 : |
| 60 | &emsp;→&nbsp;`mbRATValid` = TRUE(1) 이면 : |
| 61 | &emsp;&emsp;→&nbsp;환기 온도(RAT) 센서값 (`FWU_RAT`) > 환기 온도(RAT) 상한 알람 설정값 (`VP_FWU_RAT_High_Alarm_SP`) 이면 : |
| 62 | &emsp;&emsp;&emsp;→&nbsp;환기 온도(RAT) 상한 알람 (`VP_FWU_RAT_High_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 63 | &emsp;&emsp;→&nbsp;61행 조건이 성립하지 않으면 : |
| 64 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 65 | &emsp;&emsp;→&nbsp;환기 온도(RAT) 센서값 (`FWU_RAT`) < 환기 온도(RAT) 상한 알람 설정값 (`VP_FWU_RAT_High_Alarm_SP`) - `TEMPERATURE_HYSTERESIS`(0.5) 이면 : |
| 66 | &emsp;&emsp;&emsp;→&nbsp;환기 온도(RAT) 상한 알람 (`VP_FWU_RAT_High_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 67 | &emsp;&emsp;→&nbsp;65행 조건이 성립하지 않으면 : |
| 68 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 70 | &emsp;&emsp;→&nbsp;환기 온도(RAT) 센서값 (`FWU_RAT`) < 환기 온도(RAT) 하한 알람 설정값 (`VP_FWU_RAT_Low_Alarm_SP`) 이면 : |
| 71 | &emsp;&emsp;&emsp;→&nbsp;환기 온도(RAT) 하한 알람 (`VP_FWU_RAT_Low_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 72 | &emsp;&emsp;→&nbsp;70행 조건이 성립하지 않으면 : |
| 73 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 74 | &emsp;&emsp;→&nbsp;환기 온도(RAT) 센서값 (`FWU_RAT`) > 환기 온도(RAT) 하한 알람 설정값 (`VP_FWU_RAT_Low_Alarm_SP`) + `TEMPERATURE_HYSTERESIS`(0.5) 이면 : |
| 75 | &emsp;&emsp;&emsp;→&nbsp;환기 온도(RAT) 하한 알람 (`VP_FWU_RAT_Low_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 76 | &emsp;&emsp;→&nbsp;74행 조건이 성립하지 않으면 : |
| 77 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 78 | &emsp;→&nbsp;60행 조건이 성립하지 않으면 : |
| 79 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 81 | &emsp;→&nbsp;`mbRAHValid` = TRUE(1) 이면 : |
| 82 | &emsp;&emsp;→&nbsp;환기 습도(RAH) 센서값 (`FWU_RAH`) > 환기 습도(RAH) 상한 알람 설정값 (`VP_FWU_RAH_High_Alarm_SP`) 이면 : |
| 83 | &emsp;&emsp;&emsp;→&nbsp;환기 습도(RAH) 상한 알람 (`VP_FWU_RAH_High_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 84 | &emsp;&emsp;→&nbsp;82행 조건이 성립하지 않으면 : |
| 85 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 86 | &emsp;&emsp;→&nbsp;환기 습도(RAH) 센서값 (`FWU_RAH`) < 환기 습도(RAH) 상한 알람 설정값 (`VP_FWU_RAH_High_Alarm_SP`) - `HUMIDITY_HYSTERESIS`(5) 이면 : |
| 87 | &emsp;&emsp;&emsp;→&nbsp;환기 습도(RAH) 상한 알람 (`VP_FWU_RAH_High_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 88 | &emsp;&emsp;→&nbsp;86행 조건이 성립하지 않으면 : |
| 89 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 91 | &emsp;&emsp;→&nbsp;환기 습도(RAH) 센서값 (`FWU_RAH`) < 환기 습도(RAH) 하한 알람 설정값 (`VP_FWU_RAH_Low_Alarm_SP`) 이면 : |
| 92 | &emsp;&emsp;&emsp;→&nbsp;환기 습도(RAH) 하한 알람 (`VP_FWU_RAH_Low_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 93 | &emsp;&emsp;→&nbsp;91행 조건이 성립하지 않으면 : |
| 94 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 95 | &emsp;&emsp;→&nbsp;환기 습도(RAH) 센서값 (`FWU_RAH`) > 환기 습도(RAH) 하한 알람 설정값 (`VP_FWU_RAH_Low_Alarm_SP`) + `HUMIDITY_HYSTERESIS`(5) 이면 : |
| 96 | &emsp;&emsp;&emsp;→&nbsp;환기 습도(RAH) 하한 알람 (`VP_FWU_RAH_Low_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 97 | &emsp;&emsp;→&nbsp;95행 조건이 성립하지 않으면 : |
| 98 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 99 | &emsp;→&nbsp;81행 조건이 성립하지 않으면 : |
| 100 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 102 | &emsp;→&nbsp;`mbSATValid` = TRUE(1) 이면 : |
| 103 | &emsp;&emsp;→&nbsp;급기 온도(SAT) 센서값 (`FWU_SAT`) > 급기 온도(SAT) 상한 알람 설정값 (`VP_FWU_SAT_High_Alarm_SP`) 이면 : |
| 104 | &emsp;&emsp;&emsp;→&nbsp;급기 온도(SAT) 상한 알람 (`VP_FWU_SAT_High_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 105 | &emsp;&emsp;→&nbsp;103행 조건이 성립하지 않으면 : |
| 106 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 107 | &emsp;&emsp;→&nbsp;급기 온도(SAT) 센서값 (`FWU_SAT`) < 급기 온도(SAT) 상한 알람 설정값 (`VP_FWU_SAT_High_Alarm_SP`) - `TEMPERATURE_HYSTERESIS`(0.5) 이면 : |
| 108 | &emsp;&emsp;&emsp;→&nbsp;급기 온도(SAT) 상한 알람 (`VP_FWU_SAT_High_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 109 | &emsp;&emsp;→&nbsp;107행 조건이 성립하지 않으면 : |
| 110 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 112 | &emsp;&emsp;→&nbsp;급기 온도(SAT) 센서값 (`FWU_SAT`) < 급기 온도(SAT) 하한 알람 설정값 (`VP_FWU_SAT_Low_Alarm_SP`) 이면 : |
| 113 | &emsp;&emsp;&emsp;→&nbsp;급기 온도(SAT) 하한 알람 (`VP_FWU_SAT_Low_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 114 | &emsp;&emsp;→&nbsp;112행 조건이 성립하지 않으면 : |
| 115 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 116 | &emsp;&emsp;→&nbsp;급기 온도(SAT) 센서값 (`FWU_SAT`) > 급기 온도(SAT) 하한 알람 설정값 (`VP_FWU_SAT_Low_Alarm_SP`) + `TEMPERATURE_HYSTERESIS`(0.5) 이면 : |
| 117 | &emsp;&emsp;&emsp;→&nbsp;급기 온도(SAT) 하한 알람 (`VP_FWU_SAT_Low_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 118 | &emsp;&emsp;→&nbsp;116행 조건이 성립하지 않으면 : |
| 119 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 120 | &emsp;→&nbsp;102행 조건이 성립하지 않으면 : |
| 121 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 123 | &emsp;→&nbsp;`mbSAHValid` = TRUE(1) 이면 : |
| 124 | &emsp;&emsp;→&nbsp;급기 습도(SAH) 센서값 (`FWU_SAH`) > 급기 습도(SAH) 상한 알람 설정값 (`VP_FWU_SAH_High_Alarm_SP`) 이면 : |
| 125 | &emsp;&emsp;&emsp;→&nbsp;급기 습도(SAH) 상한 알람 (`VP_FWU_SAH_High_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 126 | &emsp;&emsp;→&nbsp;124행 조건이 성립하지 않으면 : |
| 127 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 128 | &emsp;&emsp;→&nbsp;급기 습도(SAH) 센서값 (`FWU_SAH`) < 급기 습도(SAH) 상한 알람 설정값 (`VP_FWU_SAH_High_Alarm_SP`) - `HUMIDITY_HYSTERESIS`(5) 이면 : |
| 129 | &emsp;&emsp;&emsp;→&nbsp;급기 습도(SAH) 상한 알람 (`VP_FWU_SAH_High_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 130 | &emsp;&emsp;→&nbsp;128행 조건이 성립하지 않으면 : |
| 131 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 133 | &emsp;&emsp;→&nbsp;급기 습도(SAH) 센서값 (`FWU_SAH`) < 급기 습도(SAH) 하한 알람 설정값 (`VP_FWU_SAH_Low_Alarm_SP`) 이면 : |
| 134 | &emsp;&emsp;&emsp;→&nbsp;급기 습도(SAH) 하한 알람 (`VP_FWU_SAH_Low_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 135 | &emsp;&emsp;→&nbsp;133행 조건이 성립하지 않으면 : |
| 136 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 137 | &emsp;&emsp;→&nbsp;급기 습도(SAH) 센서값 (`FWU_SAH`) > 급기 습도(SAH) 하한 알람 설정값 (`VP_FWU_SAH_Low_Alarm_SP`) + `HUMIDITY_HYSTERESIS`(5) 이면 : |
| 138 | &emsp;&emsp;&emsp;→&nbsp;급기 습도(SAH) 하한 알람 (`VP_FWU_SAH_Low_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 139 | &emsp;&emsp;→&nbsp;137행 조건이 성립하지 않으면 : |
| 140 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 141 | &emsp;→&nbsp;123행 조건이 성립하지 않으면 : |
| 142 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 144 | &emsp;→&nbsp;*[주석] CZT: 고는 집계 최대값, 저는 집계 최소값으로 본다. 집계값이 무효면 알람을 끈다* |
| 145 | &emsp;→&nbsp;냉복도 온도 제어용 값 유효 표시 (`VP_FWU_CZT_PV_Valid`) = TRUE(1) 이면 : |
| 146 | &emsp;&emsp;→&nbsp;냉복도 온도 최대값 (`VP_FWU_CZT_Max`) > 냉복도 온도 상한 알람 설정값 (`VP_FWU_CZT_High_Alarm_SP`) 이면 : |
| 147 | &emsp;&emsp;&emsp;→&nbsp;냉복도 온도 상한 알람 (`VP_FWU_CZT_High_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 148 | &emsp;&emsp;→&nbsp;146행 조건이 성립하지 않으면 : |
| 149 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 150 | &emsp;&emsp;→&nbsp;냉복도 온도 최대값 (`VP_FWU_CZT_Max`) < 냉복도 온도 상한 알람 설정값 (`VP_FWU_CZT_High_Alarm_SP`) - `TEMPERATURE_HYSTERESIS`(0.5) 이면 : |
| 151 | &emsp;&emsp;&emsp;→&nbsp;냉복도 온도 상한 알람 (`VP_FWU_CZT_High_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 152 | &emsp;&emsp;→&nbsp;150행 조건이 성립하지 않으면 : |
| 153 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 154 | &emsp;&emsp;→&nbsp;냉복도 온도 최소값 (`VP_FWU_CZT_Min`) < 냉복도 온도 하한 알람 설정값 (`VP_FWU_CZT_Low_Alarm_SP`) 이면 : |
| 155 | &emsp;&emsp;&emsp;→&nbsp;냉복도 온도 하한 알람 (`VP_FWU_CZT_Low_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 156 | &emsp;&emsp;→&nbsp;154행 조건이 성립하지 않으면 : |
| 157 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 158 | &emsp;&emsp;→&nbsp;냉복도 온도 최소값 (`VP_FWU_CZT_Min`) > 냉복도 온도 하한 알람 설정값 (`VP_FWU_CZT_Low_Alarm_SP`) + `TEMPERATURE_HYSTERESIS`(0.5) 이면 : |
| 159 | &emsp;&emsp;&emsp;→&nbsp;냉복도 온도 하한 알람 (`VP_FWU_CZT_Low_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 160 | &emsp;&emsp;→&nbsp;158행 조건이 성립하지 않으면 : |
| 161 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 162 | &emsp;→&nbsp;145행 조건이 성립하지 않으면 : |
| 163 | &emsp;&emsp;→&nbsp;냉복도 온도 상한 알람 (`VP_FWU_CZT_High_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 164 | &emsp;&emsp;→&nbsp;냉복도 온도 하한 알람 (`VP_FWU_CZT_Low_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 166 | &emsp;→&nbsp;*[주석] HZT: 고는 집계 최대값, 저는 집계 최소값으로 본다. 집계값이 무효면 알람을 끈다* |
| 167 | &emsp;→&nbsp;열복도 온도 제어용 값 유효 표시 (`VP_FWU_HZT_PV_Valid`) = TRUE(1) 이면 : |
| 168 | &emsp;&emsp;→&nbsp;열복도 온도 최대값 (`VP_FWU_HZT_Max`) > 열복도 온도 상한 알람 설정값 (`VP_FWU_HZT_High_Alarm_SP`) 이면 : |
| 169 | &emsp;&emsp;&emsp;→&nbsp;열복도 온도 상한 알람 (`VP_FWU_HZT_High_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 170 | &emsp;&emsp;→&nbsp;168행 조건이 성립하지 않으면 : |
| 171 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 172 | &emsp;&emsp;→&nbsp;열복도 온도 최대값 (`VP_FWU_HZT_Max`) < 열복도 온도 상한 알람 설정값 (`VP_FWU_HZT_High_Alarm_SP`) - `TEMPERATURE_HYSTERESIS`(0.5) 이면 : |
| 173 | &emsp;&emsp;&emsp;→&nbsp;열복도 온도 상한 알람 (`VP_FWU_HZT_High_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 174 | &emsp;&emsp;→&nbsp;172행 조건이 성립하지 않으면 : |
| 175 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 176 | &emsp;&emsp;→&nbsp;열복도 온도 최소값 (`VP_FWU_HZT_Min`) < 열복도 온도 하한 알람 설정값 (`VP_FWU_HZT_Low_Alarm_SP`) 이면 : |
| 177 | &emsp;&emsp;&emsp;→&nbsp;열복도 온도 하한 알람 (`VP_FWU_HZT_Low_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 178 | &emsp;&emsp;→&nbsp;176행 조건이 성립하지 않으면 : |
| 179 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 180 | &emsp;&emsp;→&nbsp;열복도 온도 최소값 (`VP_FWU_HZT_Min`) > 열복도 온도 하한 알람 설정값 (`VP_FWU_HZT_Low_Alarm_SP`) + `TEMPERATURE_HYSTERESIS`(0.5) 이면 : |
| 181 | &emsp;&emsp;&emsp;→&nbsp;열복도 온도 하한 알람 (`VP_FWU_HZT_Low_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 182 | &emsp;&emsp;→&nbsp;180행 조건이 성립하지 않으면 : |
| 183 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 184 | &emsp;→&nbsp;167행 조건이 성립하지 않으면 : |
| 185 | &emsp;&emsp;→&nbsp;열복도 온도 상한 알람 (`VP_FWU_HZT_High_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 186 | &emsp;&emsp;→&nbsp;열복도 온도 하한 알람 (`VP_FWU_HZT_Low_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 188 | &emsp;→&nbsp;*[주석] RDP: 고는 집계 최대값, 저는 집계 최소값으로 본다. 집계값이 무효면 알람을 끈다* |
| 189 | &emsp;→&nbsp;룸 차압 제어용 값 유효 표시 (`VP_FWU_RDP_PV_Valid`) = TRUE(1) 이면 : |
| 190 | &emsp;&emsp;→&nbsp;룸 차압 최대값 (`VP_FWU_RDP_Max`) > 룸 차압 상한 알람 설정값 (`VP_FWU_RDP_High_Alarm_SP`) 이면 : |
| 191 | &emsp;&emsp;&emsp;→&nbsp;룸 차압 상한 알람 (`VP_FWU_RDP_High_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 192 | &emsp;&emsp;→&nbsp;190행 조건이 성립하지 않으면 : |
| 193 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 194 | &emsp;&emsp;→&nbsp;룸 차압 최대값 (`VP_FWU_RDP_Max`) < 룸 차압 상한 알람 설정값 (`VP_FWU_RDP_High_Alarm_SP`) - `PRESSURE_HYSTERESIS`(0.5) 이면 : |
| 195 | &emsp;&emsp;&emsp;→&nbsp;룸 차압 상한 알람 (`VP_FWU_RDP_High_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 196 | &emsp;&emsp;→&nbsp;194행 조건이 성립하지 않으면 : |
| 197 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 198 | &emsp;&emsp;→&nbsp;룸 차압 최소값 (`VP_FWU_RDP_Min`) < 룸 차압 하한 알람 설정값 (`VP_FWU_RDP_Low_Alarm_SP`) 이면 : |
| 199 | &emsp;&emsp;&emsp;→&nbsp;룸 차압 하한 알람 (`VP_FWU_RDP_Low_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 200 | &emsp;&emsp;→&nbsp;198행 조건이 성립하지 않으면 : |
| 201 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 202 | &emsp;&emsp;→&nbsp;룸 차압 최소값 (`VP_FWU_RDP_Min`) > 룸 차압 하한 알람 설정값 (`VP_FWU_RDP_Low_Alarm_SP`) + `PRESSURE_HYSTERESIS`(0.5) 이면 : |
| 203 | &emsp;&emsp;&emsp;→&nbsp;룸 차압 하한 알람 (`VP_FWU_RDP_Low_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 204 | &emsp;&emsp;→&nbsp;202행 조건이 성립하지 않으면 : |
| 205 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 206 | &emsp;→&nbsp;189행 조건이 성립하지 않으면 : |
| 207 | &emsp;&emsp;→&nbsp;룸 차압 상한 알람 (`VP_FWU_RDP_High_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 208 | &emsp;&emsp;→&nbsp;룸 차압 하한 알람 (`VP_FWU_RDP_Low_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 210 | 59행 조건이 성립하지 않으면 : |
| 211 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |

<a id="section-4"></a>

## 213~231행 · 팬이 서면 시작 지연 타이머와 상·하한 알람을 모두 푼다

| 행 | 해석 |
|---:|---|
| 213 | *[주석] 팬이 서면 시작 지연 타이머와 상·하한 알람을 모두 푼다* |
| 214 | 팬 운전 상태 (`VP_FWU_SF_Status`) = OFF(0) 이면 : |
| 215 | &emsp;→&nbsp;타이머 `LIMIT_TIMER`(0번: 팬이 돌기 시작한 뒤 지난 시간 (상·하한 알람 시작 지연))를 0초로 초기화 |
| 216 | &emsp;→&nbsp;환기 온도(RAT) 상한 알람 (`VP_FWU_RAT_High_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 217 | &emsp;→&nbsp;환기 온도(RAT) 하한 알람 (`VP_FWU_RAT_Low_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 218 | &emsp;→&nbsp;환기 습도(RAH) 상한 알람 (`VP_FWU_RAH_High_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 219 | &emsp;→&nbsp;환기 습도(RAH) 하한 알람 (`VP_FWU_RAH_Low_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 220 | &emsp;→&nbsp;급기 온도(SAT) 상한 알람 (`VP_FWU_SAT_High_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 221 | &emsp;→&nbsp;급기 온도(SAT) 하한 알람 (`VP_FWU_SAT_Low_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 222 | &emsp;→&nbsp;급기 습도(SAH) 상한 알람 (`VP_FWU_SAH_High_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 223 | &emsp;→&nbsp;급기 습도(SAH) 하한 알람 (`VP_FWU_SAH_Low_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 224 | &emsp;→&nbsp;냉복도 온도 상한 알람 (`VP_FWU_CZT_High_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 225 | &emsp;→&nbsp;냉복도 온도 하한 알람 (`VP_FWU_CZT_Low_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 226 | &emsp;→&nbsp;열복도 온도 상한 알람 (`VP_FWU_HZT_High_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 227 | &emsp;→&nbsp;열복도 온도 하한 알람 (`VP_FWU_HZT_Low_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 228 | &emsp;→&nbsp;룸 차압 상한 알람 (`VP_FWU_RDP_High_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 229 | &emsp;→&nbsp;룸 차압 하한 알람 (`VP_FWU_RDP_Low_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 230 | 214행 조건이 성립하지 않으면 : |
| 231 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |

<a id="section-5"></a>

## 233~268행 · 내부 센서 고장: 측정값이 유효 범위 밖에 20초 넘게 있으면 고장

| 행 | 해석 |
|---:|---|
| 233 | *[주석] 내부 센서 고장: 측정값이 유효 범위 밖에 20초 넘게 있으면 고장* |
| 234 | `mbSATValid` = TRUE(1) 이면 : |
| 235 | &emsp;→&nbsp;타이머 `SAT_FAIL_TIMER`(2번: SAT 값이 유효 범위 밖에 있던 시간)를 0초로 초기화 |
| 236 | &emsp;→&nbsp;급기 온도(SAT) 센서 고장 알람 (`VP_FWU_SAT_Failure_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 237 | 234행 조건이 성립하지 않으면 : |
| 238 | &emsp;→&nbsp;타이머 `SAT_FAIL_TIMER`(2번: SAT 값이 유효 범위 밖에 있던 시간) 경과시간 > `SENSOR_FAIL_CONFIRM_SECONDS`(20) 이면 : |
| 239 | &emsp;&emsp;→&nbsp;급기 온도(SAT) 센서 고장 알람 (`VP_FWU_SAT_Failure_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 240 | &emsp;→&nbsp;238행 조건이 성립하지 않으면 : |
| 241 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 243 | `mbSAHValid` = TRUE(1) 이면 : |
| 244 | &emsp;→&nbsp;타이머 `SAH_FAIL_TIMER`(3번: SAH 값이 유효 범위 밖에 있던 시간)를 0초로 초기화 |
| 245 | &emsp;→&nbsp;급기 습도(SAH) 센서 고장 알람 (`VP_FWU_SAH_Failure_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 246 | 243행 조건이 성립하지 않으면 : |
| 247 | &emsp;→&nbsp;타이머 `SAH_FAIL_TIMER`(3번: SAH 값이 유효 범위 밖에 있던 시간) 경과시간 > `SENSOR_FAIL_CONFIRM_SECONDS`(20) 이면 : |
| 248 | &emsp;&emsp;→&nbsp;급기 습도(SAH) 센서 고장 알람 (`VP_FWU_SAH_Failure_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 249 | &emsp;→&nbsp;247행 조건이 성립하지 않으면 : |
| 250 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 252 | `mbRATValid` = TRUE(1) 이면 : |
| 253 | &emsp;→&nbsp;타이머 `RAT_FAIL_TIMER`(4번: RAT 값이 유효 범위 밖에 있던 시간)를 0초로 초기화 |
| 254 | &emsp;→&nbsp;환기 온도(RAT) 센서 고장 알람 (`VP_FWU_RAT_Failure_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 255 | 252행 조건이 성립하지 않으면 : |
| 256 | &emsp;→&nbsp;타이머 `RAT_FAIL_TIMER`(4번: RAT 값이 유효 범위 밖에 있던 시간) 경과시간 > `SENSOR_FAIL_CONFIRM_SECONDS`(20) 이면 : |
| 257 | &emsp;&emsp;→&nbsp;환기 온도(RAT) 센서 고장 알람 (`VP_FWU_RAT_Failure_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 258 | &emsp;→&nbsp;256행 조건이 성립하지 않으면 : |
| 259 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 261 | `mbRAHValid` = TRUE(1) 이면 : |
| 262 | &emsp;→&nbsp;타이머 `RAH_FAIL_TIMER`(5번: RAH 값이 유효 범위 밖에 있던 시간)를 0초로 초기화 |
| 263 | &emsp;→&nbsp;환기 습도(RAH) 센서 고장 알람 (`VP_FWU_RAH_Failure_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 264 | 261행 조건이 성립하지 않으면 : |
| 265 | &emsp;→&nbsp;타이머 `RAH_FAIL_TIMER`(5번: RAH 값이 유효 범위 밖에 있던 시간) 경과시간 > `SENSOR_FAIL_CONFIRM_SECONDS`(20) 이면 : |
| 266 | &emsp;&emsp;→&nbsp;환기 습도(RAH) 센서 고장 알람 (`VP_FWU_RAH_Failure_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 267 | &emsp;→&nbsp;265행 조건이 성립하지 않으면 : |
| 268 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |

<a id="section-6"></a>

## 270~283행 · FMS(풍량 차압 센서) 고장: 팬은 충분히 도는데(최대 RPM > 기준) 급기 차압이 기준보다 낮으면 고장으로 본다

> RPM과 차압이 안 맞는 것만 보는 것이라, 실제 풍량 부족과 센서·배선 이상은 구분하지 못한다 (engine.MAX는 인자를 5개까지만 받아서 팬 1~4, 5~8로 나눠 구한 뒤 다시 비교한다)

| 행 | 해석 |
|---:|---|
| 270 | *[주석] FMS(풍량 차압 센서) 고장: 팬은 충분히 도는데(최대 RPM > 기준) 급기 차압이 기준보다 낮으면 고장으로 본다* |
| 271 | *[주석] RPM과 차압이 안 맞는 것만 보는 것이라, 실제 풍량 부족과 센서·배선 이상은 구분하지 못한다* |
| 272 | *[주석] (engine.MAX는 인자를 5개까지만 받아서 팬 1~4, 5~8로 나눠 구한 뒤 다시 비교한다)* |
| 273 | 급기 풍량 차압(FMS) (`FWU_SAFLOW_DP`) < FMS 고장 판단 차압 설정 (`VP_FWU_SAF_Fail_DP_Set`) **그리고** [[팬 1번 현재 RPM (`FWU_SF-1.Current_RPM`), 팬 2번 현재 RPM (`FWU_SF-2.Current_RPM`), 팬 3번 현재 RPM (`FWU_SF-3.Current_RPM`), 팬 4번 현재 RPM (`FWU_SF-4.Current_RPM`)] 중 최댓값, [팬 5번 현재 RPM (`FWU_SF-5.Current_RPM`), 팬 6번 현재 RPM (`FWU_SF-6.Current_RPM`), 팬 7번 현재 RPM (`FWU_SF-7.Current_RPM`), 팬 8번 현재 RPM (`FWU_SF-8.Current_RPM`)] 중 최댓값] 중 최댓값 > FMS 고장 판단 RPM 설정 (`VP_FWU_SAF_Fail_RPM_Set`) 이면 : |
| 274 | &emsp;→&nbsp;타이머 `SAF_FAIL_TIMER`(6번: 팬은 도는데 급기 차압이 낮았던 시간 (FMS 고장 판단)) 경과시간 > `FMS_FAIL_CONFIRM_SECONDS`(20) 이면 : |
| 275 | &emsp;&emsp;→&nbsp;FMS(풍량 차압 센서) 고장 알람 (`VP_FWU_SAF_Failure_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 276 | &emsp;→&nbsp;274행 조건이 성립하지 않으면 : |
| 277 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 278 | 273행 조건이 성립하지 않으면 : |
| 279 | &emsp;→&nbsp;타이머 `SAF_FAIL_TIMER`(6번: 팬은 도는데 급기 차압이 낮았던 시간 (FMS 고장 판단))를 0초로 초기화 |
| 280 | &emsp;→&nbsp;FMS(풍량 차압 센서) 고장 알람 (`VP_FWU_SAF_Failure_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 282 | *[주석] JSY 2026-11-23 수정 구간 끝. 주제 = Alarm-1에서 상·하한 알람과 센서 고장 알람을 떼어 만듦, Coding Rule 적용* |
| 283 | *[주석] LJH 2026-11-17 수정 표시. 주제 = 내부 센서 유효성 및 팬·댐퍼 알람* |
