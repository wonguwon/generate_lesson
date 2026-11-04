from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL = "gemini-3.8-flash"

client = genai.Client()

short_question = "수강 정정 기간을 한 문장으로 설명해 줘."

long_question = """아래 안내문을 읽고 '확인'이라고만 답해.

수강 신청은 학년마다 시작하는 날이 다릅니다. 신청 전에 학과 공지에서 내 학년의 날짜를 확인하세요. 정정 기간에는 과목을 바꾸거나 취소할 수 있습니다. 궁금한 점은 학과 사무실에 문의하세요."""


def ask(title, question):
    interaction = client.interactions.create(model=MODEL, input=question)
    usage = interaction.usage
    print(f"[{title}] {interaction.output_text}")
    print("입력 토큰:", usage.total_input_tokens)
    print("출력 토큰:", usage.total_output_tokens)
    print("생각 토큰:", usage.total_thought_tokens)
    print("합계:", usage.total_tokens)
    print()


ask("짧은 질문", short_question)
ask("긴 질문", long_question)
