#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from html import unescape
from pathlib import Path

SKILL_NAME = "YouTube Channel Link Exporter"
VIDEO_RE = re.compile(r'(?:https?://(?:www\.)?youtube\.com)?/(?:watch\?[^"\'<> ]*?v=|shorts/)([A-Za-z0-9_-]{11})')
TITLE_RE = re.compile(r'<title[^>]*>(.*?)</title>', re.I | re.S)
ITEM_RE = re.compile(r'<ytd-rich-item-renderer\b.*?</ytd-rich-item-renderer>', re.I | re.S)
GRID_RE = re.compile(r'<ytd-rich-grid-renderer\b.*?</ytd-rich-grid-renderer>', re.I | re.S)
AGE_ES = re.compile(r'hace\s+(\d+|un|una)\s+(minutos?|horas?|d[ií]as?|semanas?|mes(?:es)?|a[nñ]os?)', re.I)
AGE_EN = re.compile(r'(\d+|a|an|one)\s+(minutes?|hours?|days?|weeks?|months?|years?)\s+ago', re.I)
INVALID = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


class ExportError(RuntimeError):
    pass


def clean_text(value: str) -> str:
    return re.sub(r'\s+', ' ', unescape(re.sub(r'<[^>]+>', ' ', value))).strip()


def channel_name(html: str, source: Path) -> str:
    match = TITLE_RE.search(html)
    if match:
        title = clean_text(match.group(1))
        title = re.sub(r'\s*[-–—]\s*YouTube\s*$', '', title, flags=re.I).strip()
        if title and title.lower() != 'youtube':
            return title
    return re.sub(r'\s*[-–—]\s*YouTube\s*$', '', source.stem, flags=re.I).strip() or 'YouTube Channel'


def sanitize(name: str) -> str:
    value = INVALID.sub('_', re.sub(r'\s+', ' ', name).strip()).rstrip(' .')
    return value[:180] or 'YouTube Channel'


def age_days(text: str) -> tuple[float, float] | None:
    normalized = clean_text(text).lower()
    match = AGE_ES.search(normalized) or AGE_EN.search(normalized)
    if not match:
        return None
    raw_n, raw_unit = match.groups()
    n = 1 if raw_n.lower() in {'un', 'una', 'a', 'an', 'one'} else int(raw_n)
    unit = raw_unit.lower()
    if unit.startswith(('minut', 'minute')):
        factor, width = 1 / 1440, 1 / 1440
    elif unit.startswith(('hora', 'hour')):
        factor, width = 1 / 24, 1 / 24
    elif unit.startswith(('día', 'dia', 'day')):
        factor, width = 1, 1
    elif unit.startswith(('semana', 'week')):
        factor, width = 7, 7
    elif unit.startswith(('mes', 'month')):
        factor, width = 30.4375, 30.4375
    else:
        factor, width = 365.25, 365.25
    return n * factor, (n + 1) * width


def duration(value: str) -> float:
    match = re.fullmatch(r'\s*(\d+(?:\.\d+)?)\s*(d|day|days|w|week|weeks|mo|month|months|y|year|years)\s*', value, re.I)
    if not match:
        raise argparse.ArgumentTypeError('Use durations such as 90d, 6mo or 4y.')
    n, unit = float(match.group(1)), match.group(2).lower()
    factors = {'d': 1, 'day': 1, 'days': 1, 'w': 7, 'week': 7, 'weeks': 7,
               'mo': 30.4375, 'month': 30.4375, 'months': 30.4375,
               'y': 365.25, 'year': 365.25, 'years': 365.25}
    return n * factors[unit]


def extract(html: str) -> tuple[list[tuple[str, str, bool, tuple[float, float] | None]], bool]:
    grids = GRID_RE.findall(html)
    region = max(grids, key=lambda grid: len(ITEM_RE.findall(grid))) if grids else html
    items = ITEM_RE.findall(region) or [region]
    records: list[tuple[str, str, bool, tuple[float, float] | None]] = []
    seen: set[str] = set()
    for item in items:
        matches = list(VIDEO_RE.finditer(item.replace('&amp;', '&')))
        if not matches:
            continue
        video_id = matches[0].group(1)
        if video_id in seen:
            continue
        seen.add(video_id)
        is_short = f'/shorts/{video_id}' in item
        records.append((video_id, item, is_short, age_days(item)))
    loading = bool(re.search(r'ytd-ghost-grid-renderer|id=["\']ghost-cards["\']', region, re.I))
    return records, loading


def desktop() -> Path:
    for candidate in (Path.home() / 'Desktop', Path.home() / 'Escritorio'):
        if candidate.is_dir():
            return candidate
    raise ExportError('No desktop directory found; specify --output-dir.')


def unique(path: Path, overwrite: bool) -> Path:
    if overwrite or not path.exists():
        return path
    index = 2
    while True:
        candidate = path.with_name(f'{path.stem} ({index}){path.suffix}')
        if not candidate.exists():
            return candidate
        index += 1


def process(source: Path, args: argparse.Namespace, out_dir: Path) -> dict:
    html = source.read_text(encoding='utf-8', errors='ignore')
    name = channel_name(html, source)
    records, loading = extract(html)
    if not records:
        raise ExportError(f'No YouTube video links found in {source.name}.')

    if args.max_age is not None:
        known = [record[3][1] for record in records if record[3] is not None]
        oldest = max(known) if known else None
        if oldest is None:
            raise ExportError(f'No supported relative timestamps found in {source.name}.')
        if oldest < args.max_age and not args.allow_partial and not args.assume_complete:
            raise ExportError(f'{source.name} does not reach the requested period. Scroll farther before saving, or use --allow-partial.')
        if loading and args.assume_complete:
            raise ExportError(f'{source.name} still contains loading placeholders and cannot be treated as complete.')
        filtered = []
        for record in records:
            interval = record[3]
            if interval is None:
                if args.unknown_age == 'include':
                    filtered.append(record)
                elif args.unknown_age == 'error':
                    raise ExportError('A video has no supported relative timestamp.')
                continue
            lower, upper = interval
            include = upper <= args.max_age if args.boundary == 'conservative' else lower <= args.max_age
            if include:
                filtered.append(record)
        records = filtered

    if args.exclude_shorts:
        records = [record for record in records if not record[2]]
    if args.order == 'reverse':
        records.reverse()

    lines = [
        f'https://www.youtube.com/shorts/{record[0]}'
        if args.url_style == 'native' and record[2]
        else f'https://www.youtube.com/watch?v={record[0]}'
        for record in records
    ]
    output_name = args.output_name if args.output_name and len(args.html) == 1 else name
    target = unique(out_dir / f'{sanitize(output_name)}.txt', args.overwrite)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('\n'.join(lines) + ('\n' if lines else ''), encoding='utf-8')
    return {'source': str(source), 'channel': name, 'output': str(target), 'video_count': len(lines), 'warnings': []}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description='Export video links from saved YouTube channel HTML files.')
    parser.add_argument('html', nargs='+')
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--output-name')
    parser.add_argument('--max-age', type=duration)
    parser.add_argument('--boundary', choices=('conservative', 'inclusive'), default='conservative')
    parser.add_argument('--unknown-age', choices=('exclude', 'include', 'error'), default='exclude')
    parser.add_argument('--assume-complete', action='store_true')
    parser.add_argument('--allow-partial', action='store_true')
    parser.add_argument('--exclude-shorts', action='store_true')
    parser.add_argument('--order', choices=('source', 'reverse'), default='source')
    parser.add_argument('--url-style', choices=('watch', 'native'), default='watch')
    parser.add_argument('--overwrite', action='store_true')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)

    if len(args.html) > 1 and args.output_name:
        parser.error('--output-name is valid only with one HTML file.')

    try:
        sources = [Path(path).expanduser().resolve() for path in args.html]
        missing = [str(path) for path in sources if not path.is_file()]
        if missing:
            raise ExportError('Input file(s) not found: ' + ', '.join(missing))
        out_dir = args.output_dir.expanduser().resolve() if args.output_dir else (
            desktop() if len(sources) == 1 else desktop() / SKILL_NAME
        )
        results = [process(source, args, out_dir) for source in sources]
    except (ExportError, OSError) as exc:
        if getattr(args, 'json', False):
            print(json.dumps({'error': str(exc)}, ensure_ascii=False, indent=2))
        else:
            print(f'ERROR: {exc}', file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps({'exports': results}, ensure_ascii=False, indent=2))
    else:
        for result in results:
            print(f"WROTE\t{result['output']}\t{result['video_count']}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
