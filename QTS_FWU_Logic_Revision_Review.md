# QTS 요구사항 기반 FWU 로직 수정 검토서 (rev.2)

**검토일:** 2026-11-10  
**대상:** QTS `FWU(390 kW)` / FWU-F8-ATS 로직 8개 및 DDC 설정 파일  
**문서 단계:** 코드 작성 전 요구사항·경량화·추가 코드·Point 설계 검토

**rev.2 변경 사항**
- 작업 폴더의 설정 파일(DDC.xml, IO/Modbus/VirtualPoint, BMS Modbus 주소표)과 대조해, 이전 판의 "자료 미제출" 판정을 갱신했다.
- **Point 삭제 금지 원칙**을 적용했다. 로직에서 쓰지 않는 Point도 HMI/BMS/외부에서 쓸 수 있으므로 Point는 추가만 하고 삭제·개명하지 않는다. 그 결과 이전 판의 "Point 삭제 후보(§6.6)"는 폐지하고, 경량화를 **코드 경로 정리**로 한정했다.
- 신규로 분류했던 일부 Point(필터, 화재, 팬 Run Fail, ATS)를 **기존 Point 재사용**으로 정정했다.
- 파일명을 실제 이름 `SF Control.py`로 정정했다(이전 판 `SF Control(1).py`, 행번호는 동일).
- **사용자 결정 반영(2026-11-10):** Backup 운전(L11)은 BMS PLC 연동 계획이 있어 **유지하고 BMS 주소표에 연결**한다. Failover 자동 정지(L12)는 **철회**하고 현행 코드를 유지한다(QTS 근거 없음, 동작 변경). 인접 보상(L13)은 **유지**한다. 따라서 선택 경량화 3건은 모두 코드 삭제 없이 **BMS 주소표 연결 작업(X02)** 으로 바뀌었다.

## 1. 먼저 볼 결론

1. 현재 코드는 팬 제어(고정/RAT/RDP/ΔT/CZT), SAT 기반 PICV 제어, 수동/자동, 로컬/원격, 원격 정지, 비상 정지, 팬 통신 감시를 이미 갖고 있다.
2. QTS 대비 **코드로 바로 보완 가능한 항목**은 BMS 통신 두절 시 HOLD/MAX, 팬별 운전실패 알람, 연기(화재) 검출 시 동작 선택, 정지 경로 결함 수정이다. 모두 **기존 Point와 기존 I/O로 구현 가능**하며, 신규 가상 Point는 7개다.
3. **하드웨어 없이는 불가능한 항목**은 누수 검출, 팬별 풍량 스위치, 원격 on/off 3단자, 냉수 입·출구 온도다. 필요한 입력 14점에 비해 여유 입력은 13점이라 **I/O 증설 또는 취득 방식 변경**이 필요하다.
4. **경량화 폭은 작다.** 동작에 영향 없는 중복·미사용 코드 정리(L01~L04)만 수행한다. 현장 전용 기능(Backup, Failover 자동 정지, 인접 보상)은 BMS PLC 연동 계획과 QTS 근거 부재를 고려해 **모두 현행 유지**로 결정했다. 대신 BMS PLC가 이 기능을 쓸 수 있도록 **주소표 연결**이 필요하다(§5.2, X02).
5. 로직 외 설정에서 먼저 처리할 위험이 있다. BMS Heartbeat의 BMS 쓰기 경로가 없고, ATS 절체 관련 쓰기 Point가 BMS에 노출되어 있으며, 실행 순서가 Alarm-3 주석과 다르다.

| 구분 | 내용 | 비고 |
| --- | --- | --- |
| 1차 코드 추가 | BMS 두절 HOLD/MAX, 팬별 Run Fail 알람, 연기 동작 선택, 통합 정지 상태, ATS/유량계 통신 감시 | 현재 I/O로 가능 |
| 1차 결함 수정 | 원격 정지 중 Run Command 유지(C01), PICV 닫힘 무한 대기(C03), 미정의 모드값(C06), RAT/ΔT 센서 고장 대응(C08) | |
| 확정 경량화 | ΔT 중복 계산, 미사용 HZT Gain 읽기, 반복 조건 정리 | 동작 변화 없음 |
| 현장 맞춤 기능 유지 | Backup 운전, Failover 자동 정지, 인접 보상 | 코드 유지. BMS PLC 연동용 주소표 추가(X02) |
| 설정 변경 | DDC 실행 순서, BMS 주소표 추가, HMI 알람 속성, ATS 쓰기 권한 | 코드 외 |
| 2차(하드웨어 후) | 누수, 팬별 풍량 스위치, 원격 3단자, 냉수 온도 | I/O 확정 후 |

**Python 파일 추가는 필요 없다.** 기존 8개 파일 안에서 남는 타이머로 수용한다(§8.3).

## 2. 검토 근거

### 2.1 사용 자료

| 자료 | 적용 범위 | 비고 |
| --- | --- | --- |
| `QTS_Airside Equipment_CDE_260628-2 1.xlsx` | `FWU(390 kW)` 시트, SECTION 23 81 24.3-PP | 작업 폴더 루트에 있음. rev.2에서는 B행 인용을 재검증하지 않고 이전 검토 결과를 사용 |
| `LDPL Programming Guide-v27.pdf` | 우선순위, 타이머, PI, 작성 규칙 | 작업 폴더에 없음. 이전 검토 결과 인용 |
| `Logic/*.py` 8개 | 제어·알람 로직 | 전체 대조 |
| `DDC.xml` | 포트, 로직 등록 순서, 이중화 | 대조 완료 |
| `ControlPoint/IO.xml` | 물리 I/O와 여유 슬롯 | 대조 완료 |
| `ControlPoint/Modbus1~3.xml` | 팬 8대, ATS, 유량계 | 대조 완료 |
| `ControlPoint/VirtualPoint.xml` | 가상 Point 172개, 기본값 | 대조 완료 |
| `ProtocolSerivce/Modbus/ModbusServiceInfo.xml` | BMS용 Modbus 슬레이브 주소표 | 대조 완료 |
| `ProtocolSerivce/BACnet/BACnetServiceInfo.xml` | BACnet 객체 매핑 | 비어 있음 |
| `ScheduleInfo/*.xml` | 스케줄 | 빈 Schedule01~18만 존재 |

QTS 위치는 `FWU(390 kW)!B행번호`, 코드 위치는 `파일명:행번호`로 표시한다.

### 2.2 설정 파일에서 확인한 구성

| 항목 | 확인 내용 |
| --- | --- |
| 통신 포트 | 포트 1 = SF-1~4, 포트 2 = SF-5~8, 포트 3 = ATS(슬레이브 01)·유량계(02), 모두 Modbus RTU 마스터 9600 bps. 포트 4 = BMS용 Modbus RTU 슬레이브 19200 bps |
| Ethernet 프로토콜 | Modbus TCP 설정 비어 있음. BACnet은 장치 번호(3)만 있고 객체 매핑 없음 |
| DDC 이중화 | Duplex 활성(상대 192.168.1.132, 가상 IP 192.168.1.133) |
| 로직 실행 순서 | Initialization → PICV Control → SF Control → Alarm-1 → Alarm-2 → Alarm-3 → Remote Shutdown → Failover. Remote Shutdown만 등록 주소가 `VP1000000001`로 다름 |
| 여유 물리 I/O | 입력 13점(CPU UI1~6, DI1~4, CM02 UI5·UI6·UI8), DO 5점(CPU DO1~3, CM02 DO10·DO11), AO 4점(CPU AO1~3, CM02 AO4). UI14 모듈은 14점 모두 사용 |
| BMS 주소표 | 가상 Point 172개 중 94개만 등록. 모든 가상 Point의 `alarmEnable=0` |
| 주요 기본값 | Speed SP 50 %, SF Speed Min **30 %**, Speed Max 100 %, Design RPM 1569, Failure RPM 150, Adj Comp Weight 70 %, Chilled Water Supply Condition **1** |

### 2.3 아직 판정할 수 없는 사항

- QTS B133이 참조하는 `BMS HVAC Controls Systems Points List V1.3.R0`가 없다. BMS Point의 최종 누락 판정은 불가능하다.
- I/O 결선도, HMI 화면, 팬·밸브·응축수 펌프·ATS 사양서가 없다.
- BMS·HMI가 각 Point를 어떤 우선순위로 쓰는지 알 수 없다(C01 판단에 영향).
- QTS C열 `O`는 준수 표시일 뿐 구현 증거로 보지 않았다.

## 3. 작업 원칙: Point 유지

| 원칙 | 적용 |
| --- | --- |
| 삭제 금지 | VirtualPoint/IO/Modbus Point와 BMS 주소표 항목을 삭제하지 않는다. 존재하지 않는 Point를 가리키는 주소표 항목도 별도 승인 전까지 유지한다 |
| 개명 금지 | 기존 Point 이름은 바꾸지 않는다. HMI·BMS 참조가 이름/ID로 연결되어 있다 |
| 값 멈춤 방지 | 로직 경로를 걷어낼 때, 해당 경로가 쓰던 Point는 **중립값을 계속 기록**한다. 예: 인접 보상 제거 시 `CZT Comp PV = CZT PV` |
| 표시용 계산 유지 | BMS 주소표에 노출된 계산값(CZT/HZT/RDP/CZH Avg·Max·Min 등)은 외부 사용 가능성이 있으므로 계산을 유지한다 |
| 신규 Point | 필요한 최소 수만 추가한다. 이중화 동기화가 필요한 값은 `backupEnable=1`, 외부 확인이 필요한 값은 BMS 주소표에 추가한다 |

## 4. QTS 요구사항과 현재 구현의 차이 (설정 파일 반영)

### 4.1 운전·제어·통신

| ID | QTS 근거 | 요구사항 | 현재 구현과 판정 | 수정 방향 |
| --- | --- | --- | --- | --- |
| Q01 | B124 | 원격 온도·급기온도·환기온도·원격 차압 활용 제어 | **구현.** 팬 고정/RAT/RDP/ΔT/CZT, 밸브 SAT PI | 유지 |
| Q02 | B127 | BMS에서 팬 속도 쓰기 | **구현(고정 모드).** `VP_FWU_Speed SP`가 BMS HR 1076으로 쓰기 가능. PI 모드에서는 속도를 직접 정하지 않음 | 유지. 고정 모드 선택(`SF Control Select`)도 BMS에서 쓸 수 있는지 주소표 확인 |
| Q03 | B129:B131 | BMS 통신 두절 시 직전 속도 유지 또는 최대속도를 설정으로 선택 | **미구현.** Heartbeat 감시는 있으나 CZT/RDP PV 무효 시 `Speed SP`로 전환(`SF Control.py:54–61`). RAT/ΔT/고정 모드에는 대응 없음. **Heartbeat가 BMS 주소표에 없어** BMS가 Modbus로 쓸 수 없음 | N01 추가. Heartbeat·Comm Fault·Reset을 주소표에 추가(X02) |
| Q04 | B132 | 원격 on/off 단자 3개 | **미구현.** 원격 정지는 BMS Coil 1027의 가상 Point 1개. 물리 단자 없음 | 2차(H03). 여유 DI 필요 |
| Q05 | B16, B124 | Ethernet·RS485, BACnet/Modbus TCP | **부분.** RS485 Modbus RTU 슬레이브만 설정됨. Modbus TCP·BACnet 매핑 비어 있음 | 설정 작업(X05). 로직 수정 아님 |
| Q06 | B17:B29, B133 | 변수·주소·단위·범위 제공 | **부분.** Modbus 주소표 있음(94/172). BACnet 객체표 없음. V1.3 목록 없음 | 신규·미등록 Point 주소표 추가(X02), V1.3 대조 |
| Q07 | B108 | 팬 저속 20 % 조건 | **확인 필요.** `SF Speed Min` 기본값 30 %. "최저속도 한계 ≤ 20 %"로 해석하면 비준수 가능 | 기본값 변경 여부 결정(K10). 코드 변경 없음 |
| Q08 | B115, B120, B128 | 2-way 변조 밸브로 SAT 유지 | **구현.** `PICV Control.py:44–50` | 유지 |
| Q09 | B120 | 비스프링리턴, 정전 시 위치 | **하드웨어 확인.** | 액추에이터 설정으로 확인 |

### 4.2 센서·장치·알람

| ID | QTS 근거 | 요구사항 | 현재 구현과 판정 | 수정 방향 |
| --- | --- | --- | --- | --- |
| Q10 | B109 | 팬별 고장 감지(풍량 스위치) | **미구현.** 팬별 판정은 내부 변수뿐이고 4대 이상만 종합 알람(`Alarm-1.py:233`). `VP_FWU_SF-1~8 Run Fail Alarm` Point는 **이미 있으나 미사용** | 1차: RPM 기반 팬별 알람(N02). 2차: 풍량 스위치 입력 결합(H02) |
| Q11 | B136 | 급기온도 센서 | **구현.** `FWU_SAT` | 유지 |
| Q12 | B137 | 환기 온·습도 | **구현.** `FWU_RAT`, `FWU_RAH` | 유지 |
| Q13 | B138 | 냉수 입구온도 | **Point 없음** | 2차(H04) |
| Q14 | B139 | 냉수 출구온도 | **Point 없음** | 2차(H04) |
| Q15 | B140 | 유량계 | **구현.** `FWU-Flow.Rate`(포트 3, BMS IR 28020), 밸브 진단에 사용 | 유량계 통신 고장 감시 추가(N05) |
| Q16 | B104, B141 | 필터 DP 스위치·오염 알람 | **입력 있음.** `FWU_FILTER ALARM` DI(UI14 모듈 8번), BMS DI 102로 노출. 로직·HMI 알람 없음 | 코드 추가 없이 DI의 HMI 알람 속성 활성화(X03) |
| Q17 | B142 | 누수 감지, 누수로 정지 금지 | **Point 없음** | 2차(H01). 알람만 |
| Q18 | B143 | 연기 검출, 운전 지속/정지 현장 선택 | **입력 있음, 로직 없음.** `FWU_FIRE ALARM` DI(BMS DI 101)와 미사용 `VP_FWU_Fire Alarm` 존재. 현재 주석상 화재 인터록 없음 | N03: 동작 선택 추가. 기본값은 현재 동작과 같은 CONTINUE. DI가 환기부 연기검출기인지 확인(K07) |
| Q19 | B118 | 이중 플로트 응축수 펌프 | **Point 없음.** | 하드웨어 확인 후 결정(H05) |
| Q20 | B112 | 역류 방지 | **전동 SAD 4개로 구현** | 유지 |

### 4.3 전원·시험·코드 외

| ID | QTS 근거 | 요구사항 | 현재 구현과 판정 | 조치 |
| --- | --- | --- | --- | --- |
| Q21 | B125 | 정전 중 제어전원 유지 | **하드웨어 확인** | 상태 접점 제공 시 관제 |
| Q22 | B148 | 이중 전원 자동 절체·복귀, 우선전원 선택, 상태 표시 | **통신 Point 있음.** `FWU-ATS`(포트 3): Current/A/B Power, S1/S2 선간전압, Alarm, `Source Priority`·`Auto transfer mode`·`Transfer by comm request`(RW). 로직 미사용 | 절체는 ATS 자체 기능 유지. DDC는 상태 수집과 ATS 통신 고장 감시(N05). **BMS 쓰기 노출 검토(K11)** |
| Q23 | B59, B52 | 공장 시험 | **자료 없음** | §12 시험을 FAT 항목으로 사용 |
| Q24 | B111, B147 | 고조파·단로·SCCR | **장치 사양** | 코드 대상 아님 |

## 5. 경량화 범위 (Point 유지 전제)

Point를 지우지 않으므로, 경량화는 **실행 코드에서 중복·미사용 경로를 걷어내는 것**으로 한정한다. 현장 맞춤 기능은 사용자 결정에 따라 §5.2처럼 처리한다.

### 5.1 확정 경량화 (동작 변화 없음)

| ID | 위치 | 내용 | Point 처리 |
| --- | --- | --- | --- |
| L01 | `SF Control.py:63–64` | ΔT PV 중복 계산 제거. `Initialization.py:269`만 계산 | `VP_FWU_DeltaT PV` 유지(Initialization이 계속 기록) |
| L02 | `SF Control.py:66–68` | 사용하지 않는 HZT PGain/IGain 읽기 제거 | `VP_FWU_SF HZT PGain/IGain` Point 유지 |
| L03 | `Initialization.py` CZT/HZT/RDP 집계부 | CZT/HZT/RDP 집계의 `BMS_OK == 1 and` 반복 조건을 상위 조건 하나로 묶음 | 결과값 동일 |
| L04 | `Failover.py:18–20` | 주석 "-1 C"를 실제 값 "-0.5 C"로 정정 | 주석만(실행 코드는 변경 없음) |

### 5.2 현장 맞춤 기능 처리 결정 (2026-11-10 확정)

| ID | 위치 | 내용 | 결정 | 필요한 후속 작업 |
| --- | --- | --- | --- | --- |
| L11 | `SF Control.py:77–82, 143–149`; `PICV Control.py:32–36` | Backup 운전(팬 최대 + SAT SP −0.5 ℃). 이 FWU의 `Failover Alarm`이 0일 때만 적용 | **유지.** BMS PLC 연동 계획 있음 | `VP_FWU_Backup Operation`이 BMS 주소표에 없어 BMS PLC가 켤 수 없음(BACnet 매핑도 비어 있어 현재는 HMI로만 가능). 주소표 추가(X02) |
| L12 | `Failover.py:50–53` | Failover 확정 시 Command 0 자동 정지 | **철회. 코드 변경 없음.** QTS FWU 시트에 Failover·"정지 금지" 근거가 없고, 정지를 없애면 동작이 바뀜 | `Failover Alarm`이 BMS 주소표에 없어 BMS PLC가 이웃 FWU의 Backup을 시작할 수 없음. 주소표 추가(X02). DoO "FWU Failover Criteria" 확인(K01) |
| L13 | `Initialization.py:220–266` | 인접 CZT/RDP 보상 | **유지** | Adj 센서·Weight·Margin이 주소표에 없어 이웃 값이 기본값(CZT 25 ℃, RDP 5 Pa)에 고정되고, 이 기본값으로는 보상 조건이 성립하지 않아 **현재 보상이 동작하지 않음**. 주소표 추가(X02) |

#### 5.2.1 BMS PLC 연동용 주소표 추가 대상

| Point | 방향 | 용도 |
| --- | --- | --- |
| `VP_FWU_Backup Operation` | BMS PLC 쓰기 | 이웃 FWU 고장 시 보충 운전 요청 |
| `VP_FWU_Failover Alarm` | BMS PLC 읽기 | 이 FWU가 용량을 공급할 수 없다는 통지 |
| `VP_FWU_Failover Reset` | BMS PLC 쓰기(필요 시) | 알람 해제. HMI로도 가능 |
| `VP_FWU_Group Control Mode` | BMS PLC 쓰기 | 그룹 제어 모드. 1이고 Command 0이면 Failover 원인 4 |
| `VP_FWU_CZT Adj-1~4`, `VP_FWU_RDP Adj-1~2` | BMS PLC 쓰기 | 이웃 구역 온도·차압 |
| `VP_FWU_Adj Comp Weight`, `CZT/RDP Comp Own Margin` | BMS/HMI 설정 | 보상 가중치·자기 구역 여유 |
| `VP_FWU_CZT Comp PV`, `RDP Comp PV` | BMS PLC 읽기 | 보상 적용 PV 확인 |

연동 시 확인할 점은 K17에 둔다. 아래 L11~L13의 구 검토 문구는 이력으로만 남긴다.

<details><summary>이전 판 L11~L13 검토 문구(이력)</summary>

| ID | 위치 | 내용 | 현재 실효성 | 걷어낼 때 Point 처리 | 권고 |
| --- | --- | --- | --- | --- | --- |
| L11 | `SF Control.py:77–82, 143–149`; `PICV Control.py:32–36` | Backup 운전(팬 최대 + SAT SP −0.5 ℃) | `VP_FWU_Backup Operation`이 BMS 주소표에 없음. Modbus BMS로는 켤 수 없고 HMI로만 가능(BACnet 매핑은 비어 있음) | `PICV SAT SP Active = PICV SAT SP` 계속 기록. Backup Operation Point는 남지만 무시 | 사용처 확인 후 제거(K02) |
| L12 | `Failover.py:50–53` | Failover 확정 시 Command 0 자동 정지 | Group Control Mode·Failover Alarm/Reset이 주소표에 없음 | Failover Alarm 판정과 Reset은 유지, 자동 정지만 제거 | 자동 정지만 제거(K01) |
| L13 | `Initialization.py:220–266` | 인접 CZT/RDP 보상 | Adj 센서·Weight가 주소표에 없음. Adj 기본값(CZT 25 ℃, RDP 5 Pa)에서는 CZT는 `25 > SP(30)` 불성립, RDP는 `5 < SP(3)` 불성립으로 **현재 보상이 걸리지 않음** | `CZT/RDP Comp PV = CZT/RDP PV` 계속 기록. SF Control은 Comp PV를 그대로 읽어 변경 최소화 | 제거(K03). 단, HMI에서 Adj 값을 쓰고 있다면 유지 |

</details>

### 5.3 경량화하지 않는 항목과 이유

| 항목 | 유지 이유 |
| --- | --- |
| CZT/HZT/RDP/CZH Avg·Max·Min, PV Select | BMS 주소표에 노출됨. 계산을 멈추면 외부 표시값이 멈춤 |
| CZT/HZT/RDP 센서 고장 알람(Alarm-2) | 집계에서 고장 센서 제외에 사용 |
| ΔT·RAT 제어 모드 | 모드 선택 기능. 제거 시 모드 번호 의미 변경 위험 |
| SAH 알람, SAD 4개 인터록, 공통 SAFLOW DP 풍량 | 실제 장착 장치와 연결됨 |
| 1920 rpm·Design RPM×1.1 환산 | 팬 사양값. 설정으로 관리 |

### 5.4 이전 판 D항목과의 대응

| 이전 판 | rev.2 처리 |
| --- | --- |
| D01 인접 보상 | L13. 유지 결정, 주소표 연결 |
| D02 Failover | L12. 철회, 현행 유지 |
| D03 Backup | L11. 유지 결정, 주소표 연결 |
| D04 HZT 집계·Gain | 집계 유지(BMS 노출), Gain 읽기만 제거(L02) |
| D05 CZH 집계 | 유지(BMS HR 노출) |
| D06 ΔT 중복 | L01 |
| D07~D14 | 유지 또는 설정 관리. Point 삭제 없음 |

## 6. 추가 코드 범위

### 6.1 1차: 현재 I/O로 구현 가능

| ID | 파일 | 추가 내용 | 사용 Point(신규는 ★) | 타이머 |
| --- | --- | --- | --- | --- |
| N01 | `SF Control.py` | BMS 통신 두절 대응(HOLD_LAST/MAX). 정상 시 직전 유효 속도 저장 | `VP_FWU_BMS PLC Comm Fault`, ★`VP_FWU_BMS Comm Fail Mode`, ★`VP_FWU_Last Valid SF Speed`, ★`VP_FWU_BMS Fallback Active` | 없음 |
| N02 | `Alarm-1.py` | 팬별 Run Fail 알람. 기존 판정 변수 `SF1_FAIL~SF8_FAIL`을 기존 Point에 기록 | `VP_FWU_SF-1~8 Run Fail Alarm`(기존) | 기존 1번(60 s) 공유 |
| N03 | `Remote Shutdown.py` | 화재/연기 입력 확인, 동작 선택(CONTINUE/SHUTDOWN), 통합 정지 상태 산출 | `FWU_FIRE ALARM`, `VP_FWU_Fire Alarm`(기존), ★`VP_FWU_Smoke Action`, ★`VP_FWU_Shutdown Active` | 0번(입력 확인 지연) |
| N04 | `SF Control.py`, `PICV Control.py` | 통합 정지 상태를 팬 속도·Run Command·밸브에 일관 반영(C01). PICV 닫힘 대기 Timeout(C03). 미정의 모드값·RAT/SAT 고장 시 고정속도 전환(C06, C08). Command=1·팬 정지 시 밸브 처리(C04, K08) | `VP_FWU_Shutdown Active` 등 | SF Control 2번(PICV 닫힘 대기) |
| N05 | `Alarm-3.py` | ATS·유량계 통신 고장 감시. 유량계 통신 고장 시 PICV 유량 진단 억제(C12) | `FWU-ATS.Current Power`, `FWU-Flow.Rate`, ★`VP_FWU_ATS Comm Fault`, ★`VP_FWU_Flow Comm Fault` | 8번, 9번 |

**신규 가상 Point는 7개다.** 별도 Fallback 시작속도 설정, Last Valid 유효 플래그, Heartbeat Timeout 설정, Alarm Summary, 필터 VP 알람은 만들지 않는다(경량화).

### 6.2 2차: 하드웨어·결선 확정 후

| ID | 내용 | 필요 입력 | 배치 |
| --- | --- | --- | --- |
| H01 | 로프 누수 알람(정지 금지) | DI 1 | Alarm-2 8번 타이머 |
| H02 | 팬별 풍량 스위치를 N02 판정에 결합(`RPM 미달 or 풍량 미확인`) | DI 8 | Alarm-1 기존 1번 타이머 공유 |
| H03 | 원격 on/off 3단자 | DI 3 | Remote Shutdown |
| H04 | 냉수 입·출구 온도와 센서 고장 | AI 2(또는 통신 취득) | Alarm-2 9번 타이머(공통 지연) |
| H05 | 응축수 고수위/펌프 고장 | 제공 접점에 따름 | 장치 확정 후 |

필요 입력은 **14점**(누수 1 + 풍량 8 + 원격 3 + 냉수 온도 2)이고, 연기검출기를 화재 접점과 따로 받으면 15점이다. 여유 입력 13점으로는 부족하다. 다음 중 하나가 필요하다(K13).
- I/O 확장 모듈 추가
- 냉수 온도를 통신(BTU/유량계 등)으로 취득해 AI 2점 절감
- CPU 내장 UI/DI 실제 사용 가능 여부 확인

### 6.3 설정 변경 (로직 파일 외)

| ID | 대상 | 내용 |
| --- | --- | --- |
| X01 | `DDC.xml` | 실행 순서 변경: **Alarm-3 → Initialization → Remote Shutdown → PICV Control → SF Control → Alarm-1 → Alarm-2 → Failover**. Alarm-3 주석 요구와 정지 상태의 같은 스캔 반영을 맞춤 |
| X02 | `ModbusServiceInfo.xml` | 주소표 **추가**: Heartbeat(HR, BMS 쓰기), Comm Fault(읽기), Comm Reset(쓰기), **BMS PLC 연동 Point(§5.2.1: Backup Operation, Failover Alarm/Reset, Group Control Mode, Adj-1~4, RDP Adj-1~2, Adj Comp Weight, Comp Own Margin, Comp PV)**, 신규 Point 7개, `Chilled Water Supply Condition`(쓰기), 미등록 기존 알람(SAT/SAH/RAT/RAH/SAF 고장, PICV, SAD 4종, Fire, Run Fail 8개, CZT/HZT/RDP 고장·상하한 등) |
| X03 | Point 속성 | HMI 알람 이력이 필요한 Point의 `alarmEnable` 설정(`FWU_FILTER ALARM`, `FWU_FIRE ALARM`, 신규 알람 등) |
| X04 | `VirtualPoint.xml` | 신규 7개 등록. `Last Valid SF Speed`, `BMS Comm Fail Mode`, `Smoke Action`은 `backupEnable=1`(이중화 절체 시 유지) |
| X05 | 프로토콜 | QTS가 Ethernet BACnet/Modbus TCP를 요구하면 해당 서비스 매핑 작성 |
| X06 | ATS 쓰기 매핑 | HR 28000~28004(`Source Priority`, `Auto transfer mode`, `Transfer by comm request`)의 BMS 쓰기 허용 여부 결정(K11). 삭제가 아니라 R/W 속성 변경 |

## 7. Point 목록

### 7.1 재사용하는 기존 Point (이전 판에서 신규로 분류했던 항목)

| 기존 Point | 위치 | 이전 판 분류 | rev.2 처리 |
| --- | --- | --- | --- |
| `FWU_FILTER ALARM` | IO.xml DI, BMS DI 102 | P03 신규 DI | 재사용. HMI 알람 속성만 설정 |
| `FWU_FIRE ALARM` | IO.xml DI, BMS DI 101 | P05 신규 DI | 재사용(연기검출기 여부 확인) |
| `VP_FWU_Fire Alarm` | VirtualPoint, 미사용 | A03 신규 | 재사용(확인 지연 후 기록) |
| `VP_FWU_SF-1~8 Run Fail Alarm` | VirtualPoint, 미사용 | A04 신규 8점 | 재사용 |
| `FWU-ATS.*` | Modbus3.xml, BMS 노출 | P12~P15 신규 DI | 재사용. DI 신규 불필요 |
| `VP_FWU_Speed SP` | BMS HR 1076 | R03 | BMS 속도 명령으로 유지 |
| `VP_FWU_BMS PLC Heartbeat/Prev/Comm Fault/Comm Reset` | VirtualPoint, 주소표 없음 | R06 | 유지, 주소표 추가(X02) |

### 7.2 신규 가상 Point (1차, 7개)

| 제안 Point | 형식 | 값 | 기본값 | 쓰는 주체 → 읽는 주체 | backup |
| --- | --- | --- | --- | --- | --- |
| `VP_FWU_BMS Comm Fail Mode` | 수치/열거 | 0 = HOLD_LAST, 1 = MAX | 0 | HMI/BMS → SF Control | 1 |
| `VP_FWU_Last Valid SF Speed` | 수치 % | 직전 유효 적용 속도 | 0 | SF Control → SF Control, HMI/BMS | 1 |
| `VP_FWU_BMS Fallback Active` | 이진 | 1 = 두절 대체운전 중 | 0 | SF Control → HMI/BMS | 0 |
| `VP_FWU_Smoke Action` | 이진/열거 | 0 = CONTINUE, 1 = SHUTDOWN | 0 | HMI 설정 → Remote Shutdown | 1 |
| `VP_FWU_Shutdown Active` | 이진 | 1 = 원격 정지 또는 연기 정지 활성 | 0 | Remote Shutdown → SF/PICV Control | 0 |
| `VP_FWU_ATS Comm Fault` | 이진 | 1 = ATS 통신 고장 | 0 | Alarm-3 → HMI/BMS | 0 |
| `VP_FWU_Flow Comm Fault` | 이진 | 1 = 유량계 통신 고장 | 0 | Alarm-3 → Alarm-1, HMI/BMS | 0 |

이름은 제안명이다. 실제 ID·주소는 VirtualPoint.xml의 빈 ID 범위를 확인해 배정한다.

### 7.3 신규 물리 입력 (2차)

| 제안 Point | 수량 | 비고 |
| --- | --- | --- |
| `FWU_LEAK DETECT` | DI 1 | 알람만, 정지 금지 |
| `FWU_SF-1~8 AIRFLOW` | DI 8 | 팬별 풍량 스위치 |
| `FWU_REMOTE ENABLE-1~3` | DI 3 | 접점 의미(허용/정지, NO/NC) 확정 후 이름·극성 결정 |
| `FWU_CHW ENT TEMP`, `FWU_CHW LVG TEMP` | AI 2 | 통신 취득 가능하면 Modbus Point로 대체 |
| 응축수 고수위/펌프 고장 | 접점에 따름 | 장치 확정 후 |

알람 Point(누수, 냉수 센서 고장)는 2차 입력 확정 시 함께 추가한다.

### 7.4 정리 권고 (삭제하지 않음, 별도 승인 대상)

| 항목 | 내용 |
| --- | --- |
| 주소표의 고아 항목 | Coil 1000~1026(ID 050000C8~D2, 05000131, 05000134~143), HR 1146/1148(0200015A/B), 1A000000~4, 19000000~3은 존재하지 않는 Point를 가리킴. Point 삭제 금지 원칙과 별개로, 정리 여부를 승인받아 처리(K15) |
| 로직 미사용 Point | `HZT Adj-1~4`, `HZT SP`, `SF Start FD`, `Fan Restart`, `PICV Flow/PIDOut/Max LPM/Design LPM`, `SF Control RDP/HZT Out`, `SF Speed Start Value`, `CZT Control Min`, `SAF VA-1`, `SF Failure Flow Set`, `VP_RAD Check Alarm`, `Model` 등. **유지**한다. 외부에서 쓰지 않는다면 HMI/BMS에 "로직 미사용"으로 표기만 권고 |

## 8. 파일별 수정 계획

### 8.1 파일별 변경 요약

| 파일 | 1차 변경 | 경량화 |
| --- | --- | --- |
| `Initialization.py` | 변경 없음(BMS 통신 판정은 기존 유지). 인접 보상 유지 | L03 |
| `SF Control.py` | N01, N04(정지 상태 반영, PICV 대기 Timeout, 모드값 검증, RAT/SAT 고장 시 고정속도). Backup 유지 | L01, L02 |
| `PICV Control.py` | N04(정지 상태 반영, Command=1·팬 정지 시 처리). Backup SAT SP 보정 유지 | 없음 |
| `Remote Shutdown.py` | N03(화재/연기 동작 선택, `Shutdown Active` 산출, 기존 강제출력 조건을 통합 정지로 확장) | |
| `Alarm-1.py` | N02(팬별 Run Fail), 유량계 통신 고장 시 유량 진단 억제 | |
| `Alarm-2.py` | 변경 없음(2차에서 누수·냉수 센서) | |
| `Alarm-3.py` | N05(ATS·유량계 통신 고장) | |
| `Failover.py` | 변경 없음(자동 정지 유지, L12 철회) | L04(주석만) |

### 8.2 쓰기 책임과 실행 순서

| 구분 | 주 쓰기 담당 | 주 소비자 |
| --- | --- | --- |
| 팬·ATS·유량계 통신 상태 | Alarm-3 | Initialization, Alarm-1 |
| BMS 통신 상태, 센서 집계, SF Status, Local/Remote 명령 | Initialization | 전체 |
| 화재/연기 확인, `Shutdown Active` | Remote Shutdown | PICV/SF Control |
| 밸브 출력 | PICV Control | 실제 밸브 |
| 팬 Speed Value, Run Command, RPM/AO, Last Valid 속도 | SF Control | 실제 팬, HMI/BMS |
| 장치 알람 | Alarm-1/2 | HMI/BMS, Failover |

현재 등록 순서에서는 Alarm-3가 Initialization 뒤에 있어 팬 통신 고장이 1스캔 늦게 반영되고, Remote Shutdown이 SF/PICV 뒤에 있어 정지 상태도 1스캔 늦다. X01 순서로 바꾼다.

### 8.3 타이머 배분 (파일당 0~9)

| 파일 | 현재 | 변경 후 |
| --- | --- | --- |
| Initialization | 5, 6, 7 | 동일 |
| SF Control | 1 | 1, **2(PICV 닫힘 대기 Timeout)** |
| PICV Control | 없음 | 없음 |
| Remote Shutdown | 없음 | **0(화재/연기 입력 확인)** |
| Alarm-1 | 0~9 전부 | 동일(N02는 기존 1번 공유) |
| Alarm-2 | 0~7 | 동일. 8·9는 2차(누수, 냉수 센서) 예약 |
| Alarm-3 | 0~7 | 0~7, **8(ATS 통신), 9(유량계 통신)** |
| Failover | 1, 2 | 동일 |

이전 판 §7.3 배분안은 기존 Alarm-1의 SF Failure 60 s와 SAF 센서 고장 타이머 배치가 빠져 있었다. rev.2는 Alarm-1 배치를 바꾸지 않는다.

## 9. 추가 로직의 동작 원칙

### 9.1 BMS 통신 두절 대응 (N01)

| 상황 | 동작 |
| --- | --- |
| 정상(Comm Fault 0), 자동, Command 1, SAD 전부 열림, 정지 상태 아님 | 기존 모드대로 제어. 적용 속도 > 0이면 `Last Valid SF Speed`에 저장 |
| 두절 + HOLD_LAST | `Last Valid SF Speed` 적용. 저장값이 없으면(0) Speed Max 적용(K05). PI 누적값 초기화 |
| 두절 + MAX | Speed Max 적용. PI 누적값 초기화 |
| 두절 중 | `Last Valid` 갱신 중지, `BMS Fallback Active = 1` |
| 비상, 원격 정지, 연기 SHUTDOWN, Command 0, 수동 | 정지·수동이 우선. Fallback으로 새로 기동하지 않음 |
| 정상 PV 무효(BMS 정상, CZT/RDP 센서 전부 고장) | 기존대로 `Speed SP` 고정 운전 유지 |
| 복구 | 기존 래치 유지: 운전자 Reset 후 정상 제어 복귀(C05, K16) |

- 적용 범위는 자동 운전의 모든 제어 모드, Local/Remote 무관을 권고한다(K04).
- `Last Valid SF Speed`는 `backupEnable=1`로 두어 DDC 이중화 절체 후에도 HOLD_LAST가 유지되게 한다.
- 팬 Modbus 통신 고장(AO 전환)과 BMS 통신 고장은 별개로 유지한다.

### 9.2 화재/연기 검출 (N03)

| 상태 | 동작 |
| --- | --- |
| `FWU_FIRE ALARM` 입력 확인(지연 후) | `VP_FWU_Fire Alarm = 1` |
| CONTINUE(기본) | 알람만. 운전 유지(현재 동작과 동일) |
| SHUTDOWN | 원격 정지와 같은 강제 정지(P2), Command 0(P11). 수동/자동·로컬/원격 무관 |
| 해소 | P2 해제. Command는 0으로 남아 운전자가 재기동(원격 정지와 동일) |

- `FWU_EMERGENCY`와 별개로 처리한다.
- 누수는 이 정지 경로에 넣지 않는다(H01).

### 9.3 팬별 운전실패 (N02, H02)

1. 기존 조건(Command 1, Speed Value ≥ Speed Min, 60 s 경과)에서 팬별 판정 결과를 `VP_FWU_SF-n Run Fail Alarm`에 기록한다.
2. 조건 해제 시 8개 모두 0.
3. 종합 `SF Failure Alarm`(4대 이상)은 그대로 유지한다.
4. 2차에서 풍량 스위치가 들어오면 판정식에 `풍량 미확인`을 OR로 추가한다.
5. 통신 고장 팬은 기존과 같이 공통 DP로 추정하며, 풍량 스위치 설치 후에는 스위치를 우선한다.

## 10. 기존 결함·모호점과 처리 단계

| ID | 위치 | 내용 | 처리 |
| --- | --- | --- | --- |
| C01 | `Remote Shutdown.py:17–32`; `SF Control.py:214–231` | 원격 정지 중 Speed Value는 P11만 0. BMS/HMI가 Command를 P11보다 높은 우선순위로 쓰거나 수동 모드이면 Speed Value > 0이 남아 Run Command 1 유지 | **1차(N04)**: Run Command는 `Speed Value > 0` 그리고 정지 상태·비상이 아닐 때만 1. 자동에서 정지 상태면 Speed Value 0 |
| C02 | `SF Control.py:242` | 일반 속도 출력 5 s 주기 | 정지는 P1/P2 강제출력이 즉시 처리하므로 유지 |
| C03 | `SF Control.py:168` | PICV 피드백 < 5 % 무한 대기 | **1차(N04)**: Timeout(제안 60 s, K09) 후 팬 정지 진행 |
| C04 | `PICV Control.py:44–56` | Command 1·SF Status 0이면 밸브 지령 없음 | **1차(N04, K08)**: 0 % 및 PI 초기화 제안 |
| C05 | `Initialization.py:49–64` | Reset 허용 범위가 주석보다 넓음, 래치 유지 | 결정(K16). 1차 변경 없음 |
| C06 | `SF Control.py:54–61` | 0~4 외 모드값이면 이전 속도 유지 | **1차(N04)**: 고정속도 전환 |
| C07 | `Alarm-2.py:84` | RDP ≤ 0을 고장으로 판정 | 결정(K12) |
| C08 | `SF Control.py:117–138` | RAT/ΔT 모드에서 센서 고장 대응 없음 | **1차(N04)**: RAT 고장(모드 1), RAT·SAT 고장(모드 3) 시 고정속도 |
| C09 | `Initialization.py:288–361` | 통신 고장 팬을 공통 DP로 추정 | 2차(H02) |
| C10 | `SF Control.py:160` | SAD 이동 중 이전 속도 유지 | 유지(SAD Not Open 알람 120 s로 감시) |
| C11 | `SF Control.py:245–246`; `Initialization.py:390` | 1920 rpm 고정, Min/Max 정합성 검사 없음 | 결정 시 반영 |
| C12 | `Alarm-1.py:352–379` | 유량 진단에 품질 확인 없음 | **1차(N05)**: 유량계 통신 고장 시 유량 기반 판정 억제 |
| C13 | `Initialization.py` 집계부 | 무효 시 0 기록 | `PV Valid`와 함께 사용 중이므로 유지 |
| C14 | `Alarm-3.py` 주석 / `DDC.xml` | Alarm-3를 Initialization 앞에 등록하라는 주석과 실제 순서 불일치 | **X01** |
| C15 | `Initialization.py:380–387`(Local/Remote) | Command 우선순위 P5 해제 후 P11 기록. BMS 쓰기 우선순위에 따라 정지 무효화 가능 | BMS 쓰기 우선순위 확인 |

## 11. LDPL 규칙과 주의점 (이전 검토 인용)

| 근거 | 규칙 | 적용 |
| --- | --- | --- |
| §8 | 첫 줄 `engine = ddc_logic()`, 들여쓰기 규칙 | 기존 형식 유지 |
| §6.2 | `SECTIMER(index, option)`, 0~9 | §8.3 배분 준수 |
| §6.1 | `WAIT`는 파일 전체를 멈춤 | 사용하지 않음 |
| §7.3~7.4 | `LOOP2`, `LOOP2_INIT` | Fallback·정지·고정 전환 시 PI 초기화 |
| §4.2~4.3 | 기본 우선순위 5, 1~16 지정·해제 | P1(비상)/P2(원격·연기 정지)/P5(제어)/P11(유지값) 소유자 유지 |
| §4.10 | 경보값 8 = 통신 경보 | ATS·유량계 통신 감시도 `READPOINT_ALARM == 8` 패턴 사용 |

## 12. 코드 작성 전에 확정할 결정

| ID | 우선 | 결정 항목 | 권고(코드 기본값) |
| --- | --- | --- | --- |
| K01 | P0 | Failover 자동 정지 | **확정: 현행 유지(L12 철회).** DoO "FWU Failover Criteria" 확인은 계속 필요. 팬 4대 이상 고장 시 남은 팬까지 정지하며 `Failover Alarm`이 BMS에 보이지 않던 점은 X02로 해소 |
| K02 | P0 | Backup 운전 경로 | **확정: 유지, BMS PLC 연동.** 주소표 추가(X02) |
| K03 | P0 | 인접 보상 | **확정: 유지.** 주소표 추가(X02) |
| K04 | P0 | BMS 두절 대응 적용 범위 | 자동 운전 전 모드, Local/Remote 무관 |
| K05 | P0 | 저장 속도 없을 때 | Speed Max |
| K06 | P0 | Heartbeat 쓰기 경로 | BMS 주소표 HR 추가 |
| K07 | P0 | `FWU_FIRE ALARM` 의미·극성 | 환기부 연기검출기로 가정, 기본 CONTINUE |
| K08 | P1 | Command 1·팬 정지 시 밸브 | 0 % + PI 초기화 |
| K09 | P1 | PICV 닫힘 대기 Timeout | 60 s 후 팬 정지 진행 |
| K10 | P1 | Speed Min 기본값 | 20 % 검토(팬 보증 범위 확인) |
| K11 | P0 | ATS 쓰기 Point의 BMS 노출 | 읽기 전용 전환 권고 |
| K12 | P2 | RDP ≤ 0 고장 판정 | 센서 범위 확인 후 결정 |
| K13 | P0 | 2차 입력 14~15점 수용 방법 | I/O 확장 또는 통신 취득 |
| K14 | P0 | BMS Point List V1.3 | 확보 후 주소표 대조 |
| K15 | P2 | 주소표 고아 항목 | 승인 후 정리 |
| K16 | P2 | BMS 통신 고장 래치·복구 | 현행 유지 |
| K17 | P0 | BMS PLC 연동 사양 | (a) Backup Operation 해제 책임: BMS PLC가 직접 0으로 되돌림, BMS 두절 시 1이 남으면 팬 최대 유지(현행 동작, 냉방 측으로 안전). (b) N01 두절 대응과 Backup이 겹치면 Backup(최대속도)을 우선. (c) 이웃 Adj 값의 갱신 주기·단위·범위(CZT < 0, RDP ≤ 0은 무시됨). (d) Modbus 주소 배정과 쓰기 우선순위 |

## 13. 수정 후 검증할 동작

| 시험 | 상황 | 확인 결과 |
| --- | --- | --- |
| T01 | BMS가 Speed SP 쓰기(고정 모드) | 적용 속도·RPM/AO 일치 |
| T02 | 62 % 운전, Speed SP 40 %, BMS 두절, HOLD_LAST | 62 % 유지, Fallback Active 1 |
| T03 | 같은 조건, MAX | Speed Max 적용 |
| T04 | 전원 투입 직후 BMS 없음 | Speed Max 적용 |
| T05 | BMS 두절 + 원격 정지/비상/연기 SHUTDOWN | 정지 우선, Run Command 0 |
| T06 | DDC 이중화 절체 중 BMS 두절 | 절체 후에도 직전 속도 유지 |
| T07 | Heartbeat를 BMS가 Modbus로 갱신 | Comm Fault 미발생 |
| T08 | 팬 1대 RPM 미달 | 해당 팬 Run Fail Alarm만 1, 종합 알람 0 |
| T09 | 화재 입력, CONTINUE / SHUTDOWN | 알람만 / 강제 정지. 해소 후 운전자 재기동 |
| T10 | 원격 정지 중 수동 모드에서 속도 입력 | Run Command 0 유지 |
| T11 | 정지 명령 후 PICV 피드백 미복귀 | Timeout 후 팬 정지 |
| T12 | 모드값 7, RAT 센서 고장(모드 1) | 고정속도 전환 |
| T13 | 유량계 통신 단절 | Flow Comm Fault 1, PICV 유량 오경보 없음 |
| T14 | ATS 통신 단절 | ATS Comm Fault 1 |
| T15 | BMS PLC 연동(주소표 추가 후) | BMS PLC가 Backup Operation 1 → 팬 Speed Max, `SAT SP Active` = SAT SP − 0.5. 0으로 해제 시 복귀. 이 FWU `Failover Alarm` 1이면 Backup 무시 |
| T15a | 이웃 Adj 값 쓰기, Weight 70 % | CZT 이웃 > SP 일 때 `CZT Comp PV` 상승, Weight 0이면 보상 없음 |
| T15b | 팬 4대 이상 고장(5 s 지속) | `Failover Alarm` 1, Command 0(현행 동작). BMS에서 `Failover Alarm` 읽힘 |
| T16 | 전체 실행 | 미등록 Point 참조 오류 없음, 기존 BMS 주소 값 정상 |

## 14. 진행 순서

1. **결정 확정:** §12 K04~K11, K17의 P0/P1 항목 확인. (K01~K03은 확정)
2. **1차 코드 수정:** 경량화 L01~L04, 추가 N01~N05, 결함 C01·C03·C04·C06·C08·C12. Backup·Failover·인접 보상 코드는 변경하지 않는다.
3. **설정 반영:** 신규 Point 7개 등록(X04), DDC 실행 순서(X01), BMS 주소표 추가(X02), 알람 속성(X03).
4. **ATS 쓰기 권한(X06)과 프로토콜(X05)** 결정·반영.
5. **2차:** I/O 증설 방안 확정 후 H01~H05 구현.
6. **FAT:** §13 시험.

---

**수정 범위의 핵심:** Point는 하나도 지우지 않고, 현장 맞춤 기능(Backup, Failover, 인접 보상)은 BMS PLC 연동을 위해 유지하며 주소표만 연결한다. QTS가 요구하는 BMS 두절 대응·팬별 고장·연기 동작 선택은 기존 Point와 최소 신규 Point로 추가하고, 하드웨어가 필요한 항목은 I/O 확정 후 2차로 진행한다.
