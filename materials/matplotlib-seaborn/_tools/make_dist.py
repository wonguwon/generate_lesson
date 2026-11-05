"""학생 배포 파일을 모은다.

학생은 차시별 학생용 노트북을 Colab에 업로드하고, data 폴더를 구글 드라이브의 실습 폴더에 올린다.
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
    shutil.copytree(ROOT / 'data', OUT / 'data', dirs_exist_ok=True)


if __name__ == '__main__':
    main()
