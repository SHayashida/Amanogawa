# Quantifying Clustering and Milky Way Band Morphology from a Single Smartphone Exposure

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](#license)  

## Overview
This repository contains the open, reproducible workflow accompanying the manuscript:

> Hayashida, S. (2025). *Quantifying Clustering and Band Morphology of the Milky Way from a Single Smartphone Exposure.* (In preparation for Zenodo / journal submission.)

Using a single long‐exposure consumer smartphone image, the pipeline derives:
1. Two‑point correlation function \(\xi(r)\) of detected stars.
2. Box‑count (fractal) dimension \(D\) of the spatial distribution.
3. Principal axis and perpendicular full width at half maximum (FWHM) of the Milky Way band via weighted PCA and profile fitting.
4. Magnitude‑stratified clustering analysis (Bright / Mid / Faint terciles).

The goal is to demonstrate that a citizen‐science friendly, low‑barrier dataset can yield astrophysically meaningful clustering and structural measurements.

## Key Features
- End‑to‑end reproducible pipeline (Colab + local scripts).
- Robustness checks via detection threshold sweep.
- Bootstrap confidence intervals for magnitude‑stratified \(\xi(r)\).
- Dual profile (Gaussian & Lorentzian) Milky Way band width estimates.
- All intermediate data (CSV / JSON) and figures prepared for Zenodo archival.
- Modular design to swap in alternative detection or correlation estimators (e.g. Landy–Szalay).

## Repository Structure (intended)
```
├── notebooks/
│   ├── 01_detection_and_threshold_sweep.ipynb
│   ├── 02_two_point_and_fractal.ipynb
│   ├── 03_magnitude_stratified_clustering.ipynb
│   ├── 04_band_axis_and_width.ipynb
│   └── 99_utility_functions.ipynb
├── src/
│   ├── detection.py              # LoG detection / threshold sweep
│   ├── spatial_stats.py          # two-point correlation, box-count, NND
│   ├── band_geometry.py          # PCA axis + width fitting
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
(If some files are not yet present, treat this as a target layout. Adjust paths in notebooks accordingly.)

## Quick Start
### Option A: Google Colab (fastest)
1. Open the notebook `notebooks/01_detection_and_threshold_sweep.ipynb` in Colab (use the "Open in Colab" badge if added later).
2. Upload (or mount) `IMG_5991.jpg` (and WCS FITS if available) into the Colab session under `data/raw/`.
3. Run all cells sequentially; generated CSV/JSON and figures will appear in `outputs/`.
4. Proceed with `02_`, `03_`, and `04_` notebooks for full analysis.

### Option B: Local Environment
1. Clone the repository.
2. Create a virtual environment and install dependencies (see below).
3. Place `IMG_5991.jpg` into `data/raw/`.
4. Run the detection threshold sweep script:
   ```bash
   python -m src.detection --image data/raw/IMG_5991.jpg --out outputs/ --threshold-min 0.03 --threshold-max 0.08 --steps 10
   ```
5. Compute spatial statistics:
   ```bash
   python -m src.spatial_stats --coords outputs/IMG_5991_star_coords.csv --out outputs/
   ```
6. Magnitude stratified clustering:
   ```bash
   python -m src.photometry --image data/raw/IMG_5991.jpg --coords outputs/IMG_5991_star_coords.csv --out outputs/
   python -m src.spatial_stats --coords outputs/IMG_5991_star_coords.csv --magnitude-bins outputs/magnitude_bins.csv --out outputs/
   ```
7. Band geometry:
   ```bash
   python -m src.band_geometry --coords outputs/IMG_5991_star_coords.csv --wcs data/raw/IMG_5991_wcs.fits --out outputs/
   ```
8. Generate publication figures:
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
1. Detection threshold sweep produces: `IMG_5991_star_coords.csv` (fiducial) and `threshold_sweep_summary.csv`.
2. Spatial statistics script computes: two-point correlation (binned), nearest-neighbor distribution, box-count scaling (stores slope / D).
3. Photometry assigns magnitude terciles; re-run correlation for each bin with bootstrap resampling.
4. Band geometry script: weighted PCA axis + perpendicular profile fits (Gaussian & Lorentzian) -> `band_width_fit_summary.json`.
5. Plotting consolidates outputs into figure PNGs matching manuscript captions.
6. (Optional) Export provenance metadata (software versions, command arguments) into `outputs/run_metadata.yaml`.

## Method Notes
- Detection: Laplacian-of-Gaussian blob detection; threshold sweep ensures stability of \(\xi(r)\) and \(D\).
- Two-point correlation: simple \(DD/RR - 1\); for publication-level refinement add Landy–Szalay with DR and edge corrections.
- Fractal dimension: linear fit in log–log occupancy vs inverse box size.
- Band width: rotate into PCA frame; integrate counts perpendicular to the ridge; fit both Gaussian & Lorentzian to capture core vs wings.
- Plate scale: derived from an astrometry.net WCS flagged as truncated; angle estimates are approximate.

## Outputs & Files
| File | Description |
|------|-------------|
| `IMG_5991_star_coords.csv` | Detected star positions (x, y, radius) at fiducial threshold. |
| `threshold_sweep_summary.csv` | Rows of threshold, N, D, mean ξ. |
| `band_width_fit_summary.json` | Principal axis angle, Gaussian/Lorentzian FWHM (px & degrees). |
| `TaskA.png` | Threshold sweep diagnostics. |
| `TaskB.png` | Magnitude-stratified ξ(r). |
| `Two_point_correlation.png` | Full-sample ξ(r) curve. |
| `Box_count_scaling.png` | Fractal dimension regression plot. |
| `NND.png` | Nearest-neighbor distance distribution. |

## Quality & Validation
- Internal assertions (recommended):
  - Star coordinate array non-empty and within image bounds.
  - Monotonic decrease of detection counts with threshold.
  - Positive mean ξ across thresholds (warn if not).
  - PCA axis reproducibility under bootstrap (angle dispersion < chosen tolerance).
- Add lightweight unit tests under `tests/` (e.g., pytest) for math utilities.

## Extending
- Replace LoG with PSF-fitting (e.g., DAOStarFinder / photutils) to improve faint source fidelity.
- Implement Landy–Szalay estimator and compare variance reduction.
- Integrate multi-epoch images to study temporal band width variability vs environmental conditions.

## FAQ
**Q:** Do I need the WCS file?  
**A:** Only if you want angular (degree) conversions; pixel-space results work without it.

**Q:** Why are angle estimates labeled approximate?  
**A:** The FITS plate solution file was flagged truncated; treat scale/rotation as provisional.

**Q:** Can I use another smartphone image?  
**A:** Yes—place it in `data/raw/` and adjust script arguments; thresholds may need tuning.

## Contributing
Pull requests are welcome. Please:
1. Open an issue describing proposed changes.
2. Adhere to existing code style (PEP8; run `ruff` or `flake8` if configured).
3. Include tests for new analytic functions.
4. Update README / docs if behavior changes.

## Citation
If you use this code or derived data, please cite the manuscript and the Zenodo archive (replace DOI after publication):

**Plain text:**  
Hayashida, S. (2025). Quantifying clustering and band morphology of the Milky Way from a single smartphone exposure. Zenodo. https://doi.org/10.5281/zenodo.xxxxxxx

**BibTeX:**
```bibtex
@misc{hayashida2025smartphone_milky_way,
  author       = {Hayashida, Shunya},
  title        = {Quantifying Clustering and Band Morphology of the Milky Way from a Single Smartphone Exposure},
  year         = {2025},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.xxxxxxx},
  url          = {https://doi.org/10.5281/zenodo.xxxxxxx},
  note         = {Version 1.0.0}
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
