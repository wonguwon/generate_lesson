import datetime as dt, random
STORES=[("강남점",12),("송파점",9),("분당점",10),("일산점",6),("인천점",7),("수원점",8)]
ITEMS=[("생수 2L(6입)",14,5900),("라면 5입",10,4500),("즉석밥 12입",6,13800),("참치캔 3입",8,7980),("식용유 1.8L",3,8900),("두루마리 휴지 30롤",5,15900)]
PRICE={n:p for n,_,p in ITEMS}
def gen(month, ndays, seed):
    rng=random.Random(seed); Q={}
    for d in range(1,ndays+1):
        w=4 if dt.date(2026,month,d).weekday()>=5 else 0
        for si in range(6):
            for pi in range(6):
                Q[d,si,pi]=STORES[si][1]+ITEMS[pi][1]+w+rng.randint(0,8)
    return Q
def rows9(Q,d):
    if d==25: return []
    rows=[[d,si,pi,Q[d,si,pi],Q[d,si,pi]*ITEMS[pi][2]] for si in range(6) for pi in range(6)]
    if d==16: rows+= [list(r) for r in rows[6:9]]
    if d==9: rows.append([d,0,0,-4,-4*5900])
    if d==30: rows.append([d,4,4,-2,-2*8900])
    return rows
def rows10(Q,d):
    rows=[[d,si,pi,Q[d,si,pi],Q[d,si,pi]*ITEMS[pi][2]] for si in range(6) for pi in range(6)]
    if d==15: rows+= [list(r) for r in rows[12:14]]
    if d==20: rows.append([d,5,1,-3,-3*4500])
    return rows
def report(month,ndays,seed,rowsf,weeks):
    Q=gen(month,ndays,seed)
    allr=[]; 
    tot_rows=0; tot_q=0
    for d in range(1,ndays+1):
        r=rowsf(Q,d); tot_rows+=len(r); tot_q+=sum(x[3] for x in r)
        allr+=r
    # dedupe & remove neg
    seen=set(); clean=[]
    for r in allr:
        t=tuple(r)
        if t in seen: continue
        seen.add(t)
        if r[3]<0: continue
        clean.append(r)
    print(month,"files rows",tot_rows,"qty",tot_q,"clean rows",len(clean),"qty",sum(r[3] for r in clean),"amt",sum(r[4] for r in clean))
    tot=sum(r[4] for r in clean)
    for si in range(6):
        q=sum(r[3] for r in clean if r[1]==si); a=sum(r[4] for r in clean if r[1]==si)
        print(" ",STORES[si][0],q,a,round(a/tot*100,1),round(a/1000))
    for wi,(s,e) in enumerate(weeks):
        q=sum(r[3] for r in clean if s<=r[0]<=e); a=sum(r[4] for r in clean if s<=r[0]<=e)
        print("  wk",wi+1,s,e,q,a,round(a/1000))
    daily={}
    for r in clean: daily[r[0]]=daily.get(r[0],0)+r[3]
    print("  maxday",max(daily,key=daily.get),max(daily.values()),"minday",min(daily,key=daily.get),min(daily.values()))
    print("  first row qty", Q[1,0,0], "dup values", )
    return Q
Q9=report(9,30,2126,rows9,[(1,6),(7,13),(14,20),(21,27),(28,30)])
print(" 9/16 dup", [Q9[16,1,p] for p in range(3)])
Q10=report(10,31,1031,rows10,[(1,4),(5,11),(12,18),(19,25),(26,31)])
print(" 10/15 dup", [Q10[15,2,p] for p in range(2)])
print(dt.date(2026,9,1).strftime('%a'),dt.date(2026,10,1).strftime('%a'),dt.date(2026,10,31).strftime('%a'),dt.date(2026,9,21).strftime('%a'))
# xls not deleted scenario
