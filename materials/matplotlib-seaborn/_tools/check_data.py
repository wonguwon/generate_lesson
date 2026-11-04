"""make_data.py가 만든 CSV에 의도한 특징이 들어 있는지 검증하고 data_facts.md를 쓴다.

실행:
    _tools/.venv/Scripts/python.exe _tools/check_data.py

검증에 실패하면 AssertionError로 멈춘다. 모두 통과하면 data_facts.md를 새로 쓴다.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

TOOLS = Path(__file__).resolve().parent
DATA = TOOLS.parent / "data"
OUT = TOOLS / "data_facts.md"

MIN_GAP = 0.03  # 1·2위(또는 최하위·차하위) 사이 최소 상대 차이

s = pd.read_csv(DATA / "students.csv")
c = pd.read_csv(DATA / "cafe_sales.csv", parse_dates=["date"])

checks: list[tuple[str, str, bool]] = []  # (항목, 결과, 통과)


def check(name: str, ok: bool, detail: str) -> None:
    checks.append((name, detail, bool(ok)))


def gap_check(name: str, ser: pd.Series) -> None:
    v = ser.sort_values(ascending=False)
    top = (v.iloc[0] - v.iloc[1]) / abs(v.iloc[0])
    bot = (v.iloc[-2] - v.iloc[-1]) / abs(v.iloc[-2])
    detail = (f"최대 {v.index[0]}({v.iloc[0]:,.2f}) vs 2위 {v.index[1]}({v.iloc[1]:,.2f}) 차이 {top:.1%} / "
              f"최소 {v.index[-1]}({v.iloc[-1]:,.2f}) vs 차하위 {v.index[-2]}({v.iloc[-2]:,.2f}) 차이 {bot:.1%}")
    check(f"순위 차이: {name}", top >= MIN_GAP and bot >= MIN_GAP, detail)


def fmt(x) -> str:
    if isinstance(x, (float, np.floating)):
        if np.isnan(x):
            return "NaN"
        return f"{x:,.2f}"
    if isinstance(x, (int, np.integer)):
        return f"{x:,}"
    return str(x)


def md_table(df: pd.DataFrame, index: bool = True) -> str:
    d = df.reset_index() if index else df
    cols = [str(col) for col in d.columns]
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
    for row in d.itertuples(index=False):
        lines.append("| " + " | ".join(fmt(x) for x in row) + " |")
    return "\n".join(lines)


def col_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in df.columns:
        ser = df[col]
        if pd.api.types.is_numeric_dtype(ser):
            rng = f"{fmt(ser.min())} ~ {fmt(ser.max())}"
            mean = fmt(ser.mean())
        elif pd.api.types.is_datetime64_any_dtype(ser):
            rng = f"{ser.min():%Y-%m-%d} ~ {ser.max():%Y-%m-%d}"
            mean = "-"
        else:
            vals = ser.unique()
            rng = " · ".join(map(str, vals)) if len(vals) <= 12 else f"{ser.min()} ~ {ser.max()} ({len(vals)}개)"
            mean = "-"
        rows.append({"열": col, "pandas 자료형": str(ser.dtype), "결측": int(ser.isna().sum()),
                     "범위·값": rng, "평균": mean})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# students.csv 검증
# ---------------------------------------------------------------------------
check("students 행·열", s.shape == (300, 12), f"{s.shape}")
mc = s["major"].value_counts()
check("전공 인원", mc.to_dict() == {"공학": 80, "사회과학": 70, "인문": 55, "자연과학": 55, "예체능": 40},
      ", ".join(f"{k} {v}" for k, v in mc.items()))

na = s.isna().sum()
check("결측치", na["sleep_hours"] == 15 and na["sns_minutes"] == 6 and na.drop(["sleep_hours", "sns_minutes"]).sum() == 0,
      f"sleep_hours {na['sleep_hours']}, sns_minutes {na['sns_minutes']}, 나머지 0")
check("이상치 sns 900 한 명", (s["sns_minutes"] == 900).sum() == 1 and s.loc[s["sns_minutes"] != 900, "sns_minutes"].max() <= 480,
      f"900 {int((s['sns_minutes'] == 900).sum())}명, 그다음 최댓값 {s.loc[s['sns_minutes'] != 900, 'sns_minutes'].max():.0f}")
cm_out = s[s["commute_minutes"] == 180]
check("이상치 commute 180 한 명", len(cm_out) == 1 and s.loc[s["commute_minutes"] != 180, "commute_minutes"].max() <= 120,
      f"180 {len(cm_out)}명, 그다음 최댓값 {s.loc[s['commute_minutes'] != 180, 'commute_minutes'].max()}")

ranges_ok = (s["grade"].between(1, 4).all() and s["study_hours"].between(0, 40).all()
             and s["sleep_hours"].dropna().between(4, 9.5).all() and s["part_time_hours"].between(0, 25).all()
             and s["coffee_cups"].between(0, 20).all() and s["exam_score"].between(0, 100).all()
             and s["gpa"].between(0, 4.5).all())
check("값 범위(학년·공부·수면·알바·커피·점수·평점)", ranges_ok, "모두 명세 범위 안")
for h, (lo, hi) in {"기숙사": (5, 15), "자취": (5, 30), "통학": (30, 120)}.items():
    v = s.loc[(s["housing"] == h) & (s["commute_minutes"] != 180), "commute_minutes"]
    check(f"통학 시간 범위 {h}", v.between(lo, hi).all(), f"{v.min()}~{v.max()}분")
zero_pt = (s["part_time_hours"] == 0).mean()
check("아르바이트 0시간 비율 약 40%", 0.35 <= zero_pt <= 0.45, f"{zero_pt:.1%}")
check("수면 평균 약 6.6", abs(s["sleep_hours"].mean() - 6.6) < 0.15, f"{s['sleep_hours'].mean():.2f}")
check("SNS 평균 약 150(이상치 포함)", abs(s["sns_minutes"].mean() - 150) < 15, f"{s['sns_minutes'].mean():.2f}")

CORR_PAIRS = [("study_hours", "exam_score", 0.6), ("exam_score", "gpa", 0.7),
              ("sns_minutes", "sleep_hours", -0.4), ("part_time_hours", "study_hours", -0.3),
              ("coffee_cups", "sleep_hours", -0.2)]
corr_rows = []
for a, b, target in CORR_PAIRS:
    r = s[a].corr(s[b])
    tol = 0.1 if a != "coffee_cups" else 0.15
    check(f"상관 {a}-{b} (목표 {target})", abs(r - target) <= tol, f"r = {r:.2f}")
    corr_rows.append({"변수 쌍": f"{a} ↔ {b}", "의도": f"약 {target}", "r (pandas .corr, 결측 제외)": round(r, 2)})
t = s[s["sns_minutes"] != 900]
r_no = t["sns_minutes"].corr(t["sleep_hours"])
corr_rows.append({"변수 쌍": "sns_minutes ↔ sleep_hours (900분 이상치 뺀 경우)", "의도": "-", "r (pandas .corr, 결측 제외)": round(r_no, 2)})

skew = s[["sleep_hours", "study_hours", "sns_minutes", "exam_score"]].skew()
check("분포 모양(왜도)", skew["study_hours"] > 0.5 and skew["sns_minutes"] > 0.5 and abs(skew["sleep_hours"]) < 0.3 and skew["exam_score"] < -0.2,
      ", ".join(f"{k} {v:.2f}" for k, v in skew.items()))

by_major = s.groupby("major")[["study_hours", "exam_score", "gpa", "sleep_hours", "sns_minutes", "coffee_cups"]].mean()
by_major.insert(0, "학생 수", s["major"].value_counts())
by_major = by_major.sort_values("study_hours", ascending=False)
gap_check("전공별 평균 study_hours", by_major["study_hours"])
gap_check("전공별 평균 exam_score", by_major["exam_score"])
ordered = list(by_major.index)
check("공부 시간: 공학·자연과학 높고 인문·예체능 낮음", set(ordered[:2]) == {"공학", "자연과학"} and set(ordered[-2:]) == {"인문", "예체능"},
      " > ".join(ordered))

slopes = {m: np.polyfit(g["study_hours"], g["exam_score"], 1)[0] for m, g in s.groupby("major")}
others = max(v for k, v in slopes.items() if k != "공학")
check("공학 기울기가 가장 가파름", slopes["공학"] > others * 1.15,
      ", ".join(f"{k} {v:.2f}" for k, v in sorted(slopes.items(), key=lambda kv: -kv[1])))

by_housing = s.groupby("housing")[["commute_minutes", "part_time_hours", "study_hours", "sleep_hours"]].mean()
by_housing.insert(0, "학생 수", s["housing"].value_counts())
by_housing.insert(3, "아르바이트 하는 비율(%)", s.groupby("housing")["part_time_hours"].apply(lambda x: (x > 0).mean() * 100))
by_housing = by_housing.sort_values("commute_minutes", ascending=False)
gap_check("주거별 평균 commute_minutes", by_housing["commute_minutes"])
gap_check("주거별 평균 part_time_hours", by_housing["part_time_hours"])
gap_check("주거별 학생 수", by_housing["학생 수"].astype(float))
cmh = by_housing["commute_minutes"]
check("통학 ≫ 자취 > 기숙사", cmh["통학"] > 3 * cmh["자취"] and cmh["자취"] > cmh["기숙사"],
      f"통학 {cmh['통학']:.2f}, 자취 {cmh['자취']:.2f}, 기숙사 {cmh['기숙사']:.2f}")
check("아르바이트 자취 최고", by_housing["part_time_hours"].idxmax() == "자취", f"{by_housing['part_time_hours'].round(2).to_dict()}")

by_grade = s.groupby("grade")[["study_hours", "exam_score", "gpa", "part_time_hours"]].mean()
by_grade.insert(0, "학생 수", s["grade"].value_counts().sort_index())
major_housing = pd.crosstab(s["major"], s["housing"], margins=True, margins_name="합계")

# ---------------------------------------------------------------------------
# cafe_sales.csv 검증
# ---------------------------------------------------------------------------
MENU = ["americano", "latte", "ade", "tea"]
PRICE = {"americano": 2500, "latte": 3500, "ade": 4000, "tea": 3000}
WD = ["월", "화", "수", "목", "금", "토", "일"]
PERIODS = ["1학기", "여름방학", "2학기", "겨울방학"]

check("cafe 행·열", c.shape == (365, 14), f"{c.shape}")
check("기간 2025-03-01~2026-02-28 하루 1행",
      c["date"].min() == pd.Timestamp("2025-03-01") and c["date"].max() == pd.Timestamp("2026-02-28") and c["date"].is_unique,
      f"{c['date'].min():%Y-%m-%d} ~ {c['date'].max():%Y-%m-%d}")
check("cafe 결측 없음", c.isna().sum().sum() == 0, f"{int(c.isna().sum().sum())}개")
check("sales = 잔 수 × 가격 합", (c["sales"] == sum(c[m] * p for m, p in PRICE.items())).all(), "365행 모두 일치")

closed = c[c["customers"] == 0]
closed_expected = ["2025-10-05", "2025-10-06", "2025-10-07", "2025-10-08", "2026-02-16", "2026-02-17", "2026-02-18"]
check("휴무일(모든 판매 0)", list(closed["date"].dt.strftime("%Y-%m-%d")) == closed_expected
      and (closed[MENU + ["sales"]] == 0).all().all(), ", ".join(closed_expected))
check("시험 주간 4주(28일)", c["exam_week"].sum() == 28, f"{int(c['exam_week'].sum())}일")
check("비 온 날 약 25%", 0.22 <= c["rain"].mean() <= 0.28, f"{c['rain'].mean():.1%}")

op = c[c["customers"] > 0]
sem = op[op["period"].isin(["1학기", "2학기"])]
exam_ratio = sem.loc[sem["exam_week"] == 1, "customers"].mean() / sem.loc[sem["exam_week"] == 0, "customers"].mean()
check("시험 주간 손님 약 1.3배(학기 중 영업일 기준)", 1.2 <= exam_ratio <= 1.4, f"{exam_ratio:.2f}배")
rain_all = c.groupby("rain")["customers"].mean()
rain_ratio = rain_all[1] / rain_all[0]
check("비 오는 날 손님 약 -10%(전체 365일 단순 평균)", 0.86 <= rain_ratio <= 0.94, f"{rain_ratio - 1:+.1%}")

sem_wd = op[op["period"].isin(["1학기", "2학기"]) & (op["exam_week"] == 0)]
sem_weekday = sem_wd[~sem_wd["weekday"].isin(["토", "일"])]["customers"].mean()
sem_weekend = sem_wd[sem_wd["weekday"].isin(["토", "일"])]["customers"].mean()
vac_weekday = op[op["period"].isin(["여름방학", "겨울방학"]) & ~op["weekday"].isin(["토", "일"])]["customers"].mean()
check("학기 평일 약 420 / 주말 약 150 / 방학 평일 약 180",
      380 <= sem_weekday <= 460 and 120 <= sem_weekend <= 180 and 150 <= vac_weekday <= 210,
      f"학기 평일 {sem_weekday:.1f}, 학기 주말 {sem_weekend:.1f}, 방학 평일 {vac_weekday:.1f} (시험 주간·휴무일 제외)")

temp_corr = op[["avg_temp"] + MENU + ["customers"]].corr()["avg_temp"].drop("avg_temp")
check("기온: 에이드↑ 라떼·차↓ 아메리카노 무관",
      temp_corr["ade"] > 0.4 and temp_corr["latte"] < -0.25 and temp_corr["tea"] < -0.4 and abs(temp_corr["americano"]) < 0.15,
      ", ".join(f"{k} {v:.2f}" for k, v in temp_corr.items()))
sem_temp_corr = sem[["avg_temp"] + MENU + ["customers"]].corr()["avg_temp"].drop("avg_temp")
check("기온 범위 약 -8~30", -10 <= c["avg_temp"].min() <= -6.5 and 28 <= c["avg_temp"].max() <= 32,
      f"{c['avg_temp'].min()} ~ {c['avg_temp'].max()}")

by_month = c.groupby("year_month").agg(
    영업일=("customers", lambda x: int((x > 0).sum())),
    손님_합계=("customers", "sum"), 손님_평균=("customers", "mean"),
    매출_합계=("sales", "sum"), 매출_평균=("sales", "mean"),
    평균기온=("avg_temp", "mean"),
    americano=("americano", "sum"), latte=("latte", "sum"), ade=("ade", "sum"), tea=("tea", "sum"),
)
gap_check("월별 매출 합계", by_month["매출_합계"].astype(float))
gap_check("월별 손님 평균", by_month["손님_평균"])
gap_check("월별 손님 합계", by_month["손님_합계"].astype(float))
for m in MENU:
    gap_check(f"월별 {m} 합계", by_month[m].astype(float))

by_wd = c.groupby("weekday").agg(손님_평균=("customers", "mean"), 매출_평균=("sales", "mean")).reindex(WD)
by_wd["손님_평균(휴무일 제외)"] = op.groupby("weekday")["customers"].mean().reindex(WD)
by_wd["휴무일 수"] = (c["customers"] == 0).groupby(c["weekday"]).sum().reindex(WD).astype(int)
gap_check("요일별 손님 평균(전체)", by_wd["손님_평균"])
gap_check("요일별 손님 평균(휴무일 제외)", by_wd["손님_평균(휴무일 제외)"])
gap_check("요일별 매출 평균", by_wd["매출_평균"])

by_period = c.groupby("period").agg(일수=("date", "size"), 손님_평균=("customers", "mean"),
                                    매출_평균=("sales", "mean"), 매출_합계=("sales", "sum"),
                                    평균기온=("avg_temp", "mean")).reindex(PERIODS)
gap_check("period별 손님 평균", by_period["손님_평균"])
gap_check("period별 매출 평균", by_period["매출_평균"])
check("학기 중 높고 방학 낮음", by_period.loc[["1학기", "2학기"], "손님_평균"].min() > 2 * by_period.loc[["여름방학", "겨울방학"], "손님_평균"].max(),
      by_period["손님_평균"].round(1).to_dict().__str__())

by_exam = c.groupby("exam_week").agg(일수=("date", "size"), 손님_평균=("customers", "mean"), 매출_평균=("sales", "mean"))
by_exam_sem = sem.groupby("exam_week").agg(일수=("date", "size"), 손님_평균=("customers", "mean"), 매출_평균=("sales", "mean"))
by_rain = c.groupby("rain").agg(일수=("date", "size"), 손님_평균=("customers", "mean"), 매출_평균=("sales", "mean"))

menu_tot = c[MENU].sum().sort_values(ascending=False)
gap_check("메뉴별 총판매량", menu_tot.astype(float))
menu_rev = pd.Series({m: c[m].sum() * PRICE[m] for m in MENU}).sort_values(ascending=False)
gap_check("메뉴별 매출 합계", menu_rev.astype(float))

pivot = c.pivot_table(index="year_month", columns="weekday", values="customers", aggfunc="mean").reindex(columns=WD)
exam_days = c[c["exam_week"] == 1].groupby((c["exam_week"].diff() != 0).cumsum())["date"].agg(["min", "max"])

# ---------------------------------------------------------------------------
# 결과 출력
# ---------------------------------------------------------------------------
failed = [x for x in checks if not x[2]]
for name, detail, ok in checks:
    print(("PASS " if ok else "FAIL ") + name + " :: " + detail)
assert not failed, f"{len(failed)}개 검증 실패"

# ---------------------------------------------------------------------------
# data_facts.md
# ---------------------------------------------------------------------------
na_sleep = s[s["sleep_hours"].isna()]
na_sns = s[s["sns_minutes"].isna()]
sns_out = s[s["sns_minutes"] == 900]


def rows_desc(df: pd.DataFrame) -> str:
    return ", ".join(f"{sid}(index {i})" for i, sid in zip(df.index, df["student_id"]))


md = []
md.append("# 실습 데이터 정답표 (data_facts)\n")
md.append("`make_data.py`로 만든 가상 데이터의 실제 값이다. `check_data.py`가 CSV를 읽어 자동으로 쓴 파일이므로 손으로 고치지 않는다. "
          "교안·노트북의 정답 숫자는 여기서 가져다 쓴다. 숫자는 소수 2자리 반올림, index는 `pd.read_csv` 기본 0부터 시작하는 행 번호다.\n")
md.append("- 다시 만들기: `_tools/.venv/Scripts/python.exe _tools/make_data.py` → `_tools/.venv/Scripts/python.exe _tools/check_data.py`")
md.append("- 인코딩: UTF-8(BOM 없음). 범주값은 한글.\n")

md.append("## 검증 결과\n")
md.append(f"{len(checks)}개 항목 모두 통과. 순위 차이 기준은 1·2위, 최하위·차하위 사이 상대 차이 {MIN_GAP:.0%} 이상.\n")
md.append(md_table(pd.DataFrame([{"항목": n, "결과": d} for n, d, _ in checks]), index=False) + "\n")

md.append("## students.csv\n")
md.append(f"- {s.shape[0]}행 × {s.shape[1]}열, 학생 1명 = 1행\n")
md.append(md_table(col_summary(s), index=False) + "\n")
md.append("### 결측치\n")
md.append(f"- sleep_hours 결측 {len(na_sleep)}개: {rows_desc(na_sleep)}")
md.append(f"- sns_minutes 결측 {len(na_sns)}개: {rows_desc(na_sns)}")
md.append("- 두 열이 함께 빈 행은 없다. 결측 때문에 sleep_hours·sns_minutes는 float64로 읽힌다.\n")
md.append("### 이상치\n")
r = sns_out.iloc[0]
md.append(f"- sns_minutes 900: {r['student_id']}(index {sns_out.index[0]}), {r['major']}·{r['housing']}·{r['grade']}학년, sleep_hours {r['sleep_hours']}. "
          f"그다음 큰 값은 {s.loc[s['sns_minutes'] != 900, 'sns_minutes'].max():.0f}분")
r = cm_out.iloc[0]
md.append(f"- commute_minutes 180: {r['student_id']}(index {cm_out.index[0]}), {r['major']}·{r['housing']}·{r['grade']}학년. "
          f"그다음 큰 값은 {s.loc[s['commute_minutes'] != 180, 'commute_minutes'].max()}분")
q1, q3 = s["sns_minutes"].quantile([0.25, 0.75])
md.append(f"- 참고(IQR 규칙): sns_minutes Q1 {q1:.2f}, Q3 {q3:.2f}, 위쪽 경계 {q3 + 1.5 * (q3 - q1):.2f} → 경계를 넘는 값 "
          f"{int((s['sns_minutes'] > q3 + 1.5 * (q3 - q1)).sum())}개(박스플롯 점으로 찍히는 개수)")
q1, q3 = s["commute_minutes"].quantile([0.25, 0.75])
md.append(f"- 참고(IQR 규칙): commute_minutes Q1 {q1:.2f}, Q3 {q3:.2f}, 위쪽 경계 {q3 + 1.5 * (q3 - q1):.2f} → 경계를 넘는 값 "
          f"{int((s['commute_minutes'] > q3 + 1.5 * (q3 - q1)).sum())}개(전체 기준. 통학생이 많아 경계가 높다)\n")
md.append("### 상관계수\n")
md.append(md_table(pd.DataFrame(corr_rows), index=False) + "\n")
md.append("전체 상관행렬(`s.corr(numeric_only=True)`):\n")
md.append(md_table(s.corr(numeric_only=True)) + "\n")
md.append("### 전공별 study_hours-exam_score 회귀 기울기(np.polyfit 1차)\n")
md.append(md_table(pd.DataFrame({"기울기(점/시간)": pd.Series(slopes)}).sort_values("기울기(점/시간)", ascending=False)) + "\n")
md.append("### 분포 모양(왜도, `skew()`)\n")
md.append(md_table(pd.DataFrame({"왜도": s.drop(columns=["student_id", "major", "housing"]).skew()})) + "\n")
md.append(f"- 아르바이트 0시간: {int((s['part_time_hours'] == 0).sum())}명({zero_pt:.1%})")
md.append(f"- gpa 4.5(만점): {int((s['gpa'] == 4.5).sum())}명, exam_score 100점: {int((s['exam_score'] == 100).sum())}명, study_hours 40: {int((s['study_hours'] == 40).sum())}명\n")
md.append("### 전공별 평균 (공부 시간 내림차순)\n")
md.append(md_table(by_major) + "\n")
md.append("### 주거별 평균 (통학 시간 내림차순)\n")
md.append(md_table(by_housing) + "\n")
md.append("### 학년별 평균\n")
md.append(md_table(by_grade) + "\n")
md.append("### 전공 × 주거 인원\n")
md.append(md_table(major_housing) + "\n")
md.append("### 전체 기술통계(`describe()`)\n")
md.append(md_table(s.describe().T) + "\n")

md.append("## cafe_sales.csv\n")
md.append(f"- {c.shape[0]}행 × {c.shape[1]}열, 하루 = 1행, 결측 없음. 표의 date 자료형은 `parse_dates=['date']`로 읽은 경우\n")
md.append(md_table(col_summary(c), index=False) + "\n")
md.append("- 가격: 아메리카노 2,500 · 라떼 3,500 · 에이드 4,000 · 차 3,000원. sales는 365행 모두 잔 수 × 가격의 합과 같다.\n")
md.append("### 휴무일(모든 판매 값 0)\n")
md.append("- 2025 추석 연휴 10/5(일)~10/7(화) + 대체공휴일 10/8(수), 2026 설 연휴 2/16(월)~2/18(수). holidays 패키지(KR)로 날짜 확인\n")
md.append(md_table(closed[["date", "weekday", "period", "avg_temp", "rain", "customers", "sales"]].assign(date=closed["date"].dt.strftime("%Y-%m-%d")), index=False) + "\n")
md.append("- 휴무일에도 avg_temp·rain은 기록되어 있다(날씨는 있으므로). exam_week는 모두 0.\n")
md.append("### 시험 주간\n")
md.append(", ".join(f"{pd.Timestamp(a):%Y-%m-%d}~{pd.Timestamp(b):%m-%d}" for a, b in exam_days.values) + " (각 월~일 7일, 총 28일)\n")
md.append("전체 365일:\n")
md.append(md_table(by_exam) + "\n")
md.append("학기 중(1학기·2학기) 영업일만:\n")
md.append(md_table(by_exam_sem) + "\n")
md.append(f"- 학기 중 시험 주간 손님 / 비시험 주간 손님 = {exam_ratio:.2f}배\n")
md.append("### 비 여부별 평균(전체 365일)\n")
md.append(md_table(by_rain) + "\n")
md.append(f"- 비 온 날 손님은 안 온 날보다 {rain_ratio - 1:+.1%}. 비 온 날은 {int(c['rain'].sum())}일({c['rain'].mean():.1%})이며, 학사 기간·평일/주말에 고르게 퍼지도록 뽑았다.\n")
md.append("### 학사 기간(period)별\n")
md.append(md_table(by_period) + "\n")
md.append(f"- 시험 주간·휴무일 제외 학기 평일 손님 평균 {sem_weekday:.2f}, 학기 주말 {sem_weekend:.2f}, 방학 평일(휴무일 제외) {vac_weekday:.2f}\n")
md.append("### 월별 (학년도 순)\n")
md.append("- 손님_평균·매출_평균은 그 달 전체 날짜(휴무일 0 포함)로 나눈 값이다. 10월은 휴무 4일, 2월은 휴무 3일.\n")
md.append(md_table(by_month) + "\n")
v = by_month["매출_합계"].sort_values(ascending=False)
md.append(f"- 매출 합계 최대 {v.index[0]}({v.iloc[0]:,}원), 2위 {v.index[1]}({v.iloc[1]:,}원) / 최소 {v.index[-1]}({v.iloc[-1]:,}원), 차하위 {v.index[-2]}({v.iloc[-2]:,}원)")
v = by_month["손님_평균"].sort_values(ascending=False)
md.append(f"- 손님 평균 최대 {v.index[0]}({v.iloc[0]:.2f}), 최소 {v.index[-1]}({v.iloc[-1]:.2f})\n")
md.append("### 요일별\n")
md.append(md_table(by_wd) + "\n")
md.append("### 메뉴별 합계\n")
md.append(md_table(pd.DataFrame({"판매 잔 수": menu_tot, "매출(원)": menu_rev.reindex(menu_tot.index),
                                 "비율(%)": menu_tot / menu_tot.sum() * 100})) + "\n")
md.append("### 기온과 메뉴 판매량 상관\n")
md.append(md_table(pd.DataFrame({"영업일 전체(358일)": temp_corr, "학기 중 영업일": sem_temp_corr.reindex(temp_corr.index)})) + "\n")
md.append("- 기온이 높은 7·8월이 방학이라 손님 자체가 적다. 기온-에이드 산점도에서 학기/방학을 hue로 나누면 두 갈래가 보인다.\n")
md.append("### 월 × 요일 손님 평균(피벗 히트맵용)\n")
md.append(md_table(pivot) + "\n")
md.append("### 전체 기술통계(`describe()`)\n")
md.append(md_table(c.drop(columns=["date"]).describe().T) + "\n")

OUT.write_text("\n".join(md), encoding="utf-8")
print(f"\n{len(checks)}개 모두 통과 → {OUT}")
