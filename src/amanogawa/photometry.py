from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from .io import load_image_gray, to_unit


@dataclass(frozen=True)
class PhotometryConfig:
    aperture_radius_px: int = 2
    annulus_inner_radius_px: int = 6
    annulus_outer_radius_px: int = 10
    max_points: int = 15000


def _disc_mask_in_stamp(radius: int, stamp_radius: int) -> np.ndarray:
    """Boolean mask for a disk inside a (2*stamp_radius+1)^2 stamp."""

    radius = int(radius)
    stamp_radius = int(stamp_radius)
    if radius < 0 or stamp_radius < 0:
        raise ValueError("radius and stamp_radius must be >= 0")
    if radius > stamp_radius:
        raise ValueError("radius must be <= stamp_radius")
    y, x = np.ogrid[-stamp_radius : stamp_radius + 1, -stamp_radius : stamp_radius + 1]
    return (x * x + y * y) <= radius * radius


def _annulus_mask(r_in: int, r_out: int) -> np.ndarray:
    r_in = int(r_in)
    r_out = int(r_out)
    if r_in < 0 or r_out < 0 or r_out < r_in:
        raise ValueError("Invalid annulus radii")
    y, x = np.ogrid[-r_out : r_out + 1, -r_out : r_out + 1]
    rr2 = x * x + y * y
    return (rr2 <= r_out * r_out) & (rr2 >= r_in * r_in)


def aperture_photometry(
    image: np.ndarray,
    coords: pd.DataFrame,
    *,
    aperture_radius_px: int = 2,
    annulus_inner_radius_px: int = 6,
    annulus_outer_radius_px: int = 10,
    max_points: int = 15000,
    rng: np.random.Generator | None = None,
) -> pd.DataFrame:
    """Compute simple aperture photometry and instrumental magnitudes.

    Parameters
    ----------
    image:
        2D array (H, W).
    coords:
        DataFrame with columns ``x`` and ``y`` (pixels). Additional columns are preserved.

    Returns
    -------
    DataFrame
        Columns: ``x``, ``y``, ``flux``, ``mag``, and bookkeeping fields.

    Notes
    -----
    - Background is estimated as the *median* value in an annulus.
    - Instrumental magnitudes are computed as ``-2.5*log10(flux)``.
    """

    rng = rng or np.random.default_rng()

    if not {"x", "y"}.issubset(coords.columns):
        raise ValueError("coords must contain columns 'x' and 'y'")

    img = to_unit(np.asarray(image, dtype=float))
    height, width = img.shape

    df = coords.reset_index(drop=False).rename(columns={"index": "source_index"}).copy()

    if len(df) > max_points:
        idx = rng.choice(len(df), max_points, replace=False)
        df = df.iloc[np.sort(idx)].reset_index(drop=True)

    r_out = int(annulus_outer_radius_px)

    ap_mask = _disc_mask_in_stamp(aperture_radius_px, r_out)
    an_mask = _annulus_mask(annulus_inner_radius_px, r_out)

    ap_npix = int(np.sum(ap_mask))

    fluxes: list[float] = []
    mags: list[float] = []
    bkg_medians: list[float] = []
    valid: list[bool] = []

    for x, y in zip(df["x"].to_numpy(), df["y"].to_numpy()):
        xi = int(np.rint(x))
        yi = int(np.rint(y))

        x0 = xi - r_out
        x1 = xi + r_out + 1
        y0 = yi - r_out
        y1 = yi + r_out + 1

        if x0 < 0 or y0 < 0 or x1 > width or y1 > height:
            fluxes.append(float("nan"))
            mags.append(float("nan"))
            bkg_medians.append(float("nan"))
            valid.append(False)
            continue

        stamp = img[y0:y1, x0:x1]
        ap_vals = stamp[ap_mask]
        an_vals = stamp[an_mask]

        if an_vals.size == 0:
            fluxes.append(float("nan"))
            mags.append(float("nan"))
            bkg_medians.append(float("nan"))
            valid.append(False)
            continue

        bkg = float(np.median(an_vals))
        flux = float(np.sum(ap_vals) - bkg * ap_npix)

        if not np.isfinite(flux) or flux <= 0.0:
            fluxes.append(flux)
            mags.append(float("nan"))
            bkg_medians.append(bkg)
            valid.append(False)
            continue

        mag = float(-2.5 * np.log10(flux))

        fluxes.append(flux)
        mags.append(mag)
        bkg_medians.append(bkg)
        valid.append(True)

    out = df.copy()
    out["flux"] = fluxes
    out["mag"] = mags
    out["bkg_median"] = bkg_medians
    out["is_valid"] = valid
    return out


def assign_magnitude_bins(
    photometry_df: pd.DataFrame,
    *,
    labels: tuple[str, str, str] = ("Bright", "Mid", "Faint"),
) -> pd.DataFrame:
    """Assign tercile magnitude bins to a photometry table.

    Brighter sources have *smaller* instrumental magnitudes.

    Returns a copy with a new column ``mag_bin``.
    """

    if "mag" not in photometry_df.columns:
        raise ValueError("photometry_df must contain column 'mag'")

    df = photometry_df.copy()
    mag = df["mag"].to_numpy(dtype=float)
    ok = np.isfinite(mag)

    df["mag_bin"] = "Unknown"
    if int(np.sum(ok)) < 3:
        return df

    q1, q2 = np.quantile(mag[ok], [1.0 / 3.0, 2.0 / 3.0])

    # Smaller magnitude => brighter
    df.loc[ok & (df["mag"] <= q1), "mag_bin"] = labels[0]
    df.loc[ok & (df["mag"] > q1) & (df["mag"] <= q2), "mag_bin"] = labels[1]
    df.loc[ok & (df["mag"] > q2), "mag_bin"] = labels[2]
    return df


def assign_magnitude_bins_from_files(
    image_path: str | Path,
    coords_csv: str | Path,
    out_dir: str | Path,
    *,
    config: PhotometryConfig = PhotometryConfig(),
    seed: int = 42,
) -> Path:
    """Convenience helper: load image + coords, compute mags, and write magnitude bins CSV."""

    image, _ = load_image_gray(image_path)
    coords = pd.read_csv(coords_csv)

    rng = np.random.default_rng(seed)
    phot = aperture_photometry(
        image,
        coords,
        aperture_radius_px=config.aperture_radius_px,
        annulus_inner_radius_px=config.annulus_inner_radius_px,
        annulus_outer_radius_px=config.annulus_outer_radius_px,
        max_points=config.max_points,
        rng=rng,
    )
    phot = assign_magnitude_bins(phot)

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "magnitude_bins.csv"

    # Keep alignment by x/y; include source_index to help with joins.
    cols = [c for c in ["source_index", "x", "y", "flux", "mag", "mag_bin", "is_valid"] if c in phot.columns]
    phot[cols].to_csv(out_path, index=False)

    meta = {
        "aperture_radius_px": config.aperture_radius_px,
        "annulus_inner_radius_px": config.annulus_inner_radius_px,
        "annulus_outer_radius_px": config.annulus_outer_radius_px,
        "max_points": config.max_points,
        "seed": seed,
    }
    (out_dir / "photometry_metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return out_path


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="amanogawa-photometry", description="Aperture photometry + magnitude terciles")
    p.add_argument("--image", required=True, help="Path to input image")
    p.add_argument("--coords", required=True, help="CSV with columns x,y")
    p.add_argument("--out", required=True, help="Output directory")
    p.add_argument("--aperture-radius", type=int, default=2)
    p.add_argument("--annulus-inner", type=int, default=6)
    p.add_argument("--annulus-outer", type=int, default=10)
    p.add_argument("--max-points", type=int, default=15000)
    p.add_argument("--seed", type=int, default=42)
    return p


def main(argv: Optional[list[str]] = None) -> int:
    args = _build_parser().parse_args(argv)
    config = PhotometryConfig(
        aperture_radius_px=int(args.aperture_radius),
        annulus_inner_radius_px=int(args.annulus_inner),
        annulus_outer_radius_px=int(args.annulus_outer),
        max_points=int(args.max_points),
    )
    assign_magnitude_bins_from_files(args.image, args.coords, args.out, config=config, seed=int(args.seed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
