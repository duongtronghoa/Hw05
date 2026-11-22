"""Create the final HW05 ZIP only after student-owned evidence is present."""

import argparse
import re
import subprocess
import zipfile
from pathlib import Path


WORK = Path(__file__).resolve().parents[1]
ROOT = WORK.parent


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--grade", required=True, type=int, help="Student's own total, 0..100")
    args = p.parse_args()
    if not 0 <= args.grade <= 100:
        p.error("grade must be 0..100")
    required = [
        "README.md", "report.md", "report.pdf", "ai-critique.md", "ai-critique.pdf", "ai_audit.md", "ai_audit.pdf", "git-commits.txt",
        "evidence/hardware-spec.json", "evidence/hardware-spec.md", "evidence/dxdiag-system.png", "evidence/load-live.png", "evidence/stress-live.png", "evidence/spike-live.png", "evidence/video-links.md", "skill/hw05-api-performance/SKILL.md",
    ]
    for scenario in ("Load", "Stress", "Spike"):
        required.append(f"plans/23120127_{scenario}_20261122.jmx")
        slug = scenario.lower()
        required += [f"results/{slug}/{slug}.jtl", f"results/{slug}/jmeter.log", f"results/{slug}/html/index.html", f"results/{slug}/resources.csv"]
    required += ["results/soak/soak.jtl", "results/soak/jmeter.log", "results/soak/html/index.html", "results/soak/resources.csv"]
    missing = [rel for rel in required if not (WORK / rel).is_file()]
    if missing:
        p.error("missing required files: " + ", ".join(missing))
    links = (WORK / "evidence/video-links.md").read_text(encoding="utf-8")
    if not re.search(r"https://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)", links):
        p.error("video-links.md needs a real unlisted YouTube URL")
    audit = (WORK / "ai_audit.md").read_text(encoding="utf-8")
    if "Human review/correction: Chờ người học" in audit:
        p.error("AI audit still has pending human review entries")
    readme = (WORK / "README.md").read_text(encoding="utf-8")
    if "Chưa chấm" in readme or "Chưa tạo GitHub" in readme:
        p.error("README self-assessment/status is unfinished")
    if f"{args.grade:03}" not in readme:
        p.error("README must state the student's matching 3-digit total grade")
    try:
        visibility = subprocess.run(["gh", "repo", "view", "duongtronghoa/Hw05", "--json", "visibility", "--jq", ".visibility"], cwd=WORK, capture_output=True, text=True, timeout=20)
        if visibility.returncode or visibility.stdout.strip() != "PUBLIC":
            p.error("GitHub repository is not confirmed public")
    except FileNotFoundError:
        p.error("gh CLI unavailable; verify public GitHub repository manually first")
    target = ROOT / f"23120127_HW05_AI_Performance_{args.grade:03}.zip"
    if target.exists():
        p.error(f"ZIP already exists: {target}")
    paths = [x for x in WORK.rglob("*") if x.is_file() and not any(part in {".git", "tmp", "__pycache__", "node_modules"} for part in x.relative_to(WORK).parts) and x.name not in {"ai-audit.md"} and x.suffix not in {".pyc", ".sqlite"}]
    paths = [x for x in paths if not (x.relative_to(WORK).parts[:3] == ("results", "smoke", "plans"))]
    with zipfile.ZipFile(target, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        archive.write(ROOT / "HW05_PLAN.md", "HW05_PLAN.md")
        for path in sorted(paths):
            archive.write(path, "hw05-work/" + path.relative_to(WORK).as_posix())
    with zipfile.ZipFile(target) as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError(f"corrupt ZIP member: {bad}")
        print(f"Created {target} with {len(archive.namelist())} files, {target.stat().st_size} bytes")


if __name__ == "__main__":
    main()
