"""덱 스펙(JSON)을 ppt_design/templates.json 규격대로 .pptx로 만든다.

좌표·색·글자 크기는 이 파일에 적지 않는다. 모두 templates.json에서 읽으므로
디자인을 바꿀 때는 templates.json만 고치면 된다.

사용법:
  python build_deck.py --templates ppt_design/templates.json --spec deck.json --out out.pptx
  python build_deck.py --list-icons book
"""
import argparse
import json
import re
import sys
import tempfile
from copy import deepcopy
from pathlib import Path

from lxml import etree
from PIL import Image, ImageDraw, ImageFont
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.oxml.ns import qn
from pptx.util import Pt

ASSETS = Path(__file__).resolve().parent.parent / "assets"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
ANCHORS = {"top": MSO_ANCHOR.TOP, "middle": MSO_ANCHOR.MIDDLE, "bottom": MSO_ANCHOR.BOTTOM}
ALIGNS = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT}
TITLE_ONLY_LAYOUT = 5
REQUIRED_FIELDS = ("organization", "course", "instructor", "day")


def rgb(hex_color):
    return RGBColor.from_string(hex_color.lstrip("#").upper())


def box_of(d):
    return d["x"], d["y"], d["w"], d["h"]


def element(archetype, role):
    return next(e for e in archetype["elements"] if e["role"] == role)


class Design:
    """templates.json 읽기 도우미."""

    def __init__(self, path):
        self.t = json.loads(Path(path).read_text(encoding="utf-8"))
        self.palette = self.t["color_palette"]
        self.fonts = self.t["typography"]["font_family"]
        self.styles = self.t["typography"]["styles"]
        self.bullet = self.t["typography"]["bullet"]
        self.layout = self.t["layout_and_spacing"]
        self.zones = self.layout["vertical_zones"]
        self.comp = self.t["component_rules"]
        self.arch = self.t["slide_archetypes"]
        self.radius = self.comp["global"]["corner_radius_pt"]

    def style(self, ref, **override):
        """스타일 이름 또는 "20pt Bold #0F172A" 같은 문자열을 dict로 푼다."""
        if isinstance(ref, dict):
            base = dict(ref)
        elif ref in self.styles:
            base = dict(self.styles[ref])
            base["bold"] = base.get("weight") == "Bold"
            base["size"] = base["size_pt"]
        else:
            size = re.search(r"(\d+(?:\.\d+)?)pt", ref)
            color = re.search(r"#[0-9A-Fa-f]{6}", ref)
            base = {
                "size": float(size.group(1)),
                "bold": "Bold" in ref,
                "color": color.group(0) if color else self.palette["text"]["body_on_light"],
            }
        base.update(override)
        return base


class Icons:
    """Lucide 폰트에서 아이콘 PNG를 만든다 (256x256, 단색, 투명 배경)."""

    def __init__(self, workdir):
        self.dir = Path(workdir)
        self.map = json.loads((ASSETS / "codepoints.json").read_text(encoding="utf-8"))
        self.font = ImageFont.truetype(str(ASSETS / "lucide.ttf"), 216)

    def png(self, name, color):
        if name not in self.map:
            near = [k for k in self.map if name.split("-")[0] in k][:8]
            raise SystemExit(f"없는 아이콘: {name} (비슷한 이름: {near})")
        path = self.dir / f"{name}_{color.lstrip('#')}.png"
        if not path.exists():
            img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
            ImageDraw.Draw(img).text(
                (128, 128), chr(self.map[name]), font=self.font, fill=color, anchor="mm"
            )
            img.save(path)
        return str(path)


class Builder:
    def __init__(self, design, spec, spec_dir, workdir):
        self.d = design
        self.spec = spec
        self.spec_dir = spec_dir
        self.workdir = Path(workdir)
        self.icons = Icons(workdir)
        self.prs = Presentation()
        self.setup_presentation()
        self.phase = self.d.zones["nav_tab_row"]["tabs"][0]
        self.part = 0
        self.hero = None

    # ---------- 파일 설정 ----------
    def setup_presentation(self):
        slide = self.d.t["slide"]
        ratio = slide["width_emu"] / self.prs.slide_width
        self.prs.slide_width = slide["width_emu"]
        self.prs.slide_height = slide["height_emu"]
        master = self.prs.slide_master
        for holder in [master, *master.slide_layouts]:
            for shape in holder.placeholders:
                xfrm = shape._element.spPr.find(qn("a:xfrm"))
                if xfrm is not None:
                    shape.left = int(shape.left * ratio)
                    shape.width = int(shape.width * ratio)
        self.apply_theme(master)

    def apply_theme(self, master):
        """새 슬라이드나 직접 입력한 글자도 같은 색·폰트를 쓰도록 테마를 바꾼다."""
        part = master.part.part_related_by(RT.THEME)
        root = etree.fromstring(part.blob)
        scheme = root.find(f".//{{{A_NS}}}clrScheme")
        names = {
            "dk1": "dk1_tx1", "lt1": "lt1_bg1", "dk2": "dk2_tx2", "lt2": "lt2_bg2",
            **{f"accent{i}": f"accent{i}" for i in range(1, 7)},
            "hlink": "hyperlink", "folHlink": "followed_hyperlink",
        }
        for tag, key in names.items():
            slot = scheme.find(f"{{{A_NS}}}{tag}")
            for child in list(slot):
                slot.remove(child)
            etree.SubElement(slot, f"{{{A_NS}}}srgbClr").set(
                "val", self.d.palette["theme_scheme"][key].lstrip("#")
            )
        for group, key in (("majorFont", "major_heading"), ("minorFont", "minor_body")):
            node = root.find(f".//{{{A_NS}}}{group}")
            for tag in ("latin", "ea"):
                node.find(f"{{{A_NS}}}{tag}").set("typeface", self.d.fonts[key])
        part._blob = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)

    # ---------- 도형 ----------
    def shape(self, slide, role, box, fill=None, border=None, radius=None, alpha=None):
        x, y, w, h = box
        kind = MSO_SHAPE.ROUNDED_RECTANGLE if radius else MSO_SHAPE.RECTANGLE
        s = slide.shapes.add_shape(kind, Pt(x), Pt(y), Pt(w), Pt(h))
        s.name = role
        s.shadow.inherit = False
        if radius:
            s.adjustments[0] = radius / min(w, h)
        if fill:
            s.fill.solid()
            s.fill.fore_color.rgb = rgb(fill)
            if alpha is not None:
                clr = s._element.spPr.find(qn("a:solidFill")).find(qn("a:srgbClr"))
                etree.SubElement(clr, qn("a:alpha")).set("val", str(alpha * 1000))
        else:
            s.fill.background()
        if border:
            s.line.color.rgb = rgb(border[0])
            s.line.width = Pt(border[1])
        else:
            s.line.fill.background()
        return s

    def card(self, slide, role, box, name):
        c = self.d.comp["card_container"][name]
        border = None
        if c.get("border", "none") != "none":
            border = (c["border"], c["border_width_pt"])
        return self.shape(
            slide, role, box, c["fill"], border, c["radius_pt"], c.get("fill_alpha_percent")
        )

    def line(self, slide, role, x1, y1, x2, y2, rule):
        ln = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Pt(x1), Pt(y1), Pt(x2), Pt(y2))
        ln.name = role
        ln.line.color.rgb = rgb(rule["color"])
        ln.line.width = Pt(rule["width_pt"])
        etree.SubElement(ln._element.spPr, qn("a:effectLst"))  # 테마 기본 그림자를 끈다
        return ln

    def picture(self, slide, role, path, box, radius=None):
        x, y, w, h = box
        with Image.open(path) as img:
            scale = min(w / img.width, h / img.height)
            pw, ph = img.width * scale, img.height * scale
        pic = slide.shapes.add_picture(
            str(path), Pt(x + (w - pw) / 2), Pt(y + (h - ph) / 2), Pt(pw), Pt(ph)
        )
        pic.name = role
        if radius:
            geom = pic._element.spPr.find(qn("a:prstGeom"))
            geom.set("prst", "roundRect")
            av = geom.find(qn("a:avLst"))
            if av is None:
                av = etree.SubElement(geom, qn("a:avLst"))
            gd = etree.SubElement(av, qn("a:gd"))
            gd.set("name", "adj")
            gd.set("fmla", f"val {int(radius / min(pw, ph) * 100000)}")
        return pic

    def image_path(self, value):
        path = Path(value)
        return path if path.is_absolute() else self.spec_dir / path

    # ---------- 글자 ----------
    def runs(self, text, style):
        """**굵게**, [[강조색]] 표시를 나눠 (글자, 스타일) 목록으로 돌려준다."""
        on_dark = style.get("color", "").upper() in (
            self.d.palette["text"]["subtitle_on_dark"],
            self.d.palette["text"]["body_on_dark_navy_panel"],
            self.d.palette["text"]["title_on_dark"],
        )
        keyword = (
            self.d.palette["text"]["title_on_dark"]
            if on_dark
            else self.d.palette["sub_point"]["point_blue"]
        )
        out = []
        for piece in re.split(r"(\*\*.+?\*\*|\[\[.+?\]\])", text):
            if piece.startswith("**"):
                out.append((piece[2:-2], {**style, "bold": True}))
            elif piece.startswith("[["):
                out.append((piece[2:-2], {**style, "color": keyword}))
            elif piece:
                out.append((piece, style))
        return out

    def write_run(self, paragraph, text, style):
        run = paragraph.add_run()
        run.text = text
        font = run.font
        font.size = Pt(style["size"])
        font.bold = bool(style.get("bold"))
        font.color.rgb = rgb(style["color"])
        name = style.get("font") or self.d.fonts["minor_body"]
        font.name = name
        rpr = run._r.get_or_add_rPr()
        for tag in ("a:ea", "a:cs"):
            etree.SubElement(rpr, qn(tag)).set("typeface", self.d.fonts["minor_body"] if tag == "a:ea" else name)
        if style.get("letter_spacing_pt"):
            rpr.set("spc", str(int(style["letter_spacing_pt"] * 100)))

    def text(self, slide, role, box, paras, anchor="top", align="left", shape=None):
        """paras는 dict(text 또는 runs, style, level, after) 목록이다."""
        x, y, w, h = box
        tb = shape or slide.shapes.add_textbox(Pt(x), Pt(y), Pt(w), Pt(h))
        tb.left, tb.top, tb.width, tb.height = Pt(x), Pt(y), Pt(w), Pt(h)
        tb.name = role
        tf = tb.text_frame
        tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
        tf.word_wrap = True
        tf.auto_size = MSO_AUTO_SIZE.NONE
        tf.vertical_anchor = ANCHORS[anchor]
        for i, item in enumerate(paras):
            p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            p.alignment = ALIGNS[align]
            p.line_spacing = 1.0
            p.space_before = Pt(0)
            p.space_after = Pt(item.get("after", 0))
            for piece, style in item.get("runs") or self.runs(item["text"], item["style"]):
                for j, part in enumerate(piece.split("\n")):
                    if j:
                        p.add_line_break()
                    if part:
                        self.write_run(p, part, style)
            if item.get("level"):
                self.bullet_format(p, item["level"])
        return tb

    def bullet_format(self, paragraph, level):
        b = self.d.bullet
        ppr = paragraph._p.get_or_add_pPr()
        left = b["left_margin_pt"] if level == 1 else b["level_2_left_margin_pt"]
        ppr.set("marL", str(Pt(left)))
        ppr.set("indent", str(Pt(b["hanging_indent_pt"])))
        etree.SubElement(ppr, qn("a:buFont")).set("typeface", b["bullet_font"])
        char = b["character"] if level == 1 else b["level_2_character"]
        etree.SubElement(ppr, qn("a:buChar")).set("char", char)

    def bullets(self, slide, role, box, items, style):
        style = self.d.style(style)
        paras = []
        for item in items:
            level = item.get("level", 1) if isinstance(item, dict) else 1
            text = item["text"] if isinstance(item, dict) else item
            paras.append(
                {"text": text, "style": style, "level": level, "after": self.d.bullet["space_after_pt"]}
            )
        return self.text(slide, role, box, paras)

    def single(self, slide, role, box, text, style, anchor=None, align=None, shape=None):
        style = self.d.style(style)
        return self.text(
            slide, role, box, [{"text": text, "style": style}],
            anchor or style.get("vertical_anchor", "top"),
            align or style.get("align", "left"),
            shape,
        )

    def title(self, slide, text, box, style):
        """제목은 제목 개체를 쓴다. 파워포인트 개요 보기와 화면 낭독기가 읽을 수 있다."""
        shape = slide.shapes.title
        slide.shapes._spTree.append(shape._element)
        return self.single(slide, "title", box, text, style, shape=shape)

    def slide_title(self, slide, text):
        self.title(slide, text, box_of(self.d.zones["title_zone"]), "header_slide_title")

    # ---------- 타일·칩 ----------
    def icon_tile(self, slide, role, x, y, size, icon_pt, icon, fill=None, icon_color=None):
        cc = self.d.comp["icon_tile"]
        fill = fill or cc["fill_on_light_background"]
        color = icon_color or self.d.palette["icon"]["on_primary_or_dark_tile"]
        self.shape(slide, role, (x, y, size, size), fill, radius=cc["radius_pt"])
        off = (size - icon_pt) / 2
        self.picture(slide, f"{role}-icon", self.icons.png(icon, color), (x + off, y + off, icon_pt, icon_pt))

    def number_tile(self, slide, role, x, y, size, number, fill, style):
        self.shape(slide, role, (x, y, size, size), fill, radius=self.d.comp["icon_tile"]["radius_pt"])
        self.single(slide, f"{role}-number", (x, y, size, size), number, style, "middle", "center")

    def chip(self, slide, role, box, variant, text):
        v = self.d.comp["chip_and_button"]["variants"][variant]
        border = None
        if "border" in v:
            color, width = v["border"].split(" / ")
            border = (color, float(width.replace("pt", "")))
        self.shape(slide, role, box, v["fill"], border, self.d.comp["chip_and_button"]["radius_pt"])
        style = self.d.style("chip_text", color=v["text"])
        self.single(slide, f"{role}-text", box, text, style, "middle", "center")

    # ---------- 공통 크롬 ----------
    def chrome(self, slide, number):
        z, s = self.d.zones, self.d.styles
        nav = z["nav_tab_row"]
        rule = self.d.comp["header_footer_chrome"]
        fill = lambda text, stop=" (": text.split(stop)[0]
        course = self.spec.get("course_short") or self.spec["course"]
        instructor = self.spec["instructor"]
        organization = self.spec["organization"]

        head = z["header_bar"]
        self.shape(slide, "chrome-header", (0, head["y"], self.d.t["slide"]["width_pt"], head["h"]), head["fill"])
        left = self.d.layout["margins_pt"]["left"]
        self.single(
            slide, "chrome-logo", (left, head["y"], nav["tab_x"][0] - left, head["h"]),
            s["header_bar_logo"]["text"].replace("기관명", organization), "header_bar_logo", "middle",
        )
        for x, tab in zip(nav["tab_x"], nav["tabs"]):
            active = tab == self.phase
            style = "nav_tab_active" if active else "nav_tab_inactive"
            self.single(
                slide, f"chrome-tab-{'active' if active else 'idle'}",
                (x, nav["y"], nav["tab_width"], nav["active_underline"]["y"]), tab, style, "middle", "center",
            )
            if active:
                bar = nav["active_underline"]
                self.shape(
                    slide, "chrome-tab-underline", (x, bar["y"], bar["w"], bar["h"]),
                    self.d.palette["text"]["active_nav"],
                )
        right = fill(rule["header_bar"]["right_text"]).replace("과목명", course).replace("담당 강사", instructor)
        self.single(slide, "chrome-course", box_of(s["header_bar_course"]["position"]), right, "header_bar_course", "middle")
        self.single(slide, "chrome-day", box_of(nav["day_label"]), self.spec["day"], "nav_day_label", "middle")

        foot = z["footer_bar"]
        self.shape(slide, "chrome-footer", (0, foot["y"], self.d.t["slide"]["width_pt"], foot["h"]), foot["fill"])
        text = fill(rule["footer_bar"]["text"]).replace("기관명", organization).replace("과목명", self.spec["course"])
        self.single(slide, "chrome-footer-text", (foot["text_x"], foot["y"], foot["text_w"], foot["h"]), text, "caption_footer", "middle")
        self.single(slide, "chrome-page", box_of(s["page_number"]["position"]), str(number), "page_number", "middle")

    def hero_image(self):
        """표지 그라데이션 이미지를 templates.json의 색으로 만든다."""
        if self.hero:
            return self.hero
        g = self.d.palette["background"]["title_hero_gradient"]
        start, stop = [tuple(int(g[k][i:i + 2], 16) for i in (1, 3, 5)) for k in ("from", "to")]
        img = Image.new("RGB", (200, 103))
        px = img.load()
        for yy in range(103):
            for xx in range(200):
                t = (xx / 199 + yy / 102) / 2
                px[xx, yy] = tuple(round(a + (b - a) * t) for a, b in zip(start, stop))
        self.hero = str(self.workdir / "hero_gradient.png")
        img.resize((2000, 1032), Image.BICUBIC).save(self.hero)
        return self.hero

    def hero_background(self, slide):
        s = self.d.t["slide"]
        top = self.d.zones["header_bar"]["h"]
        pic = slide.shapes.add_picture(
            self.hero_image(), 0, Pt(top), Pt(s["width_pt"]), Pt(s["height_pt"] - top)
        )
        pic.name = "bg-hero"

    # ---------- 아키타입 ----------
    def cover(self, slide, s):
        a, z = self.d.arch["cover"], self.d.layout["cover_slide_zones"]
        self.hero_background(slide)
        self.title(slide, s["title"], box_of(z["title"]), "cover_title")
        self.single(slide, "subtitle", box_of(z["subtitle"]), s.get("subtitle", ""), "cover_subtitle")
        chip = element(a, "day_chip")
        chip_box = box_of(chip["box"])
        if not self.spec.get("semester"):
            # 학기 칩이 없으면 Day 칩이 빈자리에 떠 보이므로 제목 왼쪽 끝에 맞춘다.
            chip_box = (z["title"]["x"], *chip_box[1:])
        self.chip(slide, "day-chip", chip_box, chip["variant"], self.spec["day"])
        if self.spec.get("semester"):
            # templates.json에는 학기 칩 요소가 없다. 입력했을 때만 Day 칩 왼쪽 빈자리에 놓는다.
            rule = self.d.comp["chip_and_button"]
            width = rule["variants"]["outline_white"]["example_width_pt"]
            x = chip["box"]["x"] - rule["gap_between_chips_pt"] - width
            self.chip(slide, "semester-chip", (x, chip["box"]["y"], width, rule["height_pt"]), "outline_white", self.spec["semester"])
        meta = s.get("meta") or f"{self.spec['course']} | {self.spec['instructor']}"
        self.single(slide, "meta", box_of(z["meta_line"]), meta, "cover_meta")
        self.card(slide, "media-frame", box_of(z["media_frame"]), "glass_frame_on_dark")
        if s.get("image"):
            self.picture(slide, "media", self.image_path(s["image"]), box_of(z["media_frame"]), self.d.radius)

    def closing(self, slide, s):
        a, z = self.d.arch["closing"], self.d.layout["cover_slide_zones"]
        self.hero_background(slide)
        self.title(slide, s.get("title") or element(a, "title")["example"], box_of(z["title"]), "cover_title")
        self.single(slide, "subtitle", box_of(z["subtitle"]), s.get("subtitle") or element(a, "subtitle")["example"], "cover_subtitle")
        if s.get("contact"):
            self.single(slide, "contact", box_of(z["meta_line"]), s["contact"], "cover_meta")

    def agenda_with_goals(self, slide, s):
        a = self.d.arch["agenda_with_goals"]
        self.slide_title(slide, s["title"])
        lst, panel = element(a, "agenda_list_left"), element(a, "goal_panel_right")
        p = lst["item_pattern"]
        tile, tb, div = p["number_tile"], p["text_box"], p["divider"]
        rows = lst["row_y_start"]
        for i, item in enumerate(s["items"]):
            y = rows[i]
            self.number_tile(slide, f"agenda-{i}", tile["x"], y, tile["size_pt"], f"{i + 1:02d}", tile["fill"], tile["text"])
            paras = [{"text": item["title"], "style": self.d.style(tb["line_1"])}]
            if item.get("desc"):
                paras.append({"text": item["desc"], "style": self.d.style(tb["line_2"])})
            top = y + (tile["size_pt"] - tb["h"]) / 2
            self.text(slide, f"agenda-{i}-text", (tb["x"], top, tb["w"], tb["h"]), paras, "middle")
            if i < len(s["items"]) - 1:
                mid = (y + tile["size_pt"] + rows[i + 1]) / 2
                self.line(slide, f"agenda-{i}-divider", div["x"], mid, div["x"] + div["w"], mid, div)
        self.card(slide, "goal-panel", box_of(panel["box"]), "soft_blue_panel")
        kids = {c["role"]: c for c in panel["children"]}
        t = kids["icon_tile"]
        self.icon_tile(slide, "goal-tile", t["box"]["x"], t["box"]["y"], t["box"]["w"], t["icon_size_pt"], s["goal_icon"], t["fill"])
        self.single(slide, "goal-heading", box_of(kids["heading"]["box"]), s.get("goal_title", "학습 목표"), kids["heading"]["style"], "middle")
        self.bullets(slide, "goal-list", box_of(kids["bullet_list"]["box"]), s["goals"], kids["bullet_list"]["style"])

    def section_divider(self, slide, s):
        z = self.d.layout["section_slide_zones"]
        band = z["hero_band"]
        self.part += 1
        number = f"{self.part:02d}"
        self.shape(slide, "bg-band", (0, band["y"], band["full_width"], band["h"]), band["fill"])
        self.single(slide, "section-watermark", box_of(z["watermark_number"]), number, "section_watermark_number")
        self.single(slide, "section-label", box_of(z["label"]), f"PART {number}", "section_label")
        self.title(slide, s["title"], box_of(z["title"]), "section_title")
        if s.get("intro"):
            self.single(slide, "section-intro", box_of(z["intro_sentence"]), s["intro"], "section_intro")

    def text_plus_key_point(self, slide, s):
        a = self.d.arch["text_plus_key_point"]
        self.slide_title(slide, s["title"])
        lst = element(a, "bullet_list_left")
        self.bullets(slide, "bullet-list", box_of(lst["box"]), s["bullets"], "body_large")
        panel = element(a, "key_point_panel_right")
        self.card(slide, "key-panel", box_of(panel["box"]), "filled_primary_card")
        kids = {c["role"]: c for c in panel["children"]}
        t = kids["icon_tile"]
        self.icon_tile(slide, "key-tile", t["box"]["x"], t["box"]["y"], t["box"]["w"], t["icon_size_pt"], s["icon"], t["fill"], t["icon_color"])
        self.single(slide, "key-heading", box_of(kids["heading"]["box"]), s["key_title"], kids["heading"]["style"], "middle")
        self.single(slide, "key-message", box_of(kids["message"]["box"]), s["key_message"], kids["message"]["style"])

    def three_column_card_compare(self, slide, s):
        a = self.d.arch["three_column_card_compare"]
        self.slide_title(slide, s["title"])
        p = a["column_pattern"]
        v = a["vertical_dividers"]
        for x in v["x"]:
            self.line(slide, "column-divider", x, v["y"], x, v["y"] + v["h"], v)
        for i, col in enumerate(s["columns"]):
            x, w = a["column_x"][i], a["column_w"][i]
            tile = p["icon_tile"]
            self.icon_tile(slide, f"col-{i}-tile", x, tile["y"], tile["size_pt"], tile["icon_size_pt"], col["icon"], tile["fill"])
            self.single(slide, f"col-{i}-title", (x, p["title"]["y"], w, p["title"]["h"]), col["title"], p["title"]["style"])
            self.single(slide, f"col-{i}-desc", (x, p["description"]["y"], w, p["description"]["h"]), col["desc"], p["description"]["style"])

    def two_column_versus(self, slide, s):
        a = self.d.arch["two_column_versus"]
        self.slide_title(slide, s["title"])
        for side, role in (("left", "left_card"), ("right", "right_card")):
            e = element(a, role)
            data = s[side]
            self.card(slide, f"{side}-card", box_of(e["box"]), e["style"])
            self.single(slide, f"{side}-heading", box_of(e["heading"]["box"]), data["title"], e["heading"]["style"], "middle")
            self.bullets(slide, f"{side}-list", box_of(e["list"]["box"]), data["bullets"], e["list"]["style"])

    def process_steps(self, slide, s):
        a = self.d.arch["process_steps"]
        self.slide_title(slide, s["title"])
        unit = element(a, "step_unit")
        tile, card, ttl, desc = unit["number_tile"], unit["card"], unit["title"], unit["description"]
        steps = s["steps"]
        n = len(steps)
        safe = self.d.layout["margins_pt"]["safe_area"]
        gap = self.d.layout["column_split_rules"]["four_columns"]["gap"]
        if n == a["step_count"]:
            xs, w = a["step_x_card"], card["w"]
        else:
            w = (safe["w"] - (n - 1) * gap) / n
            xs = [safe["x"] + i * (w + gap) for i in range(n)]
        size = tile["size_pt"]
        tile_x = [x + (w - size) / 2 for x in xs]
        center = tile["y"] + size / 2
        conn = element(a, "connector_line")
        self.line(slide, "step-connector", tile_x[0] + size / 2, center, tile_x[-1] + size / 2, center, conn)
        desc_style = self.d.style(desc["style"])
        if n >= 5:
            desc_style["size"] = self.d.t["generation_rules"]["content_limits"]["min_font_size_pt"]
        for i, step in enumerate(steps):
            self.number_tile(slide, f"step-{i}", tile_x[i], tile["y"], size, str(i + 1), tile["fill"], tile["text"])
            self.card(slide, f"step-{i}-card", (xs[i], card["y"], w, card["h"]), "soft_gray_card")
            inner = w - 2 * ttl["offset_x"]
            self.single(slide, f"step-{i}-title", (xs[i] + ttl["offset_x"], card["y"] + ttl["offset_y"], inner, ttl["h"]), step["title"], ttl["style"])
            self.single(slide, f"step-{i}-desc", (xs[i] + desc["offset_x"], card["y"] + desc["offset_y"], inner, desc["h"]), step["desc"], desc_style)

    def code_or_formula_explain(self, slide, s):
        a = self.d.arch["code_or_formula_explain"]
        self.slide_title(slide, s["title"])
        block = element(a, "code_block")
        self.card(slide, "code-block", box_of(block["box"]), "code_block")
        inner = box_of(block["text_box"])
        if s.get("image"):
            self.picture(slide, "code-image", self.image_path(s["image"]), inner, self.d.radius)
        else:
            self.text(slide, "code-text", inner, self.code_paragraphs(s, a))
        heading = element(a, "explain_heading")
        self.single(slide, "explain-heading", box_of(heading["box"]), s["explain_title"], heading["style"], "middle")
        lst = element(a, "explain_list")
        self.bullets(slide, "explain-list", box_of(lst["box"]), s["bullets"], lst["style"])
        if s.get("tip"):
            tip = element(a, "tip_box")
            x, y, w, h = box_of(tip["box"])
            rule = self.d.comp["card_container"]["tip_box"]
            pad = rule["inner_padding_horizontal_pt"]
            self.card(slide, "tip-box", (x, y, w, h), "tip_box")
            self.single(slide, "tip-text", (x + pad, y, w - 2 * pad, h), s["tip"], self.d.style(f"{rule['text_size_pt']}pt {rule['text_color']}"), "middle")

    def code_paragraphs(self, s, a):
        rule = next(r for r in a["rules"] if "키워드" in r)
        words = re.search(r"\((.+?)\)", rule).group(1).split(", ") + s.get("keywords", [])
        pattern = re.compile(r"\b(" + "|".join(map(re.escape, words)) + r")\b")
        base = self.d.style("code")
        base["font"] = self.d.fonts["code"]
        kw = {**base, "bold": True, "color": base["keyword_color"]}
        paras = []
        for line in s["code"].split("\n"):
            parts = [(p, kw if i % 2 else base) for i, p in enumerate(pattern.split(line)) if p]
            paras.append({"runs": parts or [(" ", base)]})
        return paras

    def activity_list_with_time(self, slide, s):
        a = self.d.arch["activity_list_with_time"]
        self.slide_title(slide, s["title"])
        p = a["row_pattern"]
        tile, tb, btn, div = p["icon_tile"], p["text_box"], p["time_button"], p["divider"]
        rows = a["row_tile_y"]
        gap = self.d.layout["recommended_gaps_pt"]["divider_to_next_row_tile"]
        for i, item in enumerate(s["rows"]):
            y = rows[i]
            size = tile["size_pt"]
            self.icon_tile(slide, f"row-{i}-tile", tile["x"], y, size, tile["icon_size_pt"], item["icon"], tile["fill"])
            paras = [
                {"text": item["title"], "style": self.d.style(tb["line_1"])},
                {"text": item["desc"], "style": self.d.style(tb["line_2"])},
            ]
            self.text(slide, f"row-{i}-text", (tb["x"], y + (size - tb["h"]) / 2, tb["w"], tb["h"]), paras, "middle")
            self.chip(slide, f"row-{i}-time", (btn["x"], y + (size - btn["h"]) / 2, btn["w"], btn["h"]), "filled_primary_time", item["time"])
            if i < len(s["rows"]) - 1:
                line_y = rows[i + 1] - gap
                self.line(slide, f"row-{i}-divider", div["x"], line_y, div["x"] + div["w"], line_y, div)

    def summary_with_next(self, slide, s):
        a = self.d.arch["summary_with_next"]
        self.slide_title(slide, s["title"])
        left = element(a, "summary_rows_left")
        p = left["row_pattern"]
        tile, tb, div = p["icon_tile"], p["text_box"], p["divider"]
        gap = self.d.layout["recommended_gaps_pt"]["divider_to_next_row_tile"]
        rows = left["row_tile_y"]
        for i, item in enumerate(s["rows"]):
            y = rows[i]
            size = tile["size_pt"]
            self.icon_tile(slide, f"sum-{i}-tile", tile["x"], y, size, tile["icon_size_pt"], item["icon"], tile["fill"])
            self.single(slide, f"sum-{i}-text", (tb["x"], y + (size - tb["h"]) / 2, tb["w"], tb["h"]), item["text"], tb["style"], "middle")
            if i < len(s["rows"]) - 1:
                line_y = rows[i + 1] - gap
                self.line(slide, f"sum-{i}-divider", div["x"], line_y, div["x"] + div["w"], line_y, div)
        panel = element(a, "next_week_panel_right")
        self.card(slide, "next-panel", box_of(panel["box"]), panel["style"])
        kids = {c["role"]: c for c in panel["children"]}
        over, head, lst = kids["overline_label"], kids["heading"], kids["bullet_list"]
        self.single(slide, "next-label", box_of(over["box"]), s.get("next_label") or over["text"], over["style"], "middle")
        self.single(slide, "next-heading", box_of(head["box"]), s.get("next_title") or head["text"], head["style"], "middle")
        self.bullets(slide, "next-list", box_of(lst["box"]), s["next"], lst["style"])

    # ---------- 덱 ----------
    def active_phase(self, s):
        name = s["archetype"]
        if "phase" in s:
            return s["phase"]
        match = re.search(r"-(도입|정리)", self.d.arch[name].get("layout", ""))
        return match.group(1) if match else self.phase

    def build(self):
        missing = [k for k in REQUIRED_FIELDS if not self.spec.get(k)]
        if missing:
            raise SystemExit(f"deck.json에 필수 항목이 없습니다: {', '.join(missing)}")
        for number, s in enumerate(self.spec["slides"], 1):
            name = s.get("archetype")
            if not hasattr(self, str(name)) or name not in self.d.arch:
                raise SystemExit(f"슬라이드 {number}: 알 수 없는 아키타입 {name}")
            slide = self.prs.slides.add_slide(self.prs.slide_layouts[TITLE_ONLY_LAYOUT])
            slide._element.cSld.set("name", name)
            try:
                if name in ("cover", "closing"):
                    getattr(self, name)(slide, s)
                else:
                    self.phase = self.active_phase(s)
                    self.chrome(slide, number)
                    getattr(self, name)(slide, s)
                if s.get("notes"):
                    slide.notes_slide.notes_text_frame.text = s["notes"]
            except KeyError as e:
                raise SystemExit(f"슬라이드 {number}({name}): 필드 {e} 가 없습니다")
            except IndexError:
                raise SystemExit(f"슬라이드 {number}({name}): 항목 수가 templates.json 규격보다 많습니다")
        return self.prs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--templates")
    ap.add_argument("--spec")
    ap.add_argument("--out")
    ap.add_argument("--list-icons", metavar="단어")
    args = ap.parse_args()
    if args.list_icons:
        names = json.loads((ASSETS / "codepoints.json").read_text(encoding="utf-8"))
        print("\n".join(k for k in names if args.list_icons in k))
        return
    if not (args.templates and args.spec and args.out):
        ap.error("--templates, --spec, --out 이 모두 필요합니다")
    spec_path = Path(args.spec).resolve()
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as tmp:
        prs = Builder(Design(args.templates), spec, spec_path.parent, tmp).build()
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        prs.save(out)
    print(f"완료: {out} ({len(spec['slides'])}장)")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    main()
