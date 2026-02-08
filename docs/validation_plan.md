# Validation Plan

This validation plan defines acceptance gates for Amanogawa pipeline changes.

## Validation Targets

1. Numerical stability
- No crash on empty or sparse inputs.
- Deterministic outputs under fixed seeds.

2. Scientific consistency
- 2PCF behavior remains consistent with estimator definition.
- Band axis/width estimates stay within expected synthetic-data tolerance.
- Dark morphology metrics remain finite and interpretable on baseline inputs.

3. I/O conformance
- Output JSON schemas remain backward-compatible or explicitly versioned.
- FITS export header mapping remains stable for key summary fields.

## Test Layers

1. Unit tests
- Core numerical functions (stats, geometry, calibration transforms).
- FITS header mapping with known metadata.

2. CLI smoke/integration tests
- Single-image and directory workflows.
- Resume-mode behavior in `amanogawa-run`.

3. Dataset regression checks
- Re-run reference image(s) and compare key metrics with tolerance bounds.

## Proposed Acceptance Gates

- All tests pass in CI.
- Lint passes with no new violations.
- For reference dataset:
  - star count delta within predefined threshold band,
  - 2PCF mean sign/trend unchanged unless intentionally modified,
  - band angle and empirical width within tolerance windows.

## Change Control

- Any scientific-method change must include:
  - method note in docs,
  - updated tests,
  - explicit migration note if output semantics changed.
