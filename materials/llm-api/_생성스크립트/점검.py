"""llm-api 실습 폴더 점검

실행: llm-api 폴더에서 py -X utf8 _생성스크립트/점검.py
- 모든 .py 문법 확인(compile만 하므로 __pycache__가 생기지 않음)
- 있어야 할 파일 목록
- 강사용·학습자용·__pycache__·.env가 남아 있지 않은지
- .py·.txt·.csv는 BOM 없음, README.md와 메모장으로 여는 01 실습_요청문.txt는 BOM 있음
- data/handbook_paragraphs.txt 문단 10줄, data/reviews.csv 데이터 24행
마지막 줄이 "모두 일치"면 정상.
"""
import csv
import sys

sys.dont_write_bytecode = True
from pathlib import Path  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BOM = b"\xef\xbb\xbf"

EXPECTED = [
    "README.md", "requirements.txt", ".env.example", ".gitignore",
    "01_api-vs-web/README.md", "01_api-vs-web/실습_요청문.txt",
    "02_first-call/README.md",
    "02_first-call/실습1_버전확인.py", "02_first-call/실습2_키확인.py",
    "02_first-call/실습3_첫호출.py", "02_first-call/실습4_토큰확인.py",
    "03_model-config/README.md",
    "03_model-config/실습1_모델비교.py", "03_model-config/실습2_시스템지시.py",
    "03_model-config/실습3_생성설정.py", "03_model-config/실습4_퓨샷분류.py",
    "04_chat-history/README.md",
    "04_chat-history/실습1_무상태.py", "04_chat-history/실습2_기록직접관리.py",
    "04_chat-history/실습3_터미널챗봇.py", "04_chat-history/실습4_방식비교.py",
    "05_streamlit-chat/README.md",
    "05_streamlit-chat/실습1_한화면앱.py", "05_streamlit-chat/실습2_채팅앱.py",
    "05_streamlit-chat/실습3_스트리밍.py", "05_streamlit-chat/app.py",
    "06_structured-output/README.md",
    "06_structured-output/실습1_JSON요청.py", "06_structured-output/실습2_스키마.py",
    "06_structured-output/실습3_열거형.py", "06_structured-output/app.py",
    "07_multimodal/README.md",
    "07_multimodal/실습1_이미지질문.py", "07_multimodal/실습2_영수증분석.py",
    "07_multimodal/실습3_검증.py", "07_multimodal/app.py",
    "08_function-calling/README.md",
    "08_function-calling/실습1_함수선언.py", "08_function-calling/실습2_함수실행.py",
    "08_function-calling/app.py",
    "09_rag/README.md",
    "09_rag/실습1_환각확인.py", "09_rag/실습2_임베딩유사도.py",
    "09_rag/실습3_미니RAG.py", "09_rag/실습4_랭체인.py",
    "10_langchain-rag/README.md",
    "10_langchain-rag/실습1_문서분할.py", "10_langchain-rag/실습2_벡터검색.py",
    "10_langchain-rag/실습3_RAG체인.py", "10_langchain-rag/app.py",
    "data/reviews.csv", "data/campus.jpg",
    "data/receipts/receipt1_cafe.jpg", "data/receipts/receipt2_store.jpg",
    "data/receipts/receipt3_book.jpg", "data/receipts/receipt4_blur.jpg",
    "data/handbook_paragraphs.txt", "data/handbook.pdf",
    "_생성스크립트/make_06.py", "_생성스크립트/make_07.py",
    "_생성스크립트/make_09.py", "_생성스크립트/make_pdf.py", "_생성스크립트/점검.py",
]
FORBIDDEN = {"강사용", "학습자용", "__pycache__", ".env"}

problems = []

# 1. 있어야 할 파일
for rel in EXPECTED:
    if not (ROOT / rel).is_file():
        problems.append(f"없음: {rel}")

# 2. 남으면 안 되는 이름
for p in ROOT.rglob("*"):
    if p.name in FORBIDDEN:
        problems.append(f"남아 있음: {p.relative_to(ROOT).as_posix()}")

# 3. BOM 규칙과 .py 문법
py_count = 0
for p in sorted(ROOT.rglob("*")):
    if not p.is_file():
        continue
    rel = p.relative_to(ROOT).as_posix()
    raw = p.read_bytes()
    if p.name == "README.md" or rel == "01_api-vs-web/실습_요청문.txt":
        if not raw.startswith(BOM):
            problems.append(f"BOM 없음(README·요청문은 BOM 필요): {rel}")
    elif p.suffix in {".py", ".txt", ".csv"}:
        if raw.startswith(BOM):
            problems.append(f"BOM 있음: {rel}")
    if p.suffix == ".py":
        py_count += 1
        try:
            compile(raw.decode("utf-8"), str(p), "exec")
        except (SyntaxError, UnicodeDecodeError) as error:
            problems.append(f"문법 오류: {rel}: {error}")

# 4. 자료 내용
handbook = ROOT / "data" / "handbook_paragraphs.txt"
if handbook.is_file():
    lines = [line for line in handbook.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(lines) != 10:
        problems.append(f"handbook_paragraphs.txt 문단 수 {len(lines)} (10이어야 함)")

reviews = ROOT / "data" / "reviews.csv"
if reviews.is_file():
    with open(reviews, encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    if rows[0] != ["강의명", "강의평"]:
        problems.append(f"reviews.csv 머리글 {rows[0]}")
    if len(rows) - 1 != 24:
        problems.append(f"reviews.csv 데이터 {len(rows) - 1}행 (24이어야 함)")

print(f"확인한 파일 {len(EXPECTED)}개, .py 문법 {py_count}개")
if problems:
    for line in problems:
        print("문제:", line)
    sys.exit(1)
print("모두 일치")
