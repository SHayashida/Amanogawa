<!-- NOTE: Japanese version lives in README_ja.md -->
# Amanogawa

Quantifying Milky Way stellar clustering and dark-lane morphology from a single smartphone exposure.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](#license)
[![CI](https://github.com/SHayashida/Amanogawa/actions/workflows/ci.yml/badge.svg)](https://github.com/SHayashida/Amanogawa/actions/workflows/ci.yml)

[Open in Colab: Band Analysis](https://colab.research.google.com/github/SHayashida/Amanogawa/blob/main/notebooks/01_band_analysis.ipynb)

[Open in Colab: Dark Morphology](https://colab.research.google.com/github/SHayashida/Amanogawa/blob/main/notebooks/02_dark_morphology.ipynb)

English | [日本語 / Japanese](./README_ja.md)

## Statement of need

Wide-field Milky Way images (including consumer smartphone long exposures) contain measurable structure: clustered stellar fields and dust-driven dark lanes. Amanogawa provides a compact, reproducible pipeline that extracts quantitative metrics (clustering statistics, principal-axis/width estimates, and dark-lane morphology) from a single image to support citizen-science workflows and lightweight scientific exploration.

## What is included

- **Core library:** installable Python package under `src/amanogawa/`.
- **CLIs:** entry points for the main steps (`amanogawa-*`).
- **Notebooks:** tutorials under `notebooks/` that exercise the library and reproduce figures.
- **User guide:** `docs/USER_GUIDE.md` - FAQ, troubleshooting, and output metrics explained.
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
apt-get install -y gcc g++ build-essential python3-dev git

# 2. Clone the repository
git clone https://github.com/SHayashida/Amanogawa.git
cd Amanogawa

# 3. Install package with all dependencies
pip install -e .
```

Verify the installation:

```bash
cd /  # Move outside the project directory
python3 -c "import amanogawa; print('Success')"
```

If you see `Success`, the installation was successful and paths are correctly configured.

Run tests to verify functionality:

```bash
cd /Amanogawa
pytest
```

All tests should pass (12 passed). Some deprecation warnings from matplotlib are expected and can be safely ignored.

## Image Acquisition Guide (iPhone 16/17)

Amanogawa is optimized for single 30-second smartphone exposures of the Milky Way. Here is how to capture high-quality images using iPhone 16 or 17:

### 1. Choose a location

- Find a **dark location away from city lights** (mountains, rural areas, etc.)
- **New moon phase preferred** (around new moon to avoid moonlight)
- Check light pollution maps online if available

### 2. Prepare your tripod

- **Mount iPhone securely** on a stable tripod (most critical step—vibration prevents 30-second exposure)
- An inexpensive smartphone tripod is sufficient
- Ensure the mount is completely still before shooting

### 3. Configure your camera app

- Open Camera app and switch to **Photo mode**
- **Turn off Flash** (essential for night sky)
- **Turn off Live Photo** (can interfere with long-exposure stability)

### 4. Compose your shot

- **Point at the Milky Way** (zenith or band orientation)
- You should see a **yellow moon icon** (Night mode) appear automatically in the upper-left corner

### 5. Set exposure to 30 seconds

- Tap the **↓ icon** at the top to reveal the control bar
- Tap the **Night mode icon** (moon symbol)
- Drag the slider all the way to the right to **"Max"** (starts at ~10 seconds)
- If iPhone is completely stable, it will **automatically switch to 30 seconds**

### 6. Capture the image

- Press the **shutter button**
- To avoid vibration, use a **timer** (3-second or 10-second delay) or **Apple Watch remote shutter** if available
- **Do not move the iPhone** for the full 30 seconds—silence notifications, avoid touch
- Wait for the exposure to complete

### 7. Review and post-process (optional)

- Check the photo in the Photos app
- Adjust **brightness/contrast** if desired (Photos app can make minor tweaks)
- For professional results, use Lightroom, Snapseed, or other post-processing tools

### Tips for success

- **Stability is critical**: A wobbly tripod will make 30-second exposure impossible
- **Disable notifications**: Put iPhone in airplane mode 1 minute before shooting
- **Cool sensor**: Let iPhone cool for 5 minutes in cold night air (thermal noise reduction)
- **Steady framing**: Frame shot before starting exposure; avoid adjusting during countdown
- **Clear weather**: Avoid haze; autumn/winter usually offer clearer skies

Once you have your image, load it into the Amanogawa pipeline using the CLI commands in the **Quick start** section below.

## Quick start (CLI)

1. Star detection (writes coordinates CSV + threshold sweep summaries):

```bash
amanogawa-detect --image data/raw/IMG_5991.jpg --out outputs/ \
  --threshold-min 0.03 --threshold-max 0.08 --steps 10
```

To generate a visualization of detected stars, add the `--plot-output` flag:

```bash
amanogawa-detect --image data/raw/IMG_5991.jpg --out outputs/ \
  --threshold 0.05 --plot-output
```

This creates `outputs/star_detection_overlay.png` showing detected stars overlaid on the original image.

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

### Custom visualization with matplotlib

You can create custom plots using the CSV output. Here's a simple example:

```python
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image

# Load detected star coordinates
coords = pd.read_csv("outputs/IMG_5991_star_coords.csv")

# Load original image
img = Image.open("data/raw/IMG_5991.jpg")

# Create visualization
fig, ax = plt.subplots(figsize=(12, 8))
ax.imshow(img)
ax.scatter(coords["x"], coords["y"], s=30, c="red", alpha=0.5, 
           edgecolors="white", linewidths=0.3)
ax.set_title(f"Detected {len(coords)} stars")
plt.savefig("outputs/custom_star_plot.png", dpi=150, bbox_inches="tight")
plt.show()
```

For more advanced analysis and visualization examples, see the notebooks in `notebooks/`.

## Example Output

Below is an example of the star detection visualization generated with the `--plot-output` flag:

![Star Detection Results](outputs/sample_star_detection_overlay.png)

*Figure: Detected stars (red markers) overlaid on a 30-second smartphone exposure of the Milky Way. This sample output demonstrates the detection pipeline's visualization capability.*

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

## Quick Verification (for reviewers)

Clone, install, test, and run in one block:

```bash
git clone https://github.com/SHayashida/Amanogawa.git
cd Amanogawa
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check src tests
amanogawa-detect --image data/raw/IMG_5991.jpg --out outputs/ --threshold 0.05 --plot-output
```

All tests should pass (12 passed), lint should pass, and `outputs/sample_star_detection_overlay.png` will be generated.

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
