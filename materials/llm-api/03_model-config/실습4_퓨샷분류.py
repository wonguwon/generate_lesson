from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL = "gemini-3.8-flash"

client = genai.Client()

questions = [
    "졸업 요건을 채웠는지 어디서 확인하나요?",
    "국가장학금 신청 기간을 놓쳤어요.",
    "전공 필수 과목이 마감됐는데 어떻게 하죠?",
    "복학하려면 어떤 서류가 필요한가요?",
    "동아리 박람회는 어디서 하나요?",
    "교내 근로 장학생은 어떻게 뽑나요?",
    "계절학기 수강 신청은 언제 하나요?",
]


def zero_shot(question):
    return f"다음 문의를 학사, 장학, 수강, 기타 중 하나로 분류해 줘.\n문의: {question}"


def few_shot(question):
    return f"""문의를 학사, 장학, 수강, 기타 중 한 단어로 분류한다.

문의: 휴학 신청은 언제까지 해야 하나요?
분류: 학사

문의: 성적 장학금 기준이 궁금해요.
분류: 장학

문의: 수강 정정 기간에 과목을 바꿀 수 있나요?
분류: 수강

문의: 학생식당은 몇 시에 문을 여나요?
분류: 기타

문의: {question}
분류:"""


def ask(prompt):
    interaction = client.interactions.create(
        model=MODEL,
        input=prompt,
        generation_config={"thinking_level": "low"},
    )
    return interaction.output_text.strip()


print("[제로샷]", ask(zero_shot(questions[0])))
print()

for question in questions:
    print(question, "→", ask(few_shot(question)))
