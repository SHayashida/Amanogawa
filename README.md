<!-- NOTE: Japanese version has been moved to README_ja.md -->
# Amanogawa: Quantifying Milky Way Stellar Clustering & Dark Lane Morphology from a Single Smartphone Exposure

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](#license)
[![Reproducibility](https://img.shields.io/badge/Reproducible-Yes-blue.svg)](#reproducibility-workflow)
[![Status](https://img.shields.io/badge/Status-Alpha-orange.svg)]()
[![Colab: Dark Analysis](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SHayashida/Amanogawa/blob/main/notebooks/Amanogawa_dark.ipynb)
[![Colab: Band Geometry](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/SHayashida/Amanogawa/blob/main/notebooks/Amanogawa_band.ipynb)

<!-- If the repository is private the Colab links above will fail. Make the repo public or adjust branch/path if renamed. -->

English | [日本語 / Japanese](./README_ja.md)

## Overview
This repository demonstrates how a *single consumer smartphone long‑exposure* Milky Way image can yield:

1. Stellar spatial clustering metrics (two‑point correlation function \(\xi(r)\), nearest‑neighbour distribution, box‑count / fractal dimension \(D\)).
2. Milky Way band & dark lane (dust lane) morphology: principal axis, multi‑model width (Gaussian & Lorentzian), and a normalized intensity deficit (NID) tracing absorption contrast.

The scientific motivation is to lower the barrier for quantitative Galactic structure exploration to a citizen‑science friendly data source while still preserving methodological rigor.

> Hayashida, S. (2025). *Quantifying Clustering and Dark Lane / Band Morphology of the Milky Way from a Single Smartphone Exposure.* (In preparation)

### Dual Perspective from One Image
| Aspect | Derived Metrics | Scientific Signal |
|--------|-----------------|-------------------|
| Stellar Clustering | \(\xi(r)\), NND PDF, fractal dimension \(D\) | Hierarchical structure, dissolved cluster remnants |
| Band Geometry | Principal axis angle, FWHM (Gaussian / Lorentzian) | Projected width vs atmospheric / optical smoothing |
| Dark Lane Contrast | Normalized intensity deficit profile | Relative dust column variation (qualitative) |
| Magnitude-Stratified Clustering | Bright / mid / faint tercile \(\xi(r)\) + bootstrap CI | Scale dependence with luminosity selection |

The dark lane module operates in the same transformed PCA coordinate frame as clustering, enabling cross‑scale comparison between extinction structure and stellar correlation features.

## Key Features
- Single-image end‑to‑end pipeline (no stacking required)
- Colab‑first reproducibility; zero local install required to explore
- Threshold sweep robustness diagnostics for detection biases
- Magnitude‑stratified clustering with bootstrap confidence intervals
- Dual profile (Gaussian + Lorentzian) band width estimation (core vs wings)
- Dark lane normalized intensity deficit (NID) metric in shared geometry frame
- Modular architecture: swap detection, correlation estimators (e.g., Landy–Szalay)
- Ready for citizen‑science workshops / teaching demonstrations

## Repository Structure
```
├── notebooks/                        # Colab / Jupyter ノートブック（後日追加）
│   ├── Amanogawa_band.ipynb          # バンド & 暗黒帯解析（既存）
│   └── Amanogawa_dark.ipynb          # クラスタリング + 暗黒帯統合（既存）
├── src/
│   ├── detection.py              # LoG detection / threshold sweep
│   ├── spatial_stats.py          # two-point correlation, box-count, NND
│   ├── band_geometry.py          # PCA axis + width fitting + dark lane contrast
│   ├── photometry.py             # simple aperture photometry & magnitude bins
│   └── plotting.py               # figure generation utilities
├── data/
│   ├── raw/IMG_5991.jpg          # smartphone sky image (if license permits)
│   ├── raw/IMG_5991_wcs.fits     # (truncated) WCS solution (optional)
│   ├── interim/                  # intermediate serialized objects
│   └── processed/                # final derived CSV / JSON outputs
├── outputs/
│   ├── figures/TaskA.png
│   ├── figures/TaskB.png
│   ├── figures/Two_point_correlation.png
│   ├── figures/Box_count_scaling.png
│   ├── figures/NND.png
│   ├── IMG_5991_star_coords.csv
│   ├── threshold_sweep_summary.csv
│   └── band_width_fit_summary.json
├── paper.md                      # Manuscript (source)
├── references.bib                # Bibliography
├── CITATION.cff                  # Citation metadata
├── requirements.txt (or environment.yml)
└── README.md
```
Missing items are staged for addition; notebooks assume this layout.

## Quick Start
### A. Google Colab (fastest)
1. Open `notebooks/Amanogawa_dark.ipynb` in Colab.
2. Upload your Milky Way image to `data/raw/` in the Colab session.
3. Run cells top‑to‑bottom (detection → threshold sweep → clustering → band & dark lane morphology).
4. Artifacts appear under `outputs/` (CSV / JSON / PNG).

### B. Local Execution
1. Clone repo.
2. Create virtual environment & install dependencies.
3. Place image in `data/raw/`.
4. Detection + threshold sweep:
   ```bash
   python -m src.detection --image data/raw/IMG_5991.jpg --out outputs/ \
       --threshold-min 0.03 --threshold-max 0.08 --steps 10
   ```
5. Spatial statistics:
   ```bash
   python -m src.spatial_stats --coords outputs/IMG_5991_star_coords.csv --out outputs/
   ```
6. Magnitude‑stratified clustering:
   ```bash
   python -m src.photometry --image data/raw/IMG_5991.jpg \
       --coords outputs/IMG_5991_star_coords.csv --out outputs/
   python -m src.spatial_stats --coords outputs/IMG_5991_star_coords.csv \
       --magnitude-bins outputs/magnitude_bins.csv --out outputs/
   ```
7. Band geometry + dark lane contrast:
   ```bash
   python -m src.band_geometry --coords outputs/IMG_5991_star_coords.csv \
       --wcs data/raw/IMG_5991_wcs.fits --out outputs/
   ```
8. Figures:
   ```bash
   python -m src.plotting --out outputs/figures/
   ```

## Dependencies
Recommended baseline (pin exact versions for reproducibility when finalizing Zenodo DOI):
```
python >= 3.10
numpy
scipy
scikit-image
pandas
matplotlib
astropy
scikit-learn   # (optional for PCA; otherwise use numpy.linalg)
photutils      # (optional: more robust photometry)
pyyaml         # (config handling, optional)
```
Create `requirements.txt` (example):
```
numpy==1.26.4
scipy==1.13.1
scikit-image==0.24.0
pandas==2.2.2
matplotlib==3.9.0
astropy==6.1.0
scikit-learn==1.5.1
photutils==1.11.0
pyyaml==6.0.1
```
Install:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Reproducibility Workflow
1. Detection & threshold sweep → `IMG_5991_star_coords.csv`, `threshold_sweep_summary.csv`
2. Spatial stats → correlation, NND, fractal dimension
3. Magnitude binning & bootstrap clustering
4. Band axis & width (Gaussian / Lorentzian) + dark lane normalized intensity deficit profile
5. Plot + aggregate → figures & summary JSON
6. (Optional) provenance export: `outputs/run_metadata.yaml`

## Method Notes
- Detection: Laplacian‑of‑Gaussian + threshold sweep to locate stability plateau (avoid under/over detection bias)
- Two‑point correlation: baseline \(DD/RR - 1\); future: Landy–Szalay with edge correction
- Fractal dimension: log–log box count regression slope
- Dark lane: extract perpendicular strips in PCA frame → robust (median) background → normalized intensity deficit ( (background − signal)/background )
- Band width: fit Gaussian + Lorentzian to separate core concentration vs broader scattered wings
- Angular calibration: approximate WCS (astrometry.net) — treat angles as provisional

## Outputs & Files
| File | Description |
|------|-------------|
| `IMG_5991_star_coords.csv` | Detected star positions (x, y, radius) |
| `threshold_sweep_summary.csv` | Threshold, count, fractal D, mean ξ, stability flag |
| `band_width_fit_summary.json` | Axis angle, Gaussian/Lorentzian FWHM (px/deg), dark lane contrast metrics |
| `TaskA.png` | Threshold sweep diagnostics |
| `TaskB.png` | Magnitude‑stratified \(\xi(r)\) |
| `Two_point_correlation.png` | Full‑sample \(\xi(r)\) |
| `Box_count_scaling.png` | Fractal dimension regression |
| `NND.png` | Nearest‑neighbour distance distribution |
| `Dark_lane_profile.png` | Normalized intensity deficit profile |

## Quality & Validation
- Internal assertions (recommended):
  - Star coordinate array non-empty and within image bounds.
  - Monotonic decrease of detection counts with threshold.
  - Positive mean ξ across thresholds (warn if not).
  - PCA axis reproducibility under bootstrap (angle dispersion < chosen tolerance).
- Add lightweight unit tests under `tests/` (e.g., pytest) for math utilities.

## Extending
- Replace LoG with PSF fitting (DAOStarFinder) for faint star completeness
- Landy–Szalay / Ripley K for bias reduction & variance diagnostics
- Cross‑correlate dark lane contrast vs clustering scale
- Multi‑epoch / varying light‑pollution comparative meta‑analysis

## FAQ
**Q:** Do I need WCS?  
**A:** Only for angular conversions; pixel‑space analysis works without it.

**Q:** Light pollution impact on dark lane metrics?  
**A:** Robust background estimation mitigates moderate gradients; extreme skyglow still reduces S/N.

**Q:** Use another smartphone image?  
**A:** Yes—drop it in `data/raw/`, re‑tune detection thresholds if optics / exposure differ.

## Contributing
Pull requests are welcome. Please:
1. Open an issue describing proposed changes.
2. Adhere to existing code style (PEP8; run `ruff` or `flake8` if configured).
3. Include tests for new analytic functions.
4. Update README / docs if behavior changes.

## Citation
Update DOI after Zenodo release.

Plain text:
Hayashida, S. (2025). Quantifying clustering and dark lane / band morphology of the Milky Way from a single smartphone exposure. Zenodo. https://doi.org/10.5281/zenodo.xxxxxxx

BibTeX:
```bibtex
@misc{hayashida2025amanogawa,
   author       = {Hayashida, Shunya},
   title        = {Quantifying Clustering and Dark Lane / Band Morphology of the Milky Way from a Single Smartphone Exposure},
   year         = {2025},
   publisher    = {Zenodo},
   doi          = {10.5281/zenodo.xxxxxxx},
   url          = {https://doi.org/10.5281/zenodo.xxxxxxx},
   note         = {Amanogawa v1.0.0}
}
```

## License
Code: MIT License (see below).  
Data & manuscript text: CC BY 4.0 (recommended; ensure compatibility before release).

```
MIT License

Copyright (c) 2025 Shunya Hayashida

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Zenodo Deposition Checklist
1. Push all final code & data to a tagged GitHub release (e.g., `v1.0.0`).
2. Enable GitHub–Zenodo integration (first time only) and re‑create the release to trigger DOI.
3. Update the DOI badge and BibTeX entry here with the minted DOI.
4. Upload any large files (>100 MB) directly in Zenodo if they cannot be committed.
5. Freeze `requirements.txt` with exact versions (use `pip freeze > requirements.txt`).
6. (Optional) Add an `environment.yml` (Conda) or `uv.lock`/`poetry.lock` for fully pinned reproducibility.

## Contact
Questions / suggestions: 1720067169@campus.ouj.ac.jp (Shunya Hayashida)

---
*Prepared for transparent citizen‑science reproducibility and archival on Zenodo.*
