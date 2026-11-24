# PICV Feedback 줄별 해석

> **대상 코드** : `fwu_v3/Logic/PICV Feedback.py` (320 줄, refac 예제 원본)  
> **기준** : `sy 브랜치 2026-11-24 (댐퍼 설치 여부 설정 반영)`  
> **행** = 코드 줄 번호 (빈 줄은 생략)  
> **표기** : `→` 들여쓰기 단계 · *[주석]* 코드 안 주석 · `이름` 코드 안 상수·변수 · **※** 읽을 때 주의할 점

PICV 4대의 개도·유량·온도 수신값을 확인하고, 닫힘 여부·명령-개도 차이·유량 이상을 판단해 밸브별 알람과 종합 상태를 낸다. refac 예제 원본 파일이다.

**※** 이 파일(refac 예제 원본)은 탭과 스페이스가 섞여 있어 Python에서 TabError가 난다. 원본을 그대로 두었으며, 아래 들여쓰기 단계는 탭을 4칸으로 보고 표시했다.

**목차**

- [1~33행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수](#section-1)
- [35~51행 · PICV1(1/2): valid check(개도, 유량, 온도에서 alarm 없음)](#section-2)
- [53~102행 · PICV1(2/2): 개도 및 유량 범위 확인](#section-3)
- [104~120행 · PICV2(1/2): valid check(개도, 유량, 온도에서 alarm 없음)](#section-4)
- [122~171행 · PICV2(2/2): 개도 및 유량 범위 확인](#section-5)
- [173~189행 · PICV3(1/2): valid check(개도, 유량, 온도에서 alarm 없음)](#section-6)
- [191~238행 · PICV3(2/2): 개도 및 유량 범위 확인](#section-7)
- [240~256행 · PICV4(1/2): valid check(개도, 유량, 온도에서 alarm 없음)](#section-8)
- [258~307행 · PICV4(2/2): 개도 및 유량 범위 확인](#section-9)
- [309~313행 · 모니터링 flag setting](#section-10)
- [315~320행 · PICV 상태, 유량 등의 정보를 VP_...에 업데이트](#section-11)

**※ 읽는 법**

- **[조건]** 줄은 조건이 맞을 때만 바로 아래 한 칸 더 들여쓴(→가 하나 더 붙은) 줄들을 실행한다. **[아니면]** 줄은 그 조건이 맞지 않을 때 실행하는 부분이다.
- 값은 [ ] 안에 적었다. TRUE·ON·SET·TMR_READ·DEC = 1, FALSE·OFF·CLEAR·TMR_CLEAR·INC = 0 이다. 0/1 값 옆 (= …)은 그 관제점에서 0/1이 뜻하는 상태다.
- **우선순위 칸**: 관제점 하나에 번호가 붙은 여러 칸이 있고, **숫자가 작은 칸의 값이 이긴다**. 1 = 비상정지, 2 = 원격·화재 정지, 5 = 일반 로직(번호 없이 쓰는 `WRITEPOINT`), 11 = 값 보관·정지 요청. 칸을 지우면(해제) 그다음 칸의 값이 적용된다.
- 조건이 맞지 않는다고 관제점이 저절로 0이 되지는 않는다. 그 분기에 쓰는 줄이 없으면 **이전 값이 그대로 남는다**.
- 타이머는 0으로 되돌린 순간부터 흐른 시간(초)을 잰다. 대문자 이름은 상수, `m`으로 시작하는 이름은 이 파일 전체에서 쓰는 변수, 이름에 `b`가 붙은 변수는 TRUE/FALSE 값이다.

<a id="section-1"></a>

## 1~33행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수

| 행 | 해석 |
|---:|---|
| 1 | *[주석] LJH 2026-11-17 수정 구간 시작. 주제 = 밸브별 수신 유효성 및 닫힘 확인* |
| 3 | *[주석] 로직엔진 loading* |
| 4 | DDC 로직 엔진을 불러온다. 이 아래에서 `engine.READPOINT`(관제점 읽기), `engine.WRITEPOINT`(관제점 쓰기) 같은 기능을 이 이름으로 쓴다 |
| 6 | *[주석] Macro상수 정의* |
| 7 | 매크로 상수 정의: TMR_READ, SET, ON, TRUE, DEC를 모두 숫자 1으로 정한다. 코드에서 숫자 1 대신 뜻이 보이는 이름으로 쓰기 위한 것이다 (타이머 읽기·켜짐·참·DEC 방향처럼 '긍정' 또는 1을 뜻하는 인자) |
| 8 | 매크로 상수 정의: TMR_CLEAR, CLEAR, OFF, FALSE, INC를 모두 숫자 0으로 정한다. 코드에서 숫자 0 대신 뜻이 보이는 이름으로 쓰기 위한 것이다 (타이머 초기화·꺼짐·거짓·INC 방향처럼 '부정' 또는 0을 뜻하는 인자) |
| 9 | 상수 `DEV_TIME_OUT` = 40. 뜻: deviation timer는 40초 까지 |
| 10 | 상수 `POS_HYST` = 30. 뜻: 개도의 히스테리시스는 +/-30% 까지 |
| 11 | 상수 `POS_OPEN` = 30. 뜻: 30% 이상 열리면 PICV가 "충분히" 열린 것으로 판단 |
| 12 | 설정값 상수 `NO_FLOW`: 유량 없음 판단 유량 설정 (`VP_FWU_PICV_No_Flow_Set`) 값을 이 로직이 실행될 때마다 한 번 읽어 이 이름에 담아 둔다. 뜻: '유량없음'으로 판단하는 최소 유량 |
| 13 | 설정값 상수 `LEAK_FLOW`: 누설 판단 유량 설정 (`VP_FWU_PICV_Leak_Flow_Set`) 값을 이 로직이 실행될 때마다 한 번 읽어 이 이름에 담아 둔다. 뜻: leak로 판단하는 유량 (?) |
| 15 | *[주석] 타이머 정의: PICV의 현재 개도가 tolerance를 벗어난 경우* |
| 16 | 타이머 번호에 이름 붙이기: `PICV_1_DEVIATION_TIMER` = 타이머 4번. 이 타이머로 'PICV 1번 명령과 실제 개도가 크게 다른 상태가 이어진 시간'을 잰다 (한 로직에서 타이머는 0~9번 10개까지) |
| 17 | 타이머 번호에 이름 붙이기: `PICV_2_DEVIATION_TIMER` = 타이머 5번. 이 타이머로 'PICV 2번 명령과 실제 개도가 크게 다른 상태가 이어진 시간'을 잰다 (한 로직에서 타이머는 0~9번 10개까지) |
| 18 | 타이머 번호에 이름 붙이기: `PICV_3_DEVIATION_TIMER` = 타이머 6번. 이 타이머로 'PICV 3번 명령과 실제 개도가 크게 다른 상태가 이어진 시간'을 잰다 (한 로직에서 타이머는 0~9번 10개까지) |
| 19 | 타이머 번호에 이름 붙이기: `PICV_4_DEVIATION_TIMER` = 타이머 7번. 이 타이머로 'PICV 4번 명령과 실제 개도가 크게 다른 상태가 이어진 시간'을 잰다 (한 로직에서 타이머는 0~9번 10개까지) |
| 21 | *[주석] CH3에 FWU_PICV-1~4의 Position, Flow, Temperature 통신점을 등록한 뒤 Input_Enable=1로 설정* |
| 22 | *[주석] 개도는 %, 유량은 L/min, 온도는 냉수 출구 온도(℃)로 환산* |
| 24 | *[주석] 전역변수 선언* |
| 25 | 전역변수 `mbAllClosed`(네 밸브가 모두 닫혔는지, TRUE면 모두 닫힘)를 만들고 처음 값을 [TRUE(1)]로 둔다. 이 로직이 실행될 때마다 이 값에서 다시 시작한다 |
| 26 | 전역변수 `mbMonitorReady`(밸브 감시가 준비됐는지, TRUE면 준비됨)를 만들고 처음 값을 [TRUE(1)]로 둔다. 이 로직이 실행될 때마다 이 값에서 다시 시작한다 |
| 27 | 전역변수 `mbAnyFault`(밸브 알람이 하나라도 있는지, TRUE면 있음)를 만들고 처음 값을 [FALSE(0)]로 둔다. 이 로직이 실행될 때마다 이 값에서 다시 시작한다 |
| 28 | 전역변수 `mbAnyCommFault`(밸브 수신 이상이 하나라도 있는지, TRUE면 있음)를 만들고 처음 값을 [FALSE(0)]로 둔다. 이 로직이 실행될 때마다 이 값에서 다시 시작한다 |
| 29 | 전역변수 `mbPICVValid`(지금 보는 밸브의 수신값을 믿을 수 있는지, TRUE면 유효)를 만들고 처음 값을 [FALSE(0)]로 둔다. 이 로직이 실행될 때마다 이 값에서 다시 시작한다 |
| 30 | `mbPICVInputEnable`(PICV 통신 입력을 쓰는지, TRUE면 씀)에 판단 결과를 넣는다: PICV 통신 입력 사용 설정 (`VP_FWU_PICV_Input_Enable`) 값이 [1]임 (= PICV 통신 입력 씀)<br>→ 맞으면 TRUE(1), 아니면 FALSE(0) |
| 31 | `mbPICVFlowChkEnable`(밸브 유량 감시를 하는지, TRUE면 함)에 판단 결과를 넣는다: 밸브 유량 감시 사용 설정 (`VP_FWU_PICV_Flow_Check_Enable`) 값이 [1]임 (= 유량 감시 함)<br>→ 맞으면 TRUE(1), 아니면 FALSE(0) |
| 32 | `mbCHWSCondi`(냉수 공급이 정상인지, TRUE면 정상)에 판단 결과를 넣는다: 냉수 공급 조건 성립 표시 (`VP_FWU_Chilled_Water_Supply_Condition`) 값이 [1]임 (= 냉수 공급 정상)<br>→ 맞으면 TRUE(1), 아니면 FALSE(0) |
| 33 | 전역변수 `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%))를 만들고 처음 값을 [0]로 둔다. 이 로직이 실행될 때마다 이 값에서 다시 시작한다<br>*[주석] PICV의 현재 개도값* |

<a id="section-2"></a>

## 35~51행 · PICV1(1/2): valid check(개도, 유량, 온도에서 alarm 없음)

| 행 | 해석 |
|---:|---|
| 35 | *[주석] PICV1(1/2): valid check(개도, 유량, 온도에서 alarm 없음)* |
| 36 | `mbPICVValid`(지금 보는 밸브의 수신값을 믿을 수 있는지, TRUE면 유효) 값을 [FALSE(0)]로 바꾼다<br>*[주석] 초기화* |
| 37 | **[조건]** `mbPICVInputEnable`(PICV 통신 입력을 쓰는지, TRUE면 씀) 값이 [TRUE(1)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 38 | &emsp;→&nbsp;**[조건]** 다음이 **모두** 맞음<br>① PICV 1번 개도 통신점 (`FWU_PICV-1.Position`)의 알람 코드가 [0]임 (= 알람 없음, 정상 수신)<br>② PICV 1번 유량 통신점 (`FWU_PICV-1.Flow`)의 알람 코드가 [0]임 (= 알람 없음, 정상 수신)<br>③ PICV 1번 온도 통신점 (`FWU_PICV-1.Temperature`)의 알람 코드가 [0]임 (= 알람 없음, 정상 수신)<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 39 | &emsp;&emsp;→&nbsp;PICV 1번 개도 표시값 (`VP_FWU_PICV-1_Position`) 값을 PICV 1번 개도 통신점 (`FWU_PICV-1.Position`)의 지금 값과 똑같이 맞춘다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 40 | &emsp;&emsp;→&nbsp;PICV 1번 유량 표시값 (`VP_FWU_PICV-1_Flow`) 값을 PICV 1번 유량 통신점 (`FWU_PICV-1.Flow`)의 지금 값과 똑같이 맞춘다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 41 | &emsp;&emsp;→&nbsp;PICV 1번 온도 표시값 (`VP_FWU_PICV-1_Temperature`) 값을 PICV 1번 온도 통신점 (`FWU_PICV-1.Temperature`)의 지금 값과 똑같이 맞춘다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 42 | &emsp;&emsp;→&nbsp;`mbPICVValid`(지금 보는 밸브의 수신값을 믿을 수 있는지, TRUE면 유효) 값을 [TRUE(1)]로 바꾼다 |
| 43 | &emsp;→&nbsp;**[아니면]** 38행 조건의 반대 상황, 즉 아래 조건 중 **하나라도 맞지 않음**<br>① PICV 1번 개도 통신점 (`FWU_PICV-1.Position`)의 알람 코드가 [0]임 (= 알람 없음, 정상 수신)<br>② PICV 1번 유량 통신점 (`FWU_PICV-1.Flow`)의 알람 코드가 [0]임 (= 알람 없음, 정상 수신)<br>③ PICV 1번 온도 통신점 (`FWU_PICV-1.Temperature`)의 알람 코드가 [0]임 (= 알람 없음, 정상 수신)<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 44 | &emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 46 | `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%))에 PICV 1번 개도 표시값 (`VP_FWU_PICV-1_Position`) 값을 읽어 넣는다 |
| 47 | **[조건]** `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [0] 이상이고 [100] 이하<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 48 | &emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 49 | **[아니면]** 47행 조건의 반대 상황, 즉 `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [0]~[100] 범위 밖임<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 50 | &emsp;→&nbsp;`mbPICVValid`(지금 보는 밸브의 수신값을 믿을 수 있는지, TRUE면 유효) 값을 [FALSE(0)]로 바꾼다 |
| 51 | PICV 1번 수신값 유효 표시 (`VP_FWU_PICV-1_Feedback_Valid`) 값을 [`mbPICVValid`(지금 보는 밸브의 수신값을 믿을 수 있는지, TRUE면 유효)]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |

<a id="section-3"></a>

## 53~102행 · PICV1(2/2): 개도 및 유량 범위 확인

| 행 | 해석 |
|---:|---|
| 53 | *[주석] PICV1(2/2): 개도 및 유량 범위 확인* |
| 54 | **[조건]** `mbPICVValid`(지금 보는 밸브의 수신값을 믿을 수 있는지, TRUE면 유효) 값이 [TRUE(1)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 55 | &emsp;→&nbsp;PICV 1번 수신 이상 (`VP_FWU_PICV-1_Comm_Fault`) 값을 [FALSE(0)]로 바꾼다 (= 통신 정상) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 57 | &emsp;→&nbsp;**[조건]** `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [5] 이상<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 58 | &emsp;&emsp;→&nbsp;`mbAllClosed`(네 밸브가 모두 닫혔는지, TRUE면 모두 닫힘) 값을 [FALSE(0)]로 바꾼다 |
| 59 | &emsp;→&nbsp;**[아니면]** 57행 조건의 반대 상황, 즉 `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [5]보다 작음<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 60 | &emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 62 | &emsp;→&nbsp;*[주석] 위치 제어 모드에서만 명령과 실제 개도를 비교한다.* |
| 63 | &emsp;→&nbsp;`bValveFault`(지금 보는 밸브를 고장으로 볼지, TRUE면 고장) 값을 [FALSE(0)]로 바꾼다 |
| 64 | &emsp;→&nbsp;**[조건]** 밸브 제어 모드(0 미확정, 1 위치, 2 유량) (`VP_FWU_PICV_Control_Mode`) 값이 [1]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다<br>*[주석] 좌변이 boolean인가? (?)* |
| 65 | &emsp;&emsp;→&nbsp;**[조건]** PICV 공통 개도 명령(AO) (`FWU_PICV_CONTROL`) 값이 [`mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) - `POS_HYST`(= 30, 개도의 히스테리시스는 +/-30% 까지)]보다 크고 [`mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) + `POS_HYST`(= 30, 개도의 히스테리시스는 +/-30% 까지)]보다 작음<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 66 | &emsp;&emsp;&emsp;→&nbsp;타이머 4번 `PICV_1_DEVIATION_TIMER`(PICV 1번 명령과 실제 개도가 크게 다른 상태가 이어진 시간)를 0으로 되돌린다. 이 시점부터 시간을 새로 잰다 |
| 67 | &emsp;&emsp;→&nbsp;**[아니면]** 65행 조건의 반대 상황, 즉 PICV 공통 개도 명령(AO) (`FWU_PICV_CONTROL`) 값이 [`mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) - `POS_HYST`(= 30, 개도의 히스테리시스는 +/-30% 까지)]~[`mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) + `POS_HYST`(= 30, 개도의 히스테리시스는 +/-30% 까지)] 범위 밖임<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 68 | &emsp;&emsp;&emsp;→&nbsp;**[조건]** 타이머 4번 `PICV_1_DEVIATION_TIMER`(PICV 1번 명령과 실제 개도가 크게 다른 상태가 이어진 시간)으로 잰 시간(초)이 [`DEV_TIME_OUT`(= 40, deviation timer는 40초 까지)]초보다 김<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 69 | &emsp;&emsp;&emsp;&emsp;→&nbsp;`bValveFault`(지금 보는 밸브를 고장으로 볼지, TRUE면 고장) 값을 [TRUE(1)]로 바꾼다 |
| 70 | &emsp;&emsp;&emsp;→&nbsp;**[아니면]** 68행 조건의 반대 상황, 즉 타이머 4번 `PICV_1_DEVIATION_TIMER`(PICV 1번 명령과 실제 개도가 크게 다른 상태가 이어진 시간)으로 잰 시간(초)이 아직 [`DEV_TIME_OUT`(= 40, deviation timer는 40초 까지)]초를 넘지 않음<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 71 | &emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 72 | &emsp;→&nbsp;**[아니면]** 64행 조건의 반대 상황, 즉 밸브 제어 모드(0 미확정, 1 위치, 2 유량) (`VP_FWU_PICV_Control_Mode`) 값이 [1]이 아님<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 73 | &emsp;&emsp;→&nbsp;타이머 4번 `PICV_1_DEVIATION_TIMER`(PICV 1번 명령과 실제 개도가 크게 다른 상태가 이어진 시간)를 0으로 되돌린다. 이 시점부터 시간을 새로 잰다 |
| 75 | &emsp;→&nbsp;*[주석] 유량 기준 30/10 LPM은 밸브별 설계 유량 확인 후 감시를 켤 것.* |
| 76 | &emsp;→&nbsp;**[조건]** `mbPICVFlowChkEnable`(밸브 유량 감시를 하는지, TRUE면 함) 값이 [TRUE(1)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 77 | &emsp;&emsp;→&nbsp;`PICVCurrFlow`(지금 보는 밸브의 현재 유량)에 PICV 1번 유량 표시값 (`VP_FWU_PICV-1_Flow`) 값을 읽어 넣는다 |
| 78 | &emsp;&emsp;→&nbsp;**[조건]** 다음이 **모두** 맞음<br>① `mbCHWSCondi`(냉수 공급이 정상인지, TRUE면 정상) 값이 [TRUE(1)]임<br>② `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [`POS_OPEN`(= 30, 30% 이상 열리면 PICV가 "충분히" 열린 것으로 판단)]보다 큼<br>③ `PICVCurrFlow`(지금 보는 밸브의 현재 유량) 값이 [`NO_FLOW`(설정값: '유량없음'으로 판단하는 최소 유량)]보다 작음<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 79 | &emsp;&emsp;&emsp;→&nbsp;`bValveFault`(지금 보는 밸브를 고장으로 볼지, TRUE면 고장) 값을 [TRUE(1)]로 바꾼다 |
| 80 | &emsp;&emsp;→&nbsp;**[아니면]** 78행 조건의 반대 상황, 즉 아래 조건 중 **하나라도 맞지 않음**<br>① `mbCHWSCondi`(냉수 공급이 정상인지, TRUE면 정상) 값이 [TRUE(1)]임<br>② `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [`POS_OPEN`(= 30, 30% 이상 열리면 PICV가 "충분히" 열린 것으로 판단)]보다 큼<br>③ `PICVCurrFlow`(지금 보는 밸브의 현재 유량) 값이 [`NO_FLOW`(설정값: '유량없음'으로 판단하는 최소 유량)]보다 작음<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 81 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 83 | &emsp;&emsp;→&nbsp;**[조건]** 다음이 **모두** 맞음<br>① `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [1]보다 작음<br>② `PICVCurrFlow`(지금 보는 밸브의 현재 유량) 값이 [`LEAK_FLOW`(설정값: leak로 판단하는 유량 (?))]보다 큼<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 84 | &emsp;&emsp;&emsp;→&nbsp;`bValveFault`(지금 보는 밸브를 고장으로 볼지, TRUE면 고장) 값을 [TRUE(1)]로 바꾼다 |
| 85 | &emsp;&emsp;→&nbsp;**[아니면]** 83행 조건의 반대 상황, 즉 아래 조건 중 **하나라도 맞지 않음**<br>① `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [1]보다 작음<br>② `PICVCurrFlow`(지금 보는 밸브의 현재 유량) 값이 [`LEAK_FLOW`(설정값: leak로 판단하는 유량 (?))]보다 큼<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 86 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 87 | &emsp;→&nbsp;**[아니면]** 76행 조건의 반대 상황, 즉 `mbPICVFlowChkEnable`(밸브 유량 감시를 하는지, TRUE면 함) 값이 [FALSE(0)]임<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 88 | &emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 90 | &emsp;→&nbsp;PICV 1번 밸브 알람 (`VP_FWU_PICV-1_Alarm`) 값을 [`bValveFault`(지금 보는 밸브를 고장으로 볼지, TRUE면 고장)]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 91 | **[아니면]** 54행 조건의 반대 상황, 즉 `mbPICVValid`(지금 보는 밸브의 수신값을 믿을 수 있는지, TRUE면 유효) 값이 [FALSE(0)]임<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 92 | &emsp;→&nbsp;`mbAllClosed`(네 밸브가 모두 닫혔는지, TRUE면 모두 닫힘) 값을 [FALSE(0)]로 바꾼다 |
| 93 | &emsp;→&nbsp;`mbMonitorReady`(밸브 감시가 준비됐는지, TRUE면 준비됨) 값을 [FALSE(0)]로 바꾼다 |
| 94 | &emsp;→&nbsp;`mbAnyCommFault`(밸브 수신 이상이 하나라도 있는지, TRUE면 있음) 값을 [TRUE(1)]로 바꾼다 |
| 95 | &emsp;→&nbsp;PICV 1번 수신 이상 (`VP_FWU_PICV-1_Comm_Fault`) 값을 [TRUE(1)]로 바꾼다 (= 통신 이상) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 96 | &emsp;→&nbsp;PICV 1번 밸브 알람 (`VP_FWU_PICV-1_Alarm`)을 켠다 — 값 [TRUE(1)] (= 알람 걸림) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 97 | &emsp;→&nbsp;타이머 4번 `PICV_1_DEVIATION_TIMER`(PICV 1번 명령과 실제 개도가 크게 다른 상태가 이어진 시간)를 0으로 되돌린다. 이 시점부터 시간을 새로 잰다 |
| 99 | **[조건]** PICV 1번 밸브 알람 (`VP_FWU_PICV-1_Alarm`) 값이 [TRUE(1)]임 (= 알람 걸림)<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 100 | &emsp;→&nbsp;`mbAnyFault`(밸브 알람이 하나라도 있는지, TRUE면 있음) 값을 [TRUE(1)]로 바꾼다 |
| 101 | **[아니면]** 99행 조건의 반대 상황, 즉 PICV 1번 밸브 알람 (`VP_FWU_PICV-1_Alarm`) 값이 [TRUE(1)]이 아님 (= 알람 없음)<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 102 | &emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |

<a id="section-4"></a>

## 104~120행 · PICV2(1/2): valid check(개도, 유량, 온도에서 alarm 없음)

| 행 | 해석 |
|---:|---|
| 104 | *[주석] PICV2(1/2): valid check(개도, 유량, 온도에서 alarm 없음)* |
| 105 | `mbPICVValid`(지금 보는 밸브의 수신값을 믿을 수 있는지, TRUE면 유효) 값을 [FALSE(0)]로 바꾼다<br>*[주석] 초기화* |
| 106 | **[조건]** `mbPICVInputEnable`(PICV 통신 입력을 쓰는지, TRUE면 씀) 값이 [TRUE(1)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 107 | &emsp;→&nbsp;**[조건]** 다음이 **모두** 맞음<br>① PICV 2번 개도 통신점 (`FWU_PICV-2.Position`)의 알람 코드가 [0]임 (= 알람 없음, 정상 수신)<br>② PICV 2번 유량 통신점 (`FWU_PICV-2.Flow`)의 알람 코드가 [0]임 (= 알람 없음, 정상 수신)<br>③ PICV 2번 온도 통신점 (`FWU_PICV-2.Temperature`)의 알람 코드가 [0]임 (= 알람 없음, 정상 수신)<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 108 | &emsp;&emsp;→&nbsp;PICV 2번 개도 표시값 (`VP_FWU_PICV-2_Position`) 값을 PICV 2번 개도 통신점 (`FWU_PICV-2.Position`)의 지금 값과 똑같이 맞춘다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 109 | &emsp;&emsp;→&nbsp;PICV 2번 유량 표시값 (`VP_FWU_PICV-2_Flow`) 값을 PICV 2번 유량 통신점 (`FWU_PICV-2.Flow`)의 지금 값과 똑같이 맞춘다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 110 | &emsp;&emsp;→&nbsp;PICV 2번 온도 표시값 (`VP_FWU_PICV-2_Temperature`) 값을 PICV 2번 온도 통신점 (`FWU_PICV-2.Temperature`)의 지금 값과 똑같이 맞춘다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 111 | &emsp;&emsp;→&nbsp;`mbPICVValid`(지금 보는 밸브의 수신값을 믿을 수 있는지, TRUE면 유효) 값을 [TRUE(1)]로 바꾼다 |
| 112 | &emsp;→&nbsp;**[아니면]** 107행 조건의 반대 상황, 즉 아래 조건 중 **하나라도 맞지 않음**<br>① PICV 2번 개도 통신점 (`FWU_PICV-2.Position`)의 알람 코드가 [0]임 (= 알람 없음, 정상 수신)<br>② PICV 2번 유량 통신점 (`FWU_PICV-2.Flow`)의 알람 코드가 [0]임 (= 알람 없음, 정상 수신)<br>③ PICV 2번 온도 통신점 (`FWU_PICV-2.Temperature`)의 알람 코드가 [0]임 (= 알람 없음, 정상 수신)<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 113 | &emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 115 | `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%))에 PICV 2번 개도 표시값 (`VP_FWU_PICV-2_Position`) 값을 읽어 넣는다 |
| 116 | **[조건]** `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [0] 이상이고 [100] 이하<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 117 | &emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 118 | **[아니면]** 116행 조건의 반대 상황, 즉 `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [0]~[100] 범위 밖임<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 119 | &emsp;→&nbsp;`mbPICVValid`(지금 보는 밸브의 수신값을 믿을 수 있는지, TRUE면 유효) 값을 [FALSE(0)]로 바꾼다 |
| 120 | PICV 2번 수신값 유효 표시 (`VP_FWU_PICV-2_Feedback_Valid`) 값을 [`mbPICVValid`(지금 보는 밸브의 수신값을 믿을 수 있는지, TRUE면 유효)]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |

<a id="section-5"></a>

## 122~171행 · PICV2(2/2): 개도 및 유량 범위 확인

| 행 | 해석 |
|---:|---|
| 122 | *[주석] PICV2(2/2): 개도 및 유량 범위 확인* |
| 123 | **[조건]** `mbPICVValid`(지금 보는 밸브의 수신값을 믿을 수 있는지, TRUE면 유효) 값이 [TRUE(1)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 124 | &emsp;→&nbsp;PICV 2번 수신 이상 (`VP_FWU_PICV-2_Comm_Fault`) 값을 [FALSE(0)]로 바꾼다 (= 통신 정상) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 126 | &emsp;→&nbsp;**[조건]** `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [5] 이상<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 127 | &emsp;&emsp;→&nbsp;`mbAllClosed`(네 밸브가 모두 닫혔는지, TRUE면 모두 닫힘) 값을 [FALSE(0)]로 바꾼다 |
| 128 | &emsp;→&nbsp;**[아니면]** 126행 조건의 반대 상황, 즉 `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [5]보다 작음<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 129 | &emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 131 | &emsp;→&nbsp;*[주석] 위치 제어 모드에서만 명령과 실제 개도를 비교한다.* |
| 132 | &emsp;→&nbsp;`bValveFault`(지금 보는 밸브를 고장으로 볼지, TRUE면 고장) 값을 [FALSE(0)]로 바꾼다 |
| 133 | &emsp;→&nbsp;**[조건]** 밸브 제어 모드(0 미확정, 1 위치, 2 유량) (`VP_FWU_PICV_Control_Mode`) 값이 [1]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다<br>*[주석] 좌변이 boolean인가? (?)* |
| 134 | &emsp;&emsp;→&nbsp;**[조건]** PICV 공통 개도 명령(AO) (`FWU_PICV_CONTROL`) 값이 [`mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) - `POS_HYST`(= 30, 개도의 히스테리시스는 +/-30% 까지)]보다 크고 [`mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) + `POS_HYST`(= 30, 개도의 히스테리시스는 +/-30% 까지)]보다 작음<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 135 | &emsp;&emsp;&emsp;→&nbsp;타이머 5번 `PICV_2_DEVIATION_TIMER`(PICV 2번 명령과 실제 개도가 크게 다른 상태가 이어진 시간)를 0으로 되돌린다. 이 시점부터 시간을 새로 잰다 |
| 136 | &emsp;&emsp;→&nbsp;**[아니면]** 134행 조건의 반대 상황, 즉 PICV 공통 개도 명령(AO) (`FWU_PICV_CONTROL`) 값이 [`mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) - `POS_HYST`(= 30, 개도의 히스테리시스는 +/-30% 까지)]~[`mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) + `POS_HYST`(= 30, 개도의 히스테리시스는 +/-30% 까지)] 범위 밖임<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 137 | &emsp;&emsp;&emsp;→&nbsp;**[조건]** 타이머 5번 `PICV_2_DEVIATION_TIMER`(PICV 2번 명령과 실제 개도가 크게 다른 상태가 이어진 시간)으로 잰 시간(초)이 [`DEV_TIME_OUT`(= 40, deviation timer는 40초 까지)]초보다 김<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 138 | &emsp;&emsp;&emsp;&emsp;→&nbsp;`bValveFault`(지금 보는 밸브를 고장으로 볼지, TRUE면 고장) 값을 [TRUE(1)]로 바꾼다 |
| 139 | &emsp;&emsp;&emsp;→&nbsp;**[아니면]** 137행 조건의 반대 상황, 즉 타이머 5번 `PICV_2_DEVIATION_TIMER`(PICV 2번 명령과 실제 개도가 크게 다른 상태가 이어진 시간)으로 잰 시간(초)이 아직 [`DEV_TIME_OUT`(= 40, deviation timer는 40초 까지)]초를 넘지 않음<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 140 | &emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 141 | &emsp;→&nbsp;**[아니면]** 133행 조건의 반대 상황, 즉 밸브 제어 모드(0 미확정, 1 위치, 2 유량) (`VP_FWU_PICV_Control_Mode`) 값이 [1]이 아님<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 142 | &emsp;&emsp;→&nbsp;타이머 5번 `PICV_2_DEVIATION_TIMER`(PICV 2번 명령과 실제 개도가 크게 다른 상태가 이어진 시간)를 0으로 되돌린다. 이 시점부터 시간을 새로 잰다 |
| 144 | &emsp;→&nbsp;*[주석] 유량 기준 30/10 LPM은 밸브별 설계 유량 확인 후 감시를 켤 것.* |
| 145 | &emsp;→&nbsp;**[조건]** `mbPICVFlowChkEnable`(밸브 유량 감시를 하는지, TRUE면 함) 값이 [TRUE(1)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 146 | &emsp;&emsp;→&nbsp;`PICVCurrFlow`(지금 보는 밸브의 현재 유량)에 PICV 2번 유량 표시값 (`VP_FWU_PICV-2_Flow`) 값을 읽어 넣는다 |
| 147 | &emsp;&emsp;→&nbsp;**[조건]** 다음이 **모두** 맞음<br>① `mbCHWSCondi`(냉수 공급이 정상인지, TRUE면 정상) 값이 [TRUE(1)]임<br>② `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [`POS_OPEN`(= 30, 30% 이상 열리면 PICV가 "충분히" 열린 것으로 판단)]보다 큼<br>③ `PICVCurrFlow`(지금 보는 밸브의 현재 유량) 값이 [`NO_FLOW`(설정값: '유량없음'으로 판단하는 최소 유량)]보다 작음<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 148 | &emsp;&emsp;&emsp;→&nbsp;`bValveFault`(지금 보는 밸브를 고장으로 볼지, TRUE면 고장) 값을 [TRUE(1)]로 바꾼다 |
| 149 | &emsp;&emsp;→&nbsp;**[아니면]** 147행 조건의 반대 상황, 즉 아래 조건 중 **하나라도 맞지 않음**<br>① `mbCHWSCondi`(냉수 공급이 정상인지, TRUE면 정상) 값이 [TRUE(1)]임<br>② `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [`POS_OPEN`(= 30, 30% 이상 열리면 PICV가 "충분히" 열린 것으로 판단)]보다 큼<br>③ `PICVCurrFlow`(지금 보는 밸브의 현재 유량) 값이 [`NO_FLOW`(설정값: '유량없음'으로 판단하는 최소 유량)]보다 작음<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 150 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 152 | &emsp;&emsp;→&nbsp;**[조건]** 다음이 **모두** 맞음<br>① `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [1]보다 작음<br>② `PICVCurrFlow`(지금 보는 밸브의 현재 유량) 값이 [`LEAK_FLOW`(설정값: leak로 판단하는 유량 (?))]보다 큼<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 153 | &emsp;&emsp;&emsp;→&nbsp;`bValveFault`(지금 보는 밸브를 고장으로 볼지, TRUE면 고장) 값을 [TRUE(1)]로 바꾼다 |
| 154 | &emsp;&emsp;→&nbsp;**[아니면]** 152행 조건의 반대 상황, 즉 아래 조건 중 **하나라도 맞지 않음**<br>① `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [1]보다 작음<br>② `PICVCurrFlow`(지금 보는 밸브의 현재 유량) 값이 [`LEAK_FLOW`(설정값: leak로 판단하는 유량 (?))]보다 큼<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 155 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 156 | &emsp;→&nbsp;**[아니면]** 145행 조건의 반대 상황, 즉 `mbPICVFlowChkEnable`(밸브 유량 감시를 하는지, TRUE면 함) 값이 [FALSE(0)]임<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 157 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 159 | &emsp;→&nbsp;PICV 2번 밸브 알람 (`VP_FWU_PICV-2_Alarm`) 값을 [`bValveFault`(지금 보는 밸브를 고장으로 볼지, TRUE면 고장)]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 160 | **[아니면]** 123행 조건의 반대 상황, 즉 `mbPICVValid`(지금 보는 밸브의 수신값을 믿을 수 있는지, TRUE면 유효) 값이 [FALSE(0)]임<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 161 | &emsp;→&nbsp;`mbAllClosed`(네 밸브가 모두 닫혔는지, TRUE면 모두 닫힘) 값을 [FALSE(0)]로 바꾼다 |
| 162 | &emsp;→&nbsp;`mbMonitorReady`(밸브 감시가 준비됐는지, TRUE면 준비됨) 값을 [FALSE(0)]로 바꾼다 |
| 163 | &emsp;→&nbsp;`mbAnyCommFault`(밸브 수신 이상이 하나라도 있는지, TRUE면 있음) 값을 [TRUE(1)]로 바꾼다 |
| 164 | &emsp;→&nbsp;PICV 2번 수신 이상 (`VP_FWU_PICV-2_Comm_Fault`) 값을 [TRUE(1)]로 바꾼다 (= 통신 이상) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 165 | &emsp;→&nbsp;PICV 2번 밸브 알람 (`VP_FWU_PICV-2_Alarm`)을 켠다 — 값 [TRUE(1)] (= 알람 걸림) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 166 | &emsp;→&nbsp;타이머 5번 `PICV_2_DEVIATION_TIMER`(PICV 2번 명령과 실제 개도가 크게 다른 상태가 이어진 시간)를 0으로 되돌린다. 이 시점부터 시간을 새로 잰다 |
| 168 | **[조건]** PICV 2번 밸브 알람 (`VP_FWU_PICV-2_Alarm`) 값이 [TRUE(1)]임 (= 알람 걸림)<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 169 | &emsp;→&nbsp;`mbAnyFault`(밸브 알람이 하나라도 있는지, TRUE면 있음) 값을 [TRUE(1)]로 바꾼다 |
| 170 | **[아니면]** 168행 조건의 반대 상황, 즉 PICV 2번 밸브 알람 (`VP_FWU_PICV-2_Alarm`) 값이 [TRUE(1)]이 아님 (= 알람 없음)<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 171 | &emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |

<a id="section-6"></a>

## 173~189행 · PICV3(1/2): valid check(개도, 유량, 온도에서 alarm 없음)

| 행 | 해석 |
|---:|---|
| 173 | *[주석] PICV3(1/2): valid check(개도, 유량, 온도에서 alarm 없음)* |
| 174 | `mbPICVValid`(지금 보는 밸브의 수신값을 믿을 수 있는지, TRUE면 유효) 값을 [FALSE(0)]로 바꾼다<br>*[주석] 초기화* |
| 175 | **[조건]** `mbPICVInputEnable`(PICV 통신 입력을 쓰는지, TRUE면 씀) 값이 [TRUE(1)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 176 | &emsp;→&nbsp;**[조건]** 다음이 **모두** 맞음<br>① PICV 3번 개도 통신점 (`FWU_PICV-3.Position`)의 알람 코드가 [0]임 (= 알람 없음, 정상 수신)<br>② PICV 3번 유량 통신점 (`FWU_PICV-3.Flow`)의 알람 코드가 [0]임 (= 알람 없음, 정상 수신)<br>③ PICV 3번 온도 통신점 (`FWU_PICV-3.Temperature`)의 알람 코드가 [0]임 (= 알람 없음, 정상 수신)<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 177 | &emsp;&emsp;→&nbsp;PICV 3번 개도 표시값 (`VP_FWU_PICV-3_Position`) 값을 PICV 3번 개도 통신점 (`FWU_PICV-3.Position`)의 지금 값과 똑같이 맞춘다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 178 | &emsp;&emsp;→&nbsp;PICV 3번 유량 표시값 (`VP_FWU_PICV-3_Flow`) 값을 PICV 3번 유량 통신점 (`FWU_PICV-3.Flow`)의 지금 값과 똑같이 맞춘다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 179 | &emsp;&emsp;→&nbsp;PICV 3번 온도 표시값 (`VP_FWU_PICV-3_Temperature`) 값을 PICV 3번 온도 통신점 (`FWU_PICV-3.Temperature`)의 지금 값과 똑같이 맞춘다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 180 | &emsp;&emsp;→&nbsp;`mbPICVValid`(지금 보는 밸브의 수신값을 믿을 수 있는지, TRUE면 유효) 값을 [TRUE(1)]로 바꾼다 |
| 181 | &emsp;→&nbsp;**[아니면]** 176행 조건의 반대 상황, 즉 아래 조건 중 **하나라도 맞지 않음**<br>① PICV 3번 개도 통신점 (`FWU_PICV-3.Position`)의 알람 코드가 [0]임 (= 알람 없음, 정상 수신)<br>② PICV 3번 유량 통신점 (`FWU_PICV-3.Flow`)의 알람 코드가 [0]임 (= 알람 없음, 정상 수신)<br>③ PICV 3번 온도 통신점 (`FWU_PICV-3.Temperature`)의 알람 코드가 [0]임 (= 알람 없음, 정상 수신)<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 182 | &emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 184 | `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%))에 PICV 3번 개도 표시값 (`VP_FWU_PICV-3_Position`) 값을 읽어 넣는다 |
| 185 | **[조건]** `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [0] 이상이고 [100] 이하<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 186 | &emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 187 | **[아니면]** 185행 조건의 반대 상황, 즉 `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [0]~[100] 범위 밖임<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 188 | &emsp;→&nbsp;`mbPICVValid`(지금 보는 밸브의 수신값을 믿을 수 있는지, TRUE면 유효) 값을 [FALSE(0)]로 바꾼다 |
| 189 | PICV 3번 수신값 유효 표시 (`VP_FWU_PICV-3_Feedback_Valid`) 값을 [`mbPICVValid`(지금 보는 밸브의 수신값을 믿을 수 있는지, TRUE면 유효)]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |

<a id="section-7"></a>

## 191~238행 · PICV3(2/2): 개도 및 유량 범위 확인

| 행 | 해석 |
|---:|---|
| 191 | *[주석] PICV3(2/2): 개도 및 유량 범위 확인* |
| 192 | **[조건]** `mbPICVValid`(지금 보는 밸브의 수신값을 믿을 수 있는지, TRUE면 유효) 값이 [TRUE(1)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 193 | &emsp;→&nbsp;PICV 3번 수신 이상 (`VP_FWU_PICV-3_Comm_Fault`) 값을 [FALSE(0)]로 바꾼다 (= 통신 정상) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 195 | &emsp;→&nbsp;**[조건]** `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [5] 이상<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 196 | &emsp;&emsp;→&nbsp;`mbAllClosed`(네 밸브가 모두 닫혔는지, TRUE면 모두 닫힘) 값을 [FALSE(0)]로 바꾼다 |
| 197 | &emsp;→&nbsp;**[아니면]** 195행 조건의 반대 상황, 즉 `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [5]보다 작음<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 198 | &emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 200 | *[주석] 위치 제어 모드에서만 명령과 실제 개도를 비교한다.* |
| 201 | &emsp;→&nbsp;`bValveFault`(지금 보는 밸브를 고장으로 볼지, TRUE면 고장) 값을 [FALSE(0)]로 바꾼다 |
| 202 | &emsp;→&nbsp;**[조건]** 밸브 제어 모드(0 미확정, 1 위치, 2 유량) (`VP_FWU_PICV_Control_Mode`) 값이 [1]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다<br>*[주석] 좌변이 boolean인가? (?)* |
| 203 | &emsp;&emsp;→&nbsp;**[조건]** PICV 공통 개도 명령(AO) (`FWU_PICV_CONTROL`) 값이 [`mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) - `POS_HYST`(= 30, 개도의 히스테리시스는 +/-30% 까지)]보다 크고 [`mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) + `POS_HYST`(= 30, 개도의 히스테리시스는 +/-30% 까지)]보다 작음<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 204 | &emsp;&emsp;&emsp;→&nbsp;타이머 6번 `PICV_3_DEVIATION_TIMER`(PICV 3번 명령과 실제 개도가 크게 다른 상태가 이어진 시간)를 0으로 되돌린다. 이 시점부터 시간을 새로 잰다 |
| 205 | &emsp;&emsp;→&nbsp;**[아니면]** 203행 조건의 반대 상황, 즉 PICV 공통 개도 명령(AO) (`FWU_PICV_CONTROL`) 값이 [`mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) - `POS_HYST`(= 30, 개도의 히스테리시스는 +/-30% 까지)]~[`mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) + `POS_HYST`(= 30, 개도의 히스테리시스는 +/-30% 까지)] 범위 밖임<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 206 | &emsp;&emsp;&emsp;→&nbsp;**[조건]** 타이머 6번 `PICV_3_DEVIATION_TIMER`(PICV 3번 명령과 실제 개도가 크게 다른 상태가 이어진 시간)으로 잰 시간(초)이 [`DEV_TIME_OUT`(= 40, deviation timer는 40초 까지)]초보다 김<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 207 | &emsp;&emsp;&emsp;&emsp;→&nbsp;`bValveFault`(지금 보는 밸브를 고장으로 볼지, TRUE면 고장) 값을 [TRUE(1)]로 바꾼다 |
| 208 | &emsp;&emsp;&emsp;→&nbsp;**[아니면]** 206행 조건의 반대 상황, 즉 타이머 6번 `PICV_3_DEVIATION_TIMER`(PICV 3번 명령과 실제 개도가 크게 다른 상태가 이어진 시간)으로 잰 시간(초)이 아직 [`DEV_TIME_OUT`(= 40, deviation timer는 40초 까지)]초를 넘지 않음<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 209 | &emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 210 | &emsp;→&nbsp;**[아니면]** 202행 조건의 반대 상황, 즉 밸브 제어 모드(0 미확정, 1 위치, 2 유량) (`VP_FWU_PICV_Control_Mode`) 값이 [1]이 아님<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 211 | &emsp;&emsp;→&nbsp;타이머 6번 `PICV_3_DEVIATION_TIMER`(PICV 3번 명령과 실제 개도가 크게 다른 상태가 이어진 시간)를 0으로 되돌린다. 이 시점부터 시간을 새로 잰다 |
| 212 | &emsp;→&nbsp;*[주석] 유량 기준 30/10 LPM은 밸브별 설계 유량 확인 후 감시를 켤 것.* |
| 213 | &emsp;→&nbsp;**[조건]** `mbPICVFlowChkEnable`(밸브 유량 감시를 하는지, TRUE면 함) 값이 [TRUE(1)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 214 | &emsp;&emsp;→&nbsp;`PICVCurrFlow`(지금 보는 밸브의 현재 유량)에 PICV 3번 유량 표시값 (`VP_FWU_PICV-3_Flow`) 값을 읽어 넣는다 |
| 215 | &emsp;&emsp;→&nbsp;**[조건]** 다음이 **모두** 맞음<br>① `mbCHWSCondi`(냉수 공급이 정상인지, TRUE면 정상) 값이 [TRUE(1)]임<br>② `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [`POS_OPEN`(= 30, 30% 이상 열리면 PICV가 "충분히" 열린 것으로 판단)]보다 큼<br>③ `PICVCurrFlow`(지금 보는 밸브의 현재 유량) 값이 [`NO_FLOW`(설정값: '유량없음'으로 판단하는 최소 유량)]보다 작음<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 216 | &emsp;&emsp;&emsp;→&nbsp;`bValveFault`(지금 보는 밸브를 고장으로 볼지, TRUE면 고장) 값을 [TRUE(1)]로 바꾼다 |
| 217 | &emsp;&emsp;→&nbsp;**[아니면]** 215행 조건의 반대 상황, 즉 아래 조건 중 **하나라도 맞지 않음**<br>① `mbCHWSCondi`(냉수 공급이 정상인지, TRUE면 정상) 값이 [TRUE(1)]임<br>② `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [`POS_OPEN`(= 30, 30% 이상 열리면 PICV가 "충분히" 열린 것으로 판단)]보다 큼<br>③ `PICVCurrFlow`(지금 보는 밸브의 현재 유량) 값이 [`NO_FLOW`(설정값: '유량없음'으로 판단하는 최소 유량)]보다 작음<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 218 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 220 | &emsp;&emsp;→&nbsp;**[조건]** 다음이 **모두** 맞음<br>① `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [1]보다 작음<br>② `PICVCurrFlow`(지금 보는 밸브의 현재 유량) 값이 [`LEAK_FLOW`(설정값: leak로 판단하는 유량 (?))]보다 큼<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 221 | &emsp;&emsp;&emsp;→&nbsp;`bValveFault`(지금 보는 밸브를 고장으로 볼지, TRUE면 고장) 값을 [TRUE(1)]로 바꾼다 |
| 222 | &emsp;&emsp;→&nbsp;**[아니면]** 220행 조건의 반대 상황, 즉 아래 조건 중 **하나라도 맞지 않음**<br>① `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [1]보다 작음<br>② `PICVCurrFlow`(지금 보는 밸브의 현재 유량) 값이 [`LEAK_FLOW`(설정값: leak로 판단하는 유량 (?))]보다 큼<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 223 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 224 | &emsp;→&nbsp;**[아니면]** 213행 조건의 반대 상황, 즉 `mbPICVFlowChkEnable`(밸브 유량 감시를 하는지, TRUE면 함) 값이 [FALSE(0)]임<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 225 | &emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 226 | &emsp;→&nbsp;PICV 3번 밸브 알람 (`VP_FWU_PICV-3_Alarm`) 값을 [`bValveFault`(지금 보는 밸브를 고장으로 볼지, TRUE면 고장)]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 227 | **[아니면]** 192행 조건의 반대 상황, 즉 `mbPICVValid`(지금 보는 밸브의 수신값을 믿을 수 있는지, TRUE면 유효) 값이 [FALSE(0)]임<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 228 | &emsp;→&nbsp;`mbAllClosed`(네 밸브가 모두 닫혔는지, TRUE면 모두 닫힘) 값을 [FALSE(0)]로 바꾼다 |
| 229 | &emsp;→&nbsp;`mbMonitorReady`(밸브 감시가 준비됐는지, TRUE면 준비됨) 값을 [FALSE(0)]로 바꾼다 |
| 230 | &emsp;→&nbsp;`mbAnyCommFault`(밸브 수신 이상이 하나라도 있는지, TRUE면 있음) 값을 [TRUE(1)]로 바꾼다 |
| 231 | &emsp;→&nbsp;PICV 3번 수신 이상 (`VP_FWU_PICV-3_Comm_Fault`) 값을 [TRUE(1)]로 바꾼다 (= 통신 이상) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 232 | &emsp;→&nbsp;PICV 3번 밸브 알람 (`VP_FWU_PICV-3_Alarm`)을 켠다 — 값 [TRUE(1)] (= 알람 걸림) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 233 | &emsp;→&nbsp;타이머 6번 `PICV_3_DEVIATION_TIMER`(PICV 3번 명령과 실제 개도가 크게 다른 상태가 이어진 시간)를 0으로 되돌린다. 이 시점부터 시간을 새로 잰다 |
| 235 | **[조건]** PICV 3번 밸브 알람 (`VP_FWU_PICV-3_Alarm`) 값이 [TRUE(1)]임 (= 알람 걸림)<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 236 | &emsp;→&nbsp;`mbAnyFault`(밸브 알람이 하나라도 있는지, TRUE면 있음) 값을 [TRUE(1)]로 바꾼다 |
| 237 | **[아니면]** 235행 조건의 반대 상황, 즉 PICV 3번 밸브 알람 (`VP_FWU_PICV-3_Alarm`) 값이 [TRUE(1)]이 아님 (= 알람 없음)<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 238 | &emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |

<a id="section-8"></a>

## 240~256행 · PICV4(1/2): valid check(개도, 유량, 온도에서 alarm 없음)

| 행 | 해석 |
|---:|---|
| 240 | *[주석] PICV4(1/2): valid check(개도, 유량, 온도에서 alarm 없음)* |
| 241 | `mbPICVValid`(지금 보는 밸브의 수신값을 믿을 수 있는지, TRUE면 유효) 값을 [FALSE(0)]로 바꾼다<br>*[주석] 초기화* |
| 242 | **[조건]** `mbPICVInputEnable`(PICV 통신 입력을 쓰는지, TRUE면 씀) 값이 [TRUE(1)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 243 | &emsp;→&nbsp;**[조건]** 다음이 **모두** 맞음<br>① PICV 4번 개도 통신점 (`FWU_PICV-4.Position`)의 알람 코드가 [0]임 (= 알람 없음, 정상 수신)<br>② PICV 4번 유량 통신점 (`FWU_PICV-4.Flow`)의 알람 코드가 [0]임 (= 알람 없음, 정상 수신)<br>③ PICV 4번 온도 통신점 (`FWU_PICV-4.Temperature`)의 알람 코드가 [0]임 (= 알람 없음, 정상 수신)<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 244 | &emsp;&emsp;→&nbsp;PICV 4번 개도 표시값 (`VP_FWU_PICV-4_Position`) 값을 PICV 4번 개도 통신점 (`FWU_PICV-4.Position`)의 지금 값과 똑같이 맞춘다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 245 | &emsp;&emsp;→&nbsp;PICV 4번 유량 표시값 (`VP_FWU_PICV-4_Flow`) 값을 PICV 4번 유량 통신점 (`FWU_PICV-4.Flow`)의 지금 값과 똑같이 맞춘다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 246 | &emsp;&emsp;→&nbsp;PICV 4번 온도 표시값 (`VP_FWU_PICV-4_Temperature`) 값을 PICV 4번 온도 통신점 (`FWU_PICV-4.Temperature`)의 지금 값과 똑같이 맞춘다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 247 | &emsp;&emsp;→&nbsp;`mbPICVValid`(지금 보는 밸브의 수신값을 믿을 수 있는지, TRUE면 유효) 값을 [TRUE(1)]로 바꾼다 |
| 248 | &emsp;→&nbsp;**[아니면]** 243행 조건의 반대 상황, 즉 아래 조건 중 **하나라도 맞지 않음**<br>① PICV 4번 개도 통신점 (`FWU_PICV-4.Position`)의 알람 코드가 [0]임 (= 알람 없음, 정상 수신)<br>② PICV 4번 유량 통신점 (`FWU_PICV-4.Flow`)의 알람 코드가 [0]임 (= 알람 없음, 정상 수신)<br>③ PICV 4번 온도 통신점 (`FWU_PICV-4.Temperature`)의 알람 코드가 [0]임 (= 알람 없음, 정상 수신)<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 249 | &emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 251 | `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%))에 PICV 4번 개도 표시값 (`VP_FWU_PICV-4_Position`) 값을 읽어 넣는다 |
| 252 | **[조건]** `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [0] 이상이고 [100] 이하<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 253 | &emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 254 | **[아니면]** 252행 조건의 반대 상황, 즉 `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [0]~[100] 범위 밖임<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 255 | &emsp;→&nbsp;`mbPICVValid`(지금 보는 밸브의 수신값을 믿을 수 있는지, TRUE면 유효) 값을 [FALSE(0)]로 바꾼다 |
| 256 | PICV 4번 수신값 유효 표시 (`VP_FWU_PICV-4_Feedback_Valid`) 값을 [`mbPICVValid`(지금 보는 밸브의 수신값을 믿을 수 있는지, TRUE면 유효)]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |

<a id="section-9"></a>

## 258~307행 · PICV4(2/2): 개도 및 유량 범위 확인

| 행 | 해석 |
|---:|---|
| 258 | *[주석] PICV4(2/2): 개도 및 유량 범위 확인* |
| 259 | **[조건]** `mbPICVValid`(지금 보는 밸브의 수신값을 믿을 수 있는지, TRUE면 유효) 값이 [TRUE(1)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 260 | &emsp;→&nbsp;PICV 4번 수신 이상 (`VP_FWU_PICV-4_Comm_Fault`) 값을 [FALSE(0)]로 바꾼다 (= 통신 정상) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 262 | &emsp;→&nbsp;**[조건]** `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [5] 이상<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 263 | &emsp;&emsp;→&nbsp;`mbAllClosed`(네 밸브가 모두 닫혔는지, TRUE면 모두 닫힘) 값을 [FALSE(0)]로 바꾼다 |
| 264 | &emsp;→&nbsp;**[아니면]** 262행 조건의 반대 상황, 즉 `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [5]보다 작음<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 265 | &emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 267 | &emsp;→&nbsp;*[주석] 위치 제어 모드에서만 명령과 실제 개도를 비교한다.* |
| 268 | &emsp;→&nbsp;`bValveFault`(지금 보는 밸브를 고장으로 볼지, TRUE면 고장) 값을 [FALSE(0)]로 바꾼다 |
| 269 | &emsp;→&nbsp;**[조건]** 밸브 제어 모드(0 미확정, 1 위치, 2 유량) (`VP_FWU_PICV_Control_Mode`) 값이 [1]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다<br>*[주석] 좌변이 boolean인가? (?)* |
| 270 | &emsp;&emsp;→&nbsp;**[조건]** PICV 공통 개도 명령(AO) (`FWU_PICV_CONTROL`) 값이 [`mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) - `POS_HYST`(= 30, 개도의 히스테리시스는 +/-30% 까지)]보다 크고 [`mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) + `POS_HYST`(= 30, 개도의 히스테리시스는 +/-30% 까지)]보다 작음<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 271 | &emsp;&emsp;&emsp;→&nbsp;타이머 7번 `PICV_4_DEVIATION_TIMER`(PICV 4번 명령과 실제 개도가 크게 다른 상태가 이어진 시간)를 0으로 되돌린다. 이 시점부터 시간을 새로 잰다 |
| 272 | &emsp;&emsp;→&nbsp;**[아니면]** 270행 조건의 반대 상황, 즉 PICV 공통 개도 명령(AO) (`FWU_PICV_CONTROL`) 값이 [`mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) - `POS_HYST`(= 30, 개도의 히스테리시스는 +/-30% 까지)]~[`mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) + `POS_HYST`(= 30, 개도의 히스테리시스는 +/-30% 까지)] 범위 밖임<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 273 | &emsp;&emsp;&emsp;→&nbsp;**[조건]** 타이머 7번 `PICV_4_DEVIATION_TIMER`(PICV 4번 명령과 실제 개도가 크게 다른 상태가 이어진 시간)으로 잰 시간(초)이 [`DEV_TIME_OUT`(= 40, deviation timer는 40초 까지)]초보다 김<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 274 | &emsp;&emsp;&emsp;&emsp;→&nbsp;`bValveFault`(지금 보는 밸브를 고장으로 볼지, TRUE면 고장) 값을 [TRUE(1)]로 바꾼다 |
| 275 | &emsp;&emsp;&emsp;→&nbsp;**[아니면]** 273행 조건의 반대 상황, 즉 타이머 7번 `PICV_4_DEVIATION_TIMER`(PICV 4번 명령과 실제 개도가 크게 다른 상태가 이어진 시간)으로 잰 시간(초)이 아직 [`DEV_TIME_OUT`(= 40, deviation timer는 40초 까지)]초를 넘지 않음<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 276 | &emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 277 | &emsp;→&nbsp;**[아니면]** 269행 조건의 반대 상황, 즉 밸브 제어 모드(0 미확정, 1 위치, 2 유량) (`VP_FWU_PICV_Control_Mode`) 값이 [1]이 아님<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 278 | &emsp;&emsp;→&nbsp;타이머 7번 `PICV_4_DEVIATION_TIMER`(PICV 4번 명령과 실제 개도가 크게 다른 상태가 이어진 시간)를 0으로 되돌린다. 이 시점부터 시간을 새로 잰다 |
| 280 | &emsp;→&nbsp;*[주석] 유량 기준 30/10 LPM은 밸브별 설계 유량 확인 후 감시를 켤 것.* |
| 281 | &emsp;→&nbsp;**[조건]** `mbPICVFlowChkEnable`(밸브 유량 감시를 하는지, TRUE면 함) 값이 [TRUE(1)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 282 | &emsp;&emsp;→&nbsp;`PICVCurrFlow`(지금 보는 밸브의 현재 유량)에 PICV 4번 유량 표시값 (`VP_FWU_PICV-4_Flow`) 값을 읽어 넣는다 |
| 283 | &emsp;&emsp;→&nbsp;**[조건]** 다음이 **모두** 맞음<br>① `mbCHWSCondi`(냉수 공급이 정상인지, TRUE면 정상) 값이 [TRUE(1)]임<br>② `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [`POS_OPEN`(= 30, 30% 이상 열리면 PICV가 "충분히" 열린 것으로 판단)]보다 큼<br>③ `PICVCurrFlow`(지금 보는 밸브의 현재 유량) 값이 [`NO_FLOW`(설정값: '유량없음'으로 판단하는 최소 유량)]보다 작음<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 284 | &emsp;&emsp;&emsp;→&nbsp;`bValveFault`(지금 보는 밸브를 고장으로 볼지, TRUE면 고장) 값을 [TRUE(1)]로 바꾼다 |
| 285 | &emsp;&emsp;→&nbsp;**[아니면]** 283행 조건의 반대 상황, 즉 아래 조건 중 **하나라도 맞지 않음**<br>① `mbCHWSCondi`(냉수 공급이 정상인지, TRUE면 정상) 값이 [TRUE(1)]임<br>② `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [`POS_OPEN`(= 30, 30% 이상 열리면 PICV가 "충분히" 열린 것으로 판단)]보다 큼<br>③ `PICVCurrFlow`(지금 보는 밸브의 현재 유량) 값이 [`NO_FLOW`(설정값: '유량없음'으로 판단하는 최소 유량)]보다 작음<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 286 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 288 | &emsp;&emsp;→&nbsp;**[조건]** 다음이 **모두** 맞음<br>① `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [1]보다 작음<br>② `PICVCurrFlow`(지금 보는 밸브의 현재 유량) 값이 [`LEAK_FLOW`(설정값: leak로 판단하는 유량 (?))]보다 큼<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 289 | &emsp;&emsp;&emsp;→&nbsp;`bValveFault`(지금 보는 밸브를 고장으로 볼지, TRUE면 고장) 값을 [TRUE(1)]로 바꾼다 |
| 290 | &emsp;&emsp;→&nbsp;**[아니면]** 288행 조건의 반대 상황, 즉 아래 조건 중 **하나라도 맞지 않음**<br>① `mPICVCurrPos`(지금 보는 밸브의 현재 개도(%)) 값이 [1]보다 작음<br>② `PICVCurrFlow`(지금 보는 밸브의 현재 유량) 값이 [`LEAK_FLOW`(설정값: leak로 판단하는 유량 (?))]보다 큼<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 291 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 292 | &emsp;→&nbsp;**[아니면]** 281행 조건의 반대 상황, 즉 `mbPICVFlowChkEnable`(밸브 유량 감시를 하는지, TRUE면 함) 값이 [FALSE(0)]임<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 293 | &emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 295 | &emsp;→&nbsp;PICV 4번 밸브 알람 (`VP_FWU_PICV-4_Alarm`) 값을 [`bValveFault`(지금 보는 밸브를 고장으로 볼지, TRUE면 고장)]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 296 | **[아니면]** 259행 조건의 반대 상황, 즉 `mbPICVValid`(지금 보는 밸브의 수신값을 믿을 수 있는지, TRUE면 유효) 값이 [FALSE(0)]임<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 297 | &emsp;→&nbsp;`mbAllClosed`(네 밸브가 모두 닫혔는지, TRUE면 모두 닫힘) 값을 [FALSE(0)]로 바꾼다 |
| 298 | &emsp;→&nbsp;`mbMonitorReady`(밸브 감시가 준비됐는지, TRUE면 준비됨) 값을 [FALSE(0)]로 바꾼다 |
| 299 | &emsp;→&nbsp;`mbAnyCommFault`(밸브 수신 이상이 하나라도 있는지, TRUE면 있음) 값을 [TRUE(1)]로 바꾼다 |
| 300 | &emsp;→&nbsp;PICV 4번 수신 이상 (`VP_FWU_PICV-4_Comm_Fault`) 값을 [TRUE(1)]로 바꾼다 (= 통신 이상) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 301 | &emsp;→&nbsp;PICV 4번 밸브 알람 (`VP_FWU_PICV-4_Alarm`)을 켠다 — 값 [TRUE(1)] (= 알람 걸림) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 302 | &emsp;→&nbsp;타이머 7번 `PICV_4_DEVIATION_TIMER`(PICV 4번 명령과 실제 개도가 크게 다른 상태가 이어진 시간)를 0으로 되돌린다. 이 시점부터 시간을 새로 잰다 |
| 304 | **[조건]** PICV 4번 밸브 알람 (`VP_FWU_PICV-4_Alarm`) 값이 [TRUE(1)]임 (= 알람 걸림)<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 305 | &emsp;→&nbsp;`mbAnyFault`(밸브 알람이 하나라도 있는지, TRUE면 있음) 값을 [TRUE(1)]로 바꾼다 |
| 306 | **[아니면]** 304행 조건의 반대 상황, 즉 PICV 4번 밸브 알람 (`VP_FWU_PICV-4_Alarm`) 값이 [TRUE(1)]이 아님 (= 알람 없음)<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 307 | &emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |

<a id="section-10"></a>

## 309~313행 · 모니터링 flag setting

| 행 | 해석 |
|---:|---|
| 309 | *[주석] 모니터링 flag setting* |
| 310 | **[조건]** 다음 중 **하나라도** 맞음<br>① 밸브 제어 모드(0 미확정, 1 위치, 2 유량) (`VP_FWU_PICV_Control_Mode`) 값이 [0]임<br>② `mbPICVFlowChkEnable`(밸브 유량 감시를 하는지, TRUE면 함) 값이 [FALSE(0)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다<br>*[주석] 좌변의 첫번째 term이 boolean인가? (?)* |
| 311 | &emsp;→&nbsp;`mbMonitorReady`(밸브 감시가 준비됐는지, TRUE면 준비됨) 값을 [0]로 바꾼다 |
| 312 | **[아니면]** 310행 조건의 반대 상황, 즉 아래가 **모두** 맞음 (원래 조건이 하나도 맞지 않음)<br>① 밸브 제어 모드(0 미확정, 1 위치, 2 유량) (`VP_FWU_PICV_Control_Mode`) 값이 [0]이 아님<br>② `mbPICVFlowChkEnable`(밸브 유량 감시를 하는지, TRUE면 함) 값이 [FALSE(0)]이 아님<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 313 | &emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |

<a id="section-11"></a>

## 315~320행 · PICV 상태, 유량 등의 정보를 VP_...에 업데이트

| 행 | 해석 |
|---:|---|
| 315 | *[주석] PICV 상태, 유량 등의 정보를 VP_...에 업데이트* |
| 316 | 네 밸브 모두 닫힘 표시 (`VP_FWU_PICV_All_Closed`) 값을 [`mbAllClosed`(네 밸브가 모두 닫혔는지, TRUE면 모두 닫힘)]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 317 | 밸브 감시 준비 표시 (`VP_FWU_PICV_Monitor_Ready`) 값을 [`mbMonitorReady`(밸브 감시가 준비됐는지, TRUE면 준비됨)]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 318 | PICV 알람 종합 (`VP_FWU_PICV_Alarm`) 값을 [`mbAnyFault`(밸브 알람이 하나라도 있는지, TRUE면 있음)]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 319 | PICV 수신 이상 종합 (`VP_FWU_Flow_Comm_Fault`) 값을 [`mbAnyCommFault`(밸브 수신 이상이 하나라도 있는지, TRUE면 있음)]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 320 | *[주석] LJH 2026-11-17 수정 구간 끝. 주제 = 밸브별 수신 유효성 및 닫힘 확인* |
