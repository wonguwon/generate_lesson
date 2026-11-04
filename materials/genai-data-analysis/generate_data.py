"""온새미 카페 실습 데이터와 정답표를 만든다.

    python generate_data.py              # data/ 폴더의 CSV·압축 파일과 정답표.md를 만든다
    python generate_data.py --find-seed  # 조건을 모두 통과하는 시드를 찾는다

교안 조건은 validate()에 모았다. 하나라도 어긋나면 파일을 쓰지 않고 멈춘다.
"""
import argparse
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 2035

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

COLUMNS = ["주문번호", "주문일시", "지점", "메뉴", "카테고리", "수량", "단가", "금액", "결제수단", "회원여부"]

# 교안의 [지점 1·2·3] 순서. 가나다순이라 Codex 기본 정렬과 같다.
BRANCHES = ["공원점", "역앞점", "정문점"]
BRANCH_SHARE = np.array([0.33, 0.30, 0.37])

# 메뉴, 카테고리, 단가, 지점별 인기 가중치
MENUS = [
    ("아메리카노", "커피", 4500, (26, 30, 28)),
    ("카페라떼", "커피", 5000, (14, 17, 12)),
    ("바닐라라떼", "커피", 5500, (8, 6, 10)),
    ("카푸치노", "커피", 5200, (3, 4, 2.5)),
    ("콜드브루", "커피", 4800, (5, 8, 6)),
    ("에스프레소", "커피", 3800, (1.5, 2.5, 1)),
    ("카라멜마키아토", "커피", 5700, (4, 2.5, 7)),
    ("얼그레이", "티", 4600, (3, 1.5, 2)),
    ("캐모마일", "티", 4700, (2, 1, 1.5)),
    ("녹차", "티", 4400, (2.5, 1.8, 1.2)),
    ("유자차", "티", 5100, (4.5, 2, 3)),
    ("레몬에이드", "음료", 5300, (3.5, 2, 4.5)),
    ("자몽에이드", "음료", 5400, (2.8, 1.6, 3.6)),
    ("초코라떼", "음료", 5600, (3.2, 2.2, 2.6)),
    ("딸기스무디", "음료", 6000, (2.4, 1.2, 3.2)),
    ("치즈케이크", "디저트", 6800, (5, 2, 3.8)),
    ("티라미수", "디저트", 7200, (3.6, 1.4, 2.8)),
    ("크루아상", "디저트", 4200, (2.2, 6, 1.8)),
    ("스콘", "디저트", 3900, (1.8, 2.6, 1.4)),
    ("마들렌", "디저트", 3200, (1.6, 1.2, 2.2)),
]
NEW_MENUS = {"아이스 아메리카노": ("커피", 4500), "유자에이드": ("음료", 5900)}

MENU_NAMES = [m[0] for m in MENUS]
MENU_CATEGORY = np.array([m[1] for m in MENUS])
MENU_PRICE = np.array([m[2] for m in MENUS])
MENU_WEIGHT = np.array([m[3] for m in MENUS], dtype=float).T

# 1~12월 주문량 계수
MONTH_FACTOR = np.array([0.86, 0.82, 1.02, 1.04, 1.08, 0.98, 1.10, 1.14, 1.00, 1.05, 0.94, 1.22])
SLOT_NAMES = ["오전", "점심", "오후", "저녁"]
SLOT_HOURS = [(7, 11), (11, 14), (14, 17), (17, 22)]
SLOT_SHARE = np.array([
    [0.16, 0.26, 0.38, 0.20],  # 공원점: 오후
    [0.36, 0.28, 0.16, 0.20],  # 역앞점: 오전
    [0.17, 0.39, 0.22, 0.22],  # 정문점: 점심
])
WEEKEND_DAY_FACTOR = np.array([1.25, 0.70, 0.85])  # 지점별 주말 하루 주문량
QTY_WEEKDAY = np.array([0.66, 0.24, 0.07, 0.02, 0.01])
QTY_WEEKEND = np.array([0.60, 0.27, 0.09, 0.03, 0.01])

COUNTS_2025 = dict(
    orders=59950, dup=48, refund=720, q999=7, group=36, null_pay=318, null_member=412,
    spaced=350, text=940, ice=268, lower=132,
)
COUNTS_2026 = dict(
    orders=4990, dup=3, refund=58, q999=1, group=3, null_pay=26, null_member=33,
    spaced=29, text=78, ice=22, lower=11, new_ice=178, new_yuja=116,
)


def build_orders(rng, start, end, n, id_prefix):
    """오류가 없는 주문 표를 만든다. 금액은 항상 수량×단가."""
    days = pd.date_range(start, end, freq="D")
    branch = rng.choice(3, size=n, p=BRANCH_SHARE)

    day_idx = np.empty(n, dtype=int)
    weekend_day = (days.day_of_week >= 5).astype(float)
    for b in range(3):
        weight = MONTH_FACTOR[days.month - 1] * (1 + weekend_day * (WEEKEND_DAY_FACTOR[b] - 1))
        mask = branch == b
        day_idx[mask] = rng.choice(len(days), size=mask.sum(), p=weight / weight.sum())
    date = days[day_idx]
    weekend = date.day_of_week >= 5

    # 가중치는 지점·계절·요일에 따라 달라진다.
    summer = np.isin(date.month, [6, 7, 8, 9])
    winter = np.isin(date.month, [12, 1, 2])
    weight = MENU_WEIGHT[branch].copy()
    cold = np.isin(MENU_NAMES, ["콜드브루", "레몬에이드", "자몽에이드", "딸기스무디"])
    tea = MENU_CATEGORY == "티"
    weight[np.ix_(summer, cold)] *= 1.7
    weight[np.ix_(winter, tea)] *= 1.6
    weight[np.ix_(weekend, MENU_CATEGORY == "디저트")] *= 1.35
    cum = np.cumsum(weight, axis=1)
    cum /= cum[:, -1:]
    menu_idx = (rng.random(n)[:, None] > cum).sum(axis=1)

    slot = (rng.random(n)[:, None] > np.cumsum(SLOT_SHARE[branch], axis=1)).sum(axis=1).clip(0, 3)
    hour = np.array([rng.integers(*SLOT_HOURS[s]) for s in slot])
    minute = rng.integers(0, 60, n)

    qty = rng.choice(np.arange(1, 6), size=n, p=QTY_WEEKDAY)
    weekend_qty = rng.choice(np.arange(1, 6), size=n, p=QTY_WEEKEND)
    qty[weekend] = weekend_qty[weekend]

    df = pd.DataFrame({
        "주문일시": date + pd.to_timedelta(hour, "h") + pd.to_timedelta(minute, "m"),
        "지점": np.array(BRANCHES)[branch],
        "메뉴": np.array(MENU_NAMES)[menu_idx],
        "카테고리": MENU_CATEGORY[menu_idx],
        "수량": qty,
        "단가": MENU_PRICE[menu_idx],
        "결제수단": rng.choice(["카드", "간편결제", "현금", "상품권"], size=n, p=[0.58, 0.31, 0.08, 0.03]),
        "회원여부": rng.choice(["회원", "비회원"], size=n, p=[0.42, 0.58]),
    })
    df = df.sort_values("주문일시", kind="stable").reset_index(drop=True)
    df["주문번호"] = [f"{id_prefix}-{i:06d}" for i in range(1, n + 1)]
    return df


def inject_errors(df, rng, counts):
    """의도된 오류를 서로 겹치지 않는 행에 심는다."""
    df = df.copy()
    used = np.zeros(len(df), dtype=bool)

    def pick(mask, size):
        chosen = rng.choice(np.flatnonzero(mask & ~used), size=size, replace=False)
        used[chosen] = True
        return chosen

    for name, key in [("아이스 아메리카노", "new_ice"), ("유자에이드", "new_yuja")]:
        if counts.get(key):
            base = "아메리카노" if key == "new_ice" else "레몬에이드"
            chosen = pick((df["메뉴"] == base).to_numpy(), counts[key])
            df.loc[chosen, "메뉴"] = name
            df.loc[chosen, ["카테고리", "단가"]] = NEW_MENUS[name]

    americano = (df["메뉴"] == "아메리카노").to_numpy()
    df.loc[pick(americano, counts["ice"]), "메뉴"] = "아메리카노(ICE)"
    df.loc[pick(americano, counts["lower"]), "메뉴"] = "americano"

    everything = np.ones(len(df), dtype=bool)
    refund = pick(everything, counts["refund"])
    q999 = pick(everything, counts["q999"])
    group = pick(everything, counts["group"])
    df.loc[refund, "수량"] = -df.loc[refund, "수량"]
    df.loc[q999, "수량"] = 999
    df.loc[group, "수량"] = rng.integers(20, 51, counts["group"])

    df["금액"] = (df["수량"] * df["단가"]).astype(object)

    df.loc[pick(everything, counts["null_pay"]), "결제수단"] = ""
    df.loc[pick(everything, counts["null_member"]), "회원여부"] = ""

    spaced = pick(everything, counts["spaced"])
    forms = rng.integers(0, 3, counts["spaced"])
    for row, form in zip(spaced, forms):
        name = df.at[row, "지점"]
        df.at[row, "지점"] = [f" {name}", f"{name} ", f" {name} "][form]

    text = pick(everything, counts["text"])
    forms = rng.choice(3, size=counts["text"], p=[0.6, 0.3, 0.1])
    for row, form in zip(text, forms):
        value = int(df.at[row, "금액"])
        df.at[row, "금액"] = [f"{value:,}원", f"{value:,}", f"{value}원"][form]

    # 중복 쌍은 바로 아래 줄에 그대로 복사해 원본에서 바이트까지 같다.
    dup = pick(everything, counts["dup"])
    copies = df.iloc[dup]
    df = pd.concat([df, copies]).sort_index(kind="stable").reset_index(drop=True)

    df["주문일시"] = df["주문일시"].dt.strftime("%Y-%m-%d %H:%M")
    return df[COLUMNS]


def build_sample(raw, rng):
    """1차시 발췌본: 오류가 전혀 없는 평범한 행 50개."""
    plain = raw[
        raw["수량"].between(1, 5)
        & (raw["결제수단"] != "")
        & (raw["회원여부"] != "")
        & raw["지점"].isin(BRANCHES)
        & raw["금액"].map(lambda v: isinstance(v, (int, np.integer)))
        & raw["메뉴"].isin(MENU_NAMES)
        & ~raw.duplicated(keep=False)
    ]
    parts = []
    for branch, size in zip(BRANCHES, [19, 13, 18]):
        rows = plain[plain["지점"] == branch]
        parts.append(rows.iloc[rng.choice(len(rows), size=size, replace=False)])
    return pd.concat(parts).sort_values("주문일시", kind="stable")


def build_survey(rng, total=20000, dup=12):
    n = total - dup
    grade = rng.choice(4, size=n, p=[0.29, 0.27, 0.23, 0.21])
    study = np.clip(rng.normal(14 + grade * 1.5, 6.5, n), 0, 60).round().astype(int)
    sleep = np.clip(rng.normal(7.0 - 0.03 * (study - 14), 0.9, n), 3.5, 10.5).round(1)
    cafe = np.clip(rng.poisson(2.2 + 0.05 * study), 0, 14)
    job = rng.choice(["예", "아니오"], size=n, p=[0.44, 0.56])
    score = 2.6 + 0.28 * (sleep - 7) + 0.02 * (study - 14) - 0.15 * (job == "예") + rng.normal(0, 0.85, n)
    df = pd.DataFrame({
        "응답ID": [f"S{i:05d}" for i in range(1, n + 1)],
        "학년": [f"{g + 1}학년" for g in grade],
        "전공계열": rng.choice(["인문", "사회", "자연", "공학", "예체능", "의약"], size=n,
                            p=[0.16, 0.26, 0.15, 0.27, 0.09, 0.07]),
        "주당 공부시간": pd.array(study, dtype="Int64"),
        "평균 수면시간": sleep,
        "주당 카페 이용 횟수": cafe,
        "아르바이트 여부": job,
        "학교생활 만족도": pd.array(np.clip(score.round(), 1, 5).astype(int), dtype="Int64"),
    })
    order = rng.permutation(n)
    df.loc[order[:143], "주당 공부시간"] = pd.NA
    df.loc[order[143:329], "학교생활 만족도"] = pd.NA
    df.loc[order[329:347], "평균 수면시간"] = rng.choice([0.0, 24.5, 25.0, 30.0], size=18)
    df.loc[order[347:356], "학교생활 만족도"] = rng.choice([0, 6, 7], size=9)
    df.loc[order[356:361], "주당 공부시간"] = rng.choice([120, 168, 200], size=5)
    copies = df.iloc[order[361:361 + dup]]
    return pd.concat([df, copies]).sort_index(kind="stable").reset_index(drop=True)


def layers(raw):
    """교안의 계산 기준 층. L1 값 정리, L2 환불 제외, L3 정제본, L4 정제본에서 환불 제외."""
    l1 = raw.copy()
    l1["지점"] = l1["지점"].str.strip()
    l1["금액"] = l1["금액"].astype(str).str.replace("원", "").str.replace(",", "").astype(int)
    l1["일시"] = pd.to_datetime(l1["주문일시"], format="%Y-%m-%d %H:%M")
    l1["월"] = l1["일시"].dt.strftime("%Y-%m")
    l1["시간대"] = pd.cut(l1["일시"].dt.hour, [-1, 10, 13, 16, 24], labels=SLOT_NAMES).astype(str)
    l1["요일"] = l1["일시"].dt.day_of_week
    l2 = l1[l1["수량"] > 0]
    l3 = l1.drop_duplicates(subset=COLUMNS)
    l3 = l3[l3["수량"] != 999].copy()
    l3["메뉴"] = l3["메뉴"].replace({"아메리카노(ICE)": "아메리카노", "americano": "아메리카노"})
    l3["결제수단"] = l3["결제수단"].replace("", "미기록")
    l3["회원여부"] = l3["회원여부"].replace("", "미기록")
    l3["환불여부"] = np.where(l3["수량"] < 0, "Y", "N")
    l4 = l3[l3["환불여부"] == "N"]
    return l1, l2, l3, l4


def analyze(raw25, raw26, sample, survey):
    """정답표에 들어갈 값을 모두 계산한다."""
    l1, l2, l3, l4 = layers(raw25)
    n1, n2, n3, n4 = layers(raw26)
    r = dict(l1=l1, l2=l2, l3=l3, l4=l4, n1=n1, n2=n2, n3=n3, n4=n4)
    r["ann"] = l2.groupby("지점")["금액"].sum()
    r["can"] = l4.groupby("지점")["금액"].sum()
    r["piv"] = l4.pivot_table(index="지점", columns="월", values="금액", aggfunc="sum")
    r["h2"] = l2[l2["월"] >= "2025-07"].pivot_table(index="지점", columns="월", values="금액", aggfunc="sum")
    l2q = l2.assign(분기=l2["일시"].dt.quarter)
    r["quarter"] = l2q.pivot_table(index="지점", columns="분기", values="금액", aggfunc="sum")
    r["slot"] = l2.pivot_table(index="지점", columns="시간대", values="금액", aggfunc="sum")[SLOT_NAMES]
    r["top"] = {b: l2[l2["지점"] == b]["메뉴"].value_counts().sort_index()
                .sort_values(ascending=False, kind="stable") for b in BRANCHES}
    r["aov_cell"] = (l4.groupby(["요일", "시간대"])["금액"].sum() / l4.groupby(["요일", "시간대"]).size())
    end = l4["요일"] >= 5
    r["aov_weekend"] = l4[end]["금액"].sum() / end.sum()
    r["aov_weekday"] = l4[~end]["금액"].sum() / (~end).sum()
    r["cat"] = l4.groupby("카테고리")["금액"].sum().sort_values(ascending=False)
    r["growth"] = (r["piv"].iloc[0, 1] - r["piv"].iloc[0, 0]) / r["piv"].iloc[0, 0] * 100
    r["ratio"] = r["can"].max() / r["can"].min()
    r["new_piv"] = n4.groupby("지점")["금액"].sum()
    return r


def near_half(value, digits):
    """반올림 경계(마지막 자리 다음이 5 근처)면 True."""
    scaled = abs(value) * 10 ** digits
    return abs(scaled - np.floor(scaled) - 0.5) < 0.05


def validate(raw25, raw26, sample, survey, r):
    """교안과 설계 페이지의 데이터 조건. 어긋난 항목 이름을 돌려준다."""
    l1, l2, l3, l4 = r["l1"], r["l2"], r["l3"], r["l4"]
    n1, n3, n4 = r["n1"], r["n3"], r["n4"]
    fails = []

    def need(ok, name):
        if not bool(ok):
            fails.append(name)

    for label, raw, parsed in [("2025", raw25, l1), ("2026", raw26, n1)]:
        need((parsed["금액"] == parsed["수량"] * parsed["단가"]).all(), f"{label} 금액=수량×단가")
        need(parsed["지점"].nunique() == 3, f"{label} 지점 3곳")
        dup_rows = raw[raw.duplicated(keep=False)]
        need(len(dup_rows) % 2 == 0 and dup_rows.groupby("주문번호").size().eq(2).all(), f"{label} 중복은 2행 쌍")
        stripped = parsed.drop_duplicates(subset=COLUMNS)
        need(len(stripped) == len(raw) - len(dup_rows) // 2, f"{label} 정리 후 새 중복 없음")
        special = parsed[parsed.duplicated(subset=COLUMNS, keep=False)]
        need(special["수량"].between(1, 5).all(), f"{label} 중복에 환불·999·단체 없음")
        need(not ((raw["결제수단"] == "") & (raw["회원여부"] == "")).any(), f"{label} 빈 값 동시 없음")
        need(parsed[(parsed["수량"] < 1) | (parsed["수량"] > 5)]["수량"].map(
            lambda q: q == 999 or q < 0 or 20 <= q <= 50).all(), f"{label} 수량 범위")
        need(not parsed["수량"].eq(0).any(), f"{label} 수량 0 없음")
        need(raw["주문번호"].str.fullmatch(r"ORD-\d{4}-\d{6}").all(), f"{label} 주문번호 형식")

    need(l1["일시"].dt.year.eq(2025).all(), "2025 파일은 2025년만")
    need(l4["일시"].dt.date.min() == l1["일시"].dt.date.min(), "정제본 첫날 = 원본 첫날")
    need(l4["일시"].dt.date.max() == l1["일시"].dt.date.max(), "정제본 마지막 날 = 원본")
    need(str(l1["일시"].min())[:10] == "2025-01-01" and str(l1["일시"].max())[:10] == "2025-12-31", "2025 기간")
    need(str(n4["일시"].max())[:10] == "2026-01-31", "2026-01-31 정상 행")
    need(str(n4["일시"].min())[:10] == "2026-01-01", "2026-01-01 정상 행")
    need(not set(raw25["주문번호"]) & set(raw26["주문번호"]), "주문번호 파일 간 중복 없음")

    dec = l1[l1["월"] == "2025-12"]
    need(dec["지점"].nunique() == 3 and dec["일시"].dt.date.nunique() > 20, "12월 지점·날짜")
    need((dec["수량"] < 0).any() and raw25.loc[dec.index].duplicated().any(), "12월에 환불·중복")
    need((l1[l1["월"] >= "2025-07"]["수량"] < 0).any(), "하반기 환불")

    # 1차시
    groups = sample.groupby("지점")["금액"]
    need(sample["지점"].nunique() == 3 and groups.size().nunique() == 3 and groups.sum().nunique() == 3, "50행 지점별 값")

    # 2차시
    h2 = r["h2"]
    cells = h2.to_numpy().ravel()
    need((cells > 0).all() and len(set(cells)) == 18, "하반기 18칸")

    # 5차시
    need(r["quarter"].to_numpy().min() > 0 and len(set(r["quarter"].to_numpy().ravel())) == 12, "지점×분기 12칸")
    need(r["ann"].nunique() == 3, "지점별 연간 매출")

    # 7차시
    for branch, counts in r["top"].items():
        head = counts.head(6)
        need(head.is_unique, f"{branch} 1~6위 동률 없음")
        need(not set(head.index) & {"아메리카노(ICE)", "americano"}, f"{branch} 표기 흔들림이 6위 안")
    need(r["slot"].notna().all().all(), "지점×시간대 12칸")
    need(r["slot"].sum(axis=1).equals(r["ann"].loc[r["slot"].index]), "시간대 합 = 연간 매출")

    # 8·11차시
    need(l3.groupby("메뉴")["단가"].nunique().eq(1).all() and l3.groupby("메뉴")["단가"].first().is_unique,
         "메뉴 단가 고유")
    need(raw25["메뉴"].nunique() - l3["메뉴"].nunique() == 2, "메뉴 종류 전-후 = 2")
    first_month = l1.groupby("메뉴")["월"].min()
    need(first_month.max() < "2025-12", "모든 메뉴가 12월 이전에 등장")
    new_names = set(raw26["메뉴"]) - set(raw25["메뉴"])
    need(new_names == set(NEW_MENUS), "새 메뉴는 2개뿐")
    need(n3[n3["메뉴"].isin(NEW_MENUS)]["주문번호"].is_unique, "새 메뉴 중복 없음")
    need(r["new_piv"].nunique() == 3, "2026-01 지점별 매출")

    # 9차시
    need((r["piv"].to_numpy() > 0).all(), "지점×월 36칸")
    need(len(r["aov_cell"]) == 28, "요일×시간대 28칸")
    need(not near_half(r["aov_cell"].max(), 0) and not near_half(r["aov_cell"].min(), 0), "최고·최저 칸 반올림 경계")
    need(not near_half(l4["금액"].sum() / len(l4), 0), "전체 객단가 반올림 경계")
    need(not any(near_half(v, 1) for v in r["cat"] / r["cat"].sum() * 100), "카테고리 구성비 반올림 경계")
    rounded = r["aov_cell"].round().sort_values()
    need(rounded.iloc[0] < rounded.iloc[1] and rounded.iloc[-1] > rounded.iloc[-2], "최고·최저 칸 유일")
    need(round(r["aov_weekend"]) > round(r["aov_weekday"]), "주말 객단가 > 평일")
    need(l4[l4["요일"] >= 5]["금액"].sum() < l4[l4["요일"] < 5]["금액"].sum(), "평일 총매출 > 주말")
    need(not near_half(r["growth"], 1), "증감률 반올림 경계")
    need(not near_half(r["aov_weekend"], 0) and not near_half(r["aov_weekday"], 0), "객단가 반올림 경계")
    share = (r["cat"] / r["cat"].sum() * 100).round(1)
    need(share.is_unique, "카테고리 구성비 동률")

    # 10차시
    need(1.1 <= r["ratio"] <= 1.3, "최대÷최소 1.1~1.3")
    need(not near_half(r["ratio"], 2), "배수 반올림 경계")
    monthly = r["piv"].sum()
    need(monthly.sort_values().iloc[0] < monthly.sort_values().iloc[1], "월 합계 최소 유일")
    need(monthly.sort_values().iloc[-1] > monthly.sort_values().iloc[-2], "월 합계 최대 유일")
    total13 = pd.concat([monthly, pd.Series({"2026-01": r["new_piv"].sum()})]).sort_values()
    need(total13.iloc[0] < total13.iloc[1] and total13.iloc[-1] > total13.iloc[-2], "13개월 최대·최소 유일")

    # 설문
    need(survey.duplicated().sum() == 12, "설문 중복")
    need(len(survey) == 20000, "설문 행 수")
    return fails


def generate(seed):
    rng = np.random.default_rng(seed)
    raw25 = inject_errors(
        build_orders(rng, "2025-01-01", "2025-12-31", COUNTS_2025["orders"], "ORD-2025"), rng, COUNTS_2025)
    raw26 = inject_errors(
        build_orders(rng, "2026-01-01", "2026-01-31", COUNTS_2026["orders"], "ORD-2026"), rng, COUNTS_2026)
    sample = build_sample(raw25, rng)
    survey = build_survey(rng)
    return raw25, raw26, sample, survey


def won(value):
    return f"{int(value):,}원"


def table(headers, rows):
    lines = ["| " + " | ".join(map(str, headers)) + " |", "|" + " --- |" * len(headers)]
    lines += ["| " + " | ".join(map(str, row)) + " |" for row in rows]
    return "\n".join(lines)


def answer_sheet(raw25, raw26, sample, survey, r, seed):
    l1, l2, l3, l4, n1, n3, n4 = r["l1"], r["l2"], r["l3"], r["l4"], r["n1"], r["n3"], r["n4"]
    rows = len(raw25)
    h2 = r["h2"]
    refund_h2 = int((l1[l1["월"] >= "2025-07"]["수량"] < 0).sum())
    refund = int((l1["수량"] < 0).sum())
    null_pay = int((raw25["결제수단"] == "").sum())
    null_member = int((raw25["회원여부"] == "").sum())
    dup_mask = raw25.duplicated()
    dup_n = int(dup_mask.sum())
    dup_amount = int(l1[dup_mask]["금액"].sum())
    q999 = l1[l1["수량"] == 999]
    group = l1[(l1["수량"] >= 10) & (l1["수량"] != 999)]
    null_rows = l2[(l2["결제수단"] == "") | (l2["회원여부"] == "")]
    months = list(r["piv"].columns)
    first, last = l1["일시"].dt.date.min(), l1["일시"].dt.date.max()
    quarter = r["quarter"].stack()
    best = quarter.idxmax()
    aov_all = l4["금액"].sum() / len(l4)
    cell = r["aov_cell"]
    day = "월화수목금토일"
    p = []
    add = p.append

    add(f"""# 온새미 카페 실습 정답표

강사용 자료입니다. `generate_data.py`가 시드 {seed}로 만들었습니다. 다시 실행하면 같은 값이 나옵니다.

## 공통

{table(["교안 자리", "값"], [[f"[지점 {i + 1}]", b] for i, b in enumerate(BRANCHES)])}

- 카페 데이터 행: **{rows:,}** · 설문 데이터 행: **{len(survey):,}**
- 첫 날짜 **{first}** · 마지막 날짜 **{last}**
- 금액은 쉼표와 원을 붙여 적었습니다. CSV에는 쉼표 없는 숫자로 저장됩니다.

| 기호 | 기준 |
| --- | --- |
| L1 | 원본 전체. 지점 빈칸과 글자 금액만 정리 (환불·중복·999 포함) |
| L2 | L1에서 수량 < 0 제외 (5·7차시까지의 매출) |
| L4 | 8차시 정제본에서 환불여부 = N (9차시부터의 매출) |
""")

    groups = sample.groupby("지점")["금액"]
    add("## 1차시 실습 3 (cafe_sample_50.csv)\n")
    add(table(["지점", "행 수", "금액 합계"],
              [[b, groups.size()[b], won(groups.sum()[b])] for b in BRANCHES]
              + [["전체", len(sample), won(sample["금액"].sum())]]))

    annual_l1 = l1.groupby("지점")["금액"].sum()
    add("\n## 2차시\n\n실습 1 지점별 금액 합계 (L1, 환불 금액은 음수로 포함)\n")
    add(table(["지점", "금액 합계"], [[b, won(annual_l1[b])] for b in BRANCHES]))
    add("\n실습 2 하반기 지점×월 (L2)\n")
    add(table(["지점"] + [m[-2:] + "월" for m in h2.columns],
              [[b] + [won(v) for v in h2.loc[b]] for b in BRANCHES]))
    add(f"""
- 실습 2 뺀 환불 행 수(7~12월): **{refund_h2}**
- 실습 3 {BRANCHES[0]} 9월: **{won(h2.loc[BRANCHES[0], "2025-09"])}**
- 실습 3 {BRANCHES[1]} 12월: **{won(h2.loc[BRANCHES[1], "2025-12"])}**
- 참고: 실습 3 Codex가 걸러 낸 행 수. {BRANCHES[0]} 9월 {len(l1[(l1["지점"] == BRANCHES[0]) & (l1["월"] == "2025-09")]):,}행(환불 제외 {len(l2[(l2["지점"] == BRANCHES[0]) & (l2["월"] == "2025-09")]):,}행), {BRANCHES[1]} 12월 {len(l1[(l1["지점"] == BRANCHES[1]) & (l1["월"] == "2025-12")]):,}행(환불 제외 {len(l2[(l2["지점"] == BRANCHES[1]) & (l2["월"] == "2025-12")]):,}행)

## 3차시

- 실습 2 ④ 두 칸과 환불 행 수는 2차시와 같습니다.
- 참고: 하반기 글자 금액 값 수 {int(raw25.loc[l1[l1["월"] >= "2025-07"].index, "금액"].map(lambda v: isinstance(v, str)).sum())}개

## 4차시

- `12월주문.csv` 데이터 행: **{int((l1["월"] == "2025-12").sum()):,}** (환불·중복 포함, 12월의 수량 999 행 {int(((l1["월"] == "2025-12") & (l1["수량"] == 999)).sum())}개)

## 5차시

- 실습 1 뺀 환불 행 수(연간): **{refund}**
- 실습 1 매출이 가장 큰 지점·분기·금액: **{best[0]}, {best[1]}분기, {won(quarter.max())}**
""")
    add(table(["지점", "연간 매출 (L2)", "비율"],
              [[b, won(r["ann"][b]), f"{r['ann'][b] / r['ann'].sum() * 100:.1f}%"] for b in BRANCHES]
              + [["합계", won(r["ann"].sum()), "100%"]]))

    add(f"""
## 6차시

| 항목 | 카페 | 설문 |
| --- | --- | --- |
| 행 수 | {rows:,} | {len(survey):,} |
| 열 수 | 10 | 8 |
| 빈 값 | 결제수단 {null_pay}, 회원여부 {null_member} | 주당 공부시간 {int(survey["주당 공부시간"].isna().sum())}, 학교생활 만족도 {int(survey["학교생활 만족도"].isna().sum())} |
| 중복 행 | {dup_n} | {int(survey.duplicated().sum())} |
| 날짜 범위 | {first} ~ {last} | 날짜 열 없음 |

- 설문 열 이름 8개: {", ".join(survey.columns)}
- 범위 밖 값(교안 정답 자리 없음, 11차시 과제용): 평균 수면시간 18행(0, 24.5, 25, 30), 학교생활 만족도 9행(0, 6, 7), 주당 공부시간 5행(120, 168, 200)

## 7차시

실습 1 지점별 상위 5개 메뉴 (L2, 메뉴 이름 원본 그대로)
""")
    add(table(["지점", "1위", "2위", "3위", "4위", "5위"],
              [[b] + [f"{m} {n:,}건" for m, n in r["top"][b].head(5).items()] for b in BRANCHES]))
    add("\n실습 1 지점×시간대 매출 (L2)\n")
    add(table(["지점"] + SLOT_NAMES,
              [[b] + [won(v) for v in r["slot"].loc[b]] for b in BRANCHES]
              + [["합계"] + [won(v) for v in r["slot"].sum()]]))

    amer = raw25["메뉴"].value_counts()
    menu_before, menu_after = raw25["메뉴"].nunique(), l3["메뉴"].nunique()
    add(f"""
## 8차시

- 실습 2 빈 값: 결제수단 **{null_pay}**, 회원여부 **{null_member}**, 빈 값이 있는 행 **{null_pay + null_member}**
- 실습 2 중복 **{dup_n}**쌍
- 실습 2 빈 값 행을 지우면 합계가 줄어드는 금액: **{won(null_rows["금액"].sum())}**
- 실습 2 중복을 하나만 남기면 줄어드는 금액: **{won(dup_amount)}**
- 실습 3 수량 999 행: **{len(q999)}**
- 실습 3 수량 10 이상 999 아님: **{len(group)}**행, 가장 큰 값 **{group["수량"].max()}**
- 실습 3 표기별 행 수: 아메리카노 **{amer["아메리카노"]:,}**, 아메리카노(ICE) **{amer["아메리카노(ICE)"]}**, americano **{amer["americano"]}**
- 실습 3 뺀 행 수: 중복 **{dup_n}**, 999 **{len(q999)}**
- 실습 3 정제 후 행 수: **{len(l3):,}**
- 실습 3 메뉴 종류 수: **{menu_before} → {menu_after}**
- 실습 3 합계 차이: 중복 **{won(dup_amount)}**, 999 **{won(q999["금액"].sum())}**
- 참고: 지점 빈칸 행 {int((raw25["지점"] != l1["지점"]).sum())}개, 글자 금액 값 {int(raw25["금액"].map(lambda v: isinstance(v, str)).sum())}개, 환불여부 Y {refund}개
""")
    add(table(["지점", "정제 전", "정제 후", "차이"],
              [[b, won(r["ann"][b]), won(r["can"][b]), won(r["ann"][b] - r["can"][b])] for b in BRANCHES]
              + [["합계", won(r["ann"].sum()), won(r["can"].sum()), won(r["ann"].sum() - r["can"].sum())]]))

    hi, lo = cell.idxmax(), cell.idxmin()
    add(f"""
## 9차시

- 주문 건수 합: **{len(l4):,}** (정제 후 {len(l3):,} − 환불 {refund})
- 전체 객단가: **{won(round(aov_all))}**
- 가장 높은 칸: **{day[hi[0]]}요일 {hi[1]}, {won(round(cell.max()))}**
- 가장 낮은 칸: **{day[lo[0]]}요일 {lo[1]}, {won(round(cell.min()))}**
- 주말 객단가 **{won(round(r["aov_weekend"]))}** · 평일 객단가 **{won(round(r["aov_weekday"]))}**
- 주말 매출 {won(l4[l4["요일"] >= 5]["금액"].sum())} · 평일 매출 {won(l4[l4["요일"] < 5]["금액"].sum())}

표 1 요일×시간대 객단가
""")
    add(table(["요일"] + SLOT_NAMES,
              [[day[d] + "요일"] + [won(round(cell[(d, s)])) for s in SLOT_NAMES] for d in range(7)]))
    add("\n지점×월 매출 (L4)\n")
    piv = r["piv"]
    add(table(["월"] + BRANCHES + ["합계"],
              [[m] + [won(piv.loc[b, m]) for b in BRANCHES] + [won(piv[m].sum())] for m in months]))
    add(f"\n실습 3 {BRANCHES[0]} 2월 증감률: **{r['growth']:+.1f}%**\n")
    growth = piv.T.pct_change().mul(100)
    add("월별 증감률 (참고)\n")
    add(table(["월"] + BRANCHES,
              [[m] + [f"{growth.loc[m, b]:+.1f}%" for b in BRANCHES] for m in months[1:]]))
    cat_branch = l4.pivot_table(index="카테고리", columns="지점", values="금액", aggfunc="sum")
    share_branch = cat_branch / cat_branch.sum() * 100
    share = r["cat"] / r["cat"].sum() * 100
    add(f"\n카테고리 수: **{l3['카테고리'].nunique()}** · 가장 큰 카테고리: **{share.index[0]} {share.iloc[0]:.1f}%**\n")
    add(table(["카테고리"] + BRANCHES + ["전체"],
              [[c] + [f"{share_branch.loc[c, b]:.1f}%" for b in BRANCHES] + [f"{share[c]:.1f}%"] for c in share.index]))

    monthly = piv.sum()
    add(f"""
## 10차시

- 실습 2 실제 배수: **{r["ratio"]:.2f}배** ({r["can"].idxmax()} ÷ {r["can"].idxmin()})
- 가장 높은 달 {monthly.idxmax()} {won(monthly.max())} · 가장 낮은 달 {monthly.idxmin()} {won(monthly.min())}
- 막대 3개는 8차시 정제 후 매출, 선 12점은 9차시 합계 행입니다.

## 11차시
""")
    new_raw = n1["메뉴"].value_counts()
    add(f"""- cafe_sales_2026_01.csv 데이터 행: **{len(raw26):,}**
- 아이스 아메리카노: **{new_raw["아이스 아메리카노"]}**행, **{won(NEW_MENUS["아이스 아메리카노"][1])}**
- 유자에이드: **{new_raw["유자에이드"]}**행, **{won(NEW_MENUS["유자에이드"][1])}**
- 2026-01 정제 후 행 수: **{len(n3):,}** (합치면 {len(l3):,} + {len(n3):,} = {len(l3) + len(n3):,})
- 메뉴 종류: 첫 실행 {menu_after + 2}, 판단 후 {menu_after + 1}
""")
    add(table(["지점", "2026-01 매출 (L4)"],
              [[b, won(r["new_piv"][b])] for b in BRANCHES] + [["합계", won(r["new_piv"].sum())]]))

    naive = pd.to_numeric(raw25["금액"], errors="coerce")
    naive_branch = naive.groupby(raw25["지점"]).sum().sort_index()
    add(f"""
## 강사용: 정리하지 않은 기준

Codex나 ChatGPT가 정리 없이 계산했을 때 나오는 숫자입니다. 화면 값이 이렇게 나오면 어디서 틀렸는지 바로 짚을 수 있습니다.

- 숫자로 읽히는 금액만 더한 합계: {won(naive.sum())} (글자 금액 {int(naive.isna().sum())}개가 빠지고 환불은 음수로 더해짐)
- 지점 이름이 {raw25["지점"].nunique()}가지로 세어집니다.
""")
    add(table(["원본 지점 표기", "숫자 금액 합계"], [[f"`{k}`", won(v)] for k, v in naive_branch.items()]))

    add("\n## 1차시 토글에 붙일 50행 원문\n\n```\n" + sample.to_csv(index=False, lineterminator="\n") + "```\n")
    return "\n".join(p)


def write_outputs(raw25, raw26, sample, survey, r, seed):
    DATA_DIR.mkdir(exist_ok=True)
    files = {
        "cafe_sales_2025.csv": raw25,
        "cafe_sample_50.csv": sample,
        "student_survey.csv": survey,
        "cafe_sales_2026_01.csv": raw26,
    }
    for name, df in files.items():
        df.to_csv(DATA_DIR / name, index=False, encoding="utf-8-sig")

    with zipfile.ZipFile(DATA_DIR / "cafe_sales_2025.zip", "w", zipfile.ZIP_DEFLATED) as z:
        z.write(DATA_DIR / "cafe_sales_2025.csv", "cafe_sales_2025.csv")
    with zipfile.ZipFile(DATA_DIR / "cafe_sales_2026_01.zip", "w", zipfile.ZIP_DEFLATED) as z:
        z.write(DATA_DIR / "cafe_sales_2026_01.csv", "cafe_sales_2026_01.csv")
    with zipfile.ZipFile(DATA_DIR / "온새미카페_분석.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for name in ["cafe_sales_2025.csv", "student_survey.csv"]:
            z.write(DATA_DIR / name, f"온새미카페_분석/{name}")

    (BASE_DIR / "정답표.md").write_text(answer_sheet(raw25, raw26, sample, survey, r, seed), encoding="utf-8")


def run(seed):
    raw25, raw26, sample, survey = generate(seed)
    r = analyze(raw25, raw26, sample, survey)
    return (raw25, raw26, sample, survey), r, validate(raw25, raw26, sample, survey, r)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--find-seed", action="store_true")
    args = parser.parse_args()

    if args.find_seed:
        for seed in range(SEED, SEED + 200):
            _, _, fails = run(seed)
            print(seed, "통과" if not fails else fails)
            if not fails:
                return
        sys.exit("200개 시드에서 찾지 못했습니다.")

    data, r, fails = run(SEED)
    if fails:
        sys.exit(f"시드 {SEED} 조건 실패: {fails}")
    write_outputs(*data, r, SEED)
    print(f"완료: 카페 {len(data[0]):,}행, 새 달 {len(data[1]):,}행, 설문 {len(data[3]):,}행")


if __name__ == "__main__":
    main()
