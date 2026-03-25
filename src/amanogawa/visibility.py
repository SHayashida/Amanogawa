from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from PIL import ExifTags, Image

from .band_geometry import analyze_band_geometry
from .dark_morphology import detect_dark_lane_mask_from_file
from .detection import DetectionConfig, detect_stars_log

SCORE_VERSION = "visibility-v1"
DEFAULT_VISIBILITY_THRESHOLDS = (0.03, 0.04, 0.05, 0.06, 0.07)

# Bootstrap percentile windows. Replace with goldset-derived values in a later phase.
DEFAULT_REFERENCE_PERCENTILES: dict[str, dict[str, float | bool]] = {
    "star_density_median": {"p10": 25.0, "p90": 1200.0, "invert": False},
    "star_count_robustness": {"p10": 0.20, "p90": 0.95, "invert": False},
    "blob_radius_median_inverse": {"p10": 0.16, "p90": 0.70, "invert": False},
    "band_prominence": {"p10": 0.05, "p90": 0.55, "invert": False},
    "band_angle_stability": {"p10": 0.20, "p90": 0.98, "invert": False},
    "band_width_stability": {"p10": 0.15, "p90": 0.95, "invert": False},
    "dark_lane_bonus": {"p10": 0.00, "p90": 0.75, "invert": False},
    "background_p50": {"p10": 0.08, "p90": 0.50, "invert": True},
    "background_gradient_p95_p5": {"p10": 0.05, "p90": 0.55, "invert": True},
    "clipped_fraction": {"p10": 0.00, "p90": 0.08, "invert": True},
}

EDITING_SOFTWARE_MARKERS = (
    "lightroom",
    "snapseed",
    "photoshop",
    "instagram",
    "vsco",
    "gimp",
    "pixelmator",
    "adobe",
    "google",
)


def _safe_float(value: Any) -> float | None:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def _safe_mean(values: list[float]) -> float | None:
    arr = np.asarray(values, dtype=float)
    finite = arr[np.isfinite(arr)]
    if finite.size == 0:
        return None
    return float(np.mean(finite))


def _safe_median(values: list[float]) -> float | None:
    arr = np.asarray(values, dtype=float)
    finite = arr[np.isfinite(arr)]
    if finite.size == 0:
        return None
    return float(np.median(finite))


def _safe_percentile(values: np.ndarray, q: float) -> float | None:
    finite = np.asarray(values, dtype=float)
    finite = finite[np.isfinite(finite)]
    if finite.size == 0:
        return None
    return float(np.percentile(finite, q))


def _robustness(values: list[float]) -> float:
    arr = np.asarray(values, dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return 0.0
    p10 = float(np.percentile(arr, 10))
    p50 = float(np.percentile(arr, 50))
    p90 = float(np.percentile(arr, 90))
    if p50 <= 0.0:
        return 0.0
    return float(np.clip(1.0 - (p90 - p10) / p50, 0.0, 1.0))


def _angle_stability_deg(angles_deg: list[float]) -> float:
    arr = np.asarray(angles_deg, dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size < 2:
        return 0.0
    theta = np.deg2rad(2.0 * arr)
    resultant = np.abs(np.mean(np.exp(1j * theta)))
    return float(np.clip(resultant, 0.0, 1.0))


def _normalize_feature(name: str, value: float | None) -> float:
    if value is None or not math.isfinite(value):
        return 0.0

    cfg = DEFAULT_REFERENCE_PERCENTILES[name]
    low = float(cfg["p10"])
    high = float(cfg["p90"])
    if high <= low:
        return 0.0

    norm = (float(value) - low) / (high - low)
    norm = float(np.clip(norm, 0.0, 1.0))
    return 1.0 - norm if bool(cfg["invert"]) else norm


def _grade(score: float) -> str:
    if score >= 80.0:
        return "excellent"
    if score >= 60.0:
        return "good"
    if score >= 40.0:
        return "marginal"
    return "poor"


def _qc_status(*, total_score: float, star_density_median: float | None, band_prominence: float | None, star_count_robustness: float, clipped_fraction: float | None, background_gradient: float | None) -> str:
    if (
        total_score < 40.0
        or (star_density_median is not None and star_density_median <= 0.0)
        or (band_prominence is not None and band_prominence < 0.05)
        or (clipped_fraction is not None and clipped_fraction > 0.20)
        or (background_gradient is not None and background_gradient > 0.60)
    ):
        return "fail"

    if (
        total_score < 60.0
        or star_count_robustness < 0.25
        or (band_prominence is not None and band_prominence < 0.10)
        or (clipped_fraction is not None and clipped_fraction > 0.10)
        or (background_gradient is not None and background_gradient > 0.35)
    ):
        return "warn"
    return "pass"


def _get_exif_payload(image_path: str | Path) -> dict[str, Any]:
    path = Path(image_path)
    payload: dict[str, Any] = {
        "device_model": None,
        "device_make": None,
        "software": None,
        "datetime_original": None,
        "exif_available": False,
        "edited_flag": False,
    }

    try:
        with Image.open(path) as img:
            raw_exif = img.getexif()
    except Exception:
        return payload

    if not raw_exif:
        return payload

    exif_map: dict[str, Any] = {}
    for key, value in raw_exif.items():
        tag = ExifTags.TAGS.get(key, str(key))
        exif_map[str(tag)] = value

    payload["exif_available"] = True
    make = exif_map.get("Make")
    model = exif_map.get("Model")
    software = exif_map.get("Software")
    datetime_original = exif_map.get("DateTimeOriginal") or exif_map.get("DateTime")

    make_str = str(make).strip() if make is not None else None
    model_str = str(model).strip() if model is not None else None
    software_str = str(software).strip() if software is not None else None

    device_model: str | None = None
    if make_str and model_str and not model_str.lower().startswith(make_str.lower()):
        device_model = f"{make_str} {model_str}"
    else:
        device_model = model_str or make_str

    payload["device_make"] = make_str
    payload["device_model"] = device_model
    payload["software"] = software_str
    payload["datetime_original"] = str(datetime_original).strip() if datetime_original is not None else None
    if software_str:
        payload["edited_flag"] = any(marker in software_str.lower() for marker in EDITING_SOFTWARE_MARKERS)
    return payload


def _background_mask(shape: tuple[int, int], coords_df: pd.DataFrame) -> np.ndarray:
    mask = np.ones(shape, dtype=bool)
    if coords_df.empty:
        return mask

    yy, xx = np.indices(shape)
    for row in coords_df.itertuples(index=False):
        x = float(getattr(row, "x"))
        y = float(getattr(row, "y"))
        r = max(2.0, 2.0 * float(getattr(row, "r", 2.0)))
        local = (xx - x) ** 2 + (yy - y) ** 2 <= r**2
        mask[local] = False
    return mask


def _background_features(image: np.ndarray, coords_df: pd.DataFrame) -> dict[str, float | None]:
    scaled = np.asarray(image, dtype=float)
    if scaled.size == 0:
        return {
            "background_p50": None,
            "background_gradient_p95_p5": None,
            "clipped_fraction": None,
        }

    scaled = scaled / 255.0 if np.nanmax(scaled) > 1.0 else np.clip(scaled, 0.0, 1.0)
    bg_mask = _background_mask(scaled.shape, coords_df)
    background = scaled[bg_mask]
    if background.size == 0:
        background = scaled.reshape(-1)

    p50 = _safe_percentile(background, 50.0)
    p05 = _safe_percentile(background, 5.0)
    p95 = _safe_percentile(background, 95.0)
    clipped_fraction = float(np.mean(scaled >= 250.0 / 255.0))
    return {
        "background_p50": p50,
        "background_gradient_p95_p5": None if p95 is None or p05 is None else float(p95 - p05),
        "clipped_fraction": clipped_fraction,
    }


def _band_prominence_from_payload(payload: dict[str, Any]) -> float | None:
    profile = payload.get("profile", {})
    if not isinstance(profile, dict):
        return None
    density = np.asarray(profile.get("density", []), dtype=float)
    density = density[np.isfinite(density)]
    if density.size == 0:
        return None
    peak = float(np.max(density))
    background = float(np.percentile(density, 10))
    if peak <= 0.0:
        return 0.0
    return float(np.clip((peak - background) / peak, 0.0, 1.0))


def _dark_lane_bonus(dark_payload: dict[str, Any] | None) -> float:
    if not dark_payload:
        return 0.0
    dark_fraction = _safe_float(dark_payload.get("dark_area_fraction")) or 0.0
    components = _safe_float(dark_payload.get("num_dark_components")) or 0.0
    frac_score = float(np.clip((dark_fraction - 0.01) / 0.19, 0.0, 1.0))
    comp_score = float(np.clip((components - 1.0) / 7.0, 0.0, 1.0))
    return 0.6 * frac_score + 0.4 * comp_score


def _read_json(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    p = Path(path)
    if not p.exists():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def analyze_visibility(
    *,
    image_path: str | Path,
    detection_summary_json: str | Path,
    band_geometry_json: str | Path | None = None,
    dark_morphology_json: str | Path | None = None,
    thresholds: tuple[float, ...] = DEFAULT_VISIBILITY_THRESHOLDS,
) -> tuple[dict[str, Any], dict[str, Any]]:
    detection_payload = _read_json(detection_summary_json)
    if detection_payload is None:
        raise FileNotFoundError(f"Missing detection summary: {detection_summary_json}")

    coords_csv = Path(str(detection_payload["coords_csv"]))
    coords_df = pd.read_csv(coords_csv)
    image = np.asarray(Image.open(Path(image_path)).convert("L"), dtype=float)
    width_px = int(detection_payload["width_px"])
    height_px = int(detection_payload["height_px"])

    detect_cfg = detection_payload.get("detection", {})
    max_sigma = float(detect_cfg.get("max_sigma", DetectionConfig.max_sigma))
    num_sigma = int(detect_cfg.get("num_sigma", DetectionConfig.num_sigma))

    sweep_rows: list[dict[str, float | None]] = []
    for threshold in thresholds:
        df = detect_stars_log(image, threshold=float(threshold), max_sigma=max_sigma, num_sigma=num_sigma)
        points = df[["x", "y"]].to_numpy(dtype=float) if not df.empty else np.empty((0, 2), dtype=float)
        fit = analyze_band_geometry(points, width_px, height_px, bins_x=60, nbins_profile=120)
        sweep_rows.append(
            {
                "threshold": float(threshold),
                "num_stars": float(len(df)),
                "blob_radius_median": _safe_median(df["r"].astype(float).tolist()) if "r" in df else None,
                "band_angle_deg": _safe_float(fit.angle_deg),
                "band_empirical_fwhm_px": _safe_float(fit.empirical_fwhm_px),
            }
        )

    star_counts = [float(row["num_stars"] or 0.0) for row in sweep_rows]
    blob_radius_medians = [row["blob_radius_median"] for row in sweep_rows if row["blob_radius_median"] is not None]
    band_angles = [row["band_angle_deg"] for row in sweep_rows if row["band_angle_deg"] is not None]
    band_widths = [row["band_empirical_fwhm_px"] for row in sweep_rows if row["band_empirical_fwhm_px"] is not None]

    star_density_values = [
        (float(count) * 1_000_000.0) / max(float(width_px * height_px), 1.0)
        for count in star_counts
    ]
    star_density_median = _safe_median(star_density_values)
    star_count_robustness = _robustness(star_counts)
    blob_radius_median = _safe_median([float(v) for v in blob_radius_medians])
    blob_radius_median_inverse = None if blob_radius_median is None or blob_radius_median <= 0.0 else float(1.0 / blob_radius_median)

    band_payload = _read_json(band_geometry_json)
    if band_payload is None:
        base_fit = analyze_band_geometry(coords_df[["x", "y"]].to_numpy(dtype=float), width_px, height_px, bins_x=60, nbins_profile=120)
        band_payload = {
            "principal_axis": {
                "angle_deg": base_fit.angle_deg,
                "center_px": [float(base_fit.center_px[0]), float(base_fit.center_px[1])],
                "axis_ratio": base_fit.axis_ratio,
            },
            "band_width_measurements": {
                "gaussian_fwhm_px": base_fit.gaussian_fwhm_px,
                "lorentzian_fwhm_px": base_fit.lorentzian_fwhm_px,
                "empirical_fwhm_px": base_fit.empirical_fwhm_px,
            },
            "profile": {"y_centers": base_fit.y_centers, "density": base_fit.density_profile},
        }

    dark_payload = _read_json(dark_morphology_json)
    if dark_payload is None:
        try:
            dark_payload = detect_dark_lane_mask_from_file(image_path).metrics
        except Exception:
            dark_payload = None

    band_prominence = _band_prominence_from_payload(band_payload)
    band_angle_stability = _angle_stability_deg([float(v) for v in band_angles])
    band_width_stability = _robustness([float(v) for v in band_widths])
    dark_lane_bonus = _dark_lane_bonus(dark_payload)
    background = _background_features(image, coords_df)
    metadata = _get_exif_payload(image_path)

    raw_features = {
        "star_density_median": star_density_median,
        "star_count_robustness": star_count_robustness,
        "blob_radius_median": blob_radius_median,
        "blob_radius_median_inverse": blob_radius_median_inverse,
        "band_prominence": band_prominence,
        "band_angle_stability": band_angle_stability,
        "band_width_stability": band_width_stability,
        "dark_lane_bonus": dark_lane_bonus,
        "background_p50": background["background_p50"],
        "background_gradient_p95_p5": background["background_gradient_p95_p5"],
        "clipped_fraction": background["clipped_fraction"],
    }

    normalized_features = {
        key: _normalize_feature(key, _safe_float(value))
        for key, value in raw_features.items()
        if key in DEFAULT_REFERENCE_PERCENTILES
    }

    point_score = 100.0 * (
        0.45 * normalized_features["star_density_median"]
        + 0.35 * normalized_features["star_count_robustness"]
        + 0.20 * normalized_features["blob_radius_median_inverse"]
    )
    diffuse_score = 100.0 * (
        0.45 * normalized_features["band_prominence"]
        + 0.25 * normalized_features["band_angle_stability"]
        + 0.20 * normalized_features["band_width_stability"]
        + 0.10 * normalized_features["dark_lane_bonus"]
    )
    background_score = 100.0 * (
        0.40 * normalized_features["background_p50"]
        + 0.35 * normalized_features["background_gradient_p95_p5"]
        + 0.25 * normalized_features["clipped_fraction"]
    )
    total_score = float(np.clip(0.35 * point_score + 0.45 * diffuse_score + 0.20 * background_score, 0.0, 100.0))

    qc_status = _qc_status(
        total_score=total_score,
        star_density_median=star_density_median,
        band_prominence=band_prominence,
        star_count_robustness=star_count_robustness,
        clipped_fraction=_safe_float(background["clipped_fraction"]),
        background_gradient=_safe_float(background["background_gradient_p95_p5"]),
    )

    features_payload: dict[str, Any] = {
        "status": "ok",
        "score_version": SCORE_VERSION,
        "image": Path(image_path).name,
        "image_path": str(Path(image_path)),
        "image_dimensions": {"width_px": width_px, "height_px": height_px},
        "device_metadata": metadata,
        "interpretation": {
            "semantics": "image-based relative visibility / analyzability",
            "limitation": "low scores can reflect device limits or capture quality rather than true sky quality",
        },
        "reference_profile": {
            "source": "v1_bootstrap_defaults",
            "percentile_window": "P10-P90",
        },
        "threshold_sweep": {
            "thresholds": [float(row["threshold"]) for row in sweep_rows],
            "star_counts": star_counts,
            "blob_radius_medians": [row["blob_radius_median"] for row in sweep_rows],
            "band_angles_deg": [row["band_angle_deg"] for row in sweep_rows],
            "band_empirical_fwhm_px": [row["band_empirical_fwhm_px"] for row in sweep_rows],
        },
        "raw_features": raw_features,
    }

    score_payload: dict[str, Any] = {
        "status": "ok",
        "score_version": SCORE_VERSION,
        "visibility_score": total_score,
        "grade": _grade(total_score),
        "qc_status": qc_status,
        "research_usable": qc_status == "pass",
        "branch_scores": {
            "point_visibility": point_score,
            "diffuse_visibility": diffuse_score,
            "background_conditions": background_score,
        },
        "normalized_features": normalized_features,
        "interpretation_note": "This score reflects the evidence present in the submitted image, not the true sky quality in isolation.",
        "device_limitation_note": "v1 does not adjust for device differences; low scores may reflect hardware, software processing, or capture quality.",
    }
    return features_payload, score_payload


def write_visibility_outputs(
    *,
    image_path: str | Path,
    detection_summary_json: str | Path,
    out_dir: str | Path,
    band_geometry_json: str | Path | None = None,
    dark_morphology_json: str | Path | None = None,
    thresholds: tuple[float, ...] = DEFAULT_VISIBILITY_THRESHOLDS,
) -> dict[str, Any]:
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    features_payload, score_payload = analyze_visibility(
        image_path=image_path,
        detection_summary_json=detection_summary_json,
        band_geometry_json=band_geometry_json,
        dark_morphology_json=dark_morphology_json,
        thresholds=thresholds,
    )
    features_json = out_path / "visibility_features.json"
    score_json = out_path / "visibility_score.json"
    features_json.write_text(json.dumps(features_payload, indent=2), encoding="utf-8")
    score_json.write_text(json.dumps(score_payload, indent=2), encoding="utf-8")
    return {
        "features_json": str(features_json),
        "score_json": str(score_json),
        "visibility_score": float(score_payload["visibility_score"]),
        "qc_status": str(score_payload["qc_status"]),
        "research_usable": bool(score_payload["research_usable"]),
    }
