import math,tempfile,unittest
from pathlib import Path
from datetime import date
from astra_math.pnp_foundations import Draw,FeatureStore,mutation_check,ForecastLog
from astra_math.pnp_sequential import *

class SequentialTests(unittest.TestCase):
    def test_length_leak(self):
        ds=tuple(Draw(date(2025,1,i),(0,)*27) for i in range(1,5))
        self.assertFalse(mutation_check(lambda rows,t:len(rows),ds,date(2025,1,3))['passed'])
    def test_endpoint_leak(self):
        ds=tuple(Draw(date(2025,1,i),(0,)*27) for i in range(1,5))
        self.assertFalse(mutation_check(lambda rows,t:rows[-1].day.isoformat(),ds,date(2025,1,3))['passed'])
    def test_draw_gap_holiday(self):
        ds=(Draw(date(2020,3,31),(0,)*27),Draw(date(2020,4,23),(1,)*27))
        f=FeatureStore(ds).features(date(2020,4,24))
        self.assertEqual(f.gap_draws[:3],(2,1,None))
        self.assertEqual(f.gap_calendar_days[:2],(24,1))
    def test_exact_mixture(self):
        ys=[0,2,1,4]
        expected=sum(math.prod(1+l*(y-1.35) for y in ys) for l in MEAN_LAMBDAS)/5
        self.assertAlmostEqual(eprocess_mean(ys)['wealth'],expected)
        self.assertEqual(eprocess_mean([])['wealth'],1)
    def test_null_one_step_expectation(self):
        # Exact binomial null expectation, no Monte Carlo false-positive claim.
        for l in MEAN_LAMBDAS:
            ew=sum(math.comb(27,y)*.05**y*.95**(27-y)*(1+l*(y-1.35)) for y in range(28))
            self.assertAlmostEqual(ew,1)
    def test_secondary(self):
        for u in (1,15,27):
            p=float(p_set_any_given_u(u))
            for l in HIT_LAMBDAS:
                self.assertAlmostEqual(p*(1+l*(1-p)/p)+(1-p)*(1-l),1)
        self.assertEqual(eprocess_any_hit([0],[0])['wealth'],1)
    def test_extreme_and_invalid(self):
        self.assertIsNone(eprocess_mean([27]*2000)['wealth'])
        self.assertTrue(math.isfinite(eprocess_mean([27]*2000)['log_wealth']))
        for bad in ([-1],[28],[True],[1.5]):
            with self.assertRaises(ValueError):eprocess_mean(bad)
        with self.assertRaises(ValueError):eprocess_any_hit([1],[0])
    def test_linked_score_and_rejections(self):
        with tempfile.TemporaryDirectory() as d:
            forecasts=ForecastLog(Path(d)/'f.jsonl');scores=SyntheticScoreLog(Path(d)/'s.jsonl')
            record={'mode':'synthetic','target_date':'2025-01-02','method_id':'F3','selected_numbers':[0,1,2,3,4],
                'presence_probabilities':[.237]*100,'code_sha256':'a'*64,'source_prefix_sha256':'b'*64}
            forecast=forecasts.append_forecast(record)
            result=scores.score(forecasts,'F3',Draw(date(2025,1,2),(0,)*27))['payload']['event']
            self.assertEqual(result['forecast_sha256'],forecast['sha256'])
            self.assertEqual(result['simulation_net'],400000*27-562500)
            with self.assertRaises(ValueError):scores.score(forecasts,'F3',Draw(date(2025,1,2),(0,)*27))
            self.assertEqual(len(scores.read()),1)

    def test_saved_path_matches_canonical_and_ever_crossing(self):
        from astra_math import xsmb_audit as audit
        from datetime import timedelta
        ys=[27]*5+[0]*100
        canonical=audit.eprocess_mean(ys,mu=1.35)
        hitpath=audit.eprocess_any_hit([int(y>0) for y in ys],[float(p_set_any_given_u(1))]*len(ys))
        with tempfile.TemporaryDirectory() as d:
            forecasts=ForecastLog(Path(d)/'f');scores=SyntheticScoreLog(Path(d)/'s')
            for i,y in enumerate(ys):
                day=date(2025,1,1)+timedelta(days=i)
                forecasts.append_forecast({'mode':'synthetic','target_date':day.isoformat(),'method_id':'F3',
                    'selected_numbers':[0,1,2,3,4],'presence_probabilities':[.237]*100,
                    'code_sha256':'a'*64,'source_prefix_sha256':'b'*64})
                event=scores.score(forecasts,'F3',Draw(day,((0 if y else 99),)*27))['payload']['event']
                self.assertAlmostEqual(event['primary']['log_wealth'],math.log(canonical[i]),delta=1e-12)
                self.assertAlmostEqual(event['secondary_descriptive']['log_wealth'],math.log(hitpath[i]),delta=1e-12)
            events=[r['payload']['event'] for r in scores.read()]
            self.assertTrue(any(e['primary_crossed'] for e in events))
            self.assertFalse(events[-1]['primary_crossed'])
            self.assertEqual(len(events),len(ys))

if __name__=='__main__':unittest.main()
