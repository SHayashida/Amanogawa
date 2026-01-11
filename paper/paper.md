---
title: 'Amanogawa: Reproducible quantification of Milky Way structure from single-exposure smartphone images'
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
  - name: Faculty of Liberal Arts, Department of Liberal Arts, The Open University of Japan
    index: 1
date: 2026-01-11
bibliography: paper.bib
---

# Summary

Amanogawa is an open-source, MIT-licensed Python package and reproducible workflow for extracting quantitative summaries of Milky Way structure from a single wide-field smartphone long-exposure image. The software bridges widely accessible astrophotography and transparent, inspectable measurements suitable for small research projects, education, and citizen-science studies.

From a single image, Amanogawa detects candidate point sources, exports coordinate catalogs, and computes spatial statistics that summarize stellar clustering across scales. In parallel, it estimates the principal axis of the Milky Way band in image coordinates and measures band width from perpendicular profiles, enabling consistent within-image and cross-image comparisons. These analyses are intentionally formulated to remain meaningful even in the absence of full astrometric calibration.

The workflow supports both interactive notebook use and a command-line interface, producing archival-friendly artifacts including star catalogs, threshold-sweep summaries, fitted band-width parameters, and diagnostic/publication-quality figures (CSV/JSON/PNG). By combining explicit robustness diagnostics with a standardized, end-to-end pipeline, Amanogawa enables repeatable quantitative analyses of accessible single-exposure imagery while keeping intermediate results transparent and reusable.

# Statement of need

Consumer astrophotography and citizen-science observations have become widespread, yet the scientific potential of smartphone-collected wide-field Milky Way images remains largely untapped. Common tools for smartphone and hobbyist images primarily target aesthetic outputs (stacking, denoising, stretching) rather than transparent measurement and robustness diagnostics, creating a barrier to quantitative citizen participation in astronomical observation and discovery. Conversely, quantitative studies of Galactic structure and stellar clustering often rely on curated survey catalogs and pipelines that assume calibrated instruments and rich metadata. This creates a practical gap: single-exposure images are easy to collect and share, yet difficult to convert into defensible, reproducible summaries of spatial structure and band/dark-lane morphology.

Existing astronomical software such as SExtractor [@bertin1996] and astrometry.net [@lang2010astrometrynet] excel at source detection and astrometric calibration for calibrated telescope data, but are not optimized for the specific workflow of single smartphone exposures without prior astrometry. Photometric and morphological analysis tools like Astropy and Photutils [@astropy2022; @photutils1110] provide excellent building blocks but require significant configuration and do not inherently address the **radiometric and geometric challenges of smartphone imagery** (non-linear sensor response, uneven illumination, and high-ISO noise). Amanogawa mitigates these through **per-image intensity normalization** (adaptive scaling for varying exposure conditions), **robust photometric estimation** (median-based background in annuli to suppress hot pixels and random noise), and **multi-scale sensitivity analysis** (detection threshold sweeps to quantify parameter dependence, multi-threshold background subtraction for dark-lane detection in non-uniform fields). By wrapping these adaptive routines into a cohesive, end-to-end pipeline, Amanogawa enables reproducible analysis without requiring detailed calibration knowledge.

Amanogawa addresses this gap by providing an end-to-end pipeline that connects (1) source detection, (2) spatial statistics, and (3) Milky Way band geometry into a coherent and inspectable workflow. For source detection, Amanogawa uses Laplacian-of-Gaussian (LoG) blob detection [@lindeberg1998] (implemented via standard scientific Python image-processing tooling [@vanderwalt2014scikitimage]) and includes an explicit *threshold-sweep* routine that recomputes downstream metrics across a range of detection thresholds. This built-in sensitivity analysis helps users avoid over-interpreting results tied to a single parameter choice and provides a simple, teachable approach to robustness for non-specialists.

For clustering analysis, Amanogawa computes the two-point correlation function $\xi(r)$ using a catalog-based DD/RR estimator against repeated Poisson reference sets [@peebleshauser1974; @peebles1980], alongside nearest-neighbour distance distributions [@clark1954]. The software also includes box-count scaling as a compact descriptive summary of multi-scale occupancy rather than as a formal estimator of fractal dimension, complementing $\xi(r)$ by providing an intuitive, coarse-grained view of spatial structure. The software additionally supports magnitude-stratified clustering by pairing simple aperture photometry with quantile binning, allowing users to compare $\xi(r)$ across brightness groups without leaving the workflow [@photutils1110; @astropy2022].

For Milky Way band morphology, Amanogawa estimates the band principal axis from the second-order moments of the source-density distribution, equivalent to a PCA on the density field [@pedregosa2011sklearn]. This choice provides a simple, rotation-invariant summary of the dominant elongation of the Milky Way band and avoids subjective, image-edge–based axis selection. The software then measures the perpendicular band width by fitting smooth profile families (Gaussian and Lorentzian), capturing both core width and heavy-tail behaviour. When a plate scale is available (e.g., via WCS metadata used in the analysis), widths can be reported in angular units for cross-image comparison; otherwise, pixel units remain valid for within-image and relative analyses [@astropy2022; @lang2010astrometrynet].

While smartphone optics introduce geometric distortions, Amanogawa focuses on extracting internal relative consistencies. Future versions will support distortion correction via standard WCS headers if provided.

The workflow was demonstrated on a single 30 s smartphone exposure, producing stable summary outputs across a detection-threshold sweep (including consistently positive $\xi(r)$ over the tested range) and band-width estimates on the order of 12–18° depending on the profile model. While these values are presented as an example of the pipeline’s quantitative outputs rather than as definitive astrophysical claims, they illustrate the type of reproducible, parameter-aware measurement Amanogawa enables. By packaging these steps into a reusable library and standardized artifacts, Amanogawa lowers the barrier for small research projects, classroom labs, and scalable citizen-science campaigns based on accessible, single-exposure imagery. The software is designed to encourage participation from non-specialists, enabling the democratization of wide-field Galactic observations and fostering community-driven scientific discovery.

# Example Output

The figure illustrates a representative diagnostic visualization generated by the pipeline; it is included here to demonstrate the type of artifact produced rather than to support a scientific claim.

![Star detection results showing detected point sources overlaid on a smartphone Milky Way image.](figures/sample_star_detection_overlay.png)

This visualization is automatically generated using the `--plot-output` flag in the `amanogawa-detect` CLI tool, providing immediate visual feedback on detection quality and enabling quick assessment of detection parameters.

# Acknowledgements
Amanogawa is built on the scientific Python ecosystem. The author thanks the maintainers and contributors of the open-source libraries that make this work possible, including NumPy [@harris2020numpy], SciPy [@virtanen2020scipy], scikit-image [@vanderwalt2014scikitimage], Astropy and Photutils [@astropy2022; @photutils1110], and the broader data/visualization stack used to produce the exported artifacts and figures.

The author welcomes and anticipates future contributions from citizen astronomers and community members who wish to share smartphone observations and join in collaborative analysis of wide-field Milky Way structure.

# AI usage disclosure

The following generative AI tools were used in the development and documentation of this work:

- **Tools/Models**: ChatGPT 5.2 Thinking, GitHub Copilot (Claude Haiku 4.5)
- **Where**: Code (e.g., function implementations, test generation), documentation (e.g., README, docstrings), and paper (e.g., phrasing, grammar review)
- **Nature of assistance**: Code generation, refactoring, documentation writing, proofreading, and test generation
- **Human review**: All AI-generated content was reviewed, validated, and verified by the author; final judgments on scientific claims, methodology, and correctness remain the author's responsibility

# References
