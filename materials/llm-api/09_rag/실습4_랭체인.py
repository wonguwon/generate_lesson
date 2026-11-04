from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

MODEL = "gemini-3.8-flash"

llm = ChatGoogleGenerativeAI(model=MODEL)

response = llm.invoke("수강 정정 기간이 뭔지 한 문장으로 알려 줘.")
print(type(response).__name__)
print(response.text)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "너는 OO대학교 학사 안내 도우미다. 대학 신입생에게 두 문장 이내로 설명한다."),
        ("human", "{topic}에 대해 알려 줘."),
    ]
)
print(prompt.invoke({"topic": "휴학"}))

chain = prompt | llm | StrOutputParser()
print(chain.invoke({"topic": "휴학"}))

for topic in ["재수강", "계절학기"]:
    print(f"[{topic}]", chain.invoke({"topic": topic}))
