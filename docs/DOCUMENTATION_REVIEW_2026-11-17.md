# Documentation review — 17 November 2026

Base: `a59ea5fbdf9257929255431ae40c5b63ecfe420a` (the public evidence-verifier
proposal). This documentation change is intended to follow that proposal.

## Changes

- Lead the README with the problem, Alberto's contribution and scoped measured
  latency. Move historical validation and the video below the results.
- Display FP32 Hard Hit@1 17/20 next to INT8 14/20, with Wilson intervals and the
  desktop/Android preprocessing distinction.
- Add per-set counts, losses/gains, top-1 agreement, exact McNemar values and
  Wilson intervals in `RETRIEVAL_QUALITY.md`. Keep the related-set sum descriptive
  and explain that non-significant tests do not establish equivalence.
- Make image-aware query curation, related sets, unknown pretraining overlap,
  single-device testing and the historical timing boundary explicit.
- Describe 1.82% first/last-20 drift as a within-run observation; no unverified
  Spearman p-value is added.
- Specify written, recipient- and material-specific approval before private
  source access. No access grant or company approval is implied by this change.

## Verification performed

Python 3.12.14. The 8 count/change/p-value rows and 12 displayed Wilson intervals
were compared with the committed CSV counts and recomputed intervals. All match.
The 32 local Markdown/HTML links and fragments in the five principal revised
documents resolve; the document index additionally links to the new quality page.
The six-row quality table distinguishes desktop encoders from Android preprocessing.

```sh
python evidence/verify_stats.py
python -m unittest discover -s evidence -p 'test_*.py' -v
git diff --check
```

Results: 501 public evidence checks pass; 7 unittest methods pass, covering the
same 39 rejected corrupted fixtures documented in `VALIDATION_2026-11-17.md`;
no whitespace errors. All 11 public numerical CSV/JSON files remain byte-identical
to the base. Public PDF v2 remains unchanged with SHA-256
`85e72a451426c4a52917521015ff71ffcfa95ccf15a827c80e878451e72c0fd7`.

## Work not claimed complete

This is a Markdown revision, not a PDF/video rebuild, a source test-suite run,
a device benchmark or a visual mobile/desktop browser review. The existing video
is explicitly identified as predating the wording clarifications. Final claims
about schools, institutional programmes and publication permissions need their
separate checks. No new private source, images or linked query records are added.
