import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL = "gemini-3.8-flash"
LITE_MODEL = "gemini-3.5-flash-lite"

client = genai.Client()

question = "대학 신입생이 첫 학기 교양 과목을 고를 때 볼 기준 세 가지를 알려 줘."


def ask(model_name):
    start = time.perf_counter()
    interaction = client.interactions.create(model=model_name, input=question)
    seconds = time.perf_counter() - start
    usage = interaction.usage
    print(f"[{model_name}] {seconds:.1f}초")
    print(interaction.output_text)
    print("입력 토큰:", usage.total_input_tokens)
    print("출력 토큰:", usage.total_output_tokens)
    print("생각 토큰:", usage.total_thought_tokens)
    print()


ask(MODEL)
ask(LITE_MODEL)
