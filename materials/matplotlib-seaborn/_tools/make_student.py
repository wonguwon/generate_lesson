"""강사용 노트북 → 학생용 노트북 변환.

사용법:
    python make_student.py 강사용.ipynb 학생용.ipynb

규칙
- 마크다운 셀은 그대로 둔다.
- 코드 셀은 빈 칸으로 둔다. 학생은 강의를 따라 코드를 입력한다.
- 첫 줄이 '# keep'인 셀(준비 셀)만 코드를 남기고 그 표시를 지운다.
- 모든 코드 셀의 출력과 실행 번호를 지운다.
"""
import sys
from pathlib import Path

import nbformat

KEEP = "# keep"


def convert(src: Path, dst: Path) -> None:
    nb = nbformat.read(src, as_version=4)
    kept = emptied = 0
    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        lines = cell.source.splitlines()
        if lines and lines[0].strip() == KEEP:
            cell.source = "\n".join(lines[1:]).strip()
            kept += 1
        else:
            cell.source = ""
            emptied += 1
        cell.outputs = []
        cell.execution_count = None
        cell.metadata.pop("execution", None)
    nb.metadata.pop("widgets", None)
    nbformat.validate(nb)
    dst.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(nb, dst)
    print(f"{dst.name}: 남긴 셀 {kept}개, 비운 코드 셀 {emptied}개")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("사용법: python make_student.py 강사용.ipynb 학생용.ipynb")
    convert(Path(sys.argv[1]), Path(sys.argv[2]))
