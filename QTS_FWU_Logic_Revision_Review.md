# QTS 요구사항 기반 FWU 로직 수정 검토서 (rev.3)

**검토일:** 2026-11-12
**대상:** QTS `FWU(390 kW)` 시트 / `FWU-F8-ATS` 로직 8개 및 DDC 설정 파일
**기준 코드:** `sy` 브랜치 "logic code 수정 2" 이후 (`FWU-F8-ATS/Logic/*.py`)
**문서 단계:** 코드 반영 완료 후 현황 검토 (현장 시험 전)

**rev.3 변경 사항 (rev.2 대비)**
- rev.2는 "코드 작성 전 계획서"였다. rev.3은 **현재 코드에 실제로 반영된 내용**만 기준으로 다시 썼다.
- rev.2에서 계획했던 경량화(L01~L04)와 신규 Point 7개 안은 **적용하지 않았다.** 기존 코드 구조를 유지하고, 필요한 기능만 덧붙이는 방식으로 바꿨다.
- `LDPL Programming Guide-v27.pdf`(저장소 루트)로 함수·규칙을 대조했다(§9).
- ΔT 제어 루프 방향 결함을 찾아 고쳤다(§5.2).

---

## 1. 먼저 볼 결론

1. 코드로 구현할 수 있는 QTS 항목은 반영했다: BMS 통신 이상 시 팬 속도 선택(129~131), 연기 감지 시 계속/정지 선택(143), 팬별 고장 알람(109), 누수 알람(142), 필터 알람(104·141), ATS·유량계 통신 이상(140·148).
2. 기존 결함 2개를 고쳤다: ΔT 제어 루프 방향(type 0 → 1), 원격 정지 중 팬 Run Command가 1로 남을 수 있던 문제.
3. **현장 적용 전에 반드시 할 일**은 두 가지다.
   - BMS Modbus 맵에 `VP_FWU_BMS PLC Heartbeat` 추가 (없으면 30초 후 BMS PLC 통신 이상 래치)
   - 신규 관제점 3개 정의 (`FWU_LEAK DETECT`, `VP_FWU_Leak Alarm`, `VP_FWU_Filter Alarm`) 후 Alarm-2 다운로드
4. 하드웨어·동작 규칙이 정해지지 않은 항목(냉수 입·출구 온도, 원격 3단자, 팬별 풍량 스위치)은 관제점 목록만 만들고 로직에는 넣지 않았다.
5. 이번 수정으로 새로 생긴 관제점 7점(그중 XML 정의가 필요한 점 3점)은 `QTS_신규_관제점_목록.xlsx`에 한국어 이름·의미·신호 출처와 함께 정리했다. 원래부터 BMS 맵에 없던 기존 관제점 61점은 같은 파일의 참고 시트에 따로 두었다.

| 구분 | 내용 | 상태 |
| --- | --- | --- |
| QTS 기능 추가 | 129~131, 143, 109, 142, 104·141, 140·148 | 코드 반영 |
| 기존 결함 수정 | ΔT 루프 방향, 정지 중 Run Command | 코드 반영 |
| 정책 반영 | 연기 정지를 Failover 원인에서 제외 | 코드 반영 (정책 확인 필요) |
| 설정 작업 | BMS 맵 추가, 신규 Point 정의, 기본값 확인 | 엑셀 목록 작성, 현장 작업 필요 |
| 하드웨어 후속 | 냉수 온도, 원격 3단자, 팬 풍량 스위치 | 관제점 목록만 작성 |

## 2. 검토 근거

| 자료 | 용도 |
| --- | --- |
| `QTS_Airside Equipment_CDE_260628-2 1.xlsx` | `FWU(390 kW)` 시트 요구사항 (행 번호로 인용) |
| `LDPL Programming Guide-v27.pdf` | 함수 규격(§3~7), 작성 규칙(§8) |
| `FWU-F8-ATS/Logic/*.py` 8개 | 제어·알람 로직 |
| `FWU-F8-ATS/DDC.xml` | 포트, 로직 실행 순서, BACnet, 이중화 |
| `FWU-F8-ATS/ControlPoint/*.xml` | IO / Modbus / VirtualPoint 정의와 기본값 |
| `FWU-F8-ATS/ProtocolSerivce/Modbus/ModbusServiceInfo.xml` | BMS Modbus 슬레이브 맵 |
| `QTS_SW_통신_관제점_반영현황.xlsx` | QTS 반영 현황표 (ver2) |
| `QTS_신규_관제점_목록.xlsx` | 이번 수정으로 생긴 신규 관제점 7점 (참고: 처음 쓰기 시작한 기존점 12점, BMS 맵 미등록 기존점 61점) |

### 2.1 설정 파일에서 확인한 구성

| 항목 | 내용 |
| --- | --- |
| 통신 포트 | 포트 1 = SF-1~4 (주소 82~85), 포트 2 = SF-5~8 (86~89), 포트 3 = ATS(01)·유량계(02). 모두 Modbus RTU 마스터 9600 bps. 포트 4 = BMS용 Modbus RTU 슬레이브 19200 bps |
| BACnet | `DDC.xml`: Device Instance 3, B/IP(Dnet 76, UDP 47808), MS/TP(Dnet 100, 38400 bps). 현장 값 확정 필요 |
| Modbus TCP | `ModbusTCP.xml` 비어 있음 |
| DDC 이중화 | 상대 192.168.1.132, 가상 IP 192.168.1.133 |
| 로직 실행 순서 | Initialization → PICV Control → SF Control → Alarm-1 → Alarm-2 → Alarm-3 → Remote Shutdown → Failover |
| 여유 입력 | DI 4점(CPU00-DI1~4), UI 9점(CPU00-UI1~6, CM02-UI5·6·8) |
| 주요 기본값 | Speed SP 50 %, SF Speed Min 30 %, Speed Max 100 %, DeltaT SP −2, BMS Comm Fail Mode 0, Smoke Action 0 |

## 3. QTS 요구사항 대비 현재 구현

| QTS 행 | 요구사항 | 현재 구현 | 판정 |
| --- | --- | --- | --- |
| 104·141 | 필터 오염 알람 | `FWU_FILTER ALARM` DI 30초 확인 → `VP_FWU_Filter Alarm` (Alarm-2) | 반영 (신규 VP 정의 필요) |
| 108 | 팬 저속 한계 20 % 이하 | 하한 기능 있음. 기본값 30 % | 설정 변경 필요 |
| 109 | 팬별 고장 감지 | 팬별 RPM(통신 이상 시 공통 차압) 판정 → `VP_FWU_SF-1~8 Run Fail Alarm` (Alarm-1). 풍량 스위치는 없음 | 기능 반영, 스위치는 하드웨어 후속 |
| 115·124·128 | 2-way 밸브로 급기온도 유지 | PICV SAT PI 제어 | 반영 |
| 120 | 밸브 마지막/안전 위치 | 수동 전환 시 마지막 값 유지, 비상·원격 정지 0 %, SAT 고장 100 % | 부분 (적용 조건 확인 필요) |
| 124 | 원격 온도·환기온도·원격 차압 기반 제어 | CZT / RAT / RDP 팬 PI 제어 | 반영 |
| 124 | 급기온도 기반 제어 | 밸브로 SAT 제어. 팬 모드에 SAT 없음 | 부분 (해석 확인) |
| 127 | BMS 팬 속도 쓰기 | `VP_FWU_Speed SP` = BMS HR 1076, 고정값 모드에서 사용 | 반영 (Select = 0 조건) |
| 129~131 | BMS 통신 이상 시 마지막 속도/최대 속도 선택 | `VP_FWU_BMS Comm Fail Mode` (SF Control) | **반영** |
| 132 | 원격 on/off 3단자 | 원격 정지 VP 1점만 있음 | 하드웨어 후속 |
| 133 | BMS Points List 표시 | V1.3 목록 미확보 | 확인 불가 |
| 138·139 | 냉수 입·출구 온도 | 관제점 없음 | 하드웨어 후속 |
| 140 | 유량계 | `FWU-Flow.Rate` + 통신 이상 감시(Alarm-3) | 반영 |
| 142 | 누수 알람, 정지 금지 | `FWU_LEAK DETECT` 5초 확인 → `VP_FWU_Leak Alarm` (Alarm-2), 정지 없음 | 반영 (신규 DI·VP 정의 필요) |
| 143 | 연기 감지 시 계속/정지 선택 | `VP_FWU_Smoke Action` (Remote Shutdown) | **반영** |
| 148 | 자동 절체 | ATS 자체 기능. DDC는 상태·통신 이상 감시(Alarm-3) | 감시 반영, 절체는 ATS 확인 |
| 16·18~21 | BACnet·Modbus TCP, 네트워크 정보 | BACnet 설정 있음, Modbus TCP 없음 | 현장 값 확정 |

## 4. 코드 변경 내역 (파일별)

| 파일 | 변경 | QTS |
| --- | --- | --- |
| `SF Control.py` | BMS PLC 통신 이상 시 RDP·CZT 모드, Remote 고정값 모드에서 `BMS Comm Fail Mode` 적용 (0 마지막 속도 유지, 1 최대). Backup 운전이 우선 | 129~131 |
| `SF Control.py` | ΔT 루프 방향 type 0 → 1 | 결함 수정 |
| `Remote Shutdown.py` | 연기감지 3초 확인 → `VP_FWU_Fire Alarm`. `Smoke Action = 1`이면 원격 정지와 같은 경로로 정지 | 143 |
| `Remote Shutdown.py` | 원격·연기 정지 중 `FWU SF-1~8.Run Command` 0 (P2), 해제 시 RELEASE_PRI | 결함 수정 |
| `Failover.py` | 연기 정지 중에는 Failover 원인 4(그룹 제어 중 정지)를 판정하지 않음 | 143 (정책) |
| `Alarm-1.py` | 팬별 판정 결과를 `VP_FWU_SF-1~8 Run Fail Alarm`에 기록. 유량계 통신 이상 중 유량 기반 PICV 알람 미판정 | 109, 140 |
| `Alarm-2.py` | 누수 알람(타이머 8, 5초), 필터 알람(타이머 9, 30초). 파일 끝에 배치 | 142, 104·141 |
| `Alarm-3.py` | ATS 통신 이상(타이머 8), 유량계 통신 이상(타이머 9), 통신 경보 8 판정 10초 | 140, 148 |
| `PICV Control.py` | 주석만 수정 (연기 정지 설명) | - |
| `Initialization.py` | 변경 없음 | - |

## 5. 주요 변경의 동작 원칙

### 5.1 BMS 통신 이상 시 팬 속도 (QTS 129~131)

| 상황 | 동작 |
| --- | --- |
| BMS 정상 | 기존 모드대로 제어 |
| BMS 통신 이상 + RDP(2) 또는 CZT(4) 모드 | Comm Fail Mode 0: 현재 속도 유지 (속도가 Speed Min 미만이면 최대). 1: Speed Max |
| BMS 통신 이상 + 고정값(0) 모드 + Remote | 위와 같음 (BMS가 쓰는 Speed SP가 멈췄으므로) |
| BMS 통신 이상 + 고정값(0) 모드 + Local | 기존대로 Speed SP (터치스크린 설정값) |
| BMS 통신 이상 + RAT(1) 또는 ΔT(3) 모드 | FWU 자체 센서로 계속 제어 |
| Backup 운전 지령 | 항상 Speed Max (마지막에 써서 우선) |
| 정상 센서 없음 (BMS는 정상) | 기존대로 Speed SP 고정 |

- BMS PLC 통신 이상은 기존 로직대로 **래치**된다. 운전자가 `VP_FWU_BMS PLC Comm Reset`을 눌러야 원래 제어로 돌아간다.
- `VP_FWU_SF Speed Value`는 backupEnable = 1이라 DDC 이중화 절체 후에도 유지 값이 남는다.
- 통신 이상으로 PI 제어를 멈출 때 LOOP2_INIT(1~4)로 누적값을 초기화한다(LDPL §7.4). 복귀하면 PI는 시작값 60 %에서 다시 시작한다.

### 5.2 ΔT 루프 방향 수정

| 근거 | 내용 |
| --- | --- |
| 물리 | ΔT = RAT − SAT는 풍량이 줄면 커진다. ΔT < SP이면 속도를 내리고, ΔT > SP이면 속도를 올려야 한다 |
| LDPL §7.3 | type 1 = 현재값을 설정값으로 **하향** (PV > SP → 출력 증가), type 0 = **상향** (PV < SP → 출력 증가) |
| LDPL 8장 예제 | type 1: 냉방밸브(급기온도), CO2 외기댐퍼. type 0: 가습밸브, 덕트 정압 팬 |
| 기존 코드 | PICV(SAT)·RAT·CZT = type 1, RDP = type 0 → 모두 위 정의와 일치 |
| 결론 | ΔT는 type 1이어야 한다. type 0이면 속도가 반대로 움직여 최저 또는 최대로 발산 |

모의 결과(ΔT = 600 / 속도): 수정 후 SP 12 → ΔT 12 K 수렴, 수정 전 SP 12 → 팬 최대로 발산, SP −2 → 팬 최저 30 %로 고정.

**남은 설정:** `VP_FWU_DeltaT SP` 기본값 −2는 ΔT(양수)와 맞지 않는다. type 1에서는 팬 최대 속도로 간다(냉각 쪽이라 위험은 낮음). ΔT 모드를 쓰기 전에 설계 ΔT로 설정해야 한다.

### 5.3 연기 감지 (QTS 143)

| 상태 | 동작 |
| --- | --- |
| `FWU_FIRE ALARM` 3초 이상 ON | `VP_FWU_Fire Alarm = 1` (OFF면 즉시 0) |
| Smoke Action 0 (기본) | 알람만. 운전 유지 (변경 전과 같은 동작) |
| Smoke Action 1 | 원격 정지와 같은 경로: Command 0 (P11), PICV·팬 출력·Run Command 0 (P2), 팬 정지 후 SAD 닫힘 |
| 해소 | P2 해제. Command는 0으로 남아 운전자가 재기동 |

## 6. 우선순위(Priority) 사용 규칙

| 우선순위 | 쓰는 곳 | 용도 |
| --- | --- | --- |
| P1 | SF Control, PICV Control (비상 정지) | 비상 시 출력 0 강제 |
| P2 | Remote Shutdown | 원격 정지·연기 정지 시 출력 0 강제 |
| P5 | 모든 로직의 `WRITEPOINT` (LDPL 기본 우선순위) | 일반 제어 |
| P11 | 자동 제어 값 미러, 정지 시 운전명령 0, Reset 0 복귀 | 수동 전환 시 값 유지, 운전명령 |

- 강제로 쓴 우선순위는 조건이 풀리면 반드시 `RELEASE_PRI`로 해제한다.
- 수동 모드에서는 P5를 해제(`RELEASE_PRI(…, 5)`)하고 P11의 유지값이나 운전자 값을 쓴다.

## 7. 타이머 배분 (파일당 0~9, LDPL §6.2)

| 파일 | 사용 타이머 |
| --- | --- |
| Initialization | 5 (SF Status 5 s), 6 (Heartbeat 30 s), 7 (Comm Reset 5 s) |
| PICV Control | 없음 |
| SF Control | 1 (속도 출력 5 s 주기) |
| Alarm-1 | 0~9 전부 |
| Alarm-2 | 0~7 (존 센서 고장), **8 (누수 5 s), 9 (필터 30 s)** |
| Alarm-3 | 0~7 (팬 통신 이상), **8 (ATS 10 s), 9 (유량계 10 s)** |
| Remote Shutdown | **0 (화재 3 s)** |
| Failover | 1 (원인 5 s), 2 (Reset 5 s) |

## 8. 남은 작업과 결정 사항

| ID | 우선 | 항목 | 내용 |
| --- | --- | --- | --- |
| K01 | P0 | Heartbeat 맵 | `VP_FWU_BMS PLC Heartbeat`를 BMS 맵(HR 쓰기)에 추가. 가장 먼저 처리 |
| K02 | P0 | 신규 Point | `FWU_LEAK DETECT`(DI), `VP_FWU_Leak Alarm`, `VP_FWU_Filter Alarm` 정의 후 Alarm-2 다운로드 |
| K03 | P0 | BMS 맵 추가 | 신규 7점(`QTS_신규_관제점_목록.xlsx` 1번 시트). BMS PLC 연동에 필요한 기존 점은 3번 시트 참고 |
| K04 | P0 | `READPOINT_ALARM` | LDPL v27에는 `ALARM`만 있으나 기존 코드에서 쓰던 함수라 유지. 현장 DDC에서 동작 확인 |
| K05 | P1 | Comm Fail Mode 기본값 | 현재 0(유지). 냉각 우선이면 1(최대). Heartbeat 연결 전 시운전 중에는 1 권장 |
| K06 | P1 | Smoke Action | 1로 바꾸기 전 `FWU_FIRE ALARM` 극성(1 = 연기 감지) 확인 |
| K07 | P1 | 연기 정지와 Failover | 연기 정지 중 인접 FWU Backup을 요청하지 않음. 현장 정책 확인 |
| K08 | P1 | ΔT SP | 기본값 −2 → 설계 ΔT로 |
| K09 | P1 | Speed Min | 30 % → 20 % 이하 검토 (QTS 108) |
| K10 | P2 | BMS 쓰기 우선순위 | BMS가 Command를 P11보다 높게 쓰면 Failover의 Command 0(P11)이 먹히지 않음. 원격·연기 정지는 Run Command P2로 보완됨 |
| K11 | P2 | DDC 실행 순서 | Alarm-3가 Initialization 뒤라 팬 통신 이상이 1스캔 늦게 반영. 필요 시 Alarm-3를 맨 앞으로 |
| K12 | P2 | 하드웨어 후속 | 냉수 입·출구 온도(AI 2), 원격 3단자(DI 3), 팬 풍량 스위치(DI 8, I/O 부족) |
| K13 | P2 | SF Control Select 범위 밖 값 | 0~4 밖이면 속도가 그대로 멈춤 (기존 동작) |

## 9. LDPL 규칙 대조 결과

| LDPL | 규칙 | 결과 |
| --- | --- | --- |
| §8 작성 주의점 | 첫 줄 `engine = ddc_logic()`, 들여쓰기, 줄 끝 `:` | 8개 파일 통과. 탭만 사용, 비ASCII 문자 없음 |
| §4.2 WRITE_PRI | 우선순위 1~16, 기본 5 | 사용 1, 2, 11. 함수명 `WRITEPOINT_PRI`는 개정 이력 v1.3에 명시 |
| §4.3 RELEASE_PRI | 지정 우선순위 해제 | 강제한 점은 조건 해제 시 모두 해제 |
| §4.10 ALARM | 0/1/2/4/8, 8 = 통신 경보 | 기존 코드의 `READPOINT_ALARM(…) == 8` 유지 |
| §6.2 SECTIMER | 0~9, 조건문 안에서는 동작 안 함 | 모든 타이머가 "조건 거짓이면 0으로 리셋" 패턴 |
| §6.1 WAIT | 물리점 100개당 1초 | 해당 없음 (파일당 물리점 쓰기 최대 22개) |
| §7.3 LOOP2 | 인자 13개, type, loop_id 0~9 | 5개 모두 13개, id 1~4, 방향 일치(ΔT 수정 후) |
| §7.4 LOOP2_INIT | 제어 중단 시 초기화 | 정지·모드 전환·BMS 이상·Backup 시 초기화 |
| §3.3·3.4 MAX/MIN | 인자 최대 5개 | 최대 4개 |

- 사용 함수는 원본 코드와 똑같다: `READPOINT`, `WRITEPOINT`, `WRITEPOINT_PRI`, `RELEASE_PRI`, `READPOINT_ALARM`, `SECTIMER`, `LOOP2`, `LOOP2_INIT`, `MAX`, `MIN`.
- Python 구문도 원본과 같은 범위(`if/else`, 비교, 대입)만 쓴다.

## 10. 현장 시험 항목

| 시험 | 상황 | 기대 결과 |
| --- | --- | --- |
| T01 | CZT 모드 운전 중 Heartbeat 정지 30초+ | BMS PLC Comm Fault = 1, 팬 속도 직전 값 유지 |
| T02 | T01 상태에서 Comm Fail Mode = 1 | 팬 속도 = Speed Max |
| T03 | T01 상태에서 Backup Operation = 1 | Speed Max (Backup 우선) |
| T04 | RAT 모드에서 BMS 통신 이상 | RAT PI 제어 계속 |
| T05 | Local 고정값 모드에서 BMS 통신 이상 | Speed SP 그대로 |
| T06 | ΔT 모드, ΔT SP = 설계값 | 속도가 SP 근처로 수렴. ΔT < SP면 속도 감소 |
| T07 | 팬 1대 RPM 저하 (운전 60초 후) | 해당 Run Fail Alarm만 1, SF Failure Alarm 0 |
| T08 | 팬 4대 고장 | SF Failure Alarm = 1 → Failover |
| T09 | FWU_FIRE ALARM ON, Smoke Action 0 / 1 | 알람만 / 원격 정지와 같이 정지, 해소 후 Command 0 유지 |
| T10 | 원격 정지 중 BMS가 Command 1 유지 | Run Command 0, Target RPM 0 |
| T11 | 유량계 통신선 분리 10초+ | Flow Comm Fault = 1, 유량 기반 PICV 알람 미발생 |
| T12 | ATS 통신선 분리 10초+ | ATS Comm Fault = 1 |
| T13 | 누수 입력 5초+ / 필터 입력 30초+ | 각 알람 1, 운전 유지 |
| T14 | 원격 정지 해제 반복 | 팬 포트 1·2 통신 품질 이상 없음 (Run Command RELEASE_PRI 부하 확인) |
