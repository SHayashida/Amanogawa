from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from . import __version__
from .band_geometry import main as band_main
from .dark_morphology import main as dark_main
from .detection import (
    DEFAULT_IMAGE_EXTENSIONS,
    _image_slug,
    _parse_extensions,
    _run_detection_for_image,
    discover_images,
)
from .spatial_stats import main as stats_main


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _path_from_payload(path_value: object, *, base_dir: Path, default: Path) -> Path:
    if not isinstance(path_value, str) or not path_value.strip():
        return default

    raw = Path(path_value)
    if raw.is_absolute():
        return raw

    by_base = base_dir / raw
    if by_base.exists():
        return by_base
    return raw


def _load_detection_meta_if_complete(detection_dir: Path) -> dict[str, object] | None:
    summary_path = detection_dir / "detection_summary.json"
    if not summary_path.exists():
        return None

    try:
        payload = json.loads(summary_path.read_text(encoding="utf-8"))
    except Exception:
        return None

    width = payload.get("width_px")
    height = payload.get("height_px")
    num_stars = payload.get("num_stars")
    if width is None or height is None or num_stars is None:
        return None

    coords_path = _path_from_payload(
        payload.get("coords_csv"),
        base_dir=detection_dir,
        default=detection_dir / "star_coords.csv",
    )
    if not coords_path.exists():
        return None

    payload["coords_csv"] = str(coords_path)
    payload["width_px"] = int(width)
    payload["height_px"] = int(height)
    payload["num_stars"] = int(num_stars)
    return payload


def _run_stats_step(
    *,
    coords_csv: Path,
    out_dir: Path,
    width_px: int,
    height_px: int,
    seed: int,
    max_points: int,
) -> None:
    rc = stats_main(
        [
            "--coords",
            str(coords_csv),
            "--out",
            str(out_dir),
            "--width",
            str(width_px),
            "--height",
            str(height_px),
            "--seed",
            str(seed),
            "--max-points",
            str(max_points),
        ]
    )
    if rc != 0:
        raise RuntimeError(f"amanogawa-stats exited with status {rc}")


def _run_band_step(
    *,
    coords_csv: Path,
    out_dir: Path,
    width_px: int,
    height_px: int,
    bins_x: int,
    profile_bins: int,
) -> None:
    rc = band_main(
        [
            "--coords",
            str(coords_csv),
            "--out",
            str(out_dir),
            "--width",
            str(width_px),
            "--height",
            str(height_px),
            "--bins-x",
            str(bins_x),
            "--profile-bins",
            str(profile_bins),
        ]
    )
    if rc != 0:
        raise RuntimeError(f"amanogawa-band exited with status {rc}")


def _run_dark_step(*, image_path: Path, out_dir: Path) -> None:
    rc = dark_main(["--image", str(image_path), "--out", str(out_dir)])
    if rc != 0:
        raise RuntimeError(f"amanogawa-dark exited with status {rc}")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="amanogawa-run",
        description="Run detect -> stats -> band -> dark across one image or an image directory",
    )
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--image", help="Path to one input image")
    src.add_argument("--image-dir", help="Directory containing multiple input images")

    p.add_argument("--out", required=True, help="Output root directory")
    p.add_argument("--recursive", action="store_true", help="Recursively discover images under --image-dir")
    p.add_argument(
        "--extensions",
        default=",".join(ext.lstrip(".") for ext in DEFAULT_IMAGE_EXTENSIONS),
        help="Comma-separated extensions used with --image-dir",
    )
    p.add_argument("--resume", action="store_true", help="Skip a step when its output already exists")
    p.add_argument("--fail-fast", action="store_true", help="Stop the pipeline at the first error")

    # Detection parameters
    p.add_argument("--threshold", type=float, default=0.05)
    p.add_argument("--max-sigma", type=float, default=6.0)
    p.add_argument("--num-sigma", type=int, default=12)
    p.add_argument("--threshold-min", type=float, default=None)
    p.add_argument("--threshold-max", type=float, default=None)
    p.add_argument("--threshold-steps", type=int, default=10)
    p.add_argument("--plot-output", action="store_true")

    # Optional step toggles
    p.add_argument("--skip-stats", action="store_true")
    p.add_argument("--skip-band", action="store_true")
    p.add_argument("--skip-dark", action="store_true")

    # Quality gates
    p.add_argument(
        "--min-stars-stats",
        type=int,
        default=0,
        help="Skip stats when detected stars are fewer than this value (default: disabled)",
    )
    p.add_argument(
        "--min-stars-band",
        type=int,
        default=0,
        help="Skip band fit when detected stars are fewer than this value (default: disabled)",
    )

    # Stats / band parameters
    p.add_argument("--stats-seed", type=int, default=42)
    p.add_argument("--stats-max-points", type=int, default=3500)
    p.add_argument("--band-bins-x", type=int, default=60)
    p.add_argument("--band-profile-bins", type=int, default=200)
    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = _build_parser().parse_args(argv)

    out_root = Path(args.out).resolve()
    out_root.mkdir(parents=True, exist_ok=True)

    if args.image is not None:
        image_paths = [Path(args.image).resolve()]
        image_mode = "single_image"
        extensions = None
    else:
        extensions = _parse_extensions(str(args.extensions))
        image_paths = [p.resolve() for p in discover_images(args.image_dir, recursive=bool(args.recursive), extensions=extensions)]
        if not image_paths:
            raise ValueError(f"No matching images found in: {args.image_dir}")
        image_mode = "image_dir"

    started_at = _utc_now_iso()
    image_reports: list[dict[str, object]] = []
    total_errors = 0

    for image_path in image_paths:
        slug = _image_slug(image_path)
        image_out = out_root / slug
        detection_dir = image_out / "detection"
        stats_dir = image_out / "spatial_stats"
        band_dir = image_out / "band_geometry"
        dark_dir = image_out / "dark_morphology"

        report: dict[str, object] = {
            "image": image_path.name,
            "image_path": str(image_path),
            "slug": slug,
            "out_dir": str(image_out),
            "steps": {},
        }
        steps: dict[str, dict[str, object]] = report["steps"]  # type: ignore[assignment]

        detection_meta: dict[str, object] | None = None
        detect_error = False

        # Detect
        try:
            if bool(args.resume):
                detection_meta = _load_detection_meta_if_complete(detection_dir)
            if detection_meta is not None:
                steps["detect"] = {
                    "status": "skipped",
                    "reason": "resume",
                    "out_dir": str(detection_dir),
                    "summary_json": str(detection_dir / "detection_summary.json"),
                }
            else:
                detection_meta = _run_detection_for_image(
                    image_path=image_path,
                    out_dir=detection_dir,
                    detect_threshold=float(args.threshold),
                    max_sigma=float(args.max_sigma),
                    num_sigma=int(args.num_sigma),
                    threshold_min=args.threshold_min,
                    threshold_max=args.threshold_max,
                    steps=int(args.threshold_steps),
                    plot_output=bool(args.plot_output),
                )
                steps["detect"] = {
                    "status": "ok",
                    "out_dir": str(detection_dir),
                    "summary_json": str(detection_dir / "detection_summary.json"),
                }
            report["detected_stars"] = int(detection_meta["num_stars"]) if detection_meta is not None else 0
        except Exception as exc:
            detect_error = True
            total_errors += 1
            steps["detect"] = {"status": "error", "error": str(exc), "out_dir": str(detection_dir)}
            report["detected_stars"] = 0

        if detect_error and bool(args.fail_fast):
            report["status"] = "error"
            image_reports.append(report)
            break

        # Stats
        if bool(args.skip_stats):
            steps["stats"] = {"status": "skipped", "reason": "disabled"}
        elif detection_meta is None:
            steps["stats"] = {"status": "skipped", "reason": "missing_detection"}
        elif int(detection_meta["num_stars"]) < int(args.min_stars_stats):
            steps["stats"] = {
                "status": "skipped",
                "reason": "quality_gate",
                "min_stars_required": int(args.min_stars_stats),
                "detected_stars": int(detection_meta["num_stars"]),
            }
        elif bool(args.resume) and (stats_dir / "spatial_statistics_analysis.json").exists():
            steps["stats"] = {
                "status": "skipped",
                "reason": "resume",
                "out_dir": str(stats_dir),
                "summary_json": str(stats_dir / "spatial_statistics_analysis.json"),
            }
        else:
            try:
                _run_stats_step(
                    coords_csv=Path(str(detection_meta["coords_csv"])),
                    out_dir=stats_dir,
                    width_px=int(detection_meta["width_px"]),
                    height_px=int(detection_meta["height_px"]),
                    seed=int(args.stats_seed),
                    max_points=int(args.stats_max_points),
                )
                steps["stats"] = {
                    "status": "ok",
                    "out_dir": str(stats_dir),
                    "summary_json": str(stats_dir / "spatial_statistics_analysis.json"),
                }
            except Exception as exc:
                total_errors += 1
                steps["stats"] = {"status": "error", "error": str(exc), "out_dir": str(stats_dir)}
                if bool(args.fail_fast):
                    report["status"] = "error"
                    image_reports.append(report)
                    break

        # Band
        if bool(args.skip_band):
            steps["band"] = {"status": "skipped", "reason": "disabled"}
        elif detection_meta is None:
            steps["band"] = {"status": "skipped", "reason": "missing_detection"}
        elif int(detection_meta["num_stars"]) < int(args.min_stars_band):
            steps["band"] = {
                "status": "skipped",
                "reason": "quality_gate",
                "min_stars_required": int(args.min_stars_band),
                "detected_stars": int(detection_meta["num_stars"]),
            }
        elif bool(args.resume) and (band_dir / "band_geometry_analysis.json").exists():
            steps["band"] = {
                "status": "skipped",
                "reason": "resume",
                "out_dir": str(band_dir),
                "summary_json": str(band_dir / "band_geometry_analysis.json"),
            }
        else:
            try:
                _run_band_step(
                    coords_csv=Path(str(detection_meta["coords_csv"])),
                    out_dir=band_dir,
                    width_px=int(detection_meta["width_px"]),
                    height_px=int(detection_meta["height_px"]),
                    bins_x=int(args.band_bins_x),
                    profile_bins=int(args.band_profile_bins),
                )
                steps["band"] = {
                    "status": "ok",
                    "out_dir": str(band_dir),
                    "summary_json": str(band_dir / "band_geometry_analysis.json"),
                }
            except Exception as exc:
                total_errors += 1
                steps["band"] = {"status": "error", "error": str(exc), "out_dir": str(band_dir)}
                if bool(args.fail_fast):
                    report["status"] = "error"
                    image_reports.append(report)
                    break

        # Dark
        if bool(args.skip_dark):
            steps["dark"] = {"status": "skipped", "reason": "disabled"}
        elif bool(args.resume) and (dark_dir / "improved_dark_detection.json").exists():
            steps["dark"] = {
                "status": "skipped",
                "reason": "resume",
                "out_dir": str(dark_dir),
                "summary_json": str(dark_dir / "improved_dark_detection.json"),
            }
        else:
            try:
                _run_dark_step(image_path=image_path, out_dir=dark_dir)
                steps["dark"] = {
                    "status": "ok",
                    "out_dir": str(dark_dir),
                    "summary_json": str(dark_dir / "improved_dark_detection.json"),
                }
            except Exception as exc:
                total_errors += 1
                steps["dark"] = {"status": "error", "error": str(exc), "out_dir": str(dark_dir)}
                if bool(args.fail_fast):
                    report["status"] = "error"
                    image_reports.append(report)
                    break

        has_error = any(step.get("status") == "error" for step in steps.values())
        report["status"] = "error" if has_error else "ok"
        image_reports.append(report)

    manifest = {
        "status": "ok" if total_errors == 0 else "completed_with_errors",
        "started_at_utc": started_at,
        "finished_at_utc": _utc_now_iso(),
        "version": __version__,
        "run_config": {
            "mode": image_mode,
            "image": args.image,
            "image_dir": args.image_dir,
            "out": str(out_root),
            "recursive": bool(args.recursive),
            "extensions": list(extensions) if extensions is not None else None,
            "resume": bool(args.resume),
            "fail_fast": bool(args.fail_fast),
            "steps": {
                "stats": not bool(args.skip_stats),
                "band": not bool(args.skip_band),
                "dark": not bool(args.skip_dark),
            },
            "quality_gates": {
                "min_stars_stats": int(args.min_stars_stats),
                "min_stars_band": int(args.min_stars_band),
            },
            "detection": {
                "threshold": float(args.threshold),
                "max_sigma": float(args.max_sigma),
                "num_sigma": int(args.num_sigma),
                "threshold_min": args.threshold_min,
                "threshold_max": args.threshold_max,
                "threshold_steps": int(args.threshold_steps),
                "plot_output": bool(args.plot_output),
            },
            "spatial_stats": {
                "seed": int(args.stats_seed),
                "max_points": int(args.stats_max_points),
            },
            "band_geometry": {
                "bins_x": int(args.band_bins_x),
                "profile_bins": int(args.band_profile_bins),
            },
        },
        "num_images": len(image_reports),
        "num_images_ok": sum(int(r.get("status") == "ok") for r in image_reports),
        "num_images_error": sum(int(r.get("status") == "error") for r in image_reports),
        "images": image_reports,
    }
    (out_root / "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
