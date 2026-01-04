"""Legacy module kept for backward compatibility.

The core implementation lives in :mod:`amanogawa.photometry`.

This module exists so older commands like ``python -m src.photometry`` keep working.
"""

from __future__ import annotations

from amanogawa.photometry import (  # noqa: F401
    PhotometryConfig,
    aperture_photometry,
    assign_magnitude_bins,
    assign_magnitude_bins_from_files,
    main,
)


def assign_magnitude_bins_legacy(image_path: str, coords_csv: str, out_dir: str) -> str:
    """Legacy wrapper matching the old placeholder intent."""

    out_path = assign_magnitude_bins_from_files(image_path, coords_csv, out_dir)
    return str(out_path)
