"""10차시 강사용 노트북 생성: python build_10.py → 10_미니프로젝트/10_미니프로젝트_강사용.ipynb

- 질문 ①(cafe): 학기 중 영업일(1·2학기, 손님 > 0) 218일. 시험 주간 28일 평균 455.07, 평소 190일 평균 340.24 → 1.34배.
- 질문 ②(students): 전공별 study_hours-exam_score r: 공학 0.83 · 자연과학 0.50 · 사회과학 0.41 · 인문 0.49 · 예체능 0.18.
  자연과학 0.50과 인문 0.49가 거의 같아 중간 순위는 묻지 않는다(가장 뚜렷 공학, 가장 약함 예체능만).
- 질문 ③(students): 주거별 수면 시간 평균 기숙사 6.46 · 자취 6.67 · 통학 6.48, 중앙값 6.3 · 6.8 · 6.5, 응답 83 · 110 · 92(결측 15 제외).
  답은 "크게 다르지 않다"(세 상자가 대부분 겹침). 순위를 묻지 않는다.
- 요약 그림은 output/summary.png(노트북 폴더 안). 배포 zip에서 output/은 뺀다.
"""
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

OUT = Path(__file__).resolve().parent.parent / "10_미니프로젝트" / "10_미니프로젝트_강사용.ipynb"

cells = []
md = lambda s: cells.append(new_markdown_cell(s.strip("\n")))
code = lambda s: cells.append(new_code_cell(s.strip("\n")))

md("""
### <b>10강 미니 프로젝트 - 질문하고 그래프로 답하기</b>

* 두 CSV로 <b>질문 세 개</b>를 세우고, 질문마다 필요한 열·필터·집계로 <b>그래프에 넣을 표</b>를 먼저 만든다.
* 질문의 종류(비교·관계·분포)에 맞는 그래프를 고르고, 제목에 질문 대신 <b>답</b>을 쓴다. 세 그래프를 <b>1×3 요약 그림</b> 한 장으로 묶어 저장한다.
* <b>점검 목록</b> 다섯 가지로 일부러 덜 다듬은 그래프를 고친다. 그래프는 질문에 답하는 그림이다.
""")

md("""
* 첫 코드 셀은 6강에서 정한 <b>설정 셀</b> 그대로다.
  * <b>sns.set_theme(...)</b>에 한글 폰트와 마이너스 설정을 함께 넘긴다. 그래프 글자가 깨지면 이 셀을 다시 실행한다.
""")
code("""
# keep
# 설명: 설정 셀이라 출력이 없다. 오류 없이 끝나면 된다. 오른쪽 위 커널이 .venv인지 먼저 함께 본다.
# 설명: 1~9차시에서 쓴 세 라이브러리를 이번에는 한 노트북에서 모두 쓴다. 그래서 설정도 처음에 한 번 정리한다.
# 설명: 커널을 다시 시작하고 이 셀을 건너뛰면 뒤 그래프 제목이 □로 나온다고 말해 둔다.
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
* 전공 순서 리스트(6강)도 미리 만들어 둔다.
""")
code("""
# keep
# 설명: 출력 (300, 12) (365, 14)부터 본다. 행과 열 수가 맞으면 두 파일을 제대로 읽은 것이다.
# 설명: 경로의 ../는 노트북 폴더의 한 칸 위를 뜻한다. data 폴더가 10_미니프로젝트와 나란히 있어야 한다.
# 설명: major_order는 질문 ②에서 전공을 돌 때 쓴다. 뒤 출력과 범례의 전공 순서도 이 리스트가 정한다.
students = pd.read_csv('../data/students.csv')
cafe = pd.read_csv('../data/cafe_sales.csv', parse_dates=['date'])
print(students.shape, cafe.shape)

major_order = ['공학', '자연과학', '사회과학', '인문', '예체능']
""")

# 1) ------------------------------------------------------------------
md("""
#### <b>1) 질문 세 개와 그래프에 넣을 표 준비</b>

* 그래프를 그리기 전에 질문을 정한다. 좋은 질문은 <b>"무엇을 무엇과 비교하는가"</b>가 분명하다.
* 오늘의 질문 세 개
  * <b>① 시험 주간에 카페 손님은 얼마나 늘까?</b> (비교) - cafe
  * <b>② 공부 시간과 점수의 관계는 전공마다 다를까?</b> (관계) - students
  * <b>③ 주거 형태에 따라 수면 시간이 다를까?</b> (분포) - students
* 질문마다 쓸 열, 고를 행(필터), 묶는 방법(집계)을 정하고 2강 방법으로 표를 만든다.

* <b>질문 ①</b>: 시험 주간과 무엇을 비교할지 먼저 정한다.
  * 시험은 학기 중에만 있다. 방학 날까지 넣으면 "평소"가 방학 때문에 낮아져 차이가 부풀려진다.
  * 휴무일(손님 0명, 2강)은 문을 닫은 날이라 "평소 손님"이 아니다.
  * 그래서 <b>학기 중(1학기·2학기) 영업일</b>만 고르고, 그 안에서 시험 주간(exam_week 1)과 평소(exam_week 0)를 비교한다.
""")
code("""
# 설명: 실행 전에 365일 가운데 며칠이 남을지 물어본다.
# 설명: 조건 두 개를 &로 잇고 비교식에는 괄호를 친다. and로 쓰면 Series 관련 ValueError가 난다.
# 설명: 출력 218은 1학기 112일과 2학기 110일을 더한 222일에서 추석 휴무 4일이 빠진 값이다.
# 설명: 표의 count 190과 28을 더하면 218이 되는 것을 짚는다. 필터가 맞게 걸렸는지 보는 습관이다.
semester_days = cafe[cafe['period'].isin(['1학기', '2학기']) & (cafe['customers'] > 0)]
print(len(semester_days))

semester_days.groupby('exam_week')['customers'].agg(['count', 'mean']).round(2)
""")

md("""
* 학기 중 영업일 218일 가운데 평소 190일은 하루 평균 340.24명, 시험 주간 28일은 455.07명이다.
* 그래프에 넣을 표는 평균 두 개다. <b>customers_by_exam</b>으로 저장하고, 시험 주간 평균을 평소 평균으로 나눠 몇 배인지 구한다.
  * Series에서 <b>[0]</b>·<b>[1]</b>은 순서가 아니라 index 이름(exam_week 값 0·1)으로 값을 꺼낸다.
""")
code("""
# 설명: 앞 셀은 표를 보기만 했고, 여기서 평균만 변수에 담는다. 뒤의 막대 그래프가 모두 이 변수를 쓴다.
# 설명: 나눗셈은 시험 주간 [1]이 위, 평소 [0]이 아래다. 출력 1.34가 그래프 제목의 '약 1.3배'가 된다고 예고한다.
# 설명: 필터 없이 cafe 전체로 계산하면 평소가 252.40으로 낮아져 1.80배가 된다.
# 설명: 같은 데이터도 비교 기준에 따라 답이 달라진다는 점을 말한다.
customers_by_exam = semester_days.groupby('exam_week')['customers'].mean().round(2)
print(customers_by_exam)
print(round(customers_by_exam[1] / customers_by_exam[0], 2))
""")

md("""
* 시험 주간 손님은 평소의 <b>1.34배</b>다. 이것이 질문 ①의 답이 된다.

* <b>질문 ②</b>: "관계가 다를까"는 전공마다 상관계수(8강)를 구해 비교한다.
  * 9강처럼 전공을 하나씩 돌며 그 전공 학생만 골라 r을 구한다.
  * 결과를 <b>사전(dict)</b>에 담았다가 <b>pd.Series(사전)</b>로 바꾸면, 키는 index·값은 값인 Series가 된다.
""")
code("""
# 설명: corr_by_major는 사전으로 시작해 Series로 다시 덮어쓴다. 이름이 같아 헷갈리기 쉬우니 짚고 간다.
# 설명: 출력은 r 크기순이 아니라 major_order 순서다. 사회과학 0.41이 인문 0.49보다 위에 있는 이유다.
# 설명: 전체 300명의 r은 0.65 하나뿐이다. 전공으로 나누니 0.18에서 0.83까지 벌어지는 것을 보여 준다.
corr_by_major = {}
for major in major_order:
    part = students[students['major'] == major]
    corr_by_major[major] = round(part['study_hours'].corr(part['exam_score']), 2)

corr_by_major = pd.Series(corr_by_major)
corr_by_major
""")

md("""
* 다섯 전공 모두 양수다. 공부 시간이 길수록 점수가 높은 방향은 어느 전공이나 같다.
* 세기는 다르다. <b>공학 0.83</b>이 가장 뚜렷하고 <b>예체능 0.18</b>이 가장 약하다.
  * 자연과학 0.50과 인문 0.49처럼 거의 같은 값은 순위를 매기지 않는다.

* <b>질문 ③</b>: "다를까"를 평균 하나로만 보면 퍼짐을 놓친다(6강). 주거별로 응답 수·평균·중앙값을 함께 본다.
  * sleep_hours에는 빈 값 15개가 있다(2강). <b>count</b>는 빈 값을 뺀 응답 수다.
""")
code("""
# 설명: 질문별 표의 마지막이다. 이번에는 값 하나가 아니라 count, mean, median 세 열을 함께 만든다.
# 설명: count를 더하면 83 + 110 + 92 = 285다. 300명에서 빈 값 15개가 빠진 수와 맞는다.
# 설명: 주거별 학생 수 85, 115, 100과 견주면 빠진 응답은 2, 5, 8명이다.
# 설명: 실행 후 답을 정하지 않는다. 숫자의 차이가 큰지 묻고 다음 그래프로 넘긴다.
sleep_by_housing = students.groupby('housing')['sleep_hours'].agg(['count', 'mean', 'median']).round(2)
sleep_by_housing
""")

md("""
* 평균은 6.46~6.67시간, 중앙값은 6.3~6.8시간이다. 가장 큰 차이도 평균 약 0.2시간(약 13분)이다.
* 표만으로는 이 차이가 큰지 작은지 판단하기 어렵다. 2)에서 박스플롯으로 퍼짐까지 보고 답한다.
""")

# 2) ------------------------------------------------------------------
md("""
#### <b>2) 질문별 그래프 세 개 그리기</b>

* 질문의 종류가 그래프의 종류를 정한다.
  * 비교(① 평소 vs 시험 주간) → <b>막대</b>(4강)
  * 관계(② 공부 시간-점수, 전공별) → <b>회귀선</b>(8강)
  * 분포(③ 주거별 수면 시간) → <b>박스플롯</b>(6강)
* 제목에는 질문이 아니라 <b>답</b>을 쓴다(5강). 보는 사람이 제목만 읽어도 결론을 안다.

* <b>질문 ①</b>: 평균 두 개를 막대 두 개로 그린다.
  * 0과 1 대신 <b>'평소'</b>, <b>'시험 주간'</b> 글자 리스트를 x로 넘긴다. 값 순서(0, 1)와 글자 순서를 같게 둔다.
  * 시험 주간 막대만 강조색, 평소 막대는 회색이다(5강).
  * 막대는 길이로 비교하므로 y축이 0에서 시작해야 한다. ax.bar는 기본으로 0에서 시작한다.
""")
code("""
# 설명: 1)에서 만든 customers_by_exam을 그대로 쓴다. .values는 index 0, 1을 빼고 숫자만 넘긴다.
# 설명: 글자, 값, 색의 순서가 모두 평소 먼저다. 어긋나면 막대 이름과 값이 뒤바뀐다.
# 설명: 실행 후 y축 눈금이 0부터인지 함께 본다. 제목의 '약 1.3배'는 앞에서 구한 1.34에서 왔다.
# 설명: 4)에서 같은 숫자를 일부러 덜 다듬어 그린 그래프와 비교한다고 예고한다.
fig, ax = plt.subplots(figsize=(5, 4))
ax.bar(['평소', '시험 주간'], customers_by_exam.values, color=['lightgray', '#d62728'])
ax.set_title('시험 주간 손님은 평소의 약 1.3배')
ax.set_xlabel('학기 중 영업일')
ax.set_ylabel('하루 평균 손님 수(명)')
plt.show()
""")

md("""
* 회색 막대 약 340명, 빨간 막대 약 455명. 빨간 막대가 회색 막대보다 3분의 1쯤 더 길다.

* <b>질문 ②</b>: 8강 lmplot은 전공마다 칸을 따로 만들었다. 이번에는 다섯 전공의 회귀선을 <b>한 칸에 겹쳐</b> 기울기를 바로 비교한다.
  * regplot은 axes 수준 함수라 같은 ax에 여러 번 그릴 수 있다(8강).
  * <b>scatter=False</b>: 점은 빼고 회귀선만 긋는다. 점 300개가 겹치면 선이 가려진다.
  * <b>ci=None</b>: 신뢰구간 띠를 그리지 않는다. 띠 다섯 개가 겹치면 읽기 어렵다.
  * <b>label=major</b>: 범례 이름. 색은 부를 때마다 다음 기본 색이 된다.
""")
code("""
# 설명: fig를 만드는 줄이 for 밖에 있는 것을 짚는다. 칸 하나에 다섯 번 그리기 때문이다.
# 설명: label은 이름만 정한다. 범례는 마지막의 ax.legend 줄이 있어야 나온다.
# 설명: 실행 후 범례에서 공학과 예체능 색부터 찾아 선을 따라간다. 기울기는 1.51과 0.50점/시간이다.
# 설명: 기울기와 r은 다른 숫자다. 인문은 기울기 1.01에 r 0.49이니 가운데 전공은 순위를 말하지 않는다.
fig, ax = plt.subplots(figsize=(6, 4))
for major in major_order:
    part = students[students['major'] == major]
    sns.regplot(data=part, x='study_hours', y='exam_score', scatter=False, ci=None, label=major, ax=ax)
ax.set_title('공부 시간과 점수의 관계는 공학에서 가장 뚜렷')
ax.set_xlabel('주간 공부 시간(시간)')
ax.set_ylabel('시험 점수(점)')
ax.legend(title='전공')
plt.show()
""")

md("""
* 다섯 선이 모두 오른쪽 위로 오른다. 방향은 같다.
* 공학 선이 가장 가파르고, 예체능 선이 가장 완만하다. 1)의 r(공학 0.83, 예체능 0.18)과 같은 이야기다.
* 공학 선 오른쪽 끝이 100점을 넘는다. 점수가 100점을 넘었다는 뜻이 아니라, 직선을 그 전공의 가장 긴 공부 시간까지 그었기 때문이다.
* 회귀선은 관계의 방향을 보여 줄 뿐 원인을 말하지 않는다(8강). "공학은 공부하면 점수가 더 오른다"가 아니라 "공학 학생들에게서 공부 시간과 점수가 더 뚜렷하게 함께 움직인다"로 읽는다.

* <b>질문 ③</b>: 주거별 수면 시간 분포를 박스플롯으로 그린다(6강).
  * 차이가 없을 수도 있는 질문이라 강조할 상자가 없다. <b>color='lightgray'</b>로 세 상자를 같은 색으로 둔다.
  * 빈 값은 Seaborn이 알아서 뺀다(6강).
""")
code("""
# 설명: 막대는 평균 표로 그렸지만 박스플롯에는 원본 students를 넘긴다. 분포를 그리려면 값 전체가 필요하다.
# 설명: 실행 전에 앞 표의 평균 차이 약 0.2시간을 떠올리게 하고, 상자가 겹칠지 물어본다.
# 설명: 실행 후 상자끼리 겹치는 범위부터 본다. 가운데 가로선의 작은 차이보다 겹침이 훨씬 크다.
# 설명: 빨강이 없는 것도 짚는다. 강조할 차이가 없으니 색도 쓰지 않았다.
fig, ax = plt.subplots(figsize=(5, 4))
sns.boxplot(data=students, x='housing', y='sleep_hours', color='lightgray', ax=ax)
ax.set_title('주거 형태가 달라도 수면 시간은 비슷')
ax.set_xlabel('주거 형태')
ax.set_ylabel('하루 수면 시간(시간)')
plt.show()
""")

md("""
* 세 상자의 높이(가운데 50%)가 대부분 겹친다. 상자 아래·위 끝이 기숙사 5.9~7.2, 자취 6.0~7.3, 통학 5.7~7.2시간이다.
* 상자 안 가로선(중앙값)은 자취가 조금 높지만(6.8시간), 상자끼리 겹치는 부분이 훨씬 크다. 답은 "주거 형태에 따라 수면 시간이 크게 다르지 않다"이다.
* 차이가 없다는 것도 답이다(9강). 질문을 정하고 확인했기 때문에 "다르지 않다"고 말할 수 있다.
""")

# 3) ------------------------------------------------------------------
md("""
#### <b>3) 1×3 요약 그림으로 묶어 저장</b>

* 질문 하나에 그래프 하나. 세 그래프를 5강의 <b>plt.subplots(1, 3)</b>으로 한 장에 모은다.
  * 한 줄 배치라 칸은 <b>axes[0]</b>·<b>axes[1]</b>·<b>axes[2]</b>로 고른다(5강).
  * Matplotlib 함수는 <b>axes[i].bar(...)</b>처럼, Seaborn 함수는 <b>ax=axes[i]</b>로 칸을 정한다(6강). 한 그림 안에 섞어 그려도 된다.
* 요약 그림에서는 질문 ②도 강조 규칙을 따른다. 공학 선만 강조색, 나머지 네 전공은 회색이다.
  * 범례에는 공학만 남긴다. <b>label=None</b>인 선은 범례에 들어가지 않는다.
* 그림 전체 제목은 <b>fig.suptitle</b>, 저장은 <b>fig.savefig</b>를 <b>plt.show() 앞</b>에 둔다(5강). 저장 폴더 <b>output</b>을 먼저 만든다.
""")
code("""
# 설명: 출력이 없는 셀이다. 실행 후 탐색기의 10_미니프로젝트 안에 output 폴더가 생긴 것을 보여 준다.
# 설명: exist_ok=True가 있어 다시 실행해도 오류가 나지 않는다.
# 설명: 이 폴더가 없으면 다음 셀의 savefig에서 FileNotFoundError가 난다. 그래서 저장보다 먼저 만든다.
import os

os.makedirs('output', exist_ok=True)
""")

md("""
* 2)의 세 코드를 칸만 바꿔 한 셀에 모은다.
""")
code("""
# 설명: 코드는 길지만 새 내용은 적다. 2)의 세 코드에서 ax가 axes[0], axes[1], axes[2]로 바뀐 곳을 따라간다.
# 설명: figsize=(15, 4.5)는 칸 세 개를 가로로 놓는 크기다. layout='constrained'로 칸끼리 글자가 겹치지 않게 한다.
# 설명: 실행 후 칸 제목을 ①②③ 순서로 읽어 준다. 제목만으로 답 세 개가 전해지는지 확인한다.
fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), layout='constrained')

axes[0].bar(['평소', '시험 주간'], customers_by_exam.values, color=['lightgray', '#d62728'])
axes[0].set_title('① 시험 주간 손님은 평소의 약 1.3배')
axes[0].set_xlabel('학기 중 영업일')
axes[0].set_ylabel('하루 평균 손님 수(명)')

# 설명: 가운데 칸은 regplot이다. lmplot은 figure 수준 함수라 칸에 넣을 수 없다.
for major in major_order:
    part = students[students['major'] == major]
    # 설명: 2)와 달라진 곳이다. 공학만 빨강과 범례 이름을 주고, 나머지 네 전공은 회색에 label=None을 준다.
    if major == '공학':
        sns.regplot(data=part, x='study_hours', y='exam_score', scatter=False, ci=None,
                    color='#d62728', label='공학', ax=axes[1])
    else:
        sns.regplot(data=part, x='study_hours', y='exam_score', scatter=False, ci=None,
                    color='lightgray', label=None, ax=axes[1])
axes[1].set_title('② 공부-점수 관계는 공학에서 가장 뚜렷(회색: 나머지 전공)')
axes[1].set_xlabel('주간 공부 시간(시간)')
axes[1].set_ylabel('시험 점수(점)')
axes[1].legend()

sns.boxplot(data=students, x='housing', y='sleep_hours', color='lightgray', ax=axes[2])
axes[2].set_title('③ 주거 형태가 달라도 수면 시간은 비슷')
axes[2].set_xlabel('주거 형태')
axes[2].set_ylabel('하루 수면 시간(시간)')

fig.suptitle('캠퍼스 카페와 학생 설문: 질문 세 개에 그래프로 답하기')
# 설명: 저장 줄이 plt.show() 앞에 있다. 뒤로 옮기면 summary.png가 흰 그림이 된다.
fig.savefig('output/summary.png', dpi=200, bbox_inches='tight')
plt.show()
""")

md("""
* 칸마다 제목이 그 질문의 답이다. 그림 한 장만 보고도 세 가지 결론을 읽을 수 있다.
* 저장된 파일을 확인한다(5강). VS Code 탐색기의 10_미니프로젝트 › output › summary.png를 열어 봐도 된다.
""")
code("""
# 설명: 화면에 그림이 나온 것과 파일이 저장된 것은 별개라 따로 확인한다.
# 설명: 출력 ['summary.png']로 파일이 있는 것을 보고, (923, 3023, 4)를 읽는다.
# 설명: shape는 세로가 먼저, 가로가 그다음이다. 마지막 4는 픽셀마다 값이 네 개라는 뜻이다.
# 설명: 그림 크기 15×4.5인치에 dpi 200을 곱한 가로 3,000, 세로 900과 견주어 본다.
print(os.listdir('output'))
print(plt.imread('output/summary.png').shape)
""")

md("""
* summary.png가 보이고, 크기는 세로 약 900 × 가로 약 3,000 픽셀이다(15×4.5인치 × dpi 200, 여백을 잘라 내 조금 다름).
""")

# 4) ------------------------------------------------------------------
md("""
#### <b>4) 점검 목록으로 그래프 고치기</b>

* 그래프를 다 그렸으면 저장하거나 보여 주기 전에 다섯 가지를 점검한다(이 강의에서 정리한 목록).
  * <b>제목 = 결론</b>: 제목만 읽어도 답을 아는가
  * <b>축 이름과 단위</b>: 축마다 무엇을 어떤 단위로 쟀는지 적었는가
  * <b>막대는 0부터</b>: 막대 그래프의 y축이 0에서 시작하는가(점·선은 아니어도 된다, 7강)
  * <b>색에 뜻이 있고 범례가 있다</b>: 색마다 뜻이 있고, 그 뜻을 범례·제목·눈금 글자에서 알 수 있는가
  * <b>한글·마이너스가 정상이다</b>: 글자가 네모(□)로 나오거나 음수 부호가 깨지지 않는가
* 아래는 질문 ①을 <b>일부러 덜 다듬어</b> 그린 그래프다. 다섯 가지로 점검해 본다.
""")
code("""
# 설명: 데이터는 앞과 같은 customers_by_exam이다. 숫자는 틀리지 않았다고 먼저 말한다.
# 설명: 실행 후 답을 바로 말하지 않는다. 다섯 가지 중 어디에 걸리는지 학생이 먼저 찾게 한다.
# 설명: 막대 길이만 보면 몇 배로 보이는지 물어본다. set_ylim(300, 470)이 그렇게 만든 것이다.
# 설명: 제목의 '별' 글자가 제대로 나오는 것도 본다. 다섯 가지 중 한글·마이너스만 통과한다.
fig, ax = plt.subplots(figsize=(5, 4))
ax.bar(['0', '1'], customers_by_exam.values, color=['tab:blue', 'tab:orange'])
ax.set_ylim(300, 470)
ax.set_title('exam_week별 customers')
plt.show()
""")

md("""
* 점검 결과
  * <b>제목 = 결론</b>: 실패. 'exam_week별 customers'는 무엇을 그렸는지만 말한다.
  * <b>축 이름과 단위</b>: 실패. x축 0·1이 무슨 뜻인지, y축이 무엇을 몇 명 단위로 쟀는지 없다.
  * <b>막대는 0부터</b>: 실패. y축이 300에서 시작한다. 막대 길이가 약 40 대 155가 되어 시험 주간이 <b>약 4배</b>처럼 보인다. 실제는 1.34배다.
  * <b>색에 뜻이 있고 범례가 있다</b>: 실패. 파랑·주황에 뜻이 없고 범례도 없다.
  * <b>한글·마이너스가 정상이다</b>: 통과. 설정 셀 덕분이다. 제목의 글자가 네모로 나오면 설정 셀부터 다시 실행한다.
* 고치는 방법은 2)에서 이미 썼다. 같은 데이터로 고치기 전·후를 나란히 놓아 비교한다.
""")
code("""
# 설명: 같은 표를 두 칸에 그린다. 왼쪽은 앞 셀, 오른쪽은 2) 질문 ①의 코드다.
# 설명: set_ylim은 axes[0]에만 있다. 오른쪽까지 옮기면 고친 뒤에도 y축이 300부터 시작한다.
# 설명: 실행 후 두 칸의 y축 눈금을 비교한다. 왼쪽은 300 위로 약 40 대 155, 오른쪽은 약 340 대 455다.
# 설명: 이 과정의 마지막 코드 셀이다. 같은 순서를 자기 CSV 하나에 적용해 보라고 권한다.
fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout='constrained')

axes[0].bar(['0', '1'], customers_by_exam.values, color=['tab:blue', 'tab:orange'])
axes[0].set_ylim(300, 470)
axes[0].set_title('고치기 전: exam_week별 customers')

axes[1].bar(['평소', '시험 주간'], customers_by_exam.values, color=['lightgray', '#d62728'])
axes[1].set_title('고친 뒤: 시험 주간 손님은 평소의 약 1.3배')
axes[1].set_xlabel('학기 중 영업일')
axes[1].set_ylabel('하루 평균 손님 수(명)')
plt.show()
""")

md("""
* 같은 숫자인데 왼쪽은 차이가 크게 부풀려 보이고, 오른쪽은 실제 비율(약 1.3배)대로 보인다.
* 오른쪽은 다섯 가지를 모두 통과한다. 제목이 결론을 말하고, 축이 단위를 말하고, 막대가 0에서 시작하고, 빨강 하나가 시험 주간을 가리킨다.
* 오늘 정리: 질문을 정하고 → 질문에 맞는 표를 만들고 → 질문의 종류에 맞는 그래프를 고르고 → 제목에 답을 쓰고 → 점검 목록으로 다듬어 저장한다. 그래프는 질문에 답하는 그림이다.
""")

nb = new_notebook(cells=cells)
nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
nb.metadata["language_info"] = {"name": "python"}
nbformat.validate(nb)
OUT.parent.mkdir(parents=True, exist_ok=True)
nbformat.write(nb, OUT)
print(OUT)
