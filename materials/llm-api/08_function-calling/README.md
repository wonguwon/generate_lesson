# 함수 호출과 캠퍼스 도우미 - 실습 파일 (8차시)

교안: [8️⃣ API8 : 함수 호출과 캠퍼스 도우미](https://app.notion.com/p/993435fcbd9d82c4ab960110f61b81c9)

학식·도서관 가상 데이터(OO대학교, 실습용 가상 자료)는 교안 코드 안의 딕셔너리(`CAFETERIA_MENU`·`LIBRARY_SEATS`)로 들어가고, 실습용 오늘은 2026-11-10 화요일로 고정입니다.
따로 쓰는 데이터 파일도 시작 파일도 없습니다(교안이 새 폴더·새 파일을 만들게 하고, 실습 2는 실습 1을 복사해 고침).

교안의 코드는 **프로젝트 맨 위 폴더**(`llm-api`)에서 실행한다고 가정합니다(VS Code 실행 버튼, `streamlit run 08_function-calling/app.py`).

## 파일

교안 코드 블록을 단계 순서대로 이어 붙인 **마지막 상태**입니다. 변수 이름·시스템 지시·함수 설명서·print 줄은 교안과 같습니다.

| 파일 | 쓰는 곳 | 내용 |
| --- | --- | --- |
| 실습1_함수선언.py | 실습 1 ①~④ | 가상 데이터·두 함수, `print(get_...)` 두 줄, MENU_TOOL·SEATS_TOOL·TOOLS, `show`, 질문 세 개(내일 점심 / 수강 정정 기간 / 오늘 저녁 + 과학도서관) |
| 실습2_함수실행.py | 실습 2 ①② | 실습 1에서 print 두 줄과 `def show` 아래를 지운 뒤 FUNCTIONS·`run_call`·`ask`(최대 5번 루프)를 넣은 상태. 맨 아래 질문은 ②의 "오늘 저녁 메뉴랑 과학도서관 빈자리 알려 줘." |
| app.py | 실습 3 | 캠퍼스 도우미. 5차시 `app.py` 틀(키 확인·session_state·대화 초기화·error_message) + `run_call`·`ask`, `TOOL_LABELS`, 말풍선 위 "… 조회함" 캡션, messages에 `"tools"` 저장 |

## 실행

`llm-api` 폴더에서 실행합니다.

```bash
python 08_function-calling/실습2_함수실행.py
```

```bash
streamlit run 08_function-calling/app.py
```

### 단계별로 바꾸는 줄

| 단계 | 파일 | 바꾸는 곳 |
| --- | --- | --- |
| 실습 2 ① | 실습2_함수실행.py | `def ask`부터 끝까지 대신 교안 ①의 "내일 점심" create + `for step ...: print(run_call(step))` 코드. function_result 항목 모양만 보여 줄 때 |
| 실습 2 ③ | 실습2_함수실행.py | 맨 아래 `ask("…")`의 질문을 `인문도서관에 빈자리 있어?` → `이번 주 토요일 점심 메뉴는 뭐야?`로 차례로 바꿔 실행 |

## 정답 요약

실제 API 키로는 아직 돌려 보지 않았습니다. 함수 결과 문장(아래 코드체)은 데이터로 정해지는 값이고, 모델이 함수를 부를지·문장 표현은 실행마다 달라질 수 있습니다(예상).

| 확인할 것 | 정답(예상) |
| --- | --- |
| 실습 1 ① | `2026-11-11 학생식당 점심: 돈가스, 크림수프 / 저녁: 비빔밥, 된장국` · `중앙도서관 열람실 빈자리 77석 / 전체 420석` (모델 호출 없이 확정) |
| 실습 1 ② | steps에 `function_call`(앞에 `thought`가 있을 수 있음), `get_cafeteria_menu {'date': '2026-11-11'}`와 긴 id, output_text `''`인 경우가 많음, status는 `requires_action`일 수 있음 |
| 실습 1 ③ | function_call 없음, `model_output`, 수강 정정 기간을 설명하는 한 문장 |
| 실습 1 ④ | 두 줄: `get_cafeteria_menu {'date': '2026-11-10'}` · `get_library_seats {'building': '과학도서관'}` (하나씩 부를 수도 있음) |
| 실습 2 ① | `[함수 실행] get_cafeteria_menu({'date': '2026-11-11'}) → 2026-11-11 학생식당 …` 다음 줄 `{'type': 'function_result', 'call_id': '…', 'name': 'get_cafeteria_menu', 'result': '…'}` |
| 실습 2 ② | 함수 실행 두 줄(`… 저녁: 김치찌개, 계란말이` · `과학도서관 열람실 빈자리 29석 / 전체 160석`), 부른 함수 `['get_cafeteria_menu', 'get_library_seats']`, 답은 김치찌개·계란말이와 29석 |
| 실습 2 ③ 인문도서관 | `인문도서관: 없는 도서관 이름입니다. 조회할 수 있는 곳: 중앙도서관, 과학도서관`, 답은 중앙·과학도서관 안내 |
| 실습 2 ③ 토요일 | 인자 `{'date': '2026-11-14'}`, 결과 `2026-11-14에는 학생식당 식단이 없습니다.` |
| 실습 3 ② | 1턴 "학식 메뉴 조회함" + 치킨마요덮밥·우동 / 2턴 "도서관 좌석 조회함" + 77석 / 터미널에 질문마다 `[함수 실행]` |
| 실습 3 ③ | 1턴 "학식 메뉴 조회함" + 2026-11-11 저녁 비빔밥·된장국(앞 대화를 이어 받음) / 2턴 조회함 없음, 운영 시간은 홈페이지·도서관에서 확인하라는 안내 / 다음 질문 뒤에도 앞 조회함 표시가 남음 |

## 확인한 것 (가짜 응답)

- 세 파일 모두 문법 확인, `httpx.MockTransport`로 Interactions API 응답을 흉내 내어 실행.
- 함수 결과 문장 77석·29석·없는 도서관·식단 없는 날, function_result 요청에 `previous_interaction_id`·`system_instruction`·`tools`가 다시 들어가는 것 확인.
- app.py는 `streamlit.testing`으로 실습 3의 네 질문을 보내 캡션 3개, messages의 `tools`, `last_id` 이어 받기, 대화 초기화, 키 없을 때 안내 문구 확인.
