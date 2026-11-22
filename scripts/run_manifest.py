"""Write immutable provenance for an actual JMeter run after it finishes."""

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--scenario", required=True)
    p.add_argument("--jmx", required=True, type=Path)
    p.add_argument("--jtl", required=True, type=Path)
    p.add_argument("--resources", required=True, type=Path)
    p.add_argument("--category-snapshot", required=True, type=Path)
    p.add_argument("--node-pid", required=True, type=int)
    p.add_argument("--params", required=True)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    if args.output.exists():
        p.error(f"manifest already exists: {args.output}")
    with args.jtl.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    with args.resources.open(encoding="utf-8", newline="") as stream:
        resources = list(csv.DictReader(stream))
    if not rows or not resources:
        p.error("JTL/resources empty")
    with args.category_snapshot.open(encoding="utf-8", newline="") as stream:
        categories = list(csv.DictReader(stream))
    start = min(int(r["timeStamp"]) for r in rows)
    end = max(int(r["timeStamp"]) + int(r["elapsed"]) for r in rows)
    document = {
        "scenario": args.scenario,
        "created_local": datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).isoformat(timespec="seconds"),
        "params": args.params,
        "node_pid": args.node_pid,
        "jmx": str(args.jmx), "jmx_sha256": sha(args.jmx),
        "jtl": str(args.jtl), "jtl_sha256": sha(args.jtl), "jtl_bytes": args.jtl.stat().st_size,
        "resources": str(args.resources), "resources_sha256": sha(args.resources),
        "category_snapshot": str(args.category_snapshot), "category_snapshot_sha256": sha(args.category_snapshot),
        "sample_start_epoch_ms": start, "sample_end_epoch_ms": end,
        "sample_count": len(rows),
        "failed_samples": sum(r["success"].lower() != "true" for r in rows),
        "labels": dict(Counter(r["label"] for r in rows)),
        "thread_groups": dict(Counter(r["threadName"].split(" ")[0] for r in rows)),
        "category_count_after_before_cleanup": len(categories),
        "hw05_categories_after_before_cleanup": sum(r["hw05_candidate"] == "1" for r in categories),
        "node_rss_max_mib": max(float(r["node_rss_mib"]) for r in resources if r["node_rss_mib"]),
        "system_cpu_max_pct": max(float(r["system_cpu_pct"]) for r in resources if r["system_cpu_pct"]),
        "live_screenshot": "missing; student will capture during narrated rerun",
        "narrated_video": "missing; student reported unable to record now",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(document, stream, ensure_ascii=False, indent=2)
    print(args.output)


if __name__ == "__main__":
    main()
