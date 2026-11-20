"""nuri_orders.py를 처음 한 번 만든 생성기 (기록용). 다시 돌릴 필요 없음: py -3.14 -X utf8 gen_orders.py nuri_orders.py

동률 없음·반올림 경계 피하기·월 합계 범위 조건을 만족하는 첫 seed를 찾아 ORDERS를 고정 값으로 씀.
"""
import random, datetime as dt, sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
import nuri_data as D

HOL = {dt.date(2026,7,17), dt.date(2026,8,14), dt.date(2026,8,17), dt.date(2026,9,24), dt.date(2026,9,25),
       dt.date(2026,9,28), dt.date(2026,10,5), dt.date(2026,10,9), dt.date(2026,8,15)}
QTY = {"개": [300,400,500,600,800,1000,1200,1500,2000,2500,3000], "롤": [5,8,10,12,15,20,25,30], "묶음": [10,15,20,25,30,40,50]}
SMALL = {"포장 테이프(투명)": [40,60,80,100,120,150,200]}
FIXED = {7: [("2026-07-08","윤슬찬푸드","아이스팩(500g)",1500)], 8: [("2026-08-05","윤슬찬푸드","보냉 파우치",3000)],
         9: [("2026-09-09","윤슬찬푸드","골판지 박스(대)",1600)], 10: [("2026-10-07","윤슬찬푸드","포장 테이프(투명)",120)],
         11: [("2026-11-02","윤슬찬푸드","골판지 박스(대)",2000,800),("2026-11-02","윤슬찬푸드","보냉 파우치",3500,320),("2026-11-02","윤슬찬푸드","아이스팩(500g)",1500,410)]}
N = {7:18, 8:19, 9:21, 10:20, 11:22}
UNIT = {p[1]: p[3] for p in D.PRODUCTS}
STAFF = {c[1]: c[4] for c in D.CLIENTS}
others = [c[1] for c in D.CLIENTS if c[1] != "윤슬찬푸드"]
NOTES = ["오전 납품", "분할 납품", "샘플 동봉", "세금계산서 별도 요청"]

def days(m):
    d = dt.date(2026, m, 1); out = []
    while d.month == m:
        if d.weekday() < 5 and d not in HOL: out.append(d)
        d += dt.timedelta(1)
    return out

def gen(seed):
    r = random.Random(seed); res = {}
    for m in (7,8,9,10,11):
        rows = [tuple(x) if len(x)==5 else (*x, D.PRICE[x[2]]) for x in FIXED[m]]
        ds = days(m)
        while len(rows) < N[m]:
            d = r.choice(ds).isoformat(); c = r.choice(others); p = r.choice(list(D.PRICE))
            cand = [q for q in SMALL.get(p, QTY[UNIT[p]]) if 150_000 <= q * D.PRICE[p] <= 1_600_000]
            if not cand: continue
            q = r.choice(cand)
            rows.append((d, c, p, q, D.PRICE[p]))
        rows.sort(key=lambda x: (x[0], x[1], x[2]))
        out = []
        for i, (d, c, p, q, u) in enumerate(rows, 1):
            note = r.choice(NOTES) if r.random() < 0.2 else ""
            out.append((f"NR-26{m:02d}-{i:03d}", d, c, p, q, u, STAFF[c], note))
        res[m] = out
    return res

def stats(rows):
    tot = sum(q*u for _,_,_,_,q,u,_,_ in rows)
    cl = {}; pr = {}
    for _,_,c,p,q,u,_,_ in rows:
        cl[c] = cl.get(c,0)+q*u; pr[p] = pr.get(p,0)+q*u
    return tot, sorted(cl.items(), key=lambda x:-x[1]), sorted(pr.items(), key=lambda x:-x[1])

def ok(res):
    tots = []
    for m in res:
        tot, cl, pr = stats(res[m]); tots.append(tot)
        v = [x[1] for x in cl[:4]]; w = [x[1] for x in pr[:4]]
        if len(set(v)) < 4 or len(set(w)) < 4: return False
        if len(set(r[2] for r in res[m])) < 8: return False
        for _, a in cl[:3]:
            x = a/tot*1000
            if abs(x - int(x) - 0.5) < 0.1: return False
        if v[2] - v[3] < 50000 or v[1]-v[2] < 50000: return False
    if len(set(tots)) < 5: return False
    for a, b in zip(tots, tots[1:]):
        x = (b-a)/a*1000
        if abs(x - int(x) - 0.5) < 0.1 or abs(b-a)/a < 0.02: return False
    # 9월이 8월보다 큼, 상위 거래처 7~9월 정해진 순서 아님
    if not (1.06 < tots[2]/tots[1] < 1.25): return False
    if min(tots) < 9_000_000 or max(tots) > 16_000_000: return False
    return True

for s in range(1, 200000):
    res = gen(s)
    if ok(res):
        print("seed", s)
        for m in res:
            t, cl, pr = stats(res[m]); print(m, len(res[m]), t, cl[:4], pr[:4])
        import pprint
        with open(sys.argv[1], "w", encoding="utf-8") as f:
            f.write('"""누리상사 월별 주문 (7~11월) 고정 데이터. gen_orders.py(seed %d)로 한 번 만든 뒤 고정함.\n\n' % s)
            f.write('행: (주문번호, 주문일 YYYY-MM-DD, 거래처, 상품, 수량, 단가, 담당자, 비고). 중복·빈칸 같은 지저분함은 make_02.py에서 더함.\n"""\n\n')
            f.write("ORDERS = " + pprint.pformat(res, width=140) + "\n")
        break
