"""ASTRA STOCK — Lưới an toàn lệnh HOSE (U3). Các hàm ở đây đã được chứng minh bằng Z3
(xem astra_math/proofs/hose_order_z3.py) cho MỌI giá 1.000–2.000.000đ và MỌI ngân sách 0–10 tỷ:
đúng bước giá, lô chẵn 100, không vượt ngân sách, mua tối đa, giá trần/sàn nằm trong biên độ.

Quy tắc giả định (cần đối chiếu văn bản HOSE hiện hành trước khi dùng thật):
  bước giá 10đ (<10.000), 50đ (10.000–49.950), 100đ (>=50.000); lô 100; biên độ ±7%.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List

LOT = 100
BAND_PCT = 7


def tick_size(price: int) -> int:
    if price < 10_000:
        return 10
    if price < 50_000:
        return 50
    return 100


def round_down_tick(price: int) -> int:
    return price - price % tick_size(price)


def round_up_tick(price: int) -> int:
    r = price % tick_size(price)
    return price if r == 0 else price - r + tick_size(price)


def is_valid_tick(price: int) -> bool:
    return price > 0 and price % tick_size(price) == 0


def ceiling_price(ref: int, band_pct: int = BAND_PCT) -> int:
    return round_down_tick(ref * (100 + band_pct) // 100)


def floor_price(ref: int, band_pct: int = BAND_PCT) -> int:
    # Làm tròn LÊN phép chia trước (Z3 tìm ra lỗi khi làm tròn xuống trước, ví dụ ref=7.570)
    return round_up_tick(-(-ref * (100 - band_pct) // 100))


def buy_order(budget_vnd: int, limit_price: int):
    """Trả về (giá đặt hợp lệ, số cổ phiếu) tối đa trong ngân sách. Giá được làm tròn XUỐNG bước giá."""
    p = round_down_tick(limit_price)
    shares = (budget_vnd // (p * LOT)) * LOT
    return p, shares


@dataclass
class OrderCheck:
    ok: bool
    errors: List[str]


def validate_order(side: str, price: int, shares: int, ref_price: int, cash_vnd: int | None = None,
                   max_order_vnd: int | None = None, restricted: bool = False) -> OrderCheck:
    """Kiểm tra lệnh trước khi đẩy sàn. Trả về danh sách lỗi (rỗng nếu hợp lệ)."""
    e = []
    if side not in ("BUY", "SELL"):
        e.append("side phải là BUY hoặc SELL")
    if not is_valid_tick(price):
        e.append(f"giá {price} sai bước giá {tick_size(price)}đ")
    if shares <= 0 or shares % LOT:
        e.append(f"khối lượng {shares} không phải bội số lô {LOT}")
    lo, hi = floor_price(ref_price), ceiling_price(ref_price)
    if not (lo <= price <= hi):
        e.append(f"giá {price} ngoài biên độ [{lo}, {hi}]")
    if restricted:
        e.append("mã nằm trong danh sách hạn chế")
    if side == "BUY" and cash_vnd is not None and price * shares > cash_vnd:
        e.append("vượt tiền mặt khả dụng")
    if max_order_vnd is not None and price * shares > max_order_vnd:
        e.append("vượt hạn mức giá trị một lệnh")
    return OrderCheck(not e, e)
