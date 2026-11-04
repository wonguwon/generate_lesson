"""1차시 강사용 노트북 생성: python build_01.py → 01_환경설정/01_환경설정_강사용.ipynb"""
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

OUT = Path(__file__).resolve().parent.parent / "01_환경설정" / "01_환경설정_강사용.ipynb"

cells = []
md = lambda s: cells.append(new_markdown_cell(s.strip("\n")))
code = lambda s: cells.append(new_code_cell(s.strip("\n")))

md("""
### <b>1강 개발 환경과 첫 그래프 - 설치 확인 · 커널 · 한글 폰트</b>

* 이 노트북은 VS Code에서 프로젝트 폴더의 <b>.venv</b> 커널을 고른 뒤에 실행한다.
* 먼저 노트북이 어떤 파이썬으로 실행되는지, 세 라이브러리가 설치되었는지 확인한다.
* 리스트 두 개로 첫 그래프를 그리고, 한글과 마이너스 기호가 깨지는 것을 직접 고친다.
""")

md("""
#### <b>1) 설치 확인</b>

* <b>커널(Kernel)</b>: 노트북의 코드를 실제로 실행하는 파이썬이다. 노트북 오른쪽 위에 지금 고른 커널 이름이 보인다.
* <b>sys.version</b>은 파이썬 버전, <b>sys.executable</b>은 지금 코드를 실행하는 파이썬 파일의 위치다.
  * 경로 안에 <b>.venv</b>가 보이면 프로젝트의 가상환경 커널을 고른 것이다.
  * 버전은 3.11 이상이면 된다. 숫자는 설치한 시점에 따라 다를 수 있다.
""")
code("""
import sys

print(sys.version)
print(sys.executable)
""")

md("""
* <b>import 라이브러리 as 별명</b>: 라이브러리를 불러오고, 긴 이름 대신 짧은 별명으로 부른다.
  * pandas는 <b>pd</b>, seaborn은 <b>sns</b>로 부르는 것이 널리 쓰는 관례다.
* <b>라이브러리.__version__</b>: 설치된 버전을 알려 준다. 오류 없이 버전이 나오면 설치가 끝난 것이다.
  * <b>ModuleNotFoundError</b>가 나오면 다른 커널을 골랐거나, 가상환경에 설치하지 않은 것이다.
""")
code("""
import pandas as pd
import matplotlib
import seaborn as sns

print('pandas', pd.__version__)
print('matplotlib', matplotlib.__version__)
print('seaborn', sns.__version__)
""")

md("""
#### <b>2) 첫 그래프</b>

* 그래프에 넣을 데이터는 리스트 두 개다. 요일은 x축, 기온은 y축에 놓는다.
  * 이 기온은 연습용으로 만든 가상의 값이다.
  * 두 리스트는 길이가 같아야 한다. 같은 자리의 값끼리 점 하나가 된다.
""")
code("""
days = ['월', '화', '수', '목', '금', '토', '일']
temps = [-5, -2, 1, 3, 0, -1, 2]

print(len(days), len(temps))
""")

md("""
* <b>matplotlib.pyplot</b>: 그래프를 그리는 함수를 모아 둔 모듈이다. 보통 <b>plt</b>라는 별명으로 부른다.
* <b>plt.plot(x, y)</b>: x와 y 값을 점으로 찍고 차례로 이어 선 그래프를 그린다.
* <b>plt.title('제목')</b>: 그래프 위에 제목을 단다. <b>plt.show()</b>: 그린 그래프를 화면에 보여 준다.
""")
code("""
import matplotlib.pyplot as plt

plt.plot(days, temps)
plt.title('이번 주 아침 기온')
plt.show()
""")

md("""
* 제목과 x축의 한글이 <b>네모(□)</b>로 보인다. 아래에 <b>Glyph ... missing from font(s) DejaVu Sans</b> 경고도 나온다.
  * matplotlib의 기본 폰트(DejaVu Sans)에는 한글 글자가 없기 때문이다.
* <b>plt.rcParams</b>: matplotlib의 기본 설정을 모아 둔 사전이다. <b>'font.family'</b>에 한글 폰트 이름을 넣으면 이후 그래프에 그 폰트가 쓰인다.
  * Windows는 <b>Malgun Gothic</b>(맑은 고딕), Mac은 <b>AppleGothic</b>을 쓴다. 둘 다 운영체제에 기본으로 들어 있다.
* <b>platform.system()</b>: 지금 운영체제 이름을 알려 준다. Windows는 'Windows', Mac은 'Darwin'이다.
  * 이 값으로 나눠 두면 같은 노트북을 Windows와 Mac 어디서 열어도 한글이 보인다.
""")
code("""
import platform

if platform.system() == 'Windows':
    plt.rcParams['font.family'] = 'Malgun Gothic'
else:
    plt.rcParams['font.family'] = 'AppleGothic'

plt.plot(days, temps)
plt.title('이번 주 아침 기온')
plt.show()
""")

md("""
* 이제 한글은 보이지만, y축 <b>-1부터 -5까지 눈금의 마이너스 기호</b>가 네모로 보이고 <b>Glyph 8722 (MINUS SIGN)</b> 경고가 나온다.
  * matplotlib은 축 눈금에 키보드의 하이픈(-)이 아닌 <b>유니코드 마이너스(−)</b>를 쓰는데, 이 폰트에는 그 글자가 없다.
* <b>plt.rcParams['axes.unicode_minus'] = False</b>: 축 눈금의 마이너스를 일반 하이픈(-)으로 바꾼다.
""")
code("""
plt.rcParams['axes.unicode_minus'] = False

plt.plot(days, temps)
plt.title('이번 주 아침 기온')
plt.show()
""")

md("""
* 한글 제목, 요일, 음수 눈금이 모두 바르게 보인다. 가장 낮은 날은 월요일(-5), 가장 높은 날은 목요일(3)이다.
* rcParams 설정은 <b>커널이 켜져 있는 동안만</b> 유지된다. 노트북을 새로 열거나 커널을 다시 시작하면 처음 상태로 돌아간다.
* 그래서 아래 셀을 <b>설정 셀</b>로 정하고, 다음 시간부터 모든 노트북의 첫 코드 셀로 실행한다.
  * pandas는 다음 시간부터 쓰므로 미리 함께 불러 둔다.
""")
code("""
import platform
import pandas as pd
import matplotlib.pyplot as plt

if platform.system() == 'Windows':
    plt.rcParams['font.family'] = 'Malgun Gothic'
else:
    plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False
""")

nb = new_notebook(cells=cells)
nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
nb.metadata["language_info"] = {"name": "python"}
nbformat.validate(nb)
OUT.parent.mkdir(parents=True, exist_ok=True)
nbformat.write(nb, OUT)
print(OUT)
