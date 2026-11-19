# Codex PNP starter — MASTER-005

20/11/2026. Initial engineering delivery, not completion of WP0–WP6 or a validated
lottery predictor. The data and historical hypotheses remain exploratory.

## Implemented

- `astra_math/xsmb_exact.py`: Fraction probabilities for presence, joint presence,
  occurrence counts, selected occupancy, conditional random-k baseline and EV.
- `astra_math/pnp_prototypes.py`: real Z3 MaxSAT finite OR-rule selection, bounded
  affine-modular SMT feasibility, and fixed-k weighted empirical coverage.
- `astra_math/pnp_foundations.py`: immutable draws, past-only views/features,
  suffix mutation diagnostic, budgeted synthetic candidate ledger and forecast log.
- `astra_math/pnp_integration.py`: exact probability agreement with the upstream
  `xsmb_audit.py` and two-loader agreement on a SHA-locked CSV. No empirical test
  or model search is performed by this compatibility check.
- `astra_math/pnp_starter.py`: runnable synthetic smoke fixtures with resource
  measurement and three ledger entries. Output directories cannot be overwritten.

The upstream `xsmb_audit.py` is included unmodified in the portable ZIP. It already
exists on the target ASTRA branch and is not part of the proposed source changes.

## Run from this directory

Python >=3.10. Exact probabilities and foundations use only the standard library;
solver examples require the dependency below. This installation is not needed to
import `xsmb_exact` alone.

```powershell
python -m pip install -r requirements-pnp.txt
python run_pnp_tests.py --report-dir fresh_test_report
python -m astra_math.pnp_starter demo --out fresh_synthetic_run
```

Read-only compatibility with the delivered historical snapshot:

```powershell
python -m astra_math.pnp_starter validate-csv PATH_TO_CLEAN_CSV --sha256 07e110accc140cb6b34b26fd30e833f1240316ea9314e4c2167cfa0a5f865b78 --out fresh_integration_run
```

Source data: https://drive.google.com/file/d/13Taq-rcObiLurTjhOBK_53Zm4uAI0Upc/view
No hidden download or update is done. The input must match the declared snapshot.

## Meaning of the three prototypes

F1 selects an OR of already-materialized Boolean rules and minimizes weighted
training errors plus rule-count penalty. It does not yet create a calibrated
100-number predictor or the complete planned rule grammar. F2 is deliberately a
tiny DSL `y=(a*x+b)%m`; it verifies solver plumbing and planted examples, not the
full proposed depth3/node15 grammar or a robust noisy-data learner. F3 optimizes
coverage of supplied past scenarios, not an unknown future outcome. None returns
validated probabilities from solver scores.

Optimizer results only set `optimal=True` with closed finite objective bounds.
UNSAT applies only to the encoded finite problem. UNKNOWN/timeouts are not
evidence of absence of lottery rules. Lexicographic tie-breaking is included for
repeatable selected rules/sets. Runtime is machine-dependent. The reported
tracemalloc peak covers Python allocations, not all native Z3 RAM.

## Audit boundaries

- A prior-only view and mutation tests are diagnostics, not a sandbox against a
  malicious Python closure, filesystem access, or global state. Full-pipeline
  calibration/tuning/ensemble leakage review remains pending.
- Local append locks protect one append transaction; stale locks require review.
  Hash chains detect edits against an externally retained head. They do not make
  local timestamps trusted or stop an actor replacing/re-hashing the whole chain.
- Candidate ledger accepts synthetic work only and caps each family at500 and
  total1500; ERROR and TIMEOUT entries still count. Caller must log actual calls;
  solver functions do not automatically intercept arbitrary unlogged execution.
- ForecastLog accepts only synthetic records in this starter. It forbids duplicate
  method/date entries; it is not an opened real prediction registry.
- Marginal presence probabilities need not sum to1 or27. Joint and conditional
  occupancy baselines have different assumptions, stated in the exact module.
- No new historical distinguisher, significance scan, or prospective forecast was
  run. No Alpha/WP2 budget is implicitly granted by passing these tests.

## Integration

Additive modules only; review through a draft PR against the ASTRA working branch.
Do not replace its `__init__.py` or `xsmb_audit.py`. A future integration can expose
the exact APIs through the main CLI after interface review; the bridge currently
compares functions without changing the upstream CLI or statistical conclusions.

Before empirical work: freeze the complete grammar, calibration, search budget,
candidate ledger policy and six primary comparisons, and obtain Council review.
Before prospective work: power analysis, external time anchor, immutable code/
data/protocol and forecast snapshots. This starter is not preregistration.
