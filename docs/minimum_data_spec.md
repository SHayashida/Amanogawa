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

## Accepted input scope

Visibility v1 accepts one still image that can be read by the current image I/O layer.

Supported directly:

- `jpg`
- `jpeg`
- `png`
- `tif`
- `tiff`

Supported with optional HEIF support installed:

- `heif`
- `heic`
- `hif`

PNG is acceptable for v1 **if it preserves the content of one capture**.
In other words, a PNG exported from a single original image can still support the
minimum v1 analysis contract.

The following are out of scope for the current contract:

- stacked composites,
- mosaics,
- screenshots,
- annotated images,
- social-media recompressions with unknown processing history,
- images that combine multiple exposures into one file.

## Resolution and quality floor

Visibility v1 does **not** impose a hard-coded minimum resolution threshold.

Instead, the quality floor is operational:

- preserve original resolution whenever possible,
- avoid aggressive downsampling before analysis,
- keep the image close to the original single-capture content,
- let `visibility_score`, `qc_status`, and `research_usable` reflect whether the
  image contains enough usable evidence.

This means a lower-resolution PNG can still be processed, but if it no longer
retains enough stars, band contrast, or dark-lane structure, Amanogawa should
return a lower score or fail the QC gate rather than infer missing information.

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
