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

## Image Acquisition Guide (iPhone 16/17)

Amanogawa is optimized for analyzing single 30-second smartphone long-exposure images of the Milky Way. This section explains how to capture high-quality images using iPhone 16 or 17.

### Location Selection

**Dark sky site criteria:**
- **Bortle scale 4 or lower** (minimal light pollution)
- **Mountain peaks, rural countryside**, far from cities
- **New moon phase** (moonlight washes out faint structure)
- **Clear weather** (avoid haze; autumn/winter are often clearest)

**Online resources:**
- Light Pollution Map (lightpollutionmap.info)
- Stellarium Mobile (plan sky position and moon phase)
- Clear Sky Chart (cloud forecasts for astronomy sites)

### Equipment Setup

**Tripod selection:**
- Any smartphone tripod under $20–30 USD works fine
- **Stability matters more than quality** (wobbly = no 30-second exposure)
- Ensure ball head or pan-tilt moves smoothly without drift

**Pre-shoot checklist:**
- iPhone mounted and tightened securely
- Tripod leveled and stable on ground (test by gently pushing)
- No wind or vibration sources nearby (avoid traffic, machinery)
- Notifications silenced (airplane mode recommended 1 minute before)

### iPhone Camera Configuration

**Prepare your iPhone:**

1. **Open Camera app** → **Photo mode**
   - Avoid Portrait, Video, or other modes

2. **Disable Flash**
   - Tap lightning bolt icon → "Off"

3. **Disable Live Photo**
   - Tap the overlapping circles icon (top right) → "Off"
   - Live Photo can introduce noise/artifacts in long exposures

4. **Optional: Enable Grid** (Settings > Camera > Grid = "On")
   - Helps with framing and horizon leveling

### Exposure Capture Workflow

**Step 1: Compose the shot**

- Point iPhone at Milky Way (zenith if possible, or band orientation)
- Watch for yellow **moon icon** to appear in upper-left corner (Night mode activation)
- If no moon icon appears, lighting is too bright for long exposure (find darker location)

**Step 2: Set 30-second exposure**

1. Tap the **↓ icon** at the top of the screen to reveal control panel
2. Tap the **Night mode icon** (yellow moon symbol)
3. A slider appears; drag all the way to the right ("Max")
   - Initially shows ~10 seconds
   - If iPhone is completely stable, **automatically upgrades to 30 seconds** (watch the counter)
4. Confirm: "30s" should display in Night mode indicator

**Step 3: Trigger the exposure**

- Use **timer** (3-second or 10-second delay) to avoid hand vibration
  - Tap the timer icon (looks like a clock with curved arrow) → "3s" or "10s"
- Alternative: Use **Apple Watch** (if paired) to trigger shutter remotely
- Tap shutter button

**Step 4: Wait (do not move)**

- **30 seconds is a long time**; absolute stillness is critical
- Do not touch iPhone, tripod, or ground nearby
- Avoid any vibration (heavy footsteps, traffic, wind pushes)
- Wait for completion (camera will chime and show captured frame)

### Post-Capture Review & Processing

**Quick review:**

- Check **Photos app** immediately
- Look for:
  - Star trails or smearing (indicates vibration—try again with better stability)
  - Excessive noise (ISO too high—may need darker location)
  - Desired Milky Way structure visible (band, dark lanes, bright core)

**Optional post-processing:**

- Use **iOS Photos app** for minor adjustments (brightness, warmth)
- For serious editing:
  - **Lightroom Mobile** (free or subscription)
  - **Snapseed** (free; strong for night sky)
  - **Adobe Camera Raw** (works well for astrophotography)
- Typical edits:
  - Increase vibrance/saturation (stars pop more)
  - Lift shadows gently (reveal fainter stars)
  - Reduce highlights (if sun still low on horizon)
  - Avoid extreme compression artifacts

### Troubleshooting

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| No moon icon appears | Too bright / poor dark adaptation | Move to darker location; wait 20 min for eyes to adapt |
| Stops at 10 sec, doesn't reach 30 s | Tripod vibration | Tighten mount; use timer delay; test stability by pushing |
| Stars are trails, not points | Camera moved during capture | Use timer or Apple Watch; ensure tripod is locked |
| Image very noisy/grainy | High ISO in bad location | Move away from city lights; try full moon night (lower noise, trade-off in structure) |
| Milky Way too faint | Light pollution or poor contrast | Find darker site; post-process more aggressively |
| Image soft / blurry overall | Out of focus | Pre-focus on bright star or distant light before Night mode |

### Tips for Best Results

1. **Thermal stability**: Let iPhone cool in night air for 5–10 minutes (reduces thermal noise)
2. **Sky direction**: Point at **Milky Way band** (south in Northern Hemisphere, north in Southern; varies by season)
3. **Lens cleaning**: Wipe lens gently before each shot (fingerprints reduce contrast)
4. **Multiple exposures**: Take 3–5 exposures from same location; Amanogawa can process each independently
5. **Moon avoidance**: Bright moon can wash out faint structure even from "dark" sites; check lunar phase calendar

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

**Why this happens:**
- Photutils requires compiled dependencies (C/Fortran components)
- macOS: Xcode command-line tools not installed → compiler unavailable
- Windows: MSVC build tools may be missing
- All platforms: Outdated pip/setuptools can't handle wheels correctly

**Solutions (in order):**

1. **Install build tools (macOS/Linux):**
   ```bash
   # macOS: Install Xcode command-line tools
   xcode-select --install
   
   # Then retry installation
   pip install -e ".[dev]"
   ```

2. **Upgrade pip and setuptools:**
   ```bash
   python -m pip install --upgrade pip setuptools wheel
   pip install -e ".[dev]"
   ```

3. **Use Docker (clean environment verification):**
   See README.md "Docker-based installation" section for step-by-step instructions. This guarantees a reproducible build environment.

4. **If issue persists:**
   ```bash
   # Show detailed build logs
   pip install --verbose -e ".[dev]"
   
   # Share the output in a GitHub issue
   ```

**Note:** 
- Both `pip install -e ".[dev]"` and `pip install -e "."` should work after build tools are installed
- CI tests both configurations on Ubuntu and macOS; if your system fails, it's likely a local environment issue (see Docker option)

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
