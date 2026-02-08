from __future__ import annotations

import numpy as np
import pandas as pd

from amanogawa.band_geometry import analyze_band_geometry
from amanogawa.dark_morphology import detect_dark_lane_mask
from amanogawa.detection import detect_stars_log
from amanogawa.photometry import aperture_photometry
from amanogawa.spatial_stats import boxcount_fractal_dimension, nearest_neighbor_distances


def test_detect_stars_log_empty_image_returns_empty_catalog() -> None:
    image = np.zeros((64, 64), dtype=float)
    df = detect_stars_log(image, threshold=0.2)
    assert len(df) == 0
    assert {"x", "y", "r"}.issubset(df.columns)


def test_spatial_stats_helpers_accept_empty_points() -> None:
    points = np.empty((0, 2), dtype=float)
    nnd = nearest_neighbor_distances(points)
    assert nnd.size == 0

    d, eps, counts = boxcount_fractal_dimension(points, 100, 100, steps=8)
    assert np.isnan(d)
    assert len(eps) == 8
    assert np.all(counts == 0)


def test_band_geometry_empty_points_returns_no_detection_fit() -> None:
    points = np.empty((0, 2), dtype=float)
    fit = analyze_band_geometry(points, 200, 150)
    assert np.isnan(fit.angle_deg)
    assert fit.gaussian_fwhm_px is None
    assert fit.lorentzian_fwhm_px is None
    assert np.isnan(fit.empirical_fwhm_px)
    assert fit.y_centers == []


def test_aperture_photometry_empty_coords_returns_empty_dataframe() -> None:
    image = np.ones((40, 40), dtype=float)
    coords = pd.DataFrame(columns=["x", "y"])
    out = aperture_photometry(image, coords)
    assert len(out) == 0
    assert {"x", "y", "flux", "mag", "is_valid"}.issubset(out.columns)


def test_dark_morphology_handles_uniform_input() -> None:
    image = np.ones((96, 96), dtype=float)
    res = detect_dark_lane_mask(image)
    assert "dark_area_fraction" in res.metrics
    assert "num_dark_components" in res.metrics
