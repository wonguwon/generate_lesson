"""학생 배포 파일을 모은다.

학생은 차시별 학생용 노트북만 받아 Colab에 업로드한다. 데이터는 준비 셀이 내려받는다.
강사용 노트북은 넣지 않는다.

사용: python make_dist.py   (결과: ../_배포/NN_주제.ipynb)
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


if __name__ == '__main__':
    main()
