"""Chứng minh Z3 cho astra_math/hose_order.py: mã hóa lại đúng từng hàm bằng số nguyên Z3
và chứng minh các tính chất cho MỌI giá 1.000–2.000.000đ, MỌI ngân sách 0–10 tỷ.
Chạy: python3 -m astra_math.proofs.hose_order_z3   (cần: pip install z3-solver)"""
import json, sys
from z3 import And, If, Int, Ints, Not, Solver, sat, unsat


def tick(p): return If(p < 10000, 10, If(p < 50000, 50, 100))
def rdown(p): return p - p % tick(p)
def rup(p): return If(p % tick(p) == 0, p, p - p % tick(p) + tick(p))
def valid(p): return p % tick(p) == 0


def run():
    P, B, R = Ints("P B R")
    dom = [P >= 1000, P <= 2_000_000, B >= 0, B <= 10_000_000_000, R >= 1000, R <= 2_000_000]
    p = rdown(P); sh = (B / (p * 100)) * 100
    ceil_ = rdown(R * 107 / 100); floor_ = rup((R * 93 + 99) / 100)
    claims = {
        "buy_order: gia dung buoc gia": valid(p),
        "buy_order: gia <= gia dat, cach < 1 buoc": And(p <= P, P - p < tick(P)),
        "buy_order: lo chan 100": sh % 100 == 0,
        "buy_order: khong vuot ngan sach": sh * p <= B,
        "buy_order: mua toi da so lo": (sh + 100) * p > B,
        "tran/san: dung buoc gia va trong bien do 7%": And(valid(ceil_), valid(floor_), ceil_ * 100 <= R * 107,
                                                              floor_ * 100 >= R * 93, ceil_ >= floor_),
    }
    out = {}
    for name, c in claims.items():
        s = Solver(); s.set("timeout", 120000); s.add(*dom); s.add(Not(c))
        r = s.check()
        out[name] = "DA CHUNG MINH" if r == unsat else ("PHAN VI DU: " + str(s.model()) if r == sat else "KHONG XAC DINH")
    return out


if __name__ == "__main__":
    res = run(); print(json.dumps(res, indent=1, ensure_ascii=False))
    sys.exit(0 if all(v == "DA CHUNG MINH" for v in res.values()) else 1)
