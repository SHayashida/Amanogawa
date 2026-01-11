# Amanogawa User Guide

## Quick Reference

### What Amanogawa Does

Amanogawa extracts **quantitative measurements** from a single wide-field Milky Way image (including smartphone photos):

- **Star detection**: Identifies point sources using Laplacian-of-Gaussian blob detection
- **Spatial statistics**: Computes clustering metrics (two-point correlation, nearest-neighbor distances, fractal dimension)
- **Band geometry**: Estimates Milky Way band's principal axis and width
- **Dark morphology**: Detects and characterizes dark lanes (dust obscuration)

### Key Assumptions (for images without WCS/astrometry)

When analyzing images **without World Coordinate System (WCS) metadata**:

1. **Pixel coordinates only**: All measurements are in image pixel units unless you manually provide a plate scale
2. **Internal consistency**: Relative positions and clustering are valid; absolute sky coordinates require astrometry
3. **Flat field assumption**: No correction for optical distortion (e.g., smartphone lens distortion)
4. **Linear intensity**: Assumes intensity roughly correlates with stellar brightness (adequate for clustering analysis)

**Future versions** will support distortion correction via standard WCS headers if provided.

## Output Metrics Explained

### Star Detection (`amanogawa-detect`)

**Outputs:**
- `star_coords.csv`: Detected star positions (x, y) and size (r) in pixels
- `detection_summary.json`: Metadata (image size, detection parameters, star count)
- `threshold_sweep_summary.csv`: Star counts across detection thresholds (sensitivity analysis)

**Key metrics:**
- **N (star count)**: Total detected point sources at given threshold
- **threshold**: Blob detection sensitivity (lower = more detections, higher noise)

### Spatial Statistics (`amanogawa-stats`)

**Outputs:**
- Correlation function: `two_point_correlation.csv`
- Nearest-neighbor distances: `nearest_neighbor_distances.csv`
- Fractal dimension: `fractal_dimension.json`

**Key metrics:**
- **ξ(r)** (xi): Two-point correlation function - measures clustering excess over random distribution
  - ξ(r) > 0: Stars are clustered at scale r
  - ξ(r) = 0: Random distribution
  - ξ(r) < 0: Anti-correlated (under-dense)
- **NND**: Nearest-neighbor distance distribution - reveals characteristic clustering scales
- **D (fractal dimension)**: Box-counting dimension - quantifies multi-scale structure (D ≈ 2 for plane-filling, D < 2 for fractal)

### Band Geometry (`amanogawa-band`)

**Outputs:**
- `band_geometry.json`: Principal axis angle, band width estimates

**Key metrics:**
- **principal_angle** (degrees): Milky Way band orientation in image coordinates
- **width_gaussian** (pixels): FWHM assuming Gaussian profile perpendicular to band
- **width_lorentzian** (pixels): FWHM assuming Lorentzian (heavy-tailed) profile
- Convert to angular units: `width_degrees = width_pixels * plate_scale_arcsec_per_pixel / 3600`

### Dark Morphology (`amanogawa-dark`)

**Outputs:**
- `dark_lane_mask.png`: Binary mask of dark regions
- `dark_morphology_summary.json`: Dark lane statistics

**Key metrics:**
- **area_fraction**: Percentage of image covered by dark lanes
- **mean_intensity**: Average brightness of dark regions
- **perimeter**: Total edge length of dark lanes (indicates complexity)

## Common Issues and Solutions

### Problem: "No stars detected" or very few detections

**Causes:**
- Detection threshold too high
- Image too dark or low contrast
- Background too bright (light pollution, gradient)

**Solutions:**
```bash
# Try lower threshold (increase sensitivity)
amanogawa-detect --image INPUT.jpg --out outputs/ --threshold 0.02

# Run threshold sweep to find optimal value
amanogawa-detect --image INPUT.jpg --out outputs/ \
  --threshold-min 0.01 --threshold-max 0.10 --steps 20
```

### Problem: "Too many false detections" (noise, hot pixels)

**Causes:**
- Detection threshold too low
- High ISO noise
- Compression artifacts

**Solutions:**
```bash
# Increase threshold
amanogawa-detect --image INPUT.jpg --out outputs/ --threshold 0.08

# Check threshold_sweep_summary.csv to find the "knee" where counts stabilize
```

### Problem: Installation fails with "photutils build error"

**Solution:**
```bash
# Ensure build tools are installed (Mac)
xcode-select --install

# Or use Docker environment (see README Docker section)
```

### Problem: Band angle estimate seems incorrect

**Causes:**
- Insufficient star density in image
- Field of view doesn't include enough of the Milky Way band
- Strong background gradient

**Solutions:**
- Verify star distribution visually: `amanogawa-detect --plot-output`
- Use images with clear Milky Way band structure
- Manually inspect `band_roi_contrast_summary.json` for quality metrics

### Problem: Spatial statistics show no clustering (ξ(r) ≈ 0)

**Causes:**
- Uniform background with sparse stars
- Detection threshold captured mostly noise
- Image field too small for meaningful clustering analysis

**Solutions:**
- Verify detections are real stars (use `--plot-output`)
- Try different threshold values
- Ensure image contains dense stellar fields (e.g., Milky Way core region)

## Glossary

**Blob detection**: Image processing technique to identify compact, roughly circular features (stars)

**LoG (Laplacian of Gaussian)**: Specific blob detection algorithm combining smoothing and edge detection

**Two-point correlation function**: Statistical measure of how star positions deviate from randomness

**Fractal dimension**: Metric quantifying complexity and self-similarity across scales

**Principal axis**: Dominant orientation of elongated structures (Milky Way band direction)

**FWHM (Full Width at Half Maximum)**: Standard width measurement of a profile

**WCS (World Coordinate System)**: FITS header standard mapping pixel coordinates to sky coordinates

**Plate scale**: Angular size per pixel (arcseconds/pixel or degrees/pixel)

**Photometry**: Measurement of object brightness (flux)

**Aperture photometry**: Summing flux within a circular region around a star

## Tips for Best Results

### Image Selection

✅ **Good images:**
- Clear Milky Way band visible
- Minimal light pollution
- 10-30 second exposure (smartphone)
- Stars appear as distinct points (not trailed)
- Includes dense stellar regions

❌ **Challenging images:**
- Heavy light pollution
- Excessive noise/grain
- Star trailing (too long exposure or tracking issues)
- Heavy vignetting or uneven background

### Parameter Tuning

**Detection threshold** (`--threshold`):
- Start with 0.05
- Decrease (0.02-0.03) for faint fields
- Increase (0.08-0.10) for bright/noisy images
- Use threshold sweep to optimize

**Spatial statistics scales**:
- Default settings work for typical smartphone images
- For higher resolution: adjust `--rmax` and `--bins` in spatial_stats

**Band width fits**:
- Both Gaussian and Lorentzian are provided
- Lorentzian often better for real Milky Way profiles (extended wings)

## Further Reading

- **Notebooks**: See `notebooks/01_band_analysis.ipynb` for step-by-step examples
- **Paper**: Read `paper/paper.md` for methodology details
- **API Reference**: Check function docstrings in `src/amanogawa/`
