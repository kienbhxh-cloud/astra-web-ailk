"""Ngữ pháp F1-v1 (đặc tả KTST, 20/11/2026) — đặc trưng thật của XSMB, chỉ dùng các kỳ TRƯỚC kỳ t.

Mỗi đặc trưng là mệnh đề Boolean về số n (00..99) tại kỳ t. Đếm theo THỨ TỰ KỲ QUAY, không theo ngày lịch.
Một luật = hội (AND) của <= s đặc trưng, mỗi nhóm tối đa 1. Luật "bật" cho (n, t) nếu mọi đặc trưng đúng.

Nhóm (14 nhóm, F = 39 đặc trưng):
  G1..G7  trễ L = 1..7: "n về ở kỳ t-L" (V_L) / "n không về ở kỳ t-L" (K_L)            7 nhóm x 2
  G8      gan (số kỳ từ lần về gần nhất) >= g, g in {2,3,4,5,7,10,15}                  1 nhóm x 7
  G9      số lần về trong 10 kỳ trước: =0, =1, =2, >=3                                1 nhóm x 4
  G10     về >= 2 nháy ở kỳ t-1                                                       1
  G11     n = 2 số cuối giải ĐB kỳ t-1                                                1
  G12     chữ số hàng đơn vị của n = chữ số cuối giải ĐB kỳ t-1 ("chạm đuôi ĐB")       1
  G13     n là số kép (00, 11, ..., 99)                                               1
  G14     (chục + đơn vị) mod 10 = k, k = 0..9                                        1 nhóm x 10

Ràng buộc chéo (cặp mâu thuẫn HOẶC thừa — để mỗi luật đếm được là một hàm KHÁC nhau):
  - V_L ∧ gan>=g với g > L  (mâu thuẫn);  K_L ∧ gan>=g với g > L  (thừa: gan>=g đã kéo theo K_L)
  - đếm10=0 ∧ V_L (mâu thuẫn); đếm10=0 ∧ K_L (thừa); đếm10=0 ∧ gan>=g, mọi g (thừa); đếm10>=1 ∧ gan>=15 (mâu thuẫn)
    đếm10 in {1,2,>=3} ∧ gan>=g với g>=11: không có g như vậy ngoài 15 (đã xử lý)
  - >=2 nháy kỳ t-1 ∧ (K_1 | gan>=g | đếm10=0 | đếm10=1)  (mâu thuẫn);  ∧ V_1 (thừa)
  - ĐB kỳ t-1 ∧ (K_1 | gan>=g | đếm10=0) (mâu thuẫn); ∧ V_1 (thừa)
  - kép ∧ tổng lẻ (mâu thuẫn: kép thì tổng = 2d chẵn)
  - ĐB kỳ t-1 ∧ chạm đuôi ĐB (thừa)
  Giới hạn đã biết: một số mâu thuẫn 3 chiều (vd đếm10=1 ∧ V_1 ∧ V_2) không mã hóa được bằng cặp,
  nên |G_s| là CẬN TRÊN (an toàn: hiệu chỉnh hơi bảo thủ).
"""
from __future__ import annotations

from typing import List, Sequence, Tuple

import numpy as np

GAN = (2, 3, 4, 5, 7, 10, 15)
GROUP_SIZES = [2] * 7 + [7, 4, 1, 1, 1, 1, 10]
F = sum(GROUP_SIZES)  # 39


def _idx():
    names, k = [], 0
    for L in range(1, 8):
        names += [f"V{L}", f"K{L}"]
    names += [f"gan>={g}" for g in GAN]
    names += ["dem10=0", "dem10=1", "dem10=2", "dem10>=3", "nhay2_t-1", "DB_t-1", "cham_duoi_DB", "kep"]
    names += [f"tong%10={k}" for k in range(10)]
    return {n: i for i, n in enumerate(names)}, names


IDX, NAMES = _idx()


def cross_exclusions() -> List[Tuple[int, int]]:
    ex = set()
    def add(a, b):
        ex.add(tuple(sorted((IDX[a], IDX[b]))))
    for L in range(1, 8):
        for g in GAN:
            if g > L:
                add(f"V{L}", f"gan>={g}")
                add(f"K{L}", f"gan>={g}")
        add("dem10=0", f"V{L}")
        add("dem10=0", f"K{L}")
    for g in GAN:   # g<=10: gan>=g bị kéo theo bởi đếm10=0; g=15: đếm10=0 bị kéo theo bởi gan>=15 — đều thừa
        add("dem10=0", f"gan>={g}")
    for c in ("dem10=1", "dem10=2", "dem10>=3"):
        add(c, "gan>=15")
    for x in ("nhay2_t-1", "DB_t-1"):
        for y in ["K1", "V1", "dem10=0"] + [f"gan>={g}" for g in GAN]:
            add(x, y)
    add("nhay2_t-1", "dem10=1")
    for k in (1, 3, 5, 7, 9):
        add("kep", f"tong%10={k}")
    add("DB_t-1", "cham_duoi_DB")
    return sorted(ex)


def features(tails: np.ndarray, t: int) -> np.ndarray:
    """Ma trận (100, F) Boolean cho kỳ t, CHỈ dùng tails[:t] (tails: mảng (N, 27), cột 0 là ĐB)."""
    if t < 15:
        raise ValueError("cần ít nhất 15 kỳ trước")
    hist = tails[:t]
    X = np.zeros((100, F), dtype=bool)
    nums = np.arange(100)
    cnt = np.zeros((min(len(hist), 15), 100), dtype=int)   # cnt[L-1, n] = số nháy ở kỳ t-L
    for L in range(1, cnt.shape[0] + 1):
        cnt[L - 1] = np.bincount(hist[-L], minlength=100)
    for L in range(1, 8):
        X[:, IDX[f"V{L}"]] = cnt[L - 1] > 0
        X[:, IDX[f"K{L}"]] = cnt[L - 1] == 0
    seen = cnt > 0
    gan = np.where(seen.any(0), seen.argmax(0) + 1, 16)       # số kỳ từ lần về gần nhất (tối đa 16)
    for g in GAN:
        X[:, IDX[f"gan>={g}"]] = gan >= g
    c10 = cnt[:10].sum(0)
    X[:, IDX["dem10=0"]] = c10 == 0
    X[:, IDX["dem10=1"]] = c10 == 1
    X[:, IDX["dem10=2"]] = c10 == 2
    X[:, IDX["dem10>=3"]] = c10 >= 3
    X[:, IDX["nhay2_t-1"]] = cnt[0] >= 2
    db = hist[-1, 0]
    X[:, IDX["DB_t-1"]] = nums == db
    X[:, IDX["cham_duoi_DB"]] = nums % 10 == db % 10
    X[:, IDX["kep"]] = nums // 10 == nums % 10
    for k in range(10):
        X[:, IDX[f"tong%10={k}"]] = (nums // 10 + nums % 10) % 10 == k
    return X


def feature_tensor(tails: np.ndarray, start: int) -> np.ndarray:
    """(T, 100, F) cho các kỳ start..N-1."""
    return np.stack([features(tails, t) for t in range(start, len(tails))])


def presence(tails: np.ndarray, start: int) -> np.ndarray:
    """(T, 100) số nháy thật của n ở kỳ t."""
    return np.stack([np.bincount(tails[t], minlength=100) for t in range(start, len(tails))])


P0 = 1 - 0.99 ** 27   # P(n về >= 1 lần) dưới H0


def best_lift_up_to3(X: np.ndarray, Y: np.ndarray, min_support: int = 1000) -> dict:
    """Điểm trong mẫu của LUẬT TỐT NHẤT với s = 1, 2, 3: lift = tỷ lệ (n về) trong các ô luật bật − P0.
    X: (cells, F) bool; Y: (cells,) bool. Chỉ xét luật hợp lệ (khác nhóm, không vi phạm ràng buộc chéo)
    và có số ô bật >= min_support."""
    Xf = X.astype(np.float32); Yf = Y.astype(np.float32)
    grp = np.array([gi for gi, g in enumerate(GROUP_SIZES) for _ in range(g)])
    ok2 = grp[:, None] != grp[None, :]
    for a, b in cross_exclusions():
        ok2[a, b] = ok2[b, a] = False
    out = {}
    n1 = Xf.sum(0); h1 = (Xf * Yf[:, None]).sum(0)
    m = n1 >= min_support
    out[1] = float((h1[m] / n1[m]).max() - P0) if m.any() else None
    n2 = Xf.T @ Xf; h2 = Xf.T @ (Xf * Yf[:, None])
    iu = np.triu(ok2, 1) & (n2 >= min_support)
    out[2] = float((h2[iu] / n2[iu]).max() - P0) if iu.any() else None
    best3 = -1.0
    for a in range(F):
        Xa = Xf * Xf[:, a:a + 1]
        n3 = Xa.T @ Xf; h3 = Xa.T @ (Xf * Yf[:, None])
        okb = ok2[a][:, None] & ok2[a][None, :] & ok2 & np.triu(np.ones((F, F), bool), 1)
        okb[:a + 1, :] = False
        mask = okb & (n3 >= min_support)
        if mask.any():
            best3 = max(best3, float((h3[mask] / n3[mask]).max()))
    out[3] = best3 - P0 if best3 >= 0 else None
    return out


def null_threshold(n_days: int = 1460, reps: int = 200, seed: int = 0, min_support: int = 1000, q: float = 0.95):
    """tau_s = phân vị q của điểm luật tốt nhất trên `reps` bộ dữ liệu giả lập theo H0 (cùng kích thước)."""
    rng = np.random.default_rng(seed)
    vals = {1: [], 2: [], 3: []}
    for _ in range(reps):
        tails = rng.integers(0, 100, (n_days + 20, 27))
        X = feature_tensor(tails, 20).reshape(-1, F)
        Y = (presence(tails, 20) > 0).reshape(-1)
        b = best_lift_up_to3(X, Y, min_support)
        for s in vals:
            if b[s] is not None:
                vals[s].append(b[s])
    return {s: (float(np.quantile(v, q)), float(np.mean(v)), len(v)) for s, v in vals.items()}
