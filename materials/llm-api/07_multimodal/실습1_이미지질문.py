import base64

from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL = "gemini-3.8-flash"

client = genai.Client()

with open("data/campus.jpg", "rb") as f:
    image_bytes = f.read()

print("바이트 수:", len(image_bytes))
print("앞 3바이트:", image_bytes[:3])

image_data = base64.b64encode(image_bytes).decode()
print("base64 앞 20글자:", image_data[:20])

QUESTION = "이 사진에 무엇이 보이는지 세 문장으로 설명해 줘."

interaction = client.interactions.create(
    model=MODEL,
    input=[
        {"type": "text", "text": QUESTION},
        {"type": "image", "mime_type": "image/jpeg", "data": image_data},
    ],
)
print(interaction.output_text)
print("입력 토큰:", interaction.usage.total_input_tokens)
print("종류별:", interaction.usage.input_tokens_by_modality)

text_only = client.interactions.create(model=MODEL, input=QUESTION)
print(text_only.output_text)
print("이미지 없이 입력 토큰:", text_only.usage.total_input_tokens)
