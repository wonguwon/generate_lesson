"""4차시 강사용 노트북 생성: python build_04.py → 04_기본그래프/04_기본그래프_강사용.ipynb"""
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

OUT = Path(__file__).resolve().parent.parent / "04_기본그래프" / "04_기본그래프_강사용.ipynb"

cells = []
md = lambda s: cells.append(new_markdown_cell(s.strip("\n")))
code = lambda s: cells.append(new_code_cell(s.strip("\n")))

md("""
### <b>4강 막대·산점도·히스토그램 - bar · scatter · hist</b>

* 범주끼리 크기를 비교할 때는 <b>막대 그래프</b>(<b>ax.bar</b>·<b>ax.barh</b>)를 그린다. 메뉴별 총판매량, 전공별 학생 수와 평균 공부 시간을 막대로 옮긴다.
* 두 수치의 관계는 <b>산점도</b>(<b>ax.scatter</b>)로 점을 찍어 본다. 공부 시간과 시험 점수, 기온과 에이드 판매량을 비교한다.
* 값이 어디에 몰려 있는지는 <b>히스토그램</b>(<b>ax.hist</b>)으로 구간을 나눠 세어 본다. 수면 시간과 SNS 사용 시간의 분포, 이상치를 확인한다.
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
* 오늘은 두 파일을 모두 쓴다. 2강과 같은 방법으로 읽는다.
  * <b>students</b>: 학생 300명의 생활 습관 설문(가상), 학생 1명 = 1행
  * <b>cafe</b>: 캠퍼스 카페 365일 판매(가상), 하루 = 1행. date 열은 날짜로 읽는다.
""")
code("""
# keep
students = pd.read_csv('../data/students.csv')
cafe = pd.read_csv('../data/cafe_sales.csv', parse_dates=['date'])
print(students.shape, cafe.shape)
""")

# 1) ------------------------------------------------------------------
md("""
#### <b>1) 메뉴별 총판매량 막대</b>

* 1년 동안 메뉴마다 몇 잔이 팔렸는지 비교한다. 먼저 그래프에 넣을 표를 만든다.
  * <b>cafe[['americano', 'latte', 'ade', 'tea']]</b>: 메뉴 4개 열만 고른다.
  * <b>sum()</b>: 열마다 값을 모두 더한다. 결과는 메뉴 이름이 index, 합계가 values인 <b>Series</b>다.
""")
code("""
menu_total = cafe[['americano', 'latte', 'ade', 'tea']].sum()
menu_total
""")

md("""
* <b>ax.bar(x, y)</b>: x의 범주마다 y 높이의 세로 막대를 그린다.
  * 3강의 선 그래프와 같이 index를 x, values를 y로 넣는다. 그리는 함수만 plot에서 bar로 바뀐다.
  * 제목과 y축 이름(단위)도 3강처럼 붙인다.
""")
code("""
fig, ax = plt.subplots()
ax.bar(menu_total.index, menu_total.values)
ax.set_title('메뉴별 총판매량')
ax.set_ylabel('판매량(잔)')
plt.show()
""")

md("""
* 그래프에서 읽을 것
  * 아메리카노(40,866잔)가 가장 높고, 차(9,770잔)가 가장 낮다. 아메리카노 막대가 차 막대의 약 4배 길이다.
  * 라떼(22,611잔)와 에이드(20,523잔)는 높이가 비슷하다.
* 막대의 y축은 저절로 <b>0</b>에서 시작한다. 막대는 길이로 크기를 비교하므로 0에서 시작해야 "4배 길면 4배 많다"가 맞다.
  * 선 그래프는 흐름을 보는 그래프라 y축이 0에서 시작하지 않아도 된다(3강의 월별 평균 그래프는 110 근처에서 시작했다).
""")

# 2) ------------------------------------------------------------------
md("""
#### <b>2) 전공별 학생 수 가로 막대와 정렬</b>

* 2강의 <b>value_counts()</b>로 전공마다 학생 수를 센다. 결과는 많은 순으로 정렬된 Series다.
  * 자연과학과 인문은 둘 다 55명으로 같다.
""")
code("""
major_count = students['major'].value_counts()
major_count
""")

md("""
* <b>ax.barh(y, 너비)</b>: 가로 막대를 그린다. 범주 이름이 세로축에 놓이고, 막대가 오른쪽으로 뻗는다.
  * 범주 이름이 길거나 범주가 많을 때 글자가 겹치지 않아 읽기 쉽다.
  * 가로 막대에서는 값이 x축에 있으므로 단위는 <b>set_xlabel</b>에 쓴다.
""")
code("""
fig, ax = plt.subplots()
ax.barh(major_count.index, major_count.values)
ax.set_title('전공별 학생 수')
ax.set_xlabel('학생 수(명)')
plt.show()
""")

md("""
* 가장 많은 공학이 맨 아래에 있다. barh는 첫 번째 값을 <b>맨 아래</b>에 그리고 위로 쌓아 올리기 때문이다.
* 큰 막대를 맨 위에 두려면 작은 값부터 오도록 정렬해서 넘긴다.
  * <b>sort_values()</b>: 값을 작은 것부터 정렬한다(2강의 ascending=False를 빼면 오름차순).
  * 정렬해서 그리면 막대 길이 순서와 위아래 순서가 같아져 순위가 한눈에 읽힌다.
""")
code("""
major_count_sorted = major_count.sort_values()

fig, ax = plt.subplots()
ax.barh(major_count_sorted.index, major_count_sorted.values)
ax.set_title('전공별 학생 수')
ax.set_xlabel('학생 수(명)')
plt.show()
""")

md("""
* 그래프에서 읽을 것
  * 공학(80명)이 맨 위에서 가장 길고, 예체능(40명)이 맨 아래에서 가장 짧다.
  * 자연과학과 인문은 55명으로 막대 길이가 같다. 같은 값끼리는 순서가 정해져 있지 않으니 순위로 읽지 않는다.
""")

# 3) ------------------------------------------------------------------
md("""
#### <b>3) 전공별 평균 공부 시간 막대(groupby 결과)</b>

* 2강에서 만든 전공별 평균 공부 시간 표를 다시 만든다. 큰 값부터 정렬된 Series다.
""")
code("""
study_by_major = students.groupby('major')['study_hours'].mean().round(2).sort_values(ascending=False)
study_by_major
""")

md("""
* groupby 결과도 index(전공)와 values(평균)가 있으므로 1)과 똑같이 <b>ax.bar</b>로 그린다.
  * 큰 값부터 정렬한 표라서 막대가 왼쪽부터 높은 순으로 놓인다.
""")
code("""
fig, ax = plt.subplots()
ax.bar(study_by_major.index, study_by_major.values)
ax.set_title('전공별 주간 평균 공부 시간')
ax.set_ylabel('공부 시간(시간)')
plt.show()
""")

md("""
* 그래프에서 읽을 것
  * 공학(18.16시간)이 가장 높고 예체능(6.28시간)이 가장 낮다. 공학이 예체능의 약 3배다.
  * 막대가 왼쪽부터 공학 → 자연과학 → 사회과학 → 인문 → 예체능 순으로 낮아진다.
* 막대 그래프는 개수(value_counts)든 평균(groupby)이든 <b>범주 하나에 값 하나</b>인 표를 그린다.
""")

# 4) ------------------------------------------------------------------
md("""
#### <b>4) 공부 시간과 시험 점수 산점도</b>

* <b>산점도</b>: 두 수치 열을 x와 y로 놓고 한 행을 점 하나로 찍는 그래프다. 여기서는 학생 한 명이 점 하나다.
* <b>ax.scatter(x, y)</b>: x와 y 자리에 점을 찍는다. plot과 달리 점을 선으로 잇지 않는다.
  * x에 주간 공부 시간, y에 시험 점수를 넣는다. 점 300개가 찍힌다.
""")
code("""
fig, ax = plt.subplots()
ax.scatter(students['study_hours'], students['exam_score'])
ax.set_title('공부 시간과 시험 점수')
ax.set_xlabel('주간 공부 시간(시간)')
ax.set_ylabel('시험 점수(점)')
plt.show()
""")

md("""
* 그래프에서 읽을 것
  * 점들이 왼쪽 아래에서 오른쪽 위로 비스듬히 퍼져 있다. 공부 시간이 길수록 점수가 높은 학생이 많다.
  * 한 줄로 딱 붙어 있지는 않다. 같은 공부 시간이어도 점수가 넓게 흩어져 있다.
* 0~20시간 근처는 점이 빽빽하게 겹쳐 몇 개가 모여 있는지 보이지 않는다.
  * <b>s</b>: 점 크기. 기본값은 36이다. 작게 하면 겹침이 줄어든다.
  * <b>alpha</b>: 투명도. 0(투명)~1(불투명). 0.5로 하면 점이 겹친 곳이 더 진하게 보인다.
""")
code("""
fig, ax = plt.subplots()
ax.scatter(students['study_hours'], students['exam_score'], s=15, alpha=0.5)
ax.set_title('공부 시간과 시험 점수')
ax.set_xlabel('주간 공부 시간(시간)')
ax.set_ylabel('시험 점수(점)')
plt.show()
""")

md("""
* 점이 작고 투명해져, 진하게 겹친 곳(공부 5~20시간, 점수 60~90점 근처)에 학생이 많이 모여 있는 것이 보인다.
* 오른쪽 끝 40시간 근처의 점들은 점수가 88~100점으로 높다.
""")

# 5) ------------------------------------------------------------------
md("""
#### <b>5) 기온과 에이드 판매량 산점도</b>

* 카페 데이터에서 하루가 점 하나다. x에 그날 평균 기온, y에 에이드 판매 잔 수를 놓는다.
""")
code("""
fig, ax = plt.subplots()
ax.scatter(cafe['avg_temp'], cafe['ade'], s=15, alpha=0.5)
ax.set_title('기온과 에이드 판매량')
ax.set_xlabel('평균 기온(°C)')
ax.set_ylabel('에이드 판매량(잔)')
plt.show()
""")

md("""
* 그래프에서 읽을 것
  * 기온이 오를수록 에이드가 많이 팔리는 쪽으로 점이 올라간다. 영하의 날은 많아야 40잔이 안 된다.
  * 10°C 무렵부터 점이 위아래 두 갈래로 벌어진다. 위 갈래는 손님이 많은 학기 평일, 아래 갈래는 손님이 적은 주말·방학이다(무리를 나눠 색으로 그리는 방법은 8강).
  * 맨 아래 0에 붙은 점 7개는 추석·설 휴무일이다.
* 비교로 기온과 <b>손님 수</b>를 찍어 본다. 관계가 약하면 어떤 모양인지 본다.
""")
code("""
fig, ax = plt.subplots()
ax.scatter(cafe['avg_temp'], cafe['customers'], s=15, alpha=0.5)
ax.set_title('기온과 손님 수')
ax.set_xlabel('평균 기온(°C)')
ax.set_ylabel('손님 수(명)')
plt.show()
""")

md("""
* 기온이 바뀌어도 점들이 오르거나 내려가지 않는다. 기온과 손님 수는 관계가 거의 없다.
  * 점이 위(학기 평일)와 아래(주말·방학) 두 띠로 나뉘는 것은 기온이 아니라 학사 일정 때문이다.
* 산점도는 점들이 <b>기울어진 방향</b>으로 관계를 읽는다. 오른쪽 위로 올라가면 함께 늘고, 평평하게 퍼지면 관계가 약하다.
""")

# 6) ------------------------------------------------------------------
md("""
#### <b>6) 수면 시간 히스토그램과 bins 바꿔 보기</b>

* <b>분포</b>: 값들이 어느 범위에 얼마나 퍼져 있는지, 어디에 몰려 있는지의 모양이다.
* 2강에서 sleep_hours에 빈 값이 15개 있었다. 히스토그램을 그리기 전에 빈 값을 빼 둔다.
  * <b>Series.dropna()</b>: 빈 값(NaN)을 뺀 새 Series를 돌려준다. 2강의 dropna(subset=...)를 열 하나에 쓴 것이다.
  * <b>len()</b>으로 남은 개수를 확인한다. 300명 중 15명이 빠져 285명이다.
  * 이 버전의 ax.hist는 빈 값을 말없이 건너뛴다. 미리 빼고 개수를 확인해야 몇 명을 그린 그래프인지 안다.
""")
code("""
sleep = students['sleep_hours'].dropna()
len(sleep)
""")

md("""
* <b>ax.hist(값)</b>: 값의 범위를 같은 너비의 <b>구간(bin)</b>으로 나누고, 구간마다 값이 몇 개 들어가는지 세어 막대로 그린다.
  * 기본 구간 수는 10개다. x축은 수면 시간, y축은 그 구간에 든 학생 수다.
  * 막대 그래프는 x축이 범주(전공)지만, 히스토그램은 x축이 이어진 수치 구간이라 막대 사이에 틈이 없다.
""")
code("""
fig, ax = plt.subplots()
ax.hist(sleep)
ax.set_title('수면 시간 분포')
ax.set_xlabel('하루 수면 시간(시간)')
ax.set_ylabel('학생 수(명)')
plt.show()
""")

md("""
* 가운데(6~7시간대)가 높고 양 끝(4시간대, 8시간대)으로 갈수록 낮아지는 종 모양이다.
  * 가장 높은 막대는 6.88~7.31시간 구간으로 57명이다.
* <b>bins</b>: 구간 수를 정한다. 같은 데이터라도 bins에 따라 모양이 달라 보인다.
  * bins=5: 구간이 넓어 막대 5개로 뭉뚱그려진다. 큰 모양만 보인다.
""")
code("""
fig, ax = plt.subplots()
ax.hist(sleep, bins=5)
ax.set_title('수면 시간 분포 (bins=5)')
ax.set_xlabel('하루 수면 시간(시간)')
ax.set_ylabel('학생 수(명)')
plt.show()
""")

md("""
* bins=20: 구간이 좁아져 막대가 촘촘해진다. 종 모양이 유지되면서 조금 더 자세히 보인다.
""")
code("""
fig, ax = plt.subplots()
ax.hist(sleep, bins=20)
ax.set_title('수면 시간 분포 (bins=20)')
ax.set_xlabel('하루 수면 시간(시간)')
ax.set_ylabel('학생 수(명)')
plt.show()
""")

md("""
* bins=50: 구간이 너무 좁아 중간중간 빈 구간이 생기고 막대가 들쭉날쭉하다.
  * 수면 시간은 6.5, 6.6처럼 0.1시간 단위로 적혀 있는데, 구간 너비(약 0.09시간)가 그보다 좁아 값이 하나도 안 들어가는 구간이 생긴다.
* bins는 너무 적으면 모양이 뭉개지고, 너무 많으면 잡음이 커진다. 몇 가지 값을 바꿔 보며 모양이 안정적으로 보이는 값을 고른다.
""")
code("""
fig, ax = plt.subplots()
ax.hist(sleep, bins=50)
ax.set_title('수면 시간 분포 (bins=50)')
ax.set_xlabel('하루 수면 시간(시간)')
ax.set_ylabel('학생 수(명)')
plt.show()
""")

# 7) ------------------------------------------------------------------
md("""
#### <b>7) SNS 사용 시간 히스토그램에서 이상치 찾기</b>

* sns_minutes도 빈 값 6개를 빼고 시작한다. 294명이 남는다.
""")
code("""
sns_min = students['sns_minutes'].dropna()
len(sns_min)
""")

md("""
* 하루 SNS 사용 시간을 bins=20으로 그린다.
""")
code("""
fig, ax = plt.subplots()
ax.hist(sns_min, bins=20)
ax.set_title('SNS 사용 시간 분포')
ax.set_xlabel('하루 SNS 사용 시간(분)')
ax.set_ylabel('학생 수(명)')
plt.show()
""")

md("""
* 그래프에서 읽을 것
  * 대부분의 막대가 왼쪽(25~200분)에 몰려 있고, 오른쪽으로 갈수록 낮아지는 긴 꼬리 모양이다.
  * 오른쪽 끝 900분 근처에 높이 1짜리 막대가 홀로 떨어져 있다. 그 앞 약 510~850분 구간은 비어 있다.
  * 값 하나 때문에 x축이 900까지 늘어나, 나머지 막대가 왼쪽에 좁게 눌려 있다.
* 2강의 필터로 400분 이상인 학생을 찾아본다. 900분은 S026 한 명이고, 그다음은 480분이다.
""")
code("""
students[students['sns_minutes'] >= 400][['student_id', 'major', 'sns_minutes']]
""")

md("""
* 900분(15시간)은 다른 값과 동떨어진 <b>이상치</b>다. 히스토그램에서는 홀로 떨어진 막대로 드러난다.
* 900분을 빼고 그리면 나머지 학생들의 분포가 넓게 펼쳐져 보인다.
  * <b>sns_min[sns_min < 900]</b>: 2강의 조건 필터를 Series에 쓴 것이다. 900분 미만만 남긴다.
  * 그래프를 보려고 잠시 뺀 것이다. 원래 데이터에서 지울지는 입력 실수인지 확인한 뒤 정한다.
""")
code("""
fig, ax = plt.subplots()
ax.hist(sns_min[sns_min < 900], bins=20)
ax.set_title('SNS 사용 시간 분포 (900분 제외)')
ax.set_xlabel('하루 SNS 사용 시간(분)')
ax.set_ylabel('학생 수(명)')
plt.show()
""")

md("""
* x축이 480분까지로 줄어, 70~185분 근처에 가장 많이 몰려 있고 오른쪽으로 꼬리가 길게 늘어진 모양이 또렷해진다.
  * 오른쪽 끝의 작은 막대는 그다음으로 큰 480분이다.
* 오늘 그린 세 그래프를 정리하면 <b>비교는 막대(bar·barh), 관계는 점(scatter), 분포는 구간(hist)</b>이다.
""")

nb = new_notebook(cells=cells)
nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
nb.metadata["language_info"] = {"name": "python"}
nbformat.validate(nb)
OUT.parent.mkdir(parents=True, exist_ok=True)
nbformat.write(nb, OUT)
print(OUT)
