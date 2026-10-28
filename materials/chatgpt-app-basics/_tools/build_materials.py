# [기본] ChatGPT 앱 기본 - 차시별 실습 자료 전체 만들기
# 필요: Python 3.10 이상, openpyxl, xlwt, xlrd, Pillow, python-docx, python-pptx
# 사용: python build_materials.py [자료 폴더 경로]   (기본: 이 파일의 한 단계 위 폴더 = chatgpt-app-basics)
# 9월·10월 일보는 make_ilbo.py / make_ilbo_10.py(씨앗값 고정)를 그대로 실행해 만든다.
# 5차시 시작 자료의 '9월_판매요약.xlsx'는 수식과 함께 계산 결과 값도 넣는다(Excel로 한 번 열어 저장한 상태와 같게).
import datetime as dt
import os
import shutil
import subprocess
import sys
import tempfile
from collections import OrderedDict

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font

TOOLS = os.path.dirname(os.path.abspath(__file__))
MAT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(TOOLS)
PY = sys.executable
PROJ = "다온유통_영업지원팀"
S = {1: "01_codex-agent", 2: "02_permissions-git", 3: "03_batch-files",
     4: "04_outputs-edit", 5: "05_agents-skills"}

STORES = ["강남점", "송파점", "분당점", "일산점", "인천점", "수원점"]
ITEMS = [("생수 2L(6입)", 5900), ("라면 5입", 4500), ("즉석밥 12입", 13800),
         ("참치캔 3입", 7980), ("식용유 1.8L", 8900), ("두루마리 휴지 30롤", 15900)]
ITEM_ORDER = {n: i for i, (n, _) in enumerate(ITEMS)}
STAFF = ["김서연", "이도현", "박지우", "최민준", "정하은", "윤지호"]
FONT = "맑은 고딕"


def wtxt(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\r\n" if path.endswith(".txt") else "\n") as f:
        f.write(text)


def proj(n):
    return os.path.join(MAT, S[n], PROJ)


# ---------------------------------------------------------------- 1차시: 처음 8개 파일
CLIENTS = ["한빛마트", "새솔상회", "푸른들식자재", "동네곳간", "바른식품", "늘봄마트", "온새미유통", "다솜상회",
           "해오름마트", "가온식자재", "미리내상회", "초록마켓", "별빛마트", "누리식품", "한결상회", "소담마트",
           "이음식자재", "다래마트"]
SALES8 = [4820, 3910, 4150, 2980, 3340, 3620]
GOAL8 = [4700, 4000, 4100, 3100, 3300, 3600]
SALES9 = [5130, 3870, 4290, 3050, 3280, 3710]
GOAL9 = [5000, 4000, 4200, 3100, 3400, 3700]
RETURNS = """2026-09-02,가온식자재,두루마리 휴지 30롤,10,수량 착오
2026-09-02,다솜상회,생수 2L(6입),9,유통기한 임박
2026-09-03,다래마트,생수 2L(6입),6,포장 파손
2026-09-03,푸른들식자재,라면 5입,8,포장 파손
2026-09-04,온새미유통,라면 5입,2,포장 파손
2026-09-04,이음식자재,식용유 1.8L,3,오배송
2026-09-07,소담마트,식용유 1.8L,1,포장 파손
2026-09-08,새솔상회,참치캔 3입,10,수량 착오
2026-09-10,누리식품,즉석밥 12입,9,포장 파손
2026-09-10,별빛마트,두루마리 휴지 30롤,6,포장 파손
2026-09-11,바른식품,식용유 1.8L,11,포장 파손
2026-09-14,누리식품,생수 2L(6입),4,포장 파손
2026-09-18,누리식품,생수 2L(6입),10,포장 파손
2026-09-21,가온식자재,참치캔 3입,8,오배송
2026-09-21,가온식자재,참치캔 3입,11,유통기한 임박
2026-09-21,새솔상회,참치캔 3입,4,수량 착오
2026-09-21,한결상회,라면 5입,5,유통기한 임박
2026-09-22,다래마트,식용유 1.8L,6,수량 착오
2026-09-22,한결상회,라면 5입,10,포장 파손
2026-09-23,초록마켓,참치캔 3입,8,수량 착오
2026-09-28,다래마트,참치캔 3입,6,오배송
2026-09-28,늘봄마트,두루마리 휴지 30롤,4,포장 파손
2026-09-30,이음식자재,즉석밥 12입,1,포장 파손"""


def bold_header(ws):
    for c in ws[1]:
        c.font = Font(bold=True)


def make_base_files(d):
    os.makedirs(d, exist_ok=True)
    # 거래처목록.xlsx (18행)
    wb = Workbook(); ws = wb.active; ws.title = "거래처목록"
    ws.append(["거래처코드", "거래처명", "담당지점", "담당자"])
    for i, n in enumerate(CLIENTS):
        ws.append([f"C{101 + i}", n, STORES[i % 6], STAFF[i % 6]])
    bold_header(ws); ws.column_dimensions["B"].width = 14
    wb.save(os.path.join(d, "거래처목록.xlsx"))
    # 8월·9월 지점별 매출 (6행, 만원, 전 품목)
    for m, sales, goal in [(8, SALES8, GOAL8), (9, SALES9, GOAL9)]:
        wb = Workbook(); ws = wb.active; ws.title = f"{m}월"
        ws.append(["지점", "매출(만원)", "목표(만원)"])
        for s, a, g in zip(STORES, sales, goal):
            ws.append([s, a, g])
        for r in range(2, 8):
            for c in (2, 3):
                ws.cell(row=r, column=c).number_format = "#,##0"
        bold_header(ws)
        wb.save(os.path.join(d, f"{m}월_지점별_매출.xlsx"))
    # 반품접수_9월.xlsx (23행)
    wb = Workbook(); ws = wb.active; ws.title = "반품접수"
    ws.append(["접수일", "거래처명", "품목", "수량", "사유"])
    for line in RETURNS.splitlines():
        a, b, c, q, r = line.split(",")
        ws.append([dt.date.fromisoformat(a), b, c, int(q), r])
        ws.cell(row=ws.max_row, column=1).number_format = "yyyy-mm-dd"
    bold_header(ws)
    for col, w in zip("ABCDE", (12, 14, 20, 6, 14)):
        ws.column_dimensions[col].width = w
    wb.save(os.path.join(d, "반품접수_9월.xlsx"))
    make_minutes(os.path.join(d, "주간회의록_0921.docx"))
    make_form(os.path.join(d, "주간보고_양식.docx"))
    wtxt(os.path.join(d, "팀_업무분장.txt"), TEAM_TXT)
    wtxt(os.path.join(d, "매장점검_체크리스트.txt"), CHECK_TXT)


TEAM_TXT = """다온유통 영업지원팀 업무분장 (2026년 9월 기준)

정식 지점명 (6개): 강남점, 송파점, 분당점, 일산점, 인천점, 수원점
※ 문서·일보에는 위 정식 지점명을 씁니다. (예: '강남'이 아니라 '강남점')

담당자    담당 지점    주요 업무
김서연    강남점       일보 취합, 거래처 3곳 관리
이도현    송파점       일보 취합, 거래처 3곳 관리
박지우    분당점       일보 취합, 거래처 3곳 관리
최민준    일산점       일보 취합, 거래처 3곳 관리
정하은    인천점       일보 취합, 거래처 3곳 관리
윤지호    수원점       일보 취합, 거래처 3곳 관리

공통 업무
- 주간보고: 매주 금요일 오후 5시까지 '주간보고_양식.docx'로 공유
- 반품 접수: 접수 당일 '반품접수' 파일에 기록
- 매장 점검: 월 1회 담당 지점 방문, '매장점검_체크리스트.txt' 항목 확인
"""

CHECK_TXT = """다온유통 매장 방문 점검 체크리스트

점검일:            지점:            점검자:

[ ] 1. 주요 6개 품목 진열 상태 (생수·라면·즉석밥·참치캔·식용유·휴지)
[ ] 2. 가격표와 행사 안내물이 실제 판매가와 같은지
[ ] 3. 유통기한 임박 상품 분리 진열 여부
[ ] 4. 냉장 진열대 온도와 작동 상태
[ ] 5. 창고 재고와 일보 수량 차이
[ ] 6. 포장 파손 상품 보관과 반품 접수 여부
[ ] 7. 매장 청결과 통로 안전
[ ] 8. 지점 건의 사항 기록

※ 점검 결과는 주간보고 '반품·특이사항'에 한 줄로 적습니다.
"""


def set_doc_font(doc):
    from docx.oxml.ns import qn
    for name in ("Normal", "Title", "Heading 1", "Heading 2"):
        try:
            st = doc.styles[name]
        except KeyError:
            continue
        st.font.name = FONT
        rpr = st.element.get_or_add_rPr()
        rf = rpr.find(qn("w:rFonts"))
        if rf is None:
            rf = rpr.makeelement(qn("w:rFonts"), {})
            rpr.append(rf)
        for k in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
            rf.set(qn(k), FONT)
        for k in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
            if rf.get(qn(k)) is not None:
                del rf.attrib[qn(k)]


def new_doc():
    from docx import Document
    doc = Document()
    set_doc_font(doc)
    return doc


def add_table(doc, rows, widths=None):
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.style = "Table Grid"
    for i, r in enumerate(rows):
        for j, v in enumerate(r):
            cell = t.cell(i, j)
            cell.text = str(v)
            if i == 0:
                for run in cell.paragraphs[0].runs:
                    run.bold = True
    return t


def make_minutes(path):
    doc = new_doc()
    doc.add_heading("영업지원팀 주간회의록", level=1)
    doc.add_paragraph("일시: 2026년 9월 21일(월) 오전 10:00~10:40\n장소: 본사 3층 회의실\n"
                      "참석: 김서연, 이도현, 박지우, 최민준, 정하은, 윤지호 (6명)")
    doc.add_heading("안건 1. 8월 실적과 9월 목표 점검", level=2)
    doc.add_paragraph("- 8월 지점별 매출은 '8월_지점별_매출.xlsx'로 공유함. 강남점은 목표를 넘었고, 송파점·일산점은 목표에 못 미침.\n"
                      "- 9월 실적은 월말 마감 뒤 '9월_지점별_매출.xlsx'로 목표와 비교하기로 함.\n"
                      "- 9월 25일(금) 추석 당일은 전 지점 휴무로 일보가 없음.")
    doc.add_heading("안건 2. 9월 반품 접수 현황", level=2)
    doc.add_paragraph("- 9월 들어 포장 파손으로 들어온 반품이 가장 많음. 상세 내역은 '반품접수_9월.xlsx' 참고.\n"
                      "- 포장 파손이 반복되는 거래처는 담당자가 배송 상태를 확인하기로 함.")
    doc.add_heading("안건 3. 주간보고 양식 통일", level=2)
    doc.add_paragraph("- 지점 담당자마다 주간보고 양식과 항목 순서가 달라 취합에 시간이 걸림.\n"
                      "- 결정: 다음 주부터 '주간보고_양식.docx'(항목 4개: 이번 주 요약 / 지점별 매출 / 반품·특이사항 / 다음 주 계획)로 통일.\n"
                      "- 주간보고는 매주 금요일 오후 5시까지 '주간보고_양식.docx'로 공유한다.")
    doc.add_heading("결정 사항과 할 일", level=2)
    add_table(doc, [["할 일", "담당", "기한"],
                    ["9월 지점별 매출 마감 후 목표 대비 비교", "김서연", "10월 첫 주"],
                    ["포장 파손 반품 거래처 배송 상태 확인", "각 지점 담당자", "9월 24일"],
                    ["주간보고 양식 통일 공지", "이도현", "9월 22일"]])
    doc.save(path)


def make_form(path):
    doc = new_doc()
    doc.add_heading("영업지원팀 주간보고 (  월  주차)", level=1)
    doc.add_paragraph("작성자:                    작성일:")
    for h, guide in [("1. 이번 주 요약", "(3줄 이내)"), ("2. 지점별 매출", "(지점별 표)"),
                     ("3. 반품·특이사항", "(반품 건수와 수량, 특이사항)"), ("4. 다음 주 계획", "(할 일 목록)")]:
        doc.add_heading(h, level=2)
        doc.add_paragraph(guide)
    doc.save(path)


# ---------------------------------------------------------------- 1차시 결과: 폴더요약.md
def folder_summary(title, extra_line=False):
    t = f"""# {title}

읽은 곳: '원본' 폴더 (읽기만 함)

| 파일 이름 | 확장자 | 한 줄 요약 |
| --- | --- | --- |
| 거래처목록.xlsx | .xlsx | 거래처 18곳의 코드·이름·담당 지점·담당자 목록 |
| 8월_지점별_매출.xlsx | .xlsx | 6개 지점의 8월 매출과 목표 (만원) |
| 9월_지점별_매출.xlsx | .xlsx | 6개 지점의 9월 매출과 목표 (만원) |
| 반품접수_9월.xlsx | .xlsx | 9월 반품 접수 23건 (접수일·거래처명·품목·수량·사유) |
| 주간회의록_0921.docx | .docx | 9월 21일(월) 주간회의 기록. 안건 3개, 주간보고 양식 통일 결정 |
| 주간보고_양식.docx | .docx | 비어 있는 주간보고 양식 (항목 4개: 이번 주 요약, 지점별 매출, 반품·특이사항, 다음 주 계획) |
| 팀_업무분장.txt | .txt | 담당자 6명의 담당 지점과 정식 지점명 6개 |
| 매장점검_체크리스트.txt | .txt | 매장 방문 점검 항목 8개 |

전체 파일 수: 8개
"""
    t += """
## 엑셀 파일별 데이터 행 수 (머리글 제외)

| 파일 | 데이터 행 |
| --- | --- |
| 거래처목록.xlsx | 18 |
| 8월_지점별_매출.xlsx | 6 |
| 9월_지점별_매출.xlsx | 6 |
| 반품접수_9월.xlsx | 23 |
"""
    return t


RETURN_SUMMARY = """# 9월 반품 접수 사유별 요약

기준: '원본/반품접수_9월.xlsx' (읽기만 함)

| 사유 | 건수 | 수량 합계 |
| --- | --- | --- |
| 포장 파손 | 12 | 72 |
| 수량 착오 | 5 | 38 |
| 유통기한 임박 | 3 | 25 |
| 오배송 | 3 | 17 |
| **합계** | **23** | **152** |

정렬: 수량 합계가 큰 순서
"""


# ---------------------------------------------------------------- 3차시 결과: 이름 변경·형식 변환·통합
def read_ilbo(path):
    """(시트 이름 목록, 머리글, 데이터 행) - xls/xlsx 모두"""
    if path.endswith(".xls"):
        import xlrd
        b = xlrd.open_workbook(path)
        s = b.sheet_by_name("일보")
        hdr = s.row_values(0)
        rows = []
        for i in range(1, s.nrows):
            v = s.row_values(i)
            v[0] = xlrd.xldate_as_datetime(v[0], b.datemode).date()
            v[3] = int(v[3]); v[4] = int(v[4])
            rows.append(v)
        return b.sheet_names(), hdr, rows
    wb = load_workbook(path)
    vals = list(wb["일보"].values)
    rows = [list(r) for r in vals[1:]]
    for r in rows:
        if isinstance(r[0], dt.datetime):
            r[0] = r[0].date()
    return wb.sheetnames, list(vals[0]), rows


def name_date(fname, month):
    """파일 안 날짜 열을 우선, 비어 있으면 파일 이름에서 날짜를 읽는다."""
    import re
    m = re.search(r"(\d{4})(\d{2})(\d{2})", fname)
    if m:
        return dt.date(int(m[1]), int(m[2]), int(m[3]))
    raise ValueError(fname)


def rename_copies(p, month, src_dir_name, dst_dir_name):
    src = os.path.join(p, "원본", src_dir_name)
    dst = os.path.join(p, "출력", dst_dir_name)
    os.makedirs(dst, exist_ok=True)
    table = []
    for f in sorted(os.listdir(src)):
        _, _, rows = read_ilbo(os.path.join(src, f))
        if rows:
            d = rows[0][0]
            note = ""
        else:
            d = name_date(f, month)
            note = "데이터 행 없음 → 파일 이름의 날짜 사용"
        ext = os.path.splitext(f)[1]
        new = f"일보_{d.isoformat()}{ext}"
        if f == "12.09 일보.xlsx":
            note = "이름이 일.월 순서 → 날짜 열(9/12)로 확인"
        if "(최종)" in f:
            note = "이름에 날짜 없음 → 날짜 열로 확인"
        table.append((d, f, new, note))
    table.sort()
    news = [t[2] for t in table]
    assert len(set(news)) == len(news), "바꿀 이름 겹침"
    for _, f, new, _ in table:
        shutil.copy2(os.path.join(src, f), os.path.join(dst, new))
    return table


def rename_md(table):
    s = "# 9월 일보 이름 변경 목록\n\n- 원본: '원본/9월_일보' (그대로 둠)\n- 복사본: '출력/9월_일보'\n" \
        "- 규칙: 일보_YYYY-MM-DD + 원래 확장자. 날짜는 파일 안 '날짜' 열과 파일 이름을 함께 보고 정함\n\n" \
        "| 날짜 | 지금 이름 | 바꾼 이름 | 비고 |\n| --- | --- | --- | --- |\n"
    for d, f, new, note in table:
        s += f"| {d.month}/{d.day} | {f} | {new} | {note} |\n"
    s += f"\n전체 {len(table)}개, 바꿀 이름 겹침 없음\n"
    return s


CANON = {"강남": "강남점", "분당지점": "분당점", "수원 점": "수원점", "송파": "송파점"}


def integrate(p, month, dir_name, out_name):
    """통합 + 전처리 정보 반환"""
    src = os.path.join(p, "출력", dir_name)
    info = OrderedDict(files=0, raw_rows=0, raw_qty=0, colmap=[], fixed=[], dups=[], negs=[], empty=[], memo=[])
    clean = []
    seen = set()
    for f in sorted(os.listdir(src)):
        sheets, hdr, rows = read_ilbo(os.path.join(src, f))
        info["files"] += 1
        info["raw_rows"] += len(rows)
        info["raw_qty"] += sum(r[3] for r in rows)
        if hdr[1] == "매장":
            info["colmap"].append(f)
        if not rows:
            info["empty"].append(f)
        for sh in sheets:
            if sh != "일보":
                wb = load_workbook(os.path.join(src, f))
                info["memo"].append((f, sh, wb[sh]["A1"].value))
        for i, r in enumerate(rows, start=2):
            r = list(r)
            key = tuple(r)
            if key in seen:
                info["dups"].append((f, i, r)); continue
            seen.add(key)
            if r[3] < 0:
                info["negs"].append((f, i, r)); continue
            if r[1] in CANON:
                info["fixed"].append((f, r[1], CANON[r[1]]))
                r[1] = CANON[r[1]]
            clean.append(r + [f])
    clean.sort(key=lambda r: (r[0], STORES.index(r[1]), ITEM_ORDER[r[2]]))
    wb = Workbook(); ws = wb.active; ws.title = "통합"
    ws.append(["날짜", "지점", "품목", "판매수량", "판매금액", "출처파일"])
    for r in clean:
        ws.append(r)
        ws.cell(row=ws.max_row, column=1).number_format = "yyyy-mm-dd"
        ws.cell(row=ws.max_row, column=4).number_format = "#,##0"
        ws.cell(row=ws.max_row, column=5).number_format = "#,##0"
    bold_header(ws)
    for col, w in zip("ABCDEF", (12, 9, 20, 10, 12, 24)):
        ws.column_dimensions[col].width = w
    wb.save(os.path.join(p, "출력", out_name))
    info["rows"] = len(clean)
    info["qty"] = sum(r[3] for r in clean)
    info["amt"] = sum(r[4] for r in clean)
    return clean, info


def preprocess_md(info, title, src_label, out_label):
    from collections import Counter
    def md(d):
        return f"{d.month}/{d.day}"
    s = f"# {title}\n\n- 대상: '{src_label}' 파일 {info['files']}개\n- 결과: '{out_label}' (시트 '통합')\n" \
        "- 통합 열: 날짜, 지점, 품목, 판매수량, 판매금액, 출처파일\n" \
        "- 정렬: 날짜 → 지점(강남점·송파점·분당점·일산점·인천점·수원점) → 품목(일보에 적힌 순서)\n\n"
    s += "## 1. 열 대응\n\n| 원래 열 | 통합 열 | 해당 파일 |\n| --- | --- | --- |\n"
    files = ", ".join(info["colmap"])
    s += f"| 매장 | 지점 | {files} ({len(info['colmap'])}개) |\n| 수량 | 판매수량 | 같음 |\n\n"
    s += "## 2. 고친 행 (지점명 표기)\n\n정식 지점명은 '원본/팀_업무분장.txt'의 6개(강남점·송파점·분당점·일산점·인천점·수원점)를 따름.\n\n" \
         "| 파일 | 원래 표기 | 고친 이름 | 행 수 |\n| --- | --- | --- | --- |\n"
    c = Counter(info["fixed"])
    for (f, a, b), n in c.items():
        s += f"| {f} | {a} | {b} | {n} |\n"
    s += f"| **합계** |  |  | **{len(info['fixed'])}** |\n\n"
    s += "## 3. 뺀 행\n\n| 이유 | 파일 | 엑셀 행 | 내용 (날짜·지점·품목·판매수량·판매금액) |\n| --- | --- | --- | --- |\n"
    for f, i, r in info["dups"]:
        s += f"| 중복 행 (모든 칸이 같은 행이 앞에 있음, 하나만 남김) | {f} | {i} | {md(r[0])} {r[1]} {r[2]} {r[3]} {r[4]:,} |\n"
    for f, i, r in info["negs"]:
        s += f"| 판매수량 음수 | {f} | {i} | {md(r[0])} {r[1]} {r[2]} {r[3]} {r[4]:,} |\n"
    dq = sum(r[3] for _, _, r in info["dups"]); nq = sum(r[3] for _, _, r in info["negs"])
    s += f"\n- 중복 {len(info['dups'])}행 (판매수량 {dq}), 음수 {len(info['negs'])}행 (판매수량 {nq})\n\n"
    s += "## 4. 통합에 넣지 않은 것\n\n"
    if info["empty"]:
        for f in info["empty"]:
            s += f"- 빈 파일: {f} (머리글만 있고 데이터 행 0개. 9/25 추석 당일, 판매 기록 없음)\n"
    else:
        s += "- 빈 파일: 없음\n"
    if info["memo"]:
        for f, sh, v in info["memo"]:
            s += f"- '{sh}' 시트: {f} - \"{v}\"\n"
    else:
        s += "- '일보' 밖의 다른 시트: 없음\n"
    s += "\n## 5. 결과\n\n| 항목 | 값 |\n| --- | --- |\n"
    s += f"| 파일 수 | {info['files']}개 |\n| 파일별 데이터 행 수의 합 | {info['raw_rows']:,}행 |\n" \
         f"| 뺀 행 | {len(info['dups']) + len(info['negs'])}행 (중복 {len(info['dups'])} + 음수 {len(info['negs'])}) |\n" \
         f"| 통합 결과 행 수 | {info['rows']:,}행 |\n| 파일별 판매수량의 합 | {info['raw_qty']:,} |\n" \
         f"| 통합 판매수량 합계 | {info['qty']:,} |\n| 통합 판매금액 합계 | {info['amt']:,}원 |\n"
    return s


def build_s4_outputs(p):
    """3차시 결과물을 p(04 또는 05의 프로젝트 폴더)에 만든다."""
    table = rename_copies(p, 9, "9월_일보", "9월_일보")
    wtxt(os.path.join(p, "출력", "이름변경목록.md"), rename_md(table))
    os.makedirs(os.path.join(p, "출력", "스크립트"), exist_ok=True)
    shutil.copy2(os.path.join(TOOLS, "형식변환.py"), os.path.join(p, "출력", "스크립트", "형식변환.py"))
    subprocess.run([PY, os.path.join(TOOLS, "형식변환.py"), p], check=True)
    clean, info = integrate(p, 9, "9월_일보", "9월_일보통합.xlsx")
    wtxt(os.path.join(p, "출력", "전처리기록.md"),
         preprocess_md(info, "9월 일보 전처리 기록", "출력/9월_일보", "출력/9월_일보통합.xlsx"))
    return clean, info


# ---------------------------------------------------------------- 4차시 결과물
WEEKS9 = [("1주차", dt.date(2026, 9, 1), dt.date(2026, 9, 6)), ("2주차", dt.date(2026, 9, 7), dt.date(2026, 9, 13)),
          ("3주차", dt.date(2026, 9, 14), dt.date(2026, 9, 20)), ("4주차", dt.date(2026, 9, 21), dt.date(2026, 9, 27)),
          ("5주차", dt.date(2026, 9, 28), dt.date(2026, 9, 30))]
NEXT_PLAN = ["10월 일보 정리 규칙을 문서로 남기기", "포장 파손 반품이 많은 거래처 확인", "강남점 냉장 진열대 점검 결과 확인"]


def stats(clean):
    tq = sum(r[3] for r in clean); ta = sum(r[4] for r in clean)
    st = [(s, sum(r[3] for r in clean if r[1] == s), sum(r[4] for r in clean if r[1] == s)) for s in STORES]
    wk = [(n, a, b, sum(r[3] for r in clean if a <= r[0] <= b), sum(r[4] for r in clean if a <= r[0] <= b))
          for n, a, b in WEEKS9]
    days = sorted({r[0] for r in clean})
    daily = OrderedDict((d, sum(r[3] for r in clean if r[0] == d)) for d in days)
    return tq, ta, st, wk, days, daily


EXPECT_MD = """# 9월 판매 기대값 (기준: 출력/9월_일보통합.xlsx)
| 항목 | 기대값 |
| --- | --- |
| 9월 총판매수량 | 22,357 |
| 9월 총매출(판매금액 합계) | 202,883,040원 |
| 지점 수 | 6 |
| 판매 기록이 있는 날 | 29일 (9/25 추석 당일은 일보 없음) |
| 매출 1위 지점(판매금액 기준) | 강남점 39,353,380원 |
"""


def make_summary_xlsx(p, clean):
    path = os.path.join(p, "출력", "9월_판매요약.xlsx")
    wb = Workbook()
    ws1 = wb.active; ws1.title = "지점별"
    ws2 = wb.create_sheet("주차별"); ws3 = wb.create_sheet("데이터")
    ws3.append(["날짜", "지점", "품목", "판매수량", "판매금액", "출처파일"])
    for r in clean:
        ws3.append(r)
        ws3.cell(row=ws3.max_row, column=1).number_format = "yyyy-mm-dd"
        ws3.cell(row=ws3.max_row, column=4).number_format = "#,##0"
        ws3.cell(row=ws3.max_row, column=5).number_format = "#,##0"
    ws1.append(["지점", "판매수량", "판매금액", "매출비중"])
    for i, s in enumerate(STORES, start=2):
        ws1.append([s, f"=SUMIFS(데이터!D:D,데이터!B:B,A{i})", f"=SUMIFS(데이터!E:E,데이터!B:B,A{i})", f"=C{i}/$C$8"])
    ws1.append(["합계", "=SUM(B2:B7)", "=SUM(C2:C7)", "=SUM(D2:D7)"])
    for r in range(2, 9):
        ws1.cell(row=r, column=2).number_format = "#,##0"
        ws1.cell(row=r, column=3).number_format = "#,##0"
        ws1.cell(row=r, column=4).number_format = "0.0%"
    ws1["A8"].font = Font(bold=True)
    ws2.append(["주차", "시작일", "종료일", "판매수량", "판매금액"])
    for i, (n, a, b) in enumerate(WEEKS9, start=2):
        ws2.append([n, a, b, f'=SUMIFS(데이터!D:D,데이터!A:A,">="&B{i},데이터!A:A,"<="&C{i})',
                    f'=SUMIFS(데이터!E:E,데이터!A:A,">="&B{i},데이터!A:A,"<="&C{i})'])
    ws2.append(["합계", None, None, "=SUM(D2:D6)", "=SUM(E2:E6)"])
    for r in range(2, 8):
        ws2.cell(row=r, column=2).number_format = "yyyy-mm-dd"
        ws2.cell(row=r, column=3).number_format = "yyyy-mm-dd"
        ws2.cell(row=r, column=4).number_format = "#,##0"
        ws2.cell(row=r, column=5).number_format = "#,##0"
    ws2["A7"].font = Font(bold=True)
    for ws, widths in [(ws1, (10, 10, 14, 10)), (ws2, (8, 12, 12, 10, 14)), (ws3, (12, 9, 20, 10, 12, 24))]:
        bold_header(ws)
        for col, w in zip("ABCDEF", widths):
            ws.column_dimensions[col].width = w
    wb.save(path)
    tq, ta, st, wk, _, _ = stats(clean)
    vals = {"지점별": {}, "주차별": {}}
    for i, (s, q, a) in enumerate(st, start=2):
        vals["지점별"].update({f"B{i}": q, f"C{i}": a, f"D{i}": a / ta})
    vals["지점별"].update({"B8": tq, "C8": ta, "D8": sum(a / ta for _, _, a in st)})
    for i, w in enumerate(wk, start=2):
        vals["주차별"].update({f"D{i}": w[3], f"E{i}": w[4]})
    vals["주차별"].update({"D7": tq, "E7": ta})
    inject_cached_values(path, vals)
    return path


def inject_cached_values(path, vals):
    """수식 칸에 계산 결과(<v>)를 함께 넣는다. Excel로 한 번 열어 저장한 파일처럼(4차시 ⑥),
    수식은 그대로 두고 다른 프로그램이 읽어도 결과 숫자가 보이게 한다."""
    import re
    import zipfile
    z = zipfile.ZipFile(path)
    items = {n: z.read(n) for n in z.namelist()}
    z.close()
    wbx = items["xl/workbook.xml"].decode("utf-8")
    rels = items["xl/_rels/workbook.xml.rels"].decode("utf-8")
    for sheet, cells in vals.items():
        rid = re.search(rf'<sheet[^>]*name="{sheet}"[^>]*r:id="(rId\d+)"', wbx).group(1)
        target = re.search(rf'<Relationship[^>]*Id="{rid}"[^>]*Target="([^"]+)"', rels) or \
            re.search(rf'<Relationship[^>]*Target="([^"]+)"[^>]*Id="{rid}"', rels)
        name = "xl/" + target.group(1).lstrip("/").replace("xl/", "")
        xml = items[name].decode("utf-8")
        for ref, v in cells.items():
            pat = re.compile(rf'(<c r="{ref}"[^>]*>)(<f>.*?</f>)(?:<v\s*/>|<v>.*?</v>)?(</c>)')
            xml, n = pat.subn(lambda m: f"{m.group(1)}{m.group(2)}<v>{v!r}</v>{m.group(3)}", xml)
            assert n == 1, (sheet, ref)
        items[name] = xml.encode("utf-8")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for n, b in items.items():
            z.writestr(n, b)


def make_weekly_docx(p, tq, ta, st, wk, ndays):
    doc = new_doc()
    doc.add_heading("영업지원팀 주간보고 (9월 5주차)", level=1)
    doc.add_paragraph("작성자:                    작성일:")
    doc.add_heading("1. 이번 주 요약", level=2)
    top = max(st, key=lambda x: x[2])
    best = max(wk, key=lambda x: x[4])
    for line in [f"9월 마감: 총판매수량 {tq:,}개, 총매출 {ta:,}원, 판매 기록이 있는 날 {ndays}일",
                 f"매출 1위 지점은 {top[0]}으로 {top[2]:,}원",
                 f"주차별 판매금액은 {best[0]}({best[4]:,}원)가 가장 많았고, 5주차는 9/28~9/30 3일치라 {wk[4][4]:,}원으로 적음"]:
        doc.add_paragraph(line, style="List Number")
    doc.add_heading("2. 지점별 매출", level=2)
    rows = [["지점", "판매수량", "판매금액(원)", "매출비중"]]
    for s, q, a in st:
        rows.append([s, f"{q:,}", f"{a:,}", f"{a / ta * 100:.1f}%"])
    rows.append(["합계", f"{tq:,}", f"{ta:,}", "100.0%"])
    add_table(doc, rows)
    doc.add_heading("3. 반품·특이사항", level=2)
    for line in ["9월 반품 23건(152개) 중 포장 파손이 12건(72개)으로 가장 많음",
                 "9/25 추석 당일은 일보 없음(빈 파일)",
                 "9/3 강남점 냉장 진열대 점검으로 오후 2시간 판매 중단 (일보 '메모' 시트)",
                 "일보 통합에서 중복 3행, 판매수량 음수 2행을 뺌 (지점명 표기 18행은 정식 이름으로 고침)"]:
        doc.add_paragraph(line, style="List Bullet")
    doc.add_heading("4. 다음 주 계획", level=2)
    for line in NEXT_PLAN:
        doc.add_paragraph(line, style="List Bullet")
    doc.save(os.path.join(p, "출력", "주간보고_9월5주차.docx"))




def make_pptx(p, tq, ta, st, wk, ndays):
    from pptx import Presentation
    from pptx.chart.data import CategoryChartData
    from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
    from pptx.util import Inches, Pt
    from pptx.oxml.ns import qn
    from pptx.dml.color import RGBColor

    def set_font_tree(el):
        for rpr in el.iter():
            if rpr.tag in (qn("a:rPr"), qn("a:defRPr"), qn("a:endParaRPr")):
                for tag in ("a:latin", "a:ea", "a:cs"):
                    e = rpr.find(qn(tag))
                    if e is None:
                        e = rpr.makeelement(qn(tag), {})
                        rpr.append(e)
                    e.set("typeface", FONT)

    prs = Presentation()
    prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
    title_only = prs.slide_layouts[5]
    # 1장 표지
    s = prs.slides.add_slide(prs.slide_layouts[0])
    s.shapes.title.text = "다온유통 9월 판매 실적"
    s.placeholders[1].text = "영업지원팀"
    # 2장 핵심 숫자
    s = prs.slides.add_slide(title_only)
    s.shapes.title.text = "9월 핵심 숫자"
    top = max(st, key=lambda x: x[2])
    cards = [("총판매수량", f"{tq:,}개"), ("총매출", f"{ta:,}원"), ("판매 기록이 있는 날", f"{ndays}일"),
             ("매출 1위 지점(판매금액 기준)", f"{top[0]} {top[2]:,}원")]
    for i, (k, v) in enumerate(cards):
        box = s.shapes.add_textbox(Inches(0.8 + (i % 2) * 6.1), Inches(1.9 + (i // 2) * 2.4), Inches(5.6), Inches(2.0))
        tf = box.text_frame; tf.word_wrap = True
        tf.text = k; tf.paragraphs[0].runs[0].font.size = Pt(20)
        para = tf.add_paragraph(); r = para.add_run(); r.text = v; r.font.size = Pt(36); r.font.bold = True
    # 3장 지점별 막대
    s = prs.slides.add_slide(title_only)
    s.shapes.title.text = "지점별 판매금액 (원)"
    cd = CategoryChartData(); cd.categories = [x[0] for x in st]; cd.add_series("판매금액(원)", [x[2] for x in st])
    ch = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.6), cd).chart
    ch.has_legend = False
    ch.value_axis.tick_labels.number_format = "#,##0"; ch.value_axis.tick_labels.number_format_is_linked = False
    pl = ch.plots[0]; pl.has_data_labels = True
    pl.data_labels.number_format = "#,##0"; pl.data_labels.number_format_is_linked = False
    ch.font.size = Pt(14)
    # 4장 주차별 추이
    s = prs.slides.add_slide(title_only)
    s.shapes.title.text = "주차별 판매금액 추이 (원)"
    cd = CategoryChartData()
    cd.categories = [f"{n} {a.month}/{a.day}~{b.month}/{b.day}" for n, a, b, _, _ in wk]
    cd.add_series("판매금액(원)", [x[4] for x in wk])
    ch = s.shapes.add_chart(XL_CHART_TYPE.LINE_MARKERS, Inches(0.8), Inches(1.5), Inches(11.7), Inches(5.6), cd).chart
    ch.has_legend = False
    ch.value_axis.tick_labels.number_format = "#,##0"; ch.value_axis.tick_labels.number_format_is_linked = False
    pl = ch.plots[0]; pl.has_data_labels = True
    pl.data_labels.number_format = "#,##0"; pl.data_labels.number_format_is_linked = False
    ch.font.size = Pt(14)
    # 5장 다음 주 할 일
    s = prs.slides.add_slide(prs.slide_layouts[1])
    s.shapes.title.text = "다음 주 할 일"
    tf = s.placeholders[1].text_frame
    tf.text = NEXT_PLAN[0]
    for line in NEXT_PLAN[1:]:
        tf.add_paragraph().text = line
    # 글꼴: 모든 글자(차트 포함)에 맑은 고딕
    for slide in prs.slides:
        for sh in slide.shapes:
            if sh.has_text_frame:
                for para in sh.text_frame.paragraphs:
                    for r in para.runs:
                        r.font.name = FONT
                    para.font.name = FONT
                set_font_tree(sh.text_frame._txBody)
            if getattr(sh, "has_chart", False) and sh.has_chart:
                sh.chart.font.name = FONT
                set_font_tree(sh.chart._chartSpace)
    prs.save(os.path.join(p, "출력", "9월_판매실적.pptx"))


def make_dashboard(p, tq, ta, st, daily, edited=True):
    title = "다온유통 9월 판매 대시보드" if edited else "9월 판매 대시보드"
    bar_color = "#1F3A68"  # 남색 한 가지
    top = max(st, key=lambda x: x[2])
    # 막대 차트
    W, H, L, B, T = 640, 300, 90, 40, 20
    mx = 45_000_000
    bw = (W - L - 20) / 6
    bars = []
    for i, (s, q, a) in enumerate(st):
        h = (H - B - T) * a / mx
        x = L + i * bw + bw * 0.2
        y = H - B - h
        bars.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw * 0.6:.1f}" height="{h:.1f}" fill="{bar_color}"/>'
                    f'<text x="{x + bw * 0.3:.1f}" y="{y - 6:.1f}" text-anchor="middle" class="v">{a:,}</text>'
                    f'<text x="{x + bw * 0.3:.1f}" y="{H - B + 18}" text-anchor="middle">{s}</text>')
    grid = "".join(f'<line x1="{L}" x2="{W - 20}" y1="{H - B - (H - B - T) * v / mx:.1f}" y2="{H - B - (H - B - T) * v / mx:.1f}" class="g"/>'
                   f'<text x="{L - 8}" y="{H - B - (H - B - T) * v / mx + 4:.1f}" text-anchor="end" class="v">{v // 10000:,}만</text>'
                   for v in range(0, mx + 1, 10_000_000))
    bar_svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="지점별 판매금액">{grid}{"".join(bars)}</svg>'
    # 선 차트 (일별 판매수량, 9/25 비움)
    W2, H2, L2 = 900, 300, 50
    lo, hi = 600, 950
    def xy(day, v):
        x = L2 + (day - 1) * (W2 - L2 - 20) / 29
        y = H2 - 40 - (H2 - 60) * (v - lo) / (hi - lo)
        return x, y
    segs, cur = [], []
    for day in range(1, 31):
        d = dt.date(2026, 9, day)
        if d in daily:
            cur.append(xy(day, daily[d]))
        else:
            if cur: segs.append(cur); cur = []
    if cur: segs.append(cur)
    lines = "".join('<polyline fill="none" stroke="#2E7D6B" stroke-width="2" points="'
                    + " ".join(f"{x:.1f},{y:.1f}" for x, y in sg) + '"/>' for sg in segs)
    dots = "".join(f'<circle cx="{xy(d.day, v)[0]:.1f}" cy="{xy(d.day, v)[1]:.1f}" r="3.5" fill="#2E7D6B"><title>{d.month}/{d.day} {v:,}</title></circle>'
                   for d, v in daily.items())
    hx = xy(25, lo)[0]
    holiday = (f'<rect x="{hx - 12:.1f}" y="20" width="24" height="{H2 - 60}" fill="#9993" />'
               f'<text x="{hx:.1f}" y="16" text-anchor="middle" class="v">추석 휴무</text>')
    xt = "".join(f'<text x="{xy(day, lo)[0]:.1f}" y="{H2 - 20}" text-anchor="middle" class="v">9/{day}</text>'
                 for day in (1, 5, 10, 15, 20, 25, 30))
    yt = "".join(f'<line x1="{L2}" x2="{W2 - 20}" y1="{xy(1, v)[1]:.1f}" y2="{xy(1, v)[1]:.1f}" class="g"/>'
                 f'<text x="{L2 - 6}" y="{xy(1, v)[1] + 4:.1f}" text-anchor="end" class="v">{v}</text>' for v in range(600, 951, 50))
    line_svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W2} {H2}" role="img" aria-label="일별 판매수량">{yt}{holiday}{lines}{dots}{xt}</svg>'
    rows = "".join(f"<tr><td>{s}</td><td>{q:,}</td><td>{a:,}</td><td>{a / ta * 100:.1f}%</td></tr>" for s, q, a in st)
    rows += f'<tr class="t"><td>합계</td><td>{tq:,}</td><td>{ta:,}</td><td>100.0%</td></tr>'
    cards = [("총판매수량", f"{tq:,}"), ("총매출", f"{ta:,}원"), ("지점 수", "6"),
             ("판매 기록이 있는 날", f"{len(daily)}일"), ("매출 1위 지점", f"{top[0]}<small>{top[2]:,}원</small>")]
    card_html = "".join(f'<div class="card"><div class="k">{k}</div><div class="n">{v}</div></div>' for k, v in cards)
    html = f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
body {{ font-family: "Malgun Gothic", "맑은 고딕", "Apple SD Gothic Neo", sans-serif; margin: 0; padding: 24px; background: #f5f6f8; color: #222; }}
h1 {{ margin: 0 0 4px; font-size: 26px; }}
.sub {{ color: #666; margin-bottom: 20px; }}
.cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px; margin-bottom: 20px; }}
.card {{ background: #fff; border-radius: 8px; padding: 14px 16px; box-shadow: 0 1px 3px #0002; }}
.card .k {{ color: #666; font-size: 14px; }}
.card .n {{ font-size: 24px; font-weight: bold; margin-top: 6px; }}
.card small {{ display: block; font-size: 14px; font-weight: normal; color: #444; }}
.panel {{ background: #fff; border-radius: 8px; padding: 16px; margin-bottom: 20px; box-shadow: 0 1px 3px #0002; }}
.panel h2 {{ font-size: 18px; margin: 0 0 10px; }}
svg {{ width: 100%; height: auto; font-size: 12px; }}
svg .v {{ font-size: 11px; fill: #555; }}
svg .g {{ stroke: #ddd; }}
table {{ border-collapse: collapse; width: 100%; }}
th, td {{ border-bottom: 1px solid #ddd; padding: 8px; text-align: right; }}
th:first-child, td:first-child {{ text-align: left; }}
tr.t td {{ font-weight: bold; }}
</style>
</head>
<body>
<h1>{title}</h1>
<div class="sub">기준: 출력/9월_판매요약.xlsx (9월 1일~30일, 주요 6개 품목)</div>
<div class="cards">{card_html}</div>
<div class="panel"><h2>지점별 판매금액 (원)</h2>{bar_svg}</div>
<div class="panel"><h2>일별 판매수량 추이 (9/25 추석 휴무, 일보 없음)</h2>{line_svg}</div>
<div class="panel"><h2>지점별 표</h2>
<table><thead><tr><th>지점</th><th>판매수량</th><th>판매금액(원)</th><th>매출비중</th></tr></thead>
<tbody>{rows}</tbody></table></div>
</body>
</html>
"""
    wtxt(os.path.join(p, "출력", "9월_대시보드.html"), html)


COMPARE_MD = """# 9월 결과물 기대값 대조 결과

- 기대값: '출력/기대값.md' (이번 대조에서는 연습으로 '판매 기록이 있는 날'만 30일로 바꿔 대조함. 기대값.md 파일은 고치지 않음)
- 대조한 파일: 9월_판매요약.xlsx, 주간보고_9월5주차.docx, 9월_판매실적.pptx, 9월_대시보드.html (파일은 고치지 않음)
- 표기: ○ 일치 / 숫자는 파일에 있는 값 / 없음은 파일에 해당 항목이 없음

| 항목 (이번 대조의 기대값) | 엑셀 | Word | PowerPoint | 대시보드 |
| --- | --- | --- | --- | --- |
| 총판매수량 22,357 | ○ | ○ | ○ | ○ |
| 총매출 202,883,040원 | ○ | ○ | ○ | ○ |
| 지점 수 6 | ○ (지점별 6행) | ○ (지점별 표 6행) | ○ (막대 6개) | ○ |
| 판매 기록이 있는 날 30일 | 29 ('데이터' 시트의 날짜 수) | 29 | 29 | 29 |
| 매출 1위 강남점 39,353,380원 | ○ | ○ | ○ | ○ |

## 다른 곳과 원인

- '판매 기록이 있는 날'만 다릅니다. 네 파일은 모두 29일입니다.
- '출력/전처리기록.md'에 따르면 9/25(추석 당일) 일보는 데이터 행이 없는 빈 파일이라 통합에 넣지 않았습니다. 그래서 9월 30일 중 판매 기록이 있는 날은 29일입니다.
- 네 파일은 맞고, 이번 대조에 쓴 기대값(30일)이 틀렸습니다. 파일은 고치지 않았습니다.
"""


# ---------------------------------------------------------------- 실행
def run_maker(script, month_dir):
    tmp = tempfile.mkdtemp()
    subprocess.run([PY, os.path.join(TOOLS, script), tmp], check=True)
    return os.path.join(tmp, "원본", month_dir), tmp


def main():
    for n in S:
        shutil.rmtree(os.path.join(MAT, S[n]), ignore_errors=True)
    # 01: 파일 8개 (평평하게)
    make_base_files(proj(1))
    # 02: 원본(8) + 출력/폴더요약.md (1차시 결과)
    shutil.copytree(proj(1), os.path.join(proj(2), "원본"))
    wtxt(os.path.join(proj(2), "출력", "폴더요약.md"), folder_summary("다온유통_영업지원팀 폴더 요약"))
    # 03: 2차시 결과(폴더요약 제목 변경, 반품요약.md) + 9월 일보·영수증(프로젝트 밖)
    shutil.copytree(proj(2), proj(3))
    wtxt(os.path.join(proj(3), "출력", "폴더요약.md"), folder_summary("다온유통 영업지원팀 자료 현황"))
    wtxt(os.path.join(proj(3), "출력", "반품요약.md"), RETURN_SUMMARY)
    src9, tmp9 = run_maker("make_ilbo.py", "9월_일보")
    shutil.copytree(src9, os.path.join(MAT, S[3], "9월_일보"))
    shutil.copytree(os.path.join(tmp9, "원본", "영수증"), os.path.join(MAT, S[3], "영수증"))
    shutil.rmtree(tmp9, ignore_errors=True)
    # 04: 3차시 결과 (원본에 9월 일보·영수증, 출력에 이름 변경·형식 변환·통합·전처리기록)
    shutil.copytree(proj(3), proj(4))
    shutil.copytree(os.path.join(MAT, S[3], "9월_일보"), os.path.join(proj(4), "원본", "9월_일보"))
    shutil.copytree(os.path.join(MAT, S[3], "영수증"), os.path.join(proj(4), "원본", "영수증"))
    clean, info = build_s4_outputs(proj(4))
    print("9월 통합:", info["files"], info["raw_rows"], info["raw_qty"], "→", info["rows"], info["qty"], info["amt"])
    # 05: 4차시 결과 + 10월 일보(프로젝트 밖)
    shutil.copytree(proj(4), proj(5))
    p = proj(5)
    tq, ta, st, wk, days, daily = stats(clean)
    wtxt(os.path.join(p, "출력", "기대값.md"), EXPECT_MD)
    make_summary_xlsx(p, clean)
    make_weekly_docx(p, tq, ta, st, wk, len(days))
    make_pptx(p, tq, ta, st, wk, len(days))
    make_dashboard(p, tq, ta, st, daily)
    wtxt(os.path.join(p, "출력", "대조결과.md"), COMPARE_MD)
    src10, tmp10 = run_maker("make_ilbo_10.py", "10월_일보")
    shutil.copytree(src10, os.path.join(MAT, S[5], "10월_일보"))
    shutil.rmtree(tmp10, ignore_errors=True)
    print("완료")


if __name__ == "__main__":
    main()
