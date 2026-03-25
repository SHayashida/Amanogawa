# Minimum Scientific Data Spec (Visibility v1)

This document defines the minimum data contract for Amanogawa's first
citizen-science visibility workflow.

## Intended claim

Visibility v1 reports **image-based relative visibility / analyzability**.
It does **not** estimate absolute light pollution or true sky quality on its own.

Low scores can reflect:

- device limitations,
- aggressive camera-app processing,
- motion blur,
- haze or clouds,
- poor framing/exposure,
- bright sky background.

They should not be interpreted as a direct claim that the site itself has a poor sky.

## Required input

- One original or near-original sky image file.
- Image dimensions.
- Stored EXIF metadata when available.
- Pipeline outputs required for reproducibility:
  - `detection_summary.json`
  - `star_coords.csv`

## Minimum metadata snapshot

The visibility step preserves a device snapshot for later calibration-aware analysis:

- `device_model`
- `device_make`
- `software`
- `datetime_original`
- `exif_available`
- `edited_flag`

These fields are descriptive only in v1. They are not used to adjust the score.

## Output contract

Visibility v1 produces:

- `visibility_features.json`
  - raw features
  - threshold-sweep summaries
  - device metadata snapshot
  - score version
- `visibility_score.json`
  - branch scores
  - total score
  - grade
  - `qc_status`
  - `research_usable`
  - interpretation notes

## Minimal semantics

- `visibility_score`: observation-based score for what the submitted image shows.
- `qc_status`: pass/warn/fail gate for scientific reuse.
- `research_usable`: `true` only when `qc_status == "pass"`.

## Explicit non-claims

Visibility v1 does not claim:

- device-adjusted comparability,
- absolute sky brightness,
- absolute light pollution level,
- calibrated photometry,
- cross-device fairness.

## Future extension

Later versions may add:

- device-family calibration,
- external skyglow / moon / weather joins,
- WCS-based expected-star completeness metrics,
- a separate device-adjusted score.
