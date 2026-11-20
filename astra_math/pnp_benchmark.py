"""READ-007 synthetic solver benchmark; no historical lottery input."""
import argparse,hashlib,itertools,json,platform,random,time
from pathlib import Path
from .pnp_prototypes import maximize_set_coverage

CONFIG={'version':'READ007-1','seeds':[11,29,47,83],'regimes':['uniform','planted'],
        'universe':list(range(16)),'k':5,'train_days':60,'test_days':120,
        'draw_size':27,'alphabet':100,'random_candidates':500,'solver_timeout_ms':2000}

def mask(row):return sum(1<<x for x in set(row))
def coverage(selected,rows):
    chosen=mask(selected)
    return sum(bool(chosen&r) for r in rows)
def exact_optimum(rows,universe,k):
    return max((coverage(c,rows),-sum(1<<x for x in c),c) for c in itertools.combinations(universe,k))
def metrics(selected,draws):
    ss=set(selected)
    return {'days':len(draws),'any_hit_rate':sum(bool(ss&set(d)) for d in draws)/len(draws),
            'distinct_hits_per_day':sum(len(ss&set(d)) for d in draws)/len(draws),
            'occurrences_per_day':sum(sum(x in ss for x in d) for d in draws)/len(draws)}
def make_draws(seed,regime,n):
    rng=random.Random(seed)
    weights=[2 if regime=='planted' and x<5 else 1 for x in range(100)]
    return [rng.choices(range(100),weights=weights,k=27) for _ in range(n)]

def run(config=None):
    cfg=dict(CONFIG if config is None else config);results=[]
    for regime in cfg['regimes']:
        for seed in cfg['seeds']:
            draws=make_draws(seed,regime,cfg['train_days']+cfg['test_days'])
            training=draws[:cfg['train_days']];testing=draws[cfg['train_days']:]
            scenarios=[sorted(set(d)&set(cfg['universe'])) for d in training]
            rows=[mask(d) for d in scenarios]
            start=time.perf_counter();exact=exact_optimum(rows,cfg['universe'],cfg['k']);ex_time=time.perf_counter()-start
            start=time.perf_counter();solver=maximize_set_coverage(scenarios,cfg['universe'],k=cfg['k'],timeout_ms=cfg['solver_timeout_ms']);solver_wall=time.perf_counter()-start
            rng=random.Random(seed+100000)
            start=time.perf_counter();candidates=[tuple(sorted(rng.sample(cfg['universe'],cfg['k']))) for _ in range(cfg['random_candidates'])]
            best=max(candidates,key=lambda c:(coverage(c,rows),-mask(c)));random_wall=time.perf_counter()-start
            picks={'solver':solver['selected_labels'],'random_single':candidates[0],'random_search500':best}
            selected=solver['selected_labels'];verified=selected is not None and coverage(selected,rows)==exact[0] and tuple(selected)==exact[2]
            results.append({'regime':regime,'seed':seed,'solver_status':solver['status'],'solver_optimal_flag':solver['optimal'],
                'exhaustive_agreement':verified,'training_optimum':exact[0],'exhaustive_candidates':4368,
                'solver_wall_seconds':solver_wall,'exhaustive_wall_seconds':ex_time,'random_search_wall_seconds':random_wall,
                'solver_detail':solver,'methods':{name:{'selected':pick,'train_coverage':coverage(pick,rows),
                    'test':metrics(pick,testing)} for name,pick in picks.items() if pick is not None}})
    return {'config':cfg,'config_sha256':hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest(),
            'python':platform.python_version(),'results':results,
            'scope':'synthetic only; exhaustive verification of finite instances, not DRAT/LRAT proof; no P=NP or predictive claim',
            'budget_note':'random search evaluates 500 subsets; Z3 internal search budget is timeout, not matched candidate count; no equal-compute superiority claim'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args()
    result=run();out=Path(a.out);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({'instances':len(result['results']),'exact_agreements':sum(r['exhaustive_agreement'] for r in result['results']),
                      'out':str(out)}))
if __name__=='__main__':main()
