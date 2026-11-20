"""ASTRA-LO/DISC-001 (KTST): ước lượng TRẦN lợi thế dự báo bằng thành phần phương sai.
Mô hình: mỗi số n có xác suất mỗi lượt quay theta_n(t) = p(1 + e_n(t)), p = 1/100.
- Phần cố định: e_n không đổi theo thời gian.
- Phần thay đổi nhưng bền: cov(e_n(b), e_n(b+1)) giữa hai khối W kỳ liền nhau.
Đếm nháy C[b,n] trong khối W kỳ: E = 27W p, Var = 27W p(1-p) + (27Wp)^2 Var(e).
=> hiệp phương sai trễ 1 của độ lệch C (chuẩn hóa theo (27Wp)^2) ước lượng phần dự báo được của e.
Null: hoán vị thứ tự KỲ (giữ lệch cố định, phá phụ thuộc thời gian)."""
import csv, sys, json, numpy as np
rows=list(csv.reader(open(sys.argv[1],encoding='utf-8')))[1:]
T=np.array([[int(x[-2:]) for x in r[1:]] for r in rows]); N=len(T)
Cday=np.zeros((N,100)); 
for t in range(N): np.add.at(Cday[t],T[t],1)
p=0.01
def stats(Cd,W):
    B=len(Cd)//W; C=Cd[:B*W].reshape(B,W,100).sum(1); mu=27*W*p
    d=C-mu
    g1=np.mean(d[:-1]*d[1:])/mu**2            # cov trễ 1 (đơn vị e^2)
    v=(np.mean(d**2)-27*W*p*(1-p))/mu**2      # Var(e) tổng (cố định + thay đổi)
    fixed=(np.var(Cd.sum(0)/ (len(Cd)*27*p) -1) - (1-p)/(len(Cd)*27*p))  # phương sai phần cố định
    return g1,v,fixed
rng=np.random.default_rng(20261120); R=int(sys.argv[2]) if len(sys.argv)>2 else 300
out={}
for W in (7,30,90,180,365):
    g1,v,fx=stats(Cday,W)
    null=np.array([stats(Cday[rng.permutation(N)],W)[0] for _ in range(R)])
    exc=g1-null.mean()                                   # phần thay đổi theo thời gian, bền qua 1 khối
    pval=(1+np.sum(null>=g1))/(R+1)
    sd_pred=np.sqrt(max(exc,0))
    out[W]=dict(cov_tre1=round(g1*1e4,3),null_tb=round(null.mean()*1e4,3),null_sd=round(null.std()*1e4,3),
                p_mot_phia=round(pval,4),sd_e_du_bao_duoc_pct=round(100*sd_pred,2),
                tran_loi_the_top5_pct=round(100*2.33*sd_pred,2),var_e_tong_x1e4=round(v*1e4,3))
out["phan_co_dinh_sd_e_pct"]=round(100*np.sqrt(max(fx,0)),2)
out["can_de_hoa_von_pct"]=4.17
print(json.dumps(out,ensure_ascii=False,indent=1))
