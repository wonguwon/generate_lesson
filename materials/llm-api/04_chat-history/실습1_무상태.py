from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL = "gemini-3.8-flash"

client = genai.Client()

first = client.interactions.create(
    model=MODEL,
    input="제 이름은 한지우이고 컴퓨터공학과 1학년이에요.",
)
print("답 1:", first.output_text)

second = client.interactions.create(
    model=MODEL,
    input="제 이름과 학년이 뭐였죠?",
)
print("답 2:", second.output_text)
