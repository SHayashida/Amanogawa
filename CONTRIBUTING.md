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

### Verifying clean installation (for reviewers and CI parity)

To verify that the package installs and tests pass in a fresh environment (as JOSS reviewers will test):

**On your local machine:**
```bash
# Create a new temporary venv
python -m venv /tmp/amanogawa-test
source /tmp/amanogawa-test/bin/activate

# Install from your local clone
pip install -e ".[dev]"

# Verify import works
python -c "import amanogawa; print('Import OK')"

# Run tests
pytest

# Clean up
deactivate
rm -rf /tmp/amanogawa-test
```

**Or use Docker (guaranteed clean environment):**
```bash
docker run -v "$PWD:/work" -w /work python:3.10-slim bash -c "
  pip install -e '.[dev]' && \
  python -c 'import amanogawa; print(\"Import OK\")' && \
  pytest
"
```

This ensures that `pip install -e .` works without additional configuration, exactly as reviewers will experience it.

You can locally compile the manuscript for review and verification.

### HTML (with citations)

```bash
pandoc paper/paper.md \
	--from=markdown --to=html \
	--citeproc --bibliography=paper/paper.bib \
	--resource-path=paper \
	-o paper/paper.html
```

### PDF (XeLaTeX)

```bash
pandoc paper/paper.md \
	--pdf-engine=xelatex \
	--citeproc --bibliography=paper/paper.bib \
	--resource-path=paper \
	-o paper/paper.pdf
```

Notes:
- Figures live under `paper/figures/`; the manuscript references `figures/sample_star_detection_overlay.png`.
- `--resource-path=paper` ensures images and bibliography resolve when building inside containers or mounted volumes.
- `paper/paper.pdf` is intentionally ignored by `.gitignore`; commit only `paper/paper.md` and `paper/paper.bib`.

### Docker-friendly commands

```bash
# HTML
docker run --rm -v "$PWD/paper:/data" pandoc/core:latest \
	-f markdown -t html --citeproc --bibliography=/data/paper.bib \
	--resource-path=/data \
	-o /data/paper.html /data/paper.md

# PDF (image must include a LaTeX engine like xelatex)
docker run --rm -v "$PWD/paper:/data" pandoc/core:latest \
	--pdf-engine=xelatex --citeproc --bibliography=/data/paper.bib \
	--resource-path=/data \
	-o /data/paper.pdf /data/paper.md
```

## Pull requests
- Keep PRs focused (one change theme per PR).
- Add/adjust tests when behavior changes.
- Prefer pure-Python + NumPy/SciPy implementations over new heavy dependencies.

## Reporting security issues
Please do not open a public issue for security-sensitive reports.
Use the contact in SECURITY.md.
