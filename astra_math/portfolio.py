"""ASTRA STOCK — Tối ưu danh mục có ràng buộc rời rạc bằng CP-SAT (U2).

Ràng buộc hỗ trợ: vốn, lô 100, số mã tối đa, tỷ trọng min/max mỗi mã, trần ngành, mã cấm,
giới hạn thanh khoản theo ADV20, cặp tương quan cao (chỉ chọn 1), phí cố định + phí tỷ lệ,
và (tùy chọn) danh mục hiện tại để tính phí tái cân bằng.
Mục tiêu: tối đa lợi nhuận kỳ vọng ròng = sum(v_i * r_i) - phí.

Lưu ý: tối ưu chỉ tốt bằng dự báo r_i đưa vào. Module này không tạo ra alpha.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from ortools.sat.python import cp_model


@dataclass
class Asset:
    ticker: str
    sector: str
    price: int              # đồng / cổ phiếu
    exp_return: float       # lợi suất kỳ vọng mỗi kỳ (giả định/đầu vào từ mô hình alpha)
    adv20_vnd: float = float("inf")
    restricted: bool = False


@dataclass
class Constraints:
    capital: int = 1_000_000_000
    lot: int = 100
    max_names: int = 6
    w_min: float = 0.08
    w_max: float = 0.25
    sector_max: float = 0.35
    liq_frac_adv: float = 0.005
    exclusive_pairs: Sequence[Tuple[str, str]] = ()
    fixed_fee: int = 3_000_000
    prop_fee: float = 0.0015
    current_shares: Dict[str, int] = field(default_factory=dict)  # danh mục hiện có (tái cân bằng)


def _max_lots(a: Asset, c: Constraints) -> int:
    if a.restricted:
        return 0
    return int(min(c.w_max * c.capital, c.liq_frac_adv * a.adv20_vnd) // (a.price * c.lot))


def check(assets: List[Asset], c: Constraints, shares: Dict[str, int]):
    """Kiểm tra độc lập mọi ràng buộc; trả về (lợi_nhuận_ròng_kỳ_vọng, danh_sách_lỗi)."""
    idx = {a.ticker: a for a in assets}
    v = {t: s * idx[t].price for t, s in shares.items() if s}
    err = []
    if sum(v.values()) > c.capital:
        err.append("vượt vốn")
    if len(v) > c.max_names:
        err.append("quá số mã")
    for t, val in v.items():
        a = idx[t]
        if shares[t] % c.lot:
            err.append(f"lẻ lô {t}")
        if not (c.w_min * c.capital - 1e-6 <= val <= c.w_max * c.capital + 1e-6):
            err.append(f"tỷ trọng {t}")
        if val > c.liq_frac_adv * a.adv20_vnd + 1e-6:
            err.append(f"thanh khoản {t}")
        if a.restricted:
            err.append(f"mã cấm {t}")
    for s in {a.sector for a in assets}:
        if sum(val for t, val in v.items() if idx[t].sector == s) > c.sector_max * c.capital + 1e-6:
            err.append(f"ngành {s}")
    for x, y in c.exclusive_pairs:
        if x in v and y in v:
            err.append(f"cặp {x}-{y}")
    traded = sum(abs(shares.get(t, 0) - c.current_shares.get(t, 0)) * idx[t].price for t in idx)
    obj = sum(val * idx[t].exp_return for t, val in v.items()) - c.prop_fee * traded - c.fixed_fee * len(v)
    return obj, err


def optimize(assets: List[Asset], c: Constraints, time_limit: float = 30.0, workers: int = 4, seed: int = 2026):
    """Giải tối ưu. Trả về dict: shares, objective, status, seconds."""
    m = cp_model.CpModel()
    n = len(assets)
    L = [m.NewIntVar(0, _max_lots(a, c), f"L_{a.ticker}") for a in assets]
    S = [m.NewBoolVar(f"S_{a.ticker}") for a in assets]
    lotv = [a.price * c.lot for a in assets]
    V = [L[i] * lotv[i] for i in range(n)]
    for i in range(n):
        m.Add(L[i] == 0).OnlyEnforceIf(S[i].Not())
        m.Add(V[i] >= int(c.w_min * c.capital)).OnlyEnforceIf(S[i])
    m.Add(sum(V) <= c.capital)
    m.Add(sum(S) <= c.max_names)
    for s in {a.sector for a in assets}:
        m.Add(sum(V[i] for i in range(n) if assets[i].sector == s) <= int(c.sector_max * c.capital))
    pos = {a.ticker: i for i, a in enumerate(assets)}
    for x, y in c.exclusive_pairs:
        if x in pos and y in pos:
            m.Add(S[pos[x]] + S[pos[y]] <= 1)
    SCALE = 10_000
    terms = []
    for i, a in enumerate(assets):
        cur_lots = c.current_shares.get(a.ticker, 0) // c.lot
        terms.append(L[i] * int(round(lotv[i] * a.exp_return * SCALE)))
        # phí tỷ lệ trên phần giao dịch |L - cur|
        d = m.NewIntVar(0, max(_max_lots(a, c), cur_lots) + cur_lots, f"D_{a.ticker}")
        m.AddAbsEquality(d, L[i] - cur_lots)
        terms.append(-d * int(round(lotv[i] * c.prop_fee * SCALE)))
    terms.append(-sum(S) * int(c.fixed_fee * SCALE))
    m.Maximize(sum(terms))
    sv = cp_model.CpSolver()
    sv.parameters.max_time_in_seconds = time_limit
    sv.parameters.num_workers = workers
    sv.parameters.random_seed = seed
    st = sv.Solve(m)
    shares = {a.ticker: sv.Value(L[i]) * c.lot for i, a in enumerate(assets) if sv.Value(L[i])}
    obj, err = check(assets, c, shares)
    return {"shares": shares, "objective": obj, "errors": err, "status": sv.StatusName(st),
            "seconds": sv.WallTime()}


def greedy(assets: List[Asset], c: Constraints, key=None):
    """Baseline tham lam: xếp theo key (mặc định lợi suất kỳ vọng), mua tối đa cho phép."""
    key = key or (lambda a: a.exp_return)
    chosen, used, secv = {}, 0, {}
    for a in sorted(assets, key=lambda a: -key(a)):
        if len(chosen) >= c.max_names:
            break
        if a.restricted or a.exp_return - c.prop_fee <= 0:
            continue
        if any((a.ticker == x and y in chosen) or (a.ticker == y and x in chosen) for x, y in c.exclusive_pairs):
            continue
        cap = min(c.capital - used, c.sector_max * c.capital - secv.get(a.sector, 0), c.w_max * c.capital,
                  c.liq_frac_adv * a.adv20_vnd)
        lots = int(cap // (a.price * c.lot))
        val = lots * a.price * c.lot
        if val < c.w_min * c.capital or val * (a.exp_return - c.prop_fee) - c.fixed_fee <= 0:
            continue
        chosen[a.ticker] = lots * c.lot
        used += val
        secv[a.sector] = secv.get(a.sector, 0) + val
    obj, err = check(assets, c, chosen)
    return {"shares": chosen, "objective": obj, "errors": err}
