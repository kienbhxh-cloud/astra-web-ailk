"""Kiểm định 'cầu vị trí' (ghép 2 chữ số ở 2 vị trí trong bảng kết quả kỳ trước) và 'nuôi cầu chạy ổn định'.
Cầu (i,j): lấy chữ số thứ i và thứ j trong 107 chữ số của kỳ t -> số d_i d_j; cầu 'ăn' nếu số đó về ở kỳ t+1.
Câu hỏi: cầu đã ăn liên tiếp k kỳ thì kỳ sau có ăn nhiều hơn mốc 23,77% không?"""
import csv, sys, numpy as np, json
path=sys.argv[1]
rows=list(csv.reader(open(path,encoding='utf-8')))[1:]
digs=np.array([[int(c) for c in ''.join(r[1:])] for r in rows],dtype=np.int8)   # (N,107)
tails=np.array([[int(x[-2:]) for x in r[1:]] for r in rows])
N,D=digs.shape; assert D==107
I,J=np.where(~np.eye(D,dtype=bool)); C=len(I)                                   # 11.342 cầu
pres=np.zeros((N,100),bool)
for t in range(N): pres[t,tails[t]]=True
streak=np.zeros(C,np.int32); K=12
hit_by=np.zeros(K+1); n_by=np.zeros(K+1)
for t in range(N-1):
    num=digs[t,I]*10+digs[t,J]
    hit=pres[t+1,num]
    k=np.minimum(streak,K)
    np.add.at(n_by,k,1); np.add.at(hit_by,k,hit)
    streak=np.where(hit,streak+1,0)
p0=1-0.99**27
out=[]
for k in range(K+1):
    n,h=n_by[k],hit_by[k]; r=h/n; z=(h-n*p0)/np.sqrt(n*p0*(1-p0))
    out.append(dict(chuoi_an=f"{k}{'+' if k==K else ''}",so_lan=int(n),ty_le_an_tiep=round(100*r,3),z=round(float(z),2)))
print(json.dumps(dict(so_cau=C,so_ky=N,moc=round(100*p0,3),ket_qua=out),ensure_ascii=False,indent=0))
