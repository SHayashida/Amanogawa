# Contributing

Thanks for your interest in contributing to Amanogawa.

## What to contribute
- Bug reports and minimal repro cases (ideally with a small sample input).
- Documentation improvements (README, notebooks, docstrings).
- Unit tests for core functions.
- Performance improvements (while keeping results reproducible).

## Development setup

Clone the repository and install in development mode:

```bash
git clone https://github.com/SHayashida/Amanogawa.git
cd Amanogawa

python -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"  # Installs package + dev dependencies (pytest, ruff)
```

Verify the installation:

```bash
pytest  # All tests should pass
ruff check src tests  # Linting should pass
```

## Pull requests
- Keep PRs focused (one change theme per PR).
- Add/adjust tests when behavior changes.
- Prefer pure-Python + NumPy/SciPy implementations over new heavy dependencies.

## Reporting security issues
Please do not open a public issue for security-sensitive reports.
Use the contact in SECURITY.md.
