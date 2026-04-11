#!/usr/bin/env python3
import argparse
import json
import re
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import date, timedelta
from pathlib import Path
from typing import List

DATE_FILE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:.*)?\.md$")
DATE_HEADER_RE = re.compile(r"^#\s+\d{4}-\d{2}-\d{2}\s*$", re.MULTILINE)
SECTION_SPLIT_RE = re.compile(r"(?m)^##\s+")


@dataclass
class FileReport:
    file: str
    duplicate_date_headers: int
    duplicate_sections: int
    duplicate_section_titles: List[str]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Find duplicate headers/sections in daily memory files.")
    p.add_argument("files", nargs="*", help="Specific daily memory files to scan")
    p.add_argument("--root", default="/home/node/.openclaw/workspace/memory", help="Memory directory root")
    p.add_argument("--days", type=int, default=None, help="Only scan files whose YYYY-MM-DD filename falls within the last N days")
    p.add_argument("--json", action="store_true", help="Emit JSON")
    return p.parse_args()


def iter_files(root: Path, files: List[str], days: int | None) -> List[Path]:
    if files:
        return [Path(f) for f in files]

    candidates = sorted(root.glob("*.md"))
    if days is None:
        return candidates

    cutoff = date.today() - timedelta(days=max(days - 1, 0))
    selected = []
    for path in candidates:
        m = DATE_FILE_RE.match(path.name)
        if not m:
            continue
        try:
            d = date.fromisoformat(m.group(1))
        except ValueError:
            continue
        if d >= cutoff:
            selected.append(path)
    return selected


def scan_file(path: Path) -> FileReport:
    text = path.read_text(encoding="utf-8")

    date_header_count = len(DATE_HEADER_RE.findall(text))
    duplicate_date_headers = max(date_header_count - 1, 0)

    duplicate_titles: List[str] = []
    seen_sections = defaultdict(int)

    parts = SECTION_SPLIT_RE.split(text)
    for part in parts[1:]:
        normalized = ("## " + part.strip()).strip()
        if not normalized:
            continue
        title = normalized.splitlines()[0]
        seen_sections[normalized] += 1
        if seen_sections[normalized] == 2:
            duplicate_titles.append(title)

    duplicate_sections = len(duplicate_titles)
    return FileReport(
        file=str(path),
        duplicate_date_headers=duplicate_date_headers,
        duplicate_sections=duplicate_sections,
        duplicate_section_titles=duplicate_titles,
    )


def main() -> int:
    args = parse_args()
    root = Path(args.root)
    files = iter_files(root, args.files, args.days)
    reports = [scan_file(path) for path in files if path.exists() and path.is_file()]
    reports = [r for r in reports if r.duplicate_date_headers or r.duplicate_sections]

    if args.json:
        print(json.dumps([asdict(r) for r in reports], ensure_ascii=False, indent=2))
        return 0

    if not reports:
        print("No exact duplicate daily-memory sections or extra date headers found.")
        return 0

    for report in reports:
        print(report.file)
        print(f"  duplicate_date_headers: {report.duplicate_date_headers}")
        print(f"  duplicate_sections: {report.duplicate_sections}")
        if report.duplicate_section_titles:
            for title in report.duplicate_section_titles:
                print(f"    - {title}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
