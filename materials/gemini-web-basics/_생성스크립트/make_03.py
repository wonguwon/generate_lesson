"""3교시 '연결된 앱으로 문서·시트 만들기' 실습 파일 생성. usage: python -X utf8 make_03.py <gemini-web-basics 폴더>"""
import sys
from pathlib import Path

import haneul_data as M
import writers as W

ROOT = Path(sys.argv[1]) / "03_연결된_앱으로_문서_시트_만들기"
L, T = ROOT / "학습자용", ROOT / "강사용"
DRIVE = L / "Drive에_올릴_파일"

# ---------------- 교안 정답과 대조 ----------------
A = M.answer_rows()
assert A == [
    ["영업팀", "출장비", 145800, 300000, 210000, 4],
    ["영업팀", "접대비", 426000, 400000, 330000, 3],
    ["영업팀", "소모품", 85500, 100000, 60000, 6],
    ["마케팅팀", "광고비", 750000, 800000, 820000, 1],
    ["마케팅팀", "행사비", 552000, 600000, 310000, 2],
    ["마케팅팀", "소모품", 113000, 150000, 90000, 5],
]
sal = sum(r[2] for r in A if r[0] == "영업팀")
mkt = sum(r[2] for r in A if r[0] == "마케팅팀")
sal_b = sum(r[3] for r in A if r[0] == "영업팀")
mkt_b = sum(r[3] for r in A if r[0] == "마케팅팀")
assert (sal, mkt, sal + mkt) == (657300, 1415000, 2072300)
assert (sal_b, mkt_b, sal_b + mkt_b) == (800000, 1550000, 2350000)
assert (M.pct(sal, sal_b), M.pct(mkt, mkt_b), M.pct(sal + mkt, sal_b + mkt_b)) == ("82.2", "91.3", "88.2")
over = [(r[0], r[1], r[2] - r[3]) for r in A if r[2] > r[3]]
assert over == [("영업팀", "접대비", 26000)]
# 틀린 합계 진단
dup = sum(M.dept_rows(M.SALES, 1, dedupe=False).values())
wide = lambda d: True
out_s = sum(M.dept_rows(M.SALES, 1, wide).values())
out_m = sum(M.dept_rows(M.MKT, 1000, wide).values())
raw_m = sum(M.dept_rows(M.MKT, 1).values())
assert dup == 755300 and dup + mkt == 2170300
assert out_s == 925300 and out_m == 1615000 and out_s + out_m == 2540300
assert sal + raw_m == 658715
assert 426000 + 154000 == 580000  # 대본: 11월 행이 섞이면 18만 원 초과로 보임
# 실습 4
S = sorted(A, key=lambda r: -r[2])
DIFF = [r[2] - r[4] for r in S]
assert [(r[0], r[1]) for r in S] == [("마케팅팀", "광고비"), ("마케팅팀", "행사비"), ("영업팀", "접대비"),
                                    ("영업팀", "출장비"), ("마케팅팀", "소모품"), ("영업팀", "소모품")]
assert DIFF == [-70000, 242000, 96000, -64200, 23000, 25500] and sum(DIFF) == 252300
assert sum(r[4] for r in A) == 1820000

# ---------------- 파일 쓰기 ----------------
W.reset_dir(ROOT)


def expense_book(name, head, rows, sheet):
    wb = W.new_wb()
    ws = W.add_sheet(wb, sheet, head, rows, widths=[13, 13, 10, 26, 12], first=True)
    for row in ws.iter_rows(min_row=2, max_col=1):
        row[0].number_format = "yyyy-mm-dd"
    W.save_wb(wb, DRIVE / name)


expense_book("영업팀_10월_지출.xlsx", M.SALES_HEAD, M.SALES, "영업팀 지출")
expense_book("마케팅팀_10월_지출.xlsx", M.MKT_HEAD, M.MKT, "마케팅팀 지출")

doc = W.new_doc()
doc.add_paragraph(M.BUDGET_TITLE, style="Heading 1")
doc.add_paragraph(M.BUDGET_BY)
doc.add_paragraph(M.BUDGET_UNIT)
for dep in ("영업팀", "마케팅팀"):
    doc.add_paragraph(dep, style="Heading 2")
    for d, cat, bud, sep in M.BUDGET:
        if d == dep:
            doc.add_paragraph(f"{cat}: 10월 예산 {bud}, 9월 지출 {sep}", style="List Bullet")
doc.save(DRIVE / "부서별_10월_예산.docx")

W.write_text(L / "실습_요청문.txt", M.blocks(
    "연결된 앱으로 문서·시트 만들기 - 실습 요청문 모음 (3교시)",
    ["교안의 순서대로 적었습니다. 필요한 블록만 복사해 붙여넣습니다."],
    [("[실습 1] ② 합치기 요청하기 - Drive 파일 3개를 불러온 새 채팅", """불러온 파일 3개로 2026년 10월 부서별 지출 표를 만들어 줘.
- 기간: 2026-10-01부터 2026-10-31까지 날짜의 행만
- 금액은 모두 원 단위로
- 열: 부서 / 분류 / 10월 지출(원) / 10월 예산(원) / 9월 지출(원) / 순위
- 행은 부서별로 분류 6줄. 순위는 10월 지출이 큰 순서
- 합계 행은 표에 넣지 말고, 표 아래에 부서별 합계와 전체 합계를 따로 적어"""),
     ("[실습 2] ② 초안 요청하기 - 실습 1의 대화에서 Canvas를 켠 뒤", """위에서 확인한 표로 정하윤 팀장에게 보낼 2026년 10월 부서별 지출 보고서 초안을 써 줘.
- 순서: 요약 / 부서별 지출 표 / 예산 대비 / 결론
- 예산 대비에는 부서별 집행률(%)을 소수점 첫째 자리까지, 예산을 넘은 분류와 넘은 금액을 적어
- 표의 숫자는 바꾸지 마"""),
     ("[실습 2] ③ 결론 문단만 고치기 - Canvas에서 결론 문단을 드래그한 뒤 요청 칸", """접대비가 예산을 26,000원 넘었고, 11월부터는 접대비를 쓰기 전에 총무팀과 미리 협의한다는 내용으로 두 문장으로 고쳐 줘."""),
     ("[실습 3] ② 요약 문단 다듬기 - 10월_지출_보고서의 Docs 사이드패널", """이 문서의 요약 문단을 팀장 보고용으로 세 문장 이내로 다듬어 줘.
숫자와 부서 이름은 그대로 두고, 문장만 짧게 고쳐."""),
     ("[실습 4] ② 열 추가와 정렬 맡기기 - 10월_부서별_지출의 Sheets 사이드패널", """이 시트에 두 가지를 해 줘.
1. 맨 오른쪽에 "전월 대비(원)" 열을 추가해. 값은 10월 지출 − 9월 지출이고, 수식으로 넣어.
2. 10월 지출이 큰 순서로 행 전체를 정렬하고, 맨 아래에 10월 지출·10월 예산·9월 지출·전월 대비의 합계 행을 수식으로 넣어."""),
     ]))

wb = W.new_wb()
W.add_sheet(wb, "실습1_정답", ["부서", "분류", "10월 지출(원)", "10월 예산(원)", "9월 지출(원)", "순위"], A,
            widths=[12, 10, 15, 15, 15, 8], money_cols=(3, 4, 5), first=True,
            notes=[f"영업팀 합계: 10월 지출 {sal:,}원 / 10월 예산 {sal_b:,}원",
                   f"마케팅팀 합계: 10월 지출 {mkt:,}원 / 10월 예산 {mkt_b:,}원",
                   f"전체 합계: 10월 지출 {sal + mkt:,}원 / 10월 예산 {sal_b + mkt_b:,}원"])
W.add_sheet(wb, "틀린합계_진단", ["나온 값", "어디 합계", "원인", "고치는 요청"], [
    [2170300, "전체 지출", "S-1004 숙박비를 두 번 더함", "영수증 번호가 같은 행은 한 번만 계산해 줘"],
    [2540300, "전체 지출", "9월·11월 날짜 행 3개를 넣음", "10월 날짜 행만 다시 계산해 줘"],
    [658715, "전체 지출", "마케팅팀 천원 단위를 원으로 읽음", "마케팅팀 시트 금액은 천원 단위야. 원으로 바꿔 다시 계산해 줘"],
    [755300, "영업팀 합계", "S-1004 중복", "영수증 번호가 같은 행은 한 번만 계산해 줘"],
    [925300, "영업팀 합계", "기간 밖 행(9/25, 11/2) 포함", "10월 날짜 행만 다시 계산해 줘"],
    [1615000, "마케팅팀 합계", "11월 행(11/3) 포함", "10월 날짜 행만 다시 계산해 줘"],
], widths=[13, 14, 34, 56], money_cols=(1,))
W.add_sheet(wb, "실습2_3_확인", ["확인할 곳", "정답"], [
    ["전체 지출", f"{sal + mkt:,}원"],
    ["부서 지출", f"영업팀 {sal:,}원, 마케팅팀 {mkt:,}원"],
    ["집행률", "영업팀 82.2%, 마케팅팀 91.3%, 전체 88.2%"],
    ["예산을 넘은 분류", "영업팀 접대비, 26,000원 초과"],
], widths=[20, 46])
rows4 = [[r[5], r[0], r[1], r[2], r[3], r[4], f"=D{i}-F{i}"] for i, r in enumerate(S, start=2)]
rows4.append([None, None, "합계"] + [f"=SUM({c}2:{c}7)" for c in "DEFG"])
ws = W.add_sheet(wb, "실습4_정답", ["순위", "부서", "분류", "10월 지출(원)", "10월 예산(원)", "9월 지출(원)", "전월 대비(원)"], rows4,
                 widths=[7, 12, 10, 15, 15, 15, 15])
for row in ws.iter_rows(min_row=2, max_row=8, min_col=4, max_col=7):
    for c in row:
        c.number_format = "#,##0"
W.save_wb(wb, T / "정답_3교시.xlsx")

W.write_text(ROOT / "README.md", """# 연결된 앱으로 문서·시트 만들기 - 실습 파일 (3교시)

교안: [3️⃣ 연결된 앱으로 문서·시트 만들기](https://app.notion.com/p/357435fcbd9d83599d50810fd5b2407f)

## 학습자용

| 파일 | 쓰는 곳 | 내용 |
| --- | --- | --- |
| Drive에_올릴_파일/영업팀_10월_지출.xlsx | 실습 1 | 9행, 원 단위. 중복 S-1004 두 줄, 기간 밖 9/25·11/2 행 포함 |
| Drive에_올릴_파일/마케팅팀_10월_지출.xlsx | 실습 1 | 7행, 천원 단위. 기간 밖 11/3 행 포함 |
| Drive에_올릴_파일/부서별_10월_예산.docx | 실습 1 | 부서·분류별 10월 예산과 9월 지출, 만원 단위 |
| 실습_요청문.txt | 실습 1~4 | 교안의 요청문 모음 |

세 파일은 Google 스프레드시트·문서로 변환해 공유합니다(방법은 과정 README).
실수를 찾는 실습이라 파일 안의 중복·기간 밖 행·단위 차이는 일부러 넣은 것입니다.

## 강사용 (배포하지 않음)

| 파일 | 내용 |
| --- | --- |
| 정답_3교시.xlsx | 실습 1 정답, 틀린 합계 진단, 실습 2·3 확인 값, 실습 4 정렬 정답(수식) |
""")
print("03 완료")
