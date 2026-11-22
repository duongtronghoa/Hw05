"""Print a UTF-8 Markdown document to PDF through headless Chrome."""

import argparse
import html
import subprocess
import tempfile
from pathlib import Path

import markdown


CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
CSS = """
@page { size: A4; margin: 18mm 16mm; }
body { font-family: Arial, sans-serif; color: #17212b; font-size: 10pt; line-height: 1.43; }
h1 { font-size: 20pt; color: #123a5c; border-bottom: 2px solid #2b6b96; padding-bottom: 5px; }
h2 { font-size: 15pt; color: #174c71; margin-top: 20px; break-after: avoid; }
h3 { font-size: 12pt; color: #174c71; break-after: avoid; }
p, li { overflow-wrap: anywhere; }
table { border-collapse: collapse; width: 100%; font-size: 8.5pt; margin: 10px 0; }
th, td { border: 1px solid #b9c8d4; padding: 5px; vertical-align: top; overflow-wrap: anywhere; }
th { background: #e8f1f7; }
tr { break-inside: avoid; }
pre { white-space: pre-wrap; overflow-wrap: anywhere; background: #f4f6f8; padding: 8px; font-size: 8pt; }
code { font-family: Consolas, monospace; font-size: .9em; overflow-wrap: anywhere; }
blockquote { border-left: 3px solid #aac3d5; padding-left: 10px; color: #334b5b; }
img { max-width: 100%; }
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if not CHROME.is_file():
        parser.error(f"Chrome not found at {CHROME}")
    source = args.source.resolve()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    body = markdown.markdown(source.read_text(encoding="utf-8"), extensions=["tables", "fenced_code", "toc"])
    title = html.escape(source.stem)
    base_uri = source.parent.as_uri() + "/"
    page = f'<!doctype html><html lang="vi"><head><meta charset="utf-8"><base href="{base_uri}"><title>{title}</title><style>{CSS}</style></head><body>{body}</body></html>'
    with tempfile.TemporaryDirectory(prefix="hw05_pdf_") as temp:
        temp_dir = Path(temp)
        html_file = temp_dir / "input.html"
        html_file.write_text(page, encoding="utf-8")
        cmd = [str(CHROME), "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--user-data-dir={temp_dir / 'profile'}", f"--print-to-pdf={output}", html_file.as_uri()]
        done = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if done.returncode != 0 or not output.is_file():
            raise RuntimeError(f"Chrome PDF failed ({done.returncode}): {done.stderr[-1200:]}")
    print(f"{output} ({output.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
