from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

MODEL = "gemini-3.8-flash"
EMBED_MODEL = "gemini-embedding-001"
PDF_PATH = "data/handbook.pdf"


def load_pdf(path):
    reader = PdfReader(path)
    pages = []
    for number, page in enumerate(reader.pages, start=1):
        pages.append(Document(page_content=page.extract_text(), metadata={"source": path, "page": number}))
    return pages


pages = load_pdf(PDF_PATH)
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(pages)

embeddings = GoogleGenerativeAIEmbeddings(model=EMBED_MODEL)
vector_store = InMemoryVectorStore.from_documents(chunks, embeddings)
print("저장한 조각:", len(chunks))
print("벡터 길이:", len(embeddings.embed_query("휴학")))
print()

RULES = """너는 OO대학교 학사 안내 도우미다.
[규칙]
- 질문과 함께 보낸 [문서]에 적힌 내용만 근거로 답한다
- [문서]에 답이 없으면 "학사 안내 문서에서 찾을 수 없습니다. 학사지원팀에 문의하세요."라고만 답한다
- 존댓말, 세 문장 이내
"""

retriever = vector_store.as_retriever(search_kwargs={"k": 3})
llm = ChatGoogleGenerativeAI(model=MODEL)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def make_chain(system):
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system),
            ("human", "[문서]\n{context}\n\n[질문]\n{question}"),
        ]
    )
    return (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )


rag_chain = make_chain(RULES)
print(rag_chain.invoke("직전 학기 평점이 4.2면 이번 학기에 몇 학점까지 신청할 수 있어요?"))
print()

print(rag_chain.invoke("기숙사 입사 신청은 언제 해요?"))
print()

loose_chain = make_chain("너는 OO대학교 학사 안내 도우미다.")
print(loose_chain.invoke("기숙사 입사 신청은 언제 해요?"))
