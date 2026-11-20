import csv, sys, numpy as np
rows=list(csv.reader(open(sys.argv[1],encoding='utf-8')))[1:]
digs=np.array([[int(c) for c in ''.join(r[1:])] for r in rows],dtype=np.int8)
tails=np.array([[int(x[-2:]) for x in r[1:]] for r in rows]); N=len(rows)
I,J=np.where(~np.eye(107,dtype=bool))
pres=np.zeros((N,100),bool)
for t in range(N): pres[t,tails[t]]=True
p0=1-0.99**27
day=np.array([pres[t+1,digs[t,I]*10+digs[t,J]].mean() for t in range(N-1)])
# null: hoán vị thứ tự ngày (giữ nguyên mọi lệch cố định, phá phụ thuộc giữa ngày liền kề)
obs=day.mean(); rng=np.random.default_rng(20261120); ge=0; R=300; vals=[]
for r in range(R):
    perm=rng.permutation(N); d2=digs[perm]; p2=pres[perm]
    v=np.mean([p2[t+1,d2[t,I]*10+d2[t,J]].mean() for t in range(N-1)]); vals.append(v); ge+=v>=obs
print(f"ty le an trung binh theo ngay: {100*obs:.4f}% | moc {100*p0:.4f}%")
print(f"null hoan vi ngay: trung binh {100*np.mean(vals):.4f}%, sd {100*np.std(vals):.4f}, p mot phia = {(ge+1)/(R+1):.4f}")
# phần đóng góp: cầu ghép đúng 2 số cuối của một giải hôm qua (tức là 'lô về lại')
