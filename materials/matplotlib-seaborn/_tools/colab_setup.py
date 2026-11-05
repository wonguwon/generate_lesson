"""모든 노트북이 함께 쓰는 Colab 준비 셀. build_NN.py가 불러 쓴다."""

PREPARE_MD = """
* 맨 위 코드 셀은 <b>준비 셀</b>이다. 구글 드라이브를 연결해 실습 폴더로 이동하고, 한글 폰트를 설치해 등록한다.
  * 구글 드라이브에 <b>데이터_시각화_실습</b> 폴더를 만들고, 그 안에 <b>data</b> 폴더를 올려 둔 뒤 실행한다.
  * 내용은 고치지 않고 실행만 한다. 드라이브 접근을 묻는 창이 뜨면 허용한다. 출력에 CSV 파일 이름 두 개가 보이면 끝난 것이다.
  * 세션이 끊겨도 입력한 코드는 남아 있다. 이어서 할 셀을 선택하고 <b>런타임 › 이전 셀 실행</b>을 누르면 준비 셀부터 다시 실행된다.
* 나머지 코드 칸은 강의를 따라 입력한다. 주석(#)은 입력하지 않아도 되고, 앞 셀과 비슷한 코드는 복사해 고친다.
"""

PREPARE = """
# keep
# 1. 구글 드라이브 연결
from google.colab import drive
drive.mount('/content/drive')

# 2. 실습 폴더로 기본 작업 위치 이동 (폴더명 변경 필요)
import os
os.chdir('/content/drive/MyDrive/데이터_시각화_실습')

# 3. 현재 위치 확인 (설정한 폴더 경로가 출력됨)
print("현재 작업 폴더:", os.getcwd())

# 4. 나눔고딕 폰트를 설치하고 Matplotlib에 등록
!apt-get -qq install -y fonts-nanum > /dev/null
from matplotlib import font_manager
font_manager.fontManager.addfont('/usr/share/fonts/truetype/nanum/NanumGothic.ttf')

# 5. 실습 데이터 확인 (CSV 파일 이름 두 개가 출력됨)
!ls data
"""
