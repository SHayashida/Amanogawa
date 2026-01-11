---
title: 'Amanogawa: Quantifying Milky Way clustering and band morphology from a single smartphone exposure'
tags:
  - Python
  - astronomy
  - astrophotography
  - spatial statistics
  - image processing
  - citizen science
authors:
  - name: Shunya Hayashida
    affiliation: 1
affiliations:
  - name: The Open University of Japan
    index: 1
date: 2026-01-11
bibliography: paper.bib
---

# Summary

Amanogawa is an open-source Python package and reproducible workflow for extracting quantitative, research-oriented measurements from a *single* wide-field smartphone long-exposure image of the Milky Way. From one image, Amanogawa detects candidate point sources, exports a coordinate catalogue, and computes spatial statistics that summarize clustering across scales. In parallel, it estimates the Milky Way band’s principal axis in image coordinates and measures the band width from perpendicular profiles, enabling consistent comparisons across images, sites, and acquisition settings.

The workflow supports both interactive notebook environments and command-line workflows, producing archival-friendly artefacts: star coordinate tables, threshold-sweep summaries, fitted band-width parameters, and publication-ready figures (CSV/JSON/PNG). By combining a core library with command-line style execution in notebooks/scripts, Amanogawa supports repeatable analyses where intermediate products can be inspected and reused.

# Statement of need

Consumer astrophotography and citizen-science observations have become widespread, but common tools for smartphone and hobbyist images primarily target aesthetic outputs (stacking, denoising, stretching) rather than transparent measurement and robustness diagnostics. Conversely, quantitative studies of Galactic structure and stellar clustering often rely on curated survey catalogues and pipelines that assume calibrated instruments and rich metadata. This creates a practical gap: single-exposure images are easy to collect and share, yet difficult to convert into defensible, reproducible summaries of spatial structure and band/dark-lane morphology.

Existing astronomical software such as SExtractor [@bertin1996] and astrometry.net [@lang2010astrometrynet] excel at source detection and astrometric calibration for calibrated telescope data, but are not optimized for the specific workflow of single smartphone exposures without prior astrometry. Photometric and morphological analysis tools like Photutils [@photutils1110] provide excellent building blocks but require users to assemble custom pipelines. Amanogawa fills this niche by providing an integrated, end-to-end workflow specifically designed for accessible, wide-field Milky Way imagery.

Amanogawa addresses this gap by providing an end-to-end pipeline that connects (1) source detection, (2) spatial statistics, and (3) Milky Way band geometry into a coherent and inspectable workflow. For source detection, Amanogawa uses Laplacian-of-Gaussian (LoG) blob detection [@lindeberg1998] (implemented via standard scientific Python image-processing tooling [@vanderwalt2014scikitimage]) and includes an explicit *threshold-sweep* routine that recomputes downstream metrics across a range of detection thresholds. This built-in sensitivity analysis helps users avoid over-interpreting results tied to a single parameter choice and provides a simple, teachable approach to robustness for non-specialists.

For clustering analysis, Amanogawa computes the two-point correlation function ξ(r) using a catalogue-based DD/RR estimator against repeated Poisson reference sets [@peebleshauser1974; @peebles1980], alongside nearest-neighbour distance distributions [@clark1954] and box-count scaling summaries (a compact proxy for multi-scale structure) [@mandelbrot1982]. The software also supports magnitude-stratified clustering by pairing simple aperture photometry with quantile binning, allowing users to compare ξ(r) across brightness groups without leaving the workflow [@photutils1110; @astropy2022].

For Milky Way band morphology, Amanogawa estimates the band principal axis from a source-density representation (via a PCA-style axis estimate) [@pedregosa2011sklearn] and measures the perpendicular band width by fitting smooth profile families (Gaussian and Lorentzian), capturing both core width and heavy-tail behaviour. When a plate scale is available (e.g., via WCS metadata used in the analysis), widths can be reported in angular units for cross-image comparison; otherwise, pixel units remain valid for within-image and relative analyses [@astropy2022; @lang2010astrometrynet].

While smartphone optics introduce geometric distortions, Amanogawa focuses on extracting internal relative consistencies. Future versions will support distortion correction via standard WCS headers if provided.

The workflow was demonstrated on a single 30 s smartphone exposure, producing stable summary outputs across a detection-threshold sweep (including consistently positive ξ(r) over the tested range) and band-width estimates on the order of 12–18° depending on the profile model. While these values are presented as an example of the pipeline’s quantitative outputs rather than as definitive astrophysical claims, they illustrate the type of reproducible, parameter-aware measurement Amanogawa enables. By packaging these steps into a reusable library and standardized artefacts, Amanogawa lowers the barrier for small research projects, classroom labs, and scalable citizen-science campaigns based on accessible, single-exposure imagery.
# Example Output

The figure below shows an example output from the star detection pipeline, with detected point sources overlaid on the original smartphone image:

![Star detection results showing detected point sources overlaid on a smartphone Milky Way image.](../outputs/sample_star_detection_overlay.png)

This visualization is automatically generated using the `--plot-output` flag in the `amanogawa-detect` CLI tool, providing immediate visual feedback on detection quality and enabling quick assessment of detection parameters.
# Acknowledgements
Amanogawa is built on the scientific Python ecosystem. The author thanks the maintainers and contributors of the open-source libraries that make this work possible, including NumPy [@harris2020numpy], SciPy [@virtanen2020scipy], scikit-image [@vanderwalt2014scikitimage], Astropy and Photutils [@astropy2022; @photutils1110], and the broader data/visualization stack used to produce the exported artefacts and figures.

# References
