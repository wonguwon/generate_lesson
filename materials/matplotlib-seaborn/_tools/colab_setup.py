"""모든 노트북이 함께 쓰는 Colab 준비 셀. build_NN.py가 불러 쓴다.

데이터를 내려받을 브랜치는 DATA_REF 한 곳에서 정한다.
"""
DATA_REF = "feature/lesson-subagents"
DATA_URL = f"https://raw.githubusercontent.com/wonguwon/generate_lesson/{DATA_REF}/materials/matplotlib-seaborn/data"

PREPARE_MD = """
* 맨 위 코드 셀은 <b>준비 셀</b>이다. 한글 폰트를 설치해 등록하고, 실습 데이터를 <b>data</b> 폴더에 내려받는다.
  * 내용은 고치지 않고 실행만 한다. 출력에 CSV 파일 이름 두 개가 보이면 끝난 것이다.
  * 세션이 끊겨도 입력한 코드는 남아 있다. 이어서 할 셀을 선택하고 <b>런타임 › 이전 셀 실행</b>을 누르면 준비 셀부터 다시 실행된다.
* 나머지 코드 칸은 강의를 따라 입력한다. 주석(#)은 입력하지 않아도 되고, 앞 셀과 비슷한 코드는 복사해 고친다.
"""

PREPARE = f"""
# keep
# 나눔고딕 폰트를 설치한다
!apt-get -qq install -y fonts-nanum > /dev/null
# 실습 데이터를 data 폴더에 내려받는다
!mkdir -p data
!wget -q -nc -P data {DATA_URL}/students.csv {DATA_URL}/cafe_sales.csv
# 설치한 폰트를 Matplotlib에 등록한다
from matplotlib import font_manager
font_manager.fontManager.addfont('/usr/share/fonts/truetype/nanum/NanumGothic.ttf')
# 내려받은 파일을 확인한다
!ls data
"""
