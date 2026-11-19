"""Đếm mô hình có trọng số (weighted model counting) bằng co mạng tensor.

Đây là kỹ thuật cốt lõi trong các chứng minh bác bỏ ETH (OpenAI Phụ lục D, Anthropic),
dùng ở dạng thực dụng: khử biến theo thứ tự min-degree. Chi phí ~ 2^(độ rộng khử biến),
nên nhanh khi bài toán có cấu trúc (độ rộng nhỏ), chậm lại khi phụ thuộc dày đặc.

- exact=True: dùng số nguyên Python / Fraction, không sai số làm tròn.
- exact=False: dùng float64, nhanh hơn.
"""
from __future__ import annotations
import itertools
from fractions import Fraction
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np

Factor = Tuple[Tuple[int, ...], np.ndarray]  # (danh sách biến, bảng giá trị 2x2x...x2)


def clause_factor(clause: Sequence[Tuple[int, bool]], exact: bool = True) -> Factor:
    """Mệnh đề OR của các literal (biến, dấu). Trả về factor 0/1."""
    vs = tuple(sorted({v for v, _ in clause}))
    T = np.empty((2,) * len(vs), dtype=object if exact else float)
    for idx in itertools.product((0, 1), repeat=len(vs)):
        a = dict(zip(vs, idx))
        T[idx] = 1 if any(a[v] == int(s) for v, s in clause) else 0
    return vs, T


def unary_factor(v: int, p_true, exact: bool = True) -> Factor:
    """Trọng số của một biến: P(v=1)=p_true, P(v=0)=1-p_true."""
    if exact:
        p = Fraction(p_true) if not isinstance(p_true, Fraction) else p_true
        return (v,), np.array([1 - p, p], dtype=object)
    return (v,), np.array([1.0 - float(p_true), float(p_true)])


def table_factor(vs: Sequence[int], fn, exact: bool = True) -> Factor:
    """Factor tổng quát: fn(dict biến->0/1) trả về trọng số."""
    vs = tuple(vs)
    T = np.empty((2,) * len(vs), dtype=object if exact else float)
    for idx in itertools.product((0, 1), repeat=len(vs)):
        T[idx] = fn(dict(zip(vs, idx)))
    return vs, T


def _contract(factors: List[Factor], v: int) -> Factor:
    allv = sorted(set(x for vs, _ in factors for x in vs))
    letters = {x: chr(97 + i) for i, x in enumerate(allv)}
    if len(allv) > 26:
        raise ValueError("Độ rộng khử biến > 26: bài toán quá dày cho bộ khử biến này")
    out_v = [x for x in allv if x != v]
    expr = ",".join("".join(letters[x] for x in vs) for vs, _ in factors)
    expr += "->" + "".join(letters[x] for x in out_v)
    res = np.einsum(expr, *[T for _, T in factors])
    if not isinstance(res, np.ndarray):
        res = np.array(res, dtype=object)
    return tuple(out_v), res


def weighted_count(factors: Iterable[Factor], variables: Iterable[int], max_width: int = 22):
    """Tổng trên mọi phép gán của tích các factor. Trả về (giá_trị, độ_rộng_lớn_nhất)."""
    fs = list(factors)
    remaining = set(variables) | {x for vs, _ in fs for x in vs}
    width = 0
    while remaining:
        # chọn biến min-degree (ít biến lân cận nhất)
        def degree(v):
            return len({x for vs, _ in fs if v in vs for x in vs})
        v = min(remaining, key=lambda x: (degree(x), x))
        inv = [f for f in fs if v in f[0]]
        fs = [f for f in fs if v not in f[0]]
        remaining.discard(v)
        if not inv:  # biến tự do không có factor: nhân 2
            fs.append(((), np.array(2, dtype=object)))
            continue
        nb = len({x for vs, _ in inv for x in vs})
        width = max(width, nb)
        if nb > max_width:
            raise ValueError(f"Độ rộng {nb} vượt max_width={max_width}")
        fs.append(_contract(inv, v))
    val = 1
    for _, T in fs:
        val = val * (T.item() if hasattr(T, "item") else T)
    return val, width


def count_cnf(n: int, clauses: Sequence[Sequence[Tuple[int, bool]]], weights: Dict[int, object] | None = None,
              exact: bool = True, max_width: int = 22):
    """#SAT (hoặc xác suất nếu có weights) của CNF trên biến 0..n-1."""
    fs = [clause_factor(c, exact) for c in clauses]
    if weights:
        fs += [unary_factor(v, p, exact) for v, p in weights.items()]
    val, w = weighted_count(fs, range(n), max_width)
    if weights:
        # biến không có trọng số được đếm 2 lần mỗi biến tự do; với xác suất, mọi biến nên có trọng số
        pass
    return val, w


def brute_force_count(n: int, clauses, weights=None):
    """Đối chiếu bằng vét cạn (chỉ dùng cho n nhỏ)."""
    tot = 0 if weights is None else Fraction(0)
    for x in itertools.product((0, 1), repeat=n):
        if all(any(x[v] == int(s) for v, s in c) for c in clauses):
            if weights is None:
                tot += 1
            else:
                w = Fraction(1)
                for v, p in weights.items():
                    p = Fraction(p)
                    w *= p if x[v] else 1 - p
                tot += w
    return tot
