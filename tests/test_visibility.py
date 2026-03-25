from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image

from amanogawa.detection import detect_stars_log
from amanogawa.visibility import analyze_visibility, write_visibility_outputs


def _visibility_test_image(height: int = 128, width: int = 128) -> np.ndarray:
    yy, xx = np.mgrid[0:height, 0:width]
    img = np.full((height, width), 18.0, dtype=float)

    band = np.exp(-0.5 * ((yy - (0.45 * xx + 28.0)) / 9.0) ** 2)
    img += 52.0 * band

    dark_lane = np.exp(-0.5 * ((yy - (0.45 * xx + 34.0)) / 4.0) ** 2)
    img -= 18.0 * dark_lane

    for (x0, y0, sigma, amp) in [
        (20, 28, 1.3, 180.0),
        (35, 40, 1.2, 170.0),
        (52, 50, 1.1, 165.0),
        (68, 60, 1.2, 175.0),
        (86, 69, 1.1, 160.0),
        (101, 79, 1.4, 185.0),
    ]:
        img += amp * np.exp(-0.5 * (((xx - x0) / sigma) ** 2 + ((yy - y0) / sigma) ** 2))

    return np.clip(img, 0.0, 255.0)


def _write_detection_artifacts(tmp_path: Path) -> tuple[Path, Path]:
    image = _visibility_test_image()
    image_path = tmp_path / "visibility.png"
    Image.fromarray(image.astype(np.uint8), mode="L").save(image_path)

    coords = detect_stars_log(image, threshold=0.04, max_sigma=6.0, num_sigma=12)
    coords_path = tmp_path / "star_coords.csv"
    coords.to_csv(coords_path, index=False)

    summary = {
        "image": image_path.name,
        "image_path": str(image_path),
        "width_px": int(image.shape[1]),
        "height_px": int(image.shape[0]),
        "num_stars": int(len(coords)),
        "coords_csv": str(coords_path),
        "detection": {"threshold": 0.04, "max_sigma": 6.0, "num_sigma": 12},
    }
    summary_path = tmp_path / "detection_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return image_path, summary_path


def test_analyze_visibility_is_deterministic_without_exif(tmp_path: Path) -> None:
    image_path, summary_path = _write_detection_artifacts(tmp_path)

    features_a, score_a = analyze_visibility(image_path=image_path, detection_summary_json=summary_path)
    features_b, score_b = analyze_visibility(image_path=image_path, detection_summary_json=summary_path)

    assert features_a["device_metadata"]["exif_available"] is False
    assert features_a["device_metadata"]["device_model"] is None
    assert score_a["visibility_score"] == score_b["visibility_score"]
    assert score_a["branch_scores"] == score_b["branch_scores"]
    assert 0.0 <= score_a["visibility_score"] <= 100.0


def test_write_visibility_outputs_writes_expected_json(tmp_path: Path) -> None:
    image_path, summary_path = _write_detection_artifacts(tmp_path)
    out_dir = tmp_path / "visibility"

    meta = write_visibility_outputs(image_path=image_path, detection_summary_json=summary_path, out_dir=out_dir)

    features = json.loads((out_dir / "visibility_features.json").read_text(encoding="utf-8"))
    score = json.loads((out_dir / "visibility_score.json").read_text(encoding="utf-8"))

    assert Path(meta["features_json"]).exists()
    assert Path(meta["score_json"]).exists()
    assert features["score_version"] == "visibility-v1"
    assert "raw_features" in features
    assert score["score_version"] == "visibility-v1"
    assert score["qc_status"] in {"fail", "warn", "pass"}
    assert isinstance(score["research_usable"], bool)


def test_write_visibility_outputs_handles_empty_detection_catalog(tmp_path: Path) -> None:
    image = np.zeros((64, 64), dtype=np.uint8)
    image_path = tmp_path / "empty.png"
    Image.fromarray(image, mode="L").save(image_path)

    coords_path = tmp_path / "star_coords.csv"
    pd.DataFrame(columns=["x", "y", "r"]).to_csv(coords_path, index=False)
    summary_path = tmp_path / "detection_summary.json"
    summary_path.write_text(
        json.dumps(
            {
                "image": image_path.name,
                "image_path": str(image_path),
                "width_px": 64,
                "height_px": 64,
                "num_stars": 0,
                "coords_csv": str(coords_path),
                "detection": {"threshold": 0.05, "max_sigma": 6.0, "num_sigma": 12},
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    out_dir = tmp_path / "visibility"
    write_visibility_outputs(image_path=image_path, detection_summary_json=summary_path, out_dir=out_dir)

    score = json.loads((out_dir / "visibility_score.json").read_text(encoding="utf-8"))
    assert score["visibility_score"] < 40.0
    assert score["qc_status"] == "fail"
