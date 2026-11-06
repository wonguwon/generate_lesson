"""강사용 노트북 → 학생용 노트북 변환.

사용법:
    python make_student.py 강사용.ipynb 학생용.ipynb

규칙
- 마크다운 셀은 그대로 둔다.
- 코드 셀은 빈 칸으로 둔다. 학생은 강의를 따라 코드를 입력한다.
- student_hints.py에 있는 차시는 빈 칸에 할 일 주석을 한 줄 넣는다.
- 첫 줄이 '# keep'인 셀(준비 셀)만 코드를 남기고 그 표시를 지운다.
- 모든 코드 셀의 출력과 실행 번호를 지운다.
"""
import sys
from pathlib import Path

import nbformat

from student_hints import HINTS

KEEP = "# keep"


def convert(src: Path, dst: Path) -> None:
    nb = nbformat.read(src, as_version=4)
    hints = HINTS.get(dst.name[:2], [])
    kept = emptied = 0
    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        lines = cell.source.splitlines()
        if lines and lines[0].strip() == KEEP:
            cell.source = "\n".join(lines[1:]).strip()
            kept += 1
        else:
            cell.source = f"# {hints[emptied]}" if emptied < len(hints) else ""
            emptied += 1
        cell.outputs = []
        cell.execution_count = None
        cell.metadata.pop("execution", None)
    if hints and len(hints) != emptied:
        sys.exit(f"{dst.name}: 주석 {len(hints)}개와 코드 칸 {emptied}개가 맞지 않습니다")
    nb.metadata.pop("widgets", None)
    nbformat.validate(nb)
    dst.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(nb, dst)
    print(f"{dst.name}: 남긴 셀 {kept}개, 비운 코드 셀 {emptied}개")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("사용법: python make_student.py 강사용.ipynb 학생용.ipynb")
    convert(Path(sys.argv[1]), Path(sys.argv[2]))
