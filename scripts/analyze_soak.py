"""Measure the sustained post-ramp window of a scheduled JMeter soak run."""

import argparse
import csv
import json
import math
import re
import statistics
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo


ZONE = ZoneInfo("Asia/Ho_Chi_Minh")


def percentile95(values: list[int]) -> int:
    values = sorted(values)
    return values[math.ceil(0.95 * len(values)) - 1]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--jtl", required=True, type=Path)
    p.add_argument("--log", required=True, type=Path)
    p.add_argument("--resources", required=True, type=Path)
    p.add_argument("--ramp", required=True, type=int)
    p.add_argument("--duration", required=True, type=int)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    if args.output.exists():
        p.error("output already exists")
    log = args.log.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d,\d{3}) INFO .*Starting ThreadGroup: 1", log, flags=re.MULTILINE)
    if not match:
        p.error("JMeter ThreadGroup start not found in log")
    start = datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S,%f").replace(tzinfo=ZONE)
    hold_start = start + timedelta(seconds=args.ramp)
    end = start + timedelta(seconds=args.duration)
    hold_seconds = args.duration - args.ramp
    with args.jtl.open(encoding="utf-8", newline="") as stream:
        all_rows = list(csv.DictReader(stream))
    rows = [r for r in all_rows if int(r["timeStamp"]) >= hold_start.timestamp() * 1000 and int(r["timeStamp"]) + int(r["elapsed"]) <= end.timestamp() * 1000]
    if not rows:
        p.error("no complete samples in hold window")
    labels = {}
    for label in sorted({r["label"] for r in rows}):
        items = [r for r in rows if r["label"] == label]
        labels[label] = {"n": len(items), "failed": sum(r["success"].lower() != "true" for r in items), "p95_ms": percentile95([int(r["elapsed"]) for r in items]), "rps": round(len(items) / hold_seconds, 3)}
    with args.resources.open(encoding="utf-8", newline="") as stream:
        resource_all = list(csv.DictReader(stream))
    resource = [(datetime.fromisoformat(r["time_local"]), r) for r in resource_all if r["node_rss_mib"]]
    resource = [(t, r) for t, r in resource if hold_start <= t <= end]
    if not resource:
        p.error("no resource samples in hold window")
    start_mem = [float(r["node_rss_mib"]) for t, r in resource if t < hold_start + timedelta(seconds=60)]
    end_mem = [float(r["node_rss_mib"]) for t, r in resource if t >= end - timedelta(seconds=60)]
    rss = [float(r["node_rss_mib"]) for _, r in resource]
    private = [float(r["node_private_mib"]) for _, r in resource if r["node_private_mib"]]
    result = {
        "engine_start_local": start.isoformat(timespec="milliseconds"),
        "hold_start_local": hold_start.isoformat(timespec="milliseconds"),
        "hold_end_local": end.isoformat(timespec="milliseconds"),
        "hold_seconds": hold_seconds,
        "all_run_requests": len(all_rows),
        "hold_requests": len(rows),
        "hold_failed": sum(r["success"].lower() != "true" for r in rows),
        "hold_error_pct": round(100 * sum(r["success"].lower() != "true" for r in rows) / len(rows), 4),
        "hold_rps": round(len(rows) / hold_seconds, 3),
        "hold_p95_all_ms": percentile95([int(r["elapsed"]) for r in rows]),
        "labels": labels,
        "node_rss_first_mib": rss[0],
        "node_rss_last_mib": rss[-1],
        "node_rss_min_mib": min(rss),
        "node_rss_max_mib": max(rss),
        "node_private_first_mib": private[0] if private else None,
        "node_private_last_mib": private[-1] if private else None,
        "node_private_min_mib": min(private) if private else None,
        "node_private_max_mib": max(private) if private else None,
        "node_rss_first_minute_median_mib": round(statistics.median(start_mem), 2) if start_mem else None,
        "node_rss_last_minute_median_mib": round(statistics.median(end_mem), 2) if end_mem else None,
        "resource_samples_in_hold": len(resource),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
