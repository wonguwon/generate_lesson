"""Matplotlib·Seaborn 시각화 과정 실습 데이터(가상) 생성 스크립트.

실행:
    _tools/.venv/Scripts/python.exe _tools/make_data.py

결과:
    data/students.csv    대학생 생활 습관 설문(가상) 300행
    data/cafe_sales.csv  캠퍼스 카페 일별 판매(가상) 365행

난수 시드를 고정해 실행할 때마다 같은 파일이 나온다.
특징 검증과 정답 숫자 정리는 check_data.py가 한다.
"""

from pathlib import Path

import numpy as np
import pandas as pd

SEED_STUDENTS = 292
SEED_CAFE = 6

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


# ---------------------------------------------------------------------------
# students.csv
# ---------------------------------------------------------------------------
MAJOR_COUNTS = {"공학": 80, "사회과학": 70, "인문": 55, "자연과학": 55, "예체능": 40}
# 전공별 주간 자습 시간 기준값(시간)
MAJOR_STUDY = {"공학": 17.5, "자연과학": 14.5, "사회과학": 11.5, "인문": 9.0, "예체능": 6.5}
HOUSING_COUNTS = {"기숙사": 85, "자취": 115, "통학": 100}
# 주거별 아르바이트 하는 비율, 하는 사람의 평균 시간
HOUSING_PARTTIME = {"기숙사": (0.45, 9.0), "자취": (0.82, 14.0), "통학": (0.60, 10.0)}


def make_students(seed: int = SEED_STUDENTS) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    n = sum(MAJOR_COUNTS.values())

    major = rng.permutation(np.repeat(list(MAJOR_COUNTS), list(MAJOR_COUNTS.values())))
    housing = rng.permutation(np.repeat(list(HOUSING_COUNTS), list(HOUSING_COUNTS.values())))
    grade = rng.choice([1, 2, 3, 4], size=n, p=[0.28, 0.26, 0.24, 0.22])

    # 통학 시간(분)
    commute = np.empty(n)
    for h, (lo, hi) in {"기숙사": (5, 15), "자취": (5, 30), "통학": (30, 120)}.items():
        m = housing == h
        if h == "기숙사":
            v = rng.uniform(lo, hi + 1, m.sum())
        elif h == "자취":
            v = lo + rng.gamma(2.5, 4.0, m.sum())
        else:
            v = rng.normal(68, 20, m.sum())
        commute[m] = np.clip(v, lo, hi)
    commute = np.round(commute).astype(int)

    # 아르바이트 시간(주간)
    part = np.zeros(n)
    for h, (p, mu) in HOUSING_PARTTIME.items():
        m = housing == h
        works = rng.random(m.sum()) < p
        hours = np.clip(rng.normal(mu, 5.0, m.sum()), 3, 25)
        part[m] = np.where(works, hours, 0.0)
    part = np.round(part * 2) / 2  # 0.5시간 단위

    # 주간 자습 시간: 전공 기준값 × 오른쪽 꼬리 잡음 + 학년 - 아르바이트
    base = np.array([MAJOR_STUDY[m] for m in major])
    study = base * rng.gamma(4.0, 0.25, n) + 0.6 * (grade - 2.5) - 0.33 * (part - part.mean())
    study = np.round(np.clip(study, 0, 40), 1)

    # SNS(분)·커피(잔)·수면(시간)
    z_sns = rng.normal(size=n)
    sns = np.exp(np.log(132) + 0.48 * z_sns)
    sns = np.clip(np.round(sns / 5) * 5, 10, 480)

    z_coffee = rng.normal(size=n)
    coffee = rng.poisson(np.exp(np.log(5.5) + 0.45 * z_coffee + 0.015 * (study - study.mean())))
    coffee = np.clip(coffee, 0, 20).astype(int)

    sleep = 6.6 - 0.34 * z_sns - 0.07 * (coffee - coffee.mean()) + rng.normal(0, 0.80, n)
    sleep = np.round(np.clip(sleep, 4.0, 9.5), 1)

    # 기말 점수: 공부 시간과 양의 상관, 공학은 기울기가 조금 더 가파름, 왼쪽 꼬리
    slope = np.where(major == "공학", 1.6, 1.0)
    center = np.array([MAJOR_STUDY[m] for m in major])
    noise = rng.normal(0, 6.0, n) - rng.exponential(8.0, n) + 8.0
    exam = 73 + slope * (study - center) + 1.0 * (center - 12) + noise
    exam = np.clip(np.round(exam), 0, 100).astype(int)

    # 직전 학기 평점: 점수와 강한 양의 상관
    gpa = 0.75 + 0.035 * exam + rng.normal(0, 0.45, n)
    gpa = np.round(np.clip(gpa, 0.0, 4.5), 2)

    df = pd.DataFrame(
        {
            "student_id": [f"S{i:03d}" for i in range(1, n + 1)],
            "major": major,
            "grade": grade,
            "housing": housing,
            "commute_minutes": commute,
            "study_hours": study,
            "sleep_hours": sleep,
            "sns_minutes": sns.astype(float),
            "part_time_hours": part,
            "coffee_cups": coffee,
            "exam_score": exam,
            "gpa": gpa,
        }
    )

    # 이상치: SNS 900분 1명(수면도 짧게), 통학 180분 1명(통학생)
    sns_out = df.index[df["housing"] == "자취"][7]
    df.loc[sns_out, "sns_minutes"] = 900.0
    df.loc[sns_out, "sleep_hours"] = 4.3
    commute_out = df.index[df["housing"] == "통학"][11]
    df.loc[commute_out, "commute_minutes"] = 180

    # 결측치: sleep_hours 15개, sns_minutes 6개(이상치 행 제외, 서로 겹치지 않게)
    candidates = np.setdiff1d(df.index, [sns_out, commute_out])
    picked = rng.choice(candidates, size=21, replace=False)
    df.loc[np.sort(picked[:15]), "sleep_hours"] = np.nan
    df.loc[np.sort(picked[15:]), "sns_minutes"] = np.nan

    return df


# ---------------------------------------------------------------------------
# cafe_sales.csv
# ---------------------------------------------------------------------------
START, END = "2025-03-01", "2026-02-28"
WEEKDAY_KO = ["월", "화", "수", "목", "금", "토", "일"]
# 요일 계수(학기 평일 약 420, 주말 약 150)
WEEKDAY_FACTOR = {"월": 1.02, "화": 1.09, "수": 1.17, "목": 0.94, "금": 0.82, "토": 0.40, "일": 0.33}
# 학사 기간별 평일 기준 손님 수
PERIOD_BASE = {"1학기": 430, "여름방학": 180, "2학기": 405, "겨울방학": 170}
# 시험 주간(월~일, 각 1주)
EXAM_WEEKS = [
    ("2025-04-21", "2025-04-27"),  # 1학기 중간
    ("2025-06-09", "2025-06-15"),  # 1학기 기말
    ("2025-10-20", "2025-10-26"),  # 2학기 중간
    ("2025-12-08", "2025-12-14"),  # 2학기 기말
]
# 휴무일: 2025 추석 연휴(10/5~10/7) + 대체공휴일(10/8), 2026 설 연휴(2/16~2/18)
# 날짜는 holidays 패키지(KR)로 확인함
CLOSED_DAYS = pd.to_datetime(
    ["2025-10-05", "2025-10-06", "2025-10-07", "2025-10-08",
     "2026-02-16", "2026-02-17", "2026-02-18"]
)
PRICE = {"americano": 2500, "latte": 3500, "ade": 4000, "tea": 3000}


def academic_period(d: pd.Timestamp) -> str:
    md = (d.month, d.day)
    if (3, 1) <= md <= (6, 20):
        return "1학기"
    if (6, 21) <= md <= (8, 31):
        return "여름방학"
    if (9, 1) <= md <= (12, 19):
        return "2학기"
    return "겨울방학"


def make_cafe(seed: int = SEED_CAFE) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range(START, END, freq="D")
    n = len(dates)

    weekday = np.array([WEEKDAY_KO[d.weekday()] for d in dates])
    period = np.array([academic_period(d) for d in dates])
    exam = np.zeros(n, dtype=int)
    for s, e in EXAM_WEEKS:
        exam[(dates >= s) & (dates <= e)] = 1

    # 기온: 서울 월평균 기온(평년값 근사)을 매달 15일에 두고 날짜별로 보간 + 자기상관 잡음
    mid = pd.to_datetime([f"{y}-{m:02d}-15" for y, m in
                          [(2025, 2)] + [(2025, m) for m in range(3, 13)] + [(2026, 1), (2026, 2), (2026, 3)]])
    normals = [0.7, 6.1, 12.6, 18.2, 22.7, 25.3, 26.1, 21.6, 15.0, 7.5, 0.2, -2.0, 0.7, 6.1]
    seasonal = np.interp(dates.asi8, mid.asi8, normals)
    ar = np.zeros(n)
    for i in range(1, n):
        ar[i] = 0.7 * ar[i - 1] + rng.normal(0, 2.0)
    temp = np.round(np.clip(seasonal + ar, -10.0, 31.5), 1)

    # 비: 1년 내내 약 25%(계절·요일에 치우치지 않게 해 비 여부별 평균 비교가 깔끔하게 나오게)
    # 학사 기간 × 평일/주말 묶음마다 정확히 25%를 비 온 날로 뽑는다
    rain = np.zeros(n, dtype=int)
    is_weekend = np.isin(weekday, ["토", "일"])
    for p in PERIOD_BASE:
        for wk in (False, True):
            idx = np.flatnonzero((period == p) & (is_weekend == wk))
            k = int(round(len(idx) * 0.25))
            rain[rng.choice(idx, size=k, replace=False)] = 1

    # 손님 수
    base = np.array([PERIOD_BASE[p] for p in period], dtype=float)
    wf = np.array([WEEKDAY_FACTOR[w] for w in weekday])
    # 방학 주말은 학기만큼 크게 떨어지지 않음(방학 평일 자체가 낮음)
    vac = np.isin(period, ["여름방학", "겨울방학"])
    wf = np.where(vac & (wf < 0.5), wf + 0.12, wf)
    lam = base * wf * np.where(exam == 1, 1.33, 1.0) * np.where(rain == 1, 0.93, 1.0)
    customers = np.round(lam * rng.lognormal(0, 0.06, n)).astype(int)

    # 메뉴 비율: 기온이 오를수록 에이드↑, 라떼·차↓, 아메리카노는 거의 일정
    t = temp + 8  # 0~39
    share = np.column_stack(
        [
            np.full(n, 0.42),
            np.clip(0.36 - 0.0060 * t, 0.05, None),
            np.clip(0.02 + 0.0090 * t, 0.01, None),
            np.clip(0.20 - 0.0048 * t, 0.01, None),
        ]
    )
    share = share * rng.lognormal(0, 0.05, share.shape)
    cups = rng.poisson(customers[:, None] * share)
    americano, latte, ade, tea = cups.T

    closed = dates.isin(CLOSED_DAYS)
    for arr in (customers, americano, latte, ade, tea):
        arr[closed] = 0
    exam[closed] = 0

    sales = (americano * PRICE["americano"] + latte * PRICE["latte"]
             + ade * PRICE["ade"] + tea * PRICE["tea"])

    return pd.DataFrame(
        {
            "date": dates.strftime("%Y-%m-%d"),
            "year_month": dates.strftime("%Y-%m"),
            "month": dates.month,
            "weekday": weekday,
            "period": period,
            "exam_week": exam,
            "avg_temp": temp,
            "rain": rain,
            "customers": customers,
            "americano": americano,
            "latte": latte,
            "ade": ade,
            "tea": tea,
            "sales": sales,
        }
    )


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    students = make_students()
    cafe = make_cafe()
    students.to_csv(DATA_DIR / "students.csv", index=False, encoding="utf-8")
    cafe.to_csv(DATA_DIR / "cafe_sales.csv", index=False, encoding="utf-8")
    print(f"students.csv   {students.shape}")
    print(f"cafe_sales.csv {cafe.shape}")


if __name__ == "__main__":
    main()
