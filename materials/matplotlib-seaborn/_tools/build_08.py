"""8차시 강사용 노트북 생성: python build_08.py → 08_관계추세/08_관계추세_강사용.ipynb

regplot·lmplot의 연한 띠와 lineplot의 띠는 부트스트랩 95% 신뢰구간이라 seed를 주지 않으면 실행마다 조금 달라진다.
선(회귀선·평균선) 자체는 매번 같다. 기울기·상관계수·평균은 data_facts.md와 맞춘다.
lmplot에 ax=를 넣으면 TypeError가 나므로 오류 셀은 만들지 않고 마크다운에 문구만 적는다(오류 셀 0개 유지).
"""
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

OUT = Path(__file__).resolve().parent.parent / "08_관계추세" / "08_관계추세_강사용.ipynb"

cells = []
md = lambda s: cells.append(new_markdown_cell(s.strip("\n")))
code = lambda s: cells.append(new_code_cell(s.strip("\n")))

md("""
### <b>8강 관계와 추세 그래프 - scatterplot · regplot · lmplot · lineplot</b>

* <b>scatterplot</b>은 두 수치의 관계를 점으로 그리고, 세 번째 변수를 <b>hue</b>(색)와 <b>size</b>(점 크기)로 더한다. 4강 기온-에이드 산점도의 두 갈래를 색으로 나눠 본다.
* <b>regplot</b>·<b>lmplot</b>은 점 위에 회귀선(추세선)을 긋고, <b>corr()</b>로 구한 <b>상관계수</b>가 그 관계의 방향과 강도를 숫자로 보여 준다. 추세선은 방향을 보여 줄 뿐 원인을 말하지 않는다.
* <b>lineplot</b>은 x값마다 값이 여러 개면 평균선과 신뢰구간 띠를 함께 그린다. 일별 값의 출렁임은 <b>rolling(7).mean()</b>(7일 이동평균)으로 걸러 추세만 남긴다.
""")

md("""
* 첫 코드 셀은 6강에서 정한 <b>설정 셀</b> 그대로다.
  * <b>sns.set_theme(...)</b>에 한글 폰트와 마이너스 설정을 함께 넘긴다. 그래프 글자가 깨지면 이 셀을 다시 실행한다.
""")
code("""
# keep
# 설명: 6강에서 정한 설정 셀 그대로라 새로 설명할 것이 없다. 실행하고 넘어간다. 출력은 없다.
# 설명: 노트북을 새로 열면 커널이 비어 있으니 이 셀부터 실행해야 한다고 짚는다.
# 설명: 이후 셀에서 sns나 plt가 없다는 NameError가 나면 이 셀을 건너뛴 것이다.
import platform
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

if platform.system() == 'Windows':
    font_name = 'Malgun Gothic'
else:
    font_name = 'AppleGothic'
sns.set_theme(style='whitegrid', font=font_name, rc={'axes.unicode_minus': False})
""")

md("""
* 오늘은 두 파일을 모두 쓴다. 2강과 같은 방법으로 읽는다.
  * <b>students</b>: 학생 300명의 생활 습관 설문(가상), 학생 1명 = 1행
  * <b>cafe</b>: 캠퍼스 카페 1년 일별 판매(가상), 하루 = 1행
* 범주 순서 리스트도 7강과 같이 미리 만들어 둔다.
""")
code("""
# keep
# 설명: 출력 (300, 12) (365, 14)로 두 표가 제대로 읽혔는지만 확인한다. 300명, 365일이다.
# 설명: parse_dates=['date']가 있어야 date가 날짜로 읽힌다. 4)의 일별 lineplot x축에서 쓰인다.
# 설명: major_order, period_order는 뒤 셀의 hue_order, col_order에 쓰인다. 출력은 없다.
# 설명: FileNotFoundError가 나면 ../data 경로가 안 맞는 것이다. 노트북 위치부터 확인하게 한다.
students = pd.read_csv('../data/students.csv')
cafe = pd.read_csv('../data/cafe_sales.csv', parse_dates=['date'])
print(students.shape, cafe.shape)

major_order = ['공학', '자연과학', '사회과학', '인문', '예체능']
weekday_order = ['월', '화', '수', '목', '금', '토', '일']
period_order = ['1학기', '여름방학', '2학기', '겨울방학']
""")

# 1) ------------------------------------------------------------------
md("""
#### <b>1) 전공별 색을 넣은 공부 시간-점수 산점도</b>

* 4강에서는 <b>ax.scatter(x값, y값)</b>에 두 열의 값을 꺼내 넘겼다.
* <b>sns.scatterplot(data=표, x='열', y='열')</b>: 표와 열 이름만 넘기면 한 행을 점 하나로 찍는다.
  * 4강의 <b>s</b>(점 크기)·<b>alpha</b>(투명도)도 그대로 넘길 수 있다.
  * 다른 Seaborn 함수처럼 <b>ax=</b>로 그릴 칸을 정하고, 축 이름은 열 이름이 저절로 붙는다.
* 두 방법을 1×2 칸에 나란히 그려 비교한다.
""")
code("""
# 설명: 코드 두 줄을 비교하게 한다. ax.scatter는 값을 꺼내 넘기고, sns.scatterplot은 표와 열 이름만 넘긴다.
# 설명: 실행 후 두 칸의 점 위치가 같은 것을 확인한다. 오른쪽 점이 조금 작고 연해 보이는 것은 Seaborn 기본 테두리가 흰색이라서다.
# 설명: 왼쪽은 축 이름이 없고 오른쪽은 x축에 study_hours가 붙었다.
# 설명: 오른쪽 y축 이름은 보이지 않는다. sharey=True로 왼쪽 눈금을 같이 쓰는 칸이라 Seaborn이 숨긴 것이다.
fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True, layout='constrained')
axes[0].scatter(students['study_hours'], students['exam_score'], s=15, alpha=0.5)
axes[0].set_title('ax.scatter')
sns.scatterplot(data=students, x='study_hours', y='exam_score', s=15, alpha=0.5, ax=axes[1])
axes[1].set_title('sns.scatterplot')
plt.show()
""")

md("""
* 두 그래프의 점 300개는 같은 자리에 찍힌다. 오른쪽 칸에는 study_hours·exam_score 축 이름이 저절로 붙었다.
* 점 무리가 왼쪽 아래에서 오른쪽 위로 기운다(4강). 이 점들에 <b>세 번째 변수</b>를 더해 본다.
* <b>hue='major'</b>: 전공마다 점 색을 다르게 칠한다(6·7강의 hue와 같다).
  * <b>hue_order=major_order</b>: 범례와 색을 공학 → 예체능 순서로 놓는다. 빼면 표에 처음 나온 순서다.
""")
code("""
# 설명: 앞 셀의 산점도에 hue와 hue_order를 더한 것이 핵심이다. 범례는 따로 부르지 않아도 저절로 생긴다.
# 설명: s를 뺐으므로 점이 앞 셀보다 크다. 범례는 점이 적은 오른쪽 아래에 놓인다.
# 설명: 실행 후 전공 평균을 곁들여 읽는다. 공부 시간 평균은 공학 18.16시간, 예체능 6.28시간이다.
fig, ax = plt.subplots(figsize=(8, 5))
sns.scatterplot(data=students, x='study_hours', y='exam_score',
                hue='major', hue_order=major_order, alpha=0.7, ax=ax)
ax.set_title('전공별 공부 시간과 시험 점수')
ax.set_xlabel('주간 공부 시간(시간)')
ax.set_ylabel('시험 점수(점)')
plt.show()
""")

md("""
* 그래프에서 읽을 것
  * 공학 점이 오른쪽(공부 시간이 긴 쪽)에 많이 퍼져 있고, 예체능 점은 왼쪽 10시간 아래에 몰려 있다. 6·7강 박스플롯에서 본 공부 시간 차이가 산점도에서도 보인다.
  * 전공이 달라도 오른쪽 위로 기우는 방향은 같다.
* <b>size='part_time_hours'</b>: 주간 아르바이트 시간이 길수록 점을 크게 그린다. 이제 한 그래프에 변수가 네 개(x·y·색·크기)다.
  * 범례가 전공 다섯 줄과 크기 여섯 줄로 길어진다. <b>sns.move_legend(ax, 'upper left', bbox_to_anchor=(1, 1))</b>로 범례를 그래프 바깥 오른쪽 위로 옮겨 점을 가리지 않게 한다.
""")
code("""
# 설명: 앞 셀과 달라진 핵심은 size='part_time_hours'와 move_legend 한 줄이다.
# 설명: move_legend의 'upper left'는 범례의 어느 모서리를 맞출지, (1, 1)은 그 모서리를 둘 축의 오른쪽 위다. 둘을 헷갈리기 쉽다.
# 설명: 실행 후 범례 part_time_hours 쪽을 읽는다. 0시간도 사라지지 않고 작은 점으로 찍힌다.
# 설명: 아르바이트 0시간 학생이 112명(37.3%)이라 작은 점이 많다.
fig, ax = plt.subplots(figsize=(9, 5))
sns.scatterplot(data=students, x='study_hours', y='exam_score',
                hue='major', hue_order=major_order, size='part_time_hours', alpha=0.6, ax=ax)
sns.move_legend(ax, 'upper left', bbox_to_anchor=(1, 1))
ax.set_title('전공별 공부 시간과 시험 점수 (점 크기 = 아르바이트 시간)')
ax.set_xlabel('주간 공부 시간(시간)')
ax.set_ylabel('시험 점수(점)')
plt.show()
""")

md("""
* 큰 점(아르바이트를 오래 하는 학생)이 왼쪽에 조금 더 많다. 아르바이트 시간과 공부 시간은 약한 음의 관계다(아래 2)에서 숫자로 확인).
* 하지만 색과 크기를 함께 읽기는 어렵다. 크기는 차이를 눈으로 비교하기 힘들고, 점이 커질수록 서로 가린다.
  * 산점도에 더하는 변수는 <b>두 개(색 하나, 크기 하나)까지</b>만 권한다. 하나로 충분하면 하나만 쓴다.

* 이제 4강의 기온-에이드 산점도로 돌아간다. 10°C 무렵부터 점이 위아래 두 갈래로 벌어졌고, 위 갈래는 학기 평일, 아래 갈래는 주말·방학이라고 읽었다.
* 이것을 색으로 확인하려면 hue에 넣을 열이 필요하다. period(학사 기간) 열은 학기 주말도 '1학기'·'2학기'라서 두 갈래와 딱 맞지 않는다.
* 2강의 <b>.loc</b>으로 새 열 <b>day_type</b>을 만든다.
  * 먼저 모든 날을 '주말·방학'으로 채운다.
  * period가 1학기·2학기이고(<b>isin</b>) 요일이 토·일이 아닌(<b>~</b>, 조건 뒤집기) 날만 '학기 평일'로 바꾼다.
""")
code("""
# 설명: 두 단계로 읽어 준다. 첫 줄은 모든 행을 같은 값으로 채우고, 둘째 줄은 조건에 맞는 행만 덮어쓴다.
# 설명: .loc[조건, 열] = 값 형태다. 쉼표 앞이 고를 행, 뒤가 바꿀 열이다.
# 설명: 마지막 줄이 값이라 print 없이 출력된다. 205와 160을 더하면 365가 되는지 본다.
# 설명: 이 셀을 건너뛰면 뒤 셀들이 day_type 열을 찾지 못해 오류가 난다.
cafe['day_type'] = '주말·방학'
cafe.loc[cafe['period'].isin(['1학기', '2학기']) & ~cafe['weekday'].isin(['토', '일']), 'day_type'] = '학기 평일'
day_type_order = ['학기 평일', '주말·방학']

cafe['day_type'].value_counts()
""")

md("""
* 학기 평일 160일, 주말·방학 205일이다.
* hue를 period로 준 그래프와 day_type으로 준 그래프를 1×2로 나란히 그려, 어느 열이 두 갈래를 나누는지 비교한다.
""")
code("""
# 설명: 실행 전에 묻는다. 어느 쪽 칸에서 위 갈래와 아래 갈래가 한 색씩 나뉠까.
# 설명: 왼쪽 칸은 방학 색부터 본다. 겨울방학은 왼쪽 아래, 여름방학은 오른쪽 아래 갈래에 모여 있다.
# 설명: 오른쪽 칸에서 바닥 0의 점을 찾게 한다. 15~18°C 근처에 넷, 1~3°C 근처에 셋이다.
# 설명: set_ylabel은 axes[0]에만 준다. sharey=True라 오른쪽 칸 y축 이름은 어차피 보이지 않는다.
fig, axes = plt.subplots(1, 2, figsize=(12, 4), sharey=True, layout='constrained')
sns.scatterplot(data=cafe, x='avg_temp', y='ade', hue='period', hue_order=period_order,
                s=15, alpha=0.6, ax=axes[0])
axes[0].set_title("hue='period'")
sns.scatterplot(data=cafe, x='avg_temp', y='ade', hue='day_type', hue_order=day_type_order,
                s=15, alpha=0.6, ax=axes[1])
axes[1].set_title("hue='day_type'")
axes[0].set_xlabel('일 평균 기온(°C)')
axes[1].set_xlabel('일 평균 기온(°C)')
axes[0].set_ylabel('에이드 판매량(잔)')
plt.show()
""")

md("""
* 그래프에서 읽을 것
  * 왼쪽(period): 1학기·2학기 색 점이 위 갈래와 아래 갈래에 모두 있다. 학기 주말이 아래 갈래에 섞여서다.
  * 오른쪽(day_type): 위 갈래는 거의 학기 평일 색, 아래 갈래는 거의 주말·방학 색으로 깔끔하게 나뉜다.
  * 바닥 0에 붙은 점 7개는 휴무일이다. 추석 10/6~10/8 세 점은 평일이라 학기 평일 색, 10/5(일)과 설 연휴 세 점은 주말·방학 색이다.
* hue로 나눌 열은 "점 무리를 가르는 것이 무엇인가"를 생각해서 고른다. 맞는 열이 없으면 이렇게 만들어 쓴다.
""")

# 2) ------------------------------------------------------------------
md("""
#### <b>2) 공부 시간과 점수 regplot + 상관계수</b>

* <b>회귀선</b>: 점들을 가장 잘 지나가도록 그은 직선. 점 무리가 기우는 방향을 선 하나로 보여 준다. 추세선이라고도 한다.
* <b>sns.regplot(data=표, x='열', y='열')</b>: 산점도를 찍고 그 위에 회귀선을 긋는다.
  * 선 둘레의 연한 띠는 회귀선의 <b>95% 신뢰구간</b>이다. 7강 barplot의 오차 막대와 같은 뜻으로, 전체 데이터의 선이 있을 법한 범위다. 데이터를 다시 뽑았을 때 선이 얼마나 흔들리는지로 구한다. 부트스트랩으로 구해서 실행마다 띠가 조금 달라진다.
  * 점 모양은 <b>scatter_kws={'s': 15, 'alpha': 0.5}</b>처럼 사전(dict)으로 넘긴다. 점과 선 두 가지를 그리는 함수라서 점에만 줄 설정을 따로 묶는다.
""")
code("""
# 설명: scatter_kws로 묶는 이유를 실행 전에 말한다. regplot에 s=15를 바로 넣으면 TypeError가 난다.
# 설명: 실행 후 선 양 끝을 짚는다. 0시간 쪽은 약 60점이고 40시간 쪽은 100점을 넘는다.
# 설명: exam_score 최댓값은 100이다. 직선은 상한을 모르므로 선이 넘어간다. 실제 점수가 아니다.
# 설명: 학생 화면의 띠가 강사 화면과 조금 달라도 오류가 아니다. 선은 같다.
fig, ax = plt.subplots(figsize=(8, 5))
sns.regplot(data=students, x='study_hours', y='exam_score', scatter_kws={'s': 15, 'alpha': 0.5}, ax=ax)
ax.set_title('공부 시간과 시험 점수 (회귀선)')
ax.set_xlabel('주간 공부 시간(시간)')
ax.set_ylabel('시험 점수(점)')
plt.show()
""")

md("""
* 회귀선이 오른쪽 위로 올라간다. 공부 시간이 길수록 점수가 높은 경향이다.
  * 선의 기울기는 약 1.12다. 공부 시간이 1시간 길면 점수가 평균 1.12점쯤 높다는 뜻이다(직선 기준).
* 띠는 가운데(10~15시간)가 좁고 양 끝이 넓다. 학생이 적은 35시간 이상 쪽은 선이 더 흔들릴 수 있다.
* 점이 선에서 얼마나 떨어져 흩어졌는지는 선만으로는 알 수 없다. 이것을 숫자로 보는 것이 <b>상관계수</b>다.
  * <b>상관계수 r</b>: -1~1 사이 숫자. 부호는 방향(+ 함께 늘어남, - 한쪽이 늘면 다른 쪽이 줄어듦), 0에서 멀수록 점이 직선 가까이 모여 있다.
  * <b>열1.corr(열2)</b>: 두 열의 상관계수를 구한다. 빈 값이 있는 행은 빼고 계산한다.
""")
code("""
# 설명: 실행 전에 예고한다. 네 줄은 공부-점수, 점수-평점, SNS-수면, 아르바이트-공부 순서다.
# 설명: 출력 0.65, 0.72, -0.36, -0.28을 부호 먼저, 0에서 먼 정도를 다음으로 읽는다.
# 설명: 셋째 줄은 sleep_hours 15명, sns_minutes 6명이 비어 있어 279명으로 계산된 값이다.
# 설명: SNS 900분인 학생 한 명을 빼도 -0.34다. 이상치를 묻는 질문이 나오면 답한다.
print(round(students['study_hours'].corr(students['exam_score']), 2))
print(round(students['exam_score'].corr(students['gpa']), 2))
print(round(students['sns_minutes'].corr(students['sleep_hours']), 2))
print(round(students['part_time_hours'].corr(students['study_hours']), 2))
""")

md("""
* 네 쌍의 r
  * 공부 시간-시험 점수 0.65, 시험 점수-평점 0.72: 양의 관계. 점수-평점이 직선에 조금 더 가깝게 모여 있다.
  * SNS 시간-수면 시간 -0.36: 음의 관계. SNS를 오래 쓰는 학생일수록 잠이 짧은 경향이다.
  * 아르바이트 시간-공부 시간 -0.28: 약한 음의 관계. 1)의 큰 점이 왼쪽에 조금 많았던 것과 맞다.
* r은 직선 관계만 잰다. 곡선 모양 관계나 두 갈래로 섞인 관계는 r만 보면 놓칠 수 있다. 숫자와 산점도를 함께 본다.

* 이번에는 전공별로 회귀선을 따로 그어 기울기를 비교한다. <b>sns.lmplot</b>을 쓴다.
  * <b>col='major'</b>: 전공마다 칸을 하나씩 만들어 옆으로 늘어놓는다. <b>col_order</b>로 칸 순서를 정한다.
* lmplot은 지금까지의 Seaborn 함수와 다르다.
  * 지금까지(scatterplot·regplot·histplot…): 우리가 만든 칸(Axes)에 <b>ax=</b>로 그리고, Axes를 돌려준다.
  * lmplot: Figure와 칸을 <b>스스로</b> 만들고 <b>FacetGrid</b>(칸 묶음)를 돌려준다. 그래서 <b>ax=</b>를 받지 않는다. 넣으면 <b>TypeError: lmplot() got an unexpected keyword argument 'ax'</b>가 난다.
  * 크기는 figsize 대신 <b>height</b>(칸 하나의 높이, 인치)로 정한다.
  * 칸 제목은 <b>g.set_titles('{col_name}')</b>로 단다. 글자 안의 {col_name} 자리에 그 칸의 값(공학 등)이 들어간다. 축 이름은 <b>g.set_axis_labels('x 이름', 'y 이름')</b>으로 모든 칸에 한 번에 단다.
""")
code("""
# 설명: 첫 줄이 fig, ax =가 아니라 g =로 시작하는 것부터 보여 준다. 칸을 미리 만들지 않는다.
# 설명: g에 담아 두는 이유는 다음 셀에서 칸을 꺼내 쓰기 위해서다.
# 설명: 실행 후 맨 아래 <class 'seaborn.axisgrid.FacetGrid'>를 읽어 준다. Axes가 아니라 칸 묶음이다.
# 설명: 공학 선은 오른쪽 끝이 100을 넘고, 예체능 선은 23시간쯤에서 끝난다. 선은 그 전공의 점이 있는 구간까지만 그어진다.
g = sns.lmplot(data=students, x='study_hours', y='exam_score', col='major', col_order=major_order,
               height=3, scatter_kws={'s': 10, 'alpha': 0.5})
g.set_titles('{col_name}')
g.set_axis_labels('주간 공부 시간(시간)', '시험 점수(점)')
plt.show()

print(type(g))
""")

md("""
* 칸 다섯 개가 한 줄로 놓이고, 칸마다 그 전공 학생만으로 그은 회귀선이 있다. y축은 다섯 칸이 같아서 높이를 바로 비교할 수 있다.
* 공학 선이 가장 가파르고 예체능 선이 가장 평평하다. 기울기를 숫자로 확인한다.
  * <b>g.axes</b>: FacetGrid 안의 칸 배열. 5강 axes처럼 <b>g.axes[0, i]</b>로 i번째 칸을 꺼낸다.
  * 칸의 첫 번째 선(<b>lines[0]</b>)이 회귀선이다. 선 양 끝의 높이 차이를 가로 길이로 나누면 기울기다.
""")
code("""
# 설명: 회귀선은 직선이라 양 끝 두 점만 있으면 기울기가 나온다. get_data()로 그 좌표를 꺼낸다.
# 설명: g는 바로 앞 셀의 FacetGrid다. 뒤의 g = 셀을 실행한 다음 이 셀을 다시 돌리면 칸이 하나뿐이라 오류가 난다.
# 설명: 출력은 큰 순서가 아니라 major_order 순서다. 공학 1.51 다음에 자연과학 0.83이 나온다.
# 설명: 예체능 0.5는 0.50이 끝의 0 없이 출력된 것이다.
for i in range(5):
    x, y = g.axes[0, i].lines[0].get_data()
    print(major_order[i], round((y[-1] - y[0]) / (x[-1] - x[0]), 2))
""")

md("""
* 공학 1.51 → 인문 1.01 → 사회과학 0.84 → 자연과학 0.83 → 예체능 0.50(점/시간). 공학이 가장 가파르다.
  * 공학 학생은 공부 시간이 1시간 길 때 점수 차이가 평균 1.5점쯤으로, 예체능(0.5점쯤)의 세 배쯤이다.
  * 사회과학 0.84와 자연과학 0.83은 거의 같다. 두 전공의 순위는 따지지 않는다.
* 예체능은 점이 0~15시간에 몰려 있어 오른쪽 띠가 넓다. 학생 수가 적고 범위가 좁으면 기울기도 더 흔들린다.
""")

# 3) ------------------------------------------------------------------
md("""
#### <b>3) 기온과 에이드·라떼 판매량 lmplot</b>

* 카페 데이터로 기온과 메뉴 판매량의 관계를 본다. 먼저 전체 365일로 회귀선을 긋는다.
  * regplot은 Axes에 그리는 함수라서 1×2 칸에 나눠 그릴 수 있다. lmplot은 칸을 스스로 만들기 때문에 이렇게 남의 칸에 넣을 수 없다.
""")
code("""
# 설명: 앞의 lmplot과 달리 칸을 먼저 만들고 regplot에 ax=로 넘긴다. 코드 구조의 차이를 짚는다.
# 설명: 왼쪽 에이드 선을 본다. 선이 위 갈래와 아래 갈래 사이를 지나서 어느 무리도 잘 나타내지 못한다.
# 설명: 출력 0.51 -0.25를 선 방향과 맞춘다. 라떼 -0.25는 휴무일 7일을 포함한 365일 값이다. 휴무일을 빼면 -0.26이다.
# 설명: avg_temp, ade, latte는 축 이름을 주지 않아 열 이름이 그대로 붙은 것이다.
fig, axes = plt.subplots(1, 2, figsize=(12, 4), layout='constrained')
sns.regplot(data=cafe, x='avg_temp', y='ade', scatter_kws={'s': 10, 'alpha': 0.4}, ax=axes[0])
axes[0].set_title('기온과 에이드')
sns.regplot(data=cafe, x='avg_temp', y='latte', scatter_kws={'s': 10, 'alpha': 0.4}, ax=axes[1])
axes[1].set_title('기온과 라떼')
plt.show()

print(round(cafe['avg_temp'].corr(cafe['ade']), 2), round(cafe['avg_temp'].corr(cafe['latte']), 2))
""")

md("""
* 에이드 선은 오른쪽 위로(r = 0.51), 라떼 선은 오른쪽 아래로(r = -0.25) 기운다. 더운 날 에이드가 더 팔리고 라떼는 덜 팔리는 경향이다.
* 하지만 1)에서 본 것처럼 이 점들은 학기 평일과 주말·방학 두 무리가 섞여 있다. lmplot의 <b>hue='day_type'</b>으로 무리마다 회귀선을 따로 긋는다.
  * lmplot에서 hue는 점 색과 회귀선을 함께 나눈다. 칸은 하나이므로 <b>g.ax</b>로 그 칸을 꺼내 제목을 단다.
""")
code("""
# 설명: 앞 셀 왼쪽 그래프를 hue='day_type'으로 다시 그린 것이다. 선 하나가 둘로 나뉜다고 예고한다.
# 설명: 칸이 하나뿐이라 g.axes[0, i] 대신 g.ax로 꺼낸다. 앞의 전공별 코드와 비교하게 한다.
# 설명: lines[0]이 학기 평일, lines[1]이 주말·방학 선이다. 출력 3.8과 1.41도 day_type_order 순서다.
# 설명: 두 선이 왼쪽 끝에서는 가깝고 오른쪽으로 갈수록 벌어지는 모양을 보여 준다.
g = sns.lmplot(data=cafe, x='avg_temp', y='ade', hue='day_type', hue_order=day_type_order,
               height=4, aspect=1.5, scatter_kws={'s': 10, 'alpha': 0.5})
g.set_axis_labels('일 평균 기온(°C)', '에이드 판매량(잔)')
g.ax.set_title('기온과 에이드 판매량 (학기 평일 / 주말·방학)')
plt.show()

for i in range(2):
    x, y = g.ax.lines[i].get_data()
    print(day_type_order[i], round((y[-1] - y[0]) / (x[-1] - x[0]), 2))
""")

md("""
* <b>aspect</b>: 칸의 가로 ÷ 세로 비율. height=4, aspect=1.5면 칸 하나가 가로 6인치다.
* 두 무리 모두 오른쪽 위로 올라가지만 기울기가 다르다.
  * 학기 평일: 기온 1°C당 약 3.80잔, 주말·방학: 약 1.41잔. 손님이 많은 학기 평일에는 기온에 따른 판매량 차이가 더 크다.
  * 학기 평일 선 아래쪽 바닥의 세 점은 추석 휴무일(10/6~10/8)이다.
* 무리를 나누면 상관계수도 달라진다. 무리마다 r을 구한다.
""")
code("""
# 설명: 출력 한 줄의 앞 숫자가 에이드, 뒤 숫자가 라떼다. for가 무리마다 part를 바꿔 같은 계산을 한다.
# 설명: 앞 셀 기울기와 나란히 놓는다. 에이드 기울기는 학기 평일이 크고(3.80, 1.41), r은 주말·방학이 크다(0.72, 0.82).
# 설명: 기울기와 r을 같은 것으로 여기기 쉽다. 기울기는 1°C당 몇 잔인지, r은 점이 직선에 얼마나 모여 있는지다.
for day in day_type_order:
    part = cafe[cafe['day_type'] == day]
    print(day, round(part['avg_temp'].corr(part['ade']), 2), round(part['avg_temp'].corr(part['latte']), 2))
""")

md("""
* 에이드: 전체 0.51 → 학기 평일 0.72, 주말·방학 0.82. 라떼: 전체 -0.25 → 학기 평일 -0.59, 주말·방학 -0.54.
  * 손님 수가 크게 다른 두 무리가 섞여 있으면, 무리 안에서는 뚜렷한 관계가 전체로는 약하게 보일 수 있다.
* 라떼도 같은 방법으로 그려 본다.
  * <b>혼자 해 보기</b>: 위 에이드 lmplot 코드에서 y를 latte로 바꾸고 제목·축 이름을 고쳐 본다.
""")
code("""
# 설명: 학생이 에이드 셀을 먼저 고쳐 보게 한 뒤 이 셀을 실행한다. 고칠 곳은 y, y축 이름, 제목 세 군데다.
# 설명: 에이드 그래프를 떠올리게 한다. y만 바꿨는데 두 선 모두 방향이 반대로 내려간다.
# 설명: 이 셀은 기울기를 출력하지 않는다. 기울기 차이는 눈으로만 읽는다.
g = sns.lmplot(data=cafe, x='avg_temp', y='latte', hue='day_type', hue_order=day_type_order,
               height=4, aspect=1.5, scatter_kws={'s': 10, 'alpha': 0.5})
g.set_axis_labels('일 평균 기온(°C)', '라떼 판매량(잔)')
g.ax.set_title('기온과 라떼 판매량 (학기 평일 / 주말·방학)')
plt.show()
""")

md("""
* 두 무리 모두 오른쪽 아래로 내려간다. 학기 평일 선이 더 가파르다.

* <b>상관은 인과가 아니다.</b> 두 값이 함께 움직여도 한쪽이 다른 쪽을 움직인다는 뜻은 아니다.
* 에이드와 아메리카노 판매량의 상관계수를 구해 본다.
""")
code("""
# 설명: 실행 전에 묻는다. 에이드가 많이 팔린 날 아메리카노도 많이 팔릴까, 그렇다면 왜일까.
# 설명: 출력 세 줄은 에이드-아메리카노, 에이드-손님, 아메리카노-손님 순서다. 0.8은 0.80이다.
# 설명: 기온 때문이라는 답이 나오면 기온-아메리카노 r이 영업일 기준 0.04임을 알려 준다. 기온으로는 설명되지 않는다.
print(round(cafe['ade'].corr(cafe['americano']), 2))
print(round(cafe['ade'].corr(cafe['customers']), 2))
print(round(cafe['americano'].corr(cafe['customers']), 2))
""")

md("""
* 에이드-아메리카노 r = 0.80으로 아주 강한 양의 관계다. 그렇다고 에이드가 팔려서 아메리카노가 팔린 것은 아니다.
  * 두 메뉴 모두 손님 수와 강하게 함께 움직인다(0.81, 0.98). 손님이 많은 날(학기 평일) 둘 다 많이 팔린 것이다.
  * 이처럼 두 값을 함께 움직이는 제3의 변수가 있으면, 원인과 상관없이 r이 높게 나온다.
* 회귀선과 r은 "함께 움직이는 방향과 정도"를 보여 줄 뿐이다. 왜 그런지는 데이터가 만들어진 상황을 보고 따로 따져야 한다.
""")

# 4) ------------------------------------------------------------------
md("""
#### <b>4) 월별 손님 수 lineplot과 7일 이동평균</b>

* <b>시계열</b>: 날짜·월처럼 시간 순서로 놓인 값. cafe는 하루 = 1행인 시계열이다.
* 3강에서는 월별 평균 손님 수를 두 단계로 그렸다.
  * <b>groupby('year_month')</b>로 월별 평균 표(customers_by_month)를 만들고, <b>ax.plot</b>에 index와 values를 넘겼다.
* <b>sns.lineplot(data=표, x='열', y='열')</b>: x값마다 y의 <b>평균</b>을 계산해 선으로 잇는다. 원래 표를 그대로 넘긴다.
  * year_month('2025-03' 같은 글자)를 x로 쓰면 표에 나온 순서(2025-03 → 2026-02)대로 놓인다.
* 두 방법을 위아래 2×1 칸에 그려 비교한다. 월 글자 12개가 겹치지 않게 가로를 넓게 잡는다(3강).
""")
code("""
# 설명: 위 칸은 groupby 후 ax.plot 두 단계, 아래 칸은 lineplot 한 줄이다. 같은 선이 나오는지 보는 셀이다.
# 설명: axes[1].lines[0]은 아래 칸의 선이다. 앞에서 회귀선을 꺼낸 것과 같은 방법이다.
# 설명: 출력은 2025-03부터 차례다. 첫 값 344.은 344.00이 끝의 0 없이 나온 것이다.
# 설명: 2025-10의 309.45와 2026-02의 125.79에는 휴무일의 0이 들어 있다. 10월 4일, 2월 3일이다.
customers_by_month = cafe.groupby('year_month')['customers'].mean().round(2)

fig, axes = plt.subplots(2, 1, figsize=(10, 7), sharey=True, layout='constrained')
axes[0].plot(customers_by_month.index, customers_by_month.values, marker='o')
axes[0].set_title('groupby + ax.plot')
sns.lineplot(data=cafe, x='year_month', y='customers', marker='o', ax=axes[1])
axes[1].set_title('sns.lineplot')
plt.show()

print(axes[1].lines[0].get_ydata().round(2))
""")

md("""
* 두 선의 높이는 같다. 출력한 값이 customers_by_month와 같다(2025-04 381.37 가장 높음, 2026-02 125.79 가장 낮음).
* 아래 lineplot에는 선 둘레에 연한 <b>띠</b>가 있다.
  * 한 달에 날이 30일쯤 있어서 x값 하나에 y값이 여러 개다. lineplot은 그 평균을 선으로, 평균의 <b>95% 신뢰구간</b>을 띠로 그린다. 7강 barplot의 errorbar와 같은 기본값이다.
  * 7강처럼 <b>errorbar='sd'</b>로 표준편차 띠, <b>errorbar=None</b>으로 띠 없이 그릴 수 있다. 부트스트랩이라 seed가 없으면 띠가 실행마다 조금 달라진다.
* 띠 너비가 달마다 다르다.
  * 학기 달(3~6월, 9~12월)은 띠가 넓고, 방학 달(7·8월, 1월)은 좁다. 학기 달에는 평일(약 410명)과 주말(약 150명)이 섞여 값이 넓게 퍼지기 때문이다.

* 이번에는 월 평균 대신 <b>일별</b> 손님 수를 그대로 그린다. x에 date를 주면 x값 하나에 값이 하나라 띠가 생기지 않는다.
* 일별 선은 평일·주말에 따라 매주 크게 오르내려서 큰 흐름이 잘 안 보인다.
* <b>이동평균</b>: 날마다 "오늘 포함 지난 며칠"의 평균을 다시 구한 값. 짧은 출렁임을 걸러 추세만 남긴다.
  * <b>열.rolling(7).mean()</b>: 행마다 그 행과 바로 위 6행(모두 7행)의 평균을 낸다. cafe는 하루 = 1행이라 7일 이동평균이다.
  * 처음 6일은 7일치가 모이지 않아 빈 값(NaN)이 된다.
  * 끝의 <b>round(2)</b>는 2강처럼 소수 둘째 자리까지 반올림한다.
""")
code("""
# 설명: 실행 전에 예고한다. 위 6행은 NaN으로 나온다. 오류가 아니다.
# 설명: 3/7에서 3/8로 넘어가는 두 줄을 비교한다. 3/1의 169가 빠지고 3/8의 158이 들어와 359.86이 358.29가 된다.
# 설명: rolling은 위쪽 행을 쓰므로 표가 날짜순이어야 뜻이 맞다. cafe는 날짜순이다.
# 설명: customers_7d를 열로 저장하는 이유는 다음 두 셀에서 쓰기 때문이다.
cafe['customers_7d'] = cafe['customers'].rolling(7).mean().round(2)
cafe[['date', 'weekday', 'customers', 'customers_7d']].head(8)
""")

md("""
* 0~5행(3/1~3/6)은 NaN이다. 3/7 값 359.86은 3/1~3/7 손님 수의 평균이다.
* 일별 선은 흐리게(<b>alpha=0.3</b>), 이동평균 선은 진하게 같은 칸에 겹쳐 그린다. <b>label=</b>로 범례 이름을 단다.
  * lineplot은 빈 값을 건너뛰고 그리므로 처음 6일은 이동평균 선이 없다.
""")
code("""
# 설명: 같은 ax로 lineplot을 두 번 부르면 선이 겹쳐 그려진다. 일별 선을 먼저, 이동평균 선을 나중에 그린다.
# 설명: 범례는 label=을 줘서 생겼다. 앞 셀을 건너뛰면 customers_7d가 없어 이 셀에서 오류가 난다.
# 설명: 일별 선이 바닥 0에 닿는 두 곳을 찾게 한다. 10월 초와 2월 중순이고 이동평균도 같은 자리에서 꺼진다.
# 설명: 이동평균 봉우리 네 개를 왼쪽부터 짚는다. 가장 높은 곳이 6월 중순인 것을 눈으로 본 뒤 다음 셀로 간다.
fig, ax = plt.subplots(figsize=(10, 4))
sns.lineplot(data=cafe, x='date', y='customers', alpha=0.3, label='일별', ax=ax)
sns.lineplot(data=cafe, x='date', y='customers_7d', label='7일 이동평균', ax=ax)
ax.set_title('일별 손님 수와 7일 이동평균')
ax.set_xlabel('날짜')
ax.set_ylabel('손님 수(명)')
plt.show()
""")

md("""
* 그래프에서 읽을 것
  * 일별 선(흐림)은 매주 평일에 오르고 주말에 떨어지는 톱니 모양이다.
  * 이동평균 선(진함)은 톱니가 사라지고 학기에 높고 방학(7·8월, 1·2월)에 낮은 큰 흐름만 남는다.
  * 4월 말·6월 중순·10월 말·12월 중순에 이동평균이 솟는다. 네 번의 시험 주간이다(5강 주석).
  * 10월 초와 2월 중순에는 이동평균이 움푹 꺼진다. 추석·설 연휴 휴무일의 0이 들어간 주다.
* 이동평균이 가장 높은 날과 가장 낮은 날을 2강의 <b>sort_values</b>로 확인한다. 빈 값은 정렬 맨 뒤로 간다.
""")
code("""
# 설명: 앞 그래프에서 눈으로 찾은 가장 높은 곳과 낮은 곳을 숫자로 맞춰 본다.
# 설명: 위 표의 세 날은 6/13~6/15로 이어져 있다. 창이 하루씩만 밀리므로 이웃한 날의 값이 비슷하다.
# 설명: 아래 표의 2/18, 2/22, 2/21은 모두 휴무일 2/16~2/18 세 날이 7일 안에 다 들어가는 날이다.
# 설명: 왼쪽 106, 354는 원래 행 번호다. 정렬해도 index는 행을 따라간다.
print(cafe.sort_values('customers_7d', ascending=False)[['date', 'customers_7d']].head(3))
print(cafe.sort_values('customers_7d')[['date', 'customers_7d']].head(3))
""")

md("""
* 가장 높은 날은 2025-06-15(485.29명)다. 6/9~6/15 기말 시험 주간 7일이 꼭 맞게 들어간 평균이다.
* 가장 낮은 날은 2026-02-18(67.71명)이다. 설 연휴 휴무일(2/16~2/18) 세 날의 0이 7일 평균에 들어가 있다.
* 오늘 정리: <b>scatterplot</b>은 관계와 세 번째 변수, <b>regplot·lmplot</b>은 관계의 방향(상관계수로 강도), <b>lineplot</b>은 시간에 따른 평균과 범위, <b>rolling</b>은 출렁임을 걸러낸 추세를 보여 준다.
""")

nb = new_notebook(cells=cells)
nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
nb.metadata["language_info"] = {"name": "python"}
nbformat.validate(nb)
OUT.parent.mkdir(parents=True, exist_ok=True)
nbformat.write(nb, OUT)
print(OUT)
