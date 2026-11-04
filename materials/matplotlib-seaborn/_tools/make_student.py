"""강사용 노트북 → 학생용 노트북 변환.

사용법:
    python make_student.py 강사용.ipynb 학생용.ipynb

규칙
- 마크다운 셀은 그대로 둔다.
- 코드 셀의 코드는 남긴다. 학생은 코드를 입력하지 않고 셀을 하나씩 실행한다.
- 강사용 설명 주석('# 설명:'으로 시작하는 줄)과 첫 줄 '# keep' 표시는 지운다.
- 모든 코드 셀의 출력과 실행 번호를 지운다.
"""
import sys
from pathlib import Path

import nbformat

KEEP = "# keep"
NOTE = "# 설명:"


def convert(src: Path, dst: Path) -> None:
    nb = nbformat.read(src, as_version=4)
    kept = notes = 0
    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        lines = cell.source.splitlines()
        if lines and lines[0].strip() == KEEP:
            lines = lines[1:]
        code = [line for line in lines if not line.strip().startswith(NOTE)]
        notes += len(lines) - len(code)
        cell.source = "\n".join(code).strip()
        kept += 1
        cell.outputs = []
        cell.execution_count = None
        cell.metadata.pop("execution", None)
    nb.metadata.pop("widgets", None)
    nbformat.validate(nb)
    dst.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(nb, dst)
    print(f"{dst.name}: 코드 셀 {kept}개, 지운 설명 주석 {notes}줄")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("사용법: python make_student.py 강사용.ipynb 학생용.ipynb")
    convert(Path(sys.argv[1]), Path(sys.argv[2]))
