"""학생 배포 파일을 모은다.

학생은 차시별 학생용 노트북을 Colab에 업로드하고, data 폴더를 구글 드라이브의 실습 폴더에 올린다.
10차시 전에 10차시_추가데이터/bike_rentals.csv를 드라이브의 data 폴더에 추가로 올린다.
강사용 노트북은 넣지 않는다.

사용: python make_dist.py   (결과: ../_배포/NN_주제.ipynb, ../_배포/data/)
"""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / '_배포'


def main():
    OUT.mkdir(exist_ok=True)
    for lesson in sorted(p for p in ROOT.iterdir() if p.is_dir() and p.name[:2].isdigit()):
        student = lesson / f'{lesson.name}.ipynb'
        shutil.copy2(student, OUT / student.name)
        print(student.name)
    # 처음에 받는 data 폴더에는 1~9차시용 두 파일만 넣고, 10차시 추가 데이터는 따로 둔다.
    (OUT / 'data').mkdir(exist_ok=True)
    for name in ('students.csv', 'cafe_sales.csv'):
        shutil.copy2(ROOT / 'data' / name, OUT / 'data' / name)
    (OUT / 'data' / 'bike_rentals.csv').unlink(missing_ok=True)
    extra = OUT / '10차시_추가데이터'
    extra.mkdir(exist_ok=True)
    shutil.copy2(ROOT / 'data' / 'bike_rentals.csv', extra / 'bike_rentals.csv')


if __name__ == '__main__':
    main()
