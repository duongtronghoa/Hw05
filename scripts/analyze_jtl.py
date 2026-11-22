"""Ground-truth JTL analyzer for HW05 Performance Testing.

Reads raw JTL CSV files directly, verifies headers, splits by ThreadGroup / phase,
and computes sample counts, error counts, response codes, RPS, and percentiles
(p50, p90, p95, p99) per label and phase.
"""

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


def calc_percentile(sorted_vals: list[int], pct: float) -> int:
    if not sorted_vals:
        return 0
    k = math.ceil(pct * len(sorted_vals)) - 1
    k = max(0, min(k, len(sorted_vals) - 1))
    return sorted_vals[k]


def analyze_samples(rows: list[dict]) -> dict:
    if not rows:
        return {"samples": 0}
    
    start_ms = min(int(r["timeStamp"]) for r in rows)
    end_ms = max(int(r["timeStamp"]) + int(r["elapsed"]) for r in rows)
    span_s = max(0.001, (end_ms - start_ms) / 1000.0)
    
    total_samples = len(rows)
    failed_samples = sum(1 for r in rows if r["success"].strip().lower() != "true")
    error_rate = (failed_samples / total_samples) * 100.0
    
    elapsed_all = sorted(int(r["elapsed"]) for r in rows)
    status_codes = dict(Counter(r.get("responseCode", "") for r in rows))
    
    # Per label breakdown
    by_label = defaultdict(list)
    for r in rows:
        by_label[r["label"]].append(r)
        
    labels_summary = {}
    for label, lrows in sorted(by_label.items()):
        l_elapsed = sorted(int(r["elapsed"]) for r in lrows)
        l_failed = sum(1 for r in lrows if r["success"].strip().lower() != "true")
        labels_summary[label] = {
            "samples": len(lrows),
            "errors": l_failed,
            "error_rate_pct": round((l_failed / len(lrows)) * 100.0, 3),
            "p50_ms": calc_percentile(l_elapsed, 0.50),
            "p90_ms": calc_percentile(l_elapsed, 0.90),
            "p95_ms": calc_percentile(l_elapsed, 0.95),
            "p99_ms": calc_percentile(l_elapsed, 0.99),
            "avg_ms": round(sum(l_elapsed) / len(l_elapsed), 2),
            "min_ms": l_elapsed[0] if l_elapsed else 0,
            "max_ms": l_elapsed[-1] if l_elapsed else 0,
            "rps": round(len(lrows) / span_s, 3),
        }
        
    return {
        "samples": total_samples,
        "errors": failed_samples,
        "error_rate_pct": round(error_rate, 3),
        "start_epoch_ms": start_ms,
        "end_epoch_ms": end_ms,
        "span_seconds": round(span_s, 3),
        "rps": round(total_samples / span_s, 3),
        "p50_ms": calc_percentile(elapsed_all, 0.50),
        "p90_ms": calc_percentile(elapsed_all, 0.90),
        "p95_ms": calc_percentile(elapsed_all, 0.95),
        "p99_ms": calc_percentile(elapsed_all, 0.99),
        "avg_ms": round(sum(elapsed_all) / len(elapsed_all), 2),
        "min_ms": elapsed_all[0] if elapsed_all else 0,
        "max_ms": elapsed_all[-1] if elapsed_all else 0,
        "status_codes": status_codes,
        "labels": labels_summary,
    }


def analyze_jtl_file(jtl_path: Path) -> dict:
    with jtl_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        rows = list(reader)
        
    # Group by thread group prefix
    by_tg = defaultdict(list)
    for r in rows:
        tname = r.get("threadName", "")
        tg = tname.rsplit(" ", 1)[0] if " " in tname else tname
        by_tg[tg].append(r)
        
    phases = {}
    for tg, tg_rows in sorted(by_tg.items(), key=lambda kv: min(int(x["timeStamp"]) for x in kv[1])):
        phases[tg] = analyze_samples(tg_rows)
        
    return {
        "file": str(jtl_path),
        "headers": headers,
        "total": analyze_samples(rows),
        "phases": phases,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", type=Path, default=Path("hw05-work/results"))
    parser.add_argument("--output-json", type=Path, default=Path("hw05-work/analysis/jtl-metrics-ground-truth.json"))
    args = parser.parse_args()
    
    results = {}
    for scenario in ["load", "stress", "spike", "soak"]:
        jtl_file = args.results_dir / scenario / f"{scenario}.jtl"
        if jtl_file.is_file():
            results[scenario] = analyze_jtl_file(jtl_file)
        else:
            print(f"Warning: {jtl_file} not found")
            
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    with args.output_json.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    print(f"Ground truth analysis written to {args.output_json}")


if __name__ == "__main__":
    main()
