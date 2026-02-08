from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree


def _safe_mean(values: np.ndarray) -> float | None:
    arr = np.asarray(values, dtype=float)
    finite = arr[np.isfinite(arr)]
    if finite.size == 0:
        return None
    return float(np.mean(finite))


def _safe_std(values: np.ndarray) -> float | None:
    arr = np.asarray(values, dtype=float)
    finite = arr[np.isfinite(arr)]
    if finite.size == 0:
        return None
    return float(np.std(finite))


def _safe_median(values: np.ndarray) -> float | None:
    arr = np.asarray(values, dtype=float)
    finite = arr[np.isfinite(arr)]
    if finite.size == 0:
        return None
    return float(np.median(finite))


def _safe_min(values: np.ndarray) -> float | None:
    arr = np.asarray(values, dtype=float)
    finite = arr[np.isfinite(arr)]
    if finite.size == 0:
        return None
    return float(np.min(finite))


def _safe_max(values: np.ndarray) -> float | None:
    arr = np.asarray(values, dtype=float)
    finite = arr[np.isfinite(arr)]
    if finite.size == 0:
        return None
    return float(np.max(finite))


def nearest_neighbor_distances(points: np.ndarray) -> np.ndarray:
    """Nearest-neighbor distances for a 2D point set."""

    points = np.asarray(points, dtype=float)
    if len(points) == 0:
        return np.array([], dtype=float)
    tree = cKDTree(points)
    distances, _ = tree.query(points, k=min(2, len(points)))
    if len(points) == 1:
        return np.array([np.nan], dtype=float)
    return distances[:, 1]


def two_point_correlation_function(
    points: np.ndarray,
    width_px: int,
    height_px: int,
    r_bins: np.ndarray,
    *,
    max_points: int = 4000,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Two-point correlation function ξ(r) ≈ DD/RR − 1.

    Notes
    -----
    - ``DD`` counts *unique* point pairs (i<j) in each radial bin.
    - ``RR`` uses a Poisson reference expectation for a rectangular window.
    """

    rng = rng or np.random.default_rng()
    P = np.asarray(points, dtype=float)
    if len(P) == 0:
        r_centers = 0.5 * (r_bins[1:] + r_bins[:-1])
        return r_centers, np.full_like(r_centers, np.nan, dtype=float)

    if len(P) > max_points:
        idx = rng.choice(len(P), max_points, replace=False)
        P = P[idx]

    r_centers = 0.5 * (r_bins[1:] + r_bins[:-1])
    r_max = float(np.max(r_bins))

    # Data-data pairs (unique pairs within r_max)
    tree = cKDTree(P)
    pairs = tree.query_pairs(r_max, output_type="ndarray")
    if len(pairs) == 0:
        DD = np.zeros(len(r_centers), dtype=float)
    else:
        dxy = P[pairs[:, 0]] - P[pairs[:, 1]]
        d = np.sqrt(np.sum(dxy * dxy, axis=1))
        DD, _ = np.histogram(d, bins=r_bins)

    # Expected random pairs for unique-pair counting
    area = float(width_px) * float(height_px)
    density = len(P) / area
    annulus_areas = np.pi * (r_bins[1:] ** 2 - r_bins[:-1] ** 2)
    RR_expected = 0.5 * len(P) * density * annulus_areas

    xi = (DD / np.maximum(RR_expected, 1.0)) - 1.0
    return r_centers, xi


def boxcount_fractal_dimension(
    points: np.ndarray,
    width_px: int,
    height_px: int,
    *,
    exp_from: float = -1.0,
    exp_to: float = -2.2,
    steps: int = 10,
) -> tuple[float, np.ndarray, np.ndarray]:
    """Box-count fractal dimension on points normalized to [0,1]^2."""

    points = np.asarray(points, dtype=float)
    if len(points) == 0:
        eps = np.logspace(exp_from, exp_to, steps)
        return float("nan"), eps, np.zeros_like(eps)

    X = np.column_stack([points[:, 0] / float(width_px), points[:, 1] / float(height_px)])
    eps_list = np.logspace(exp_from, exp_to, steps)
    box_counts: list[int] = []

    for eps in eps_list:
        bins = int(np.ceil(1.0 / eps))
        bins = max(bins, 1)
        grid_coords = np.floor(X * bins).astype(int)
        grid_coords[grid_coords == bins] = bins - 1
        box_counts.append(int(len(np.unique(grid_coords, axis=0))))

    eps = np.asarray(eps_list, dtype=float)
    Ns = np.asarray(box_counts, dtype=float)
    coeffs = np.polyfit(np.log(1.0 / eps), np.log(Ns + 1e-9), 1)
    return float(coeffs[0]), eps, Ns


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="amanogawa-stats", description="Spatial statistics on star coordinates")
    p.add_argument("--coords", required=True, help="CSV with columns x,y")
    p.add_argument(
        "--magnitude-bins",
        default=None,
        help="Optional CSV with columns x,y and mag_bin (e.g., from photometry); writes magnitude_analysis.json",
    )
    p.add_argument("--out", required=True, help="Output directory")
    p.add_argument("--width", type=int, default=None, help="Image width in pixels (optional if in CSV metadata)")
    p.add_argument("--height", type=int, default=None, help="Image height in pixels")
    p.add_argument("--max-points", type=int, default=3500, help="Maximum sampled points for 2PCF (default: 3500)")
    p.add_argument("--seed", type=int, default=42, help="Random seed for deterministic sampling (default: 42)")
    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.coords)
    points = df[["x", "y"]].to_numpy(dtype=float)
    seed = int(args.seed)
    max_points = int(args.max_points)
    rng = np.random.default_rng(seed)

    # Empty coordinate tables are valid and should not crash the CLI.
    if len(points) == 0:
        width = int(args.width) if args.width is not None else 0
        height = int(args.height) if args.height is not None else 0
        payload = {
            "status": "no_detections",
            "image_size": {"width_px": width, "height_px": height},
            "sampling": {"seed": seed, "max_points": max_points},
            "nearest_neighbor": {"mean": None, "std": None, "median": None, "min": None, "max": None},
            "fractal_dimension": None,
            "fractal_boxcount": {"eps": [], "box_counts": []},
            "two_point_correlation": {"r_centers": [], "xi_values": [], "xi_mean": None, "xi_max": None},
        }
        (out_dir / "spatial_statistics_analysis.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

        if args.magnitude_bins:
            (out_dir / "magnitude_analysis.json").write_text(
                json.dumps({"status": "no_detections", "bins": {}}, indent=2),
                encoding="utf-8",
            )
        return 0

    # If width/height aren't provided, fall back to max coords + 1.
    width = int(args.width) if args.width else int(np.nanmax(points[:, 0]) + 1)
    height = int(args.height) if args.height else int(np.nanmax(points[:, 1]) + 1)

    nnd = nearest_neighbor_distances(points)
    D, eps, Ns = boxcount_fractal_dimension(points, width, height)

    r_max = min(width, height) / 3.0
    r_bins = np.linspace(5.0, r_max, 22)
    rc, xi = two_point_correlation_function(points, width, height, r_bins, max_points=max_points, rng=rng)

    payload = {
        "status": "ok",
        "image_size": {"width_px": width, "height_px": height},
        "sampling": {"seed": seed, "max_points": max_points},
        "nearest_neighbor": {
            "mean": _safe_mean(nnd),
            "std": _safe_std(nnd),
            "median": _safe_median(nnd),
            "min": _safe_min(nnd),
            "max": _safe_max(nnd),
        },
        "fractal_dimension": None if not np.isfinite(D) else float(D),
        "fractal_boxcount": {"eps": eps.tolist(), "box_counts": Ns.tolist()},
        "two_point_correlation": {
            "r_centers": rc.tolist(),
            "xi_values": xi.tolist(),
            "xi_mean": _safe_mean(xi),
            "xi_max": _safe_max(xi),
        },
    }
    (out_dir / "spatial_statistics_analysis.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if args.magnitude_bins:
        mdf = pd.read_csv(args.magnitude_bins)
        if not {"x", "y", "mag_bin"}.issubset(mdf.columns):
            raise ValueError("magnitude bins CSV must contain columns x,y,mag_bin")

        out: dict[str, object] = {"bins": {}}
        for bin_name, g in mdf.groupby("mag_bin"):
            g_points = g[["x", "y"]].to_numpy(dtype=float)
            rc_b, xi_b = two_point_correlation_function(
                g_points,
                width,
                height,
                r_bins,
                max_points=max_points,
                rng=rng,
            )
            out["bins"][str(bin_name)] = {
                "n_points": int(len(g_points)),
                "r_centers": rc_b.tolist(),
                "xi_values": xi_b.tolist(),
                "xi_mean": _safe_mean(xi_b),
            }

        (out_dir / "magnitude_analysis.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
