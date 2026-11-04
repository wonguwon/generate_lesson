from dotenv import load_dotenv
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
