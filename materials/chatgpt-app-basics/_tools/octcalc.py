import datetime as dt, random, sys
STORES=[("강남점",12),("송파점",9),("분당점",10),("일산점",6),("인천점",7),("수원점",8)]
ITEMS=[("생수 2L(6입)",14,5900),("라면 5입",10,4500),("즉석밥 12입",6,13800),("참치캔 3입",8,7980),("식용유 1.8L",3,8900),("두루마리 휴지 30롤",5,15900)]
PRICE={n:p for n,_,p in ITEMS}
seed=int(sys.argv[1])
rng=random.Random(seed); Q={}
for d in range(1,32):
  w=4 if dt.date(2026,10,d).weekday()>=5 else 0
  for s in range(6):
    for p in range(6): Q[d,s,p]=STORES[s][1]+ITEMS[p][1]+w+rng.randint(0,8)
def fname(d):
  if d<=2: return f"일보 10-{d}.xls"
  if d<=11: return f"10{d:02d}_일보.xlsx"
  if d<=18: return f"10월{d}일 판매.xlsx"
  if d<=25: return f"일보_202610{d}.xlsx"
  if d==31: return "10월 일보(최종).xlsx"
  return f"판매일보(10.{d}).xlsx"
def rows(d):
  date=dt.date(2026,10,d); r=[]
  for si,(s,_) in enumerate(STORES):
    nm="송파" if (d==12 and s=="송파점") else s
    for pi,(it,_,pr) in enumerate(ITEMS):
      q=Q[d,si,pi]; r.append([date,nm,it,q,q*pr])
  if d==15: r+= [list(x) for x in r[12:14]]
  if d==20: r.append([date,"수원점","라면 5입",-3,-3*PRICE["라면 5입"]])
  return r
WD="월화수목금토일"
tot_rows=0; tot_q=0
print("day file rows qty weekday")
for d in range(1,32):
  rr=rows(d); q=sum(x[3] for x in rr); tot_rows+=len(rr); tot_q+=q
  print(d,WD[dt.date(2026,10,d).weekday()],fname(d),len(rr),q)
print("raw",tot_rows,tot_q)
# clean
cq=sum(Q.values()); ca=sum(Q[k]*ITEMS[k[2]][2] for k in Q)
print("clean rows",31*36,"qty",cq,"amt",ca)
dup=[rows(15)[i] for i in (12,13)]; print("dup",[(x[1],x[2],x[3],x[4]) for x in dup])
print("neg qty -3 amt",-3*4500)
st={}
for si,(s,_) in enumerate(STORES):
  q=sum(Q[d,si,p] for d in range(1,32) for p in range(6)); a=sum(Q[d,si,p]*ITEMS[p][2] for d in range(1,32) for p in range(6)); st[s]=(q,a)
for s,(q,a) in st.items(): print(s,q,a,round(a/ca*100,1), round(a/1000))
print("sum rounded k", sum(round(a/1000) for q,a in st.values()), "total k", round(ca/1000))
weeks=[(1,4),(5,11),(12,18),(19,25),(26,31)]
for i,(a,b) in enumerate(weeks,1):
  q=sum(Q[d,s,p] for d in range(a,b+1) for s in range(6) for p in range(6)); m=sum(Q[d,s,p]*ITEMS[p][2] for d in range(a,b+1) for s in range(6) for p in range(6))
  print(f"{i}주차 10/{a}({WD[dt.date(2026,10,a).weekday()]})~10/{b}({WD[dt.date(2026,10,b).weekday()]}) days {b-a+1} q {q} amt {m} k {round(m/1000)}")
print("sum week k", sum(round(sum(Q[d,s,p]*ITEMS[p][2] for d in range(a,b+1) for s in range(6) for p in range(6))/1000) for a,b in weeks))
dq={d:sum(Q[d,s,p] for s in range(6) for p in range(6)) for d in range(1,32)}
print("max day",sorted(dq.items(),key=lambda x:-x[1])[:3],"min",sorted(dq.items(),key=lambda x:x[1])[:3])
