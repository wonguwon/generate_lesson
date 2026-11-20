"""4교시 실습 파일 만들기: py -3.14 -X utf8 make_04.py ..

학습자용/주문내역_11월.csv, 학습자용/4교시_실습자료.zip,
학습자용/실습_요청문.txt, 강사용/정답_4교시.txt
11월 값은 2교시 작성 때 정답_2교시.txt 끝에 미리 적어 둔 값과 같아야 한다.
"""
import csv
import shutil
import sys
import zipfile
from pathlib import Path

import nuri_data as D
from make_02 import check_data, pct, text, write_csv

M = 11
def main(out):
    out = Path(out) / "04_코드로_작업물_만들기"
    A = check_data()
    a10, a11 = A[10], A[11]
    t = {m: A[m]["total"] for m in (7, 8, 9, 10, 11)}
    top = a11["top_clients"][:3]

    # 2교시에 정해 둔 11월 값 그대로
    assert D.ORDER_FILES[M] == "주문내역_11월.csv" and M not in D.DATE_FMT
    assert D.ORDER_COLS_RENAMED[M] == {"주문일": "일자", "거래처": "거래처명", "수량": "주문수량"}
    assert (a11["raw"], a11["clean"], t[11]) == (24, 22, 10_110_000)
    assert (a11["exact"], a11["reentry"], a11["blank"]) == (1, 0, 1)
    assert a11["blank_no"] == ["NR-2611-023"]
    assert top == [("윤슬찬푸드", 3_335_000), ("온기베이커리", 1_850_000), ("다온밀키트", 1_038_000)]
    assert [pct(a, t[11]) for _, a in top] == [33.0, 18.3, 10.3]
    assert [a11["staff"][c] for c, _ in top] == ["김도현", "김도현", "박준영"]
    assert len(set(a for _, a in a11["top_clients"][:4])) == 4
    # 윤슬찬푸드 11월 주문 = 1교시 수정 견적 공급가액
    assert top[0][1] == D.quote_totals(D.QUOTE_2)[0]
    assert t[11] - t[10] == 725_500 and pct(t[11] - t[10], t[10]) == 7.7

    # 실습 1: 스크립트로 10월 다시 실행 = 3교시 정답 그대로 (정리본은 그 달을 지우고 새로 → 78행 유지)
    assert (a10["raw"], a10["dup"], a10["blank"], a10["clean"], t[10]) == (23, 2, 1, 20, 9_384_500)
    assert a10["top_clients"][:3] == [("해든푸드", 1_688_000), ("온기베이커리", 1_438_000), ("한결유업", 1_230_000)]
    assert sum(A[m]["clean"] for m in (7, 8, 9, 10)) == 78
    # 11월 실행 뒤 정리본 100행
    assert sum(A[m]["clean"] for m in (7, 8, 9, 10, 11)) == 100
    # 다르게 나오면
    raw = D.raw_order_rows(M)
    no_dedup = [r for r in raw if r[4]]
    nd_total = sum(int(r[6]) for r in no_dedup)
    nd_on = sum(int(r[6]) for r in no_dedup if r[2] == "온기베이커리")
    assert (len(no_dedup), nd_total, nd_on) == (23, 10_930_000, 2_670_000)
    assert len(raw) - a11["dup"] == 23  # 수량 빈 행을 남기면 23행, 합계는 같음
    # 10월을 지우지 않고 다시 더하면
    assert 78 + 20 == 98

    # 실습 2 대시보드 (정리본 7~11월)
    rows = [r for m in (7, 8, 9, 10, 11) for r in D.ORDERS[m]]
    assert len(rows) == 100 and sum(r[4] * r[5] for r in rows) == 51_247_500
    by_c = {}
    for r in rows:
        by_c[r[2]] = by_c.get(r[2], 0) + r[4] * r[5]
    all_top = sorted(by_c.items(), key=lambda x: -x[1])
    assert all_top[:2] == [("윤슬찬푸드", 6_414_000), ("온기베이커리", 6_125_500)]
    assert A[9]["top_clients"][0] == ("고운떡집", 2_134_000) and (A[9]["clean"], t[9]) == (21, 11_675_500)
    assert A[10]["top_clients"][0] == ("해든푸드", 1_688_000)
    assert [t[m] for m in (7, 8, 9, 10, 11)] == [9_915_000, 10_162_500, 11_675_500, 9_384_500, 10_110_000]
    assert max(t.values()) == t[9]
    yun11 = [r for r in D.ORDERS[11] if r[2] == "윤슬찬푸드"]
    assert len(yun11) == 3
    # 원본(정리 전)을 읽었을 때 9월
    assert len(D.raw_order_rows(9)) == 24


    # 파일 쓰기
    for sub in ("학습자용", "강사용"):
        if (out / sub).exists():
            shutil.rmtree(out / sub)
    learn = out / "학습자용"
    learn.mkdir(parents=True)
    header = [D.ORDER_COLS_RENAMED[M].get(c, c) for c in D.ORDER_COLS]
    csv_path = learn / D.ORDER_FILES[M]
    write_csv(csv_path, header, raw)
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        got = list(csv.reader(f))
    assert got[0] == ["주문번호", "일자", "거래처명", "상품", "주문수량", "단가", "금액", "담당자", "비고"]
    assert len(got) - 1 == 24 and all(r[1].startswith("2026-11-") for r in got[1:])


    with zipfile.ZipFile(learn / "4교시_실습자료.zip", "w", zipfile.ZIP_DEFLATED) as z:
        z.write(csv_path, csv_path.name)
    text(learn / "실습_요청문.txt", REQUESTS)

    line = " / ".join(f"{c}({a11['staff'][c]}) {v:,}원 {pct(v, t[11])}%" for c, v in top)
    key = f"""[4교시 정답] 누리상사 영업관리팀 (강사용, 배포하지 않음)

시작 상태: 3교시 결과물(출력/주문_정리본.csv 78행, 처리기록.md, 출력/월별주문 4개, CLAUDE.md에 작업 규칙·월간 주문 정리)

실습 1 Python 스크립트
- Python 확인·설치: 없으면 설치 승인 창 → 설치 → 앱을 완전히 닫고 다시 열기 → \"Python 버전 알려줘\"에 3.x 버전
- scripts/주문정리.py 로 10월 실행 결과 (3교시 정답과 같음)
  합치기 전 23행 / 중복 2행·수량 빈칸 1행 뺌 / 정리 후 20행 / 판매 합계 {t[10]:,}원
  상위 3곳 해든푸드 1,688,000 / 온기베이커리 1,438,000 / 한결유업 1,230,000
  정리본은 그대로 78행 (10월을 지우고 새로 씀). 98행이면 10월이 두 번 들어간 것
- 11월 자료: {D.ORDER_FILES[M]} 열 이름 {', '.join(f'{k}→{v}' for k, v in D.ORDER_COLS_RENAMED[M].items())}. 24행
  똑같은 행 NR-2611-012, 수량 빈칸 NR-2611-023
- 11월 첫 실행: 멈춤. 없는 열 주문일·거래처·수량 (파일에는 일자·거래처명·주문수량)
- 고친 뒤 11월 실행: 합치기 전 24행 / 중복 1행·수량 빈칸 1행 뺌 / 정리 후 22행 / 판매 합계 {t[11]:,}원
  상위 3곳 {line}
  정리본 100행 (7월 18 · 8월 19 · 9월 21 · 10월 20 · 11월 22), 출력/월별주문 5개 (2026-11_주문.csv 추가)
  10월 대비 {t[11] - t[10]:+,}원 ({pct(t[11] - t[10], t[10]):+}%)
- 다르게 나오면: 23행·합계 10,930,000·온기베이커리 2,670,000 = 중복을 안 뺌 / 23행·합계 10,110,000 = 수량 빈 행 남김

실습 2 대시보드 (정리본 7~11월 100행)
- 월별 막대: 7월 9,915,000 / 8월 10,162,500 / 9월 11,675,500 / 10월 9,384,500 / 11월 10,110,000 (9월이 가장 큼)
- 9월: 21건, 11,675,500원, 1위 고운떡집 2,134,000원 (2교시 Docs와 같음)
- 10월: 20건, 9,384,500원, 1위 해든푸드 1,688,000원 (3교시 Docs와 같음)
- 11월: 22건, 10,110,000원, 1위 윤슬찬푸드 3,335,000원 / 11월+윤슬찬푸드: 3건 3,335,000원 (1교시 수정 견적 공급가액)
- 전체: 100건, 51,247,500원, 1위 윤슬찬푸드 6,414,000원
- 한 곳만 고치기: 전체·전체에서 9월 막대만 다른 색, 카드 숫자 그대로(100건, 51,247,500원), 선택 칸 동작 그대로
- 다르게 나오면: 9월 24건 = 정리본 대신 원본을 읽은 것

"""
    text(out / "강사용" / "정답_4교시.txt", key)
    print(key)


REQUESTS = open(Path(__file__).with_name("requests_04.txt"), encoding="utf-8").read()

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "..")
