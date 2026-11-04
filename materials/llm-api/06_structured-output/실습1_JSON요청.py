import json

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
