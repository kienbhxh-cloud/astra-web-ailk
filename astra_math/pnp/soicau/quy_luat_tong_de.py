"""Kiểm định quy luật của bạn LK (20/11/2026): cộng các chữ số của đề ra số d < 10
=> trong 7 kỳ tiếp theo, đề có d ở đầu hoặc đít."""
import csv, sys, json, math
rows=list(csv.reader(open(sys.argv[1],encoding='utf-8')))[1:]
db=[r[1].zfill(5) for r in rows]; de=[int(x[-2:]) for x in db]; N=len(db)
W=7
def has(d,x): return x//10==d or x%10==d
def droot(s): 
    while s>=10: s=sum(map(int,str(s)))
    return s
cach={
 "A: tong 2 so cuoi, chi khi < 10": lambda i: (de[i]//10+de[i]%10) if de[i]//10+de[i]%10<10 else None,
 "B: tong 2 so cuoi mod 10 (moi ky)": lambda i: (de[i]//10+de[i]%10)%10,
 "C: cong don 5 chu so den khi < 10": lambda i: droot(sum(map(int,db[i]))),
}
p1=1-0.9**2; pW=1-(1-p1)**W
out={"moc_1_ky":round(100*p1,2),"moc_7_ky_neu_ngau_nhien":round(100*pW,3)}
for name,f in cach.items():
    n=h=0; first=[0]*W; n1=h1=0
    for i in range(N-W):
        d=f(i)
        if d is None: continue
        n+=1; hits=[has(d,de[i+k]) for k in range(1,W+1)]
        h+=any(hits)
        n1+=1; h1+=hits[0]
    z=(h-n*pW)/math.sqrt(n*pW*(1-pW))
    out[name]=dict(so_lan_kich_hoat=n,dung=h,ty_le_dung=round(100*h/n,3),z_so_voi_ngau_nhien=round(z,2),
                   ky_ngay_sau_dung=round(100*h1/n1,2))
print(json.dumps(out,ensure_ascii=False,indent=1))
