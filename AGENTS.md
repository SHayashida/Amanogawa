# Amanogawa agent memory (minimal)

## Source of truth
- Scientific/core implementation lives in `src/amanogawa/`.
- Do not add core scientific logic directly in notebooks.
- Keep notebooks as thin demo wrappers (web/Colab friendly) that call `amanogawa.*` APIs.

## Notebooks policy
- Notebook outputs should be written under `outputs/notebooks/<notebook_name>/`.
- `notebooks/03_astronomical_validity.ipynb` should consume `amanogawa-run` artifacts (`outputs/run/run_manifest.json`).

## Generated metadata policy
- `src/amanogawa.egg-info/*` is generated metadata from packaging/install steps.
- Do not commit routine/local-only changes in `PKG-INFO`, `SOURCES.txt`, `entry_points.txt`.
- If project policy requires tracked egg-info updates, update all related files together in one intentional release-oriented commit.

## DOI consistency policy
- Canonical project DOI: `10.5281/zenodo.18213564`.
- If DOI-related text is changed, keep these files synchronized:
  - `README.md`
  - `README_ja.md`
  - `CITATION.cff`
  - `paper/paper.md`
