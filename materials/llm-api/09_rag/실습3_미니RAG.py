import numpy as np
from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL = "gemini-3.8-flash"
EMBED_MODEL = "gemini-embedding-2"

client = genai.Client()

with open("data/handbook_paragraphs.txt", encoding="utf-8") as f:
    HANDBOOK = [line for line in f.read().splitlines() if line.strip()]


def embed_texts(texts):
    result = client.models.embed_content(
        model=EMBED_MODEL,
        contents=[{"parts": [{"text": text}]} for text in texts],
    )
    return np.array([e.values for e in result.embeddings])


def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


doc_vectors = embed_texts([f"title: none | text: {p}" for p in HANDBOOK])
print("문단 벡터:", doc_vectors.shape)


def search(question, k=3):
    q = embed_texts([f"task: search result | query: {question}"])[0]
    scores = [cosine(q, v) for v in doc_vectors]
    top = np.argsort(scores)[::-1][:k]
    return [(scores[i], HANDBOOK[i]) for i in top]


for score, paragraph in search("휴학은 최대 몇 학기까지 할 수 있어요?"):
    print(f"{score:.3f} {paragraph[:25]}")

SYSTEM_INSTRUCTION = """너는 OO대학교 학사 안내 도우미다.
[규칙]
- 질문과 함께 보낸 [문서]에 적힌 내용만 근거로 답한다
- [문서]에 답이 없으면 "학사 안내 문서에서 찾을 수 없습니다. 학사지원팀에 문의하세요."라고만 답한다
- 존댓말, 세 문장 이내
"""


def answer(question):
    found = search(question)
    context = "\n\n".join(paragraph for _, paragraph in found)
    interaction = client.interactions.create(
        model=MODEL,
        system_instruction=SYSTEM_INSTRUCTION,
        input=f"[문서]\n{context}\n\n[질문]\n{question}",
    )
    return interaction.output_text, found


QUESTIONS = [
    "휴학은 최대 몇 학기까지 할 수 있어요?",
    "직전 학기 평점이 4.2면 이번 학기에 몇 학점까지 신청할 수 있어요?",
    "기숙사 입사 신청은 언제 해요?",
]

for question in QUESTIONS:
    text, found = answer(question)
    print("질문:", question)
    for score, paragraph in found:
        print(f"  {score:.3f} {paragraph[:25]}")
    print("답:", text)
    print()
