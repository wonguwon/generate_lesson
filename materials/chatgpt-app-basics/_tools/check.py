import datetime as dt, random
from collections import defaultdict, Counter
STORES = [("강남점", 12), ("송파점", 9), ("분당점", 10),("일산점", 6), ("인천점", 7), ("수원점", 8)]
ITEMS = [("생수 2L(6입)", 14, 5900), ("라면 5입", 10, 4500),("즉석밥 12입", 6, 13800), ("참치캔 3입", 8, 7980),("식용유 1.8L", 3, 8900), ("두루마리 휴지 30롤", 5, 15900)]
PRICE = {n:p for n,_,p in ITEMS}
def gen(month, ndays, seed):
    rng = random.Random(seed); Q={}
    for day in range(1, ndays+1):
        w = 4 if dt.date(2026, month, day).weekday() >= 5 else 0
        for si in range(6):
            for pi in range(6):
                Q[day,si,pi] = STORES[si][1]+ITEMS[pi][1]+w+rng.randint(0,8)
    return Q
def rows9(Q, day):
    RS = {14: ("강남점", "강남"), 22: ("분당점", "분당지점"), 29: ("수원점", "수원 점")}
    if day==25: return []
    d=dt.date(2026,9,day); rows=[]
    for si,(s,_) in enumerate(STORES):
        n=s
        if day in RS and RS[day][0]==s: n=RS[day][1]
        for pi,(it,_,p) in enumerate(ITEMS):
            q=Q[day,si,pi]; rows.append([d,n,it,q,q*p])
    if day==16: rows += [list(r) for r in rows[6:9]]
    if day==9: rows.append([d,"강남점","생수 2L(6입)",-4,-4*5900])
    if day==30: rows.append([d,"인천점","식용유 1.8L",-2,-2*8900])
    return rows
def rows10(Q, day):
    d=dt.date(2026,10,day); rows=[]
    for si,(s,_) in enumerate(STORES):
        n = "송파" if (day==12 and s=="송파점") else s
        for pi,(it,_,p) in enumerate(ITEMS):
            q=Q[day,si,pi]; rows.append([d,n,it,q,q*p])
    if day==15: rows += [list(r) for r in rows[12:14]]
    if day==20: rows.append([d,"수원점","라면 5입",-3,-3*4500])
    return rows
canon={"강남":"강남점","분당지점":"분당점","수원 점":"수원점","송파":"송파점"}
def analyze(month, nd, seed, rowsf):
    Q=gen(month,nd,seed); allr=[]; per={}
    for day in range(1,nd+1):
        r=rowsf(Q,day); per[day]=(len(r),sum(x[3] for x in r)); allr+=r
    print(month,"월 per-day:", per)
    print("total rows",sum(v[0] for v in per.values()),"qty",sum(v[1] for v in per.values()))
    # dedupe exact, drop negatives
    seen=set(); out=[]; dup=[]; neg=[]
    for r in allr:
        t=tuple(r)
        if t in seen: dup.append(r); continue
        seen.add(t)
        if r[3]<0: neg.append(r); continue
        out.append([r[0],canon.get(r[1],r[1]),r[2],r[3],r[4]])
    print("dups",[(str(x[0]),x[1],x[2],x[3]) for x in dup]); print("neg",[(str(x[0]),x[1],x[2],x[3]) for x in neg])
    print("out rows",len(out),"qty",sum(r[3] for r in out),"amt",sum(r[4] for r in out))
    st=defaultdict(lambda:[0,0]); tot=sum(r[4] for r in out)
    for r in out: st[r[1]][0]+=r[3]; st[r[1]][1]+=r[4]
    for s,_ in STORES: print(s, st[s], round(st[s][1]/tot*100,2), round(st[s][1]/1000))
    print("sum of rounded pct", sum(round(st[s][1]/tot*100,1) for s,_ in STORES), "sum thousand", sum(round(st[s][1]/1000) for s,_ in STORES), round(tot/1000))
    # weeks Mon-Sun
    wk=defaultdict(lambda:[0,0,set()])
    first=dt.date(2026,month,1); start=first-dt.timedelta(days=first.weekday())
    for r in out:
        w=(r[0]-start).days//7+1; wk[w][0]+=r[3]; wk[w][1]+=r[4]; wk[w][2].add(r[0])
    for w in sorted(wk): print("week",w,wk[w][0],wk[w][1],len(wk[w][2]),min(wk[w][2]),max(wk[w][2]), round(wk[w][1]/1000))
    dq=defaultdict(int); da=defaultdict(int)
    for r in out: dq[r[0]]+=r[3]; da[r[0]]+=r[4]
    print("max qty day", max(dq.items(), key=lambda x:x[1]), "min", min(dq.items(), key=lambda x:x[1]))
    print("max amt day", max(da.items(), key=lambda x:x[1]))
    # ties
    print("qty counter top", sorted(dq.values())[-3:], sorted(dq.values())[:3])
    # first row
    print("first row", out[0])
    return out
o9=analyze(9,30,2126,rows9)
o10=analyze(10,31,1031,rows10)
for m,n in [(9,30),(10,31)]:
    print([ (d, "월화수목금토일"[dt.date(2026,m,d).weekday()]) for d in range(1,n+1)])
print(dt.date(2026,9,21).weekday(), dt.date(2026,9,24), dt.date(2026,9,25).weekday())
