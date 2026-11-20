import csv,json,tempfile,unittest
from datetime import date,timedelta
from pathlib import Path
from astra_math.pnp_foundations import Draw,FeatureStore,mutation_check,CandidateLedger,ForecastLog,load_csv

def synthetic(n=12):return tuple(Draw(date(2025,1,1)+timedelta(days=i),tuple((i+j)%100 for j in range(27))) for i in range(n))

class FeaturesTests(unittest.TestCase):
    def test_strict_cutoff_and_replay(self):
        rows=synthetic();target=date(2025,1,8);f=FeatureStore(rows).features(target)
        self.assertEqual(f.history_draws,7);self.assertEqual(f.cutoff,date(2025,1,7))
        self.assertEqual(f,FeatureStore(rows).features(target));self.assertEqual(sum(f.last_counts),27)
    def test_suffix_mutation(self):
        def predict(rows,t):
            f=FeatureStore(rows).features(t)
            return {'prefix':f.prefix_sha256,'p':f.presence_probabilities}
        self.assertTrue(mutation_check(predict,synthetic(),date(2025,1,8))['passed'])
    def test_deliberate_leak_detected(self):
        def leak(rows,t):return list(next(d for d in rows if d.day==t).tails)
        self.assertFalse(mutation_check(leak,synthetic(),date(2025,1,8))['passed'])
    def test_empty_history_has_prior(self):
        f=FeatureStore(synthetic()).features(date(2024,12,31))
        self.assertEqual(f.history_draws,0);self.assertIsNone(f.cutoff)
        self.assertAlmostEqual(f.presence_probabilities[0][0],1-.99**27)
    def test_immutable_and_ordered(self):
        with self.assertRaises(ValueError):FeatureStore(reversed(synthetic()))
        with self.assertRaises(ValueError):Draw(date.today(),(0,)*26)
    def test_csv_rejects_duplicate_and_bad_hash(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'a.csv'
            with p.open('w',newline='') as f:
                w=csv.writer(f);w.writerow(['date','special']+list(map(str,range(26))))
                for _ in range(2):w.writerow(['2025-01-01']+list(range(27)))
            with self.assertRaises(ValueError):load_csv(p)
            with self.assertRaises(ValueError):load_csv(p,'a'*64)

class LogsTests(unittest.TestCase):
    def test_budget_counts_errors_and_cannot_be_expanded(self):
        with tempfile.TemporaryDirectory() as d:
            log=CandidateLedger(Path(d)/'l.jsonl',per_family_limit=1,total_limit=2)
            log.append_candidate('failed','F1',{},'ERROR')
            with self.assertRaises(ValueError):log.append_candidate('retry','F1',{},'SAT')
            log.append_candidate('other','F2',{},'SAT')
            with self.assertRaises(ValueError):log.append_candidate('third','F3',{},'SAT')
            with self.assertRaises(ValueError):CandidateLedger(Path(d)/'bad',per_family_limit=501)
    def test_ledger_detects_tampering_and_unsupported_wp(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'l.jsonl';log=CandidateLedger(p)
            log.append_candidate('one','F1',{'depth':1},'SAT')
            with self.assertRaises(ValueError):log.append_candidate('one','F1',{},'SAT')
            with self.assertRaises(ValueError):log.append_candidate('two','WP2',{},'SAT')
            with self.assertRaises(ValueError):log.append_candidate('two','F1',{},'SAT',mode='historical')
            r=json.loads(p.read_text());r['payload']['event']['status']='UNSAT';p.write_text(json.dumps(r)+'\n')
            with self.assertRaises(ValueError):log.read()
    def test_forecast_is_synthetic_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            log=ForecastLog(Path(d)/'forecasts.jsonl')
            r={'mode':'synthetic','target_date':'2025-01-02','method_id':'baseline','presence_probabilities':[.237]*100,'code_sha256':'a'*64,'source_prefix_sha256':'b'*64}
            log.append_forecast(r)
            with self.assertRaises(ValueError):log.append_forecast(r)
            with self.assertRaises(ValueError):log.append_forecast({**r,'mode':'prospective'})

if __name__=='__main__':unittest.main()
