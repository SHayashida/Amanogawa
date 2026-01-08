<!-- NOTE: Japanese version lives in README_ja.md -->
# Amanogawa

Quantifying Milky Way stellar clustering and dark-lane morphology from a single smartphone exposure.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](#license)

[Open in Colab: Band Analysis](https://colab.research.google.com/github/SHayashida/Amanogawa/blob/main/notebooks/01_band_analysis.ipynb)

[Open in Colab: Dark Morphology](https://colab.research.google.com/github/SHayashida/Amanogawa/blob/main/notebooks/02_dark_morphology.ipynb)

English | [日本語 / Japanese](./README_ja.md)

## Statement of need

Wide-field Milky Way images (including consumer smartphone long exposures) contain measurable structure: clustered stellar fields and dust-driven dark lanes. Amanogawa provides a compact, reproducible pipeline that extracts quantitative metrics (clustering statistics, principal-axis/width estimates, and dark-lane morphology) from a single image to support citizen-science workflows and lightweight scientific exploration.

## What is included

- **Core library:** installable Python package under `src/amanogawa/`.
- **CLIs:** entry points for the main steps (`amanogawa-*`).
- **Notebooks:** tutorials under `notebooks/` that exercise the library and reproduce figures.
- **JOSS paper:** `paper/paper.md` (+ `paper/paper.bib`).

## Installation

> Tested & recommended with **Python 3.12.x**. Avoid 3.13 for now.

```bash
python -m venv .venv
source .venv/bin/activate

pip install -e .
```

For development (tests/lint):

```bash
pip install -e ".[dev]"
```

### Docker-based installation (for reviewers and verification)

If you encounter build issues on Mac or want a clean environment for verification:

```bash
docker run -it --rm python:3.10-slim /bin/bash
```

Inside the container:

```bash
# 1. Install system packages required for building
apt-get update
apt-get install -y gcc g++ build-essential python3-dev

# 2. Install photutils separately to avoid build failures
pip install --no-cache-dir photutils

# 3. Continue with installation
pip install -r requirements.txt
pip install -e .
```

Verify the installation:

```bash
cd /  # Move outside the project directory
python3 -c "import amanogawa; print('Success')"
```

If you see `Success`, the installation was successful and paths are correctly configured.

## Quick start (CLI)

Place an image in `data/raw/` (the repository ships `data/raw/IMG_5991.jpg`).

1. Star detection (writes coordinates CSV + threshold sweep summaries):

```bash
amanogawa-detect --image data/raw/IMG_5991.jpg --out outputs/ \
  --threshold-min 0.03 --threshold-max 0.08 --steps 10
```

1. Spatial statistics (two-point correlation, NND, box-count fractal dimension):

```bash
amanogawa-stats --coords outputs/IMG_5991_star_coords.csv --out outputs/
```

1. Band geometry (principal axis + Gaussian/Lorentzian width fits):

```bash
amanogawa-band --coords outputs/IMG_5991_star_coords.csv --width 4032 --height 3024 --out outputs/
```

1. Dark morphology (dark-lane mask + morphology metrics):

```bash
amanogawa-dark --image data/raw/IMG_5991.jpg --out outputs/dark_morphology/results
```

This writes:

- `outputs/dark_morphology/results/improved_dark_detection.json`
- `outputs/dark_morphology/results/dark_lane_mask.png`

## Notebooks

The notebooks are tutorial-style drivers:

- `notebooks/01_band_analysis.ipynb`: band geometry + clustering pipeline
- `notebooks/02_dark_morphology.ipynb`: dark-lane morphology pipeline
- `notebooks/03_astronomical_validity.ipynb`: integrated cross-checks using exported `outputs/`

They are intentionally not the “core implementation”; the reusable code lives in `src/amanogawa/`.

## Tests and code quality

Run unit tests:

```bash
pytest
```

Run lint:

```bash
ruff check src tests
```

CI runs lint + tests on push/PR.

## Citation

JOSS paper sources: `paper/paper.md` and `paper/paper.bib`.

If you use this software before a DOI is minted, cite the repository and/or the included paper draft. After Zenodo release, update this section with the DOI.

## Data license (image)

This repository includes a sample smartphone sky image at `data/raw/IMG_5991.jpg`.

- Copyright: © 2025 Shunya Hayashida
- License: CC BY 4.0

See `DATA_LICENSE.md` for details.

## License

Software is released under the MIT License (see `LICENSE`).

## Contributing

See `CONTRIBUTING.md` and `CODE_OF_CONDUCT.md`.

## Contact

Questions/suggestions: [1720067169@campus.ouj.ac.jp](mailto:1720067169@campus.ouj.ac.jp) (Shunya Hayashida)
