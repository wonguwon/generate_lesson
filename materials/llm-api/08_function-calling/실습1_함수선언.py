from dotenv import load_dotenv
from google import genai

load_dotenv()

MODEL = "gemini-3.8-flash"
TODAY = "2026-11-10"

SYSTEM_INSTRUCTION = f"너는 OO대학교 캠퍼스 도우미다. 오늘은 {TODAY} 화요일이다."

client = genai.Client()

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


print(get_cafeteria_menu("2026-11-11"))
print(get_library_seats("중앙도서관"))

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


def show(interaction):
    print("status:", interaction.status)
    print("steps:", [step.type for step in interaction.steps])
    for step in interaction.steps:
        if step.type == "function_call":
            print("function_call:", step.name, step.arguments, step.id)
    print("output_text:", repr(interaction.output_text))
    print()


interaction = client.interactions.create(
    model=MODEL,
    system_instruction=SYSTEM_INSTRUCTION,
    input="내일 점심 메뉴 알려 줘.",
    tools=TOOLS,
)
show(interaction)

interaction = client.interactions.create(
    model=MODEL,
    system_instruction=SYSTEM_INSTRUCTION,
    input="수강 정정 기간이 뭔지 한 문장으로 알려 줘.",
    tools=TOOLS,
)
show(interaction)

interaction = client.interactions.create(
    model=MODEL,
    system_instruction=SYSTEM_INSTRUCTION,
    input="오늘 저녁 메뉴랑 과학도서관 빈자리 알려 줘.",
    tools=TOOLS,
)
show(interaction)
