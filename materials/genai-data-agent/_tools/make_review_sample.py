"""4차시 실습용 리뷰 표본 200개를 만든다.

실행:
    _tools/.venv/Scripts/python.exe _tools/make_review_sample.py

- 정제 규칙은 check_data.py의 clean()을 그대로 가져다 쓴다(기본 파일, 14주차 새 규칙 없이).
- 정제 뒤 리뷰 1,127개에서 감성 비율(긍정 120 · 부정 60 · 중립 20)을 맞춰 200개를 고른다.
  주제 순위가 전체 리뷰와 같고(맛 > 배달 > 양 > 가격 > 기타 > 포장) 주제 개수에 동률이 없는 시드를 찾는다.
- 1~20번(검수용)은 정해진 구성으로 골라 앞에 두고, 나머지는 섞는다. 1~20번은 무작위가 아니라 강의용으로 고른 것이다.
  구성: "빨리 왔는데 식었다"류 2 · 그 밖의 키워드 함정(긍정) 1 · 함정(중립, 리뷰에 '맛'이 들어간 것) 1 ·
  반대 말을 덧붙인 리뷰(긍정 2 · 부정 1) · 주제가 둘인 같은 결 리뷰 3 · 짧은 한마디 부정 1 · 나머지 일반 리뷰
- 결과:
    data/reviews_sample_200.csv           배포용(sample_no, order_id, category, menu, review_text)
    _tools/reviews_sample_200_answer.csv  강사용 정답(감성·주제·덧붙인 주제·함정 번호)
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")
TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import review_bank as rb  # noqa: E402

# check_data.py의 읽기·정제 부분만 실행(검사·data_facts 쓰기는 하지 않음)
_src = (TOOLS / "check_data.py").read_text(encoding="utf-8").splitlines()
_end = next(i for i, l in enumerate(_src) if l.startswith("cl, info = {}, {}"))
_g = {"__file__": str(TOOLS / "check_data.py"), "__name__": "check_data_part"}
exec(compile("\n".join(_src[:_end]), "check_data.py", "exec"), _g)

D, _ = _g["clean"](_g["raw"]["w01-12"], new_rules=False)
k = _g["kf"]["w01-12"].set_index("index")[["sentiment", "topic", "topic2", "trap"]]
D = D.join(k)
R = D[D.review_text != ""].copy()

OPP = {"긍정": "neg", "부정": "pos"}
MILD_TEXT = {s: [t for lst in rb.MILD[o].values() for t, _ in lst] for s, o in OPP.items()}
R["mixed"] = [r.sentiment in OPP and any(t in r.review_text for t in MILD_TEXT[r.sentiment]) for r in R.itertuples()]
R["istrap"] = R.trap != ""
R["short"] = R.review_text.str.len() <= 6
POP_ORDER = R.topic.value_counts().index.tolist()  # 맛, 배달, 양, 가격, 기타, 포장
TARGET = {"긍정": 120, "부정": 60, "중립": 20}

S = None
for seed in range(1, 20000):
    rng = np.random.default_rng(seed)
    parts = [R[R.sentiment == s].loc[lambda g: rng.choice(g.index, n, replace=False)] for s, n in TARGET.items()]
    cand = pd.concat(parts)
    tc = cand.topic.value_counts()
    if tc.index.tolist() != POP_ORDER or tc.duplicated().any():
        continue
    if not (14 <= cand.istrap.sum() <= 20 and (cand.trap == "1").sum() >= 3):
        continue
    if not ((cand.trap == "7").sum() >= 1 and ((cand.trap == "7") & cand.review_text.str.contains("맛")).sum() >= 1):
        continue
    if not ((cand.short & (cand.sentiment == "부정")).sum() >= 1):
        continue
    S, SEED = cand, seed
    break
assert S is not None

rng = np.random.default_rng(404)
pick: list = []


def take(mask, n):
    c = [i for i in S.index[mask] if i not in pick]
    pick.extend(rng.choice(c, n, replace=False).tolist())


plain = ~S.istrap & ~S.mixed & ~S.short
take(S.trap == "1", 2)
take(S.istrap & (S.trap != "1") & (S.sentiment == "긍정"), 1)
take((S.trap == "7") & S.review_text.str.contains("맛"), 1)
take(S.mixed & (S.sentiment == "긍정"), 2)
take(S.mixed & (S.sentiment == "부정"), 1)
take(plain & (S.topic2 != ""), 3)
take(S.short & (S.sentiment == "부정"), 1)
take(plain & (S.topic2 == "") & (S.sentiment == "부정"), 2)
take(plain & (S.topic2 == "") & (S.sentiment == "중립"), 1)
take(plain & (S.topic2 == "") & (S.sentiment == "긍정"), 20 - len(pick))
first = S.loc[pick]
first = first.loc[rng.permutation(first.index)]
rest = S.drop(pick)
rest = rest.loc[rng.permutation(rest.index)]
P = pd.concat([first, rest]).reset_index(drop=True)
P.insert(0, "sample_no", np.arange(1, len(P) + 1))

P[["sample_no", "order_id", "category", "menu", "review_text"]].to_csv(
    TOOLS.parent / "data" / "reviews_sample_200.csv", index=False, encoding="utf-8-sig")
P[["sample_no", "order_id", "sentiment", "topic", "topic2", "trap", "review_text"]].rename(
    columns={"topic2": "second_topic"}).to_csv(TOOLS / "reviews_sample_200_answer.csv", index=False, encoding="utf-8-sig")

print("seed", SEED)
print("감성", P.sentiment.value_counts().to_dict())
print("주제", P.topic.value_counts().to_dict())
print("함정", int(P.istrap.sum()), "반대 덧붙임", int(P.mixed.sum()), "주제 둘", int((P.topic2 != "").sum()))
print(pd.crosstab(P.topic, P.sentiment, margins=True).to_string())
pd.set_option("display.width", 250)
pd.set_option("display.max_colwidth", 120)
print(P.head(20)[["sample_no", "order_id", "sentiment", "topic", "topic2", "trap", "mixed", "review_text"]].to_string())
m = P.review_text.str.contains("빨리|빨랐|빠른|빠르")
print(P[m][["sample_no", "sentiment", "topic", "trap", "review_text"]].to_string())
