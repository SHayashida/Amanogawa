"""CLI smoke tests to verify command-line interface functionality."""

import json
import subprocess
import sys

import numpy as np
import pandas as pd
from PIL import Image


def test_detect_help():
    """Test that amanogawa-detect --help runs without error."""
    result = subprocess.run(
        [sys.executable, "-m", "amanogawa.detection", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "amanogawa-detect" in result.stdout or "usage" in result.stdout.lower()


def test_stats_help():
    """Test that amanogawa-stats --help runs without error."""
    result = subprocess.run(
        [sys.executable, "-m", "amanogawa.spatial_stats", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()


def test_band_help():
    """Test that amanogawa-band --help runs without error."""
    result = subprocess.run(
        [sys.executable, "-m", "amanogawa.band_geometry", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()


def test_dark_help():
    """Test that amanogawa-dark --help runs without error."""
    result = subprocess.run(
        [sys.executable, "-m", "amanogawa.dark_morphology", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()


def test_run_help():
    """Test that amanogawa-run --help runs without error."""
    result = subprocess.run(
        [sys.executable, "-m", "amanogawa.run", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "amanogawa-run" in result.stdout or "usage" in result.stdout.lower()


def test_fits_export_help():
    """Test that amanogawa-fits-export --help runs without error."""
    result = subprocess.run(
        [sys.executable, "-m", "amanogawa.fits_export", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "amanogawa-fits-export" in result.stdout or "usage" in result.stdout.lower()


def test_run_single_image_executes_full_pipeline(tmp_path) -> None:
    image_path = tmp_path / "frame.png"
    out_dir = tmp_path / "run_out"

    arr = np.zeros((64, 64), dtype=np.uint8)
    arr[14, 18] = 255
    arr[31, 29] = 220
    arr[50, 45] = 210
    Image.fromarray(arr, mode="L").save(image_path)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "amanogawa.run",
            "--image",
            str(image_path),
            "--out",
            str(out_dir),
            "--threshold",
            "0.2",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0

    manifest = json.loads((out_dir / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "ok"
    assert manifest["num_images"] == 1

    image_payload = manifest["images"][0]
    slug = image_payload["slug"]
    assert (out_dir / slug / "detection" / "detection_summary.json").exists()
    assert (out_dir / slug / "spatial_stats" / "spatial_statistics_analysis.json").exists()
    assert (out_dir / slug / "band_geometry" / "band_geometry_analysis.json").exists()
    assert (out_dir / slug / "dark_morphology" / "improved_dark_detection.json").exists()


def test_run_resume_skips_existing_outputs(tmp_path) -> None:
    image_path = tmp_path / "frame.png"
    out_dir = tmp_path / "run_out"

    arr = np.zeros((64, 64), dtype=np.uint8)
    arr[12, 20] = 255
    arr[30, 35] = 230
    Image.fromarray(arr, mode="L").save(image_path)

    cmd = [
        sys.executable,
        "-m",
        "amanogawa.run",
        "--image",
        str(image_path),
        "--out",
        str(out_dir),
        "--threshold",
        "0.2",
    ]
    first = subprocess.run(cmd, capture_output=True, text=True)
    assert first.returncode == 0

    second = subprocess.run(cmd + ["--resume"], capture_output=True, text=True)
    assert second.returncode == 0

    manifest = json.loads((out_dir / "run_manifest.json").read_text(encoding="utf-8"))
    image_payload = manifest["images"][0]
    statuses = {name: step["status"] for name, step in image_payload["steps"].items()}
    assert statuses == {"detect": "skipped", "stats": "skipped", "band": "skipped", "dark": "skipped"}


def test_run_image_dir_processes_all_images(tmp_path) -> None:
    image_dir = tmp_path / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    out_dir = tmp_path / "run_batch"

    arr = np.zeros((48, 48), dtype=np.uint8)
    arr[10, 12] = 255
    arr[25, 20] = 220
    Image.fromarray(arr, mode="L").save(image_dir / "a.png")
    Image.fromarray(arr, mode="L").save(image_dir / "b.jpg")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "amanogawa.run",
            "--image-dir",
            str(image_dir),
            "--out",
            str(out_dir),
            "--threshold",
            "0.2",
            "--skip-dark",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0

    manifest = json.loads((out_dir / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "ok"
    assert manifest["num_images"] == 2

    for slug in ("a_png", "b_jpg"):
        assert (out_dir / slug / "detection" / "detection_summary.json").exists()
        assert (out_dir / slug / "spatial_stats" / "spatial_statistics_analysis.json").exists()
        assert (out_dir / slug / "band_geometry" / "band_geometry_analysis.json").exists()


def test_detect_image_dir_processes_all_images(tmp_path) -> None:
    image_dir = tmp_path / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    out_dir = tmp_path / "out_batch"

    arr = np.zeros((32, 32), dtype=np.uint8)
    arr[10, 10] = 255
    arr[22, 19] = 200
    Image.fromarray(arr, mode="L").save(image_dir / "a.png")
    Image.fromarray(arr, mode="L").save(image_dir / "b.jpg")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "amanogawa.detection",
            "--image-dir",
            str(image_dir),
            "--out",
            str(out_dir),
            "--threshold",
            "0.2",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0

    payload = json.loads((out_dir / "batch_detection_summary.json").read_text(encoding="utf-8"))
    assert payload["status"] == "ok"
    assert payload["num_images"] == 2

    for folder in ("a_png", "b_jpg"):
        assert (out_dir / folder / "star_coords.csv").exists()
        assert (out_dir / folder / "detection_summary.json").exists()


def test_stats_empty_coords_returns_no_detections(tmp_path) -> None:
    """Empty coordinate CSV should return status=no_detections, not crash."""
    coords = tmp_path / "coords_empty.csv"
    coords.write_text("x,y\n", encoding="utf-8")
    out_dir = tmp_path / "out_stats_empty"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "amanogawa.spatial_stats",
            "--coords",
            str(coords),
            "--out",
            str(out_dir),
            "--seed",
            "7",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0

    payload = json.loads((out_dir / "spatial_statistics_analysis.json").read_text(encoding="utf-8"))
    assert payload["status"] == "no_detections"
    assert payload["sampling"]["seed"] == 7


def test_band_empty_coords_returns_no_detections(tmp_path) -> None:
    """Empty coordinate CSV should return status=no_detections, not crash."""
    coords = tmp_path / "coords_empty.csv"
    coords.write_text("x,y\n", encoding="utf-8")
    out_dir = tmp_path / "out_band_empty"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "amanogawa.band_geometry",
            "--coords",
            str(coords),
            "--out",
            str(out_dir),
            "--width",
            "100",
            "--height",
            "100",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0

    payload = json.loads((out_dir / "band_geometry_analysis.json").read_text(encoding="utf-8"))
    assert payload["status"] == "no_detections"


def test_stats_cli_is_deterministic_with_seed(tmp_path) -> None:
    """Same input+seed should produce identical JSON outputs."""
    rng = np.random.default_rng(0)
    points = rng.random((250, 2))
    points[:, 0] *= 300.0
    points[:, 1] *= 200.0

    coords = tmp_path / "coords.csv"
    pd.DataFrame(points, columns=["x", "y"]).to_csv(coords, index=False)

    out1 = tmp_path / "out1"
    out2 = tmp_path / "out2"

    cmd = [
        sys.executable,
        "-m",
        "amanogawa.spatial_stats",
        "--coords",
        str(coords),
        "--out",
        "",  # placeholder replaced below
        "--width",
        "300",
        "--height",
        "200",
        "--seed",
        "123",
        "--max-points",
        "100",
    ]

    cmd1 = cmd.copy()
    cmd1[cmd1.index("--out") + 1] = str(out1)
    cmd2 = cmd.copy()
    cmd2[cmd2.index("--out") + 1] = str(out2)

    result1 = subprocess.run(cmd1, capture_output=True, text=True)
    result2 = subprocess.run(cmd2, capture_output=True, text=True)

    assert result1.returncode == 0
    assert result2.returncode == 0
    text1 = (out1 / "spatial_statistics_analysis.json").read_text(encoding="utf-8")
    text2 = (out2 / "spatial_statistics_analysis.json").read_text(encoding="utf-8")
    assert text1 == text2
