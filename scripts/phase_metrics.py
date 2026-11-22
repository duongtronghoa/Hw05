"""Read raw JTL and report request statistics by JMeter thread group."""

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path


def p95(values: list[int]) -> int:
    ordered = sorted(values)
    return ordered[math.ceil(0.95 * len(ordered)) - 1]


def summarize(rows: list[dict]) -> dict:
    start = min(int(x["timeStamp"]) for x in rows)
    end = max(int(x["timeStamp"]) + int(x["elapsed"]) for x in rows)
    seconds = (end - start) / 1000
    labels = defaultdict(list)
    for row in rows:
        labels[row["label"]].append(row)
    return {
        "requests": len(rows),
        "failed": sum(x["success"].lower() != "true" for x in rows),
        "start_epoch_ms": start,
        "end_epoch_ms": end,
        "span_s": round(seconds, 3),
        "rps": round(len(rows) / seconds, 3),
        "p95_all_ms": p95([int(x["elapsed"]) for x in rows]),
        "labels": {label: {"n": len(items), "failed": sum(x["success"].lower() != "true" for x in items), "p95_ms": p95([int(x["elapsed"]) for x in items])} for label, items in sorted(labels.items())},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("jtl", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    with args.jtl.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    groups = defaultdict(list)
    for row in rows:
        groups[row["threadName"].rsplit(" ", 1)[0]].append(row)
    result = {"jtl": str(args.jtl), "all": summarize(rows), "phases": {group: summarize(items) for group, items in sorted(groups.items(), key=lambda kv: min(int(x["timeStamp"]) for x in kv[1]))}}
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        if args.output.exists():
            parser.error("output already exists")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output + "\n", encoding="utf-8")
        print(args.output)
    else:
        print(output)


if __name__ == "__main__":
    main()
