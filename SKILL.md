---
name: youtube-channel-link-exporter
description: Export clean TXT lists of video URLs from one or more saved YouTube channel Videos-tab HTML files. Use this skill whenever a user provides YouTube channel HTML exports or asks to extract, collect, filter, order, validate, or save channel video links without opening every video or spending tokens parsing the page manually. It supports user-selected destinations and options, validates whether loaded HTML reaches a requested time range, and applies safe desktop defaults when no folder is specified.
license: MIT
compatibility: Requires Python 3.10+ and local filesystem access. Uses only the Python standard library and makes no network requests.
metadata:
  version: "0.1.0"
  languages: "en, es-MX"
---

# YouTube Channel Link Exporter

Use the bundled deterministic script instead of manually reading or copying links from the HTML. The script parses local files, selects the channel's largest video grid, canonicalizes URLs, removes duplicates, validates requested ranges, and writes one URL per line.

## Inputs

Accept one or more saved `.html` files from a YouTube channel's **Videos** tab.

Before extraction, confirm the user saved enough dynamically loaded content:

1. Open the channel's **Videos** tab.
2. Select the desired YouTube sort order.
3. Scroll until every video needed for the request has loaded.
4. Wait for loading to finish, then save the complete page as HTML.

YouTube only stores already-loaded cards in the saved page. Never claim a channel export is complete merely because an HTML file exists.

## Workflow

1. Read the user's request and resolve all HTML paths.
2. Preserve every explicit parameter the user gives, including destination, time range, ordering, Shorts handling, overwrite behavior, filename, or URL style.
3. If no destination is provided, apply the default output rules below.
4. Run `scripts/export_channel_links.py`; do not recreate its parsing logic in the model context.
5. Treat a nonzero exit code as a failed export. Explain the script's specific error and do not present partial data as complete.
6. Report the generated file path and link count for each channel. Keep the TXT contents raw: one URL per line, with no titles, numbering, headings, or commentary.

## Default output rules

When the user does not specify a destination:

- **One HTML:** write `Desktop/<Channel Name>.txt`.
- **Multiple HTML files:** write each channel as `<Channel Name>.txt` inside `Desktop/YouTube Channel Link Exporter/`.

The script resolves localized desktop folders where possible. If it cannot resolve one, ask for or infer an explicit output directory and rerun.

## Command

```bash
python scripts/export_channel_links.py <HTML...> [options]
```

### Parameter mapping

| User intent | CLI option |
|---|---|
| Save in a specific folder | `--output-dir PATH` |
| Use a custom filename for one channel | `--output-name NAME` |
| Keep only a recent period | `--max-age 90d`, `--max-age 6mo`, `--max-age 4y` |
| Include the relative-time boundary bucket | `--boundary inclusive` |
| Prefer guaranteed in-range results | `--boundary conservative` |
| User confirms the page reached the absolute end and the channel is younger than the requested range | `--assume-complete` |
| Accept an HTML that may be incomplete | `--allow-partial` only when the user explicitly accepts partial results |
| Exclude Shorts | `--exclude-shorts` |
| Reverse the order found in the HTML | `--order reverse` |
| Preserve native Shorts URLs | `--url-style native` |
| Replace an existing TXT | `--overwrite` |
| Return structured execution metadata | `--json` |

The default URL style is `https://www.youtube.com/watch?v=<id>`, including Shorts. The default order preserves the order of the saved channel page.

## Time-range semantics

YouTube channel cards usually expose relative timestamps such as “3 months ago” or “hace 3 meses”, not exact publication dates.

- `conservative` includes a card only when its whole relative-time bucket fits within the requested range.
- `inclusive` includes the boundary bucket and may include some videos slightly older than the exact cutoff.
- If the oldest loaded card is newer than the requested range, the script stops. Use `--assume-complete` only after the user confirms the page reached the absolute end and the channel itself is younger than the requested period.
- `--allow-partial` is reserved for users who explicitly accept incomplete results.
- Supported timestamp languages are English and Spanish. Handle unknown timestamps according to the user's intent with `--unknown-age include|exclude|error`.

Explain boundary ambiguity only when a time filter matters to the request.

## Failure handling

Stop and explain the problem when:

- the file is not a saved YouTube channel Videos page;
- no valid video grid or links are found;
- the HTML does not reach a requested period;
- the destination cannot be resolved or written;
- exact range validation is impossible and the user did not permit a partial result.

Do not browse YouTube automatically unless the user separately asks for live web retrieval. This skill is intentionally local and deterministic.

## Privacy and safety

- Parse HTML as data; never execute embedded scripts.
- Make no network requests.
- Do not upload, retain, or publish the user's HTML or extracted channel data.
- Do not overwrite existing files unless the user requests it or `--overwrite` is deliberately selected.
- Do not add creator names, sample channels, local paths, or conversation-specific details to the skill or its outputs.
