# Calibration Protocol (P1 Baseline)

This protocol defines the minimum calibration workflow for Amanogawa.
It aligns with the initial calibration module classes:

- `CalibrationProfile`
- `DarkFrameSubtractor`
- `FlatFieldCorrector`
- `VignettingCorrector`

## Goals

- Reduce device- and capture-dependent bias.
- Improve reproducibility across iPhone models and sessions.
- Keep implementation lightweight enough for iterative field use.

## Required Assets

1. Dark frame set
- Capture with lens covered, matching ISO/exposure mode when feasible.
- Acquire multiple frames and combine (median) to suppress random noise.

2. Flat-field set
- Capture uniform illumination frames (dawn sky / calibrated panel).
- Exclude frames with saturation or strong gradients.
- Build master flat and normalize by robust central tendency (median).

3. Vignetting profile
- Either:
  - empirical gain map from flat-field residuals, or
  - parametric radial model (strength, center, power).

## Application Order

Apply corrections in this order:

1. Dark-frame subtraction
2. Flat-field correction
3. Vignetting correction

Rationale: additive offsets are removed first; multiplicative response corrections follow.

## Profile Structure

At minimum, a profile should define:

- `device_model`
- optional `dark_frame`
- optional `flat_field`
- optional `vignette_gain_map`
- optional parametric vignetting fields (`vignette_strength`, `vignette_center_xy`, `vignette_power`)

## Quality Checks

Before accepting a profile:

- Shape consistency: all maps must match image dimensions.
- Flat-field positivity: no non-positive global normalization.
- Residual gradients: compare radial medians pre/post correction.
- Noise impact: confirm no systematic amplification in dark backgrounds.

## Versioning

- Track profile creation date, acquisition conditions, and software version.
- Store immutable profile snapshots for reproducible reprocessing.
- Recompute profile if camera pipeline or capture settings significantly change.
