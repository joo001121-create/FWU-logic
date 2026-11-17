# FWU v2 — F8 검토용 코드

세 제어 블록과 필요한 연계 로직을 작성했다. **실장용 통신·IO 연결은 미완성이며, 현재 파일을 그대로 장비에 다운로드하는 단계는 아니다.**

기준: `joo001121-create/FWU-logic`, `jh`, `a017e7f1fe52ede6e510cee8c66d1125f07bd8b6`.

먼저 [IMPLEMENTATION.md](IMPLEMENTATION.md)를 읽는다. 반영 내용과 실제 장비 적용 전에 남은 일이 정리돼 있다.

- [CONTROL_DECISIONS.md](CONTROL_DECISIONS.md): 코드 작성 전 합의 원본. 문서에 쓰인 미구현 상태는 작성 당시의 기록이다.
- [INTEGRATION.md](INTEGRATION.md): 벨리모 수신 연결, 통신맵, HMI·현장 설정 조건
- [WORK_LOG.md](WORK_LOG.md): 작업 이력과 검증 범위
- [POINTS_ADDED.csv](POINTS_ADDED.csv): 추가된 관제점 111개의 이름·ID·기본값
- [STATIC_CHECKS.json](STATIC_CHECKS.json), [TEST_RESULTS.txt](TEST_RESULTS.txt): 정적 검사와 모의시험 결과
- [CHANGES.diff](CHANGES.diff): v1 대비 실행 코드·XML 차이
- [SOURCE_HEADERS.md](SOURCE_HEADERS.md): 기존 코드 주석 이력 보존

`Logic`에는 기존 8개와 보조 5개로 총 13개 블록이 있다. `DDC.xml`에 등록했지만 실제 도구에서 블록 추가·ID·실행 순서를 검증해야 한다. 물리 IO와 팬/ATS/유량계의 기존 통신 설정은 원본을 보존했다. 새 HW의 완성된 맵이 아니다.

PC 모의시험: `python -m unittest discover -s fwu_v2/tests -v`

현재 GitHub 앱 쓰기가 거절되는 상태이므로 ZIP으로 전달한다. PC에서 기존 저장소의 `jh`에 이 폴더를 추가하고, diff 검토 후 일반 커밋·푸시한다. 기존 `FWU_v1`과 SMX01 폴더를 덮어쓰지 않는다.
