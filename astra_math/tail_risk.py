"""ASTRA STOCK — Rủi ro đuôi chính xác cho danh mục (U1).

Mô hình phân tầng: sốc thị trường M -> sốc ngành S_g -> từng mã X_i giảm sâu (Bernoulli).
Có điều kiện theo (M, S) các mã độc lập, nên phân phối số mã giảm và phân phối THUA LỖ
của danh mục được tính chính xác bằng tích chập (quy hoạch động / co tensor theo cây).
Chi phí đa thức theo số mã, thay vì 2^N kịch bản.

Đầu ra: P(>= k mã cùng giảm), phân phối lỗ, VaR và Expected Shortfall chính xác trong mô hình.
Giới hạn: kết quả chỉ đúng trong mô hình; tham số phải được ước lượng và kiểm định ngoài mẫu.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Sequence

import numpy as np


@dataclass
class Stock:
    ticker: str
    sector: str
    p_down_normal: float      # P(giảm sâu | ngành bình thường)
    p_down_shock: float       # P(giảm sâu | ngành bị sốc)
    loss_if_down: int = 0     # số đơn vị lỗ (vd triệu đồng) nếu mã giảm sâu


@dataclass
class HierarchicalModel:
    p_market_shock: float
    p_sector_shock_normal: Dict[str, float]   # P(sốc ngành | thị trường bình thường)
    p_sector_shock_market: Dict[str, float]   # P(sốc ngành | thị trường sốc)
    stocks: List[Stock] = field(default_factory=list)

    def sectors(self) -> List[str]:
        return sorted({s.sector for s in self.stocks})


def _bern_conv(probs: Sequence[float], sizes: Sequence[int]) -> np.ndarray:
    d = np.array([1.0])
    for q, sz in zip(probs, sizes):
        nd = np.zeros(len(d) + sz)
        nd[: len(d)] += d * (1 - q)
        nd[sz: sz + len(d)] += d * q
        d = nd
    return d


def _mixture(model: HierarchicalModel, use_loss: bool) -> np.ndarray:
    total = None
    for shock, wM in ((0, 1 - model.p_market_shock), (1, model.p_market_shock)):
        pS = model.p_sector_shock_market if shock else model.p_sector_shock_normal
        d = np.array([1.0])
        for g in model.sectors():
            st = [s for s in model.stocks if s.sector == g]
            sizes = [s.loss_if_down if use_loss else 1 for s in st]
            d0 = _bern_conv([s.p_down_normal for s in st], sizes)
            d1 = _bern_conv([s.p_down_shock for s in st], sizes)
            dg = (1 - pS[g]) * d0 + pS[g] * d1
            d = np.convolve(d, dg)
        total = wM * d if total is None else _add(total, wM * d)
    return total


def _add(a, b):
    n = max(len(a), len(b)); out = np.zeros(n)
    out[: len(a)] += a; out[: len(b)] += b
    return out


def count_down_distribution(model: HierarchicalModel) -> np.ndarray:
    """dist[k] = P(đúng k mã giảm sâu)."""
    return _mixture(model, use_loss=False)


def loss_distribution(model: HierarchicalModel) -> np.ndarray:
    """dist[L] = P(lỗ đúng L đơn vị)."""
    return _mixture(model, use_loss=True)


def tail_prob(dist: np.ndarray, k: int) -> float:
    return float(dist[k:].sum())


def var_es(dist: np.ndarray, alpha: float = 0.99):
    """VaR và Expected Shortfall chính xác (đơn vị lỗ) ở mức tin cậy alpha."""
    cdf = np.cumsum(dist)
    var = int(np.searchsorted(cdf, alpha - 1e-15))
    tail = dist[var + 1:]
    tail_mass = tail.sum()
    # ES: kỳ vọng lỗ trong phần đuôi 1-alpha (chuẩn Acerbi–Tasche)
    losses = np.arange(len(dist))
    beyond = (losses[var + 1:] * tail).sum()
    es = (beyond + var * ((1 - alpha) - tail_mass)) / (1 - alpha)
    return var, float(es)


def scenario_attribution(model: HierarchicalModel, k: int) -> Dict[str, float]:
    """Tỷ trọng đóng góp của nhánh sốc thị trường vào P(>=k mã giảm)."""
    m0 = HierarchicalModel(0.0, model.p_sector_shock_normal, model.p_sector_shock_market, model.stocks)
    m1 = HierarchicalModel(1.0, model.p_sector_shock_normal, model.p_sector_shock_market, model.stocks)
    t0 = tail_prob(count_down_distribution(m0), k) * (1 - model.p_market_shock)
    t1 = tail_prob(count_down_distribution(m1), k) * model.p_market_shock
    tot = t0 + t1
    return {"P_tong": tot, "ty_trong_soc_thi_truong": t1 / tot if tot else 0.0, "ty_trong_binh_thuong": t0 / tot if tot else 0.0}


def monte_carlo_count(model: HierarchicalModel, n: int, seed: int = 0) -> np.ndarray:
    """Mô phỏng Monte Carlo cùng mô hình (dùng làm đối chứng)."""
    r = np.random.default_rng(seed)
    secs = model.sectors()
    M = r.random(n) < model.p_market_shock
    K = np.zeros(n, dtype=int)
    for g in secs:
        pS = np.where(M, model.p_sector_shock_market[g], model.p_sector_shock_normal[g])
        S = r.random(n) < pS
        for s in (s for s in model.stocks if s.sector == g):
            q = np.where(S, s.p_down_shock, s.p_down_normal)
            K += r.random(n) < q
    return K
