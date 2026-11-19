"""E-1 (đăng ký trước 20/11/2026): bộ 5 số 'nóng' theo 90 kỳ gần nhất, chấm tương lai bằng e-process.

Quy tắc (KHÓA): với kỳ t, đếm số lần xuất hiện của 00..99 (2 số cuối của 27 giải) trong 90 KỲ QUAY
liền trước t (theo thứ tự kỳ, không theo ngày lịch). Chọn 5 số có số lần lớn nhất; hòa thì số nhỏ hơn trước.
Chỉ số chính: số nháy Y_t của bộ 5 tại kỳ t. H0: E[Y_t | quá khứ] <= 1,35.
E-process: xsmb_audit.eprocess_mean(Y, 1.35) với lambda mặc định (0,01; 0,02; 0,044; 0,1; 0,2).
Bác bỏ H0 khi W_t >= 80 (= 20 x 4: dành chỗ cho E-1 + 3 thuật toán F1/F2/F3, Bonferroni, alpha tổng 0,05).
Chỉ số phụ (mô tả, không tiêu alpha): hiệu nháy nóng90 - lạnh90, eprocess_mean(D, 0, lambdas=(0.002,0.005,0.01,0.02,0.035), y_min=-27).
Kỳ chấm đầu tiên: kỳ quay ngày 20/11/2026. Không dừng sớm vì kết quả thuận lợi trừ khi W_t >= 80.
"""
from __future__ import annotations
import csv, sys
from typing import List, Sequence


def load_tails(path: str):
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig", newline="")))
    cols = [c for c in rows[0] if c != "date"]
    return [r["date"] for r in rows], [[int(r[c][-2:]) for c in cols] for r in rows]


def pick(history: Sequence[Sequence[int]], window: int = 90, k: int = 5, hot: bool = True) -> List[int]:
    cnt = [0] * 100
    for day in history[-window:]:
        for v in day:
            cnt[v] += 1
    key = (lambda v: (-cnt[v], v)) if hot else (lambda v: (cnt[v], v))
    return sorted(sorted(range(100), key=key)[:k])


if __name__ == "__main__":
    dates, D = load_tails(sys.argv[1])
    print("du lieu den", dates[-1], "| hot90:", pick(D), "| cold90:", pick(D, hot=False))
