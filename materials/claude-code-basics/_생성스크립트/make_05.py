"""5교시 실습 파일 만들기: py -3.14 -X utf8 make_05.py ..

학습자용/거래처_다솜제과, 학습자용/거래처_해든푸드 (폴더마다 견적서 PDF·거래내역 xlsx·메모 txt),
학습자용/5교시_거래처폴더.zip, 학습자용/실습_요청문.txt,
강사용/정답_5교시.txt, 강사용/예시_SKILL_monthly-report.md, 강사용/예시_checker.md
거래처_윤슬찬푸드는 1교시 폴더를 그대로 쓴다(원본 안에 있음).
11월 보고서 값은 4교시 정답, 윤슬찬푸드 값은 1교시 실습 2 정답과 같아야 한다.
"""
import datetime as dt
import io
import shutil
import sys
import zipfile
from pathlib import Path

from openpyxl import load_workbook

import nuri_data as D
from make_01 import FONT, FONT_BD, text, xlsx
from make_02 import HOL, check_data, pct

HOL5 = HOL | {"2026-01-01", "2026-02-16", "2026-02-17", "2026-02-18", "2026-03-02", "2026-05-05",
              "2026-05-25", "2026-06-03", "2026-12-25"}
WD = "월화수목금토일"

# ---------------- 거래처 폴더 2곳 (윤슬찬푸드는 1교시 그대로) ----------------
# 거래내역: 1~6월은 여기서 정하고, 7~10월은 nuri_orders의 주문과 같게 (1교시 윤슬찬푸드와 같은 방식)
EARLY = {
    "다솜제과": [("2026-01-20", "골판지 박스(소)", 1200), ("2026-02-10", "식품 라벨 스티커", 25),
             ("2026-03-17", "지퍼백(중)", 30), ("2026-04-21", "골판지 박스(중)", 800),
             ("2026-06-09", "골판지 박스(중)", 900)],
    "해든푸드": [("2026-01-15", "아이스팩(500g)", 2000), ("2026-03-12", "보냉 파우치", 2500),
             ("2026-04-09", "아이스팩(500g)", 1800), ("2026-05-20", "보냉 박스(스티로폼)", 300),
             ("2026-06-17", "식품용 비닐 롤백", 25)],
}
CONTACT = {"다솜제과": ("구매 담당", "대리", "문서윤"), "해든푸드": ("구매팀", "과장", "탁재원")}
QUOTES = {
    "다솜제과": {"date": "2026-11-05", "no": "NR-Q-2611-003",
             "items": [("골판지 박스(소)", 3000, 430), ("식품 라벨 스티커", 30, 8400), ("포장 테이프(투명)", 100, 1200)]},
    "해든푸드": {"date": "2026-10-26", "no": "NR-Q-2610-024",
             "items": [("아이스팩(500g)", 2500, 410), ("보냉 박스(스티로폼)", 500, 1900), ("식품용 비닐 롤백", 40, 6800)]},
}
MEMO_FILE = {"다솜제과": "방문메모_다솜제과_2026-11-03.txt", "해든푸드": "통화메모_해든푸드_2026-10-20.txt"}
MEMOS = {
    "다솜제과": """[방문 메모] 다솜제과 구매 담당 미팅 (실습용 가상 회사)
일시: 2026년 11월 3일(화) 오후 2시~3시
장소: 다솜제과 본점 사무실
참석: 다솜제과 문서윤 대리 / 누리상사 이수아

논의
- 연말 선물세트용 포장 문의 (10월 27일 영업회의에서 공유된 건)
- 골판지 박스(소) 3,000개, 식품 라벨 스티커 30롤, 포장 테이프(투명) 100개
- 첫 납품 희망일: 2026년 12월 1일(화)

할 일
- 이수아: 견적서를 11월 5일(목)까지 송부
- 이수아: 박스에 로고 인쇄가 되는지 확인해 회신
""",
    "해든푸드": """[통화 메모] 해든푸드 구매팀 (실습용 가상 회사)
일시: 2026년 10월 20일(화) 오전 10시
통화: 해든푸드 탁재원 과장 / 누리상사 박준영

내용
- 겨울철 반찬 배송용 보냉 포장을 늘릴 예정
- 견적 요청: 아이스팩(500g) 2,500개, 보냉 박스(스티로폼) 500개, 식품용 비닐 롤백 40롤
- 보냉 박스를 11월 셋째 주까지 받을 수 있는지 확인 요청

할 일
- 박준영: 견적서를 10월 26일(월)까지 송부
- 박준영: 해든푸드 회신 기한 11월 6일(금)까지 납기 확인
""",
}
STAFF = {c[1]: c[4] for c in D.CLIENTS}


def trades(client):
    early = [(d, i, n) for d, i, n in EARLY[client]]
    later = [(r[1], r[3], r[4]) for m in (7, 8, 9, 10) for r in D.ORDERS[m] if r[2] == client]
    rows = sorted(early + later)
    return [(d, i, n, D.PRICE[i], n * D.PRICE[i]) for d, i, n in rows]


def quote_pdf(path, client, q, title):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas

    if "Malgun" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("Malgun", str(FONT)))
        pdfmetrics.registerFont(TTFont("MalgunBd", str(FONT_BD)))
    dept, rank, name = CONTACT[client]
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, invariant=1)
    c.setTitle(title)
    w, h = A4
    c.setFont("MalgunBd", 20)
    c.drawCentredString(w / 2, h - 80, title)
    c.setFont("Malgun", 10)
    y = h - 120
    for line in [f"견적번호: {q['no']}", f"견적일: {q['date']}", f"수신: {client} {dept} {name} {rank}",
                 f"발신: 누리상사 영업관리팀 {STAFF[client]}", "유효기간: 견적일로부터 30일"]:
        c.drawString(60, y, line)
        y -= 16
    y -= 10
    cols = [60, 250, 340, 430]
    c.setFont("MalgunBd", 10)
    for x, t in zip(cols, ["품목", "수량", "단가(원)", "금액(원)"]):
        c.drawString(x, y, t)
    c.line(60, y - 5, 535, y - 5)
    y -= 22
    c.setFont("Malgun", 10)
    for item, n, p in q["items"]:
        c.drawString(cols[0], y, item)
        c.drawRightString(cols[1] + 60, y, f"{n:,}")
        c.drawRightString(cols[2] + 60, y, f"{p:,}")
        c.drawRightString(cols[3] + 100, y, f"{n * p:,}")
        y -= 18
    c.line(60, y + 8, 535, y + 8)
    s, v, t = D.quote_totals(q)
    for label, val, bold in [("공급가액", s, False), ("부가세(10%)", v, False), ("합계", t, True)]:
        y -= 16
        c.setFont("MalgunBd" if bold else "Malgun", 11 if bold else 10)
        c.drawString(cols[2], y, label)
        c.drawRightString(cols[3] + 100, y, f"{val:,}")
    c.setFont("Malgun", 8)
    c.drawString(60, 50, D.NOTE)
    c.showPage()
    c.save()
    path.write_bytes(buf.getvalue())


def wd(d):
    return WD[dt.date.fromisoformat(d).weekday()]


SKILL_EXAMPLE = """---
name: monthly-report
description: 새 달 주문 CSV로 월간 주문 정리와 Claude Docs 월간 주문 보고서를 만들 때 쓴다.
argument-hint: [YYYY-MM]
---

# 월간 주문 보고 ($ARGUMENTS)

1. '원본/월별주문'에서 $ARGUMENTS 달의 주문 CSV를 찾아 'scripts/주문정리.py'로 정리한다. 새로 짜지 않는다.
2. Claude Docs로 'YYYY년 M월 월간 주문 보고서'를 만든다.
   1) 요약: 주문 건수, 판매 합계, 전월 대비 금액·%
   2) 7월부터 월별 추이 표
   3) 거래처 상위 3곳 표(거래처/담당자/판매 금액/그 달 합계 대비 비중)와 3곳 합 비중 한 줄
   4) 그 달 수량이 비어 빠진 주문번호
3. 끝나면 주문 건수, 판매 합계, 전월 대비와 Docs 링크를 채팅에 보여 준다.

- 발표자료(Claude Slides)는 따로 요청할 때만 만든다.
"""

CHECKER_EXAMPLE = """---
name: checker
description: 월간 정리 결과와 보고서 숫자를 원본 주문 CSV와 대조해 검산할 때 쓴다.
tools: Read, Grep, Glob
---

너는 검산 담당이다. 파일을 고치거나 명령을 실행하지 않는다.
- 원본 CSV를 직접 다시 세어 '항목 / 받은 값 / 다시 센 값 / 일치' 대조표로 답한다.
- 안 맞으면 어디서 어긋났는지 적고, 고치지 않는다.
"""


def main(out):
    out = Path(out) / "05_스킬과_서브에이전트"
    A = check_data()
    t = {m: A[m]["total"] for m in (7, 8, 9, 10, 11)}
    a10, a11 = A[10], A[11]

    # ---- 실습 1: /monthly-report 2026-11 = 4교시 11월 정답, 이름 없이 10월 = 3교시 정답
    top11 = a11["top_clients"][:3]
    assert (a11["raw"], a11["dup"], a11["blank"], a11["clean"], t[11]) == (24, 1, 1, 22, 10_110_000)
    assert a11["blank_no"] == ["NR-2611-023"] and D.MESS[11]["exact"] == ["NR-2611-012"]
    assert top11 == [("윤슬찬푸드", 3_335_000), ("온기베이커리", 1_850_000), ("다온밀키트", 1_038_000)]
    assert [a11["staff"][c] for c, _ in top11] == ["김도현", "김도현", "박준영"]
    assert [pct(a, t[11]) for _, a in top11] == [33.0, 18.3, 10.3]
    s3 = sum(a for _, a in top11)
    assert s3 == 6_223_000 and pct(s3, t[11]) == 61.6
    x = s3 / t[11] * 1000
    assert abs(x - int(x) - 0.5) > 0.02  # 61.55 경계에서 떨어져 있음 (615.53)
    for _, a in top11:
        y = a / t[11] * 1000
        assert abs(y - int(y) - 0.5) > 0.1, a
    assert t[11] - t[10] == 725_500 and pct(t[11] - t[10], t[10]) == 7.7
    assert [A[m]["clean"] for m in (7, 8, 9, 10, 11)] == [18, 19, 21, 20, 22]
    assert sum(A[m]["clean"] for m in (7, 8, 9, 10, 11)) == 100
    assert len(set(a for _, a in a11["top_clients"][:4])) == 4
    top10 = a10["top_clients"][:3]
    assert (a10["clean"], t[10]) == (20, 9_384_500) and t[10] - t[9] == -2_291_000 and pct(t[10] - t[9], t[9]) == -19.6
    assert top10 == [("해든푸드", 1_688_000), ("온기베이커리", 1_438_000), ("한결유업", 1_230_000)]
    assert [pct(a, t[10]) for _, a in top10] == [18.0, 15.3, 13.1] and pct(sum(a for _, a in top10), t[10]) == 46.4
    assert a10["blank_no"] == ["NR-2610-021"]

    # ---- 실습 3: 거래처 3곳 비교
    s1, v1, tq1 = D.quote_totals(D.QUOTE_2)
    yun = D.answers()
    assert (tq1, yun["trade_count"], yun["trade_sum"]) == (3_668_500, 11, 9_940_000)  # 1교시 실습 2 정답
    cmp = {"윤슬찬푸드": (STAFF["윤슬찬푸드"], tq1, yun["trade_count"], yun["trade_sum"])}
    for c in ("다솜제과", "해든푸드"):
        tr = trades(c)
        cmp[c] = (STAFF[c], D.quote_totals(QUOTES[c])[2], len(tr), sum(r[4] for r in tr))
    assert cmp["다솜제과"] == ("이수아", 1_828_200, 6, 2_542_000), cmp["다솜제과"]
    assert cmp["해든푸드"] == ("박준영", 2_471_700, 12, 6_760_000), cmp["해든푸드"]
    assert D.quote_totals(QUOTES["다솜제과"]) == (1_662_000, 166_200, 1_828_200)
    assert D.quote_totals(QUOTES["해든푸드"]) == (2_247_000, 224_700, 2_471_700)
    for k in (1, 2, 3):  # 동률 없음
        assert len({v[k] for v in cmp.values()}) == 3
    assert max(cmp, key=lambda c: cmp[c][3]) == "윤슬찬푸드"
    assert max(cmp, key=lambda c: cmp[c][2]) == "해든푸드"
    # 날짜·요일 (주말·공휴일 아님, 거래내역은 1~10월)
    for c in ("다솜제과", "해든푸드"):
        for d, *_ in trades(c):
            assert "2026-01-01" <= d <= "2026-10-31" and dt.date.fromisoformat(d).weekday() < 5 and d not in HOL5, d
        assert dt.date.fromisoformat(QUOTES[c]["date"]).weekday() < 5 and QUOTES[c]["date"] not in HOL5
    assert [wd(d) for d in ("2026-11-03", "2026-11-05", "2026-12-01", "2026-10-20", "2026-10-26", "2026-11-06")] == \
        ["화", "목", "화", "화", "월", "금"]
    assert wd("2026-10-27") == "화"
    # 진행 중인 메모의 숫자 = 견적서 품목
    assert [(i, n) for i, n, _ in QUOTES["다솜제과"]["items"]] == [("골판지 박스(소)", 3000), ("식품 라벨 스티커", 30), ("포장 테이프(투명)", 100)]
    assert [(i, n) for i, n, _ in QUOTES["해든푸드"]["items"]] == [("아이스팩(500g)", 2500), ("보냉 박스(스티로폼)", 500), ("식품용 비닐 롤백", 40)]
    for c in QUOTES:
        assert all(p == D.PRICE[i] for i, _, p in QUOTES[c]["items"])

    # ---- 파일 쓰기
    for sub in ("학습자용", "강사용"):
        if (out / sub).exists():
            shutil.rmtree(out / sub)
    learn = out / "학습자용"
    learn.mkdir(parents=True)
    for c in ("다솜제과", "해든푸드"):
        cdir = learn / f"거래처_{c}"
        cdir.mkdir()
        q = QUOTES[c]
        quote_pdf(cdir / f"견적서_{c}_{q['date']}.pdf", c, q, "견 적 서")
        xlsx(cdir / f"거래내역_{c}_2026.xlsx", "2026", ["거래일", "품목", "수량", "단가(원)", "공급가액(원)"],
             trades(c), [12, 20, 10, 12, 16], money=(3, 4, 5))
        text(cdir / MEMO_FILE[c], MEMOS[c])
        # 다시 읽어 확인
        assert load_workbook(cdir / f"거래내역_{c}_2026.xlsx").active.max_row - 1 == cmp[c][2]
        from pypdf import PdfReader
        assert f"{cmp[c][1]:,}" in PdfReader(str(cdir / f"견적서_{c}_{q['date']}.pdf")).pages[0].extract_text()
        assert len(list(cdir.iterdir())) == 3

    zpath = learn / "5교시_거래처폴더.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for c in ("다솜제과", "해든푸드"):
            for p in sorted((learn / f"거래처_{c}").rglob("*")):
                z.write(p, p.relative_to(learn).as_posix())
    with zipfile.ZipFile(zpath) as z:
        assert len(z.namelist()) == 6
    text(learn / "실습_요청문.txt", REQUESTS)

    teach = out / "강사용"
    text(teach / "예시_SKILL_monthly-report.md", SKILL_EXAMPLE)
    text(teach / "예시_checker.md", CHECKER_EXAMPLE)

    top_line = lambda a, tops, tt: " / ".join(f"{c}({a['staff'][c]}) {v:,}원 {pct(v, tt)}%" for c, v in tops)
    rows3 = "\n".join(f"  {c}: 담당 {s} / 최근 견적 합계 {q:,}원 / 거래 {n}건 / 공급가액 합계 {tot:,}원"
                      for c, (s, q, n, tot) in cmp.items())
    key = f"""[5교시 정답] 누리상사 영업관리팀 (강사용, 배포하지 않음)

시작 상태: 4교시 결과물(출력/주문_정리본.csv 100행, scripts/주문정리.py, CLAUDE.md 작업 규칙 4줄 + 월간 주문 정리 + 스크립트 한 줄)

실습 1 스킬 (monthly-report)
- .claude/skills/monthly-report/SKILL.md: 맨 위 name·description, 본문 단계 3개(스크립트 → Docs → 채팅 보고), 달 자리($ARGUMENTS 등)
  예시: 예시_SKILL_monthly-report.md (Claude가 쓴 내용은 매번 다름)
- CLAUDE.md: '월간 주문 정리' 항목이 없어지고 작업 규칙 5줄(4줄 + '/monthly-report 스킬로' 한 줄)
- /monthly-report 2026-11 (4교시 11월 정답과 같음)
  스크립트: 합치기 전 24행 / 중복 1행 NR-2611-012 · 수량 빈칸 1행 NR-2611-023 / 정리 후 22행 / {t[11]:,}원
  정리본 그대로 100행 (11월을 지우고 새로 씀)
  Docs '2026년 11월 월간 주문 보고서'
    1) 22건, {t[11]:,}원, 10월 대비 {t[11] - t[10]:+,}원 ({pct(t[11] - t[10], t[10]):+}%)
    2) 7월 18건 {t[7]:,} / 8월 19건 {t[8]:,} / 9월 21건 {t[9]:,} / 10월 20건 {t[10]:,} / 11월 22건 {t[11]:,}
    3) {top_line(a11, top11, t[11])}  (3곳 합 {pct(s3, t[11])}%)
    4) NR-2611-023
- 이름 없이 '10월 월간 보고 만들어 줘' (3교시 10월 정답과 같음): 진행 기록에 monthly-report를 쓴 줄
  20건, {t[10]:,}원, 9월 대비 {t[10] - t[9]:+,}원 ({pct(t[10] - t[9], t[9]):+}%) / {top_line(a10, top10, t[10])} (3곳 합 46.4%) / NR-2610-021
  월별 추이 7~10월 4줄
- 다르게 나오면: 정리본 122행 = 11월이 두 번 들어감 / 11월 23행·10,930,000 = 중복을 안 뺌(스크립트 대신 새로 짰을 수 있음)

실습 2 서브에이전트 (checker)
- .claude/agents/checker.md: name checker, description, tools Read, Grep, Glob, 아래 지시. 예시: 예시_checker.md
- 새 세션에서 맡긴 검산 대조표: 합치기 전 24 / 중복 NR-2611-012 / 수량 빈칸 NR-2611-023 / 정리 후 22 / {t[11]:,}원 /
  상위 3곳 윤슬찬푸드 3,335,000 · 온기베이커리 1,850,000 · 다온밀키트 1,038,000 → 모두 일치
- 메인 세션 진행 기록에는 원본 CSV를 읽는 줄이 없고 서브에이전트 호출과 결과만. checker는 파일을 쓰지 않음

실습 3 병렬 (거래처 폴더 3곳, 윤슬찬푸드는 1교시 폴더)
{rows3}
- 공급가액 합계 1위 윤슬찬푸드, 거래 건수 1위 해든푸드 (12건)
- 진행 중인 일: 윤슬찬푸드 = 10/22 수정 견적 회신 대기, 11/5(목) 첫 납품 / 다솜제과 = 연말 선물세트용 견적 11/5(목) 송부, 12/1(화) 첫 납품 희망, 로고 인쇄 확인
  / 해든푸드 = 10/26(월) 견적 회신 대기, 보냉 박스 11월 셋째 주 납기 확인(기한 11/6(금))
- 다르게 나오면: 윤슬찬푸드 견적 3,602,500 = 1차 견적을 읽음 / 거래 건수 12·7·13 = 머리글까지 셈
- 파일: 출력/2026-11_거래처3곳비교.md
"""
    text(teach / "정답_5교시.txt", key)
    print(key)


REQUESTS = open(Path(__file__).with_name("requests_05.txt"), encoding="utf-8").read()

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "..")
