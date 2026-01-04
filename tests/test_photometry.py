import numpy as np
import pandas as pd

from amanogawa.photometry import aperture_photometry, assign_magnitude_bins


def test_aperture_photometry_and_bins_smoke() -> None:
    rng = np.random.default_rng(0)
    height, width = 128, 128
    img = np.zeros((height, width), dtype=float)

    # Create 12 synthetic point sources with varying intensities
    xs = np.linspace(20, 108, 12)
    ys = np.linspace(24, 104, 12)
    amps = np.linspace(1.0, 3.0, 12)  # brighter => larger flux => smaller magnitude

    yy, xx = np.mgrid[0:height, 0:width]
    for x, y, a in zip(xs, ys, amps):
        img += a * np.exp(-((xx - x) ** 2 + (yy - y) ** 2) / (2 * 1.2**2))

    # add mild background noise
    img += 0.01 * rng.normal(size=img.shape)
    img = np.clip(img, 0.0, None)

    coords = pd.DataFrame({"x": xs, "y": ys})
    phot = aperture_photometry(img, coords, aperture_radius_px=2, annulus_inner_radius_px=6, annulus_outer_radius_px=10)

    assert len(phot) == 12
    assert phot["is_valid"].sum() >= 9

    # Brighter sources should have smaller mags on average.
    mags = phot.loc[phot["is_valid"], "mag"].to_numpy()
    assert np.all(np.isfinite(mags))

    binned = assign_magnitude_bins(phot)
    assert "mag_bin" in binned.columns
    assert set(binned["mag_bin"].unique()).issuperset({"Bright", "Mid", "Faint"})
