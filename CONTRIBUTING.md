# Contributing

Thanks for your interest in contributing to Amanogawa.

## What to contribute

### Code and documentation contributions
- Bug reports and minimal repro cases (ideally with a small sample input).
- Documentation improvements (README, notebooks, docstrings).
- Unit tests for core functions.
- Performance improvements (while keeping results reproducible).

### Data contributions (citizen science)

We welcome smartphone Milky Way images and measurements from citizen astronomers worldwide!

- **Share your observations**: Smartphone long exposures from your location provide geographic diversity.
- **Report findings**: Share interesting stellar clustering patterns or dark-lane morphology you discover.
- **Build the dataset**: Community observations strengthen the dataset for future collaborative analysis.
- **Help validate**: Test Amanogawa on images from different cameras, locations, and seasons.

If you have data to contribute, please open an issue with:
- Image metadata (location, date, equipment)
- Amanogawa output (star coordinates, spatial statistics)
- Any interesting observations or patterns you notice

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
