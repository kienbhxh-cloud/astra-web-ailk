"""ASTRA STOCK — quy trình đầu-cuối bằng ASTRA Math (minh họa trên dữ liệu 30 mã của Gemini).

  1. Tối ưu danh mục CP-SAT (so với baseline tham lam)
  2. Sinh lệnh mua và kiểm từng lệnh qua lưới an toàn HOSE (hàm đã chứng minh Z3)
  3. Kiểm thử stress: xác suất nhiều mã cùng giảm, phân phối lỗ, VaR/ES 99% CHÍNH XÁC trong mô hình;
     so sánh với Monte Carlo.

GIẢ ĐỊNH (phải thay bằng ước lượng thật trước khi dùng):
  - lợi suất kỳ vọng r = (alpha - 0.60) * 0.20 mỗi kỳ; alpha là điểm minh họa, không phải dự báo.
  - "giảm sâu" = giảm 2*vol% trong phiên; P(giảm sâu | ngành bình thường) = 1%*vol/2,
    P(giảm sâu | ngành sốc) = min(0.6, 0.2*vol); sốc thị trường 5%; sốc ngành 3% (bình thường) / 50% (khi thị trường sốc).
Chạy: python3 -m astra_math.demo_stock [--json out.json]
"""
import csv, json, os, sys, time
import numpy as np
from astra_math import portfolio as pf, hose_order as ho, tail_risk as tr

HERE = os.path.dirname(__file__)
rows = list(csv.DictReader(open(os.path.join(HERE, "data", "hose30_minh_hoa.csv"))))
vol = {r["ticker"]: float(r["vol"]) for r in rows}
assets = [pf.Asset(r["ticker"], r["sector"], int(r["price"]), (float(r["alpha"]) - 0.6) * 0.2,
                   float(r["adv20"]) * 1e9, r["restricted"] == "1") for r in rows]
pairs = [("TCB", "MBB"), ("HSG", "NKG"), ("SSI", "HCM"), ("VHM", "VIC"), ("MWG", "PNJ")]
C = pf.Constraints(exclusive_pairs=pairs)
out = {"gia_dinh": "xem docstring; du lieu minh hoa, chua co ngay/nguon gia"}

# 1. Tối ưu
opt = pf.optimize(assets, C, time_limit=20); g = pf.greedy(assets, C)
out["1_toi_uu"] = {"trang_thai": opt["status"], "giay": round(opt["seconds"], 3),
    "loi_nhuan_ky_vong_rong_CPSAT": round(opt["objective"]), "loi_nhuan_ky_vong_rong_tham_lam": round(g["objective"]),
    "chenh_lech_pct": round(100 * (opt["objective"] - g["objective"]) / abs(g["objective"]), 2),
    "danh_muc": opt["shares"], "vi_pham": opt["errors"]}

# 2. Lệnh + lưới an toàn
px = {a.ticker: a.price for a in assets}
orders = []
for t, sh in opt["shares"].items():
    budget = sh * px[t]
    p, s = ho.buy_order(budget, px[t])
    chk = ho.validate_order("BUY", p, s, px[t], cash_vnd=C.capital, max_order_vnd=int(C.w_max * C.capital))
    orders.append({"ma": t, "gia": p, "khoi_luong": s, "hop_le": chk.ok, "loi": chk.errors})
bad = ho.validate_order("BUY", 50050, 307, 50000)
out["2_lenh"] = {"lenh": orders, "vi_du_lenh_loi_bi_chan": {"gia": 50050, "kl": 307, "loi": bad.errors}}

# 3. Stress test chính xác trên danh mục đã tối ưu (lỗ tính theo triệu đồng)
held = [a for a in assets if a.ticker in opt["shares"]]
sectors = sorted({a.sector for a in assets})
stocks = []
for a in held:
    v = opt["shares"][a.ticker] * a.price
    stocks.append(tr.Stock(a.ticker, a.sector, 0.01 * vol[a.ticker] / 2, min(0.6, 0.2 * vol[a.ticker]),
                           loss_if_down=int(round(v * 2 * vol[a.ticker] / 100 / 1e6))))
model = tr.HierarchicalModel(0.05, {s: 0.03 for s in sectors}, {s: 0.5 for s in sectors}, stocks)
t0 = time.time(); dist_k = tr.count_down_distribution(model); dist_L = tr.loss_distribution(model); t_ex = time.time() - t0
var, es = tr.var_es(dist_L, 0.99)
K = tr.monte_carlo_count(model, 20_000, seed=1)
out["3_stress"] = {"giay_tinh_chinh_xac": round(t_ex, 4),
    "P_ít_nhất_k_mã_giảm_sâu": {k: tr.tail_prob(dist_k, k) for k in range(1, len(stocks) + 1)},
    "MonteCarlo_20000_mau": {k: float((K >= k).mean()) for k in range(1, len(stocks) + 1)},
    "VaR99_trieu_dong": var, "ES99_trieu_dong": round(es, 2), "lo_toi_da_trieu_dong": len(dist_L) - 1,
    "phan_ra_nguyen_nhan_P>=3": tr.scenario_attribution(model, 3)}

print(json.dumps(out, indent=1, ensure_ascii=False))
if "--json" in sys.argv:
    json.dump(out, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1, ensure_ascii=False)
