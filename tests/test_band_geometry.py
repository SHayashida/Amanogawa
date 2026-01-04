from __future__ import annotations

import math

import numpy as np

from amanogawa.band_geometry import analyze_band_geometry


def _angle_diff_deg(a: float, b: float) -> float:
    """Smallest difference between two angles in degrees (mod 180 for axis)."""
    # PCA axis is bidirectional (theta and theta+180 are equivalent)
    d = abs((a - b) % 180.0)
    return min(d, 180.0 - d)


def test_analyze_band_geometry_recovers_axis_and_width() -> None:
    rng = np.random.default_rng(42)
    width, height = 800, 600

    # Generate a synthetic "band": points along a rotated axis with Gaussian thickness
    true_angle = 30.0
    th = math.radians(true_angle)
    n = 5000
    s = rng.uniform(-300, 300, size=n)
    perp = rng.normal(0, 20, size=n)

    cx, cy = width / 2, height / 2
    x = cx + s * math.cos(th) - perp * math.sin(th)
    y = cy + s * math.sin(th) + perp * math.cos(th)
    points = np.column_stack([x, y])

    # Keep in bounds
    m = (points[:, 0] >= 0) & (points[:, 0] < width) & (points[:, 1] >= 0) & (points[:, 1] < height)
    points = points[m]

    fit = analyze_band_geometry(points, width, height, bins_x=60, nbins_profile=150)
    assert _angle_diff_deg(fit.angle_deg, true_angle) < 20.0
    assert fit.empirical_fwhm_px > 0
