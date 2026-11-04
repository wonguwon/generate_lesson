"""6차시 구조화 출력과 강의평 분석기 - 실습 파일 생성

사용: llm-api 폴더에서 py -X utf8 _생성스크립트/make_06.py .
(인자는 llm-api 폴더. 코드는 06_structured-output/, 자료는 data/reviews.csv에 덮어씀.
 다른 파일은 지우거나 건드리지 않음)
"""
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
OUT = ROOT / "06_structured-output"
DATA = ROOT / "data"

# ── data/reviews.csv : 교안 토글 원문 그대로 ──────────────────────
# (강의명, 강의평, 분류) 분류는 assert용. 애매 = 긍정·부정이 섞인 평
REVIEWS = [
    ("데이터베이스", "예제가 많아서 SQL을 처음 배우는 사람도 따라가기 좋았어요.", "긍정"),
    ("데이터베이스", "과제 피드백이 꼼꼼해서 실력이 늘었다는 게 느껴졌습니다.", "긍정"),
    ("데이터베이스", "매주 퀴즈가 있고 수업은 교재 순서대로 진행됩니다.", "중립"),
    ("데이터베이스", "팀 프로젝트 조 편성이 엉망이라 한 학기 내내 스트레스였어요.", "부정"),
    ("운영체제", "어려운 개념을 그림으로 풀어 주셔서 이해가 잘 됐어요.", "긍정"),
    ("운영체제", "진도가 너무 빨라서 중간부터는 무슨 말인지 하나도 몰랐어요.", "부정"),
    ("운영체제", "내용은 정말 유익했는데 과제 양이 감당하기 힘들 만큼 많았어요.", "애매"),
    ("운영체제", "실습 환경 설정을 직접 도와주셔서 막힘없이 따라갔습니다.", "긍정"),
    ("통계학", "R 실습이 있어서 이론이 실제로 어떻게 쓰이는지 알 수 있었어요.", "긍정"),
    ("통계학", "수업은 녹화 강의로 진행되고 시험은 대면으로 봅니다.", "중립"),
    ("통계학", "질문을 해도 답이 늦고 공지가 자주 바뀌어서 불편했어요.", "부정"),
    ("통계학", "시험은 쉬웠는데 막상 남는 건 별로 없는 것 같아요.", "애매"),
    ("영어회화", "원어민 선생님과 매시간 대화해서 말하기 자신감이 생겼어요.", "긍정"),
    ("영어회화", "발표 기회가 골고루 돌아가서 분위기가 편했어요.", "긍정"),
    ("영어회화", "분반별로 교재가 다르고 출석은 전자출결로 확인합니다.", "중립"),
    ("영어회화", "평가 기준이 공지되지 않아 성적을 납득하기 어려웠어요.", "부정"),
    ("파이썬프로그래밍", "코딩을 처음 해 보는데도 단계별로 차근차근 알려 주셔서 좋았어요.", "긍정"),
    ("파이썬프로그래밍", "실습 시간이 넉넉해서 수업 중에 과제를 거의 끝낼 수 있었어요.", "긍정"),
    ("파이썬프로그래밍", "강의 자료 오타가 많아서 따라 치다가 오류가 자주 났어요.", "부정"),
    ("파이썬프로그래밍", "재미있긴 한데 다음 학기에 또 듣고 싶은지는 잘 모르겠어요.", "애매"),
    ("글쓰기와표현", "첨삭을 받으면서 보고서 쓰는 법이 확실히 좋아졌어요.", "긍정"),
    ("글쓰기와표현", "매주 짧은 글을 한 편씩 제출하고 기말에는 에세이를 냅니다.", "중립"),
    ("글쓰기와표현", "토론 수업이 활발해서 생각을 정리하는 데 도움이 됐어요.", "긍정"),
    ("글쓰기와표현", "과제 마감이 다른 과목 시험 기간과 겹쳐서 너무 힘들었어요.", "부정"),
]

# 실습 3 ②의 reviews 목록 (교안 그대로)
EX3_REVIEWS = [
    ("운영체제", "내용은 정말 유익했는데 과제 양이 감당하기 힘들 만큼 많았어요."),
    ("통계학", "시험은 쉬웠는데 막상 남는 건 별로 없는 것 같아요."),
    ("파이썬프로그래밍", "재미있긴 한데 다음 학기에 또 듣고 싶은지는 잘 모르겠어요."),
]

# ── 교안 정답 표 확인 ─────────────────────────────────────────────────────
assert len(REVIEWS) == 24, "데이터 행 24"
courses = Counter(c for c, _, _ in REVIEWS)
assert len(courses) == 6 and set(courses.values()) == {4}, "강의 6개 × 4건"
labels = Counter(l for _, _, l in REVIEWS)
assert labels == {"긍정": 11, "부정": 6, "중립": 4, "애매": 3}, labels
assert [(c, r) for c, r, l in REVIEWS if l == "애매"] == EX3_REVIEWS, "애매한 평 = 실습 3 세 건"
first5 = Counter(l for _, _, l in REVIEWS[:5])
assert first5.most_common(1)[0][0] == "긍정", "③ 5건: 긍정 막대가 가장 높음"
# ④ 24건 범위: 애매 3건이 어디로 가든 긍정 11~14 · 부정 6~9 · 중립 4~7
assert (labels["긍정"], labels["긍정"] + 3) == (11, 14)
assert (labels["부정"], labels["부정"] + 3) == (6, 9)
assert (labels["중립"], labels["중립"] + 3) == (4, 7)
assert all("," not in r and '"' not in r for _, r, _ in REVIEWS), "따옴표 없는 CSV"

CSV = "강의명,강의평\n" + "".join(f"{c},{r}\n" for c, r, _ in REVIEWS)

# ── 완성 코드 : 교안 코드 블록 그대로 (단계별로 이어 붙인 최종 상태) ──────
EX1 = r'''import json

from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL = "gemini-3.8-flash"

client = genai.Client()

REVIEW = """강의명: 데이터베이스
강의평: 교수님 설명이 쉽고 예제가 많아서 좋았어요. 다만 기말고사 범위가 너무 넓었어요."""

prompt = f"다음 강의평을 분석해서 코드 블록 없이 JSON만 줘.\n\n{REVIEW}"

for i in range(3):
    interaction = client.interactions.create(model=MODEL, input=prompt)
    text = interaction.output_text
    print(f"--- {i + 1}번째 답 ---")
    print(text)
    try:
        data = json.loads(text)
        print("파싱 성공, 키:", list(data))
    except json.JSONDecodeError as error:
        print("파싱 실패:", error)
    print()
'''
EX1_STEP2_PROMPT = 'prompt = f"다음 강의평을 분석해서 JSON으로 줘.\\n\\n{REVIEW}"'
EX1_STEP3_PROMPT = 'prompt = f"다음 강의평을 분석해서 코드 블록 없이 JSON만 줘.\\n\\n{REVIEW}"'
assert EX1_STEP3_PROMPT in EX1

EX2 = r'''from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel

load_dotenv()

MODEL = "gemini-3.8-flash"

client = genai.Client()

REVIEW = """강의명: 데이터베이스
강의평: 교수님 설명이 쉽고 예제가 많아서 좋았어요. 다만 기말고사 범위가 너무 넓었어요."""


class ReviewAnalysis(BaseModel):
    course: str
    sentiment: str
    score: int
    keywords: list[str]


print(ReviewAnalysis.model_json_schema())

interaction = client.interactions.create(
    model=MODEL,
    input=f"다음 강의평을 분석해 줘.\n\n{REVIEW}",
    response_format={
        "type": "text",
        "mime_type": "application/json",
        "schema": ReviewAnalysis.model_json_schema(),
    },
)
print(interaction.output_text)

result = ReviewAnalysis.model_validate_json(interaction.output_text)
print("강의명:", result.course)
print("감성:", result.sentiment)
print("점수:", result.score)
print("키워드:", result.keywords)
'''

EX3 = r'''from typing import Literal

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field, ValidationError

load_dotenv()

MODEL = "gemini-3.8-flash"

client = genai.Client()


class ReviewAnalysis(BaseModel):
    course: str = Field(description="강의명")
    sentiment: Literal["긍정", "부정", "중립"] = Field(
        description="강의평 전체의 감성. 긍정과 부정이 섞여 있으면 더 강한 쪽, 비슷하면 중립"
    )
    score: int = Field(ge=1, le=5, description="만족도. 1 매우 불만족, 3 보통, 5 매우 만족")
    keywords: list[str] = Field(max_length=3, description="강의평의 핵심 키워드 1~3개")


print(ReviewAnalysis.model_json_schema())

reviews = [
    ("운영체제", "내용은 정말 유익했는데 과제 양이 감당하기 힘들 만큼 많았어요."),
    ("통계학", "시험은 쉬웠는데 막상 남는 건 별로 없는 것 같아요."),
    ("파이썬프로그래밍", "재미있긴 한데 다음 학기에 또 듣고 싶은지는 잘 모르겠어요."),
]


def analyze(course, review):
    interaction = client.interactions.create(
        model=MODEL,
        input=f"다음 강의평을 분석해 줘.\n\n강의명: {course}\n강의평: {review}",
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": ReviewAnalysis.model_json_schema(),
        },
    )
    return ReviewAnalysis.model_validate_json(interaction.output_text)


for course, review in reviews:
    result = analyze(course, review)
    print(course, "→", result.sentiment, result.score, result.keywords)

wrong = '{"course": "통계학", "sentiment": "좋음", "score": 7, "keywords": []}'
try:
    ReviewAnalysis.model_validate_json(wrong)
except ValidationError as error:
    print(error)
'''

APP = r'''import os
from typing import Literal

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field

load_dotenv()

MODEL = "gemini-3.8-flash"

SYSTEM_INSTRUCTION = "너는 대학 강의평을 분석하는 도우미다. 강의평에 적힌 내용만 근거로 판단한다."


class ReviewAnalysis(BaseModel):
    course: str = Field(description="강의명")
    sentiment: Literal["긍정", "부정", "중립"] = Field(
        description="강의평 전체의 감성. 긍정과 부정이 섞여 있으면 더 강한 쪽, 비슷하면 중립"
    )
    score: int = Field(ge=1, le=5, description="만족도. 1 매우 불만족, 3 보통, 5 매우 만족")
    keywords: list[str] = Field(max_length=3, description="강의평의 핵심 키워드 1~3개")


st.title("강의평 분석기")

if not os.getenv("GEMINI_API_KEY"):
    st.error("API 키가 없습니다. .env에 GEMINI_API_KEY를 넣고 앱을 다시 실행하세요.")
    st.stop()

client = genai.Client()


def analyze(course, review):
    interaction = client.interactions.create(
        model=MODEL,
        system_instruction=SYSTEM_INSTRUCTION,
        input=f"강의명: {course}\n강의평: {review}",
        generation_config={"thinking_level": "low"},
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": ReviewAnalysis.model_json_schema(),
        },
    )
    return ReviewAnalysis.model_validate_json(interaction.output_text)


def error_message(error):
    code = getattr(error, "status_code", None)
    if code == 429:
        return "요청이 너무 많습니다. 잠시 뒤에 다시 보내 주세요."
    if code in (400, 401, 403):
        return "요청이 거절되었습니다. API 키를 확인하세요."
    if code == 404:
        return "모델을 찾을 수 없습니다. MODEL 이름을 확인하세요."
    if code is not None and code >= 500:
        return "Gemini 서버가 바쁩니다. 잠시 뒤에 다시 보내 주세요."
    return "답을 받지 못했습니다. 인터넷 연결을 확인하고 다시 보내 주세요."


reviews = pd.read_csv("data/reviews.csv")
st.caption(f"강의평 {len(reviews)}건")

count = st.slider("분석할 강의평 수", 1, len(reviews), 5)

if st.button("분석 시작"):
    rows = reviews.head(count).to_dict("records")
    results = []
    progress = st.progress(0, text="분석 준비 중")

    for i, row in enumerate(rows, start=1):
        try:
            result = analyze(row["강의명"], row["강의평"])
        except Exception as error:
            print(error)
            st.error(f"{i}번째에서 멈춤: {error_message(error)}")
            break
        results.append(result.model_dump())
        progress.progress(i / count, text=f"{i}/{count}건 분석")

    if results:
        table = pd.DataFrame(results)
        st.dataframe(table)
        st.bar_chart(table["sentiment"].value_counts())
'''

# 실습 3의 클래스는 app.py와 같아야 함 (교안: "ReviewAnalysis는 실습 3 그대로")
_cls = EX3[EX3.index("class ReviewAnalysis"):EX3.index("print(ReviewAnalysis")]
assert _cls in APP
# 실습 3 의 애매한 평은 CSV와 같은 문장
for c, r in EX3_REVIEWS:
    assert f'("{c}", "{r}")' in EX3

TEACHER = {
    "실습1_JSON요청.py": EX1,
    "실습2_스키마.py": EX2,
    "실습3_열거형.py": EX3,
    "app.py": APP,
}

# ── 쓰기 ─────────────────────────────────────────────────────────────────
DATA.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

# pd.read_csv 기본 인코딩(utf-8)에 맞춰 BOM 없이, 줄바꿈 \n
(DATA / "reviews.csv").write_bytes(CSV.encode("utf-8"))
for name, code in TEACHER.items():
    compile(code, name, "exec")
    (OUT / name).write_bytes(code.encode("utf-8"))

print("06_structured-output 생성 완료:", OUT)
print("  data/reviews.csv", len(REVIEWS), "행", dict(labels))
for name in TEACHER:
    print("  06_structured-output/" + name)
