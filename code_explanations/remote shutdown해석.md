# Remote Shutdown 줄별 해석

> **대상 코드** : `fwu_v2/Logic/Remote Shutdown.py`  
> **기준 커밋** : `0e0a374d983bf194220e75da79b28598673bc0fa` (`jh`)  
> **행** = 코드 줄 번호 (빈 줄은 생략)  
> **표기** : `→` 들여쓰기 단계 · *[주석]* 코드 안 주석 · **※** 읽을 때 주의할 점

원격 정지 또는 정지하도록 설정된 화재 알람에 따라 팬과 밸브 출력을 강제 정지한다.

**목차**

- [1~11행 · 화재 입력 확인](#section-1)
- [13~20행 · 강제 정지 여부 결정](#section-2)
- [22~48행 · 강제 정지 출력](#section-3)
- [49~72행 · 강제 정지 해제](#section-4)

**※ 공통 표기**: 알람 1=발생, 0=해제. 조건이 거짓이라고 모든 관제점이 자동으로 0이 되지는 않는다. 해당 분기에 쓰기 명령이 없으면 이전 값이 남는다. `SECTIMER(..., 0)`은 타이머 초기화, `SECTIMER(..., 1)`은 경과시간 확인이다. 명시적 P번호가 없는 쓰기는 `WRITEPOINT` 기본 우선순위를 사용한다.

<a id="section-1"></a>

## 1~11행 · 화재 입력 확인

> 감지 입력이 3초 초과 지속되면 화재 알람

| 행 | 해석 |
|---:|---|
| 1 | *[주석] LJH[2026.1117]원격 및 연기 정지 우선순위 유지: S ----* |
| 2 | 상수: 화재 확인 타이머 번호 = 0 (`FIRE_CONFIRM_TIMER`) |
| 3 | 상수: 화재 확인시간(초) = 3 (`FIRE_CONFIRM_SECONDS`) |
| 4 | DDC 로직 엔진 객체 생성 (이후 engine.xxx로 관제점을 읽고 씀) |
| 6 | 화재 감지 입력 (`FWU_FIRE_ALARM`) = 1이면 : |
| 7 | &emsp;→&nbsp;화재 확인 타이머(번호 0) 경과시간이 3초 초과하면 : |
| 8 | &emsp;&emsp;→&nbsp;화재 확정 알람 (`VP_FWU_Fire_Alarm`)에 1 (알람 발생) 기록 — 기본 쓰기 우선순위 |
| 9 | 6행 조건이 성립하지 않으면 : |
| 10 | &emsp;→&nbsp;화재 확인 타이머(번호 0)를 0초로 초기화 |
| 11 | &emsp;→&nbsp;화재 확정 알람 (`VP_FWU_Fire_Alarm`)에 0 (알람 해제) 기록 — 기본 쓰기 우선순위 |

<a id="section-2"></a>

## 13~20행 · 강제 정지 여부 결정

> 원격 정지 또는 화재 알람과 정지 설정의 조합

| 행 | 해석 |
|---:|---|
| 13 | *[주석] Smoke_Action_Set: 0=알람만, 1=정지. HMI: 화재 감지 시 운전 방식.* |
| 14 | *[주석] 일반 운전 ON/OFF와 별개의 강제 정지이며 로컬·수동 운전에도 적용한다.* |
| 15 | *[주석] 하드웨어 화재 차단 회로는 이 설정으로 무효화되지 않는다.* |
| 16 | 강제 정지 필요 여부 (`b_shutdown`) = 0 (아니오) |
| 17 | 원격 강제 정지 명령 (`VP_FWU_Remote_Shutdown_Command`) = 1이면 : |
| 18 | &emsp;→&nbsp;강제 정지 필요 여부 (`b_shutdown`) = 1 (예) |
| 19 | 화재 확정 알람 (`VP_FWU_Fire_Alarm`) = 1 **그리고** 화재 시 운전 방식 설정(0=알람만, 1=정지) (`VP_FWU_Smoke_Action_Set`) = 1이면 : |
| 20 | &emsp;→&nbsp;강제 정지 필요 여부 (`b_shutdown`) = 1 (예) |

<a id="section-3"></a>

## 22~48행 · 강제 정지 출력

> 팬과 밸브는 P2, 운전 명령 등은 P11 기록

| 행 | 해석 |
|---:|---|
| 22 | 강제 정지 필요 여부 = 1이면 : |
| 23 | &emsp;→&nbsp;FWU 운전 명령 (`VP_FWU_Command`)에 0 (정지) 기록 — P11 |
| 24 | &emsp;→&nbsp;HMI 운전 명령 (`VP_FWU_Command-HMI`)에 0 (정지) 기록 — P11 |
| 25 | &emsp;→&nbsp;밸브 4대 공통 제어 출력 (`FWU_PICV_CONTROL`)에 0 (냉방 요구 0%) 기록 — P2 |
| 26 | &emsp;→&nbsp;밸브 4대 공통 제어 출력 (`FWU_PICV_CONTROL`)에 0 (냉방 요구 0%) 기록 — P11 |
| 27 | &emsp;→&nbsp;팬 속도 요구값 (`VP_FWU_SF_Speed_Value`)에 0 기록 — P11 |
| 28 | &emsp;→&nbsp;팬 1~4번 공통 속도 출력 (`FWU_SF-1_4_SPEED_CONTROL`)에 0 기록 — P2 |
| 29 | &emsp;→&nbsp;팬 5~8번 공통 속도 출력 (`FWU_SF-5_8_SPEED_CONTROL`)에 0 기록 — P2 |
| 30 | &emsp;→&nbsp;팬 1번 목표 회전수 (`FWU_SF-1.Target_RPM_Set`)에 0 기록 — P2 |
| 31 | &emsp;→&nbsp;팬 2번 목표 회전수 (`FWU_SF-2.Target_RPM_Set`)에 0 기록 — P2 |
| 32 | &emsp;→&nbsp;팬 3번 목표 회전수 (`FWU_SF-3.Target_RPM_Set`)에 0 기록 — P2 |
| 33 | &emsp;→&nbsp;팬 4번 목표 회전수 (`FWU_SF-4.Target_RPM_Set`)에 0 기록 — P2 |
| 34 | &emsp;→&nbsp;팬 5번 목표 회전수 (`FWU_SF-5.Target_RPM_Set`)에 0 기록 — P2 |
| 35 | &emsp;→&nbsp;팬 6번 목표 회전수 (`FWU_SF-6.Target_RPM_Set`)에 0 기록 — P2 |
| 36 | &emsp;→&nbsp;팬 7번 목표 회전수 (`FWU_SF-7.Target_RPM_Set`)에 0 기록 — P2 |
| 37 | &emsp;→&nbsp;팬 8번 목표 회전수 (`FWU_SF-8.Target_RPM_Set`)에 0 기록 — P2 |
| 38 | &emsp;→&nbsp;팬 1번 운전 명령 (`FWU_SF-1.Run_Command`)에 0 (정지) 기록 — P2 |
| 39 | &emsp;→&nbsp;팬 2번 운전 명령 (`FWU_SF-2.Run_Command`)에 0 (정지) 기록 — P2 |
| 40 | &emsp;→&nbsp;팬 3번 운전 명령 (`FWU_SF-3.Run_Command`)에 0 (정지) 기록 — P2 |
| 41 | &emsp;→&nbsp;팬 4번 운전 명령 (`FWU_SF-4.Run_Command`)에 0 (정지) 기록 — P2 |
| 42 | &emsp;→&nbsp;팬 5번 운전 명령 (`FWU_SF-5.Run_Command`)에 0 (정지) 기록 — P2 |
| 43 | &emsp;→&nbsp;팬 6번 운전 명령 (`FWU_SF-6.Run_Command`)에 0 (정지) 기록 — P2 |
| 44 | &emsp;→&nbsp;팬 7번 운전 명령 (`FWU_SF-7.Run_Command`)에 0 (정지) 기록 — P2 |
| 45 | &emsp;→&nbsp;팬 8번 운전 명령 (`FWU_SF-8.Run_Command`)에 0 (정지) 기록 — P2 |
| 46 | &emsp;→&nbsp;팬 운전 상태 (`VP_FWU_SF_Status`) = 0이면 : |
| 47 | &emsp;&emsp;→&nbsp;댐퍼 4대 공통 명령(1=열기, 0=닫기) (`FWU_SAD-1_4_COMMAND`)에 0 (닫기) 기록 — P2 |
| 48 | &emsp;&emsp;→&nbsp;댐퍼 4대 공통 명령(1=열기, 0=닫기) (`FWU_SAD-1_4_COMMAND`)에 0 (닫기) 기록 — P11 |

<a id="section-4"></a>

## 49~72행 · 강제 정지 해제

> P2 쓰기를 내려놓고 다른 우선순위의 명령에 맡김

| 행 | 해석 |
|---:|---|
| 49 | 22행 조건이 성립하지 않으면 : |
| 50 | &emsp;→&nbsp;*[주석] P2 해제 후 상위 우선순위에 남은 운전 명령에 따라 재기동할 수 있다.* |
| 51 | &emsp;→&nbsp;*[주석] P11 OFF는 별도 재기동 금지 래치가 아니다.* |
| 52 | &emsp;→&nbsp;밸브 4대 공통 제어 출력 (`FWU_PICV_CONTROL`)의 P2 쓰기를 해제 (0을 쓰는 것이 아니라 이 우선순위의 명령을 내려놓음) |
| 53 | &emsp;→&nbsp;팬 1~4번 공통 속도 출력 (`FWU_SF-1_4_SPEED_CONTROL`)의 P2 쓰기를 해제 (0을 쓰는 것이 아니라 이 우선순위의 명령을 내려놓음) |
| 54 | &emsp;→&nbsp;팬 5~8번 공통 속도 출력 (`FWU_SF-5_8_SPEED_CONTROL`)의 P2 쓰기를 해제 (0을 쓰는 것이 아니라 이 우선순위의 명령을 내려놓음) |
| 55 | &emsp;→&nbsp;팬 1번 목표 회전수 (`FWU_SF-1.Target_RPM_Set`)의 P2 쓰기를 해제 (0을 쓰는 것이 아니라 이 우선순위의 명령을 내려놓음) |
| 56 | &emsp;→&nbsp;팬 2번 목표 회전수 (`FWU_SF-2.Target_RPM_Set`)의 P2 쓰기를 해제 (0을 쓰는 것이 아니라 이 우선순위의 명령을 내려놓음) |
| 57 | &emsp;→&nbsp;팬 3번 목표 회전수 (`FWU_SF-3.Target_RPM_Set`)의 P2 쓰기를 해제 (0을 쓰는 것이 아니라 이 우선순위의 명령을 내려놓음) |
| 58 | &emsp;→&nbsp;팬 4번 목표 회전수 (`FWU_SF-4.Target_RPM_Set`)의 P2 쓰기를 해제 (0을 쓰는 것이 아니라 이 우선순위의 명령을 내려놓음) |
| 59 | &emsp;→&nbsp;팬 5번 목표 회전수 (`FWU_SF-5.Target_RPM_Set`)의 P2 쓰기를 해제 (0을 쓰는 것이 아니라 이 우선순위의 명령을 내려놓음) |
| 60 | &emsp;→&nbsp;팬 6번 목표 회전수 (`FWU_SF-6.Target_RPM_Set`)의 P2 쓰기를 해제 (0을 쓰는 것이 아니라 이 우선순위의 명령을 내려놓음) |
| 61 | &emsp;→&nbsp;팬 7번 목표 회전수 (`FWU_SF-7.Target_RPM_Set`)의 P2 쓰기를 해제 (0을 쓰는 것이 아니라 이 우선순위의 명령을 내려놓음) |
| 62 | &emsp;→&nbsp;팬 8번 목표 회전수 (`FWU_SF-8.Target_RPM_Set`)의 P2 쓰기를 해제 (0을 쓰는 것이 아니라 이 우선순위의 명령을 내려놓음) |
| 63 | &emsp;→&nbsp;팬 1번 운전 명령 (`FWU_SF-1.Run_Command`)의 P2 쓰기를 해제 (0을 쓰는 것이 아니라 이 우선순위의 명령을 내려놓음) |
| 64 | &emsp;→&nbsp;팬 2번 운전 명령 (`FWU_SF-2.Run_Command`)의 P2 쓰기를 해제 (0을 쓰는 것이 아니라 이 우선순위의 명령을 내려놓음) |
| 65 | &emsp;→&nbsp;팬 3번 운전 명령 (`FWU_SF-3.Run_Command`)의 P2 쓰기를 해제 (0을 쓰는 것이 아니라 이 우선순위의 명령을 내려놓음) |
| 66 | &emsp;→&nbsp;팬 4번 운전 명령 (`FWU_SF-4.Run_Command`)의 P2 쓰기를 해제 (0을 쓰는 것이 아니라 이 우선순위의 명령을 내려놓음) |
| 67 | &emsp;→&nbsp;팬 5번 운전 명령 (`FWU_SF-5.Run_Command`)의 P2 쓰기를 해제 (0을 쓰는 것이 아니라 이 우선순위의 명령을 내려놓음) |
| 68 | &emsp;→&nbsp;팬 6번 운전 명령 (`FWU_SF-6.Run_Command`)의 P2 쓰기를 해제 (0을 쓰는 것이 아니라 이 우선순위의 명령을 내려놓음) |
| 69 | &emsp;→&nbsp;팬 7번 운전 명령 (`FWU_SF-7.Run_Command`)의 P2 쓰기를 해제 (0을 쓰는 것이 아니라 이 우선순위의 명령을 내려놓음) |
| 70 | &emsp;→&nbsp;팬 8번 운전 명령 (`FWU_SF-8.Run_Command`)의 P2 쓰기를 해제 (0을 쓰는 것이 아니라 이 우선순위의 명령을 내려놓음) |
| 71 | &emsp;→&nbsp;댐퍼 4대 공통 명령(1=열기, 0=닫기) (`FWU_SAD-1_4_COMMAND`)의 P2 쓰기를 해제 (0을 쓰는 것이 아니라 이 우선순위의 명령을 내려놓음) |
| 72 | *[주석] LJH[2026.1117]원격 및 연기 정지 우선순위 유지: E ----* |

## 읽을 때 짚어둘 점

- **※** P2 해제는 출력에 0을 다시 쓰는 동작이 아니다. 남아 있는 다른 우선순위 명령이 적용될 수 있다.
- **※** P11 OFF 기록은 재기동 금지 래치가 아니다. 더 높은 우선순위의 ON이 남아 있으면 정지 해제 후 재기동할 수 있다.
- **※** 댐퍼 닫기 명령은 팬 정지 상태가 확인된 경우에만 쓴다. 이 블록은 밸브 닫힘 피드백을 기다린 뒤 팬을 끄는 순서가 아니다.
