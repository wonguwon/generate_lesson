"""만든 파일을 다시 읽어 데이터 모듈 없이 교안 숫자를 재계산한다. usage: python -X utf8 점검.py <gemini-web-basics 폴더>"""
import re
import sys
from pathlib import Path

from docx import Document
from openpyxl import load_workbook

R = Path(sys.argv[1])
D3 = R / "03_연결된_앱으로_문서_시트_만들기" / "학습자용" / "Drive에_올릴_파일"
L4 = R / "04_스킬로_반복_지시_남기기" / "학습자용"
L5 = R / "05_Task로_메일_처리하고_예약하기" / "학습자용"


def rows(p):
    ws = load_workbook(p).active
    return list(ws.iter_rows(values_only=True))


s, m = rows(D3 / "영업팀_10월_지출.xlsx"), rows(D3 / "마케팅팀_10월_지출.xlsx")
assert s[0][4] == "금액(원)" and m[0][4] == "금액(천원)" and (len(s), len(m)) == (10, 8)
oct_ = lambda r: r[0].year == 2026 and r[0].month == 10
seen, sal = set(), {}
for r in filter(oct_, s[1:]):
    if r[1] not in seen:
        seen.add(r[1])
        sal[r[2]] = sal.get(r[2], 0) + r[4]
mk = {}
for r in filter(oct_, m[1:]):
    mk[r[2]] = mk.get(r[2], 0) + r[4] * 1000
assert sal == {"출장비": 145800, "접대비": 426000, "소모품": 85500}
assert mk == {"광고비": 750000, "행사비": 552000, "소모품": 113000}
assert sum(sal.values()) + sum(mk.values()) == 2072300

doc = Document(D3 / "부서별_10월_예산.docx")
txt = [p.text for p in doc.paragraphs]
assert "단위: 만원" in txt
b = re.findall(r"10월 예산 (\d+), 9월 지출 (\d+)", "\n".join(txt))
assert len(b) == 6 and sum(int(x) for x, _ in b) == 235 and sum(int(y) for _, y in b) == 182

sep = (L4 / "9월_지출_자료.txt").read_bytes()
assert sep.startswith(b"\xef\xbb\xbf")
amt = [int(l.rsplit("|", 1)[1]) for l in sep.decode("utf-8-sig").splitlines()[2:]]
assert len(amt) == 12 and sum(amt) == 1820000

mail = (L5 / "실습메일_8통.txt").read_text(encoding="utf-8-sig")
assert len(re.findall(r"^제목: \[주간 업무\]", mail, re.M)) == 8

for f in sorted(R.glob("0*/*/**/*")):
    if f.is_file():
        print(f.relative_to(R), f.stat().st_size)
print("모두 일치")
