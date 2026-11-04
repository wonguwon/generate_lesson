# LLM API 활용 및 AI 애플리케이션 개발 - 실습 파일

이 폴더는 학습자가 수업에서 만들어 가는 `llm-api` 프로젝트의 완성본입니다. VS Code에서 이 폴더를 열고, 모든 명령은 이 폴더(맨 위)에서 실행합니다. 차시 폴더 안에는 완성 코드가 바로 있고, 여러 차시가 함께 쓰는 자료는 맨 위 `data` 폴더에 있습니다. 각 폴더의 README에 파일별 용도와 정답 요약이 있습니다.

| 폴더 | 교안 | 파일 | 쓰는 데이터 |
| --- | --- | --- | --- |
| 01_api-vs-web | [1️⃣ 웹 생성형 AI와 LLM API](https://app.notion.com/p/7b6435fcbd9d838e91de0130f00c63b5) | 실습_요청문.txt (붙여넣기용, 코드 없음) | 없음 |
| 02_first-call | [2️⃣ 개발 환경과 첫 API 호출](https://app.notion.com/p/d8e435fcbd9d82b894a101018abb56f0) | 실습1_버전확인.py, 실습2_키확인.py, 실습3_첫호출.py, 실습4_토큰확인.py | 없음 |
| 03_model-config | [3️⃣ 모델 선택과 생성 설정](https://app.notion.com/p/7b2435fcbd9d82f48c5b817154fb9691) | 실습1_모델비교.py, 실습2_시스템지시.py, 실습3_생성설정.py, 실습4_퓨샷분류.py | 없음 |
| 04_chat-history | [4️⃣ 대화 기록과 멀티턴 챗봇](https://app.notion.com/p/add435fcbd9d83f39e8f016fb9b6e783) | 실습1_무상태.py, 실습2_기록직접관리.py, 실습3_터미널챗봇.py, 실습4_방식비교.py | 없음 |
| 05_streamlit-chat | [5️⃣ Streamlit 챗봇 앱](https://app.notion.com/p/9ac435fcbd9d826c846e018b62cfb6a2) | 실습1_한화면앱.py, 실습2_채팅앱.py, 실습3_스트리밍.py, app.py | 없음 |
| 06_structured-output | [6️⃣ 구조화 출력과 강의평 분석기](https://app.notion.com/p/1c6435fcbd9d8211b73581df46713e91) | 실습1_JSON요청.py, 실습2_스키마.py, 실습3_열거형.py, app.py | data/reviews.csv |
| 07_multimodal | [7️⃣ 멀티모달과 영수증 가계부](https://app.notion.com/p/abc435fcbd9d83c6822c81257611b257) | 실습1_이미지질문.py, 실습2_영수증분석.py, 실습3_검증.py, app.py | data/campus.jpg, data/receipts/ (영수증 4장) |
| 08_function-calling | [8️⃣ 함수 호출과 캠퍼스 도우미](https://app.notion.com/p/993435fcbd9d82c4ab960110f61b81c9) | 실습1_함수선언.py, 실습2_함수실행.py, app.py | 없음 (가상 데이터는 코드 안에 있음) |
| 09_rag | [9️⃣ 임베딩과 RAG 원리](https://app.notion.com/p/9b2435fcbd9d836ca60901016f19c282) | 실습1_환각확인.py, 실습2_임베딩유사도.py, 실습3_미니RAG.py, 실습4_랭체인.py | data/handbook_paragraphs.txt |
| 10_langchain-rag | [🔟 LangChain RAG 챗봇](https://app.notion.com/p/416435fcbd9d8292919081518fc72664) | 실습1_문서분할.py, 실습2_벡터검색.py, 실습3_RAG체인.py, app.py | data/handbook.pdf |

텍스트는 UTF-8로 저장했습니다. README.md와 메모장으로 여는 `01_api-vs-web/실습_요청문.txt`만 BOM이 있고, 코드·자료(.py·.txt·.csv)는 BOM이 없습니다(BOM이 있으면 `data/handbook_paragraphs.txt` 첫 문단 맨 앞에 붙음).

## 준비

Python 3.11 이상이 필요합니다. 이 폴더에서 가상환경을 만들고 켭니다.

```bash
python -m venv .venv
```

```bash
.venv\Scripts\activate
```

```bash
pip install -r requirements.txt
```

`.env.example`을 복사해 `.env`를 만들고, `GEMINI_API_KEY=` 뒤에 자기 키를 넣습니다.

```bash
copy .env.example .env
```

실행 예(이 폴더에서):

```bash
python 02_first-call/실습3_첫호출.py
```

```bash
streamlit run 05_streamlit-chat/app.py
```

## 배포

학습자에게는 `data` 폴더만 압축해 나눠 줍니다. 코드는 수업에서 직접 칩니다. 학습자는 자기 `llm-api` 폴더 맨 위에 `data` 폴더를 그대로 풀면 교안의 경로(`data/reviews.csv` 등)와 맞습니다.
`.env`는 절대 넣지 않습니다(이 폴더에 `.env`를 만들었다면 압축·공유 전에 빠졌는지 확인합니다).

## 주의

- 각 차시 README의 정답 표는 실제 키로 돌려 보지 않은 예상값입니다. 촬영 전에 촬영 키로 확인합니다.
- `data/campus.jpg`는 그림으로 그린 일러스트라 실제 사진이 아닙니다. 교안은 직접 찍었거나 자유 이용 이미지를 쓰라고 하므로, 실제 캠퍼스 사진(얼굴·차량 번호가 안 보이는 JPEG)으로 바꿔 넣습니다.

## 다시 만들기

자료와 6·7차시 코드는 `_생성스크립트`에서 만듭니다. 스크립트는 교안 정답 표가 기대는 숫자를 assert로 확인한 뒤 자기 파일만 덮어쓰고, 다른 파일은 지우지 않습니다. 모두 이 폴더에서 실행합니다.

```bash
py -X utf8 _생성스크립트/make_06.py .
```

```bash
py -X utf8 _생성스크립트/make_07.py .
```

```bash
py -X utf8 _생성스크립트/make_09.py
```

```bash
py -X utf8 _생성스크립트/make_pdf.py
```

```bash
py -X utf8 _생성스크립트/점검.py
```

| 스크립트 | 만드는 파일 |
| --- | --- |
| make_06.py | data/reviews.csv, 06_structured-output의 .py 네 개 |
| make_07.py | data/campus.jpg, data/receipts/ 네 장, 07_multimodal의 .py 네 개 |
| make_09.py | data/handbook_paragraphs.txt |
| make_pdf.py | data/handbook.pdf (만든 시각이 들어가 바이트는 매번 다르지만 쪽별 글은 같음) |

`점검.py`는 모든 .py 문법, 있어야 할 파일 목록, `강사용`·`학습자용`·`__pycache__`·`.env`가 남아 있지 않은지, BOM 규칙, `data/handbook_paragraphs.txt` 10줄과 `data/reviews.csv` 24행을 확인합니다. 마지막 줄이 "모두 일치"면 정상입니다.

필요한 것: Windows 맑은 고딕 글꼴(`C:\Windows\Fonts\malgun.ttf`, `malgunbd.ttf`, 영수증 jpg·PDF 한글용)과 아래 패키지. reportlab·pillow는 requirements.txt 맨 아래 주석에만 적혀 있습니다.

```bash
pip install reportlab pillow pypdf langchain-text-splitters
```
