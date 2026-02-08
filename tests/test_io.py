from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from amanogawa.io import load_image_gray


def test_load_image_gray_png(tmp_path: Path) -> None:
    img_path = tmp_path / "tiny.png"
    arr = np.array([[0, 255], [128, 64]], dtype=np.uint8)
    Image.fromarray(arr, mode="L").save(img_path)

    data, (width, height) = load_image_gray(img_path)
    assert (width, height) == (2, 2)
    assert data.shape == (2, 2)
    assert np.isclose(data[0, 1], 255.0)


def test_load_image_gray_heif_requires_plugin(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    heif_path = tmp_path / "sample.heif"
    heif_path.write_bytes(b"not-a-real-heif")

    monkeypatch.setattr("amanogawa.io._register_heif_opener", lambda: False)

    with pytest.raises(RuntimeError, match="pillow-heif"):
        load_image_gray(heif_path)
