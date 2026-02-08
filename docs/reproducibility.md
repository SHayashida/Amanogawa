# Reproducibility Guide

This guide describes how to reproduce Amanogawa outputs consistently.

## Environment

- Use a pinned Python range: 3.10-3.12.
- Install with project dependencies from `pyproject.toml`.
- Record package version and commit hash for each analysis run.

## Deterministic Controls

1. Spatial statistics
- Set `--seed` and `--max-points` in `amanogawa-stats`.
- Keep image dimensions fixed when re-running.

2. Photometry
- Set `--seed` and `--max-points` in `amanogawa-photometry` when subsampling is active.

3. Orchestrated runs
- Use `amanogawa-run` and archive `run_manifest.json`.
- Re-run with the same CLI parameters and same input files.

## Artifact Preservation

For each run, preserve:

- input image checksum(s),
- `detection_summary.json`,
- `spatial_statistics_analysis.json`,
- `band_geometry_analysis.json`,
- `improved_dark_detection.json`,
- `run_manifest.json`,
- optional FITS export.

## Practical Workflow

1. Run full batch
```bash
amanogawa-run --image-dir data/raw --out outputs/run --recursive
```

2. Export summary FITS (optional)
```bash
amanogawa-fits-export \
  --coords outputs/run/IMG_5991_jpg/detection/star_coords.csv \
  --detection-json outputs/run/IMG_5991_jpg/detection/detection_summary.json \
  --stats-json outputs/run/IMG_5991_jpg/spatial_stats/spatial_statistics_analysis.json \
  --band-json outputs/run/IMG_5991_jpg/band_geometry/band_geometry_analysis.json \
  --dark-json outputs/run/IMG_5991_jpg/dark_morphology/improved_dark_detection.json \
  --out outputs/run/IMG_5991_jpg/amanogawa_summary.fits
```

3. Compare with previous run
- Verify identical seeds and parameters.
- Diff JSON artifacts and check key metrics.

## Known Sources of Non-Reproducibility

- Input image preprocessing outside this repository.
- Floating-point/library differences across platforms.
- Hidden camera-app processing differences across iOS/device generations.
