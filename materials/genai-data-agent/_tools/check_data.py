"""make_data.py가 만든 CSV에 의도한 특징이 들어 있는지 검사하고 data_facts.md를 쓴다.

실행:
    _tools/.venv/Scripts/python.exe _tools/check_data.py

CSV는 글자 그대로(dtype=str, 빈칸은 빈 문자열) 읽어 문제를 다시 찾아내고, _tools/answer_key.csv(심은 문제·리뷰 정답)와
맞춰 본다. 실패한 항목도 표에 '실패'로 적고 data_facts.md를 쓴 뒤, 실패가 하나라도 있으면 종료 코드 1로 끝난다.
"""

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

TOOLS = Path(__file__).resolve().parent
DATA = TOOLS.parent / "data"
OUT = TOOLS / "data_facts.md"
FILES = ["w01-12", "w13", "w14", "w15", "w16"]
FNAME = {f: f"orders_2025_{f}.csv" for f in FILES}
RANGES = {"w01-12": ("2025-03-03", "2025-05-25"), "w13": ("2025-05-26", "2025-06-01"),
          "w14": ("2025-06-02", "2025-06-08"), "w15": ("2025-06-09", "2025-06-15"), "w16": ("2025-06-16", "2025-06-22")}
MIDTERM = ("2025-04-21", "2025-04-25")
FINAL = ("2025-06-16", "2025-06-20")
BOOST = ["야식", "치킨", "카페디저트"]
CATS = ["치킨", "분식", "한식", "중식", "피자", "카페디저트", "야식"]
AREAS = ["기숙사", "정문", "후문", "쪽문", "원룸촌"]
PAYS = ["카드", "간편결제", "현금"]
STATUS = ["완료", "취소", "환불"]
DOW_KO = ["월", "화", "수", "목", "금", "토", "일"]
MIN_GAP = 0.03

# 정제 규칙의 표기 통일표(앞뒤 공백은 먼저 지운다)
CAT_MAP = {"chicken": "치킨", "pizza": "피자", "카페/디저트": "카페디저트", "카페 디저트": "카페디저트"}
PAY_MAP = {"신용카드": "카드", "card": "카드", "간편 결제": "간편결제"}
AREA_MAP = {"정문앞": "정문", "정문 앞": "정문", "후문 앞": "후문", "원룸": "원룸촌"}
# 8차시에 사람이 정해 스킬에 추가하는 규칙(14주차 새 표기)
NEW_RULES = {"category": {"떡볶이": "분식"}, "payment_method": {"페이": "간편결제"}}

BRANDS = ["교촌", "BBQ", "bhc", "굽네", "네네", "처갓집", "푸라닭", "노랑통닭", "60계", "엽기", "신전", "배떡", "죠스",
          "도미노", "피자헛", "미스터피자", "파파존스", "피자스쿨", "스타벅스", "이디야", "메가커피", "컴포즈", "빽다방", "투썸",
          "공차", "설빙", "원할머니", "홍콩반점", "김밥천국", "본죽", "맘스터치", "배달의민족", "배민", "요기요", "쿠팡",
          "카카오", "네이버", "토스"]

checks: list[tuple[str, str, bool]] = []


def check(name, ok, detail):
    checks.append((name, str(detail), bool(ok)))


def won(x):
    return f"{int(round(x)):,}원"


def gap_ok(ser: pd.Series, top=True, bottom=True):
    v = ser.sort_values(ascending=False)
    t = (v.iloc[0] - v.iloc[1]) / abs(v.iloc[0])
    b = (v.iloc[-2] - v.iloc[-1]) / abs(v.iloc[-2])
    return (not top or t >= MIN_GAP) and (not bottom or b >= MIN_GAP), t, b


# ---------------------------------------------------------------------------
# 읽기
# ---------------------------------------------------------------------------
raw, bom = {}, {}
for f in FILES:
    p = DATA / FNAME[f]
    bom[f] = p.read_bytes()[:3] == b"\xef\xbb\xbf"
    raw[f] = pd.read_csv(p, dtype=str, keep_default_na=False, encoding="utf-8-sig")
key = pd.read_csv(TOOLS / "answer_key.csv", dtype=str, keep_default_na=False, encoding="utf-8-sig")
key["index"] = key["index"].astype(int)
kf = {f: key[key.file == FNAME[f]].reset_index(drop=True) for f in FILES}

DT_STD = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")
DT_DOT = re.compile(r"^\d{4}\.\d{1,2}\.\d{1,2} \d{2}:\d{2}$")
DT_US = re.compile(r"^\d{2}/\d{2}/\d{4} \d{1,2}:\d{2} (AM|PM)$")


def dt_kind(s: str) -> str:
    if DT_STD.match(s):
        return "표준"
    if DT_DOT.match(s):
        return "점"
    if DT_US.match(s):
        return "미국식"
    return "기타"


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


# ---------------------------------------------------------------------------
# 정제(기준 구현). 규칙 번호는 data_facts.md의 정제 규칙 표와 같다.
# ---------------------------------------------------------------------------
def clean(df_raw: pd.DataFrame, new_rules=True):
    log = [("원본", len(df_raw))]
    d = df_raw.copy()
    d["excel_row"] = np.arange(len(d)) + 2  # 엑셀 행 번호
    # 1. 완전 중복 제거
    dup = d.drop(columns="excel_row").duplicated()
    d = d[~dup].copy()
    log.append(("1. 완전 중복 제거", len(d)))
    # 2. 형식 통일
    d["order_datetime"] = parse_dt(d.order_datetime)
    for c in ["quantity", "unit_price", "delivery_fee", "discount", "delivery_minutes", "rating"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d["total_amount"] = num(d.total_amount)
    for c in ["category", "payment_method", "delivery_area"]:
        d[c] = d[c].str.strip()
    d["category"] = d.category.replace(CAT_MAP)
    d["payment_method"] = d.payment_method.replace(PAY_MAP)
    d["delivery_area"] = d.delivery_area.replace(AREA_MAP)
    if new_rules:
        d["category"] = d.category.replace(NEW_RULES["category"])
        d["payment_method"] = d.payment_method.replace(NEW_RULES["payment_method"])
    log.append(("2. 형식·표기 통일", len(d)))
    # 3. 같은 order_id에 금액만 다른 행: 계산식과 맞는 행만 남김
    calc = computed(d)
    multi = d.order_id.duplicated(keep=False)
    drop_conf = multi & (d.total_amount != calc)
    conflict_ids = sorted(d.loc[multi, "order_id"].unique())
    d = d[~drop_conf].copy()
    log.append(("3. 같은 주문번호 다른 금액 정리", len(d)))
    # 4. 수량 0 제외
    q0 = d.quantity == 0
    d = d[~q0].copy()
    log.append(("4. 수량 0 제외", len(d)))
    # 5. 계산 불일치는 계산값으로
    calc = computed(d)
    mis = d.total_amount != calc
    d["amount_fixed"] = mis
    d.loc[mis, "total_amount"] = calc[mis]
    # 6. 배달 시간 이상치(0분, 180분 초과)는 빈칸
    out_dm = (d.delivery_minutes == 0) | (d.delivery_minutes > 180)
    d.loc[out_dm, "delivery_minutes"] = np.nan
    # 7. 지역 빈칸은 '미상'
    d["delivery_area"] = d.delivery_area.replace("", "미상")
    log.append(("5~7. 금액 재계산·이상치 빈칸·지역 미상(행 수 변화 없음)", len(d)))
    d["date"] = d.order_datetime.dt.normalize()
    d["hour"] = d.order_datetime.dt.hour
    d["dow"] = d.order_datetime.dt.day_of_week
    info = dict(dup=int(dup.sum()), conflict_ids=conflict_ids, conflict_drop=int(drop_conf.sum()), qty0=int(q0.sum()),
                mismatch=int(mis.sum()), dm_out=int(out_dm.sum()), log=log)
    return d, info


cl, info = {}, {}
for f in FILES:
    cl[f], info[f] = clean(raw[f])

# ---------------------------------------------------------------------------
# A. 파일 기본
# ---------------------------------------------------------------------------
COLS = ["order_id", "order_datetime", "store_id", "store_name", "category", "menu", "quantity", "unit_price",
        "delivery_fee", "discount", "total_amount", "payment_method", "delivery_area", "customer_id",
        "delivery_minutes", "status", "rating", "review_text"]
for f in FILES:
    check(f"{FNAME[f]} 열 18개·이름", list(raw[f].columns) == COLS, f"{raw[f].shape[1]}열")
    check(f"{FNAME[f]} UTF-8 BOM", bom[f], "있음" if bom[f] else "없음")
    lo, hi = RANGES[f]
    ds = cl[f].date
    own = cl[f][~cl[f].order_id.isin(cl["w01-12"].order_id)] if f == "w13" else cl[f]
    check(f"{FNAME[f]} 기간", own.date.min() == pd.Timestamp(lo) and own.date.max() == pd.Timestamp(hi),
          f"{own.date.min().date()} ~ {own.date.max().date()}")
    check(f"{FNAME[f]} 날짜 모두 읽힘", cl[f].order_datetime.notna().all(), f"못 읽은 값 {cl[f].order_datetime.isna().sum()}개")
n_rows = {f: len(raw[f]) for f in FILES}
check("기본 파일 약 4,500행", 4400 <= n_rows["w01-12"] <= 4650, f"{n_rows['w01-12']:,}행")
for f in ["w13", "w14", "w15"]:
    check(f"{f} 약 375행", 340 <= n_rows[f] <= 410, f"{n_rows[f]}행")
check("w16이 15주차보다 뚜렷이 많음(설계 약 450행, 시험 배율 1.4만 넣어 덜 나옴 → 8번 항목)",
      n_rows["w16"] >= n_rows["w15"] * 1.08, f"{n_rows['w16']}행 (15주차의 {n_rows['w16'] / n_rows['w15']:.2f}배)")

# ---------------------------------------------------------------------------
# B. 원본 문제 다시 찾기(글자 그대로)
# ---------------------------------------------------------------------------
def raw_issues(f):
    r = raw[f]
    k = kf[f]
    nd = r.drop_duplicates()
    out = {}
    out["rows"] = len(r)
    out["blank"] = {c: int((r[c] == "").sum()) for c in COLS}
    out["dup"] = int(r.duplicated().sum())
    out["conflict_ids"] = sorted(nd.order_id[nd.order_id.duplicated(keep=False)].unique())
    kinds = r.order_datetime.map(dt_kind)
    out["dt"] = kinds.value_counts().to_dict()
    out["amt_str"] = int(r.total_amount.str.contains("원|,", regex=True).sum())
    out["neg"] = int((num(r.total_amount) < 0).sum())
    out["dm999"] = int((r.delivery_minutes == "999").sum())
    out["dm0"] = int((r.delivery_minutes == "0").sum())
    out["qty0"] = int((r.quantity == "0").sum())
    out["cat_vals"] = r.category.value_counts().to_dict()
    out["pay_vals"] = r.payment_method.value_counts().to_dict()
    out["area_vals"] = r.delivery_area.value_counts().to_dict()
    out["status"] = r.status.value_counts().to_dict()
    nonstd = lambda vals, std: {v: n for v, n in vals.items() if v not in std and v != ""}
    out["cat_var"] = nonstd(out["cat_vals"], CATS)
    out["pay_var"] = nonstd(out["pay_vals"], PAYS)
    out["area_var"] = nonstd(out["area_vals"], AREAS)
    canc = r.status == "취소"
    out["dm_blank_cancel"] = int(((r.delivery_minutes == "") & canc).sum())
    out["dm_blank_other"] = int(((r.delivery_minutes == "") & ~canc).sum())
    out["reviews_raw"] = int((r.review_text != "").sum())
    # 정답표와 맞추기
    iss = k.issues.str.split(";")
    cnt = lambda t: int(iss.map(lambda x: t in x).sum())
    out["key"] = {t: cnt(t) for t in ["dup_copy", "conflict_drop", "mismatch", "qty0", "dm999", "dm0", "dm_missing",
                                      "amount_str", "area_missing", "cat_var", "pay_var", "area_var", "date_fmt1",
                                      "date_fmt2", "new_cat", "new_pay", "overlap_w12"]}
    return out


ri = {f: raw_issues(f) for f in FILES}
for f in FILES:
    x, kk, c = ri[f], ri[f]["key"], info[f]
    nm = FNAME[f]
    check(f"{nm} 완전 중복 = 심은 수", x["dup"] == kk["dup_copy"], f"찾음 {x['dup']} / 심음 {kk['dup_copy']}")
    check(f"{nm} 금액만 다른 중복 = 심은 수", len(x["conflict_ids"]) == kk["conflict_drop"] == c["conflict_drop"],
          f"찾음 {len(x['conflict_ids'])} / 심음 {kk['conflict_drop']}")
    check(f"{nm} 계산 불일치 = 심은 수", c["mismatch"] == kk["mismatch"], f"찾음 {c['mismatch']} / 심음 {kk['mismatch']}")
    check(f"{nm} 금액 글자 = 심은 수(중복 사본 포함 전)", x["amt_str"] >= kk["amount_str"], f"글자 {x['amt_str']}행 / 심은 원본 {kk['amount_str']}")
    check(f"{nm} 날짜 형식은 세 가지뿐", set(x["dt"]) <= {"표준", "점", "미국식"}, x["dt"])
    check(f"{nm} 999분·0분·수량0 = 심은 수", (x["dm999"], x["dm0"], x["qty0"]) >= (kk["dm999"], kk["dm0"], kk["qty0"])
          and c["dm_out"] == kk["dm999"] + kk["dm0"] - 0, f"999분 {x['dm999']}, 0분 {x['dm0']}, 수량0 {x['qty0']}")

b = ri["w01-12"]
nb = b["rows"]
check("기본: 완전 중복 약 90", 80 <= b["dup"] <= 100, b["dup"])
check("기본: 금액만 다른 중복 약 8", len(b["conflict_ids"]) == 8, len(b["conflict_ids"]))
check("기본: rating·review 약 75% 빈칸", .70 <= b["blank"]["review_text"] / nb <= .80,
      f"review 빈칸 {b['blank']['review_text'] / nb:.1%}, rating 빈칸 {b['blank']['rating'] / nb:.1%}")
check("기본: delivery_area 약 1% 빈칸", .007 <= b["blank"]["delivery_area"] / nb <= .013, f"{b['blank']['delivery_area']}행 {b['blank']['delivery_area'] / nb:.1%}")
check("기본: 날짜 표준 약 85·점 약 10·미국식 약 5%",
      abs(b["dt"]["표준"] / nb - .85) < .02 and abs(b["dt"]["점"] / nb - .10) < .015 and abs(b["dt"]["미국식"] / nb - .05) < .012,
      {k: f"{v} ({v / nb:.1%})" for k, v in b["dt"].items()})
check("기본: 금액 글자 약 3%", .025 <= b["amt_str"] / nb <= .035, f"{b['amt_str']}행 {b['amt_str'] / nb:.1%}")
check("기본: '12,500원' 실제로 있음", (raw["w01-12"].total_amount == "12,500원").any(), int((raw["w01-12"].total_amount == "12,500원").sum()))
ncv = sum(b["cat_var"].values())
check("기본: category 흔들림 약 4%", .03 <= ncv / nb <= .05, f"{ncv}행 {ncv / nb:.1%} {b['cat_var']}")
check("기본: payment 흔들림", sum(b["pay_var"].values()) > 0, b["pay_var"])
check("기본: area 흔들림", sum(b["area_var"].values()) > 0, b["area_var"])
check("기본: 999분 4·0분 2·수량0 2", (b["dm999"], b["dm0"], b["qty0"]) == (4, 2, 2), (b["dm999"], b["dm0"], b["qty0"]))
check("기본: 계산 불일치 약 1%", .007 <= info["w01-12"]["mismatch"] / nb <= .013, info["w01-12"]["mismatch"])
st = b["status"]
check("기본: 상태 완료 약 95·취소 약 4·환불 약 1%",
      abs(st["완료"] / nb - .95) < .015 and abs(st["취소"] / nb - .04) < .012 and abs(st["환불"] / nb - .01) < .006,
      {k: f"{v} ({v / nb:.1%})" for k, v in st.items()})
check("기본: 환불은 모두 음수 금액", b["neg"] == st["환불"], f"음수 {b['neg']} / 환불 {st['환불']}")
check("취소 주문은 delivery_minutes 빈칸", all(ri[f]["dm_blank_cancel"] == ri[f]["status"].get("취소", 0) for f in FILES), "")

# 주차 파일에 기본 파일에 없던 값이 나오는지
base_tokens = {c: set(raw["w01-12"][c]) for c in ["category", "payment_method", "delivery_area", "status"]}
base_dt = set(b["dt"])
for f in ["w13", "w14", "w15", "w16"]:
    new = {c: sorted(set(raw[f][c]) - base_tokens[c]) for c in base_tokens}
    new = {c: v for c, v in new.items() if v}
    if f == "w14":
        check("w14 새 표기는 category '떡볶이'·payment '페이' 두 가지뿐", new == {"category": ["떡볶이"], "payment_method": ["페이"]}, new)
    else:
        check(f"{f} 새 표기 없음", not new, new or "없음")
    check(f"{f} 날짜 형식도 기본 파일에 있던 것만", set(ri[f]["dt"]) <= base_dt, ri[f]["dt"])
w14 = raw["w14"]
pos_cat = w14.index[w14.category == "떡볶이"]
pos_pay = w14.index[w14.payment_method == "페이"]
check("w14 떡볶이는 분식 가게 행", set(w14.loc[pos_cat, "store_name"]) <= {"후문떡볶이", "쪽문분식", "엄마손김밥", "매콤떡집", "오늘분식", "학교앞튀김"},
      sorted(set(w14.loc[pos_cat, "store_name"])))
# 13주차 겹침
ov = raw["w13"][raw["w13"].order_id.isin(raw["w01-12"].order_id)]
check("w13 기본 파일 마지막 날(05-25)과 겹치는 주문 몇 건", 5 <= len(ov) <= 10 and parse_dt(ov.order_datetime).dt.date.astype(str).eq("2025-05-25").all(),
      f"{len(ov)}건")
# 주문번호 이어짐
ids = {f: cl[f].order_id.str[1:].astype(int) for f in FILES}
prev = ids["w01-12"].max()
cont = True
for f in ["w13", "w14", "w15", "w16"]:
    own = ids[f][ids[f] > prev]
    cont &= own.min() == prev + 1
    prev = own.max()
check("주문번호가 주차 파일로 이어짐", cont, f"O000001 ~ O{prev:06d}")
dd = (DATA / "data_dictionary.md").read_text(encoding="utf-8") if (DATA / "data_dictionary.md").exists() else ""
check("data_dictionary.md에 14주차 새 표기 없음", dd and "`떡볶이`" not in dd and "페이" not in dd, "확인" if dd else "파일 없음")
allnames = " ".join(sorted(set(pd.concat([raw[f].store_name for f in FILES])))) + " " + " ".join(
    sorted(set(pd.concat([raw[f].review_text for f in FILES]))))
hits = [x for x in BRANDS if x.lower() in allnames.lower()]
check("실제 브랜드명 없음(목록 대조)", not hits, hits or "없음")

# ---------------------------------------------------------------------------
# C. 정제한 기본 파일의 패턴
# ---------------------------------------------------------------------------
B = cl["w01-12"]
Bd = B[B.status == "완료"]
by_hour = Bd.groupby("hour").size().reindex([10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 0, 1], fill_value=0)
top3 = by_hour.sort_values(ascending=False).index[:3].tolist()
check("시간대: 저녁 18~20시가 상위 3", set(top3) == {18, 19, 20}, f"상위 {top3}")
check("시간대: 21시에 꺼졌다가 22·23시 야식 봉우리", by_hour[22] > by_hour[21] and by_hour[23] > by_hour[21] * .95,
      f"21시 {by_hour[21]}, 22시 {by_hour[22]}, 23시 {by_hour[23]}")
night = Bd.hour.isin([22, 23, 0, 1])
ns = Bd[Bd.delivery_area != "미상"].groupby("delivery_area").apply(lambda g: g.hour.isin([22, 23, 0, 1]).mean())
check("야식 봉우리는 기숙사에서 크게", ns.idxmax() == "기숙사" and ns["기숙사"] > ns.drop(["기숙사", "미상"], errors="ignore").max() * 1.3,
      {k: f"{v:.1%}" for k, v in ns.items()})
by_dow = Bd.groupby("dow").size()
ndays = B.groupby("dow").date.nunique()
per_dow = by_dow / ndays
top2 = per_dow.sort_values(ascending=False).index[:2].tolist()
check("요일: 금·토 최고", set(top2) == {4, 5}, {DOW_KO[i]: round(v, 1) for i, v in per_dow.items()})
lunch = Bd[Bd.hour.isin([11, 12, 13])].groupby("dow").size() / ndays
check("일요일 점심이 가장 높음", lunch.idxmax() == 6 and lunch[6] > lunch.drop(6).max() * 1.15, {DOW_KO[i]: round(v, 1) for i, v in lunch.items()})
dinner = Bd[Bd.hour.isin([18, 19, 20])].groupby("dow").size() / ndays
check("금·토 저녁이 최고", set(dinner.sort_values(ascending=False).index[:2]) == {4, 5}, {DOW_KO[i]: round(v, 1) for i, v in dinner.items()})


def exam_ratio(D, exam, base_mask_fn, cats=BOOST):
    x = D[D.category.isin(cats)]
    days = D.date.drop_duplicates()
    ex_days = days[(days >= exam[0]) & (days <= exam[1])]
    bd = days[base_mask_fn(days)]
    a = x[x.date.isin(ex_days)].shape[0] / len(ex_days)
    c = x[x.date.isin(bd)].shape[0] / len(bd)
    return a / c, a, c


mid = (pd.Timestamp(MIDTERM[0]), pd.Timestamp(MIDTERM[1]))
not_exam = lambda d: ~((d >= mid[0]) & (d <= mid[1]))
weekday = lambda d: d.dt.day_of_week < 5
adj = lambda d: ((d >= "2025-04-14") & (d <= "2025-04-18")) | ((d >= "2025-04-28") & (d <= "2025-05-02"))
r_wd = exam_ratio(Bd, mid, lambda d: not_exam(d) & weekday(d))
r_all = exam_ratio(Bd, mid, not_exam)
r_adj = exam_ratio(Bd, mid, adj)
r_oth = exam_ratio(Bd, mid, lambda d: not_exam(d) & weekday(d), cats=[c for c in CATS if c not in BOOST])
check("중간고사 야식·치킨·카페디저트 약 1.4배(시험 외 평일 대비)", 1.28 <= r_wd[0] <= 1.52, f"{r_wd[0]:.2f}배")
check("중간고사 배율이 다른 기준에서도 1보다 뚜렷이 큼", r_all[0] >= 1.2 and r_adj[0] >= 1.25, f"전체 날 대비 {r_all[0]:.2f}, 앞뒤 주 평일 대비 {r_adj[0]:.2f}")
check("다른 카테고리는 시험 기간 변화 거의 없음", 0.85 <= r_oth[0] <= 1.15, f"{r_oth[0]:.2f}배")

area = Bd.groupby("delivery_area").total_amount.agg(["count", "sum", "mean"]).drop("미상", errors="ignore")
check("지역: 기숙사 주문 수 최다", area["count"].idxmax() == "기숙사", area["count"].to_dict())
ok, t, bt = gap_ok(area["mean"])
check("지역: 건당 금액 원룸촌 최고·기숙사 최저(차이 3% 이상)",
      area["mean"].idxmax() == "원룸촌" and area["mean"].idxmin() == "기숙사" and ok,
      f"{ {k: int(v) for k, v in area['mean'].items()} } 1·2위 차 {t:.1%}, 최하·차하 차 {bt:.1%}")
cat = Bd.groupby("category").total_amount.agg(["count", "sum", "mean"])
ok, t, bt = gap_ok(cat["sum"])
check("카테고리 매출 1·2위, 최하·차하위 차이 3% 이상", ok, f"1·2위 {t:.1%}, 최하·차하 {bt:.1%}")


def corr_block(D):
    rv = D[D.rating.notna() & D.delivery_minutes.notna()]
    overall = rv[["delivery_minutes", "rating"]].corr().iloc[0, 1]
    sub = rv[rv.delivery_area != "미상"]
    per = sub.groupby("delivery_area").apply(lambda g: g[["delivery_minutes", "rating"]].corr().iloc[0, 1])
    dm = sub.delivery_minutes - sub.groupby("delivery_area").delivery_minutes.transform("mean")
    rt = sub.rating - sub.groupby("delivery_area").rating.transform("mean")
    pooled = np.corrcoef(dm, rt)[0, 1]
    n = sub.groupby("delivery_area").size()
    return overall, per, pooled, len(rv), n


def cum(upto):
    parts = []
    seen = set()
    for f in FILES:
        x = cl[f][~cl[f].order_id.isin(seen)]
        parts.append(x)
        seen |= set(x.order_id)
        if f == upto:
            break
    return pd.concat(parts, ignore_index=True)


corr_res = {}
for lbl, D in (("기본(1~12주)", B), ("15주차까지 누적", cum("w15")), ("16주차까지 누적", cum("w16"))):
    corr_res[lbl] = corr_block(D[D.status != "취소"])
    o, per, pooled, n, nn = corr_res[lbl]
    check(f"배달시간-평점 전체 음의 관계({lbl})", o <= -0.25, f"r = {o:.2f} (n={n})")
    check(f"지역 안에서는 약함({lbl})", abs(pooled) <= 0.12 and per.abs().max() <= 0.25,
          f"지역 안 r = {pooled:.2f}, 지역별 {', '.join(f'{k} {v:.2f}' for k, v in per.items())}")
raw_rv = raw["w01-12"][(raw["w01-12"].rating != "") & (raw["w01-12"].delivery_minutes != "")]
raw_corr = np.corrcoef(raw_rv.delivery_minutes.astype(float), raw_rv.rating.astype(float))[0, 1]

# ---------------------------------------------------------------------------
# D. 리뷰
# ---------------------------------------------------------------------------
def kclean(f):
    """정제 뒤 남은 행의 정답표(사본 제외)."""
    k = kf[f]
    return k[(k.is_copy == "0") & ~k.issues.str.contains("qty0")]


rev_counts = {}
for f in FILES:
    rev_counts[f] = int((cl[f].review_text != "").sum())
cum_rev = {}
for f in FILES:
    D = cum(f)
    cum_rev[f] = int((D.review_text != "").sum())
check("리뷰 수: 기본 약 1,100", 1050 <= rev_counts["w01-12"] <= 1150, rev_counts["w01-12"])
check("리뷰 수: 15주차까지 누적 약 1,400", 1330 <= cum_rev["w15"] <= 1450, cum_rev["w15"])
check("리뷰 수: 16주차 약 110", 95 <= rev_counts["w16"] <= 125, rev_counts["w16"])
kall = pd.concat([kclean(f) for f in FILES])
kall = kall[kall.sentiment != ""]
sent_share = kall.sentiment.value_counts(normalize=True)
check("감성 긍정 약 60·부정 약 30·중립 약 10%",
      abs(sent_share["긍정"] - .6) < .03 and abs(sent_share["부정"] - .3) < .03 and abs(sent_share["중립"] - .1) < .02,
      {k: f"{v:.1%}" for k, v in sent_share.items()})
topic_share = kall.topic.value_counts(normalize=True)
check("주제 6가지 모두 나옴", set(topic_share.index) == {"맛", "배달", "양", "포장", "가격", "기타"}, {k: f"{v:.1%}" for k, v in topic_share.items()})
traps = kall[kall.trap != ""]
check("키워드 함정 리뷰 있음(약 5~10%)", .05 <= len(traps) / len(kall) <= .10, f"{len(traps)}개 {len(traps) / len(kall):.1%}")
btxt = set(raw["w01-12"].review_text)
for phrase in ["빨리 왔는데 다 식었어요", "맛없을 줄 알았는데 맛있어요"]:
    check(f"강의 예시 '{phrase}'가 기본 파일에 있음", any(phrase in t for t in btxt), sum(phrase in t for t in btxt))
# 리뷰-행 일관성
allc = pd.concat([cl[f].assign(_f=f) for f in FILES])
allk = pd.concat([kf[f].assign(_f=f) for f in FILES])
rv = allc[allc.review_text != ""].drop_duplicates("order_id")
rv = rv.merge(allk[allk.is_copy == "0"][["order_id", "sentiment", "dm_true", "exam"]], on="order_id", how="left")
rv["dm_true"] = pd.to_numeric(rv.dm_true)
bad_slow = rv[rv.review_text.str.contains("분 넘게 걸려|한 시간 가까이|배달이 너무 늦어요|조금 늦었어요|살짝 늦긴") & (rv.dm_true < 38)]
bad_fast = rv[rv.review_text.str.contains("금방 왔어요|빨리 도착|빨리 왔어요|20분도 안|번개처럼|배달은 빨랐") & (rv.dm_true > 26)]
bad_exam = rv[rv.review_text.str.contains("시험|중간고사|기말고사|벼락치기") & (rv.exam == "")]
rv = rv.merge(allk[allk.is_copy == "0"][["order_id"]].assign(_k=1), on="order_id", how="left")
# 메뉴에 맞지 않는 표현(정규식, 그 표현이 나와도 되는 메뉴)
MENU_RULES = [
    ("불어서|면이 ", {"짜장면", "짬뽕", "라볶이", "마라탕"}), ("해물", {"짬뽕"}), ("춘장", {"짜장면"}), ("라떼|우유", {"카페라떼"}),
    ("커피가|원두|샷이", {"아메리카노", "카페라떼"}), ("토핑|도우|치즈가", {"페퍼로니 피자", "포테이토 피자", "콤비네이션 피자", "불고기 피자", "고구마 피자", "치즈 피자 미디엄"}),
    ("크림", {"조각케이크", "마카롱 세트"}), ("펄|밀크티", {"버블티"}), ("버터 향|바삭함이 하나도", {"크로플"}),
    ("탕수육|부먹", {"탕수육 소", "탕수육 대"}), ("순대가|내장", {"순대"}), ("김밥 속|단무지", {"김밥", "참치김밥"}),
    ("떡이", {"떡볶이", "떡볶이 세트", "라볶이"}), ("양념이 너무 달|양념이 짭짤|양념에 튀김|양념이 속까지", {"양념치킨", "반반치킨", "간장치킨", "매운 양념치킨"}),
    ("닭이|튀김옷이 얇", {"후라이드", "순살 후라이드", "양념치킨", "반반치킨", "간장치킨", "매운 양념치킨"}),
    ("마라|향신료", {"마라탕"}), ("족발|껍데기|쌈 채소|비계", {"족발 중", "보쌈 중"}),
]
bad_menu = []
for rx, ok_menus in MENU_RULES:
    hit = rv[rv.review_text.str.contains(rx, regex=True) & ~rv.menu.isin(ok_menus)]
    bad_menu += [f"{r.order_id}({r.menu}: {rx})" for r in hit.itertuples()]
check("리뷰 표현이 그 행의 메뉴와 맞음", not bad_menu, f"어긋남 {len(bad_menu)}건 {bad_menu[:5]}")
rmap = {"긍정": {4, 5}, "중립": {2, 3, 4}, "부정": {1, 2, 3}}
bad_rating = rv[~rv.apply(lambda r: r.rating in rmap[r.sentiment], axis=1)]
check("리뷰와 행이 맞음(늦음·빠름·시험 언급·평점)", len(bad_slow) + len(bad_fast) + len(bad_exam) + len(bad_rating) == 0,
      f"늦음 {len(bad_slow)}, 빠름 {len(bad_fast)}, 시험 {len(bad_exam)}, 평점 {len(bad_rating)}")
texts = rv.review_text
vc = texts.value_counts()
uniq = texts.nunique() / len(texts)
sent_tok = texts.str.replace(r" ?(ㅎㅎㅎ|ㅎㅎ|ㅋㅋ|ㅠㅠ|ㅠ|ㅡㅡ)$", "", regex=True).str.split(r"(?<=[.!~])\s").explode()
top_sent = sent_tok.value_counts()
check("리뷰 반복이 티 나지 않음(서로 다른 글 90% 이상, 같은 글 최대 6번, 가장 흔한 문장 4% 미만)",
      uniq >= .90 and vc.max() <= 6 and top_sent.iloc[0] / len(texts) < .04,
      f"서로 다른 글 {uniq:.1%}, 최다 반복 {vc.max()}번('{vc.index[0]}'), 가장 흔한 문장 '{top_sent.index[0]}' {top_sent.iloc[0] / len(texts):.1%}")

# 기말고사(16주차)
W = cum("w16")
Wd = W[W.status == "완료"]
fin = (pd.Timestamp(FINAL[0]), pd.Timestamp(FINAL[1]))
r_fin = exam_ratio(Wd, fin, lambda d: (d >= "2025-05-26") & (d <= "2025-06-15") & (d.dt.day_of_week < 5))
check("기말고사(16주차) 야식·치킨·카페디저트 약 1.4배(13~15주 평일 대비)", 1.28 <= r_fin[0] <= 1.52, f"{r_fin[0]:.2f}배")

# ---------------------------------------------------------------------------
# data_facts.md 쓰기
# ---------------------------------------------------------------------------
L = []
w = L.append
fails = [c for c in checks if not c[2]]
w("# 실습 데이터 정답표 (data_facts)\n")
w("`make_data.py`로 만든 가상 데이터의 실제 값이다. `check_data.py`가 CSV를 읽어 자동으로 쓴 파일이므로 손으로 고치지 않는다. "
  "교안·대본의 정답 숫자는 여기서 가져다 쓴다.\n")
w("- 다시 만들기: `_tools/.venv/Scripts/python.exe _tools/make_data.py` → `_tools/.venv/Scripts/python.exe _tools/check_data.py`")
w("- 행 번호: 엑셀 행 번호 = pandas index + 2(1행은 머리글). 아래 '엑셀 N행'은 원본 CSV를 엑셀로 열었을 때의 행이다.")
w("- 금액 단위는 원. 비율은 소수 첫째 자리 반올림.")
w("- 리뷰 감성·주제·함정 정답은 `_tools/answer_key.csv`(배포하지 않음). 감성·주제 비율은 이 정답표 기준이다.\n")
w(f"## 검증 결과\n\n{len(checks)}개 항목 중 {len(checks) - len(fails)}개 통과" + (f", **{len(fails)}개 실패**." if fails else ".") + "\n")
w("| 항목 | 결과 | 통과 |\n| --- | --- | --- |")
for n_, d_, ok_ in checks:
    w(f"| {n_} | {str(d_).replace('|', '/')} | {'통과' if ok_ else '**실패**'} |")

w("\n## 1. 파일과 행 수\n")
w("| 파일 | 원본 행 | 기간 | 정제 뒤 행 | 정제 뒤 리뷰 |\n| --- | --- | --- | --- | --- |")
for f in FILES:
    w(f"| `{FNAME[f]}` | {n_rows[f]:,} | {RANGES[f][0]} ~ {RANGES[f][1]} | {len(cl[f]):,} | {rev_counts[f]:,} |")
w(f"\n열 18개 공통. 합계 원본 {sum(n_rows.values()):,}행. 인코딩 UTF-8(BOM 있음).")
w("13주차 정제 뒤 행 수에는 기본 파일과 겹치는 주문이 들어 있다. 누적할 때 order_id로 빼면 아래 누적표가 된다.\n")

w("## 2. 정제 규칙\n")
w("설계 페이지에 정해진 것은 ①평점·리뷰 빈칸은 정상이라 그대로 둔다 ②취소 주문은 지우지 않고 매출에서만 뺀다 "
  "③같은 주문번호에 금액만 다른 행은 사람이 판단한다, 세 가지다. 나머지는 이 자료에서 정한 기준 규칙이며 아래 숫자는 모두 이 규칙으로 계산했다.\n")
w("| 순서 | 문제 | 처리 | 출처 |\n| --- | --- | --- | --- |")
rules = [
    ("1", "완전히 같은 행", "하나만 남기고 지움", "자료 기준"),
    ("2", "날짜 형식 3가지, 금액 `12,500원`, 표기 흔들림", "날짜 `YYYY-MM-DD HH:MM`, 금액 숫자, 앞뒤 공백 제거 뒤 표기 통일표대로", "자료 기준"),
    ("3", "같은 order_id에 금액만 다른 행", "수량×단가+배달비-할인과 맞는 행을 남기고 다른 행을 지움(정확히 한 행이 맞게 만들어 둠)", "설계: 사람 판단 / 자료 기준"),
    ("4", "수량 0", "있을 수 없는 주문이라 분석에서 뺌", "자료 기준"),
    ("5", "total_amount ≠ 수량×단가+배달비-할인", "계산값으로 고치고 고친 행을 기록(환불은 음수 계산값)", "자료 기준"),
    ("6", "배달 시간 999분·0분", "기록 오류로 보고 빈칸(행은 남겨 매출에 포함, 배달 시간 분석에서만 빠짐)", "자료 기준"),
    ("7", "delivery_area 빈칸", "`미상`으로 채움", "자료 기준"),
    ("8", "rating·review_text 빈칸", "리뷰를 안 쓴 정상 빈칸이라 그대로", "설계"),
    ("9", "delivery_minutes 빈칸", "취소 주문은 정상 빈칸, 나머지는 기록 누락. 둘 다 그대로 두고 배달 시간 분석에서만 뺌", "자료 기준"),
    ("10", "취소·환불", "지우지 않음. 매출 = status `완료`의 total_amount 합계(취소·환불 제외)", "설계(취소) / 자료 기준(환불)"),
    ("11", "14주차 새 표기(8차시에 추가)", "category `떡볶이` → `분식`, payment_method `페이` → `간편결제`", "8차시 실습에서 사람이 정함"),
]
for r in rules:
    w("| " + " | ".join(r) + " |")
w("\n표기 통일표: category " + ", ".join(f"`{k}`→`{v}`" for k, v in CAT_MAP.items()) + ", 앞뒤 공백(`치킨 ` 등) 제거 / "
  "payment_method " + ", ".join(f"`{k}`→`{v}`" for k, v in PAY_MAP.items()) + " / delivery_area " +
  ", ".join(f"`{k}`→`{v}`" for k, v in AREA_MAP.items()) + "\n")

w("### 기본 파일 정제 단계별 행 수\n")
w("| 단계 | 행 수 |\n| --- | --- |")
for s_, n_ in info["w01-12"]["log"]:
    w(f"| {s_} | {n_:,} |")
ib = info["w01-12"]
w(f"\n- 지운 행: 완전 중복 {ib['dup']}, 금액만 다른 중복 {ib['conflict_drop']}, 수량 0 {ib['qty0']} → 합계 {ib['dup'] + ib['conflict_drop'] + ib['qty0']}행")
w(f"- 고친 행: 계산 불일치 {ib['mismatch']}행, 배달 시간 이상치 빈칸 {ib['dm_out']}행, 지역 미상 {int((B.delivery_area == '미상').sum())}행\n")

w("## 3. 기본 파일 품질 점검표(2차시 정답)\n")
w("원본 `orders_2025_w01-12.csv` 글자 그대로 센 값이다.\n")
w("| 문제 | 개수 | 예시(order_id, 엑셀 행) |\n| --- | --- | --- |")
r0 = raw["w01-12"]


def ex(mask, n=3):
    idx = r0.index[mask][:n]
    return ", ".join(f"{r0.order_id[i]}(엑셀 {i + 2}행)" for i in idx)


dupmask = r0.duplicated()
confmask = r0.order_id.isin(b["conflict_ids"]) & ~dupmask
w(f"| rating 빈칸 | {b['blank']['rating']:,} ({b['blank']['rating'] / nb:.1%}) | 리뷰를 안 쓴 정상 빈칸 |")
w(f"| review_text 빈칸 | {b['blank']['review_text']:,} ({b['blank']['review_text'] / nb:.1%}) | 리뷰를 안 쓴 정상 빈칸 |")
w(f"| delivery_minutes 빈칸 | {b['blank']['delivery_minutes']} ({b['blank']['delivery_minutes'] / nb:.1%}) | 취소 주문 {b['dm_blank_cancel']}(정상) + 기록 누락 {b['dm_blank_other']}: {ex((r0.delivery_minutes == '') & (r0.status != '취소'))} |")
w(f"| delivery_area 빈칸 | {b['blank']['delivery_area']} ({b['blank']['delivery_area'] / nb:.1%}) | {ex(r0.delivery_area == '')} |")
w(f"| 완전히 같은 행(두 번째 이후) | {b['dup']} | {ex(dupmask)} |")
w(f"| 같은 order_id에 금액만 다른 행 | {len(b['conflict_ids'])}쌍 | {', '.join(b['conflict_ids'])} |")
w(f"| 날짜 형식 | 표준 {b['dt']['표준']:,} · 점(`2025.3.5 18:32`) {b['dt']['점']} · 미국식(`03/05/2025 6:32 PM`) {b['dt']['미국식']} | 점 {ex(r0.order_datetime.map(dt_kind) == '점', 2)} / 미국식 {ex(r0.order_datetime.map(dt_kind) == '미국식', 2)} |")
w(f"| 금액이 글자(`12,500원` 꼴) | {b['amt_str']} ({b['amt_str'] / nb:.1%}) | {ex(r0.total_amount.str.contains('원'))}, `12,500원` {ex(r0.total_amount == '12,500원', 1)} |")
w(f"| category 표기 흔들림 | {ncv} ({ncv / nb:.1%}) | " + ", ".join(f"`{k}` {v}" for k, v in b["cat_var"].items()) + " |")
w(f"| payment_method 표기 흔들림 | {sum(b['pay_var'].values())} | " + ", ".join(f"`{k}` {v}" for k, v in b["pay_var"].items()) + " |")
w(f"| delivery_area 표기 흔들림 | {sum(b['area_var'].values())} | " + ", ".join(f"`{k}` {v}" for k, v in b["area_var"].items()) + " |")
w(f"| 배달 999분 | {b['dm999']} | {ex(r0.delivery_minutes == '999', 4)} |")
w(f"| 배달 0분 | {b['dm0']} | {ex(r0.delivery_minutes == '0')} |")
w(f"| 수량 0 | {b['qty0']} | {ex(r0.quantity == '0')} |")
mis_ids = cl["w01-12"][cl["w01-12"].amount_fixed]
w(f"| 계산 불일치(형식 통일·중복 정리 뒤) | {ib['mismatch']} ({ib['mismatch'] / nb:.1%}) | " +
  ", ".join(f"{r.order_id}(엑셀 {r.excel_row}행)" for r in mis_ids.head(3).itertuples()) + " |")
w(f"| 상태 | 완료 {st['완료']:,} · 취소 {st['취소']} · 환불 {st['환불']} | 환불은 음수 금액 {b['neg']}행 |")
w(f"| 리뷰 있는 행(원본, 중복 포함) | {b['reviews_raw']:,} | 정제 뒤 {rev_counts['w01-12']:,} |\n")

w("## 4. 1차시 실습용(원본 앞부분 합계)\n")
for n_ in (20, 30):
    h = r0.head(n_)
    s_all = num(h.total_amount).sum()
    s_done = num(h.total_amount[h.status == "완료"]).sum()
    notes = []
    for i, r in h.iterrows():
        if r.status != "완료" or not re.fullmatch(r"-?\d+", r.total_amount):
            notes.append(f"엑셀 {i + 2}행 {r.order_id} {r.status} `{r.total_amount}`")
    w(f"- 앞 {n_}행 total_amount 합계(글자 금액도 숫자로 읽음): {won(s_all)} / 완료만: {won(s_done)}" + (f" — 주의 행: {'; '.join(notes)}" if notes else ""))
w("")

w("## 5. 기본 파일 분석 정답(정제 뒤, 3차시)\n")
w("주문 건수·매출은 status `완료`만 센다. 시간대·요일 표도 `완료` 기준.\n")
tot_done = Bd.total_amount.sum()
tot_net = B[B.status != "취소"].total_amount.sum()
naive = num(raw["w01-12"].total_amount).sum()
w("### 핵심 지표\n")
w("| 지표 | 값 |\n| --- | --- |")
w(f"| 매출(완료 합계) | {won(tot_done)} |")
w(f"| 참고: 환불을 빼고 셈(완료+환불 음수) | {won(tot_net)} |")
w(f"| 참고: 정제 전 원본 total_amount 단순 합(글자 금액 숫자로, 중복·취소 포함) | {won(naive)} |")
w(f"| 완료 주문 수 | {len(Bd):,} |")
w(f"| 건당 평균 금액 | {won(Bd.total_amount.mean())} (중앙값 {won(Bd.total_amount.median())}) |")
w(f"| 취소 / 환불 | {int((B.status == '취소').sum())}건 ({(B.status == '취소').mean():.1%}) / {int((B.status == '환불').sum())}건 |")
w(f"| 평균 평점(리뷰 있는 주문) | {B.rating.mean():.2f} (리뷰 {rev_counts['w01-12']:,}개) |")
w(f"| 평균 배달 시간(이상치 뺀 뒤) | {B.delivery_minutes.mean():.1f}분 (중앙값 {B.delivery_minutes.median():.0f}분) |\n")
w("### 카테고리별\n")
w("| 카테고리 | 건수 | 매출 | 건당 금액 |\n| --- | --- | --- | --- |")
for c_, r in cat.sort_values("sum", ascending=False).iterrows():
    w(f"| {c_} | {int(r['count']):,} | {won(r['sum'])} | {won(r['mean'])} |")
w("\n### 지역별\n")
area_all = Bd.groupby("delivery_area").agg(count=("total_amount", "size"), sum=("total_amount", "sum"), mean=("total_amount", "mean"))
dm_area = B.groupby("delivery_area").delivery_minutes.mean()
rt_area = B.groupby("delivery_area").rating.mean()
w("| 지역 | 건수 | 매출 | 건당 금액 | 평균 배달 시간 | 평균 평점 |\n| --- | --- | --- | --- | --- | --- |")
for a_, r in area_all.sort_values("count", ascending=False).iterrows():
    w(f"| {a_} | {int(r['count']):,} | {won(r['sum'])} | {won(r['mean'])} | {dm_area[a_]:.1f}분 | {rt_area.get(a_, np.nan):.2f} |")
w("\n### 카테고리 × 지역 매출(피벗)\n")
pv = Bd.pivot_table(index="category", columns="delivery_area", values="total_amount", aggfunc="sum", fill_value=0)
pv = pv[[a for a in AREAS + ["미상"] if a in pv.columns]]
w("| 카테고리 | " + " | ".join(pv.columns) + " |\n| --- |" + " --- |" * len(pv.columns))
for c_, r in pv.iterrows():
    w(f"| {c_} | " + " | ".join(f"{int(v):,}" for v in r) + " |")
w("\n### 시간대·요일\n")
w("시간대별 완료 주문 수(0·1시는 그날 새벽): " + ", ".join(f"{h}시 {v}" for h, v in by_hour.items()))
w(f"\n- 최고 시간대: {by_hour.idxmax()}시({by_hour.max()}건). 상위 3: {', '.join(f'{h}시' for h in top3)}. 21시 {by_hour[21]}건으로 꺼졌다가 22시 {by_hour[22]}·23시 {by_hour[23]}건 야식 봉우리")
w("- 22~01시 주문 비율(지역별): " + ", ".join(f"{k} {v:.1%}" for k, v in ns.sort_values(ascending=False).items()))
w("- 요일별 하루 평균 완료 주문: " + ", ".join(f"{DOW_KO[i]} {v:.1f}" for i, v in per_dow.items()) +
  f" → 최고 {DOW_KO[per_dow.idxmax()]}, 2위 {DOW_KO[per_dow.sort_values().index[-2]]}")
w("- 요일별 하루 평균 점심(11~13시) 주문: " + ", ".join(f"{DOW_KO[i]} {v:.1f}" for i, v in lunch.items()))
hw = Bd.groupby(["dow", "hour"]).size().unstack(fill_value=0)
hw = hw.div(ndays, axis=0)
mx = hw.stack().sort_values(ascending=False)
w("- 시간대×요일 하루 평균 주문 상위 5칸: " + ", ".join(f"{DOW_KO[d_]} {h_}시 {v:.1f}" for (d_, h_), v in mx.head(5).items()) + "\n")
w("### 시험 기간(가상 중간고사 2025-04-21~25, 월~금)\n")
w(f"야식·치킨·카페디저트 하루 평균 완료 주문: 시험 기간 {r_wd[1]:.1f}건\n")
w("| 비교 기준 | 기준 하루 평균 | 배율 |\n| --- | --- | --- |")
w(f"| 시험 기간 밖 월~금 | {r_wd[2]:.1f} | {r_wd[0]:.2f}배 |")
w(f"| 시험 기간 밖 모든 날(금·토 포함이라 배율이 작게 나옴) | {r_all[2]:.1f} | {r_all[0]:.2f}배 |")
w(f"| 바로 앞뒤 주 월~금(04-14~18, 04-28~05-02) | {r_adj[2]:.1f} | {r_adj[0]:.2f}배 |")
w(f"| 참고: 나머지 4개 카테고리(시험 밖 월~금 대비) | {r_oth[2]:.1f} | {r_oth[0]:.2f}배 |\n")
w("### 배달 시간과 평점(상관 vs 인과)\n")
w("평점이 있고 배달 시간이 빈칸이 아닌 주문(취소 제외, 정제 뒤). '지역 안'은 지역별 평균을 뺀 뒤 구한 상관(지역을 통제한 값).\n")
w("| 범위 | n | 전체 r | 지역 안 r | " + " | ".join(AREAS) + " |\n| --- | --- | --- | --- |" + " --- |" * len(AREAS))
for lbl, (o, per, pooled, n, nn) in corr_res.items():
    w(f"| {lbl} | {n:,} | {o:.2f} | {pooled:.2f} | " + " | ".join(f"{per.get(a, np.nan):.2f} (n={nn.get(a, 0)})" for a in AREAS) + " |")
w(f"\n- 참고: 정제 전 원본(999분·0분 포함)으로 구하면 r = {raw_corr:.2f}. 이상치가 상관을 흐린다.")
w(f"- 해석 근거: 원룸촌은 평균 배달 {dm_area['원룸촌']:.1f}분·평점 {rt_area['원룸촌']:.2f}로 다른 지역(배달 {dm_area.drop(['원룸촌', '미상'], errors='ignore').min():.1f}~{dm_area.drop(['원룸촌', '미상'], errors='ignore').max():.1f}분, 평점 {rt_area.drop(['원룸촌', '미상'], errors='ignore').min():.2f}~{rt_area.drop(['원룸촌', '미상'], errors='ignore').max():.2f})보다 배달이 길고 평점이 낮다. 지역 안에서 보면 관계가 거의 사라진다.\n")

w("## 6. 리뷰(4·9차시)\n")
w(f"- 리뷰 수(정제 뒤): 기본 {rev_counts['w01-12']:,} / 13주차까지 누적 {cum_rev['w13']:,} / 14주차까지 {cum_rev['w14']:,} / 15주차까지 {cum_rev['w15']:,} / 16주차 파일 {rev_counts['w16']} (16주차까지 누적 {cum_rev['w16']:,})")
for lbl, fs in (("기본", ["w01-12"]), ("15주차까지 누적", ["w01-12", "w13", "w14", "w15"]), ("16주차까지 누적", FILES)):
    kk = pd.concat([kclean(f) for f in fs])
    kk = kk[kk.sentiment != ""]
    ss = kk.sentiment.value_counts()
    tt = kk.topic.value_counts()
    w(f"- 감성({lbl}, {len(kk):,}개): " + ", ".join(f"{k} {v} ({v / len(kk):.1%})" for k, v in ss.items()) +
      " / 주제: " + ", ".join(f"{k} {v} ({v / len(kk):.1%})" for k, v in tt.items()))
kb = kclean("w01-12")
kb = kb[kb.sentiment != ""]
mixed = kb[kb.topic2 != ""]
w(f"- 주제를 두 개 담은 리뷰(정답표 topic2): 기본 {len(mixed)}개. 주제 정답은 주된 주제 하나(topic) 기준")
w(f"- 평점 분포(기본): " + ", ".join(f"{int(k)}점 {v}" for k, v in B.rating.value_counts().sort_index().items()))
w(f"- 키워드 함정 리뷰: 기본 {int((kb.trap != '').sum())}개, 전체 {len(traps)}개. 함정 유형별 예시(기본 파일):\n")
import importlib.util

spec = importlib.util.spec_from_file_location("rb", TOOLS / "review_bank.py")
rbm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rbm)
w("| 유형 | 정답 감성·주제 | 기본 파일 개수 | 예시 order_id |\n| --- | --- | --- | --- |")
kb2 = kb.merge(cl["w01-12"][["order_id", "review_text"]], on="order_id")
for i, tr in enumerate(rbm.TRAPS, start=1):
    sub = kb2[kb2.trap == str(i)]
    sname = {"pos": "긍정", "neg": "부정", "neu": "중립"}[tr[1]]
    w(f"| \"{tr[0][0]}\" 류 | {sname}·{tr[2]} | {len(sub)} | {', '.join(sub.order_id.head(2))} |")
w(f"\n- 리뷰 글 반복: 서로 다른 글 {uniq:.1%}, 같은 글 최다 {vc.max()}번, 가장 흔한 문장 '{top_sent.index[0]}' {top_sent.iloc[0] / len(texts):.1%}\n")

w("## 7. 주차 파일(7~10차시)\n")
w("| 파일 | 원본 행 | 완전 중복 | 금액만 다른 중복 | 계산 불일치 | 금액 글자 | 날짜 점·미국식 | 표기 흔들림(cat/pay/area) | 999분·0분·수량0 | 배달 기록 누락 | 지역 빈칸 | 리뷰(정제 뒤) |")
w("| --- |" + " --- |" * 11)
for f in FILES[1:]:
    x = ri[f]
    w(f"| `{FNAME[f]}` | {x['rows']} | {x['dup']} | {len(x['conflict_ids'])} | {info[f]['mismatch']} | {x['amt_str']} | "
      f"{x['dt'].get('점', 0)}·{x['dt'].get('미국식', 0)} | {sum(x['cat_var'].values())}/{sum(x['pay_var'].values())}/{sum(x['area_var'].values())} | "
      f"{x['dm999']}·{x['dm0']}·{x['qty0']} | {x['dm_blank_other']} | {x['blank']['delivery_area']} | {rev_counts[f]} |")
w("\n(14주차의 category 흔들림 수에는 새 표기 `떡볶이`가 들어 있음)\n")
w(f"- 13주차 겹침: 기본 파일 마지막 날(2025-05-25) 주문 {len(ov)}건이 파일 맨 앞(엑셀 2~{len(ov) + 1}행)에 다시 들어 있다: {', '.join(ov.order_id)}. "
  "order_id로 이미 붙인 주문을 빼지 않으면 누적 파일에 두 번 들어간다.")
w(f"- 14주차 새 표기: category `떡볶이` {len(pos_cat)}행(엑셀 " + ", ".join(str(i + 2) for i in pos_cat) + "행), "
  f"payment_method `페이` {len(pos_pay)}행(엑셀 " + ", ".join(str(i + 2) for i in pos_pay) + "행). 둘 다 기본 파일과 데이터 사전에 없는 값")
w(f"  - `떡볶이` 행 order_id: {', '.join(w14.order_id[pos_cat])}")
w(f"  - `페이` 행 order_id: {', '.join(w14.order_id[pos_pay])}")
cl14_norule, _ = clean(raw["w14"], new_rules=False)
w(f"  - 새 규칙 없이 정제하면 category 값이 {cl14_norule.category.nunique()}종, payment_method가 {cl14_norule.payment_method.nunique()}종으로 남는다")
w("- 15·16주차: 기본 파일에 없던 표기나 날짜 형식이 없다(새 문제 없음).")
w(f"- 16주차(가상 기말고사 2025-06-16~20): 야식·치킨·카페디저트 하루 평균 완료 주문 {r_fin[1]:.1f}건, 13~15주 월~금 {r_fin[2]:.1f}건 → {r_fin[0]:.2f}배. "
  f"16주차 원본 {n_rows['w16']}행은 15주차 {n_rows['w15']}행의 {n_rows['w16'] / n_rows['w15']:.2f}배\n")
w("### 누적(정제 뒤, order_id 중복 뺌)\n")
w("| 붙인 파일까지 | 누적 행 | 누적 완료 주문 | 누적 매출(완료) | 누적 리뷰 | 이번에 새로 붙은 행 |\n| --- | --- | --- | --- | --- | --- |")
prev_n = 0
for f in FILES:
    D = cum(f)
    Dd = D[D.status == "완료"]
    w(f"| {f} | {len(D):,} | {len(Dd):,} | {won(Dd.total_amount.sum())} | {cum_rev[f]:,} | {len(D) - prev_n:,} |")
    prev_n = len(D)
w("\n### 16주차까지 누적 핵심 지표(10차시 대시보드)\n")
Wc = W[W.status == "완료"]
w(f"- 매출 {won(Wc.total_amount.sum())}, 완료 주문 {len(Wc):,}, 건당 {won(Wc.total_amount.mean())}, 평균 평점 {W.rating.mean():.2f}, 리뷰 {cum_rev['w16']:,}")
wk = Wc.assign(week=((Wc.date - pd.Timestamp("2025-03-03")).dt.days // 7 + 1)).groupby("week").agg(n=("order_id", "size"), sales=("total_amount", "sum"))
w("- 주차별 완료 주문 수: " + ", ".join(f"{i}주 {r.n}" for i, r in wk.iterrows()))
bw = Wc[Wc.category.isin(BOOST)].assign(week=lambda x: (x.date - pd.Timestamp("2025-03-03")).dt.days // 7 + 1).groupby("week").size()
w("- 주차별 야식·치킨·카페디저트 완료 주문 수: " + ", ".join(f"{i}주 {v}" for i, v in bw.items()) + "\n")

w("## 8. 설계안과 다른 점\n")
w(f"- delivery_minutes 빈칸: 설계는 '약 2%(취소 주문은 정상, 나머지는 기록 누락)'. 취소가 약 4%라 취소를 모두 빈칸으로 두면 2%를 넘는다. "
  f"그래서 취소 주문은 모두 빈칸, 그 밖에 배달된 주문의 약 2%를 기록 누락으로 비웠다. 기본 파일 빈칸 합계 {b['blank']['delivery_minutes']}행({b['blank']['delivery_minutes'] / nb:.1%}).")
w(f"- 16주차 행 수: 설계 약 450행. 시험 기간(06-16~20, 5일) 세 카테고리만 1.4배로 늘리면 {n_rows['w16']}행이 된다. 맞추려고 다른 증가를 더 넣지 않았다.")
w("- 정제 규칙 중 설계 페이지에 없는 것(위 규칙 표의 '자료 기준')은 이 자료에서 정한 기준이다. 교안에서 다른 규칙을 쓰면 정제 뒤 숫자가 달라진다.")
w("- 평점은 리뷰를 쓴 주문에만 있다(평점만 있고 글이 없는 주문은 없음).")
w("- `처리기록.md`는 설계 파일 표에 있지만 이번 제작 범위 밖이라 만들지 않았다. 7차시 실습 1이 처리 기록을 읽게 하므로 빈 시작 파일을 둘지 교안에서 정해야 한다.")
w(f"- 9차시 실습 1(누적 리뷰 전체 분류) 시점에는 14주차까지만 누적돼 리뷰가 {cum_rev['w14']:,}개다. 설계의 '약 1,400개'는 15주차까지 누적({cum_rev['w15']:,}개) 기준이라 실습 1 시점과 맞지 않는다.")
OUT.write_text("\n".join(L) + "\n", encoding="utf-8")

print(f"{len(checks)}개 중 {len(checks) - len(fails)}개 통과")
for n_, d_, ok_ in checks:
    if not ok_:
        print("실패:", n_, "→", d_)
print(f"→ {OUT}")
sys.exit(1 if fails else 0)
