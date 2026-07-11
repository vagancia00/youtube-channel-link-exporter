#!/usr/bin/env python3
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = "youtube-channel-link-exporter"
INCLUDE = [
    "SKILL.md",
    "LICENSE",
    "scripts/export_channel_links.py",
    "assets/icon.svg",
]


def package_skill(root: Path, destination: Path) -> Path:
    destination = destination.expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative in INCLUDE:
            source = root / relative
            if source.is_file():
                archive.write(source, f"{SKILL_NAME}/{relative}")
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description="Package the repository as a .skill archive.")
    parser.add_argument("destination", nargs="?", type=Path, default=ROOT / f"{SKILL_NAME}.skill")
    args = parser.parse_args()
    result = package_skill(ROOT, args.destination)
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
