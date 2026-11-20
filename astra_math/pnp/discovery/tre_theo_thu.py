"""Giả thuyết H-DAI: mỗi đài quay (theo thứ trong tuần) có lệch riêng -> phụ thuộc mạnh nhất ở trễ 7, 14.
Thống kê: hiệp phương sai trễ L của số nháy mỗi số giữa kỳ t và t-L, L = 1..21. Null: hoán vị kỳ."""
import csv, sys, json, numpy as np, datetime as dt
rows=list(csv.reader(open(sys.argv[1],encoding='utf-8')))[1:]
T=np.array([[int(x[-2:]) for x in r[1:]] for r in rows]); N=len(T)
dates=[dt.date.fromisoformat(r[0]) for r in rows]
C=np.zeros((N,100))
for t in range(N): np.add.at(C[t],T[t],1)
D=C-0.27
def g(Cm,L): return float(np.mean(Cm[L:]*Cm[:-L]))
# trễ tính theo NGÀY LỊCH đúng L (bỏ cặp vắng ngày) để 'cùng thứ' chính xác
idx={d:i for i,d in enumerate(dates)}
def g_cal(Dm,L):
    a=[i for i,d in enumerate(dates) if d-dt.timedelta(days=L) in idx]
    b=[idx[dates[i]-dt.timedelta(days=L)] for i in a]
    return float(np.mean(Dm[a]*Dm[b]))
rng=np.random.default_rng(7); R=int(sys.argv[2])
obs={L:g_cal(D,L) for L in range(1,22)}
null={L:[] for L in obs}
for _ in range(R):
    Dp=D[rng.permutation(N)]
    for L in obs: null[L].append(g_cal(Dp,L))
res=[]
for L in obs:
    nl=np.array(null[L]); z=(obs[L]-nl.mean())/nl.std()
    res.append(dict(tre_ngay=L,cung_thu=L%7==0,cov_x1e4=round(obs[L]*1e4,3),z=round(z,2),p_mot_phia=round((1+np.sum(nl>=obs[L]))/(R+1),4)))
print(json.dumps(res,ensure_ascii=False))
