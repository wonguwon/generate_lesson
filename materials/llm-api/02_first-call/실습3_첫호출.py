from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL = "gemini-3.8-flash"

client = genai.Client()

interaction = client.interactions.create(
    model=MODEL,
    input="대학 신입생에게 '수강 정정 기간'이 무엇인지 두 문장으로 설명해 줘.",
)

print(interaction.output_text)
