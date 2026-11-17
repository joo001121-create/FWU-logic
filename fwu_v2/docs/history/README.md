> **2026-11-17 LDPL 재검토 수정안:** 먼저 [README_LDPL_REPAIR.md](README_LDPL_REPAIR.md)와 [LDPL_REVIEW.md](LDPL_REVIEW.md)를 읽는다. PICV Feedback만 수정했으며 새 샘플 순번 방식은 사용하지 않는다. 아래 내용은 이전 개발 범위 안내다.

# FWU v2 — 후속 알람·정지 리뷰 반영본

2026-11-17. 이전 v2 전체 폴더에 Alarm-1/2/3, Remote Shutdown, Failover 합의와 관제점 명칭 정리를 반영했다. 기존 Initialize·SF·PICV 및 보조 블록을 포함한 **전체본**이다. 코드 블록은 **13개로 그대로**다.

**검토용 코드이며 실제 장비 다운로드 전 통신·IO 연결과 DDC 시험이 필요하다.** 팬·ATS·PICV의 새 포트 배치, Belimo 실제 통신점 등록, AO3 배율, 누수 DI 등은 아직 실장 완료 상태가 아니다.

## 먼저 볼 파일

1. [DELIVERY_NOTES.md](DELIVERY_NOTES.md): 이번 변경, PC 적용 순서, 검증 범위
2. [REVIEW_DECISIONS_ALARMS_SHUTDOWN_FAILOVER.md](REVIEW_DECISIONS_ALARMS_SHUTDOWN_FAILOVER.md): 후속 다섯 블록 합의서
3. [POINT_RENAME_MAP.csv](POINT_RENAME_MAP.csv): 공백 관제점 구명칭→신명칭, 기존 ID·주소
4. [INTEGRATION.md](INTEGRATION.md): 실제 통신·IO 연결 및 HMI 조건

기존 [CONTROL_DECISIONS.md](CONTROL_DECISIONS.md)는 최초 세 블록 합의 원본이다. 과거 이름과 작성 당시 상태를 보존했으며, 현재 이름은 대응표와 실행 코드가 기준이다. [SOURCE_HEADERS.md](SOURCE_HEADERS.md)는 기존 작성 이력 보관용으로 현재 동작 설명과 구분한다.

[IMPLEMENTATION.md](IMPLEMENTATION.md), [WORK_LOG.md](WORK_LOG.md)에 구현 및 작업 이력을 기록했다. [POINTS_ADDED.csv](POINTS_ADDED.csv)는 최초 v2에서 추가한 111개 점의 현재 명칭이다. 이번 후속 수정에서는 관제점을 추가하지 않았다.

## PC에서 검사

Python 3 환경에서 `fwu_v2` 폴더의 상위 폴더를 열고 실행한다. 추가 패키지는 필요 없다.

```sh
python -m unittest discover -s fwu_v2/tests -v
python fwu_v2/tests/validate_project.py
```

- [TEST_RESULTS.txt](TEST_RESULTS.txt): 모의시험 27개 결과
- [STATIC_CHECKS.json](STATIC_CHECKS.json): 구문·관제점·타이머·등록 정적 검사
- [CHANGES.diff](CHANGES.diff): 기준 v1 대비 코드·XML 누적 차이
- [FOLLOWUP_CHANGES.diff](FOLLOWUP_CHANGES.diff): 이전 전달 ZIP 대비 코드·XML 차이
- [PACKAGE_SHA256.json](PACKAGE_SHA256.json): 이 파일 자체를 제외한 패키지 파일 체크섬

비교 기준 v1: `joo001121-create/FWU-logic`, `jh`, `a017e7f1fe52ede6e510cee8c66d1125f07bd8b6`. 최신 원격 커밋을 새로 내려받은 결과물이 아니라 이전 전달본의 후속 수정본이다. 원격 저장소에 커밋·푸시하지 않았다.
