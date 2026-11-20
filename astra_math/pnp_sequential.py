"""QD-001 e-process replay. Synthetic-only scoring until G3 is verified.

Primary validity requires E[Y_t | past] <= 1.35, Y_t in [0,27].
Secondary conditional-u benchmark requires exchangeable uniform labels,
not merely the primary mean null. It is descriptive, not another alpha claim.
"""
import math
from fractions import Fraction
from math import comb
from .pnp_foundations import HashLog

MEAN_LAMBDAS=(.01,.02,.044,.1,.2)
HIT_LAMBDAS=(.05,.1,.2,.5,1.)

def _mixture(observations,lambdas):
    logs=[0.]*len(lambdas)
    for increment in observations:
        for i,lam in enumerate(lambdas):
            factor=1+lam*increment
            if factor<0:raise ValueError('Negative betting factor')
            logs[i]=logs[i]+math.log(factor) if factor else -math.inf
    peak=max(logs)
    logw=peak+math.log(sum(math.exp(v-peak) for v in logs)/len(logs)) if peak!=-math.inf else -math.inf
    return {'log_wealth':logw,'wealth':math.exp(logw) if logw<709 else None}

def eprocess_mean(counts):
    counts=tuple(counts)
    if any(type(y)!=int or not 0<=y<=27 for y in counts):raise ValueError('Counts must be integers 0..27')
    return _mixture((y-1.35 for y in counts),MEAN_LAMBDAS)

def p_set_any_given_u(u):
    if type(u)!=int or not 0<=u<=27:raise ValueError('u must be 0..27')
    return 1-Fraction(comb(100-u,5),comb(100,5))

def eprocess_any_hit(hits,unique_counts):
    hits=tuple(hits);unique_counts=tuple(unique_counts)
    if len(hits)!=len(unique_counts):raise ValueError('Length mismatch')
    increments=[]
    for hit,u in zip(hits,unique_counts):
        if type(hit)!=int or hit not in (0,1):raise ValueError('Binary hit required')
        p=float(p_set_any_given_u(u))
        if p==0:
            if hit:raise ValueError('Impossible hit with u=0')
            increments.append(0.)
        else:increments.append((hit-p)/p)
    return _mixture(increments,HIT_LAMBDAS)

class SyntheticScoreLog(HashLog):
    def score(self,forecast_log,method_id,draw,m=3):
        if type(m)!=int or not 1<=m<=3:raise ValueError('m must be fixed 1..3')
        forecasts=[r for r in forecast_log.read() if r['payload']['event'].get('method_id')==method_id and r['payload']['event'].get('target_date')==draw.day.isoformat()]
        if len(forecasts)!=1:raise ValueError('Exactly one existing forecast required')
        forecast=forecasts[0];event=forecast['payload']['event']
        if event.get('mode')!='synthetic':raise ValueError('G3 closed: synthetic only')
        selected=event.get('selected_numbers',[])
        if len(selected)!=5 or len(set(selected))!=5 or any(type(x)!=int or not 0<=x<100 for x in selected):raise ValueError('Five distinct frozen selections required')
        count=sum(x in selected for x in draw.tails);hit=int(count>0);u=len(set(draw.tails))
        def check(rows):
            if len(rows)!=len(snapshot):raise ValueError('Concurrent append: replay score')
            past=[r['payload']['event'] for r in rows if r['payload']['event']['method_id']==method_id]
            if any(e['target_date']>=draw.day.isoformat() for e in past):raise ValueError('Duplicate or out-of-order score')
            if any(e['m']!=m for e in past):raise ValueError('Cannot change multiplicity')
        rows=self.read();snapshot=rows;check(rows)
        past=[r['payload']['event'] for r in rows if r['payload']['event']['method_id']==method_id]
        primary=eprocess_mean([e['count'] for e in past]+[count])
        secondary=eprocess_any_hit([e['hit'] for e in past]+[hit],[e['unique_count'] for e in past]+[u])
        return self.append({'kind':'synthetic_score','mode':'synthetic','method_id':method_id,'target_date':draw.day.isoformat(),
            'forecast_sha256':forecast['sha256'],'count':count,'hit':hit,'unique_count':u,'m':m,
            'primary':primary,'secondary_descriptive':secondary,'threshold':20*m,
            'primary_crossed':primary['log_wealth']>=math.log(20*m),
            'simulation_cost':562500,'simulation_payout':400000*count,'simulation_net':400000*count-562500},check)
