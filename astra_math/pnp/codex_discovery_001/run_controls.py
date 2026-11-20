"""Frozen small stress suite, not a 1000-replicate null calibration."""
import json,time
from pathlib import Path
import numpy as np
from engine import features,grammar,evaluate,fit,predict,daily_brier,P0,encoded,digest

CONFIG={'seeds':[101,211,307,401,503,601],'regimes':{'null':0,'copy14':14},'train':180,'selection':120,'evaluation':180,'ridge':[1.,10.]}
def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    if (out/'FREEZE.json').exists():raise ValueError('Controls already run')
    (out/'FREEZE.json').write_bytes(encoded({'config':CONFIG,'source_sha256':digest(Path(__file__).read_bytes())}))
    results=[]
    for regime,copy_count in CONFIG['regimes'].items():
        for seed in CONFIG['seeds']:
            rng=np.random.default_rng(seed);n=sum(CONFIG[k] for k in ('train','selection','evaluation'));tails=rng.integers(0,100,size=(n,27))
            if copy_count:
                for t in range(1,n):tails[t,:copy_count]=rng.choice(tails[t-1],size=copy_count,replace=True)
            y,c,b,baseline=features(tails);idx=np.arange(n);train=(idx>=90)&(idx<180);sel=(idx>=180)&(idx<300);test=idx>=300
            best=None;ledger=[]
            for i,(expr,ridge) in enumerate((e,r) for e in grammar() for r in CONFIG['ridge']):
                x=evaluate(expr,b);f=fit(x,y,train,ridge);score=float(daily_brier(predict(x[sel],f),y[sel]).mean())
                ledger.append({'candidate':i+1,'selection_brier':score,'fit':f})
                if best is None or score<best[0]:best=(score,expr,ridge,f)
            pred=predict(evaluate(best[1],b)[test],best[3]);delta=float((daily_brier(pred,y[test])-daily_brier(baseline['uniform'][test],y[test])).mean())
            results.append({'regime':regime,'seed':seed,'copy_count':copy_count,'selected_expression':best[1],'ridge':best[2],
                'evaluation_delta_brier_vs_uniform':delta,'all_30_training_selection_fits':ledger})
    report={'config':CONFIG,'results':results,'candidate_evaluations':len(results)*30,'scope':'12 stress runs, not a reliable type-I error estimate or mandatory F1 1000-null calibration'}
    (out/'results.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({'candidate_evaluations':report['candidate_evaluations'],'deltas':[{k:r[k] for k in ('regime','seed','evaluation_delta_brier_vs_uniform')} for r in results]}))
if __name__=='__main__':run(Path(__file__).parent/'04_CONTROLS')
