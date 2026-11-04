# Matplotlib·Seaborn 데이터 시각화 - 실습 파일

차시마다 폴더가 하나씩 있습니다. 폴더 안에는 `강사용`(코드와 실행 결과 포함, 배포하지 않음)과 `학생용`(코드 셀 비움) 노트북이 한 벌씩 있습니다. 두 노트북은 셀 구성과 마크다운이 같고, 학생용에는 설정 셀과 데이터 읽기 셀(`# keep`)만 코드가 남아 있습니다.

교안 전체와 촬영 전 확인할 것은 노션 [과정 설계 페이지](https://app.notion.com/p/f0c2018657fa4cc1a0531f4cdf24a455)에 있습니다.

| 폴더 | 교안 | 쓰는 데이터 |
| --- | --- | --- |
| 01_환경설정 | [시각화1 : 개발 환경과 첫 그래프](https://app.notion.com/p/48e435fcbd9d8258a00981abeda3719c) | 없음 (리스트로 첫 그래프) |
| 02_pandas | [시각화2 : pandas로 데이터 다루기](https://app.notion.com/p/aa7435fcbd9d82f5a63201064c38b026) | students, cafe_sales |
| 03_선그래프 | [시각화3 : Figure·Axes와 선 그래프](https://app.notion.com/p/4e6435fcbd9d837cb5e90198011b6e3a) | cafe_sales |
| 04_기본그래프 | [시각화4 : 막대·산점도·히스토그램](https://app.notion.com/p/bf8435fcbd9d82aaa3e801d9372ea23a) | students, cafe_sales |
| 05_꾸미기 | [시각화5 : 꾸미기와 여러 그래프](https://app.notion.com/p/ba8435fcbd9d83ea83e6814a6dfc812e) | students, cafe_sales |
| 06_분포 | [시각화6 : Seaborn과 분포 그래프](https://app.notion.com/p/e41435fcbd9d8363b917818aa86943c2) | students |
| 07_범주비교 | [시각화7 : 범주 비교 그래프](https://app.notion.com/p/d64435fcbd9d8393915f815ccb0dd7fa) | students, cafe_sales |
| 08_관계추세 | [시각화8 : 관계와 추세 그래프](https://app.notion.com/p/53d435fcbd9d8290bcba81510898e71a) | students, cafe_sales |
| 09_히트맵다중 | [시각화9 : 히트맵과 다중 그래프](https://app.notion.com/p/e34435fcbd9d83df949e8144de077a25) | students, cafe_sales |
| 10_미니프로젝트 | [시각화10 : 미니 프로젝트 - 질문하고 그래프로 답하기](https://app.notion.com/p/cf4435fcbd9d82eb855e818034ed3176) | students, cafe_sales |

`data/`의 두 CSV는 가상 데이터입니다. `students.csv`(학생 300명, 12열)와 `cafe_sales.csv`(2025-03-01~2026-02-28, 365일, 14열)이고, 교안 정답 숫자는 `_tools/data_facts.md`에 있습니다.

## 배포(압축)

`_배포/NN_주제_실습.zip`이 차시별 배포 파일입니다. zip 하나에는 그 차시 학생용 노트북과 `data/` 폴더가 들어 있습니다. 학생이 프로젝트 폴더(`시각화실습/`, 1차시에 만듦)에 풀면 노트북의 `../data/` 경로가 그대로 맞습니다.

- 강사용 노트북과 `05_꾸미기/output/`·`10_미니프로젝트/output/`(저장 실습 결과)은 넣지 않습니다.
- 노트북을 다시 만들었으면 `_tools/make_zips.py`로 zip을 다시 만듭니다.

## 다시 만들기

실행 환경은 `_tools/.venv`(Python 3.11, matplotlib 3.11.2, seaborn 0.13.2, pandas 3.1.0)입니다. git에는 올라가지 않으니 없으면 새로 만듭니다.

```bash
cd _tools
python -m venv .venv
.venv/Scripts/python -m pip install matplotlib==3.11.2 seaborn==0.13.2 pandas==3.1.0 nbformat nbconvert ipykernel
```

- 데이터: `make_data.py`로 만들고(시드 고정), `check_data.py`로 의도한 특징을 확인한 뒤 `data_facts.md`를 다시 씁니다.
- 노트북: `build_NN.py`로 강사용을 만들고, 차시 폴더에서 `python -m jupyter nbconvert --to notebook --execute --inplace NN_주제_강사용.ipynb`로 실행해 출력을 저장합니다. 그다음 `make_student.py 강사용 학생용`으로 학생용을 만듭니다. 학생용은 손으로 고치지 않습니다.
- 강사용 노트북의 출력은 제작 PC에서 실행한 것입니다. 경고 문구에 제작 PC 경로가 찍혀 있으니, 촬영 전에 강의용 프로젝트 폴더에서 다시 실행합니다.
