"""Probe C07-C09 outside benchmark; never persist JWT or passwords."""

import argparse
import json
import sqlite3
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "src" / "eshop-sut" / "backend" / "database.sqlite"
BASE = "http://localhost:3000"


def call(method: str, path: str, data: dict | None = None, token: str | None = None) -> tuple[int, dict | list]:
    raw = json.dumps(data).encode() if data is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(BASE + path, data=raw, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status, json.load(response)
    except urllib.error.HTTPError as error:
        return error.code, json.load(error)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output already exists")
    result = {"time_local": datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).isoformat(timespec="seconds"), "sut_commit": "85af3ba875c88283615e22cb108f13e2fccaf0e9"}
    unique = uuid.uuid4().hex[:12]
    email = f"hw05_edge_{unique}@example.test"
    password = "HW05_Sacrificial_Only!"
    category_id = None
    user_id = None
    try:
        status, body = call("POST", "/api/register", {"name": "HW05 edge probe", "email": email, "password": password})
        if status != 200:
            raise RuntimeError(f"register failed: {status}")
        user_id = body["id"]
        wrong = []
        for _ in range(2):
            code, response = call("POST", "/api/login", {"email": email, "password": "wrong"})
            wrong.append({"status": code, "response": response})
            time.sleep(0.3)
        code, response = call("POST", "/api/login", {"email": email, "password": password})
        with sqlite3.connect(DB) as db:
            count, locked_until = db.execute("SELECT login_attempts,locked_until FROM users WHERE id=?", (user_id,)).fetchone()
        result["C07_lockout"] = {"email": email, "wrong_attempts": wrong, "correct_after_two_wrong": {"status": code, "response": response if code != 200 else {"message": response.get("message")}}, "db_login_attempts": count, "db_locked_until": locked_until, "expected_from_README": "lock after 3 consecutive wrong attempts for 30 seconds"}

        code, body = call("POST", "/api/login", {"email": "test@eshop.com", "password": "Test1234!"})
        if code != 200 or body.get("user", {}).get("role") != "user":
            raise RuntimeError("seed normal-user login failed")
        user_token = body["token"]
        category_name = "HW05_23120127_EDGE_" + unique
        code, body = call("POST", "/api/categories", {"name": category_name}, user_token)
        created = {"status": code, "response": body}
        if code == 200 and isinstance(body, dict) and "id" in body:
            category_id = body["id"]
            update_code, update_body = call("PUT", f"/api/categories/{category_id}", {"name": category_name + "_updated"}, user_token)
            delete_code, delete_body = call("DELETE", f"/api/categories/{category_id}", token=user_token)
            result["C08_nonadmin_write"] = {"role": "user", "create": created, "update": {"status": update_code, "response": update_body}, "delete": {"status": delete_code, "response": delete_body}, "expected_from_README": "403 or equivalent refusal for non-admin token on category writes"}
        else:
            result["C08_nonadmin_write"] = {"role": "user", "create": created, "expected_from_README": "403 or equivalent refusal for non-admin token on category writes"}

        admin = Path(__file__).resolve().parents[1] / "data" / "admin1.csv"
        import csv
        with admin.open(encoding="utf-8", newline="") as stream:
            credential = next(csv.DictReader(stream))
        code, body = call("POST", "/api/login", {"email": credential["email"], "password": credential["password"]})
        if code != 200:
            raise RuntimeError("synthetic admin login failed")
        admin_token = body["token"]
        absent_id = 2_147_483_647
        with sqlite3.connect(DB) as db:
            before = db.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
        put_code, put_body = call("PUT", f"/api/categories/{absent_id}", {"name": "HW05_23120127_NONEXISTENT"}, admin_token)
        delete_code, delete_body = call("DELETE", f"/api/categories/{absent_id}", token=admin_token)
        with sqlite3.connect(DB) as db:
            after = db.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
        result["C09_absent_id"] = {"id": absent_id, "put": {"status": put_code, "response": put_body}, "delete": {"status": delete_code, "response": delete_body}, "category_count_before": before, "category_count_after": after, "note": "Actual no-op 200; API spec does not explicitly require 404, so classify separately from confirmed bugs."}
    finally:
        with sqlite3.connect(DB) as db:
            if category_id is not None:
                db.execute("DELETE FROM categories WHERE id=? AND name LIKE 'HW05_23120127_EDGE_%'", (category_id,))
            if user_id is not None:
                db.execute("DELETE FROM users WHERE id=? AND email=?", (user_id, email))
            db.commit()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
    print(args.output)


if __name__ == "__main__":
    main()
