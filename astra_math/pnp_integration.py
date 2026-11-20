"""Compatibility bridge: no historical rule discovery or statistical testing."""
from pathlib import Path
import hashlib
from . import xsmb_exact as exact
from . import xsmb_audit as audit
from .pnp_foundations import load_csv

def probability_compatibility():
    checks={'presence':exact.p_presence()==audit.p_lo(),
            'xien2':exact.p_all_distinct(2)==audit.p_xien(2),
            'xien3':exact.p_all_distinct(3)==audit.p_xien(3),
            'nhay':tuple(exact.nhay_distribution())==tuple(audit.nhay_distribution())}
    if not all(checks.values()):raise ValueError('Upstream probability mismatch')
    return checks

def validate_snapshot(path,expected_sha256):
    rows=load_csv(path,expected_sha256);upstream=audit.load_draws(str(path),strict_lengths=True)
    if len(rows)!=len(upstream) or any(a.day!=b.day or a.tails!=tuple(b.numbers) for a,b in zip(rows,upstream)):raise ValueError('Loader disagreement')
    return {'csv_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),'draws':len(rows),
            'first':rows[0].day.isoformat(),'last':rows[-1].day.isoformat(),'loaders_agree':True,
            'probabilities_agree':probability_compatibility(),'purpose':'structure/hash compatibility only; no empirical search'}
