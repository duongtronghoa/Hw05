"""Create repeatable synthetic admin accounts and one CSV per future virtual user.

Run while the EShop backend is already up. EShop re-seeds its database on every
server start, so run this script again after a restart. This is test setup, not
a measured performance workload.
"""

import argparse
import csv
import sqlite3
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parents[2]
DEFAULT_DB = WORKSPACE / "src" / "eshop-sut" / "backend" / "database.sqlite"
DEFAULT_DATA = Path(__file__).resolve().parents[1] / "data"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--student-id", default="23120127")
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    args = parser.parse_args()

    if not args.student_id.isdigit() or args.count < 1:
        parser.error("student-id must be numeric and count must be positive")
    if not args.db.is_file():
        parser.error(f"database not found: {args.db}")

    password = f"Hw05_{args.student_id}_Admin!"  # synthetic local SUT password
    users = [
        (
            f"hw05_{args.student_id}_{number:03d}@example.test",
            password,
            f"HW05_{args.student_id}_T{number:03d}",
        )
        for number in range(1, args.count + 1)
    ]

    created = 0
    with sqlite3.connect(args.db, timeout=30) as conn:
        for email, account_password, _ in users:
            rows = conn.execute(
                "SELECT id, password, role FROM users WHERE email = ?", (email,)
            ).fetchall()
            if len(rows) > 1:
                raise RuntimeError(f"duplicate email already in SUT: {email}")
            if rows:
                if rows[0][1] != account_password or rows[0][2] != "admin":
                    raise RuntimeError(f"existing account does not match test setup: {email}")
            else:
                conn.execute(
                    "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
                    (f"HW05 Admin {email.split('_')[-1].split('@')[0]}", email, account_password, "admin"),
                )
                created += 1

    args.data_dir.mkdir(parents=True, exist_ok=True)
    for number, (email, account_password, category_prefix) in enumerate(users, 1):
        path = args.data_dir / f"admin{number}.csv"
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["email", "password", "category_prefix"])
            writer.writerow([email, account_password, category_prefix])

    with sqlite3.connect(args.db, timeout=30) as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM users WHERE email LIKE ? AND role = 'admin'",
            (f"hw05_{args.student_id}_%@example.test",),
        ).fetchone()[0]
    csv_count = len(list(args.data_dir.glob("admin*.csv")))
    if count != args.count or csv_count != args.count:
        raise RuntimeError(f"expected {args.count} accounts/CSVs; got {count}/{csv_count}")

    print(f"created_admin_accounts={created}")
    print(f"verified_admin_accounts={count}")
    print(f"verified_csv_files={csv_count}")
    print(f"database={args.db}")
    print(f"data_dir={args.data_dir}")


if __name__ == "__main__":
    main()
