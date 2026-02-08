# Scientific Assumptions

This document records the current scientific assumptions used by Amanogawa.
It is the baseline for interpretation, review, and planned calibration work.

## Scope

- Target data: single wide-field smartphone long-exposure images.
- Primary objective: reproducible relative structure measurements, not absolute astrometry.
- Output unit basis: pixels unless external plate scale/WCS is provided.

## Core Assumptions

1. Source detection assumptions
- Candidate stars are approximated as local blob-like maxima in grayscale images.
- Detection uses Laplacian-of-Gaussian response with user-visible thresholds.
- Threshold sweep is used to assess sensitivity to parameter choice.

2. Spatial statistics assumptions
- Two-point correlation uses DD/RR_expected - 1.
- RR_expected is the analytic Poisson expectation for annuli in a rectangular field.
- For large catalogs, reproducible subsampling (fixed RNG seed) is used.

3. Band geometry assumptions
- Milky Way orientation is represented by a principal axis of density moments.
- Width is summarized from profiles perpendicular to this axis.
- Gaussian, Lorentzian, and empirical FWHM are descriptive model summaries.

4. Dark morphology assumptions
- Dark-lane signal is enhanced using inversion + multi-scale background suppression.
- Multi-threshold binary fusion and morphology produce region-level descriptors.
- Fractal descriptors are treated as comparative metrics, not direct physical laws.

## Known Limitations

- No guaranteed radiometric linearity for smartphone-processed imagery.
- Lens distortion and vignetting are not fully corrected by default.
- Atmospheric extinction, haze, and local light gradients can bias counts and widths.
- Cross-device comparability remains limited without calibration profiles.

## Interpretation Guidance

- Use relative comparisons within controlled acquisition settings.
- Prefer trend analysis across repeated captures over single-value conclusions.
- Treat pixel-scale outputs as internal metrics unless calibrated conversion is available.
