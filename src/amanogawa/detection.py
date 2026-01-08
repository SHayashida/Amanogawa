from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Optional

import numpy as np
import pandas as pd
from skimage.feature import blob_log

from .io import load_image_gray, to_unit


@dataclass(frozen=True)
class DetectionConfig:
    max_sigma: float = 6.0
    num_sigma: int = 12
    threshold: float = 0.05


def plot_star_overlay(
    image_path: str | Path,
    coords_df: pd.DataFrame,
    output_path: str | Path,
    *,
    marker_size: float = 50,
    marker_color: str = "red",
    marker_alpha: float = 0.6,
) -> None:
    """Create and save a visualization of detected stars overlaid on the image.

    Parameters
    ----------
    image_path : str | Path
        Path to the original image file.
    coords_df : pd.DataFrame
        DataFrame with 'x' and 'y' columns for star coordinates.
    output_path : str | Path
        Path where the output PNG/JPG will be saved.
    marker_size : float, optional
        Size of the markers for detected stars, by default 50.
    marker_color : str, optional
        Color of the markers, by default "red".
    marker_alpha : float, optional
        Transparency of the markers (0-1), by default 0.6.
    """
    import matplotlib.pyplot as plt
    from PIL import Image

    # Load original image
    img = Image.open(Path(image_path))

    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8), dpi=150)
    ax.imshow(img, cmap="gray" if img.mode == "L" else None)

    # Overlay detected stars
    if len(coords_df) > 0:
        ax.scatter(
            coords_df["x"],
            coords_df["y"],
            s=marker_size,
            c=marker_color,
            alpha=marker_alpha,
            edgecolors="white",
            linewidths=0.5,
            label=f"{len(coords_df)} stars detected",
        )
        ax.legend(loc="upper right", fontsize=10, framealpha=0.8)

    ax.set_xlabel("X (pixels)", fontsize=10)
    ax.set_ylabel("Y (pixels)", fontsize=10)
    ax.set_title("Star Detection Results", fontsize=12, fontweight="bold")
    ax.grid(False)

    # Save figure
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def detect_stars_log(
    image: np.ndarray,
    *,
    max_sigma: float = 6.0,
    num_sigma: int = 12,
    threshold: float = 0.05,
) -> pd.DataFrame:
    """Detect stars using Laplacian-of-Gaussian blob detection.

    Returns a DataFrame with columns: ``x``, ``y``, ``r`` (pixels).
    """

    img_u = to_unit(image)
    blobs = blob_log(img_u, max_sigma=max_sigma, num_sigma=num_sigma, threshold=threshold)
    if len(blobs) == 0:
        return pd.DataFrame(columns=["x", "y", "r"])
    # blob_log returns (y, x, sigma)
    return pd.DataFrame({"x": blobs[:, 1], "y": blobs[:, 0], "r": blobs[:, 2]})


def load_or_detect_stars(
    coords_csv: str | Path,
    image_path: str | Path,
    *,
    detect_threshold: float = 0.05,
    max_sigma: float = 6.0,
    num_sigma: int = 12,
) -> tuple[np.ndarray, tuple[int, int], pd.DataFrame]:
    """Load existing coordinate CSV or perform star detection.

    Returns
    -------
    image, (W, H), df
    """

    image, (width, height) = load_image_gray(image_path)
    p = Path(coords_csv)

    if p.exists():
        df = pd.read_csv(p)
    else:
        df = detect_stars_log(image, threshold=detect_threshold, max_sigma=max_sigma, num_sigma=num_sigma)
        p.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(p, index=False)

    # Keep only stars within image bounds
    mask = (df["x"].between(0, width - 1)) & (df["y"].between(0, height - 1))
    df = df[mask].reset_index(drop=True)
    return image, (width, height), df


def threshold_sweep(
    image_path: str | Path,
    *,
    thresholds: Iterable[float],
    out_dir: str | Path,
    max_sigma: float = 6.0,
    num_sigma: int = 12,
) -> pd.DataFrame:
    """Run LoG detection across a range of thresholds and save a summary CSV."""

    image, (width, height) = load_image_gray(image_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, float]] = []
    for t in thresholds:
        df = detect_stars_log(image, threshold=float(t), max_sigma=max_sigma, num_sigma=num_sigma)
        rows.append({"threshold": float(t), "N": float(len(df)), "width_px": float(width), "height_px": float(height)})

    summary = pd.DataFrame(rows).sort_values("threshold").reset_index(drop=True)
    summary.to_csv(out_dir / "threshold_sweep_summary.csv", index=False)
    return summary


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="amanogawa-detect", description="LoG star detection + optional threshold sweep")
    p.add_argument("--image", required=True, help="Path to input image (e.g., JPG)")
    p.add_argument("--out", required=True, help="Output directory")
    p.add_argument("--coords", default=None, help="Optional output coords CSV path (default: <out>/star_coords.csv)")
    p.add_argument("--threshold", type=float, default=0.05, help="LoG detection threshold (default: 0.05)")
    p.add_argument("--max-sigma", type=float, default=6.0)
    p.add_argument("--num-sigma", type=int, default=12)
    p.add_argument("--threshold-min", type=float, default=None)
    p.add_argument("--threshold-max", type=float, default=None)
    p.add_argument("--steps", type=int, default=10)
    p.add_argument("--plot-output", action="store_true", help="Generate and save a visualization of detected stars")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    coords_csv = Path(args.coords) if args.coords else (out_dir / "star_coords.csv")
    image, (width, height), df = load_or_detect_stars(
        coords_csv,
        args.image,
        detect_threshold=float(args.threshold),
        max_sigma=float(args.max_sigma),
        num_sigma=int(args.num_sigma),
    )
    df.to_csv(coords_csv, index=False)

    meta = {
        "image": str(Path(args.image).name),
        "width_px": width,
        "height_px": height,
        "num_stars": int(len(df)),
        "detection": asdict(DetectionConfig(max_sigma=float(args.max_sigma), num_sigma=int(args.num_sigma), threshold=float(args.threshold))),
    }
    (out_dir / "detection_summary.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

    if args.threshold_min is not None and args.threshold_max is not None:
        thresholds = np.linspace(float(args.threshold_min), float(args.threshold_max), int(args.steps))
        threshold_sweep(
            args.image,
            thresholds=thresholds,
            out_dir=out_dir,
            max_sigma=float(args.max_sigma),
            num_sigma=int(args.num_sigma),
        )

    # Generate visualization if requested
    if args.plot_output:
        plot_star_overlay(args.image, df, out_dir / "star_detection_overlay.png")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
