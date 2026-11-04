from typing import Literal

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
