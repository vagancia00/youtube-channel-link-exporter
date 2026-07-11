# Contributing

Contributions are welcome when they preserve the project's narrow contract: convert saved YouTube channel HTML into reliable links-only TXT files through a portable Agent Skill.

## Before opening a change

- Search existing issues and pull requests.
- Keep examples generic and synthetic.
- Do not commit real channel exports, cookies, browser profiles, local paths or extracted private data.
- Avoid adding network access unless the project scope is explicitly changed and reviewed.
- Keep extraction deterministic instead of asking a model to parse repetitive HTML.

## Development

Python 3.10 or later is sufficient. Runtime code uses only the standard library.

```bash
python -m unittest discover -s tests -v
python scripts/check_repository.py
python scripts/package_skill.py
```

## Pull requests

A pull request should explain the behavior being changed, include tests with synthetic data, preserve the one-URL-per-line contract and update both English and Mexican Spanish documentation when user-facing behavior changes.
