"""강사용 노트북 → 학생용 노트북 변환.

사용법:
    python make_student.py 강사용.ipynb 학생용.ipynb

규칙
- 마크다운 셀은 그대로 둔다.
- 코드 셀은 내용을 비운다. 단 첫 줄이 '# keep'인 셀은 코드를 남긴다
  (첫 줄 '# keep' 표시는 학생용에서 지운다).
- 모든 코드 셀의 출력과 실행 번호를 지운다.
"""
import sys
from pathlib import Path

import nbformat

KEEP = "# keep"


def convert(src: Path, dst: Path) -> None:
    nb = nbformat.read(src, as_version=4)
    kept = cleared = 0
    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        lines = cell.source.splitlines()
        if lines and lines[0].strip() == KEEP:
            cell.source = "\n".join(lines[1:]).lstrip("\n")
            kept += 1
        else:
            cell.source = ""
            cleared += 1
        cell.outputs = []
        cell.execution_count = None
        cell.metadata.pop("execution", None)
    nb.metadata.pop("widgets", None)
    nbformat.validate(nb)
    dst.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(nb, dst)
    print(f"{dst.name}: 남긴 코드 셀 {kept}개, 비운 코드 셀 {cleared}개")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("사용법: python make_student.py 강사용.ipynb 학생용.ipynb")
    convert(Path(sys.argv[1]), Path(sys.argv[2]))
