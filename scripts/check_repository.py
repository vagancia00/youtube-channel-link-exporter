#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "SKILL.md",
    "README.md",
    "README.es-MX.md",
    "LICENSE",
    "scripts/export_channel_links.py",
    "tests/test_export_channel_links.py",
]
FORBIDDEN = [
    re.compile(r"Fazt", re.I),
    re.compile(r"/mnt/data/", re.I),
    re.compile(r"C:\\\\Users\\", re.I),
    re.compile(r"AIza[0-9A-Za-z_-]{20,}"),
]


def main() -> int:
    errors: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"Missing required file: {relative}")

    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if not skill.startswith("---\n"):
        errors.append("SKILL.md is missing YAML frontmatter")
    if "\nname: youtube-channel-link-exporter\n" not in skill:
        errors.append("SKILL.md has an unexpected name")
    if "\ndescription: " not in skill:
        errors.append("SKILL.md is missing description")

    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts:
            continue
        if path.suffix.lower() not in {".md", ".py", ".toml", ".yml", ".yaml", ".json", ".svg", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in FORBIDDEN:
            if pattern.search(text):
                errors.append(f"Potential private or conversation-specific content in {path.relative_to(ROOT)}")

    if errors:
        print("Repository validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Repository validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
