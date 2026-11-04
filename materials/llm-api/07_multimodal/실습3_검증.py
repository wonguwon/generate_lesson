import base64
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


def analyze_receipt(image_bytes, mime_type="image/jpeg"):
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


def check_receipt(receipt):
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
