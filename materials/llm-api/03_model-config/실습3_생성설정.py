import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL = "gemini-3.8-flash"

client = genai.Client()

PROBLEM = """아래 조건을 모두 지키는 이번 학기 시간표를 짜 줘.

[과목과 분반]
- 데이터베이스: A반 월 1~2교시 / B반 화 3~4교시
- 운영체제: A반 월 1~2교시 / B반 수 1~2교시 / C반 목 3~4교시
- 통계학: A반 화 3~4교시 / B반 목 3~4교시 / C반 금 1~2교시
- 영어회화: A반 수 1~2교시 / B반 목 1~2교시

[조건]
1. 네 과목을 하나씩 모두 듣는다
2. 같은 요일·같은 교시의 두 분반은 함께 들을 수 없다
3. 금요일에는 수업을 듣지 않는다
4. 목요일에는 수업을 하나만 듣는다
5. 영어회화는 운영체제보다 앞 요일에 듣는다

답은 '과목: 분반' 네 줄로만 써."""


def ask(question, level, max_tokens=None):
    config = {"thinking_level": level}
    if max_tokens:
        config["max_output_tokens"] = max_tokens

    start = time.perf_counter()
    interaction = client.interactions.create(
        model=MODEL,
        input=question,
        generation_config=config,
    )
    seconds = time.perf_counter() - start

    usage = interaction.usage
    print(f"[{level}, 상한 {max_tokens}] {seconds:.1f}초 / 상태: {interaction.status}")
    print(interaction.output_text)
    print("출력 토큰:", usage.total_output_tokens)
    print("생각 토큰:", usage.total_thought_tokens)
    print()


ask(PROBLEM, "low")
ask(PROBLEM, "high")
