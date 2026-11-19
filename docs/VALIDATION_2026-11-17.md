# Public evidence validation — 17 November 2026

## Scope and baseline

This change hardens independent public verification tooling. The base commit is
`40a4cd9e6f4286da23c1cc30d4b4bfd7d643de8d`. It does not change the numerical
CSV/JSON evidence, application code, benchmarks, report PDF or video. The exact
verifier and test-source SHA-256 hashes below identify the tested implementation;
the containing commit and pull request identify the reviewable change.

## Reproduction

Python **3.12.14**, standard library only, run from the repository root:

```bash
python evidence/verify_stats.py
python -m unittest discover -s evidence -p 'test_*.py' -v
git diff --check
```

Results: **501 checks passed**, **7 unittest methods passed**, and no whitespace
errors. The tests exercise **39 altered-data fixtures**: nine summary fields,
22 individual CSV mutations, five structural mutations, two multi-cell
consistency mutations, and one invalid CLI invocation. The intact dataset and
valid CLI invocation also pass. Every altered fixture is rejected for its
expected reason. Test mutations operate on temporary copies and leave the
committed evidence unchanged.

The baseline verifier and the revised verifier were also run independently
against the three specific corruptions raised in review:

| Alteration | Baseline exit | Revised exit |
| :-- | --: | --: |
| Summary `max_ms`: 486.647 → 999 | 0 (missed) | 1 (rejected) |
| Hard INT8 Hit@1: 14 → 19 | 0 (missed) | 1 (rejected) |
| TinyCLIP 39M/16 Hit@1: 85% → 95% | 0 (missed) | 1 (rejected) |

## Coverage and limits

- Every sustained-search summary field is recomputed, including count, mean,
  median, P95, minimum, maximum, first/last-20 medians and drift.
- Retrieval totals are reconciled with each set, FP32 counts with the deeper
  comparison, model percentages with interval counts, and paired contingency
  cells with their marginals and query totals.
- INT8 and model-selection Wilson intervals and exact McNemar values are checked.
  The related sets' aggregate remains descriptive; no pooled inference is added.
- All nine CSV schemas and expected keys are checked. Timing run IDs must be
  ordered, unique and complete; timing values must be finite and positive.
- Warm-search and startup values receive structural/plausibility checks, not
  fresh measurements. Nested timing components are deliberately not summed.
- Temporal cases receive structural checks, not a rerun of the gallery filter.
- Engineering-summary coverage remains limited to the text-model size reduction;
  other measurement provenance and cross-artifact claims remain separate work.
- These tests demonstrate internal consistency and known regression detection.
  They do not authenticate measurements, establish model equivalence, validate
  Android builds or inspect statements in the PDF, video, README or portfolio.

No hosted workflow was added or run. Local commands provide reproducible
validation without consuming GitHub Actions minutes.

## Tested source hashes

- `evidence/verify_stats.py`: `cf97d5828763940372bed8901f557af54da0889a33c4fd660a4e9dcdd3f8df8d`
- `evidence/test_verify_stats.py`: `492fe4e59fabb0d01f2d044262462e700244be3042dcb5ab11bf84b1ce88644f`
