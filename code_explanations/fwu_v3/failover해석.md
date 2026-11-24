# Failover 줄별 해석

> **대상 코드** : `fwu_v3/Logic/Failover.py` (56 줄)  
> **기준** : `sy 브랜치 2026-11-24 (댐퍼 설치 여부 설정 반영)`  
> **행** = 코드 줄 번호 (빈 줄은 생략)  
> **표기** : `→` 들여쓰기 단계 · *[주석]* 코드 안 주석 · `이름` 코드 안 상수·변수 · **※** 읽을 때 주의할 점

댐퍼 미개방·전폐 또는 팬 종합 고장이 이어지면 Failover 알람을 내고 운전 OFF를 한 번 기록한다. 원인이 없어진 뒤 Reset으로 해제한다.

**목차**

- [1~18행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수](#section-1)
- [20~26행 · 장치 고장 원인 모으기](#section-2)
- [28~38행 · Failover 알람: 처음 걸릴 때 P11에 운전 OFF를 한 번 써 둔다](#section-3)
- [40~56행 · Reset: 원인이 없어진 뒤에 Reset을 해야 알람이 꺼진다](#section-4)

**※ 읽는 법**

- **[조건]** 줄은 조건이 맞을 때만 바로 아래 한 칸 더 들여쓴(→가 하나 더 붙은) 줄들을 실행한다. **[아니면]** 줄은 그 조건이 맞지 않을 때 실행하는 부분이다.
- 값은 [ ] 안에 적었다. TRUE·ON·SET·TMR_READ·DEC = 1, FALSE·OFF·CLEAR·TMR_CLEAR·INC = 0 이다. 0/1 값 옆 (= …)은 그 관제점에서 0/1이 뜻하는 상태다.
- **우선순위 칸**: 관제점 하나에 번호가 붙은 여러 칸이 있고, **숫자가 작은 칸의 값이 이긴다**. 1 = 비상정지, 2 = 원격·화재 정지, 5 = 일반 로직(번호 없이 쓰는 `WRITEPOINT`), 11 = 값 보관·정지 요청. 칸을 지우면(해제) 그다음 칸의 값이 적용된다.
- 조건이 맞지 않는다고 관제점이 저절로 0이 되지는 않는다. 그 분기에 쓰는 줄이 없으면 **이전 값이 그대로 남는다**.
- 타이머는 0으로 되돌린 순간부터 흐른 시간(초)을 잰다. 대문자 이름은 상수, `m`으로 시작하는 이름은 이 파일 전체에서 쓰는 변수, 이름에 `b`가 붙은 변수는 TRUE/FALSE 값이다.

<a id="section-1"></a>

## 1~18행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수

| 행 | 해석 |
|---:|---|
| 1 | *[주석] LJH 2026-11-17 수정 구간 시작. 주제 = 기존 Failover 원인과 래치 유지* |
| 2 | *[주석] JSY 2026-11-23 수정 구간 시작. 주제 = Coding Rule 적용(매크로 상수, 변수명, if-else 짝 맞춤, 주석)* |
| 4 | *[주석] 로직엔진 loading* |
| 5 | DDC 로직 엔진을 불러온다. 이 아래에서 `engine.READPOINT`(관제점 읽기), `engine.WRITEPOINT`(관제점 쓰기) 같은 기능을 이 이름으로 쓴다 |
| 7 | *[주석] Macro상수 정의* |
| 8 | 매크로 상수 정의: TMR_READ, SET, ON, TRUE, DEC를 모두 숫자 1으로 정한다. 코드에서 숫자 1 대신 뜻이 보이는 이름으로 쓰기 위한 것이다 (타이머 읽기·켜짐·참·DEC 방향처럼 '긍정' 또는 1을 뜻하는 인자) |
| 9 | 매크로 상수 정의: TMR_CLEAR, CLEAR, OFF, FALSE, INC를 모두 숫자 0으로 정한다. 코드에서 숫자 0 대신 뜻이 보이는 이름으로 쓰기 위한 것이다 (타이머 초기화·꺼짐·거짓·INC 방향처럼 '부정' 또는 0을 뜻하는 인자) |
| 10 | 상수 `FAILOVER_CONFIRM_SECONDS` = 5. 뜻: 고장 원인이 5초 넘게 이어져야 Failover로 본다 |
| 11 | 상수 `FAILOVER_RESET_HOLD_SECONDS` = 5. 뜻: Reset 입력을 5초 뒤 스스로 되돌린다 (알람 해제 대기 시간이 아님) |
| 13 | *[주석] 타이머 정의* |
| 14 | 타이머 번호에 이름 붙이기: `FAILOVER_CONFIRM_TIMER` = 타이머 1번. 이 타이머로 'Failover 원인이 이어진 시간'을 잰다 (한 로직에서 타이머는 0~9번 10개까지) |
| 15 | 타이머 번호에 이름 붙이기: `FAILOVER_RESET_TIMER` = 타이머 2번. 이 타이머로 'Reset 입력이 켜져 있던 시간'을 잰다 (한 로직에서 타이머는 0~9번 10개까지) |
| 17 | *[주석] 전역변수 선언* |
| 18 | 전역변수 `mbFailTotal`(Failover 원인이 하나라도 있는지, TRUE면 있음)를 만들고 처음 값을 [FALSE(0)]로 둔다. 이 로직이 실행될 때마다 이 값에서 다시 시작한다<br>*[주석] 댐퍼 미개방·전폐, 팬 종합 고장 중 하나라도 있으면 TRUE* |

<a id="section-2"></a>

## 20~26행 · 장치 고장 원인 모으기

> 장치 고장 상태를 상위에 알리는 용도다. 옆 FWU와의 협조 운전은 상위에서 판단한다. 개별 PICV 알람과 Damper Signal Alarm의 추가 댐퍼 알람은 Failover 조건에 넣지 않는다. 댐퍼 원인 2개는 댐퍼 설치(VP_FWU_SAD_Installed = 1) 때만 걸린다.

| 행 | 해석 |
|---:|---|
| 20 | *[주석] 장치 고장 원인 모으기* |
| 21 | *[주석] 장치 고장 상태를 상위에 알리는 용도다. 옆 FWU와의 협조 운전은 상위에서 판단한다.* |
| 22 | *[주석] 개별 PICV 알람과 Damper Signal Alarm의 추가 댐퍼 알람은 Failover 조건에 넣지 않는다. 댐퍼 원인 2개는 댐퍼 설치(VP_FWU_SAD_Installed = 1) 때만 걸린다.* |
| 23 | **[조건]** 다음 중 **하나라도** 맞음<br>① 댐퍼 미개방 알람 (`VP_FWU_SAD_Not_Open_Alarm`) 값이 [TRUE(1)]임 (= 알람 걸림)<br>② 댐퍼 전폐 알람 (`VP_FWU_SAD_Full_Close_Alarm`) 값이 [TRUE(1)]임 (= 알람 걸림)<br>③ 팬 종합 고장 알람 (`VP_FWU_SF_Failure_Alarm`) 값이 [TRUE(1)]임 (= 알람 걸림)<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 24 | &emsp;→&nbsp;`mbFailTotal`(Failover 원인이 하나라도 있는지, TRUE면 있음) 값을 [TRUE(1)]로 바꾼다 |
| 25 | **[아니면]** 23행 조건의 반대 상황, 즉 아래가 **모두** 맞음 (원래 조건이 하나도 맞지 않음)<br>① 댐퍼 미개방 알람 (`VP_FWU_SAD_Not_Open_Alarm`) 값이 [TRUE(1)]이 아님 (= 알람 없음)<br>② 댐퍼 전폐 알람 (`VP_FWU_SAD_Full_Close_Alarm`) 값이 [TRUE(1)]이 아님 (= 알람 없음)<br>③ 팬 종합 고장 알람 (`VP_FWU_SF_Failure_Alarm`) 값이 [TRUE(1)]이 아님 (= 알람 없음)<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 26 | &emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |

<a id="section-3"></a>

## 28~38행 · Failover 알람: 처음 걸릴 때 P11에 운전 OFF를 한 번 써 둔다

> 계속 세워 두거나 재기동을 막는 것은 아니고, 더 높은 우선순위의 ON이 있으면 그쪽이 이긴다.

| 행 | 해석 |
|---:|---|
| 28 | *[주석] Failover 알람: 처음 걸릴 때 P11에 운전 OFF를 한 번 써 둔다* |
| 29 | *[주석] 계속 세워 두거나 재기동을 막는 것은 아니고, 더 높은 우선순위의 ON이 있으면 그쪽이 이긴다.* |
| 30 | **[조건]** `mbFailTotal`(Failover 원인이 하나라도 있는지, TRUE면 있음) 값이 [TRUE(1)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 31 | &emsp;→&nbsp;**[조건]** 다음이 **모두** 맞음<br>① 타이머 1번 `FAILOVER_CONFIRM_TIMER`(Failover 원인이 이어진 시간)으로 잰 시간(초)이 [`FAILOVER_CONFIRM_SECONDS`(= 5, 고장 원인이 5초 넘게 이어져야 Failover로 본다)]초보다 김<br>② Failover 알람 (`VP_FWU_Failover_Alarm`) 값이 [FALSE(0)]임 (= 알람 없음)<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 32 | &emsp;&emsp;→&nbsp;Failover 알람 (`VP_FWU_Failover_Alarm`)을 켠다 — 값 [TRUE(1)] (= 알람 걸림) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 33 | &emsp;&emsp;→&nbsp;운전 명령(BMS) (`VP_FWU_Command`) 값을 [OFF(0)]로 바꾼다 (= 정지 명령) — 우선순위 11 칸(값 보관·정지 요청용 칸. 숫자가 작은 칸이 모두 비어 있을 때 적용됨)에 쓴다 |
| 34 | &emsp;&emsp;→&nbsp;운전 명령(HMI) (`VP_FWU_Command_HMI`) 값을 [OFF(0)]로 바꾼다 (= 정지 명령) — 우선순위 11 칸(값 보관·정지 요청용 칸. 숫자가 작은 칸이 모두 비어 있을 때 적용됨)에 쓴다 |
| 35 | &emsp;→&nbsp;**[아니면]** 31행 조건의 반대 상황, 즉 아래 조건 중 **하나라도 맞지 않음**<br>① 타이머 1번 `FAILOVER_CONFIRM_TIMER`(Failover 원인이 이어진 시간)으로 잰 시간(초)이 [`FAILOVER_CONFIRM_SECONDS`(= 5, 고장 원인이 5초 넘게 이어져야 Failover로 본다)]초보다 김<br>② Failover 알람 (`VP_FWU_Failover_Alarm`) 값이 [FALSE(0)]임 (= 알람 없음)<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 36 | &emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 37 | **[아니면]** 30행 조건의 반대 상황, 즉 `mbFailTotal`(Failover 원인이 하나라도 있는지, TRUE면 있음) 값이 [TRUE(1)]이 아님<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 38 | &emsp;→&nbsp;타이머 1번 `FAILOVER_CONFIRM_TIMER`(Failover 원인이 이어진 시간)를 0으로 되돌린다. 이 시점부터 시간을 새로 잰다 |

<a id="section-4"></a>

## 40~56행 · Reset: 원인이 없어진 뒤에 Reset을 해야 알람이 꺼진다

> HMI/BMS가 더 높은 우선순위로 Reset을 썼다면 그 입력도 직접 풀어야 한다.

| 행 | 해석 |
|---:|---|
| 40 | *[주석] Reset: 원인이 없어진 뒤에 Reset을 해야 알람이 꺼진다* |
| 41 | *[주석] HMI/BMS가 더 높은 우선순위로 Reset을 썼다면 그 입력도 직접 풀어야 한다.* |
| 42 | **[조건]** Failover Reset 입력 (`VP_FWU_Failover_Reset`) 값이 [TRUE(1)]임 (= Reset 누름)<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 43 | &emsp;→&nbsp;**[조건]** `mbFailTotal`(Failover 원인이 하나라도 있는지, TRUE면 있음) 값이 [FALSE(0)]임<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 44 | &emsp;&emsp;→&nbsp;Failover 알람 (`VP_FWU_Failover_Alarm`)을 끈다 — 값 [FALSE(0)] (= 알람 없음) — 우선순위 5 칸(일반 로직이 쓰는 칸) |
| 45 | &emsp;→&nbsp;**[아니면]** 43행 조건의 반대 상황, 즉 `mbFailTotal`(Failover 원인이 하나라도 있는지, TRUE면 있음) 값이 [FALSE(0)]이 아님<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 46 | &emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 47 | &emsp;→&nbsp;**[조건]** 타이머 2번 `FAILOVER_RESET_TIMER`(Reset 입력이 켜져 있던 시간)으로 잰 시간(초)이 [`FAILOVER_RESET_HOLD_SECONDS`(= 5, Reset 입력을 5초 뒤 스스로 되돌린다 (알람 해제 대기 시간이 아님))]초보다 김<br>→ **맞으면** 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 48 | &emsp;&emsp;→&nbsp;Failover Reset 입력 (`VP_FWU_Failover_Reset`) 값을 [FALSE(0)]로 바꾼다 (= Reset 안 누름) — 우선순위 11 칸(값 보관·정지 요청용 칸. 숫자가 작은 칸이 모두 비어 있을 때 적용됨)에 쓴다 |
| 49 | &emsp;&emsp;→&nbsp;타이머 2번 `FAILOVER_RESET_TIMER`(Reset 입력이 켜져 있던 시간)를 0으로 되돌린다. 이 시점부터 시간을 새로 잰다 |
| 50 | &emsp;→&nbsp;**[아니면]** 47행 조건의 반대 상황, 즉 타이머 2번 `FAILOVER_RESET_TIMER`(Reset 입력이 켜져 있던 시간)으로 잰 시간(초)이 아직 [`FAILOVER_RESET_HOLD_SECONDS`(= 5, Reset 입력을 5초 뒤 스스로 되돌린다 (알람 해제 대기 시간이 아님))]초를 넘지 않음<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 51 | &emsp;&emsp;→&nbsp;아무것도 하지 않는다 (위 조건에 해당할 때 따로 할 일이 없다는 표시, do_nothing) |
| 52 | **[아니면]** 42행 조건의 반대 상황, 즉 Failover Reset 입력 (`VP_FWU_Failover_Reset`) 값이 [TRUE(1)]이 아님 (= Reset 안 누름)<br>→ 이때 바로 아래 한 칸 더 들여쓴 줄들을 실행한다 |
| 53 | &emsp;→&nbsp;타이머 2번 `FAILOVER_RESET_TIMER`(Reset 입력이 켜져 있던 시간)를 0으로 되돌린다. 이 시점부터 시간을 새로 잰다 |
| 55 | *[주석] JSY 2026-11-23 수정 구간 끝. 주제 = Coding Rule 적용(매크로 상수, 변수명, if-else 짝 맞춤, 주석)* |
| 56 | *[주석] LJH 2026-11-17 수정 구간 끝. 주제 = 기존 Failover 원인과 래치 유지* |
