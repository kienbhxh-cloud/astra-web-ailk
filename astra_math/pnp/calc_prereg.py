from math import comb, sqrt, ceil
from fractions import Fraction as F
from statistics import NormalDist
N=NormalDist()
# exact baselines
p_lo = 1-F(99,100)**27
def p_set_any_u(u,k=5): return 1-F(comb(100-u,k),comb(100,k))
print("p_lo", float(p_lo))
# distribution of u (distinct endings among 27 iid uniform) -> exact via occupancy DP
dp={0:F(1)}
for _ in range(27):
    nd={}
    for u,pr in dp.items():
        nd[u]=nd.get(u,0)+pr*F(u,100); nd[u+1]=nd.get(u+1,0)+pr*F(100-u,100)
    dp=nd
Eany=sum(pr*p_set_any_u(u) for u,pr in dp.items())
Eu=sum(pr*u for u,pr in dp.items())
print("E[u]",float(Eu),"P(any of 5 | random5, uncond)",float(Eany))
# presence variable Brier baseline: each number present w.p. p_lo; Brier of constant p_lo forecast = p(1-p)
print("Brier baseline per number", float(p_lo*(1-p_lo)))
# nhay per day for 5 numbers
mu=1.35; var=27*0.05*0.95; print("nhay mean/var",mu,var)
for price in (22500,23000):
    be = 5*price/80000   # needed nhay per day for 5 pts each? per point: hits*80000 = price -> hits per number = price/80000; for 5 numbers
    print(price,"break-even nhay/day",be,"edge needed %", (be/mu-1)*100)
za1=N.inv_cdf(1-0.05/6); zb=N.inv_cdf(0.8)
print("z_alpha(0.05/6 one-sided)",za1)
p0=float(Eany); q0=1-p0
print("\nPower: any-hit metric (5-set), alpha=0.05/6 one-sided, power 0.8")
for d in (0.01,0.02,0.03,0.05):
    p1=p0+d; n=((za1*sqrt(p0*q0)+zb*sqrt(p1*(1-p1)))/d)**2; print(f" +{d*100:.0f}pp -> n={ceil(n)}")
print("Power: nhay metric")
sd=sqrt(var)
for name,d in (("break-even 22.5k",5*22500/80000-1.35),("break-even 23k",5*23000/80000-1.35),("+10%",0.135),("+20%",0.27)):
    n=((za1+zb)*sd/d)**2; print(f" {name}: delta={d:.4f} -> n={ceil(n)} ky")
# power at 180 days for break-even
for n in (60,180,365,1000):
    for d in (5*22500/80000-1.35,):
        pw=1-N.cdf(za1-d*sqrt(n)/sd); print(f" n={n}: power to detect break-even(22.5k) edge = {pw:.3f}")
