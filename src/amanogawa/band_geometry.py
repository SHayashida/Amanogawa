from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit


def pca_principal_axis(points: np.ndarray, width_px: int, height_px: int, *, bins_x: int = 60) -> tuple[float, tuple[float, float], float]:
    """PCA on a density-weighted 2D histogram.

    Returns
    -------
    angle_deg, (cx, cy), axis_ratio
    """

    points = np.asarray(points, dtype=float)
    bins_y = int(bins_x * height_px / width_px)

    hist, xedges, yedges = np.histogram2d(
        points[:, 0],
        points[:, 1],
        bins=[bins_x, bins_y],
        range=[[0, width_px], [0, height_px]],
    )

    xc = 0.5 * (xedges[1:] + xedges[:-1])
    yc = 0.5 * (yedges[1:] + yedges[:-1])
    XX, YY = np.meshgrid(xc, yc, indexing="xy")
    w = hist.T

    xw = float(np.average(XX, weights=w))
    yw = float(np.average(YY, weights=w))
    dx = XX - xw
    dy = YY - yw

    Cxx = float(np.average(dx * dx, weights=w))
    Cxy = float(np.average(dx * dy, weights=w))
    Cyy = float(np.average(dy * dy, weights=w))
    C = np.array([[Cxx, Cxy], [Cxy, Cyy]], dtype=float)

    eigenvals, eigenvecs = np.linalg.eig(C)
    idx = int(np.argmax(eigenvals))
    principal_vec = eigenvecs[:, idx]
    angle_deg = float(math.degrees(math.atan2(float(principal_vec[1]), float(principal_vec[0]))))

    sorted_vals = np.sort(eigenvals)
    axis_ratio = float(math.sqrt(sorted_vals[0] / sorted_vals[1])) if sorted_vals[1] > 0 else 1.0
    return angle_deg, (xw, yw), axis_ratio


def rotate_xy(x: np.ndarray, y: np.ndarray, *, center: tuple[float, float], angle_deg: float) -> tuple[np.ndarray, np.ndarray]:
    """Rotate coordinates around center by angle_deg."""

    th = math.radians(angle_deg)
    cx, cy = center
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    xr = (x - cx) * math.cos(th) + (y - cy) * math.sin(th)
    yr = -(x - cx) * math.sin(th) + (y - cy) * math.cos(th)
    return xr, yr


def gaussian_with_background(x: np.ndarray, amplitude: float, center: float, sigma: float, background: float) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    sigma = float(sigma) if sigma != 0 else 1e-9
    return amplitude * np.exp(-0.5 * ((x - center) / sigma) ** 2) + background


def lorentzian_with_background(x: np.ndarray, amplitude: float, center: float, gamma: float, background: float) -> np.ndarray:
    x = np.asarray(x, dtype=float)
    gamma = float(gamma) if gamma != 0 else 1e-9
    return amplitude * (gamma**2) / ((x - center) ** 2 + gamma**2) + background


@dataclass(frozen=True)
class BandWidthFit:
    y_centers: list[float]
    density_profile: list[float]
    angle_deg: float
    center_px: tuple[float, float]
    axis_ratio: float
    gaussian_fwhm_px: float | None
    lorentzian_fwhm_px: float | None
    empirical_fwhm_px: float


def band_density_profile(points: np.ndarray, *, center: tuple[float, float], angle_deg: float, nbins: int = 200) -> tuple[np.ndarray, np.ndarray]:
    """Compute a 1D star-density profile perpendicular to the principal axis."""

    points = np.asarray(points, dtype=float)
    _, y_rot = rotate_xy(points[:, 0], points[:, 1], center=center, angle_deg=angle_deg)
    hist, edges = np.histogram(y_rot, bins=nbins)
    centers = 0.5 * (edges[1:] + edges[:-1])
    return centers, hist.astype(float)


def _half_crossing(centers: np.ndarray, profile: np.ndarray, *, peak_idx: int, half_max: float, direction: int) -> float:
    i = int(peak_idx)
    while 0 <= i + direction < len(profile) and profile[i + direction] > half_max:
        i += direction
    j = i + direction
    if j < 0 or j >= len(profile):
        return float(centers[i])
    x1, y1 = float(centers[i]), float(profile[i])
    x2, y2 = float(centers[j]), float(profile[j])
    if abs(y2 - y1) < 1e-12:
        return x1
    return x1 + (half_max - y1) * (x2 - x1) / (y2 - y1)


def fit_band_width(y_centers: np.ndarray, density_profile: np.ndarray) -> tuple[float | None, float | None, float]:
    """Fit Gaussian and Lorentzian width (FWHM) plus empirical FWHM."""

    y_centers = np.asarray(y_centers, dtype=float)
    prof = np.asarray(density_profile, dtype=float)
    if len(prof) == 0:
        return None, None, float("nan")

    peak_idx = int(np.argmax(prof))
    peak_y = float(y_centers[peak_idx])
    peak_value = float(prof[peak_idx])
    background = float(np.percentile(prof, 10))

    # Empirical FWHM around peak
    half_max = background + 0.5 * (peak_value - background)
    left = _half_crossing(y_centers, prof, peak_idx=peak_idx, half_max=half_max, direction=-1)
    right = _half_crossing(y_centers, prof, peak_idx=peak_idx, half_max=half_max, direction=+1)
    empirical = float(right - left)

    # Fit models
    gauss_fwhm: float | None = None
    lorentz_fwhm: float | None = None

    try:
        p0 = [max(1.0, peak_value - background), peak_y, max(1.0, 0.25 * empirical), background]
        popt, _ = curve_fit(gaussian_with_background, y_centers, prof, p0=p0, maxfev=20000)
        sigma = float(abs(popt[2]))
        gauss_fwhm = float(2.0 * math.sqrt(2.0 * math.log(2.0)) * sigma)
    except Exception:
        gauss_fwhm = None

    try:
        p0 = [max(1.0, peak_value - background), peak_y, max(1.0, 0.25 * empirical), background]
        popt, _ = curve_fit(lorentzian_with_background, y_centers, prof, p0=p0, maxfev=20000)
        gamma = float(abs(popt[2]))
        lorentz_fwhm = float(2.0 * gamma)
    except Exception:
        lorentz_fwhm = None

    return gauss_fwhm, lorentz_fwhm, empirical


def analyze_band_geometry(points: np.ndarray, width_px: int, height_px: int, *, bins_x: int = 60, nbins_profile: int = 200) -> BandWidthFit:
    angle_deg, center, axis_ratio = pca_principal_axis(points, width_px, height_px, bins_x=bins_x)
    y_centers, density_profile = band_density_profile(points, center=center, angle_deg=angle_deg, nbins=nbins_profile)
    gauss_fwhm, lorentz_fwhm, empirical = fit_band_width(y_centers, density_profile)
    return BandWidthFit(
        y_centers=y_centers.tolist(),
        density_profile=density_profile.tolist(),
        angle_deg=float(angle_deg),
        center_px=center,
        axis_ratio=float(axis_ratio),
        gaussian_fwhm_px=gauss_fwhm,
        lorentzian_fwhm_px=lorentz_fwhm,
        empirical_fwhm_px=float(empirical),
    )


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="amanogawa-band", description="Band geometry (PCA axis + width fit)")
    p.add_argument("--coords", required=True, help="CSV with columns x,y")
    p.add_argument("--out", required=True, help="Output directory")
    p.add_argument("--width", type=int, required=True)
    p.add_argument("--height", type=int, required=True)
    p.add_argument("--bins-x", type=int, default=60)
    p.add_argument("--profile-bins", type=int, default=200)
    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(args.coords)
    points = df[["x", "y"]].to_numpy()

    fit = analyze_band_geometry(points, int(args.width), int(args.height), bins_x=int(args.bins_x), nbins_profile=int(args.profile_bins))
    payload = {
        "principal_axis": {"angle_deg": fit.angle_deg, "center_px": [float(fit.center_px[0]), float(fit.center_px[1])], "axis_ratio": fit.axis_ratio},
        "band_width_measurements": {
            "gaussian_fwhm_px": fit.gaussian_fwhm_px,
            "lorentzian_fwhm_px": fit.lorentzian_fwhm_px,
            "empirical_fwhm_px": fit.empirical_fwhm_px,
        },
        "profile": {"y_centers": fit.y_centers, "density": fit.density_profile},
    }
    (out_dir / "band_geometry_analysis.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
