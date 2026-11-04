# 덱 스펙(deck.json) 작성법

`scripts/build_deck.py`가 읽는 입력 파일이다. 내용과 아키타입만 적는다. 좌표·색·글자 크기는 적지 않는다. 모두 `ppt_design/templates.json`에서 읽는다.

## 맨 위 항목

| 항목 | 필수 | 내용 |
| --- | --- | --- |
| `course` | 필수 | 과목명. 표지 메타 라인과 푸터에 쓴다 |
| `course_short` | 선택 | 헤더용 짧은 과목명. 헤더가 한 줄을 넘으면 넣는다 |
| `organization` | 필수 | 기관명. 헤더 왼쪽과 푸터에 쓴다 |
| `instructor` | 필수 | 담당 강사 이름. 호칭 없이 이름만 적는다 |
| `day` | 필수 | `Day 03` 형식 |
| `semester` | 선택 | 표지 학기 칩 글자. 없으면 칩을 그리지 않는다 |
| `slides` | 필수 | 슬라이드 목록. 순서대로 만든다 |

## 글자 표시

- `**글자**`: 굵게
- `[[글자]]`: 강조색. 어두운 패널 위에서는 알맞은 색으로 저절로 바뀐다
- 문자열 안의 `\n`: 줄바꿈. 표지 제목 등 끊기는 자리를 정할 때 쓴다
- 불릿 2단계: 문자열 대신 `{"text": "내용", "level": 2}`

## 대본

모든 아키타입에 `"notes": "대본"`을 넣을 수 있다. 슬라이드 노트에 들어가고, 문자열 안의 `\n`은 문단을 나눈다. 슬라이드 글자 표시(`**`, `[[ ]]`)는 노트에 쓰지 않는다.

## 내비 탭(도입·본론·정리)

`section_divider`에 `phase`를 적으면 이후 슬라이드가 그 단계를 이어받는다. `agenda_with_goals`는 도입, `summary_with_next`는 정리로 정해진다. 슬라이드에 `phase`를 직접 적으면 그 값이 우선한다.

## 아키타입별 항목

`icon`, `goal_icon`은 Lucide 아이콘 이름이다. 찾을 때는 `--list-icons 단어`를 쓴다.

```json
{"archetype": "cover", "title": "제목", "subtitle": "부제", "meta": "(선택) 없으면 과목명 | 담당 강사", "image": "(선택) 표지 프레임 이미지"}
{"archetype": "agenda_with_goals", "title": "제목", "goal_icon": "target", "goal_title": "(선택) 없으면 학습 목표",
 "items": [{"title": "항목", "desc": "부연"}], "goals": ["목표"]}
{"archetype": "section_divider", "phase": "본론", "title": "섹션 제목", "intro": "도입 문장"}
{"archetype": "text_plus_key_point", "title": "제목", "bullets": ["불릿"], "icon": "lightbulb", "key_title": "핵심", "key_message": "핵심 한 문장"}
{"archetype": "three_column_card_compare", "title": "제목", "columns": [{"icon": "box", "title": "제목", "desc": "설명"}]}
{"archetype": "two_column_versus", "title": "제목", "left": {"title": "중립", "bullets": ["불릿"]}, "right": {"title": "강조", "bullets": ["불릿"]}}
{"archetype": "process_steps", "title": "제목", "steps": [{"title": "단계", "desc": "설명"}]}
{"archetype": "code_or_formula_explain", "title": "제목", "code": "코드", "keywords": ["(선택) 강조할 키워드"],
 "explain_title": "해설 제목", "bullets": ["해설"], "tip": "(선택) Tip"}
{"archetype": "activity_list_with_time", "title": "제목", "rows": [{"icon": "users", "title": "활동", "desc": "설명", "time": "10분"}]}
{"archetype": "summary_with_next", "title": "제목", "rows": [{"icon": "check", "text": "한 문장"}],
 "next_label": "(선택) 없으면 NEXT WEEK", "next_title": "(선택) 없으면 다음 주 예고", "next": ["예고"]}
{"archetype": "closing", "title": "(선택)", "subtitle": "(선택)", "contact": "(선택) 연락처 라인"}
```

- `code_or_formula_explain`은 `code` 대신 `image`(파일 경로)를 넣으면 코드 블록 자리에 이미지를 넣는다. 수식, 다이어그램, 교안의 그림은 이 방식으로 넣는다.
- 경로는 deck.json 기준 상대 경로나 절대 경로로 적는다.
- 개수는 templates.json의 아키타입 규칙을 따른다. 아젠다 4행, 3단 3열, 활동·요약 3행까지, 단계는 3~5개다.
