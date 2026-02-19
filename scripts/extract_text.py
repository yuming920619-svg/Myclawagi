#!/usr/bin/env python3
"""
Extract plain text from PDF/Word files for quick analysis.

Supported formats:
- .pdf  (via `pdftotext` if available, otherwise pypdf/PyPDF2)
- .docx (pure-Python XML extraction, no external dependency)
- .doc  (via `antiword` if available)

Examples:
  python3 scripts/extract_text.py hamming1/hamming.pdf
  python3 scripts/extract_text.py hamming1/hamming_rules.docx -o hamming1/hamming_rules.txt
  python3 scripts/extract_text.py hamming1/hamming.pdf --max-chars 5000 --stdout
"""

from __future__ import annotations

import argparse
import html
import re
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Optional


def run_cmd(cmd: list[str]) -> Optional[str]:
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if proc.returncode == 0:
            return proc.stdout
        return None
    except FileNotFoundError:
        return None


def extract_pdf(path: Path) -> str:
    # Best quality when poppler is installed.
    text = run_cmd(["pdftotext", "-layout", str(path), "-"])
    if text is not None:
        return text

    # Fallback to Python libs if installed.
    for mod in ("pypdf", "PyPDF2"):
        try:
            if mod == "pypdf":
                from pypdf import PdfReader  # type: ignore
            else:
                from PyPDF2 import PdfReader  # type: ignore

            reader = PdfReader(str(path))
            pages = []
            for p in reader.pages:
                pages.append(p.extract_text() or "")
            return "\n\n".join(pages)
        except Exception:
            continue

    raise RuntimeError(
        "Cannot parse PDF. Install one of: pdftotext (poppler), pypdf, or PyPDF2."
    )


def extract_docx(path: Path) -> str:
    # No dependency approach: read WordprocessingML XML.
    with zipfile.ZipFile(path, "r") as zf:
        xml_bytes = zf.read("word/document.xml")

    xml_text = xml_bytes.decode("utf-8", errors="ignore")

    # Preserve paragraph boundaries first.
    xml_text = re.sub(r"</w:p>", "\n", xml_text)
    xml_text = re.sub(r"</w:tr>", "\n", xml_text)

    # Strip all XML tags.
    plain = re.sub(r"<[^>]+>", "", xml_text)
    plain = html.unescape(plain)

    # Normalize whitespace.
    plain = re.sub(r"\r\n?", "\n", plain)
    plain = re.sub(r"\n{3,}", "\n\n", plain)
    return plain.strip() + "\n"


def extract_doc(path: Path) -> str:
    text = run_cmd(["antiword", str(path)])
    if text is not None:
        return text
    raise RuntimeError("Cannot parse .doc. Install `antiword`.")


def extract_text(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".pdf":
        return extract_pdf(path)
    if ext == ".docx":
        return extract_docx(path)
    if ext == ".doc":
        return extract_doc(path)
    raise ValueError(f"Unsupported file type: {ext}")


def default_output_path(inp: Path) -> Path:
    return inp.with_suffix(inp.suffix + ".txt")


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract text from PDF/DOC/DOCX")
    parser.add_argument("input", type=Path, help="Input file path")
    parser.add_argument("-o", "--output", type=Path, help="Output .txt path")
    parser.add_argument("--stdout", action="store_true", help="Print extracted text to stdout")
    parser.add_argument("--max-chars", type=int, default=0, help="Truncate output to N chars (0 = no limit)")

    args = parser.parse_args()
    inp: Path = args.input

    if not inp.exists() or not inp.is_file():
        print(f"[ERROR] File not found: {inp}", file=sys.stderr)
        return 2

    try:
        text = extract_text(inp)
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1

    if args.max_chars and args.max_chars > 0:
        text = text[: args.max_chars]

    if args.stdout or not args.output:
        print(text, end="" if text.endswith("\n") else "\n")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"[OK] Wrote: {args.output}", file=sys.stderr)
    elif not args.stdout:
        out = default_output_path(inp)
        out.write_text(text, encoding="utf-8")
        print(f"[OK] Wrote: {out}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
