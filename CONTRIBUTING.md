# Contributing

Thanks for your interest in contributing to Amanogawa.

## What to contribute
- Bug reports and minimal repro cases (ideally with a small sample input).
- Documentation improvements (README, notebooks, docstrings).
- Unit tests for core functions.
- Performance improvements (while keeping results reproducible).

## Development setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
```

## Pull requests
- Keep PRs focused (one change theme per PR).
- Add/adjust tests when behavior changes.
- Prefer pure-Python + NumPy/SciPy implementations over new heavy dependencies.

## Reporting security issues
Please do not open a public issue for security-sensitive reports.
Use the contact in SECURITY.md.
