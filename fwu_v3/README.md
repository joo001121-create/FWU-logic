# FWU v2 전체 프로젝트 교체본

2026-11-17. 코드 기준은 `FWU-logic/jh`의 `0e0a374d983bf194220e75da79b28598673bc0fa`와 이후 전달한 PICV Feedback 수정안이다.

이 폴더에는 ControlPoint, Device, Logic, ProtocolSerivce, ScheduleInfo, DDC.xml이 모두 들어 있다. 해석 MD는 포함하지 않았다. `ProtocolSerivce`는 기존 프로젝트의 폴더명을 그대로 유지한 것이다.

## 반영 내용

| 구성 | 반영 내용 |
|---|---|
| Logic | 이전에 전달한 수정 코드 13개 그대로. 이번에 추가 코드 변경 없음 |
| ControlPoint/VirtualPoint.xml | 사용하지 않는 Input_OK·Sample_Seq·Sample_Prev·Input_Timeout 13점 삭제 |
| ControlPoint/Modbus1.xml | 팬 8대를 확인된 CH1 구성으로 배치. 기존 주소·레지스터·관제점 ID 유지 |
| ControlPoint/Modbus2.xml | ATS를 확인된 CH2 구성으로 이동. 기존 장치 주소·레지스터·관제점 ID 유지 |
| ControlPoint/Modbus3.xml | 구형 단일 유량계 제거. PICV 4대의 실제 통신점 12개와 읽기 요청 12개 추가 |
| ControlPoint/IO.xml | 사용하지 않는 기존 배선식 PICV 피드백 입력을 isUsed=false로 표시. AO3 설정은 임의 변경하지 않음 |
| ProtocolSerivce/Modbus/ModbusServiceInfo.xml | 구형 유량계와 미사용 배선 피드백의 외부 공개 항목 제거. 나머지 공개 주소 유지 |
| DDC.xml | CH3를 PICV 통신 설정안인 38400bps, 8N2로 반영. 기존 13블록 등록·실행 순서 유지 |
| Device·ScheduleInfo·나머지 서비스 XML | 이번 변경의 영향을 받는 참조가 없어 원문 유지 |

## PICV 통신 설정의 근거와 적용 조건

제조사 공식 [EPIV Modbus V4.3.0 통신표](https://www.belimo.com/mam/general-documents/system_integration/Modbus/belimo_Modbus-Register_2way-EPIV_V4_3_0_en-gb.pdf)의 기본 계측 레지스터를 적용했다. 실제 납품품의 펌웨어가 이 표와 일치하는지는 확인이 필요하다.

| 값 | 문서 Register No. | 실제 통신 주소(0부터) | 자료형 | 코드에 들어가는 값 |
|---|---:|---:|---|---|
| 개도 | 5 | 4 | UINT16 | 원시값 × 0.01, % |
| 유량 | 8 | 7 | UINT16 | 원시값 × 0.6, L/min |
| 온도 | 22 | 21 | INT16 | 원시값 × 0.01, ℃ |

밸브 장치 주소 1·2·3·4는 **이번 프로젝트에서 배정한 설치 계획값**이다. 실제 장치에서 읽어 확인한 값이 아니다. 엔지니어가 장치 주소와 통신 설정을 맞춰야 한다. PICV_Input_Enable 기본값 0은 유지했다.

명령은 기존 AO3, 수신은 RS485다. Modbus로 밸브 제어 모드나 명령값을 쓰는 기능은 추가하지 않았다. 밸브는 실제 아날로그 명령을 받도록 설정해야 한다. 온도는 밸브 본체의 유체 온도이므로 냉수 출구 온도로 사용할 설치 위치도 확인한다.

## 교체와 실장 구분

개발 파일은 이 `fwu_v2` 폴더 단위로 교체할 수 있다. 동료가 별도로 편집한 파일이 있다면 먼저 비교한다. **장비에 즉시 다운로드할 최종 시운전 완료본은 아니다.** 아래 확인 항목은 남아 있다.

1. 실제 PICV 모델·펌웨어, 장치 주소 1~4, 38400/8N2 설정 및 읽은 값의 단위 확인.
2. DDC 엔지니어링 도구에서 생성된 통신 주소 문자열·요청·배율을 확인하고 가져오기/컴파일/실행 시험.
3. 기존 미등록 `FWU_LEAK_DETECT`의 실제 DI 주소 등록. 물리 주소를 추정해 넣지 않았다.
4. AO3의 실제 모듈 주소와 2~10V 환산 확인. 기존 XML은 0~10V 설정이므로 그대로 확정값으로 사용하지 않는다. 팬 AO와 새로운 하드웨어 배치도 대조한다.
5. DDC 첫 응답 전 상태, 통신 단절/복구, 재부팅·이중화 절체, 기존 팬 PI 모드 전환 시험.

외부 Modbus 공개 주소는 기존 계약을 보존했다. 새 PICV 값을 어떤 주소로 BMS에 공개할지는 확정된 외부 통신맵에 맞춰 별도로 배정한다. 기존 표시용 VP는 유지했지만, 새 공개 주소를 임의로 추가하지 않았다.

기존 외부 공개맵에는 현재 XML 정의에서 찾을 수 없는 ID 참조 38개가 이미 있었다. 이번 수정 전후 목록은 같다. 시스템 내부점인지 폐기된 점인지 확정할 근거가 없어 삭제하거나 다른 점으로 연결하지 않았다. `INHERITED_EXPORT_REFERENCES.csv`에 기록했으며 DDC 도구에서 확인해야 한다. 설정 검사는 신규 미정의 참조가 늘지 않았음을 확인한 것이고, 이 기존 항목의 정상 동작까지 확인한 것은 아니다.

## 검증 및 파일

- `STATIC_CHECKS.json`: 코드·XML·관제점·타이머·등록 검사.
- `TEST_RESULTS.txt`: 모의 제어 및 설정 시험 결과.
- `PICV_POINT_MAPPING.csv`: 적용한 12점의 주소·자료형·배율.
- `POINT_INVENTORY.csv`: 현재 관제점 목록.
- `RETIRED_POINTS.csv`: 삭제한 VP 13개와 구형 유량계 4개 점.
- `CHANGED_FILES.csv`: 직전 전체 수정안 대비 변경 파일.
- `WORK_LOG.md`: 작업·검증·미검증 이력.
- `docs/history/`: 이전 합의·분석 문서 보존. 현재 연결 상태는 이 README와 검사 결과를 우선한다.

`tests`는 PC에서 실행하는 검사 코드이며 DDC 로직으로 등록하지 않는다.

```bash
python -m unittest discover -s tests -v
python tests/validate_project.py
```
