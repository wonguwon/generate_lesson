"""차시별 학생 배포 zip을 만든다.

zip 하나 = 그 차시 학생용 노트북 + data/ 폴더 + requirements.txt.
학생이 프로젝트 폴더(시각화실습/)에 풀면 `NN_주제/NN_주제_학생용.ipynb`, `data/`, `requirements.txt`가 생기고,
노트북의 `../data/파일.csv` 경로가 그대로 맞는다.
강사용 노트북과 output/ 폴더(5·10차시 저장 결과)는 넣지 않는다.

사용: python make_zips.py   (결과: ../_배포/NN_주제_실습.zip)
"""
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / '_배포'


def main():
    OUT.mkdir(exist_ok=True)
    data_files = sorted((ROOT / 'data').glob('*.csv'))
    for lesson in sorted(p for p in ROOT.iterdir() if p.is_dir() and p.name[:2].isdigit()):
        student = lesson / f'{lesson.name}_학생용.ipynb'
        zip_path = OUT / f'{lesson.name}_실습.zip'
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
            z.write(student, f'{lesson.name}/{student.name}')
            for f in data_files:
                z.write(f, f'data/{f.name}')
            z.write(ROOT / 'requirements.txt', 'requirements.txt')
        with zipfile.ZipFile(zip_path) as z:
            names = z.namelist()
        print(zip_path.name, names)


if __name__ == '__main__':
    main()
