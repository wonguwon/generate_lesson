"""2차시 강사용 노트북 생성: python build_02.py → 02_pandas/02_pandas_강사용.ipynb"""
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

from colab_setup import PREPARE, PREPARE_MD

OUT = Path(__file__).resolve().parent.parent / "02_pandas" / "02_pandas_강사용.ipynb"

cells = []
md = lambda s: cells.append(new_markdown_cell(s.strip("\n")))
code = lambda s: cells.append(new_code_cell(s.strip("\n")))

md("""
### <b>2차시 pandas로 데이터 다루기 - read_csv · 열 선택 · 필터 · groupby · 결측치</b>

* 실습 데이터 두 개(<b>students.csv</b>, <b>cafe_sales.csv</b>)를 읽고, 표의 모양과 자료형을 확인한다.
* 열은 이름으로, 행은 조건으로 고르고, 범주별로 묶어 개수·평균을 낸다.
* 그리기 전에 빈 값과 튀는 값을 찾아 두고, 0처럼 이상해 보이는 값이 실제 값인지 판단한다.
""")

md(PREPARE_MD)
code(PREPARE)

md("""
* 준비 셀 다음 셀에 <b>설정 셀</b>을 입력한다. 1차시에서 정한 그대로다.
  * 오늘은 그래프를 그리지 않지만, 설정 셀은 매 시간 똑같이 입력해 실행한다.
""")
code("""
# 표를 다루는 pandas와 그래프를 그리는 plt를 불러온다
import pandas as pd
import matplotlib.pyplot as plt

# 그래프의 기본 폰트를 나눔고딕으로 정한다
plt.rcParams['font.family'] = 'NanumGothic'
# 축 눈금의 마이너스를 일반 하이픈으로 바꾼다
plt.rcParams['axes.unicode_minus'] = False
""")

# 1) ------------------------------------------------------------------
md("""
#### <b>1) 두 CSV 읽고 모양과 자료형 보기</b>

* 이 과정의 실습 데이터는 두 파일이다. 둘 다 이 과정을 위해 만든 <b>가상 데이터</b>로, 실제 학교·카페·학생과 관계가 없다.
  * <b>students.csv</b>: 대학생 300명의 생활 습관 설문. 학생 1명이 1행이다.
  * <b>cafe_sales.csv</b>: 캠퍼스 카페의 1년(2025-03-01 ~ 2026-02-28) 일별 판매. 하루가 1행이다.
* <b>CSV</b>: 쉼표(,)로 칸을 나눈 표 파일이다. 왼쪽 파일 탭의 drive › MyDrive › 데이터_시각화_실습 › data에서 students.csv를 더블클릭하면 내용을 볼 수 있다. 첫 줄에 열 이름, 그 아래 줄마다 값이 있다.
* <b>pd.read_csv('경로')</b>: CSV를 읽어 <b>DataFrame</b>(행과 열로 된 표)으로 만든다.
  * <b>'data/students.csv'</b>: data 폴더 안의 파일이다. data는 드라이브의 실습 폴더에 올려 둔 폴더다.
* <b>head()</b>: 표의 앞 5행을 보여 준다. 왼쪽 굵은 숫자 0, 1, 2…는 행 번호(<b>index</b>)다.
""")
code("""
# 학생 설문 CSV를 읽어 students에 담는다
students = pd.read_csv('data/students.csv')
# 앞 5행을 본다
students.head()
""")

md("""
* <b>shape</b>: 표의 모양을 <b>(행 수, 열 수)</b>로 알려 준다. 괄호 없이 쓴다.
  * students는 300행 12열이다. 학생 300명, 항목 12개라고 읽는다.
""")
code("""
# 표의 행 수와 열 수를 본다
students.shape
""")

md("""
* <b>info()</b>: 열마다 이름, 빈 값이 아닌 개수(<b>Non-Null Count</b>), 자료형(<b>Dtype</b>)을 한 번에 보여 준다.
* <b>자료형(dtype)</b>: 열에 든 값의 종류다. 그래프를 그릴 수 있는 열인지 여기서 먼저 확인한다.
  * <b>int64</b>: 정수(학년, 점수), <b>float64</b>: 소수(공부 시간, 수면 시간)
  * <b>object</b>: 글자(전공, 주거 형태)
* sleep_hours는 285, sns_minutes는 294로 300보다 적다. 빈 값이 있다는 뜻이다(6)에서 다시 본다).
""")
code("""
# 열 이름, 빈 값이 아닌 개수, 자료형을 본다
students.info()
""")

md("""
* cafe_sales.csv의 <b>date</b> 열은 날짜다. 그런데 그냥 읽으면 pandas는 이 열을 글자(<b>object</b>)로 읽는다.
  * 글자로 된 날짜는 '2025-03-01'이라는 문자열일 뿐이라, 날짜 순서나 간격을 모른다.
""")
code("""
# 날짜 옵션 없이 카페 CSV를 읽는다
raw = pd.read_csv('data/cafe_sales.csv')
# date 열의 자료형을 출력한다
print(raw['date'].dtype)
""")

md("""
* <b>parse_dates=['date']</b>: 읽을 때 date 열을 날짜 자료형(<b>datetime64</b>)으로 바꾼다.
  * 날짜 자료형이어야 3차시 선 그래프에서 x축이 날짜 순서와 간격대로 그려진다.
* <b>dtypes</b>: 열별 자료형만 따로 보여 준다. cafe는 365행 14열이다.
  * 맨 아래 줄의 <b>dtype: object</b>는 이 결과(열별 자료형 목록)의 자료형이고, 위 표의 object는 각 열의 자료형이다.
""")
code("""
# date 열을 날짜로 바꿔 읽어 cafe에 담는다
cafe = pd.read_csv('data/cafe_sales.csv', parse_dates=['date'])
# 표의 행 수와 열 수를 출력한다
print(cafe.shape)
# 열별 자료형을 본다
cafe.dtypes
""")

md("""
* 앞 5행을 보면 하루가 한 줄이고, 손님 수(customers), 메뉴별 잔 수(americano·latte·ade·tea), 매출(sales)이 열로 있다.
  * year_month는 '2025-03' 같은 연-월 글자, period는 학사 기간(1학기·여름방학·2학기·겨울방학), exam_week는 시험 주간이면 1이다.
""")
code("""
# cafe의 앞 5행을 본다
cafe.head()
""")

# 2) ------------------------------------------------------------------
md("""
#### <b>2) 시험 주간(exam_week == 1)만 골라 손님 수 보기</b>

* <b>df['열 이름']</b>: 열 하나를 고른다. 결과는 <b>Series</b>(이름표가 붙은 값 한 줄)다.
  * 열 이름은 철자·대소문자까지 같아야 한다. 틀리면 <b>KeyError</b>가 난다.
""")
code("""
# customers 열 하나를 골라 앞 5개를 본다
cafe['customers'].head()
""")

md("""
* <b>df[['열1', '열2']]</b>: 여러 열을 고른다. 대괄호 안에 <b>열 이름 리스트</b>를 넣으므로 대괄호가 두 겹이다.
  * 결과는 다시 DataFrame(표)이다.
""")
code("""
# 두 열을 골라 앞 5행을 본다
cafe[['date', 'customers']].head()
""")

md("""
* <b>조건식</b>: <b>cafe['exam_week'] == 1</b>처럼 열과 값을 비교하면 행마다 <b>True/False</b>가 담긴 Series가 나온다.
  * <b>sum()</b>을 하면 True를 1로 세므로, 조건에 맞는 행의 개수가 된다. 시험 주간은 28일이다.
""")
code("""
# 시험 주간이면 True인 조건식을 만든다
is_exam = cafe['exam_week'] == 1
# 조건식의 앞 5개를 출력한다
print(is_exam.head())
# True의 개수를 세어 출력한다
print('True 개수:', is_exam.sum())
""")

md("""
* <b>df[조건]</b>: 조건이 True인 행만 남긴 새 표를 만든다. 이것을 <b>필터</b>라고 한다.
  * 결과 표를 변수에 담아 두면 이어서 열을 고르거나 평균을 낼 수 있다.
""")
code("""
# 시험 주간 행만 골라 exam에 담는다
exam = cafe[cafe['exam_week'] == 1]
# 고른 행의 개수를 출력한다
print(len(exam))
# 세 열을 골라 앞 5행을 본다
exam[['date', 'weekday', 'customers']].head()
""")

md("""
* 시험 주간과 나머지 날의 평균 손님 수를 비교한다. <b>mean()</b>은 평균, <b>round(값, 2)</b>는 소수 2자리 반올림이다.
  * 시험 주간 평균은 455.07명, 나머지 날은 252.4명이다.
""")
code("""
# 시험 주간이 아닌 행을 normal에 담는다
normal = cafe[cafe['exam_week'] == 0]
# 두 표의 평균 손님 수를 출력한다
print('시험 주간:', round(exam['customers'].mean(), 2))
print('나머지 날:', round(normal['customers'].mean(), 2))
""")

md("""
* <b>df.loc[행 조건, 열 이름]</b>: 행과 열을 한 번에 고른다. 쉼표 앞이 행, 뒤가 열이다.
  * 위의 <b>exam[['date', 'weekday', 'customers']]</b>를 한 줄로 쓴 것과 같다.
  * 값을 <b>바꿀 때</b>도 <b>.loc</b>을 쓴다. 6)에서 직접 확인한다.
""")
code("""
# loc으로 행과 열을 한 번에 골라 앞 5행을 본다
cafe.loc[cafe['exam_week'] == 1, ['date', 'weekday', 'customers']].head()
""")

# 3) ------------------------------------------------------------------
md("""
#### <b>3) 공학 전공이면서 기숙사에 사는 학생만 고르기</b>

* 조건 두 개를 묶을 때는 <b>&</b>(그리고), <b>|</b>(또는)를 쓴다.
  * 조건 하나하나를 <b>괄호</b>로 감싼다. 괄호를 빼면 TypeError가 난다.
  * 파이썬의 <b>and</b>·<b>or</b>는 쓰지 않는다. 쓰면 ValueError(The truth value of a Series is ambiguous)가 난다.
* 공학이면서 기숙사인 학생은 22명이다.
""")
code("""
# 공학이면서 기숙사인 학생을 고른다
eng_dorm = students[(students['major'] == '공학') & (students['housing'] == '기숙사')]
# 고른 학생 수를 출력한다
print(len(eng_dorm))
# 네 열을 골라 앞 5행을 본다
eng_dorm[['student_id', 'major', 'housing', 'study_hours']].head()
""")

md("""
* <b>|</b>(또는): 자취이거나 기숙사인 학생을 고른다. 둘 중 하나만 맞아도 남는다.
  * 자취 115명 + 기숙사 85명 = 200명이다.
""")
code("""
# 자취이거나 기숙사인 학생을 고른다
dorm_or_alone = students[(students['housing'] == '자취') | (students['housing'] == '기숙사')]
# 고른 학생 수를 센다
len(dorm_or_alone)
""")

md("""
* <b>isin(리스트)</b>: 값이 리스트 안에 있으면 True다. 같은 열에 '또는'을 여러 번 쓸 때 짧게 쓴다.
  * 위의 | 조건과 결과(200명)가 같다.
""")
code("""
# isin으로 같은 학생을 골라 수를 센다
len(students[students['housing'].isin(['자취', '기숙사'])])
""")

md("""
* 고른 표에서도 열을 골라 평균을 낼 수 있다. 공학·기숙사 학생의 평균 공부 시간은 18.2시간으로, 전체 평균 12.61시간보다 길다.
""")
code("""
# 공학·기숙사 학생과 전체의 평균 공부 시간을 출력한다
print('공학·기숙사:', round(eng_dorm['study_hours'].mean(), 2))
print('전체:', round(students['study_hours'].mean(), 2))
""")

# 4) ------------------------------------------------------------------
md("""
#### <b>4) 전공별 학생 수와 평균 공부 시간</b>

* <b>value_counts()</b>: 열의 값마다 몇 번 나오는지 세어, 많은 순으로 보여 준다.
  * 공학 80, 사회과학 70, 자연과학 55, 인문 55, 예체능 40명이다.
  * 자연과학과 인문은 55명으로 같다. 같은 개수끼리의 순서는 바뀔 수 있다.
""")
code("""
# 전공별 학생 수를 센다
students['major'].value_counts()
""")

md("""
* <b>groupby('묶을 열')['계산할 열'].mean()</b>: 묶을 열의 값이 같은 행끼리 모아, 계산할 열의 평균을 낸다.
  * 읽는 순서: 전공별로 묶어서 → 공부 시간 열을 골라 → 평균
  * 계산할 열을 고르지 않고 <b>students.groupby('major').mean()</b>을 하면 TypeError가 난다. 글자 열(student_id·housing)은 평균을 낼 수 없기 때문이다.
""")
code("""
# 전공별로 묶어 평균 공부 시간을 낸다
students.groupby('major')['study_hours'].mean()
""")

md("""
* 결과는 전공 이름의 가나다순이다. 비교하기 쉽게 정렬한다.
  * <b>round(2)</b>: 소수 2자리 반올림, <b>sort_values(ascending=False)</b>: 큰 값부터
* 공학 18.16시간이 가장 길고 예체능 6.28시간이 가장 짧다. 이런 표를 막대 그래프로 옮기는 방법은 4차시에서 다루고, 그때 필요한 표는 그 차시 노트북에서 다시 만든다.
""")
code("""
# 전공별 평균을 반올림해 큰 값부터 정렬한다
study_by_major = students.groupby('major')['study_hours'].mean().round(2).sort_values(ascending=False)
# 만든 표를 본다
study_by_major
""")

md("""
* <b>agg(['mean', 'count'])</b>: 여러 계산을 한 번에 한다. 결과는 계산마다 열이 하나씩 생긴 표다.
  * <b>sort_values('mean', ascending=False)</b>: 표는 정렬할 열 이름을 넣는다.
  * count 열은 value_counts()의 학생 수와 같다.
""")
code("""
# 전공별 평균과 학생 수를 함께 내어 정렬한다
students.groupby('major')['study_hours'].agg(['mean', 'count']).round(2).sort_values('mean', ascending=False)
""")

# 5) ------------------------------------------------------------------
md("""
#### <b>5) 기간(period)별·요일별 평균 손님 수</b>

* 같은 방법으로 cafe를 학사 기간별로 묶어 평균 손님 수를 낸다.
  * 결과가 1학기 → 2학기 → 겨울방학 → 여름방학 순이다. 시간 순서가 아니라 <b>가나다순</b>이다.
""")
code("""
# 학사 기간별 평균 손님 수를 낸다
cafe.groupby('period')['customers'].mean().round(2)
""")

md("""
* <b>reindex(순서 리스트)</b>: 결과의 행을 리스트에 적은 순서로 다시 놓는다.
  * 시간 순서(1학기 → 여름방학 → 2학기 → 겨울방학)로 두어야 그래프로 옮길 때 흐름이 바르게 보인다.
* 1학기 364.00명, 2학기 332.91명으로 학기 중이 높고, 여름방학 149.11명, 겨울방학 136.30명으로 방학이 낮다.
""")
code("""
# 학사 기간을 시간 순서로 적은 리스트
period_order = ['1학기', '여름방학', '2학기', '겨울방학']
# 기간별 평균을 시간 순서로 다시 놓는다
customers_by_period = cafe.groupby('period')['customers'].mean().round(2).reindex(period_order)
# 만든 표를 본다
customers_by_period
""")

md("""
* 요일도 가나다순(금·목·수·월…)으로 나오므로 월~일 순서로 다시 놓는다.
* 수요일 374.10명이 가장 많고, 일요일 113.79명이 가장 적다. 주말에 크게 떨어진다.
  * 이 평균에는 카페가 쉰 날의 0이 섞여 있다. 6)에서 확인한다.
""")
code("""
# 요일을 월요일부터 적은 리스트
weekday_order = ['월', '화', '수', '목', '금', '토', '일']
# 요일별 평균을 월~일 순서로 다시 놓는다
customers_by_weekday = cafe.groupby('weekday')['customers'].mean().round(2).reindex(weekday_order)
# 만든 표를 본다
customers_by_weekday
""")

# 6) ------------------------------------------------------------------
md("""
#### <b>6) 빈 값 세기와 튀는 값 찾기</b>

* <b>결측치(NaN)</b>: 비어 있는 값이다. 설문에 답하지 않은 칸처럼 값이 없는 자리다.
* <b>isna()</b>: 칸마다 비어 있으면 True다. <b>sum()</b>을 붙이면 열별로 빈 칸 수를 센다.
  * sleep_hours 15개, sns_minutes 6개가 비어 있고, 나머지 열은 0개다.
""")
code("""
# 열별로 빈 칸 수를 센다
students.isna().sum()
""")

md("""
* <b>dropna(subset=['열'])</b>: 그 열이 비어 있는 행을 뺀 <b>새 표</b>를 돌려준다. 원래 students는 그대로다.
  * 수면 시간을 그릴 때는 sleep_hours가 빈 15행을 빼고 285행으로 그린다.
""")
code("""
# sleep_hours가 빈 행을 뺀 새 표를 만든다
sleep_ok = students.dropna(subset=['sleep_hours'])
# 원래 표와 새 표의 크기를 출력한다
print(students.shape, sleep_ok.shape)
""")

md("""
* <b>이상치</b>: 다른 값과 동떨어진 값이다. <b>describe()</b>로 개수·평균·최솟값·사분위수·최댓값을 보면 찾기 쉽다.
  * <b>25% · 50% · 75%</b>: 값을 작은 순으로 줄 세웠을 때 4분의 1, 가운데, 4분의 3 자리의 값이다.
  * sns_minutes는 75%가 180분인데 최댓값(max)이 900분이다. commute_minutes는 75%가 50분인데 최댓값이 180분이다.
""")
code("""
# 세 열의 요약 통계를 소수 2자리로 본다
students[['sleep_hours', 'sns_minutes', 'commute_minutes']].describe().round(2)
""")

md("""
* 최댓값이 누구인지 필터로 찾는다. SNS를 하루 500분 넘게 쓴 학생은 <b>S026</b> 한 명(900분)이다.
  * 900분은 하루 15시간이다. 그다음으로 큰 값은 480분이다.
""")
code("""
# SNS를 500분 이상 쓴 학생을 네 열로 본다
students[students['sns_minutes'] >= 500][['student_id', 'major', 'housing', 'sns_minutes']]
""")

md("""
* <b>sort_values('열', ascending=False).head(3)</b>: 큰 값부터 3행을 본다.
  * 통학 시간 1위는 <b>S037</b>의 180분이고, 2위는 114분으로 차이가 크다.
* 이상치는 바로 지우지 않는다. 실제로 그런 학생일 수도, 입력 실수일 수도 있으므로 찾아서 적어 둔다.
  * 6차시 박스플롯에서 이 값들이 따로 떨어진 점으로 다시 보인다.
""")
code("""
# 통학 시간이 긴 학생 3명을 세 열로 본다
students.sort_values('commute_minutes', ascending=False).head(3)[['student_id', 'housing', 'commute_minutes']]
""")

md("""
* cafe에는 빈 값이 없다. 대신 손님 수가 <b>0</b>인 날이 있다.
  * 7일 모두 판매 값이 0이고, 날짜가 2025년 추석 연휴(10/5~10/8)와 2026년 설 연휴(2/16~2/18)다.
* 0은 잘못 들어간 값이 아니라 <b>카페가 쉰 날의 실제 값</b>이다. 지우지 않고 휴무일이라고 표시해 둔다.
""")
code("""
# 손님이 0명인 날을 다섯 열로 본다
cafe[cafe['customers'] == 0][['date', 'weekday', 'period', 'customers', 'sales']]
""")

md("""
* 먼저 모든 날을 '영업'으로 적은 status 열을 만들고, 손님이 0인 날만 '휴무'로 바꿔 본다.
* 아래처럼 <b>필터한 표에 다시 열을 골라 값을 넣는 방식</b>(연쇄 할당)은 원래 cafe를 바꾸지 못한다.
  * 조건으로 고른 결과는 원본과 따로인 복사본이라, 값이 복사본에만 들어간다.
  * <b>SettingWithCopyWarning</b> 경고가 나오고, '휴무'가 0개 그대로다. 이 경고는 일부러 보여 주는 것이다.
""")
code("""
# 모든 날을 '영업'으로 적은 status 열을 만든다
cafe['status'] = '영업'
# 필터한 표에서 열을 골라 '휴무'를 넣는다
cafe[cafe['customers'] == 0]['status'] = '휴무'
# status 값별 날짜 수를 센다
cafe['status'].value_counts()
""")

md("""
* <b>df.loc[행 조건, '열'] = 값</b>: 행과 열을 한 번에 지정해 원래 표의 값을 바꾼다. 값을 바꿀 때는 이 방식만 쓴다.
  * 이제 휴무 7일, 영업 358일이다.
""")
code("""
# loc으로 손님이 0명인 날을 '휴무'로 바꾼다
cafe.loc[cafe['customers'] == 0, 'status'] = '휴무'
# status 값별 날짜 수를 센다
cafe['status'].value_counts()
""")

md("""
* 영업한 날만 골라 요일별 평균 손님 수를 다시 낸다.
  * 휴무일이 있던 월·화·수·일요일의 평균이 올라간다. 수요일은 374.10 → 389.06명이다.
  * 쉰 날을 넣을지 뺄지는 질문에 따라 정한다. 표시해 두면 둘 다 바로 계산할 수 있다.
* 다음 시간부터 필요한 표는 그 차시 노트북에서 다시 만들어 그래프로 옮긴다.
""")
code("""
# 영업한 날만 골라 open_days에 담는다
open_days = cafe[cafe['status'] == '영업']
# 영업일의 요일별 평균 손님 수를 낸다
open_days.groupby('weekday')['customers'].mean().round(2).reindex(weekday_order)
""")

nb = new_notebook(cells=cells)
nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
nb.metadata["language_info"] = {"name": "python"}
nbformat.validate(nb)
OUT.parent.mkdir(parents=True, exist_ok=True)
nbformat.write(nb, OUT)
print(OUT)
