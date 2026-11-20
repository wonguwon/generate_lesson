# [기본] Claude 앱 ClaudeCode - 실습 파일

가상 회사 **누리상사 영업관리팀**(포장재 공급) 하나로 1~5교시를 잇습니다. 교시마다 폴더 하나, 안은 `학습자용`(배포)과 `강사용`(정답, 배포하지 않음)입니다.

| 폴더 | 교안 | 학습자용 |
| --- | --- | --- |
| 01_Claude_Code와_작업폴더 | [1️⃣ Claude Code와 작업 폴더](https://app.notion.com/p/84d435fcbd9d827ca3fc018ffbf291c2) | 누리상사_영업관리팀 (맨 위 파일 6개 + 거래처_윤슬찬푸드 폴더 파일 6개), 같은 이름 zip, 실습_요청문.txt |
| 02_계획모드와_Docs_Slides | [2️⃣ 계획 모드와 Docs·Slides](https://app.notion.com/p/6a5435fcbd9d8218b2fa01d93a80be89) | 월별주문 (7·8·9월 주문 CSV 3개 + 빈 양식 1개, `원본` 안에 넣음), 2교시_월별주문.zip, 실습_요청문.txt |
| 03_CLAUDE.md와_컨텍스트 | [3️⃣ CLAUDE.md와 컨텍스트](https://app.notion.com/p/c1b435fcbd9d8235a59d81c74568e1be) | 10월_주문내역(최종).csv (23행, 날짜 2026/10/dd, `원본/월별주문` 안에 넣음), 3교시_10월주문.zip, 실습_요청문.txt (CLAUDE.md에 더할 규칙 포함) |
| 04_코드로_작업물_만들기 | [4️⃣ 코드로 작업물 만들기](https://app.notion.com/p/4bb435fcbd9d83d4adc881af7e81c376) | 주문내역_11월.csv (24행, 열 이름 일자·거래처명·주문수량, `원본/월별주문` 안에 넣음), 4교시_실습자료.zip, 실습_요청문.txt |
| 05_스킬과_서브에이전트 | [5️⃣ 스킬과 서브에이전트](https://app.notion.com/p/2a5435fcbd9d83569e520181cdce653f) | 거래처_다솜제과·거래처_해든푸드 (폴더마다 견적서 PDF·거래내역 xlsx·메모 txt, `원본` 안에 넣음. 거래처_윤슬찬푸드는 1교시 폴더 그대로), 5교시_거래처폴더.zip, 실습_요청문.txt |

공통 데이터(담당자·거래처 14곳·상품 12종과 기준단가)는 `_생성스크립트/nuri_data.py`에 있고, 뒤 교시도 이 값을 이어 씁니다. 7~11월 주문 행은 `nuri_orders.py`에 고정했고(`gen_orders.py`로 한 번 생성), 월별 파일 이름·날짜 형식·중복·빈칸·11월 열 이름은 `nuri_data.py`의 `ORDER_FILES`·`DATE_FMT`·`MESS`·`ORDER_COLS_RENAMED`에 있습니다. 3교시(10월)·4교시(11월) 정답은 `02_계획모드와_Docs_Slides/강사용/정답_2교시.txt` 끝에 미리 적어 두었고, 3교시 정답은 `03_CLAUDE.md와_컨텍스트/강사용/정답_3교시.txt`, 4교시 정답(스크립트 10·11월 실행, 대시보드, 견적 계산기 예시 3건)은 `04_코드로_작업물_만들기/강사용/정답_4교시.txt`에 있습니다(`make_03.py`·`make_04.py`가 2교시에 정한 10·11월 값을 assert로 확인). 5교시 정답(/monthly-report 11월 보고서 = 4교시 11월 정답, 이름 없이 부른 10월 = 3교시 정답, checker 검산표, 거래처 3곳 비교표 = 윤슬찬푸드는 1교시 실습 2 정답)은 `05_스킬과_서브에이전트/강사용/정답_5교시.txt`, 스킬·서브에이전트 파일 예시는 같은 폴더의 `예시_SKILL_monthly-report.md`·`예시_checker.md`에 있습니다(`make_05.py`가 assert로 확인).

## 다시 만들기

```bash
cd _생성스크립트
py -3.14 -X utf8 make_01.py ..
py -3.14 -X utf8 make_02.py ..
py -3.14 -X utf8 make_03.py ..
py -3.14 -X utf8 make_04.py ..
py -3.14 -X utf8 make_05.py ..
```

교안 정답 표의 숫자를 assert로 확인한 뒤에만 `학습자용`·`강사용`을 지우고 다시 씁니다. 필요한 것: Python 3.10 이상, `openpyxl pillow reportlab pypdf`, Windows 맑은 고딕 글꼴.
