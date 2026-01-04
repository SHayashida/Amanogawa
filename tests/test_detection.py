from __future__ import annotations

import numpy as np

from amanogawa.detection import detect_stars_log


def _synthetic_image(height: int = 128, width: int = 128) -> np.ndarray:
    yy, xx = np.mgrid[0:height, 0:width]
    img = np.zeros((height, width), dtype=float)
    # Three bright Gaussian blobs
    for (x0, y0, sigma, amp) in [(32, 40, 2.0, 1.0), (80, 70, 3.0, 0.9), (50, 100, 2.5, 0.8)]:
        img += amp * np.exp(-0.5 * (((xx - x0) / sigma) ** 2 + ((yy - y0) / sigma) ** 2))
    return img


def test_detect_stars_log_finds_blobs() -> None:
    img = _synthetic_image()
    df = detect_stars_log(img, threshold=0.05, max_sigma=6, num_sigma=12)
    # blob_log may find >3 depending on scale-space peaks; require at least 3.
    assert len(df) >= 3
    assert {"x", "y", "r"}.issubset(df.columns)
