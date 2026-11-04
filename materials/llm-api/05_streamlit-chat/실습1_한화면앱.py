from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL = "gemini-3.8-flash"

client = genai.Client()

st.title("Gemini에게 물어보기")
st.caption(f"마지막 실행: {datetime.now():%H:%M:%S}")

question = st.text_input("질문")

if st.button("보내기"):
    interaction = client.interactions.create(model=MODEL, input=question)
    st.write(interaction.output_text)
