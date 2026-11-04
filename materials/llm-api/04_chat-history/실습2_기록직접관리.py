from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL = "gemini-3.8-flash"

client = genai.Client()

history = []


def chat(text):
    history.append({"type": "user_input", "content": [{"type": "text", "text": text}]})
    interaction = client.interactions.create(
        model=MODEL,
        input=history,
        store=False,
    )
    for step in interaction.steps:
        history.append(step.model_dump())
    return interaction.output_text


print("답 1:", chat("제 이름은 한지우이고 컴퓨터공학과 1학년이에요."))
print("답 2:", chat("제 이름과 학년이 뭐였죠?"))
print("단계 수:", len(history))
print([step["type"] for step in history])
