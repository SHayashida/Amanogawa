from __future__ import annotations

from pathlib import Path

import numpy as np


def _register_heif_opener() -> bool:
    """Register HEIF/HEIC support for Pillow if pillow-heif is available."""
    try:
        import pillow_heif
    except ImportError:
        return False

    pillow_heif.register_heif_opener()
    return True


def _is_heif_path(path: Path) -> bool:
    return path.suffix.lower() in {".heif", ".heic", ".hif"}


def load_image_gray(path: str | Path) -> tuple[np.ndarray, tuple[int, int]]:
    """Load an image and return a grayscale array and (W, H).

    Parameters
    ----------
    path:
        Path to an image readable by Pillow.
    """

    # Pillow is the core image reader. HEIF/HEIC additionally needs pillow-heif.
    from PIL import Image, UnidentifiedImageError

    image_path = Path(path)
    if _is_heif_path(image_path) and not _register_heif_opener():
        raise RuntimeError(
            "HEIF/HEIC input requires optional dependency 'pillow-heif'. "
            "Install with: pip install pillow-heif"
        )

    try:
        img = Image.open(image_path).convert("L")
    except UnidentifiedImageError as exc:
        # Retry once after HEIF plugin registration, then raise a helpful message.
        if _register_heif_opener():
            try:
                img = Image.open(image_path).convert("L")
            except UnidentifiedImageError:
                raise RuntimeError(f"Unsupported or unreadable image format: {image_path}") from exc
        else:
            raise RuntimeError(f"Unsupported or unreadable image format: {image_path}") from exc

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
