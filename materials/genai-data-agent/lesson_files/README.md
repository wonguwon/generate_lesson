# 차시별 실습 파일

교안의 실습 재료는 텍스트 블록 대신 파일로 나눠 줍니다. 지난 시간을 따라오지 못한 학습자를 위한 시작 파일도 차시마다 있습니다. 데이터는 모두 가상입니다.

- 재료 파일(`01/` ~ `10/`): 노션 교안 토글의 재료 부분을 글자 그대로 옮긴 것. 요청 문장은 교안에 그대로 있습니다.
- 시작 파일(`start/`): 앞 차시까지 마친 상태의 결과물. `_tools/make_start_files.py`로 만들고, 숫자는 교안의 확인할 것과 같습니다.
- 인코딩: 모두 UTF-8. CSV는 BOM 있음(엑셀에서 바로 열림), md·txt는 BOM 없음. 시작 zip 안의 `시작파일_안내.txt`만 메모장용으로 BOM·CRLF.

## 차시별로 올릴 파일

`data/`·`skill/`은 과정 자료 폴더(`materials/genai-data-agent/`)의 기존 파일입니다.

| 차시 | 올릴 파일 |
| --- | --- |
| 1 생성형 AI와 데이터 분석 | `data/orders_2025_w01-12.csv`, `lesson_files/01/orders_앞20행.txt` |
| 2 데이터 탐색과 전처리 | `data/orders_2025_w01-12.csv`, `data/data_dictionary.md`, `lesson_files/02/정제규칙.md` |
| 3 분석 질문과 집계·비교 분석 | `data/data_dictionary.md`, `lesson_files/start/03_정제파일/orders_2025_w01-12_clean.csv` |
| 4 리뷰 텍스트 분류와 분석 결과 시트 | `data/data_dictionary.md`, `data/reviews_sample_200.csv`, `lesson_files/04/리뷰기준표_처음.md`, `lesson_files/04/리뷰기준표_더할규칙.md`, `lesson_files/04/결과시트_구성.md`, `lesson_files/start/03_정제파일/orders_2025_w01-12_clean.csv` |
| 5 HTML 대시보드 만들기 | `data/dashboard_sketch.md`, `lesson_files/05/대시보드_규칙.md`, `lesson_files/start/05_결과시트/analysis_summary.xlsx` |
| 6 에이전트와 작업 모드 | `data/orders_2025_w01-12.csv`, `data/data_dictionary.md`, `data/dashboard_sketch.md`, `lesson_files/02/정제규칙.md`, `lesson_files/04/결과시트_구성.md`, `lesson_files/05/대시보드_규칙.md`, `lesson_files/start/04_리뷰기준표/리뷰기준표.md`, `lesson_files/start/05_결과시트/analysis_summary.xlsx`, `lesson_files/start/06_대시보드/index.html` |
| 7 커넥터로 새 데이터 가져오기 | `data/orders_2025_w13.csv`, `lesson_files/start/07차시_시작_배달주문_실습.zip`, `lesson_files/02/정제규칙.md` |
| 8 스킬로 갱신 절차 묶기 | `data/orders_2025_w14.csv`, `skill/weekly-order-update/SKILL.md`, `lesson_files/start/08차시_시작_배달주문_실습.zip` |
| 9 서브에이전트로 나눠 처리하기 | `data/orders_2025_w15.csv`, `lesson_files/09/스킬_고칠내용.md`, `skill/8차시_완성본/weekly-order-update/SKILL.md`, `skill/9차시_완성본/weekly-order-update/SKILL.md`, `lesson_files/start/09차시_시작_배달주문_실습.zip` |
| 10 Sites 배포와 예약 작업 | `data/orders_2025_w16.csv`, `lesson_files/10/예약요청문.txt`, `lesson_files/start/10차시_시작_배달주문_실습.zip` |

## 재료 파일

| 파일 | 차시 | 설명 |
| --- | --- | --- |
| `01/orders_앞20행.txt` | 1 | 기본 파일의 머리글과 주문 20행(원본 CSV 1~21줄 글자 그대로). 실습 1에서 통째로 복사해 붙여 넣음 |
| `02/정제규칙.md` | 2·6·7 | 정제 규칙 1~10. 2차시 실습 3, 6차시 위임 요청 [1. 정제], 7차시 가져오기·누적 요청 [2. 정제]에 같은 글로 들어감 |
| `04/리뷰기준표_처음.md` | 4 | 리뷰 분류 기준표 [감성]·[주제]·[예시]. 실습 1 |
| `04/리뷰기준표_더할규칙.md` | 4 | 표본 검수 뒤 기준표에 더할 규칙 1~5와 예시. 실습 2 ③ |
| `04/결과시트_구성.md` | 4·6 | 분석 결과 시트 8개(기준~리뷰표본)의 정의. 실습 3 |
| `05/대시보드_규칙.md` | 5·6 | 대시보드 요청의 [숫자]·[화면] 규칙. 실습 1 |
| `09/스킬_고칠내용.md` | 9 | 스킬에서 바꾸는 기준 파일 줄과 새 절차 6~11. 실습 3 |
| `10/예약요청문.txt` | 10 | 예약 요청문 전체(갱신 → 다시 게시 → 실행 보고). 실습 2 |

## 시작 파일

| 파일 | 차시 | 설명 |
| --- | --- | --- |
| `start/03_정제파일/orders_2025_w01-12_clean.csv` | 3·4 | 2차시 정제 결과. 4,426행 · 18열, 완료 4,193건 · 매출 90,182,000원 |
| `start/04_리뷰기준표/리뷰기준표.md` | 6 | 4차시 결과. 처음 기준표에 더한 규칙 1~5를 합친 것 |
| `start/05_결과시트/analysis_summary.xlsx` | 5·6 | 4차시 결과 시트 8개. 리뷰 라벨은 자료에서 정한 값(표본 200개, 맛 79 · 배달 38 · 양 32 · 가격 23 · 기타 15 · 포장 13) |
| `start/06_대시보드/index.html` | 6 | 5차시 결과 대시보드(차트 3을 누적 막대로 고친 뒤). 파일 하나, 인터넷에서 불러오는 것 없음 |
| `start/07_드라이브시작/배달주문_실습/` | 7 | 7차시 드라이브에 올릴 폴더(아래 zip을 푼 것과 같음). 빈 `수신/` 폴더는 git에 남지 않으니 zip을 씀 |
| `start/07차시_시작_배달주문_실습.zip` | 7 | 6차시까지 마친 상태: 누적(1~12주 정제 파일) · 결과(xlsx·html) · 기준(파일 4개) · 빈 수신 |
| `start/08차시_시작_배달주문_실습.zip` | 8 | 7차시까지: 13주차 누적 4,790행, 처리기록.md(13주차), 결과 13주차 반영, 수신에 w13 |
| `start/09차시_시작_배달주문_실습.zip` | 9 | 8차시까지: 14주차 누적 5,155행(규칙 11 적용), 처리기록.md(13·14주차), 수신에 w13·w14 |
| `start/10차시_시작_배달주문_실습.zip` | 10 | 9차시까지: 15주차 누적 5,521행, 결과 시트 9개(리뷰전체 1,405행), 출처 줄을 고친 스케치, 수신에 w13~w15 |

zip은 맨 위에 `시작파일_안내.txt`와 `배달주문_실습/` 폴더가 있습니다. 드라이브에는 `배달주문_실습/` 폴더만 올립니다.

- 기준 폴더(`정제규칙.md` · `data_dictionary.md` · `리뷰기준표.md` · `dashboard_sketch.md`)는 교안보다 이르게 7차시 시작 파일부터 넣었습니다.
- 처리기록.md의 처리한 날은 주차가 끝난 다음 월요일(13주차 2025-06-02, 14주차 06-09, 15주차 06-16)로 정한 값입니다.
- 리뷰 라벨은 `_tools/reviews_sample_200_answer.csv`(표본)·`_tools/answer_key.csv`(전체)의 정답을 씁니다. 직접 분류한 결과와 조금 다를 수 있다는 것을 각 zip의 안내 파일에 적었습니다.

## 다시 만들기

```bash
_tools/.venv/Scripts/python.exe -m pip install -r _tools/requirements.txt
_tools/.venv/Scripts/python.exe _tools/make_start_files.py
```

- `data/`의 CSV와 `lesson_files/02`·`04`의 재료 파일을 읽어 `lesson_files/start/`를 새로 씁니다. 재료 파일을 고치면 시작 파일의 기준 폴더도 바뀝니다.
- 만든 파일을 다시 읽어 교안의 확인할 것 숫자와 대조하고, 하나라도 다르면 종료 코드 1로 끝납니다.
- 무작위 요소가 없고 xlsx·zip 안의 시각을 고정해, 같은 패키지 버전이면 몇 번을 실행해도 같은 파일이 나옵니다.
