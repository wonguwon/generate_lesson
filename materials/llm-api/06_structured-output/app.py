import os
from typing import Literal

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel, Field

load_dotenv()

MODEL = "gemini-3.8-flash"

SYSTEM_INSTRUCTION = "너는 대학 강의평을 분석하는 도우미다. 강의평에 적힌 내용만 근거로 판단한다."


class ReviewAnalysis(BaseModel):
    course: str = Field(description="강의명")
    sentiment: Literal["긍정", "부정", "중립"] = Field(
        description="강의평 전체의 감성. 긍정과 부정이 섞여 있으면 더 강한 쪽, 비슷하면 중립"
    )
    score: int = Field(ge=1, le=5, description="만족도. 1 매우 불만족, 3 보통, 5 매우 만족")
    keywords: list[str] = Field(max_length=3, description="강의평의 핵심 키워드 1~3개")


st.title("강의평 분석기")

if not os.getenv("GEMINI_API_KEY"):
    st.error("API 키가 없습니다. .env에 GEMINI_API_KEY를 넣고 앱을 다시 실행하세요.")
    st.stop()

client = genai.Client()


def analyze(course, review):
    interaction = client.interactions.create(
        model=MODEL,
        system_instruction=SYSTEM_INSTRUCTION,
        input=f"강의명: {course}\n강의평: {review}",
        generation_config={"thinking_level": "low"},
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": ReviewAnalysis.model_json_schema(),
        },
    )
    return ReviewAnalysis.model_validate_json(interaction.output_text)


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


reviews = pd.read_csv("data/reviews.csv")
st.caption(f"강의평 {len(reviews)}건")

count = st.slider("분석할 강의평 수", 1, len(reviews), 5)

if st.button("분석 시작"):
    rows = reviews.head(count).to_dict("records")
    results = []
    progress = st.progress(0, text="분석 준비 중")

    for i, row in enumerate(rows, start=1):
        try:
            result = analyze(row["강의명"], row["강의평"])
        except Exception as error:
            print(error)
            st.error(f"{i}번째에서 멈춤: {error_message(error)}")
            break
        results.append(result.model_dump())
        progress.progress(i / count, text=f"{i}/{count}건 분석")

    if results:
        table = pd.DataFrame(results)
        st.dataframe(table)
        st.bar_chart(table["sentiment"].value_counts())
