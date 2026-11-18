"""바이브코딩 심화 - 소담상점 2024 샘플 매출 엑셀과 정답 합계표 만들기.

교안에 고정된 값(과정 설명 페이지 결정 24·29·36·39·44, 검토 G-05)을 지킨다.
- 상반기: 날짜순, 깨끗한 값. 첫 6행은 2-2 토글과 같음. 1월 2·3일 행은 첫 4행뿐.
- 하반기: 첫 5행은 2-7 토글과 같음(3번째는 빈 행). 7월 1·2일 행은 그 4행뿐.
  일부러 지저분한 값: 날짜 일련번호(일반 서식 숫자), 쉼표 섞인 글자 금액, 빈 행,
  플랫폼 표기 흔들림("스마트 스토어", "쿠팡 ").
- 금액은 모두 수량×단가. 플랫폼·상품·월 합계에 동률 없음.
- 기간 경계 날짜 행 포함: 03-01, 03-31, 06-30 / 07-01, 09-30, 12-31.
  (01-01은 첫 행이 01-02로 고정이라 넣지 않음 - 신정 휴무로 둠)
- 주문번호(맨 앞 칸): 날짜 YYMMDD-그날 순번 3자리(예 240102-001), 한 행 = 주문 상품 하나라 행마다 다름.
  두 파일 사이에도 겹치지 않음. 서비스는 (사용자, 주문번호)로 중복을 막고 덮어씀.
실행: py -3 make_samples.py  (같은 시드라 몇 번을 돌려도 같은 파일)
"""
import random
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

OUT = Path(__file__).resolve().parent.parent / "samples"
HEADER = ["주문번호", "날짜", "플랫폼", "상품", "수량", "단가", "금액", "주문자"]
PLATFORMS = ["스마트스토어", "쿠팡", "자사몰"]
PRODUCTS = {  # 교안에 나온 6개 + 추가 3개
    "대나무 칫솔 4개입": 6900,
    "면 행주 5매": 8900,
    "유리 밀폐용기 3종": 24000,
    "천연 수세미 3개입": 4500,
    "리필 주방세제 1L": 7800,
    "원목 도마": 19000,
    "밀랍 랩 3종": 12000,
    "스테인리스 빨대 세트": 8500,
    "소창 행주 2매": 11000,
}
SURNAMES = "김이박최정강조윤장임한오서신권황안송류홍"
GIVEN = ["하늘", "서준", "수아", "민재", "유나", "도윤", "지호", "예린", "민서", "태윤",
         "지우", "서연", "하준", "채원", "시우", "다은", "윤서", "건우", "소율", "현우",
         "지안", "은호", "나연", "주원", "하린", "도현", "서아", "준서", "예준", "가은"]

H1_FIXED = [  # 2-2 토글 (날짜, 플랫폼, 상품, 수량, 주문자)
    (date(2024, 1, 2), "스마트스토어", "대나무 칫솔 4개입", 2, "김하늘"),
    (date(2024, 1, 2), "쿠팡", "면 행주 5매", 1, "박서준"),
    (date(2024, 1, 3), "자사몰", "유리 밀폐용기 3종", 1, "이수아"),
    (date(2024, 1, 3), "쿠팡", "천연 수세미 3개입", 3, "최민재"),
    (date(2024, 1, 4), "스마트스토어", "리필 주방세제 1L", 2, "정유나"),
    (date(2024, 1, 5), "자사몰", "원목 도마", 1, "한도윤"),
]
# 2-7 토글: (날짜, 플랫폼 원문, 상품, 수량, 주문자, 날짜를 일련번호로, 금액을 글자로) / None = 빈 행
H2_FIXED = [
    (date(2024, 7, 1), "스마트스토어", "대나무 칫솔 4개입", 1, "윤지호", False, False),
    (date(2024, 7, 1), "쿠팡 ", "면 행주 5매", 2, "서예린", True, True),
    None,
    (date(2024, 7, 2), "스마트 스토어", "원목 도마", 1, "강민서", False, True),
    (date(2024, 7, 2), "자사몰", "유리 밀폐용기 3종", 1, "오태윤", True, False),
]
EXCEL_EPOCH = date(1899, 12, 30)


_seq = Counter()


def order_no(d):
    _seq[d] += 1
    return f"{d:%y%m%d}-{_seq[d]:03d}"


def serial(d):
    return (d - EXCEL_EPOCH).days


def name(rng):
    return rng.choice(SURNAMES) + rng.choice(GIVEN)


def random_rows(rng, start, end, n, must_dates):
    """start~end(포함) 사이 n행. must_dates의 날짜에는 최소 1행."""
    days = [start + timedelta(i) for i in range((end - start).days + 1)]
    picked = list(must_dates) + [rng.choice(days) for _ in range(n - len(must_dates))]
    prod_w = [9, 12, 6, 10, 11, 5, 7, 8, 4]  # 상품마다 팔리는 정도를 다르게
    plat_w = [5, 4, 3]
    rows = []
    for d in sorted(picked):
        prod = rng.choices(list(PRODUCTS), weights=prod_w)[0]
        plat = rng.choices(PLATFORMS, weights=plat_w)[0]
        qty = rng.choices([1, 2, 3, 4, 5], weights=[50, 28, 12, 6, 4])[0]
        rows.append((d, plat, prod, qty, name(rng)))
    return rows


def totals(rows):
    """rows: (date, 정리된 플랫폼, 상품, 수량, 금액)"""
    t = {"행 수": len(rows), "합계": sum(r[4] for r in rows)}
    by_month, by_plat, by_prod, by_day = Counter(), Counter(), Counter(), Counter()
    mar_coupang = 0
    for d, p, prod, q, amt in rows:
        by_month[d.month] += amt
        by_plat[p] += amt
        by_prod[prod] += amt
        by_day[d] += amt
        if d.month == 3 and p == "쿠팡":
            mar_coupang += amt
    return t, by_month, by_plat, by_prod, by_day, mar_coupang


def no_ties(counter):
    v = list(counter.values())
    return len(v) == len(set(v))


def build(seed):
    rng = random.Random(seed)
    # 상반기: 첫 6행 고정, 나머지는 1-05 이후(1-05는 고정 6행째와 같은 날 허용)
    h1_rest = random_rows(rng, date(2024, 1, 5), date(2024, 6, 30), 514,
                         [date(2024, 3, 1), date(2024, 3, 31), date(2024, 6, 30)])
    h1 = H1_FIXED + h1_rest
    # 하반기: 고정 5행 뒤 7-03 이후
    h2_rest = random_rows(rng, date(2024, 7, 3), date(2024, 12, 31), 492,
                          [date(2024, 9, 30), date(2024, 12, 31)])
    return rng, h1, h2_rest


def h1_clean(h1):
    return [(d, p, prod, q, q * PRODUCTS[prod]) for d, p, prod, q, _ in h1]


def main():
    seed = 2024
    while True:  # 동률이 없을 때까지 시드를 올림
        rng, h1, h2_rest = build(seed)
        c1 = h1_clean(h1)
        c2 = [(d, p, prod, q, q * PRODUCTS[prod]) for d, p, prod, q, _ in h2_rest]
        fixed2 = [(r[0], r[1].replace(" ", ""), r[2], r[3], r[3] * PRODUCTS[r[2]])
                  for r in H2_FIXED if r]
        ok = True
        for rows in (c1, fixed2 + c2, c1 + fixed2 + c2):
            _, m, pl, pr, _, _ = totals(rows)
            ok &= no_ties(m) and no_ties(pl) and no_ties(pr)
        if ok:
            break
        seed += 1

    OUT.mkdir(parents=True, exist_ok=True)
    date_fmt = "yyyy-mm-dd"

    # ---- 상반기 (깨끗) ----
    wb = Workbook(); ws = wb.active; ws.title = "매출"
    ws.append(HEADER)
    for d, p, prod, q, who in h1:
        ws.append([order_no(d), datetime(d.year, d.month, d.day), p, prod, q, PRODUCTS[prod], q * PRODUCTS[prod], who])
        ws.cell(ws.max_row, 2).number_format = date_fmt
    style(ws); wb.save(OUT / "소담상점_2024_상반기.xlsx")

    # ---- 하반기 (지저분) ----
    rng2 = random.Random(seed + 1000)
    wb = Workbook(); ws = wb.active; ws.title = "매출"
    ws.append(HEADER)
    h2_written = []  # 정리된 값 (date, platform, prod, qty, amt)
    def put(d, plat_raw, prod, q, who, as_serial, as_text):
        amt = q * PRODUCTS[prod]
        dv = serial(d) if as_serial else datetime(d.year, d.month, d.day)
        av = f"{amt:,}" if as_text else amt
        ws.append([order_no(d), dv, plat_raw, prod, q, PRODUCTS[prod], av, who])
        c = ws.cell(ws.max_row, 2)
        c.number_format = "General" if as_serial else date_fmt
        if as_text:
            ws.cell(ws.max_row, 7).number_format = "@"
        h2_written.append((d, plat_raw.replace(" ", ""), prod, q, amt))
    for r in H2_FIXED:
        if r is None:
            ws.append([None] * 8)
        else:
            put(*r)
    blank_after = set(rng2.sample(range(20, len(h2_rest) - 5), 5))
    for i, (d, p, prod, q, who) in enumerate(h2_rest):
        roll = rng2.random()
        plat_raw = p
        if p == "스마트스토어" and roll < 0.12:
            plat_raw = "스마트 스토어"
        elif p == "쿠팡" and roll < 0.12:
            plat_raw = "쿠팡 "
        put(d, plat_raw, prod, q, who, rng2.random() < 0.15, rng2.random() < 0.15)
        if i in blank_after:
            ws.append([None] * 8)
    style(ws); wb.save(OUT / "소담상점_2024_하반기.xlsx")

    # ---- 정답 합계표 (한 파일, 상반기·하반기 칸) ----
    t1, m1, pl1, pr1, d1, mc1 = totals(c1)
    t2, m2, pl2, pr2, d2, mc2 = totals(h2_written)
    blank_rows = 1 + len(blank_after)
    wb = Workbook(); ws = wb.active; ws.title = "정답 합계표"
    ws.append(["소담상점 2024년 정답 합계표 (가상 데이터, 금액 단위 원)"])
    ws.append([])
    ws.append(["항목", "상반기 (1~6월)", "하반기 (7~12월)"])
    rows = [
        ("행 수 (빈 행 제외)", t1["행 수"], t2["행 수"]),
        ("합계", t1["합계"], t2["합계"]),
        ("3월 합계", m1[3], None),
        ("3월 · 쿠팡 합계", mc1, None),
    ]
    for p in PLATFORMS:
        rows.append((f"플랫폼별 - {p}", pl1[p], pl2[p]))
    for r in rows:
        ws.append(list(r))
    ws.append([])
    ws.append(["월별 합계", "월", "합계"])
    for mth in range(1, 13):
        ws.append(["", f"{mth}월", (m1 if mth <= 6 else m2)[mth]])
    ws.append([])
    ws.append(["상품별 합계", "상반기", "하반기"])
    for prod in PRODUCTS:
        ws.append([prod, pr1[prod], pr2[prod]])
    ws.append([])
    ws.append(["일별 대조값", "날짜", "합계"])
    for dd, src in [(date(2024, 1, 2), d1), (date(2024, 1, 3), d1), (date(2024, 7, 1), d2), (date(2024, 7, 2), d2)]:
        ws.append(["", dd.isoformat(), src[dd]])
    ws.append([])
    ws.append(["참고", "하반기 파일의 빈 행 수", blank_rows])
    for row in ws.iter_rows(min_row=1):
        for c in row:
            if isinstance(c.value, int):
                c.number_format = "#,##0"
    ws["A1"].font = Font(bold=True, size=12)
    for col, w in zip("ABC", [26, 18, 18]):
        ws.column_dimensions[col].width = w
    for r in ws.iter_rows():
        if r[0].value in ("항목", "월별 합계", "상품별 합계", "일별 대조값"):
            for c in r:
                c.font = Font(bold=True)
                c.fill = PatternFill("solid", fgColor="E8F5E9")
    wb.save(OUT / "소담상점_2024_정답합계표.xlsx")

    print("seed", seed)
    print("상반기", t1, "3월", m1[3], "3월쿠팡", mc1, dict(pl1))
    print("하반기", t2, dict(pl2), "빈 행", blank_rows)
    print("월별", {k: v for k, v in sorted((m1 + m2).items())})
    print("일별", d1[date(2024, 1, 2)], d1[date(2024, 1, 3)], d2[date(2024, 7, 1)], d2[date(2024, 7, 2)])


def style(ws):
    for c in ws[1]:
        c.font = Font(bold=True)
        c.fill = PatternFill("solid", fgColor="E8F5E9")
        c.alignment = Alignment(horizontal="center")
    for col, w in zip("ABCDEFGH", [12, 12, 14, 20, 6, 9, 10, 9]):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "A2"


if __name__ == "__main__":
    main()
