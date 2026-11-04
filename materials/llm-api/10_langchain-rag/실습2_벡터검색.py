from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

load_dotenv()

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

QUESTIONS = [
    "1학년 수강 신청일은 언제야?",
    "휴학은 최대 몇 학기까지 할 수 있어?",
    "여름방학에 듣는 수업은 학점당 얼마야?",
]

for question in QUESTIONS:
    print("질문:", question)
    for doc, score in vector_store.similarity_search_with_score(question, k=3):
        title = [line for line in doc.page_content.splitlines() if not line.strip().startswith("-")][0]
        print(f"  {score:.3f} {doc.metadata['page']}쪽 {title}")
    print()

retriever = vector_store.as_retriever(search_kwargs={"k": 3})
docs = retriever.invoke("휴학은 최대 몇 학기까지 할 수 있어?")
print(type(docs).__name__, len(docs))
print([doc.metadata["page"] for doc in docs])
