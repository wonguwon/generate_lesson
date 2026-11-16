"""생성형 AI 기반 데이터 분석 과정 실습 데이터(가상) 생성 스크립트.

실행:
    _tools/.venv/Scripts/python.exe _tools/make_data.py

결과(data/, UTF-8 BOM):
    orders_2025_w01-12.csv   기본 파일, 2025-03-03 ~ 05-25 (1~12주)
    orders_2025_w13.csv      05-26 ~ 06-01
    orders_2025_w14.csv      06-02 ~ 06-08 (처음 보는 표기 두 가지)
    orders_2025_w15.csv      06-09 ~ 06-15
    orders_2025_w16.csv      06-16 ~ 06-22 (가상 기말고사 주간)
정답표(_tools/, 배포하지 않음):
    answer_key.csv           행마다 심은 문제, 리뷰 감성·주제·함정 여부

모든 값은 가상이다. 난수 시드를 고정해 몇 번을 실행해도 같은 파일이 나온다.
특징 검증과 정답 숫자 정리는 check_data.py가 한다.
"""

import csv
import datetime as dt
from pathlib import Path

import numpy as np

import review_bank as rb

import sys
sys.stdout.reconfigure(encoding="utf-8")

SEED = 20250303
TOOLS = Path(__file__).resolve().parent
DATA = TOOLS.parent / "data"

COLUMNS = ["order_id", "order_datetime", "store_id", "store_name", "category", "menu", "quantity", "unit_price",
           "delivery_fee", "discount", "total_amount", "payment_method", "delivery_area", "customer_id",
           "delivery_minutes", "status", "rating", "review_text"]

START = dt.date(2025, 3, 3)
N_WEEKS = 16
MIDTERM = (dt.date(2025, 4, 21), dt.date(2025, 4, 25))
FINAL = (dt.date(2025, 6, 16), dt.date(2025, 6, 20))
EXAM_BOOST = 1.4
BOOST_CATS = ["야식", "치킨", "카페디저트"]
BASE_DAILY = 51.8

CATS = ["치킨", "분식", "한식", "중식", "피자", "카페디저트", "야식"]
AREAS = ["기숙사", "정문", "후문", "쪽문", "원룸촌"]
HOURS = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 0, 1]

# ---------------------------------------------------------------------------
# 가게·메뉴(모두 지어낸 이름)
# ---------------------------------------------------------------------------
STORES = {
    "치킨": ["정문치킨", "바삭한통닭", "꼬꼬마치킨", "골목닭집", "황금튀김닭", "캠퍼스치킨", "두마리통닭"],
    "분식": ["후문떡볶이", "쪽문분식", "엄마손김밥", "매콤떡집", "오늘분식", "학교앞튀김"],
    "한식": ["든든한밥상", "할매찌개", "한그릇덮밥", "소담정식", "집밥식당", "뚝배기마을"],
    "중식": ["홍매반점", "청룡각", "금화루", "불꽃짬뽕", "소림반점"],
    "피자": ["치즈폭탄피자", "화덕공방", "대학로피자", "도우하우스", "한조각피자"],
    "카페디저트": ["달빛카페", "크로플공방", "오후의디저트", "몽글케이크", "버블앤티", "새벽커피"],
    "야식": ["족발한상", "밤도깨비곱창", "불닭발포차", "야밤보쌈", "막창골목"],
}
# (메뉴, 단가, 맛 표현 종류, 매운 메뉴인지)
MENUS = {
    "치킨": [("후라이드", 19000, "fried", 0), ("양념치킨", 20000, "sauced", 0), ("반반치킨", 20000, "sauced", 0),
             ("간장치킨", 21000, "sauced", 0), ("순살 후라이드", 21000, "fried", 0), ("매운 양념치킨", 21000, "sauced", 1)],
    "분식": [("떡볶이", 5000, "tteok", 1), ("떡볶이 세트", 13000, "tteok", 1), ("라볶이", 6500, "tteok", 1),
             ("김밥", 3500, "gimbap", 0), ("참치김밥", 4500, "gimbap", 0), ("순대", 5000, "sundae", 0), ("튀김 모둠", 6000, "twigim", 0)],
    "한식": [("제육덮밥", 9000, "rice_meat", 1), ("김치찌개", 8500, "soup", 1), ("된장찌개", 8000, "soup", 0),
             ("불고기 정식", 11000, "rice_meat", 0), ("순두부찌개", 8500, "soup", 1), ("비빔밥", 8000, "rice", 0)],
    "중식": [("짜장면", 7000, "jjajang", 0), ("짬뽕", 8500, "jjamppong", 1), ("볶음밥", 8000, "rice", 0),
             ("탕수육 소", 16000, "tangsu", 0), ("탕수육 대", 25000, "tangsu", 0), ("마라탕", 12000, "mara", 1)],
    "피자": [("페퍼로니 피자", 23000, "pizza", 0), ("포테이토 피자", 26000, "pizza", 0), ("콤비네이션 피자", 24000, "pizza", 0),
             ("불고기 피자", 25000, "pizza", 0), ("고구마 피자", 27000, "pizza", 0), ("치즈 피자 미디엄", 18000, "pizza", 0)],
    "카페디저트": [("아메리카노", 3000, "americano", 0), ("카페라떼", 4000, "latte", 0), ("버블티", 5000, "bubble", 0),
               ("크로플", 5500, "croffle", 0), ("조각케이크", 6500, "cake", 0), ("마카롱 세트", 9000, "cake", 0)],
    "야식": [("족발 중", 32000, "meat", 0), ("보쌈 중", 30000, "meat", 0), ("불닭발", 18000, "grill", 1),
             ("곱창볶음", 22000, "grill", 1), ("막창구이", 24000, "grill", 0)],
}
# 가게마다 주로 파는 메뉴. 여기 없는 가게는 같은 카테고리 메뉴를 고루 판다.
# 값이 0인 메뉴는 그 가게에서 팔지 않는다.
STORE_FOCUS = {
    "후문떡볶이": {"떡볶이": 4, "떡볶이 세트": 4, "라볶이": 2, "튀김 모둠": 1, "순대": 1, "김밥": .5, "참치김밥": 0},
    "매콤떡집": {"떡볶이": 4, "떡볶이 세트": 3, "라볶이": 3, "튀김 모둠": 1, "순대": 1, "김밥": 0, "참치김밥": 0},
    "엄마손김밥": {"김밥": 4, "참치김밥": 4, "떡볶이": 1, "라볶이": 1, "순대": .5, "떡볶이 세트": .5, "튀김 모둠": 0},
    "학교앞튀김": {"튀김 모둠": 4, "떡볶이": 2, "떡볶이 세트": 2, "순대": 1, "김밥": .5, "참치김밥": .5, "라볶이": .5},
    "할매찌개": {"김치찌개": 4, "된장찌개": 3, "순두부찌개": 3, "제육덮밥": .5, "비빔밥": .5, "불고기 정식": 0},
    "뚝배기마을": {"김치찌개": 2, "된장찌개": 2, "순두부찌개": 3, "불고기 정식": 1, "비빔밥": 1, "제육덮밥": 1},
    "한그릇덮밥": {"제육덮밥": 4, "비빔밥": 3, "불고기 정식": 1, "김치찌개": 0, "된장찌개": 0, "순두부찌개": 0},
    "불꽃짬뽕": {"짬뽕": 5, "짜장면": 2, "탕수육 소": 1, "볶음밥": 1, "탕수육 대": .5, "마라탕": 0},
    "청룡각": {"마라탕": 4, "짬뽕": 1, "짜장면": 1, "볶음밥": 1, "탕수육 소": 1, "탕수육 대": .5},
    "크로플공방": {"크로플": 5, "아메리카노": 2, "카페라떼": 2, "조각케이크": .5, "마카롱 세트": 0, "버블티": 0},
    "몽글케이크": {"조각케이크": 5, "마카롱 세트": 3, "아메리카노": 1, "카페라떼": 1, "크로플": 0, "버블티": 0},
    "버블앤티": {"버블티": 6, "카페라떼": 1, "아메리카노": .5, "크로플": .5, "조각케이크": 0, "마카롱 세트": 0},
    "족발한상": {"족발 중": 5, "보쌈 중": 2, "불닭발": 0, "곱창볶음": 0, "막창구이": 0},
    "야밤보쌈": {"보쌈 중": 5, "족발 중": 2, "불닭발": 0, "곱창볶음": 0, "막창구이": 0},
    "밤도깨비곱창": {"곱창볶음": 5, "막창구이": 2, "족발 중": 0, "보쌈 중": 0, "불닭발": 0},
    "불닭발포차": {"불닭발": 5, "곱창볶음": 1, "족발 중": 0, "보쌈 중": 0, "막창구이": 0},
    "막창골목": {"막창구이": 5, "곱창볶음": 2, "족발 중": 0, "보쌈 중": 0, "불닭발": 0},
}
SOUPY_TAGS = {"soup", "jjamppong", "tteok", "mara"}
DRINK_TAGS = {"americano", "latte", "bubble"}
COLD_TAGS = {"americano", "latte", "bubble", "croffle", "cake"}
CRISPY_TAGS = {"fried", "sauced", "tangsu", "twigim"}
NOODLE_MENUS = {"짜장면", "짬뽕", "라볶이", "마라탕"}

# ---------------------------------------------------------------------------
# 주문이 생기는 정도
# ---------------------------------------------------------------------------
DOW = [0.88, 0.88, 0.92, 0.97, 1.20, 1.22, 1.00]  # 월~일
HOUR_W = {10: .5, 11: 2.4, 12: 4.0, 13: 2.4, 14: 1.0, 15: .8, 16: 1.0, 17: 2.4, 18: 6.0, 19: 7.0, 20: 5.4, 21: 3.2,
          22: 4.6, 23: 4.1, 0: 2.0, 1: .8}
AREA_W = {"기숙사": .30, "정문": .18, "후문": .18, "쪽문": .12, "원룸촌": .22}
CAT_W = {"치킨": .20, "분식": .15, "한식": .14, "중식": .11, "피자": .10, "카페디저트": .15, "야식": .15}
NIGHT = {22, 23, 0, 1}
LUNCH = {11, 12, 13}
AFTERNOON = {14, 15, 16, 17}
DINNER = {18, 19, 20}


def hour_weights(dow: int) -> np.ndarray:
    w = []
    for h in HOURS:
        v = HOUR_W[h]
        if dow == 6 and h in LUNCH:
            v *= 1.9  # 일요일 점심
        if dow == 5 and h in LUNCH:
            v *= 1.2
        if dow in (4, 5) and h in DINNER:
            v *= 1.35  # 금·토 저녁
        if dow in (4, 5) and h in NIGHT:
            v *= 1.25
        w.append(v)
    w = np.array(w)
    return w / w.sum()


def area_weights(h: int) -> np.ndarray:
    w = np.array([AREA_W[a] for a in AREAS])
    if h in NIGHT:
        w = w * np.array([2.0, .9, .9, .9, 1.0])  # 야식은 기숙사에서 크게
    if h in LUNCH:
        w = w * np.array([.9, 1.2, 1.2, 1.0, .9])
    return w / w.sum()


def cat_weights(area: str, h: int) -> np.ndarray:
    m = dict(CAT_W)
    if h in LUNCH:
        f = {"치킨": .45, "분식": 1.3, "한식": 2.2, "중식": 1.9, "피자": .7, "카페디저트": .8, "야식": .08}
    elif h in AFTERNOON:
        f = {"치킨": .6, "분식": 1.6, "한식": .8, "중식": .8, "피자": .8, "카페디저트": 3.2, "야식": .2}
    elif h in DINNER:
        f = {"치킨": 1.3, "분식": .9, "한식": 1.1, "중식": 1.1, "피자": 1.4, "카페디저트": .5, "야식": .7}
    elif h == 21:
        f = {"치킨": 1.4, "분식": 1.0, "한식": .6, "중식": .7, "피자": 1.1, "카페디저트": .6, "야식": 1.8}
    elif h in NIGHT:
        f = {"치킨": 1.5, "분식": 1.0, "한식": .25, "중식": .35, "피자": .8, "카페디저트": .6, "야식": 3.2}
    else:  # 10시
        f = {"치킨": .2, "분식": 1.0, "한식": 1.6, "중식": .6, "피자": .3, "카페디저트": 2.5, "야식": .05}
    a = {"기숙사": {"분식": 1.4, "카페디저트": 1.4, "치킨": 1.1, "피자": .55, "야식": .85, "한식": .8},
         "원룸촌": {"피자": 1.7, "야식": 1.4, "한식": 1.2, "분식": .7, "카페디저트": .6},
         "정문": {}, "후문": {}, "쪽문": {}}[area]
    w = np.array([m[c] * f[c] * a.get(c, 1.0) for c in CATS])
    return w / w.sum()


def is_exam(d: dt.date) -> str:
    if MIDTERM[0] <= d <= MIDTERM[1]:
        return "mid"
    if FINAL[0] <= d <= FINAL[1]:
        return "final"
    return ""


# ---------------------------------------------------------------------------
# 1. 깨끗한 주문 만들기(16주 전체)
# ---------------------------------------------------------------------------
def josa(word: str, pair: str) -> str:
    ch = word[-1]
    code = ord(ch) - 0xAC00
    batchim = 0 <= code < 11172 and code % 28 != 0
    a, b = {"이가": ("이", "가"), "은는": ("은", "는"), "을를": ("을", "를"), "이에요": ("이에요", "예요")}[pair]
    return word + (a if batchim else b)


def make_orders(rng: np.random.Generator) -> list[dict]:
    cells = [(h, a, c) for h in HOURS for a in AREAS for c in CATS]
    orders = []
    for k in range(N_WEEKS * 7):
        d = START + dt.timedelta(days=k)
        dow = d.weekday()
        hw = hour_weights(dow)
        p = np.array([hw[i] * area_weights(h)[AREAS.index(a)] * cat_weights(a, h)[CATS.index(c)]
                      for i, h in enumerate(HOURS) for a in AREAS for c in CATS])
        exam = is_exam(d)
        if exam:
            boost = np.array([EXAM_BOOST if c in BOOST_CATS else 1.0 for (_, _, c) in cells])
            scale = (p * boost).sum()
            p = p * boost / scale
        else:
            scale = 1.0
        n = int(round(BASE_DAILY * DOW[dow] * scale * float(np.exp(rng.normal(0, 0.04)))))
        # 카테고리별 건수는 기댓값에 맞춰 나눈다(최대 나머지 방식). 시험 기간 배율이 우연에 흔들리지 않게 하려는 것.
        cat_idx = np.array([CATS.index(c) for (_, _, c) in cells])
        pc = np.array([p[cat_idx == j].sum() for j in range(len(CATS))])
        exp_n = n * pc
        nc = np.floor(exp_n).astype(int)
        rest = n - nc.sum()
        order = np.argsort(-(exp_n - nc) + rng.uniform(0, 1e-9, len(CATS)), kind="stable")
        nc[order[:rest]] += 1
        counts = np.zeros(len(cells), dtype=int)
        for j in range(len(CATS)):
            m = cat_idx == j
            counts[m] = rng.multinomial(nc[j], p[m] / p[m].sum())
        for idx in np.nonzero(counts)[0]:
            h, a, c = cells[idx]
            for _ in range(counts[idx]):
                orders.append({"date": d, "hour": h, "minute": int(rng.integers(0, 60)), "area": a, "category": c,
                               "exam": exam})
    # 시각 순 정렬. 0·1시 주문은 그날 새벽이므로 그날 맨 앞에 온다.
    orders.sort(key=lambda o: (o["date"], o["hour"], o["minute"]))
    return orders


def fill_orders(orders: list[dict], rng: np.random.Generator) -> None:
    store_ids = {}
    sid = 1
    for c in CATS:
        for name in STORES[c]:
            store_ids[name] = f"S{sid:02d}"
            sid += 1
    store_pop = {c: np.array([1 / (i + 1.5) for i in range(len(STORES[c]))]) for c in CATS}
    for c in CATS:
        store_pop[c] = store_pop[c] / store_pop[c].sum()

    # 고객(지역별로 사는 곳이 정해져 있음)
    cust_counts = {"기숙사": 750, "정문": 450, "후문": 450, "쪽문": 300, "원룸촌": 550}
    cust_by_area, cid = {}, 1
    for a in AREAS:
        ids = [f"C{cid + i:04d}" for i in range(cust_counts[a])]
        cid += cust_counts[a]
        w = rng.pareto(1.6, len(ids)) + 0.3
        cust_by_area[a] = (ids, w / w.sum())

    dm_mean = {"기숙사": 22, "정문": 25, "후문": 27, "쪽문": 30, "원룸촌": 42}
    dm_sd = {"기숙사": 5.5, "정문": 6, "후문": 6, "쪽문": 6.5, "원룸촌": 8}
    fee_choices = {"기숙사": ([0, 1000, 1500, 2000], [.35, .3, .2, .15]),
                   "정문": ([1500, 2000, 2500, 3000], [.2, .35, .3, .15]),
                   "후문": ([1500, 2000, 2500, 3000], [.2, .3, .3, .2]),
                   "쪽문": ([2000, 2500, 3000], [.3, .4, .3]),
                   "원룸촌": ([3000, 3500, 4000], [.3, .4, .3])}
    qty_p = {"카페디저트": [.34, .30, .16, .12, .05, .03], "분식": [.45, .35, .15, .05],
             "한식": [.60, .30, .08, .02], "중식": [.62, .28, .08, .02],
             "치킨": [.84, .14, .02], "피자": [.86, .13, .01], "야식": [.88, .11, .01]}

    for o in orders:
        c, a = o["category"], o["area"]
        si = int(rng.choice(len(STORES[c]), p=store_pop[c]))
        o["store_name"] = STORES[c][si]
        o["store_id"] = store_ids[o["store_name"]]
        menus = MENUS[c]
        # 가게마다 잘 팔리는 메뉴가 조금씩 다름
        focus = STORE_FOCUS.get(o["store_name"])
        if focus:
            mw = np.array([float(focus.get(m[0], 1.0)) for m in menus])
        else:
            mw = np.array([1.0 + ((si + j) % 3 == 0) * 1.5 for j in range(len(menus))])
        mi = int(rng.choice(len(menus), p=mw / mw.sum()))
        o["menu"], o["unit_price"], o["tag"], o["spicy"] = menus[mi]
        q = int(rng.choice(len(qty_p[c]), p=qty_p[c])) + 1
        if a == "원룸촌" and rng.random() < .30:
            q = min(q + 1, 6)
        if a == "기숙사" and q > 1 and rng.random() < .25:
            q -= 1  # 기숙사는 혼자 시키는 주문이 많음
        o["quantity"] = q
        fv, fp = fee_choices[a]
        o["delivery_fee"] = int(rng.choice(fv, p=fp))
        o["discount"] = int(rng.choice([0, 1000, 2000, 3000, 5000], p=[.64, .13, .12, .07, .04]))
        sub = q * o["unit_price"]
        if o["discount"] >= sub:
            o["discount"] = 0
        o["payment_method"] = str(rng.choice(["카드", "간편결제", "현금"], p=[.50, .42, .08]))
        ids, w = cust_by_area[a]
        o["customer_id"] = ids[int(rng.choice(len(ids), p=w))]
        busy = 3 if (o["date"].weekday() in (4, 5) and o["hour"] in DINNER) else 0
        late = 3 if o["hour"] in NIGHT else 0
        dmv = rng.normal(dm_mean[a] + busy + late, dm_sd[a])
        o["dm_true"] = int(np.clip(round(dmv), 15, 80))
        pc = .055 if a == "원룸촌" else .036
        r = rng.random()
        o["status"] = "취소" if r < pc else ("환불" if r < pc + .01 else "완료")
        total = sub + o["delivery_fee"] - o["discount"]
        o["total_true"] = -total if o["status"] == "환불" else total


# ---------------------------------------------------------------------------
# 2. 리뷰
# ---------------------------------------------------------------------------
AREA_EFF = {"기숙사": .15, "정문": .05, "후문": 0.0, "쪽문": -.25, "원룸촌": -1.15}
DM_SLOPE = -0.013  # 같은 지역 안에서 배달 시간 1분당 만족도 변화(약함)
AREA_DM_MEAN = {"기숙사": 22, "정문": 25, "후문": 27, "쪽문": 30, "원룸촌": 42}
TOPIC_W = {
    "pos": {"맛": .46, "배달": .14, "양": .15, "포장": .07, "가격": .11, "기타": .07},
    "neg": {"맛": .30, "배달": .28, "양": .13, "포장": .12, "가격": .10, "기타": .07},
    "neu": {"맛": .40, "배달": .10, "양": .16, "포장": .06, "가격": .20, "기타": .08},
}
TOPICS = ["맛", "배달", "양", "포장", "가격", "기타"]


def cond_ok(cond, o) -> bool:
    if not cond:
        return True
    dm = o["dm_true"]
    tag = o["tag"]
    h = o["hour"]
    for c in cond.split():
        ok = {
            "food": tag not in DRINK_TAGS, "drink": tag in DRINK_TAGS, "hot": tag not in COLD_TAGS,
            "soupy": tag in SOUPY_TAGS, "spicy": bool(o["spicy"]), "crispy": tag in CRISPY_TAGS,
            "noodle": o["menu"] in NOODLE_MENUS, "pizza": tag == "pizza",
            "fast": dm <= 26, "vfast": dm <= 19, "slow": dm >= 38, "vslow": dm >= 55,
            "dorm": o["area"] == "기숙사", "oneroom": o["area"] == "원룸촌",
            "disc": o["discount"] > 0, "freefee": o["delivery_fee"] == 0,
            "night": h in NIGHT, "lunch": h in LUNCH, "morning": h == 10, "afternoon": h in AFTERNOON,
            "weekend": o["date"].weekday() >= 5, "exam": bool(o["exam"]),
            "mid": o["exam"] == "mid", "final": o["exam"] == "final",
        }[c]
        if not ok:
            return False
    return True


def fill_text(t: str, o) -> str:
    dm = o["dm_true"]
    mins = "한 시간 가까이" if dm >= 55 else f"{dm // 10 * 10}분 넘게"
    menu = o["menu"]
    for suf in (" 중", " 소", " 대", " 미디엄"):
        if menu.endswith(suf):
            menu = menu[: -len(suf)]  # 리뷰에서는 크기 표시를 빼고 부른다
    return t.format(menu=menu, menu_이=josa(menu, "이가"), menu_은=josa(menu, "은는"),
                    menu_을=josa(menu, "을를"), menu_이에요=josa(menu, "이에요"),
                    store=o["store_name"], store_은=josa(o["store_name"], "은는"), mins=mins)


def pick(rng, items):
    return items[int(rng.integers(0, len(items)))]


def core_sentence(rng, o, sent, topic) -> str | None:
    cands = [t for t, c in rb.TOPIC_BANK[topic][sent] if cond_ok(c, o)]
    if topic == "맛" and sent in ("pos", "neg") and rng.random() < .6:
        cands = rb.TASTE[o["tag"]][sent]
    if not cands:
        return None
    return fill_text(pick(rng, cands), o)


def make_review(rng, o, sent) -> tuple[str, str, str, int]:
    """(리뷰 글, 주제, 덧붙인 주제, 함정 번호) 반환. 함정 아니면 -1."""
    # 함정 리뷰
    # 부정인데 배달은 빨랐던 주문은 "빨리 왔는데 식었다"류가 자연스러워 함정 비율을 높인다
    trap_p = .30 if (sent == "neg" and o["dm_true"] <= 26) else .065
    if rng.random() < trap_p:
        traps = [i for i, tr in enumerate(rb.TRAPS) if tr[1] == sent and cond_ok(tr[3], o)]
        if traps:
            ti = pick(rng, traps)
            if 0 in traps and rng.random() < .5:
                ti = 0  # 4차시 대표 예시("빨리 왔는데 다 식었어요")류를 넉넉히
            text = pick(rng, rb.TRAPS[ti][0])
            ctx = [t for t, c in rb.CONTEXT if cond_ok(c, o)]
            if rng.random() < .40:
                text = fill_text(pick(rng, ctx), o) + " " + text
            if rng.random() < .50:
                text += " " + pick(rng, rb.CLOSING[sent])
            return text, rb.TRAPS[ti][2], "", ti
    # 짧은 한 줄
    if rng.random() < .04:
        return pick(rng, rb.SHORT[sent]) + pick(rng, rb.TAIL[sent]), "맛" if sent != "neu" else "기타", "", -1

    w = dict(TOPIC_W[sent])
    if sent == "neg" and o["dm_true"] >= 38:
        w["배달"] *= 3.5
    if sent == "pos" and o["dm_true"] <= 22:
        w["배달"] *= 1.8
    while True:
        ws = np.array([w[t] for t in TOPICS])
        topic = TOPICS[int(rng.choice(len(TOPICS), p=ws / ws.sum()))]
        core = core_sentence(rng, o, sent, topic)
        if core:
            break
        w[topic] = 0.0
    parts = []
    ctx = [t for t, c in rb.CONTEXT if cond_ok(c, o)]
    exam_ctx = [t for t, c in rb.CONTEXT if c and set(c.split()) & {"exam", "mid", "final"} and cond_ok(c, o)]
    if o["exam"] and exam_ctx and rng.random() < .45:
        parts.append(fill_text(pick(rng, exam_ctx), o))
    elif rng.random() < .38:
        parts.append(fill_text(pick(rng, ctx), o))
    parts.append(core)
    second = ""
    r = rng.random()
    if r < .30:
        # 같은 결의 두 번째 문장(같은 주제나 다른 주제)
        t2 = pick(rng, [t for t in TOPICS if t != "기타"])
        s2 = core_sentence(rng, o, sent, t2)
        if s2 and s2 != core:
            parts.append(s2)
            second = t2 if t2 != topic else ""
    elif r < .48 and sent != "neu":
        # 반대 결의 약한 덧붙임
        other = "neg" if sent == "pos" else "pos"
        opts = [(t2, s) for t2, lst in rb.MILD[other].items() if t2 != topic for s, c in lst if cond_ok(c, o)]
        if opts:
            t2, s = pick(rng, opts)
            joiner = pick(rng, ["", "다만 ", "그래도 "]) if sent == "pos" else pick(rng, ["", "그나마 "])
            parts.append(joiner + s)
            second = t2
    if rng.random() < .45:
        parts.append(pick(rng, rb.CLOSING[sent]))
    text = " ".join(parts)
    tail = pick(rng, rb.TAIL[sent])
    if tail and text.endswith("."):
        text = text[:-1] + tail if tail in ("!!", "~", "...") else text + tail
    elif tail and not text.endswith(("!", "~")):
        text = text + tail
    return text, topic, second, -1


def fill_reviews(orders, rng) -> None:
    # 리뷰를 남기는 주문: 주마다 완료 주문의 26.5%, 환불 주문의 45%(우연에 흔들리지 않게 개수를 정해 뽑음)
    for o in orders:
        o["review"] = None
        o["has_review"] = False
        o["week"] = (o["date"] - START).days // 7
    for wk in range(N_WEEKS):
        for st, share in (("완료", .265), ("환불", .45)):
            grp = [o for o in orders if o["week"] == wk and o["status"] == st]
            k = int(round(share * len(grp)))
            for i in sorted(int(x) for x in rng.choice(len(grp), size=k, replace=False)):
                grp[i]["has_review"] = True
    for o in orders:
        o["s"] = AREA_EFF[o["area"]] + DM_SLOPE * (o["dm_true"] - AREA_DM_MEAN[o["area"]]) + rng.normal(0, 1.0)
    revs = [o for o in orders if o["has_review"] and o["status"] == "완료"]
    s = np.array([o["s"] for o in revs])
    # 환불 리뷰는 모두 부정. 전체 부정 약 30%가 되도록 완료 리뷰의 기준선을 잡는다.
    n_ref = sum(1 for o in orders if o["has_review"] and o["status"] == "환불")
    n_all = len(revs) + n_ref
    q_neg = max((0.30 * n_all - n_ref) / len(revs), 0.0)
    t_neg = np.quantile(s, q_neg)
    t_neu = np.quantile(s, q_neg + 0.10 * n_all / len(revs))
    for o in orders:
        if not o["has_review"]:
            continue
        if o["status"] == "환불" or o["s"] < t_neg:
            sent = "neg"
        elif o["s"] < t_neu:
            sent = "neu"
        else:
            sent = "pos"
        o["sentiment"] = sent
    # 평점: 감성 안에서 만족도 순서대로
    for sent in ("pos", "neu", "neg"):
        grp = [o for o in orders if o["has_review"] and o["sentiment"] == sent]
        ss = np.array([o["s"] for o in grp])
        med = np.median(ss)
        for o in grp:
            u = rng.random()
            if sent == "pos":
                o["rating"] = 5 if (o["s"] >= med) ^ (u < .12) else 4
            elif sent == "neu":
                o["rating"] = 3 if u < .74 else (4 if u < .88 else 2)
            else:
                o["rating"] = 1 if (o["s"] < med) ^ (u < .12) else 2
                if u > .93:
                    o["rating"] = 3
    for o in orders:
        if o["has_review"]:
            text, topic, second, trap = make_review(rng, o, o["sentiment"])
            o["review"], o["topic"], o["topic2"], o["trap"] = text, topic, second, trap
    # 강의에서 그대로 인용하는 두 문장이 기본 파일(1~12주)에 꼭 있게 한다
    base = [o for o in orders if o["has_review"] and o["week"] < 12]
    for ti in (0, 1):
        texts, sent, topic, cond = rb.TRAPS[ti]
        if any(texts[0] in o["review"] for o in base):
            continue
        cands = [o for o in base if o["sentiment"] == sent and o["trap"] == ti] or                 [o for o in base if o["sentiment"] == sent and o["trap"] < 0 and cond_ok(cond, o)]
        o = cands[0]
        o["review"], o["topic"], o["topic2"], o["trap"] = texts[0], topic, "", ti


# ---------------------------------------------------------------------------
# 3. 파일로 나누고 지저분하게 만들기
# ---------------------------------------------------------------------------
CAT_VAR = {"치킨": ["치킨 ", "chicken"], "분식": ["분식 "], "한식": ["한식 "], "중식": ["중식 "],
           "피자": ["피자 ", "pizza"], "카페디저트": ["카페/디저트", "카페 디저트"], "야식": ["야식 "]}
PAY_VAR = {"카드": ["신용카드", "card"], "간편결제": ["간편 결제"], "현금": []}
AREA_VAR = {"정문": ["정문앞", "정문 앞"], "후문": ["후문 앞"], "원룸촌": ["원룸"], "기숙사": [], "쪽문": []}

FILE_CFG = {
    # 파일: (완전 중복, 금액만 다른 중복, 배달시간 기록 누락 비율, 지역 빈칸 비율, 금액 글자 비율,
    #        category·결제·지역 표기 흔들림 비율, 999분, 0분, 수량 0, 계산 불일치 비율)
    "w01-12": dict(dup=90, conflict=8, dm_miss=.02, area_miss=.01, amt_str=.03, cat_var=.04, pay_var=.04, area_var=.03,
                   dm999=4, dm0=2, qty0=2, mismatch=.01),
    "w13": dict(dup=3, conflict=1, dm_miss=.012, area_miss=.008, amt_str=.02, cat_var=.02, pay_var=.02, area_var=.02,
                dm999=1, dm0=0, qty0=0, mismatch=.01),
    "w14": dict(dup=3, conflict=1, dm_miss=.012, area_miss=.008, amt_str=.02, cat_var=.02, pay_var=.02, area_var=.02,
                dm999=0, dm0=1, qty0=0, mismatch=.01),
    "w15": dict(dup=3, conflict=1, dm_miss=.012, area_miss=.008, amt_str=.02, cat_var=.02, pay_var=.02, area_var=.02,
                dm999=1, dm0=0, qty0=1, mismatch=.01),
    "w16": dict(dup=4, conflict=1, dm_miss=.012, area_miss=.008, amt_str=.02, cat_var=.02, pay_var=.02, area_var=.02,
                dm999=1, dm0=0, qty0=0, mismatch=.01),
}
W13_OVERLAP = 7
W14_TTEOK = 9
W14_PAY = 7


def fmt_dt(o, style: int) -> str:
    d, h, m = o["date"], o["hour"], o["minute"]
    if style == 0:
        return f"{d.year}-{d.month:02d}-{d.day:02d} {h:02d}:{m:02d}"
    if style == 1:
        return f"{d.year}.{d.month}.{d.day} {h:02d}:{m:02d}"
    h12 = h % 12 or 12
    return f"{d.month:02d}/{d.day:02d}/{d.year} {h12}:{m:02d} {'AM' if h < 12 else 'PM'}"


def file_of(o) -> str:
    w = (o["date"] - START).days // 7 + 1
    return "w01-12" if w <= 12 else f"w{w}"


def choose(rng, pool: list[int], k: int, used: set) -> list[int]:
    cand = [i for i in pool if i not in used]
    k = min(k, len(cand))
    sel = sorted(int(x) for x in rng.choice(cand, size=k, replace=False)) if k else []
    used.update(sel)
    return sel


def mess_file(name: str, rows: list[dict], rng, base_rows_last_day: list[dict] | None):
    cfg = FILE_CFG[name]
    n = len(rows)
    for o in rows:
        o["issues"] = []
        o["out"] = {
            "order_id": o["order_id"], "order_datetime": None, "store_id": o["store_id"], "store_name": o["store_name"],
            "category": o["category"], "menu": o["menu"], "quantity": str(o["quantity"]), "unit_price": str(o["unit_price"]),
            "delivery_fee": str(o["delivery_fee"]), "discount": str(o["discount"]), "total_amount": str(o["total_true"]),
            "payment_method": o["payment_method"], "delivery_area": o["area"], "customer_id": o["customer_id"],
            "delivery_minutes": "" if o["status"] == "취소" else str(o["dm_true"]), "status": o["status"],
            "rating": str(o["rating"]) if o["has_review"] else "", "review_text": o["review"] or "",
        }
    idx_all = list(range(n))
    done = [i for i in idx_all if rows[i]["status"] == "완료"]
    delivered = [i for i in idx_all if rows[i]["status"] != "취소"]
    major: set = set()

    # 서로 겹치지 않는 큰 문제들
    conflict = choose(rng, done, cfg["conflict"], major)
    mismatch = choose(rng, done, int(round(cfg["mismatch"] * n)), major)
    qty0 = choose(rng, done, cfg["qty0"], major)
    dm999 = choose(rng, delivered, cfg["dm999"], major)
    dm0 = choose(rng, delivered, cfg["dm0"], major)
    dmmiss = choose(rng, delivered, int(round(cfg["dm_miss"] * len(delivered))), major)
    amt_pool = [i for i in done]
    if name == "w01-12":
        # 강의 예시 "12,500원"이 기본 파일에 실제로 있게
        e = [i for i in amt_pool if rows[i]["total_true"] == 12500 and i not in major]
        forced = [e[0]] if e else []
        major.update(forced)
    else:
        forced = []
    amtstr = forced + choose(rng, amt_pool, int(round(cfg["amt_str"] * n)) - len(forced), major)
    for i in conflict:
        rows[i]["issues"].append("conflict_keep")
    for i in mismatch:
        o = rows[i]
        typ = int(rng.integers(0, 3))
        t = o["total_true"]
        if typ == 0 and o["delivery_fee"] > 0:
            bad = t - o["delivery_fee"]
        elif typ == 1 and o["discount"] > 0:
            bad = t + o["discount"]
        else:
            bad = t + int(rng.choice([-1000, 1000, -500, 500, 2000]))
        o["out"]["total_amount"] = str(bad)
        o["issues"].append("mismatch")
    for i in qty0:
        rows[i]["out"]["quantity"] = "0"
        rows[i]["issues"].append("qty0")
    for i in dm999:
        rows[i]["out"]["delivery_minutes"] = "999"
        rows[i]["issues"].append("dm999")
    for i in dm0:
        rows[i]["out"]["delivery_minutes"] = "0"
        rows[i]["issues"].append("dm0")
    for i in dmmiss:
        rows[i]["out"]["delivery_minutes"] = ""
        rows[i]["issues"].append("dm_missing")
    for i in amtstr:
        rows[i]["out"]["total_amount"] = f"{rows[i]['total_true']:,}원"
        rows[i]["issues"].append("amount_str")

    # 겉모양 문제(겹쳐도 됨)
    for i in sorted(int(x) for x in rng.choice(idx_all, size=int(round(cfg["area_miss"] * n)), replace=False)):
        rows[i]["out"]["delivery_area"] = ""
        rows[i]["issues"].append("area_missing")
    for key, var, rate, tag in (("category", CAT_VAR, cfg["cat_var"], "cat_var"),
                                ("payment_method", PAY_VAR, cfg["pay_var"], "pay_var"),
                                ("delivery_area", AREA_VAR, cfg["area_var"], "area_var")):
        pool = [i for i in idx_all if rows[i]["out"][key] and var[rows[i]["out"][key]]]
        k = int(round(rate * n))
        for i in sorted(int(x) for x in rng.choice(pool, size=min(k, len(pool)), replace=False)):
            rows[i]["out"][key] = pick(rng, var[rows[i]["out"][key]])
            rows[i]["issues"].append(tag)
    styles = rng.choice([0, 1, 2], size=n, p=[.85, .10, .05])
    for o, st in zip(rows, styles):
        o["out"]["order_datetime"] = fmt_dt(o, int(st))
        if st:
            o["issues"].append(f"date_fmt{int(st)}")

    # 14주차: 처음 보는 표기
    if name == "w14":
        pool = [i for i in done if rows[i]["category"] == "분식" and rows[i]["tag"] == "tteok"
                and rows[i]["out"]["category"] == "분식"]
        for i in sorted(int(x) for x in rng.choice(pool, size=W14_TTEOK, replace=False)):
            rows[i]["out"]["category"] = "떡볶이"
            rows[i]["issues"].append("new_cat")
        pool = [i for i in idx_all if rows[i]["out"]["payment_method"] == "간편결제"]
        for i in sorted(int(x) for x in rng.choice(pool, size=W14_PAY, replace=False)):
            rows[i]["out"]["payment_method"] = "페이"
            rows[i]["issues"].append("new_pay")

    lines = [(o["out"], o) for o in rows]
    # 같은 order_id에 금액만 다른 행
    extra = []
    for i in conflict:
        o = rows[i]
        bad = dict(o["out"])
        bad["total_amount"] = str(o["total_true"] + int(rng.choice([1000, -1000, 2000, -500, 3000])))
        extra.append((bad, {"order_id": o["order_id"], "issues": ["conflict_drop"], "copy": True}))
    # 완전 중복(큰 문제가 없는 행에서)
    pool = [i for i in idx_all if i not in major]
    for i in sorted(int(x) for x in rng.choice(pool, size=cfg["dup"], replace=False)):
        extra.append((dict(rows[i]["out"]), {"order_id": rows[i]["order_id"], "issues": ["dup_copy"], "copy": True}))
        rows[i]["issues"].append("dup_source")
    # 섞어 넣기: 원래 행 뒤 어딘가(1~40행 뒤)에 넣는다
    for out, meta in extra:
        src = next(k for k, (_, m) in enumerate(lines) if m["order_id"] == meta["order_id"])
        pos = min(len(lines), src + 1 + int(rng.integers(0, 40)))
        lines.insert(pos, (out, meta))
    # 13주차: 기본 파일 마지막 날 주문이 다시 들어옴(맨 앞)
    if name == "w13" and base_rows_last_day:
        tail = base_rows_last_day[-W13_OVERLAP:]
        lines = [(dict(o["out"]), {"order_id": o["order_id"], "issues": ["overlap_w12"], "copy": True}) for o in tail] + lines
    return lines


def main() -> None:
    rng = np.random.default_rng(SEED)
    orders = make_orders(rng)
    fill_orders(orders, rng)
    fill_reviews(orders, rng)
    for k, o in enumerate(orders, start=1):
        o["order_id"] = f"O{k:06d}"

    files = {}
    for o in orders:
        files.setdefault(file_of(o), []).append(o)
    DATA.mkdir(parents=True, exist_ok=True)
    key_rows = []
    last_day = None
    for name in ["w01-12", "w13", "w14", "w15", "w16"]:
        rows = files[name]
        lines = mess_file(name, rows, rng, last_day)
        if name == "w01-12":
            last_day = [o for o in rows if o["date"] == START + dt.timedelta(days=83)
                        and not set(o["issues"]) & {"conflict_keep", "dup_source", "mismatch", "qty0", "dm999", "dm0",
                                                      "amount_str", "dm_missing"}]
        path = DATA / f"orders_2025_{name}.csv"
        with open(path, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f, lineterminator="\r\n")
            w.writerow(COLUMNS)
            for out, meta in lines:
                w.writerow([out[c] for c in COLUMNS])
        for r, (out, meta) in enumerate(lines):
            src = meta if meta.get("copy") else None
            o = None if src else meta
            key_rows.append({
                "file": path.name, "index": r, "excel_row": r + 2, "order_id": out["order_id"],
                "is_copy": int(bool(src)), "issues": ";".join(meta["issues"]),
                "sentiment": "" if src or not o["has_review"] else {"pos": "긍정", "neg": "부정", "neu": "중립"}[o["sentiment"]],
                "topic": "" if src or not o["has_review"] else o["topic"],
                "topic2": "" if src or not o["has_review"] else o["topic2"],
                "trap": "" if src or not o["has_review"] or o["trap"] < 0 else o["trap"] + 1,
                "dm_true": "" if src or o["status"] == "취소" else o["dm_true"],
                "total_true": "" if src else o["total_true"], "exam": "" if src else o["exam"],
            })
        print(f"{path.name}: {len(lines)}행")
    with open(TOOLS / "answer_key.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(key_rows[0]), lineterminator="\r\n")
        w.writeheader()
        w.writerows(key_rows)
    print(f"answer_key.csv: {len(key_rows)}행")


if __name__ == "__main__":
    main()
