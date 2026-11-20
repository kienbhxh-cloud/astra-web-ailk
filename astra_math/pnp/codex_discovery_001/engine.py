"""ASTRA Automated Pattern Discovery Engine 0.1: bounded declarative formulas.

No eval/exec, generated imports or network access inside the engine. Historical
results remain exploratory. New grammar/parameters require a new version/run.
"""
import argparse,csv,hashlib,itertools,json,math,platform,time
from datetime import date,datetime,timezone
from pathlib import Path
import numpy as np

P0=1-.99**27
def digest(data):return hashlib.sha256(data).hexdigest()
def encoded(obj):return json.dumps(obj,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def load(path,expected):
    raw=Path(path).read_bytes()
    if digest(raw)!=expected:raise ValueError('Input hash mismatch')
    rows=list(csv.reader(raw.decode('utf-8-sig').splitlines()))
    widths=[5]*10+[4]*10+[3]*3+[2]*4
    dates=[];tails=[];full=[]
    for row in rows[1:]:
        if len(row)!=28 or any(not x.isascii() or not x.isdigit() or len(x)!=w for x,w in zip(row[1:],widths)):raise ValueError('Invalid prize width/content')
        date.fromisoformat(row[0]);dates.append(row[0]);full.append(tuple(row[1:]));tails.append([int(x[-2:]) for x in row[1:]])
    if not dates or dates!=sorted(set(dates)):raise ValueError('Dates must be unique, sorted')
    if len(set(full))!=len(full):raise ValueError('Exact full-row duplicate across dates: review G0')
    return np.array(dates),np.array(tails,dtype=np.int16)

def features(tails,prior=100):
    n=len(tails);counts=np.zeros((n,100),dtype=np.float64)
    for t,row in enumerate(tails):np.add.at(counts[t],row,1)
    y=(counts>0).astype(float);cum=np.vstack([np.zeros((1,100)),np.cumsum(y,axis=0)])
    base={};baselines={'uniform':np.full_like(y,P0)}
    denom=np.arange(n)[:,None]
    baselines['history']=(cum[:-1]+prior*P0)/(denom+prior)
    for w in (7,30,90,365):
        idx=np.maximum(0,np.arange(n)-w);length=np.arange(n)-idx
        f=(cum[np.arange(n)]-cum[idx]+prior*P0)/(length[:,None]+prior)
        base['freq'+str(w)]=f-P0
        if w!=7:baselines['window'+str(w)]=f
    previous=np.vstack([np.zeros((1,100)),y[:-1]])
    base['last']=previous;base['reverse_last']=previous[:,np.array([10*(i%10)+i//10 for i in range(100)])]
    gap=np.full((n,100),0.);last=np.full(100,-1,dtype=int)
    ew=np.full(100,P0);ewma=np.zeros_like(y);alpha=1-2**(-1/90)
    for t in range(n):
        gap[t]=np.where(last>=0,1/(1+t-last),0)
        ewma[t]=ew;ew=(1-alpha)*ew+alpha*y[t]
        last[y[t]>0]=t
    base['gap_inverse']=gap;baselines['ewma90']=ewma
    prev_counts=np.vstack([np.zeros((1,100)),counts[:-1]])
    heads=prev_counts.reshape(n,10,10).sum(axis=2);units=prev_counts.reshape(n,10,10).sum(axis=1)
    base['head_pressure']=(heads[:,np.arange(100)//10]-2.7)/2.7
    base['tail_pressure']=(units[:,np.arange(100)%10]-2.7)/2.7
    prev_db=np.r_[0,tails[:-1,0]]
    base['db_mod_cos']=np.cos(2*np.pi*(np.arange(100)[None,:]-prev_db[:,None])/100);base['db_mod_cos'][0]=0
    return y,counts,base,baselines

def grammar():
    atoms=['freq7','freq30','freq90','freq365','last','reverse_last','gap_inverse','head_pressure','tail_pressure','db_mod_cos']
    expressions=[{'atom':a} for a in atoms]
    expressions += [{'op':'sub','args':[{'atom':a},{'atom':b}]} for a,b in itertools.combinations(['freq7','freq30','freq90'],2)]
    expressions += [{'op':'mul','args':[{'atom':'last'},{'atom':'reverse_last'}]},
        {'op':'mul','args':[{'op':'sub','args':[{'atom':'head_pressure'},{'atom':'tail_pressure'}]},
                            {'op':'sub','args':[{'atom':'freq7'},{'atom':'freq90'}]}]}]
    return expressions

def evaluate(expr,base,depth=0):
    if depth>3:raise ValueError('Grammar depth exceeded')
    if set(expr)=={'atom'} and expr['atom'] in base:return base[expr['atom']]
    if set(expr)!={'op','args'} or expr['op'] not in ('sub','mul') or len(expr['args'])!=2:raise ValueError('Unapproved expression')
    a,b=[evaluate(x,base,depth+1) for x in expr['args']]
    return a-b if expr['op']=='sub' else a*b

def fit(x,y,train,ridge):
    xx=x[train];yy=y[train]-P0;mean=float(xx.mean());sd=float(xx.std())
    sd=max(sd,1e-12);z=(xx-mean)/sd
    intercept=float(yy.mean());slope=float(np.mean(z*(yy-intercept))/(1+ridge))
    return {'mean':mean,'sd':sd,'intercept':intercept,'slope':slope}
def predict(x,fit):return np.clip(P0+fit['intercept']+fit['slope']*(x-fit['mean'])/fit['sd'],1e-6,1-1e-6)
def daily_brier(p,y):return np.mean((p-y)**2,axis=1)
def top_metrics(p,y,counts):
    result={}
    # Stable ties resolved by smaller label; only ranking is affected.
    ranking=np.argsort(-p,axis=1,kind='stable')
    for k in (1,3,5):
        ix=ranking[:,:k];present=np.take_along_axis(y,ix,axis=1);nhay=np.take_along_axis(counts,ix,axis=1)
        result[str(k)]={'any_hit':float(np.mean(np.any(present,axis=1))),
            'distinct_per_day':float(np.mean(present.sum(axis=1))),'occurrences_per_day':float(np.mean(nhay.sum(axis=1)))}
    u=y.sum(axis=1).astype(int);result['random_expected']={}
    for k in (1,3,5):result['random_expected'][str(k)]={'any_hit':float(np.mean([1-math.comb(100-int(v),k)/math.comb(100,k) for v in u])),
        'distinct_per_day':float(np.mean(k*u/100)),'occurrences_per_day':k*27/100}
    return result
def calibration(p,y):
    bins=[]
    for lo,hi in zip([0,.1,.2,.25,.3,.4,.6],[.1,.2,.25,.3,.4,.6,1.000001]):
        mask=(p>=lo)&(p<hi)
        if mask.any():bins.append({'lo':lo,'hi':min(hi,1),'n':int(mask.sum()),'predicted':float(p[mask].mean()),'observed':float(y[mask].mean())})
    return bins
def bootstrap(delta,seed,reps=2000,block=14):
    rng=np.random.default_rng(seed);n=len(delta);means=np.empty(reps)
    for b in range(reps):
        starts=rng.integers(0,n,size=math.ceil(n/block));ix=((starts[:,None]+np.arange(block))%n).ravel()[:n]
        means[b]=delta[ix].mean()
    return {'mean_delta':float(delta.mean()),'ci95':list(map(float,np.quantile(means,[.025,.975]))),
        'p_centered_bootstrap':float((1+np.sum(np.abs(means-delta.mean())>=abs(delta.mean())))/(reps+1)),
        'method':'paired circular moving-block bootstrap over draw days; interval descriptive after selection, not prospective confirmation'}

def holm_adjust(pvalues):
    ordered=sorted(pvalues,key=pvalues.get);out={};running=0
    for i,key in enumerate(ordered):
        running=max(running,min(1,(len(ordered)-i)*pvalues[key]));out[key]=running
    return out

def run(csv_path,protocol_path,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    if (out/'FREEZE.json').exists():raise ValueError('Run already exists: never overwrite')
    cfg=json.loads(Path(protocol_path).read_text());expressions=grammar()
    freeze={'utc':datetime.now(timezone.utc).isoformat(),'protocol':cfg,'grammar':expressions,
            'source_sha256':digest(Path(__file__).read_bytes()),'numpy':np.__version__,'python':platform.python_version()}
    (out/'FREEZE.json').write_bytes(encoded(freeze));freeze_sha=digest(encoded(freeze))
    dates,tails=load(csv_path,cfg['data_sha256']);y,counts,base,baselines=features(tails,cfg['prior_draws'])
    valid=np.arange(len(y))>=cfg['warmup_draws'];train=valid&(dates<=cfg['training_end'])
    selection=valid&(dates>cfg['training_end'])&(dates<=cfg['selection_end']);test=valid&(dates>=cfg['evaluation_start'])
    if min(train.sum(),selection.sum(),test.sum())<100:raise ValueError('Insufficient chronological split')
    previous=None;candidates=[];best=None
    for expr,ridge in itertools.product(expressions,cfg['ridge_penalties']):
        if len(candidates)>=cfg['max_candidates']:raise ValueError('Candidate budget exceeded')
        cid='APDE-'+str(len(candidates)+1).zfill(3);start=time.perf_counter()
        event={'id':cid,'expression':expr,'ridge':ridge,'freeze_sha256':freeze_sha}
        try:
            x=evaluate(expr,base);f=fit(x,y,train,ridge);p=predict(x[selection],f);score=float(daily_brier(p,y[selection]).mean())
            event.update(status='OK',fit=f,selection_brier=score)
            if best is None or score<best['selection_brier']:best=dict(event)
        except Exception as error:event.update(status='ERROR',error=str(error))
        event['seconds']=time.perf_counter()-start;candidates.append(event)
        payload={'previous':previous,'event':event};record={'payload':payload,'sha256':digest(encoded(payload))};previous=record['sha256']
        with (out/'candidate_ledger.jsonl').open('ab') as f:f.write(encoded(record)+b'\n')
    if best is None:raise ValueError('No valid candidate')
    (out/'SELECTED_BEFORE_EVALUATION.json').write_bytes(encoded(best))
    predictions={name:p[test] for name,p in baselines.items()}
    predictions[best['id']]=predict(evaluate(best['expression'],base)[test],best['fit'])
    yy=y[test];cc=counts[test];results={};daily={}
    for name,p in predictions.items():
        loss=daily_brier(p,yy);daily[name]=loss
        annual={year:float(loss[np.char.startswith(dates[test],year)].mean()) for year in sorted(set(d[:4] for d in dates[test]))}
        results[name]={'brier':float(loss.mean()),'log_loss':float(np.mean(-yy*np.log(p)-(1-yy)*np.log(1-p))),
            'topk':top_metrics(p,yy,cc),'calibration':calibration(p,yy),'brier_by_year':annual}
    comparison={name:bootstrap(daily[name]-daily['uniform'],cfg['seed'],cfg['bootstrap_repetitions'],cfg['bootstrap_block_draws']) for name in daily if name!='uniform'}
    selected_comparisons={name:bootstrap(daily[best['id']]-daily[name],cfg['seed'],cfg['bootstrap_repetitions'],cfg['bootstrap_block_draws']) for name in ('uniform','history','window90')}
    family={**{'uniform:'+k:v for k,v in comparison.items()},**{'selected:'+k:v for k,v in selected_comparisons.items()}}
    adjusted=holm_adjust({k:v['p_centered_bootstrap'] for k,v in family.items()})
    for key,value in family.items():value['holm_adjusted_p_9_comparisons']=adjusted[key]
    report={'freeze_sha256':freeze_sha,'data_sha256':cfg['data_sha256'],'rows':len(dates),'first':str(dates[0]),'last':str(dates[-1]),
        'split_counts':{'train':int(train.sum()),'selection':int(selection.sum()),'evaluation':int(test.sum())},
        'candidate_count':len(candidates),'selected':best,'results':results,'vs_uniform':comparison,'selected_vs_baselines':selected_comparisons,
        'evidence_status':'EXPLORATORY_ONLY; no global multiple-testing claim; selected only on selection period; no prospective forecast',
        'conclusion':'Chưa tìm thấy lợi thế dự đoán đáng tin cậy'}
    (out/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    np.savez_compressed(out/'retrospective_predictions.npz',dates=dates[test],presence=yy,counts=cc,**predictions)
    with (out/'model_comparison.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.writer(f);w.writerow(['method','brier','log_loss','top1_any','top3_any','top5_any'])
        for name,r in results.items():w.writerow([name,r['brier'],r['log_loss']]+[r['topk'][str(k)]['any_hit'] for k in (1,3,5)])
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--csv',required=True);p.add_argument('--protocol',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    r=run(a.csv,a.protocol,a.out);print(json.dumps({k:r[k] for k in ['rows','split_counts','candidate_count','selected','conclusion']},ensure_ascii=False))
