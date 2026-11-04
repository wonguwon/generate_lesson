import base64
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
