"""PowerPoint로 .pptx를 열어 슬라이드를 PNG로 내보낸다 (실제 렌더링 확인용).

사용법: python export_png.py --deck out.pptx --out-dir 폴더 [--slides 1,3,5]
"""
import argparse
import sys
from pathlib import Path

import win32com.client

WIDTH = 1280
HEIGHT = 720
WITH_WINDOW_FALSE = 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--deck", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--slides", help="쉼표로 구분한 슬라이드 번호. 없으면 전체")
    args = ap.parse_args()
    out = Path(args.out_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)
    app = win32com.client.Dispatch("PowerPoint.Application")
    deck = app.Presentations.Open(str(Path(args.deck).resolve()), True, False, WITH_WINDOW_FALSE)
    try:
        numbers = (
            [int(x) for x in args.slides.split(",")]
            if args.slides
            else range(1, deck.Slides.Count + 1)
        )
        for n in numbers:
            deck.Slides(n).Export(str(out / f"slide_{n:02d}.png"), "PNG", WIDTH, HEIGHT)
    finally:
        deck.Close()
        if app.Presentations.Count == 0:
            app.Quit()
    print(f"완료: {out}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
