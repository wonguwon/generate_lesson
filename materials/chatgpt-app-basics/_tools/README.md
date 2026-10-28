# _tools - 실습 자료 제작·검산 스크립트

## 준비

Python 3.10 이상, Windows 권장(영수증 사진 글꼴이 맑은 고딕). Excel은 필요 없습니다.

```
pip install openpyxl xlwt xlrd pillow python-docx python-pptx
```

## 전체 다시 만들기

```
python build_materials.py            # chatgpt-app-basics 아래 01~05 차시 폴더를 지우고 다시 만듦
python check_materials.py            # 만든 파일을 다시 열어 교안 숫자와 대조, 마지막 줄이 "모두 일치"면 정상
```

`build_materials.py`는 `_answer_key`와 `_tools`는 건드리지 않습니다. 씨앗값이 고정돼 있어 몇 번 실행해도 같은 숫자가 나옵니다(파일 수정 날짜만 바뀜). 5차시 시작 자료의 `9월_판매요약.xlsx`에는 수식과 함께 계산 결과 값도 넣어, Excel로 한 번 열어 저장한 상태(4차시 ⑥)와 같게 만듭니다.

## 파일

| 파일 | 하는 일 |
| --- | --- |
| build_materials.py | 01~05 차시 시작 자료 전체. 처음 8개 파일, 앞 차시 결과물(폴더요약.md, 반품요약.md, 이름 변경·형식 변환·통합, 전처리기록.md, 4차시 결과물 6개)을 교안 숫자대로 만듦 |
| make_ilbo.py | 9월 일보 30개 + 영수증 사진 6장 (seed 2126, 교안 3차시 스크립트와 같음). `python make_ilbo.py <폴더>` → `<폴더>/원본/9월_일보`, `원본/영수증` |
| make_ilbo_10.py | 10월 일보 31개 (seed 1031, 교안 5차시 스크립트와 같음). `python make_ilbo_10.py <폴더>` → `<폴더>/원본/10월_일보` |
| 형식변환.py | 출력/9월_일보의 xls 5개 → xlsx, 영수증 6장 → `출력/영수증_9월.pdf`. 4·5차시 자료의 `출력/스크립트`에도 같은 파일이 들어 있음 |
| check_materials.py | 자료 파일 기반 검산 (9월·10월 행 수·합계, 지점별·주차별, 결과물 숫자, 대시보드 외부 주소 등) |
| verify.py, check.py, calc4.py, octcalc.py | 처음 교안 숫자를 정할 때 쓴 계산용 (파일을 읽지 않고 씨앗값으로 다시 계산) |
| check10.py | 폴더 하나의 일보 파일을 직접 읽어 정리 후 숫자를 계산. `python check10.py <10월_일보 폴더>` |

## 차시 폴더와 교안의 대응

| 폴더 | 교안 | 시작 상태 |
| --- | --- | --- |
| 01_codex-agent | Codex와 에이전트 | 파일 8개 (원본/출력 없음) |
| 02_permissions-git | 권한과 변경 관리 | 원본 8 + 출력/폴더요약.md |
| 03_batch-files | 여러 파일 한 번에 | + 출력/반품요약.md, 폴더요약.md 제목 변경 / 프로젝트 밖 `9월_일보`, `영수증` |
| 04_outputs-edit | 결과물 만들고 직접 고치기 | 3차시 결과 전체 |
| 05_agents-skills | AGENTS.md와 스킬 | 4차시 결과 전체 / 프로젝트 밖 `10월_일보` |

`.git`, `AGENTS.md`, 스킬(`SKILL.md`), 10월 결과물은 수업 중에 Codex가 만드는 것이라 넣지 않았습니다.
