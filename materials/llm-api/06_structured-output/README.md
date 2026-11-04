# 구조화 출력과 강의평 분석기 - 실습 파일 (6차시)

교안: [6️⃣ API6 : 구조화 출력과 강의평 분석기](https://app.notion.com/p/1c6435fcbd9d8211b73581df46713e91)

교안의 코드는 모두 **프로젝트 맨 위 폴더**(`llm-api`)에서 실행한다고 가정합니다(VS Code 실행 버튼, `streamlit run 06_structured-output/app.py`).
그래서 `reviews.csv`는 `06_structured-output` 안이 아니라 프로젝트 맨 위의 공용 `data` 폴더에 있습니다.

## 파일

코드 파일은 교안 코드 블록을 단계 순서대로 이어 붙인 **마지막 상태**입니다. 변수 이름·프롬프트·클래스·print 줄은 교안과 같습니다.

| 파일 | 쓰는 곳 | 내용 |
| --- | --- | --- |
| ../data/reviews.csv | 실습 4 ① (앱이 `pd.read_csv("data/reviews.csv")`로 읽음) | 교안 토글 "reviews.csv 원문" 그대로. 강의명·강의평 두 열, 강의 6개 × 4건 = 24행. UTF-8(BOM 없음) |
| 실습1_JSON요청.py | 실습 1 | ③까지 반영한 상태(prompt가 "코드 블록 없이 JSON만 줘"). ② 시연은 prompt 줄을 `f"다음 강의평을 분석해서 JSON으로 줘.\n\n{REVIEW}"`로 돌려서 |
| 실습2_스키마.py | 실습 2 | ①②③ 전부. ReviewAnalysis(str·str·int·list[str]) → response_format → model_validate_json |
| 실습3_열거형.py | 실습 3 | ①②③ 전부. Literal 감성·Field 범위·설명, analyze 함수, 애매한 평 3건, 틀린 JSON 검사 |
| app.py | 실습 4 | 강의평 분석기. 슬라이더로 건수, 진행 막대, st.dataframe, 감성 st.bar_chart, 429면 멈추고 받은 데까지 표시 |

실습 1~3은 교안 코드에 강의평이 들어 있어 따로 쓰는 데이터 파일이 없습니다. 시작 파일도 없습니다(교안이 새 파일을 만들게 함).

## 실행

`llm-api` 폴더에서 실행합니다.

```bash
python 06_structured-output/실습1_JSON요청.py
```

```bash
streamlit run 06_structured-output/app.py
```

실습 2·3도 `python 06_structured-output/파일이름.py`로 실행합니다.

## 정답 요약

실제 API 키로는 아직 돌려 보지 않았습니다. 아래는 교안 정답 표와 자료로 정해지는 값이고, 모델 답(감성·점수·키워드 표현)은 실행마다 달라질 수 있습니다.

| 확인할 것 | 정답(예상) |
| --- | --- |
| 실습 1 ② | 코드 블록 표시로 시작하는 답이 많고, 그런 답은 `파싱 실패: Expecting value: line 1 column 1 (char 0)`. 세 답의 키 이름이 다를 수 있음 |
| 실습 2 ① | properties에 course·sentiment·score·keywords, score `integer`, keywords `array`, required 네 칸 |
| 실습 2 ③ | 강의명 데이터베이스, 키워드는 문자열 리스트, 감성·점수 표현은 실행마다 다를 수 있음 |
| 실습 3 ① | sentiment `enum ['긍정','부정','중립']`, score `minimum 1`·`maximum 5`, keywords `maxItems 3`, 칸마다 description |
| 실습 3 ② | 운영체제·통계학·파이썬프로그래밍 세 줄. 감성은 셋 중 하나(정해진 정답 없음) |
| 실습 3 ③ | `2 validation errors for ReviewAnalysis` - sentiment `Input should be '긍정', '부정' or '중립'`, score `Input should be less than or equal to 5` (모델 호출 없이 확정) |
| 실습 4 ③ 5건 | 앞 5행은 뚜렷한 긍정 3 · 중립 1 · 부정 1 → 긍정 막대가 가장 높음 |
| 실습 4 ④ 24건 | 자료 구성: 뚜렷한 긍정 11 · 부정 6 · 중립 4 + 애매 3 → 긍정 11~14 · 부정 6~9 · 중립 4~7 |

reviews.csv의 행별 분류(assert용)는 `_생성스크립트/make_06.py`의 `REVIEWS`에 있습니다. 애매한 3건은 실습 3의 `reviews` 목록과 같은 문장입니다.

## 다시 만들기

`llm-api` 폴더에서 실행합니다.

```bash
py -X utf8 _생성스크립트/make_06.py .
```

교안 정답 표의 숫자(24행, 6개 × 4건, 11/6/4/3, 애매 3건 = 실습 3 문장, 앞 5건 긍정 최다)를 assert로 확인한 뒤 `data/reviews.csv`와 이 폴더의 코드 파일 네 개만 덮어씁니다. 다른 파일은 지우지 않습니다.

필요한 것: `google-genai`·`streamlit`·`pydantic`·`python-dotenv`·`pandas`(모두 과정 `requirements.txt`에 있음).
