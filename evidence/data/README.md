# Public evidence data

The historical files retain the original engineering measurements. They contain aggregate or de-identified engineering evidence only: no classroom photos, media identifiers, filenames, exact capture dates, personal paths, credentials or linked per-query records are included.

## Verify the headline statistics

From the repository root:

```bash
python evidence/verify_stats.py
```

The verifier uses only the Python standard library and recomputes the sustained-search median/P95/drift, text-model size reduction, descriptive FP32/INT8 retrieval totals, Wilson confidence intervals and exact McNemar tests from the committed evidence. The verifier is new public portfolio tooling and contains no TeachScribe application implementation.

The November [tokenizer ranking comparison](tokenizer_ranking_november.csv) adds four aggregate rows from a later desktop CPU study. The last two columns apply only to the labelled controls. The verifier compares every cell with the aggregate retained from the paired CPU run. This check detects changes to the published CSV. A new inference run requires the study inputs and encoders.

## Evidence stages

Do not combine the following into a single accuracy or performance claim:

1. **Desktop model selection** — five pretrained vision-language models on a small curated Hard set; the two leading candidates were also compared on Expanded and New Images sets.
2. **Historical Android benchmark** — physical Huawei MediaPad M3 Lite 8 (CPN-W09), Android 7 / ARM64; latency, startup, memory, thermal and battery-side measurements from the benchmark build.
3. **Functional acceptance** — temporal filtering, persistence and later on-device behaviour checks.
4. **Post-delivery review** — FP32/INT8 retrieval comparison, behaviour-equivalence checks and later fail-closed invalid-embedding guards in the audited private edition.

## Files

- `model_comparison.csv` — five-model desktop comparison on the common Hard set.
- `deeper_quality.csv` — MobileCLIP-S0 vs TinyCLIP 39M/16 on Hard, Expanded and New Images.
- `hit_rate_intervals.csv` — Hit@1/Hit@5 counts and 95% Wilson intervals.
- `paired_model_comparison.csv` — paired exact McNemar comparisons for the two finalists.
- `deployed_int8_quality.csv` — shipped INT8 encoders vs FP32 retrieval on the same labelled sets.
- [November tokenizer results](tokenizer_ranking_november.csv) — four groups on the fixed eight-photo CPU gallery.
- `sustained_search_108_runs.csv` — 108 consecutive cached-search durations.
- `recomputed_statistics.json` — statistics recomputed from those 108 durations.
- `warm_search_5_runs.csv` — five-run warm reference with nested timing fields.
- `startup_5_runs.csv` — process and React Native startup milestones; not first-frame/fully-interactive timing.
- `temporal_cases.csv` — de-identified fixed-target date/window acceptance cases.
- `engineering_summary.json` — scoped engineering measurements for power, thermal, memory, scheduling, quantisation, preprocessing and one cold-path example.

## Interpretation limits

Alberto delivered the Android app on 29 September 2026. TeachScribe released photo search in its app on 19 November 2026 for the 50+ UK schools it serves. School-level usage and classroom impact metrics for the feature are pending.

[Recomputed statistics](recomputed_statistics.json) · [Public verifier](../verify_stats.py).
