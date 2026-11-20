"""WP2 — chạy MỘT LẦN trên dữ liệu XSMB thật theo WP2_PREREG v1.1 (chỉ đổi dữ liệu sang SRC-002B v2).
Kiểm SHA-256 của mã và dữ liệu trước khi chạy; ghi thời điểm bắt đầu/kết thúc (UTC)."""
import hashlib, json, sys, time, datetime as dt
from astra_math import wp2_distinguishers as w

MODULE_SHA = "9983468af4939b4982c2dd1a530dbc8e417d07879bdd160684b9d6398415a9c3"
DATA_SHA = "85aabd573c67bf4c0dbba4151a05f6771113c8c542dd6dd4dcdfaf4d27535909"   # SRC-002B (v2, sửa 21/09/2006)
csv_path, out_path = sys.argv[1], sys.argv[2]
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()
assert sha(w.__file__) == MODULE_SHA, "mã WP2 khác bản đã khóa"
assert sha(csv_path) == DATA_SHA, "dữ liệu khác snapshot đã khóa"
assert (w.B_PERM, w.B_LZMA, w.SEED, w.ALPHA, len(w.TESTS)) == (9999, 999, 20261120, 0.05, 13)
start = dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'); t0 = time.time()
dates, raw = w.load_raw(csv_path)
assert len(dates) == 7622
p = w.run_all(dates, raw)
rep = w.holm_report(p)
rep.update(module_sha256=MODULE_SHA, data_sha256=DATA_SHA, so_ky=len(dates), tu=str(dates[0]), den=str(dates[-1]),
           B_PERM=w.B_PERM, B_LZMA=w.B_LZMA, seed=w.SEED, bat_dau_utc=start,
           ket_thuc_utc=dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds'), giay=round(time.time() - t0),
           p_day_du={k: v for k, v in p.items()}, ten_phep=w.TESTS)
json.dump(rep, open(out_path, 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: rep[k] for k in ('p', 'bac_bo_holm', 'giay')}, ensure_ascii=False))
