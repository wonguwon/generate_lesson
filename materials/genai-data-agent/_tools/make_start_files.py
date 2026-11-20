"""차시별 시작 파일(지난 시간을 못 따라온 학습자용)을 만든다.

실행:
    _tools/.venv/Scripts/python.exe _tools/make_start_files.py

- 정제는 check_data.py의 clean()과 같은 규칙(정제 규칙 1~10, 14주차부터 규칙 11)을 이 파일에 옮겨 와 쓴다.
  check_data.py는 import하면 data_facts.md를 다시 쓰므로 import하지 않는다.
- 리뷰 라벨은 강사용 정답표를 쓴다: 표본 200개는 _tools/reviews_sample_200_answer.csv,
  리뷰 전체는 _tools/answer_key.csv(사본이 아닌 행, order_id로 붙임).
- 처리기록.md의 처리한 날은 주차가 끝난 다음 월요일로 고정한다(아래 PROC_DATE).
- 무작위 요소는 없다. xlsx·zip 안의 시각은 고정값이라 같은 패키지 버전이면 같은 내용이 나온다.
- 만든 파일을 다시 읽어 교안의 확인할 것 숫자와 맞춰 보고, 하나라도 다르면 종료 코드 1로 끝난다.

결과(materials/genai-data-agent/lesson_files/start/):
    03_정제파일/orders_2025_w01-12_clean.csv
    04_리뷰기준표/리뷰기준표.md
    05_결과시트/analysis_summary.xlsx
    06_대시보드/index.html
    07_드라이브시작/배달주문_실습/ (폴더) · 07차시_시작_배달주문_실습.zip
    08차시_시작_배달주문_실습.zip · 09차시_시작_배달주문_실습.zip · 10차시_시작_배달주문_실습.zip
"""

import html
import io
import re
import shutil
import sys
import zipfile
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from html.parser import HTMLParser
from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd
from openpyxl.styles import Font

sys.stdout.reconfigure(encoding="utf-8")

TOOLS = Path(__file__).resolve().parent
BASE = TOOLS.parent
DATA = BASE / "data"
LF = BASE / "lesson_files"
START = LF / "start"

FILES = ["w01-12", "w13", "w14", "w15"]
FNAME = {f: f"orders_2025_{f}.csv" for f in FILES}
PROC_DATE = {"w13": "2025-06-02", "w14": "2025-06-09", "w15": "2025-06-16"}  # 주차가 끝난 다음 월요일
RULE11_FROM = "w14"  # 규칙 11은 8차시(14주차)에 생김
WEEK1 = pd.Timestamp("2025-03-03")
MIDTERM = (pd.Timestamp("2025-04-21"), pd.Timestamp("2025-04-25"))
FIXED_TIME = (2025, 6, 2, 9, 0, 0)

COLS = ["order_id", "order_datetime", "store_id", "store_name", "category", "menu", "quantity", "unit_price",
        "delivery_fee", "discount", "total_amount", "payment_method", "delivery_area", "customer_id",
        "delivery_minutes", "status", "rating", "review_text"]
INT_COLS = ["quantity", "unit_price", "delivery_fee", "discount", "total_amount", "delivery_minutes", "rating"]
CATS = ["치킨", "분식", "한식", "중식", "피자", "카페디저트", "야식"]
BOOST = ["야식", "치킨", "카페디저트"]
AREAS = ["기숙사", "정문", "후문", "쪽문", "원룸촌", "미상"]
DOW_KO = ["월", "화", "수", "목", "금", "토", "일"]
HOURS = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 0, 1]
TOPICS = ["맛", "배달", "양", "포장", "가격", "기타"]
SENTS = ["긍정", "부정", "중립"]

CAT_MAP = {"chicken": "치킨", "pizza": "피자", "카페/디저트": "카페디저트", "카페 디저트": "카페디저트"}
PAY_MAP = {"신용카드": "카드", "card": "카드", "간편 결제": "간편결제"}
AREA_MAP = {"정문앞": "정문", "정문 앞": "정문", "후문 앞": "후문", "원룸": "원룸촌"}
NEW_RULES = {"category": {"떡볶이": "분식"}, "payment_method": {"페이": "간편결제"}}

FAILS: list = []


def expect(name, got, want):
    ok = got == want
    print(f"  {'OK ' if ok else 'FAIL'} {name}: {got!r}" + ("" if ok else f" (교안 {want!r})"))
    if not ok:
        FAILS.append(name)


def r_half(x, nd=0):
    q = Decimal(1).scaleb(-nd)
    v = Decimal(str(x)).quantize(q, rounding=ROUND_HALF_UP)
    return int(v) if nd == 0 else float(v)


# ---------------------------------------------------------------------------
# 정제(check_data.py의 parse_dt·num·computed·clean을 옮겨 와 규칙별 숫자를 더 셈)
# ---------------------------------------------------------------------------
DT_STD = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")
DT_DOT = re.compile(r"^\d{4}\.\d{1,2}\.\d{1,2} \d{2}:\d{2}$")
DT_US = re.compile(r"^\d{2}/\d{2}/\d{4} \d{1,2}:\d{2} (AM|PM)$")


def parse_dt(s: pd.Series) -> pd.Series:
    out = pd.Series(pd.NaT, index=s.index, dtype="datetime64[ns]")
    for fmt, rx in (("%Y-%m-%d %H:%M", DT_STD), ("%Y.%m.%d %H:%M", DT_DOT), ("%m/%d/%Y %I:%M %p", DT_US)):
        m = s.str.match(rx)
        out[m] = pd.to_datetime(s[m], format=fmt)
    return out


def num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.str.replace(",", "", regex=False).str.replace("원", "", regex=False), errors="coerce")


def computed(df) -> pd.Series:
    c = df.quantity * df.unit_price + df.delivery_fee - df.discount
    return c.where(df.status != "환불", -c)


def clean(df_raw: pd.DataFrame, rule11: bool):
    st = {"raw": len(df_raw)}
    d = df_raw.copy()
    # 1. 완전히 같은 행
    dup = d.duplicated()
    st["r1"] = int(dup.sum())
    d = d[~dup].copy()
    # 2. 형식
    bad_dt = ~d.order_datetime.str.match(DT_STD)
    bad_amt = ~d.total_amount.str.fullmatch(r"-?\d+")
    st["r2_dt"], st["r2_amt"], st["r2"] = int(bad_dt.sum()), int(bad_amt.sum()), int((bad_dt | bad_amt).sum())
    d["order_datetime"] = parse_dt(d.order_datetime)
    assert d.order_datetime.notna().all(), "읽지 못한 날짜"
    for c in ["quantity", "unit_price", "delivery_fee", "discount", "delivery_minutes", "rating"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d["total_amount"] = num(d.total_amount)
    assert d.total_amount.notna().all()
    # 3. 표기
    before = d[["category", "payment_method", "delivery_area"]].copy()
    for c in ["category", "payment_method", "delivery_area"]:
        d[c] = d[c].str.strip()
    d["category"] = d.category.replace(CAT_MAP)
    d["payment_method"] = d.payment_method.replace(PAY_MAP)
    d["delivery_area"] = d.delivery_area.replace(AREA_MAP)
    ch = before != d[["category", "payment_method", "delivery_area"]]
    st["r3_cat"], st["r3_pay"], st["r3_area"] = (int(ch[c].sum()) for c in ch.columns)
    st["r3"] = int(ch.any(axis=1).sum())
    # 4. 같은 order_id에 금액만 다른 행
    calc = computed(d)
    multi = d.order_id.duplicated(keep=False)
    drop = multi & (d.total_amount != calc)
    st["r4"] = int(drop.sum())
    d = d[~drop].copy()
    assert not d.order_id.duplicated().any()
    # 5. 수량 0
    q0 = d.quantity == 0
    st["r5"] = int(q0.sum())
    d = d[~q0].copy()
    # 6. 계산 불일치
    calc = computed(d)
    mis = d.total_amount != calc
    st["r6"] = int(mis.sum())
    d.loc[mis, "total_amount"] = calc[mis]
    # 7. 배달 999분·0분
    m999, m0 = d.delivery_minutes == 999, d.delivery_minutes == 0
    st["r7_999"], st["r7_0"] = int(m999.sum()), int(m0.sum())
    d.loc[m999 | m0, "delivery_minutes"] = np.nan
    # 8. 지역 빈칸
    blank = d.delivery_area == ""
    st["r8"] = int(blank.sum())
    d.loc[blank, "delivery_area"] = "미상"
    # 9·10. 그대로
    st["cancel"], st["refund"] = int((d.status == "취소").sum()), int((d.status == "환불").sum())
    # 11. 새 표기(14주차부터)
    st["r11_cat"] = st["r11_pay"] = st["r11"] = 0
    if rule11:
        st["r11"] = int((d.category.isin(list(NEW_RULES["category"])) | d.payment_method.isin(list(NEW_RULES["payment_method"]))).sum())
        for c, mp in NEW_RULES.items():
            m = d[c].isin(list(mp))
            st["r11_cat" if c == "category" else "r11_pay"] = int(m.sum())
            d[c] = d[c].replace(mp)
    st["clean"] = len(d)
    return d.reset_index(drop=True), st


def to_csv_bytes(d: pd.DataFrame) -> bytes:
    out = d[COLS].copy()
    out["order_datetime"] = out.order_datetime.dt.strftime("%Y-%m-%d %H:%M")
    for c in INT_COLS:
        out[c] = out[c].astype("Int64")
    buf = io.StringIO()
    out.to_csv(buf, index=False, lineterminator="\n")
    return ("﻿" + buf.getvalue()).encode("utf-8")


# ---------------------------------------------------------------------------
# 읽기·정제·누적
# ---------------------------------------------------------------------------
raw = {f: pd.read_csv(DATA / FNAME[f], dtype=str, keep_default_na=False, encoding="utf-8-sig") for f in FILES}
cl, stats = {}, {}
for f in FILES:
    cl[f], stats[f] = clean(raw[f], rule11=FILES.index(f) >= FILES.index(RULE11_FROM))

states = {}  # 'w12','w13','w14','w15' -> 누적 DataFrame
log_rows = []
cum = cl["w01-12"].copy()
states["w12"] = cum.copy()
for f in FILES[1:]:
    new = cl[f]
    exist = new.order_id.isin(cum.order_id)
    add = new[~exist]
    cum = pd.concat([cum, add], ignore_index=True)
    stats[f].update(existing=int(exist.sum()), added=len(add), cum=len(cum),
                    existing_ids=new.loc[exist, "order_id"].tolist(),
                    existing_dates=sorted(set(new.loc[exist, "order_datetime"].dt.strftime("%Y-%m-%d"))))
    states[f] = cum.copy()

# 리뷰 라벨
key = pd.read_csv(TOOLS / "answer_key.csv", dtype=str, keep_default_na=False, encoding="utf-8-sig")
key = key[(key.is_copy == "0") & (key.sentiment != "")]
assert not key.order_id.duplicated().any()
LABEL = key.set_index("order_id")[["sentiment", "topic"]]
sample = pd.read_csv(DATA / "reviews_sample_200.csv", dtype=str, keep_default_na=False, encoding="utf-8-sig")
sample_ans = pd.read_csv(TOOLS / "reviews_sample_200_answer.csv", dtype=str, keep_default_na=False, encoding="utf-8-sig")
assert (sample.order_id == sample_ans.order_id).all()
sample = sample.assign(sentiment=sample_ans.sentiment, topic=sample_ans.topic)
sample["sample_no"] = sample.sample_no.astype(int)


def all_reviews(D):
    R = D[D.review_text != ""].sort_values("order_id").reset_index(drop=True)
    R = R[["order_id", "category", "menu", "review_text"]].copy()
    R.insert(0, "review_no", np.arange(1, len(R) + 1))
    lab = LABEL.reindex(R.order_id)
    assert lab.sentiment.notna().all(), "라벨 없는 리뷰"
    R["sentiment"], R["topic"] = lab.sentiment.values, lab.topic.values
    return R


# ---------------------------------------------------------------------------
# 결과 시트
# ---------------------------------------------------------------------------
def build_tables(D, review_mode):
    C = D[D.status == "완료"].copy()
    C["date"] = C.order_datetime.dt.normalize()
    last = D.order_datetime.max().normalize()
    nweeks = (last - WEEK1).days // 7 + 1
    period = f"2025-03-03 ~ {last:%Y-%m-%d}(1~{nweeks}주)"
    T = {}
    sales, n = int(C.total_amount.sum()), len(C)
    T["핵심지표"] = [["지표", "값", "단위"],
                 ["매출", sales, "원"], ["완료 주문 수", n, "건"], ["건당 평균 금액", r_half(sales / n), "원"],
                 ["평균 평점", r_half(D.rating.mean(), 2), "점"],
                 ["평균 배달 시간", r_half(D.delivery_minutes.mean(), 1), "분"]]
    C["week"] = (C.date - WEEK1).dt.days // 7 + 1
    rows = [["주차", "시작일", "완료 주문 수", "매출"]]
    for w in range(1, nweeks + 1):
        g = C[C.week == w]
        rows.append([w, f"{WEEK1 + pd.Timedelta(days=7 * (w - 1)):%Y-%m-%d}", len(g), int(g.total_amount.sum())])
    T["주차별"] = rows
    assert set(C.category) <= set(CATS) and set(C.delivery_area) <= set(AREAS)
    pv = C.pivot_table(index="category", columns="delivery_area", values="total_amount", aggfunc="sum", fill_value=0)
    pv = pv.reindex(index=CATS, columns=AREAS, fill_value=0)
    rows = [["카테고리"] + AREAS + ["합계"]]
    for c in CATS:
        rows.append([c] + [int(v) for v in pv.loc[c]] + [int(pv.loc[c].sum())])
    rows.append(["합계"] + [int(pv[a].sum()) for a in AREAS] + [int(pv.values.sum())])
    T["카테고리x지역"] = rows
    assert set(C.order_datetime.dt.hour) <= set(HOURS)
    hd = C.groupby([C.order_datetime.dt.hour, C.order_datetime.dt.day_of_week]).size()
    rows = [["시간대"] + DOW_KO]
    for h in HOURS:
        rows.append([f"{h}시"] + [int(hd.get((h, w), 0)) for w in range(7)])
    T["시간대x요일"] = rows
    days = C.date.drop_duplicates()
    ex_days = days[(days >= MIDTERM[0]) & (days <= MIDTERM[1])]
    base_days = days[~((days >= MIDTERM[0]) & (days <= MIDTERM[1])) & (days.dt.day_of_week < 5)]
    rows = [["묶음", "시험 기간 하루 평균", "평소 월~금 하루 평균", "배율"]]
    exam_raw = {}
    for name, cats in (("야식·치킨·카페디저트", BOOST), ("나머지 네 카테고리", [c for c in CATS if c not in BOOST])):
        x = C[C.category.isin(cats)]
        a = x.date.isin(ex_days).sum() / len(ex_days)
        b = x.date.isin(base_days).sum() / len(base_days)
        rows.append([name, r_half(a, 1), r_half(b, 1), r_half(a / b, 2)])
        exam_raw[name] = (len(ex_days), len(base_days))
    T["시험기간"] = rows
    if review_mode == "sample":
        R = sample
        rv_desc = "리뷰 표본 200개. 리뷰기준표.md(고친 기준표)로 분류하고 1~20번을 사람이 검수"
    else:
        R = all_reviews(D)
        rv_desc = f"{nweeks}주차까지 누적 리뷰 전체 {len(R):,}개. 리뷰기준표.md, 서브에이전트 분류·검토"
    ct = pd.crosstab(R.topic, R.sentiment).reindex(index=TOPICS, columns=SENTS, fill_value=0)
    rows = [["주제"] + SENTS + ["합계"]]
    for t in TOPICS:
        rows.append([t] + [int(v) for v in ct.loc[t]] + [int(ct.loc[t].sum())])
    rows.append(["합계"] + [int(ct[s].sum()) for s in SENTS] + [int(ct.values.sum())])
    T["리뷰분류"] = rows
    sc = ["sample_no", "order_id", "category", "menu", "review_text", "sentiment", "topic"]
    T["리뷰표본"] = [sc] + sample[sc].values.tolist()
    if review_mode == "all":
        rc = ["review_no", "order_id", "category", "menu", "review_text", "sentiment", "topic"]
        T["리뷰전체"] = [rc] + [[int(r[0])] + list(r[1:]) for r in R[rc].values.tolist()]
    done = "status가 완료인 주문"
    base = [["시트", "기간", "고른 주문", "단위"],
            ["핵심지표", period, "매출·완료 주문 수·건당 평균 금액은 status가 완료인 주문, 평균 평점은 평점이 있는 주문 전체, "
                                 "평균 배달 시간은 배달 시간이 있는 주문 전체", "원·건·점·분"],
            ["주차별", period + ", 1주차는 2025-03-03(월)부터 7일씩", done, "건·원"],
            ["카테고리x지역", period, done + ", 매출(total_amount 합계)", "원"],
            ["시간대x요일", period, done + ", 0시·1시는 날짜에 적힌 요일 그대로", "건"],
            ["시험기간", period + ", 시험 기간 2025-04-21~04-25(월~금), 평소는 그 밖의 월~금",
             done + ", 묶음별 하루 평균 주문 수", "건(하루 평균)·배"],
            ["리뷰분류", period, rv_desc, "개"],
            ["리뷰표본", "2025-03-03 ~ 2025-05-25(1~12주)",
             "리뷰 표본 200개. sentiment·topic은 리뷰기준표.md로 분류하고 사람이 검수한 라벨", "행"]]
    if review_mode == "all":
        base.append(["리뷰전체", period, f"review_text가 있는 주문 전체 {len(R):,}개, review_no는 order_id 오름차순. "
                                        "sentiment·topic은 리뷰기준표.md로 서브에이전트가 분류하고 검토", "행"])
    order = ["기준", "핵심지표", "주차별", "카테고리x지역", "시간대x요일", "시험기간", "리뷰분류", "리뷰표본"]
    if review_mode == "all":
        order.append("리뷰전체")
    T["기준"] = base
    return {k: T[k] for k in order}, dict(period=period, nweeks=nweeks, exam_days=exam_raw)


WIDTH = {"기준": [14, 52, 70, 16], "리뷰표본": [10, 10, 12, 16, 60, 10, 8], "리뷰전체": [10, 10, 12, 16, 60, 10, 8]}


def normalize_zip(data: bytes) -> bytes:
    src = zipfile.ZipFile(io.BytesIO(data))
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for info in src.infolist():
            zi = zipfile.ZipInfo(info.filename, date_time=FIXED_TIME)
            zi.compress_type = zipfile.ZIP_DEFLATED
            b = src.read(info.filename)
            if info.filename == "docProps/core.xml":  # openpyxl이 저장 시각을 modified에 넣으므로 고정값으로 바꿈
                b = re.sub(rb"(<dcterms:modified[^>]*>)[^<]*", rb"\g<1>2025-06-02T09:00:00Z", b)
            z.writestr(zi, b)
    return out.getvalue()


def xlsx_bytes(T) -> bytes:
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    wb.properties.creator = "make_start_files.py"
    wb.properties.created = wb.properties.modified = datetime(*FIXED_TIME)
    for name, rows in T.items():
        ws = wb.create_sheet(name)
        for r in rows:
            ws.append(r)
        for c in ws[1]:
            c.font = Font(bold=True)
        for i, w in enumerate(WIDTH.get(name, [14] * len(rows[0]))):
            ws.column_dimensions[openpyxl.utils.get_column_letter(i + 1)].width = w
    buf = io.BytesIO()
    wb.save(buf)
    return normalize_zip(buf.getvalue())


def read_xlsx(data: bytes):
    wb = openpyxl.load_workbook(io.BytesIO(data))
    return {ws.title: [list(r) for r in ws.iter_rows(values_only=True)] for ws in wb.worksheets}


# ---------------------------------------------------------------------------
# 대시보드(파일 하나, 인터넷에서 불러오는 것 없음, 숫자는 결과 시트 값만)
# ---------------------------------------------------------------------------
SRC_SAMPLE = "숫자 출처 analysis_summary.xlsx, 리뷰는 표본 200개를 분류한 결과"
SRC_ALL = "숫자 출처 analysis_summary.xlsx, 리뷰는 리뷰분류 시트의 리뷰 전체를 분류한 결과"
COL_POS, COL_NEG, COL_NEU = "#2a78d6", "#eb6834", "#a8a7a0"


def esc(s):
    return html.escape(str(s), quote=True)


def mix(c1, c2, t):
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def chart1(rows):
    data = rows[1:]
    W, H, L, R_, T_, B = 640, 300, 24, 24, 40, 44
    ys = [r[2] for r in data]
    lo, hi = min(ys), max(ys)
    span = max(hi - lo, 1)
    lo, hi = lo - span * 0.6, hi + span * 0.25
    xs = [L + (W - L - R_) * (i / max(len(data) - 1, 1)) for i in range(len(data))]
    yv = [T_ + (H - T_ - B) * (1 - (v - lo) / (hi - lo)) for v in ys]
    out = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="주차별 완료 주문 수 선 차트">']
    out.append(f'<line class="axis" x1="{L}" y1="{H - B}" x2="{W - R_}" y2="{H - B}"/>')
    for i, r in enumerate(data):
        if r[1] == "2025-04-21":
            out.append(f'<rect class="exam" x="{xs[i] - 18:.1f}" y="{T_ - 24}" width="36" height="{H - B - T_ + 24}" rx="4"/>')
            out.append(f'<text class="exam-label" x="{xs[i]:.1f}" y="{T_ - 10}" text-anchor="middle">중간고사</text>')
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, yv))
    out.append(f'<polyline class="line" points="{pts}"/>')
    for i, r in enumerate(data):
        out.append(f'<g class="pt"><title>{r[0]}주차(시작일 {r[1]}) 완료 주문 {r[2]:,}건 · 매출 {r[3]:,}원</title>'
                   f'<circle cx="{xs[i]:.1f}" cy="{yv[i]:.1f}" r="5"/>'
                   f'<circle class="hit" cx="{xs[i]:.1f}" cy="{yv[i]:.1f}" r="14"/></g>')
        out.append(f'<text class="val" x="{xs[i]:.1f}" y="{yv[i] - 11:.1f}" text-anchor="middle">{r[2]:,}</text>')
        out.append(f'<text class="tick" x="{xs[i]:.1f}" y="{H - B + 20}" text-anchor="middle">{r[0]}주</text>')
    out.append("</svg>")
    return "\n".join(out)


def chart2(rows):
    vals = [v for r in rows[1:] for v in r[1:]]
    mx = max(vals)
    out = ['<table class="heat"><thead><tr><th scope="col">시간대</th>'
           + "".join(f'<th scope="col">{d}</th>' for d in rows[0][1:]) + "</tr></thead><tbody>"]
    for r in rows[1:]:
        cells = []
        for d, v in zip(rows[0][1:], r[1:]):
            t = v / mx
            bg = mix("#eef4fc", "#0d3b7a", t)
            fg = "#ffffff" if t > 0.55 else "#0b0b0b"
            cells.append(f'<td style="background:{bg};color:{fg}" title="{esc(d)}요일 {esc(r[0])} {v:,}건">{v:,}</td>')
        out.append(f'<tr><th scope="row">{esc(r[0])}</th>{"".join(cells)}</tr>')
    out.append("</tbody></table>")
    return "\n".join(out)


def chart3(rows):
    data = rows[1:-1]
    W, H, L, R_, T_, B = 900, 360, 20, 20, 30, 40
    mx = max(r[4] for r in data)
    slot = (W - L - R_) / len(data)
    bw = min(70, slot * 0.5)
    sc = (H - T_ - B) / mx
    out = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="주제별 감성 리뷰 수 누적 막대 차트">']
    out.append(f'<line class="axis" x1="{L}" y1="{H - B}" x2="{W - R_}" y2="{H - B}"/>')
    order = [("부정", 2, COL_NEG), ("중립", 3, COL_NEU), ("긍정", 1, COL_POS)]  # 아래부터: 불만을 바닥에 붙여 비교
    for i, r in enumerate(data):
        cx = L + slot * (i + 0.5)
        x = cx - bw / 2
        y = H - B
        side_y = H
        for name, j, col in order:
            v = r[j]
            h = v * sc
            if v:
                out.append(f'<g class="seg"><title>{esc(r[0])} · {name} {v:,}개</title>'
                           f'<rect x="{x:.1f}" y="{y - h + 1:.1f}" width="{bw:.1f}" height="{max(h - 2, 1):.1f}" '
                           f'rx="3" fill="{col}"/></g>')
                if h >= 16:
                    fg = "#ffffff" if name != "중립" else "#0b0b0b"
                    out.append(f'<text class="seg-val" x="{cx:.1f}" y="{y - h / 2 + 4:.1f}" text-anchor="middle" '
                               f'fill="{fg}">{v:,}</text>')
                else:
                    ly = min(y - h / 2 + 4, side_y - 12)  # 작은 칸 숫자가 겹치지 않게 위로 밀어 올림
                    side_y = ly
                    out.append(f'<text class="seg-val side" x="{x + bw + 4:.1f}" y="{ly:.1f}">{v:,}</text>')
            y -= h
        out.append(f'<text class="val" x="{cx:.1f}" y="{y - 8:.1f}" text-anchor="middle">{r[4]:,}</text>')
        out.append(f'<text class="tick" x="{cx:.1f}" y="{H - B + 22}" text-anchor="middle">{esc(r[0])}</text>')
    out.append("</svg>")
    legend = ('<div class="legend">'
              + "".join(f'<span><i style="background:{c}"></i>{n}</span>' for n, c in
                        (("부정", COL_NEG), ("중립", COL_NEU), ("긍정", COL_POS)))
              + "</div>")
    tbl = ['<table class="mini"><caption>주제별 리뷰 수(리뷰분류 시트)</caption><thead><tr>'
           + "".join(f'<th scope="col">{esc(h)}</th>' for h in rows[0]) + "</tr></thead><tbody>"]
    for r in rows[1:]:
        tbl.append("<tr>" + f'<th scope="row">{esc(r[0])}</th>' + "".join(f"<td>{v:,}</td>" for v in r[1:]) + "</tr>")
    tbl.append("</tbody></table>")
    return legend + "\n" + "\n".join(out) + "\n" + "\n".join(tbl)


CSS = """
:root{--bg:#f4f3f0;--panel:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--line:#d9d7d0;--accent:#2a78d6;--exam:#fde9c4}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"Malgun Gothic","맑은 고딕","Apple SD Gothic Neo","Noto Sans KR",sans-serif;line-height:1.45}
main{max-width:1180px;margin:0 auto;padding:24px 16px 40px}
h1{font-size:26px;margin:0 0 4px}
.sub{color:var(--ink2);margin:0 0 20px;font-size:14px}
.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:12px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px}
.card .name{color:var(--ink2);font-size:14px}
.card .num{font-size:28px;font-weight:700;margin-top:4px;font-variant-numeric:tabular-nums}
.row2{display:grid;grid-template-columns:3fr 2fr;gap:12px;margin-bottom:12px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:16px;min-width:0}
.panel h2{font-size:17px;margin:0 0 2px}
.panel .note{color:var(--ink2);font-size:13px;margin:0 0 8px}
svg.chart{width:100%;height:auto;display:block}
.axis{stroke:var(--line);stroke-width:1}
.line{fill:none;stroke:var(--accent);stroke-width:2}
.pt circle{fill:var(--accent);stroke:var(--panel);stroke-width:2}
.pt circle.hit{fill:transparent;stroke:none}
.pt:hover circle:first-of-type{r:7}
.val{fill:var(--ink);font-size:12px;font-weight:600}
.tick,.axis-title{fill:var(--ink2);font-size:12px}
.exam{fill:var(--exam)}
.exam-label{fill:var(--ink);font-size:12px;font-weight:700}
.seg-val{font-size:12px;font-weight:600}
.seg-val.side{fill:var(--ink2);font-size:11px}
.seg:hover rect{opacity:.85}
.legend{display:flex;gap:16px;font-size:13px;color:var(--ink2);margin:4px 0}
.legend i{display:inline-block;width:12px;height:12px;border-radius:3px;margin-right:6px;vertical-align:-1px}
.heatwrap{overflow-x:auto}
table.heat{border-collapse:separate;border-spacing:2px;width:100%;font-size:12px;font-variant-numeric:tabular-nums}
table.heat th{color:var(--ink2);font-weight:600;padding:2px 4px}
table.heat td{text-align:center;padding:3px 2px;border-radius:3px;min-width:34px}
table.mini{border-collapse:collapse;margin-top:10px;font-size:13px;font-variant-numeric:tabular-nums}
table.mini caption{text-align:left;color:var(--ink2);margin-bottom:4px}
table.mini th,table.mini td{border-bottom:1px solid var(--line);padding:3px 10px;text-align:right}
table.mini th[scope=row],table.mini thead th:first-child{text-align:left}
footer{color:var(--ink2);font-size:13px;margin-top:16px}
@media (max-width:820px){.cards{grid-template-columns:repeat(2,1fr)}.row2{grid-template-columns:1fr}}
"""


def dashboard_html(S, source_line):
    kpi = {r[0]: r[1] for r in S["핵심지표"][1:]}
    base = {r[0]: r for r in S["기준"][1:]}
    period = base["핵심지표"][1]
    cards = [("매출", f"{kpi['매출']:,}원"), ("완료 주문 수", f"{kpi['완료 주문 수']:,}건"),
             ("건당 평균 금액", f"{kpi['건당 평균 금액']:,}원"), ("평균 평점", f"{kpi['평균 평점']:.2f}")]
    parts = ['<!doctype html>', '<html lang="ko">', '<head>', '<meta charset="utf-8">',
             '<meta name="viewport" content="width=device-width, initial-scale=1">',
             '<title>대학가 배달 주문 대시보드</title>', f"<style>{CSS}</style>", "</head>", "<body>", "<main>",
             "<header><h1>대학가 배달 주문 대시보드</h1>",
             f'<p class="sub">{esc(period)} · 매출과 주문 수는 status가 완료인 주문, 평균 평점은 평점이 있는 주문 전체</p></header>',
             '<section class="cards">']
    for n, v in cards:
        parts.append(f'<div class="card"><div class="name">{n}</div><div class="num">{v}</div></div>')
    parts.append("</section>")
    parts.append('<section class="row2">')
    parts.append('<div class="panel"><h2>주문은 주마다 어떻게 달라지나?</h2>'
                 '<p class="note">주차별 완료 주문 수(주차별 시트)</p>' + chart1(S["주차별"]) + "</div>")
    parts.append('<div class="panel"><h2>어느 요일, 어느 시간에 주문이 몰리나?</h2>'
                 '<p class="note">시간대 × 요일 완료 주문 수(시간대x요일 시트), 진할수록 많음</p>'
                 '<div class="heatwrap">' + chart2(S["시간대x요일"]) + "</div></div>")
    parts.append("</section>")
    parts.append('<section class="panel"><h2>어느 주제에서 불만이 많나?</h2>'
                 '<p class="note">주제마다 긍정·부정·중립 리뷰 수를 쌓은 막대(리뷰분류 시트), 막대 위 숫자는 합계</p>'
                 + chart3(S["리뷰분류"]) + "</section>")
    parts.append(f"<footer>{esc(source_line)}</footer>")
    parts += ["</main>", "</body>", "</html>", ""]
    return "\n".join(parts).encode("utf-8")


class TextGrab(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip, self.text = False, []

    def handle_starttag(self, tag, attrs):
        self.skip = tag == "style"
        for k, v in attrs:
            if k in ("title", "aria-label"):
                self.text.append(v)

    def handle_endtag(self, tag):
        self.skip = False

    def handle_data(self, data):
        if not self.skip:
            self.text.append(data)


NUM_RX = re.compile(r"\d[\d,]*(?:\.\d+)?")


def html_numbers_ok(hb: bytes, S) -> tuple:
    h = hb.decode("utf-8")
    g = TextGrab()
    g.feed(h)
    found = [m.replace(",", "") for t in g.text for m in NUM_RX.findall(t)]
    allowed = set()
    for name, rows in S.items():
        if name not in ("기준", "핵심지표", "주차별", "시간대x요일", "리뷰분류"):
            continue
        for r in rows:
            for v in r:
                if v is None:
                    continue
                if isinstance(v, float):
                    allowed |= {f"{v:.2f}", f"{v:.1f}", repr(v)}
                allowed |= {m.replace(",", "") for m in NUM_RX.findall(str(v))}
    bad = sorted(set(x for x in found if x not in allowed))
    ext = [w for w in ("http", "//cdn", "src=", "<script", "@import", "url(") if w in h]
    ids = re.findall(r"\b[OC]\d{4,6}\b", h)
    return bad, ext, ids, len(found)


# ---------------------------------------------------------------------------
# 처리 기록
# ---------------------------------------------------------------------------
def proc_log(upto):
    files = FILES[1:FILES.index(upto) + 1]
    L = ["# 처리 기록", "", f"시작 파일: 누적/orders_2025_w01-12_clean.csv ({len(states['w12']):,}행)", "",
         "| 처리한 날 | 파일 이름 | 원본 행 | 정제 뒤 행 | 이미 있던 주문 | 새로 붙인 행 | 붙인 뒤 누적 행 |",
         "| --- | --- | --- | --- | --- | --- | --- |"]
    for f in files:
        s = stats[f]
        L.append(f"| {PROC_DATE[f]} | {FNAME[f]} | {s['raw']:,} | {s['clean']:,} | {s['existing']:,} | "
                 f"{s['added']:,} | {s['cum']:,} |")
    L += ["", "## 규칙별 지운 행·고친 행", ""]
    for f in files:
        s = stats[f]
        L += [f"### {FNAME[f]}", "", "| 규칙 | 지운 행 | 고친 행 | 내용 |", "| --- | --- | --- | --- |",
              f"| 1. 완전히 같은 행 | {s['r1']} | 0 | 하나만 남김 |",
              f"| 2. 형식 | 0 | {s['r2']} | 날짜 {s['r2_dt']} · 글자 금액 {s['r2_amt']} |",
              f"| 3. 표기 | 0 | {s['r3']} | category {s['r3_cat']} · payment_method {s['r3_pay']} · delivery_area {s['r3_area']} |",
              f"| 4. 같은 order_id에 금액만 다른 행 | {s['r4']} | 0 | 계산과 맞는 행을 남김 |",
              f"| 5. 수량 0 | {s['r5']} | 0 | {'없음' if s['r5'] == 0 else '지움'} |",
              f"| 6. 계산 불일치 | 0 | {s['r6']} | 계산값으로 고침 |",
              f"| 7. 배달 999분·0분 | 0 | {s['r7_999'] + s['r7_0']} | 999분 {s['r7_999']} · 0분 {s['r7_0']}, 그 칸만 빈칸 |",
              f"| 8. delivery_area 빈칸 | 0 | {s['r8']} | 미상으로 채움 |",
              "| 9. rating·review_text·delivery_minutes 빈칸 | 0 | 0 | 그대로 둠 |",
              f"| 10. 취소·환불 주문 | 0 | 0 | 지우지 않음(취소 {s['cancel']} · 환불 {s['refund']}) |"]
        if FILES.index(f) >= FILES.index(RULE11_FROM):
            L.append(f"| 11. 새 표기 | 0 | {s['r11']} | "
                     f"category 떡볶이→분식 {s['r11_cat']} · payment_method 페이→간편결제 {s['r11_pay']} |")
        if s["existing"]:
            L.append("")
            L.append(f"이미 있던 주문 {s['existing']}건({', '.join(s['existing_dates'])}): {', '.join(s['existing_ids'])}")
        L.append("")
    return ("\n".join(L)).encode("utf-8")


# ---------------------------------------------------------------------------
# 시작 파일 안내
# ---------------------------------------------------------------------------
NOTE_COMMON = """
알아 둘 점
- 리뷰 감성·주제 라벨(리뷰표본·리뷰분류{all_sheet} 시트)은 자료를 만들 때 정한 값입니다. 직접 분류한 결과와 개수가 조금 다를 수 있습니다.
{log_line}- 숫자는 강의 자료의 정제 규칙대로 계산한 값이라 교안의 확인할 것 숫자와 같습니다.
- 이 안내 파일(시작파일_안내.txt)은 드라이브에 올리지 않습니다. 배달주문_실습 폴더만 올립니다.
- 드라이브에 올린 뒤 파일 이름이 .csv·.xlsx·.html·.md 그대로인지 확인합니다. 구글 시트·문서로 바뀌었으면 드라이브 설정에서 업로드 파일 변환을 끄고 다시 올립니다.
"""

NOTES = {
    "07": dict(title="7차시 시작 파일", state="6차시까지 마친 상태입니다(1~12주 정제 파일, 결과 시트, 대시보드).",
               body="""들어 있는 것(배달주문_실습/)
- 누적/orders_2025_w01-12_clean.csv: 정제한 1~12주 주문 4,426행. 누적의 시작점
- 결과/analysis_summary.xlsx: 분석 결과 시트(시트 8개)
- 결과/index.html: 대시보드(카드 4개 · 차트 3개, 차트 3은 긍정·부정·중립 누적 막대)
- 기준/: 정제규칙.md · data_dictionary.md · 리뷰기준표.md · dashboard_sketch.md
- 수신/: 비어 있음. 강의 자료의 orders_2025_w13.csv를 여기에 넣습니다
- 처리기록.md는 없습니다. 실습 2에서 처음 누적할 때 에이전트가 만듭니다

쓰는 법
1. 압축을 풀고 배달주문_실습 폴더를 통째로 실습용 구글 드라이브에 올립니다.
2. 수신 폴더에 orders_2025_w13.csv 하나만 넣습니다. 다음 주차 파일은 미리 넣지 않습니다.
3. 교안의 실습 1 ② 드라이브 연결부터 이어 갑니다.

기준 폴더는 교안보다 먼저 넣어 두었습니다. 실습 1의 폴더 목록에 기준 폴더의 파일 4개가 더 보이는 것은 정상이고, 8차시 실습 1 ①(기준 폴더 만들기)은 건너뜁니다.
"""),
    "08": dict(title="8차시 시작 파일", state="7차시까지 마친 상태입니다(13주차까지 누적 4,790행).",
               body="""들어 있는 것(배달주문_실습/)
- 수신/orders_2025_w13.csv: 13주차 원본(처리기록.md에 이미 처리한 파일로 적혀 있음)
- 누적/orders_2025_w01-12_clean.csv: 시작 파일 4,426행(그대로 둠)
- 누적/orders_2025_clean.csv: 13주차까지 누적 4,790행
- 처리기록.md: 시작 파일과 13주차 한 줄, 규칙별 숫자
- 결과/analysis_summary.xlsx · 결과/index.html: 13주차까지 반영한 결과 시트(시트 8개)와 대시보드
- 기준/: 정제규칙.md · data_dictionary.md · 리뷰기준표.md · dashboard_sketch.md

쓰는 법
1. 압축을 풀고 배달주문_실습 폴더를 통째로 실습용 구글 드라이브에 올립니다. 드라이브에 같은 이름의 폴더가 있으면 지우거나 이름을 바꾼 뒤 올립니다.
2. 기준 폴더가 이미 들어 있으므로 실습 1 ①(기준 폴더 만들기)은 건너뜁니다.
3. 14주차 파일(orders_2025_w14.csv)은 들어 있지 않습니다. 실습 2 ①에서 수신 폴더에 올립니다.
4. 7차시에 드라이브를 연결하지 않았다면 7차시 실습 1 ②대로 구글 드라이브를 먼저 연결합니다.
"""),
    "09": dict(title="9차시 시작 파일", state="8차시까지 마친 상태입니다(14주차까지 누적 5,155행, 정제 규칙 11 적용).",
               body="""들어 있는 것(배달주문_실습/)
- 수신/orders_2025_w13.csv · orders_2025_w14.csv: 처리기록.md에 이미 처리한 파일로 적혀 있음
- 누적/orders_2025_w01-12_clean.csv: 시작 파일 4,426행(그대로 둠)
- 누적/orders_2025_clean.csv: 14주차까지 누적 5,155행. 리뷰가 있는 행 1,312개
- 처리기록.md: 13·14주차 두 줄과 규칙별 숫자(14주차는 규칙 11 포함)
- 결과/analysis_summary.xlsx · 결과/index.html: 14주차까지 반영한 결과 시트(시트 8개)와 대시보드
- 기준/: 정제규칙.md · data_dictionary.md · 리뷰기준표.md · dashboard_sketch.md

쓰는 법
1. 압축을 풀고 배달주문_실습 폴더를 통째로 실습용 구글 드라이브에 올립니다. 드라이브에 같은 이름의 폴더가 있으면 지우거나 이름을 바꾼 뒤 올립니다.
2. 스킬은 강의 자료 skill/8차시_완성본/weekly-order-update/SKILL.md(규칙 11까지 더한 것)로 설치하거나, 이미 설치한 스킬에 규칙 11이 있는지 확인합니다.
3. 15주차 파일(orders_2025_w15.csv)은 들어 있지 않습니다. 실습 3 ②에서 수신 폴더에 올립니다.
"""),
    "10": dict(title="10차시 시작 파일", state="9차시까지 마친 상태입니다(15주차까지 누적 5,521행, 리뷰 전체 1,405개 분류).",
               body="""들어 있는 것(배달주문_실습/)
- 수신/orders_2025_w13.csv · w14 · w15: 처리기록.md에 이미 처리한 파일로 적혀 있음
- 누적/orders_2025_w01-12_clean.csv: 시작 파일 4,426행(그대로 둠)
- 누적/orders_2025_clean.csv: 15주차까지 누적 5,521행. 리뷰가 있는 행 1,405개
- 처리기록.md: 13·14·15주차 세 줄과 규칙별 숫자
- 결과/analysis_summary.xlsx: 시트 9개(맨 뒤 리뷰전체 1,405행, review_no는 order_id 오름차순). 리뷰분류는 리뷰 전체 기준
- 결과/index.html: 15주차까지 반영한 대시보드. 차트 3은 리뷰 전체 기준, 맨 아래 출처 줄도 리뷰 전체로 고친 것
- 기준/: 정제규칙.md · data_dictionary.md · 리뷰기준표.md · dashboard_sketch.md(맨 아래 출처 줄을 "리뷰는 리뷰분류 시트의 리뷰 전체를 분류한 결과"로 고친 것)

쓰는 법
1. 압축을 풀고 배달주문_실습 폴더를 통째로 실습용 구글 드라이브에 올립니다. 드라이브에 같은 이름의 폴더가 있으면 지우거나 이름을 바꾼 뒤 올립니다.
2. 스킬은 강의 자료 skill/9차시_완성본/weekly-order-update/SKILL.md(절차 11단계)로 설치하거나 고칩니다.
3. 16주차 파일(orders_2025_w16.csv)은 들어 있지 않습니다. 실습 3 ①에서 수신 폴더에 올립니다.
"""),
}


def note_bytes(k):
    n = NOTES[k]
    log_line = "" if k == "07" else "- 처리기록.md의 처리한 날은 자료에서 정한 날짜(주차가 끝난 다음 월요일)입니다. 직접 처리한 날짜·숫자와 조금 다를 수 있습니다.\n"
    txt = (f"[{n['title']}] 생성형 AI 기반 데이터 분석 - 배달 주문 실습\n\n"
           f"지난 시간을 따라오지 못했을 때 이어서 시작하는 파일입니다. {n['state']}\n\n" + n["body"]
           + NOTE_COMMON.format(all_sheet="·리뷰전체" if k == "10" else "", log_line=log_line))
    return txt.replace("\n", "\r\n").encode("utf-8-sig")  # 메모장에서 바로 열리게


def write_zip(path: Path, entries: dict, dirs=()):
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for dname in dirs:
            zi = zipfile.ZipInfo(dname, date_time=FIXED_TIME)
            zi.external_attr = 0o40755 << 16 | 0x10
            z.writestr(zi, b"")
        for name, data in entries.items():
            zi = zipfile.ZipInfo(name, date_time=FIXED_TIME)
            zi.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(zi, data)


# ---------------------------------------------------------------------------
# 만들기
# ---------------------------------------------------------------------------
def fb(p):
    return Path(p).read_bytes()


rules_md = fb(LF / "02" / "정제규칙.md")
crit_md = ("# 리뷰 분류 기준표\n\n리뷰 표본 200개를 분류하고 1~20번을 검수해 고친 기준표. 감성과 주제를 하나씩 고른다.\n\n"
           + (LF / "04" / "리뷰기준표_처음.md").read_text(encoding="utf-8") + "\n"
           + (LF / "04" / "리뷰기준표_더할규칙.md").read_text(encoding="utf-8").replace("[더할 규칙]", "[더한 규칙]", 1))
assert crit_md.count("[더한 규칙]") == 1
crit_b = crit_md.encode("utf-8")
dict_b, sketch_b = fb(DATA / "data_dictionary.md"), fb(DATA / "dashboard_sketch.md")
old_src = "리뷰는 표본 200개를 분류한 결과".encode("utf-8")
assert sketch_b.count(old_src) == 1
sketch10_b = sketch_b.replace(old_src, "리뷰는 리뷰분류 시트의 리뷰 전체를 분류한 결과".encode("utf-8"))

results = {}
for key_, mode, src in (("w12", "sample", SRC_SAMPLE), ("w13", "sample", SRC_SAMPLE), ("w14", "sample", SRC_SAMPLE),
                        ("w15", "all", SRC_ALL)):
    T, meta = build_tables(states[key_], mode)
    xb = xlsx_bytes(T)
    S = read_xlsx(xb)  # 파일에서 다시 읽은 값으로 대시보드를 만듦
    hb = dashboard_html(S, src)
    results[key_] = dict(csv=to_csv_bytes(states[key_]), xlsx=xb, html=hb, S=S, meta=meta)

base_csv = results["w12"]["csv"]
out_files = {
    START / "03_정제파일" / "orders_2025_w01-12_clean.csv": base_csv,
    START / "04_리뷰기준표" / "리뷰기준표.md": crit_b,
    START / "05_결과시트" / "analysis_summary.xlsx": results["w12"]["xlsx"],
    START / "06_대시보드" / "index.html": results["w12"]["html"],
}
d7 = START / "07_드라이브시작" / "배달주문_실습"
if d7.exists():
    shutil.rmtree(d7)
k7 = {"누적/orders_2025_w01-12_clean.csv": base_csv, "결과/analysis_summary.xlsx": results["w12"]["xlsx"],
      "결과/index.html": results["w12"]["html"], "기준/정제규칙.md": rules_md, "기준/data_dictionary.md": dict_b,
      "기준/리뷰기준표.md": crit_b, "기준/dashboard_sketch.md": sketch_b}
for rel, data in k7.items():
    out_files[d7 / rel] = data
(d7 / "수신").mkdir(parents=True, exist_ok=True)
(d7 / "수신" / ".gitkeep").unlink(missing_ok=True)
for p, data in out_files.items():
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)

R = "배달주문_실습/"
zips = {}
zips["07"] = ({R + k: v for k, v in k7.items()}, [R, R + "수신/", R + "누적/", R + "결과/", R + "기준/"])
for zk, st_key in (("08", "w13"), ("09", "w14"), ("10", "w15")):
    r = results[st_key]
    e = {R + "수신/" + FNAME[f]: fb(DATA / FNAME[f]) for f in FILES[1:FILES.index(st_key) + 1]}
    e.update({R + "기준/정제규칙.md": rules_md, R + "기준/data_dictionary.md": dict_b, R + "기준/리뷰기준표.md": crit_b,
              R + "기준/dashboard_sketch.md": sketch10_b if zk == "10" else sketch_b,
              R + "누적/orders_2025_w01-12_clean.csv": base_csv, R + "누적/orders_2025_clean.csv": r["csv"],
              R + "결과/analysis_summary.xlsx": r["xlsx"], R + "결과/index.html": r["html"],
              R + "처리기록.md": proc_log(st_key)})
    zips[zk] = (e, [R, R + "수신/", R + "누적/", R + "결과/", R + "기준/"])
for zk, (e, dirs) in zips.items():
    e = {"시작파일_안내.txt": note_bytes(zk), **e}
    write_zip(START / f"{zk}차시_시작_배달주문_실습.zip", e, dirs)

# ---------------------------------------------------------------------------
# 확인: 쓴 파일을 다시 읽어 교안 숫자와 대조
# ---------------------------------------------------------------------------
print("== 정제·누적")
for f, want in (("w01-12", (4526, 4426, 0, 4426, 4426)), ("w13", (375, 371, 7, 364, 4790)),
                ("w14", (369, 365, 0, 365, 5155)), ("w15", (371, 366, 0, 366, 5521))):
    s = stats[f]
    got = (s["raw"], s["clean"], s.get("existing", 0), s.get("added", s["clean"]), s.get("cum", s["clean"]))
    expect(f"{f} 원본·정제 뒤·이미 있던·새로·누적", got, want)
s = stats["w01-12"]
expect("w01-12 규칙 1·4·5 지운 행", (s["r1"], s["r4"], s["r5"]), (90, 8, 2))
expect("w01-12 계산 불일치·배달 빈칸·미상", (s["r6"], s["r7_999"] + s["r7_0"], s["r8"]), (44, 6, 44))
s = stats["w13"]
expect("w13 규칙별(중복·금액·수량0·불일치·999·미상)", (s["r1"], s["r4"], s["r5"], s["r6"], s["r7_999"], s["r8"]),
       (3, 1, 0, 4, 1, 3))
expect("w13 이미 있던 주문 날짜", s["existing_dates"], ["2025-05-25"])
s = stats["w14"]
expect("w14 규칙별(중복·금액·수량0·불일치·0분·미상·떡볶이·페이)",
       (s["r1"], s["r4"], s["r5"], s["r6"], s["r7_0"], s["r8"], s["r11_cat"], s["r11_pay"]), (3, 1, 0, 4, 1, 3, 9, 7))

print("== CSV 다시 읽기")
for p in [START / "03_정제파일" / "orders_2025_w01-12_clean.csv"]:
    b = p.read_bytes()
    expect("BOM", b[:3], b"\xef\xbb\xbf")
    expect("CRLF 없음", b"\r\n" in b, False)
    d = pd.read_csv(p, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    expect("행·열", d.shape, (4426, 18))
    expect("열 순서", list(d.columns), COLS)
    expect("날짜 형식", bool(d.order_datetime.str.match(DT_STD).all()), True)
    expect("정수 열에 .0 없음", any(d[c].str.contains(r"\.").any() for c in INT_COLS), False)
    dd = d.copy()
    for c in INT_COLS:
        dd[c] = pd.to_numeric(dd[c])
    expect("매출", int(dd[dd.status == "완료"].total_amount.sum()), 90182000)
for zk, st_key, n in (("08", "w13", 4790), ("09", "w14", 5155), ("10", "w15", 5521)):
    with zipfile.ZipFile(START / f"{zk}차시_시작_배달주문_실습.zip") as z:
        d = pd.read_csv(io.BytesIO(z.read(R + "누적/orders_2025_clean.csv")), dtype=str, keep_default_na=False,
                        encoding="utf-8-sig")
        expect(f"{zk} 누적 행·order_id 중복 없음", (len(d), d.order_id.duplicated().any()), (n, False))
        cats = sorted(set(d.category))
        expect(f"{zk} category 7종", cats, sorted(CATS))
        expect(f"{zk} payment 3종", sorted(set(d.payment_method)), sorted(["카드", "간편결제", "현금"]))
        logs = z.read(R + "처리기록.md").decode("utf-8")
        recv = sorted(x.split("/")[-1] for x in z.namelist() if x.startswith(R + "수신/") and x.endswith(".csv"))
        logged = sorted(set(re.findall(r"\| (orders_2025_w\d+\.csv) \|", logs)))
        expect(f"{zk} 수신 파일 = 처리기록 파일", recv, logged)
        expect(f"{zk} 기간 끝", max(d.order_datetime)[:10],
               {"w13": "2025-06-01", "w14": "2025-06-08", "w15": "2025-06-15"}[st_key])
with zipfile.ZipFile(START / "07차시_시작_배달주문_실습.zip") as z:
    names = z.namelist()
    expect("07 처리기록·누적 파일 없음",
           any(n.endswith("처리기록.md") or n.endswith("orders_2025_clean.csv") for n in names), False)
    expect("07 빈 수신 폴더 항목", R + "수신/" in names, True)


def sheet(S, n):
    return S[n]


def kv(S):
    return {r[0]: r[1] for r in S["핵심지표"][1:]}


def week_last2(S):
    return [tuple(r) for r in S["주차별"][-2:]]


def heat(S, h, dw):
    rows = S["시간대x요일"]
    return rows[[r[0] for r in rows].index(f"{h}시")][rows[0].index(dw)]


def heat_sum(S):
    return sum(v for r in S["시간대x요일"][1:] for v in r[1:])


def exam(S):
    return [tuple(r[1:]) for r in S["시험기간"][1:]]


def rv(S):
    return {r[0]: tuple(r[1:]) for r in S["리뷰분류"][1:]}


EXPECT = {
    "w12": dict(kpi={"매출": 90182000, "완료 주문 수": 4193, "건당 평균 금액": 21508, "평균 평점": 3.49, "평균 배달 시간": 29.4},
                last2=[(11, "2025-05-12", 341, None), (12, "2025-05-19", 354, 7527000)], top=("토", 19, 118),
                weeks=12),
    "w13": dict(kpi={"매출": 97761500, "완료 주문 수": 4534, "건당 평균 금액": 21562, "평균 평점": 3.48, "평균 배달 시간": 29.5},
                last2=[(12, "2025-05-19", 354, 7527000), (13, "2025-05-26", 341, 7579500)], top=("토", 19, 125),
                weeks=13),
    "w14": dict(kpi={"매출": 104969500, "완료 주문 수": 4876, "건당 평균 금액": 21528, "평균 평점": 3.47, "평균 배달 시간": 29.5},
                last2=[(13, "2025-05-26", 341, 7579500), (14, "2025-06-02", 342, 7208000)], top=("토", 19, 133),
                weeks=14),
    "w15": dict(kpi={"매출": 112175500, "완료 주문 수": 5223, "건당 평균 금액": 21477, "평균 평점": 3.49, "평균 배달 시간": None},
                last2=[(14, "2025-06-02", 342, 7208000), (15, "2025-06-09", 347, 7206000)], top=("토", 19, 145),
                weeks=15),
}
RV_SAMPLE = {"맛": (57, 17, 5, 79), "배달": (13, 23, 2, 38), "양": (19, 6, 7, 32), "포장": (4, 8, 1, 13),
             "가격": (17, 4, 2, 23), "기타": (10, 2, 3, 15), "합계": (120, 60, 20, 200)}
RV_1405 = {"맛": (388, 118, 52, 558), "배달": (128, 159, 10, 297), "양": (128, 48, 27, 203), "포장": (42, 42, 8, 92),
           "가격": (97, 37, 26, 160), "기타": (58, 20, 17, 95), "합계": (841, 424, 140, 1405)}
SHEETS8 = ["기준", "핵심지표", "주차별", "카테고리x지역", "시간대x요일", "시험기간", "리뷰분류", "리뷰표본"]

for st_key, E in EXPECT.items():
    S = results[st_key]["S"]
    print(f"== 결과 시트 {st_key} (파일에서 다시 읽음)")
    expect("시트 이름·순서", list(S), SHEETS8 + (["리뷰전체"] if st_key == "w15" else []))
    got = kv(S)
    for k, v in E["kpi"].items():
        if v is not None:
            expect(f"핵심지표 {k}", got[k], v)
    print(f"  ..  평균 배달 시간 {got['평균 배달 시간']}")
    expect("주차별 행 수", len(S["주차별"]) - 1, E["weeks"])
    l2 = week_last2(S)
    for g, w in zip(l2, E["last2"]):
        expect(f"주차별 {w[0]}주", tuple(x if y is not None else None for x, y in zip(g, w)), w)
    expect("주차별 완료 합 = 완료 주문 수", sum(r[2] for r in S["주차별"][1:]), got["완료 주문 수"])
    mxv = max(v for r in S["시간대x요일"][1:] for v in r[1:])
    dw, h, v = E["top"]
    expect(f"시간대x요일 {dw} {h}시(가장 큰 칸)", (heat(S, h, dw), mxv), (v, v))
    expect("시간대x요일 16행·합 = 완료", (len(S["시간대x요일"]) - 1, heat_sum(S)), (16, got["완료 주문 수"]))
    cx = S["카테고리x지역"]
    expect("카테고리x지역 합계 = 매출", cx[-1][-1], got["매출"])
    expect("카테고리 행(떡볶이 없음)", [r[0] for r in cx[1:-1]], CATS)
    e = exam(S)
    expect("시험기간 배율", (e[0][2], e[1][2]), (1.39, 0.94))
    if st_key in ("w12", "w13"):
        expect("시험기간 하루 평균", (e[0][0], e[0][1], e[1][0], e[1][1]), (32.8, 23.6, 22.6, 24.1))
    if st_key == "w12":
        expect("치킨 합계·치킨x기숙사", (cx[1][-1], cx[1][1]), (23430500, 8566000))
        expect("8주차 390건(가장 많음)", max((r[2], r[0]) for r in S["주차별"][1:]), (390, 8))
    if st_key == "w14":
        expect("분식 합계", cx[2][-1], 10121000)
    expect("리뷰분류", rv(S), RV_1405 if st_key == "w15" else RV_SAMPLE)
    expect("리뷰표본 행 수", len(S["리뷰표본"]) - 1, 200)
    if st_key == "w15":
        A = S["리뷰전체"]
        expect("리뷰전체 행·열", (len(A) - 1, len(A[0])), (1405, 7))
        nos = [r[0] for r in A[1:]]
        expect("review_no 1~1405 차례", nos == list(range(1, 1406)), True)
        ids = [r[1] for r in A[1:]]
        expect("review_no는 order_id 오름차순", ids == sorted(ids), True)
        w15_ids = set(cl["w15"].loc[cl["w15"].review_text != "", "order_id"])
        expect("review_no 1313~1405 = 15주차 리뷰", set(ids[1312:]) == w15_ids, True)
        first1312 = [r for r in A[1:1313]]
        c14 = pd.DataFrame([r[5:] for r in first1312], columns=["s", "t"])
        print("  ..  1~1312번 감성", c14.s.value_counts().to_dict(), "주제", c14.t.value_counts().to_dict())
        smap = {r[1]: (r[5], r[6]) for r in S["리뷰표본"][1:]}
        amap = {r[1]: (r[5], r[6]) for r in A[1:]}
        expect("리뷰표본 라벨 = 리뷰전체 라벨", all(amap[k] == v for k, v in smap.items()), True)
        expect("리뷰분류 합계 = 리뷰전체 행 수", rv(S)["합계"][3], len(A) - 1)
    hb = results[st_key]["html"]
    bad, ext, ids_, nfound = html_numbers_ok(hb, S)
    expect(f"대시보드 숫자가 모두 시트에 있음({nfound}개 확인)", bad, [])
    expect("대시보드 외부 불러오기 없음", ext, [])
    expect("대시보드 주문·고객 번호 없음", ids_, [])
    txt = hb.decode("utf-8")
    for card in (f"{got['매출']:,}원", f"{got['완료 주문 수']:,}건", f"{got['건당 평균 금액']:,}원", f"{got['평균 평점']:.2f}"):
        expect(f"카드 {card}", card in txt, True)
    expect("출처 줄", (SRC_ALL if st_key == "w15" else SRC_SAMPLE) in txt, True)
    expect("중간고사 표시", "중간고사" in txt, True)

print("== 기준 파일")
expect("10차시 스케치는 출처 줄만 다름",
       [l for l in sketch10_b.decode().splitlines() if l not in sketch_b.decode().splitlines()],
       ["- 출처 한 줄: 숫자 출처 analysis_summary.xlsx, 리뷰는 리뷰분류 시트의 리뷰 전체를 분류한 결과"])

print("== 만든 파일")
for p in sorted(START.rglob("*")):
    if p.is_file():
        print(f"  {p.relative_to(LF)}  {p.stat().st_size:,} B")
if FAILS:
    print(f"\n맞지 않은 항목 {len(FAILS)}개: {FAILS}")
    sys.exit(1)
print("\n모든 항목이 교안 숫자와 같음")
