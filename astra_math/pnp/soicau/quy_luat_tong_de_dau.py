import csv, sys, json, math
rows=list(csv.reader(open(sys.argv[1],encoding='utf-8')))[1:]
db=[r[1].zfill(5) for r in rows]; de=[int(x[-2:]) for x in db]; N=len(db); W=7
def droot(s):
    while s>=10: s=sum(map(int,str(s)))
    return s
cach={"A: tong 2 so cuoi < 10":lambda i:(de[i]//10+de[i]%10) if de[i]//10+de[i]%10<10 else None,
      "B: tong 2 so cuoi mod 10":lambda i:(de[i]//10+de[i]%10)%10,
      "C: cong don 5 chu so":lambda i:droot(sum(map(int,db[i])))}
pW=1-0.9**W; out={"moc_7_ky":round(100*pW,2)}
for name,f in cach.items():
    r={}
    for vt,g in (("dau",lambda x:x//10),("dit",lambda x:x%10)):
        n=h=0
        for i in range(N-W):
            d=f(i)
            if d is None: continue
            n+=1; h+=any(g(de[i+k])==d for k in range(1,W+1))
        r[vt]=dict(n=n,ty_le=round(100*h/n,2),z=round((h-n*pW)/math.sqrt(n*pW*(1-pW)),2))
    out[name]=r
print(json.dumps(out,ensure_ascii=False,indent=1))
