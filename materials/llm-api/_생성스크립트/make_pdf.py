"""10차시(10_langchain-rag)에서 쓰는 data/handbook.pdf를 만든다.

원문은 10차시 교안(실습 1) 토글 "실습 자료: handbook.pdf 쪽별 원문"을 그대로 옮긴 것이다.
- A4, 한 쪽에 한 주제, 맨 위 제목 한 줄(굵게) + 본문 문단, 쪽 아래 가운데 "- N -"
- 1쪽 표지에 "실습용 가상 자료" 문구가 들어 있음
필요: reportlab, pypdf, langchain-text-splitters, langchain-core / 글꼴 C:/Windows/Fonts/malgun.ttf, malgunbd.ttf

실행: llm-api 폴더에서 py -X utf8 _생성스크립트/make_pdf.py
"""
import re
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "handbook.pdf"

SOURCE = """\
[1쪽]
OO대학교 2027학년도 학사 안내 핸드북
이 핸드북은 실습용 가상 자료이며 실제 학교 규정과 관계없습니다.
학사 일정과 규정에 관한 문의는 학사지원팀으로 합니다.

[2쪽]
수강 신청
2027학년도 1학기 수강 신청은 학사관리시스템에서 학년별로 진행한다. 4학년은 2월 15일(월), 3학년은 2월 16일(화), 2학년은 2월 17일(수), 1학년은 2월 18일(목)에 신청하고, 2월 19일(금)은 전체 학년이 신청할 수 있다.
한 학기에는 12학점 이상 18학점 이하로 신청한다. 직전 학기 평점평균이 4.0 이상이면 21학점까지 신청할 수 있다.
신청 전에 학사관리시스템의 강의 시간표에서 개설 과목과 수업 시간을 확인한다. 수업 시간이 겹치는 과목은 함께 신청할 수 없다. 학년별 신청일에는 그 학년 학생만 신청할 수 있으므로, 다른 학년 과목은 전체 학년 신청일에 신청한다.

[3쪽]
수강 정정·철회
개강일인 2027년 3월 2일(화)부터 3월 8일(월)까지는 수강 정정 기간으로, 과목을 추가하거나 바꿀 수 있다.
수강 철회는 3월 29일(월)부터 4월 2일(금)까지 한 학기에 2과목까지 할 수 있으며, 철회한 뒤에도 12학점 이상이 남아 있어야 한다. 철회한 과목은 성적표에 W로 표시되고 평점평균에는 들어가지 않는다.
정정과 철회는 모두 학사관리시스템에서 신청한다. 기간이 지난 뒤에는 과목을 추가하거나 철회할 수 없다.

[4쪽]
휴학
일반휴학은 한 번에 1학기 또는 2학기씩 신청할 수 있고, 재학 중 통산 6학기까지 할 수 있다. 신청은 학기 시작 전부터 개강 후 4주 이내까지 학사관리시스템에서 한다.
신입생은 첫 학기에 일반휴학을 할 수 없으며, 군휴학 기간은 통산 6학기에 포함되지 않는다.
휴학을 신청할 때는 휴학 사유와 기간을 입력한다. 군휴학은 입영 통지서를 첨부해 신청한다. 휴학 중에는 수강 신청을 할 수 없다.

[5쪽]
복학
휴학 기간이 끝나면 복학 신청 기간에 학사관리시스템에서 복학을 신청한다. 2027학년도 1학기 복학 신청 기간은 2027년 1월 4일(월)부터 1월 8일(금)까지다.
휴학 기간이 끝났는데 복학이나 휴학 연장을 신청하지 않으면 제적 대상이 된다. 군휴학자는 전역일이 개강 후 4주 이내이면 그 학기에 복학할 수 있다.
복학을 신청한 학생은 같은 학기 수강 신청 기간에 수강 신청을 한다. 군휴학자는 전역증 사본을 첨부해 복학을 신청한다.

[6쪽]
성적장학금
성적장학금은 직전 학기에 15학점 이상을 이수하고 평점평균 3.80 이상인 학생 가운데 학과별 성적 상위 10% 이내에서 선발하며, 수업료의 50%를 감면한다. 평점평균 4.20 이상으로 학과 1등인 학생은 수업료 전액을 감면한다.
직전 학기에 F 과목이 있으면 선발에서 제외되며, 별도 신청 없이 자동으로 선발한다.
선발 결과는 학기 시작 전에 학사관리시스템의 장학 메뉴에서 확인한다. 다른 교내 장학금과 함께 받을 때는 수업료를 넘지 않는 범위에서 감면한다.

[7쪽]
교내 근로장학
교내 근로장학생은 직전 학기에 12학점 이상을 이수하고 평점평균 2.50 이상인 재학생이 신청할 수 있다. 신청은 개강 2주 전까지 학생지원팀 홈페이지에서 한다.
학기 중 근무는 주 15시간을 넘을 수 없다. 근로장학금은 근무한 시간만큼 다음 달 10일에 지급한다.
근무 부서는 신청한 학생의 시간표를 보고 학생지원팀이 배정한다. 근무 시간은 매달 말 근무 부서 담당자의 확인을 받아 학생지원팀에 낸다.

[8쪽]
졸업 요건
졸업하려면 총 130학점 이상을 이수하고, 그중 전공 60학점 이상과 교양 30학점 이상을 채워야 한다. 전체 평점평균은 2.00 이상이어야 한다.
졸업 영어 인증(TOEIC 700점 이상 또는 교내 영어 인증 시험 합격)을 통과해야 한다. 영어 인증 결과는 학사관리시스템에 등록되어야 인정된다.
요건을 모두 채운 학생은 졸업 학기에 학사관리시스템에서 졸업 사정 결과를 확인한다.

[9쪽]
재수강
성적이 C+ 이하인 과목만 재수강할 수 있다. 재수강한 과목의 성적은 A0까지만 받을 수 있고, 이전 성적은 성적표에서 지워진다.
같은 과목은 두 번까지 재수강할 수 있으며, 재학 중 재수강할 수 있는 학점은 모두 24학점까지다.
재수강은 정규 학기 수강 신청 기간에 일반 과목과 같은 방법으로 신청한다. 폐지된 과목은 학과가 정한 대체 과목으로 재수강할 수 있다.

[10쪽]
계절학기
여름·겨울 계절학기에는 학기마다 6학점까지 수강할 수 있고, 이수한 학점은 졸업 학점에 포함된다.
신청은 정규 학기 종강 2주 전부터 학사관리시스템에서 하며, 수강료는 학점당 8만 원이다. 수강 인원이 10명 미만인 과목은 폐강된다.
폐강된 과목의 수강료는 모두 돌려준다. 계절학기 성적은 정규 학기와 같은 방식으로 매긴다.

[11쪽]
성적 이의신청
성적은 학기 종강 다음 주에 학사관리시스템에 공개된다.
성적에 이의가 있으면 성적 공개 후 3일 이내에 학사관리시스템에서 담당 교수에게 이의신청을 하며, 결과는 성적 확정일 전까지 알려 준다. 성적 확정 뒤에는 성적을 바꿀 수 없다.
이 핸드북에 없는 학사 문의는 학사지원팀으로 한다.
"""

# 교안 정답표가 기대는 사실: (쪽, 들어 있어야 할 글)
FACTS = [
    (1, "실습용 가상 자료"),
    (2, "1학년은 2월 18일(목)"),                       # 실습 4 ② 1턴
    (2, "직전 학기 평점평균이 4.0 이상이면 21학점까지"),   # 실습 3 ① 평점 4.2 질문
    (4, "재학 중 통산 6학기까지"),                      # 실습 2 ②③ 휴학 질문
    (6, "평점평균 3.80 이상"),                          # 실습 4 ② 2턴
    (10, "학점당 8만 원"),                              # 실습 2 ② 여름방학 질문
]
TITLES = ["OO대학교 2027학년도 학사 안내 핸드북", "수강 신청", "수강 정정·철회", "휴학", "복학",
          "성적장학금", "교내 근로장학", "졸업 요건", "재수강", "계절학기", "성적 이의신청"]


def parse(source):
    pages = []
    for block in source.strip().split("\n\n"):
        lines = block.splitlines()
        assert re.fullmatch(r"\[\d+쪽\]", lines[0]), lines[0]
        assert int(lines[0][1:-2]) == len(pages) + 1
        pages.append((lines[1], lines[2:]))
    return pages


PAGES = parse(SOURCE)

title_style = ParagraphStyle("t", fontName="MalgunBd", fontSize=16, leading=24, spaceAfter=12)
body_style = ParagraphStyle("b", fontName="Malgun", fontSize=12, leading=20, spaceAfter=10)


def footer(canvas, doc):
    canvas.setFont("Malgun", 9)
    canvas.drawCentredString(A4[0] / 2, 20, f"- {doc.page} -")


def build(path):
    pdfmetrics.registerFont(TTFont("Malgun", "C:/Windows/Fonts/malgun.ttf"))
    pdfmetrics.registerFont(TTFont("MalgunBd", "C:/Windows/Fonts/malgunbd.ttf"))
    story = []
    for i, (title, paras) in enumerate(PAGES):
        story.append(Paragraph(title, title_style))
        for p in paras:
            story.append(Paragraph(p, body_style))
        if i < len(PAGES) - 1:
            story.append(PageBreak())
    doc = SimpleDocTemplate(str(path), pagesize=A4, title="OO대학교 학사 안내 핸드북 (실습용 가상 자료)")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def check(path):
    """교안 실습 1·2 코드와 같은 방법으로 읽어 정답표 숫자를 확인한다."""
    from langchain_core.documents import Document
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    pages = [Document(page_content=p.extract_text(), metadata={"source": "data/handbook.pdf", "page": n})
             for n, p in enumerate(reader.pages, start=1)]
    assert len(pages) == 11, len(pages)
    assert pages[1].metadata == {"source": "data/handbook.pdf", "page": 2}
    flat = {d.metadata["page"]: re.sub(r"\s+", "", d.page_content) for d in pages}
    for page, fact in FACTS:
        assert re.sub(r"\s+", "", fact) in flat[page], (page, fact)
    for d in pages:
        assert "기숙사" not in d.page_content  # 문서에 없는 질문이어야 함
        title = [line for line in d.page_content.splitlines() if not line.strip().startswith("-")][0]
        assert title == TITLES[d.metadata["page"] - 1], (d.metadata["page"], title)
        assert len(d.page_content) < 500, (d.metadata["page"], len(d.page_content))
    counts = {}
    for size in [500, 200]:
        chunks = RecursiveCharacterTextSplitter(chunk_size=size, chunk_overlap=50).split_documents(pages)
        counts[size] = len(chunks)
        if size == 200:
            # 교안 실습 1 ③ 정답: chunks[1:3] 두 조각 모두 2쪽, 앞 조각 끝부분이 다음 조각 앞에 겹침
            a, b = chunks[1], chunks[2]
            assert a.metadata["page"] == b.metadata["page"] == 2, (a.metadata, b.metadata)
            assert b.page_content.split("\n")[0] in a.page_content, "2쪽 조각 겹침 없음"
    assert counts[500] == 11, counts
    print("쪽 수 11, 2쪽 metadata OK, 쪽 제목 OK, 쪽마다 글자 수:", [len(d.page_content) for d in pages])
    print("조각 수:", counts, "(교안: 500 → 11, 200 → 19)")


if __name__ == "__main__":
    assert len(PAGES) == 11 and [t for t, _ in PAGES] == TITLES
    OUT.parent.mkdir(parents=True, exist_ok=True)
    build(OUT)
    check(OUT)
    print("저장:", OUT)
