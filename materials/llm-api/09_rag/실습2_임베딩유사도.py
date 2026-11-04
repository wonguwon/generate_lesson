import numpy as np
from dotenv import load_dotenv
from google import genai

load_dotenv()

EMBED_MODEL = "gemini-embedding-2"

client = genai.Client()

result = client.models.embed_content(model=EMBED_MODEL, contents="수강 신청 기간이 언제야?")
vector = result.embeddings[0].values
print("벡터 개수:", len(result.embeddings))
print("벡터 길이:", len(vector))
print("앞 5개:", vector[:5])

SENTENCES = [
    "수강 신청 기간이 언제야?",
    "강의 등록은 언제 할 수 있어?",
    "오늘 학식 메뉴 뭐야?",
    "학교를 잠시 쉬고 싶어.",
    "휴학 신청 방법 알려 줘.",
]


def embed_texts(texts):
    result = client.models.embed_content(
        model=EMBED_MODEL,
        contents=[{"parts": [{"text": text}]} for text in texts],
    )
    return np.array([e.values for e in result.embeddings])


vectors = embed_texts(SENTENCES)
print("모양:", vectors.shape)


def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


for i, sentence in enumerate(SENTENCES):
    row = [f"{cosine(vectors[i], vectors[j]):.2f}" for j in range(len(SENTENCES))]
    print(" ".join(row), sentence)
