# Amanogawa Roadmap

This document is the single roadmap reference for Amanogawa.
It defines the mission, scientific guardrails, phase order, and exit criteria
for future development.

When starting a new phase, return to this document first.

## Mission

Enable anyone to contribute to science from a single smartphone sky photo,
while keeping scientific claims transparent, reproducible, and appropriately limited.

## Core principle

Amanogawa must move in a straight line toward the mission above.

This means:

- lower participation cost without weakening scientific traceability,
- prefer reproducible relative measurements over overstated absolute claims,
- separate what the image shows from what the sky is,
- keep notebooks, apps, and papers aligned with the same core scientific contract.

## Scientific guardrails

These rules must be treated as non-optional constraints.

### What Visibility v1 can claim

Visibility v1 can claim:

- image-based relative visibility / analyzability,
- whether a submitted image contains usable evidence for downstream analysis,
- relative differences within controlled settings,
- reproducible internal features derived from one smartphone image.

### What Visibility v1 cannot claim

Visibility v1 must not be used to claim:

- absolute sky brightness,
- absolute light pollution level,
- device-adjusted comparability,
- calibrated photometry,
- cross-device fairness,
- definitive astrophysical conclusions from a single image,
- strong environmental conclusions from score alone.

### Interpretation rule

Low score means:

- the submitted image is weak evidence,

not:

- the sky at that site is definitively poor.

Possible causes include device limits, camera-app processing, blur, haze, clouds,
framing, exposure, and bright background.

### Analysis rule

Do not add analyses that are easy to compute but scientifically unclear.

Any new metric or derived score must answer all of the following:

1. What observable does it summarize?
2. What scientific or operational decision does it support?
3. What are its known failure modes?
4. What can it not be interpreted as?
5. How will it be validated?

If these are not clear, the metric should not be added.

### Publication rule

Do not make stronger claims in downstream papers, app UI, dashboards, or outreach
than are supported by the current data contract.

If the software says "relative visibility", the paper and app must not imply
"true sky quality" or "light pollution estimate" unless a later validated module
explicitly supports that claim.

## Source-of-truth documents

This roadmap depends on the following documents:

- `docs/minimum_data_spec.md`
- `docs/scientific_assumptions.md`
- `docs/validation_plan.md`
- `docs/calibration_protocol.md`
- `paper/paper.md`

If a future phase changes interpretation, these documents must be updated together.

## Phase roadmap

### Phase 1: JOSS review of the software design

Objective:
- Publish Amanogawa as a research software package and receive software-focused review of the current design.

Why this phase exists:
- to validate packaging, reproducibility, artifact design, CLI workflow, and scientific-software clarity before broadening claims.

Scope:
- core package in `src/amanogawa/`
- CLI and run artifacts
- reproducibility and validation docs
- visibility v1 as an observation-based score with explicit limitations

Not the goal of this phase:
- proving astrophysical novelty,
- launching a public citizen-science app,
- making device-adjusted sky-quality claims.

Exit criteria:
- JOSS submission is complete,
- reviewer-facing install/test/run path is stable,
- docs consistently describe current claims and limitations,
- `run_manifest.json` and visibility outputs are stable enough for review.

### Phase 2: Propose the scientific frame to the astronomy community

Objective:
- publish a methods-oriented astronomy paper describing what this framework can and cannot do with single smartphone images.

Why this phase exists:
- to define the scientifically acceptable use of Amanogawa outputs before opening large-scale public participation.

Scope:
- methods paper centered on relative visibility / analyzability
- validation data set with controlled repeated captures
- explicit discussion of device bias, atmospheric effects, and interpretation limits
- proposal of tractable early science questions

Target scientific framing:
- smartphone images can yield reproducible relative structure measurements and visibility proxies under stated constraints,
- Amanogawa provides a transparent framework for such measurements,
- cross-device or absolute environmental claims require later calibration and external references.

Not the goal of this phase:
- strong physical claims from sparse public data,
- absolute light pollution estimation,
- full citizen-science scaling.

Exit criteria:
- methods manuscript is submission-ready,
- validation figures and controlled pilot data support the stated claims,
- allowed and disallowed interpretations are documented clearly enough for external readers.

### Phase 3: Public citizen-science participation via app/platform

Objective:
- release a lightweight product that lets non-specialists contribute data easily while preserving the scientific contract established in earlier phases.

Why this phase exists:
- to turn the framework into a real citizen-science pipeline without sacrificing rigor.

Recommended product shape:
- upload-first smartphone web app or PWA before native app,
- one-photo submission flow,
- minimal metadata burden,
- automatic quality control and immediate result summary.

Required product behavior:
- show what the score means and does not mean,
- preserve device metadata and analysis provenance,
- distinguish submission success from research usability,
- avoid implying absolute sky-quality claims.

Not the goal of this phase:
- social features first,
- native-app complexity before the scientific workflow is stable,
- overconfident public interpretation of raw scores.

Exit criteria:
- a user can submit one photo with minimal friction,
- the system produces reproducible artifacts and QC outputs,
- the app language stays aligned with the documented limitations,
- collected data are organized for later scientific reuse.

### Phase 4: Scientific results from collected data

Objective:
- publish scientifically responsible results from the accumulated dataset.

Why this phase exists:
- to fulfill the mission through actual community-enabled science, not only software release.

Allowed early result types:
- reproducibility studies,
- same-device repeated-capture analyses,
- visibility trends under controlled conditions,
- exploratory correlations with external skyglow, moon, or weather data,
- method or dataset papers.

Higher-risk claims that require additional evidence:
- robust cross-device comparisons,
- absolute light pollution estimation,
- strong astrophysical population claims,
- environmental conclusions without calibration and external controls.

Exit criteria:
- dataset QC policy is stable,
- inclusion/exclusion rules are documented,
- claims are matched to the validated capability of the pipeline,
- manuscripts clearly separate observation-based proxies from stronger physical interpretation.

## Development priorities by default

When choosing what to build next, prefer this order:

1. Clarify the scientific contract.
2. Improve reproducibility and validation.
3. Reduce participation friction without breaking the contract.
4. Add calibration and external-reference capability.
5. Expand scientific claims only after validation supports them.

## Decision filter for future work

Before starting any new feature, paper, metric, or app flow, ask:

1. Does this directly support the mission?
2. Does it preserve or improve scientific interpretability?
3. Does it reduce or increase the risk of overstated claims?
4. Is it needed before JOSS, before the methods paper, or only after public launch?
5. Could a simpler version serve the same purpose with less scientific risk?

If a proposed task fails this filter, it should be deferred or removed.

## Current status

The project is currently in the transition between:

- Phase 1: JOSS-focused software hardening
- and the setup for Phase 2: astronomy methods framing

Visibility v1 is now part of the scientific contract.
Future work must treat it as an observation-based score with explicit device limitations.
