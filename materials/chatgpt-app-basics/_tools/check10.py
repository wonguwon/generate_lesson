import os, sys, datetime as dt, openpyxl, xlrd
D=sys.argv[1]; files=sorted(os.listdir(D)); print("files",len(files))
allrows=[]
for f in files:
    p=os.path.join(D,f)
    if f.endswith(".xls"):
        b=xlrd.open_workbook(p); s=b.sheet_by_name("일보"); hdr=s.row_values(0)
        rs=[]
        for i in range(1,s.nrows):
            v=s.row_values(i); v[0]=xlrd.xldate_as_datetime(v[0],b.datemode).date(); rs.append(v)
    else:
        wb=openpyxl.load_workbook(p); ws=wb["일보"]; vals=list(ws.values); hdr=vals[0]; rs=[list(r) for r in vals[1:]]
        for r in rs: r[0]=r[0].date() if isinstance(r[0],dt.datetime) else r[0]
    allrows+= [(f,*r) for r in rs]
    print(f, list(hdr)[1], len(rs), int(sum(r[3] for r in rs)), rs[0][0])
print("raw", len(allrows), int(sum(r[4] for r in allrows)), int(sum(r[5] for r in allrows)))
fix={"송파":"송파점"}
seen=set(); clean=[]
for r in allrows:
    key=(r[1],fix.get(r[2],r[2]),r[3],r[4],r[5])
    if r[4]<0 or key in seen: continue
    seen.add(key); clean.append(key)
print("clean",len(clean),int(sum(c[3] for c in clean)),int(sum(c[4] for c in clean)))
st={}
for c in clean: st.setdefault(c[1],[0,0]); st[c[1]][0]+=c[3]; st[c[1]][1]+=c[4]
for k,v in st.items(): print(k,int(v[0]),int(v[1]))
print("days",len({c[0] for c in clean}))
print(dt.date(2026,10,1).strftime("%A"), dt.date(2026,10,31).strftime("%A"), dt.date(2026,10,26).strftime("%A"))
