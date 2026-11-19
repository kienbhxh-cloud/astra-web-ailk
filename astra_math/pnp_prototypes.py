"""Finite, synthetic-first constraint-solving scaffolds; NOT lottery forecasts.

F1: weighted MaxSAT chooses an OR of Boolean rules, penalizing training mistakes
and rule count. F2: SMT satisfies a deliberately tiny affine-modular DSL.
F3: integer optimization maximizes weighted coverage of supplied past scenarios.
No function estimates calibrated probabilities or establishes predictive value.
Requires z3-solver; no dependency on other ASTRA modules.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from time import perf_counter
from typing import Any

import z3


def _integer(value: Any, name: str, minimum: int = 0) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")
    return value


def _bits(values: Sequence[Any], name: str) -> list[bool]:
    result = []
    for value in values:
        if not isinstance(value, (bool, int)) or value not in (0, 1):
            raise ValueError(f"{name} must contain Boolean/0-or-1 values")
        result.append(bool(value))
    return result


def _or(values):
    values = list(values)
    return z3.Or(values) if values else z3.BoolVal(False)


def _sum(values):
    values = list(values)
    return z3.Sum(values) if values else z3.IntVal(0)


def _base(start: float, status: str, *, solver_result: str,
          reason: str | None = None) -> dict[str, Any]:
    return {
        "status": status,
        "solver_result": solver_result,
        "reason_unknown": reason,
        "elapsed_seconds": perf_counter() - start,
        "z3_version": z3.get_version_string(),
        "scope": "synthetic_scaffold_only; no forecasting or calibration claim",
    }


def _optimization_status(opt: z3.Optimize, checked, handles):
    """Never infer optimality merely from availability of a feasible model."""
    if checked == z3.unsat:
        return "unsat", False, [], None
    if checked == z3.unknown:
        return "unknown", False, [], opt.reason_unknown()
    bounds = []
    for handle in handles:
        lower, upper = opt.lower(handle), opt.upper(handle)
        finite = "oo" not in str(lower) and "oo" not in str(upper)
        closed = finite and z3.is_true(z3.simplify(lower == upper))
        bounds.append({"lower": str(lower), "upper": str(upper),
                       "finite_closed": bool(closed)})
    proved = bool(bounds) and all(bound["finite_closed"] for bound in bounds)
    return "optimal" if proved else "sat", proved, bounds, None


def select_rules_maxsat(
    predictors: Mapping[str, Sequence[bool | int]],
    targets: Sequence[bool | int], *, max_rules: int = 3,
    mistake_weight: int = 10, rule_penalty: int = 1,
    required_rules: Sequence[str] = (), timeout_ms: int = 1000,
) -> dict[str, Any]:
    """Select a finite OR-rule set by weighted MaxSAT.

    Minimize mistake_weight * training classification errors +
    rule_penalty * selected_rule_count, then a canonical bit-mask tie-break.
    This is a discrete training surrogate, NOT Brier score or probability fitting.
    Inputs are already-materialized rule outputs; caller must enforce past-only
    feature construction. Required rules can make the hard problem infeasible.
    """
    start = perf_counter()
    _integer(max_rules, "max_rules")
    _integer(mistake_weight, "mistake_weight", 1)
    _integer(rule_penalty, "rule_penalty")
    _integer(timeout_ms, "timeout_ms", 1)
    y = _bits(targets, "targets")
    if not y:
        raise ValueError("At least one training target is required")
    if not isinstance(predictors, Mapping):
        raise ValueError("predictors must be a name-to-values mapping")
    if any(not isinstance(name, str) or not name for name in predictors):
        raise ValueError("Rule names must be nonempty strings")
    names = sorted(predictors)
    columns = {name: _bits(predictors[name], name) for name in names}
    if any(len(column) != len(y) for column in columns.values()):
        raise ValueError("Every rule must have exactly one value per target")
    if any(name not in columns for name in required_rules):
        raise ValueError("Unknown required rule")
    chosen = {name: z3.Bool(f"choose_{i}") for i, name in enumerate(names)}
    opt = z3.Optimize()
    opt.set(timeout=timeout_ms, priority="lex")
    opt.add(_sum(z3.If(chosen[name], 1, 0) for name in names) <= max_rules)
    for name in required_rules:
        opt.add(chosen[name])
    predictions = [_or(chosen[name] for name in names if columns[name][row])
                   for row in range(len(y))]
    loss_handle = None
    for prediction, target in zip(predictions, y):
        loss_handle = opt.add_soft(prediction if target else z3.Not(prediction),
                                   weight=mistake_weight, id="training_cost")
    if rule_penalty:
        for name in names:
            opt.add_soft(z3.Not(chosen[name]), weight=rule_penalty,
                         id="training_cost")
    tie = opt.minimize(_sum(z3.If(chosen[name], 1 << i, 0)
                            for i, name in enumerate(names)))
    checked = opt.check()
    status, optimal, bounds, reason = _optimization_status(
        opt, checked, [loss_handle, tie])
    result = _base(start, status, solver_result=str(checked), reason=reason)
    result.update({"optimal": optimal, "objective_bounds": bounds,
                   "objective_definition": "mistake_weight*errors + rule_penalty*rule_count",
                   "training_rows": len(y), "candidate_rules": len(names),
                   "selected_rules": None, "training_predictions": None,
                   "training_errors": None, "training_cost": None})
    if checked == z3.sat:
        model = opt.model()
        selected = [name for name in names
                    if z3.is_true(model.eval(chosen[name], model_completion=True))]
        predicted = [any(columns[name][row] for name in selected)
                     for row in range(len(y))]
        errors = sum(a != b for a, b in zip(predicted, y))
        result.update({"selected_rules": selected,
                       "training_predictions": predicted,
                       "training_errors": errors,
                       "training_cost": mistake_weight * errors + rule_penalty * len(selected)})
    result["elapsed_seconds"] = perf_counter() - start
    return result


def synthesize_affine_modular(
    examples: Sequence[tuple[int, int]], *, modulus: int = 100,
    max_a: int | None = None, max_b: int | None = None,
    timeout_ms: int = 1000,
) -> dict[str, Any]:
    """SMT feasibility for y=(a*x+b)%modulus with bounded nonnegative a,b.

    Satisfies the supplied examples exactly. UNSAT rules out this finite DSL only;
    it says nothing about every possible formula. No extrapolation guarantee.
    """
    start = perf_counter()
    _integer(modulus, "modulus", 2)
    max_a = modulus - 1 if max_a is None else _integer(max_a, "max_a")
    max_b = modulus - 1 if max_b is None else _integer(max_b, "max_b")
    _integer(timeout_ms, "timeout_ms", 1)
    if not examples:
        raise ValueError("At least one example is required")
    normalized = []
    for example in examples:
        if len(example) != 2:
            raise ValueError("Each example must be (x,y)")
        x, y = example
        _integer(x, "example x"); _integer(y, "example y")
        if x >= modulus or y >= modulus:
            raise ValueError("Example values must be in the modular alphabet")
        normalized.append((x, y))
    a, b = z3.Ints("affine_a affine_b")
    solver = z3.Solver()
    solver.set(timeout=timeout_ms, random_seed=0)
    solver.add(a >= 0, a <= max_a, b >= 0, b <= max_b)
    for x, y in normalized:
        solver.add((a * x + b) % modulus == y)
    checked = solver.check()
    result = _base(start, str(checked), solver_result=str(checked),
                   reason=solver.reason_unknown() if checked == z3.unknown else None)
    result.update({"optimal": None, "parameters": None,
                   "dsl": "y=(a*x+b)%modulus", "modulus": modulus,
                   "parameter_bounds": {"a": [0, max_a], "b": [0, max_b]},
                   "training_examples": len(normalized), "training_predictions": None})
    if checked == z3.sat:
        model = solver.model()
        aa, bb = model.eval(a).as_long(), model.eval(b).as_long()
        result.update({"parameters": {"a": aa, "b": bb},
                       "training_predictions": [(aa * x + bb) % modulus
                                                for x, _ in normalized]})
    result["elapsed_seconds"] = perf_counter() - start
    return result


def maximize_set_coverage(
    scenarios: Sequence[Sequence[int]], universe: Sequence[int], *, k: int,
    weights: Sequence[int] | None = None, timeout_ms: int = 1000,
) -> dict[str, Any]:
    """Choose exactly k labels maximizing weighted covered past scenarios.

    A scenario is covered when >=1 selected label occurs. Scenario labels outside
    the candidate universe cannot cover that scenario. Repeated labels within a
    scenario count only once. This empirical objective is not future probability.
    """
    start = perf_counter()
    _integer(k, "k"); _integer(timeout_ms, "timeout_ms", 1)
    labels = list(universe)
    for label in labels:
        _integer(label, "universe label")
    if len(set(labels)) != len(labels):
        raise ValueError("Universe labels must be distinct")
    labels.sort()
    if not scenarios:
        raise ValueError("At least one scenario is required")
    rows = []
    for scenario in scenarios:
        for label in scenario:
            _integer(label, "scenario label")
        rows.append(set(scenario))
    if weights is None:
        weights = [1] * len(rows)
    weights = list(weights)
    if len(weights) != len(rows):
        raise ValueError("One weight per scenario is required")
    for weight in weights:
        _integer(weight, "scenario weight")
    pick = {label: z3.Bool(f"cover_choose_{i}")
            for i, label in enumerate(labels)}
    covered = [_or(pick[label] for label in labels if label in row) for row in rows]
    objective = z3.Sum([z3.If(hit, weight, 0)
                        for hit, weight in zip(covered, weights)])
    opt = z3.Optimize()
    opt.set(timeout=timeout_ms, priority="lex")
    # A cardinality k exceeding the universe is a valid but infeasible problem.
    opt.add(_sum(z3.If(pick[label], 1, 0) for label in labels) == k)
    main = opt.maximize(objective)
    tie = opt.minimize(_sum(z3.If(pick[label], 1 << i, 0)
                            for i, label in enumerate(labels)))
    checked = opt.check()
    status, optimal, bounds, reason = _optimization_status(opt, checked, [main, tie])
    result = _base(start, status, solver_result=str(checked), reason=reason)
    result.update({"optimal": optimal, "objective_bounds": bounds,
                   "objective_definition": "sum(weight_s * any_selected_label_in_scenario_s)",
                   "selected_labels": None, "covered_scenarios": None,
                   "weighted_coverage": None, "scenarios": len(rows), "k": k})
    if checked == z3.sat:
        model = opt.model()
        selected = [label for label in labels
                    if z3.is_true(model.eval(pick[label], model_completion=True))]
        hits = [bool(set(selected) & row) for row in rows]
        result.update({"selected_labels": selected, "covered_scenarios": hits,
                       "weighted_coverage": sum(w for w, hit in zip(weights, hits) if hit)})
    result["elapsed_seconds"] = perf_counter() - start
    return result
