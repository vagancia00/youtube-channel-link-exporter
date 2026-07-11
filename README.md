<div align="center">
  <img src="assets/banner.svg" alt="YouTube Channel Link Exporter" width="100%">

  <p><strong>Export clean video-link lists from saved YouTube channel HTML with a reusable Agent Skill.</strong></p>

  <p>
    <a href="https://agentskills.io"><img alt="Agent Skills" src="https://img.shields.io/badge/Agent%20Skills-open%20standard-ff3355?style=flat-square"></a>
    <img alt="Python 3.10+" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white">
    <img alt="Standard library only" src="https://img.shields.io/badge/runtime-standard%20library-21262d?style=flat-square">
    <img alt="No network" src="https://img.shields.io/badge/network-none-238636?style=flat-square">
    <a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-f0f6fc?style=flat-square"></a>
    <a href="https://github.com/vagancia00/youtube-channel-link-exporter/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/vagancia00/youtube-channel-link-exporter/actions/workflows/ci.yml/badge.svg"></a>
  </p>

  <p><a href="README.es-MX.md">Documentación en español de México</a></p>
</div>

## What is it?

YouTube Channel Link Exporter is a portable Agent Skill that receives one or more HTML files saved from a YouTube channel's **Videos** tab and writes clean UTF-8 `.txt` files containing one canonical video URL per line.

The agent interprets the user's natural-language parameters. A deterministic Python script performs extraction, deduplication, range validation and file writing without spending model context on repetitive HTML parsing.

It exports **links only**. It does not download video media.

## Features

- One or many channel HTML files per invocation.
- Automatic channel-name detection and filesystem-safe filenames.
- Canonical `watch?v=` URLs with optional native Shorts URLs.
- Deduplication while preserving the saved page order.
- Optional approximate time filtering such as `90d`, `6mo` or `4y`.
- Validation that the loaded HTML reaches the requested period.
- English and Spanish relative timestamp support.
- Safe default destinations on Windows, macOS and Linux.
- Local-only execution with no third-party runtime dependencies or network requests.
- Bilingual documentation and Agent Skill evaluation fixtures.

## Why an Agent Skill?

The workflow has two layers:

1. **Agent reasoning:** understand the user's files, destination, range, order and exceptions.
2. **Deterministic execution:** parse the HTML and write the exact output reliably.

This keeps the reusable instructions small, lowers token use and prevents a model from manually reconstructing hundreds of links.

## Save a usable YouTube HTML file

YouTube loads channel cards dynamically. Before saving the page:

1. Open the channel's **Videos** tab.
2. Select the desired sort order.
3. Scroll until every video needed for the export has loaded.
4. Wait for loading to stop.
5. Save the complete page as HTML.

A saved file contains only the cards that were already loaded. The skill can validate whether a requested time range is covered, but it cannot recover videos absent from the HTML.

## Installation

Clone or download this repository and place the complete folder in the skills directory supported by your agent host. Keep the directory name as:

```text
youtube-channel-link-exporter
```

The exporter can also be used directly with Python 3.10 or newer:

```bash
python scripts/export_channel_links.py --help
```

## Natural-language examples

```text
Extract every loaded video link from this channel HTML.
```

```text
Use these three YouTube channel HTML files and save one TXT per channel in D:\Research\Sources.
```

```text
Export only videos from approximately the last four years, newest first. Do not accept a partial HTML.
```

## Default output behavior

| Input | Output |
|---|---|
| One HTML file | `Desktop/<Channel Name>.txt` |
| Multiple HTML files | `Desktop/YouTube Channel Link Exporter/<Channel Name>.txt` |

An existing file is not replaced by default. A numeric suffix is added unless overwrite is explicitly requested.

## Output contract

Each generated TXT contains only URLs:

```text
https://www.youtube.com/watch?v=aaaaaaaaaaa
https://www.youtube.com/watch?v=bbbbbbbbbbb
https://www.youtube.com/watch?v=ccccccccccc
```

No titles, numbering, headings, comments or metadata are inserted.

## Privacy and security

- HTML is parsed as inert local data.
- Embedded JavaScript is never executed.
- No page contents, URLs or filenames are sent over the network.
- No credentials, cookies or browser sessions are required.
- Existing output files are preserved unless overwrite behavior is selected.

## Development

```bash
python -m unittest discover -s tests -v
python scripts/check_repository.py
python scripts/package_skill.py
```

## License

Released under the [MIT License](LICENSE).

## Trademark notice

YouTube is a trademark of Google LLC. This project is independent, is not endorsed by Google, and interacts only with HTML files saved by the user.
