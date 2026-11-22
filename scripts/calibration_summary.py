"""Summarize short calibration JTLs; this is not the final P10 analysis."""

import csv
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "results" / "calibration"
OUT = ROOT / "design" / "calibration.md"


def p95(values: list[int]) -> int:
    ordered = sorted(values)
    return ordered[math.ceil(0.95 * len(ordered)) - 1]


lines = ["# Calibration ngắn (P05)", "", "Mỗi mức dùng Load plan, ramp 5 giây, tổng 35 giây. Đây là phép đo ngắn, chưa chứng minh độ ổn định dài hạn.", "", "| VU | Requests | Lỗi | RPS toàn run | p95 tất cả (ms) | p95 đọc max (ms) | p95 ghi/xác thực max (ms) | Node RSS max (MiB) | System CPU max (%) |", "|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
for vus in (5, 10, 20, 40, 80):
    path = BASE / f"vu{vus}.jtl"
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    stamps = [int(r["timeStamp"]) for r in rows]
    end = max(int(r["timeStamp"]) + int(r["elapsed"]) for r in rows)
    seconds = (end - min(stamps)) / 1000
    errors = sum(r["success"].lower() != "true" for r in rows)
    labels = {label: [int(r["elapsed"]) for r in rows if r["label"] == label] for label in sorted({r["label"] for r in rows})}
    read = max(p95(labels[k]) for k in ("02_categories_list", "03_products_list") if k in labels)
    write = max(p95(labels[k]) for k in ("01_login", "04_category_create", "05_category_update", "06_category_delete") if k in labels)
    with (BASE / f"vu{vus}_resources.csv").open(encoding="utf-8", newline="") as stream:
        resource = list(csv.DictReader(stream))
    node_rss = max(float(r["node_rss_mib"]) for r in resource if r["node_rss_mib"])
    system_cpu = max(float(r["system_cpu_pct"]) for r in resource if r["system_cpu_pct"])
    lines.append(f"| {vus} | {len(rows)} | {errors} | {len(rows)/seconds:.2f} | {p95([int(r['elapsed']) for r in rows])} | {read} | {write} | {node_rss:.1f} | {system_cpu:.1f} |")
lines += ["", "Nguồn: `results/calibration/vu*.jtl` và `vu*_resources.csv`. RPS = số request / thời gian từ request đầu đến response cuối; mỗi p95 tính từ mẫu gốc của nhóm tương ứng. Khi scheduler hết hạn, VU có thể dừng giữa CREATE và DELETE: snapshot sau cả 5 lượt có 71 category thử còn lại (xem `results/calibration/post_all_categories.csv`), đã dọn đúng 71 ID/tên để đưa baseline về 3. Việc dọn không sửa JTL.", "", "Tiêu chí dự kiến đã ghi trước đo trong `design/test-design.md`: error ≤1%, read p95 ≤500 ms, auth/write p95 ≤2000 ms, không HTTP 500, không rác category sau khi dọn và kiểm chứng. Mức soak tạm chọn 20 VU để đại diện tải thường; 80 VU chỉ được chứng minh qua 35 giây, cần run dài để đánh giá. Không gọi 80 VU là tối đa tuyệt đối.", ""]
OUT.write_text("\n".join(lines), encoding="utf-8")
print(OUT)
