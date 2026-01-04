from __future__ import annotations

import numpy as np

from amanogawa.spatial_stats import (
    boxcount_fractal_dimension,
    nearest_neighbor_distances,
    two_point_correlation_function,
)


def test_nearest_neighbor_distances_shape() -> None:
    points = np.array([[0.0, 0.0], [3.0, 4.0], [10.0, 10.0]])
    d = nearest_neighbor_distances(points)
    assert d.shape == (3,)
    assert np.all(np.isfinite(d))


def test_boxcount_fractal_dimension_reasonable_ranges() -> None:
    rng = np.random.default_rng(0)

    # Points on a line -> D ~ 1
    t = np.linspace(0, 1, 500)
    line = np.column_stack([t, t]) * 1000
    D_line, _, _ = boxcount_fractal_dimension(line, 1000, 1000, steps=12)
    assert 0.7 < D_line < 1.3

    # Uniform random in 2D -> D tends toward 2, but finite samples can bias low
    pts = rng.random((5000, 2)) * 1000
    D_rand, _, _ = boxcount_fractal_dimension(pts, 1000, 1000, steps=12)
    assert 1.2 < D_rand < 2.2


def test_two_point_correlation_runs() -> None:
    rng = np.random.default_rng(1)
    pts = rng.random((2000, 2))
    pts[:, 0] *= 500
    pts[:, 1] *= 300
    r_bins = np.linspace(2, 80, 20)
    rc, xi = two_point_correlation_function(pts, 500, 300, r_bins, max_points=1500, rng=rng)
    assert rc.shape == (len(r_bins) - 1,)
    assert xi.shape == (len(r_bins) - 1,)
    assert np.all(np.isfinite(xi))
