# Matplotlib·Seaborn 데이터 시각화 - 실습 파일

차시마다 폴더가 하나씩 있습니다. 폴더 안에는 `강사용`(코드와 실행 결과 포함, 배포하지 않음)과 `학생용`(코드 셀 비움) 노트북이 한 벌씩 있습니다. 두 노트북은 셀 구성과 마크다운이 같고, 학생용에는 설정 셀과 데이터 읽기 셀(`# keep`)만 코드가 남아 있습니다.

교안 전체와 촬영 전 확인할 것은 노션 [과정 설계 페이지](https://app.notion.com/p/f0c2018657fa4cc1a0531f4cdf24a455)에 있습니다.

| 폴더 | 교안 | 쓰는 데이터 |
| --- | --- | --- |
| 01_환경설정 | [1차시 : 개발 환경과 첫 그래프](https://app.notion.com/p/8b41aa50ced24310945231b1b91d7c94) | 없음 (리스트로 첫 그래프) |
| 02_pandas | [2차시 : pandas로 데이터 다루기](https://app.notion.com/p/e3300ef79ac74888b02a7e2209315ede) | students, cafe_sales |
| 03_선그래프 | [3차시 : Figure·Axes와 선 그래프](https://app.notion.com/p/0851978d307b4566b93b53de906106d1) | cafe_sales |
| 04_기본그래프 | [4차시 : 막대·산점도·히스토그램](https://app.notion.com/p/e0c7903d80314222a5d7265c11a964e2) | students, cafe_sales |
| 05_꾸미기 | [5차시 : 꾸미기와 여러 그래프](https://app.notion.com/p/cbc840f40e2c4f46b7c02f16ad2f1c8d) | students, cafe_sales |
| 06_분포 | [6차시 : Seaborn과 분포 그래프](https://app.notion.com/p/fffe90859b5b4100ae245a00be2be9bd) | students |
| 07_범주비교 | [7차시 : 범주 비교 그래프](https://app.notion.com/p/c66f8497639447ba9a7ac24293e9637e) | students, cafe_sales |
| 08_관계추세 | [8차시 : 관계와 추세 그래프](https://app.notion.com/p/6c7ecfa4358d468da48c86c4e1da180e) | students, cafe_sales |
| 09_히트맵다중 | [9차시 : 히트맵과 다중 그래프](https://app.notion.com/p/73c483b747be4dd9a75e9011e31cf6cb) | students, cafe_sales |
| 10_미니프로젝트 | [10차시 : 미니 프로젝트 - 질문하고 그래프로 답하기](https://app.notion.com/p/45a0bbea549e48f2ad9b38b5a9b4b482) | students, cafe_sales |

`data/`의 두 CSV는 가상 데이터입니다. `students.csv`(학생 300명, 12열)와 `cafe_sales.csv`(2025-03-01~2026-02-28, 365일, 14열)이고, 교안 정답 숫자는 `_tools/data_facts.md`에 있습니다.

## 배포(압축)

`_배포/NN_주제_실습.zip`이 차시별 배포 파일입니다. zip 하나에는 그 차시 학생용 노트북, `data/` 폴더, `requirements.txt`가 들어 있습니다. 학생이 프로젝트 폴더(`시각화실습/`, 1차시에 만듦)에 풀면 노트북의 `../data/` 경로가 그대로 맞습니다.

- 강사용 노트북과 `05_꾸미기/output/`·`10_미니프로젝트/output/`(저장 실습 결과)은 넣지 않습니다.
- 노트북을 다시 만들었으면 `_tools/make_zips.py`로 zip을 다시 만듭니다.

## 다시 만들기

실행 환경은 `_tools/.venv`(Python 3.11)이고, 패키지 버전은 `requirements.txt`에 있습니다. 학생도 같은 파일로 설치합니다. `.venv`는 git에 올라가지 않으니 없으면 새로 만듭니다.

```bash
cd _tools
python -m venv .venv
.venv/Scripts/python -m pip install -r ../requirements.txt nbformat nbconvert
```

- 데이터: `make_data.py`로 만들고(시드 고정), `check_data.py`로 의도한 특징을 확인한 뒤 `data_facts.md`를 다시 씁니다.
- 노트북: `build_NN.py`로 강사용을 만들고, 차시 폴더에서 `python -m jupyter nbconvert --to notebook --execute --inplace NN_주제_강사용.ipynb`로 실행해 출력을 저장합니다. 그다음 `make_student.py 강사용 학생용`으로 학생용을 만듭니다. 학생용은 손으로 고치지 않습니다.
- 강사용 노트북의 출력은 제작 PC에서 실행한 것입니다. 경고 문구에 제작 PC 경로가 찍혀 있으니, 촬영 전에 강의용 프로젝트 폴더에서 다시 실행합니다.
