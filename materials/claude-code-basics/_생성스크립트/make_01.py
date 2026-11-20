"""1교시 실습 파일 만들기: py -3.14 -X utf8 make_01.py ..

학습자용/누리상사_영업관리팀 (맨 위 파일 6개 + 거래처_윤슬찬푸드 폴더, 그 안 파일 6개)
학습자용/누리상사_영업관리팀.zip, 학습자용/실습_요청문.txt, 강사용/정답_1교시.txt
"""
import io
import shutil
import sys
import zipfile
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from PIL import Image, ImageDraw, ImageFont

import nuri_data as D

FONT = Path("C:/Windows/Fonts/malgun.ttf")
FONT_BD = Path("C:/Windows/Fonts/malgunbd.ttf")
HEAD = Font(bold=True, color="FFFFFF")
FILL = PatternFill("solid", fgColor="1F4E78")


def text(path, s):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(s.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8-sig"))


def xlsx(path, sheet, header, rows, widths, money=()):
    wb = Workbook()
    ws = wb.active
    ws.title = sheet
    ws.append(header)
    for c in ws[1]:
        c.font, c.fill = HEAD, FILL
    for r in rows:
        ws.append(list(r))
    for row in ws.iter_rows(min_row=2):
        for c in row:
            if c.column in money:
                c.number_format = "#,##0"
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "A2"
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)


def quote_pdf(path, q, title):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas

    if "Malgun" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("Malgun", str(FONT)))
        pdfmetrics.registerFont(TTFont("MalgunBd", str(FONT_BD)))
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, invariant=1)
    c.setTitle(title)
    w, h = A4
    c.setFont("MalgunBd", 20)
    c.drawCentredString(w / 2, h - 80, title)
    c.setFont("Malgun", 10)
    y = h - 120
    for line in [f"견적번호: {q['no']}", f"견적일: {q['date']}", "수신: 윤슬찬푸드 구매팀 윤재희 과장",
                 "발신: 누리상사 영업관리팀 김도현", "유효기간: 견적일로부터 30일"]:
        c.drawString(60, y, line)
        y -= 16
    y -= 10
    cols = [60, 250, 340, 430]
    c.setFont("MalgunBd", 10)
    for x, t in zip(cols, ["품목", "수량(개)", "단가(원)", "금액(원)"]):
        c.drawString(x, y, t)
    c.line(60, y - 5, 535, y - 5)
    y -= 22
    c.setFont("Malgun", 10)
    for item, n, p in q["items"]:
        c.drawString(cols[0], y, item)
        c.drawRightString(cols[1] + 60, y, f"{n:,}")
        c.drawRightString(cols[2] + 60, y, f"{p:,}")
        c.drawRightString(cols[3] + 100, y, f"{n * p:,}")
        y -= 18
    c.line(60, y + 8, 535, y + 8)
    s, v, t = D.quote_totals(q)
    for label, val, bold in [("공급가액", s, False), ("부가세(10%)", v, False), ("합계", t, True)]:
        y -= 16
        c.setFont("MalgunBd" if bold else "Malgun", 11 if bold else 10)
        c.drawString(cols[2], y, label)
        c.drawRightString(cols[3] + 100, y, f"{val:,}")
    c.setFont("Malgun", 8)
    c.drawString(60, 50, D.NOTE)
    c.showPage()
    c.save()
    path.write_bytes(buf.getvalue())


def font(size, bold=False):
    return ImageFont.truetype(str(FONT_BD if bold else FONT), size)


def card_jpg(path):
    k = D.CARD
    img = Image.new("RGB", (640, 360), (252, 252, 248))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 640, 14), fill=(46, 125, 80))
    d.text((40, 40), k["company"], font=font(30, True), fill=(46, 125, 80))
    d.text((40, 130), k["name"], font=font(34, True), fill=(30, 30, 30))
    d.text((40, 182), f"{k['dept']} {k['title']}", font=font(20), fill=(70, 70, 70))
    y = 240
    for t in [f"T. {k['tel']}", f"M. {k['mobile']}", f"E. {k['email']}"]:
        d.text((40, y), t, font=font(16), fill=(60, 60, 60))
        y += 24
    d.text((360, 330), "실습용 가상 명함", font=font(12), fill=(150, 150, 150))
    img.save(path, "JPEG", quality=90)


def receipt_jpg(path):
    r = D.RECEIPT
    lines = [(r["shop"], 20, True, "c"), ("영수증", 18, True, "c"), ("-",), (f"일시  {r['date']}", 15, False, "l"), ("-",)]
    for name, n, p in r["items"]:
        lines.append((f"{name} x{n}\t{n * p:,}", 16, False, "l"))
    lines += [("-",), (f"합계\t{D.receipt_total():,}원", 19, True, "l"), ("결제  법인카드(실습용)", 14, False, "l")]
    h = 60 + sum(18 if len(t) == 1 else int(t[1] * 1.7) for t in lines)
    img = Image.new("RGB", (460, h), (250, 249, 244))
    d = ImageDraw.Draw(img)
    y = 30
    for t in lines:
        if len(t) == 1:
            d.line((24, y + 8, 436, y + 8), fill=(120, 120, 120))
            y += 18
            continue
        s, size, bold, align = t
        f = font(size, bold)
        if "\t" in s:
            a, b = s.split("\t")
            d.text((24, y), a, font=f, fill=(30, 30, 30))
            d.text((436 - d.textlength(b, font=f), y), b, font=f, fill=(30, 30, 30))
        else:
            x = (460 - d.textlength(s, font=f)) / 2 if align == "c" else 24
            d.text((x, y), s, font=f, fill=(30, 30, 30))
        y += int(size * 1.7)
    img = img.rotate(-2, expand=True, fillcolor=(205, 200, 190))
    img.save(path, "JPEG", quality=88)


REQUESTS = """[1교시 실습 요청문] 교안 순서대로 복사해 씁니다.

[실습 1-② 목록·요약·행 수 요청]
이 폴더 맨 위에 있는 파일과 폴더 목록을 알려줘.
- 파일마다 직접 열어 본 내용으로 한 줄 요약
- 엑셀 파일(.xlsx)은 파일마다 데이터 행 수(머리글 행 제외)
- 마지막에 행이 가장 많은 엑셀 파일 이름과 행 수
하위 폴더는 이름만 적고 안은 열지 마.

[실습 2-① 거래처 폴더 통째로 요약]
'거래처_윤슬찬푸드' 폴더의 파일을 모두 열어 보고 파일별로 정리해 줘.
- 표 열: 파일 이름 / 형식 / 핵심 내용 / 핵심 숫자
- 핵심 숫자: 견적서는 합계(부가세 포함), 거래내역은 거래 건수와 공급가액 합계, 영수증은 결제 금액
- 마지막에 윤슬찬푸드와 지금 진행 중인 일을 세 줄로
파일은 읽기만 하고 고치지 마.

[실습 2-② @로 견적서 2개만 비교]
@견적서_윤슬찬푸드_2026-10-08.pdf @견적서_윤슬찬푸드_2026-10-22_수정.pdf
이 두 견적서만 비교해 줘. 다른 파일은 열지 마.
- 표 열: 품목 / 1차 수량·단가·금액 / 수정 수량·단가·금액 / 바뀐 점
- 마지막 줄: 공급가액과 합계(부가세 포함)가 각각 얼마 달라졌는지

[실습 3-② 수동으로 실행]
원본 폴더 내용을 정리한 요약 문서를 만들어줘.
- 읽을 곳: '원본' 폴더. 원본 폴더의 파일은 읽기만 하고, 고치거나 옮기거나 지우지 마.
- 쓸 곳: '출력' 폴더에만 써.
- 파일 이름: 폴더요약_수동.md
- 내용: 원본 맨 위의 파일 목록 표(파일 이름, 형식, 한 줄 요약), 엑셀 파일별 데이터 행 수(머리글 제외), '거래처_윤슬찬푸드' 폴더의 파일 수

[실습 3-③ 자동으로 실행] 위 요청에서 파일 이름만 폴더요약_자동.md 로 바꿔 새 세션에서 보냄
"""


def main(out):
    out = Path(out) / "01_Claude_Code와_작업폴더"
    A = D.answers()
    # 교안 정답 표와 맞는지 먼저 확인
    assert A["xlsx_rows"] == {"거래처목록.xlsx": 14, "상품목록.xlsx": 12,
                              "2026_상반기_담당자별_실적.xlsx": 5, "반품접수_2026_상반기.xlsx": 17}, A["xlsx_rows"]
    assert A["q1"] == (3_275_000, 327_500, 3_602_500), A["q1"]
    assert A["q2"] == (3_335_000, 333_500, 3_668_500), A["q2"]
    assert A["trade_count"] == 11, A["trade_count"]
    assert A["trade_sum"] == 9_940_000, A["trade_sum"]
    assert A["receipt"] == 84_000
    counts = sorted(A["xlsx_rows"].values())
    assert len(set(counts)) == len(counts)  # 행 수 동률 없음

    for sub in ("학습자용", "강사용"):
        if (out / sub).exists():
            shutil.rmtree(out / sub)
    root = out / "학습자용" / D.ROOT
    cdir = root / D.CLIENT_DIR
    cdir.mkdir(parents=True)

    xlsx(root / "거래처목록.xlsx", "거래처", ["거래처코드", "거래처명", "업종", "지역", "담당자"], D.CLIENTS, [12, 16, 18, 16, 10])
    xlsx(root / "상품목록.xlsx", "상품", ["상품코드", "상품명", "규격", "단위", "기준단가(원)"], D.PRODUCTS, [10, 20, 22, 8, 14], money=(5,))
    xlsx(root / "2026_상반기_담당자별_실적.xlsx", "상반기", ["담당자", "담당 지역", "상반기 매출(원)", "상반기 목표(원)"], D.H1_SALES, [10, 16, 18, 18], money=(3, 4))
    xlsx(root / "반품접수_2026_상반기.xlsx", "반품", ["접수일", "거래처", "상품", "수량", "사유"], D.RETURNS, [12, 14, 20, 8, 12])
    text(root / "팀_업무분장.txt", D.ASSIGN)
    text(root / "영업회의_2026-10-27.txt", D.MEETING_TEAM)

    quote_pdf(cdir / "견적서_윤슬찬푸드_2026-10-08.pdf", D.QUOTE_1, "견 적 서")
    quote_pdf(cdir / "견적서_윤슬찬푸드_2026-10-22_수정.pdf", D.QUOTE_2, "견 적 서 (수정)")
    xlsx(cdir / "거래내역_윤슬찬푸드_2026.xlsx", "2026", ["거래일", "품목", "수량", "단가(원)", "공급가액(원)"], D.trade_rows(), [12, 20, 10, 12, 16], money=(3, 4, 5))
    card_jpg(cdir / "명함_윤재희_윤슬찬푸드.jpg")
    receipt_jpg(cdir / "영수증_미팅식대_2026-10-15.jpg")
    text(cdir / "미팅메모_윤슬찬푸드_2026-10-15.txt", D.MEMO)

    # 만든 파일을 다시 읽어 확인
    for name, n in A["xlsx_rows"].items():
        assert load_workbook(root / name).active.max_row - 1 == n, name
    from pypdf import PdfReader
    assert "3,602,500" in PdfReader(str(cdir / "견적서_윤슬찬푸드_2026-10-08.pdf")).pages[0].extract_text()
    assert "3,668,500" in PdfReader(str(cdir / "견적서_윤슬찬푸드_2026-10-22_수정.pdf")).pages[0].extract_text()
    assert len([p for p in root.iterdir()]) == 7 and len(list(cdir.iterdir())) == 6

    zpath = out / "학습자용" / f"{D.ROOT}.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(root.rglob("*")):
            z.write(p, p.relative_to(root.parent).as_posix())
    text(out / "학습자용" / "실습_요청문.txt", REQUESTS)

    s1, v1, t1 = A["q1"]
    s2, v2, t2 = A["q2"]
    key = f"""[1교시 정답] 누리상사 영업관리팀 (강사용, 배포하지 않음)

실습 1: 맨 위 파일 6개 + 폴더 1개(거래처_윤슬찬푸드), 엑셀 4개
""" + "\n".join(f"- {k}: {v}행" for k, v in A["xlsx_rows"].items()) + f"""
- 가장 많은 파일: 반품접수_2026_상반기.xlsx 17행 (18이면 머리글까지 센 것)

실습 2-① 거래처_윤슬찬푸드 파일 6개
- 견적서 1차(2026-10-08, NR-Q-2610-014): 공급가액 {s1:,} / 부가세 {v1:,} / 합계 {t1:,}원
- 견적서 수정(2026-10-22, NR-Q-2610-021): 공급가액 {s2:,} / 부가세 {v2:,} / 합계 {t2:,}원
- 거래내역 2026: {A['trade_count']}건, 공급가액 합계 {A['trade_sum']:,}원
- 명함: 윤슬찬푸드 구매팀 과장 윤재희
- 영수증: 2026-10-15 가온한식, {A['receipt']:,}원 (정식 4×18,000 + 음료 4×3,000)
- 미팅메모 2026-10-15(목): 박스(대) 850→800원 요청, 파우치 3,000→3,500개, 첫 납품 11/5(목), 수정 견적 10/22(목)까지

실습 2-② 견적서 비교
- 골판지 박스(대): 2,000개, 850→800원, 1,700,000→1,600,000 (-100,000)
- 보냉 파우치: 3,000→3,500개, 320원, 960,000→1,120,000 (+160,000)
- 아이스팩(500g): 1,500개, 410원, 615,000 그대로
- 공급가액 +{s2 - s1:,}원, 합계 +{t2 - t1:,}원

실습 3: 출력에 폴더요약_수동.md, 폴더요약_자동.md / 원본 맨 위 7개 그대로, 거래처_윤슬찬푸드 6개
"""
    text(out / "강사용" / "정답_1교시.txt", key)
    print("완료", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "..")
