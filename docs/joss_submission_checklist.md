# Phase 1 JOSS Submission Checklist

This document consolidates the existing JOSS-related materials for Amanogawa.
Use it as the operational checklist for Phase 1.

This checklist has two purposes:

- confirm that Amanogawa is ready for software-focused review in JOSS,
- prevent scope drift or stronger scientific claims than the current software supports.

## Phase 1 objective

Submit Amanogawa to JOSS as a reproducible research software package and receive
review of the software design, documentation, packaging, testing, and artifact model.

Phase 1 is **not** for proving strong astrophysical claims.
The JOSS submission must stay aligned with the current scientific contract:

- single-image workflow,
- reproducible relative measurements,
- visibility v1 as an image-based relative visibility / analyzability score,
- no claim of absolute light pollution estimation or device-adjusted sky-quality inference.

## Guardrail check

Before submission, confirm all of the following:

- [ ] The JOSS paper describes Amanogawa as research software, not as a validated public sky-quality instrument.
- [ ] Visibility v1 is described as observation-based and limitation-aware.
- [ ] No README, paper, or reviewer guidance implies that low score means objectively poor sky quality.
- [ ] No document claims cross-device fairness, absolute sky brightness, or absolute light pollution estimation.
- [ ] All examples and figures are framed as workflow demonstrations unless explicitly validated otherwise.

## Repository and release readiness

Repo-backed materials already present:

- [x] Open-source license is present (`LICENSE`) and referenced from the repository.
- [x] Repository has a public code host and repository URL in `pyproject.toml` and `CITATION.cff`.
- [x] Zenodo DOI is present and consistent with the canonical DOI policy.
- [x] Citation metadata exists in `CITATION.cff`.
- [x] JOSS paper sources exist in `paper/paper.md` and `paper/paper.bib`.
- [x] CI exists and runs install, import, lint, tests, and JOSS PDF generation.
- [x] Install instructions exist for standard setup and Docker-based reviewer verification.
- [x] Reproducibility and validation docs exist.

Verify manually before submission:

- [ ] The GitHub default branch is the intended submission state.
- [ ] The release/tag associated with the Zenodo archive is the intended submission version.
- [ ] The archived Zenodo record resolves correctly and points to the correct repository snapshot.
- [ ] The repository has no accidental local-only files or generated metadata changes intended to be excluded.
- [ ] The version shown in `pyproject.toml`, `CITATION.cff`, and release metadata is consistent.

## Software quality and reviewer path

Repo-backed expectations:

- [x] `pip install -e ".[dev]"` is the primary documented reviewer path.
- [x] Import smoke test is covered in CI.
- [x] `pytest` is covered in CI.
- [x] `ruff check src tests` is covered in CI.
- [x] Reviewer quick verification commands are documented in `README.md`.
- [x] Docker-based clean-environment verification is documented.

Must re-run immediately before submission:

- [ ] Install from a fresh environment using the documented commands.
- [ ] Verify `import amanogawa` works outside the repo path assumptions.
- [ ] Run `pytest` and confirm all tests pass on the submission revision.
- [ ] Run `ruff check src tests` and confirm no violations.
- [ ] Run at least one documented CLI example successfully.
- [ ] Run `amanogawa-run` or `amanogawa-detect` on the sample image and confirm expected artifacts are generated.
- [ ] Confirm `run_manifest.json` and visibility outputs are written and readable.

## Documentation completeness

Repo-backed materials already present:

- [x] README includes statement of need, install, quick start, tests, citation, and reviewer verification.
- [x] User guide explains outputs and common failure modes.
- [x] Reproducibility guide explains deterministic controls and preserved artifacts.
- [x] Validation plan defines acceptance targets and change control.
- [x] Scientific assumptions are explicitly documented.
- [x] Minimum data spec documents visibility v1 semantics and non-claims.
- [x] Roadmap now documents the relationship between JOSS, methods paper, app, and future science phases.

Verify manually before submission:

- [ ] The README and paper use compatible terminology for the software’s purpose and limits.
- [ ] Installation instructions match the current package behavior exactly.
- [ ] Output file names documented in README and USER_GUIDE match actual CLI outputs.
- [ ] Visibility v1 language is consistent across README, USER_GUIDE, roadmap, and paper.
- [ ] No documentation overstates what can be inferred from one image.

## JOSS paper content

Repo-backed materials already present:

- [x] The paper has a title, summary, statement of need, example output, acknowledgements, AI disclosure, and references.
- [x] The paper states the software’s scope as reproducible quantitative analysis from single smartphone images.
- [x] The paper includes a software archive DOI.
- [x] The paper avoids presenting the example outputs as definitive astrophysical claims.

Verify manually before submission:

- [ ] The paper cleanly answers JOSS expectations: what the software does, why it is needed, and how it differs from related tools.
- [ ] The paper focuses on software contribution rather than trying to serve as the astronomy methods paper.
- [ ] All references cited in the text are present in `paper.bib`.
- [ ] The paper PDF builds successfully from the submission revision.
- [ ] The example figure renders correctly in the generated PDF.
- [ ] The wording around visibility v1 remains limitation-aware and does not imply validated environmental inference.

## Citation and archival integrity

Repo-backed materials already present:

- [x] Canonical Zenodo DOI is recorded in README and `paper/paper.md`.
- [x] `CITATION.cff` exists and points to the repository and software DOI.

Verify manually before submission:

- [ ] DOI-related files remain synchronized:
  - `README.md`
  - `README_ja.md`
  - `CITATION.cff`
  - `paper/paper.md`
- [ ] The preferred citation metadata is acceptable for the pre-publication JOSS state.
- [ ] After JOSS acceptance, update citation guidance to include the final JOSS DOI.

## Reviewer experience

Confirm the expected reviewer journey is smooth:

- [ ] A reviewer can identify what Amanogawa is from the repository landing page alone.
- [ ] A reviewer can install the package without needing notebook-specific steps.
- [ ] A reviewer can run one short command and see concrete outputs.
- [ ] A reviewer can find the statement of scientific limitations without hunting through the repo.
- [ ] A reviewer can understand which files are core software and which are demo notebooks.

## Submission operations

Manual JOSS submission tasks:

- [ ] Prepare the JOSS submission issue / form using the correct repository URL.
- [ ] Provide the archive DOI for the exact submission version.
- [ ] Provide the paper path if requested.
- [ ] Be ready to respond to packaging, docs, tests, and scope questions during review.
- [ ] Treat review comments as software-review feedback first, not as pressure to expand scientific claims.

## Exit criteria for Phase 1

Phase 1 is complete when:

- [ ] Amanogawa has been submitted to JOSS.
- [ ] The submission revision passes install, lint, tests, and documented CLI verification.
- [ ] The repository and paper consistently describe the current scope and limitations.
- [ ] The JOSS submission does not promise capabilities that belong to the later astronomy methods phase.

## After Phase 1

Once JOSS submission is complete, the next phase is:

- propose to the astronomy community what this framework can responsibly do,
- validate that framing with controlled data,
- only then open broad citizen-science participation through an app/platform.
