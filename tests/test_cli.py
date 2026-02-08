"""CLI smoke tests to verify command-line interface functionality."""

import json
import subprocess
import sys

import numpy as np
import pandas as pd


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
