import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GEMINI_API_KEY")

if key:
    print("키를 불러왔습니다. 글자 수:", len(key))
else:
    print("키가 없습니다. .env 파일의 위치와 이름을 확인하세요.")
