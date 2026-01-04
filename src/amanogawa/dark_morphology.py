from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

import numpy as np

from scipy.ndimage import distance_transform_edt, gaussian_filter
from skimage.measure import label, regionprops
from skimage.morphology import closing, disk, opening, remove_small_objects, skeletonize
from skimage.segmentation import watershed

from .io import load_image_gray, to_unit


@dataclass(frozen=True)
class DarkMaskConfig:
    """Configuration for dark-lane mask generation.

    This mirrors the "Improved Dark Lane Detection Algorithm" in the notebook:
    invert -> multi-scale background subtraction -> multi-threshold -> morphology -> watershed.
    """

    # Preprocessing
    background_scales: tuple[int, ...] = (20, 50, 100)
    background_weight: float = 0.3

    # Multi-threshold mask fusion
    thresholds: tuple[float, ...] = (0.15, 0.25, 0.35, 0.45)
    morph_radius: int = 2
    min_size_base: int = 100

    # Watershed seeds
    min_seed_distance_px: int = 50
    min_seed_peak: float = 5.0
    max_seeds: int = 50


@dataclass(frozen=True)
class DarkMaskResult:
    combined_mask: np.ndarray  # bool
    labels_ws: np.ndarray  # int
    skeleton: np.ndarray  # bool
    metrics: dict[str, object]


def boxcount_fractal_on_mask(
    mask: np.ndarray,
    *,
    exp_from: float = -1.0,
    exp_to: float = -2.2,
    steps: int = 10,
) -> tuple[float, np.ndarray, np.ndarray]:
    """Box-counting fractal dimension for a binary mask.

    The mask's True pixels are treated as a point set.
    """

    mask = np.asarray(mask, dtype=bool)
    y, x = np.nonzero(mask)
    if len(x) == 0:
        eps = np.logspace(exp_from, exp_to, steps)
        return float("nan"), eps, np.zeros_like(eps)

    # Normalize coordinates to [0,1]
    x_n = (x - x.min()) / max(1, (x.max() - x.min()))
    y_n = (y - y.min()) / max(1, (y.max() - y.min()))
    pts = np.column_stack([x_n, y_n])

    eps_list = np.logspace(exp_from, exp_to, steps)
    Ns: list[int] = []
    for eps in eps_list:
        bins = int(np.ceil(1.0 / eps))
        bins = max(bins, 1)
        grid = np.floor(pts * bins).astype(int)
        grid[grid == bins] = bins - 1
        Ns.append(int(len(np.unique(grid, axis=0))))

    eps_arr = np.asarray(eps_list, dtype=float)
    Ns_arr = np.asarray(Ns, dtype=float)
    coeff = np.polyfit(np.log(1.0 / eps_arr), np.log(Ns_arr + 1e-9), 1)
    return float(coeff[0]), eps_arr, Ns_arr


def detect_dark_lane_mask(image: np.ndarray, *, config: DarkMaskConfig = DarkMaskConfig()) -> DarkMaskResult:
    """Detect dark-lane structures as a binary mask + watershed-separated labels.

    Parameters
    ----------
    image:
        2D grayscale image.

    Returns
    -------
    DarkMaskResult
        Includes the fused binary mask, watershed labels, skeleton mask, and summary metrics.
    """

    img_u = to_unit(np.asarray(image, dtype=float))
    height, width = img_u.shape

    # Step 1: enhanced preprocessing (invert and remove gradients on multiple scales)
    inv = 1.0 - img_u
    enhanced = inv.copy()
    for scale in config.background_scales:
        background = gaussian_filter(enhanced, sigma=float(scale))
        enhanced = enhanced - config.background_weight * background
    enhanced = to_unit(np.clip(enhanced, 0.0, None))

    # Step 2: multi-threshold detection + morphology
    selem = disk(int(config.morph_radius))
    combined = np.zeros_like(enhanced, dtype=bool)
    for i, thresh in enumerate(config.thresholds):
        local = enhanced > float(thresh)
        cleaned = opening(local, selem)
        cleaned = closing(cleaned, selem)
        min_size = int(config.min_size_base) * (i + 1)
        cleaned = remove_small_objects(cleaned, min_size=min_size)
        combined |= cleaned

    # Step 3: watershed-based segmentation
    distance = distance_transform_edt(combined)

    # Find local maxima-like seeds without relying on skimage.feature.peak_local_max,
    # to keep behavior close to the notebook and dependency surface minimal.
    flat_indices = np.argsort(distance.ravel())[::-1]
    coords = np.unravel_index(flat_indices, distance.shape)
    coords = np.column_stack([coords[0], coords[1]])  # (y, x)

    seeds = np.zeros_like(distance, dtype=bool)
    selected: list[tuple[int, int]] = []
    min_dist = float(config.min_seed_distance_px)

    for y, x in coords:
        if float(distance[y, x]) <= float(config.min_seed_peak):
            break
        if all(np.hypot(y - sy, x - sx) >= min_dist for sy, sx in selected):
            selected.append((int(y), int(x)))
            seeds[y, x] = True
            if len(selected) >= int(config.max_seeds):
                break

    markers = label(seeds)
    labels_ws = watershed(-distance, markers, mask=combined)

    # Step 4: metrics
    props = regionprops(labels_ws)
    areas = np.asarray([p.area for p in props], dtype=float)
    eccentricities = np.asarray([p.eccentricity for p in props], dtype=float)
    elongations = np.asarray(
        [
            (p.major_axis_length / p.minor_axis_length) if p.minor_axis_length > 0 else 1.0
            for p in props
        ],
        dtype=float,
    )

    skel = skeletonize(combined)
    D_mask, eps_m, Ns_m = boxcount_fractal_on_mask(combined)
    D_skel, eps_s, Ns_s = boxcount_fractal_on_mask(skel)

    metrics: dict[str, object] = {
        "image_size": {"width": int(width), "height": int(height)},
        "dark_area_fraction": float(np.mean(combined)),
        "num_dark_components": int(len(areas)),
        "component_areas": areas.tolist() if len(areas) else [],
        "mean_eccentricity": float(np.mean(eccentricities)) if len(eccentricities) else None,
        "mean_elongation": float(np.mean(elongations)) if len(elongations) else None,
        "watershed_seeds": int(len(selected)),
        "fractal_dimension_dark_mask": None if np.isnan(D_mask) else float(D_mask),
        "fractal_dimension_skeleton": None if np.isnan(D_skel) else float(D_skel),
        "fractal_boxcount_mask": {"eps": eps_m.tolist(), "box_counts": Ns_m.tolist()},
        "fractal_boxcount_skeleton": {"eps": eps_s.tolist(), "box_counts": Ns_s.tolist()},
        "config": asdict(config),
    }

    return DarkMaskResult(combined_mask=combined, labels_ws=labels_ws, skeleton=skel, metrics=metrics)


def detect_dark_lane_mask_from_file(
    image_path: str | Path,
    *,
    out_dir: str | Path | None = None,
    config: DarkMaskConfig = DarkMaskConfig(),
) -> DarkMaskResult:
    """Load an image file and compute the dark mask.

    If out_dir is provided, writes `improved_dark_detection.json` compatible summary.
    """

    image, _ = load_image_gray(image_path)
    res = detect_dark_lane_mask(image, config=config)

    if out_dir is not None:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "improved_dark_detection.json").write_text(
            json.dumps(res.metrics, indent=2),
            encoding="utf-8",
        )

    return res


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="amanogawa-dark",
        description="Detect Milky Way dark-lane structures (binary mask + morphology metrics)",
    )
    p.add_argument("--image", required=True, help="Path to input image (e.g., JPG)")
    p.add_argument("--out", required=True, help="Output directory (will be created)")
    p.add_argument(
        "--mask-png",
        default=None,
        help="Optional path to write a viewable mask PNG (default: <out>/dark_lane_mask.png)",
    )
    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    res = detect_dark_lane_mask_from_file(args.image, out_dir=out_dir)

    # Save a viewable PNG mask alongside the JSON.
    mask_path = Path(args.mask_png) if args.mask_png else (out_dir / "dark_lane_mask.png")
    try:
        from PIL import Image

        mask_png = (res.combined_mask.astype(np.uint8) * 255)
        Image.fromarray(mask_png).save(mask_path)
    except Exception:
        # Do not fail the entire CLI if PNG writing fails.
        pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
