# PICV Control 줄별 해석

> **대상 코드** : `fwu_v3/Logic/PICV Control.py` (82 줄)  
> **기준** : `sy 브랜치 2026-11-23 (naming rule·관제점 이름 변경 반영)`  
> **행** = 코드 줄 번호 (빈 줄은 생략)  
> **표기** : `→` 들여쓰기 단계 · *[주석]* 코드 안 주석 · `이름` 코드 안 상수·변수 · **※** 읽을 때 주의할 점

네 PICV에 공통 개도 명령 하나를 낸다. 자동 운전 중에는 급기 온도(SAT) 기준 PI 제어를 하고, SAT 고장 시에는 사용자 설정에 따라 마지막 위치를 유지하거나 안전 위치로 보낸다. 비상정지 때는 밸브를 닫는다.

**목차**

- [1~33행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수](#section-1)
- [35~82행 · 비상정지가 아닐 때: 자동이면 SAT 기준으로 밸브를 제어하고, 수동이면 로직 출력을 내려놓는다](#section-2)

**※ 공통 표기**: 매크로 상수 TRUE·ON·SET·TMR_READ·DEC = 1, FALSE·OFF·CLEAR·TMR_CLEAR·INC = 0. `SECTIMER(타이머, TMR_CLEAR)`는 타이머를 0초로 초기화, `SECTIMER(타이머, TMR_READ)`는 경과시간 확인이다. P번호가 없는 쓰기(`WRITEPOINT`)는 기본 우선순위 P5를 쓴다. 조건이 거짓이라고 관제점이 저절로 0이 되지는 않는다. 해당 분기에 쓰기가 없으면 이전 값이 남는다. 대문자 이름은 상수, `m`으로 시작하는 이름은 이 파일의 전역변수, `b`가 붙은 이름은 참/거짓 값이다.

<a id="section-1"></a>

## 1~33행 · 머리말 · 로직 엔진, 상수, 타이머, 전역변수

| 행 | 해석 |
|---:|---|
| 1 | *[주석] LJH 2026-11-17 수정 구간 시작. 주제 = 네 밸브 공통 냉방 명령* |
| 2 | *[주석] JSY 2026-11-23 수정 구간 시작. 주제 = Coding Rule 적용(매크로 상수, 설정값 상수, if-else 짝 맞춤, 주석)* |
| 4 | *[주석] 로직엔진 loading* |
| 5 | DDC 로직 엔진 객체 생성 (이후 engine.xxx로 관제점을 읽고 씀) |
| 7 | *[주석] Macro상수 정의* |
| 8 | 매크로 상수 정의: TMR_READ, SET, ON, TRUE, DEC = 1 (긍정의 의미 또는 1인 인자) |
| 9 | 매크로 상수 정의: TMR_CLEAR, CLEAR, OFF, FALSE, INC = 0 (부정의 의미 또는 0인 인자) |
| 11 | *[주석] DEC/INC는 LOOP2 제어 방향 (DEC: 현재값을 내리는 제어, INC: 현재값을 올리는 제어)* |
| 12 | 상수 `PICV_LOOP` = 1<br>*[주석] 이 로직의 LOOP2 번호 (같은 출력점에는 같은 번호를 쓴다)* |
| 13 | 설정값 상수 `PICV_PGAIN`: PICV PI 비례 게인 (`VP_FWU_PICV_PGain`) 값을 읽어 둠<br>*[주석] SAT 기준 냉수밸브 PI 제어의 P 게인* |
| 14 | 설정값 상수 `PICV_IGAIN`: PICV PI 적분 게인 (`VP_FWU_PICV_IGain`) 값을 읽어 둠<br>*[주석] 같은 제어의 I 게인* |
| 15 | 설정값 상수 `PICV_FAIL_MODE`: SAT 고장 시 밸브 위치 선택(0 마지막 위치 유지, 1 안전 위치) (`VP_FWU_PICV_Fail_Mode`) 값을 읽어 둠<br>*[주석] SAT 고장 시 밸브 위치 선택. 0 = 마지막 위치 유지, 1 = 안전 위치* |
| 16 | 설정값 상수 `PICV_SAFE_POSITION`: 밸브 안전 위치 개도(%) (`VP_FWU_PICV_Safe_Position`) 값을 읽어 둠<br>*[주석] 안전 위치 개도(%)* |
| 18 | *[주석] 타이머 정의: 이 로직은 타이머를 쓰지 않는다* |
| 20 | *[주석] AO3(FWU_PICV_CONTROL) 공통 명령을 네 밸브에 전달한다. 개도·유량·온도는 RS485로 각각 수신.* |
| 21 | *[주석] 유량 모드에서 100%는 설정 최대 유량 요구이며 실제 개도 100%와 다르다.* |
| 22 | *[주석] SAT 고장 시 100% 요구 유지. 복구 후 PI 누적 상태에 따른 출력·온도 변동 확인.* |
| 23 | *[주석] (JSY 2026-11-23) 아래 코드 추가: SAT 센서 고장 시 밸브 위치를 정하는 보호 기능* |
| 24 | *[주석] - VP_FWU_PICV_Fail_Mode = 1(기본) : 안전 위치(VP_FWU_PICV_Safe_Position, 기본 100%)로 보낸다. 기존 동작과 같다.* |
| 25 | *[주석] - VP_FWU_PICV_Fail_Mode = 0 : 고장 직전 PI 출력(마지막 위치)을 그대로 유지한다.* |
| 26 | *[주석] 단, 운전을 시작하고 PI 제어가 한 번도 돌기 전에 고장이 나면 '직전 명령'이 없으므로 안전 위치로 보낸다.* |
| 27 | *[주석] PI가 돌았는지는 VP_FWU_PICV_PI_Started에 기억하고, 운전 명령 OFF·수동 모드·비상정지·재부팅 때 지운다.* |
| 28 | *[주석] - 고장 중에 모드를 1→0으로 바꾸면 고장 전 PI 출력이 아니라 그때 나가던 안전 위치 값이 유지된다.* |
| 29 | *[주석] ※ QTS RFP 2.3.E.7(밸브 전원·제어 신호가 끊기거나 DDC가 멈췄을 때 마지막/안전 위치)은 이 코드가 아니라* |
| 30 | *[주석] 밸브 구동부 설정(하드웨어 사양)으로 충족한다. 그때는 DDC 명령이 밸브에 닿지 않아 코드로는 대응할 수 없다.* |
| 31 | *[주석] Command=1이고 팬 정지 상태이면 기존 명령 유지. 비상 P1·원격 P2는 별도 우선.* |
| 32 | *[주석] 수동 Command=0은 자동 닫힘 아님. 무풍 중 냉수 공급에 대한 HMI 안내 검토.* |
| 33 | *[주석] AO 단선·전원 상실 시 위치는 제조사 확인 후 대응 기능 적용 여부 결정.* |

<a id="section-2"></a>

## 35~82행 · 비상정지가 아닐 때: 자동이면 SAT 기준으로 밸브를 제어하고, 수동이면 로직 출력을 내려놓는다

| 행 | 해석 |
|---:|---|
| 35 | *[주석] 비상정지가 아닐 때: 자동이면 SAT 기준으로 밸브를 제어하고, 수동이면 로직 출력을 내려놓는다* |
| 36 | 비상정지 입력(DI) (`FWU_EMERGENCY`) = FALSE(0) 이면 : |
| 37 | &emsp;→&nbsp;PICV 공통 개도 명령(AO) (`FWU_PICV_CONTROL`)의 P1 쓰기 해제<br>*[주석] 비상정지 때 걸어 둔 P1 해제* |
| 39 | &emsp;→&nbsp;운전 모드(1 자동, 0 수동) (`VP_FWU_Operation_Mode`) = TRUE(1) 이면 :<br>*[주석] Operation_Mode 1 = 자동, 0 = 수동* |
| 40 | &emsp;&emsp;→&nbsp;*[주석] 운전 명령이 있고 팬이 돌 때만 SAT 기준으로 제어한다* |
| 41 | &emsp;&emsp;→&nbsp;운전 명령(BMS) (`VP_FWU_Command`) = ON(1) **그리고** 팬 운전 상태 (`VP_FWU_SF_Status`) = ON(1) 이면 : |
| 42 | &emsp;&emsp;&emsp;→&nbsp;급기 온도(SAT) 센서 고장 알람 (`VP_FWU_SAT_Failure_Alarm`) = TRUE(1) 이면 :<br>*[주석] SAT 센서 고장 여부 확인* |
| 43 | &emsp;&emsp;&emsp;&emsp;→&nbsp;*[주석] JSY 2026-11-23 수정 구간 시작. 주제 = SAT 센서 고장 시 밸브 마지막/안전 위치 선택 (보호 기능)* |
| 44 | &emsp;&emsp;&emsp;&emsp;→&nbsp;*[주석] SAT를 믿을 수 없어 PI 제어를 멈춘다. 이때 밸브 위치는 HMI 설정(Fail_Mode)으로 고른다* |
| 45 | &emsp;&emsp;&emsp;&emsp;→&nbsp;`PICV_FAIL_MODE`(설정값) = TRUE(1) 이면 :<br>*[주석] 1 = 안전 위치* |
| 46 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PICV 공통 개도 명령(AO) (`FWU_PICV_CONTROL`)에 `PICV_SAFE_POSITION`(설정값) 기록 — 기본 우선순위(P5) |
| 47 | &emsp;&emsp;&emsp;&emsp;→&nbsp;45행 조건이 성립하지 않으면 : |
| 48 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;*[주석] 0 = 마지막 위치 유지. 단, 이번 운전에서 PI가 한 번도 안 돌았으면 직전 명령이 없으므로 안전 위치* |
| 49 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;이번 운전에서 PI 제어가 돌았는지 기억(재부팅 시 지워짐) (`VP_FWU_PICV_PI_Started`) = TRUE(1) 이면 : |
| 50 | &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) — 출력을 새로 쓰지 않아 고장 직전 명령이 그대로 남는다 |
| 51 | &emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;49행 조건이 성립하지 않으면 : |
| 52 | &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;→&nbsp;PICV 공통 개도 명령(AO) (`FWU_PICV_CONTROL`)에 `PICV_SAFE_POSITION`(설정값) 기록 — 기본 우선순위(P5) |
| 53 | &emsp;&emsp;&emsp;&emsp;→&nbsp;*[주석] JSY 2026-11-23 수정 구간 끝. 주제 = SAT 센서 고장 시 밸브 마지막/안전 위치 선택 (보호 기능)* |
| 54 | &emsp;&emsp;&emsp;→&nbsp;42행 조건이 성립하지 않으면 :<br>*[주석] SAT 센서 정상일 때 PI 제어 수행* |
| 55 | &emsp;&emsp;&emsp;&emsp;→&nbsp;*[주석] LOOP2(방향, 현재값, 출력, 목표값, P, I, D, 샘플링(초), 시작 출력, 최소, 최대, 루프 번호, 데드밴드)* |
| 56 | &emsp;&emsp;&emsp;&emsp;→&nbsp;PI 제어(LOOP2) — 방향 DEC: 현재값이 목표보다 높으면 출력을 올리는 방향. 현재값 = 급기 온도(SAT) 센서값 (`FWU_SAT`), 출력 = PICV 공통 개도 명령(AO) (`FWU_PICV_CONTROL`), 목표값 = 급기 온도 목표값(PICV 제어) (`VP_FWU_PICV_SAT_SP`), P = `PICV_PGAIN`(설정값), I = `PICV_IGAIN`(설정값), D = 0, 샘플링 = 1, 시작 출력 = 100, 출력 범위 = PICV 최소 개도(출력 하한) 설정 (`VP_FWU_PICV_MinSP`) ~ 100, 루프 번호 = `PICV_LOOP`(1), 데드밴드 = 0 |
| 57 | &emsp;&emsp;&emsp;&emsp;→&nbsp;이번 운전에서 PI 제어가 돌았는지 기억(재부팅 시 지워짐) (`VP_FWU_PICV_PI_Started`)에 TRUE(1) 기록 — 기본 우선순위(P5)<br>*[주석] 이번 운전에서 PI가 돌았다는 표시 (마지막 위치 유지 판단에 씀)* |
| 58 | &emsp;&emsp;→&nbsp;41행 조건이 성립하지 않으면 : |
| 59 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) — 명령은 있는데 팬이 아직 안 돌면 직전 출력을 그대로 둔다 |
| 61 | &emsp;&emsp;→&nbsp;*[주석] 운전 명령이 꺼지면 PI 누적값을 지우고 밸브를 닫는다* |
| 62 | &emsp;&emsp;→&nbsp;운전 명령(BMS) (`VP_FWU_Command`) = OFF(0) 이면 : |
| 63 | &emsp;&emsp;&emsp;→&nbsp;PI 루프 `PICV_LOOP`(1) 누적값 초기화 |
| 64 | &emsp;&emsp;&emsp;→&nbsp;이번 운전에서 PI 제어가 돌았는지 기억(재부팅 시 지워짐) (`VP_FWU_PICV_PI_Started`)에 FALSE(0) 기록 — 기본 우선순위(P5)<br>*[주석] 운전이 끝났으니 PI 실행 기록도 지운다* |
| 65 | &emsp;&emsp;&emsp;→&nbsp;PICV 공통 개도 명령(AO) (`FWU_PICV_CONTROL`)에 0 기록 — 기본 우선순위(P5) |
| 66 | &emsp;&emsp;→&nbsp;62행 조건이 성립하지 않으면 :<br>*[주석] 운전 명령이 켜져 있으면 아무 것도 안 함* |
| 67 | &emsp;&emsp;&emsp;→&nbsp;아무것도 하지 않음 (do_nothing) |
| 68 | &emsp;&emsp;→&nbsp;PICV 공통 개도 명령(AO) (`FWU_PICV_CONTROL`)에 현재 값을 그대로 기록 — 우선순위 P11 |
| 69 | &emsp;→&nbsp;39행 조건이 성립하지 않으면 : |
| 70 | &emsp;&emsp;→&nbsp;*[주석] 수동 모드: 로직이 쓴 P5를 지워 사람이 넣은 값이 적용되게 한다* |
| 71 | &emsp;&emsp;→&nbsp;PI 루프 `PICV_LOOP`(1) 누적값 초기화 |
| 72 | &emsp;&emsp;→&nbsp;이번 운전에서 PI 제어가 돌았는지 기억(재부팅 시 지워짐) (`VP_FWU_PICV_PI_Started`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 73 | &emsp;&emsp;→&nbsp;PICV 공통 개도 명령(AO) (`FWU_PICV_CONTROL`)의 P5 쓰기 해제 |
| 74 | 36행 조건이 성립하지 않으면 : |
| 75 | &emsp;→&nbsp;*[주석] 비상정지: 밸브를 P1으로 닫는다* |
| 76 | &emsp;→&nbsp;PI 루프 `PICV_LOOP`(1) 누적값 초기화 |
| 77 | &emsp;→&nbsp;이번 운전에서 PI 제어가 돌았는지 기억(재부팅 시 지워짐) (`VP_FWU_PICV_PI_Started`)에 FALSE(0) 기록 — 기본 우선순위(P5) |
| 78 | &emsp;→&nbsp;PICV 공통 개도 명령(AO) (`FWU_PICV_CONTROL`)에 0 기록 — 우선순위 P1 |
| 79 | &emsp;→&nbsp;PICV 공통 개도 명령(AO) (`FWU_PICV_CONTROL`)에 0 기록 — 우선순위 P11 |
| 81 | *[주석] JSY 2026-11-23 수정 구간 끝. 주제 = Coding Rule 적용(매크로 상수, 설정값 상수, if-else 짝 맞춤, 주석)* |
| 82 | *[주석] LJH 2026-11-17 수정 구간 끝. 주제 = 네 밸브 공통 냉방 명령* |
