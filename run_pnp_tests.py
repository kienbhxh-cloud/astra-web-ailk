"""Run only the new PNP/exact suite, standalone or inside the ASTRA repo."""
import argparse,json,platform,sys,time,unittest
from pathlib import Path

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--report-dir');args=parser.parse_args()
    root=Path(__file__).resolve().parent
    tests=root/'tests' if (root/'tests/test_pnp_foundations.py').is_file() else root/'astra_math/tests'
    suite=unittest.TestSuite()
    for name in ('test_xsmb_exact.py','test_pnp_foundations.py','test_pnp_prototypes.py','test_pnp_integration.py'):
        if not (tests/name).is_file():raise FileNotFoundError(tests/name)
        suite.addTests(unittest.defaultTestLoader.discover(str(tests),pattern=name))
    start=time.perf_counter();result=unittest.TextTestRunner(verbosity=2).run(suite)
    report={'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),
            'passed':result.wasSuccessful(),'elapsed_seconds':time.perf_counter()-start,'python':platform.python_version(),
            'scope':'new exact, foundations, prototype and integration suite; no empirical historical optimization'}
    if args.report_dir:
        out=Path(args.report_dir);out.mkdir(parents=True,exist_ok=True);(out/'tests.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report));return 0 if result.wasSuccessful() else 1

if __name__=='__main__':sys.exit(main())
