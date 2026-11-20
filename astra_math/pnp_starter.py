"""Synthetic smoke runner and read-only locked-CSV compatibility checks."""
import argparse,hashlib,json,platform,time,tracemalloc
from dataclasses import asdict
from datetime import date,timedelta
from pathlib import Path
from . import xsmb_exact as exact
from .pnp_foundations import Draw,FeatureStore,mutation_check,CandidateLedger,ForecastLog
from .pnp_prototypes import select_rules_maxsat,synthesize_affine_modular,maximize_set_coverage
from .pnp_integration import validate_snapshot

def dump(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2,default=str,allow_nan=False),encoding='utf-8')

def demo(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    ledger=CandidateLedger(out/'candidate_ledger.jsonl');bench={}
    cases=[('F1',lambda:select_rules_maxsat({'planted':[0,1,0,1],'opposite':[1,0,1,0]},[0,1,0,1],max_rules=1)),
           ('F2',lambda:synthesize_affine_modular([(0,1),(1,3),(2,5),(3,0)],modulus=7)),
           ('F3',lambda:maximize_set_coverage([[0,1],[1,2],[3],[2,4]],list(range(5)),k=2))]
    for family,call in cases:
        tracemalloc.start();start=time.perf_counter();result=call();elapsed=time.perf_counter()-start
        peak=tracemalloc.get_traced_memory()[1];tracemalloc.stop()
        bench[family]={'solver':result,'wall_seconds':elapsed,'python_tracemalloc_peak_bytes':peak,'memory_limit':'Does not include all native Z3 memory'}
        ledger.append_candidate('synthetic-smoke-'+family,family,{'fixture':'built-in planted toy','discovery':False},result['status'].upper())
    history=tuple(Draw(date(2025,1,1)+timedelta(days=i),tuple((i+j)%100 for j in range(27))) for i in range(12))
    target=date(2025,1,8)
    def predict(rows,t):
        f=FeatureStore(rows).features(t)
        return {'source_prefix_sha256':f.prefix_sha256,'presence_probabilities':f.presence_probabilities[-1]}
    invariant=mutation_check(predict,history,target)
    prediction=predict(history,target)
    ForecastLog(out/'synthetic_forecasts.jsonl').append_forecast({'mode':'synthetic','target_date':target.isoformat(),'method_id':'past-only-frequency-demo',**prediction,'code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    report={'status':'SYNTHETIC_ENGINEERING_ONLY','historical_search_executed':False,'prospective_started':False,
            'python':platform.python_version(),'benchmark':bench,'leakage_diagnostic':invariant,
            'exact_reference':{'presence':str(exact.p_presence()),'xien2':str(exact.p_all_distinct(2)),
              'xien3':str(exact.p_all_distinct(3)),'random5_given24_unique':str(exact.random_k_anyhit(24,5))},
            'ledger_entries':len(ledger.read()),'notes':['No forecast or significance claim from these fixtures','F2 implements only bounded affine-modular feasibility, not full depth3 program grammar']}
    dump(out/'synthetic_report.json',report)
    return report

def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('demo');p.add_argument('--out',required=True)
    p=sub.add_parser('validate-csv');p.add_argument('csv');p.add_argument('--sha256',required=True);p.add_argument('--out',required=True)
    args=parser.parse_args()
    if args.command=='demo':r=demo(args.out)
    else:
        r=validate_snapshot(args.csv,args.sha256);out=Path(args.out);out.mkdir(parents=True,exist_ok=False);dump(out/'integration_report.json',r)
    print(json.dumps(r,ensure_ascii=False,indent=2,default=str))

if __name__=='__main__':main()
