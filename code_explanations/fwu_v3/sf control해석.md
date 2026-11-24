# SF Control 줄별 해석

> **대상 코드** : `fwu_v3/Logic/SF Control.py` (297 줄)  
> **기준** : `sy 브랜치 2026-11-24 (댐퍼 설치 여부 설정 반영)`  
> **행** = 코드 줄 번호 (빈 줄은 생략)  
> **표기** : `→` 들여쓰기 단계 · *[주석]* 코드 안 주석 · `이름` 코드 안 상수·변수 · **※** 읽을 때 주의할 점

팬 제어 기준(고정속도·RAT·RDP·ΔT·CZT)에 따라 팬 속도를 정하고, 댐퍼·밸브와 연계해 기동과 정지를 한다. 5초마다 팬 목표 RPM(팬 통신 이상 시 AO)을 내보낸다.

**목차**

- [1~39행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수](#section-1)
- [41~56행 · 고정속도로 돌릴지 판단](#section-2)
- [58~67행 · 온도 센서 고장 시 대체 운전: RAT 모드는 RAT 고장, ΔT 모드는 RAT·SAT 중 하나라도 고장이면 고정속도](#section-3)
- [69~86행 · 상위(BMS/PLC) 통신이 끊겼을 때](#section-4)
- [88~239행 · 비상정지가 아닐 때](#section-5)
- [241~259행 · 팬 운전 명령: 속도 값이 있으면 8대 모두 운전](#section-6)
- [261~297행 · 팬 속도 출력 (5초마다)](#section-7)

**※ 읽는 법**

- **[조건]** 줄은 조건이 맞을 때만 바로 아래 한 칸 더 들여쓴(→가 하나 더 붙은) 줄들을 실행한다. **[아니면]** 줄은 그 조건이 맞지 않을 때 실행하는 부분이다.
- 값은 [ ] 안에 적었다. TRUE·ON·SET·TMR_READ·DEC = 1, FALSE·OFF·CLEAR·TMR_CLEAR·INC = 0 이다. 0/1 값 옆 (= …)은 그 관제점에서 0/1이 뜻하는 상태다.
- **우선순위 칸**: 관제점 하나에 번호가 붙은 여러 칸이 있고, **숫자가 작은 칸의 값이 이긴다**. 1 = 비상정지, 2 = 원격·화재 정지, 5 = 일반 로직(번호 없이 쓰는 `WRITEPOINT`), 11 = 값 보관·정지 요청. 칸을 지우면(해제) 그다음 칸의 값이 적용된다.
- 조건이 맞지 않는다고 관제점이 저절로 0이 되지는 않는다. 그 분기에 쓰는 줄이 없으면 **이전 값이 그대로 남는다**.
- 타이머는 0으로 되돌린 순간부터 흐른 시간(초)을 잰다. 대문자 이름은 상수, `m`으로 시작하는 이름은 이 파일 전체에서 쓰는 변수, 이름에 `b`가 붙은 변수는 TRUE/FALSE 값이다.

<a id="section-1"></a>

## 1~39행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수

| 행 | 해석 |
|---:|---|
| 1 | *[주석] LJH 2026-11-17 수정 구간 시작. 주제 = 온도 센서 고장 시 대체운전, 네 밸브 닫힘과 팬 정지 연계* |
| 2 | *[주석] JSY 2026-11-23 수정 구간 시작. 주제 = Coding Rule 적용(매크로 상수, 설정값 상수, 변수명, if-else 짝 맞춤, 주석)* |
| 4 | *[주석] 로직엔진 loading* |
| 5 | DDC 로직 엔진을 불러온다. 이 아래에서 `engine.READPOINT`(관제점 읽기), `engine.WRITEPOINT`(관제점 쓰기) 같은 기능을 이 이름으로 쓴다 |
| 7 | *[주석] Macro상수 정의* |
| 8 | 매크로 상수 정의: TMR_READ, SET, ON, TRUE, DEC를 모두 숫자 1으로 정한다. 코드에서 숫자 1 대신 뜻이 보이는 이름으로 쓰기 위한 것이다 (타이머 읽기·켜짐·참·DEC 방향처럼 '긍정' 또는 1을 뜻하는 인자) |
| 9 | 매크로 상수 정의: TMR_CLEAR, CLEAR, OFF, FALSE, INC를 모두 숫자 0으로 정한다. 코드에서 숫자 0 대신 뜻이 보이는 이름으로 쓰기 위한 것이다 (타이머 초기화·꺼짐·거짓·INC 방향처럼 '부정' 또는 0을 뜻하는 인자) |
| 11 | *[주석] DEC/INC는 LOOP2 제어 방향 (DEC: 현재값을 내리는 제어, INC: 현재값을 올리는 제어)* |
| 12 | PI 루프 번호에 이름 붙이기: `RAT_LOOP` = 1번. LOOP2 번호: RAT 기준 제어 |
| 13 | PI 루프 번호에 이름 붙이기: `RDP_LOOP` = 2번. LOOP2 번호: RDP 기준 제어 |
| 14 | PI 루프 번호에 이름 붙이기: `DELTA_T_LOOP` = 3번. LOOP2 번호: ΔT(RAT-SAT) 기준 제어 |
| 15 | PI 루프 번호에 이름 붙이기: `CZT_LOOP` = 4번. LOOP2 번호: CZT 기준 제어 |
| 16 | 설정값 상수 `SF_CONTROL_SELECT`: 팬 제어 기준 선택(0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT) (`VP_FWU_SF_Control_Select`) 값을 이 로직이 실행될 때마다 한 번 읽어 이 이름에 담아 둔다. 뜻: 팬 제어 기준. 0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT |
| 17 | 설정값 상수 `RAT_PGAIN`: 팬 RAT 기준 제어 P 게인 (`VP_FWU_SF_RAT_PGain`) 값을 이 로직이 실행될 때마다 한 번 읽어 이 이름에 담아 둔다. 뜻: RAT 기준 팬 제어 P 게인 |
| 18 | 설정값 상수 `RAT_IGAIN`: 팬 RAT 기준 제어 I 게인 (`VP_FWU_SF_RAT_IGain`) 값을 이 로직이 실행될 때마다 한 번 읽어 이 이름에 담아 둔다. 뜻: RAT 기준 팬 제어 I 게인 |
| 19 | 설정값 상수 `RDP_PGAIN`: 팬 RDP 기준 제어 P 게인 (`VP_FWU_SF_RDP_PGain`) 값을 이 로직이 실행될 때마다 한 번 읽어 이 이름에 담아 둔다. 뜻: RDP 기준 팬 제어 P 게인 |
| 20 | 설정값 상수 `RDP_IGAIN`: 팬 RDP 기준 제어 I 게인 (`VP_FWU_SF_RDP_IGain`) 값을 이 로직이 실행될 때마다 한 번 읽어 이 이름에 담아 둔다. 뜻: RDP 기준 팬 제어 I 게인 |
| 21 | 설정값 상수 `DELTAT_PGAIN`: 팬 ΔT 기준 제어 P 게인 (`VP_FWU_SF_DeltaT_PGain`) 값을 이 로직이 실행될 때마다 한 번 읽어 이 이름에 담아 둔다. 뜻: ΔT 기준 팬 제어 P 게인 |
| 22 | 설정값 상수 `DELTAT_IGAIN`: 팬 ΔT 기준 제어 I 게인 (`VP_FWU_SF_DeltaT_IGain`) 값을 이 로직이 실행될 때마다 한 번 읽어 이 이름에 담아 둔다. 뜻: ΔT 기준 팬 제어 I 게인 |
| 23 | 설정값 상수 `CZT_PGAIN`: 팬 CZT 기준 제어 P 게인 (`VP_FWU_SF_CZT_PGain`) 값을 이 로직이 실행될 때마다 한 번 읽어 이 이름에 담아 둔다. 뜻: CZT 기준 팬 제어 P 게인 |
| 24 | 설정값 상수 `CZT_IGAIN`: 팬 CZT 기준 제어 I 게인 (`VP_FWU_SF_CZT_IGain`) 값을 이 로직이 실행될 때마다 한 번 읽어 이 이름에 담아 둔다. 뜻: CZT 기준 팬 제어 I 게인 |
| 25 | 설정값 상수 `SAD_INSTALLED`: 댐퍼 설치 여부 설정(0 없음, 1 있음) (`VP_FWU_SAD_Installed`) 값을 이 로직이 실행될 때마다 한 번 읽어 이 이름에 담아 둔다. 뜻: 댐퍼 설치 여부 (옵션 부품). 0 = 없음, 1 = 있음 |
| 27 | *[주석] 타이머 정의* |
| 28 | 타이머 번호에 이름 붙이기: `SPEED_OUTPUT_TIMER` = 타이머 1번. 이 타이머로 '팬 속도를 마지막으로 내보낸 뒤 지난 시간'을 잰다 (한 로직에서 타이머는 0~9번 10개까지) |
| 30 | *[주석] 전역변수 선언* |
| 31 | 전역변수 `mbFixed`(PI 대신 고정속도로 돌릴지, TRUE면 고정속도)를 만들고 처음 값을 [FALSE(0)]로 둔다. 이 로직이 실행될 때마다 이 값에서 다시 시작한다<br>*[주석] TRUE면 PI 제어 대신 고정속도(Speed_SP)로 돈다* |
| 32 | 전역변수 `mbBMSFail`(상위 통신이 끊겨 끊김 설정대로 돌지, TRUE면 그렇게 함)를 만들고 처음 값을 [FALSE(0)]로 둔다. 이 로직이 실행될 때마다 이 값에서 다시 시작한다<br>*[주석] TRUE면 상위 통신이 끊겨 Comm_Fail_Mode 설정대로 돈다* |
| 34 | *[주석] 모드 UI는 정수 0~4만 전송. 직접 쓰기를 허용하면 별도 값 검증 필요.* |
| 35 | *[주석] 수동 속도는 코드 제한 없음. HMI에서 정지 0 또는 최소~최대 속도만 허용.* |
| 36 | *[주석] HMI에서 최소 <= 최대를 확인할 것. 최소 속도 기본값 20% (QTS RFP 2.3.D.3, JSY 2026-11-24 30%→20%).* |
| 37 | *[주석] ΔT 목표 -2℃는 SMX01 기준 임시값. 양의 RAT-SAT 운전에서 최대속도에 머물 수 있어 재확인.* |
| 38 | *[주석] 정상 정지는 네 밸브 닫힘까지 대기. 미폐쇄 제한시간/대체 정지 정책은 추후 검토.* |
| 39 | *[주석] 팬 통신 이상 시 전체 AO 전환. 새 팬의 Run·AO/RPM 우선권·환산·복구 동작 확인.* |

<a id="section-2"></a>

## 41~56행 · 고정속도로 돌릴지 판단

> 고정속도(0)를 골랐거나, 고른 제어 기준의 센서값을 쓸 수 없으면 고정속도로 돈다

| 행 | 해석 |
|---:|---|
| 41 | *[주석] 고정속도로 돌릴지 판단* |
| 42 | *[주석] 고정속도(0)를 골랐거나, 고른 제어 기준의 센서값을 쓸 수 없으면 고정속도로 돈다* |
| 43 | **[조건]** `SF_CONTROL_SELECT`(설정값: 팬 제어 기준. 0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT) 값이 [0] 이상이고 [1]보다 작음<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 44 | &emsp;→&nbsp;`mbFixed`(PI 대신 고정속도로 돌릴지, TRUE면 고정속도) 값을 [TRUE(1)]로 바꾼다 |
| 45 | **[아니면]** 43행 조건의 반대 상황, 즉 `SF_CONTROL_SELECT`(설정값: 팬 제어 기준. 0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT) 값이 [0]~[1] 범위 밖임<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 46 | &emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 48 | **[조건]** 다음이 **모두** 맞음<br>① `SF_CONTROL_SELECT`(설정값: 팬 제어 기준. 0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT) 값이 [2] 이상이고 [3]보다 작음<br>② 룸 차압 제어용 값 유효 표시 (`VP_FWU_RDP_PV_Valid`) 값이 [FALSE(0)]임 (= 무효, 쓸 수 없음)<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 49 | &emsp;→&nbsp;`mbFixed`(PI 대신 고정속도로 돌릴지, TRUE면 고정속도) 값을 [TRUE(1)]로 바꾼다 |
| 50 | **[아니면]** 48행 조건의 반대 상황, 즉 아래 조건 중 **하나라도 맞지 않음**<br>① `SF_CONTROL_SELECT`(설정값: 팬 제어 기준. 0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT) 값이 [2] 이상이고 [3]보다 작음<br>② 룸 차압 제어용 값 유효 표시 (`VP_FWU_RDP_PV_Valid`) 값이 [FALSE(0)]임 (= 무효, 쓸 수 없음)<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 51 | &emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 53 | **[조건]** 다음이 **모두** 맞음<br>① `SF_CONTROL_SELECT`(설정값: 팬 제어 기준. 0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT) 값이 [4] 이상이고 [5]보다 작음<br>② 냉복도 온도 제어용 값 유효 표시 (`VP_FWU_CZT_PV_Valid`) 값이 [FALSE(0)]임 (= 무효, 쓸 수 없음)<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 54 | &emsp;→&nbsp;`mbFixed`(PI 대신 고정속도로 돌릴지, TRUE면 고정속도) 값을 [TRUE(1)]로 바꾼다 |
| 55 | **[아니면]** 53행 조건의 반대 상황, 즉 아래 조건 중 **하나라도 맞지 않음**<br>① `SF_CONTROL_SELECT`(설정값: 팬 제어 기준. 0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT) 값이 [4] 이상이고 [5]보다 작음<br>② 냉복도 온도 제어용 값 유효 표시 (`VP_FWU_CZT_PV_Valid`) 값이 [FALSE(0)]임 (= 무효, 쓸 수 없음)<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 56 | &emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |

<a id="section-3"></a>

## 58~67행 · 온도 센서 고장 시 대체 운전: RAT 모드는 RAT 고장, ΔT 모드는 RAT·SAT 중 하나라도 고장이면 고정속도

| 행 | 해석 |
|---:|---|
| 58 | *[주석] 온도 센서 고장 시 대체 운전: RAT 모드는 RAT 고장, ΔT 모드는 RAT·SAT 중 하나라도 고장이면 고정속도* |
| 59 | **[조건]** 다음이 **모두** 맞음<br>① `SF_CONTROL_SELECT`(설정값: 팬 제어 기준. 0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT) 값이 [1] 이상이고 [2]보다 작음<br>② 환기 온도(RAT) 센서 고장 알람 (`VP_FWU_RAT_Failure_Alarm`) 값이 [TRUE(1)]임 (= 알람 걸림)<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 60 | &emsp;→&nbsp;`mbFixed`(PI 대신 고정속도로 돌릴지, TRUE면 고정속도) 값을 [TRUE(1)]로 바꾼다 |
| 61 | **[아니면]** 59행 조건의 반대 상황, 즉 아래 조건 중 **하나라도 맞지 않음**<br>① `SF_CONTROL_SELECT`(설정값: 팬 제어 기준. 0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT) 값이 [1] 이상이고 [2]보다 작음<br>② 환기 온도(RAT) 센서 고장 알람 (`VP_FWU_RAT_Failure_Alarm`) 값이 [TRUE(1)]임 (= 알람 걸림)<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 62 | &emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 64 | **[조건]** 다음이 **모두** 맞음<br>① `SF_CONTROL_SELECT`(설정값: 팬 제어 기준. 0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT) 값이 [3] 이상이고 [4]보다 작음<br>② (환기 온도(RAT) 센서 고장 알람 (`VP_FWU_RAT_Failure_Alarm`) 값이 [TRUE(1)]임 (= 알람 걸림) **또는** 급기 온도(SAT) 센서 고장 알람 (`VP_FWU_SAT_Failure_Alarm`) 값이 [TRUE(1)]임 (= 알람 걸림))<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 65 | &emsp;→&nbsp;`mbFixed`(PI 대신 고정속도로 돌릴지, TRUE면 고정속도) 값을 [TRUE(1)]로 바꾼다 |
| 66 | **[아니면]** 64행 조건의 반대 상황, 즉 아래 조건 중 **하나라도 맞지 않음**<br>① `SF_CONTROL_SELECT`(설정값: 팬 제어 기준. 0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT) 값이 [3] 이상이고 [4]보다 작음<br>② (환기 온도(RAT) 센서 고장 알람 (`VP_FWU_RAT_Failure_Alarm`) 값이 [TRUE(1)]임 (= 알람 걸림) **또는** 급기 온도(SAT) 센서 고장 알람 (`VP_FWU_SAT_Failure_Alarm`) 값이 [TRUE(1)]임 (= 알람 걸림))<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 67 | &emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |

<a id="section-4"></a>

## 69~86행 · 상위(BMS/PLC) 통신이 끊겼을 때

> 상위 값을 쓰는 RDP·CZT 모드, 또는 원격 선택 상태의 고정속도 모드는 Comm_Fail_Mode 설정을 따른다

| 행 | 해석 |
|---:|---|
| 69 | *[주석] 상위(BMS/PLC) 통신이 끊겼을 때* |
| 70 | *[주석] 상위 값을 쓰는 RDP·CZT 모드, 또는 원격 선택 상태의 고정속도 모드는 Comm_Fail_Mode 설정을 따른다* |
| 71 | **[조건]** 다음이 **모두** 맞음<br>① 상위 통신 감시 사용 설정 (`VP_FWU_Upper_Comm_Enable`) 값이 [TRUE(1)]임 (= 상위 통신 감시 사용)<br>② 상위(BMS/PLC) 통신 이상 (`VP_FWU_BMS_PLC_Comm_Fault`) 값이 [TRUE(1)]임 (= 통신 이상)<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 72 | &emsp;→&nbsp;**[조건]** 다음 중 **하나라도** 맞음<br>① `SF_CONTROL_SELECT`(설정값: 팬 제어 기준. 0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT) 값이 [2] 이상이고 [3]보다 작음<br>② `SF_CONTROL_SELECT`(설정값: 팬 제어 기준. 0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT) 값이 [4] 이상이고 [5]보다 작음<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 73 | &emsp;&emsp;→&nbsp;`mbBMSFail`(상위 통신이 끊겨 끊김 설정대로 돌지, TRUE면 그렇게 함) 값을 [TRUE(1)]로 바꾼다 |
| 74 | &emsp;→&nbsp;**[아니면]** 72행 조건의 반대 상황, 즉 아래가 **모두** 맞음 (원래 조건이 하나도 맞지 않음)<br>① `SF_CONTROL_SELECT`(설정값: 팬 제어 기준. 0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT) 값이 [2]~[3] 범위 밖임<br>② `SF_CONTROL_SELECT`(설정값: 팬 제어 기준. 0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT) 값이 [4]~[5] 범위 밖임<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 75 | &emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 76 | &emsp;→&nbsp;**[조건]** 다음이 **모두** 맞음<br>① `SF_CONTROL_SELECT`(설정값: 팬 제어 기준. 0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT) 값이 [0] 이상이고 [1]보다 작음<br>② 원격(BMS) 선택 입력(DI) (`REMOTE_SELECTION`) 값이 [TRUE(1)]임 (= 원격(BMS) 선택)<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 77 | &emsp;&emsp;→&nbsp;`mbBMSFail`(상위 통신이 끊겨 끊김 설정대로 돌지, TRUE면 그렇게 함) 값을 [TRUE(1)]로 바꾼다 |
| 78 | &emsp;→&nbsp;**[아니면]** 76행 조건의 반대 상황, 즉 아래 조건 중 **하나라도 맞지 않음**<br>① `SF_CONTROL_SELECT`(설정값: 팬 제어 기준. 0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT) 값이 [0] 이상이고 [1]보다 작음<br>② 원격(BMS) 선택 입력(DI) (`REMOTE_SELECTION`) 값이 [TRUE(1)]임 (= 원격(BMS) 선택)<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 79 | &emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 80 | **[아니면]** 71행 조건의 반대 상황, 즉 아래 조건 중 **하나라도 맞지 않음**<br>① 상위 통신 감시 사용 설정 (`VP_FWU_Upper_Comm_Enable`) 값이 [TRUE(1)]임 (= 상위 통신 감시 사용)<br>② 상위(BMS/PLC) 통신 이상 (`VP_FWU_BMS_PLC_Comm_Fault`) 값이 [TRUE(1)]임 (= 통신 이상)<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 81 | &emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 83 | **[조건]** `mbBMSFail`(상위 통신이 끊겨 끊김 설정대로 돌지, TRUE면 그렇게 함) 값이 [TRUE(1)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 84 | &emsp;→&nbsp;`mbFixed`(PI 대신 고정속도로 돌릴지, TRUE면 고정속도) 값을 [FALSE(0)]로 바꾼다 |
| 85 | **[아니면]** 83행 조건의 반대 상황, 즉 `mbBMSFail`(상위 통신이 끊겨 끊김 설정대로 돌지, TRUE면 그렇게 함) 값이 [TRUE(1)]이 아님<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 86 | &emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |

<a id="section-5"></a>

## 88~239행 · 비상정지가 아닐 때

| 행 | 해석 |
|---:|---|
| 88 | *[주석] 비상정지가 아닐 때* |
| 89 | **[조건]** 비상정지 입력(DI) (`FWU_EMERGENCY`) 값이 [FALSE(0)]임 (= 정상, 비상정지 아님)<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 90 | &emsp;→&nbsp;*[주석] 비상정지 때 걸어 둔 P1 해제* |
| 91 | &emsp;→&nbsp;팬 1~4번 속도 AO 출력 (`FWU_SF-1_4_SPEED_CONTROL`)의 우선순위 1 칸(비상정지가 쓰는 칸, 가장 강함)에 써 둔 값을 지운다. 그 칸이 비면 그다음 칸(숫자가 더 큰 칸)에 있는 값이 적용된다<br>*[주석] FWU_SF-1_8_SPEED_CONTROL로 합쳐도 됨 (기존 배선이 1~4, 5~8로 나뉘어 있음)* |
| 92 | &emsp;→&nbsp;팬 5~8번 속도 AO 출력 (`FWU_SF-5_8_SPEED_CONTROL`)의 우선순위 1 칸(비상정지가 쓰는 칸, 가장 강함)에 써 둔 값을 지운다. 그 칸이 비면 그다음 칸(숫자가 더 큰 칸)에 있는 값이 적용된다 |
| 93 | &emsp;→&nbsp;팬 1번 목표 RPM (`FWU_SF-1.Target_RPM_Set`)의 우선순위 1 칸(비상정지가 쓰는 칸, 가장 강함)에 써 둔 값을 지운다. 그 칸이 비면 그다음 칸(숫자가 더 큰 칸)에 있는 값이 적용된다 |
| 94 | &emsp;→&nbsp;팬 2번 목표 RPM (`FWU_SF-2.Target_RPM_Set`)의 우선순위 1 칸(비상정지가 쓰는 칸, 가장 강함)에 써 둔 값을 지운다. 그 칸이 비면 그다음 칸(숫자가 더 큰 칸)에 있는 값이 적용된다 |
| 95 | &emsp;→&nbsp;팬 3번 목표 RPM (`FWU_SF-3.Target_RPM_Set`)의 우선순위 1 칸(비상정지가 쓰는 칸, 가장 강함)에 써 둔 값을 지운다. 그 칸이 비면 그다음 칸(숫자가 더 큰 칸)에 있는 값이 적용된다 |
| 96 | &emsp;→&nbsp;팬 4번 목표 RPM (`FWU_SF-4.Target_RPM_Set`)의 우선순위 1 칸(비상정지가 쓰는 칸, 가장 강함)에 써 둔 값을 지운다. 그 칸이 비면 그다음 칸(숫자가 더 큰 칸)에 있는 값이 적용된다 |
| 97 | &emsp;→&nbsp;팬 5번 목표 RPM (`FWU_SF-5.Target_RPM_Set`)의 우선순위 1 칸(비상정지가 쓰는 칸, 가장 강함)에 써 둔 값을 지운다. 그 칸이 비면 그다음 칸(숫자가 더 큰 칸)에 있는 값이 적용된다 |
| 98 | &emsp;→&nbsp;팬 6번 목표 RPM (`FWU_SF-6.Target_RPM_Set`)의 우선순위 1 칸(비상정지가 쓰는 칸, 가장 강함)에 써 둔 값을 지운다. 그 칸이 비면 그다음 칸(숫자가 더 큰 칸)에 있는 값이 적용된다 |
| 99 | &emsp;→&nbsp;팬 7번 목표 RPM (`FWU_SF-7.Target_RPM_Set`)의 우선순위 1 칸(비상정지가 쓰는 칸, 가장 강함)에 써 둔 값을 지운다. 그 칸이 비면 그다음 칸(숫자가 더 큰 칸)에 있는 값이 적용된다 |
| 100 | &emsp;→&nbsp;팬 8번 목표 RPM (`FWU_SF-8.Target_RPM_Set`)의 우선순위 1 칸(비상정지가 쓰는 칸, 가장 강함)에 써 둔 값을 지운다. 그 칸이 비면 그다음 칸(숫자가 더 큰 칸)에 있는 값이 적용된다 |
| 101 | &emsp;→&nbsp;댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`)의 우선순위 1 칸(비상정지가 쓰는 칸, 가장 강함)에 써 둔 값을 지운다. 그 칸이 비면 그다음 칸(숫자가 더 큰 칸)에 있는 값이 적용된다 |
| 103 | &emsp;→&nbsp;**[조건]** 운전 모드(1 자동, 0 수동) (`VP_FWU_Operation_Mode`) 값이 [TRUE(1)]임 (= 자동 운전)<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다<br>*[주석] Operation_Mode 1 = 자동, 0 = 수동* |
| 104 | &emsp;&emsp;→&nbsp;**[조건]** 운전 명령(BMS) (`VP_FWU_Command`) 값이 [ON(1)]임 (= 운전 명령)<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 105 | &emsp;&emsp;&emsp;→&nbsp;*[주석] JSY 2026-11-24 수정 구간 시작. 주제 = 댐퍼 설치 여부(옵션 부품) 반영* |
| 106 | &emsp;&emsp;&emsp;→&nbsp;*[주석] 운전: 댐퍼가 있으면 댐퍼부터 열고, 네 댐퍼가 모두 열린 뒤에 팬 속도를 정한다* |
| 107 | &emsp;&emsp;&emsp;→&nbsp;*[주석] 댐퍼가 없으면 댐퍼 명령을 내지 않고(OFF), 열림을 기다리지 않고 바로 팬 속도를 정한다* |
| 108 | &emsp;&emsp;&emsp;→&nbsp;**[조건]** `SAD_INSTALLED`(설정값: 댐퍼 설치 여부 (옵션 부품). 0 = 없음, 1 = 있음) 값이 [TRUE(1)]임 (= 댐퍼 있음)<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 109 | &emsp;&emsp;&emsp;&emsp;→&nbsp;댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`) 값을 [ON(1)]로 바꾼다 (= 댐퍼 열림 명령) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 110 | &emsp;&emsp;&emsp;&emsp;→&nbsp;`bSADReady`(팬 속도를 정해도 되는지, 댐퍼가 없거나 네 댐퍼가 모두 열렸으면 TRUE)에 판단 결과를 넣는다: 다음이 **모두** 맞음<br>① 댐퍼 1번 열림 접점 (`FWU_SAD-1_OPEN_STATUS`) 값이 [TRUE(1)]임 (= 열림 확인)<br>② 댐퍼 2번 열림 접점 (`FWU_SAD-2_OPEN_STATUS`) 값이 [TRUE(1)]임 (= 열림 확인)<br>③ 댐퍼 3번 열림 접점 (`FWU_SAD-3_OPEN_STATUS`) 값이 [TRUE(1)]임 (= 열림 확인)<br>④ 댐퍼 4번 열림 접점 (`FWU_SAD-4_OPEN_STATUS`) 값이 [TRUE(1)]임 (= 열림 확인)<br>→ 맞으면 TRUE(1), 아니면 FALSE(0)<br>*[주석] 네 댐퍼가 모두 열림* |
| 111 | &emsp;&emsp;&emsp;→&nbsp;**[아니면]** 108행 조건의 반대 상황, 즉 `SAD_INSTALLED`(설정값: 댐퍼 설치 여부 (옵션 부품). 0 = 없음, 1 = 있음) 값이 [TRUE(1)]이 아님 (= 댐퍼 없음)<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 112 | &emsp;&emsp;&emsp;&emsp;→&nbsp;댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`) 값을 [OFF(0)]로 바꾼다 (= 댐퍼 닫힘 명령) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 113 | &emsp;&emsp;&emsp;&emsp;→&nbsp;`bSADReady`(팬 속도를 정해도 되는지, 댐퍼가 없거나 네 댐퍼가 모두 열렸으면 TRUE) 값을 [TRUE(1)]로 바꾼다 |
| 114 | &emsp;&emsp;&emsp;→&nbsp;*[주석] JSY 2026-11-24 수정 구간 끝. 주제 = 댐퍼 설치 여부(옵션 부품) 반영* |
| 115 | &emsp;&emsp;&emsp;→&nbsp;**[조건]** `bSADReady`(팬 속도를 정해도 되는지, 댐퍼가 없거나 네 댐퍼가 모두 열렸으면 TRUE) 값이 [TRUE(1)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 116 | &emsp;&emsp;&emsp;&emsp;→&nbsp;*[주석] 고정속도: Speed_SP를 최소~최대 속도 안으로 맞춰서 쓴다* |
| 117 | &emsp;&emsp;&emsp;&emsp;→&nbsp;**[조건]** `mbFixed`(PI 대신 고정속도로 돌릴지, TRUE면 고정속도) 값이 [TRUE(1)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 118 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;`Speed`(고정속도로 쓸 팬 속도(임시, %))에 다음 계산값을 넣는다: [고정속도 설정값(%) (`VP_FWU_Speed_SP`), 팬 최소 속도(%) (`VP_FWU_SF_Speed_Min`)] 중 가장 큰 값 |
| 119 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;`Speed`(고정속도로 쓸 팬 속도(임시, %))에 다음 계산값을 넣는다: [`Speed`(고정속도로 쓸 팬 속도(임시, %)), 팬 최대 속도(%) (`VP_FWU_SF_Speed_Max`)] 중 가장 작은 값 |
| 120 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`) 값을 [`Speed`(고정속도로 쓸 팬 속도(임시, %))]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 121 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RAT_LOOP`(= 1, LOOP2 번호: RAT 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: RAT 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 122 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RDP_LOOP`(= 2, LOOP2 번호: RDP 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: RDP 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 123 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `DELTA_T_LOOP`(= 3, LOOP2 번호: ΔT(RAT-SAT) 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: ΔT(RAT-SAT) 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 124 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `CZT_LOOP`(= 4, LOOP2 번호: CZT 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: CZT 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 125 | &emsp;&emsp;&emsp;&emsp;→&nbsp;**[아니면]** 117행 조건의 반대 상황, 즉 `mbFixed`(PI 대신 고정속도로 돌릴지, TRUE면 고정속도) 값이 [TRUE(1)]이 아님<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 126 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 128 | &emsp;&emsp;&emsp;&emsp;→&nbsp;*[주석] LOOP2(방향, 현재값, 출력, 목표값, P, I, D, 샘플링(초), 시작 출력, 최소, 최대, 루프 번호, 데드밴드)* |
| 129 | &emsp;&emsp;&emsp;&emsp;→&nbsp;*[주석] RAT 기준: RAT가 목표보다 높으면 팬을 올린다 (DEC)* |
| 130 | &emsp;&emsp;&emsp;&emsp;→&nbsp;**[조건]** 다음이 **모두** 맞음<br>① `mbFixed`(PI 대신 고정속도로 돌릴지, TRUE면 고정속도) 값이 [FALSE(0)]임<br>② `SF_CONTROL_SELECT`(설정값: 팬 제어 기준. 0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT) 값이 [1] 이상이고 [2]보다 작음<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 131 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;**PI 자동 제어 실행**: 환기 온도(RAT) 센서값 (`FWU_RAT`)이(가) 환기 온도 목표값 (`VP_FWU_RAT_SP`)에 가까워지도록 팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`)을 계산해서 쓴다 — 우선순위 5 칸(일반 로직이 쓰는 칸)<br>· 방향 DEC: 현재값이 목표보다 **높으면 출력을 올린다** (예: 온도가 높으면 더 세게)<br>· 비례 게인 P = `RAT_PGAIN`(설정값: RAT 기준 팬 제어 P 게인), 적분 게인 I = `RAT_IGAIN`(설정값: RAT 기준 팬 제어 I 게인), 미분 D = 0 (0이면 안 씀)<br>· 계산 주기 = 0초 (0이면 기본 1초)<br>· 처음 시작할 때 출력 = 60<br>· 출력 범위 = 팬 최소 속도(%) (`VP_FWU_SF_Speed_Min`) ~ 팬 최대 속도(%) (`VP_FWU_SF_Speed_Max`) (이 범위 밖으로는 내보내지 않음)<br>· 루프 번호 = `RAT_LOOP`(= 1, LOOP2 번호: RAT 기준 제어) (LOOP2_INIT으로 이 제어를 초기화할 때 쓰는 번호)<br>· 데드밴드 = 0 (0이면 없음) |
| 132 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RDP_LOOP`(= 2, LOOP2 번호: RDP 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: RDP 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 133 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `DELTA_T_LOOP`(= 3, LOOP2 번호: ΔT(RAT-SAT) 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: ΔT(RAT-SAT) 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 134 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `CZT_LOOP`(= 4, LOOP2 번호: CZT 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: CZT 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 135 | &emsp;&emsp;&emsp;&emsp;→&nbsp;**[아니면]** 130행 조건의 반대 상황, 즉 아래 조건 중 **하나라도 맞지 않음**<br>① `mbFixed`(PI 대신 고정속도로 돌릴지, TRUE면 고정속도) 값이 [FALSE(0)]임<br>② `SF_CONTROL_SELECT`(설정값: 팬 제어 기준. 0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT) 값이 [1] 이상이고 [2]보다 작음<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 136 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 138 | &emsp;&emsp;&emsp;&emsp;→&nbsp;*[주석] RDP 기준: 차압이 목표보다 낮으면 팬을 올린다 (INC)* |
| 139 | &emsp;&emsp;&emsp;&emsp;→&nbsp;**[조건]** 다음이 **모두** 맞음<br>① `mbFixed`(PI 대신 고정속도로 돌릴지, TRUE면 고정속도) 값이 [FALSE(0)]임<br>② `mbBMSFail`(상위 통신이 끊겨 끊김 설정대로 돌지, TRUE면 그렇게 함) 값이 [FALSE(0)]임<br>③ `SF_CONTROL_SELECT`(설정값: 팬 제어 기준. 0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT) 값이 [2] 이상이고 [3]보다 작음<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 140 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;**PI 자동 제어 실행**: 룸 차압 제어용 값(PV) (`VP_FWU_RDP_PV`)이(가) 룸 차압 목표값 (`VP_FWU_RDP_SP`)에 가까워지도록 팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`)을 계산해서 쓴다 — 우선순위 5 칸(일반 로직이 쓰는 칸)<br>· 방향 INC: 현재값이 목표보다 **낮으면 출력을 올린다** (예: 차압이 낮으면 더 세게)<br>· 비례 게인 P = `RDP_PGAIN`(설정값: RDP 기준 팬 제어 P 게인), 적분 게인 I = `RDP_IGAIN`(설정값: RDP 기준 팬 제어 I 게인), 미분 D = 0 (0이면 안 씀)<br>· 계산 주기 = 0초 (0이면 기본 1초)<br>· 처음 시작할 때 출력 = 60<br>· 출력 범위 = 팬 최소 속도(%) (`VP_FWU_SF_Speed_Min`) ~ 팬 최대 속도(%) (`VP_FWU_SF_Speed_Max`) (이 범위 밖으로는 내보내지 않음)<br>· 루프 번호 = `RDP_LOOP`(= 2, LOOP2 번호: RDP 기준 제어) (LOOP2_INIT으로 이 제어를 초기화할 때 쓰는 번호)<br>· 데드밴드 = 0 (0이면 없음) |
| 141 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RAT_LOOP`(= 1, LOOP2 번호: RAT 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: RAT 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 142 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `DELTA_T_LOOP`(= 3, LOOP2 번호: ΔT(RAT-SAT) 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: ΔT(RAT-SAT) 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 143 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `CZT_LOOP`(= 4, LOOP2 번호: CZT 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: CZT 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 144 | &emsp;&emsp;&emsp;&emsp;→&nbsp;**[아니면]** 139행 조건의 반대 상황, 즉 아래 조건 중 **하나라도 맞지 않음**<br>① `mbFixed`(PI 대신 고정속도로 돌릴지, TRUE면 고정속도) 값이 [FALSE(0)]임<br>② `mbBMSFail`(상위 통신이 끊겨 끊김 설정대로 돌지, TRUE면 그렇게 함) 값이 [FALSE(0)]임<br>③ `SF_CONTROL_SELECT`(설정값: 팬 제어 기준. 0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT) 값이 [2] 이상이고 [3]보다 작음<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 145 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 147 | &emsp;&emsp;&emsp;&emsp;→&nbsp;*[주석] ΔT 기준* |
| 148 | &emsp;&emsp;&emsp;&emsp;→&nbsp;**[조건]** 다음이 **모두** 맞음<br>① `mbFixed`(PI 대신 고정속도로 돌릴지, TRUE면 고정속도) 값이 [FALSE(0)]임<br>② `SF_CONTROL_SELECT`(설정값: 팬 제어 기준. 0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT) 값이 [3] 이상이고 [4]보다 작음<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 149 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;**PI 자동 제어 실행**: ΔT(RAT-SAT) 현재값 (`VP_FWU_DeltaT_PV`)이(가) ΔT 목표값 (`VP_FWU_DeltaT_SP`)에 가까워지도록 팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`)을 계산해서 쓴다 — 우선순위 5 칸(일반 로직이 쓰는 칸)<br>· 방향 DEC: 현재값이 목표보다 **높으면 출력을 올린다** (예: 온도가 높으면 더 세게)<br>· 비례 게인 P = `DELTAT_PGAIN`(설정값: ΔT 기준 팬 제어 P 게인), 적분 게인 I = `DELTAT_IGAIN`(설정값: ΔT 기준 팬 제어 I 게인), 미분 D = 0 (0이면 안 씀)<br>· 계산 주기 = 0초 (0이면 기본 1초)<br>· 처음 시작할 때 출력 = 60<br>· 출력 범위 = 팬 최소 속도(%) (`VP_FWU_SF_Speed_Min`) ~ 팬 최대 속도(%) (`VP_FWU_SF_Speed_Max`) (이 범위 밖으로는 내보내지 않음)<br>· 루프 번호 = `DELTA_T_LOOP`(= 3, LOOP2 번호: ΔT(RAT-SAT) 기준 제어) (LOOP2_INIT으로 이 제어를 초기화할 때 쓰는 번호)<br>· 데드밴드 = 0 (0이면 없음) |
| 150 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RAT_LOOP`(= 1, LOOP2 번호: RAT 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: RAT 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 151 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RDP_LOOP`(= 2, LOOP2 번호: RDP 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: RDP 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 152 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `CZT_LOOP`(= 4, LOOP2 번호: CZT 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: CZT 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 153 | &emsp;&emsp;&emsp;&emsp;→&nbsp;**[아니면]** 148행 조건의 반대 상황, 즉 아래 조건 중 **하나라도 맞지 않음**<br>① `mbFixed`(PI 대신 고정속도로 돌릴지, TRUE면 고정속도) 값이 [FALSE(0)]임<br>② `SF_CONTROL_SELECT`(설정값: 팬 제어 기준. 0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT) 값이 [3] 이상이고 [4]보다 작음<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 154 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 156 | &emsp;&emsp;&emsp;&emsp;→&nbsp;*[주석] CZT 기준: 존 온도가 목표보다 높으면 팬을 올린다 (DEC)* |
| 157 | &emsp;&emsp;&emsp;&emsp;→&nbsp;**[조건]** 다음이 **모두** 맞음<br>① `mbFixed`(PI 대신 고정속도로 돌릴지, TRUE면 고정속도) 값이 [FALSE(0)]임<br>② `mbBMSFail`(상위 통신이 끊겨 끊김 설정대로 돌지, TRUE면 그렇게 함) 값이 [FALSE(0)]임<br>③ `SF_CONTROL_SELECT`(설정값: 팬 제어 기준. 0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT) 값이 [4] 이상이고 [5]보다 작음<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 158 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;**PI 자동 제어 실행**: 냉복도 온도 제어용 값(PV) (`VP_FWU_CZT_PV`)이(가) 냉복도 온도 목표값 (`VP_FWU_CZT_SP`)에 가까워지도록 팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`)을 계산해서 쓴다 — 우선순위 5 칸(일반 로직이 쓰는 칸)<br>· 방향 DEC: 현재값이 목표보다 **높으면 출력을 올린다** (예: 온도가 높으면 더 세게)<br>· 비례 게인 P = `CZT_PGAIN`(설정값: CZT 기준 팬 제어 P 게인), 적분 게인 I = `CZT_IGAIN`(설정값: CZT 기준 팬 제어 I 게인), 미분 D = 0 (0이면 안 씀)<br>· 계산 주기 = 0초 (0이면 기본 1초)<br>· 처음 시작할 때 출력 = 60<br>· 출력 범위 = 팬 최소 속도(%) (`VP_FWU_SF_Speed_Min`) ~ 팬 최대 속도(%) (`VP_FWU_SF_Speed_Max`) (이 범위 밖으로는 내보내지 않음)<br>· 루프 번호 = `CZT_LOOP`(= 4, LOOP2 번호: CZT 기준 제어) (LOOP2_INIT으로 이 제어를 초기화할 때 쓰는 번호)<br>· 데드밴드 = 0 (0이면 없음) |
| 159 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RAT_LOOP`(= 1, LOOP2 번호: RAT 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: RAT 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 160 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RDP_LOOP`(= 2, LOOP2 번호: RDP 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: RDP 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 161 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `DELTA_T_LOOP`(= 3, LOOP2 번호: ΔT(RAT-SAT) 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: ΔT(RAT-SAT) 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 162 | &emsp;&emsp;&emsp;&emsp;→&nbsp;**[아니면]** 157행 조건의 반대 상황, 즉 아래 조건 중 **하나라도 맞지 않음**<br>① `mbFixed`(PI 대신 고정속도로 돌릴지, TRUE면 고정속도) 값이 [FALSE(0)]임<br>② `mbBMSFail`(상위 통신이 끊겨 끊김 설정대로 돌지, TRUE면 그렇게 함) 값이 [FALSE(0)]임<br>③ `SF_CONTROL_SELECT`(설정값: 팬 제어 기준. 0 고정속도, 1 RAT, 2 RDP, 3 ΔT, 4 CZT) 값이 [4] 이상이고 [5]보다 작음<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 163 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 165 | &emsp;&emsp;&emsp;&emsp;→&nbsp;*[주석] 상위 통신 끊김: 설정이 '최대 속도'이거나 지금 속도가 최소보다 낮으면 최대 속도로 올린다* |
| 166 | &emsp;&emsp;&emsp;&emsp;→&nbsp;**[조건]** `mbBMSFail`(상위 통신이 끊겨 끊김 설정대로 돌지, TRUE면 그렇게 함) 값이 [TRUE(1)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 167 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;**[조건]** 다음 중 **하나라도** 맞음<br>① 상위 통신 끊김 시 운전 방식 설정(1 최대 속도, 0 마지막 속도) (`VP_FWU_BMS_Comm_Fail_Mode`) 값이 [TRUE(1)]임 (= 최대 속도)<br>② 팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`) 값이 [팬 최소 속도(%) (`VP_FWU_SF_Speed_Min`)]보다 작음<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다<br>*[주석] Comm_Fail_Mode 1 = 최대 속도, 0 = 마지막 속도 유지* |
| 168 | &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`) 값을 팬 최대 속도(%) (`VP_FWU_SF_Speed_Max`)의 지금 값과 똑같이 맞춘다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 169 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;**[아니면]** 167행 조건의 반대 상황, 즉 아래가 **모두** 맞음 (원래 조건이 하나도 맞지 않음)<br>① 상위 통신 끊김 시 운전 방식 설정(1 최대 속도, 0 마지막 속도) (`VP_FWU_BMS_Comm_Fail_Mode`) 값이 [TRUE(1)]이 아님 (= 마지막 속도 유지)<br>② 팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`) 값이 [팬 최소 속도(%) (`VP_FWU_SF_Speed_Min`)] 이상<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 170 | &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) — 마지막 팬 속도 유지 |
| 171 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RAT_LOOP`(= 1, LOOP2 번호: RAT 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: RAT 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 172 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RDP_LOOP`(= 2, LOOP2 번호: RDP 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: RDP 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 173 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `DELTA_T_LOOP`(= 3, LOOP2 번호: ΔT(RAT-SAT) 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: ΔT(RAT-SAT) 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 174 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `CZT_LOOP`(= 4, LOOP2 번호: CZT 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: CZT 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 175 | &emsp;&emsp;&emsp;&emsp;→&nbsp;**[아니면]** 166행 조건의 반대 상황, 즉 `mbBMSFail`(상위 통신이 끊겨 끊김 설정대로 돌지, TRUE면 그렇게 함) 값이 [TRUE(1)]이 아님<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 176 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 177 | &emsp;&emsp;&emsp;→&nbsp;**[아니면]** 115행 조건의 반대 상황, 즉 `bSADReady`(팬 속도를 정해도 되는지, 댐퍼가 없거나 네 댐퍼가 모두 열렸으면 TRUE) 값이 [TRUE(1)]이 아님<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 178 | &emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) — 댐퍼가 다 열릴 때까지 팬 속도는 그대로 둔다 |
| 180 | &emsp;&emsp;&emsp;→&nbsp;*[주석] 운전 명령 중인데 네 댐퍼가 모두 닫혀 있으면 PI를 초기화하고 속도를 0으로 (댐퍼가 있을 때만)* |
| 181 | &emsp;&emsp;&emsp;→&nbsp;**[조건]** 다음이 **모두** 맞음<br>① `SAD_INSTALLED`(설정값: 댐퍼 설치 여부 (옵션 부품). 0 = 없음, 1 = 있음) 값이 [TRUE(1)]임 (= 댐퍼 있음)<br>② 댐퍼 1번 닫힘 접점 (`FWU_SAD-1_CLOSE_STATUS`) 값이 [TRUE(1)]임 (= 닫힘 확인)<br>③ 댐퍼 2번 닫힘 접점 (`FWU_SAD-2_CLOSE_STATUS`) 값이 [TRUE(1)]임 (= 닫힘 확인)<br>④ 댐퍼 3번 닫힘 접점 (`FWU_SAD-3_CLOSE_STATUS`) 값이 [TRUE(1)]임 (= 닫힘 확인)<br>⑤ 댐퍼 4번 닫힘 접점 (`FWU_SAD-4_CLOSE_STATUS`) 값이 [TRUE(1)]임 (= 닫힘 확인)<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 182 | &emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RAT_LOOP`(= 1, LOOP2 번호: RAT 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: RAT 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 183 | &emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `RDP_LOOP`(= 2, LOOP2 번호: RDP 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: RDP 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 184 | &emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `DELTA_T_LOOP`(= 3, LOOP2 번호: ΔT(RAT-SAT) 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: ΔT(RAT-SAT) 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 185 | &emsp;&emsp;&emsp;&emsp;→&nbsp;PI 루프 `CZT_LOOP`(= 4, LOOP2 번호: CZT 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: CZT 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 186 | &emsp;&emsp;&emsp;&emsp;→&nbsp;팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`) 값을 [0]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 187 | &emsp;&emsp;&emsp;→&nbsp;**[아니면]** 181행 조건의 반대 상황, 즉 아래 조건 중 **하나라도 맞지 않음**<br>① `SAD_INSTALLED`(설정값: 댐퍼 설치 여부 (옵션 부품). 0 = 없음, 1 = 있음) 값이 [TRUE(1)]임 (= 댐퍼 있음)<br>② 댐퍼 1번 닫힘 접점 (`FWU_SAD-1_CLOSE_STATUS`) 값이 [TRUE(1)]임 (= 닫힘 확인)<br>③ 댐퍼 2번 닫힘 접점 (`FWU_SAD-2_CLOSE_STATUS`) 값이 [TRUE(1)]임 (= 닫힘 확인)<br>④ 댐퍼 3번 닫힘 접점 (`FWU_SAD-3_CLOSE_STATUS`) 값이 [TRUE(1)]임 (= 닫힘 확인)<br>⑤ 댐퍼 4번 닫힘 접점 (`FWU_SAD-4_CLOSE_STATUS`) 값이 [TRUE(1)]임 (= 닫힘 확인)<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 188 | &emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 190 | &emsp;&emsp;→&nbsp;**[아니면]** 104행 조건의 반대 상황, 즉 운전 명령(BMS) (`VP_FWU_Command`) 값이 [ON(1)]이 아님 (= 정지 명령)<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 191 | &emsp;&emsp;&emsp;→&nbsp;*[주석] 정지 명령: 밸브가 다 닫힌 뒤 팬을 세우고, 팬이 멈춘 뒤 댐퍼를 닫는다* |
| 192 | &emsp;&emsp;&emsp;→&nbsp;PI 루프 `RAT_LOOP`(= 1, LOOP2 번호: RAT 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: RAT 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 193 | &emsp;&emsp;&emsp;→&nbsp;PI 루프 `RDP_LOOP`(= 2, LOOP2 번호: RDP 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: RDP 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 194 | &emsp;&emsp;&emsp;→&nbsp;PI 루프 `DELTA_T_LOOP`(= 3, LOOP2 번호: ΔT(RAT-SAT) 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: ΔT(RAT-SAT) 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 195 | &emsp;&emsp;&emsp;→&nbsp;PI 루프 `CZT_LOOP`(= 4, LOOP2 번호: CZT 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: CZT 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 196 | &emsp;&emsp;&emsp;→&nbsp;**[조건]** 네 밸브 모두 닫힘 표시 (`VP_FWU_PICV_All_Closed`) 값이 [TRUE(1)]임 (= 네 밸브 모두 닫힘)<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 197 | &emsp;&emsp;&emsp;&emsp;→&nbsp;팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`) 값을 [0]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 198 | &emsp;&emsp;&emsp;→&nbsp;**[아니면]** 196행 조건의 반대 상황, 즉 네 밸브 모두 닫힘 표시 (`VP_FWU_PICV_All_Closed`) 값이 [TRUE(1)]이 아님 (= 닫히지 않은 밸브가 있음)<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 199 | &emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 200 | &emsp;&emsp;&emsp;→&nbsp;**[조건]** 팬 운전 상태 (`VP_FWU_SF_Status`) 값이 [OFF(0)]임 (= 팬이 한 대도 안 돎)<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 201 | &emsp;&emsp;&emsp;&emsp;→&nbsp;댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`) 값을 [OFF(0)]로 바꾼다 (= 댐퍼 닫힘 명령) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 202 | &emsp;&emsp;&emsp;→&nbsp;**[아니면]** 200행 조건의 반대 상황, 즉 팬 운전 상태 (`VP_FWU_SF_Status`) 값이 [OFF(0)]이 아님 (= 팬이 한 대라도 돌고 있음)<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 203 | &emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 204 | &emsp;&emsp;→&nbsp;팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`)의 지금 값을 우선순위 11 칸(값 보관·정지 요청용 칸. 숫자가 작은 칸이 모두 비어 있을 때 적용됨)에도 똑같이 적어 둔다. 자동 운전에서 계산한 값을 보관해 두어, 수동으로 바꾸거나 다시 시작할 때 이 값부터 이어가게 한다 |
| 205 | &emsp;&emsp;→&nbsp;댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`)의 지금 값을 우선순위 11 칸(값 보관·정지 요청용 칸. 숫자가 작은 칸이 모두 비어 있을 때 적용됨)에도 똑같이 적어 둔다. 자동 운전에서 계산한 값을 보관해 두어, 수동으로 바꾸거나 다시 시작할 때 이 값부터 이어가게 한다 |
| 206 | &emsp;→&nbsp;**[아니면]** 103행 조건의 반대 상황, 즉 운전 모드(1 자동, 0 수동) (`VP_FWU_Operation_Mode`) 값이 [TRUE(1)]이 아님 (= 수동 운전)<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 207 | &emsp;&emsp;→&nbsp;*[주석] 수동 모드: 로직이 쓴 P5를 내려놓아 사람이 넣은 값이 적용되게 한다* |
| 208 | &emsp;&emsp;→&nbsp;PI 루프 `RAT_LOOP`(= 1, LOOP2 번호: RAT 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: RAT 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 209 | &emsp;&emsp;→&nbsp;PI 루프 `RDP_LOOP`(= 2, LOOP2 번호: RDP 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: RDP 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 210 | &emsp;&emsp;→&nbsp;PI 루프 `DELTA_T_LOOP`(= 3, LOOP2 번호: ΔT(RAT-SAT) 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: ΔT(RAT-SAT) 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 211 | &emsp;&emsp;→&nbsp;PI 루프 `CZT_LOOP`(= 4, LOOP2 번호: CZT 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: CZT 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 212 | &emsp;&emsp;→&nbsp;팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`)의 우선순위 5 칸(일반 로직이 쓰는 칸)에 써 둔 값을 지운다. 그 칸이 비면 그다음 칸(숫자가 더 큰 칸)에 있는 값이 적용된다 |
| 213 | &emsp;&emsp;→&nbsp;댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`)의 우선순위 5 칸(일반 로직이 쓰는 칸)에 써 둔 값을 지운다. 그 칸이 비면 그다음 칸(숫자가 더 큰 칸)에 있는 값이 적용된다 |
| 214 | **[아니면]** 89행 조건의 반대 상황, 즉 비상정지 입력(DI) (`FWU_EMERGENCY`) 값이 [FALSE(0)]이 아님 (= 비상정지 눌림)<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 215 | &emsp;→&nbsp;*[주석] 비상정지: 운전 명령을 끄고 팬 출력을 P1으로 0으로 누른다. 댐퍼는 팬이 멈춘 뒤 닫는다* |
| 216 | &emsp;→&nbsp;운전 명령(BMS) (`VP_FWU_Command`) 값을 [OFF(0)]로 바꾼다 (= 정지 명령) — 우선순위 11 칸(값 보관·정지 요청용 칸. 숫자가 작은 칸이 모두 비어 있을 때 적용됨)에 쓴다 |
| 217 | &emsp;→&nbsp;운전 명령(HMI) (`VP_FWU_Command_HMI`) 값을 [OFF(0)]로 바꾼다 (= 정지 명령) — 우선순위 11 칸(값 보관·정지 요청용 칸. 숫자가 작은 칸이 모두 비어 있을 때 적용됨)에 쓴다 |
| 218 | &emsp;→&nbsp;PI 루프 `RAT_LOOP`(= 1, LOOP2 번호: RAT 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: RAT 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 219 | &emsp;→&nbsp;PI 루프 `RDP_LOOP`(= 2, LOOP2 번호: RDP 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: RDP 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 220 | &emsp;→&nbsp;PI 루프 `DELTA_T_LOOP`(= 3, LOOP2 번호: ΔT(RAT-SAT) 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: ΔT(RAT-SAT) 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 221 | &emsp;→&nbsp;PI 루프 `CZT_LOOP`(= 4, LOOP2 번호: CZT 기준 제어)의 누적값(I 적분값)을 지운다 (LOOP2 번호: CZT 기준 제어). 다음에 이 PI 제어를 다시 돌리면 처음(시작 출력)부터 새로 계산한다 |
| 222 | &emsp;→&nbsp;팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`) 값을 [0]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 223 | &emsp;→&nbsp;팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`) 값을 [0]로 바꾼다 — 우선순위 11 칸(값 보관·정지 요청용 칸. 숫자가 작은 칸이 모두 비어 있을 때 적용됨)에 쓴다 |
| 224 | &emsp;→&nbsp;**[조건]** 팬 운전 상태 (`VP_FWU_SF_Status`) 값이 [OFF(0)]임 (= 팬이 한 대도 안 돎)<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 225 | &emsp;&emsp;→&nbsp;댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`) 값을 [OFF(0)]로 바꾼다 (= 댐퍼 닫힘 명령) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 226 | &emsp;&emsp;→&nbsp;댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`) 값을 [OFF(0)]로 바꾼다 (= 댐퍼 닫힘 명령) — 우선순위 11 칸(값 보관·정지 요청용 칸. 숫자가 작은 칸이 모두 비어 있을 때 적용됨)에 쓴다 |
| 227 | &emsp;&emsp;→&nbsp;댐퍼 1~4번 개폐 명령(DO) (`FWU_SAD-1_4_COMMAND`) 값을 [OFF(0)]로 바꾼다 (= 댐퍼 닫힘 명령) — 우선순위 1 칸(비상정지가 쓰는 칸, 가장 강함)에 쓴다 |
| 228 | &emsp;→&nbsp;**[아니면]** 224행 조건의 반대 상황, 즉 팬 운전 상태 (`VP_FWU_SF_Status`) 값이 [OFF(0)]이 아님 (= 팬이 한 대라도 돌고 있음)<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 229 | &emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 230 | &emsp;→&nbsp;팬 1~4번 속도 AO 출력 (`FWU_SF-1_4_SPEED_CONTROL`) 값을 [0]로 바꾼다 — 우선순위 1 칸(비상정지가 쓰는 칸, 가장 강함)에 쓴다 |
| 231 | &emsp;→&nbsp;팬 5~8번 속도 AO 출력 (`FWU_SF-5_8_SPEED_CONTROL`) 값을 [0]로 바꾼다 — 우선순위 1 칸(비상정지가 쓰는 칸, 가장 강함)에 쓴다 |
| 232 | &emsp;→&nbsp;팬 1번 목표 RPM (`FWU_SF-1.Target_RPM_Set`) 값을 [0]로 바꾼다 — 우선순위 1 칸(비상정지가 쓰는 칸, 가장 강함)에 쓴다 |
| 233 | &emsp;→&nbsp;팬 2번 목표 RPM (`FWU_SF-2.Target_RPM_Set`) 값을 [0]로 바꾼다 — 우선순위 1 칸(비상정지가 쓰는 칸, 가장 강함)에 쓴다 |
| 234 | &emsp;→&nbsp;팬 3번 목표 RPM (`FWU_SF-3.Target_RPM_Set`) 값을 [0]로 바꾼다 — 우선순위 1 칸(비상정지가 쓰는 칸, 가장 강함)에 쓴다 |
| 235 | &emsp;→&nbsp;팬 4번 목표 RPM (`FWU_SF-4.Target_RPM_Set`) 값을 [0]로 바꾼다 — 우선순위 1 칸(비상정지가 쓰는 칸, 가장 강함)에 쓴다 |
| 236 | &emsp;→&nbsp;팬 5번 목표 RPM (`FWU_SF-5.Target_RPM_Set`) 값을 [0]로 바꾼다 — 우선순위 1 칸(비상정지가 쓰는 칸, 가장 강함)에 쓴다 |
| 237 | &emsp;→&nbsp;팬 6번 목표 RPM (`FWU_SF-6.Target_RPM_Set`) 값을 [0]로 바꾼다 — 우선순위 1 칸(비상정지가 쓰는 칸, 가장 강함)에 쓴다 |
| 238 | &emsp;→&nbsp;팬 7번 목표 RPM (`FWU_SF-7.Target_RPM_Set`) 값을 [0]로 바꾼다 — 우선순위 1 칸(비상정지가 쓰는 칸, 가장 강함)에 쓴다 |
| 239 | &emsp;→&nbsp;팬 8번 목표 RPM (`FWU_SF-8.Target_RPM_Set`) 값을 [0]로 바꾼다 — 우선순위 1 칸(비상정지가 쓰는 칸, 가장 강함)에 쓴다 |

<a id="section-6"></a>

## 241~259행 · 팬 운전 명령: 속도 값이 있으면 8대 모두 운전

| 행 | 해석 |
|---:|---|
| 241 | *[주석] 팬 운전 명령: 속도 값이 있으면 8대 모두 운전* |
| 242 | **[조건]** 팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`) 값이 [0]보다 큼<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 243 | &emsp;→&nbsp;팬 1번 운전 명령 (`FWU_SF-1.Run_Command`) 값을 [ON(1)]로 바꾼다 (= 운전) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 244 | &emsp;→&nbsp;팬 2번 운전 명령 (`FWU_SF-2.Run_Command`) 값을 [ON(1)]로 바꾼다 (= 운전) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 245 | &emsp;→&nbsp;팬 3번 운전 명령 (`FWU_SF-3.Run_Command`) 값을 [ON(1)]로 바꾼다 (= 운전) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 246 | &emsp;→&nbsp;팬 4번 운전 명령 (`FWU_SF-4.Run_Command`) 값을 [ON(1)]로 바꾼다 (= 운전) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 247 | &emsp;→&nbsp;팬 5번 운전 명령 (`FWU_SF-5.Run_Command`) 값을 [ON(1)]로 바꾼다 (= 운전) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 248 | &emsp;→&nbsp;팬 6번 운전 명령 (`FWU_SF-6.Run_Command`) 값을 [ON(1)]로 바꾼다 (= 운전) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 249 | &emsp;→&nbsp;팬 7번 운전 명령 (`FWU_SF-7.Run_Command`) 값을 [ON(1)]로 바꾼다 (= 운전) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 250 | &emsp;→&nbsp;팬 8번 운전 명령 (`FWU_SF-8.Run_Command`) 값을 [ON(1)]로 바꾼다 (= 운전) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 251 | **[아니면]** 242행 조건의 반대 상황, 즉 팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`) 값이 [0] 이하<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 252 | &emsp;→&nbsp;팬 1번 운전 명령 (`FWU_SF-1.Run_Command`) 값을 [OFF(0)]로 바꾼다 (= 정지) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 253 | &emsp;→&nbsp;팬 2번 운전 명령 (`FWU_SF-2.Run_Command`) 값을 [OFF(0)]로 바꾼다 (= 정지) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 254 | &emsp;→&nbsp;팬 3번 운전 명령 (`FWU_SF-3.Run_Command`) 값을 [OFF(0)]로 바꾼다 (= 정지) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 255 | &emsp;→&nbsp;팬 4번 운전 명령 (`FWU_SF-4.Run_Command`) 값을 [OFF(0)]로 바꾼다 (= 정지) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 256 | &emsp;→&nbsp;팬 5번 운전 명령 (`FWU_SF-5.Run_Command`) 값을 [OFF(0)]로 바꾼다 (= 정지) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 257 | &emsp;→&nbsp;팬 6번 운전 명령 (`FWU_SF-6.Run_Command`) 값을 [OFF(0)]로 바꾼다 (= 정지) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 258 | &emsp;→&nbsp;팬 7번 운전 명령 (`FWU_SF-7.Run_Command`) 값을 [OFF(0)]로 바꾼다 (= 정지) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 259 | &emsp;→&nbsp;팬 8번 운전 명령 (`FWU_SF-8.Run_Command`) 값을 [OFF(0)]로 바꾼다 (= 정지) — 우선순위 5 칸(일반 로직이 쓰는 칸) |

<a id="section-7"></a>

## 261~297행 · 팬 속도 출력 (5초마다)

> 평소에는 Modbus로 목표 RPM을 보내고, 팬 통신이 끊기면 AO(아날로그)로 바꿔 보낸다

| 행 | 해석 |
|---:|---|
| 261 | *[주석] 팬 속도 출력 (5초마다)* |
| 262 | *[주석] 평소에는 Modbus로 목표 RPM을 보내고, 팬 통신이 끊기면 AO(아날로그)로 바꿔 보낸다* |
| 263 | **[조건]** 타이머 1번 `SPEED_OUTPUT_TIMER`(팬 속도를 마지막으로 내보낸 뒤 지난 시간)으로 잰 시간(초)이 [5]초보다 김<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다<br>*[주석] 5초* |
| 264 | &emsp;→&nbsp;`SFSpeed`(팬 속도 요구값(임시, %))에 팬 속도 요구값(%) (`VP_FWU_SF_Speed_Value`) 값을 읽어 넣는다 |
| 265 | &emsp;→&nbsp;`SFMaxRPM`(팬 최대 RPM(임시))에 팬 최대 RPM(계산값) (`VP_FWU_SF_Max_RPM`) 값을 읽어 넣는다<br>*[주석] Initialization이 설계 RPM과 비율로 계산해 둔 값* |
| 266 | &emsp;→&nbsp;`SFRPMSet`(팬에 보낼 목표 RPM(임시))에 다음 계산값을 넣는다: [`SFSpeed`(팬 속도 요구값(임시, %)) × `SFMaxRPM`(팬 최대 RPM(임시)) ÷ 100, `SFMaxRPM`(팬 최대 RPM(임시))] 중 가장 작은 값 |
| 267 | &emsp;→&nbsp;`SFAOSet`(팬 AO로 보낼 값(임시, %))에 다음 계산값을 넣는다: `SFSpeed`(팬 속도 요구값(임시, %)) × `SFMaxRPM`(팬 최대 RPM(임시)) ÷ [팬 정격 최대 RPM (`VP_FWU_SF_Rated_Max_RPM`), 1] 중 가장 큰 값 |
| 269 | &emsp;→&nbsp;**[조건]** 팬 통신 이상 종합 (`VP_FWU_SF_Comm_Fault`) 값이 [TRUE(1)]임 (= 통신 이상)<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 270 | &emsp;&emsp;→&nbsp;팬 1~4번 속도 AO 출력 (`FWU_SF-1_4_SPEED_CONTROL`) 값을 [`SFAOSet`(팬 AO로 보낼 값(임시, %))]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 271 | &emsp;&emsp;→&nbsp;팬 5~8번 속도 AO 출력 (`FWU_SF-5_8_SPEED_CONTROL`) 값을 [`SFAOSet`(팬 AO로 보낼 값(임시, %))]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 272 | &emsp;&emsp;→&nbsp;팬 1번 목표 RPM (`FWU_SF-1.Target_RPM_Set`) 값을 [0]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 273 | &emsp;&emsp;→&nbsp;팬 2번 목표 RPM (`FWU_SF-2.Target_RPM_Set`) 값을 [0]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 274 | &emsp;&emsp;→&nbsp;팬 3번 목표 RPM (`FWU_SF-3.Target_RPM_Set`) 값을 [0]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 275 | &emsp;&emsp;→&nbsp;팬 4번 목표 RPM (`FWU_SF-4.Target_RPM_Set`) 값을 [0]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 276 | &emsp;&emsp;→&nbsp;팬 5번 목표 RPM (`FWU_SF-5.Target_RPM_Set`) 값을 [0]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 277 | &emsp;&emsp;→&nbsp;팬 6번 목표 RPM (`FWU_SF-6.Target_RPM_Set`) 값을 [0]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 278 | &emsp;&emsp;→&nbsp;팬 7번 목표 RPM (`FWU_SF-7.Target_RPM_Set`) 값을 [0]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 279 | &emsp;&emsp;→&nbsp;팬 8번 목표 RPM (`FWU_SF-8.Target_RPM_Set`) 값을 [0]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 280 | &emsp;→&nbsp;**[아니면]** 269행 조건의 반대 상황, 즉 팬 통신 이상 종합 (`VP_FWU_SF_Comm_Fault`) 값이 [TRUE(1)]이 아님 (= 통신 정상)<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 281 | &emsp;&emsp;→&nbsp;팬 1~4번 속도 AO 출력 (`FWU_SF-1_4_SPEED_CONTROL`) 값을 [0]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 282 | &emsp;&emsp;→&nbsp;팬 5~8번 속도 AO 출력 (`FWU_SF-5_8_SPEED_CONTROL`) 값을 [0]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 283 | &emsp;&emsp;→&nbsp;팬 1번 목표 RPM (`FWU_SF-1.Target_RPM_Set`) 값을 [`SFRPMSet`(팬에 보낼 목표 RPM(임시))]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 284 | &emsp;&emsp;→&nbsp;팬 2번 목표 RPM (`FWU_SF-2.Target_RPM_Set`) 값을 [`SFRPMSet`(팬에 보낼 목표 RPM(임시))]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 285 | &emsp;&emsp;→&nbsp;팬 3번 목표 RPM (`FWU_SF-3.Target_RPM_Set`) 값을 [`SFRPMSet`(팬에 보낼 목표 RPM(임시))]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 286 | &emsp;&emsp;→&nbsp;팬 4번 목표 RPM (`FWU_SF-4.Target_RPM_Set`) 값을 [`SFRPMSet`(팬에 보낼 목표 RPM(임시))]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 287 | &emsp;&emsp;→&nbsp;팬 5번 목표 RPM (`FWU_SF-5.Target_RPM_Set`) 값을 [`SFRPMSet`(팬에 보낼 목표 RPM(임시))]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 288 | &emsp;&emsp;→&nbsp;팬 6번 목표 RPM (`FWU_SF-6.Target_RPM_Set`) 값을 [`SFRPMSet`(팬에 보낼 목표 RPM(임시))]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 289 | &emsp;&emsp;→&nbsp;팬 7번 목표 RPM (`FWU_SF-7.Target_RPM_Set`) 값을 [`SFRPMSet`(팬에 보낼 목표 RPM(임시))]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 290 | &emsp;&emsp;→&nbsp;팬 8번 목표 RPM (`FWU_SF-8.Target_RPM_Set`) 값을 [`SFRPMSet`(팬에 보낼 목표 RPM(임시))]로 바꾼다 — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 292 | &emsp;→&nbsp;타이머 1번 `SPEED_OUTPUT_TIMER`(팬 속도를 마지막으로 내보낸 뒤 지난 시간)를 0으로 되돌린다. 이 시점부터 시간을 새로 잰다 |
| 293 | **[아니면]** 263행 조건의 반대 상황, 즉 타이머 1번 `SPEED_OUTPUT_TIMER`(팬 속도를 마지막으로 내보낸 뒤 지난 시간)으로 잰 시간(초)이 아직 [5]초를 넘지 않음<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 294 | &emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 296 | *[주석] JSY 2026-11-23 수정 구간 끝. 주제 = Coding Rule 적용(매크로 상수, 설정값 상수, 변수명, if-else 짝 맞춤, 주석)* |
| 297 | *[주석] LJH 2026-11-17 수정 구간 끝. 주제 = 온도 고장 대체운전과 네 밸브 정지 연계* |
