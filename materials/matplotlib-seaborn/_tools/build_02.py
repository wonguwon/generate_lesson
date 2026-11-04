"""2차시 강사용 노트북 생성: python build_02.py → 02_pandas/02_pandas_강사용.ipynb"""
from pathlib import Path

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

OUT = Path(__file__).resolve().parent.parent / "02_pandas" / "02_pandas_강사용.ipynb"

cells = []
md = lambda s: cells.append(new_markdown_cell(s.strip("\n")))
code = lambda s: cells.append(new_code_cell(s.strip("\n")))

md("""
### <b>2강 pandas로 데이터 다루기 - read_csv · 열 선택 · 필터 · groupby · 결측치</b>

* 실습 데이터 두 개(<b>students.csv</b>, <b>cafe_sales.csv</b>)를 읽고, 표의 모양과 자료형을 확인한다.
* 열은 이름으로, 행은 조건으로 고르고, 범주별로 묶어 개수·평균을 낸다.
* 그리기 전에 빈 값과 튀는 값을 찾아 두고, 0처럼 이상해 보이는 값이 실제 값인지 판단한다.
""")

md("""
* 첫 코드 셀은 매 시간 실행하는 <b>설정 셀</b>이다. 1강에서 정한 그대로다.
  * 오늘은 그래프를 그리지 않지만, 설정 셀은 매 시간 똑같이 먼저 실행한다.
""")
code("""
# keep
# 설명: 1강에서 정한 설정 셀이다. 어느 시간이든 노트북을 열면 이 셀부터 실행한다.
# 설명: 실행해도 출력은 없다. 왼쪽 대괄호에 번호가 찍히면 끝난 것이다.
# 설명: 뒤에서 NameError: name 'pd' is not defined가 나면 이 셀을 건너뛴 것이다.
import platform
import pandas as pd
import matplotlib.pyplot as plt

if platform.system() == 'Windows':
    plt.rcParams['font.family'] = 'Malgun Gothic'
else:
    plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False
""")

# 1) ------------------------------------------------------------------
md("""
#### <b>1) 두 CSV 읽고 모양과 자료형 보기</b>

* 이 과정의 실습 데이터는 두 파일이다. 둘 다 이 과정을 위해 만든 <b>가상 데이터</b>로, 실제 학교·카페·학생과 관계가 없다.
  * <b>students.csv</b>: 대학생 300명의 생활 습관 설문. 학생 1명이 1행이다.
  * <b>cafe_sales.csv</b>: 캠퍼스 카페의 1년(2025-03-01 ~ 2026-02-28) 일별 판매. 하루가 1행이다.
* <b>CSV</b>: 쉼표(,)로 칸을 나눈 표 파일이다. 메모장으로 열면 첫 줄에 열 이름, 그 아래 줄마다 값이 있다.
* <b>pd.read_csv('경로')</b>: CSV를 읽어 <b>DataFrame</b>(행과 열로 된 표)으로 만든다.
  * <b>'../data/students.csv'</b>: 노트북 폴더의 한 칸 위(<b>..</b>)에 있는 data 폴더 안의 파일이다.
* <b>head()</b>: 표의 앞 5행을 보여 준다. 왼쪽 굵은 숫자 0, 1, 2…는 행 번호(<b>index</b>)다.
""")
code("""
# 설명: 첫 줄은 파일을 읽어 students에 담고, 둘째 줄은 앞부분만 화면에 보여 준다. students에는 300행이 모두 들어 있다.
# 설명: 실행 후 첫 행을 함께 읽는다. S001은 공학 3학년, 기숙사, exam_score 24, gpa 1.76이다.
# 설명: FileNotFoundError가 나면 노트북이 02_pandas 안에 있는지, data가 한 칸 위에 있는지, 철자가 맞는지 본다.
students = pd.read_csv('../data/students.csv')
students.head()
""")

md("""
* <b>shape</b>: 표의 모양을 <b>(행 수, 열 수)</b>로 알려 준다. 괄호 없이 쓴다.
  * students는 300행 12열이다. 학생 300명, 항목 12개라고 읽는다.
""")
code("""
# 설명: 앞 셀 화면에는 5행뿐이었다. 전체가 다 읽혔는지 여기서 확인한다.
# 설명: (300, 12)가 나오면 설문 300명이 모두 들어온 것이다. 표를 읽으면 크기부터 보는 습관을 잡아 준다.
# 설명: head()와 달리 괄호가 없다. students.shape()로 쓰면 TypeError가 난다고 짚는다.
students.shape
""")

md("""
* <b>info()</b>: 열마다 이름, 빈 값이 아닌 개수(<b>Non-Null Count</b>), 자료형(<b>Dtype</b>)을 한 번에 보여 준다.
* <b>자료형(dtype)</b>: 열에 든 값의 종류다. 그래프를 그릴 수 있는 열인지 여기서 먼저 확인한다.
  * <b>int64</b>: 정수(학년, 점수), <b>float64</b>: 소수(공부 시간, 수면 시간)
  * <b>str</b>: 글자(전공, 주거 형태). pandas 3부터 글자 열은 <b>str</b>로 표시된다. 예전 자료에서는 <b>object</b>로 나온다.
* sleep_hours는 285, sns_minutes는 294로 300보다 적다. 빈 값이 있다는 뜻이다(6)에서 다시 본다).
""")
code("""
# 설명: 출력이 길지만 Non-Null Count와 Dtype 두 칸만 위에서 아래로 훑으면 된다.
# 설명: 맨 위 300 entries와 다른 줄을 찾게 한다. 6번 sleep_hours, 7번 sns_minutes 두 줄이다.
# 설명: 앞 head()에서 sns_minutes가 50.0처럼 소수로 보였다. 빈 값이 있어 float64로 읽혔기 때문이다.
# 설명: Dtype이 object로 나오면 pandas 3보다 낮은 버전이다. 1강의 버전 확인 셀로 확인한다.
students.info()
""")

md("""
* cafe_sales.csv의 <b>date</b> 열은 날짜다. 그런데 그냥 읽으면 pandas는 이 열을 글자(<b>str</b>)로 읽는다.
  * 글자로 된 날짜는 '2025-03-01'이라는 문자열일 뿐이라, 날짜 순서나 간격을 모른다.
""")
code("""
# 설명: raw는 비교용으로 잠깐 쓰는 변수다. 바로 다음 셀에서 제대로 다시 읽는다.
# 설명: 실행 전에 짚는다. CSV 안의 값은 2025-03-01처럼 날짜 모양이다.
# 설명: 출력은 str 한 단어다. 눈에는 날짜로 보여도 pandas에게는 글자라는 점을 짚는다.
raw = pd.read_csv('../data/cafe_sales.csv')
print(raw['date'].dtype)
""")

md("""
* <b>parse_dates=['date']</b>: 읽을 때 date 열을 날짜 자료형(<b>datetime64</b>)으로 바꾼다.
  * 날짜 자료형이어야 3강 선 그래프에서 x축이 날짜 순서와 간격대로 그려진다.
* <b>dtypes</b>: 열별 자료형만 따로 보여 준다. cafe는 365행 14열이다.
  * 맨 아래 <b>dtype: object</b>는 dtypes 결과 자체의 자료형이라 열 자료형과 관계없다.
""")
code("""
# 설명: 앞 셀과 달라진 곳은 parse_dates 인자 하나다. 앞으로는 raw가 아니라 이 cafe를 쓴다.
# 설명: 노트북은 셀 마지막 줄 값만 자동으로 보여 준다. 그래서 shape에는 print를 붙였다.
# 설명: (365, 14)를 먼저 보고, date 줄이 str에서 datetime64[us]로 바뀐 것을 짚는다.
# 설명: [us]는 시간을 저장하는 단위 표시다. 지금은 몰라도 된다고 넘어간다.
cafe = pd.read_csv('../data/cafe_sales.csv', parse_dates=['date'])
print(cafe.shape)
cafe.dtypes
""")

md("""
* 앞 5행을 보면 하루가 한 줄이고, 손님 수(customers), 메뉴별 잔 수(americano·latte·ade·tea), 매출(sales)이 열로 있다.
  * year_month는 '2025-03' 같은 연-월 글자, period는 학사 기간(1학기·여름방학·2학기·겨울방학), exam_week는 시험 주간이면 1이다.
""")
code("""
# 설명: students에서 쓴 head()를 cafe에도 그대로 쓴다. 표가 달라도 확인 순서는 같다.
# 설명: 첫 행을 읽는다. 2025-03-01, 토요일, 1학기, 손님 169명이다.
# 설명: 위 설명에 없는 두 열을 말로 보탠다. avg_temp는 기온, rain은 비 온 날이면 1이다.
# 설명: 첫 행 sales 572000은 메뉴별 잔 수에 가격을 곱해 더한 값이다. 손님 수에서 나온 값이 아니다.
cafe.head()
""")

# 2) ------------------------------------------------------------------
md("""
#### <b>2) 시험 주간(exam_week == 1)만 골라 손님 수 보기</b>

* <b>df['열 이름']</b>: 열 하나를 고른다. 결과는 <b>Series</b>(이름표가 붙은 값 한 줄)다.
  * 열 이름은 철자·대소문자까지 같아야 한다. 틀리면 <b>KeyError</b>가 난다.
""")
code("""
# 설명: 표에서 값 한 줄만 꺼낸다. 뒤의 필터와 평균이 모두 이 모양에서 출발한다.
# 설명: 값 169, 157, 485는 앞 표의 customers 칸과 같다. 표 없이 그 칸만 나온 것이다.
# 설명: 출력 맨 아래 Name: customers, dtype: int64 줄이 Series라는 표시다. 다음 셀과 비교할 곳이다.
cafe['customers'].head()
""")

md("""
* <b>df[['열1', '열2']]</b>: 여러 열을 고른다. 대괄호 안에 <b>열 이름 리스트</b>를 넣으므로 대괄호가 두 겹이다.
  * 결과는 다시 DataFrame(표)이다.
""")
code("""
# 설명: 앞 셀과 대괄호 겹수가 다르다. 결과 모양을 나란히 비교한다.
# 설명: 출력에 열 제목 줄이 생기고 Name 줄이 사라졌다. 표로 돌아온 것이다.
# 설명: cafe['date', 'customers']처럼 한 겹으로 쓰면 KeyError가 난다. 자주 나오는 실수다.
cafe[['date', 'customers']].head()
""")

md("""
* <b>조건식</b>: <b>cafe['exam_week'] == 1</b>처럼 열과 값을 비교하면 행마다 <b>True/False</b>가 담긴 Series가 나온다.
  * <b>sum()</b>을 하면 True를 1로 세므로, 조건에 맞는 행의 개수가 된다. 시험 주간은 28일이다.
""")
code("""
# 설명: 필터를 쓰기 전에 조건식만 떼어 안을 들여다본다. 다음 셀 필터의 재료다.
# 설명: 앞 5행이 모두 False다. 3월 초가 시험 주간이 아닐 뿐이고 코드가 틀린 것이 아니다.
# 설명: True 개수 28은 시험 주간 4주에 7일씩을 더한 값이다.
is_exam = cafe['exam_week'] == 1
print(is_exam.head())
print('True 개수:', is_exam.sum())
""")

md("""
* <b>df[조건]</b>: 조건이 True인 행만 남긴 새 표를 만든다. 이것을 <b>필터</b>라고 한다.
  * 결과 표를 변수에 담아 두면 이어서 열을 고르거나 평균을 낼 수 있다.
""")
code("""
# 설명: 앞 셀의 조건식을 대괄호 안에 넣은 것이다. cafe[is_exam]으로 써도 같다.
# 설명: 출력 28이 앞 셀의 True 개수와 맞는 것을 확인한다.
# 설명: 왼쪽 행 번호가 0이 아니라 51부터다. 원래 표의 행 번호가 남기 때문이고, 첫 날은 2025-04-21 월요일이다.
# 설명: 필터는 새 표를 만든다. cafe는 365행 그대로다.
exam = cafe[cafe['exam_week'] == 1]
print(len(exam))
exam[['date', 'weekday', 'customers']].head()
""")

md("""
* 시험 주간과 나머지 날의 평균 손님 수를 비교한다. <b>mean()</b>은 평균, <b>round(값, 2)</b>는 소수 2자리 반올림이다.
  * 시험 주간 평균은 455.07명, 나머지 날은 252.4명이다.
""")
code("""
# 설명: exam은 앞 셀에서 만들었고 normal을 여기서 만든다. 28일과 337일을 더하면 365일이다.
# 설명: 출력 252.4는 252.40이다. 끝자리 0은 표시되지 않는다.
# 설명: 나머지 날에는 방학과 쉰 날이 섞여 있다. 학기 중 영업일끼리 비교하면 340.24명 대 455.07명, 1.34배다.
# 설명: 평균은 무엇과 비교하느냐에 따라 달라진다. 쉰 날 이야기는 6)에서 이어진다.
normal = cafe[cafe['exam_week'] == 0]
print('시험 주간:', round(exam['customers'].mean(), 2))
print('나머지 날:', round(normal['customers'].mean(), 2))
""")

md("""
* <b>df.loc[행 조건, 열 이름]</b>: 행과 열을 한 번에 고른다. 쉼표 앞이 행, 뒤가 열이다.
  * 위의 <b>exam[['date', 'weekday', 'customers']]</b>를 한 줄로 쓴 것과 같다.
  * 값을 <b>바꿀 때</b>도 <b>.loc</b>을 쓴다. 6)에서 직접 확인한다.
""")
code("""
# 설명: 앞에서 두 단계로 한 일을 한 줄로 쓴 것이다. 먼저 쉼표를 찾아 앞뒤를 나눠 읽는다.
# 설명: 출력은 앞의 exam 표와 같다. 행 번호 51부터, 손님 551, 652, 631, 537, 461이다.
# 설명: .loc 뒤는 소괄호가 아니라 대괄호다. 학생이 자주 헷갈리는 곳이다.
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
# 설명: 실행 전에 코드를 끊어 읽는다. 괄호 안 조건 둘을 &로 묶고, 바깥 students[...]가 필터다.
# 설명: 조건마다 괄호를 빼면 나오는 TypeError는 'str' and 'StringArray'라는 말만 있고 괄호 이야기가 없다. 그래서 막히기 쉽다.
# 설명: 실행 후 22명을 확인하고, 표 왼쪽 행 번호가 0, 7, 22처럼 띄엄띄엄인 것을 본다. 앞의 시험 주간 표와 같은 이유다.
eng_dorm = students[(students['major'] == '공학') & (students['housing'] == '기숙사')]
print(len(eng_dorm))
eng_dorm[['student_id', 'major', 'housing', 'study_hours']].head()
""")

md("""
* <b>|</b>(또는): 자취이거나 기숙사인 학생을 고른다. 둘 중 하나만 맞아도 남는다.
  * 자취 115명 + 기숙사 85명 = 200명이다.
""")
code("""
# 설명: 앞 셀과 달리 두 조건이 같은 housing 열이고 &가 |로 바뀌었다.
# 설명: 출력 200은 검산할 수 있다. 전체 300명에서 통학 100명을 빼면 200명이다.
# 설명: 같은 열 이름을 두 번 쓰니 코드가 길다. 다음 셀에서 줄인다고 예고한다.
dorm_or_alone = students[(students['housing'] == '자취') | (students['housing'] == '기숙사')]
len(dorm_or_alone)
""")

md("""
* <b>isin(리스트)</b>: 값이 리스트 안에 있으면 True다. 같은 열에 '또는'을 여러 번 쓸 때 짧게 쓴다.
  * 위의 | 조건과 결과(200명)가 같다.
""")
code("""
# 설명: 앞 셀과 코드 길이를 비교하고, 결과가 같은 200인 것을 확인한다.
# 설명: isin도 조건식이다. True/False를 만들고 바깥 대괄호가 필터한다.
# 설명: 값이 하나여도 리스트로 넣는다. 글자 하나만 넣으면 TypeError가 난다.
len(students[students['housing'].isin(['자취', '기숙사'])])
""")

md("""
* 고른 표에서도 열을 골라 평균을 낼 수 있다. 공학·기숙사 학생의 평균 공부 시간은 18.2시간으로, 전체 평균 12.61시간보다 길다.
""")
code("""
# 설명: 앞에서 만든 eng_dorm을 다시 쓴다. 필터 결과도 표라서 열 고르기와 평균이 그대로 된다.
# 설명: 18.2와 12.61을 읽되 기숙사 때문이라고 단정하지 않는다.
# 설명: 다음 4)에서 공학 전체 평균이 18.16으로 나온다. 그때 이 숫자와 비교한다고 예고한다.
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
# 설명: 여기부터는 행을 고르지 않고 범주별로 줄인다. 300행 표가 5행 표가 된다.
# 설명: 다섯 숫자를 더하면 300이다. 빠진 학생이 없다는 뜻이다.
# 설명: 왼쪽에 행 번호 대신 전공 이름이 온다. 이 전공 이름이 뒤에서 막대 그래프의 이름표가 된다.
students['major'].value_counts()
""")

md("""
* <b>groupby('묶을 열')['계산할 열'].mean()</b>: 묶을 열의 값이 같은 행끼리 모아, 계산할 열의 평균을 낸다.
  * 읽는 순서: 전공별로 묶어서 → 공부 시간 열을 골라 → 평균
  * 계산할 열을 고르지 않고 <b>students.groupby('major').mean()</b>을 하면 TypeError가 난다. 글자 열(student_id·housing)은 평균을 낼 수 없기 때문이다.
""")
code("""
# 설명: 코드가 길어 보이면 왼쪽부터 세 덩어리로 끊어 읽는다.
# 설명: 출력에서 두 가지 불편을 찾게 한다. 18.157500처럼 소수가 길고, 큰 순서로 놓여 있지 않다.
# 설명: 다음 셀에서 둘 다 고친다.
# 설명: 열을 고르지 않으면 TypeError: dtype 'str' does not support operation 'mean'이 나온다. 메시지의 str이 글자 열이라는 뜻이다.
students.groupby('major')['study_hours'].mean()
""")

md("""
* 결과는 전공 이름의 가나다순이다. 비교하기 쉽게 정렬한다.
  * <b>round(2)</b>: 소수 2자리 반올림, <b>sort_values(ascending=False)</b>: 큰 값부터
* 공학 18.16시간이 가장 길고 예체능 6.28시간이 가장 짧다. 이 표가 4강 막대 그래프의 재료가 된다.
""")
code("""
# 설명: 앞 셀 코드 뒤에 round와 sort_values를 점으로 이어 붙였다. 왼쪽부터 차례로 적용된다.
# 설명: 첫 줄은 변수에 담기만 하므로 화면에 안 나온다. 둘째 줄 변수 이름이 출력을 만든다.
# 설명: 위에서 아래로 18.16에서 6.28까지 내려간다. 공학이 예체능의 약 2.9배다.
# 설명: 4강에서 같은 코드로 이 표를 다시 만들어 막대로 그린다.
study_by_major = students.groupby('major')['study_hours'].mean().round(2).sort_values(ascending=False)
study_by_major
""")

md("""
* <b>agg(['mean', 'count'])</b>: 여러 계산을 한 번에 한다. 결과는 계산마다 열이 하나씩 생긴 표다.
  * <b>sort_values('mean', ascending=False)</b>: 표는 정렬할 열 이름을 넣는다.
  * count 열은 value_counts()의 학생 수와 같다.
""")
code("""
# 설명: 평균이 몇 명의 평균인지 함께 보려고 쓴다. 인원이 다른 전공을 비교할 때 필요하다.
# 설명: agg에 넣은 'mean', 'count'가 그대로 열 이름이 된다. 그래서 sort_values에 'mean'을 쓸 수 있다.
# 설명: count 열을 더하면 300이다. 예체능 40명이 가장 적다.
students.groupby('major')['study_hours'].agg(['mean', 'count']).round(2).sort_values('mean', ascending=False)
""")

# 5) ------------------------------------------------------------------
md("""
#### <b>5) 기간(period)별·요일별 평균 손님 수</b>

* 같은 방법으로 cafe를 학사 기간별로 묶어 평균 손님 수를 낸다.
  * 결과가 1학기 → 2학기 → 겨울방학 → 여름방학 순이다. 시간 순서가 아니라 <b>가나다순</b>이다.
""")
code("""
# 설명: cafe에도 같은 방법을 쓴다. 표와 열 이름만 바뀌었다.
# 설명: 출력을 위에서 아래로 따라 읽게 한다. 1학기 바로 아래가 여름방학이 아니라 2학기다.
# 설명: 값은 맞고 순서만 시간과 다르다. 코드가 틀린 것이 아니다.
# 설명: 이 순서로 선을 그으면 여름방학이 맨 끝에 온다. 다음 셀에서 바로잡는다.
cafe.groupby('period')['customers'].mean().round(2)
""")

md("""
* <b>reindex(순서 리스트)</b>: 결과의 행을 리스트에 적은 순서로 다시 놓는다.
  * 시간 순서(1학기 → 여름방학 → 2학기 → 겨울방학)로 두어야 그래프로 옮길 때 흐름이 바르게 보인다.
* 1학기 364.00명, 2학기 332.91명으로 학기 중이 높고, 여름방학 149.11명, 겨울방학 136.30명으로 방학이 낮다.
""")
code("""
# 설명: 출력을 앞 셀과 나란히 놓는다. 값은 그대로이고 줄 순서만 바뀌었다.
# 설명: 이제 위에서 아래로 364.00, 149.11, 332.91, 136.30이다. 학기와 방학이 번갈아 오르내리는 모양이 읽힌다.
# 설명: 리스트 철자가 데이터와 다르면 그 줄이 NaN이 된다. '여름 방학'처럼 띄어 쓰면 그렇다.
period_order = ['1학기', '여름방학', '2학기', '겨울방학']
customers_by_period = cafe.groupby('period')['customers'].mean().round(2).reindex(period_order)
customers_by_period
""")

md("""
* 요일도 가나다순(금·목·수·월…)으로 나오므로 월~일 순서로 다시 놓는다.
* 수요일 374.10명이 가장 많고, 일요일 113.79명이 가장 적다. 주말에 크게 떨어진다.
  * 이 평균에는 카페가 쉰 날의 0이 섞여 있다. 6)에서 확인한다.
""")
code("""
# 설명: 앞 셀과 같은 틀이다. 묶을 열과 순서 리스트만 바꿨다.
# 설명: 금요일 267.42에서 토요일 137.74로 절반 가까이 떨어지는 곳을 짚는다.
# 설명: 수요일 374.10과 일요일 113.79를 기억해 두게 한다. 맨 뒤 셀에서 이 표와 비교한다.
weekday_order = ['월', '화', '수', '목', '금', '토', '일']
customers_by_weekday = cafe.groupby('weekday')['customers'].mean().round(2).reindex(weekday_order)
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
# 설명: 이제 만든 표를 믿어도 되는지 점검한다. 그래프로 옮기기 전 마지막 단계다.
# 설명: sum()은 앞의 is_exam.sum()과 같은 원리다. True를 1로 세므로 빈 칸 수가 된다.
# 설명: 1)의 info()와 맞춰 본다. 300에서 285를 빼면 15, 294를 빼면 6이다.
# 설명: 두 열이 함께 빈 행은 없다. 빈 값이 있는 학생은 모두 21명이다.
students.isna().sum()
""")

md("""
* <b>dropna(subset=['열'])</b>: 그 열이 비어 있는 행을 뺀 <b>새 표</b>를 돌려준다. 원래 students는 그대로다.
  * 수면 시간을 그릴 때는 sleep_hours가 빈 15행을 빼고 285행으로 그린다.
""")
code("""
# 설명: subset을 적는 이유를 말한다. 안 적으면 sns_minutes만 빈 6행까지 빠져 279행이 된다.
# 설명: 출력은 왼쪽이 원본, 오른쪽이 새 표다. (300, 12)가 그대로인 것을 먼저 보여 준다.
# 설명: 새 표를 변수에 담지 않으면 결과가 사라진다. 그래서 sleep_ok에 담았다.
sleep_ok = students.dropna(subset=['sleep_hours'])
print(students.shape, sleep_ok.shape)
""")

md("""
* <b>이상치</b>: 다른 값과 동떨어진 값이다. <b>describe()</b>로 개수·평균·최솟값·사분위수·최댓값을 보면 찾기 쉽다.
  * <b>25% · 50% · 75%</b>: 값을 작은 순으로 줄 세웠을 때 4분의 1, 가운데, 4분의 3 자리의 값이다.
  * sns_minutes는 75%가 180분인데 최댓값(max)이 900분이다. commute_minutes는 75%가 50분인데 최댓값이 180분이다.
""")
code("""
# 설명: 출력의 아래 두 줄, 75%와 max만 비교한다. 다른 줄은 지금 다 읽지 않아도 된다.
# 설명: sleep_hours는 7.20과 8.60으로 차이가 작다. 튀는 값이 없는 열의 모습이다.
# 설명: sns_minutes는 180에서 900으로 5배, commute_minutes는 50에서 180으로 3.6배다.
# 설명: 맨 위 count 285, 294, 300은 앞 셀의 빈 칸 수와 맞는다.
students[['sleep_hours', 'sns_minutes', 'commute_minutes']].describe().round(2)
""")

md("""
* 최댓값이 누구인지 필터로 찾는다. SNS를 하루 500분 넘게 쓴 학생은 <b>S026</b> 한 명(900분)이다.
  * 900분은 하루 15시간이다. 그다음으로 큰 값은 480분이다.
""")
code("""
# 설명: 앞 표의 900이 누구인지 찾는다. 500은 그다음 값 480보다 크게 잡은 경계다.
# 설명: 출력은 한 행이다. 행 번호 25인 S026, 자연과학, 자취, 900.0이다.
# 설명: 출력에 없는 열을 말로 보탠다. 이 학생의 sleep_hours는 4.3이다. 지우지 않고 찾아 둔다.
students[students['sns_minutes'] >= 500][['student_id', 'major', 'housing', 'sns_minutes']]
""")

md("""
* <b>sort_values('열', ascending=False).head(3)</b>: 큰 값부터 3행을 본다.
  * 통학 시간 1위는 <b>S037</b>의 180분이고, 2위는 114분으로 차이가 크다.
* 이상치는 바로 지우지 않는다. 실제로 그런 학생일 수도, 입력 실수일 수도 있으므로 찾아서 적어 둔다.
  * 6강 박스플롯에서 이 값들이 따로 떨어진 점으로 다시 보인다.
""")
code("""
# 설명: 이번에는 필터 대신 정렬로 찾는다. 경계값을 정하지 않아도 위에서부터 볼 수 있다.
# 설명: S037 180, S167 114, S087 108이다. 2위와 3위는 6분 차이인데 1위와 2위는 66분 차이다.
# 설명: 왼쪽 행 번호가 36, 166, 86으로 섞여 있다. 정렬해도 원래 행 번호가 남는다.
students.sort_values('commute_minutes', ascending=False).head(3)[['student_id', 'housing', 'commute_minutes']]
""")

md("""
* cafe에는 빈 값이 없다. 대신 손님 수가 <b>0</b>인 날이 있다.
  * 7일 모두 판매 값이 0이고, 날짜가 2025년 추석 연휴(10/5~10/8)와 2026년 설 연휴(2/16~2/18)다.
* 0은 잘못 들어간 값이 아니라 <b>카페가 쉰 날의 실제 값</b>이다. 지우지 않고 휴무일이라고 표시해 둔다.
""")
code("""
# 설명: cafe에는 빈 값이 없어 isna()로는 아무것도 안 잡힌다. 그래서 값이 0인 행을 직접 찾는다.
# 설명: 실행 후 날짜를 보여 주고 무슨 날인지 묻는다. 10/5~10/7이 추석, 10/8이 대체공휴일, 2/16~2/18이 설 연휴다.
# 설명: 요일을 세어 둔다. 월·화·수 2일씩, 일 1일이고 목·금·토는 없다. 맨 뒤 셀에서 이 차이가 드러난다.
cafe[cafe['customers'] == 0][['date', 'weekday', 'period', 'customers', 'sales']]
""")

md("""
* 먼저 모든 날을 '영업'으로 적은 status 열을 만들고, 손님이 0인 날만 '휴무'로 바꿔 본다.
* 아래처럼 <b>필터한 표에 다시 열을 골라 값을 넣는 방식</b>(연쇄 할당)은 원래 cafe를 바꾸지 못한다.
  * pandas 3은 <b>Copy-on-Write</b>(고른 결과는 원본과 따로인 복사본처럼 동작) 방식이라, 값이 복사본에만 들어간다.
  * <b>ChainedAssignmentError</b> 경고가 나오고, '휴무'가 0개 그대로다. 이 경고는 일부러 보여 주는 것이다.
""")
code("""
# 설명: 실행 전에 예고한다. 이 셀은 일부러 실패한다. 무엇이 어떻게 실패하는지 본다.
# 설명: 첫 줄의 status 열은 잘 만들어진다. 문제는 둘째 줄이다.
# 설명: 경고를 읽어 준다. Such chained assignment never works, Try using .loc 두 곳이면 충분하다.
# 설명: 오류가 아니라 경고라서 끝까지 실행된다. 출력 영업 365에 휴무 줄이 없는 것을 짚는다.
cafe['status'] = '영업'
cafe[cafe['customers'] == 0]['status'] = '휴무'
cafe['status'].value_counts()
""")

md("""
* <b>df.loc[행 조건, '열'] = 값</b>: 행과 열을 한 번에 지정해 원래 표의 값을 바꾼다. 값을 바꿀 때는 이 방식만 쓴다.
  * 이제 휴무 7일, 영업 358일이다.
""")
code("""
# 설명: 앞 셀 둘째 줄과 비교한다. 대괄호를 두 번 쓰던 것을 .loc 대괄호 하나에 모았다.
# 설명: 출력 영업 358, 휴무 7을 앞 셀의 영업 365와 나란히 본다. 합은 365로 같다.
# 설명: 앞 셀을 건너뛰고 실행하면 휴무 7만 나온다. status의 나머지 칸이 비기 때문이다.
cafe.loc[cafe['customers'] == 0, 'status'] = '휴무'
cafe['status'].value_counts()
""")

md("""
* 영업한 날만 골라 요일별 평균 손님 수를 다시 낸다.
  * 휴무일이 있던 월·화·수·일요일의 평균이 올라간다. 수요일은 374.10 → 389.06명이다.
  * 쉰 날을 넣을지 뺄지는 질문에 따라 정한다. 표시해 두면 둘 다 바로 계산할 수 있다.
* 오늘 만든 표(value_counts·groupby 결과)를 3강부터 그래프로 옮긴다.
""")
code("""
# 설명: 앞에서 표시해 둔 status로 필터한다. weekday_order는 5)에서 만든 리스트를 다시 쓴다.
# 설명: 5)의 표와 나란히 본다. 월 327.50→340.60, 화 346.21→360.06, 수 374.10→389.06, 일 113.79→116.02다.
# 설명: 목·금·토는 311.38, 267.42, 137.74 그대로다. 쉰 날이 없던 요일이다. 수요일 최고, 일요일 최저 순위도 그대로다.
# 설명: 읽고, 고르고, 묶고, 확인한 순서를 되짚는다. 다음 시간에는 Figure·Axes로 표를 선 그래프로 옮긴다.
open_days = cafe[cafe['status'] == '영업']
open_days.groupby('weekday')['customers'].mean().round(2).reindex(weekday_order)
""")

nb = new_notebook(cells=cells)
nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
nb.metadata["language_info"] = {"name": "python"}
nbformat.validate(nb)
OUT.parent.mkdir(parents=True, exist_ok=True)
nbformat.write(nb, OUT)
print(OUT)
