"""Past-only data views and append-only research logs; no solver/data mining here.

Local hash chains detect edits against a retained head. They do not authenticate
time, prevent full-chain replacement, or sandbox malicious strategy code.
"""
from __future__ import annotations
import csv
from dataclasses import dataclass,replace
from datetime import date,datetime,timezone
import hashlib,json,math,os,random
from pathlib import Path

def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')
def sha(value):return hashlib.sha256(canonical(value)).hexdigest()

@dataclass(frozen=True)
class Draw:
    day: date
    tails: tuple[int,...]
    def __post_init__(self):
        if not isinstance(self.day,date) or isinstance(self.day,datetime):raise ValueError('day must be date')
        if not isinstance(self.tails,tuple) or len(self.tails)!=27:raise ValueError('Immutable27 tails required')
        if any(isinstance(x,bool) or not isinstance(x,int) or not 0<=x<100 for x in self.tails):raise ValueError('Invalid tails')

def load_csv(path,expected_sha256=None):
    path=Path(path);raw=path.read_bytes()
    if expected_sha256 and hashlib.sha256(raw).hexdigest()!=expected_sha256:raise ValueError('CSV hash mismatch')
    rows=list(csv.reader(raw.decode('utf-8-sig').splitlines()))
    if not rows or len(rows[0])!=28 or rows[0][:2]!=['date','special']:raise ValueError('Expected canonical28 columns')
    out=[]
    for row in rows[1:]:
        if len(row)!=28 or any(not v.isascii() or not v.isdigit() for v in row[1:]):raise ValueError('Invalid prize row')
        out.append(Draw(date.fromisoformat(row[0]),tuple(int(v)%100 for v in row[1:])))
    if not out:raise ValueError('No observations')
    if len({d.day for d in out})!=len(out):raise ValueError('Duplicate dates')
    if out!=sorted(out,key=lambda d:d.day):raise ValueError('Unsorted observations')
    return tuple(out)

@dataclass(frozen=True)
class PastFeatures:
    target: date
    cutoff: date|None
    history_draws: int
    prefix_sha256: str
    last_counts: tuple[int,...]
    presence_probabilities: tuple[tuple[float,...],...]
    windows: tuple[int,...]
    gap_calendar_days: tuple[int|None,...]
    gap_draws: tuple[int|None,...]

class FeatureStore:
    def __init__(self,draws):
        self._draws=tuple(draws)
        if any(not isinstance(d,Draw) for d in self._draws):raise ValueError('Expected immutable draws')
        days=[d.day for d in self._draws]
        if days!=sorted(set(days)):raise ValueError('Dates must be strictly ordered')
    def before(self,target):return tuple(d for d in self._draws if d.day<target)
    def features(self,target,windows=(7,30,90),prior=100):
        if not isinstance(target,date) or isinstance(target,datetime):raise ValueError('Expected target date')
        if not windows or any(isinstance(w,bool) or not isinstance(w,int) or w<=0 for w in windows):raise ValueError('Positive windows required')
        if not math.isfinite(prior) or prior<=0:raise ValueError('Positive finite prior')
        past=self.before(target);p0=1-.99**27
        probs=[]
        for w in windows:
            subset=past[-w:];counts=[0]*100
            for d in subset:
                for x in set(d.tails):counts[x]+=1
            probs.append(tuple((count+prior*p0)/(len(subset)+prior) for count in counts))
        last=[0]*100
        if past:
            for x in past[-1].tails:last[x]+=1
        most_recent={}
        for d in past:
            for x in d.tails:most_recent[x]=d.day
        gaps=tuple((target-most_recent[x]).days if x in most_recent else None for x in range(100))
        prefix=[{'date':d.day.isoformat(),'tails':list(d.tails)} for d in past]
        last_index={x:i for i,d in enumerate(past) for x in d.tails}
        draw_gaps=tuple(len(past)-last_index[x] if x in last_index else None for x in range(100))
        return PastFeatures(target,past[-1].day if past else None,len(past),sha(prefix),tuple(last),tuple(probs),tuple(windows),gaps,draw_gaps)

def mutation_check(predict,draws,target,seeds=(1,2,3)):
    """Diagnostic on valid suffix mutations, not a formal noninterference proof."""
    original=canonical(predict(tuple(draws),target));checks=[]
    for name,subset in [('strict_past',tuple(d for d in draws if d.day<target)),
                        ('through_target',tuple(d for d in draws if d.day<=target))]:
        try:same=canonical(predict(subset,target))==original
        except Exception:same=False
        checks.append({'variant':name,'invariant':same})
    for seed in seeds:
        rng=random.Random(seed)
        altered=tuple(replace(d,tails=tuple(rng.randrange(100) for _ in range(27))) if d.day>=target else d for d in draws)
        same=canonical(predict(altered,target))==original
        checks.append({'seed':seed,'invariant':same})
    return {'passed':all(x['invariant'] for x in checks),'checks':checks,'proof_kind':'mutation_test_only'}

class HashLog:
    def __init__(self,path):self.path=Path(path)
    def read(self):
        if not self.path.exists():return []
        rows=[];previous=None
        for index,line in enumerate(self.path.read_text(encoding='utf-8').splitlines(),1):
            row=json.loads(line);payload=row['payload']
            if payload.get('sequence')!=index or payload.get('previous')!=previous or sha(payload)!=row.get('sha256'):raise ValueError('Log integrity mismatch')
            rows.append(row);previous=row['sha256']
        return rows
    def append(self,event,validator=None):
        self.path.parent.mkdir(parents=True,exist_ok=True);lock=self.path.with_name(self.path.name+'.lock')
        with lock.open('x') as f:f.write('exclusive local append')
        try:
            rows=self.read()
            if validator:validator(rows)
            payload={'sequence':len(rows)+1,'previous':rows[-1]['sha256'] if rows else None,
                'recorded_at_utc':datetime.now(timezone.utc).isoformat(),'event':event}
            record={'payload':payload,'sha256':sha(payload)}
            with self.path.open('ab') as f:f.write(canonical(record)+b'\n');f.flush();os.fsync(f.fileno())
            return record
        finally:lock.unlink()

class CandidateLedger(HashLog):
    def __init__(self,path,per_family_limit=500,total_limit=1500):
        super().__init__(path)
        if isinstance(per_family_limit,bool) or not isinstance(per_family_limit,int) or not 1<=per_family_limit<=500:raise ValueError('Family budget must be1..500')
        if isinstance(total_limit,bool) or not isinstance(total_limit,int) or not 1<=total_limit<=1500:raise ValueError('Total budget must be1..1500')
        self.per_family_limit=per_family_limit;self.total_limit=total_limit
    def append_candidate(self,candidate_id,family,config,status,mode='synthetic'):
        if family not in ('F1','F2','F3'):raise ValueError('Only approved F1/F2/F3; WP2 needs its own protocol')
        if mode!='synthetic':raise ValueError('Starter ledger allows synthetic work only; historical protocol not frozen')
        if not candidate_id or status not in ('OPTIMAL','SAT','UNSAT','FEASIBLE','UNKNOWN','TIMEOUT','ERROR'):raise ValueError('Candidate/status required')
        def check(rows):
            events=[r['payload']['event'] for r in rows]
            if any(e.get('candidate_id')==candidate_id for e in events):raise ValueError('Duplicate candidate id')
            if len(events)>=self.total_limit or sum(e.get('family')==family for e in events)>=self.per_family_limit:raise ValueError('Budget exhausted')
        return self.append({'kind':'candidate','candidate_id':candidate_id,'family':family,'config':config,'status':status,'mode':mode},check)

class ForecastLog(HashLog):
    def append_forecast(self,record):
        if record.get('mode')!='synthetic':raise ValueError('Starter does not issue prospective forecasts')
        day=date.fromisoformat(record['target_date']);method=record['method_id']
        if not method:raise ValueError('Empty method')
        p=record['presence_probabilities']
        if len(p)!=100 or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or not 0<=v<=1 for v in p):raise ValueError('100 finite marginal probabilities required')
        for key in ('code_sha256','source_prefix_sha256'):
            h=record[key]
            if len(h)!=64 or any(ch not in '0123456789abcdef' for ch in h):raise ValueError('Invalid SHA256')
        def check(rows):
            if any(r['payload']['event'].get('target_date')==day.isoformat() and r['payload']['event'].get('method_id')==method for r in rows):raise ValueError('Duplicate method/date snapshot')
        return self.append({**record,'kind':'forecast'},check)
