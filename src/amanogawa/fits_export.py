from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import pandas as pd
from astropy.io import fits
from astropy.table import Table

from . import __version__
from .io import load_image_gray


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load_json(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"JSON file not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def _set_float(header: fits.Header, key: str, value: Any, comment: str) -> None:
    if value is None:
        return
    try:
        header[key] = (float(value), comment)
    except Exception:
        return


def _set_int(header: fits.Header, key: str, value: Any, comment: str) -> None:
    if value is None:
        return
    try:
        header[key] = (int(value), comment)
    except Exception:
        return


def _set_str(header: fits.Header, key: str, value: Any, comment: str) -> None:
    if value is None:
        return
    text = str(value).strip()
    if not text:
        return
    header[key] = (text, comment)


def map_analysis_to_header(
    header: fits.Header,
    *,
    detection: dict[str, Any] | None = None,
    spatial_stats: dict[str, Any] | None = None,
    band_geometry: dict[str, Any] | None = None,
    dark_morphology: dict[str, Any] | None = None,
    image_path: str | Path | None = None,
) -> fits.Header:
    """Map Amanogawa analysis metadata to FITS header cards.

    This is a pragmatic FITS summary mapping for P1. Keys are compact and stable,
    while full-resolution metadata remains in the source JSON artifacts.
    """

    header["ORIGIN"] = ("Amanogawa", "Pipeline origin")
    header["AMNVER"] = (__version__, "Amanogawa package version")
    header["DATE"] = (_utc_now_iso(), "UTC export timestamp")
    _set_str(header, "AMNIMG", image_path, "Input image path")

    if detection is not None:
        _set_str(header, "DETSTAT", detection.get("status", "ok"), "Detection status")
        _set_int(header, "IMGW", detection.get("width_px"), "Image width (px)")
        _set_int(header, "IMGH", detection.get("height_px"), "Image height (px)")
        _set_int(header, "NSTAR", detection.get("num_stars"), "Detected sources")

        cfg = detection.get("detection", {})
        if isinstance(cfg, dict):
            _set_float(header, "DTHRESH", cfg.get("threshold"), "LoG threshold")
            _set_float(header, "DMAXSIG", cfg.get("max_sigma"), "LoG max sigma")
            _set_int(header, "DNUMSIG", cfg.get("num_sigma"), "LoG sigma count")

    if spatial_stats is not None:
        _set_str(header, "SPSTAT", spatial_stats.get("status"), "Spatial stats status")
        nnd = spatial_stats.get("nearest_neighbor", {})
        if isinstance(nnd, dict):
            _set_float(header, "NNDMEAN", nnd.get("mean"), "Nearest-neighbor mean")
            _set_float(header, "NNDMED", nnd.get("median"), "Nearest-neighbor median")
            _set_float(header, "NNDSTD", nnd.get("std"), "Nearest-neighbor std")
        _set_float(header, "FDIM", spatial_stats.get("fractal_dimension"), "Box-count dimension")

        xi = spatial_stats.get("two_point_correlation", {})
        if isinstance(xi, dict):
            _set_float(header, "XIMEAN", xi.get("xi_mean"), "2PCF xi mean")
            _set_float(header, "XIMAX", xi.get("xi_max"), "2PCF xi max")

    if band_geometry is not None:
        _set_str(header, "BGSTAT", band_geometry.get("status"), "Band geometry status")
        axis = band_geometry.get("principal_axis", {})
        if isinstance(axis, dict):
            _set_float(header, "BANGDEG", axis.get("angle_deg"), "Band principal axis (deg)")
            _set_float(header, "BAXRAT", axis.get("axis_ratio"), "Band axis ratio")

        widths = band_geometry.get("band_width_measurements", {})
        if isinstance(widths, dict):
            _set_float(header, "BFGWHM", widths.get("gaussian_fwhm_px"), "Gaussian FWHM (px)")
            _set_float(header, "BFLWHM", widths.get("lorentzian_fwhm_px"), "Lorentzian FWHM (px)")
            _set_float(header, "BFEWHM", widths.get("empirical_fwhm_px"), "Empirical FWHM (px)")

    if dark_morphology is not None:
        _set_float(header, "DKFRAC", dark_morphology.get("dark_area_fraction"), "Dark area fraction")
        _set_int(header, "DKCOMP", dark_morphology.get("num_dark_components"), "Dark component count")
        _set_float(header, "DKECC", dark_morphology.get("mean_eccentricity"), "Mean eccentricity")
        _set_float(header, "DKELONG", dark_morphology.get("mean_elongation"), "Mean elongation")
        _set_float(
            header,
            "DKFDM",
            dark_morphology.get("fractal_dimension_dark_mask"),
            "Dark mask fractal dimension",
        )
        _set_float(
            header,
            "DKFDS",
            dark_morphology.get("fractal_dimension_skeleton"),
            "Skeleton fractal dimension",
        )

    return header


def export_analysis_to_fits(
    *,
    out_fits: str | Path,
    coords_csv: str | Path | None = None,
    image_path: str | Path | None = None,
    detection_json: str | Path | None = None,
    spatial_stats_json: str | Path | None = None,
    band_geometry_json: str | Path | None = None,
    dark_morphology_json: str | Path | None = None,
    overwrite: bool = False,
) -> Path:
    """Export Amanogawa artifacts to a FITS container with standardized headers."""

    detection = _load_json(detection_json)
    spatial_stats = _load_json(spatial_stats_json)
    band_geometry = _load_json(band_geometry_json)
    dark_morphology = _load_json(dark_morphology_json)

    if image_path is not None:
        image, _ = load_image_gray(image_path)
        primary = fits.PrimaryHDU(data=image.astype("float32"))
        primary.header["BUNIT"] = ("ADU_NORM", "Normalized image unit")
    else:
        primary = fits.PrimaryHDU()

    map_analysis_to_header(
        primary.header,
        detection=detection,
        spatial_stats=spatial_stats,
        band_geometry=band_geometry,
        dark_morphology=dark_morphology,
        image_path=image_path,
    )

    hdus: list[fits.hdu.base.ExtensionHDU | fits.PrimaryHDU] = [primary]

    if coords_csv is not None:
        coords_path = Path(coords_csv)
        if not coords_path.exists():
            raise FileNotFoundError(f"Coordinate CSV not found: {coords_path}")
        df = pd.read_csv(coords_path)
        table = Table.from_pandas(df)
        stars = fits.BinTableHDU(table, name="STARS")
        stars.header["NROWS"] = (int(len(df)), "Number of catalog rows")
        hdus.append(stars)

    out = Path(out_fits)
    out.parent.mkdir(parents=True, exist_ok=True)
    fits.HDUList(hdus).writeto(out, overwrite=bool(overwrite))
    return out


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="amanogawa-fits-export",
        description="Export Amanogawa outputs into a FITS file with mapped summary headers",
    )
    p.add_argument("--out", required=True, help="Output FITS path")
    p.add_argument("--coords", default=None, help="Optional star coordinate CSV")
    p.add_argument("--image", default=None, help="Optional image path for Primary HDU data")
    p.add_argument("--detection-json", default=None, help="Path to detection_summary.json")
    p.add_argument("--stats-json", default=None, help="Path to spatial_statistics_analysis.json")
    p.add_argument("--band-json", default=None, help="Path to band_geometry_analysis.json")
    p.add_argument("--dark-json", default=None, help="Path to improved_dark_detection.json")
    p.add_argument("--overwrite", action="store_true", help="Overwrite existing FITS file")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    export_analysis_to_fits(
        out_fits=args.out,
        coords_csv=args.coords,
        image_path=args.image,
        detection_json=args.detection_json,
        spatial_stats_json=args.stats_json,
        band_geometry_json=args.band_json,
        dark_morphology_json=args.dark_json,
        overwrite=bool(args.overwrite),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
