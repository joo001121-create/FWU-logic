# FWU v2 LDPL 재검토 수정안

기준 커밋: `0e0a374d983bf194220e75da79b28598673bc0fa` (`FWU-logic/jh`)

**13개 제어 코드가 모두 들어 있다. 변경한 코드는 PICV Feedback 하나이며, 나머지 12개는 코드·주석을 그대로 유지했다.**

PICV의 별도 수신 어댑터 가정을 없애고 DDC 통신 관제점의 값·알람 상태를 읽도록 수정했다. 블록 추가는 없다. XML의 기존 관제점 ID와 설정은 바꾸지 않았다.

먼저 `LDPL_REVIEW.md`를 읽는다. 수정 코드, 실제 통신점 등록 목록, 확인되지 않은 기능과 회사 PC 시험 항목을 구분해 정리했다.

| 파일 | 용도 |
|---|---|
| `Logic/` | 제어 코드 13개 |
| `LDPL_REVIEW.md` | 13개 검토 결과, 수정 이유, 남은 판단 항목 |
| `PICV_POINT_MAPPING.csv` | CH3에 등록할 입력점 12개. 주소·레지스터는 미확정 |
| `INTEGRATION.md` | 수정안 기준 연결·설정 방법 |
| `LDPL_REPAIR.diff` | PICV Feedback의 실제 코드 변경분 |
| `explanations/` | 해석 MD 13개. PICV Feedback 해석을 수정 코드에 맞춰 갱신 |
| `tests/` | PC용 모의시험 및 정적 검사. DDC에 등록하지 않음 |
| `STATIC_CHECKS.json`, `TEST_RESULTS.txt` | 이번 검사 결과 |
| `SOURCE_LOGIC_SHA256.json` | 수정 전 13개 코드의 해시 |
| `WORK_LOG.md` | 변경·검증·미검증 이력 |
| `audit_history/` | 이전 버전의 검사 결과와 diff. 이번 결과가 아님 |

**장비에 바로 넣는 최종 실장본은 아니다.** PICV 실제 통신점 12개와 기존 누수 입력을 등록해야 하며, 팬/ATS 포트와 AO3 환산 등 기존 연결 작업도 남아 있다. 특히 DDC 재시작 후 첫 응답 전 정상 표시 여부와 SF 모드별 LOOP2 ID 동작은 아직 검증하지 못했다.

이전 문서의 수신 어댑터·Input_OK·Sample_Seq 의존 설명은 이번 수정안에 적용하지 않는다. 그 점들은 XML에 남아 있어도 사용하지 않는다. `VP_FWU_PICV_Input_Enable`은 실제 통신점 등록과 확인 후에만 1로 설정한다.

PC 검사 명령:

```bash
python -m unittest discover -s tests -v
python tests/validate_project.py
```

검사는 코드 분기와 참조를 확인한다. 실제 LDPL 컴파일, 통신, 배선, PI 성능을 대신하지 않는다.
