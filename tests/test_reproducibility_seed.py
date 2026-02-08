from __future__ import annotations

import numpy as np
import pandas as pd

from amanogawa.photometry import aperture_photometry
from amanogawa.spatial_stats import two_point_correlation_function


def test_two_point_correlation_is_reproducible_with_fixed_seed() -> None:
    rng_data = np.random.default_rng(0)
    points = rng_data.random((3000, 2))
    points[:, 0] *= 640.0
    points[:, 1] *= 480.0
    r_bins = np.linspace(3.0, 90.0, 20)

    rc1, xi1 = two_point_correlation_function(
        points,
        640,
        480,
        r_bins,
        max_points=500,
        rng=np.random.default_rng(123),
    )
    rc2, xi2 = two_point_correlation_function(
        points,
        640,
        480,
        r_bins,
        max_points=500,
        rng=np.random.default_rng(123),
    )

    assert np.allclose(rc1, rc2)
    assert np.allclose(xi1, xi2)


def test_aperture_photometry_subsampling_is_reproducible_with_seed() -> None:
    h, w = 120, 160
    yy, xx = np.mgrid[0:h, 0:w]
    image = np.exp(-((xx - 80) ** 2 + (yy - 60) ** 2) / (2.0 * 30.0**2))

    rng = np.random.default_rng(42)
    n = 1200
    coords = pd.DataFrame(
        {
            "x": rng.uniform(15.0, w - 15.0, size=n),
            "y": rng.uniform(15.0, h - 15.0, size=n),
        }
    )

    out1 = aperture_photometry(
        image,
        coords,
        max_points=200,
        rng=np.random.default_rng(999),
    )
    out2 = aperture_photometry(
        image,
        coords,
        max_points=200,
        rng=np.random.default_rng(999),
    )

    assert out1["source_index"].tolist() == out2["source_index"].tolist()
    assert np.allclose(out1["flux"].to_numpy(), out2["flux"].to_numpy(), equal_nan=True)
    assert np.allclose(out1["mag"].to_numpy(), out2["mag"].to_numpy(), equal_nan=True)
