# Sensor Limit Alarm 줄별 해석

> **대상 코드** : `fwu_v3/Logic/Sensor Limit Alarm.py` (283 줄)  
> **기준** : `sy 브랜치 2026-11-24 (댐퍼 설치 여부 설정 반영)`  
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

**※ 읽는 법**

- **[조건]** 줄은 조건이 맞을 때만 바로 아래 한 칸 더 들여쓴(→가 하나 더 붙은) 줄들을 실행한다. **[아니면]** 줄은 그 조건이 맞지 않을 때 실행하는 부분이다.
- 값은 [ ] 안에 적었다. TRUE·ON·SET·TMR_READ·DEC = 1, FALSE·OFF·CLEAR·TMR_CLEAR·INC = 0 이다. 0/1 값 옆 (= …)은 그 관제점에서 0/1이 뜻하는 상태다.
- **우선순위 칸**: 관제점 하나에 번호가 붙은 여러 칸이 있고, **숫자가 작은 칸의 값이 이긴다**. 1 = 비상정지, 2 = 원격·화재 정지, 5 = 일반 로직(번호 없이 쓰는 `WRITEPOINT`), 11 = 값 보관·정지 요청. 칸을 지우면(해제) 그다음 칸의 값이 적용된다.
- 조건이 맞지 않는다고 관제점이 저절로 0이 되지는 않는다. 그 분기에 쓰는 줄이 없으면 **이전 값이 그대로 남는다**.
- 타이머는 0으로 되돌린 순간부터 흐른 시간(초)을 잰다. 대문자 이름은 상수, `m`으로 시작하는 이름은 이 파일 전체에서 쓰는 변수, 이름에 `b`가 붙은 변수는 TRUE/FALSE 값이다.

<a id="section-1"></a>

## 1~30행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수

| 행 | 해석 |
|---:|---|
| 1 | *[주석] JSY 2026-11-23 수정 구간 시작. 주제 = Alarm-1에서 상·하한 알람과 센서 고장 알람을 떼어 만듦, Coding Rule 적용* |
| 3 | *[주석] 로직엔진 loading* |
| 4 | DDC 로직 엔진을 불러온다. 이 아래에서 `engine.READPOINT`(관제점 읽기), `engine.WRITEPOINT`(관제점 쓰기) 같은 기능을 이 이름으로 쓴다 |
| 6 | *[주석] Macro상수 정의* |
| 7 | 매크로 상수 정의: TMR_READ, SET, ON, TRUE, DEC를 모두 숫자 1으로 정한다. 코드에서 숫자 1 대신 뜻이 보이는 이름으로 쓰기 위한 것이다 (타이머 읽기·켜짐·참·DEC 방향처럼 '긍정' 또는 1을 뜻하는 인자) |
| 8 | 매크로 상수 정의: TMR_CLEAR, CLEAR, OFF, FALSE, INC를 모두 숫자 0으로 정한다. 코드에서 숫자 0 대신 뜻이 보이는 이름으로 쓰기 위한 것이다 (타이머 초기화·꺼짐·거짓·INC 방향처럼 '부정' 또는 0을 뜻하는 인자) |
| 9 | 상수 `LIMIT_START_SECONDS` = 300. 뜻: 팬이 돈 뒤 300초 동안은 상·하한 알람을 보지 않는다 (기동 직후 흔들림) |
| 10 | 상수 `SENSOR_FAIL_CONFIRM_SECONDS` = 20. 뜻: 센서값이 유효 범위 밖으로 20초 넘게 있으면 센서 고장 |
| 11 | 상수 `FMS_FAIL_CONFIRM_SECONDS` = 20. 뜻: 팬은 도는데 차압이 낮은 상태가 20초 넘게 이어지면 FMS 고장 |
| 12 | 상수 `TEMPERATURE_VALID_MIN` = 0. 뜻: 온도가 0℃ 미만이면 측정값을 믿지 않는다 |
| 13 | 상수 `HUMIDITY_VALID_MIN` = 5. 뜻: 습도가 5% 미만이면 측정값을 믿지 않는다 |
| 14 | 상수 `PRESSURE_HYSTERESIS` = 0.5. 뜻: 차압 알람 해제 폭 (Pa) |
| 15 | 상수 `TEMPERATURE_HYSTERESIS` = 0.5. 뜻: 온도 알람 해제 폭 (℃) |
| 16 | 상수 `HUMIDITY_HYSTERESIS` = 5. 뜻: 습도 알람 해제 폭 (%) |
| 18 | *[주석] 타이머 정의 (번호는 Alarm-1에서 쓰던 그대로)* |
| 19 | 타이머 번호에 이름 붙이기: `LIMIT_TIMER` = 타이머 0번. 이 타이머로 '팬이 돌기 시작한 뒤 지난 시간 (상·하한 알람 시작 지연)'을 잰다 (한 로직에서 타이머는 0~9번 10개까지) |
| 20 | 타이머 번호에 이름 붙이기: `SAT_FAIL_TIMER` = 타이머 2번. 이 타이머로 'SAT 값이 유효 범위 밖에 있던 시간'을 잰다 (한 로직에서 타이머는 0~9번 10개까지) |
| 21 | 타이머 번호에 이름 붙이기: `SAH_FAIL_TIMER` = 타이머 3번. 이 타이머로 'SAH 값이 유효 범위 밖에 있던 시간'을 잰다 (한 로직에서 타이머는 0~9번 10개까지) |
| 22 | 타이머 번호에 이름 붙이기: `RAT_FAIL_TIMER` = 타이머 4번. 이 타이머로 'RAT 값이 유효 범위 밖에 있던 시간'을 잰다 (한 로직에서 타이머는 0~9번 10개까지) |
| 23 | 타이머 번호에 이름 붙이기: `RAH_FAIL_TIMER` = 타이머 5번. 이 타이머로 'RAH 값이 유효 범위 밖에 있던 시간'을 잰다 (한 로직에서 타이머는 0~9번 10개까지) |
| 24 | 타이머 번호에 이름 붙이기: `SAF_FAIL_TIMER` = 타이머 6번. 이 타이머로 '팬은 도는데 급기 차압이 낮았던 시간 (FMS 고장 판단)'을 잰다 (한 로직에서 타이머는 0~9번 10개까지) |
| 26 | *[주석] 전역변수 선언: 내부 센서값을 믿을 수 있는지* |
| 27 | `mbRATValid`(RAT 센서값을 믿을 수 있는지, TRUE면 정상 범위)에 판단 결과를 넣는다: 환기 온도(RAT) 센서값 (`FWU_RAT`) 값이 [`TEMPERATURE_VALID_MIN`(= 0, 온도가 0℃ 미만이면 측정값을 믿지 않는다)] 이상<br>→ 맞으면 TRUE(1), 아니면 FALSE(0) |
| 28 | `mbRAHValid`(RAH 센서값을 믿을 수 있는지, TRUE면 정상 범위)에 판단 결과를 넣는다: 환기 습도(RAH) 센서값 (`FWU_RAH`) 값이 [`HUMIDITY_VALID_MIN`(= 5, 습도가 5% 미만이면 측정값을 믿지 않는다)] 이상<br>→ 맞으면 TRUE(1), 아니면 FALSE(0) |
| 29 | `mbSATValid`(SAT 센서값을 믿을 수 있는지, TRUE면 정상 범위)에 판단 결과를 넣는다: 급기 온도(SAT) 센서값 (`FWU_SAT`) 값이 [`TEMPERATURE_VALID_MIN`(= 0, 온도가 0℃ 미만이면 측정값을 믿지 않는다)] 이상<br>→ 맞으면 TRUE(1), 아니면 FALSE(0) |
| 30 | `mbSAHValid`(SAH 센서값을 믿을 수 있는지, TRUE면 정상 범위)에 판단 결과를 넣는다: 급기 습도(SAH) 센서값 (`FWU_SAH`) 값이 [`HUMIDITY_VALID_MIN`(= 5, 습도가 5% 미만이면 측정값을 믿지 않는다)] 이상<br>→ 맞으면 TRUE(1), 아니면 FALSE(0) |

<a id="section-2"></a>

## 32~56행 · 측정값을 믿을 수 없으면 고장으로 확정되기 전이라도 상·하한 알람은 바로 끈다

> HMI에서도 이 구간은 정상 측정으로 보이지 않게 할 것

| 행 | 해석 |
|---:|---|
| 32 | *[주석] 측정값을 믿을 수 없으면 고장으로 확정되기 전이라도 상·하한 알람은 바로 끈다* |
| 33 | *[주석] HMI에서도 이 구간은 정상 측정으로 보이지 않게 할 것* |
| 34 | **[조건]** `mbRATValid`(RAT 센서값을 믿을 수 있는지, TRUE면 정상 범위) 값이 [TRUE(1)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 35 | &emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 36 | **[아니면]** 34행 조건의 반대 상황, 즉 `mbRATValid`(RAT 센서값을 믿을 수 있는지, TRUE면 정상 범위) 값이 [TRUE(1)]이 아님<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 37 | &emsp;→&nbsp;환기 온도(RAT) 상한 알람 (`VP_FWU_RAT_High_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 38 | &emsp;→&nbsp;환기 온도(RAT) 하한 알람 (`VP_FWU_RAT_Low_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 40 | **[조건]** `mbRAHValid`(RAH 센서값을 믿을 수 있는지, TRUE면 정상 범위) 값이 [TRUE(1)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 41 | &emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 42 | **[아니면]** 40행 조건의 반대 상황, 즉 `mbRAHValid`(RAH 센서값을 믿을 수 있는지, TRUE면 정상 범위) 값이 [TRUE(1)]이 아님<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 43 | &emsp;→&nbsp;환기 습도(RAH) 상한 알람 (`VP_FWU_RAH_High_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 44 | &emsp;→&nbsp;환기 습도(RAH) 하한 알람 (`VP_FWU_RAH_Low_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 46 | **[조건]** `mbSATValid`(SAT 센서값을 믿을 수 있는지, TRUE면 정상 범위) 값이 [TRUE(1)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 47 | &emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 48 | **[아니면]** 46행 조건의 반대 상황, 즉 `mbSATValid`(SAT 센서값을 믿을 수 있는지, TRUE면 정상 범위) 값이 [TRUE(1)]이 아님<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 49 | &emsp;→&nbsp;급기 온도(SAT) 상한 알람 (`VP_FWU_SAT_High_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 50 | &emsp;→&nbsp;급기 온도(SAT) 하한 알람 (`VP_FWU_SAT_Low_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 52 | **[조건]** `mbSAHValid`(SAH 센서값을 믿을 수 있는지, TRUE면 정상 범위) 값이 [TRUE(1)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 53 | &emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 54 | **[아니면]** 52행 조건의 반대 상황, 즉 `mbSAHValid`(SAH 센서값을 믿을 수 있는지, TRUE면 정상 범위) 값이 [TRUE(1)]이 아님<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 55 | &emsp;→&nbsp;급기 습도(SAH) 상한 알람 (`VP_FWU_SAH_High_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 56 | &emsp;→&nbsp;급기 습도(SAH) 하한 알람 (`VP_FWU_SAH_Low_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |

<a id="section-3"></a>

## 58~211행 · 상·하한 알람: 팬이 돌고 300초가 지난 뒤부터 본다. 해제는 히스테리시스만큼 돌아와야 한다

| 행 | 해석 |
|---:|---|
| 58 | *[주석] 상·하한 알람: 팬이 돌고 300초가 지난 뒤부터 본다. 해제는 히스테리시스만큼 돌아와야 한다* |
| 59 | **[조건]** 다음이 **모두** 맞음<br>① 팬 운전 상태 (`VP_FWU_SF_Status`) 값이 [ON(1)]임 (= 팬이 한 대라도 돌고 있음)<br>② 타이머 0번 `LIMIT_TIMER`(팬이 돌기 시작한 뒤 지난 시간 (상·하한 알람 시작 지연))으로 잰 시간(초)이 [`LIMIT_START_SECONDS`(= 300, 팬이 돈 뒤 300초 동안은 상·하한 알람을 보지 않는다 (기동 직후 흔들림))]초보다 김<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 60 | &emsp;→&nbsp;**[조건]** `mbRATValid`(RAT 센서값을 믿을 수 있는지, TRUE면 정상 범위) 값이 [TRUE(1)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 61 | &emsp;&emsp;→&nbsp;**[조건]** 환기 온도(RAT) 센서값 (`FWU_RAT`) 값이 [환기 온도(RAT) 상한 알람 설정값 (`VP_FWU_RAT_High_Alarm_SP`)]보다 큼<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 62 | &emsp;&emsp;&emsp;→&nbsp;환기 온도(RAT) 상한 알람 (`VP_FWU_RAT_High_Alarm`)을 켠다 — 값 [TRUE(1)] (= 알람 걸림) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 63 | &emsp;&emsp;→&nbsp;**[아니면]** 61행 조건의 반대 상황, 즉 환기 온도(RAT) 센서값 (`FWU_RAT`) 값이 [환기 온도(RAT) 상한 알람 설정값 (`VP_FWU_RAT_High_Alarm_SP`)] 이하<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 64 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 65 | &emsp;&emsp;→&nbsp;**[조건]** 환기 온도(RAT) 센서값 (`FWU_RAT`) 값이 [환기 온도(RAT) 상한 알람 설정값 (`VP_FWU_RAT_High_Alarm_SP`) - `TEMPERATURE_HYSTERESIS`(= 0.5, 온도 알람 해제 폭 (℃))]보다 작음<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 66 | &emsp;&emsp;&emsp;→&nbsp;환기 온도(RAT) 상한 알람 (`VP_FWU_RAT_High_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 67 | &emsp;&emsp;→&nbsp;**[아니면]** 65행 조건의 반대 상황, 즉 환기 온도(RAT) 센서값 (`FWU_RAT`) 값이 [환기 온도(RAT) 상한 알람 설정값 (`VP_FWU_RAT_High_Alarm_SP`) - `TEMPERATURE_HYSTERESIS`(= 0.5, 온도 알람 해제 폭 (℃))] 이상<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 68 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 70 | &emsp;&emsp;→&nbsp;**[조건]** 환기 온도(RAT) 센서값 (`FWU_RAT`) 값이 [환기 온도(RAT) 하한 알람 설정값 (`VP_FWU_RAT_Low_Alarm_SP`)]보다 작음<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 71 | &emsp;&emsp;&emsp;→&nbsp;환기 온도(RAT) 하한 알람 (`VP_FWU_RAT_Low_Alarm`)을 켠다 — 값 [TRUE(1)] (= 알람 걸림) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 72 | &emsp;&emsp;→&nbsp;**[아니면]** 70행 조건의 반대 상황, 즉 환기 온도(RAT) 센서값 (`FWU_RAT`) 값이 [환기 온도(RAT) 하한 알람 설정값 (`VP_FWU_RAT_Low_Alarm_SP`)] 이상<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 73 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 74 | &emsp;&emsp;→&nbsp;**[조건]** 환기 온도(RAT) 센서값 (`FWU_RAT`) 값이 [환기 온도(RAT) 하한 알람 설정값 (`VP_FWU_RAT_Low_Alarm_SP`) + `TEMPERATURE_HYSTERESIS`(= 0.5, 온도 알람 해제 폭 (℃))]보다 큼<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 75 | &emsp;&emsp;&emsp;→&nbsp;환기 온도(RAT) 하한 알람 (`VP_FWU_RAT_Low_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 76 | &emsp;&emsp;→&nbsp;**[아니면]** 74행 조건의 반대 상황, 즉 환기 온도(RAT) 센서값 (`FWU_RAT`) 값이 [환기 온도(RAT) 하한 알람 설정값 (`VP_FWU_RAT_Low_Alarm_SP`) + `TEMPERATURE_HYSTERESIS`(= 0.5, 온도 알람 해제 폭 (℃))] 이하<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 77 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 78 | &emsp;→&nbsp;**[아니면]** 60행 조건의 반대 상황, 즉 `mbRATValid`(RAT 센서값을 믿을 수 있는지, TRUE면 정상 범위) 값이 [TRUE(1)]이 아님<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 79 | &emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 81 | &emsp;→&nbsp;**[조건]** `mbRAHValid`(RAH 센서값을 믿을 수 있는지, TRUE면 정상 범위) 값이 [TRUE(1)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 82 | &emsp;&emsp;→&nbsp;**[조건]** 환기 습도(RAH) 센서값 (`FWU_RAH`) 값이 [환기 습도(RAH) 상한 알람 설정값 (`VP_FWU_RAH_High_Alarm_SP`)]보다 큼<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 83 | &emsp;&emsp;&emsp;→&nbsp;환기 습도(RAH) 상한 알람 (`VP_FWU_RAH_High_Alarm`)을 켠다 — 값 [TRUE(1)] (= 알람 걸림) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 84 | &emsp;&emsp;→&nbsp;**[아니면]** 82행 조건의 반대 상황, 즉 환기 습도(RAH) 센서값 (`FWU_RAH`) 값이 [환기 습도(RAH) 상한 알람 설정값 (`VP_FWU_RAH_High_Alarm_SP`)] 이하<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 85 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 86 | &emsp;&emsp;→&nbsp;**[조건]** 환기 습도(RAH) 센서값 (`FWU_RAH`) 값이 [환기 습도(RAH) 상한 알람 설정값 (`VP_FWU_RAH_High_Alarm_SP`) - `HUMIDITY_HYSTERESIS`(= 5, 습도 알람 해제 폭 (%))]보다 작음<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 87 | &emsp;&emsp;&emsp;→&nbsp;환기 습도(RAH) 상한 알람 (`VP_FWU_RAH_High_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 88 | &emsp;&emsp;→&nbsp;**[아니면]** 86행 조건의 반대 상황, 즉 환기 습도(RAH) 센서값 (`FWU_RAH`) 값이 [환기 습도(RAH) 상한 알람 설정값 (`VP_FWU_RAH_High_Alarm_SP`) - `HUMIDITY_HYSTERESIS`(= 5, 습도 알람 해제 폭 (%))] 이상<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 89 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 91 | &emsp;&emsp;→&nbsp;**[조건]** 환기 습도(RAH) 센서값 (`FWU_RAH`) 값이 [환기 습도(RAH) 하한 알람 설정값 (`VP_FWU_RAH_Low_Alarm_SP`)]보다 작음<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 92 | &emsp;&emsp;&emsp;→&nbsp;환기 습도(RAH) 하한 알람 (`VP_FWU_RAH_Low_Alarm`)을 켠다 — 값 [TRUE(1)] (= 알람 걸림) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 93 | &emsp;&emsp;→&nbsp;**[아니면]** 91행 조건의 반대 상황, 즉 환기 습도(RAH) 센서값 (`FWU_RAH`) 값이 [환기 습도(RAH) 하한 알람 설정값 (`VP_FWU_RAH_Low_Alarm_SP`)] 이상<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 94 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 95 | &emsp;&emsp;→&nbsp;**[조건]** 환기 습도(RAH) 센서값 (`FWU_RAH`) 값이 [환기 습도(RAH) 하한 알람 설정값 (`VP_FWU_RAH_Low_Alarm_SP`) + `HUMIDITY_HYSTERESIS`(= 5, 습도 알람 해제 폭 (%))]보다 큼<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 96 | &emsp;&emsp;&emsp;→&nbsp;환기 습도(RAH) 하한 알람 (`VP_FWU_RAH_Low_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 97 | &emsp;&emsp;→&nbsp;**[아니면]** 95행 조건의 반대 상황, 즉 환기 습도(RAH) 센서값 (`FWU_RAH`) 값이 [환기 습도(RAH) 하한 알람 설정값 (`VP_FWU_RAH_Low_Alarm_SP`) + `HUMIDITY_HYSTERESIS`(= 5, 습도 알람 해제 폭 (%))] 이하<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 98 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 99 | &emsp;→&nbsp;**[아니면]** 81행 조건의 반대 상황, 즉 `mbRAHValid`(RAH 센서값을 믿을 수 있는지, TRUE면 정상 범위) 값이 [TRUE(1)]이 아님<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 100 | &emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 102 | &emsp;→&nbsp;**[조건]** `mbSATValid`(SAT 센서값을 믿을 수 있는지, TRUE면 정상 범위) 값이 [TRUE(1)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 103 | &emsp;&emsp;→&nbsp;**[조건]** 급기 온도(SAT) 센서값 (`FWU_SAT`) 값이 [급기 온도(SAT) 상한 알람 설정값 (`VP_FWU_SAT_High_Alarm_SP`)]보다 큼<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 104 | &emsp;&emsp;&emsp;→&nbsp;급기 온도(SAT) 상한 알람 (`VP_FWU_SAT_High_Alarm`)을 켠다 — 값 [TRUE(1)] (= 알람 걸림) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 105 | &emsp;&emsp;→&nbsp;**[아니면]** 103행 조건의 반대 상황, 즉 급기 온도(SAT) 센서값 (`FWU_SAT`) 값이 [급기 온도(SAT) 상한 알람 설정값 (`VP_FWU_SAT_High_Alarm_SP`)] 이하<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 106 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 107 | &emsp;&emsp;→&nbsp;**[조건]** 급기 온도(SAT) 센서값 (`FWU_SAT`) 값이 [급기 온도(SAT) 상한 알람 설정값 (`VP_FWU_SAT_High_Alarm_SP`) - `TEMPERATURE_HYSTERESIS`(= 0.5, 온도 알람 해제 폭 (℃))]보다 작음<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 108 | &emsp;&emsp;&emsp;→&nbsp;급기 온도(SAT) 상한 알람 (`VP_FWU_SAT_High_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 109 | &emsp;&emsp;→&nbsp;**[아니면]** 107행 조건의 반대 상황, 즉 급기 온도(SAT) 센서값 (`FWU_SAT`) 값이 [급기 온도(SAT) 상한 알람 설정값 (`VP_FWU_SAT_High_Alarm_SP`) - `TEMPERATURE_HYSTERESIS`(= 0.5, 온도 알람 해제 폭 (℃))] 이상<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 110 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 112 | &emsp;&emsp;→&nbsp;**[조건]** 급기 온도(SAT) 센서값 (`FWU_SAT`) 값이 [급기 온도(SAT) 하한 알람 설정값 (`VP_FWU_SAT_Low_Alarm_SP`)]보다 작음<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 113 | &emsp;&emsp;&emsp;→&nbsp;급기 온도(SAT) 하한 알람 (`VP_FWU_SAT_Low_Alarm`)을 켠다 — 값 [TRUE(1)] (= 알람 걸림) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 114 | &emsp;&emsp;→&nbsp;**[아니면]** 112행 조건의 반대 상황, 즉 급기 온도(SAT) 센서값 (`FWU_SAT`) 값이 [급기 온도(SAT) 하한 알람 설정값 (`VP_FWU_SAT_Low_Alarm_SP`)] 이상<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 115 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 116 | &emsp;&emsp;→&nbsp;**[조건]** 급기 온도(SAT) 센서값 (`FWU_SAT`) 값이 [급기 온도(SAT) 하한 알람 설정값 (`VP_FWU_SAT_Low_Alarm_SP`) + `TEMPERATURE_HYSTERESIS`(= 0.5, 온도 알람 해제 폭 (℃))]보다 큼<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 117 | &emsp;&emsp;&emsp;→&nbsp;급기 온도(SAT) 하한 알람 (`VP_FWU_SAT_Low_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 118 | &emsp;&emsp;→&nbsp;**[아니면]** 116행 조건의 반대 상황, 즉 급기 온도(SAT) 센서값 (`FWU_SAT`) 값이 [급기 온도(SAT) 하한 알람 설정값 (`VP_FWU_SAT_Low_Alarm_SP`) + `TEMPERATURE_HYSTERESIS`(= 0.5, 온도 알람 해제 폭 (℃))] 이하<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 119 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 120 | &emsp;→&nbsp;**[아니면]** 102행 조건의 반대 상황, 즉 `mbSATValid`(SAT 센서값을 믿을 수 있는지, TRUE면 정상 범위) 값이 [TRUE(1)]이 아님<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 121 | &emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 123 | &emsp;→&nbsp;**[조건]** `mbSAHValid`(SAH 센서값을 믿을 수 있는지, TRUE면 정상 범위) 값이 [TRUE(1)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 124 | &emsp;&emsp;→&nbsp;**[조건]** 급기 습도(SAH) 센서값 (`FWU_SAH`) 값이 [급기 습도(SAH) 상한 알람 설정값 (`VP_FWU_SAH_High_Alarm_SP`)]보다 큼<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 125 | &emsp;&emsp;&emsp;→&nbsp;급기 습도(SAH) 상한 알람 (`VP_FWU_SAH_High_Alarm`)을 켠다 — 값 [TRUE(1)] (= 알람 걸림) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 126 | &emsp;&emsp;→&nbsp;**[아니면]** 124행 조건의 반대 상황, 즉 급기 습도(SAH) 센서값 (`FWU_SAH`) 값이 [급기 습도(SAH) 상한 알람 설정값 (`VP_FWU_SAH_High_Alarm_SP`)] 이하<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 127 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 128 | &emsp;&emsp;→&nbsp;**[조건]** 급기 습도(SAH) 센서값 (`FWU_SAH`) 값이 [급기 습도(SAH) 상한 알람 설정값 (`VP_FWU_SAH_High_Alarm_SP`) - `HUMIDITY_HYSTERESIS`(= 5, 습도 알람 해제 폭 (%))]보다 작음<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 129 | &emsp;&emsp;&emsp;→&nbsp;급기 습도(SAH) 상한 알람 (`VP_FWU_SAH_High_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 130 | &emsp;&emsp;→&nbsp;**[아니면]** 128행 조건의 반대 상황, 즉 급기 습도(SAH) 센서값 (`FWU_SAH`) 값이 [급기 습도(SAH) 상한 알람 설정값 (`VP_FWU_SAH_High_Alarm_SP`) - `HUMIDITY_HYSTERESIS`(= 5, 습도 알람 해제 폭 (%))] 이상<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 131 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 133 | &emsp;&emsp;→&nbsp;**[조건]** 급기 습도(SAH) 센서값 (`FWU_SAH`) 값이 [급기 습도(SAH) 하한 알람 설정값 (`VP_FWU_SAH_Low_Alarm_SP`)]보다 작음<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 134 | &emsp;&emsp;&emsp;→&nbsp;급기 습도(SAH) 하한 알람 (`VP_FWU_SAH_Low_Alarm`)을 켠다 — 값 [TRUE(1)] (= 알람 걸림) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 135 | &emsp;&emsp;→&nbsp;**[아니면]** 133행 조건의 반대 상황, 즉 급기 습도(SAH) 센서값 (`FWU_SAH`) 값이 [급기 습도(SAH) 하한 알람 설정값 (`VP_FWU_SAH_Low_Alarm_SP`)] 이상<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 136 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 137 | &emsp;&emsp;→&nbsp;**[조건]** 급기 습도(SAH) 센서값 (`FWU_SAH`) 값이 [급기 습도(SAH) 하한 알람 설정값 (`VP_FWU_SAH_Low_Alarm_SP`) + `HUMIDITY_HYSTERESIS`(= 5, 습도 알람 해제 폭 (%))]보다 큼<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 138 | &emsp;&emsp;&emsp;→&nbsp;급기 습도(SAH) 하한 알람 (`VP_FWU_SAH_Low_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 139 | &emsp;&emsp;→&nbsp;**[아니면]** 137행 조건의 반대 상황, 즉 급기 습도(SAH) 센서값 (`FWU_SAH`) 값이 [급기 습도(SAH) 하한 알람 설정값 (`VP_FWU_SAH_Low_Alarm_SP`) + `HUMIDITY_HYSTERESIS`(= 5, 습도 알람 해제 폭 (%))] 이하<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 140 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 141 | &emsp;→&nbsp;**[아니면]** 123행 조건의 반대 상황, 즉 `mbSAHValid`(SAH 센서값을 믿을 수 있는지, TRUE면 정상 범위) 값이 [TRUE(1)]이 아님<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 142 | &emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 144 | &emsp;→&nbsp;*[주석] CZT: 고는 집계 최대값, 저는 집계 최소값으로 본다. 집계값이 무효면 알람을 끈다* |
| 145 | &emsp;→&nbsp;**[조건]** 냉복도 온도 제어용 값 유효 표시 (`VP_FWU_CZT_PV_Valid`) 값이 [TRUE(1)]임 (= 유효, 쓸 수 있음)<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 146 | &emsp;&emsp;→&nbsp;**[조건]** 냉복도 온도 최대값 (`VP_FWU_CZT_Max`) 값이 [냉복도 온도 상한 알람 설정값 (`VP_FWU_CZT_High_Alarm_SP`)]보다 큼<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 147 | &emsp;&emsp;&emsp;→&nbsp;냉복도 온도 상한 알람 (`VP_FWU_CZT_High_Alarm`)을 켠다 — 값 [TRUE(1)] (= 알람 걸림) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 148 | &emsp;&emsp;→&nbsp;**[아니면]** 146행 조건의 반대 상황, 즉 냉복도 온도 최대값 (`VP_FWU_CZT_Max`) 값이 [냉복도 온도 상한 알람 설정값 (`VP_FWU_CZT_High_Alarm_SP`)] 이하<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 149 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 150 | &emsp;&emsp;→&nbsp;**[조건]** 냉복도 온도 최대값 (`VP_FWU_CZT_Max`) 값이 [냉복도 온도 상한 알람 설정값 (`VP_FWU_CZT_High_Alarm_SP`) - `TEMPERATURE_HYSTERESIS`(= 0.5, 온도 알람 해제 폭 (℃))]보다 작음<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 151 | &emsp;&emsp;&emsp;→&nbsp;냉복도 온도 상한 알람 (`VP_FWU_CZT_High_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 152 | &emsp;&emsp;→&nbsp;**[아니면]** 150행 조건의 반대 상황, 즉 냉복도 온도 최대값 (`VP_FWU_CZT_Max`) 값이 [냉복도 온도 상한 알람 설정값 (`VP_FWU_CZT_High_Alarm_SP`) - `TEMPERATURE_HYSTERESIS`(= 0.5, 온도 알람 해제 폭 (℃))] 이상<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 153 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 154 | &emsp;&emsp;→&nbsp;**[조건]** 냉복도 온도 최소값 (`VP_FWU_CZT_Min`) 값이 [냉복도 온도 하한 알람 설정값 (`VP_FWU_CZT_Low_Alarm_SP`)]보다 작음<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 155 | &emsp;&emsp;&emsp;→&nbsp;냉복도 온도 하한 알람 (`VP_FWU_CZT_Low_Alarm`)을 켠다 — 값 [TRUE(1)] (= 알람 걸림) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 156 | &emsp;&emsp;→&nbsp;**[아니면]** 154행 조건의 반대 상황, 즉 냉복도 온도 최소값 (`VP_FWU_CZT_Min`) 값이 [냉복도 온도 하한 알람 설정값 (`VP_FWU_CZT_Low_Alarm_SP`)] 이상<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 157 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 158 | &emsp;&emsp;→&nbsp;**[조건]** 냉복도 온도 최소값 (`VP_FWU_CZT_Min`) 값이 [냉복도 온도 하한 알람 설정값 (`VP_FWU_CZT_Low_Alarm_SP`) + `TEMPERATURE_HYSTERESIS`(= 0.5, 온도 알람 해제 폭 (℃))]보다 큼<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 159 | &emsp;&emsp;&emsp;→&nbsp;냉복도 온도 하한 알람 (`VP_FWU_CZT_Low_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 160 | &emsp;&emsp;→&nbsp;**[아니면]** 158행 조건의 반대 상황, 즉 냉복도 온도 최소값 (`VP_FWU_CZT_Min`) 값이 [냉복도 온도 하한 알람 설정값 (`VP_FWU_CZT_Low_Alarm_SP`) + `TEMPERATURE_HYSTERESIS`(= 0.5, 온도 알람 해제 폭 (℃))] 이하<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 161 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 162 | &emsp;→&nbsp;**[아니면]** 145행 조건의 반대 상황, 즉 냉복도 온도 제어용 값 유효 표시 (`VP_FWU_CZT_PV_Valid`) 값이 [TRUE(1)]이 아님 (= 무효, 쓸 수 없음)<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 163 | &emsp;&emsp;→&nbsp;냉복도 온도 상한 알람 (`VP_FWU_CZT_High_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 164 | &emsp;&emsp;→&nbsp;냉복도 온도 하한 알람 (`VP_FWU_CZT_Low_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 166 | &emsp;→&nbsp;*[주석] HZT: 고는 집계 최대값, 저는 집계 최소값으로 본다. 집계값이 무효면 알람을 끈다* |
| 167 | &emsp;→&nbsp;**[조건]** 열복도 온도 제어용 값 유효 표시 (`VP_FWU_HZT_PV_Valid`) 값이 [TRUE(1)]임 (= 유효, 쓸 수 있음)<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 168 | &emsp;&emsp;→&nbsp;**[조건]** 열복도 온도 최대값 (`VP_FWU_HZT_Max`) 값이 [열복도 온도 상한 알람 설정값 (`VP_FWU_HZT_High_Alarm_SP`)]보다 큼<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 169 | &emsp;&emsp;&emsp;→&nbsp;열복도 온도 상한 알람 (`VP_FWU_HZT_High_Alarm`)을 켠다 — 값 [TRUE(1)] (= 알람 걸림) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 170 | &emsp;&emsp;→&nbsp;**[아니면]** 168행 조건의 반대 상황, 즉 열복도 온도 최대값 (`VP_FWU_HZT_Max`) 값이 [열복도 온도 상한 알람 설정값 (`VP_FWU_HZT_High_Alarm_SP`)] 이하<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 171 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 172 | &emsp;&emsp;→&nbsp;**[조건]** 열복도 온도 최대값 (`VP_FWU_HZT_Max`) 값이 [열복도 온도 상한 알람 설정값 (`VP_FWU_HZT_High_Alarm_SP`) - `TEMPERATURE_HYSTERESIS`(= 0.5, 온도 알람 해제 폭 (℃))]보다 작음<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 173 | &emsp;&emsp;&emsp;→&nbsp;열복도 온도 상한 알람 (`VP_FWU_HZT_High_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 174 | &emsp;&emsp;→&nbsp;**[아니면]** 172행 조건의 반대 상황, 즉 열복도 온도 최대값 (`VP_FWU_HZT_Max`) 값이 [열복도 온도 상한 알람 설정값 (`VP_FWU_HZT_High_Alarm_SP`) - `TEMPERATURE_HYSTERESIS`(= 0.5, 온도 알람 해제 폭 (℃))] 이상<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 175 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 176 | &emsp;&emsp;→&nbsp;**[조건]** 열복도 온도 최소값 (`VP_FWU_HZT_Min`) 값이 [열복도 온도 하한 알람 설정값 (`VP_FWU_HZT_Low_Alarm_SP`)]보다 작음<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 177 | &emsp;&emsp;&emsp;→&nbsp;열복도 온도 하한 알람 (`VP_FWU_HZT_Low_Alarm`)을 켠다 — 값 [TRUE(1)] (= 알람 걸림) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 178 | &emsp;&emsp;→&nbsp;**[아니면]** 176행 조건의 반대 상황, 즉 열복도 온도 최소값 (`VP_FWU_HZT_Min`) 값이 [열복도 온도 하한 알람 설정값 (`VP_FWU_HZT_Low_Alarm_SP`)] 이상<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 179 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 180 | &emsp;&emsp;→&nbsp;**[조건]** 열복도 온도 최소값 (`VP_FWU_HZT_Min`) 값이 [열복도 온도 하한 알람 설정값 (`VP_FWU_HZT_Low_Alarm_SP`) + `TEMPERATURE_HYSTERESIS`(= 0.5, 온도 알람 해제 폭 (℃))]보다 큼<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 181 | &emsp;&emsp;&emsp;→&nbsp;열복도 온도 하한 알람 (`VP_FWU_HZT_Low_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 182 | &emsp;&emsp;→&nbsp;**[아니면]** 180행 조건의 반대 상황, 즉 열복도 온도 최소값 (`VP_FWU_HZT_Min`) 값이 [열복도 온도 하한 알람 설정값 (`VP_FWU_HZT_Low_Alarm_SP`) + `TEMPERATURE_HYSTERESIS`(= 0.5, 온도 알람 해제 폭 (℃))] 이하<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 183 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 184 | &emsp;→&nbsp;**[아니면]** 167행 조건의 반대 상황, 즉 열복도 온도 제어용 값 유효 표시 (`VP_FWU_HZT_PV_Valid`) 값이 [TRUE(1)]이 아님 (= 무효, 쓸 수 없음)<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 185 | &emsp;&emsp;→&nbsp;열복도 온도 상한 알람 (`VP_FWU_HZT_High_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 186 | &emsp;&emsp;→&nbsp;열복도 온도 하한 알람 (`VP_FWU_HZT_Low_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 188 | &emsp;→&nbsp;*[주석] RDP: 고는 집계 최대값, 저는 집계 최소값으로 본다. 집계값이 무효면 알람을 끈다* |
| 189 | &emsp;→&nbsp;**[조건]** 룸 차압 제어용 값 유효 표시 (`VP_FWU_RDP_PV_Valid`) 값이 [TRUE(1)]임 (= 유효, 쓸 수 있음)<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 190 | &emsp;&emsp;→&nbsp;**[조건]** 룸 차압 최대값 (`VP_FWU_RDP_Max`) 값이 [룸 차압 상한 알람 설정값 (`VP_FWU_RDP_High_Alarm_SP`)]보다 큼<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 191 | &emsp;&emsp;&emsp;→&nbsp;룸 차압 상한 알람 (`VP_FWU_RDP_High_Alarm`)을 켠다 — 값 [TRUE(1)] (= 알람 걸림) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 192 | &emsp;&emsp;→&nbsp;**[아니면]** 190행 조건의 반대 상황, 즉 룸 차압 최대값 (`VP_FWU_RDP_Max`) 값이 [룸 차압 상한 알람 설정값 (`VP_FWU_RDP_High_Alarm_SP`)] 이하<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 193 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 194 | &emsp;&emsp;→&nbsp;**[조건]** 룸 차압 최대값 (`VP_FWU_RDP_Max`) 값이 [룸 차압 상한 알람 설정값 (`VP_FWU_RDP_High_Alarm_SP`) - `PRESSURE_HYSTERESIS`(= 0.5, 차압 알람 해제 폭 (Pa))]보다 작음<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 195 | &emsp;&emsp;&emsp;→&nbsp;룸 차압 상한 알람 (`VP_FWU_RDP_High_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 196 | &emsp;&emsp;→&nbsp;**[아니면]** 194행 조건의 반대 상황, 즉 룸 차압 최대값 (`VP_FWU_RDP_Max`) 값이 [룸 차압 상한 알람 설정값 (`VP_FWU_RDP_High_Alarm_SP`) - `PRESSURE_HYSTERESIS`(= 0.5, 차압 알람 해제 폭 (Pa))] 이상<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 197 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 198 | &emsp;&emsp;→&nbsp;**[조건]** 룸 차압 최소값 (`VP_FWU_RDP_Min`) 값이 [룸 차압 하한 알람 설정값 (`VP_FWU_RDP_Low_Alarm_SP`)]보다 작음<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 199 | &emsp;&emsp;&emsp;→&nbsp;룸 차압 하한 알람 (`VP_FWU_RDP_Low_Alarm`)을 켠다 — 값 [TRUE(1)] (= 알람 걸림) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 200 | &emsp;&emsp;→&nbsp;**[아니면]** 198행 조건의 반대 상황, 즉 룸 차압 최소값 (`VP_FWU_RDP_Min`) 값이 [룸 차압 하한 알람 설정값 (`VP_FWU_RDP_Low_Alarm_SP`)] 이상<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 201 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 202 | &emsp;&emsp;→&nbsp;**[조건]** 룸 차압 최소값 (`VP_FWU_RDP_Min`) 값이 [룸 차압 하한 알람 설정값 (`VP_FWU_RDP_Low_Alarm_SP`) + `PRESSURE_HYSTERESIS`(= 0.5, 차압 알람 해제 폭 (Pa))]보다 큼<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 203 | &emsp;&emsp;&emsp;→&nbsp;룸 차압 하한 알람 (`VP_FWU_RDP_Low_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 204 | &emsp;&emsp;→&nbsp;**[아니면]** 202행 조건의 반대 상황, 즉 룸 차압 최소값 (`VP_FWU_RDP_Min`) 값이 [룸 차압 하한 알람 설정값 (`VP_FWU_RDP_Low_Alarm_SP`) + `PRESSURE_HYSTERESIS`(= 0.5, 차압 알람 해제 폭 (Pa))] 이하<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 205 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 206 | &emsp;→&nbsp;**[아니면]** 189행 조건의 반대 상황, 즉 룸 차압 제어용 값 유효 표시 (`VP_FWU_RDP_PV_Valid`) 값이 [TRUE(1)]이 아님 (= 무효, 쓸 수 없음)<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 207 | &emsp;&emsp;→&nbsp;룸 차압 상한 알람 (`VP_FWU_RDP_High_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 208 | &emsp;&emsp;→&nbsp;룸 차압 하한 알람 (`VP_FWU_RDP_Low_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 210 | **[아니면]** 59행 조건의 반대 상황, 즉 아래 조건 중 **하나라도 맞지 않음**<br>① 팬 운전 상태 (`VP_FWU_SF_Status`) 값이 [ON(1)]임 (= 팬이 한 대라도 돌고 있음)<br>② 타이머 0번 `LIMIT_TIMER`(팬이 돌기 시작한 뒤 지난 시간 (상·하한 알람 시작 지연))으로 잰 시간(초)이 [`LIMIT_START_SECONDS`(= 300, 팬이 돈 뒤 300초 동안은 상·하한 알람을 보지 않는다 (기동 직후 흔들림))]초보다 김<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 211 | &emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |

<a id="section-4"></a>

## 213~231행 · 팬이 서면 시작 지연 타이머와 상·하한 알람을 모두 푼다

| 행 | 해석 |
|---:|---|
| 213 | *[주석] 팬이 서면 시작 지연 타이머와 상·하한 알람을 모두 푼다* |
| 214 | **[조건]** 팬 운전 상태 (`VP_FWU_SF_Status`) 값이 [OFF(0)]임 (= 팬이 한 대도 안 돎)<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 215 | &emsp;→&nbsp;타이머 0번 `LIMIT_TIMER`(팬이 돌기 시작한 뒤 지난 시간 (상·하한 알람 시작 지연))를 0으로 되돌린다. 이 시점부터 시간을 새로 잰다 |
| 216 | &emsp;→&nbsp;환기 온도(RAT) 상한 알람 (`VP_FWU_RAT_High_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 217 | &emsp;→&nbsp;환기 온도(RAT) 하한 알람 (`VP_FWU_RAT_Low_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 218 | &emsp;→&nbsp;환기 습도(RAH) 상한 알람 (`VP_FWU_RAH_High_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 219 | &emsp;→&nbsp;환기 습도(RAH) 하한 알람 (`VP_FWU_RAH_Low_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 220 | &emsp;→&nbsp;급기 온도(SAT) 상한 알람 (`VP_FWU_SAT_High_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 221 | &emsp;→&nbsp;급기 온도(SAT) 하한 알람 (`VP_FWU_SAT_Low_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 222 | &emsp;→&nbsp;급기 습도(SAH) 상한 알람 (`VP_FWU_SAH_High_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 223 | &emsp;→&nbsp;급기 습도(SAH) 하한 알람 (`VP_FWU_SAH_Low_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 224 | &emsp;→&nbsp;냉복도 온도 상한 알람 (`VP_FWU_CZT_High_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 225 | &emsp;→&nbsp;냉복도 온도 하한 알람 (`VP_FWU_CZT_Low_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 226 | &emsp;→&nbsp;열복도 온도 상한 알람 (`VP_FWU_HZT_High_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 227 | &emsp;→&nbsp;열복도 온도 하한 알람 (`VP_FWU_HZT_Low_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 228 | &emsp;→&nbsp;룸 차압 상한 알람 (`VP_FWU_RDP_High_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 229 | &emsp;→&nbsp;룸 차압 하한 알람 (`VP_FWU_RDP_Low_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 230 | **[아니면]** 214행 조건의 반대 상황, 즉 팬 운전 상태 (`VP_FWU_SF_Status`) 값이 [OFF(0)]이 아님 (= 팬이 한 대라도 돌고 있음)<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 231 | &emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |

<a id="section-5"></a>

## 233~268행 · 내부 센서 고장: 측정값이 유효 범위 밖에 20초 넘게 있으면 고장

| 행 | 해석 |
|---:|---|
| 233 | *[주석] 내부 센서 고장: 측정값이 유효 범위 밖에 20초 넘게 있으면 고장* |
| 234 | **[조건]** `mbSATValid`(SAT 센서값을 믿을 수 있는지, TRUE면 정상 범위) 값이 [TRUE(1)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 235 | &emsp;→&nbsp;타이머 2번 `SAT_FAIL_TIMER`(SAT 값이 유효 범위 밖에 있던 시간)를 0으로 되돌린다. 이 시점부터 시간을 새로 잰다 |
| 236 | &emsp;→&nbsp;급기 온도(SAT) 센서 고장 알람 (`VP_FWU_SAT_Failure_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 237 | **[아니면]** 234행 조건의 반대 상황, 즉 `mbSATValid`(SAT 센서값을 믿을 수 있는지, TRUE면 정상 범위) 값이 [TRUE(1)]이 아님<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 238 | &emsp;→&nbsp;**[조건]** 타이머 2번 `SAT_FAIL_TIMER`(SAT 값이 유효 범위 밖에 있던 시간)으로 잰 시간(초)이 [`SENSOR_FAIL_CONFIRM_SECONDS`(= 20, 센서값이 유효 범위 밖으로 20초 넘게 있으면 센서 고장)]초보다 김<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 239 | &emsp;&emsp;→&nbsp;급기 온도(SAT) 센서 고장 알람 (`VP_FWU_SAT_Failure_Alarm`)을 켠다 — 값 [TRUE(1)] (= 알람 걸림) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 240 | &emsp;→&nbsp;**[아니면]** 238행 조건의 반대 상황, 즉 타이머 2번 `SAT_FAIL_TIMER`(SAT 값이 유효 범위 밖에 있던 시간)으로 잰 시간(초)이 아직 [`SENSOR_FAIL_CONFIRM_SECONDS`(= 20, 센서값이 유효 범위 밖으로 20초 넘게 있으면 센서 고장)]초를 넘지 않음<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 241 | &emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 243 | **[조건]** `mbSAHValid`(SAH 센서값을 믿을 수 있는지, TRUE면 정상 범위) 값이 [TRUE(1)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 244 | &emsp;→&nbsp;타이머 3번 `SAH_FAIL_TIMER`(SAH 값이 유효 범위 밖에 있던 시간)를 0으로 되돌린다. 이 시점부터 시간을 새로 잰다 |
| 245 | &emsp;→&nbsp;급기 습도(SAH) 센서 고장 알람 (`VP_FWU_SAH_Failure_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 246 | **[아니면]** 243행 조건의 반대 상황, 즉 `mbSAHValid`(SAH 센서값을 믿을 수 있는지, TRUE면 정상 범위) 값이 [TRUE(1)]이 아님<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 247 | &emsp;→&nbsp;**[조건]** 타이머 3번 `SAH_FAIL_TIMER`(SAH 값이 유효 범위 밖에 있던 시간)으로 잰 시간(초)이 [`SENSOR_FAIL_CONFIRM_SECONDS`(= 20, 센서값이 유효 범위 밖으로 20초 넘게 있으면 센서 고장)]초보다 김<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 248 | &emsp;&emsp;→&nbsp;급기 습도(SAH) 센서 고장 알람 (`VP_FWU_SAH_Failure_Alarm`)을 켠다 — 값 [TRUE(1)] (= 알람 걸림) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 249 | &emsp;→&nbsp;**[아니면]** 247행 조건의 반대 상황, 즉 타이머 3번 `SAH_FAIL_TIMER`(SAH 값이 유효 범위 밖에 있던 시간)으로 잰 시간(초)이 아직 [`SENSOR_FAIL_CONFIRM_SECONDS`(= 20, 센서값이 유효 범위 밖으로 20초 넘게 있으면 센서 고장)]초를 넘지 않음<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 250 | &emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 252 | **[조건]** `mbRATValid`(RAT 센서값을 믿을 수 있는지, TRUE면 정상 범위) 값이 [TRUE(1)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 253 | &emsp;→&nbsp;타이머 4번 `RAT_FAIL_TIMER`(RAT 값이 유효 범위 밖에 있던 시간)를 0으로 되돌린다. 이 시점부터 시간을 새로 잰다 |
| 254 | &emsp;→&nbsp;환기 온도(RAT) 센서 고장 알람 (`VP_FWU_RAT_Failure_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 255 | **[아니면]** 252행 조건의 반대 상황, 즉 `mbRATValid`(RAT 센서값을 믿을 수 있는지, TRUE면 정상 범위) 값이 [TRUE(1)]이 아님<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 256 | &emsp;→&nbsp;**[조건]** 타이머 4번 `RAT_FAIL_TIMER`(RAT 값이 유효 범위 밖에 있던 시간)으로 잰 시간(초)이 [`SENSOR_FAIL_CONFIRM_SECONDS`(= 20, 센서값이 유효 범위 밖으로 20초 넘게 있으면 센서 고장)]초보다 김<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 257 | &emsp;&emsp;→&nbsp;환기 온도(RAT) 센서 고장 알람 (`VP_FWU_RAT_Failure_Alarm`)을 켠다 — 값 [TRUE(1)] (= 알람 걸림) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 258 | &emsp;→&nbsp;**[아니면]** 256행 조건의 반대 상황, 즉 타이머 4번 `RAT_FAIL_TIMER`(RAT 값이 유효 범위 밖에 있던 시간)으로 잰 시간(초)이 아직 [`SENSOR_FAIL_CONFIRM_SECONDS`(= 20, 센서값이 유효 범위 밖으로 20초 넘게 있으면 센서 고장)]초를 넘지 않음<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 259 | &emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 261 | **[조건]** `mbRAHValid`(RAH 센서값을 믿을 수 있는지, TRUE면 정상 범위) 값이 [TRUE(1)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 262 | &emsp;→&nbsp;타이머 5번 `RAH_FAIL_TIMER`(RAH 값이 유효 범위 밖에 있던 시간)를 0으로 되돌린다. 이 시점부터 시간을 새로 잰다 |
| 263 | &emsp;→&nbsp;환기 습도(RAH) 센서 고장 알람 (`VP_FWU_RAH_Failure_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 264 | **[아니면]** 261행 조건의 반대 상황, 즉 `mbRAHValid`(RAH 센서값을 믿을 수 있는지, TRUE면 정상 범위) 값이 [TRUE(1)]이 아님<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 265 | &emsp;→&nbsp;**[조건]** 타이머 5번 `RAH_FAIL_TIMER`(RAH 값이 유효 범위 밖에 있던 시간)으로 잰 시간(초)이 [`SENSOR_FAIL_CONFIRM_SECONDS`(= 20, 센서값이 유효 범위 밖으로 20초 넘게 있으면 센서 고장)]초보다 김<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 266 | &emsp;&emsp;→&nbsp;환기 습도(RAH) 센서 고장 알람 (`VP_FWU_RAH_Failure_Alarm`)을 켠다 — 값 [TRUE(1)] (= 알람 걸림) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 267 | &emsp;→&nbsp;**[아니면]** 265행 조건의 반대 상황, 즉 타이머 5번 `RAH_FAIL_TIMER`(RAH 값이 유효 범위 밖에 있던 시간)으로 잰 시간(초)이 아직 [`SENSOR_FAIL_CONFIRM_SECONDS`(= 20, 센서값이 유효 범위 밖으로 20초 넘게 있으면 센서 고장)]초를 넘지 않음<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 268 | &emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |

<a id="section-6"></a>

## 270~283행 · FMS(풍량 차압 센서) 고장: 팬은 충분히 도는데(최대 RPM > 기준) 급기 차압이 기준보다 낮으면 고장으로 본다

> RPM과 차압이 안 맞는 것만 보는 것이라, 실제 풍량 부족과 센서·배선 이상은 구분하지 못한다 (engine.MAX는 인자를 5개까지만 받아서 팬 1~4, 5~8로 나눠 구한 뒤 다시 비교한다)

| 행 | 해석 |
|---:|---|
| 270 | *[주석] FMS(풍량 차압 센서) 고장: 팬은 충분히 도는데(최대 RPM > 기준) 급기 차압이 기준보다 낮으면 고장으로 본다* |
| 271 | *[주석] RPM과 차압이 안 맞는 것만 보는 것이라, 실제 풍량 부족과 센서·배선 이상은 구분하지 못한다* |
| 272 | *[주석] (engine.MAX는 인자를 5개까지만 받아서 팬 1~4, 5~8로 나눠 구한 뒤 다시 비교한다)* |
| 273 | **[조건]** 다음이 **모두** 맞음<br>① 급기 풍량 차압(FMS) (`FWU_SAFLOW_DP`) 값이 [FMS 고장 판단 차압 설정 (`VP_FWU_SAF_Fail_DP_Set`)]보다 작음<br>② [[팬 1번 현재 RPM (`FWU_SF-1.Current_RPM`), 팬 2번 현재 RPM (`FWU_SF-2.Current_RPM`), 팬 3번 현재 RPM (`FWU_SF-3.Current_RPM`), 팬 4번 현재 RPM (`FWU_SF-4.Current_RPM`)] 중 가장 큰 값, [팬 5번 현재 RPM (`FWU_SF-5.Current_RPM`), 팬 6번 현재 RPM (`FWU_SF-6.Current_RPM`), 팬 7번 현재 RPM (`FWU_SF-7.Current_RPM`), 팬 8번 현재 RPM (`FWU_SF-8.Current_RPM`)] 중 가장 큰 값] 중 가장 큰 값 값이 [FMS 고장 판단 RPM 설정 (`VP_FWU_SAF_Fail_RPM_Set`)]보다 큼<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 274 | &emsp;→&nbsp;**[조건]** 타이머 6번 `SAF_FAIL_TIMER`(팬은 도는데 급기 차압이 낮았던 시간 (FMS 고장 판단))으로 잰 시간(초)이 [`FMS_FAIL_CONFIRM_SECONDS`(= 20, 팬은 도는데 차압이 낮은 상태가 20초 넘게 이어지면 FMS 고장)]초보다 김<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 275 | &emsp;&emsp;→&nbsp;FMS(풍량 차압 센서) 고장 알람 (`VP_FWU_SAF_Failure_Alarm`)을 켠다 — 값 [TRUE(1)] (= 알람 걸림) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 276 | &emsp;→&nbsp;**[아니면]** 274행 조건의 반대 상황, 즉 타이머 6번 `SAF_FAIL_TIMER`(팬은 도는데 급기 차압이 낮았던 시간 (FMS 고장 판단))으로 잰 시간(초)이 아직 [`FMS_FAIL_CONFIRM_SECONDS`(= 20, 팬은 도는데 차압이 낮은 상태가 20초 넘게 이어지면 FMS 고장)]초를 넘지 않음<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 277 | &emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 278 | **[아니면]** 273행 조건의 반대 상황, 즉 아래 조건 중 **하나라도 맞지 않음**<br>① 급기 풍량 차압(FMS) (`FWU_SAFLOW_DP`) 값이 [FMS 고장 판단 차압 설정 (`VP_FWU_SAF_Fail_DP_Set`)]보다 작음<br>② [[팬 1번 현재 RPM (`FWU_SF-1.Current_RPM`), 팬 2번 현재 RPM (`FWU_SF-2.Current_RPM`), 팬 3번 현재 RPM (`FWU_SF-3.Current_RPM`), 팬 4번 현재 RPM (`FWU_SF-4.Current_RPM`)] 중 가장 큰 값, [팬 5번 현재 RPM (`FWU_SF-5.Current_RPM`), 팬 6번 현재 RPM (`FWU_SF-6.Current_RPM`), 팬 7번 현재 RPM (`FWU_SF-7.Current_RPM`), 팬 8번 현재 RPM (`FWU_SF-8.Current_RPM`)] 중 가장 큰 값] 중 가장 큰 값 값이 [FMS 고장 판단 RPM 설정 (`VP_FWU_SAF_Fail_RPM_Set`)]보다 큼<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 279 | &emsp;→&nbsp;타이머 6번 `SAF_FAIL_TIMER`(팬은 도는데 급기 차압이 낮았던 시간 (FMS 고장 판단))를 0으로 되돌린다. 이 시점부터 시간을 새로 잰다 |
| 280 | &emsp;→&nbsp;FMS(풍량 차압 센서) 고장 알람 (`VP_FWU_SAF_Failure_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 282 | *[주석] JSY 2026-11-23 수정 구간 끝. 주제 = Alarm-1에서 상·하한 알람과 센서 고장 알람을 떼어 만듦, Coding Rule 적용* |
| 283 | *[주석] LJH 2026-11-17 수정 표시. 주제 = 내부 센서 유효성 및 팬·댐퍼 알람* |
