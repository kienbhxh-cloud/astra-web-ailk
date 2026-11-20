import hashlib,tempfile,unittest
from pathlib import Path
import numpy as np
from engine import features,evaluate,grammar,fit,predict,top_metrics,holm_adjust,load,P0

class EngineTests(unittest.TestCase):
    def test_future_mutation_and_truncation(self):
        rng=np.random.default_rng(7);tails=rng.integers(0,100,size=(60,27));target=40
        original=features(tails);modified=tails.copy();modified[target:]=rng.integers(0,100,size=(20,27))
        other=features(modified);prefix=features(tails[:target+1])
        for expr in grammar():
            np.testing.assert_equal(evaluate(expr,original[2])[:target+1],evaluate(expr,other[2])[:target+1])
            np.testing.assert_equal(evaluate(expr,original[2])[:target+1],evaluate(expr,prefix[2]))
    def test_target_not_used(self):
        tails=np.zeros((5,27),dtype=int);tails[3]=99
        y,c,b,baseline=features(tails)
        self.assertEqual(b['last'][3,99],0);self.assertEqual(b['last'][4,99],1)
        self.assertAlmostEqual(baseline['uniform'][0,0],P0)
    def test_invalid_ast(self):
        for expr in ({'op':'exec','args':[]},{'atom':'unknown'},{'atom':'last','extra':1}):
            with self.assertRaises(ValueError):evaluate(expr,{'last':np.ones((2,100))})
    def test_training_only_scaler(self):
        x=np.arange(200).reshape(2,100).astype(float);y=np.zeros_like(x);mask=np.array([True,False])
        a=fit(x,y,mask,1);x[1]=1e8;y[1]=1;b=fit(x,y,mask,1)
        self.assertEqual(a,b);self.assertTrue(np.isfinite(predict(x,a)).all())
    def test_topk_multiplicity(self):
        p=np.zeros((1,100));p[0,5]=1;y=np.zeros_like(p);y[0,5]=1;counts=y*3
        r=top_metrics(p,y,counts)['1'];self.assertEqual(r,{'any_hit':1.,'distinct_per_day':1.,'occurrences_per_day':3.})
    def test_holm(self):
        self.assertEqual(holm_adjust({'a':.01,'b':.04,'c':.2}),{'a':.03,'b':.08,'c':.2})
    def test_loader_duplicates_and_hash(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'bad.csv';row=','.join(['00000']*10+['0000']*10+['000']*3+['00']*4)
            p.write_text('date,'+','.join(map(str,range(27)))+'\n2020-01-01,'+row+'\n2020-01-02,'+row+'\n')
            with self.assertRaises(ValueError):load(p,hashlib.sha256(p.read_bytes()).hexdigest())
            with self.assertRaises(ValueError):load(p,'a'*64)
if __name__=='__main__':unittest.main(verbosity=2)
