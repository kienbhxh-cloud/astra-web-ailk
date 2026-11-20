"""MASTER-DISCOVERY-001 — H-STREAK: kiểm định toàn bộ "cầu lô vị trí" và giả thuyết "nuôi cầu đang chạy".

Cầu vị trí (dân gian): chọn 2 vị trí chữ số (i, j) trong 107 chữ số của bảng kết quả kỳ t (i ≠ j),
ghép N_t = 10·d_i + d_j, dự báo "lô N_t về ở kỳ t+1". Có 107·106 = 11.342 cầu.
"Cầu đang chạy k ngày" = cầu đã trúng liên tiếp k kỳ gần nhất.
Giả thuyết dân gian: tỷ lệ trúng kỳ tới TĂNG theo k (nuôi cầu đã thông 4–5 ngày).
H0: kết quả kỳ t+1 độc lập với quá khứ → tỷ lệ trúng ≈ P(lô cho trước về) với MỌI k.

Chạy: PYTHONPATH=. python3 PNP_XSMB_RESEARCH/discovery_cau_vi_tri.py <csv> [--sim SEED]
Chỉ dùng dữ liệu kỳ t để dự báo kỳ t+1; không có tham số nào được tinh chỉnh.
"""
import csv, json, sys
import numpy as np

W = [5] * 10 + [4] * 10 + [3] * 3 + [2] * 4   # 107 chữ số


def load_digits(path):
    rows = list(csv.reader(open(path)))[1:]
    dig = np.array([[int(c) for v, w in zip(r[1:28], W) for c in v.strip().zfill(w)] for r in rows], dtype=np.int8)
    return [r[0] for r in rows], dig


def sim_digits(n, seed):
    return None, np.random.default_rng(seed).integers(0, 10, size=(n, sum(W)), dtype=np.int8)


def tails_from_digits(dig):
    # chữ số cuối của mỗi giải: vị trí kết thúc cumsum(W)-1
    ends = np.cumsum(W) - 1
    return dig[:, ends - 1].astype(np.int16) * 10 + dig[:, ends]


def run(dig, kmax=12):
    n, m = dig.shape
    T = tails_from_digits(dig)
    P = np.zeros((n, 100), dtype=bool)
    np.put_along_axis(P, T.astype(np.int64), True, axis=1)
    ii, jj = np.where(~np.eye(m, dtype=bool))            # 11.342 cầu
    streak = np.zeros(len(ii), dtype=np.int32)
    tot = np.zeros(kmax + 1, dtype=np.int64); hit = np.zeros(kmax + 1, dtype=np.int64)
    max_streak_day = []
    for t in range(n - 1):
        N = dig[t, ii].astype(np.int64) * 10 + dig[t, jj]
        h = P[t + 1, N]
        k = np.minimum(streak, kmax)
        np.add.at(tot, k, 1); np.add.at(hit, k, h)
        streak = np.where(h, streak + 1, 0)
        max_streak_day.append(int(streak.max()))
    u = P.sum(1)[1:]
    base = float((1 - 0.99 ** 27))                       # P(1 lô cho trước về) dưới H0
    base_u = float(np.mean(u / 100.0))                   # mốc thực nghiệm theo u (= E[|S|]/100)
    return dict(so_cau=int(len(ii)), so_ky=int(n),
                theo_k={int(k): dict(lan=int(tot[k]), trung=int(hit[k]), ty_le=round(hit[k] / tot[k], 5) if tot[k] else None)
                        for k in range(kmax + 1)},
                moc_ly_thuyet=round(base, 5), moc_theo_u=round(base_u, 5),
                ky_vong_so_cau_chay_k_ngay={k: round(len(ii) * base ** k, 2) for k in (3, 4, 5, 6, 7, 8)},
                chuoi_dai_nhat_toan_bo=int(max(max_streak_day)))


if __name__ == "__main__":
    if "--sim" in sys.argv:
        seed = int(sys.argv[sys.argv.index("--sim") + 1]); _, dig = sim_digits(7622, seed); src = f"gia_lap_seed_{seed}"
    else:
        _, dig = load_digits(sys.argv[1]); src = sys.argv[1]
    res = run(dig); res["nguon"] = src
    print(json.dumps(res, ensure_ascii=False, indent=1))
