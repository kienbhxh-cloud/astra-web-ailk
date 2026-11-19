"""ASTRA LÔ XSMB — Bộ kiểm định chính xác (ASTRA Math, U8).

Mục đích: đo lường CHÍNH XÁC và chống tự lừa mình. Module này KHÔNG dự đoán kết quả xổ số.
Giả định chuẩn: xổ số công bằng, 27 giải độc lập, 2 số cuối mỗi giải đều trên 00..99.

Chức năng:
  1. Xác suất chính xác (phân số): lô, lô xiên k, đề; phân phối số nháy; giá trị kỳ vọng theo tỷ lệ trả thưởng.
  2. p-value nhị thức chính xác cho thành tích "trúng X/N ngày".
  3. Hiệu chỉnh đa kiểm định: Bonferroni, Šidák, Holm, Benjamini–Hochberg.
  4. Đánh giá một phương pháp chọn số trên dữ liệu thật, so với baseline ngẫu nhiên (kiểm định chính xác + hoán vị).
  5. Kiểm tra độ công bằng dữ liệu lịch sử (χ² trên 100 số).
  6. Sổ ĐĂNG KÝ TRƯỚC có mã băm SHA-256 nối chuỗi: chỉ chấm trên kỳ quay SAU thời điểm đăng ký.

Không phụ thuộc thư viện ngoài (chỉ thư viện chuẩn Python).
Chạy thử: python3 -m astra_math.xsmb_audit --demo
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from dataclasses import dataclass
from datetime import date, datetime, timezone
from fractions import Fraction
from typing import Callable, Dict, Iterable, List, Optional, Sequence

N_PRIZES = 27      # số giải XSMB mỗi ngày
N_NUMBERS = 100    # 00..99


# ---------------------------------------------------------------- 1. Xác suất chính xác
def p_lo(n_prizes: int = N_PRIZES) -> Fraction:
    """P(một số cho trước về ít nhất 1 lần trong ngày)."""
    return 1 - Fraction(N_NUMBERS - 1, N_NUMBERS) ** n_prizes


def p_xien(k: int, n_prizes: int = N_PRIZES) -> Fraction:
    """P(cả k số KHÁC NHAU cho trước đều về ít nhất 1 lần) — bao hàm–loại trừ, chính xác."""
    return sum(((-1) ** j) * math.comb(k, j) * Fraction(N_NUMBERS - j, N_NUMBERS) ** n_prizes for j in range(k + 1))


def p_de() -> Fraction:
    """P(2 số cuối giải Đặc biệt trùng số đã chọn)."""
    return Fraction(1, N_NUMBERS)


def nhay_distribution(n_prizes: int = N_PRIZES) -> List[Fraction]:
    """dist[j] = P(một số về đúng j nháy trong ngày) ~ Nhị thức(27, 1/100)."""
    p = Fraction(1, N_NUMBERS)
    return [math.comb(n_prizes, j) * p ** j * (1 - p) ** (n_prizes - j) for j in range(n_prizes + 1)]


def expected_value(stake: float, payout_per_hit: float, kind: str = "lo_nhay", k: int = 2) -> float:
    """Lời/lỗ kỳ vọng của MỘT cược (cùng đơn vị tiền).

    kind: 'lo_nhay' (trả theo số nháy), 'lo' (trả 1 lần nếu về), 'xien' (k số), 'de'.
    payout_per_hit: tiền thưởng nhận về cho mỗi lần trúng (không gồm tiền cược nếu nhà cái không hoàn).
    Nhập tỷ lệ trả thưởng THỰC TẾ của dự án; module không giả định tỷ lệ nào.
    """
    if kind == "lo_nhay":
        e_hits = Fraction(N_PRIZES, N_NUMBERS)
        return float(e_hits) * payout_per_hit - stake
    prob = {"lo": p_lo(), "xien": p_xien(k), "de": p_de()}[kind]
    return float(prob) * payout_per_hit - stake


def break_even_payout(stake: float, kind: str = "lo_nhay", k: int = 2) -> float:
    """Tiền thưởng tối thiểu để kỳ vọng = 0 (hòa vốn về lâu dài)."""
    if kind == "lo_nhay":
        return stake / float(Fraction(N_PRIZES, N_NUMBERS))
    prob = {"lo": p_lo(), "xien": p_xien(k), "de": p_de()}[kind]
    return stake / float(prob)


# ---------------------------------------------------------------- 2. p-value nhị thức
def binom_tail(n: int, k: int, p) -> Fraction:
    """P(X >= k), X ~ Nhị thức(n, p), chính xác nếu p là Fraction.

    Chi phí tăng rất nhanh theo n (mẫu số cỡ 100^(27n)); chỉ dùng cho n nhỏ.
    Với dữ liệu nhiều ngày dùng binom_tail_float."""
    p = Fraction(p)
    return sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(k, n + 1))


def binom_tail_float(n: int, k: int, p) -> float:
    """P(X >= k), X ~ Nhị thức(n, p) — tính trong không gian log, độ chính xác ~1e-12 tương đối,
    chạy nhanh với n hàng chục nghìn (dữ liệu XSMB nhiều năm)."""
    p = float(p)
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    if p <= 0.0:
        return 0.0
    if p >= 1.0:
        return 1.0
    lp, lq = math.log(p), math.log1p(-p)
    base = math.lgamma(n + 1)
    terms = [base - math.lgamma(j + 1) - math.lgamma(n - j + 1) + j * lp + (n - j) * lq for j in range(k, n + 1)]
    m = max(terms)
    return min(1.0, math.exp(m) * math.fsum(math.exp(t - m) for t in terms))


# ---------------------------------------------------------------- 3. Đa kiểm định
def fwer_independent(p_single: float, m: int) -> float:
    """P(ít nhất 1 'thắng giả' trong m phương pháp ĐỘC LẬP) — chặn trên thực tế khi các cầu tương quan."""
    return 1 - (1 - p_single) ** m


def bonferroni_threshold(alpha: float, m: int) -> float:
    return alpha / m


def sidak_threshold(alpha: float, m: int) -> float:
    return 1 - (1 - alpha) ** (1 / m)


def holm(pvalues: Sequence[float], alpha: float = 0.05) -> List[bool]:
    """Holm–Bonferroni: trả về True cho kiểm định bị bác bỏ H0 (kiểm soát FWER)."""
    order = sorted(range(len(pvalues)), key=lambda i: pvalues[i])
    rej = [False] * len(pvalues)
    m = len(pvalues)
    for r, i in enumerate(order):
        if pvalues[i] <= alpha / (m - r):
            rej[i] = True
        else:
            break
    return rej


def benjamini_hochberg(pvalues: Sequence[float], q: float = 0.05) -> List[bool]:
    """BH: kiểm soát tỷ lệ phát hiện sai (FDR)."""
    m = len(pvalues)
    order = sorted(range(m), key=lambda i: pvalues[i])
    kmax = 0
    for r, i in enumerate(order, 1):
        if pvalues[i] <= q * r / m:
            kmax = r
    rej = [False] * m
    for r, i in enumerate(order, 1):
        if r <= kmax:
            rej[i] = True
    return rej


def benjamini_yekutieli(pvalues: Sequence[float], q: float = 0.05) -> List[bool]:
    """BY: kiểm soát FDR dưới phụ thuộc TÙY Ý giữa các cầu (BH chỉ đảm bảo khi độc lập/PRDS).
    Tương đương BH với q thay bằng q / H_m, H_m = 1 + 1/2 + ... + 1/m."""
    m = len(pvalues)
    if m == 0:
        return []
    h_m = math.fsum(1.0 / i for i in range(1, m + 1))
    return benjamini_hochberg(pvalues, q / h_m)


# ---------------------------------------------------------------- 3b. E-process (giám sát liên tục)
DEFAULT_LAMBDAS = (0.01, 0.02, 0.044, 0.1, 0.2)


def eprocess_mean(ys: Sequence[float], mu: float, lambdas: Sequence[float] = DEFAULT_LAMBDAS,
                  y_min: float = 0.0) -> List[float]:
    """E-process kiểm định H0: E[Y_t | quá khứ] <= mu (vd số nháy/kỳ của bộ 5 số, mu = 1,35).

    W_t = trung bình theo lambda của tích (1 + lambda*(Y_s - mu)). Mỗi tích là siêu martingale
    không âm dưới H0 (cần lambda <= 1/(mu - y_min)), nên trung bình cũng vậy. Theo bất đẳng thức
    Ville: P_H0(tồn tại t: W_t >= 1/alpha) <= alpha — hợp lệ ở MỌI thời điểm dừng, xem bao nhiêu lần
    cũng được. Với m thuật toán khóa song song: bác bỏ khi W_t >= m/alpha (Bonferroni).
    Danh sách lambda phải được KHÓA trước khi chấm."""
    lam_max = 1.0 / (mu - y_min)
    if any(l < 0 or l > lam_max for l in lambdas):
        raise ValueError(f"lambda phải trong [0, {lam_max:.4f}]")
    prods = [1.0] * len(lambdas)
    path = []
    for y in ys:
        prods = [w * (1.0 + l * (y - mu)) for w, l in zip(prods, lambdas)]
        path.append(math.fsum(prods) / len(prods))
    return path


def eprocess_any_hit(hits: Sequence[int], p0s: Sequence[float],
                     lambdas: Sequence[float] = (0.05, 0.1, 0.2, 0.5, 1.0)) -> List[float]:
    """E-process cho chỉ số 'bộ k số có >= 1 số về' với mốc từng kỳ p0_t = 1 - C(100-u_t,k)/C(100,k).
    Dùng biến chuẩn hóa Y=(hit - p0)/p0 >= -1, nên lambda trong [0, 1]."""
    if any(l < 0 or l > 1 for l in lambdas):
        raise ValueError("lambda phải trong [0, 1]")
    prods = [1.0] * len(lambdas)
    path = []
    for h, p0 in zip(hits, p0s):
        prods = [w * (1.0 + l * (h - p0) / p0) for w, l in zip(prods, lambdas)]
        path.append(math.fsum(prods) / len(prods))
    return path


def p_set_any_given_u(u: int, k: int = 5) -> Fraction:
    """Mốc chính xác của kỳ có u đuôi khác nhau: P(bộ k số khác nhau có >= 1 số về)."""
    return 1 - Fraction(math.comb(N_NUMBERS - u, k), math.comb(N_NUMBERS, k))


# ---------------------------------------------------------------- Dữ liệu
@dataclass
class Draw:
    day: date
    numbers: List[int]   # 27 số 2 chữ số cuối; numbers[0] = giải Đặc biệt

    @property
    def de(self) -> int:
        return self.numbers[0]


def last2(x: str) -> int:
    s = "".join(ch for ch in str(x) if ch.isdigit())
    if not s:
        raise ValueError(f"giá trị giải không hợp lệ: {x!r}")
    return int(s[-2:])


# Số chữ số chuẩn của 27 giải theo thứ tự ĐB, G1, G2(2), G3(6), G4(4), G5(6), G6(3), G7(4)
PRIZE_DIGITS = [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 3, 3, 3, 2, 2, 2, 2]


def load_draws(path: str, strict_lengths: bool = False) -> List[Draw]:
    """CSV: cột đầu 'ngay' (YYYY-MM-DD), sau đó 27 cột giải (cột thứ 2 là giải Đặc biệt).
    Giá trị giải có thể là số đầy đủ (vd 12345); chỉ lấy 2 chữ số cuối.

    Luôn từ chối: thiếu/thừa giải, ngày trùng, và HÀNG GIẢ (27 giá trị giống hệt nhau,
    vd hàng '0,0,...,0' mà một số mã chèn cho ngày cần dự báo). Xác suất 27 giải thật
    trùng hệt nhau ~1e-52, nên đây gần như chắc chắn là placeholder, không phải quan sát.
    strict_lengths=True: kiểm tra thêm số chữ số từng giải (5/4/3/2), bắt lỗi mất số 0 đầu."""
    out = []
    with open(path, newline="", encoding="utf-8") as f:
        rd = csv.reader(f)
        header = next(rd)
        for row in rd:
            if not row or not row[0].strip():
                continue
            vals = [v.strip() for v in row[1:]]
            while vals and vals[-1] == "":          # chỉ bỏ ô trống ở CUỐI dòng
                vals.pop()
            if len(vals) != N_PRIZES:
                raise ValueError(f"ngày {row[0]}: có {len(vals)} cột giải, cần {N_PRIZES}")
            trong = [i + 1 for i, v in enumerate(vals) if v == ""]
            if trong:                               # ô trống giữa dòng làm lệch cột -> báo lỗi
                raise ValueError(f"ngày {row[0]}: ô trống ở giải thứ {trong}")
            if len(set(vals)) == 1:
                raise ValueError(f"ngày {row[0]}: 27 giải giống hệt nhau ({vals[0]!r}) — "
                                 "nghi hàng giả/placeholder, không phải kết quả quay thật")
            if strict_lengths:
                sai = [i for i, (v, n) in enumerate(zip(vals, PRIZE_DIGITS)) if len(v) != n]
                if sai:
                    raise ValueError(f"ngày {row[0]}: sai số chữ số ở giải thứ {[i + 1 for i in sai]}")
            out.append(Draw(date.fromisoformat(row[0].strip()), [last2(v) for v in vals]))
    out.sort(key=lambda d: d.day)
    days = [d.day for d in out]
    if len(set(days)) != len(days):
        raise ValueError("có ngày bị trùng trong dữ liệu")
    return out


def date_gaps(draws: List[Draw], min_gap_days: int = 2) -> List[dict]:
    """Liệt kê các khoảng trống lịch (>= min_gap_days ngày giữa hai kỳ liền nhau).
    Nghỉ Tết (~4 ngày) là bình thường; khoảng trống khác phải được giải thích trước khi phân tích."""
    return [{"tu": a.day.isoformat(), "den": b.day.isoformat(), "so_ngay_thieu": (b.day - a.day).days - 1}
            for a, b in zip(draws, draws[1:]) if (b.day - a.day).days >= min_gap_days]


def simulate_draws(n_days: int, seed: int = 0, start: date = date(2025, 1, 1)) -> List[Draw]:
    """Sinh dữ liệu xổ số CÔNG BẰNG (dùng để kiểm thử và làm baseline)."""
    r = random.Random(seed)
    return [Draw(date.fromordinal(start.toordinal() + i), [r.randrange(100) for _ in range(N_PRIZES)])
            for i in range(n_days)]


# ---------------------------------------------------------------- 4. Đánh giá phương pháp
Strategy = Callable[[List[Draw]], List[int]]   # nhận lịch sử TRƯỚC ngày cần chọn, trả về các số chọn


@dataclass
class EvalResult:
    days: int
    picks_per_day: int
    hit_days: int                 # số ngày có ít nhất 1 số chọn về (lô)
    total_hits: int               # tổng số nháy trúng
    expected_hit_days: float
    p_value_exact: float          # P(ngẫu nhiên đạt >= hit_days)
    p_value_permutation: Optional[float]
    note: str

    def as_dict(self):
        return self.__dict__.copy()


def _p_day_any(picks: int) -> Fraction:
    """P(ít nhất 1 trong 'picks' số khác nhau về trong ngày)."""
    return 1 - Fraction(N_NUMBERS - picks, N_NUMBERS) ** N_PRIZES


def evaluate_strategy(draws: List[Draw], strategy: Strategy, warmup: int = 0, permutations: int = 0,
                      seed: int = 0) -> EvalResult:
    """Chấm phương pháp theo kiểu đi tới (walk-forward): ngày t chỉ được dùng dữ liệu < t.
    Phương pháp phải trả về cùng số lượng số khác nhau mỗi ngày."""
    hit_days = total = 0
    k_set = None
    picks_log = []
    for t in range(warmup, len(draws)):
        picks = sorted(set(int(x) % 100 for x in strategy(draws[:t])))
        if k_set is None:
            k_set = len(picks)
        if len(picks) != k_set:
            raise ValueError("phương pháp phải chọn cùng số lượng số mỗi ngày")
        picks_log.append(picks)
        nums = draws[t].numbers
        h = sum(nums.count(x) for x in picks)
        total += h
        hit_days += h > 0
    n = len(picks_log)
    p_day = _p_day_any(k_set)
    p_exact = binom_tail_float(n, hit_days, p_day)
    p_perm = None
    if permutations:
        # baseline: cùng số lượng số, chọn ngẫu nhiên mỗi ngày, trên CÙNG dữ liệu
        r = random.Random(seed)
        ge = 0
        for _ in range(permutations):
            hd = 0
            for t in range(warmup, len(draws)):
                pk = r.sample(range(100), k_set)
                hd += any(x in draws[t].numbers for x in pk)
            ge += hd >= hit_days
        p_perm = (ge + 1) / (permutations + 1)
    return EvalResult(n, k_set, hit_days, total, n * float(p_day), p_exact, p_perm,
                      "p nhỏ CHƯA là bằng chứng nếu đã thử nhiều phương pháp: phải hiệu chỉnh (holm/BH) "
                      "và chỉ tính trên kỳ quay sau khi đăng ký trước")


# ---------------------------------------------------------------- 5. Độ công bằng dữ liệu
def _gammaincc(a: float, x: float) -> float:
    """Q(a, x) = Γ(a, x)/Γ(a) — hàm gamma không đầy đủ chuẩn hóa trên (Numerical Recipes)."""
    if x < 0 or a <= 0:
        raise ValueError
    if x == 0:
        return 1.0
    gln = math.lgamma(a)
    if x < a + 1:  # chuỗi
        ap, s, d = a, 1 / a, 1 / a
        for _ in range(10000):
            ap += 1; d *= x / ap; s += d
            if abs(d) < abs(s) * 1e-15:
                break
        return 1 - s * math.exp(-x + a * math.log(x) - gln)
    b = x + 1 - a; c = 1 / 1e-300; d = 1 / b; h = d  # phân số liên tục
    for i in range(1, 10000):
        an = -i * (i - a); b += 2
        d = an * d + b; d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c; c = 1e-300 if abs(c) < 1e-300 else c
        d = 1 / d; de = d * c; h *= de
        if abs(de - 1) < 1e-15:
            break
    return math.exp(-x + a * math.log(x) - gln) * h


def chi2_sf(stat: float, dof: int) -> float:
    return _gammaincc(dof / 2, stat / 2)


def fairness_test(draws: List[Draw]) -> Dict[str, float]:
    """χ² độ phù hợp: 100 số có xuất hiện đều không? (tất cả 27 giải gộp lại)."""
    cnt = [0] * N_NUMBERS
    for d in draws:
        for x in d.numbers:
            cnt[x] += 1
    n = sum(cnt); e = n / N_NUMBERS
    stat = sum((c - e) ** 2 / e for c in cnt)
    p = chi2_sf(stat, N_NUMBERS - 1)
    top = sorted(range(100), key=lambda i: -cnt[i])[:5]
    return {"so_ngay": len(draws), "so_lan_quay": n, "chi2": round(stat, 3), "bac_tu_do": 99, "p_value": p,
            "so_ve_nhieu_nhat": {f"{i:02d}": cnt[i] for i in top},
            "dien_giai": ("p < 0,001: dữ liệu lệch bất thường — kiểm tra lỗi nhập/thiếu dữ liệu TRƯỚC, không suy ra 'dự đoán được'"
                          if p < 0.001 else "không phát hiện lệch so với xổ số công bằng")}


# ---------------------------------------------------------------- 6. Sổ đăng ký trước
def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


class Registry:
    """Sổ đăng ký trước, lưu JSON. Mỗi bản ghi băm SHA-256 và nối với bản ghi trước (chống sửa ngầm)."""

    def __init__(self, path: str):
        self.path = path
        try:
            with open(path, encoding="utf-8") as f:
                self.records = json.load(f)
        except FileNotFoundError:
            self.records = []

    def register(self, name: str, rule_text: str, code_text: str, picks_per_day: int, test_days: int,
                 bet_kind: str = "lo", alpha: float = 0.05, now: Optional[datetime] = None) -> dict:
        now = now or datetime.now(timezone.utc)
        rec = {"id": f"REG-{len(self.records) + 1:04d}", "ten": name, "quy_tac": rule_text,
               "sha256_ma_nguon": _sha(code_text), "so_so_moi_ngay": picks_per_day, "so_ngay_thu": test_days,
               "loai_cuoc": bet_kind, "alpha": alpha, "dang_ky_luc_utc": now.isoformat(timespec="seconds"),
               "cham_tu_ngay": date.fromordinal(now.date().toordinal() + 1).isoformat(),
               "ban_ghi_truoc": self.records[-1]["sha256"] if self.records else None}
        rec["sha256"] = _sha(json.dumps(rec, sort_keys=True, ensure_ascii=False))
        self.records.append(rec)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.records, f, indent=1, ensure_ascii=False)
        return rec

    def verify_chain(self) -> bool:
        prev = None
        for r in self.records:
            body = {k: v for k, v in r.items() if k != "sha256"}
            if body.get("ban_ghi_truoc") != prev or _sha(json.dumps(body, sort_keys=True, ensure_ascii=False)) != r["sha256"]:
                return False
            prev = r["sha256"]
        return True

    def evaluate(self, reg_id: str, draws: List[Draw], strategy: Strategy, code_text: str) -> dict:
        rec = next(r for r in self.records if r["id"] == reg_id)
        if _sha(code_text) != rec["sha256_ma_nguon"]:
            raise ValueError("mã nguồn đã bị thay đổi so với lúc đăng ký — kết quả không hợp lệ")
        start = date.fromisoformat(rec["cham_tu_ngay"])
        idx = next((i for i, d in enumerate(draws) if d.day >= start), len(draws))
        end = min(len(draws), idx + rec["so_ngay_thu"])
        res = evaluate_strategy(draws[:end], strategy, warmup=idx)
        out = {"dang_ky": rec["id"], "so_ngay_da_cham": res.days, "du_so_ngay": res.days >= rec["so_ngay_thu"],
               **res.as_dict()}
        out["dat"] = bool(out["du_so_ngay"] and res.p_value_exact < rec["alpha"])
        return out


# ---------------------------------------------------------------- Demo
def _demo():
    print("== 1. Xác suất chính xác (xổ số công bằng) ==")
    print(f"Lô 1 số      : {float(p_lo()):.4%}")
    for k in (2, 3, 4):
        print(f"Lô xiên {k}    : {float(p_xien(k)):.4%}")
    print(f"Đề          : {float(p_de()):.2%}")
    nd = nhay_distribution()
    print("Phân phối nháy:", {j: f"{float(nd[j]):.4%}" for j in range(4)})
    print("Tiền thưởng hòa vốn cho cược lô 1 đơn vị (trả theo nháy):", round(break_even_payout(1), 4), "đơn vị")
    print("\n== 2–3. 'Cầu thắng' và đa kiểm định ==")
    p12 = float(binom_tail(30, 12, p_lo()))
    print(f"P(cầu ngẫu nhiên trúng >= 12/30 ngày) = {p12:.4%}")
    for m in (10, 100, 1000):
        print(f"  quét {m:>5} cầu độc lập: P(có ít nhất 1 cầu 'thắng' giả) = {fwer_independent(p12, m):.2%}; "
              f"ngưỡng Šidák = {sidak_threshold(0.05, m):.2e}")
    print("\n== 4. Thử 200 'cầu' trên 365 ngày dữ liệu CÔNG BẰNG giả lập ==")
    draws = simulate_draws(365, seed=2026)
    pvals = []
    for s in range(200):
        r = random.Random(s)
        strat = (lambda hist, r=r: r.sample(range(100), 1))
        pvals.append(evaluate_strategy(draws, strat, warmup=30).p_value_exact)
    print(f"  cầu 'tốt nhất' p = {min(pvals):.4f}; số cầu p<0,05 khi KHÔNG hiệu chỉnh: {sum(p < 0.05 for p in pvals)}"
          f"; sau Holm: {sum(holm(pvals))}; sau BH: {sum(benjamini_hochberg(pvals))}")
    print("\n== 5. Độ công bằng dữ liệu giả lập ==")
    print(fairness_test(draws))


if __name__ == "__main__":
    import sys
    a = sys.argv
    if "--demo" in a:
        _demo()
    elif "--csv" in a:
        draws = load_draws(a[a.index("--csv") + 1], strict_lengths="--strict" in a)
        print(f"Đã nạp {len(draws)} ngày: {draws[0].day} → {draws[-1].day}")
        print("Khoảng trống lịch:", json.dumps(date_gaps(draws), ensure_ascii=False))
        print("Độ công bằng:", json.dumps(fairness_test(draws), ensure_ascii=False, indent=1))
        if "--cau" in a:  # kiểm 1 cầu đơn giản: lặp lại 2 số cuối giải ĐB hôm trước
            res = evaluate_strategy(draws, lambda h: [h[-1].de], warmup=1)
            print("Cầu 'lặp lại đề hôm qua' (ví dụ):", json.dumps(res.as_dict(), ensure_ascii=False, indent=1))
    else:
        print(__doc__)
        print("Cách dùng: python3 -m astra_math.xsmb_audit --demo | --csv ket_qua.csv [--strict] [--cau]")
