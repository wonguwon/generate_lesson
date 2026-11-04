"""3차시 강사용 노트북 생성: python build_03.py → 03_선그래프/03_선그래프_강사용.ipynb"""
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

OUT = Path(__file__).resolve().parent.parent / "03_선그래프" / "03_선그래프_강사용.ipynb"

cells = []
md = lambda s: cells.append(new_markdown_cell(s.strip("\n")))
code = lambda s: cells.append(new_code_cell(s.strip("\n")))

md("""
### <b>3강 Figure·Axes와 선 그래프 - 그래프의 구조 · plot · 제목과 범례</b>

* 그래프를 담는 종이(<b>Figure</b>)와 그 위의 칸(<b>Axes</b>)을 만들고, 칸에 그리는 <b>객체 방식</b>(<b>fig, ax</b>)을 익힌다.
* 카페의 일별 손님 수, 메뉴별 판매량, 2강에서 만든 월별 평균 표를 선 그래프로 옮긴다.
* 제목·축 이름·범례를 달아 그래프만 보고도 무엇을 그렸는지 알 수 있게 만든다.
""")

md("""
* 첫 코드 셀은 매 시간 실행하는 <b>설정 셀</b>이다. 1강에서 정한 그대로다.
""")
code("""
# keep
# 설명: 1강에서 정한 설정 셀 그대로다. 코드를 다시 설명하지 않고 실행만 한다. 출력은 없다.
# 설명: 뒤에서 쓰는 plt와 pd를 여기서 불러온다. 이 셀을 건너뛰면 다음 셀부터 NameError가 난다.
# 설명: 그래프 글자가 □로 나오면 이 셀을 실행했는지부터 확인하게 한다.
import platform
import pandas as pd
import matplotlib.pyplot as plt

if platform.system() == 'Windows':
    plt.rcParams['font.family'] = 'Malgun Gothic'
else:
    plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False
""")

md("""
* 오늘은 카페 데이터(<b>cafe_sales.csv</b>)만 쓴다. 2강처럼 date 열을 날짜로 읽는다.
  * 날짜로 읽어야 선 그래프의 x축이 날짜 순서와 간격대로 놓인다.
""")
code("""
# keep
# 설명: 노트북이 바뀌면 변수도 새로 시작한다. 2강에서 읽은 파일이지만 여기서 다시 읽어야 한다.
# 설명: 출력 (365, 14)는 365일, 14열이다. 아래 표는 이번에 쓸 6열만 고른 것이다.
# 설명: 표에서 3/1(토) 169명, 3/2(일) 157명이 3/3(월)에 485명으로 뛴다. 뒤에서 선이 촘촘한 이유이니 눈여겨보게 한다.
# 설명: FileNotFoundError가 나오면 노트북 위치를 본다. ../data는 03_선그래프 폴더의 한 칸 위에 있는 data 폴더다.
cafe = pd.read_csv('../data/cafe_sales.csv', parse_dates=['date'])
print(cafe.shape)
cafe[['date', 'customers', 'americano', 'latte', 'ade', 'tea']].head()
""")

# 1) ------------------------------------------------------------------
md("""
#### <b>1) 빈 Figure와 Axes 만들기</b>

* 1강에서는 <b>plt.plot()</b>, <b>plt.title()</b>처럼 <b>plt.</b>로 시작하는 함수로 그렸다. 이것을 <b>pyplot 방식</b>이라고 한다.
  * 1강의 요일별 기온 그래프를 그 방식으로 다시 그려 본다. 기온은 연습용 가상 값이다.
""")
code("""
# 설명: 새로운 코드가 아니다. 1강 방식을 기준으로 삼으려고 먼저 그대로 실행한다.
# 설명: 코드에 fig도 ax도 없고 모두 plt.로 시작하는 것을 확인시킨다. 뒤의 객체 방식과 비교할 지점이다.
# 설명: 실행 후 월요일 -5가 최저, 목요일 3이 최고인 것을 짚는다. 같은 그림이 다시 나올 때 비교하는 기준이다.
# 설명: days와 temps는 뒤 셀에서도 쓴다. 이 셀을 건너뛰면 뒤에서 NameError가 난다.
days = ['월', '화', '수', '목', '금', '토', '일']
temps = [-5, -2, 1, 3, 0, -1, 2]

plt.plot(days, temps)
plt.title('이번 주 아침 기온')
plt.show()
""")

md("""
* 이번 강부터는 그래프를 그리기 전에 <b>그릴 바탕</b>을 먼저 만든다.
  * <b>Figure</b>: 그래프 전체를 담는 종이(그림 한 장)다.
  * <b>Axes</b>: 종이 위에 x축·y축이 있는 그래프 한 칸이다. 선·막대·제목은 모두 Axes에 그린다.
* <b>fig, ax = plt.subplots()</b>: Figure 하나와 그 위의 Axes 하나를 만들어 두 변수에 나눠 담는다.
  * 아직 아무것도 그리지 않았으므로 빈 칸만 보인다. 축 눈금은 기본값 0~1이다.
""")
code("""
# 설명: 실행 전에 예고한다. 선 없이 빈 칸만 나오는 것이 정상이다.
# 설명: 등호 왼쪽에 변수가 둘인 모양을 낯설어한다. subplots()가 두 개를 돌려주고 fig, ax 순서로 받는 것이다.
# 설명: 실행 후 그림을 가리키며 나눈다. 바깥 여백까지 전체가 Figure, 테두리 안쪽이 Axes다.
fig, ax = plt.subplots()
plt.show()
""")

md("""
* <b>type()</b>으로 두 변수에 무엇이 담겼는지 확인한다.
  * fig는 <b>Figure</b>, ax는 <b>Axes</b>다. 이름은 바꿔도 되지만, 보통 <b>fig</b>와 <b>ax</b>로 쓴다.
""")
code("""
# 설명: 앞 셀에서 만든 fig와 ax를 그대로 쓴다. 앞 셀을 실행하지 않았으면 NameError가 난다.
# 설명: 출력의 긴 경로는 외우지 않는다. 줄 끝 단어 Figure와 Axes만 읽어 준다.
# 설명: 눈에 보이는 종이와 칸이 변수에 들어 있다는 것을 확인했다. 이후 ax.으로 시작하는 코드는 모두 이 칸에 내리는 명령이다.
print(type(fig))
print(type(ax))
""")

md("""
* <b>figsize=(가로, 세로)</b>: 종이 크기를 인치 단위로 정한다. 기본값은 (6.4, 4.8)이다.
  * 날짜처럼 가로로 긴 데이터는 종이를 가로로 넓게 만든다. 오늘은 카페 그래프를 모두 <b>(10, 4)</b>로 그린다.
""")
code("""
# 설명: 앞의 빈 칸과 모양을 비교한다. 앞은 기본값 6.4×4.8이고, 이번은 가로가 세로의 2.5배다.
# 설명: 괄호 안 순서는 (가로, 세로)다. 순서를 바꾸면 세로로 긴 종이가 나온다.
# 설명: 실행 후에도 여전히 빈 칸이다. 종이 크기만 바꾼 셀이다. 내용은 다음 셀부터 그린다.
fig, ax = plt.subplots(figsize=(10, 4))
plt.show()
""")

md("""
* 같은 기온 그래프를 <b>객체 방식</b>으로 다시 그린다. 만든 칸(ax)에 대고 그리는 방식이다.
  * <b>plt.plot</b> → <b>ax.plot</b>, <b>plt.title</b> → <b>ax.set_title</b>로 바뀐다. 제목·축 이름 함수 앞에는 <b>set_</b>이 붙는다.
* 결과 그림은 위의 pyplot 방식과 같다. 이 과정은 앞으로 <b>fig, ax</b> 방식으로 통일한다.
  * 칸이 여러 개일 때(5강) 어느 칸에 그릴지를 ax로 정확히 가리킬 수 있기 때문이다.
""")
code("""
# 설명: 위 pyplot 셀과 나란히 놓고 읽는다. plt.subplots 한 줄이 늘고, plot과 title 두 줄의 앞이 ax로 바뀌었다.
# 설명: 마지막 plt.show()는 그대로다. 모두 ax로 바뀌는 것이 아니라는 점을 짚는다.
# 설명: 막히기 쉬운 곳: set_을 빼고 ax.title('...')로 쓰면 TypeError가 난다.
# 설명: 실행 후 선 모양은 앞과 같고 -5와 3 위치도 그대로다. 달라진 것은 (6, 3)으로 정한 종이 크기뿐이다.
fig, ax = plt.subplots(figsize=(6, 3))
ax.plot(days, temps)
ax.set_title('이번 주 아침 기온')
plt.show()
""")

# 2) ------------------------------------------------------------------
md("""
#### <b>2) 일별 손님 수 선 그래프</b>

* <b>ax.plot(x, y)</b>: x와 y 값을 점으로 찍고 순서대로 이어 선을 그린다.
  * x에 날짜 열(<b>cafe['date']</b>), y에 손님 수 열(<b>cafe['customers']</b>)을 넣으면 365일의 손님 수가 한 줄로 이어진다.
* 시간에 따른 변화는 선 그래프로 본다. 선이 오르내리는 모양이 곧 흐름이다.
""")
code("""
# 설명: 앞 셀과 틀이 같다. days와 temps 자리에 열 두 개가 들어갔을 뿐이다.
# 설명: 실행 전에 예고한다. 값이 7개에서 365개로 늘어 선이 아주 빽빽해진다.
# 설명: 실행 후 큰 모양부터 본다. 높은 구간 둘과 낮은 구간 둘이 번갈아 나오는 것을 손으로 따라간다.
# 설명: 아직 제목과 축 이름이 없다. y축 숫자가 손님 수라는 것을 말로 알려 주고, 이름 붙이기는 5)로 넘긴다.
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(cafe['date'], cafe['customers'])
plt.show()
""")

md("""
* 그래프에서 읽을 것
  * 7·8월과 1·2월은 선이 낮게 깔린다. 방학이라 손님이 적다.
  * 선이 촘촘하게 오르내리는 것은 요일 때문이다. 평일에 높고 주말에 떨어진다.
  * 4월 말, 6월 초, 10월 말, 12월 초에 위로 튄 봉우리가 있다. 시험 주간이며, 가장 높은 값은 6월 시험 주간 이틀(6/10·6/11)의 685명이다.
  * 10월 초와 2월 중순에 선이 0까지 떨어진다. 2강에서 찾은 추석·설 휴무일이다.
* x축 눈금은 2025-03, 2025-05처럼 두 달 간격으로 저절로 놓인다. date를 날짜로 읽었기 때문이다.
* 2강의 필터로 손님 수가 최댓값인 행을 찾는다. <b>cafe['customers'].max()</b>는 열의 가장 큰 값이고(2강 mean()과 같은 방식), 이 값과 같은 행만 고른다.
  * 685명인 날이 이틀이라 두 행이 나온다. 둘 다 exam_week가 1이다.
""")
code("""
# 설명: 앞 그래프 맨 위 봉우리가 어느 날인지 표로 찾는다. 그래프는 모양을, 표는 정확한 날짜를 알려 준다.
# 설명: 코드가 길어 보이니 나눠 읽는다. max()로 값을 구하고, ==로 행을 고르고, 맨 뒤 [[...]]로 열을 고른다.
# 설명: 맨 뒤 대괄호가 두 겹인 곳에서 자주 막힌다. 열 네 개를 리스트로 넘겨서 그렇다.
# 설명: 출력 왼쪽 101, 102는 행 번호다. 6/10(화), 6/11(수) 모두 685명이다.
cafe[cafe['customers'] == cafe['customers'].max()][['date', 'weekday', 'exam_week', 'customers']]
""")

# 3) ------------------------------------------------------------------
md("""
#### <b>3) 메뉴별 판매량 겹쳐 그리기</b>

* 같은 ax에 <b>ax.plot</b>을 여러 번 부르면 선이 한 칸에 겹쳐 그려진다.
  * 선마다 색이 저절로 바뀐다(파랑 → 주황 → 초록 → 빨강).
* 아메리카노·라떼·에이드·차, 네 메뉴의 일별 판매 잔 수를 한 칸에 그린다.
""")
code("""
# 설명: plt.subplots()는 맨 위에 한 번만 쓴다. 칸 하나를 만들고 ax.plot만 네 번 부르는 구조다.
# 설명: ax.plot마다 subplots를 새로 부르면 종이가 네 장 생겨 겹쳐지지 않는다.
# 설명: 실행 후 y축을 본다. 앞 손님 수 그래프와 달리 단위가 잔이고, 맨 위 봉우리는 아메리카노 317잔이다.
# 설명: 범례가 없다. 초록 선이 무슨 메뉴인지 학생에게 물어본다. 코드를 봐야만 답할 수 있다는 것을 느끼게 한다.
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(cafe['date'], cafe['americano'])
ax.plot(cafe['date'], cafe['latte'])
ax.plot(cafe['date'], cafe['ade'])
ax.plot(cafe['date'], cafe['tea'])
plt.show()
""")

md("""
* 선 네 개가 그려졌다. 하지만 어느 색이 어느 메뉴인지 그래프만 보고는 알 수 없다.
  * 가장 위의 파란 선이 첫 번째로 그린 아메리카노라는 것은 코드를 봐야 안다.
* 그래프에 이름을 붙이는 방법(범례)은 5)에서 이 그래프에 이어서 단다.
""")

# 4) ------------------------------------------------------------------
md("""
#### <b>4) 월별 평균 손님 수(groupby 결과) 선 그래프</b>

* 일별 그래프는 요일 때문에 선이 너무 촘촘하다. 2강처럼 <b>groupby</b>로 월별 평균을 내면 큰 흐름만 남는다.
  * <b>year_month</b>는 '2025-03' 같은 글자라 가나다순으로 정렬해도 2025-03 → 2026-02 순서가 맞다. reindex가 필요 없다.
* 결과는 <b>Series</b>다. 왼쪽 이름표(<b>index</b>)가 월, 오른쪽 값(<b>values</b>)이 평균 손님 수다.
""")
code("""
# 설명: 3)의 메뉴 그래프는 잠시 두고 손님 수로 돌아온다. 365개 값을 12개로 줄이는 셀이다.
# 설명: 코드는 왼쪽부터 읽는다. year_month로 묶고, customers를 고르고, 평균을 내고, 소수 둘째 자리로 반올림한다.
# 설명: 출력 12행을 위에서 아래로 읽어 준다. 300대가 이어지다가 2025-07에 153.71로 떨어지는 지점을 눈여겨보게 한다.
# 설명: 평균에는 휴무일의 0도 들어 있다. 2025-10은 4일, 2026-02는 3일이 0이다. 값이 낮은 이유 중 하나다.
customers_by_month = cafe.groupby('year_month')['customers'].mean().round(2)
customers_by_month
""")

md("""
* 표를 그대로 선 그래프로 옮긴다. x에 <b>index</b>(월), y에 <b>values</b>(평균)를 넣는다.
  * <b>marker='o'</b>: 각 값 자리에 동그라미 점을 찍는다. 값이 12개뿐이라 점이 있어야 어느 달인지 보인다.
* 일부러 기본 크기 종이에 그려 본다. 아래 x축 글자 12개가 서로 겹친다.
""")
code("""
# 설명: 앞 셀의 표가 그대로 선이 된다. 점 12개가 표의 12행과 하나씩 대응한다.
# 설명: index와 values 뒤에는 괄호가 없다. index()처럼 괄호를 붙이면 TypeError가 난다.
# 설명: 실행 후 x축을 가리킨다. 2025-03과 2025-04 글자가 붙어 읽히지 않는다. 코드 오류가 아니라 종이가 좁은 것이다.
# 설명: y축 맨 아래 눈금은 150이고 0에서 시작하지 않는다. 낮은 점이 0에 가깝다고 오해하지 않게 말해 둔다.
fig, ax = plt.subplots()
ax.plot(customers_by_month.index, customers_by_month.values, marker='o')
plt.show()
""")

md("""
* 종이를 가로로 넓히면(<b>figsize=(10, 4)</b>) 글자 사이에 자리가 생겨 겹치지 않는다.
  * 글자를 기울이거나 눈금 간격을 바꾸는 방법은 5강에서 다룬다.
* 그래프에서 읽을 것
  * 2025-04가 381.37명으로 가장 높고, 2026-02가 125.79명으로 가장 낮다.
  * 7·8월과 1·2월에 계단처럼 떨어졌다가 9월에 다시 오른다. 학기와 방학의 흐름이 일별 그래프보다 또렷하다.
""")
code("""
# 설명: 앞 셀과 달라진 곳은 첫 줄의 figsize 하나뿐이다. 실행 전에 그곳만 가리킨다.
# 설명: 실행 후 앞 그래프에서 겹치던 x축 글자가 모두 읽히는지 함께 확인한다.
# 설명: 뚝 떨어지는 두 구간을 숫자로 짚는다. 2025-06 323.17 → 2025-07 153.71, 2025-12 294.61 → 2026-01 143.74다.
# 설명: 둘 다 절반 아래로 줄었고, 2025-09는 339.13으로 되돌아온다.
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(customers_by_month.index, customers_by_month.values, marker='o')
plt.show()
""")

# 5) ------------------------------------------------------------------
md("""
#### <b>5) 메뉴별 판매량 그래프에 제목·축 이름·범례 달기</b>

* 3)의 메뉴별 그래프에 이름을 붙인다. 그래프만 보고도 무엇을 그렸는지 알 수 있어야 한다.
  * <b>ax.set_title('제목')</b>: 그래프 위 제목
  * <b>ax.set_xlabel('x축 이름')</b>, <b>ax.set_ylabel('y축 이름')</b>: 축 이름. 단위까지 쓴다(예: 판매량(잔)).
* <b>ax.plot(..., label='이름')</b>: 선마다 이름표를 붙인다.
* <b>ax.legend()</b>: 이름표를 모아 <b>범례</b>(어느 색이 무엇인지 알려 주는 상자)를 그린다.
  * label 없이 legend()만 부르면 범례가 비어 있고 "No artists with labels found" 경고가 나온다.
""")
code("""
# 설명: 3)의 코드에서 바뀐 곳만 설명한다. plot 네 줄에 label이 붙었고, set_ 세 줄과 legend 한 줄이 늘었다.
# 설명: 순서에 주의한다. ax.legend()는 plot보다 뒤에 둔다. 먼저 부르면 모을 이름표가 없다.
# 설명: 실행 후 3) 그래프와 비교한다. 선은 같고 제목, 축 이름, 범례만 늘었다.
# 설명: 3)에서 물어본 초록 선이 에이드라는 것을 범례로 확인한다. 코드를 보지 않고도 답이 나온다.
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(cafe['date'], cafe['americano'], label='아메리카노')
ax.plot(cafe['date'], cafe['latte'], label='라떼')
ax.plot(cafe['date'], cafe['ade'], label='에이드')
ax.plot(cafe['date'], cafe['tea'], label='차')
ax.set_title('메뉴별 일별 판매량')
ax.set_xlabel('날짜')
ax.set_ylabel('판매량(잔)')
ax.legend()
plt.show()
""")

md("""
* 범례 위치는 <b>loc</b>로 정한다. 기본값 <b>'best'</b>는 선을 가장 적게 가리는 자리를 저절로 고른다. 위 그래프에서는 오른쪽 위였다.
  * 자주 쓰는 값: <b>'upper right'</b>(오른쪽 위), <b>'upper left'</b>(왼쪽 위), <b>'upper center'</b>(가운데 위), <b>'lower right'</b>(오른쪽 아래)
  * <b>loc='upper center'</b>로 바꾸면 범례가 가운데 위(7월 말~9월 말 위쪽)로 옮겨 간다. 바로 아래 9월 초 봉우리와 닿지 않는지 본다.
  * 범례가 선을 가리면 loc를 바꿔 빈 자리로 옮긴다.
* 그래프에서 읽을 것
  * 거의 모든 날 아메리카노(파랑)가 맨 위에 있다. 영업한 358일 중 341일이고, 라떼와 같은 하루(6/21)까지 넣으면 342일이다.
  * 여름방학에는 에이드(초록)가 라떼(주황)보다 위, 겨울방학에는 라떼가 에이드보다 위에 있다.
""")
code("""
# 설명: 앞 셀과 달라진 곳은 맨 아래 ax.legend(loc='upper center') 한 줄뿐이다.
# 설명: loc 값은 정해진 글자다. 철자가 틀리거나 upper와 center 사이 공백이 빠지면 ValueError가 난다.
# 설명: 실행 후 범례가 오른쪽 위에서 가운데 위로 옮겨 간 것을 확인한다. 7·8월은 선이 낮아 그 위가 비어 있다.
# 설명: 여름 구간에서 초록이 주황 위, 1·2월 구간에서 주황이 초록 위인 것을 손으로 따라간다. 다음 셀에서 숫자로 확인한다.
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(cafe['date'], cafe['americano'], label='아메리카노')
ax.plot(cafe['date'], cafe['latte'], label='라떼')
ax.plot(cafe['date'], cafe['ade'], label='에이드')
ax.plot(cafe['date'], cafe['tea'], label='차')
ax.set_title('메뉴별 일별 판매량')
ax.set_xlabel('날짜')
ax.set_ylabel('판매량(잔)')
ax.legend(loc='upper center')
plt.show()
""")

md("""
* 방학별로 라떼와 에이드 판매 합계를 숫자로 확인한다. 그래프에서 본 순서와 같다.
  * 여름방학은 에이드 3,552잔 > 라떼 1,711잔, 겨울방학은 라떼 2,903잔 > 에이드 798잔이다.
* 오늘의 순서를 정리하면 <b>종이(Figure) → 칸(Axes) → 그리기(plot) → 이름 붙이기(제목·축 이름·범례)</b>다.
""")
code("""
# 설명: 앞 그래프에서 눈으로 본 순서를 숫자로 확인한다. 이번에는 평균이 아니라 sum()으로 합계를 낸다.
# 설명: reindex는 2강에서 쓴 방법이다. 빼면 period가 글자 순서로 나와 학기 흐름이 어긋난다.
# 설명: 1학기 9,347 > 8,719, 2학기 8,650 > 7,454로 학기 중에도 라떼가 많다. 네 행 중 에이드가 앞서는 곳은 여름방학뿐이다.
# 설명: 3강의 마지막 코드 셀이다. 범주 비교의 막대, 관계를 보는 산점도, 분포를 보는 히스토그램은 4강에서 다룬다고 예고한다.
period_order = ['1학기', '여름방학', '2학기', '겨울방학']
cafe.groupby('period')[['latte', 'ade']].sum().reindex(period_order)
""")

nb = new_notebook(cells=cells)
nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
nb.metadata["language_info"] = {"name": "python"}
nbformat.validate(nb)
OUT.parent.mkdir(parents=True, exist_ok=True)
nbformat.write(nb, OUT)
print(OUT)
