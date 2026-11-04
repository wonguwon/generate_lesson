from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL = "gemini-3.8-flash"

client = genai.Client()

QUESTION = "OO대학교 2027학년도 1학기 수강 신청에서 1학년은 며칠에 신청해?"

interaction = client.interactions.create(model=MODEL, input=QUESTION)
print(interaction.output_text)
print()

interaction = client.interactions.create(model=MODEL, input=QUESTION + " 설명 없이 날짜만 답해.")
print(interaction.output_text)
print()

with open("data/handbook_paragraphs.txt", encoding="utf-8") as f:
    HANDBOOK = [line for line in f.read().splitlines() if line.strip()]

print("문단 수:", len(HANDBOOK))
print(HANDBOOK[0])
print()


def ask_with(context):
    prompt = f"""아래 안내문을 보고 질문에 답해.

[안내문]
{context}

[질문]
{QUESTION}"""
    interaction = client.interactions.create(model=MODEL, input=prompt)
    print(interaction.output_text)
    print("입력 토큰:", interaction.usage.total_input_tokens)
    print()


ask_with(HANDBOOK[0])

ask_with("\n\n".join(HANDBOOK))
