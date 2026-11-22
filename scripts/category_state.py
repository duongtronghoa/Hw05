"""Snapshot category IDs and optionally remove only this assignment's leftovers.

Use after a run, once JTL/logs are saved. The CSV is evidence of every ID that
was removed. SUT's three seed categories are never targeted.
"""

import argparse
import csv
import sqlite3
from pathlib import Path


DB = Path(__file__).resolve().parents[2] / "src" / "eshop-sut" / "backend" / "database.sqlite"
PREFIX = "HW05_23120127_"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", required=True, type=Path)
    parser.add_argument("--cleanup", action="store_true")
    args = parser.parse_args()
    if args.snapshot.exists():
        parser.error(f"snapshot already exists: {args.snapshot}")
    args.snapshot.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB) as db:
        rows = db.execute("SELECT id,name FROM categories ORDER BY id").fetchall()
        candidates = [(id_, name) for id_, name in rows if name.startswith(PREFIX)]
        with args.snapshot.open("x", encoding="utf-8", newline="") as out:
            writer = csv.writer(out)
            writer.writerow(("id", "name", "hw05_candidate"))
            writer.writerows((id_, name, int(name.startswith(PREFIX))) for id_, name in rows)
        print(f"Snapshot: {args.snapshot}; total={len(rows)}; HW05 candidates={len(candidates)}")
        if args.cleanup:
            for id_, name in candidates:
                db.execute("DELETE FROM categories WHERE id=? AND name=?", (id_, name))
            db.commit()
            remaining = db.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
            print(f"Removed {len(candidates)} exact ID/name pairs; remaining={remaining}")


if __name__ == "__main__":
    main()
