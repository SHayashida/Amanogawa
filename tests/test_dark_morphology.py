import numpy as np

from amanogawa.dark_morphology import DarkMaskConfig, detect_dark_lane_mask


def test_detect_dark_lane_mask_on_synthetic_stripe() -> None:
    rng = np.random.default_rng(0)
    h, w = 256, 256

    # Bright-ish background with mild gradient
    yy, xx = np.mgrid[0:h, 0:w]
    img = 0.7 + 0.15 * (yy / (h - 1))

    # Add a dark horizontal lane
    lane_half = 10
    y0 = h // 2 - lane_half
    y1 = h // 2 + lane_half
    img[y0:y1, :] *= 0.25

    # Add small noise and clip
    img += 0.02 * rng.normal(size=img.shape)
    img = np.clip(img, 0.0, 1.0)

    cfg = DarkMaskConfig(
        background_scales=(10, 30, 60),
        thresholds=(0.12, 0.20, 0.28, 0.36),
        min_seed_distance_px=40,
        min_seed_peak=3.0,
    )

    res = detect_dark_lane_mask(img, config=cfg)

    # Mask should be non-empty and roughly stripe-sized.
    area = float(res.combined_mask.mean())
    assert area > 0.01
    assert area < 0.30

    # Should detect at least one component.
    assert int(res.metrics["num_dark_components"]) >= 1

    # Fractal dimensions should be present (finite) for non-empty masks.
    assert res.metrics["fractal_dimension_dark_mask"] is not None
    assert res.metrics["fractal_dimension_skeleton"] is not None
