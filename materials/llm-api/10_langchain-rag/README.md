# LangChain RAG 챗봇 - 실습 파일 (10차시)

교안: [🔟 API10 : LangChain RAG 챗봇](https://app.notion.com/p/416435fcbd9d8292919081518fc72664)

교안의 코드는 모두 **프로젝트 맨 위 폴더**(`llm-api`)에서 실행한다고 가정합니다(VS Code 실행 버튼, `streamlit run 10_langchain-rag/app.py`). 코드가 `PDF_PATH = "data/handbook.pdf"`로 읽으므로 자료는 `10_langchain-rag` 안이 아니라 프로젝트 맨 위의 공용 `data` 폴더에 있습니다.

## 파일

코드 파일은 교안 코드 블록을 단계 순서대로 이어 붙인 **마지막 상태**입니다. 상수·프롬프트·시스템 지시·print 줄은 교안과 같습니다.

| 파일 | 쓰는 곳 | 내용 |
| --- | --- | --- |
| ../data/handbook.pdf | 실습 1~4 | 가상 "OO대학교 2027학년도 학사 안내 핸드북"(**실습용 가상 자료**, 1쪽 표지에 문구 있음). 교안 토글 "handbook.pdf 쪽별 원문" 그대로, A4 11쪽, 한 쪽에 한 주제, 제목 굵게, 쪽 아래 가운데 `- N -`. 숫자·날짜는 9차시 handbook_paragraphs.txt와 같고 기숙사 안내는 없음 |
| 실습1_문서분할.py | 실습 1 ②③ | pypdf로 만든 `load_pdf`(쪽 번호 1부터) → `chunk_size` 500·200(겹침 50)으로 나눠 조각 수와 `chunks[1:3]` 앞뒤 15글자. `pip install pypdf langchain-text-splitters` 필요 |
| 실습2_벡터검색.py | 실습 2 ①②③ | `GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")` + `InMemoryVectorStore.from_documents`, 질문 3개 `similarity_search_with_score`(쪽 번호 줄 `-`로 시작하는 줄을 뺀 첫 줄 = 제목), 리트리버 k=3 |
| 실습3_RAG체인.py | 실습 3 ①②③ | 교안 순서대로 조립: 실습2 복사 → `QUESTIONS` 아래 삭제 → import 블록 끝에 네 줄 → `EMBED_MODEL` 위에 `MODEL` → RULES·`make_chain`·평점 4.2 / 기숙사 / 규칙 뺀 기숙사 |
| app.py | 실습 4 | 학사 안내 챗봇. `@st.cache_resource load_retriever`, `answer`(답, 조각), 근거 보기 expander(쪽 번호 + 조각 글), `error.__cause__`의 code로 오류 안내, messages에 sources 저장 |

시작 파일은 없습니다(교안이 새 파일을 만들게 하고, 실습 3은 실습 2를 복사해 고침).

## 실행

`llm-api` 폴더에서 실행합니다.

```bash
python 10_langchain-rag/실습1_문서분할.py
```

```bash
streamlit run 10_langchain-rag/app.py
```

실습 2·3도 `python 10_langchain-rag/파일이름.py`로 실행합니다.

## 정답 요약

실제 API 키로는 아직 돌려 보지 않았습니다. 쪽 수·조각 수·metadata는 PDF로 정해져 확인한 값이고, 검색 순위와 모델 답은 실행마다 달라질 수 있습니다(예상).

| 확인할 것 | 정답 | 확인 |
| --- | --- | --- |
| 실습 1 ② | 쪽 수 `11`, `{'source': 'data/handbook.pdf', 'page': 2}`, 2쪽 글은 `- 2 -` 줄이 맨 앞, 이어서 `수강 신청` | 확인함(pypdf 6.21.4) |
| 실습 1 ③ 500 | 조각 11개, `2쪽 \| - 2 - 수강 신청 202 … 체 학년 신청일에 신청한다.`, 3쪽 한 조각 | 확인함(쪽마다 98~348자) |
| 실습 1 ③ 200 | 조각 19개, `2쪽 \| - 2 - 수강 신청 202 … 직전 학기 평점평균이 4.0` · `2쪽 \| 한 학기에는 12학점 이상  … 체 학년 신청일에 신청한다.` 두 번째 조각이 앞 조각 끝 줄("한 학기에는 …")을 겹쳐 다시 시작, 두 번째 문단이 두 조각에 나뉨 | 확인함. 본문 12pt 줄바꿈 기준이라 글꼴 크기를 바꾸면 달라짐(11pt면 겹침이 안 보임) |
| 실습 2 ① | 저장한 조각 `11`, 벡터 길이 `3072` | 조각 수 확인함, 길이는 예상 |
| 실습 2 ② | 수강 신청 질문 1위 `2쪽 수강 신청`, 휴학 질문 1위 `4쪽 휴학`(5쪽 복학도), 여름방학 질문 1위 `10쪽 계절학기`인 경우가 많음 | 예상. 쪽 제목 추출은 11쪽 모두 확인 |
| 실습 2 ③ | `list 3`, 첫 번호 `4` | 예상 |
| 실습 3 ① | 21학점까지 | 예상. 2쪽 "직전 학기 평점평균이 4.0 이상이면 21학점까지" |
| 실습 3 ② | "학사 안내 문서에서 찾을 수 없습니다. 학사지원팀에 문의하세요." | 예상. PDF에 "기숙사" 없음 |
| 실습 3 ③ | 일반적인 기숙사 신청 시기·방법을 덧붙이는 경우가 많음 | 예상 |
| 실습 4 ② | 1턴 2월 18일(목), 근거 맨 위 2쪽 / 2턴 평점평균 3.80 이상, 근거에 6쪽 / 터미널 `[임베딩] 조각 11개를 벡터 저장소에 넣음` 한 줄 | 임베딩 줄 1번만 나오는 것 확인함, 나머지 예상 |
| 실습 4 ③ | 기숙사는 찾을 수 없다는 답 + 관련 없는 조각 3개 / "제가 방금 무엇을 물어봤죠?"는 앞 질문을 말하지 못함 / 앞 답의 근거 보기 유지 | 근거 보기 유지 확인함, 답은 예상 |

## API 키

- LangChain(langchain-google-genai 4.4.2)은 `.env`의 `GEMINI_API_KEY`를 그대로 읽습니다(`load_dotenv()` 필요). app.py의 키 확인도 `GEMINI_API_KEY`를 봅니다.
- 컴퓨터에 `GOOGLE_API_KEY`가 함께 있으면 "Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY." 경고와 함께 그 키를 먼저 씁니다(교안 설명과 같음, 확인함).
- 오류 안내: LangChain은 Gemini 429 등을 `GoogleRateLimitError`/`GoogleGenerativeAIError`로 감싸고 `status_code`가 없으며, `error.__cause__`가 google-genai `ClientError`(`code` 429)입니다(가짜 오류로 확인함). PDF가 없으면 `No such file` → "인터넷 연결과 PDF 위치를 확인" 안내.

## 다시 만들기

`llm-api` 폴더에서 실행합니다.

```bash
py -X utf8 _생성스크립트/make_pdf.py
```

교안 토글 원문으로 `data/handbook.pdf`를 만들고(reportlab, 글꼴 `C:/Windows/Fonts/malgun.ttf`·`malgunbd.ttf`), 교안 코드와 같은 `load_pdf`로 다시 읽어 11쪽, 2쪽 metadata, 쪽 제목, 쪽마다 500자 미만, chunk_size 500 → 11조각, 핵심 사실(2월 18일(목), 4.0 이상 21학점, 통산 6학기, 3.80 이상, 학점당 8만 원), "기숙사" 없음, chunk_size 200의 `chunks[1:3]`이 모두 2쪽이고 겹치는지를 assert로 확인합니다. 200 → 19조각도 출력합니다. 본문 글꼴 12pt는 이 겹침이 보이도록 고른 값입니다.
PDF 안에 만든 시각이 들어가므로 다시 만들 때마다 파일 바이트는 달라지지만 쪽별 글은 같습니다.

## 확인한 것 (가짜 응답)

- 네 파일 모두 문법 확인. `llm-api` 폴더에서 `python -X utf8 10_langchain-rag/실습N.py`로 실행해 `data/handbook.pdf` 상대 경로 확인.
- 임베딩·모델은 LangChain 가짜 부품(DeterministicFakeEmbedding·FakeListChatModel)으로 바꿔 실행. 체인 연결·리트리버 `list 3`·app의 캐시(임베딩 1번)·근거 보기·대화 초기화·키 없음 안내 확인. 가짜 임베딩이라 검색 순위는 확인하지 못했습니다.
