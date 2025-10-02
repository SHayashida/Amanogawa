# Amanogawa Analysis Outputs

This directory contains all analysis results from the Milky Way smartphone photography analysis project.

## Directory Structure

```
outputs/
├── band_analysis/           # Results from 01_band_analysis.ipynb
│   ├── figures/            # All visualization outputs
│   │   ├── correlation_function_detailed.png
│   │   ├── fractal_dimension_detailed.png
│   │   ├── magnitude_*.png
│   │   ├── milky_way_band_profile.png
│   │   ├── nearest_neighbor_*.png
│   │   ├── star_*.png
│   │   └── two_point_correlation.png
│   └── results/            # All numerical analysis results
│       ├── band_*.json
│       ├── complete_analysis_summary.json
│       ├── detection_summary.json
│       ├── magnitude_analysis.json
│       ├── sample_*.json
│       ├── spatial_statistics_detailed.json
│       └── threshold_sensitivity_analysis.csv
├── dark_morphology/         # Results from 02_dark_morphology.ipynb
│   ├── figures/            # Dark lane analysis visualizations
│   └── results/            # Dark morphology numerical results
│       ├── bulge_radial_profiles.csv
│       └── dark_morphology_summary.json
├── IMG_5991_star_coords.csv   # Shared star coordinates (used by both analyses)
├── sample_star_coords.csv     # Sample coordinates for testing
├── ANALYSIS_MASTER_SUMMARY.json  # Combined results summary
└── README.md               # This file
```

## File Descriptions

### Shared Data
- **IMG_5991_star_coords.csv**: Star coordinates detected from the main image
- **sample_star_coords.csv**: Sample coordinates for testing and validation
- **ANALYSIS_MASTER_SUMMARY.json**: Master summary combining all analysis results

### Band Analysis (01_band_analysis.ipynb)
Statistical analysis of stellar distribution patterns and Milky Way band structure:

**Figures:**
- Correlation functions and spatial statistics visualizations
- Fractal dimension analysis plots
- Magnitude distribution and correlation plots
- Star density maps and distributions
- Band profile measurements

**Results:**
- Detection parameters and star counts
- Spatial statistics (nearest neighbor, fractal dimension, 2-point correlation)
- Magnitude analysis and photometry results
- Band geometry measurements
- Parameter sensitivity analysis

### Dark Morphology (02_dark_morphology.ipynb)
Analysis of dark lane structure and bulge profiling:

**Results:**
- Dark nebula fractal dimensions
- Bulge radial profiles (surface brightness and star density)
- Morphological characteristics of dust lanes

## Usage

Each notebook generates its outputs in the corresponding subdirectory:
- Run `01_band_analysis.ipynb` → outputs saved to `band_analysis/`
- Run `02_dark_morphology.ipynb` → outputs saved to `dark_morphology/`

All paths are designed to work from the notebook directory using relative paths.

## Zenodo Publication

This structure is optimized for Zenodo dataset publication, with clear separation between different analysis types while maintaining shared data accessibility.
