from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL = "gemini-3.8-flash"
CONFIG = {"thinking_level": "low"}
KEEP_TURNS = 2

client = genai.Client()

questions = [
    "제 이름은 한지우이고 컴퓨터공학과 1학년이에요. 답할 때 제 이름은 부르지 말아 주세요.",
    "수강 신청 전에 확인할 것 하나만 한 문장으로 알려 주세요.",
    "장학금 공지는 보통 어디서 보나요? 한 문장으로요.",
    "학과 행사 소식은 어디서 보나요? 한 문장으로요.",
    "제 이름과 학년이 뭐였죠?",
]


def show(number, interaction):
    usage = interaction.usage
    print(f"{number}턴 입력 토큰: {usage.total_input_tokens} / 캐시 토큰: {usage.total_cached_tokens}")


def recent(history, keep):
    starts = [i for i, step in enumerate(history) if step["type"] == "user_input"]
    if len(starts) <= keep:
        return history
    return history[starts[-(keep + 1)]:]


def run_local(keep=None):
    history = []
    for number, text in enumerate(questions, start=1):
        history.append({"type": "user_input", "content": [{"type": "text", "text": text}]})
        if keep:
            to_send = recent(history, keep)
        else:
            to_send = history
        interaction = client.interactions.create(
            model=MODEL,
            input=to_send,
            store=False,
            generation_config=CONFIG,
        )
        for step in interaction.steps:
            history.append(step.model_dump())
        show(number, interaction)
    print("5턴 답:", interaction.output_text)
    print()


def run_server():
    previous_id = None
    for number, text in enumerate(questions, start=1):
        interaction = client.interactions.create(
            model=MODEL,
            input=text,
            previous_interaction_id=previous_id,
            generation_config=CONFIG,
        )
        previous_id = interaction.id
        show(number, interaction)
    print("5턴 답:", interaction.output_text)
    print()


print("[직접 관리]")
run_local()
print("[서버 저장]")
run_server()
