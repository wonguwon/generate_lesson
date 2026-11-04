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
fig, ax = plt.subplots()
plt.show()
""")

md("""
* <b>type()</b>으로 두 변수에 무엇이 담겼는지 확인한다.
  * fig는 <b>Figure</b>, ax는 <b>Axes</b>다. 이름은 바꿔도 되지만, 보통 <b>fig</b>와 <b>ax</b>로 쓴다.
""")
code("""
print(type(fig))
print(type(ax))
""")

md("""
* <b>figsize=(가로, 세로)</b>: 종이 크기를 인치 단위로 정한다. 기본값은 (6.4, 4.8)이다.
  * 날짜처럼 가로로 긴 데이터는 종이를 가로로 넓게 만든다. 오늘은 카페 그래프를 모두 <b>(10, 4)</b>로 그린다.
""")
code("""
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
customers_by_month = cafe.groupby('year_month')['customers'].mean().round(2)
customers_by_month
""")

md("""
* 표를 그대로 선 그래프로 옮긴다. x에 <b>index</b>(월), y에 <b>values</b>(평균)를 넣는다.
  * <b>marker='o'</b>: 각 값 자리에 동그라미 점을 찍는다. 값이 12개뿐이라 점이 있어야 어느 달인지 보인다.
* 일부러 기본 크기 종이에 그려 본다. 아래 x축 글자 12개가 서로 겹친다.
""")
code("""
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
