# QTS 요구사항 기반 FWU 로직 수정 검토서 (rev.4)

**검토일:** 2026-11-12
**대상:** QTS `FWU(390 kW)` 시트 / `FWU-F8-ATS` 로직 8개 및 DDC 설정 파일
**기준 코드:** `sy` 브랜치, 2026-11-12 양산 범위 정리 반영 (`FWU-F8-ATS/Logic/*.py`, 총 1,536줄)
**문서 단계:** 양산 로직 범위 정리 후 검토 (현장 시험 전)

**rev.4 변경 사항 (rev.3 대비)**
- **양산 로직 범위 원칙**을 정하고(§2) 적용했다. FWU 한 대가 혼자 판단할 수 없는 상위 조율 기능(그룹 제어, 인접 존 보상, Backup 운전)은 로직에서 빼고, 관련 관제점은 정의만 남겼다(예약).
- 동작에 영향 없는 중복·미사용 코드(HZT 게인 읽기, ΔT 중복 계산)를 뺐다.
- 상위 제어단이 빠진 기능을 구현할 때 쓸 관제점을 `QTS_신규_관제점_목록.xlsx` 4번 시트로 정리했다(§7).
- 데이터센터 양산 적용 판단을 추가했다(§10).

---

## 1. 결론

1. QTS가 FWU 자체에 요구하는 소프트웨어 기능은 반영했다: BMS 통신 이상 시 팬 동작 선택(129~131), 연기 감지 시 계속/정지 선택(143), 팬별 고장(109), 누수 알람(142), 필터 알람(104·141), ATS·유량계 통신 감시(140·148), 원격 온도·차압·환기온도 기반 제어(124).
2. 양산 로직에는 **FWU 한 대의 운전·보호·감시 기능만** 남았다. 그룹 제어, 인접 존 보상, Backup 운전은 상위 제어단(BMS·DCIM)이 기존 명령점으로 구현한다.
3. **양산 적용 판단: 조건부 적합.** 로직 구조와 동작은 데이터센터 FWU 양산 로직의 기반으로 쓸 수 있다. 다만 §10의 P0 4건을 처리하고 §12 현장 시험을 거친 뒤 적용해야 한다.

## 2. 양산 로직 범위 원칙

| 넣는 것 (양산 로직) | 빼는 것 (상위 제어단 또는 현장 엔지니어링) |
| --- | --- |
| FWU 한 대가 자기 센서·상태로 판단할 수 있는 운전·보호·감시 | 여러 FWU 정보를 모아야 판단할 수 있는 조율 기능 |
| QTS가 FWU 자체 기능으로 요구한 것 | 현장 구성·운영 정책에 따라 있고 없고가 달라지는 기능 |
| 안전 관련 (비상정지, 원격정지, 연기 정지 선택) | 안전·필수 기능이 아닌 부가 기능 |

| 기능 | 판단 | 처리 |
| --- | --- | --- |
| 그룹 제어 (Failover 원인 4) | 상위 조율 | **로직 제거**, `VP_FWU_Group Control Mode` 정의 유지 |
| 인접 존 보상 | 상위 조율 (이웃 정보 필요) | **로직 제거**, Adj·가중치·여유·Comp PV 정의 유지 |
| Backup 운전 | 상위 조율 (이웃 고장 판단 필요) | **로직 제거**, `VP_FWU_Backup Operation`·`PICV SAT SP Active` 정의 유지 |
| Failover 원인 1~3, 래치, 정지 | FWU 자체 고장 처리 | 유지 |
| BMS 통신 감시 | FWU 자체 판단, QTS 129~131 | 유지 |
| CZT·RDP 존 센서 처리와 제어모드 | QTS 124 | 유지 |
| HZT·CZH 집계, 존 상하한 알람 | FWU 자체 감시 (센서값이 FWU에 들어옴) | 유지 |
| 냉수 공급 상태 조건 | 기본값 1이면 영향 없음, 오경보 방지 | 유지 |

**값과 기능의 구분:** 현장마다 값만 다른 것(설정온도, 평균/최대 선택, 알람 기준)은 설정 관제점으로 남긴다. 기능 자체가 현장마다 있고 없는 것은 양산에서 뺀다.

**현장 추가 로직 규칙(권장):** 양산 파일 8개는 고치지 않는다. 현장 기능은 별도 로직 파일(예: `Site.py`)로 만들어 필요한 현장에서만 `DDC.xml`에 등록한다. 별도 파일은 자기 타이머 0~9를 쓰고, 우선순위 규칙(§8)을 지킨다.

## 3. 검토 근거와 구성

| 자료 | 용도 |
| --- | --- |
| `QTS_Airside Equipment_CDE_260628-2 1.xlsx` | `FWU(390 kW)` 시트 요구사항 (행 번호로 인용) |
| `LDPL Programming Guide-v27.pdf` | 함수 규격(§3~7), 작성 규칙(§8) |
| `FWU-F8-ATS/Logic/*.py` 8개, `DDC.xml`, `ControlPoint/*.xml`, `ModbusServiceInfo.xml` | 로직, 실행 순서, 관제점, BMS 맵 |
| `QTS_SW_통신_관제점_반영현황.xlsx` (ver3) | QTS 반영 현황표 |
| `QTS_신규_관제점_목록.xlsx` | 신규 관제점 9점, 상위 제어 연동 관제점 |
| `FWU_Logic_초보자_설명서.md` | 파일별 줄 해석과 흐름도 |

| 항목 | 내용 |
| --- | --- |
| 통신 포트 | 포트 1 = SF-1~4 (주소 82~85), 포트 2 = SF-5~8 (86~89), 포트 3 = ATS(01)·유량계(02), Modbus RTU 마스터 9600 bps. 포트 4 = BMS용 Modbus RTU 슬레이브 19200 bps |
| BACnet / Modbus TCP | BACnet: Device Instance 3, B/IP(Dnet 76), MS/TP(Dnet 100) - 현장 값 확정 필요. Modbus TCP: 설정 없음 |
| 로직 실행 순서 | Initialization → PICV Control → SF Control → Alarm-1 → Alarm-2 → Alarm-3 → Remote Shutdown → Failover |
| 여유 입력 | DI 4점(CPU00-DI1~4), UI 9점(CPU00-UI1~6, CM02-UI5·6·8) |

## 4. QTS 요구사항 대비 현재 구현

| QTS 행 | 요구사항 | 현재 구현 | 판정 |
| --- | --- | --- | --- |
| 104·141 | 필터 오염 알람 | `FWU_FILTER ALARM` 30초 → `VP_FWU_Filter Alarm` (Alarm-2) | 반영 (VP 정의 필요) |
| 108 | 팬 저속 한계 20 % 이하 | 하한 기능 있음, 기본값 30 % | 설정 변경 필요 |
| 109 | 팬별 고장 감지 | 팬별 RPM 판정 → `SF-1~8 Run Fail Alarm`. 풍량 스위치는 없음 | 기능 반영 |
| 115·124·128 | 2-way 밸브로 급기온도 유지 | PICV SAT PI (목표 `VP_FWU_PICV SAT SP`) | 반영 |
| 120 | 밸브 마지막/안전 위치 | 수동 전환 시 유지, 비상·원격 정지 0 %, SAT 고장 100 % | 부분 |
| 124 | 원격 온도·환기온도·원격 차압 기반 제어 | CZT PV / RAT / RDP PV 팬 PI | 반영 |
| 124 | 급기온도 기반 제어 | 밸브로 SAT 제어, 팬 모드에는 없음 | 부분 (해석 확인) |
| 127 | BMS 팬 속도 쓰기 | Speed SP (HR 1076), 고정값 모드 | 반영 |
| 129~131 | BMS 통신 이상 시 마지막/최대 속도 선택 | `VP_FWU_BMS Comm Fail Mode` | 반영 |
| 132 | 원격 on/off 3단자 | 원격 정지 VP 1점 | 하드웨어 후속 |
| 133 | BMS Points List | V1.3 목록 미확보 | 확인 불가 |
| 138·139 | 냉수 입·출수 온도 | 부품 미확정, 관제점만 예약 | 후속 |
| 140 | 유량계 | `FWU-Flow.Rate` + 통신 이상 감시 | 반영 |
| 142 | 누수 알람, 정지 금지 | 로직 반영 (Alarm-2), 입력점 미정의 | 부분 (부품 확정 후 정의) |
| 143 | 연기 감지 시 계속/정지 선택 | `VP_FWU_Smoke Action` | 반영 |
| 148 | 자동 절체 | ATS 자체 기능, DDC는 통신 감시 | 감시 반영 |

## 5. 코드 변경 내역 (원본 `1ddf755` 대비, 파일별)

| 파일 | 변경 | 근거 |
| --- | --- | --- |
| `SF Control.py` | BMS 통신 이상 시 `BMS Comm Fail Mode` 적용 (RDP·CZT, 원격 고정값) | QTS 129~131 |
| `SF Control.py` | ΔT 루프 방향 type 0 → 1 | 결함 수정 (LDPL §7.3) |
| `SF Control.py` | RDP·CZT 루프 PV를 `Comp PV` → `RDP PV`·`CZT PV` | 인접 존 보상 제거에 따른 연결 |
| `SF Control.py` | Backup 운전 제거, HZT 게인 읽기 2줄·ΔT 중복 계산 1줄 제거 | 양산 범위 / 동작 변화 없음 |
| `PICV Control.py` | Backup 운전 제거, PI 목표를 `PICV SAT SP Active` → `PICV SAT SP` | 양산 범위 (평상시 동작 같음) |
| `Initialization.py` | 인접 존 보상 계산 제거 | 양산 범위 |
| `Remote Shutdown.py` | 연기 감지 3초 → `Fire Alarm`, `Smoke Action = 1`이면 원격 정지 경로로 정지. 정지 중 팬 Run Command 0 (P2) | QTS 143 / 결함 수정 |
| `Failover.py` | 원인 4(그룹 제어) 제거. 주석 오기 −1 C → −0.5 C | 양산 범위 |
| `Alarm-1.py` | 팬별 Run Fail 알람 기록, 유량계 통신 이상 중 유량 기반 PICV 알람 미판정 | QTS 109, 140 |
| `Alarm-2.py` | 누수 알람(타이머 8, 5초), 필터 알람(타이머 9, 30초) | QTS 142, 104·141 |
| `Alarm-3.py` | ATS(타이머 8)·유량계(타이머 9) 통신 이상 10초 | QTS 140, 148 |

## 6. 주요 동작 원칙

### 6.1 BMS 통신 이상 시 팬 속도 (QTS 129~131)

| 상황 | 동작 |
| --- | --- |
| BMS 정상 | 선택 모드대로 제어 |
| 통신 이상 + RDP(2)·CZT(4) 모드 | Comm Fail Mode 0: 현재 속도 유지 (Speed Min 미만이면 최대). 1: Speed Max |
| 통신 이상 + 고정값(0) 모드 + Remote | 위와 같음 (BMS가 쓰는 Speed SP가 멈춤) |
| 통신 이상 + 고정값(0) 모드 + Local | Speed SP 그대로 (터치스크린 값) |
| 통신 이상 + RAT(1)·ΔT(3) 모드 | 자체 센서로 계속 제어 |
| 정상 센서 없음 (BMS 정상) | Speed SP 고정 |

통신 이상은 래치되며 `VP_FWU_BMS PLC Comm Reset`으로 해제한다. PI를 멈출 때 LOOP2_INIT으로 초기화하므로, 복귀하면 PI가 시작값 60 %부터 다시 제어한다.

### 6.2 ΔT 루프 방향

ΔT(RAT − SAT)는 풍량이 줄면 커진다. ΔT < SP면 속도를 내리고 ΔT > SP면 올려야 하므로 LDPL type 1(PV > SP → 출력 증가)이 맞다. LDPL 예제(냉방밸브 type 1, 덕트 정압 팬 type 0)와 기존 루프(PICV·RAT·CZT = 1, RDP = 0)도 같은 정의를 따른다. `VP_FWU_DeltaT SP` 기본값 −2는 ΔT(양수)와 맞지 않아 이 상태로 ΔT 모드를 켜면 팬이 최대로 간다. 사용 전 설계 ΔT로 설정해야 한다.

### 6.3 연기 감지 (QTS 143)

`FWU_FIRE ALARM` 3초 → `Fire Alarm = 1`. Smoke Action 0(기본)은 알람만, 1이면 원격 정지와 같은 경로(운전명령 0 P11, 밸브·팬 출력·팬 Run 0 P2, 팬 정지 후 댐퍼 닫음). 해소되면 P2 해제, 운전명령은 0으로 남아 운전자가 재기동한다.

### 6.4 Failover (FWU 고장 처리)

원인 1~3(댐퍼 미개방 120초, 댐퍼 전폐, 팬 4대 이상 고장)이 5초 계속되면 `Failover Alarm = 1`(래치)과 운전명령 0(P11)을 한 번 쓴다. 원인이 없을 때만 Reset으로 해제된다. 상위 제어단은 이 알람으로 이웃 FWU Backup을 판단한다.

## 7. 상위 제어단 구현 가이드 (FWU 로직에서 뺀 기능)

자세한 관제점과 BMS 맵 주소는 `QTS_신규_관제점_목록.xlsx` 4번 시트.

| 기능 | 상위가 읽는 점 | 상위가 쓰는 점 | 주의 |
| --- | --- | --- | --- |
| Backup 운전 | Failover Alarm, SF Failure, SAD Not Open·Full Close, SF Run Fail, SF Status, Operation Mode, REMOTE SELECTION, BMS PLC Comm Fault | SF Control Select = 0, Speed SP = 최대, PICV SAT SP 낮춤(F8 −0.5 ℃, F4 −1 ℃) | 시작 전 원래 값 저장, 끝나면 복원. 원격·자동 모드에서만 적용됨 |
| 그룹 제어 | SF Status, Failover Alarm, 운전명령 | 운전명령, 원격 정지 | - |
| 인접 존 보상 | 각 FWU의 CZT PV·RDP PV·PV Valid | 이웃이 더우면 CZT SP 낮춤, 이웃 차압 낮으면 RDP SP 높임 | 설정값을 바꾸는 방식이라 복원 책임은 상위 |

예약 관제점(Backup Operation, Group Control Mode, Adj, Comp PV 등)은 FWU가 반응하지 않는다. 상위가 상태 표시용으로 기록할 수만 있다.

## 8. 우선순위(Priority) 규칙

| 우선순위 | 쓰는 곳 | 용도 |
| --- | --- | --- |
| P1 | SF Control, PICV Control (비상 정지) | 출력 0 강제 |
| P2 | Remote Shutdown | 원격·연기 정지 시 출력·팬 Run 0 강제 |
| P5 | `WRITEPOINT` (LDPL 기본) | 일반 제어 |
| P11 | 자동 값 미러, 정지 시 운전명령 0, Reset 0 복귀 | 수동 전환 시 값 유지, 운전명령 |

강제한 우선순위는 조건이 풀리면 `RELEASE_PRI`로 해제한다. 수동 모드에서는 P5를 해제해 P11 유지값이나 운전자 값을 쓴다.

## 9. 타이머 배분 (파일당 0~9)

| 파일 | 사용 |
| --- | --- |
| Initialization | 5 (SF Status 5 s), 6 (Heartbeat 30 s), 7 (Comm Reset 5 s) |
| PICV Control | 없음 |
| SF Control | 1 (속도 출력 5 s) |
| Alarm-1 | 0~9 전부 |
| Alarm-2 | 0~7 존 센서 고장, 8 누수 5 s, 9 필터 30 s |
| Alarm-3 | 0~7 팬 통신, 8 ATS 10 s, 9 유량계 10 s |
| Remote Shutdown | 0 (화재 3 s) |
| Failover | 1 (원인 5 s), 2 (Reset 5 s) |

## 10. 데이터센터 양산 적용 판단

### 10.1 검증한 것

| 항목 | 결과 |
| --- | --- |
| LDPL 규칙 (§11) | 8개 파일 통과 |
| 사용 함수 | 원본 코드와 동일 (`READPOINT`, `WRITEPOINT`, `WRITEPOINT_PRI`, `RELEASE_PRI`, `READPOINT_ALARM`, `SECTIMER`, `LOOP2`, `LOOP2_INIT`, `MAX`, `MIN`) |
| 관제점 이름 | 신규 3점(누수 입력·누수 알람·필터 알람) 외 모두 XML에 존재 |
| 시나리오 모의 실행 | 36개 통과 (BMS 통신 이상, 연기 정지, 원격 정지, 팬 고장, 유량계·ATS 통신, 누수·필터, Failover 래치, 그룹 제어·Backup 무반응 등) + ΔT 폐루프 수렴 확인 |
| 한계 | 모의 엔진과 PI·열평형 모형은 근사. 실제 DDC 시험을 대신하지 못함 |

### 10.2 적용 전 처리 항목

| 우선 | ID | 항목 | 내용 / 권장 |
| --- | --- | --- | --- |
| **P0** | A1 | 신규 관제점 정의 | `VP_FWU_Leak Alarm`, `VP_FWU_Filter Alarm` 정의. `FWU_LEAK DETECT`는 부품 미확정이라도 Alarm-2가 참조하므로, 여유 DI(CPU00-DI1)에 임시로 정의(입력 없으면 0 → 알람 없음)하고 부품 확정 후 단자를 바꾸는 것을 권장 |
| **P0** | A2 | BMS Heartbeat | 맵에 추가하지 않거나 Heartbeat를 지원하지 않는 BMS면 30초 후 통신 이상이 래치되어 ① CZT·RDP 모드 사용 불가 ② **원격 고정값 모드가 BMS의 Speed SP 변경을 무시**(유지 또는 최대). 양산 관점에서 "BMS Heartbeat 사용 여부" 설정 관제점(신규 1점)을 두는 것을 권장 |
| **P0** | A3 | `READPOINT_ALARM` | LDPL v27에는 `ALARM`만 있음. 기존 코드 함수라 유지했으나 현장 DDC에서 동작 확인 |
| **P0** | A4 | 기본값 | ΔT SP −2 → 설계 ΔT, Speed Min 30 % → 20 % 이하(QTS 108), Comm Fail Mode 기본 0/1 결정(냉각 우선이면 1) |
| P1 | B1 | Failover 원인 3 정지 | 팬 4대 이상 고장 시 남은 팬까지 정지. 상위 Backup이 없는 현장이면 이 FWU 냉방이 0이 됨. DoO 의도(역류 방지 등) 확인 |
| P1 | B2 | 연기감지 입력 극성 | Smoke Action = 1로 바꾸기 전 `FWU_FIRE ALARM` 1 = 연기 감지 확인 |
| P2 | B3 | 재부팅 시 팬 기동 (기존, 확인 결과 문제 작음) | 운전명령 1에서 댐퍼 4개가 모두 닫혀 있으면 속도 0(SF Control 189~194)이라, 재부팅 시 댐퍼가 닫혀 있으면 팬은 돌지 않음. 댐퍼가 중간 위치(열림·닫힘 신호 모두 0)일 때만 백업 복원된 직전 속도를 유지함. 운전 중 댐퍼가 움직일 때와 같은 동작이라 조치 불필요 |
| P1 | B4 | BMS 쓰기 우선순위·방식 확인 | 로직에는 BMS 쓰기 우선순위 설정이 없음(DDC 설정). 기존 설계는 HMI·BMS 명령이 P11로 들어온다고 가정. Failover는 알람이 걸리는 순간 운전명령 0을 P11에 한 번 씀(운전자 정지와 같음, 재기동 가능). BMS가 P11보다 높은 우선순위로 쓰거나 P11에 주기적으로 계속 쓰면 Failover 정지가 바로 덮임. Failover는 안전 인터록이 아니므로(안전 정지는 P1·P2 출력 강제) BMS보다 위로 올리지 않음. 주기 쓰기 BMS면 상위 로직이 Failover 알람을 보고 명령을 끄도록 반영 |
| P1 | B5 | 상위 Backup 구현 | 설정값 복원 책임, 통신 이상 FWU 제외 (§7) |
| P2 | C1 | SF Control Select 범위 | 0~4 밖 값이면 속도가 멈춤 (기존). HMI·BMS 입력 범위 제한 |
| P2 | C2 | BMS 통신 이상 래치 | 통신이 복구돼도 운전자 Reset 전까지 유지. 무인 운전 현장이면 자동 복귀 정책 검토 |
| P2 | C3 | 실행 순서 | Alarm-3가 Initialization 뒤라 팬 통신 이상이 1스캔 늦게 반영 (영향 작음) |
| P2 | C4 | 통신 부하 | 원격 정지 해제 상태에서 매 스캔 팬 Run Command RELEASE_PRI. 포트 1·2 통신 품질 확인 |

## 11. LDPL 규칙 대조

| LDPL | 규칙 | 결과 |
| --- | --- | --- |
| §8 | 첫 줄 `engine = ddc_logic()`, 들여쓰기, 줄 끝 `:` | 통과. 탭만, 비ASCII 없음, `elif/for/while/def` 없음 (원본과 같은 구문 범위) |
| §4.2 WRITE_PRI | 우선순위 1~16, 기본 5 | 사용 1, 2, 5, 11. `WRITEPOINT_PRI`는 개정 이력 v1.3에 명시 |
| §4.3 RELEASE_PRI | 지정 우선순위 해제 | 강제한 점은 모두 해제 경로 있음 |
| §4.10 ALARM | 8 = 통신 경보 | 기존 코드의 `READPOINT_ALARM(…) == 8` 유지 |
| §6.2 SECTIMER | 0~9, 조건문 안 동작 주의 | "조건 거짓이면 리셋" 패턴 |
| §7.3 LOOP2 | 인자 13개, type, loop_id 0~9 | 5개 루프 모두 일치 (PICV 1, SF 1~4) |
| §7.4 LOOP2_INIT | 제어 중단 시 초기화 | 정지·모드 전환·BMS 이상 시 초기화 |
| §3.3·3.4 MAX/MIN | 인자 5개 이하 | 최대 4개 |

## 12. 현장 시험 항목

| 시험 | 상황 | 기대 결과 |
| --- | --- | --- |
| T01 | CZT 모드 중 Heartbeat 정지 30초+ | 통신 이상 1, 팬 속도 유지 |
| T02 | T01에서 Comm Fail Mode = 1 | Speed Max |
| T03 | `VP_FWU_Backup Operation = 1` 쓰기 | 변화 없음 (로직 제거 확인) |
| T04 | RAT 모드 중 BMS 통신 이상 | RAT PI 계속 |
| T05 | Local 고정값 모드 중 BMS 통신 이상 | Speed SP 그대로 |
| T06 | ΔT 모드, ΔT SP = 설계값 | SP 근처로 수렴, ΔT < SP면 속도 감소 |
| T07 | 팬 1대 RPM 저하 (60초 후) | 해당 Run Fail만 1 |
| T08 | 팬 4대 고장 | SF Failure → 5초 후 Failover 1, 정지, 원인 해소 후에도 Reset 전까지 알람 유지 |
| T09 | 그룹 제어 모드 1 + 운전명령 0 | Failover 안 걸림 |
| T10 | CZT 모드에서 이웃 Adj 값 기록 | 변화 없음, CZT PV로만 제어 |
| T11 | 연기 입력, Smoke Action 0 / 1 | 알람만 / 원격 정지 경로로 정지, 해소 후 운전명령 0 유지 |
| T12 | 원격 정지 중 BMS 운전명령 1 유지 | 팬 Run Command 0, RPM 0 |
| T13 | 유량계·ATS 통신선 분리 10초+ | 각 Comm Fault 1, 유량 기반 PICV 알람 미발생 |
| T14 | 누수 입력 5초+ / 필터 입력 30초+ | 알람 1, 운전 유지 |
| T15 | 상위가 Backup을 설정값으로 구현 | 제어모드 0·Speed SP 최대·SAT SP 낮춤 적용, 종료 후 원래 값 복원 |
| T16 | 원격 정지 반복 | 포트 1·2 팬 통신 품질 이상 없음 |
