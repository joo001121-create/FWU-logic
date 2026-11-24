# Failover 줄별 해석

> **대상 코드** : `fwu_v3/Logic/Failover.py` (56 줄)  
> **기준** : `sy 브랜치 2026-11-23 (naming rule·관제점 이름 변경 반영)`  
> **행** = 코드 줄 번호 (빈 줄은 생략)  
> **표기** : `→` 들여쓰기 단계 · *[주석]* 코드 안 주석 · `이름` 코드 안 상수·변수 · **※** 읽을 때 주의할 점

댐퍼 미개방·전폐 또는 팬 종합 고장이 이어지면 Failover 알람을 내고 운전 OFF를 한 번 기록한다. 원인이 없어진 뒤 Reset으로 해제한다.

**목차**

- [1~18행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수](#section-1)
- [20~26행 · 장치 고장 원인 모으기](#section-2)
- [28~38행 · Failover 알람: 처음 걸릴 때 P11에 운전 OFF를 한 번 써 둔다](#section-3)
- [40~56행 · Reset: 원인이 없어진 뒤에 Reset을 해야 알람이 꺼진다](#section-4)

**※ 공통 표기**: 매크로 상수 TRUE·ON·SET·TMR_READ·DEC = 1, FALSE·OFF·CLEAR·TMR_CLEAR·INC = 0. `SECTIMER(타이머, TMR_CLEAR)`는 타이머를 0초로 초기화, `SECTIMER(타이머, TMR_READ)`는 경과시간 확인이다. P번호가 없는 쓰기(`WRITEPOINT`)는 기본 우선순위 P5를 쓴다. 조건이 거짓이라고 관제점이 저절로 0이 되지는 않는다. 해당 분기에 쓰기가 없으면 이전 값이 남는다. 대문자 이름은 상수, `m`으로 시작하는 이름은 이 파일의 전역변수, `b`가 붙은 이름은 참/거짓 값이다.

<a id="section-1"></a>

## 1~18행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수

| 행 | 해석 |
|---:|---|
| 1 | *[주석] LJH 2026-11-17 수정 구간 시작. 주제 = 기존 Failover 원인과 래치 유지* |
| 2 | *[주석] JSY 2026-11-23 수정 구간 시작. 주제 = Coding Rule 적용(매크로 상수, 변수명, if-else 짝 맞춤, 주석)* |
| 4 | *[주석] 로직엔진 loading* |
| 5 | DDC 로직 엔진 객체 생성 (이후 engine.xxx로 관제점을 읽고 씀) |
| 7 | *[주석] Macro상수 정의* |
| 8 | 매크로 상수 정의: TMR_READ, SET, ON, TRUE, DEC = 1 (긍정의 의미 또는 1인 인자) |
| 9 | 매크로 상수 정의: TMR_CLEAR, CLEAR, OFF, FALSE, INC = 0 (부정의 의미 또는 0인 인자) |
| 10 | 상수 `FAILOVER_CONFIRM_SECONDS` = 5<br>*[주석] 고장 원인이 5초 넘게 이어져야 Failover로 본다* |
| 11 | 상수 `FAILOVER_RESET_HOLD_SECONDS` = 5<br>*[주석] Reset 입력을 5초 뒤 스스로 되돌린다 (알람 해제 대기 시간이 아님)* |
| 13 | *[주석] 타이머 정의* |
| 14 | 타이머 번호 상수 `FAILOVER_CONFIRM_TIMER` = 1번<br>*[주석] Failover 원인이 이어진 시간* |
| 15 | 타이머 번호 상수 `FAILOVER_RESET_TIMER` = 2번<br>*[주석] Reset 입력이 켜져 있던 시간* |
| 17 | *[주석] 전역변수 선언* |
| 18 | 전역변수 `mbFailTotal` 선언, 처음 값 = FALSE(0)<br>*[주석] 댐퍼 미개방·전폐, 팬 종합 고장 중 하나라도 있으면 TRUE* |

<a id="section-2"></a>

## 20~26행 · 장치 고장 원인 모으기

> 장치 고장 상태를 상위에 알리는 용도다. 옆 FWU와의 협조 운전은 상위에서 판단한다. 개별 PICV 알람과 Damper Signal Alarm의 추가 댐퍼 알람은 Failover 조건에 넣지 않는다. 댐퍼 원인 2개는 댐퍼 설치(VP_FWU_SAD_Installed = 1) 때만 걸린다.

| 행 | 해석 |
|---:|---|
| 20 | *[주석] 장치 고장 원인 모으기* |
| 21 | *[주석] 장치 고장 상태를 상위에 알리는 용도다. 옆 FWU와의 협조 운전은 상위에서 판단한다.* |
| 22 | *[주석] 개별 PICV 알람과 Damper Signal Alarm의 추가 댐퍼 알람은 Failover 조건에 넣지 않는다. 댐퍼 원인 2개는 댐퍼 설치(VP_FWU_SAD_Installed = 1) 때만 걸린다.* |
| 23 | 댐퍼 미개방 알람 (`VP_FWU_SAD_Not_Open_Alarm`) = TRUE(1) **또는** 댐퍼 전폐 알람 (`VP_FWU_SAD_Full_Close_Alarm`) = TRUE(1) **또는** 팬 종합 고장 알람 (`VP_FWU_SF_Failure_Alarm`) = TRUE(1) 이면 : |
| 24 | &emsp;→&nbsp;`mbFailTotal` ← TRUE(1) |
| 25 | 23행 조건이 성립하지 않으면 : |
| 26 | &emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |

<a id="section-3"></a>

## 28~38행 · Failover 알람: 처음 걸릴 때 P11에 운전 OFF를 한 번 써 둔다

> 계속 세워 두거나 재기동을 막는 것은 아니고, 더 높은 우선순위의 ON이 있으면 그쪽이 이긴다.

| 행 | 해석 |
|---:|---|
| 28 | *[주석] Failover 알람: 처음 걸릴 때 P11에 운전 OFF를 한 번 써 둔다* |
| 29 | *[주석] 계속 세워 두거나 재기동을 막는 것은 아니고, 더 높은 우선순위의 ON이 있으면 그쪽이 이긴다.* |
| 30 | `mbFailTotal` = TRUE(1) 이면 : |
| 31 | &emsp;→&nbsp;타이머 `FAILOVER_CONFIRM_TIMER`(1번: Failover 원인이 이어진 시간) 경과시간 > `FAILOVER_CONFIRM_SECONDS`(5) **그리고** Failover 알람 (`VP_FWU_Failover_Alarm`) = FALSE(0) 이면 : |
| 32 | &emsp;&emsp;→&nbsp;Failover 알람 (`VP_FWU_Failover_Alarm`)에 TRUE(1) 기록 — 기본 우선순위(P5) |
| 33 | &emsp;&emsp;→&nbsp;운전 명령(BMS) (`VP_FWU_Command`)에 OFF(0) 기록 — 우선순위 P11 |
| 34 | &emsp;&emsp;→&nbsp;운전 명령(HMI) (`VP_FWU_Command_HMI`)에 OFF(0) 기록 — 우선순위 P11 |
| 35 | &emsp;→&nbsp;31행 조건이 성립하지 않으면 : |
| 36 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 37 | 30행 조건이 성립하지 않으면 : |
| 38 | &emsp;→&nbsp;타이머 `FAILOVER_CONFIRM_TIMER`(1번: Failover 원인이 이어진 시간)를 0초로 초기화 |

<a id="section-4"></a>

## 40~56행 · Reset: 원인이 없어진 뒤에 Reset을 해야 알람이 꺼진다

> HMI/BMS가 더 높은 우선순위로 Reset을 썼다면 그 입력도 직접 풀어야 한다.

| 행 | 해석 |
|---:|---|
| 40 | *[주석] Reset: 원인이 없어진 뒤에 Reset을 해야 알람이 꺼진다* |
| 41 | *[주석] HMI/BMS가 더 높은 우선순위로 Reset을 썼다면 그 입력도 직접 풀어야 한다.* |
| 42 | Failover Reset 입력 (`VP_FWU_Failover_Reset`) = TRUE(1) 이면 : |
| 43 | &emsp;→&nbsp;`mbFailTotal` = FALSE(0) 이면 : |
| 44 | &emsp;&emsp;→&nbsp;Failover 알람 (`VP_FWU_Failover_Alarm`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 45 | &emsp;→&nbsp;43행 조건이 성립하지 않으면 : |
| 46 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 47 | &emsp;→&nbsp;타이머 `FAILOVER_RESET_TIMER`(2번: Reset 입력이 켜져 있던 시간) 경과시간 > `FAILOVER_RESET_HOLD_SECONDS`(5) 이면 : |
| 48 | &emsp;&emsp;→&nbsp;Failover Reset 입력 (`VP_FWU_Failover_Reset`)에 FALSE(0) 기록 — 우선순위 P11 |
| 49 | &emsp;&emsp;→&nbsp;타이머 `FAILOVER_RESET_TIMER`(2번: Reset 입력이 켜져 있던 시간)를 0초로 초기화 |
| 50 | &emsp;→&nbsp;47행 조건이 성립하지 않으면 : |
| 51 | &emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 52 | 42행 조건이 성립하지 않으면 : |
| 53 | &emsp;→&nbsp;타이머 `FAILOVER_RESET_TIMER`(2번: Reset 입력이 켜져 있던 시간)를 0초로 초기화 |
| 55 | *[주석] JSY 2026-11-23 수정 구간 끝. 주제 = Coding Rule 적용(매크로 상수, 변수명, if-else 짝 맞춤, 주석)* |
| 56 | *[주석] LJH 2026-11-17 수정 구간 끝. 주제 = 기존 Failover 원인과 래치 유지* |
