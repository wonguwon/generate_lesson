"""9차시 강사용 노트북 생성: python build_09.py → 09_히트맵다중/09_히트맵다중_강사용.ipynb

- students.corr()는 pandas 3.1.0에서 str 열(student_id 등) 때문에
  ValueError: could not convert string to float: 'S001' 이 난다. 오류 셀은 만들지 않고(오류 셀 0개) 마크다운에 문구만 적는다.
- 월×요일 피벗 최솟값은 2025-07 일·2026-02 일 75.00 동률 → 가장 연한 칸 하나를 묻지 않는다. 가장 진한 칸은 2025-03 수 528.
- 주거별 공부 시간-점수 r(기숙사 0.63·자취 0.68·통학 0.62)은 비슷해 순위를 묻지 않는다.
- pairplot은 9열 전체(81칸)를 실행하지 않고 5열만 쓴다.
"""
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

OUT = Path(__file__).resolve().parent.parent / "09_히트맵다중" / "09_히트맵다중_강사용.ipynb"

cells = []
md = lambda s: cells.append(new_markdown_cell(s.strip("\n")))
code = lambda s: cells.append(new_code_cell(s.strip("\n")))

md("""
### <b>9강 히트맵과 다중 그래프 - heatmap · pivot_table · FacetGrid · pairplot</b>

* <b>corr()</b>로 여러 열의 상관계수를 표 하나로 구하고, <b>heatmap</b>으로 칸마다 색을 칠해 한눈에 훑는다. 양·음이 있는 값은 가운데가 연한 <b>발산형 색</b>, 한쪽으로만 커지는 값은 <b>연속형 색</b>을 쓴다.
* <b>pivot_table</b>로 월×요일처럼 두 범주가 만나는 표를 만들고, 그 표를 히트맵으로 그린다.
* <b>relplot</b>·<b>catplot</b>·<b>pairplot</b>은 8강 lmplot처럼 칸을 스스로 만드는 함수다. 같은 그래프를 집단별로 쪼개 나란히 놓거나, 여러 변수 쌍을 한 장에 모은다. 많이 보여 줄수록 색과 배치의 규칙이 중요해진다.
""")

md("""
* 첫 코드 셀은 6강에서 정한 <b>설정 셀</b> 그대로다.
  * <b>sns.set_theme(...)</b>에 한글 폰트와 마이너스 설정을 함께 넘긴다. 그래프 글자가 깨지면 이 셀을 다시 실행한다.
""")
code("""
# keep
# 설명: 출력이 없는 것이 정상이다. 설정만 바꾸는 셀이라 실행 번호가 붙으면 끝난 것이다.
# 설명: 히트맵 색 막대에 -1.00 같은 음수 눈금이 나오므로 마이너스 설정도 여기서 함께 챙긴다.
# 설명: 커널을 다시 시작했으면 이 셀부터 다시 실행해야 한다고 말해 둔다.
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
# 설명: 출력 (300, 12) (365, 14)로 두 파일이 모두 읽혔는지 본다. students는 1)·3)·4), cafe는 2)에서 쓴다.
# 설명: 리스트 셋은 출력이 없다. major_order는 3)의 catplot, weekday_order는 2)의 피벗 표에서 쓴다.
# 설명: period_order는 이 노트북의 코드 셀에서 쓰지 않는다. 7강과 같이 만들어 두기만 한다.
# 설명: 뒤 셀에서 NameError가 나면 이 셀을 건너뛴 것이니 여기로 돌아오게 한다.
students = pd.read_csv('../data/students.csv')
cafe = pd.read_csv('../data/cafe_sales.csv', parse_dates=['date'])
print(students.shape, cafe.shape)

major_order = ['공학', '자연과학', '사회과학', '인문', '예체능']
weekday_order = ['월', '화', '수', '목', '금', '토', '일']
period_order = ['1학기', '여름방학', '2학기', '겨울방학']
""")

# 1) ------------------------------------------------------------------
md("""
#### <b>1) 학생 데이터 상관 히트맵</b>

* 8강에서는 <b>열1.corr(열2)</b>로 두 열의 상관계수를 한 쌍씩 구했다. 열이 많으면 쌍이 너무 많아진다.
* <b>표.corr()</b>: 표의 모든 수치 열 쌍의 상관계수를 한 번에 구해 표(<b>상관행렬</b>)로 돌려준다.
  * 그런데 students에는 student_id·major·housing 같은 글자(str) 열이 있다. pandas 3에서 그냥 <b>students.corr()</b>를 실행하면 글자를 숫자로 바꾸지 못해 <b>ValueError: could not convert string to float: 'S001'</b> 오류가 난다.
  * <b>numeric_only=True</b>: 수치 열만 골라 계산한다.
* 수치 열만 고르는 다른 방법으로 <b>select_dtypes('number')</b>가 있다. 어떤 열이 남는지 먼저 확인한다.
""")
code("""
# 설명: 실행 전에 묻는다. students 12열 가운데 어떤 열이 빠질지 말해 보게 한다.
# 설명: 출력은 표가 아니라 열 이름 리스트다. select_dtypes가 수치 열만 고르고 columns.tolist()가 이름만 꺼낸다.
# 설명: 실행 후 student_id·major·housing 세 글자 열이 빠진 것을 확인한다.
# 설명: 확인만 하는 셀이다. 결과를 변수에 담지 않으며 다음 셀은 numeric_only=True로 계산한다.
students.select_dtypes('number').columns.tolist()
""")

md("""
* 수치 열은 9개다. grade(학년)도 숫자라서 들어간다.
* 상관행렬을 만든다. 8강처럼 <b>round(2)</b>로 소수 둘째 자리까지 반올림한다.
""")
code("""
# 설명: 앞 셀의 열 9개가 행과 열에 그대로 들어가 9×9 표가 된다. student_corr에 담아 히트맵 두 개에서 다시 쓴다.
# 설명: numeric_only=True를 빠뜨리면 위 마크다운의 ValueError가 난다. 그 오류를 만나면 이 인자부터 보게 한다.
# 설명: study_hours-commute_minutes 칸의 -0.00을 짚는다. 아주 작은 음수가 반올림된 것으로 사실상 0이다.
# 설명: 결측이 있는 sleep_hours(15개)·sns_minutes(6개)도 값이 나온다. 결측을 빼고 계산하기 때문이다.
student_corr = students.corr(numeric_only=True).round(2)
student_corr
""")

md("""
* 표 읽는 법
  * 행과 열이 만나는 칸이 두 열의 r이다. 8강에서 구한 값이 그대로 들어 있다(study_hours-exam_score 0.65, exam_score-gpa 0.72, sleep_hours-sns_minutes -0.36, study_hours-part_time_hours -0.28).
  * 대각선은 자기 자신과의 상관이라 모두 1.00이다.
  * 대각선을 기준으로 위아래가 똑같다(study_hours-gpa와 gpa-study_hours는 같은 값).
* 9×9 = 81칸의 숫자를 눈으로 훑기는 어렵다. <b>sns.heatmap(표)</b>: 표의 칸마다 값에 맞는 색을 칠한다.
  * <b>annot=True</b>: 칸 안에 숫자를 쓴다. <b>fmt='.2f'</b>: 소수 둘째 자리까지 쓴다.
  * heatmap은 scatterplot처럼 Axes에 그리는 함수라서 <b>ax=</b>로 칸을 정한다.
* 먼저 색 설정 없이 그려 본다.
""")
code("""
# 설명: 실행 전에 예고한다. 색을 지정하지 않고 일부러 기본값으로 그려 본다. 문제가 보이면 다음 셀에서 고친다.
# 설명: data·x·y를 따로 주지 않는다. 표를 통째로 넘기면 행 이름이 y축, 열 이름이 x축이 된다.
# 설명: 실행 후 오른쪽 색 막대를 먼저 본다. 막대에서 0이 어디인지 찾아보게 한 뒤 칸의 색과 맞춰 본다.
fig, ax = plt.subplots(figsize=(9, 7))
sns.heatmap(student_corr, annot=True, fmt='.2f', ax=ax)
ax.set_title('학생 데이터 상관계수 (기본 색)')
plt.show()
""")

md("""
* 기본 색은 값이 작을수록 어둡고 클수록 밝다. 그런데 이 색으로는 읽기 어렵다.
  * 가장 어두운 칸은 표에서 가장 작은 값 -0.36이고, 가장 밝은 칸은 대각선 1.00이다. 색의 양 끝이 데이터에 맞춰 정해져서, 0이 어디쯤인지(양인지 음인지) 색만으로 알 수 없다.
* 상관계수는 <b>-1~1</b>이고 <b>0이 가운데</b>다. 이런 값에는 가운데가 연하고 양쪽으로 다른 색이 진해지는 <b>발산형(diverging) 색</b>을 쓴다.
  * <b>cmap='coolwarm'</b>: 음수는 파랑, 양수는 빨강, 0 근처는 연한 회색이다.
  * <b>vmin=-1, vmax=1</b>: 색의 양 끝을 -1과 1로 고정한다. 데이터가 바뀌어도 같은 색이 같은 값을 뜻한다.
  * <b>center=0</b>: 0을 가운데 색에 맞춘다.
""")
code("""
# 설명: 앞 셀과 표는 같다. 달라진 곳은 cmap·vmin·vmax·center와 제목뿐이라 칸의 숫자는 그대로이고 색만 바뀐다.
# 설명: 실행 후 색 막대가 -1.00~1.00으로 바뀐 것을 먼저 보여 준다. 가운데 0.00이 연한 회색이다.
# 설명: -0.36 칸이 막대 끝의 진한 파랑까지 가지 않는 것을 짚는다. 색 범위를 고정해서 값의 크기만큼만 진해진다.
fig, ax = plt.subplots(figsize=(9, 7))
sns.heatmap(student_corr, annot=True, fmt='.2f', cmap='coolwarm', vmin=-1, vmax=1, center=0, ax=ax)
ax.set_title('학생 데이터 상관계수')
plt.show()
""")

md("""
* 그래프에서 읽을 것
  * 대각선을 빼면 가장 진한 빨강은 exam_score-gpa(0.72), 그다음 study_hours-exam_score(0.65), study_hours-gpa(0.45)다. 공부·점수·평점이 서로 함께 움직인다.
  * 가장 진한 파랑은 sleep_hours-sns_minutes(-0.36), 그다음 study_hours-part_time_hours(-0.28)다.
  * grade·commute_minutes 줄은 거의 연한 회색이다(모두 -0.10~0.13). 학년·통학 시간은 다른 열과 직선 관계가 거의 없다.
* 히트맵은 "어디를 더 볼지" 고르는 지도다. 진한 칸을 찾으면 8강처럼 그 두 열의 산점도로 모양을 확인한다. r은 직선 관계만 잰다.
""")

# 2) ------------------------------------------------------------------
md("""
#### <b>2) 월×요일 평균 손님 수 히트맵</b>

* 히트맵은 상관행렬이 아니어도 <b>행과 열이 있는 표</b>면 무엇이든 그린다.
* 2강의 groupby는 한 방향(월별, 요일별)으로 묶었다. <b>월과 요일 두 방향</b>으로 묶으면 "2025-03의 월요일 평균" 같은 칸이 생긴다.
* <b>표.pivot_table(index='행', columns='열', values='값', aggfunc='mean')</b>
  * <b>index</b>: 행으로 놓을 열(year_month), <b>columns</b>: 열로 펼칠 열(weekday)
  * <b>values</b>: 칸에 넣을 값(customers), <b>aggfunc</b>: 묶은 값을 하나로 줄이는 방법. 'mean'(평균)이 기본값이고, 'sum'·'count'도 쓸 수 있다.
""")
code("""
# 설명: 표를 바로 보지 않고 열 이름부터 꺼내는 이유를 말한다. 요일 순서가 맞는지 먼저 보기 위해서다.
# 설명: 실행 전에 묻는다. 열이 월요일부터 나올까?
# 설명: 출력이 금으로 시작하는 것을 보여 준다. 오류가 아니며 다음 셀에서 바로잡는다.
customers_pivot = cafe.pivot_table(index='year_month', columns='weekday', values='customers', aggfunc='mean')
customers_pivot.columns.tolist()
""")

md("""
* 행(year_month)은 '2025-03' 같은 글자라 정렬해도 2025-03 → 2026-02 순서가 맞다(3강).
* 열(요일)은 groupby처럼 가나다순(금·목·수·월·일·토·화)이다. 2강의 <b>reindex</b>로 순서를 맞춘다.
  * 열 순서를 바꿀 때는 <b>reindex(columns=순서 리스트)</b>처럼 columns=를 붙인다.
""")
code("""
# 설명: customers_pivot을 같은 이름으로 덮어쓴다. 순서를 맞춘 이 표를 뒤의 히트맵까지 쓴다.
# 설명: columns=를 빠뜨리면 행을 기준으로 맞추게 되어 표가 NaN으로 채워진다. 학생이 막히기 쉬운 곳이다.
# 설명: 실행 후 열이 월~일로 바뀌었는지 보고 2025-03 수요일 칸의 528.00을 찾아 둔다. 히트맵에서 다시 짚는다.
customers_pivot = customers_pivot.reindex(columns=weekday_order).round(2)
customers_pivot
""")

md("""
* 12행 × 7열 표다. 칸 하나는 그 달 그 요일(4~5일)의 평균 손님 수다. 휴무일 0도 그대로 평균에 들어간다(2강).
* 7강의 <b>groupby(두 열) + unstack()</b>으로도 같은 표가 나온다. 확인해 본다.
""")
code("""
# 설명: 첫 줄이 길지만 왼쪽부터 읽어 준다. 묶기, 평균, unstack으로 펼치기, 요일 순서, 반올림 차례다.
# 설명: same == customers_pivot은 칸마다 True/False가 든 표다. 첫 all()은 열마다, 둘째 all()은 전체를 확인해 값 하나만 남긴다.
# 설명: same은 이 확인에만 쓴다. 뒤 셀은 계속 customers_pivot을 쓴다.
same = cafe.groupby(['year_month', 'weekday'])['customers'].mean().unstack().reindex(columns=weekday_order).round(2)
print((same == customers_pivot).all().all())
""")

md("""
* True: 모든 칸이 같다. pivot_table은 이 두 단계를 한 번에 해 준다.
* 이 표를 히트맵으로 그린다. 손님 수는 0에서 한쪽으로만 커지는 값이다. 이런 값에는 연한 색에서 진한 색으로 가는 <b>연속형(sequential) 색</b>을 쓴다.
  * <b>cmap='YlOrRd'</b>: 노랑(적음) → 주황 → 빨강(많음)
  * <b>fmt='.0f'</b>: 칸이 작아 정수로만 쓴다.
  * <b>cbar_kws={'label': '…'}</b>: 오른쪽 색 막대(colorbar)에 이름을 단다.
""")
code("""
# 설명: 상관 히트맵과 달리 vmin·vmax·center가 없다. 손님 수는 0을 가운데 둘 이유가 없는 값이다.
# 설명: 표에는 소수 둘째 자리까지 있지만 칸에는 정수만 쓴다. 528.00이 528로 보인다.
# 설명: 제목에 결론까지 적었다. 실행 후 학기 평일이 가장 붐빈다는 제목이 맞는지 그림에서 확인하게 한다.
# 설명: 가장 진한 칸은 2025-03 수요일 528이다. 가장 연한 칸은 2025-07 일과 2026-02 일이 75.00 동률이라 하나를 묻지 않는다.
fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(customers_pivot, annot=True, fmt='.0f', cmap='YlOrRd',
            cbar_kws={'label': '평균 손님 수(명)'}, ax=ax)
ax.set_title('월·요일별 평균 손님 수: 학기 평일이 가장 붐빔')
ax.set_xlabel('요일')
ax.set_ylabel('연-월')
plt.show()
""")

md("""
* 그래프에서 읽을 것
  * 진한 칸은 학기 달(3~6월, 9~12월)의 월~목에 모여 있다. 가장 진한 칸은 2025-03 수요일(528명)이다.
  * 토·일 열은 모든 달에 연하고, 방학 달(7·8월, 1·2월) 행은 모든 요일이 연하다. 가장 연한 곳은 방학 달 일요일(75~82명)이다.
  * 2025-10의 월(339)·수(398)는 학기 달의 같은 요일 가운데 가장 연하다. 추석 휴무일(10/5~10/8, 그중 월~수는 10/6~10/8)의 0이 평균에 들어갔다.
  * 2026-02는 목(165)이 월~수(128·141·137)보다 진하다. 설 휴무일(2/16~2/18, 월~수)의 0 때문이다.
* 3강 선 그래프는 월별 흐름, 7강 pointplot은 요일별 차이를 따로 보여 줬다. 피벗 히트맵은 두 가지를 한 장에 담는다.
""")

# 3) ------------------------------------------------------------------
md("""
#### <b>3) 주거 형태별로 나눈 공부 시간-점수 산점도</b>

* 8강의 <b>lmplot</b>은 Figure와 칸을 스스로 만들고 <b>FacetGrid</b>(칸 묶음)를 돌려줬다. 이런 함수를 <b>figure 수준 함수</b>라고 한다.
* Seaborn에는 figure 수준 함수가 더 있다. 지금까지 쓴 axes 수준 함수를 묶어서 칸 나누기를 더한 것이다.
  * <b>relplot</b>: 관계 그래프. <b>kind='scatter'</b>(scatterplot, 기본값) 또는 <b>kind='line'</b>(lineplot)
  * <b>catplot</b>: 범주 그래프. <b>kind='strip'</b>(기본값)·'box'·'violin'·'bar'·'count'·'point'
* 칸 나누기 인자
  * <b>col=</b>: 값마다 칸을 옆으로, <b>row=</b>: 값마다 칸을 아래로 늘어놓는다.
  * <b>col_wrap=</b>: 한 줄에 놓을 칸 수. 넘치면 다음 줄로 넘긴다.
* 5강에서 subplots로 칸을 만들고 칸마다 그리던 일을 열 이름 하나로 해 준다.
* 주거 형태(housing)마다 공부 시간-점수 산점도를 칸 하나씩 그린다. 칸 제목·축 이름은 8강 lmplot과 같은 방법으로 단다.
""")
code("""
# 설명: 앞 히트맵과 달리 fig, ax를 만들지 않고 ax=도 없다. relplot이 Figure와 칸을 스스로 만든다.
# 설명: 크기는 figsize가 아니라 height로 칸 하나의 높이를 정한다. 여기서는 3.5다.
# 설명: s와 alpha는 칸 안의 scatterplot에 그대로 전달된다. 작고 흐린 점으로 그려 겹친 곳을 읽게 한다.
# 설명: 그래프 아래 <class 'seaborn.axisgrid.FacetGrid'>를 짚는다. 8강 lmplot이 돌려준 것과 같은 종류다.
g = sns.relplot(data=students, x='study_hours', y='exam_score', col='housing', kind='scatter',
                height=3.5, s=15, alpha=0.6)
g.set_titles('{col_name}')
g.set_axis_labels('주간 공부 시간(시간)', '시험 점수(점)')
plt.show()

print(type(g))
""")

md("""
* 칸 세 개가 기숙사·자취·통학 순서(표에 처음 나온 순서)로 놓인다. 순서를 바꾸려면 <b>col_order=</b>를 준다.
* 세 칸 모두 점 무리가 오른쪽 위로 기운다. 자취 칸이 학생이 가장 많아(115명) 점이 가장 많다.
* x·y축 눈금이 세 칸에 같다(공유). 그래서 칸끼리 높이·퍼짐을 바로 비교할 수 있다.
* 주거 형태가 달라도 관계 모양은 비슷하다. 숫자로 확인한다.
""")
code("""
# 설명: 반복문이 낯선 학생을 위해 한 바퀴만 따라간다. housing이 기숙사일 때 part는 85행짜리 표가 된다.
# 설명: 출력의 가운데 숫자는 학생 수다. 85 + 115 + 100 = 300으로 전체와 맞는다.
# 설명: 오른쪽 숫자가 r이다. 값의 차이가 작으므로 어느 주거 형태가 가장 높은지 순위를 묻지 않는다.
for housing in ['기숙사', '자취', '통학']:
    part = students[students['housing'] == housing]
    print(housing, len(part), round(part['study_hours'].corr(part['exam_score']), 2))
""")

md("""
* 기숙사 0.63, 자취 0.68, 통학 0.62로 비슷하다. 칸을 나눠 봤더니 차이가 없다는 것도 하나의 답이다.

* 이번에는 <b>catplot</b>으로 박스플롯을 학년별 칸에 나눠 그린다(6강 boxplot).
  * <b>kind='box'</b>: boxplot으로 그린다. <b>order=major_order</b>로 칸 안의 상자 순서를 정한다.
  * <b>col='grade', col_wrap=2</b>: 학년 1~4를 2칸씩 두 줄(2×2)로 놓는다.
  * <b>aspect</b>: 칸의 가로 ÷ 세로(8강). 전공 이름 다섯 개가 겹치지 않게 가로를 넓힌다.
  * <b>g.set_titles('{col_name}학년')</b>: {col_name} 자리에 1·2·3·4가 들어간다.
""")
code("""
# 설명: 칸을 나누는 인자는 앞의 relplot과 같다. 바뀐 것은 함수 이름과 kind이고 그래프 종류만 달라진다.
# 설명: order=는 칸 안의 상자 순서이고, 앞에서 말한 col_order=는 칸의 순서다. 둘을 헷갈리지 않게 구분해 준다.
# 설명: 실행 후 위 줄 칸에 전공 이름이 없는 것을 짚는다. x축을 공유해 아래 줄에만 적힌 것이고 오류가 아니다.
# 설명: 전체 평균은 공학 18.16, 예체능 6.28이다. 그 차이가 학년 칸마다 유지되는지 공학과 예체능 상자를 차례로 짚는다.
g = sns.catplot(data=students, x='major', y='study_hours', col='grade', col_wrap=2, kind='box',
                order=major_order, height=3, aspect=1.5)
g.set_titles('{col_name}학년')
g.set_axis_labels('전공', '주간 공부 시간(시간)')
plt.show()
""")

md("""
* 네 칸 모두 공학 상자가 가장 높고 예체능 상자가 가장 낮다. 학년이 달라도 전공별 순서가 크게 바뀌지 않는다.
* col_wrap을 쓰면 칸이 한 줄로 늘어선 배열이 되어 <b>g.axes[i]</b>로 칸을 꺼낸다(8강의 g.axes[0, i]와 다름).

* 참고: figure 수준 함수가 안에서 하는 일을 직접 할 수도 있다.
  * <b>sns.FacetGrid(표, row='열')</b>로 빈 칸 묶음을 만들고, <b>g.map_dataframe(그릴 함수, x='열')</b>로 칸마다 그 함수를 실행한다.
  * relplot·catplot에 없는 그래프(예: histplot)를 칸마다 그릴 때 쓴다. histplot은 figure 수준 displot(col=·row=)도 있다.
* 분포를 비교할 때는 <b>row=</b>로 칸을 위아래로 쌓으면 x축이 한 줄로 맞아 비교하기 쉽다.
""")
code("""
# 설명: 지금까지는 한 번에 그렸고 여기서는 두 단계다. 첫 줄은 빈 칸만 만들고 둘째 줄이 그린다.
# 설명: sns.histplot에 괄호를 붙이지 않는다. 함수 이름만 넘겨 칸마다 실행하게 하는 것이다. 학생이 막히기 쉬운 곳이다.
# 설명: binwidth=5는 막대 하나의 폭이 5분이라는 뜻이다. aspect=3으로 칸을 가로로 길게 만든다.
# 설명: 실행 후 통학 칸 오른쪽 끝을 화면에서 짚어 준다. 막대가 작아 놓치기 쉽고, 그다음 큰 값이 114분이라 사이가 비어 있다.
g = sns.FacetGrid(students, row='housing', height=2, aspect=3)
g.map_dataframe(sns.histplot, x='commute_minutes', binwidth=5)
g.set_titles('{row_name}')
g.set_axis_labels('편도 통학 시간(분)', '학생 수(명)')
plt.show()
""")

md("""
* 기숙사·자취는 왼쪽(30분 이하)에 몰려 있고, 통학만 30분 넘는 오른쪽에 넓게 퍼져 있다. 오른쪽 끝 180분 막대 하나는 2강의 이상치(S037)다.
""")

# 4) ------------------------------------------------------------------
md("""
#### <b>4) 학생 데이터 pairplot</b>

* <b>sns.pairplot(표, vars=[열 목록])</b>: 고른 열의 모든 쌍을 산점도로 그려 격자로 늘어놓는다.
  * 대각선 칸은 같은 열끼리라 산점도 대신 그 열의 <b>분포</b>(히스토그램)를 그린다.
  * 1)의 상관 히트맵이 숫자 하나로 요약했다면, pairplot은 점 모양까지 보여 준다.
* pairplot도 figure 수준 함수다. <b>PairGrid</b>를 돌려주고 ax=를 받지 않는다. 크기는 <b>height</b>(칸 하나의 높이)로 정한다.
* 열을 다 넣으면 9열 × 9열 = 81칸이라 그리는 데 오래 걸리고, 칸이 작아 읽기 어렵다. 1) 히트맵에서 관계가 보인 열 위주로 5개만 고른다.
  * sns_minutes는 900분 이상치(2강) 하나 때문에 축이 늘어나 점이 한쪽에 몰려서 뺐다.
""")
code("""
# 설명: pair_cols를 변수로 둔 이유는 다음 셀에서 같은 열을 또 쓰기 때문이다.
# 설명: 실행 전에 예고한다. 칸이 25개라 앞 그래프보다 시간이 더 걸릴 수 있으니 끝날 때까지 기다린다.
# 설명: 축 이름을 따로 달지 않아 열 이름이 그대로 나온다. 칸을 읽을 때 맨 왼쪽과 맨 아래의 이름을 본다.
# 설명: part_time_hours 줄의 0 위치에 점이 한 줄로 깔린 것을 짚는다. 그래프 아래 출력은 FacetGrid가 아니라 PairGrid다.
pair_cols = ['study_hours', 'exam_score', 'gpa', 'sleep_hours', 'part_time_hours']

g = sns.pairplot(students, vars=pair_cols, height=2)
plt.show()

print(type(g))
""")

md("""
* 5 × 5 = 25칸이다. 칸의 행이 y축, 열이 x축이다.
  * study_hours·exam_score·gpa 셋이 만나는 칸은 점이 오른쪽 위로 기운다(1)의 진한 빨강 칸).
  * 대각선의 part_time_hours 히스토그램은 0시간 막대가 가장 높다(아르바이트를 하지 않는 학생 112명).
* 대각선 위아래는 x·y만 바뀐 같은 그래프다.
  * <b>corner=True</b>: 아래 삼각형만 그린다. 칸이 15개로 줄어 읽기 쉽다.
* <b>hue='housing'</b>으로 주거 형태마다 색을 나눈다.
  * hue를 주면 대각선은 히스토그램 대신 색마다 밀도 곡선(6강 kdeplot)을 겹쳐 그린다.
  * <b>plot_kws={'s': 10, 'alpha': 0.5}</b>: 산점도 칸에만 줄 설정을 사전으로 넘긴다(8강 scatter_kws와 같은 생각).
""")
code("""
# 설명: 앞 셀과 같은 pair_cols에 hue·corner·plot_kws만 더했다.
# 설명: 실행 후 위쪽 삼각형이 사라지고 오른쪽에 housing 범례가 생긴 것을 보여 준다.
# 설명: part_time_hours 곡선이 0 왼쪽까지 이어져도 음수 시간이 있는 것이 아니다. 곡선을 부드럽게 이어서 생긴 모양이다.
# 설명: 1) 히트맵에서 가장 진했던 exam_score-gpa(0.72)를 gpa 줄에서 찾아 숫자와 점 모양을 연결해 준다.
g = sns.pairplot(students, vars=pair_cols, hue='housing', corner=True, height=2,
                 plot_kws={'s': 10, 'alpha': 0.5})
plt.show()
""")

md("""
* 그래프에서 읽을 것
  * 대각선 part_time_hours 곡선: 기숙사·통학 곡선은 0시간 근처 봉우리가 가장 높고, 자취 곡선은 15시간 근처에 가장 높은 봉우리가 있어 오른쪽(긴 아르바이트)으로 퍼져 있다. 주거별 중앙값은 기숙사 0, 통학 5, 자취 12.5시간이다.
  * 다른 대각선 칸(공부 시간·점수·평점·수면)은 세 색 곡선이 거의 겹친다.
  * study_hours-exam_score 칸: 세 색이 섞여 같은 방향으로 기운다. 3)에서 본 것처럼 주거 형태가 이 관계를 가르지 않는다.
* 처음 받은 데이터는 pairplot으로 전체를 훑고, 눈에 띄는 쌍을 골라 8강의 산점도·회귀선이나 3)의 칸 나누기로 자세히 본다.
* 오늘 정리: <b>heatmap</b>은 표의 칸을 색으로(상관은 발산형, 한 방향 값은 연속형), <b>pivot_table</b>은 두 범주가 만나는 표, <b>relplot·catplot</b>은 같은 그래프를 집단별 칸으로, <b>pairplot</b>은 여러 변수 쌍을 한 장에 보여 준다.
""")

nb = new_notebook(cells=cells)
nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
nb.metadata["language_info"] = {"name": "python"}
nbformat.validate(nb)
OUT.parent.mkdir(parents=True, exist_ok=True)
nbformat.write(nb, OUT)
print(OUT)
