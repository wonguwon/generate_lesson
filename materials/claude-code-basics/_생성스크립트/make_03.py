"""3교시 실습 파일 만들기: py -3.14 -X utf8 make_03.py ..

학습자용/10월_주문내역(최종).csv, 학습자용/3교시_10월주문.zip, 학습자용/실습_요청문.txt,
강사용/정답_3교시.txt
10월 값은 2교시 작성 때 정답_2교시.txt 끝에 미리 적어 둔 값과 같아야 한다.
"""
import csv
import shutil
import sys
import zipfile
from pathlib import Path

import nuri_data as D
from make_02 import check_data, pct, text, write_csv

M = 10


def by_client(rows):
    out = {}
    for r in rows:
        if r[4]:
            out[r[2]] = out.get(r[2], 0) + int(r[6])
    return sorted(out.items(), key=lambda x: -x[1])


def main(out):
    out = Path(out) / "03_CLAUDE.md와_컨텍스트"
    A = check_data()
    a9, a10 = A[9], A[10]
    t7, t8, t9, t10 = (A[m]["total"] for m in (7, 8, 9, 10))
    top = a10["top_clients"][:3]

    # 2교시에 정해 둔 10월 값 그대로
    assert D.ORDER_FILES[M] == "10월_주문내역(최종).csv" and D.DATE_FMT[M] == "%Y/%m/%d"
    assert (a10["raw"], a10["clean"], t10) == (23, 20, 9_384_500)
    assert (a10["exact"], a10["reentry"], a10["blank"]) == (1, 1, 1)
    assert a10["blank_no"] == ["NR-2610-021"]
    assert t10 - t9 == -2_291_000 and pct(t10 - t9, t9) == -19.6
    assert top == [("해든푸드", 1_688_000), ("온기베이커리", 1_438_000), ("한결유업", 1_230_000)]
    assert [pct(a, t10) for _, a in top] == [18.0, 15.3, 13.1]
    assert [a10["staff"][c] for c, _ in top] == ["박준영", "김도현", "최예린"]
    top3_share = pct(sum(a for _, a in top), t10)
    assert top3_share == 46.4
    vals = [a for _, a in a10["top_clients"][:4]]
    assert len(set(vals)) == 4  # 동률 없음
    for _, a in top:  # 반올림 경계 피하기
        x = a / t10 * 1000
        assert abs(x - int(x) - 0.5) > 0.1, a
    # 정리본 누적: 7~10월
    assert sum(A[m]["clean"] for m in (7, 8, 9, 10)) == 78
    assert sum(A[m]["raw"] for m in (7, 8, 9, 10)) == 88
    assert (t7, t8, t9, t10) == (9_915_000, 10_162_500, 11_675_500, 9_384_500)
    assert max(t7, t8, t9, t10) == t9 and min(t7, t8, t9, t10) == t10

    # 처리 기준을 잘못 잡았을 때 (교안 '다르게 나오면')
    raw = D.raw_order_rows(M)
    keep_reentry = {}  # 똑같은 행만 뺌 → 재입력 행 남음
    for r in {tuple(x) for x in raw if x[4]}:
        keep_reentry[(r[0], r[8])] = r
    assert len(keep_reentry) == 21
    assert sum(int(r[6]) for r in keep_reentry.values()) == 10_334_500
    no_dedup = [r for r in raw if r[4]]  # 중복을 하나도 안 뺌
    assert len(no_dedup) == 22 and sum(int(r[6]) for r in no_dedup) == 11_564_500
    assert by_client(no_dedup)[0] == ("한결유업", 2_460_000)
    keep_blank = len(raw) - a10["dup"]  # 수량 빈 행을 남김
    assert keep_blank == 21

    # 실습 1 전후 비교 요청: 9월 거래처별 합계 (2교시 정리본 기준)
    c9 = a9["top_clients"]
    assert len(c9) == 10 and c9[0] == ("고운떡집", 2_134_000) and sum(a for _, a in c9) == t9
    assert c9[-1][1] != c9[-2][1]
    low9 = c9[-1]

    for sub in ("학습자용", "강사용"):
        if (out / sub).exists():
            shutil.rmtree(out / sub)
    learn = out / "학습자용"
    learn.mkdir(parents=True)
    csv_path = learn / D.ORDER_FILES[M]
    write_csv(csv_path, D.ORDER_COLS, raw)
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    assert rows[0] == D.ORDER_COLS and len(rows) - 1 == 23
    assert all(r[1].startswith("2026/10/") for r in rows[1:])

    with zipfile.ZipFile(learn / "3교시_10월주문.zip", "w", zipfile.ZIP_DEFLATED) as z:
        z.write(csv_path, csv_path.name)
    text(learn / "실습_요청문.txt", REQUESTS)

    line = lambda a, t: " / ".join(f"{c}({a['staff'][c]}) {v:,}원 {pct(v, t)}%" for c, v in a["top_clients"][:3])
    key = f"""[3교시 정답] 누리상사 영업관리팀 (강사용, 배포하지 않음)

시작 상태: 2교시 결과물(출력/주문_정리본.csv 58행, 처리기록.md, 출력/월별주문 3개, docx·pptx)

실습 1 CLAUDE.md와 /init
- /init 결과: 폴더 맨 위에 CLAUDE.md (내용은 매번 다름)
- 전후 비교 요청(9월 거래처별 합계): 거래처 {len(c9)}곳, 1위 고운떡집 2,134,000원, 마지막 {low9[0]} {low9[1]:,}원, 합계 {t9:,}원
  규칙 후: 출력 폴더, 파일 이름 2026-09_로 시작, 금액 2,134,000원 형식
- 10월 자료: {D.ORDER_FILES[M]} (날짜 2026/10/dd) {a10['raw']}행. 똑같은 행 NR-2610-013, 재입력 NR-2610-019, 수량 빈칸 NR-2610-021
- \"10월도 똑같이\" 정답
  출력/월별주문/2026-10_주문.csv (원본과 같은 23행, 이름만 바뀜) → 출력/월별주문 4개
  출력/주문_정리본.csv 78행 (7월 18 · 8월 19 · 9월 21 · 10월 20)
  처리기록.md 10월: 합치기 전 23행, 중복 2행, 수량 빈칸 1행 뺌
  Docs 10월 보고서: 20건, {t10:,}원, 9월 대비 {t10 - t9:+,}원 ({pct(t10 - t9, t9):+}%)
    월별: 7월 18건 {t7:,} / 8월 19건 {t8:,} / 9월 21건 {t9:,} / 10월 20건 {t10:,}
    상위 3곳: {line(a10, t10)}  (3곳 합 {top3_share}%)
    확인 필요: NR-2610-021
  Slides 5장: 숫자는 Docs와 같음. 3장 막대 4개, 9월이 가장 큼
- 다르게 나오면: 정리본 79행·10월 21행·10월 합계 10,334,500 = 재입력 행 남김
  / 10월 21행·합계 9,384,500 = 수량 빈 행 남김 / 10월 22행·합계 11,564,500·1위 한결유업 2,460,000 = 중복을 안 뺌

실습 2 /context: Memory files에 CLAUDE.md, /clear 뒤 Messages가 줄고 Memory files는 남음, 규칙 답은 같음
실습 3 /rewind: 금액 줄이 '천 원 단위로 반올림'으로 바뀐 뒤, Restore code로 '금액은 원 단위, 천 단위 쉼표 (예: 1,234,500원). %는 소수 첫째 자리.'로 돌아옴
"""
    text(out / "강사용" / "정답_3교시.txt", key)
    print(key)


REQUESTS = open(Path(__file__).with_name("requests_03.txt"), encoding="utf-8").read()

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "..")
