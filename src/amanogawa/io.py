from __future__ import annotations

from pathlib import Path

import numpy as np


def load_image_gray(path: str | Path) -> tuple[np.ndarray, tuple[int, int]]:
    """Load an image and return a grayscale array and (W, H).

    Parameters
    ----------
    path:
        Path to an image readable by Pillow.
    """

    # Pillow is an optional-but-expected runtime dependency for reading JPEG/PNG.
    from PIL import Image

    img = Image.open(Path(path)).convert("L")
    data = np.asarray(img).astype(float)
    height, width = data.shape
    return data, (width, height)


def to_unit(x: np.ndarray) -> np.ndarray:
    """Normalize array values to the [0, 1] range."""

    x = np.asarray(x, dtype=float)
    x_min = float(np.nanmin(x))
    x_max = float(np.nanmax(x))
    span = x_max - x_min
    if not np.isfinite(span) or span == 0:
        return np.zeros_like(x, dtype=float)
    return (x - x_min) / span

