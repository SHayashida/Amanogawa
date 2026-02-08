from __future__ import annotations

import json

import numpy as np
import pandas as pd
from astropy.io import fits

from amanogawa.fits_export import export_analysis_to_fits, map_analysis_to_header


def test_map_analysis_to_header_sets_expected_cards() -> None:
    header = fits.Header()
    detection = {
        "status": "ok",
        "width_px": 3024,
        "height_px": 4032,
        "num_stars": 1234,
        "detection": {"threshold": 0.05, "max_sigma": 6.0, "num_sigma": 12},
    }
    spatial = {
        "status": "ok",
        "fractal_dimension": 1.42,
        "nearest_neighbor": {"mean": 6.2, "median": 5.7, "std": 2.1},
        "two_point_correlation": {"xi_mean": 0.41, "xi_max": 1.03},
    }
    band = {
        "status": "ok",
        "principal_axis": {"angle_deg": 32.5, "axis_ratio": 0.45},
        "band_width_measurements": {
            "gaussian_fwhm_px": 180.0,
            "lorentzian_fwhm_px": 190.0,
            "empirical_fwhm_px": 175.0,
        },
    }
    dark = {
        "dark_area_fraction": 0.22,
        "num_dark_components": 8,
        "mean_eccentricity": 0.71,
        "mean_elongation": 2.4,
        "fractal_dimension_dark_mask": 1.35,
        "fractal_dimension_skeleton": 1.21,
    }

    out = map_analysis_to_header(
        header,
        detection=detection,
        spatial_stats=spatial,
        band_geometry=band,
        dark_morphology=dark,
        image_path="data/raw/IMG_5991.jpg",
    )

    assert out["ORIGIN"] == "Amanogawa"
    assert out["AMNIMG"] == "data/raw/IMG_5991.jpg"
    assert out["NSTAR"] == 1234
    assert np.isclose(out["DTHRESH"], 0.05)
    assert np.isclose(out["XIMEAN"], 0.41)
    assert np.isclose(out["BANGDEG"], 32.5)
    assert np.isclose(out["DKFRAC"], 0.22)


def test_export_analysis_to_fits_writes_header_and_star_table(tmp_path) -> None:
    coords = pd.DataFrame({"x": [10.5, 20.0], "y": [11.0, 33.5], "r": [2.2, 3.1]})
    coords_path = tmp_path / "star_coords.csv"
    coords.to_csv(coords_path, index=False)

    detection_path = tmp_path / "detection_summary.json"
    detection_path.write_text(
        json.dumps(
            {
                "status": "ok",
                "width_px": 100,
                "height_px": 80,
                "num_stars": 2,
                "detection": {"threshold": 0.07, "max_sigma": 5.0, "num_sigma": 10},
            }
        ),
        encoding="utf-8",
    )

    stats_path = tmp_path / "spatial_statistics_analysis.json"
    stats_path.write_text(
        json.dumps(
            {
                "status": "ok",
                "nearest_neighbor": {"mean": 4.4, "median": 4.2, "std": 0.8},
                "fractal_dimension": 1.1,
                "two_point_correlation": {"xi_mean": 0.2, "xi_max": 0.5},
            }
        ),
        encoding="utf-8",
    )

    out_fits = tmp_path / "amanogawa_summary.fits"
    export_analysis_to_fits(
        out_fits=out_fits,
        coords_csv=coords_path,
        detection_json=detection_path,
        spatial_stats_json=stats_path,
        overwrite=True,
    )

    with fits.open(out_fits) as hdul:
        assert hdul[0].header["ORIGIN"] == "Amanogawa"
        assert hdul[0].header["NSTAR"] == 2
        assert np.isclose(hdul[0].header["NNDMEAN"], 4.4)
        assert "STARS" in hdul
        assert len(hdul["STARS"].data) == 2
