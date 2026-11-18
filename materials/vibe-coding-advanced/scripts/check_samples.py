"""만든 샘플 엑셀을 다시 읽어 교안 조건과 정답 합계표를 따로 계산해 대조한다."""
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

from openpyxl import load_workbook

S = Path(__file__).resolve().parent.parent / "samples"
EPOCH = date(1899, 12, 30)
fails = []


def check(cond, msg):
    print(("OK  " if cond else "FAIL"), msg)
    if not cond:
        fails.append(msg)


def norm(row):
    row = row[1:]  # 맨 앞 주문번호는 따로 검사
    d, p, prod, q, price, amt, who = row
    if isinstance(d, datetime):
        d = d.date()
    elif isinstance(d, (int, float)):
        d = EPOCH + timedelta(int(d))
    if isinstance(amt, str):
        amt = int(amt.replace(",", ""))
    return d, p.replace(" ", ""), prod, q, price, amt, who


def read(name):
    ws = load_workbook(S / name).active
    return [r for r in ws.iter_rows(min_row=2, values_only=True)], ws


# ---------- 상반기 ----------
raw1, ws1 = read("소담상점_2024_상반기.xlsx")
toggle1 = """240102-001	2024-01-02	스마트스토어	대나무 칫솔 4개입	2	6900	13800	김하늘
240102-002	2024-01-02	쿠팡	면 행주 5매	1	8900	8900	박서준
240103-001	2024-01-03	자사몰	유리 밀폐용기 3종	1	24000	24000	이수아
240103-002	2024-01-03	쿠팡	천연 수세미 3개입	3	4500	13500	최민재
240104-001	2024-01-04	스마트스토어	리필 주방세제 1L	2	7800	15600	정유나
240105-001	2024-01-05	자사몰	원목 도마	1	19000	19000	한도윤""".splitlines()
first6 = ["\t".join([r[0], r[1].strftime("%Y-%m-%d")] + [str(x) for x in r[2:]]) for r in raw1[:6]]
check(first6 == toggle1, "상반기 첫 6행 = 2-2 토글")
check([c.value for c in ws1[1]] == ["주문번호", "날짜", "플랫폼", "상품", "수량", "단가", "금액", "주문자"], "상반기 칸 제목")
check(all(r[1] is not None for r in raw1), "상반기 빈 행 없음")
check(all(isinstance(r[1], datetime) and isinstance(r[6], int) for r in raw1), "상반기 날짜는 날짜 칸, 금액은 숫자")
check(all(ws1.cell(i, 2).number_format == "yyyy-mm-dd" for i in range(2, ws1.max_row + 1)), "상반기 날짜 서식 yyyy-mm-dd")
c1 = [norm(r) for r in raw1]
check([r[0] for r in c1] == sorted(r[0] for r in c1), "상반기 날짜순")
check(all(r[3] * r[4] == r[5] for r in c1), "상반기 금액 = 수량×단가")
check(sum(1 for r in c1 if r[0] in (date(2024, 1, 2), date(2024, 1, 3))) == 4, "1월 2·3일 행은 첫 4행뿐")
check(all(date(2024, 1, 1) <= r[0] <= date(2024, 6, 30) for r in c1), "상반기 기간 안")
check(all(any(r[0] == d for r in c1) for d in (date(2024, 3, 1), date(2024, 3, 31), date(2024, 6, 30))), "경계 날짜 03-01·03-31·06-30")
check(set(r[1] for r in c1) == {"스마트스토어", "쿠팡", "자사몰"} and all(r[1] == raw[2] for r, raw in zip(c1, raw1)), "상반기 플랫폼 3개, 표기 흔들림 없음")
check(sum(r[5] for r in c1[:6]) == 94800, "첫 6행 합계 94,800")

# ---------- 하반기 ----------
raw2, ws2 = read("소담상점_2024_하반기.xlsx")
check(raw2[2] == (None,) * 8, "하반기 3번째 행은 빈 행")
f = [r[1:] for r in raw2[:5]]
check(f[0][0].date() == date(2024, 7, 1) and f[0][1] == "스마트스토어" and f[0][5] == 6900 and f[0][6] == "윤지호", "하반기 1행")
check(f[1][0] == 45474 and f[1][1] == "쿠팡 " and f[1][5] == "17,800" and f[1][6] == "서예린", "하반기 2행 (일련번호·쿠팡 빈칸·글자 금액)")
check(f[3][0].date() == date(2024, 7, 2) and f[3][1] == "스마트 스토어" and f[3][5] == "19,000" and f[3][6] == "강민서", "하반기 4행")
check(f[4][0] == 45475 and f[4][1] == "자사몰" and f[4][5] == 24000 and f[4][6] == "오태윤", "하반기 5행")
check(ws2.cell(3, 2).number_format == "General" and ws2.cell(3, 7).data_type == "s", "45474 칸은 일반 서식 숫자, 17,800 칸은 글자")
data2 = [r for r in raw2 if any(v is not None for v in r)]
blank2 = len(raw2) - len(data2)
c2 = [norm(r) for r in data2]
check([r[0] for r in c2] == sorted(r[0] for r in c2), "하반기 날짜순")
check(all(r[3] * r[4] == r[5] for r in c2), "하반기 금액 = 수량×단가")
check(sum(1 for r in c2 if r[0] in (date(2024, 7, 1), date(2024, 7, 2))) == 4, "7월 1·2일 행은 고정 4행뿐")
check(set(r[1] for r in c2) == {"스마트스토어", "쿠팡", "자사몰"}, "하반기 정리하면 플랫폼 3개")
check(all(any(r[0] == d for r in c2) for d in (date(2024, 9, 30), date(2024, 12, 31))), "경계 날짜 09-30·12-31")
kinds = Counter()
for r in data2:
    kinds["일련번호"] += isinstance(r[1], int)
    kinds["글자 금액"] += isinstance(r[6], str)
    kinds["스마트 스토어"] += r[2] == "스마트 스토어"
    kinds["쿠팡 "] += r[2] == "쿠팡 "
print("    하반기 지저분한 값:", dict(kinds), "빈 행", blank2)
check(all(v > 1 for v in kinds.values()) and blank2 > 1, "지저분한 값 종류마다 여러 건")


check(len(c1) + len(c2) > 1000, f"상반기+하반기 {len(c1)+len(c2)}행 > 1000 (행 한도 확인용)")

# ---------- 주문번호 ----------
import re
o1 = [r[0] for r in raw1]; o2 = [r[0] for r in data2]
check(all(re.fullmatch(r"\d{6}-\d{3}", o) for o in o1 + o2), "주문번호 형식 YYMMDD-NNN")
check(len(set(o1 + o2)) == len(o1) + len(o2), "주문번호는 두 파일 합쳐도 겹치지 않음")
check(all(o[:6] == r[0].strftime("%y%m%d") for o, r in zip(o1 + o2, c1 + c2)), "주문번호 앞 6자리 = 날짜")
check([r[0] for r in raw2[:5]] == ["240701-001", "240701-002", None, "240702-001", "240702-002"], "하반기 첫 5행 주문번호")


# ---------- 정답 합계표 대조 ----------
def agg(rows):
    m, p, pr, d = Counter(), Counter(), Counter(), Counter()
    mc = 0
    for dt, pl, prod, q, price, amt, _ in rows:
        m[dt.month] += amt; p[pl] += amt; pr[prod] += amt; d[dt] += amt
        mc += amt if dt.month == 3 and pl == "쿠팡" else 0
    return m, p, pr, d, mc


m1, p1, pr1, d1, mc1 = agg(c1)
m2, p2, pr2, d2, mc2 = agg(c2)
check((d1[date(2024, 1, 2)], d1[date(2024, 1, 3)], d2[date(2024, 7, 1)], d2[date(2024, 7, 2)]) == (22700, 37500, 24700, 43000), "일별 22,700·37,500·24,700·43,000")
for name, cnt in [("상반기 플랫폼", p1), ("하반기 플랫폼", p2), ("월별", m1 + m2), ("상반기 상품", pr1), ("하반기 상품", pr2), ("전체 상품", pr1 + pr2)]:
    check(len(set(cnt.values())) == len(cnt), f"{name} 동률 없음")

ans = {}
for r in load_workbook(S / "소담상점_2024_정답합계표.xlsx").active.iter_rows(values_only=True):
    if r[0]:
        ans[r[0]] = r[1:]
    elif r[1]:
        ans[r[1]] = r[2:]
check(ans["행 수 (빈 행 제외)"] == (len(c1), len(c2)), "표: 행 수")
check(ans["합계"] == (sum(r[5] for r in c1), sum(r[5] for r in c2)), "표: 합계")
check(ans["3월 합계"][0] == m1[3] and ans["3월 · 쿠팡 합계"][0] == mc1, "표: 3월·3월쿠팡")
check(all(ans[f"플랫폼별 - {p}"] == (p1[p], p2[p]) for p in p1), "표: 플랫폼별")
check(all(ans[f"{i}월"][0] == (m1 if i <= 6 else m2)[i] for i in range(1, 13)), "표: 월별")
check(all(ans[k] == (pr1[k], pr2[k]) for k in pr1), "표: 상품별")
check(ans["참고"] == ("하반기 파일의 빈 행 수", blank2), "표: 빈 행 수")
print("\n실패", len(fails), "건" if fails else "건 - 모두 통과")
