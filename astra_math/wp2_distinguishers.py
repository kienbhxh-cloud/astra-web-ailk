"""WP2 — Bộ phân biệt (distinguishers) ĐĂNG KÝ TRƯỚC cho ASTRA LÔ XSMB (PNP-MASTER-005).

Câu hỏi: dữ liệu XSMB có phân biệt được với giả thuyết H0 (27 giải độc lập, mỗi chữ số đều 0–9) không?
Theo Yao (1982): không có bộ phân biệt hiệu quả ⇔ không có bộ dự báo hiệu quả.

Thiết kế:
- 13 phép kiểm D01–D13, mỗi phép trả p-value HAI PHÍA (trừ khi ghi khác), khóa trước khi chạy dữ liệu thật.
- Họ giả thuyết: Holm, alpha = 0,05 trên đúng 13 p-value (không thêm, không bớt sau khi xem kết quả).
- Nhóm A (trong ngày, giải tích): D01–D05, D12–D13.
- Nhóm B (theo thời gian, HOÁN VỊ thứ tự ngày, B = 9.999, seed khóa): D06–D11.
  Hoán vị nguyên ngày cho p-value chính xác dưới giả định yếu hơn H0: các ngày hoán đổi được (exchangeable).
- Nhóm C: D11 nén lzma (hoán vị, B nhỏ hơn vì chậm).
Không phụ thuộc thư viện ngoài trừ numpy. Đây là công cụ ĐO, không dự báo.
"""
from __future__ import annotations

import lzma
import math
from datetime import date
from typing import Dict, List, Sequence

import numpy as np

from astra_math import xsmb_audit as xa

PRIZE_DIGITS = [5] * 10 + [4] * 10 + [3] * 3 + [2] * 4
TESTS = {
    "D01": "χ² độ đều 100 đuôi, gộp 27 giải (df 99)",
    "D02": "χ² độ đều 100 đuôi theo từng vị trí giải (27 phép, gộp Šidák min-p)",
    "D03": "χ² độ đều chữ số 0–9 theo từng hàng (hàng đơn vị..hàng chục nghìn; 5 phép, Šidák)",
    "D04": "Phân phối số đuôi khác nhau u mỗi kỳ so với phân phối chính xác (χ², gộp đuôi)",
    "D05": "χ² độc lập hai chữ số cuối: bảng 10×10 hàng chục × hàng đơn vị (df 81)",
    "D06": "Trùng lặp kỳ liền kề Σ|S_t ∩ S_{t-1}| (hoán vị ngày)",
    "D07": "Trùng lặp trễ 2..7 Σ_k Σ_t |S_t ∩ S_{t-k}| (hoán vị ngày)",
    "D08": "Đề lặp: #{t: ĐB_t ∈ S_{t-1}} (hoán vị ngày)",
    "D09": "Tự tương quan hiện diện trễ 1..30, Q = Σ_k (Σ_i r_ik)² (hoán vị ngày)",
    "D10": "Lô gan: phương sai độ dài khoảng cách giữa các lần về (hoán vị ngày)",
    "D11": "Nén lzma chuỗi đuôi theo thứ tự ngày (hoán vị ngày, B = 999, một phía: nén tốt hơn)",
    "D12": "Hiệu ứng thứ trong tuần: bảng 100 đuôi × 7 thứ (χ², df 594)",
    "D13": "Trôi theo năm: bảng 100 đuôi × năm (χ²)",
}
ALPHA = 0.05
B_PERM = 9999   # 1/(B+1) = 1e-4 << 0,05/13 = 0,0038 (bắt buộc: xem hiệu chỉnh)
B_LZMA = 999
SEED = 20261120


# ------------------------------------------------------------------ dữ liệu
def load_raw(path: str):
    """CSV: date + 27 cột giải (chuỗi số, có thể mất số 0 đầu). Trả (dates, raw[n][27] chuỗi zero-pad)."""
    import csv
    rows = list(csv.reader(open(path, encoding="utf-8-sig")))[1:]
    dates = [date.fromisoformat(r[0]) for r in rows]
    raw = [[v.strip().zfill(w) for v, w in zip(r[1:28], PRIZE_DIGITS)] for r in rows]
    return dates, raw


def simulate_raw(n: int, seed: int, start: date = date(2010, 1, 1)):
    """Dữ liệu H0: mỗi chữ số mỗi lồng đều 0–9, độc lập."""
    r = np.random.default_rng(seed)
    dates = [date.fromordinal(start.toordinal() + i) for i in range(n)]
    raw = [["".join(str(d) for d in r.integers(0, 10, w)) for w in PRIZE_DIGITS] for _ in range(n)]
    return dates, raw


def tails(raw) -> np.ndarray:
    return np.array([[int(v[-2:]) for v in row] for row in raw], dtype=np.int16)


def presence(T: np.ndarray) -> np.ndarray:
    P = np.zeros((T.shape[0], 100), dtype=np.int8)
    np.put_along_axis(P, T.astype(np.int64), 1, axis=1)
    return P


# ------------------------------------------------------------------ tiện ích
def _chi2(obs: np.ndarray, exp: np.ndarray, dof: int) -> float:
    if dof <= 0:          # vd D13 khi dữ liệu chỉ có 1 năm: không kiểm được, không bác bỏ
        return 1.0
    stat = float(((obs - exp) ** 2 / exp).sum())
    return xa.chi2_sf(stat, dof)


def _sidak(pmin: float, m: int) -> float:
    return 1 - (1 - pmin) ** m


def _perm_p(stat_fn, X, B, rng, two_sided=True, larger_is_extreme=True):
    obs = stat_fn(X)
    null = np.empty(B)
    n = X.shape[0]
    for b in range(B):
        null[b] = stat_fn(X[rng.permutation(n)])
    if two_sided:
        c = null.mean()
        k = int((np.abs(null - c) >= abs(obs - c) - 1e-12).sum())
    else:
        k = int((null >= obs - 1e-12).sum()) if larger_is_extreme else int((null <= obs + 1e-12).sum())
    return (k + 1) / (B + 1), float(obs), float(null.mean())


# ------------------------------------------------------------------ các phép kiểm
def d01(T):
    c = np.bincount(T.ravel(), minlength=100)
    return _chi2(c, np.full(100, c.sum() / 100), 99)


def d02(T):
    ps = [_chi2(np.bincount(T[:, j], minlength=100), np.full(100, T.shape[0] / 100), 99) for j in range(27)]
    return _sidak(min(ps), 27)


def d03(raw):
    ps = []
    for place in range(5):  # 0 = hàng đơn vị
        cnt = np.zeros(10)
        for row in raw:
            for v in row:
                if len(v) > place:
                    cnt[int(v[-1 - place])] += 1
        ps.append(_chi2(cnt, np.full(10, cnt.sum() / 10), 9))
    return _sidak(min(ps), 5)


def d04(T):
    dist = [float(p) for p in xa.distinct_tails_distribution()]
    u = np.array([len(set(r.tolist())) for r in T])
    n = len(u)
    # gộp đuôi để kỳ vọng >= 5
    bins, cur, edges = [], 0.0, []
    lo = 0
    for k in range(28):
        cur += dist[k]
        if cur * n >= 5:
            bins.append((lo, k, cur)); lo = k + 1; cur = 0.0
    if cur > 0:
        a, b, p = bins.pop(); bins.append((a, 27, p + cur))
    obs = np.array([((u >= a) & (u <= b)).sum() for a, b, _ in bins], float)
    exp = np.array([p * n for _, _, p in bins])
    return _chi2(obs, exp, len(bins) - 1)


def d05(T):
    tab = np.zeros((10, 10))
    np.add.at(tab, (T.ravel() // 10, T.ravel() % 10), 1)
    exp = tab.sum(1, keepdims=True) * tab.sum(0, keepdims=True) / tab.sum()
    return _chi2(tab, exp, 81)


def _overlap(P, k):
    return float((P[k:] * P[:-k]).sum())


def d06(P, rng):
    return _perm_p(lambda X: _overlap(X, 1), P, B_PERM, rng)[0]


def d07(P, rng):
    return _perm_p(lambda X: sum(_overlap(X, k) for k in range(2, 8)), P, B_PERM, rng)[0]


def d08(T, P, rng):
    # ghép ĐB và tập hiện diện thành một ma trận để hoán vị nguyên ngày
    X = np.concatenate([T[:, :1].astype(np.int16), P.astype(np.int16)], axis=1)

    def stat_shift(Y):  # Σ_t P_{t-1}[ĐB_t]
        de = Y[1:, 0].astype(np.int64)
        return float(Y[:-1, 1:][np.arange(len(de)), de].sum())
    return _perm_p(stat_shift, X, B_PERM, rng)[0]


def d09(P, rng):
    def stat(X):
        Xc = X - X.mean(0, keepdims=True)
        den = (Xc ** 2).sum(0) + 1e-12
        q = 0.0
        for k in range(1, 31):
            r = (Xc[k:] * Xc[:-k]).sum(0) / den
            q += float(r.sum()) ** 2
        return q
    return _perm_p(lambda X: stat(X.astype(np.float64)), P, B_PERM, rng, two_sided=False)[0]


def d10(P, rng):
    def stat(X):
        gaps = []
        for i in range(100):
            idx = np.flatnonzero(X[:, i])
            if len(idx) > 1:
                gaps.append(np.diff(idx))
        g = np.concatenate(gaps)
        return float(g.var())
    return _perm_p(stat, P, B_PERM, rng)[0]


def d11(T, rng):
    stat = lambda X: -len(lzma.compress(X.astype(np.uint8).tobytes(), preset=6))  # lớn = nén tốt
    return _perm_p(stat, T, B_LZMA, rng, two_sided=False)[0]


def d12(T, dates):
    wd = np.array([d.weekday() for d in dates])
    tab = np.zeros((100, 7))
    for k in range(7):
        tab[:, k] = np.bincount(T[wd == k].ravel(), minlength=100)
    exp = tab.sum(1, keepdims=True) * tab.sum(0, keepdims=True) / tab.sum()
    return _chi2(tab, exp, 99 * 6)


def d13(T, dates):
    yr = np.array([d.year for d in dates])
    ys = sorted(set(yr.tolist()))
    tab = np.stack([np.bincount(T[yr == y].ravel(), minlength=100) for y in ys], axis=1).astype(float)
    exp = tab.sum(1, keepdims=True) * tab.sum(0, keepdims=True) / tab.sum()
    return _chi2(tab, exp, 99 * (len(ys) - 1))


def run_all(dates, raw, seed: int = SEED) -> Dict[str, float]:
    T = tails(raw)
    P = presence(T)
    rng = np.random.default_rng(seed)
    p = {
        "D01": d01(T), "D02": d02(T), "D03": d03(raw), "D04": d04(T), "D05": d05(T),
        "D06": d06(P, rng), "D07": d07(P, rng), "D08": d08(T, P, rng), "D09": d09(P, rng),
        "D10": d10(P, rng), "D11": d11(T, rng), "D12": d12(T, dates), "D13": d13(T, dates),
    }
    return p


def holm_report(p: Dict[str, float], alpha: float = ALPHA) -> Dict[str, object]:
    keys = list(p)
    rej = xa.holm([p[k] for k in keys], alpha)
    return {"p": {k: round(p[k], 5) for k in keys}, "bac_bo_holm": [k for k, r in zip(keys, rej) if r],
            "so_phep": len(keys), "alpha": alpha}
