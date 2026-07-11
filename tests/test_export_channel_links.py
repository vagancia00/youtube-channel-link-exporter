from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "export_channel_links.py"
SPEC = importlib.util.spec_from_file_location("export_channel_links", SCRIPT)
assert SPEC and SPEC.loader
exporter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(exporter)

SAMPLE = """<!doctype html>
<html lang="es-MX">
<head><title>Sample Engineering - YouTube</title></head>
<body><ytd-rich-grid-renderer>
<ytd-rich-item-renderer><h3><a href="/watch?v=aaaaaaaaaaa">A</a></h3><span>hace 2 días</span></ytd-rich-item-renderer>
<ytd-rich-item-renderer><h3><a href="/watch?v=bbbbbbbbbbb">B</a></h3><span>hace 3 meses</span></ytd-rich-item-renderer>
<ytd-rich-item-renderer><h3><a href="/shorts/ccccccccccc">C</a></h3><span>hace 3 años</span></ytd-rich-item-renderer>
<ytd-rich-item-renderer><h3><a href="/watch?v=ddddddddddd">D</a></h3><span>hace 4 años</span></ytd-rich-item-renderer>
</ytd-rich-grid-renderer></body></html>"""


class ExporterTests(unittest.TestCase):
    def test_channel_name(self) -> None:
        self.assertEqual(exporter.channel_name(SAMPLE, Path("fallback.html")), "Sample Engineering")

    def test_extracts_in_source_order_and_deduplicates(self) -> None:
        records, loading = exporter.extract(SAMPLE)
        self.assertFalse(loading)
        self.assertEqual([record[0] for record in records], [
            "aaaaaaaaaaa", "bbbbbbbbbbb", "ccccccccccc", "ddddddddddd"
        ])

    def test_duration_parser(self) -> None:
        self.assertAlmostEqual(exporter.duration("4y"), 1461.0)
        self.assertAlmostEqual(exporter.duration("6mo"), 182.625)

    def test_writes_links_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "channel.html"
            destination = root / "output"
            source.write_text(SAMPLE, encoding="utf-8")
            code = exporter.main([
                str(source), "--output-dir", str(destination), "--overwrite"
            ])
            self.assertEqual(code, 0)
            output = destination / "Sample Engineering.txt"
            self.assertEqual(output.read_text(encoding="utf-8").splitlines(), [
                "https://www.youtube.com/watch?v=aaaaaaaaaaa",
                "https://www.youtube.com/watch?v=bbbbbbbbbbb",
                "https://www.youtube.com/watch?v=ccccccccccc",
                "https://www.youtube.com/watch?v=ddddddddddd",
            ])

    def test_excludes_shorts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "channel.html"
            destination = root / "output"
            source.write_text(SAMPLE, encoding="utf-8")
            code = exporter.main([
                str(source), "--output-dir", str(destination), "--exclude-shorts", "--overwrite"
            ])
            self.assertEqual(code, 0)
            self.assertNotIn("ccccccccccc", (destination / "Sample Engineering.txt").read_text())


if __name__ == "__main__":
    unittest.main()
