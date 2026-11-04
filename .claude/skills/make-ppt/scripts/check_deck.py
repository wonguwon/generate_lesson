"""완성된 .pptx가 templates.json 규칙을 지키는지 검사한다. 어긋나면 종료 코드 1.

사용법: python check_deck.py --templates ppt_design/templates.json --deck out.pptx
"""
import argparse
import json
import re
import sys
from pathlib import Path

from PIL import ImageFont
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.oxml.ns import qn
from pptx.util import Emu

FONT_DIR = Path("C:/Windows/Fonts")
FONT_FILES = {
    ("Malgun Gothic", False): "malgun.ttf",
    ("Malgun Gothic", True): "malgunbd.ttf",
    ("Courier New", False): "cour.ttf",
    ("Courier New", True): "courbd.ttf",
}
LINE_HEIGHT = 1.33  # 맑은 고딕 줄 높이 (글자 크기 대비)
TOLERANCE = 0.6  # pt, 소수점 반올림 오차
MEASURE_MARGIN = 0.97  # 실제 렌더러와 측정값의 차이를 감안해 폭을 조금 좁게 본다
FONT_SCALE = 4  # 글자 폭을 정밀하게 재려고 크게 렌더링하는 배율
ORPHAN_CHARS = 2  # 마지막 줄에 이 글자 수 이하만 남으면 어색하다
CHARS_PER_MINUTE = 300  # 강의 말하기 속도 추정치 (공백 포함 글자 수)
BANNED_NOTE_WORD = "오늘"  # 녹화 강의라 학습자마다 보는 날이 다르다
NO_TITLE_RULE = ("cover", "closing", "section_divider")
FOOTER_SIZES = ("caption_footer", "page_number")


def pt(emu):
    return Emu(emu).pt


def measure_lines(runs, width):
    """글자 단위로 줄바꿈해 줄 수와 마지막 줄 글자 수를 센다 (한글은 글자 단위로 끊긴다)."""
    lines, current, last = 1, 0.0, 0
    for text, font in runs:
        for ch in text:
            advance = font.getlength(ch)
            if current + advance > width * MEASURE_MARGIN:
                lines += 1
                current, last = 0.0, 0
            current += advance
            last += not ch.isspace()
    return lines, last


class Checker:
    def __init__(self, templates, deck):
        self.t = json.loads(Path(templates).read_text(encoding="utf-8"))
        self.prs = Presentation(deck)
        self.errors, self.warnings = [], []
        theme = self.t["color_palette"]["theme_scheme"]
        keep = [v for k, v in theme.items() if "hyperlink" not in k]
        rules = " ".join(self.t["generation_rules"]["global"])
        self.colors = {c.upper() for c in keep + re.findall(r"#[0-9A-Fa-f]{6}", rules)}
        fonts = self.t["typography"]["font_family"]
        self.fonts = {fonts["minor_body"], fonts["code"]}
        self.limits = self.t["generation_rules"]["content_limits"]
        self.safe = self.t["layout_and_spacing"]["margins_pt"]["safe_area"]
        self.title_box = self.t["layout_and_spacing"]["vertical_zones"]["title_zone"]
        self.styles = self.t["typography"]["styles"]
        self.cards = self.t["component_rules"]["card_container"]
        self.radius = self.t["component_rules"]["global"]["corner_radius_pt"]
        self.cache = {}
        self.script_summary = None

    def err(self, n, msg):
        self.errors.append(f"{n}장: {msg}")

    def warn(self, n, msg):
        self.warnings.append(f"{n}장: {msg}")

    def font(self, name, bold, size):
        key = (name, bold, size)
        if key not in self.cache:
            file = FONT_FILES.get((name, bold), FONT_FILES[("Malgun Gothic", bold)])
            self.cache[key] = ImageFont.truetype(str(FONT_DIR / file), max(1, round(size * FONT_SCALE)))
        return self.cache[key]

    def check_runs(self, n, shape):
        min_size = self.limits["min_font_size_pt"]
        footer = {self.styles[k]["size_pt"] for k in FOOTER_SIZES}
        for p in shape.text_frame.paragraphs:
            for r in p.runs:
                if not r.text.strip():
                    continue
                f = r.font
                if f.name not in self.fonts:
                    self.err(n, f"폰트 {f.name}: {r.text[:15]!r}")
                ea = r._r.find(qn("a:rPr")).find(qn("a:ea"))
                if ea is None or ea.get("typeface") != self.t["typography"]["font_family"]["minor_body"]:
                    self.err(n, f"동아시아 폰트 미지정: {r.text[:15]!r}")
                if f.size is None:
                    self.err(n, f"글자 크기 미지정: {r.text[:15]!r}")
                elif f.size.pt < min_size and not (shape.name.startswith("chrome") and f.size.pt in footer):
                    self.err(n, f"최소 글자 크기 미만 {f.size.pt}pt: {r.text[:15]!r}")
                if f.italic:
                    self.err(n, f"이탤릭: {r.text[:15]!r}")
                if f.underline:
                    self.err(n, f"밑줄: {r.text[:15]!r}")

    def segments(self, paragraph):
        """줄바꿈(a:br)으로 나눈 (글자, 폰트) 목록을 돌려준다."""
        runs = iter(paragraph.runs)
        out = [[]]
        for child in paragraph._p:
            if child.tag == qn("a:br"):
                out.append([])
            elif child.tag == qn("a:r"):
                r = next(runs)
                if r.font.size:
                    out[-1].append((r.text, self.font(r.font.name, bool(r.font.bold), r.font.size.pt)))
        return out

    def check_overflow(self, n, shape):
        if not shape.text_frame.text.strip():
            return
        total, box_w = 0.0, pt(shape.width)
        for p in shape.text_frame.paragraphs:
            ppr = p._p.find(qn("a:pPr"))
            width = box_w - pt(int(ppr.get("marL", 0))) if ppr is not None else box_w
            size = max((r.font.size.pt for r in p.runs if r.font.size), default=0)
            lines = 0
            for seg in self.segments(p):
                count, last = measure_lines(seg, width * FONT_SCALE)
                lines += count
                if count > 1 and last <= ORPHAN_CHARS and shape.name != "code-text":
                    self.warn(n, f"마지막 줄에 {last}글자만 남음: {p.text[:20]!r}")
            total += lines * size * LINE_HEIGHT + (p.space_after.pt if p.space_after else 0)
            if ppr is not None and ppr.get("marL") and lines > 2:
                self.warn(n, f"불릿 {lines}줄 (2줄 이하 권장): {p.text[:20]!r}")
            if shape.name.startswith("chrome") and lines > 1:
                self.err(n, f"헤더·푸터가 한 줄을 넘음: {p.text[:30]!r}")
        if p.space_after:
            total -= p.space_after.pt
        if total > pt(shape.height) + TOLERANCE:
            self.err(n, f"글자 넘침 {shape.name}: 필요 {total:.0f}pt / 상자 {pt(shape.height):.0f}pt: {shape.text_frame.text[:20]!r}")

    def check_shape(self, n, shape, archetype):
        x, y, w, h = pt(shape.left), pt(shape.top), pt(shape.width), pt(shape.height)
        slide_w, slide_h = self.t["slide"]["width_pt"], self.t["slide"]["height_pt"]
        if x < -TOLERANCE or y < -TOLERANCE or x + w > slide_w + TOLERANCE or y + h > slide_h + TOLERANCE:
            self.err(n, f"슬라이드 밖 {shape.name}")
        free = not shape.name.startswith(("chrome", "bg", "title"))
        if free and archetype not in NO_TITLE_RULE:
            s = self.safe
            if (x < s["x"] - TOLERANCE or x + w > s["x"] + s["w"] + TOLERANCE
                    or y < s["y"] - TOLERANCE or y + h > s["y"] + s["h"] + TOLERANCE):
                self.err(n, f"콘텐츠 영역 밖 {shape.name}: ({x:.1f}, {y:.1f}, {w:.1f}, {h:.1f})")
        el = shape._element
        for clr in el.iter(qn("a:srgbClr")):
            if "#" + clr.get("val").upper() not in self.colors:
                self.err(n, f"팔레트 밖 색 #{clr.get('val')} ({shape.name})")
        sp_pr = el.find(qn("p:spPr"))
        if sp_pr is None:
            return
        if sp_pr.find(qn("a:gradFill")) is not None:
            self.err(n, f"그라데이션 도형 {shape.name}")
        if el.find(qn("p:style")) is not None and sp_pr.find(qn("a:effectLst")) is None:
            self.err(n, f"그림자 상속 {shape.name}")
        if shape.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE:
            geom = sp_pr.find(qn("a:prstGeom"))
            if geom is not None and geom.get("prst") == "roundRect":
                radius = shape.adjustments[0] * min(w, h)
                allowed = {self.radius, self.cards["glass_frame_on_dark"]["radius_pt"]}
                if not any(abs(radius - r) < 0.2 for r in allowed):
                    self.err(n, f"모서리 {radius:.1f}pt ({shape.name})")

    def check_title(self, n, slide, archetype):
        title = slide.shapes.title
        if title is None or not title.text_frame.text.strip():
            self.err(n, "제목 없음")
            return
        text = title.text_frame.text
        if archetype in ("cover", "closing"):
            return
        if len(text) > self.limits["title_chars"]:
            self.warn(n, f"제목 {len(text)}자 (20자 이내): {text!r}")
        if archetype in NO_TITLE_RULE:
            return
        z = self.title_box
        if abs(pt(title.left) - z["x"]) > TOLERANCE or abs(pt(title.top) - z["y"]) > TOLERANCE:
            self.err(n, "제목 위치가 규격과 다름")
        style = self.styles["header_slide_title"]
        run = title.text_frame.paragraphs[0].runs[0]
        if run.font.size.pt != style["size_pt"] or not run.font.bold or str(run.font.color.rgb) != style["color"].lstrip("#"):
            self.err(n, "제목 글자 스타일이 규격과 다름")

    def check_structure(self, n, slide, archetype):
        names = [s.name for s in slide.shapes]
        chrome = any(x.startswith("chrome") for x in names)
        if archetype in ("cover", "closing"):
            if chrome:
                self.err(n, "표지·마무리에 헤더·푸터가 있음")
            return
        for need in ("chrome-header", "chrome-footer", "chrome-day", "chrome-page"):
            if need not in names:
                self.err(n, f"{need} 없음")
        if names.count("chrome-tab-active") != 1:
            self.err(n, "활성 내비 탭이 1개가 아님")
        by_name = {s.name: s for s in slide.shapes}
        for name, shape in by_name.items():
            if name.endswith("-list") or name == "bullet-list":
                count = len(shape.text_frame.paragraphs)
                if count > self.limits["bullets_per_list"]:
                    self.err(n, f"불릿 {count}개 ({name})")
        if archetype == "two_column_versus":
            left = len(by_name["left-list"].text_frame.paragraphs)
            right = len(by_name["right-list"].text_frame.paragraphs)
            if left != right:
                self.err(n, f"비교 카드 불릿 수가 다름 ({left} / {right})")

    def count_emphasis(self, n, slide):
        blue = self.t["color_palette"]["sub_point"]["point_blue"].lstrip("#")
        count = 0
        for shape in slide.shapes:
            if not shape.has_text_frame or shape.name.startswith("chrome") or shape.name == "code-text":
                continue
            for p in shape.text_frame.paragraphs:
                runs = [r for r in p.runs if r.text.strip()]
                bolds = [r for r in runs if r.font.bold]
                for r in runs:
                    if r.font.color.type is not None and str(r.font.color.rgb) == blue:
                        count += 1
                if len(runs) > 1 and 0 < len(bolds) < len(runs):
                    count += len(bolds)
        if count > 2:
            self.warn(n, f"강조 {count}곳 (슬라이드당 1~2곳)")

    def check_notes(self):
        """슬라이드 노트 대본을 검사하고 말하는 시간을 추정한다."""
        notes = [
            s.notes_slide.notes_text_frame.text.strip() if s.has_notes_slide else ""
            for s in self.prs.slides
        ]
        total = sum(len(t) for t in notes)
        if not total:
            self.warnings.append("대본 없음: 슬라이드 노트가 모두 비어 있습니다")
            return
        for n, text in enumerate(notes, 1):
            if not text:
                self.warn(n, "대본 없음")
            elif BANNED_NOTE_WORD in text:
                self.warn(n, f'대본에 "{BANNED_NOTE_WORD}"가 있음')
        self.script_summary = f"대본 {total}자, 말하는 시간 약 {total / CHARS_PER_MINUTE:.0f}분"

    def run(self):
        for n, slide in enumerate(self.prs.slides, 1):
            archetype = slide._element.cSld.get("name", "")
            self.check_title(n, slide, archetype)
            self.check_structure(n, slide, archetype)
            self.count_emphasis(n, slide)
            for shape in slide.shapes:
                self.check_shape(n, shape, archetype)
                if shape.has_text_frame:
                    self.check_runs(n, shape)
                    self.check_overflow(n, shape)
        self.check_notes()
        return self.errors, self.warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--templates", required=True)
    ap.add_argument("--deck", required=True)
    args = ap.parse_args()
    checker = Checker(args.templates, args.deck)
    errors, warnings = checker.run()
    for line in errors:
        print("오류", line)
    for line in warnings:
        print("주의", line)
    if checker.script_summary:
        print(checker.script_summary)
    print(f"검사 끝: 오류 {len(errors)}건, 주의 {len(warnings)}건")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
