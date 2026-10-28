import datetime as dt, random
STORES=[("강남점",12),("송파점",9),("분당점",10),("일산점",6),("인천점",7),("수원점",8)]
ITEMS=[("생수 2L(6입)",14,5900),("라면 5입",10,4500),("즉석밥 12입",6,13800),("참치캔 3입",8,7980),("식용유 1.8L",3,8900),("두루마리 휴지 30롤",5,15900)]
rng=random.Random(2126);Q={}
for d in range(1,31):
    w=4 if dt.date(2026,9,d).weekday()>=5 else 0
    for si in range(6):
        for pi in range(6):
            Q[d,si,pi]=STORES[si][1]+ITEMS[pi][1]+w+rng.randint(0,8)
rows=[(d,si,pi,Q[d,si,pi],Q[d,si,pi]*ITEMS[pi][2]) for d in range(1,31) if d!=25 for si in range(6) for pi in range(6)]
print(len(rows),sum(r[3] for r in rows),sum(r[4] for r in rows))
print("first row",rows[0])
tq=sum(r[3] for r in rows);ta=sum(r[4] for r in rows)
for si,(s,_) in enumerate(STORES):
    q=sum(r[3] for r in rows if r[1]==si);a=sum(r[4] for r in rows if r[1]==si)
    print(s,q,a,f"{a/ta*100:.2f}% qty{q/tq*100:.2f}%")
for pi,(p,_,_) in enumerate(ITEMS):
    q=sum(r[3] for r in rows if r[2]==pi);a=sum(r[4] for r in rows if r[2]==pi)
    print(p,q,a,f"{a/ta*100:.2f}%")
weeks=[(1,6),(7,13),(14,20),(21,27),(28,30)]
for a,b in weeks:
    rr=[r for r in rows if a<=r[0]<=b]
    print(a,b,dt.date(2026,9,a).strftime('%a'),dt.date(2026,9,b).strftime('%a'),len(rr),sum(r[3] for r in rr),sum(r[4] for r in rr))
daily={}
for r in rows: daily.setdefault(r[0],[0,0]);daily[r[0]][0]+=r[3];daily[r[0]][1]+=r[4]
for d,v in daily.items(): print(d,dt.date(2026,9,d).strftime('%a'),v)
s=sorted(daily.items(),key=lambda x:x[1][0]);print("min",s[:3],"max",s[-3:])
sa=sorted(daily.items(),key=lambda x:x[1][1]);print("amt min",sa[:2],"max",sa[-2:])
print("avg daily qty",tq/29,"avg amt",ta/29)
# store 1위 by amount; check ties
