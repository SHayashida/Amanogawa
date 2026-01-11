"""CLI smoke tests to verify command-line interface functionality."""

import subprocess
import sys


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
