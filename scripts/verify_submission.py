"""Independently verify the HW05 ZIP and write a per-file SHA-256 manifest."""

import csv
import hashlib
import io
import json
import re
import subprocess
import sys
import zipfile
from collections import Counter
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

import fitz
from PIL import Image


WORK = Path(__file__).resolve().parents[1]
ROOT = WORK.parent
ZIP = ROOT / "23120127_HW05_AI_Performance_100.zip"
MANIFEST = ROOT / "ZIP_MANIFEST.tsv"
REPORT = ROOT / "ZIP_VERIFICATION.md"
SCENARIOS = ("load", "stress", "spike")


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    checks: list[tuple[str, bool, str]] = []

    def check(name: str, ok: bool, detail: str) -> None:
        checks.append((name, ok, detail))

    if not ZIP.is_file():
        raise SystemExit(f"Missing ZIP: {ZIP}")
    with zipfile.ZipFile(ZIP) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        check("ZIP CRC", archive.testzip() is None, "zipfile.testzip()")
        check("Không trùng đường dẫn", len(names) == len(set(names)), f"{len(names)} entries")
        check("Không path traversal", all(not n.startswith("/") and ".." not in Path(n).parts for n in names), "Các đường dẫn tương đối an toàn")
        prohibited = [n for n in names if n.startswith((".git/", "src/", "tools/", "node_modules/", "results/smoke/plans/")) or n.endswith((".sqlite", ".pyc")) or "/__pycache__/" in n or n.startswith("tmp_")]
        check("Không chứa file loại trừ", not prohibited, ", ".join(prohibited[:5]) or "Không có")

        selected = []
        ignored_dirs = {".git", "tmp", "__pycache__", "node_modules", "audit_inputs", "audit_outputs"}
        ignored_files = {"ai-audit.md", "HW05_PROMPTS.md", "REMAINING_FOR_ME.md", "workflow.md", "append_ai_audit.py", "tmp_load.jtl", "tmp_stress.jtl", "tmp_spike.jtl"}
        for path in WORK.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(WORK)
            if any(part in ignored_dirs for part in rel.parts) or path.name in ignored_files or path.name.startswith(".") or path.suffix in {".pyc", ".sqlite"} or rel.parts[:3] == ("results", "smoke", "plans"):
                continue
            selected.append(rel.as_posix())
        selected = sorted(selected)
        check("ZIP khớp file nguồn đã chọn", sorted(names) == selected, f"ZIP={len(names)}, nguồn={len(selected)}, thiếu={sorted(set(selected)-set(names))[:5]}, thừa={sorted(set(names)-set(selected))[:5]}")

        rows = ["path\tsize_bytes\tsha256"]
        mismatches = []
        for info in infos:
            data = archive.read(info.filename)
            original = WORK / info.filename
            if not original.is_file() or sha(data) != sha(original.read_bytes()):
                mismatches.append(info.filename)
            rows.append(f"{info.filename}\t{len(data)}\t{sha(data)}")
        check("Từng file đúng SHA-256 nguồn", not mismatches, f"{len(infos)} file; sai: {mismatches[:5]}")

        official = {f"plans/23120127_{s.title()}_20261122.jmx" for s in SCENARIOS}
        plans = {n for n in names if n.startswith("plans/") and n.endswith(".jmx")}
        check("Đúng ba JMX", plans == official, ", ".join(sorted(plans)))
        for scenario, expected_listener in (("load", "Summary Report"), ("stress", "Aggregate Report"), ("spike", "View Results Tree")):
            plan = f"plans/23120127_{scenario.title()}_20261122.jmx"
            root = ET.fromstring(archive.read(plan))
            listeners = [node.attrib.get("testname", "") for node in root.iter("ResultCollector")]
            csv_ref = any("admin${__threadNum}.csv" in (node.text or "") for node in root.iter("stringProp"))
            labels = {node.attrib.get("testname", "") for node in root.iter("HTTPSamplerProxy")}
            check(f"JMX {scenario}: listener/CSV/6 bước", expected_listener in listeners and csv_ref and len(labels) >= 6, f"listeners={listeners}, CSV={csv_ref}, HTTP labels={len(labels)}")

        csv_names = {n for n in names if re.fullmatch(r"data/admin\d+\.csv", n)}
        expected_csv = {f"data/admin{i}.csv" for i in range(1, 101)}
        check("Đúng 100 CSV", csv_names == expected_csv, f"{len(csv_names)} file")
        valid_csv = True
        for name in expected_csv:
            data = list(csv.DictReader(io.StringIO(archive.read(name).decode("utf-8-sig"))))
            if len(data) != 1 or set(data[0]) != {"email", "password", "category_prefix"} or not data[0]["email"].endswith("@example.test"):
                valid_csv = False
                break
        check("CSV có cấu trúc/dữ liệu", valid_csv, "Một tài khoản tổng hợp mỗi file")

        sample_summary = []
        for scenario in (*SCENARIOS, "soak"):
            raw = archive.read(f"results/{scenario}/{scenario}.jtl").decode("utf-8-sig")
            data = list(csv.DictReader(io.StringIO(raw)))
            errors = sum(row["success"].lower() != "true" for row in data)
            labels = Counter(row["label"] for row in data)
            required = [f"results/{scenario}/jmeter.log", f"results/{scenario}/resources.csv", f"results/{scenario}/html/index.html"]
            check(f"{scenario}: raw/HTML/monitor", bool(data) and all(n in names for n in required), f"samples={len(data)}, errors={errors}, labels={len(labels)}")
            sample_summary.append(f"- {scenario}: {len(data)} samples, {errors} JMeter errors, {len(labels)} labels.")
        check("Số mẫu khớp report", [sum(1 for _ in csv.DictReader(io.StringIO(archive.read(f"results/{s}/{s}.jtl").decode("utf-8-sig")))) for s in SCENARIOS] == [4499, 8364, 3404], "load=4499, stress=8364, spike=3404")

        pdf_summary = []
        for name in ("report.pdf", "ai-critique.pdf", "ai_audit.pdf"):
            doc = fitz.open(stream=archive.read(name), filetype="pdf")
            chars = sum(len(page.get_text()) for page in doc)
            check(f"PDF {name}", len(doc) >= 1 and chars > 1000, f"{len(doc)} pages, {chars} extracted chars")
            pdf_summary.append(f"{name}: {len(doc)} pages")
        for name in ("evidence/dxdiag-system.png", "evidence/load-live.png", "evidence/stress-live.png", "evidence/spike-live.png"):
            im = Image.open(io.BytesIO(archive.read(name)))
            im.verify()
            check(f"PNG {name}", True, "Pillow verify() thành công")

        links = archive.read("evidence/video-links.md").decode("utf-8")
        check("YouTube URL có trong ZIP", "https://youtu.be/lk0vSGCapsc" in links, "Metadata đã kiểm riêng: Unlisted, 424 giây; nội dung chưa xác minh")
        critique = archive.read("ai-critique.md").decode("utf-8")
        body_words = len(critique.split("---", 1)[1].split())
        check("AI Critique 200–300 từ", 200 <= body_words <= 300, f"{body_words} từ phần thân")

    MANIFEST.write_text("\n".join(rows) + "\n", encoding="utf-8")
    try:
        issues = subprocess.run(["gh", "issue", "list", "-R", "duongtronghoa/Hw05", "--state", "all", "--json", "number"], capture_output=True, text=True, timeout=20)
        issue_count = len(json.loads(issues.stdout)) if issues.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
        issue_count = None
    now = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    lines = ["# Kiểm định độc lập ZIP HW05", "", f"- Thời điểm: {now}", f"- ZIP: `{ZIP.name}`", f"- Kích thước: {ZIP.stat().st_size:,} bytes", f"- SHA-256 ZIP: `{sha(ZIP.read_bytes())}`", f"- Số file: {len(names)}", f"- Manifest từng file: `{MANIFEST.name}` ({len(rows)-1} dòng dữ liệu)", "", "## Kiểm tra tự động", "", "| Phép kiểm | Kết quả | Chi tiết |", "|---|---|---|"]
    for title, ok, detail in checks:
        lines.append(f"| {title} | {'PASS' if ok else 'FAIL'} | {detail.replace('|', '/')} |")
    lines += ["", "## Log thô", "", *sample_summary, "", "## PDF", "", *[f"- {x}" for x in pdf_summary], "", "## Giới hạn chứng minh", "", f"- GitHub Issues hiện có: {issue_count if issue_count is not None else 'chưa kiểm được'}; hai lỗi C07/C08 chưa có Issue và ảnh lỗi trong nguồn đã kiểm.", "- Ảnh live ghi các `tmp_*.jtl`, khác tên raw JTL chính thức. Không thể nối trực tiếp hai lượt chạy chỉ từ các file hiện có.", "- Metadata video: 424 giây, Unlisted (đã kiểm riêng). Script không xác nhận nội dung hình/giọng hoặc demo Agent Skill.", "- P00–P14 trong AI Audit lưu output tóm tắt, chưa phải toàn văn. Các lời khai human review cần sinh viên xác nhận.", "- PASS kỹ thuật không đồng nghĩa đạt đủ yêu cầu chấm điểm. Xem `hw05-work/SUBMISSION_CHECKLIST.md`.", ""]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"{REPORT} | {len(checks)} checks, {sum(ok for _, ok, _ in checks)} PASS, {sum(not ok for _, ok, _ in checks)} FAIL")
    if any(not ok for _, ok, _ in checks):
        sys.exit(1)


if __name__ == "__main__":
    main()
