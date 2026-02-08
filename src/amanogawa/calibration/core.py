from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np


def _as_float_image(image: np.ndarray) -> np.ndarray:
    arr = np.asarray(image, dtype=float)
    if arr.ndim != 2:
        raise ValueError("calibration expects a 2D grayscale image")
    return arr


def _validate_map_shape(name: str, arr: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    a = np.asarray(arr, dtype=float)
    if a.shape != shape:
        raise ValueError(f"{name} shape mismatch: expected {shape}, got {a.shape}")
    return a


@dataclass
class CalibrationProfile:
    """Per-device/per-capture calibration profile.

    This is intentionally minimal for the P1 milestone. Fields can be gradually
    populated as calibration assets become available.
    """

    device_model: str
    dark_frame: np.ndarray | None = None
    flat_field: np.ndarray | None = None
    vignette_gain_map: np.ndarray | None = None
    vignette_strength: float = 0.0
    vignette_center_xy: tuple[float, float] | None = None
    vignette_power: float = 2.0

    def validate_for_shape(self, shape: tuple[int, int]) -> None:
        if self.dark_frame is not None:
            _validate_map_shape("dark_frame", self.dark_frame, shape)
        if self.flat_field is not None:
            _validate_map_shape("flat_field", self.flat_field, shape)
        if self.vignette_gain_map is not None:
            _validate_map_shape("vignette_gain_map", self.vignette_gain_map, shape)


@dataclass(frozen=True)
class DarkFrameSubtractor:
    """Subtract dark-current/background pattern from image."""

    clip_negative: bool = True

    def apply(
        self,
        image: np.ndarray,
        *,
        dark_frame: np.ndarray | None = None,
        profile: Optional[CalibrationProfile] = None,
    ) -> np.ndarray:
        img = _as_float_image(image)
        dark = dark_frame if dark_frame is not None else (profile.dark_frame if profile is not None else None)
        if dark is None:
            return img.copy()

        dark_arr = _validate_map_shape("dark_frame", dark, img.shape)
        out = img - dark_arr
        if self.clip_negative:
            out = np.clip(out, 0.0, None)
        return out


@dataclass(frozen=True)
class FlatFieldCorrector:
    """Correct pixel-response non-uniformity with flat-field map."""

    epsilon: float = 1e-6
    normalize_gain: bool = True
    clip_negative: bool = True

    def apply(
        self,
        image: np.ndarray,
        *,
        flat_field: np.ndarray | None = None,
        profile: Optional[CalibrationProfile] = None,
    ) -> np.ndarray:
        img = _as_float_image(image)
        flat = flat_field if flat_field is not None else (profile.flat_field if profile is not None else None)
        if flat is None:
            return img.copy()

        gain = _validate_map_shape("flat_field", flat, img.shape)
        if self.normalize_gain:
            finite_positive = gain[np.isfinite(gain) & (gain > 0.0)]
            if finite_positive.size == 0:
                raise ValueError("flat_field has no finite positive entries")
            gain = gain / float(np.median(finite_positive))

        out = img / np.maximum(gain, float(self.epsilon))
        if self.clip_negative:
            out = np.clip(out, 0.0, None)
        return out


@dataclass(frozen=True)
class VignettingCorrector:
    """Apply radial or map-based vignetting correction."""

    max_gain: float = 3.0
    clip_negative: bool = True

    @staticmethod
    def radial_gain_map(
        shape: tuple[int, int],
        *,
        strength: float,
        center_xy: tuple[float, float] | None = None,
        power: float = 2.0,
        max_gain: float = 3.0,
    ) -> np.ndarray:
        height, width = shape
        if height <= 0 or width <= 0:
            raise ValueError("shape must be positive")
        if max_gain < 1.0:
            raise ValueError("max_gain must be >= 1")

        if center_xy is None:
            cx = (width - 1) / 2.0
            cy = (height - 1) / 2.0
        else:
            cx, cy = float(center_xy[0]), float(center_xy[1])

        yy, xx = np.indices(shape)
        rr = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
        rmax = float(np.max(rr))
        if rmax <= 0.0:
            return np.ones(shape, dtype=float)

        rr_n = rr / rmax
        gain = 1.0 + float(strength) * np.power(rr_n, float(power))
        return np.clip(gain, 1.0, float(max_gain))

    def apply(
        self,
        image: np.ndarray,
        *,
        gain_map: np.ndarray | None = None,
        profile: Optional[CalibrationProfile] = None,
    ) -> np.ndarray:
        img = _as_float_image(image)

        if gain_map is not None:
            gain = _validate_map_shape("gain_map", gain_map, img.shape)
        elif profile is not None and profile.vignette_gain_map is not None:
            gain = _validate_map_shape("vignette_gain_map", profile.vignette_gain_map, img.shape)
        elif profile is not None and float(profile.vignette_strength) != 0.0:
            gain = self.radial_gain_map(
                img.shape,
                strength=float(profile.vignette_strength),
                center_xy=profile.vignette_center_xy,
                power=float(profile.vignette_power),
                max_gain=float(self.max_gain),
            )
        else:
            return img.copy()

        out = img * gain
        if self.clip_negative:
            out = np.clip(out, 0.0, None)
        return out


def apply_calibration_pipeline(
    image: np.ndarray,
    *,
    profile: CalibrationProfile,
    dark_subtractor: DarkFrameSubtractor | None = None,
    flat_corrector: FlatFieldCorrector | None = None,
    vignette_corrector: VignettingCorrector | None = None,
) -> np.ndarray:
    """Apply dark/flat/vignetting corrections in sequence."""

    img = _as_float_image(image)
    profile.validate_for_shape(img.shape)

    dark_subtractor = dark_subtractor or DarkFrameSubtractor()
    flat_corrector = flat_corrector or FlatFieldCorrector()
    vignette_corrector = vignette_corrector or VignettingCorrector()

    out = dark_subtractor.apply(img, profile=profile)
    out = flat_corrector.apply(out, profile=profile)
    out = vignette_corrector.apply(out, profile=profile)
    return out
