# Matplotlib·Seaborn 데이터 시각화 - 실습 파일

실습은 Google Colab에서 합니다. 차시마다 폴더가 하나씩 있습니다. 폴더 안에는 `NN_주제_강사용.ipynb`(마크다운, 코드, 코드별 설명 주석, 실행 결과, 배포하지 않음)와 학생용 `NN_주제.ipynb`(마크다운과 빈 코드 칸)가 한 벌씩 있습니다. 두 노트북은 셀 구성과 마크다운이 같습니다. 학생용에는 맨 위 준비 셀만 코드가 있고, 나머지 코드는 강의를 따라 입력합니다.

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

## 배포

`_배포/NN_주제.ipynb`가 차시별 배포 파일입니다. 학생은 이 파일을 받아 Colab에 업로드합니다. 폰트 설치와 데이터 내려받기는 준비 셀이 맡습니다.

- 준비 셀의 데이터 주소는 `_tools/colab_setup.py`의 `DATA_REF` 브랜치를 가리킵니다. 브랜치를 합치거나 지우기 전에 이 값을 바꾸고 노트북을 다시 만듭니다.
- 노트북을 다시 만들었으면 `_tools/make_dist.py`로 배포 파일을 다시 모읍니다.

## 다시 만들기

제작 환경은 `_tools/.venv`(Python 3.11)입니다. `requirements.txt`는 학생용이 아니라 제작 환경을 Colab과 같은 패키지 버전으로 맞추는 파일입니다. Colab 버전은 [공개 목록](https://github.com/googlecolab/backend-info)에서 확인합니다. `.venv`와 `_tools/NanumGothic.ttf`는 git에 올라가지 않으니 없으면 새로 준비합니다.

```bash
cd _tools
python -m venv .venv
.venv/Scripts/python -m pip install -r ../requirements.txt nbformat nbconvert
```

- 데이터: `make_data.py`로 만들고(시드 고정), `check_data.py`로 의도한 특징을 확인한 뒤 `data_facts.md`를 다시 씁니다.
- 노트북: `_tools/rebuild_all.sh`(차시 번호를 주면 그 차시만, 예: `bash rebuild_all.sh 03`)를 실행합니다. `build_NN.py`로 강사용을 만들고, `run_notebook.py`로 임시 폴더에서 실행해 출력을 저장하고, `make_student.py`로 학생용을 만듭니다. 학생용은 손으로 고치지 않습니다. 코드와 설명 주석은 `build_NN.py`에서 고칩니다.
- 강사용 노트북의 출력은 제작 PC에서 실행한 것입니다. 촬영 전에 실제 Colab에서 다시 실행합니다.
