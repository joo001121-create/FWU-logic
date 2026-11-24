# 해설 문서 생성 스크립트

`explain_v4.py`는 `fwu_v3/Logic`의 로직 14개를 한 줄씩 읽어 `code_explanations/fwu_v3/*해석.md` 줄별 해설을 자동으로 만든다. 코드는 읽기만 하고 고치지 않는다.

## 실행

저장소 맨 위 폴더에서:

```bash
python code_explanations/tools/explain_v4.py
```

코드를 고친 뒤 다시 돌리면 행 번호와 설명이 새 코드에 맞게 다시 만들어진다. 다른 폴더를 읽거나 다른 곳에 저장하려면 `python code_explanations/tools/explain_v4.py <로직 폴더> <출력 폴더> "<기준 표시 문구>"`.

## 새 관제점·변수·파일이 생기면

| 생긴 것 | 스크립트에서 추가할 곳 |
|---|---|
| 새 관제점 | `SINGLE`(쉬운 이름). 0/1 값이면 `BIN_MEANING`(0과 1의 뜻)도 |
| 새 변수 | `VARDESC`(변수 뜻) |
| 새 로직 파일 | 맨 아래 `ORDER`(문서를 만들 파일 목록)와 `INTRO`(파일 소개 문단) |

모르는 관제점이 나오면 `KeyError: '관제점 이름'`으로 멈추므로 그 이름을 `SINGLE`에 넣으면 된다.
