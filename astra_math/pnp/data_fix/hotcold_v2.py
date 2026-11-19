import csv, numpy as np, sys
rows=list(csv.DictReader(open('xsmb_2005-10-01_to_2026-11-19_clean_v2_fix20060921.csv')))
cols=[c for c in rows[0] if c!='date']
dates=[r['date'] for r in rows]
D=np.array([[int(r[c][-2:]) for c in cols] for r in rows])          # (N,27)
N=len(D)
C=np.zeros((N,100),int)
for i in range(N): np.add.at(C[i],D[i],1)                          # counts per day per number
def contrast(C,W,start=365,k=5):
    cum=np.vstack([np.zeros(100,int),np.cumsum(C,0)])
    hot=cold=0
    for i in range(start,len(C)):
        c=cum[i]-cum[max(0,i-W)]
        o_hot=np.lexsort((np.arange(100),-c))[:k]; o_cold=np.lexsort((np.arange(100),c))[:k]
        hot+=C[i,o_hot].sum(); cold+=C[i,o_cold].sum()
    return hot,cold
n=N-365; mu=n*1.35
print("so ky danh gia",n,"ky vong nhay/bo",mu)
for W in (30,60,90,180,365):
    h,c=contrast(C,W); z=(h-c)/np.sqrt(n*2.7)
    print(f"W={W}: hot={h} ({(h-mu)/np.sqrt(n*1.2825):+.2f}) cold={c} ({(c-mu)/np.sqrt(n*1.2825):+.2f}) hot-cold={h-c} z={z:+.2f}")
# theo giai doan, W=90
for lo,hi in (("2005","2016"),("2016","2027")):
    idx=[i for i,d in enumerate(dates) if lo<=d[:4]<hi]
    a=max(0,idx[0]-365); sub=C[a:idx[-1]+1]; st=idx[0]-a if idx[0]>=365 else 365
    h,c=contrast(sub,90,start=st); m=len(sub)-st
    print(f"{lo}-{hi} W=90: hot-cold={h-c} z={(h-c)/np.sqrt(m*2.7):+.2f} (n={m})")
# null hoan vi thu tu ngay (W=90)
rng=np.random.default_rng(20261120); R=int(sys.argv[1]) if len(sys.argv)>1 else 200
for W in (60,90):
    h0,c0=contrast(C,W); obs=h0-c0; ge=0; vals=[]
    for r in range(R):
        h,c=contrast(C[rng.permutation(N)],W); vals.append(h-c); ge+= (h-c)>=obs
    print(f"W={W} hoan vi ngay R={R}: obs={obs}, null mean={np.mean(vals):.1f} sd={np.std(vals):.1f}, p_mot_phia={(ge+1)/(R+1):.4f}")
