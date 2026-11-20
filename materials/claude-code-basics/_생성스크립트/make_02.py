"""2교시 실습 파일 만들기: py -3.14 -X utf8 make_02.py ..

학습자용/월별주문 (7·8·9월 주문 CSV 3개 + 빈 양식 1개), 학습자용/2교시_월별주문.zip,
학습자용/실습_요청문.txt, 강사용/정답_2교시.txt
3교시(10월)·4교시(11월) 값도 강사용 정답에 미리 적어 둔다(파일은 해당 교시 스크립트가 만듦).
"""
import csv
import datetime as dt
import io
import shutil
import sys
import zipfile
from pathlib import Path

import nuri_data as D

HOL = {"2026-07-17", "2026-08-14", "2026-08-15", "2026-08-17", "2026-09-24", "2026-09-25", "2026-09-26",
       "2026-10-03", "2026-10-05", "2026-10-09"}


def write_csv(path, header, rows):
    buf = io.StringIO(newline="")
    w = csv.writer(buf, lineterminator="\r\n")
    w.writerow(header)
    w.writerows(rows)
    path.write_bytes(buf.getvalue().encode("utf-8-sig"))


def text(path, s):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(s.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-8-sig"))


def pct(a, b):
    return round(a / b * 100, 1)


def check_data():
    """날짜·동률·반올림 경계를 확인하고 2교시 정답을 돌려준다."""
    for m in (7, 8, 9, 10, 11):
        nos = [r[0] for r in D.ORDERS[m]] + [b[0] for b in D.MESS[m]["blank"]]
        assert len(nos) == len(set(nos)), m
        for r in D.ORDERS[m]:
            assert r[5] == D.PRICE[r[3]] or (m == 11 and r[2] == "윤슬찬푸드"), r
            assert r[6] == {c[1]: c[4] for c in D.CLIENTS}[r[2]], r
        for d in [r[1] for r in D.ORDERS[m]] + [b[1] for b in D.MESS[m]["blank"]]:
            x = dt.date.fromisoformat(d)
            assert x.month == m and x.weekday() < 5 and d not in HOL, d
    # 1교시 윤슬찬푸드 거래내역(7~10월)과 같은 주문
    yun = {(r[1], r[3], r[4]) for m in (7, 8, 9, 10) for r in D.ORDERS[m] if r[2] == "윤슬찬푸드"}
    assert yun == {(d, i, n) for d, i, n in D.TRADES if "2026-07" <= d < "2026-11"}, yun

    A = {m: D.order_answers(m) for m in (7, 8, 9, 10, 11)}
    t7, t8, t9 = (A[m]["total"] for m in (7, 8, 9))
    top = A[9]["top_clients"]
    v = [a for _, a in top[:4]]
    assert len(set(v)) == 4 and len(set(a for _, a in A[9]["top_products"][:4])) == 4
    for _, a in top[:3]:  # 반올림 경계(xx.x5) 피하기
        x = a / t9 * 1000
        assert abs(x - int(x) - 0.5) > 0.1, a
    return A


def main(out):
    out = Path(out) / "02_계획모드와_Docs_Slides"
    A = check_data()
    a7, a8, a9 = A[7], A[8], A[9]
    t7, t8, t9 = a7["total"], a8["total"], a9["total"]
    top = a9["top_clients"][:3]
    # 교안 정답 표와 맞는지 확인
    assert (a7["raw"], a8["raw"], a9["raw"]) == (20, 21, 24)
    assert (a7["clean"], a8["clean"], a9["clean"]) == (18, 19, 21)
    assert (t7, t8, t9) == (9_915_000, 10_162_500, 11_675_500)
    assert t7 + t8 + t9 == 31_753_000
    assert sum(A[m]["dup"] for m in (7, 8, 9)) == 4 and sum(A[m]["blank"] for m in (7, 8, 9)) == 3
    assert t9 - t8 == 1_513_000 and pct(t9 - t8, t8) == 14.9
    assert top == [("고운떡집", 2_134_000), ("온기베이커리", 2_009_500), ("맑은샘음료", 1_848_000)]
    assert [pct(a, t9) for _, a in top] == [18.3, 17.2, 15.8]
    assert pct(sum(a for _, a in top), t9) == 51.3
    assert [a9["staff"][c] for c, _ in top] == ["이수아", "김도현", "박준영"]
    assert max(t7, t8, t9) == t9
    # 처리 기준을 잘못 잡았을 때 나오는 숫자 (교안 '다르게 나오면')
    raw_all = [r for m in (7, 8, 9) for r in D.raw_order_rows(m)]
    exact_only = len({tuple(r) for r in raw_all if r[4]})  # 똑같은 행만 뺌 + 수량 빈 행 뺌
    assert exact_only == 60
    assert len(raw_all) - sum(A[m]["dup"] for m in (7, 8, 9)) == 61  # 수량 빈 행을 남김
    any_blank = len([r for r in raw_all if all(r)])  # 빈칸이 하나라도 있으면 뺌(비고 포함)
    keep_any = {}
    for r in raw_all:
        if r[4]:
            keep_any.setdefault(r[0], r)
    any_blank_min = len([r for r in keep_any.values() if all(r)])  # 주문번호 중복을 뺀 뒤 비고가 빈 행까지 뺌
    assert (any_blank_min, any_blank) == (9, 11)
    keep = {}
    for r in raw_all:
        if r[4]:
            keep.setdefault(r[0], r)
    assert len(keep) == 58
    # 9월에 재입력 행을 남기면 1위가 바뀜
    sep = [r for r in D.raw_order_rows(9) if r[4]]
    sep_exact = {}
    for r in {tuple(x) for x in sep}:
        sep_exact[r[2]] = sep_exact.get(r[2], 0) + int(r[6])
    wrong_top = max(sep_exact.items(), key=lambda x: x[1])
    assert wrong_top == ("푸름샐러드", 2_255_000), wrong_top
    sep_all = {}
    for r in sep:
        sep_all[r[2]] = sep_all.get(r[2], 0) + int(r[6])
    wrong_top2 = max(sep_all.items(), key=lambda x: x[1])
    assert wrong_top2 == ("온기베이커리", 3_029_500), wrong_top2

    for sub in ("학습자용", "강사용"):
        if (out / sub).exists():
            shutil.rmtree(out / sub)
    folder = out / "학습자용" / D.ORDER_DIR
    folder.mkdir(parents=True)
    for m in (7, 8, 9):
        write_csv(folder / D.ORDER_FILES[m], D.ORDER_COLS, D.raw_order_rows(m))
    write_csv(folder / D.TEMPLATE_FILE, D.ORDER_COLS, [])

    # 만든 파일을 다시 읽어 확인
    for m in (7, 8, 9):
        with open(folder / D.ORDER_FILES[m], encoding="utf-8-sig", newline="") as f:
            rows = list(csv.reader(f))
        assert rows[0] == D.ORDER_COLS and len(rows) - 1 == A[m]["raw"]
    assert len(list(folder.iterdir())) == 4

    zpath = out / "학습자용" / "2교시_월별주문.zip"
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(folder.rglob("*")):
            z.write(p, p.relative_to(folder.parent).as_posix())
    text(out / "학습자용" / "실습_요청문.txt", REQUESTS)

    def topline(a, n=3):
        t = a["total"]
        return " / ".join(f"{c}({a['staff'][c]}) {v:,}원 {pct(v, t)}%" for c, v in a["top_clients"][:n])

    a10, a11 = A[10], A[11]
    key = f"""[2교시 정답] 누리상사 영업관리팀 (강사용, 배포하지 않음)

실습 자료: 원본/월별주문 = {D.ORDER_FILES[7]}({a7['raw']}행), {D.ORDER_FILES[8]}({a8['raw']}행, 날짜 2026.08.dd),
  {D.ORDER_FILES[9]}({a9['raw']}행), {D.TEMPLATE_FILE}(머리글만). 합치기 전 {a7['raw'] + a8['raw'] + a9['raw']}행
섞인 것: 똑같은 행 2 (NR-2607-011, NR-2609-006), 비고만 '재입력'인 같은 주문번호 2 (NR-2608-015, NR-2609-018),
  수량·금액 빈 행 3 ({', '.join(b for m in (7, 8, 9) for b in A[m]['blank_no'])}). 비고는 대부분 빈칸(지우면 안 됨)

실습 1 계획 모드
- 이름 변경 3개: {D.ORDER_FILES[7]} → 2026-07_주문.csv / {D.ORDER_FILES[8]} → 2026-08_주문.csv / {D.ORDER_FILES[9]} → 2026-09_주문.csv
  ({D.TEMPLATE_FILE}은 제외). 출력/월별주문에 복사본, 원본/월별주문은 4개 그대로
- 출력/주문_정리본.csv: 58행 (7월 18, 8월 19, 9월 21) / 처리기록: 중복 4행, 수량 빈칸 3행 뺌
- 다르게 나오면: 60행 = 재입력 2행 남김 / 61행 = 수량 빈 행 남김 / {any_blank_min}~{any_blank}행 = 비고가 빈 행까지 지움

실습 2 Claude Docs 보고서 (9월)
- 9월 21건, 판매 합계 {t9:,}원, 8월 대비 +{t9 - t8:,}원 (+{pct(t9 - t8, t8)}%)
- 월별: 7월 18건 {t7:,} / 8월 19건 {t8:,} / 9월 21건 {t9:,}
- 9월 상위 3곳: {topline(a9)}  (3곳 합 {pct(sum(v for _, v in top), t9)}%)
- 확인 필요 주문: {', '.join(b for m in (7, 8, 9) for b in A[m]['blank_no'])}
- 틀린 1위: 푸름샐러드 2,255,000 = 재입력 행 남김 / 온기베이커리 3,029,500 = 중복을 하나도 안 뺌
- 문장 검토: 정답 문장은 없음. 원인 추측·전망·부풀린 표현·없는 사실·요약과 표의 숫자 엇갈림을 찾아 지우거나 숫자로 바꾸면 맞음

실습 3 Claude Slides: 개요 5장 확정 → /slides. 숫자는 실습 2와 같음. 3번 장 막대그래프(9월이 가장 큼), 4번 장 3곳 합 비중

[3교시용 10월] {D.ORDER_FILES[10]} (날짜 2026/10/dd) {a10['raw']}행 → 정리 {a10['clean']}행, 합계 {a10['total']:,}원,
  중복 {a10['dup']}(NR-2610-013 똑같은 행, NR-2610-019 재입력), 수량 빈칸 {a10['blank']} ({', '.join(a10['blank_no'])}),
  9월 대비 {a10['total'] - t9:+,}원 ({pct(a10['total'] - t9, t9):+}%), 상위 3곳 {topline(a10)}
[4교시용 11월] {D.ORDER_FILES[11]} 열 이름 주문일→일자, 거래처→거래처명, 수량→주문수량. {a11['raw']}행 → 정리 {a11['clean']}행,
  합계 {a11['total']:,}원, 중복 {a11['dup']}(NR-2611-012), 수량 빈칸 {a11['blank']} ({', '.join(a11['blank_no'])}),
  윤슬찬푸드 11/2 주문은 수정 견적 단가(박스 800원) = 3,335,000원, 상위 3곳 {topline(a11)}
"""
    text(out / "강사용" / "정답_2교시.txt", key)
    print(key)


REQUESTS = open(Path(__file__).with_name("requests_02.txt"), encoding="utf-8").read()

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "..")
