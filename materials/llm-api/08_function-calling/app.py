import os

import streamlit as st
from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL = "gemini-3.8-flash"
TODAY = "2026-11-10"

SYSTEM_INSTRUCTION = f"""너는 OO대학교 캠퍼스 도우미다.
오늘은 {TODAY} 화요일이다.

[말투] 존댓말, 세 문장 이내로 짧게
[도구] 학식 메뉴와 도서관 빈자리는 반드시 도구로 조회한 결과로만 답한다
[규칙]
- 도구 결과에 없는 정보는 지어내지 말고 학교 홈페이지나 담당 부서에서 확인하라고 안내한다
- 캠퍼스 생활과 관계없는 질문에는 "캠퍼스 생활과 관련된 질문에만 답할 수 있습니다."라고 안내한다
"""

CAFETERIA_MENU = {
    "2026-11-09": {"점심": "제육볶음, 미역국", "저녁": "카레라이스, 계란국"},
    "2026-11-10": {"점심": "치킨마요덮밥, 우동", "저녁": "김치찌개, 계란말이"},
    "2026-11-11": {"점심": "돈가스, 크림수프", "저녁": "비빔밥, 된장국"},
}

LIBRARY_SEATS = {
    "중앙도서관": {"전체": 420, "사용 중": 343},
    "과학도서관": {"전체": 160, "사용 중": 131},
}


def get_cafeteria_menu(date):
    menu = CAFETERIA_MENU.get(date)
    if menu is None:
        return f"{date}에는 학생식당 식단이 없습니다."
    return f"{date} 학생식당 점심: {menu['점심']} / 저녁: {menu['저녁']}"


def get_library_seats(building):
    seats = LIBRARY_SEATS.get(building)
    if seats is None:
        return f"{building}: 없는 도서관 이름입니다. 조회할 수 있는 곳: {', '.join(LIBRARY_SEATS)}"
    left = seats["전체"] - seats["사용 중"]
    return f"{building} 열람실 빈자리 {left}석 / 전체 {seats['전체']}석"


MENU_TOOL = {
    "type": "function",
    "name": "get_cafeteria_menu",
    "description": "OO대학교 학생식당의 날짜별 점심·저녁 메뉴를 조회한다.",
    "parameters": {
        "type": "object",
        "properties": {
            "date": {"type": "string", "description": "조회할 날짜, YYYY-MM-DD 형식"},
        },
        "required": ["date"],
    },
}

SEATS_TOOL = {
    "type": "function",
    "name": "get_library_seats",
    "description": "OO대학교 도서관 열람실의 지금 빈자리 수를 조회한다.",
    "parameters": {
        "type": "object",
        "properties": {
            "building": {"type": "string", "description": "도서관 건물 이름. 예: 중앙도서관"},
        },
        "required": ["building"],
    },
}

TOOLS = [MENU_TOOL, SEATS_TOOL]

FUNCTIONS = {
    "get_cafeteria_menu": get_cafeteria_menu,
    "get_library_seats": get_library_seats,
}

TOOL_LABELS = {
    "get_cafeteria_menu": "학식 메뉴",
    "get_library_seats": "도서관 좌석",
}

st.title("캠퍼스 도우미")

if not os.getenv("GEMINI_API_KEY"):
    st.error("API 키가 없습니다. .env에 GEMINI_API_KEY를 넣고 앱을 다시 실행하세요.")
    st.stop()

client = genai.Client()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_id" not in st.session_state:
    st.session_state.last_id = None

if st.sidebar.button("대화 초기화"):
    st.session_state.messages = []
    st.session_state.last_id = None


def run_call(call):
    result = FUNCTIONS[call.name](**call.arguments)
    print(f"[함수 실행] {call.name}({call.arguments}) → {result}")
    return {"type": "function_result", "call_id": call.id, "name": call.name, "result": result}


def ask(question, previous_id=None):
    called = []
    interaction = client.interactions.create(
        model=MODEL,
        system_instruction=SYSTEM_INSTRUCTION,
        input=question,
        tools=TOOLS,
        previous_interaction_id=previous_id,
    )
    for _ in range(5):
        calls = [step for step in interaction.steps if step.type == "function_call"]
        if not calls:
            break
        results = []
        for call in calls:
            results.append(run_call(call))
            called.append(call.name)
        interaction = client.interactions.create(
            model=MODEL,
            system_instruction=SYSTEM_INSTRUCTION,
            input=results,
            tools=TOOLS,
            previous_interaction_id=interaction.id,
        )
    return interaction, called


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


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        for name in message.get("tools", []):
            st.caption(f"{TOOL_LABELS[name]} 조회함")
        st.write(message["content"])

question = st.chat_input("학식 메뉴나 도서관 빈자리를 물어보세요")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        try:
            with st.spinner("조회하는 중"):
                interaction, called = ask(question, st.session_state.last_id)
            st.session_state.last_id = interaction.id
            for name in called:
                st.caption(f"{TOOL_LABELS[name]} 조회함")
            st.write(interaction.output_text)
            st.session_state.messages.append(
                {"role": "assistant", "content": interaction.output_text, "tools": called}
            )
        except Exception as error:
            print(error)
            st.error(error_message(error))
