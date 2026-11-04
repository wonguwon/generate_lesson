"""7차시 멀티모달과 영수증 가계부 - 실습 파일 생성

사용: llm-api 폴더에서 py -X utf8 _생성스크립트/make_07.py .
(인자는 llm-api 폴더. 코드는 07_multimodal/, 이미지는 data/campus.jpg·data/receipts/에 덮어씀.
 다른 파일은 지우거나 건드리지 않음)
필요: pillow, Windows 맑은 고딕(C:/Windows/Fonts/malgun.ttf, malgunbd.ttf)
"""
import base64
import io
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
OUT = ROOT / "07_multimodal"
DATA = ROOT / "data"
FONT = "C:/Windows/Fonts/malgun.ttf"
FONT_BOLD = "C:/Windows/Fonts/malgunbd.ttf"

# ── 영수증 데이터 : 교안 토글 "영수증 네 장에 인쇄된 내용" 그대로 ─────────
# 파일 이름: (가게, 날짜, 카테고리(정답), [(품목, 수량, 단가)], 합계)
RECEIPTS = {
    "receipt1_cafe.jpg": ("OO카페 정문점", "2026-10-26", "카페", [
        ("아메리카노", 2, 4500), ("카페라떼", 1, 5000), ("치즈케이크", 1, 6500),
    ], 20500),
    "receipt2_store.jpg": ("OO편의점 학생회관점", "2026-10-27", "식비", [
        ("삼각김밥", 2, 1500), ("컵라면", 2, 1800), ("생수 500ml", 2, 900),
        ("바나나우유", 1, 1700), ("초코바", 3, 1200), ("샌드위치", 1, 3200),
        ("요구르트", 4, 500), ("껌", 1, 1000),
    ], 19900),
    "receipt3_book.jpg": ("OO서점 캠퍼스점", "2026-10-29", "도서·문구", [
        ("파이썬 입문", 1, 28000), ("공학용 노트", 3, 2500), ("형광펜 세트", 1, 4500),
    ], 40000),
    "receipt4_blur.jpg": ("OO생활마트", "2026-10-30", "생활용품", [
        ("주방세제", 1, 8900), ("두루마리 휴지", 1, 12900), ("수세미", 2, 1500),
    ], 24800),
}
# receipt4: 휴지 줄의 12,900(단가·금액 둘 다)과 합계 24,800을 흐리게.
# 단가를 남겨 두면 1 x 12,900에서 금액을 계산해 채울 수 있어 교안의 "확인 필요" 상황이 안 생김
BLUR = {"receipt4_blur.jpg": {"items": {"두루마리 휴지"}, "total": True}}

# ── 교안 정답 표 확인 ─────────────────────────────────────────────────────
EXPECT = {  # 파일: (품목 수, 총액)  - 실습 자료 표
    "receipt1_cafe.jpg": (3, 20500),
    "receipt2_store.jpg": (8, 19900),
    "receipt3_book.jpg": (3, 40000),
    "receipt4_blur.jpg": (3, 24800),
}
for name, (store, date, cat, items, total) in RECEIPTS.items():
    amounts = [q * p for _, q, p in items]
    assert len(items) == EXPECT[name][0], name
    assert sum(amounts) == total == EXPECT[name][1], (name, sum(amounts), total)
    assert store.startswith("OO") and len(date) == 10
# 실습 2 ③: 카페 품목별 금액
assert [q * p for _, q, p in RECEIPTS["receipt1_cafe.jpg"][3]] == [9000, 5000, 6500]
# 실습 3 ②: 직접 만든 틀린 영수증 9,000 + 8,000 = 17,000 vs 14,000
assert 9000 + 8000 == 17000
# 실습 4 ③: 3 + 8 + 3 + 3 = 17줄, 카테고리별 합계
assert sum(len(v[3]) for v in RECEIPTS.values()) == 17
CAT_SUM = {v[2]: v[4] for v in RECEIPTS.values()}
assert CAT_SUM == {"카페": 20500, "식비": 19900, "도서·문구": 40000, "생활용품": 24800}
# 실습 4 ② 안내 문장
assert f"{RECEIPTS['receipt1_cafe.jpg'][0]} {20500:,}원을 추가했습니다." == "OO카페 정문점 20,500원을 추가했습니다."


# ── 영수증 그리기 ────────────────────────────────────────────────────────
def font(size, bold=False):
    return ImageFont.truetype(FONT_BOLD if bold else FONT, size)


def draw_receipt(name):
    store, date, _cat, items, total = RECEIPTS[name]
    blur = BLUR.get(name, {"items": set(), "total": False})
    W, M = 600, 40
    LINE = 40
    H = 330 + LINE * len(items) + 120
    paper = (250, 249, 244)
    ink = (38, 38, 42)
    img = Image.new("RGB", (W, H), paper)
    d = ImageDraw.Draw(img)
    f_title, f_body, f_bold, f_small = font(32, True), font(23), font(26, True), font(16)
    blur_boxes = []

    def center(y, text, f, fill=ink):
        w = d.textlength(text, font=f)
        d.text(((W - w) / 2, y), text, font=f, fill=fill)

    def right(x, y, text, f):
        w = d.textlength(text, font=f)
        d.text((x - w, y), text, font=f, fill=ink)
        return (int(x - w) - 6, y - 2, int(x) + 6, y + LINE - 6)

    def dashes(y):
        x = M
        while x < W - M:
            d.line([(x, y), (x + 8, y)], fill=(90, 90, 95), width=2)
            x += 14

    y = 36
    center(y, store, f_title)
    y += 60
    center(y, date, f_body)
    y += 50
    dashes(y)
    y += 14
    d.text((M, y), "품목", font=f_body, fill=ink)
    right(400, y, "수량 x 단가", f_body)
    right(W - M, y, "금액", f_body)
    y += LINE
    dashes(y)
    y += 14
    for item, qty, unit in items:
        d.text((M, y), item, font=f_body, fill=ink)
        right(332, y, f"{qty} x", f_body)
        ub = right(430, y, f"{unit:,}", f_body)
        ab = right(W - M, y, f"{qty * unit:,}", f_body)
        if item in blur["items"]:
            blur_boxes += [ub, ab]
        y += LINE
    y += 4
    dashes(y)
    y += 18
    d.text((M, y), "합계", font=f_bold, fill=ink)
    tb = right(W - M, y, f"{total:,}", f_bold)
    if blur["total"]:
        blur_boxes.append((tb[0] - 4, tb[1], tb[2], tb[3] + 6))
    y += 60
    dashes(y)
    y += 18
    center(y, "(실습용 가상 영수증)", f_small, fill=(140, 140, 140))
    img = img.crop((0, 0, W, y + 50))
    H = img.height

    # 번진 것처럼: 해당 칸만 잘라 크게 흐린 뒤 다시 붙임
    for box in blur_boxes:
        region = img.crop(box)
        for _ in range(2):
            region = region.filter(ImageFilter.GaussianBlur(5))
        img.paste(region, box)

    # 감열지 느낌: 약한 얼룩
    rnd = random.Random(name)
    px = img.load()
    for _ in range(W * H // 40):
        x, yy = rnd.randrange(W), rnd.randrange(H)
        r, g, b = px[x, yy]
        k = rnd.randint(-10, 4)
        px[x, yy] = (max(0, min(255, r + k)), max(0, min(255, g + k)), max(0, min(255, b + k)))
    return img


def draw_campus():
    """캠퍼스 풍경 '일러스트' (사진 아님). 강사가 실제 사진으로 바꿔 넣기를 권장."""
    W, H = 960, 640
    img = Image.new("RGB", (W, H), (176, 214, 240))
    d = ImageDraw.Draw(img)
    for i in range(380):  # 하늘 그라데이션
        c = (176 + i // 10, 214 + i // 20, 240)
        d.line([(0, i), (W, i)], fill=c)
    d.ellipse([780, 50, 870, 140], fill=(255, 236, 160))
    for cx, cy in [(180, 90), (520, 70)]:
        for dx, r in [(0, 34), (40, 44), (85, 32)]:
            d.ellipse([cx + dx - r, cy - r, cx + dx + r, cy + r], fill=(250, 250, 252))
    d.rectangle([0, 380, W, H], fill=(128, 186, 104))  # 잔디
    # 건물 세 채
    for x0, w, h, col in [(60, 260, 230, (196, 120, 96)), (350, 300, 290, (214, 206, 190)), (680, 230, 200, (170, 120, 104))]:
        d.rectangle([x0, 400 - h, x0 + w, 400], fill=col, outline=(90, 70, 60), width=3)
        for wy in range(400 - h + 22, 380, 44):
            for wx in range(x0 + 20, x0 + w - 30, 46):
                d.rectangle([wx, wy, wx + 26, wy + 26], fill=(220, 236, 248), outline=(90, 90, 100))
    d.polygon([(350, 110), (500, 50), (650, 110)], fill=(120, 90, 80))
    d.rectangle([470, 330, 530, 400], fill=(100, 80, 70))
    # 길
    d.polygon([(430, H), (560, H), (520, 400), (480, 400)], fill=(214, 200, 170))
    # 나무
    for tx in [40, 300, 640, 900, 200, 760]:
        ty = 470 if tx in (200, 760) else 420
        d.rectangle([tx - 8, ty, tx + 8, ty + 70], fill=(110, 80, 50))
        d.ellipse([tx - 46, ty - 80, tx + 46, ty + 12], fill=(60, 140, 70))
    f = font(18)
    d.text((W - 230, H - 34), "(실습용 캠퍼스 일러스트)", font=f, fill=(40, 70, 40))
    return img


def to_jpeg(img):
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=90)
    data = buf.getvalue()
    assert data[:3] == b"\xff\xd8\xff", "JPEG 첫머리"
    assert base64.b64encode(data).decode().startswith("/9j/"), "base64 /9j/"
    return data


# ── 완성 코드 : 교안 코드 블록 그대로 (단계별로 이어 붙인 최종 상태) ──────
EX1 = r'''import base64

from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL = "gemini-3.8-flash"

client = genai.Client()

with open("data/campus.jpg", "rb") as f:
    image_bytes = f.read()

print("바이트 수:", len(image_bytes))
print("앞 3바이트:", image_bytes[:3])

image_data = base64.b64encode(image_bytes).decode()
print("base64 앞 20글자:", image_data[:20])

QUESTION = "이 사진에 무엇이 보이는지 세 문장으로 설명해 줘."

interaction = client.interactions.create(
    model=MODEL,
    input=[
        {"type": "text", "text": QUESTION},
        {"type": "image", "mime_type": "image/jpeg", "data": image_data},
    ],
)
print(interaction.output_text)
print("입력 토큰:", interaction.usage.total_input_tokens)
print("종류별:", interaction.usage.input_tokens_by_modality)

text_only = client.interactions.create(model=MODEL, input=QUESTION)
print(text_only.output_text)
print("이미지 없이 입력 토큰:", text_only.usage.total_input_tokens)
'''

EX2_HEAD = r'''import base64
from typing import Literal

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field

load_dotenv()

MODEL = "gemini-3.8-flash"

client = genai.Client()

PROMPT = "이 영수증을 읽어 줘. 보이는 글자만 옮기고, 흐리거나 가려진 값은 계산하거나 짐작하지 말고 null로 둬."


class Item(BaseModel):
    name: str = Field(description="품목 이름")
    quantity: int = Field(ge=1, description="수량")
    amount: int | None = Field(description="이 품목의 금액(단가 × 수량), 원 단위 정수. 읽을 수 없으면 null")


class Receipt(BaseModel):
    store: str | None = Field(description="가게 이름. 읽을 수 없으면 null")
    date: str | None = Field(description="결제 날짜, YYYY-MM-DD 형식. 읽을 수 없으면 null")
    category: Literal["식비", "카페", "도서·문구", "생활용품", "기타"] = Field(
        description="영수증 전체의 지출 분류. 편의점·식당 먹거리는 식비, 카페 음료·디저트는 카페"
    )
    items: list[Item] = Field(description="영수증에 적힌 품목 전부, 적힌 순서대로")
    total: int | None = Field(description="영수증에 인쇄된 합계 금액, 원 단위 정수. 읽을 수 없으면 null")


'''
EX2_SCHEMA_PRINT = "print(Receipt.model_json_schema())\n\n\n"
EX2_FUNC = r'''def analyze_receipt(image_bytes, mime_type="image/jpeg"):
    interaction = client.interactions.create(
        model=MODEL,
        input=[
            {"type": "text", "text": PROMPT},
            {"type": "image", "mime_type": mime_type, "data": base64.b64encode(image_bytes).decode()},
        ],
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": Receipt.model_json_schema(),
        },
    )
    return Receipt.model_validate_json(interaction.output_text)


'''
# ④에서 파일 이름을 receipt2_store.jpg로 바꾼 최종 상태
EX2_TAIL = r'''with open("data/receipts/receipt2_store.jpg", "rb") as f:
    receipt = analyze_receipt(f.read())
print(receipt)

print(f"{receipt.store} / {receipt.date} / {receipt.category}")
for item in receipt.items:
    print(f"- {item.name} × {item.quantity}: {item.amount}원")
print("총액:", receipt.total)
'''
EX2 = EX2_HEAD + EX2_SCHEMA_PRINT + EX2_FUNC + EX2_TAIL

CHECK_FUNC = r'''def check_receipt(receipt):
    problems = []
    if receipt.store is None or receipt.date is None:
        problems.append("가게 이름이나 날짜를 읽지 못함")
    if receipt.total is None:
        problems.append("총액을 읽지 못함")
    amounts = [item.amount for item in receipt.items]
    if None in amounts:
        problems.append("금액을 읽지 못한 품목이 있음")
    elif receipt.total is not None and sum(amounts) != receipt.total:
        problems.append(f"품목 합계 {sum(amounts):,}원과 총액 {receipt.total:,}원이 다름")
    return problems
'''
# 실습 3: 실습 2 복사 → 스키마 print 줄, analyze_receipt 아래 with open·print 줄 지우기 → 함수·시험 코드 추가
EX3 = EX2_HEAD + EX2_FUNC + CHECK_FUNC + r'''

wrong = Receipt(
    store="OO카페 정문점",
    date="2026-10-26",
    category="카페",
    items=[
        Item(name="아메리카노", quantity=2, amount=9000),
        Item(name="카페라떼", quantity=1, amount=8000),
    ],
    total=14000,
)
print(check_receipt(wrong))

files = ["receipt1_cafe.jpg", "receipt2_store.jpg", "receipt3_book.jpg", "receipt4_blur.jpg"]

for name in files:
    with open(f"data/receipts/{name}", "rb") as f:
        receipt = analyze_receipt(f.read())
    problems = check_receipt(receipt)
    print(name, receipt.total, "→", problems or "통과")
'''

APP = r'''import base64
import os
from typing import Literal

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field

load_dotenv()

MODEL = "gemini-3.8-flash"

SYSTEM_INSTRUCTION = """너는 영수증 사진을 가계부 데이터로 옮기는 도우미다.
이미지에 보이는 글자만 옮긴다. 흐리거나 가려진 값은 계산하거나 짐작하지 말고 null로 둔다."""


class Item(BaseModel):
    name: str = Field(description="품목 이름")
    quantity: int = Field(ge=1, description="수량")
    amount: int | None = Field(description="이 품목의 금액(단가 × 수량), 원 단위 정수. 읽을 수 없으면 null")


class Receipt(BaseModel):
    store: str | None = Field(description="가게 이름. 읽을 수 없으면 null")
    date: str | None = Field(description="결제 날짜, YYYY-MM-DD 형식. 읽을 수 없으면 null")
    category: Literal["식비", "카페", "도서·문구", "생활용품", "기타"] = Field(
        description="영수증 전체의 지출 분류. 편의점·식당 먹거리는 식비, 카페 음료·디저트는 카페"
    )
    items: list[Item] = Field(description="영수증에 적힌 품목 전부, 적힌 순서대로")
    total: int | None = Field(description="영수증에 인쇄된 합계 금액, 원 단위 정수. 읽을 수 없으면 null")


st.title("영수증 가계부")

if not os.getenv("GEMINI_API_KEY"):
    st.error("API 키가 없습니다. .env에 GEMINI_API_KEY를 넣고 앱을 다시 실행하세요.")
    st.stop()

client = genai.Client()

if "rows" not in st.session_state:
    st.session_state.rows = []


def analyze_receipt(image_bytes, mime_type):
    interaction = client.interactions.create(
        model=MODEL,
        system_instruction=SYSTEM_INSTRUCTION,
        input=[
            {"type": "text", "text": "이 영수증을 읽어 줘."},
            {"type": "image", "mime_type": mime_type, "data": base64.b64encode(image_bytes).decode()},
        ],
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": Receipt.model_json_schema(),
        },
    )
    return Receipt.model_validate_json(interaction.output_text)


''' + CHECK_FUNC + r'''

def error_message(error):
    code = getattr(error, "status_code", None)
    if code == 429:
        return "요청이 너무 많습니다. 잠시 뒤에 다시 보내 주세요."
    if code in (400, 401, 403):
        return "요청이 거절되었습니다. API 키를 확인하세요."
    if code == 404:
        return "모델을 찾을 수 없습니다. MODEL 이름을 확인하세요."
    if code is not None and code >= 500:
        return "Gemini 서버가 바쁩니다. 잠시 뒤에 다시 보내 주세요."
    return "답을 받지 못했습니다. 인터넷 연결을 확인하고 다시 보내 주세요."


def add_receipt(uploaded):
    try:
        receipt = analyze_receipt(uploaded.getvalue(), uploaded.type)
    except Exception as error:
        print(error)
        st.error(error_message(error))
        return

    problems = check_receipt(receipt)
    if problems:
        st.warning("확인 필요: " + " / ".join(problems))
    else:
        st.success(f"{receipt.store} {receipt.total:,}원을 추가했습니다.")

    for item in receipt.items:
        st.session_state.rows.append(
            {
                "날짜": receipt.date,
                "가게": receipt.store,
                "카테고리": receipt.category,
                "품목": item.name,
                "수량": item.quantity,
                "금액": item.amount,
                "확인": "확인 필요" if problems else "",
            }
        )


uploaded = st.file_uploader("영수증 사진", type=["jpg", "jpeg", "png"])
if uploaded:
    st.image(uploaded, width=300)

if uploaded and st.button("분석해서 추가"):
    add_receipt(uploaded)

if st.session_state.rows:
    table = pd.DataFrame(st.session_state.rows)
    st.dataframe(table)

    st.subheader("카테고리별 합계")
    st.dataframe(table.groupby("카테고리")["금액"].sum())

    st.download_button(
        "CSV 내려받기",
        table.to_csv(index=False).encode("utf-8-sig"),
        file_name="가계부.csv",
        mime="text/csv",
    )
'''

# app.py의 Item·Receipt·check_receipt는 실습 2·3 그대로 (교안 설명)
_classes = EX2_HEAD[EX2_HEAD.index("class Item"):]
assert _classes.strip() in APP and CHECK_FUNC in EX3 and CHECK_FUNC in APP

TEACHER = {
    "실습1_이미지질문.py": EX1,
    "실습2_영수증분석.py": EX2,
    "실습3_검증.py": EX3,
    "app.py": APP,
}

# ── 쓰기 ─────────────────────────────────────────────────────────────────
(DATA / "receipts").mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

(DATA / "campus.jpg").write_bytes(to_jpeg(draw_campus()))
for name in RECEIPTS:
    (DATA / "receipts" / name).write_bytes(to_jpeg(draw_receipt(name)))
for name, code in TEACHER.items():
    compile(code, name, "exec")
    (OUT / name).write_bytes(code.encode("utf-8"))

print("07_multimodal 생성 완료:", OUT)
print("  data/campus.jpg (일러스트)")
for name, v in RECEIPTS.items():
    print(f"  data/receipts/{name}: {v[0]} {v[1]} {v[2]} 품목 {len(v[3])} 합계 {v[4]:,}")
for name in TEACHER:
    print("  07_multimodal/" + name)
