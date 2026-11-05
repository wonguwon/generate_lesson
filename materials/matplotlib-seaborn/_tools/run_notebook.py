"""강사용 노트북을 Colab과 같은 패키지 버전으로 실행해 출력을 저장한다.

사용법: python run_notebook.py 강사용.ipynb

임시 폴더에 data/를 복사해 실행하므로 output/ 같은 실습 결과가 저장소에 남지 않는다.
준비 셀은 Colab 전용 명령이라 실행할 때만 로컬 폰트 등록으로 바꾼다.
"""
import re
import shutil
import sys
import tempfile
from pathlib import Path

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor

TOOLS = Path(__file__).resolve().parent
FONT = TOOLS / "NanumGothic.ttf"
LOCAL_PATH = re.compile(r"[A-Za-z]:\\\S*\\")


def run(path: Path) -> None:
    nb = nbformat.read(path, as_version=4)
    prepare = [c for c in nb.cells if c.cell_type == "code" and "fonts-nanum" in c.source]
    if len(prepare) != 1:
        sys.exit(f"{path.name}: 준비 셀이 {len(prepare)}개입니다")
    original = prepare[0].source
    prepare[0].source = (
        "from matplotlib import font_manager\n"
        f"font_manager.fontManager.addfont({FONT.as_posix()!r})"
    )
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copytree(TOOLS.parent / "data", Path(tmp) / "data")
        ExecutePreprocessor(timeout=300, kernel_name="python3").preprocess(nb, {"metadata": {"path": tmp}})
    prepare[0].source = original
    prepare[0].outputs = []
    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        # 제작 PC의 파이썬 경로는 Colab 출력과 다르므로 남기지 않는다.
        if "sys.executable" in cell.source:
            cell.outputs = []
        for output in cell.get("outputs", []):
            if output.output_type == "stream":
                output.text = LOCAL_PATH.sub("…/", output.text)
    nbformat.write(nb, path)
    print(f"{path.name}: 실행 완료")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("사용법: python run_notebook.py 강사용.ipynb")
    run(Path(sys.argv[1]))
