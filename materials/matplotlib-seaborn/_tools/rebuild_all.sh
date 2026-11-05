#!/bin/bash
# 강사용 빌드 → 실행(출력 저장) → 학생용 생성. 사용: bash rebuild_all.sh [01 02 ...]
cd "$(dirname "$0")"
PY=.venv/Scripts/python.exe
[ $# -eq 0 ] && set -- 01 02 03 04 05 06 07 08 09 10
for n in "$@"; do
  dir=$(ls -d ../${n}_*/) || exit 1
  name=$(basename "$dir")
  "$PY" build_$n.py >/dev/null || exit 1
  "$PY" run_notebook.py "$dir${name}_강사용.ipynb" || exit 1
  "$PY" make_student.py "$dir${name}_강사용.ipynb" "$dir$name.ipynb"
done
