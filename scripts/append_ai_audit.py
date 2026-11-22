"""Append one real AI interaction to the canonical HW05 audit file.

The agent must save the exact user prompt and its final user-facing response
to UTF-8 files first, then send the saved response unchanged after this script
has appended it. Human review is deliberately left pending.
"""

import argparse
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


WORK_DIR = Path(__file__).resolve().parents[1]
DEFAULT_AUDIT = WORK_DIR / "ai_audit.md"


def fenced(value: str) -> str:
    runs = re.findall(r"`+", value)
    width = max(3, max((len(run) for run in runs), default=0) + 1)
    fence = "`" * width
    closing_newline = "" if value.endswith("\n") else "\n"
    return f"{fence}text\n{value}{closing_newline}{fence}"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", required=True, help="Prompt ID, e.g. P02")
    parser.add_argument("--purpose", required=True)
    parser.add_argument("--tool-model", required=True)
    parser.add_argument("--prompt-file", required=True, type=Path)
    parser.add_argument("--output-file", required=True, type=Path)
    parser.add_argument("--inputs", default="None")
    parser.add_argument("--audit-file", type=Path, default=DEFAULT_AUDIT)
    args = parser.parse_args()

    if not re.fullmatch(r"P\d{2}", args.id):
        parser.error("--id must look like P02")
    if not args.prompt_file.is_file() or not args.output_file.is_file():
        parser.error("prompt-file and output-file must exist")

    prompt = args.prompt_file.read_text(encoding="utf-8")
    output = args.output_file.read_text(encoding="utf-8")
    if not prompt.strip() or not output.strip():
        parser.error("prompt-file and output-file must be nonempty")

    audit = args.audit_file
    previous = audit.read_text(encoding="utf-8") if audit.exists() else ""
    if re.search(rf"^### \[{re.escape(args.id)}\]", previous, flags=re.MULTILINE):
        parser.error(f"{args.id} already appears in {audit}; do not overwrite earlier interactions")

    timestamp = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%Y-%m-%d %H:%M:%S +07:00")
    entry = (
        f"\n\n---\n\n### [{args.id}] {args.purpose}\n"
        f"- Tool/model: {args.tool_model}\n"
        f"- Time: {timestamp}\n"
        f"- Inputs/attachments: {args.inputs}\n"
        f"- Prompt:\n\n{fenced(prompt)}\n"
        f"- AI output:\n\n{fenced(output)}\n"
        f"- Human review/correction: Chờ người học tự kiểm tra và bổ sung; agent không tự nhận là đã human review.\n"
    )
    audit.parent.mkdir(parents=True, exist_ok=True)
    with audit.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(entry)
    print(f"Appended {args.id} to {audit}")


if __name__ == "__main__":
    main()
