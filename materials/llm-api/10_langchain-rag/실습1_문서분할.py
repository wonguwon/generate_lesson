from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

PDF_PATH = "data/handbook.pdf"


def load_pdf(path):
    reader = PdfReader(path)
    pages = []
    for number, page in enumerate(reader.pages, start=1):
        pages.append(Document(page_content=page.extract_text(), metadata={"source": path, "page": number}))
    return pages


pages = load_pdf(PDF_PATH)
print("쪽 수:", len(pages))
print(pages[1].metadata)
print(pages[1].page_content[:40])
print()

for size in [500, 200]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=50)
    chunks = splitter.split_documents(pages)
    print(f"chunk_size={size}: 조각 {len(chunks)}개")
    for chunk in chunks[1:3]:
        text = chunk.page_content.replace("\n", " ")
        print(f"  {chunk.metadata['page']}쪽 | {text[:15]} … {text[-15:]}")
    print()
