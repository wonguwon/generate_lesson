import os

import streamlit as st
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

load_dotenv()

MODEL = "gemini-3.8-flash"
EMBED_MODEL = "gemini-embedding-001"
PDF_PATH = "data/handbook.pdf"

SYSTEM_INSTRUCTION = """너는 OO대학교 학사 안내 도우미다.
[규칙]
- 질문과 함께 보낸 [문서]에 적힌 내용만 근거로 답한다
- [문서]에 답이 없으면 "학사 안내 문서에서 찾을 수 없습니다. 학사지원팀에 문의하세요."라고만 답한다
- 존댓말, 세 문장 이내
"""

st.title("학사 안내 챗봇")

if not os.getenv("GEMINI_API_KEY"):
    st.error("API 키가 없습니다. .env에 GEMINI_API_KEY를 넣고 앱을 다시 실행하세요.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

if st.sidebar.button("대화 초기화"):
    st.session_state.messages = []


def load_pdf(path):
    reader = PdfReader(path)
    pages = []
    for number, page in enumerate(reader.pages, start=1):
        pages.append(Document(page_content=page.extract_text(), metadata={"source": path, "page": number}))
    return pages


@st.cache_resource
def load_retriever():
    pages = load_pdf(PDF_PATH)
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(pages)
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBED_MODEL)
    vector_store = InMemoryVectorStore.from_documents(chunks, embeddings)
    print(f"[임베딩] 조각 {len(chunks)}개를 벡터 저장소에 넣음")
    return vector_store.as_retriever(search_kwargs={"k": 3})


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_INSTRUCTION),
        ("human", "[문서]\n{context}\n\n[질문]\n{question}"),
    ]
)
answer_chain = prompt | ChatGoogleGenerativeAI(model=MODEL) | StrOutputParser()


def answer(question):
    docs = load_retriever().invoke(question)
    text = answer_chain.invoke({"context": format_docs(docs), "question": question})
    return text, docs


def error_message(error):
    code = getattr(error.__cause__, "code", None)
    if code == 429:
        return "요청이 너무 많습니다. 잠시 뒤에 다시 보내 주세요."
    if code in (400, 401, 403):
        return "요청이 거절되었습니다. API 키를 확인하세요."
    if code == 404:
        return "모델을 찾을 수 없습니다. MODEL·EMBED_MODEL 이름을 확인하세요."
    if code is not None and code >= 500:
        return "Gemini 서버가 바쁩니다. 잠시 뒤에 다시 보내 주세요."
    return "답을 받지 못했습니다. 인터넷 연결과 PDF 위치를 확인하고 다시 보내 주세요."


def show_sources(sources):
    with st.expander("근거 보기"):
        for source in sources:
            st.caption(f"{source['page']}쪽")
            st.text(source["text"])


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message.get("sources"):
            show_sources(message["sources"])

question = st.chat_input("학사 안내에 대해 물어보세요")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("학사 안내 문서를 찾는 중"):
                text, docs = answer(question)
            sources = [{"page": doc.metadata["page"], "text": doc.page_content} for doc in docs]
            st.write(text)
            show_sources(sources)
            st.session_state.messages.append({"role": "assistant", "content": text, "sources": sources})
        except Exception as error:
            print(error)
            st.error(error_message(error))
