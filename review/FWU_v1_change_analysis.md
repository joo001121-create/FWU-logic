# FWU 1차 개발 코드 종합 비교 분석

> 분석일: 2026-11-16 · 대상: F8(팬 8대) ATS 구성 · 방법: 정적 분석
>
> **결론:** v1은 기존 기동·정지·PI·보호 구조를 유지하면서 QTS 관련 감시와 통신 이상 대응을 확장하고, 상위 조율 기능을 제거한 버전이다. 그러나 **Python이 참조하는 미정의 관제점 3개, Heartbeat·신규점 통신맵 누락, 비활성 Modbus TCP, 현장 확인 사항**이 남아 있다. 현재 자료만으로 다운로드 가능성·실장 운전 정상·RFP 전체 충족을 보증할 수 없다.

## 0. 범위와 읽는 방법

### 0.1 비교 기준

- **A / As-Is:** `SMX01-FWU-20261102/FWU-F8-ATS` 디렉터리의 실제 파일.
- **B / To-Be:** `FWU_v1` 디렉터리의 실제 파일.
- 아래 인용은 분석 시점의 **물리 줄 번호(1부터, 빈 줄·주석 포함)**다. 문서의 과거 커밋이나 주석의 개정 날짜를 비교 기준으로 대신하지 않았다.
- 초보자는 [FWU_v1_study_guide.md](FWU_v1_study_guide.md)부터 읽는다. 이 보고서는 차이·근거·미결사항을, 학습 가이드는 개념·코드 읽는 법·상황별 흐름을 담당한다.
- **사실:** 실행문, XML 속성, 원문 요구사항에서 직접 확인. **해석/추론:** 변경 의도·물리적 영향. **확인 필요:** DDC 펌웨어·장비·배선·HMI·상위 프로그램이 있어야 판단할 사항.

### 0.2 읽은 자료와 증거의 우선순위

| 자료 | 확인 범위와 용도 |
|---|---|
| 양쪽 Python 16개·XML 30개 | 전체 파일 비교, 실행문/관제점/통신맵/스케줄 정적 검사. 구현 판정의 1차 근거 |
| [상위 프로젝트 설정](../SMX01-FWU-20261102/Project.xml#L1-L9) | F8 ATS의 프로젝트 소속과 IP 문맥. F4·PAC 로직은 이번 자료에 없음 |
| [../QTS_Airside Equipment_CDE_260628-2 1.xlsx](../QTS_Airside%20Equipment_CDE_260628-2%201.xlsx) | `FWU(390 kW)` 시트의 셀 원문. RFP 행 번호는 Excel 행 번호. 다른 두 CRAH 시트는 FWU 요구사항 집계에 섞지 않음 |
| [../QTS_신규_관제점_목록.xlsx](../QTS_신규_관제점_목록.xlsx) | 요약 및 1~4번 시트 전체. 제안 ID·주소와 실제 XML 등록을 구분 |
| [../QTS_SW_통신_관제점_반영현황.xlsx](../QTS_SW_통신_관제점_반영현황.xlsx) | 단일 시트의 요구사항 분류와 기존 검토 의견을 코드에 재대조 |
| [동료 검토서](../QTS_FWU_Logic_Revision_Review.md#L1-L256) | 변경 배경, 양산 범위 원칙, 시험 주장. 구현 증명으로 단독 사용하지 않음 |
| [기존 초보자 설명서](../FWU_Logic_초보자_설명서.md#L1-L677) | 용어·흐름 설명 참고. 현재 코드와 다른 설명은 §8에서 정리 |
| [../LDPL Programming Guide-v27.pdf](../LDPL%20Programming%20Guide-v27.pdf) | 총 117쪽. 우선순위 pp.54–55, 알람 p.62, 타이머 pp.72–73, LOOP2 pp.80–82, 예제 pp.114–115 중심 대조 |

Excel은 읽기만 했으며 저장하지 않았다. 셀에 표시된 `COMPLY=O`는 고객 요구사항 충족의 코드 검증 결과가 아니다. PDF 함수 명칭/예제의 불일치도 그대로 기록했다. 별도 DoO 원본, BMS Points List V1.3.R0, HMI 화면, DDC 펌웨어/엔진, 모의시험 코드·로그는 제공 자료에서 확인되지 않았다.

## 1. 전체 구조 및 변경 규모

### 1.1 집계

| 구분 | 결과 |
|---|---:|
| 비교 대상 | A 23개 + B 23개 = **46개**, 상대 경로 기준 23쌍 |
| 추가 / 삭제 / 수정 / 동일 | **0 / 0 / 9 / 14쌍** |
| Python | 양쪽 각 8개, **8개 모두 실행문 변경** |
| XML | 양쪽 각 15개, 가상 관제점 정의만 변경, 14개 바이트 동일 |
| 전체 검토 자료 | 비교 46개 + 상위 프로젝트 1개 + 참고 자료 6개 = **53개** |
| Python 물리 줄 수 | **1,399 → 1,556**, 순증 157줄 |
| Python 줄 diff | 추가 326 / 삭제 169줄. 주석·빈 줄 포함, 기능 변경 건수와 다름 |
| 비공백·비주석 줄 | **827 → 880**. 실행문 크기 참고 지표이며 복잡도/품질 점수는 아님 |

파일 내용 바이트 비교, Python AST 비교, 주석·빈 줄 제거 후 실행문 diff를 함께 사용했다. AST가 다르다고 전부 신규 기능은 아니다. 상수→설정점 변경은 기본값이 같으면 동등하고, 중복 계산 제거도 동일 입력에서는 동등하다.

상위 [프로젝트 설정](../SMX01-FWU-20261102/Project.xml#L1-L9)은 A의 비교 루트 밖에 있다. B에 같은 파일이 없다고 **삭제 파일**로 세지 않았다. B는 장비 디렉터리 사본이지 프로젝트 전체 패키지임이 증명된 상태는 아니다.

### 1.2 Python 파일별 크기

| 파일(현행 코드) | A 줄 | B 줄 | 추가/삭제 | 비주석 A→B | 실제 차이 |
|---|---:|---:|---:|---:|---|
| [Initialization](../FWU_v1/Logic/Initialization.py#L1-L356) | 390 | 356 | +31/−65 | 251→223 | 인접 보상 제거, 모델 설정점 적용 |
| [PICV Control](../FWU_v1/Logic/PICV%20Control.py#L1-L63) | 66 | 63 | +9/−12 | 26→22 | Backup 목표 보정 제거, 직접 SAT SP 사용 |
| [SF Control](../FWU_v1/Logic/SF%20Control.py#L1-L311) | 273 | 311 | +82/−44 | 167→169 | BMS 이상 선택, ΔT 방향, 보상/Backup 제거, 정격 설정 적용 |
| [Alarm-1](../FWU_v1/Logic/Alarm-1.py#L1-L437) | 379 | 437 | +80/−22 | 226→261 | 팬별 결과 기록, 설정점, 유량계 통신 예외 |
| [Alarm-2](../FWU_v1/Logic/Alarm-2.py#L1-L120) | 89 | 120 | +32/−1 | 49→61 | 누수·필터 알람 추가 |
| [Alarm-3](../FWU_v1/Logic/Alarm-3.py#L1-L109) | 83 | 109 | +27/−1 | 53→65 | ATS·유량계 통신 감시 추가 |
| [Remote Shutdown](../FWU_v1/Logic/Remote%20Shutdown.py#L1-L96) | 50 | 96 | +52/−6 | 33→60 | 연기 알람/선택 정지, 팬 Run P2 강제 |
| [Failover](../FWU_v1/Logic/Failover.py#L1-L64) | 69 | 64 | +13/−18 | 22→19 | 그룹 정지 원인 제거, 래치/일회 정지 유지 |

### 1.3 XML 15개 전수 비교

각 링크는 B이며, 같은 상대 경로의 A와 비교했다.

| 파일 | 판정 | 확인 결과 |
|---|---|---|
| [../FWU_v1/DDC.xml](../FWU_v1/DDC.xml) | 동일 | 포트·로직 8개 등록·BACnet·DDC 이중화 설정 유지 |
| [../FWU_v1/ControlPoint/IO.xml](../FWU_v1/ControlPoint/IO.xml) | 동일 | IO 엔트리 44개. 비어 있는 ID의 여유점 22개 포함 |
| [../FWU_v1/ControlPoint/Modbus1.xml](../FWU_v1/ControlPoint/Modbus1.xml) | 동일 | SF-1~4, 장치당 23점, 합계 92점 |
| [../FWU_v1/ControlPoint/Modbus2.xml](../FWU_v1/ControlPoint/Modbus2.xml) | 동일 | SF-5~8, 합계 92점 |
| [../FWU_v1/ControlPoint/Modbus3.xml](../FWU_v1/ControlPoint/Modbus3.xml) | 동일 | ATS·유량계 합계 17점 |
| [../FWU_v1/ControlPoint/ModbusSlave4.xml](../FWU_v1/ControlPoint/ModbusSlave4.xml) | 동일 | 루트 요소만 있음. 외부 맵은 별도 서비스 설정에 존재 |
| [../FWU_v1/ControlPoint/ModbusTCP.xml](../FWU_v1/ControlPoint/ModbusTCP.xml) | 동일 | 루트 요소만 있음 |
| [../FWU_v1/ControlPoint/VirtualPoint.xml](../FWU_v1/ControlPoint/VirtualPoint.xml) | **수정** | 172→185점, **13점 추가**, 기존 점 삭제·속성 변경 없음 |
| [../FWU_v1/Device/DeviceInfos.xml](../FWU_v1/Device/DeviceInfos.xml) | 동일 | 장치 목록 자식 요소 없음. Modbus 장치가 없다는 뜻은 아님 |
| [../FWU_v1/ProtocolSerivce/BACnet/BACnetServiceInfo.xml](../FWU_v1/ProtocolSerivce/BACnet/BACnetServiceInfo.xml) | 동일 | 루트 요소만 있음. BACnet 설정 자체는 DDC에 존재 |
| [../FWU_v1/ProtocolSerivce/LGModbus/LGModbusServiceInfo.xml](../FWU_v1/ProtocolSerivce/LGModbus/LGModbusServiceInfo.xml) | 동일 | 주소 1, 비어 있는 맵 요소 |
| [../FWU_v1/ProtocolSerivce/Modbus/ModbusServiceInfo.xml](../FWU_v1/ProtocolSerivce/Modbus/ModbusServiceInfo.xml) | 동일 | 외부 맵 360엔트리. **TCP 서비스 false** |
| [../FWU_v1/ScheduleInfo/Calendars.xml](../FWU_v1/ScheduleInfo/Calendars.xml) | 동일 | 달력 항목 없음 |
| [../FWU_v1/ScheduleInfo/Schedules.xml](../FWU_v1/ScheduleInfo/Schedules.xml) | 동일 | Schedule01~50의 ID/이름/type만 존재, 시간·대상점 동작 없음 |
| [../FWU_v1/ScheduleInfo/SpecialSchedules.xml](../FWU_v1/ScheduleInfo/SpecialSchedules.xml) | 동일 | 특별 스케줄 항목 없음 |

관제점 엔트리 총수는 **417→430**(IO 44 + Modbus 201 + VP 172→185). 비어 있지 않은 ID를 가진 점만 세면 **395→408**이다. 여유 IO를 활성 설비점으로 계산하지 않도록 두 수치를 구분했다. 비어 있지 않은 관제점 ID 및 이름의 중복은 발견하지 않았다.

## 2. 주요 변경사항 12건과 유지 기능

### 2.1 주요 변경 집계 기준

아래 **C01~C12 = 12건**으로 기능 단위를 묶었다. 한 변경이 여러 파일에 걸쳐 있어도 한 건으로 계산했다. 모델 설정점 9개는 C07 한 건, 연기 정지 경로와 그 경로의 Run 강제는 C12 한 건이다.

| ID | 변경 | 변경 이유/근거 | 운전 영향 |
|---|---|---|---|
| C01 | BMS 이상 시 마지막/최대 속도 선택 | RFP 129~131, [B의 판단·대응](../FWU_v1/Logic/SF%20Control.py#L77-L99), [유지/최대 분기](../FWU_v1/Logic/SF%20Control.py#L175-L187) | RDP/CZT 및 Remote 고정값은 기존 Speed SP 대체와 달리 현재속도 유지 또는 최대 |
| C02 | ΔT PI `type 0→1` | RFP 직접 지정 아님. 제어 방향 개선: [A](../SMX01-FWU-20261102/FWU-F8-ATS/Logic/SF%20Control.py#L129-L134) → [B](../FWU_v1/Logic/SF%20Control.py#L159-L166), LDPL §7.3 | ΔT가 클 때 팬 출력을 증가시키는 방향. 수렴성은 실기 튜닝 필요 |
| C03 | 인접 존 보상 계산·사용 제거 | 동료 검토서의 양산 범위 정책. [A 계산](../SMX01-FWU-20261102/FWU-F8-ATS/Logic/Initialization.py#L234-L266), [B 자체 PV](../FWU_v1/Logic/SF%20Control.py#L152-L173) | 같은 자체 센서값이라도 이웃이 과열/저차압인 상황에서 기존 증풍 보상이 사라짐 |
| C04 | 로컬 Backup 증풍·SAT 보정 제거 | 상위 조율 기능 제외. [A 팬](../SMX01-FWU-20261102/FWU-F8-ATS/Logic/SF%20Control.py#L143-L149), [A 밸브](../SMX01-FWU-20261102/FWU-F8-ATS/Logic/PICV%20Control.py#L32-L50), [B 밸브](../FWU_v1/Logic/PICV%20Control.py#L40-L53) | Backup 점만 1로 써서는 증풍/급기온도 하향이 일어나지 않음 |
| C05 | Failover 원인 4(그룹모드+정지) 제거 | 상위 조율 기능 제외. [A](../SMX01-FWU-20261102/FWU-F8-ATS/Logic/Failover.py#L34-L44) → [B](../FWU_v1/Logic/Failover.py#L35-L39) | 그룹모드에서 일반 정지했다는 이유만으로 Failover를 만들지 않음 |
| C06 | 팬별 Run Fail 결과를 기존 VP 8점에 기록 | RFP 109의 개별 고장 감시 취지. [A 내부 집계](../SMX01-FWU-20261102/FWU-F8-ATS/Logic/Alarm-1.py#L214-L240) → [B 기록](../FWU_v1/Logic/Alarm-1.py#L230-L288) | 몇 번 팬이 저속으로 판정됐는지 내부 점에서 확인 가능. BMS 맵은 별도 미등록 |
| C07 | 모델 관련 상수 9개를 설정점으로 전환 | RFP 직접 지정 아님, 모델 공용화 준비. [XML](../FWU_v1/ControlPoint/VirtualPoint.xml#L179-L187) | 기본값에서는 기존 F8 결과와 동일. 값 변경 시 판정·풍량·출력 환산 변경 |
| C08 | ATS 통신 이상 10초 확인 | RFP 148의 감시 보강, [추가 실행문](../FWU_v1/Logic/Alarm-3.py#L96-L101) | 상태를 읽지 못함을 별도 알람화. 전원 절체를 수행하는 제어는 아님 |
| C09 | 유량계 통신 이상 감시·유량 기반 밸브 알람 억제 | RFP 140 관련 감시/오경보 개선, [감시](../FWU_v1/Logic/Alarm-3.py#L104-L109), [억제](../FWU_v1/Logic/Alarm-1.py#L416-L437) | 동결 유량값에 의한 오경보를 줄임. 지령/피드백 편차 알람은 계속 판단 |
| C10 | 누수 지연 알람 추가 | RFP 142, [추가 실행문](../FWU_v1/Logic/Alarm-2.py#L103-L110) | 알람만, 누수에 의한 정지 명령 없음. 입력·알람 XML 누락으로 부분 구현 |
| C11 | 필터 지연 알람 추가 | RFP 104·141, [추가 실행문](../FWU_v1/Logic/Alarm-2.py#L113-L120) | 기존 접점에 30초 지연 알람 추가. 결과 VP 미정의 |
| C12 | 연기 알람·선택 정지와 정지 중 Run P2 강제 추가 | RFP 143 및 정지 명령 보강, [연기 조건](../FWU_v1/Logic/Remote%20Shutdown.py#L31-L45), [P2 출력/해제](../FWU_v1/Logic/Remote%20Shutdown.py#L47-L96) | 기본 0은 알람만. 1이면 원격정지 경로로 정지. 팬 Run도 낮은 우선순위 명령보다 우선해 0 |

### 2.2 이번에 새로 생긴 기능으로 오인하면 안 되는 것

다음은 **이미 A에 구현되어 있었다**. 헤더의 10월 개정 이력을 이번 변화로 세면 안 된다.

- 자동 기동 시 SAD 4개 전개방 확인, 전폐 시 속도 0, 중간 위치에서 이전 속도 유지.
- 정상 정지 시 PICV 닫힘 지령 → 피드백 5% 미만에서 팬 속도 0 → 팬 정지상태에서 SAD 닫힘.
- 팬 8대 Run Command, 팬 하나라도 통신 이상이면 **두 AO 그룹 모두** 사용, 정상 시 Target RPM 사용, 출력 타이머 `>5`.
- 자동값 P11 미러, 수동 시 P5 Release, Emergency P1, Remote Shutdown P2, Failover P11 일회 정지.
- BMS Heartbeat 30초 감시·래치·Reset, CZT/HZT/RDP 고장 센서 제외와 PV Valid, RDP 선택의 평균/최소.
- SAT 고장 시 운전 중 밸브 100%, 냉수 공급 조건에 따른 무유량 알람 억제, 존 상하한 알람, 팬 상태 5초 확인.

근거: [A 팬 제어](../SMX01-FWU-20261102/FWU-F8-ATS/Logic/SF%20Control.py#L85-L273), [A 초기화](../SMX01-FWU-20261102/FWU-F8-ATS/Logic/Initialization.py#L49-L220), [A 알람](../SMX01-FWU-20261102/FWU-F8-ATS/Logic/Alarm-1.py#L1-L379).

**동작 변화로 세지 않은 정리:** 미사용 HZT 게인 읽기 2개 제거, SF 내부 ΔT 중복 쓰기 제거, 주석 보강·줄 이동. ΔT는 [A 초기화](../SMX01-FWU-20261102/FWU-F8-ATS/Logic/Initialization.py#L268-L269)와 [A 팬](../SMX01-FWU-20261102/FWU-F8-ATS/Logic/SF%20Control.py#L63-L68)에서 중복 계산했으며, B는 [초기화 한 곳](../FWU_v1/Logic/Initialization.py#L233-L234)에서만 계산한다. 동일 입력 스냅샷이면 기능적으로 같다. 두 파일 사이 센서 갱신이 발생할 때 읽는 시점까지 동일하다고 보증하지는 않는다.

## 3. 로직별 상세 비교

### 3.1 Initialization — 공통 상태와 제어 입력 만들기

**역할:** 이름과 달리 기동 때 한 번 실행하는 설정 스크립트가 아니라, 반복 실행을 전제로 공통 상태를 계산하는 파일이다. Heartbeat, 존 집계/PV, 팬 운전상태, 풍량, 명령 출처, 최대 RPM을 준비한다.

**A 동작 및 유지 부분**

1. Heartbeat 값이 이전과 다르면 Prev 저장·타이머 6 리셋. 30초 초과 무변화면 BMS 통신 알람을 1로 쓴다. 정상 값이 다시 와도 자동 해제하지 않는다.
2. Reset=1이고 `HB_OK=1`이면 알람을 해제한다. **정확히는 마지막 변화 이후 30초 타임아웃 전도 HB_OK=1**이다. “Reset 순간 값이 반드시 변해야 한다”는 뜻은 아니다. Reset 요청은 타이머 7로 5초 초과 후 P11에서 0 복귀한다.
3. CZT 4개, HZT 2개, RDP 2개는 BMS 정상이고 각각 Failure Alarm=0인 센서만 집계한다. 정상 수가 0이면 평균/최대/최소 및 PV=0, Valid=0이다. CZT/HZT는 Select=0이면 평균, 그 외 최대; RDP는 0이면 평균, 그 외 최소다.
4. CZH 4개는 고장·BMS 상태 필터 없이 그대로 집계한다. HZT는 감시용 PV가 있지만 팬 HZT PI 모드는 없다.
5. 팬별 통신 정상일 때 RPM>Failure RPM Set, 통신 이상일 때 공통 차압>운전 차압 기준을 사용한다. 하나라도 참이면 SF_RUN=1. 현재 SF Status와 다른 상태가 5초 초과 유지되어야 변경한다.
6. 풍량은 SF Status=1이고 DP≥5일 때만 계수×√DP×SAF VA-2. 그 외 0. 음수 차압의 제곱근 계산을 피하는 보호는 기존이다.
7. Remote이면 Command를 사용하고 Command-HMI에 P5/P11 복사, Local이면 반대. 복사 대상이 아닌 원래 명령점의 P5를 Release한다.

근거: [A Heartbeat/집계](../SMX01-FWU-20261102/FWU-F8-ATS/Logic/Initialization.py#L49-L220), [B Heartbeat/집계](../FWU_v1/Logic/Initialization.py#L56-L225), [B 상태·풍량·명령](../FWU_v1/Logic/Initialization.py#L239-L356).

**실제 변경과 영향**

- 인접 보상 제거(C03). A는 가중치를 0~1로 제한하고, 자기 존의 여유 조건을 만족하면 이웃 CZT 최대값으로 제어온도를 더 높게, 이웃 RDP 최소값으로 제어차압을 더 낮게 만들어 팬을 증속시키는 구조였다. B는 이 계산·출력 자체가 없다.
- A의 고정 `10 Pa`, `235.751976`, `1.1`, `1920 rpm`이 B에서 설정점으로 바뀌었다(C07). 기본값은 동일하다.
- 모델별 설정을 바꿀 수 있다는 뜻이지 다른 팬 수를 자동 구성한다는 뜻은 아니다. 팬 판정문은 여전히 1~8번 고정이다.

**확인 필요:** Heartbeat 외부 맵(U02), 알람 확정 전 불량 센서가 집계되는 기간(U18), CZH 유효성 정책(U18), SF 상태의 공통 차압 대체 한계(U21), 설정값 범위(U12).

### 3.2 SF Control — 팬 속도 결정과 실제 출력

**역할:** 자동 모드에서는 운전명령·댐퍼 상태·선택 모드로 Speed Value를 정하고, 별도 블록에서 팬 Run과 Modbus/AO 출력을 만든다.

| 조건/모드 | A | B |
|---|---|---|
| 고정값 0, 정상 | Speed SP를 Min~Max로 제한 | 동일 |
| RAT 1 | RAT, type 1, loop 1 | 동일 |
| RDP 2 | RDP Comp PV, type 0, loop 2 | **RDP PV 직접 사용** |
| ΔT 3 | RAT−SAT, **type 0**, loop 3 | **type 1**, 입력은 초기화가 만든 ΔT |
| CZT 4 | CZT Comp PV, type 1, loop 4 | **CZT PV 직접 사용** |
| BMS 정상, RDP/CZT Valid=0 | Speed SP 고정값 대체 | 동일 |
| BMS 이상, RDP/CZT | Valid=0으로 Speed SP 대체. Backup 조건 성립 시 최대가 나중에 덮음 | Comm Fail Mode=0 유지 또는 =1 최대. 유지속도가 Min 미만이면 최대 |
| BMS 이상, Remote 고정값 | 기존 Speed SP 계속 사용 | 위와 같은 유지/최대 |
| BMS 이상, Local 고정값 / RAT / ΔT | 각 모드 유지 | 동일. 모든 모드에 통신 이상 최대속도가 적용되는 것은 아님 |
| Backup=1, 자체 Failover=0 | 자동·Command=1·SAD 전개방에서 최대속도 | **아무 반응 없음** |

모드 번호는 `0≤값<1` 등의 구간 비교다. 1.5도 RAT 분기에 들어간다. 0~5 범위 밖은 새 속도를 쓰는 분기가 없어 기존 속도가 남을 수 있다. **“범위 밖이면 팬이 정지한다”가 아니다.**

근거: [A 선택·Backup](../SMX01-FWU-20261102/FWU-F8-ATS/Logic/SF%20Control.py#L54-L149), [B 선택·PI·BMS](../FWU_v1/Logic/SF%20Control.py#L77-L187).

**기동·정지·수동·Emergency는 기본 구조 유지**

- 자동 Command=1: SAD 공통 명령=1 → 4개 OPEN 모두 1일 때만 선택 제어 실행. 4개 CLOSE 모두 1이면 뒤의 분기에서 속도=0. 둘 다 아니면 현재 속도 유지.
- 자동 Command가 1이 아니면: PI 초기화, PICV 피드백<5에서 속도=0, SF Status=0에서 SAD=0. 밸브 피드백이 내려오지 않으면 일반 정지 완료가 지연될 수 있다.
- 자동값 Speed Value와 SAD 명령은 P11에도 복사. 수동은 루프 초기화 후 이 두 점의 P5 해제. **수동에서도** 파일 하단의 Run 및 속도 출력은 실행된다.
- Emergency가 0이 아니면 팬 AO/RPM은 P1=0, Speed Value는 P5/P11=0, 두 Command는 P11=0. 팬 정지상태가 되어야 SAD P1=0. 정상으로 복귀하면 해당 출력 P1 해제.
- Run은 Speed Value>0인지로 팬 8대 모두 매 실행 시 갱신한다. Emergency에서 Run 자체에 P1을 쓰지는 않는다. Remote/연기 정지는 B에서 Run P2=0을 따로 쓴다.

근거: [B 시퀀스](../FWU_v1/Logic/SF%20Control.py#L128-L269), [A 동일 골격](../SMX01-FWU-20261102/FWU-F8-ATS/Logic/SF%20Control.py#L99-L231).

**출력 환산**

$$
N_{max}=\min(N_{design}\,Ratio/100, N_{rated}),\quad
N_{cmd}=\min(Speed\,N_{max}/100,N_{max})
$$

$$
AO_{percent}=Speed\,N_{max}/\max(N_{rated},1)
$$

팬 통신 종합 알람이 0이면 AO=0, Modbus RPM=`N_cmd`. 1이면 두 AO 그룹=`AO_percent`, 팬 8대 Modbus RPM=0. **한 팬만 통신 불량이어도 전체 출력 경로가 전환되는 것은 유지 기능**이다. B의 변경은 AO 분모 1920을 정격 설정점으로 바꾼 부분이다. 일반 속도 출력은 `SECTIMER(1,1)>5`에서만 갱신하며 Emergency/Remote 출력 강제는 그 주기를 기다리지 않는다.

근거: [A 출력](../SMX01-FWU-20261102/FWU-F8-ATS/Logic/SF%20Control.py#L234-L273), [B 출력](../FWU_v1/Logic/SF%20Control.py#L280-L311), [최대 RPM](../FWU_v1/Logic/Initialization.py#L355-L356).

**확인 필요:** ΔT 기본 −2와 실제 설계값(U10), 팬 하한 30%(U11), BMS 이상 유지가 별도 속도 스냅샷이 아닌 현재 점의 무기록 유지라는 점(U09), 부분 댐퍼·재기동(U19), 팬 자체 AO/Modbus 전환 지원(U21).

### 3.3 PICV Control — 냉수밸브로 급기온도 유지

**A:** Backup=1이고 자체 Failover=0이면 `PICV SAT SP Active=PICV SAT SP−0.5℃`, 아니면 원래 SP를 Active에 복사하고 Active를 PI 목표로 사용했다. F8의 **실행문은 −0.5℃**이며 다른 문서의 −1℃와 구분해야 한다.

**B:** Active 계산과 Backup 판정을 제거하고 `PICV SAT SP`를 직접 목표로 사용한다(C04). Backup이 없고 같은 SP이면 정상 제어는 같다. 상위가 추가 냉방을 원하면 SP를 직접 낮추는 등의 별도 구현이 필요하다.

**유지 기능:** Emergency가 없고 자동이며 Command=1·SF Status=1일 때 SAT 고장 알람이면 100%, 아니면 SAT PI(type 1, loop 1, sampling=1초, start=100, MinSP~100). Command=0이면 PI 초기화·밸브=0. 자동 유효값은 P11에도 기록, 수동은 P5 해제, Emergency는 P1/P11=0.

근거: [A](../SMX01-FWU-20261102/FWU-F8-ATS/Logic/PICV%20Control.py#L29-L66), [B](../FWU_v1/Logic/PICV%20Control.py#L32-L63).

**추가 확인:** `Command=1, SF Status=0`이면 새 밸브값을 쓰거나 루프를 초기화하는 분기가 없다. 따라서 “팬이 안 돌면 무조건 밸브가 닫힌다”는 설명은 정확하지 않다. SAT 고장 100% 분기에도 `LOOP2_INIT`은 없다. 복귀 누적값과 무풍 중 유지 개도는 U20에서 시험한다. SAT 고장 100%는 냉각 우선 설계로 해석되지만 모든 상황에서 안전한 위치라고 보증할 수 없다.

### 3.4 Alarm-1 — 공정·팬·댐퍼·밸브 이상 판단

**A의 기본 기능은 대부분 유지:**

- SF Status=1 후 타이머 0이 300초를 초과하면 RAT/RAH/SAT/SAH 및 CZT/HZT/RDP 상하한 알람 판정. 온도·차압 히스테리시스 0.5, 습도 5. 존 알람은 Valid=1일 때 최대값으로 상한, 최소값으로 하한을 판단한다. SF Status=0이면 상하한 알람과 타이머 초기화.
- SAT/RAT<0, SAH/RAH<5가 각각 20초 초과면 센서 고장. SAF는 차압이 기준 미만이고 팬 중 최대 RPM이 기준 초과일 때 20초 초과 후 고장 알람.
- 댐퍼 Partial Close는 팬 운전 중 일부 CLOSE만 1이면 즉시 알람. Full Close는 전폐+개방명령+현재 운전 또는 기존 알람 조건으로 유지된다. Not Open은 개방명령·SF 정지 조건 120초 초과 후 OPEN 누락, Not Close는 폐쇄명령 120초 초과 후 CLOSE 누락을 검사한다.
- 밸브는 지령과 피드백 차이의 절댓값이 **30 미만**일 때 유량 검사. 정확히 30도 편차 분기에 들어간다. 편차 30 이상이 40초 초과면 알람. 피드백>30이고 냉수공급 정상인데 저유량, 피드백<1인데 유량이 크면 별도 지연 없이 같은 PICV 알람을 쓴다.

근거: [B 상하한](../FWU_v1/Logic/Alarm-1.py#L62-L165), [센서](../FWU_v1/Logic/Alarm-1.py#L297-L335), [댐퍼](../FWU_v1/Logic/Alarm-1.py#L342-L399), [밸브](../FWU_v1/Logic/Alarm-1.py#L416-L437), [A](../SMX01-FWU-20261102/FWU-F8-ATS/Logic/Alarm-1.py#L46-L379).

**변경 1: 팬별 알람 외부 저장(C06)**

운전명령=1이고 속도≥Min인 조건에서 타이머 1이 60초를 초과하면 팬별 고장을 판정한다. 통신 정상이면 RPM<Failure RPM Set, 통신 이상이면 공통 차압≤Run DP Set. A도 팬별 내부 변수는 계산했지만 합계만 썼다. B는 기존 Run Fail VP 8개에 결과를 쓰며, 판단 조건이 꺼지면 개별·종합 모두 0으로 지운다.

**60초는 고장 지속 확인이 아니다.** 이미 충분히 운전 중이라 타이머가 60초를 넘은 경우, 새로 발생한 낮은 RPM은 다음 평가에서 곧바로 고장으로 판정될 수 있다. 팬 고장 60초+Failover 5초를 모든 고장에 일률적으로 더하면 잘못된 시나리오가 된다.

**변경 2: 모델 기준(C07)**

A의 `고장 수≥4`가 B의 `고장 수×2≥MAX(SF Count,1)`로 변경. 기본 8이면 동일하다. 홀수 5라면 산술 기준은 3대지만, 팬 판정 블록은 계속 8개이므로 설정만 5로 바꾸어 5팬 모델이 완성되지는 않는다. 공통 차압이 높으면 통신 불량인 여러 팬이 모두 정상으로 판정될 수 있다는 한계도 그대로다.

**변경 3: 유량계 통신 예외(C09)**

지령/피드백 차이가 30 미만이고 Flow Comm Fault=1이면 PICV 알람을 **유지하는 것이 아니라 0으로 쓴다**. 편차 30 이상이면 유량계 상태와 무관하게 40초 편차 검사가 유지된다. 냉수공급 정상 조건은 기존 기능이다.

**확인 필요:** 팬별 풍량스위치 대체 승인(U21), 통신 유실과 실제 팬 고장 구분(U21), 알람 자동 해제·히스토리(U22), RAT/SAT 고장값이 상하한 판정에도 들어가는 점(U18). 비래치 알람을 그 자체로 결함이라 판단하지는 않는다.

### 3.5 Alarm-2 — 존 센서 고장 + 누수·필터

**기본 역할/유지:** CZT 4개와 HZT 2개는 0 미만, RDP 2개는 0 이하가 20초 초과 지속되면 각각 고장 알람. 정상값이면 즉시 알람·타이머 0. 이 결과를 다음 초기화 실행이 읽어 센서를 제외한다.

**A→B:** 끝에 누수 입력 5초 초과 → Leak Alarm, 필터 입력 30초 초과 → Filter Alarm을 추가(C10/C11). 입력이 0이면 즉시 해제한다. 두 기능은 팬·밸브·Command를 쓰지 않는다. “누수로 정지하지 말 것”이라는 RFP 취지를 코드 분기에서 확인할 수 있다.

근거: [A 전체](../SMX01-FWU-20261102/FWU-F8-ATS/Logic/Alarm-2.py#L1-L89), [B 센서](../FWU_v1/Logic/Alarm-2.py#L37-L101), [B 신규 알람](../FWU_v1/Logic/Alarm-2.py#L105-L120).

**미완성 연결:** `FWU_LEAK DETECT`, `VP_FWU_Leak Alarm`, `VP_FWU_Filter Alarm`이 양쪽 ControlPoint 전체에 없다. 필터 원시 DI만 기존에 있다. 미정의점의 다운로드 거부/실행 예외/반환값은 엔진에서 확인해야 하며, “없는 점을 읽으면 0이라 문제없다”라고 가정할 수 없다(U01).

### 3.6 Alarm-3 — 장치 통신 상태를 논리 알람으로 변환

**유지:** 팬별 Current RPM 점에 `READPOINT_ALARM(...)==8`이 10초 초과 지속되면 해당 Comm Fault=1. 그 외에는 0·타이머 초기화. 종합은 8개 중 하나라도 1인지 OR 처리한다.

**변경:** ATS Current Power와 Flow.Rate에도 같은 패턴을 추가하여 타이머 8·9를 사용(C08/C09). ATS 결과를 장비 정지나 절체 명령으로 사용하는 Python은 없다. Flow 결과는 Alarm-1의 유량 검사에 사용한다.

근거: [A](../SMX01-FWU-20261102/FWU-F8-ATS/Logic/Alarm-3.py#L1-L83), [B](../FWU_v1/Logic/Alarm-3.py#L23-L109).

**주석과 설정 불일치:** [헤더](../FWU_v1/Logic/Alarm-3.py#L7-L9)는 Initialization 앞에 등록하라고 하지만, [실제 DDC 등록](../FWU_v1/DDC.xml#L15-L22)은 뒤다. 등록 순서대로 실행한다는 전제하에 팬 통신 전환과 유량 검사 억제에 한 스캔 지연이 있다. `READPOINT_ALARM` 지원과 `==8`의 복합 알람 처리도 U05에서 확인한다.

### 3.7 Remote Shutdown — 운전 출처와 무관한 정지 출력

**A:** Remote Shutdown Command=1이면 두 운전명령 P11=0, PICV·팬 AO/RPM P2=0, 팬 정지상태 후 SAD P2/P11=0. PICV·Speed Value P11도 0. 해제 시 P2 Release. 별도 Local/Remote·자동/수동 제한은 없다.

**B:** 연기 DI가 3초 초과 지속되면 기존 Fire Alarm VP=1, 입력 해소 시 0. `Remote Shutdown Command=1 OR (Fire Alarm=1 AND Smoke Action=1)`을 정지 조건으로 사용. Smoke Action 기본 0은 알람만이다. 정지 중 팬 8대 Run에도 P2=0, 해제 시 Run P2도 Release한다(C12).

근거: [A](../SMX01-FWU-20261102/FWU-F8-ATS/Logic/Remote%20Shutdown.py#L17-L50), [B](../FWU_v1/Logic/Remote%20Shutdown.py#L31-L96), [선택 기본값](../FWU_v1/ControlPoint/VirtualPoint.xml#L175-L176).

**영향:** BMS 운전명령이 P11보다 높은 우선순위에 남아 있어도, 그 명령 때문에 팬 Run이 1로 유지되는 문제를 P2에서 억제한다. 단 **팬 Run/출력 자체를 P1로 외부 강제한 경우까지 P2가 이긴다고 말할 수 없다.**

**확인 필요:** 정지 해제 시 재기동 안 함은 유효 Command가 0으로 남는다는 조건부 설명이다. 상위의 높은 우선순위/주기 쓰기, Local 모드에서 Command에 남아 있는 P5, 짧은 정지 후 출력 P5 복귀에 따라 결과가 달라질 수 있다(U09/U23). 하드웨어 릴레이 비상회로와 동일하게 취급하지 않는다.

### 3.8 Failover — 자체 용량 상실 통지와 일회 정지

**A:** SAD Not Open, SAD Full Close, SF Failure 중 하나 또는 Group Control Mode=1·Command=0(원격정지/비상정지가 아닐 때)을 원인으로 판단했다.

**B:** 그룹 원인만 삭제(C05). 나머지 3원인의 OR가 5초 초과이고 Failover Alarm=0이면 알람=1 및 두 Command P11=0을 **한 번** 쓴다. 알람이 1인 동안 매번 정지 명령을 재발행하지 않는다. 원인이 사라져도 알람을 유지하며, Reset=1·원인 없음이면 즉시 해제. Reset 점은 5초 초과 후 P11=0으로 복귀한다.

근거: [A](../SMX01-FWU-20261102/FWU-F8-ATS/Logic/Failover.py#L34-L69), [B](../FWU_v1/Logic/Failover.py#L35-L64).

**유지/변화의 구분:** 래치와 일회 정지·Reset은 유지다. Backup 제거의 실행문은 이 파일이 아니라 SF/PICV에 있다. B는 Failover Alarm을 상위가 읽어 이웃 FWU를 운전하도록 정보를 제공하려는 구조지만, **그 상위 구현과 통신 연결은 검증되지 않았다**. Failover Alarm 자체도 현재 Modbus 맵에 없다.

**주의:** 수동에서는 Command=0만으로 자동 팬/밸브 정지 시퀀스가 실행되지 않는다. Failover는 P1/P2 직접 출력 인터록과 다르다. 고장 알람이 래치된 채 재기동하면 새로운 원인에도 알람이 이미 1이라 일회 정지 분기가 다시 실행되지 않는다. 고장 확인→원인 해소→Reset→재기동 절차와 상위 정책을 확인해야 한다(U09/U17/U20).

## 4. RFP 반영 현황

### 4.1 판정 기준

- **구현 완료:** 이 행에서 정의한 소프트웨어 범위의 실행문과 필요한 내부 XML 연결 확인. 현장 시험 합격을 의미하지 않는다.
- **부분 구현:** 일부 기능은 있으나 XML/외부맵/입력/요구 옵션 또는 제출 정보가 빠져 있음.
- **미구현:** 현행 패키지에 해당 연결·설정이 없거나 명시적으로 비활성. 제품 자체가 지원 불가라는 뜻은 아님.
- **확인 필요:** 요구 범위 해석, 별도 하드웨어/고객 목록 없이는 판정 불가.

RFP의 제어·통신·관제점 관련 사항을 **R01~R32 32개 검토 단위**로 묶었다. 모든 기계·구조·보증·물류 조항의 적합성 집계는 아니다. 하드웨어 설치·공장시험이 포함된 원문은 소프트웨어 확인과 분리했다.

### 4.2 요구사항별 A/B 비교표

출처는 모두 원본 RFP의 `FWU(390 kW)` 시트 B열 해당 행이다. 근거 링크는 실제 구현/설정이며, 맵 누락은 §5 전수 대조 결과다.

| ID / RFP 행 | 요구사항 | 기존 SMX01 | 1차 개발 코드 | 반영 상태 | 근거/남은 조건 |
|---|---|---|---|---|---|
| R01 / 104·141 | 필터 오염 알람 | 원시 DI 등록, 지연 VP 처리 없음 | 30초 지연 알람 추가, 결과 VP 없음 | 부분 구현 | [처리](../FWU_v1/Logic/Alarm-2.py#L115-L120), [DI](../FWU_v1/ControlPoint/IO.xml#L29) |
| R02 / 108 | 팬 속도 하한 최대 20% | 하한 기능, 기본 30 | 동일 | 부분 구현 | [설정](../FWU_v1/ControlPoint/VirtualPoint.xml#L17), [클램프](../FWU_v1/Logic/SF%20Control.py#L138-L141). 20% 이하 성능/설정 미확정 |
| R03 / 109 | 개별 팬 고장 감시(원문은 풍량스위치) | RPM/공통DP 내부 판정 | 기존 VP에 팬별 결과 기록 | 부분 구현 | [판정/기록](../FWU_v1/Logic/Alarm-1.py#L176-L288). 팬별 스위치·BMS 결과맵 미확인/미등록 |
| R04 / 115·128 | 2-way 밸브 비례제어로 급기온도 유지, SW 범위 | SAT PI | SAT PI 유지, Backup 보정 제거 | 구현 완료 | [PI 및 IO](../FWU_v1/Logic/PICV%20Control.py#L40-L53), [밸브 출력](../FWU_v1/ControlPoint/IO.xml#L39) |
| R05 / 120 | 밸브 마지막/안전 위치 | 수동 유지, 비상/원격 0, SAT 고장 100 | 동일 | 부분 구현 | [밸브](../FWU_v1/Logic/PICV%20Control.py#L36-L63). 정전 액추에이터 위치·옵션 해석 필요 |
| R06 / 124 | 원격 온도 기반 제어 | CZT 보상 PV PI | CZT 자체 PV PI | 부분 구현 | [PI](../FWU_v1/Logic/SF%20Control.py#L169-L173). 내부 처리 있으나 Heartbeat 공급 경로 미완성 |
| R07 / 124 | 환기온도 기반 제어, SW 범위 | RAT PI | 유지 | 구현 완료 | [RAT 루프](../FWU_v1/Logic/SF%20Control.py#L147-L151), [입력](../FWU_v1/ControlPoint/IO.xml#L24) |
| R08 / 124 | 원격 차압 기반 제어 | RDP 보상 PV PI | RDP 자체 PV PI | 부분 구현 | [PI](../FWU_v1/Logic/SF%20Control.py#L154-L158). 내부 처리 있으나 Heartbeat 경로 미완성 |
| R09 / 124 | 급기온도 기반 제어 | 밸브 SAT PI, 팬 SAT 단독 모드 없음 | 동일 | 부분 구현 | [밸브](../FWU_v1/Logic/PICV%20Control.py#L47), [팬 선택](../FWU_v1/Logic/SF%20Control.py#L138-L173). 밸브로 충족 가능한지 고객 확인 |
| R10 / 127 | BMS 팬 속도 설정 쓰기, SW 범위 | 고정값 Speed SP와 HR 맵 | 유지. BMS 이상 모드에서는 정상 명령과 다름 | 구현 완료 | [사용](../FWU_v1/Logic/SF%20Control.py#L138-L141), [HR1076](../FWU_v1/ProtocolSerivce/Modbus/ModbusServiceInfo.xml#L153) |
| R11 / 129~131 | BMS 이상 시 마지막/최대 속도 선택 | 해당 옵션 없음 | 옵션·분기 추가 | 부분 구현 | [분기](../FWU_v1/Logic/SF%20Control.py#L92-L99), [속도](../FWU_v1/Logic/SF%20Control.py#L181-L187). Heartbeat/선택점 맵 없음, 적용 모드 범위 승인 필요 |
| R12 / 132 | 원격 ON/OFF 3단자와 명령 연결 | Local/Remote, 단일 정지 VP | 유지 | 부분 구현 | [명령선택](../FWU_v1/Logic/Initialization.py#L346-L353), [정지](../FWU_v1/Logic/Remote%20Shutdown.py#L42-L49). 3단자별 IO 및 결합 규칙 없음 |
| R13 / 133 | 지정 BMS Points List 표시/인터페이스 | 일부 맵 존재 | 맵 동일 | 확인 필요 | V1.3.R0·HMI 파일 미제공. 내부 점의 존재만으로 충족 불가 |
| R14 / 138·139 | 냉수 입·출수 온도 입력 | XML/참조 없음 | 목록에서 이름만 제안, XML/참조 없음 | 미구현 | 신규 목록 `1_신규 관제점` 16~17행. 부품 확정 후 구현 대상 |
| R15 / 140 | 유량값 관제점 및 SW 수집/감시 | Flow.Rate 등록/사용 | 통신 알람 추가, 유량 판정 보강 | 구현 완료 | [유량계](../FWU_v1/ControlPoint/Modbus3.xml#L20-L29), [감시](../FWU_v1/Logic/Alarm-3.py#L104-L109). 공장 설치는 별도 |
| R16 / 142 | 누수 알람 발생, 누수로 정지하지 않음 | 처리 없음 | 비정지 알람 분기, 입력/결과 VP 없음 | 부분 구현 | [누수](../FWU_v1/Logic/Alarm-2.py#L105-L110). 로프형 센서·맵 연결 필요 |
| R17 / 143 | 연기 시 계속/정지 선택, 내부 SW 범위 | DI/Fire VP만 등록, 해당 Python 처리 없음 | 3초 알람 및 Smoke Action 선택 | 구현 완료 | [처리](../FWU_v1/Logic/Remote%20Shutdown.py#L31-L96), [선택점](../FWU_v1/ControlPoint/VirtualPoint.xml#L176). 주소형 모듈·배선·HMI는 별도 확인 |
| R18 / 148 | ATS 자동 절체/복귀·지연·전원 선택 | ATS 상태점, DDC 절체 실행문 없음 | 통신 감시만 추가 | 확인 필요 | [ATS](../FWU_v1/ControlPoint/Modbus3.xml#L3-L19). ATS 자체 설정 자료 없음 |
| R19 / 16·124 | BACnet 통신/게이트웨이 | BACnet/IP·MS/TP 설정 | 동일 | 부분 구현 | [DDC BACnet](../FWU_v1/DDC.xml#L23-L25). 실제 서비스·게이트웨이·주소 확인 필요 |
| R20 / 16·124 | Modbus TCP/IP 통신 설정 | TCP 서비스 false, TCP 점 설정 비어 있음 | 동일 | 미구현 | [명시적 false](../FWU_v1/ProtocolSerivce/Modbus/ModbusServiceInfo.xml#L373). 현재 활성 구성 기준 |
| R21 / 17·127·133 | 외부 읽기·쓰기 맵 완전성 | 360맵, Heartbeat 등 누락 | 맵 그대로, 새 사용점도 누락 | 부분 구현 | [전체 맵](../FWU_v1/ProtocolSerivce/Modbus/ModbusServiceInfo.xml#L3-L373), §5.4 |
| R22 / 18~21 | Network/ID/IP/BACnet 주소 | Device 3, Dnet 76/100 등 | 동일 | 부분 구현 | [설정](../FWU_v1/DDC.xml#L23-L28). 현장 값·이중화 IP 정합성 확인 |
| R23 / 22~24 | BACnet Object Type/Instance/Property | 내부 타입·ID 있음 | 동일 유형 | 부분 구현 | [VP 예](../FWU_v1/ControlPoint/VirtualPoint.xml#L3-L18). 내부 ID를 BACnet Instance라고 단정 불가 |
| R24 / 25 | 외부 변수 Scaling | IO/Modbus 배율 있음 | 동일 | 부분 구현 | [IO](../FWU_v1/ControlPoint/IO.xml#L22-L39). 외부 단위·엔디언·배율 대조 필요 |
| R25 / 26 | 완전한 변수명 목록/연결 | 기존 참조점 XML 일치 | 3개 미정의 참조 발생 | 부분 구현 | [미정의 사용](../FWU_v1/Logic/Alarm-2.py#L105-L120), §5.2 |
| R26 / 27 | 변수 Data Range | 일부 범위, VP 다수 min=max=0 | 동일 + 새 설정점 | 부분 구현 | [VP](../FWU_v1/ControlPoint/VirtualPoint.xml#L175-L187). 전체 운전 허용범위 정의 필요 |
| R27 / 28 | 변수별 단위 | 일부 IO unit 존재 | 동일 | 부분 구현 | [온습도·DP](../FWU_v1/ControlPoint/IO.xml#L22-L26). 전체 외부 단위표 없음 |
| R28 / 17·29 | 변수별 동작 설명 | 코드/문서 일부 | 설명서·점 목록 보강 | 부분 구현 | 참고 문서 있음. 외부 전체 변수 명세·현행 사용열 불일치 남음 |
| R29 / 135~137 | SAT 및 RAT/습도 센서 정보 처리 | AI 정의·로직 참조 | 유지 | 부분 구현 | [AI](../FWU_v1/ControlPoint/IO.xml#L22-L25). 센서 실물·공장 배선까지는 검증 불가 |
| R30 / 118 | 응축수 펌프/이중 플로트 신호 연동 | 대응 IO/로직 식별되지 않음 | 동일 | 미구현 | 현행 SW 연동 범위 기준. 독립 하드웨어 펌프 제공 여부는 별도 |
| R31 / 125 | 전원 상실 중 제어전원 유지 | 파일로 실물 사양 판단 불가 | 동일 | 확인 필요 | DDC 이중화 설정은 커패시터/전원유지 성능 증거가 아님 |
| R32 / 52·59 | 공장 기능시험/품질 보고 | 시험 원자료 없음 | 검토서의 모의시험 주장만 있음 | 확인 필요 | [동료 시험 주장](../QTS_FWU_Logic_Revision_Review.md#L199-L200). 실기 시험 로그 미제공 |

**합계: 구현 완료 5 / 부분 구현 20 / 미구현 3 / 확인 필요 4 = 32.** 이는 고객 RFP 전체의 납품 적합률이 아니다. 원문 8행의 조항별 Compliance 제출, 11~13·31~43행의 성능/도면/인증, 구조·전기·유체 사양 및 보증/운송 조항은 이 Python/XML 분석만으로 판정할 수 없다.

**RFP와 직접 관계없는 개선:** C02(ΔT 방향), C03~C05(양산/상위 책임 경계), C07(모델 설정점), 미사용/중복 코드 제거. Failover 50% 기준의 근거는 코드·동료 자료에 인용된 DoO이며, RFP 109가 직접 “4대 고장 시 전체 정지”를 요구하는 것은 아니다.

## 5. 관제점 및 외부 통신 연결

### 5.1 실제 추가된 13점 전수 목록

기존 172 VP는 동일 속성으로 유지되고 다음 점만 추가되었다. **아래 13개 전부 외부 Modbus 맵에는 없다.** XML에 존재한다는 사실과 BMS에서 읽고 쓸 수 있다는 사실은 다르다. DV는 이 프로젝트의 이산 가상값, AV는 연속 가상값이다.

| 이름 | 타입 / ID | 기본값 / backupEnable | 역할·코드 사용 | XML 근거 |
|---|---|---|---|---|
| `VP_FWU_BMS Comm Fail Mode` | DV / 05000193 | 0 / 1 | HMI/BMS 설정 의도, SF 읽기. 0 유지, 1 최대 | [등록](../FWU_v1/ControlPoint/VirtualPoint.xml#L175) |
| `VP_FWU_Smoke Action` | DV / 05000194 | 0 / 1 | Remote Shutdown 읽기. 0 계속, 1 정지. Failover는 읽지 않음 | [등록](../FWU_v1/ControlPoint/VirtualPoint.xml#L176) |
| `VP_FWU_ATS Comm Fault` | DV / 05000195 | 0 / 0 | Alarm-3 쓰기, 다른 Python 소비자 없음 | [등록](../FWU_v1/ControlPoint/VirtualPoint.xml#L177) |
| `VP_FWU_Flow Comm Fault` | DV / 05000196 | 0 / 0 | Alarm-3 쓰기 → Alarm-1 읽기 | [등록](../FWU_v1/ControlPoint/VirtualPoint.xml#L178) |
| `VP_FWU_SF Count` | AV / 02000144 | 8 / 1 | Alarm-1의 50% 판정 분모 | [등록](../FWU_v1/ControlPoint/VirtualPoint.xml#L179) |
| `VP_FWU_SF Rated Max RPM` | AV / 02000145 | 1920 / 1 | Initialization 최대RPM 상한, SF AO 분모 | [등록](../FWU_v1/ControlPoint/VirtualPoint.xml#L180) |
| `VP_FWU_SF Max RPM Ratio` | AV / 02000146 | 110 / 1 | Initialization 설계RPM에 곱하는 비율(%) | [등록](../FWU_v1/ControlPoint/VirtualPoint.xml#L181) |
| `VP_FWU_SA Flow Coef` | AV / 02000147 | 235.751976 / 1 | Initialization 풍량식 계수 | [등록](../FWU_v1/ControlPoint/VirtualPoint.xml#L182) |
| `VP_FWU_SF Run DP Set` | AV / 02000148 | 10 / 1 | Initialization/Alarm-1의 팬 통신 이상 시 차압 기준(Pa) | [등록](../FWU_v1/ControlPoint/VirtualPoint.xml#L183) |
| `VP_FWU_SAF Fail RPM Set` | AV / 02000149 | 300 / 1 | Alarm-1 차압센서 고장 검사 시 팬 RPM 기준 | [등록](../FWU_v1/ControlPoint/VirtualPoint.xml#L184) |
| `VP_FWU_SAF Fail DP Set` | AV / 0200014A | 1 / 1 | Alarm-1 차압센서 고장 검사 기준(Pa) | [등록](../FWU_v1/ControlPoint/VirtualPoint.xml#L185) |
| `VP_FWU_PICV No Flow Set` | AV / 0200014B | 30 / 1 | Alarm-1 밸브 열림 저유량 기준(LPM) | [등록](../FWU_v1/ControlPoint/VirtualPoint.xml#L186) |
| `VP_FWU_PICV Leak Flow Set` | AV / 0200014C | 10 / 1 | Alarm-1 밸브 닫힘 통과유량 기준(LPM) | [등록](../FWU_v1/ControlPoint/VirtualPoint.xml#L187) |

### 5.2 목록의 18점과 실제 13점이 다른 이유

신규 목록의 `1_신규 관제점`은 **18점 = XML 추가 13 + 참조하지만 미정의 3 + 이름만 제안 2**다. 서로 다른 모집단이지 5점을 XML에서 누락해 센 것 아니다.

| 이름 | 목록상 타입 | 실제 코드 사용 | 현재 XML | 판정 |
|---|---|---|---|---|
| `FWU_LEAK DETECT` | DI(제안) | Alarm-2 읽기 | 없음 | 연결 미완성 |
| `VP_FWU_Leak Alarm` | DV(제안) | Alarm-2 쓰기 | 없음 | 연결 미완성 |
| `VP_FWU_Filter Alarm` | DV(제안) | Alarm-2 쓰기 | 없음 | 연결 미완성 |
| `FWU_CHW ENT TEMP` | AI(제안) | 없음 | 없음 | 명칭 예약일 뿐 미구현 |
| `FWU_CHW LVG TEMP` | AI(제안) | 없음 | 없음 | 명칭 예약일 뿐 미구현 |

목록의 CPU00-DI1 할당, 새 VP ID, Coil 1048 이후/HR 1192 이후 등은 **제안 주소**다. 현재 XML 주소로 인용하거나 실제 신호가 연결되었다고 판단하지 않았다.

### 5.3 이번에 사용하기 시작한 기존 12점 및 예약점

| 기존점 | 타입·수 | A→B 사용 변화 | 기존 XML/외부맵 |
|---|---|---|---|
| `VP_FWU_SF-1~8 Run Fail Alarm` | DV 8개 | 정의만 있음 → Alarm-1 쓰기 | [VP 143~150](../FWU_v1/ControlPoint/VirtualPoint.xml#L143-L150), 외부맵 없음 |
| `VP_FWU_Fire Alarm` | DV 1개 | 정의만 있음 → Remote Shutdown 쓰기/읽기 | [VP](../FWU_v1/ControlPoint/VirtualPoint.xml#L135), 외부맵 없음 |
| `FWU_FIRE ALARM` | DI 1개 | Python 미사용 → Remote Shutdown 읽기 | [IO](../FWU_v1/ControlPoint/IO.xml#L28), DI 주소 101 |
| `FWU_FILTER ALARM` | DI 1개 | Python 미사용 → Alarm-2 읽기 | [IO](../FWU_v1/ControlPoint/IO.xml#L29), DI 주소 102 |
| `FWU-ATS.Current Power` | AI 1개 | Python 미사용 → Alarm-3 알람 속성 읽기 | [장치점](../FWU_v1/ControlPoint/Modbus3.xml#L4), IR 주소 28000 |

`Run Command` 8개와 `FWU-Flow.Rate`는 기존에도 사용했다. 이번에는 각각 P2 강제/Release와 알람 속성 읽기가 추가된 것이지 새 점이 아니다.

**정의만 남은 상위 기능:** `Backup Operation`, `Group Control Mode`, `PICV SAT SP Active`, CZT Adj-1~4/RDP Adj-1~2, Adj Comp Weight, CZT/RDP Comp Own Margin·Comp PV. B의 실행문에서 읽거나 쓰지 않는다. HZT Adj-1~4도 XML에 있으나 A/B 모두 실제 보상에 사용하지 않는다.

**중복/혼동 주의:**

- `FWU_FILTER ALARM`은 원시 DI, `VP_FWU_Filter Alarm`은 지연 가공 결과이므로 같은 기능의 무의미한 중복이 아니다. 후자만 미정의다.
- `FWU_FIRE ALARM`과 `VP_FWU_Fire Alarm`도 원시/지연 결과다.
- `VP_FWU_PICV Leak Flow Set`은 **밸브 패싱 유량** 기준이다. 바닥 로프 누수 입력과 관계없다.
- `PICV SAT SP`는 현재 PI 목표, `PICV SAT SP Active`는 폐기된 중간값. Active를 써도 제어되지 않는다.
- `SF Failure RPM Set`(기본 150)은 팬 운전/고장 기준, 새 `SAF Fail RPM Set`(기본 300)은 **차압센서** 고장 검사 기준이다.
- `SF Speed Start Value`는 정의되지만 현재 PI 시작값에 쓰이지 않는다. 실제 팬 루프 인자는 60이다.

### 5.4 BMS 맵 전수 대조

[현재 맵](../FWU_v1/ProtocolSerivce/Modbus/ModbusServiceInfo.xml#L3-L373)은 A/B 동일하고 Coil 62, DiscreteInput 36, HoldingRegister 94, InputRegister 168, **총 360엔트리**다. 레지스터 주소 숫자는 XML의 원문 값을 사용했다. 0/1-base 변환이나 4xxxx 표기 변환은 하지 않았다.

| 주요점 | 현재 맵 | 의미/주의 |
|---|---|---|
| `VP_FWU_Command` | Coil 1029 | [명령 맵](../FWU_v1/ProtocolSerivce/Modbus/ModbusServiceInfo.xml#L40). 외부 쓰기 우선순위 속성은 없음 |
| `VP_FWU_Remote Shutdown Command` | Coil 1027 | 정지 요청 입력 |
| `VP_FWU_SF Status` / `Operation Mode` | Coil 1028 / 1030 | 상태/자동수동 |
| `VP_FWU_SF Speed Value` | HR 1030, 4바이트 | 계산 결과도 맵에 있음. 외부 직접 쓰기와 자동 P5 충돌 가능 |
| `VP_FWU_SF Control Select` | HR 1060, 4바이트 | [모드 맵](../FWU_v1/ProtocolSerivce/Modbus/ModbusServiceInfo.xml#L145) |
| `VP_FWU_Speed SP` | HR 1076, 4바이트 | [설정 맵](../FWU_v1/ProtocolSerivce/Modbus/ModbusServiceInfo.xml#L153) |
| `VP_FWU_PICV SAT SP` | HR 1134, 4바이트 | [설정 맵](../FWU_v1/ProtocolSerivce/Modbus/ModbusServiceInfo.xml#L182) |
| Heartbeat / Prev / BMS Comm Fault / Reset | 없음 | Prev는 내부용이라 외부 공개가 반드시 필요한 것은 아님. **Heartbeat 공급 경로는 필요** |
| Failover Alarm / Reset | 없음 | 상위 Backup 판단/원격 Reset 연결 미완성 |
| 새 13점 / 기존 Fire Alarm·Run Fail 9점 | 없음 | 내부 기능 추가가 외부 인터페이스에 반영되지 않음 |

B에서 실행문이 참조하고 XML에도 있는 VP 중 **외부맵이 없는 점은 69개**다. 모든 점을 공개해야 한다는 의미는 아니다. 내부 계산점과 상위 연동 필수점을 분리해야 한다. 신규 목록 3번 시트의 61개는 “이전 코드에서 쓰던 점” 기준이며, 현재 69개와 집계 기준이 다르다.

**미해결 맵 ID 38개(로직 ID 5개는 별도로 정상 연결 인정):**

| 범위 | 수 | 예/주소 | 해석 |
|---|---:|---|---|
| Coil 1000~1026 | 27 | 050000C8~05000143의 해당 27개 ID | 같은 꼬리의 AV ID와 혼동 가능하지만 자동 수정/추정 연결 금지 |
| HR 0·2·4·6·8 | 5 | 1A000000~1A000004 | 시스템 내장점 가능성, 제공 ControlPoint에는 없음 |
| HR 1146·1148 | 2 | 0200015A·0200015B | [실제 맵](../FWU_v1/ProtocolSerivce/Modbus/ModbusServiceInfo.xml#L188-L189), 정의 찾지 못함 |
| IR 0·2·4·6 | 4 | 19000000~19000003 | 시스템 내장점 가능성, 제공 ControlPoint에는 없음 |

이 38개는 **제공 파일만으로 대상이 해소되지 않은 수**다. 전부 잘못된 주소 또는 다운로드 오류라고 단정하지 않았다. A에도 존재하므로 v1에서 새로 만든 문제는 아니다. 시스템 내장점 여부와 잔존 맵 정리는 U04에 기록했다.

## 6. DDC 실행·우선순위·타이머 관점

### 6.1 실행 순서와 실행 주기

[A](../SMX01-FWU-20261102/FWU-F8-ATS/DDC.xml#L15-L22)와 [B](../FWU_v1/DDC.xml#L15-L22)의 등록 순서는 같다.

**Initialization → PICV Control → SF Control → Alarm-1 → Alarm-2 → Alarm-3 → Remote Shutdown → Failover**

파일 간 함수 호출/일반 Python import로 연결하지 않고 관제점을 통해 연결한다. 위 순서대로 반복 실행되고 쓰기가 즉시 관제점에 반영된다는 실행 모델로 아래 흐름을 해석한다. 실제 스케줄러·입출력 갱신 시점은 실기 확인 대상이다.

| 전달 | 등록 순서대로 실행한다면 |
|---|---|
| Initialization 상태/PV → PICV/SF/Alarm-1 | 같은 스캔에 소비 가능 |
| Alarm-2 센서 고장 → Initialization | 다음 스캔 반영 |
| Alarm-3 팬 통신 → Initialization/SF/Alarm-1 | 다음 스캔 반영 |
| Alarm-3 Flow Comm Fault → Alarm-1 | 다음 스캔에서 유량 알람 억제 |
| Alarm-1 자체고장 → Failover | 같은 스캔에 읽을 수 있음 |
| Remote Shutdown → 팬/밸브 | 후반부 P2 쓰기로 유효출력 강제. 먼저 실행한 PI 내부 상태가 자동 초기화되는 것은 아님 |
| Failover Command P11=0 → 일반 정지 | 다음 앞단 실행에서 읽음. Local이면 P5 복사값 갱신이 더 늦어질 수 있음 |

**확정할 수 없는 것:** DDC 전체 한 스캔이 1초라는 명시 속성은 없다. `logicInfo.addr`가 대부분 VP1000000000, Remote Shutdown만 VP1000000001인 이유도 주기/우선순위로 해석할 근거가 없다.

**확인 가능한 별도 시간:** SF LOOP2의 sampling=0은 LDPL §7.3에서 기본 1초, PICV는 명시 1초다. 팬 일반 출력은 타이머 `>5`일 때 갱신한다. 포트 pollingDelay=300·timeout=500은 통신 설정이지 전체 로직 스캔주기가 아니다. 스케줄 50개는 이름/ID/type만 있어 FWU 기동·정지 시간을 실제 구성했다고 볼 수 없다.

### 6.2 주요 공유점 읽기·쓰기 관계

P5는 일반 `WRITEPOINT` 및 통상 로직 출력의 기본 우선순위라는 LDPL 설명을 적용했다. BMS/HMI 입력 우선순위는 별도 미확인이다.

| Point | 쓰는 곳 | 읽는 곳/영향 |
|---|---|---|
| `VP_FWU_Command`, `Command-HMI` | Initialization P5/P11 복사, SF Emergency P11, Remote P11, Failover P11 | SF·PICV 자동 분기, Alarm-1 팬 판정. Local/Remote에 따라 유효명령 출처 다름 |
| `VP_FWU_SF Speed Value` | SF P5 및 P11, Remote P11=0 | SF의 Run/RPM/AO 변환, Alarm-1 판정. 값이 0이 아니어도 P2 출력은 0일 수 있음 |
| `FWU_SAD-1_4 COMMAND` | SF P5/P11, Emergency P1, Remote P2/P11 | Alarm-1 댐퍼 알람. 팬 상태를 기다린 후 닫힘 |
| `FWU_PICV CONTROL` | PICV PI/P5, P11 미러, Emergency P1/P11, Remote P2/P11 | Alarm-1 피드백 편차. 일반 정지는 출력 명령과 실제 피드백을 구분 |
| `FWU SF-n.Target RPM Set`, 팬 AO 2점 | SF 일반 P5/비상 P1, Remote P2 | 통신/IO 드라이버로 실제 출력 |
| `FWU SF-n.Run Command` | SF P5, Remote P2 | 팬 제어. B에서만 원격정지 Run P2가 추가됨 |
| CZT/HZT/RDP `PV`, `PV Valid` | Initialization P5 | SF 일부 PI/고정값 분기, Alarm-1 존 상하한 |
| `SF-n Comm Fault`, `SF Comm Fault` | Alarm-3 P5 | Initialization 상태, SF 경로 전환, Alarm-1 대체 판정 |
| `SF Status` | Initialization P5 | 밸브 운전, 팬/댐퍼 정지 순서, 알람 지연 |
| `SF Failure`, `SAD Not Open`, `SAD Full Close` | Alarm-1 P5 | Failover 원인 |
| `Failover Alarm` | Failover P5 | B에서는 자체 래치 확인. 상위 소비자 구현/맵은 없음 |

### 6.3 Priority와 Release의 실제 의미

- 이 코드의 의도는 **P1 > P2 > P5 > P11**(숫자가 작을수록 높은 우선순위)다. 같은 Point의 우선순위 배열에서 경쟁한다. 파일이 뒤에 있다고 낮은 우선순위가 높은 것을 덮는 것은 아니다.
- P1: 비상 PICV, 팬 AO/RPM, 정지 후 SAD. 정상 분기에서 각 P1 Release.
- P2: Remote/선택 연기 정지의 PICV, 팬 AO/RPM, 팬 Run, 정지 후 SAD. 정지 조건이 사라지면 각 P2 Release.
- P5: 일반 제어. 수동으로 바꾸면 PICV·Speed Value·SAD의 자동 P5를 Release하지만, 팬 출력 변환/Run 갱신 P5는 계속 사용한다.
- P11: 자동값 보관, 정지 Command, Reset 복귀. 의도적으로 P11을 매번 Release하지 않는다. **0 쓰기와 Release는 다르다:** 0은 해당 슬롯이 점유된 값이고, Release는 해당 슬롯을 비워 다음 유효값을 드러낸다.
- P1/P2 강제 출력마다 해제 경로는 있다. 그러나 해제 시 남아 있던 P5 값이 드러나는지, 수동 전환 때 P11 값이 최신인지, 외부의 더 높은 강제가 있는지는 실기 추적해야 한다.

근거: [SF 전체 우선순위](../FWU_v1/Logic/SF%20Control.py#L114-L269), [PICV](../FWU_v1/Logic/PICV%20Control.py#L36-L63), [Remote](../FWU_v1/Logic/Remote%20Shutdown.py#L47-L96), LDPL §§4.2–4.3. Stop 명령을 P11에 쓴 사실만으로 “언제나 출력 0”이라고 결론내리지 않는다.

### 6.4 SECTIMER 배정 전수표

LDPL §6.2는 **한 로직당 0~9의 10개 타이머**를 설명한다. 따라서 서로 다른 파일의 1번 타이머를 번호 중복 오류로 판단하지 않았다. 실제 펌웨어에서 로직 인스턴스별 상태가 분리되는지는 현장 확인한다. 모든 시간 비교는 아래 숫자의 **초과(`>`)**이며, 정확히 그 초에 실행 완료된다는 의미가 아니다.

| 파일 | A | B | 조건/시간과 해제 |
|---|---|---|---|
| Initialization | 5,6,7 | 동일 | 5: SF 상태 변화 >5초. 6: Heartbeat 무변화 >30초. 7: Comm Reset >5초. 상태 동일/Heartbeat 변화/Reset 꺼짐에서 각각 리셋 |
| PICV | 없음 | 없음 | LOOP2 sampling과 SECTIMER를 혼동하지 않음 |
| SF | 1 | 동일 | 일반 출력 >5초마다 실행 후 리셋 |
| Alarm-1 | 0~9 | 동일 | 0 상하한 판정 대기 300; 1 팬 판정 허용 대기 60; 2 SAT/3 SAH/4 RAT/5 RAH/6 SAF 고장 20; 7 미개방/8 미폐쇄 120; 9 밸브편차 40 |
| Alarm-2 | 0~7 | **0~9** | 0~3 CZT, 4~5 HZT, 6~7 RDP 고장 20; 추가 8 누수 5, 9 필터 30. 입력 정상 시 리셋 |
| Alarm-3 | 0~7 | **0~9** | 0~7 팬 통신 10; 추가 8 ATS/9 유량계 통신 10. 알람코드가 8이 아니면 리셋 |
| Remote | 없음 | **0** | 연기 입력 >3초; 입력 해소 시 리셋 |
| Failover | 1,2 | 동일 | 1 원인 >5초 후 래치·일회 정지; 2 Reset >5초 후 요청점 0 |

근거: [초기화](../FWU_v1/Logic/Initialization.py#L56-L76), [상태 타이머](../FWU_v1/Logic/Initialization.py#L324-L329), [팬 출력](../FWU_v1/Logic/SF%20Control.py#L280-L311), [Alarm-1 배정과 실행문](../FWU_v1/Logic/Alarm-1.py#L45-L437), [Alarm-2](../FWU_v1/Logic/Alarm-2.py#L37-L120), [Alarm-3](../FWU_v1/Logic/Alarm-3.py#L23-L109), [Remote](../FWU_v1/Logic/Remote%20Shutdown.py#L31-L36), [Failover](../FWU_v1/Logic/Failover.py#L44-L64).

### 6.5 통신·IO·스케줄 구성

- [DDC 포트](../FWU_v1/DDC.xml#L3-L14): 1/2/3은 Modbus 9600·8N1, 4는 ModbusSlave 19200·8N1. 팬 주소 82~85/86~89, ATS 01/유량계 02는 각 장치 XML에 있다. RTU 장치 주소와 외부 BMS 슬레이브 주소 1은 다른 계층이다.
- [BACnet 문자열](../FWU_v1/DDC.xml#L24-L25): Device Instance 3, B/IP `eth0`, Dnet 76, UDP 47808, MS/TP Dnet 100·38400·node 0·Port 4. MS/TP Port 4와 ModbusSlave 포트 4가 같은 물리 자원인지 확인 필요하다. **숫자만으로 충돌 확정은 하지 않는다.**
- [TCP 서비스](../FWU_v1/ProtocolSerivce/Modbus/ModbusServiceInfo.xml#L373)는 `isTCPServiceEnable=false`, 포트값 502. 502 숫자가 있어도 활성 상태가 아니다.
- [이중화](../FWU_v1/DDC.xml#L27-L28)는 serviceEnable=true, ACTIVE, sibling 192.168.1.132, virtual 192.168.1.133. 프로젝트의 F8 주소 10.10.10.3과 역할·서브넷 정합성을 확인해야 한다.
- [IO](../FWU_v1/ControlPoint/IO.xml#L22-L51): SAT/RAT는 0~10V, A=10/B=−20, 범위 −20~80; 습도 A=10/B=0; SAF DP A=150/B=0. 팬 AO와 PICV는 0~10V·0~100%·A=10/B=0. 아날로그 출력은 % 관제점으로 사용하며 실제 전압 반영은 드라이버/시운전 확인 대상이다.
- Emergency/Fire/Filter 입력의 polaritySet=0. 접점 실물 NO/NC와 활성 의미는 코드만으로 확정할 수 없다.
- 실제 FWU에 이름/ID가 할당된 IO는 22개이며, 나머지 22개는 비어 있는 ID의 기본/여유 엔트리다. “IO 44개”를 실제 연결 센서 44개로 설명하지 않는다.

### 6.6 LDPL 가이드와 실제 함수명 차이

| 항목 | 가이드 확인 | 코드 | 해석 한계 |
|---|---|---|---|
| 기본 읽기/쓰기 | 예제에서 READPOINT/WRITEPOINT 사용, §4.2에서 기본 우선순위 5 설명 | 동일 명칭 | 미정의점 처리·반환 오류 규칙은 제공 근거로 확정 불가 |
| 우선순위 쓰기 | §4.2 p.54는 `WRITE_PRI(point,value,priority)`; p.3 개정이력은 `WRITEPOINT_PRI` | `WRITEPOINT_PRI` | 의도는 특정 우선순위 쓰기. 실제 지원 별칭/버전 확인 |
| 해제 | §4.3 p.55 `RELEASE_PRI(point,priority)` | 동일 | 1~16. 전체 Release와 구분 |
| 알람 읽기 | §4.10 p.62 `ALARM(point)`, 0/1/2/4/8 | `READPOINT_ALARM` | 이 이름은 PDF 텍스트에서 찾지 못함. 8=통신 경보 의미는 확인, 동일 API라고 확정 못 함 |
| 초시계 | §6.2 p.72 `SECTIMER(index,options)`, options 0 reset/1 현재 초 | 동일 | 조건문에서 호출/리셋되는 위치 중요. WAIT처럼 로직을 재우는 함수 아님 |
| PI/PID | §7.3 pp.80–81, 13인자, sampling 0=기본 1초 | LOOP2, D=0 | 내부 계산식·포화복귀·실제 응답은 런타임 검증 필요 |
| 누적 초기화 | §7.4 p.82 `LOOP2_INIT(loop_id)` | 동일 | p.4 개정이력의 `LOOP_INIT_2`와 표기 차이. 본문/코드 이름 기준 |
| MAX/MIN | §§3.3–3.4 pp.33/35, 최대 5인자 | 최대 4인자 호출, 8팬은 중첩 MAX | 제한 초과 호출 없음 |

가이드의 LOOP2 표는 type 1을 냉방/하향 PV, type 0을 상향 PV로 설명하지만 **p.81 냉방 예제는 설명·호출 숫자가 모순**이다. 본문 표와 pp.114–115의 냉방밸브 type 1/덕트압 팬 type 0 예제를 함께 근거로 방향을 해석했다. B의 ΔT 방향 변경은 해당 해석 및 일정 부하에서 풍량 증가 시 ΔT 감소라는 물리 가정에 부합한다. 실기에서 역동작이 없다는 검증을 대신하지 않는다.

또한 §7.3은 같은 제어점의 loop_id에 관한 안내를 포함하는 반면, 현재 SF는 동일 출력점에 모드별 ID 1~4를 배정하고 비선택 루프를 초기화한다. 상호 배타 운전 의도는 코드로 확인되나, 해당 엔진에서의 허용/상태 분리 여부는 U06에서 확인한다.

## 7. 대표 동작 검토 및 현장 시험 연결

초보자용 **상황 → 입력 → 판단 → 명령 → 장비 동작**의 상세 사례는 [학습 가이드](FWU_v1_study_guide.md)에 모았다. 여기서는 차이와 시험의 핵심만 정리한다. “기대 장비 동작”은 배선·장치 반응·우선순위가 정상이라는 가정이며 실측 결과가 아니다.

| 시험 | A 대비 B에서 볼 것 | 관측점 |
|---|---|---|
| 정상 기동/정지 | 기본 시퀀스 동일. 정상 정지 완료 전에 P1/P2 강제 정지와 혼동 금지 | Command, SAD OPEN/CLOSE, Speed Value, PICV CONTROL/FEEDBACK, SF Status |
| BMS Heartbeat 중단/복구 | RDP/CZT·Remote 고정값에서 유지/최대, Local 고정값/RAT/ΔT는 제외. Reset 필요 | HB/Prev/Comm Fault/Reset, 모드, Speed Value, 물리 RPM |
| CZT 한 센서/전체 고장 | 고장 제외는 유지. 전체 고장+정상 BMS는 고정값. BMS 이상과 구분 | Failure, PV Valid, PV, Speed SP |
| SAT/RAT 고장 | SAT 운전 중 밸브 100은 유지. RAT 고장으로 팬 PI가 자동 대체되지 않는 점 확인 | SAT/RAT Failure, PI 출력/누적 상태 |
| 팬 1대/4대 고장 | 새 개별 VP, 기본8에서 종합 기준 동일. 장기운전 중 고장은 추가60초 없이 판정 가능 | RPM, Run Fail 8점, SF Failure, Failover/Command |
| 팬 통신 1대 불량 | 전체 AO 경로 전환은 유지. 공통 차압 대체가 실제 고장을 가리는지 확인 | raw alarm, Comm Fault, AO 두 그룹, Target RPM/Run |
| ATS/유량계 통신 중단 | 새 통신 알람, 유량 기반 PICV 알람 0. 편차 알람은 계속 | ATS/Flow Comm Fault, Flow.Rate, PICV_Alarm |
| 연기0/1, 원격/비상/수동 조합 | 연기선택 추가, Run P2 추가, 해제 후 잔존 우선순위 확인 | 16단계 우선순위, 유효값, 접점/전압/실제 RPM |
| Group/Backup/Adj 쓰기 | A는 반응할 수 있고 B는 예약점 쓰기만으로 반응하지 않음 | SP/PV/출력, 상위 보상 프로그램·복원 동작 |

## 8. 참고 문서와 현행 구현 사이의 주의점

1. 동료 검토서/점 목록은 과거 커밋과 `sy` 기준의 개정 이력을 포함한다. 이 보고서는 지정한 두 폴더를 직접 비교했다. 5초 팬 출력·팬 Run·센서 제외·SAT 고장 전개방 등을 신규 구현으로 세지 않았다.
2. “소프트웨어 기능 반영”이라는 문서 표현보다 **실제 연결 상태를 엄격하게** 보았다. 누수/필터 미정의점, Heartbeat 누락이 있어 일부 RFP 행은 부분 구현으로 판정했다.
3. “Modbus TCP 설정 없음/미확인”에서 더 나아가 실제 서비스의 **false**를 확인했다. 제품 지원 여부와 현재 비활성 설정을 구분한다.
4. 신규 목록의 18점은 실제 XML 증가 13점과 다르다. 기존 설명서 마지막 참고표의 “신규 9점”은 모델 설정점 추가 전 설명이 남아 있는 것으로 보인다.
5. 신규 목록 1번 시트의 Smoke Action 읽기 열, 2번 시트의 Fire Alarm 읽기 열에 Failover가 남아 있고, 3번 시트 예약점의 예전 읽기/쓰기 열도 남아 있다. **B의 Failover는 Smoke Action/Fire Alarm을 읽지 않고, 예약 기능점도 읽지 않는다.** 예약 비고와 실행문을 우선한다.
6. 동료 자료의 “정격 RPM에 0 이하를 넣으면 1로 취급”은 **SF AO 분모에 한정**된다. [Initialization 최대RPM](../FWU_v1/Logic/Initialization.py#L356)은 Rated 값을 그대로 MIN 상한으로 사용한다. 0/음수이면 최대RPM이 0/음수가 될 수 있다. 모든 경로가 보호됐다는 설명은 과도하다.
7. “고장 센서만 제외”는 Failure Alarm이 확정된 뒤의 동작이다. 20초 확인 전/다음 스캔 전에는 불량 원시값이 집계될 수 있다. RAT/ΔT 팬 제어와 CZH는 별도 유효성 보호가 없다.
8. “팬 제어 선택 범위 밖이면 속도가 멈춤”은 **계산 갱신이 멈춘다**는 뜻으로 읽어야 한다. 출력이 0이라는 뜻이 아니다.
9. “해제 후 자동 재기동 없음”, “Failover는 FWU를 정지”는 일반 자동운전과 명령 우선순위가 맞는 상황의 의도다. 수동·Local P5 복사·BMS 반복 쓰기까지 포함한 무조건 보장은 아니다.
10. 검토서의 45개 모의 시나리오·118,000스캔·위반0은 **해당 문서의 시험 주장**이다. 이번 작업에서 재현하거나 실물 DDC로 검증하지 않았다. 가이드 §8은 설비 예제 중심이며, Python 구문 제한 전체를 거기서 보증한다고 보지 않았다.

## 9. 미결·미확인 항목 24건

**U01~U24 = 24건**으로 관리한다. 한 건에 관련 점/시험을 묶었다. 우선도는 분석상 제안이며 임의 수정은 하지 않았다. 확정된 누락도 아직 조치·검증되지 않았으므로 미결 수에 포함한다.

| ID | 우선 | 확인 사실/미결사항 | 필요한 확인·시험 |
|---|---|---|---|
| U01 | 최우선 | Alarm-2 참조 3점이 XML에 없음(§3.5, §5.2) | 누수 입력 단자/타입 및 두 DV 등록 설계, 다운로드 검증. 미정의점 런타임 동작 확인 |
| U02 | 최우선 | Heartbeat/Comm Reset 등 BMS 경로 누락, 사용 중단 옵션 없음 | 실제 공급 경로·주기·값 변경 방식 확정, 맵 구성 및 장애/복구 시험. 1~5초는 제안일 뿐 현행 구현 아님 |
| U03 | 높음 | 새13점, Fire/팬별 결과, Failover 등 외부맵 누락(§5.4) | 필요한 점 공개·접근권한·우선순위·HMI 연결. 현재 미등록69 VP 전부가 필수라는 뜻은 아님 |
| U04 | 높음 | 맵 미해결ID 38개가 A/B에 공통 존재 | 시스템 내장 1A/19 계열 여부, 잔존 Coil27·HR2 대상 해소. ID 꼬리만으로 치환 금지 |
| U05 | 최우선 | `READPOINT_ALARM`/`WRITEPOINT_PRI` 가이드 명칭 차이, `==8` 검사 | 실제 DDC API/펌웨어 확인. 복합 알람 비트 조합 가능 여부·8 이외 상태 시험 |
| U06 | 높음 | 실제 스캔주기·등록 순서 준수·loop/timer 상태 범위 미확인 | 스캔 추적. Alarm-3 헤더/등록 불일치, 동일 출력 모드별 loop ID 허용 확인 |
| U07 | 높음 | BACnet MS/TP Port4와 ModbusSlave port4 설정 공존 | 논리/물리 포트 대응, 동시 활성 가능 여부, 통신 드라이버 점유 확인 |
| U08 | 높음 | TCP false, BACnet/이중화/프로젝트 주소의 현장 적합성 미확인 | RFP TCP 서비스 구성, 게이트웨이·B/IP·MS/TP·서브넷·주소 충돌 시험 |
| U09 | 높음 | Command P11 정지는 외부 높은 우선순위/주기쓰기·Local P5에 가려질 수 있음 | Local/Remote·자동/수동 각각 Failover/짧은 Remote 정지, 상위 반복 쓰기 시험 |
| U10 | 최우선 | ΔT type 변경에 비해 SP 기본 −2 유지 | 설계 ΔT·PI 방향·튜닝·출력 시작값60과 범위 정합성, 열부하 변화 시험 |
| U11 | 높음 | SF Speed Min 기본30, RFP 하한 최대20과 불일치 | 20% 이하 설정·팬 최저 안정 RPM·풍량 검증, 승인값 관리 |
| U12 | 높음 | 새 설정은 F8 8블록을 동적 모델로 바꾸지 않음. Rated 상한/비율/Min·Max 입력 방어 불충분 | 모델별 블록·점 구성, 음수/0/역전범위/잘못된 모드 제한. AO 0~100 하한·상한을 모든 경로가 보장하는지 시험 |
| U13 | 높음 | 연기/비상/필터 DI 극성·Smoke 기본0의 현장 적합성 미확인 | 실물 NO/NC·단선·주소형 모듈·소방 정책·연기0/1·해제/재기동 승인 |
| U14 | 높음 | 3개 원격 ON/OFF 단자의 점/조합 없음 | 고객 단자 해석, 도면·IO·우선순위·보호회로 설계 |
| U15 | 보통 | 냉수 입·출수 온도 2점은 문서상 예약만 | 센서 사양·실제 IO/Modbus·배율·화면 정의 |
| U16 | 높음 | ATS 절체/복귀/지연·전원유지 성능은 DDC 코드로 검증 불가 | ATS 자체 설정/배선·정전/복전 시험, 제어전원 유지 사양·응축수 펌프 인터페이스 |
| U17 | 높음 | Backup/그룹/인접 보상 제거, 상위 구현 증거 없음 | 제거 범위 승인, 상위 감지·명령·SP 저장/복원·통신 장애 제외·실제 냉방용량 시험 |
| U18 | 높음 | 센서확정20초+순서지연, RAT/ΔT·CZH 보호 차이(§3.1~3.4) | 음수/고착/상한초과/0차압/복구 시험. 전체유효성 정책, 고장 중 냉방/과냉 정책 |
| U19 | 높음 | 부분 댐퍼/중간 위치에서 속도 무기록 유지, 전개방 확인은 새 PI 계산 조건 | 전원복구·수동→자동·댐퍼 모순 OPEN/CLOSE·운전 중 부분폐쇄 시험 |
| U20 | 높음 | PICV 무팬+Command1에서 유지, SAT고장시 누적 초기화 없음. 수동에서 일반 Command 정지 미적용 | 밸브 stuck/피드백≥5 정상정지 지연, SAT고장복구, 수동 Failover·무풍 개도 시험 |
| U21 | 높음 | 팬60초는 판정허용 대기, 공통DP 대체·RPM=임계값 경계·전체AO 전환 | 운전 중 단기 RPM 저하, 통신장애 동시 팬고장, 팬별 풍량스위치 요구 대체 승인. Run+RPM/AO 장치 의미 확인 |
| U22 | 보통 | 다수 알람 자동해제, Flow Fault에서 유량기반 PICV 알람0, Failover 래치와 별개 | 원인별 알람 이력·억제 상태 표시·고장복구 추적 정책. 비래치를 자동 결함 판정하지 않음 |
| U23 | 높음 | backupEnable·P11이 재부팅/절체 중 실제 출력의 연속성을 증명하지 않음 | DDC 이중화·정전복구·P1/P2 Release 때 잔존P5·짧은 정지 후 재가동 시험 |
| U24 | 높음 | 지정 BMS 목록·HMI·실기시험 원자료 없음 | 단위/범위/객체/엔디언·접근권한 전수 대조, FAT/SAT 성적서와 로그 확보 |

## 10. 검증 범위와 최종 요약

### 수행한 검증

- 비교 루트 전 파일 읽기/바이트 비교, Python 16개 AST 파싱 및 실행문 차이 검토.
- XML 전체 파싱, Point 이름·ID·기존 속성 비교, Python 문자열 인자 참조와 IO/Modbus/VP 정의 대조, 외부 맵 ID 연결 검사.
- RFP 및 두 Excel의 관련 시트 셀 내용, 참고 Markdown, LDPL 함수 규격/예제 대조.
- 정상/장애/정지/상위 기능 사례를 조건문과 우선순위 흐름으로 추적. **DDC 실기시험, PI 폐루프 성능시험, 다운로드 시험은 수행하지 않았다.**
- 두 산출물의 상대 링크 대상·줄번호 범위, 코드 발췌와 실제 실행문 일치, 변경/요구사항/미결 ID 및 상태 집계를 검사했다.

Git에는 비교 대상 밖의 옛 추적 경로 삭제 표시와 두 비교 디렉터리의 미추적 표시가 남아 있다. 이번 작업에서 해당 상태를 복구·정리·스테이징하지 않았다. **원본을 수정하지 않았다는 설명은 Git 작업 트리가 깨끗하다는 뜻이 아니다.**

### 집계 요약

| 항목 | 결과 |
|---|---|
| 분석 대상 | **53파일**: 비교46 + 프로젝트1 + 참고6 |
| 파일 차이 | **23쌍 중 수정9·동일14, 추가0·삭제0** |
| 주요 변경 | **12건(C01~C12)** |
| 실제 XML 신규점 | **13점**, 기존점 삭제/속성변경0 |
| Python 미정의 참조 | **3점**; 문서상 추가 예약만 된 냉수온도2점은 별도 |
| RFP 검토 단위 | **32건: 완료5·부분20·미구현3·확인필요4** |
| 미결/미확인 | **24건(U01~U24)** |

기존 Python·XML·참고 자료는 수정하지 않았고 Git Commit·Push를 수행하지 않았다. 산출물은 이 보고서와 [FWU_v1_study_guide.md](FWU_v1_study_guide.md) 두 개다. 현장 적용 결정은 미결항목 해소 및 실제 DDC/장비 시험 후 내려야 한다.