# Public evidence data

These files are copied from the audited private engineering repository without changing the numeric observations. They contain aggregate or de-identified engineering evidence only: no classroom photos, media identifiers, filenames, exact capture dates, personal paths, credentials or linked per-query records are included.

## Verify the headline statistics

From the repository root:

```bash
python evidence/verify_stats.py
python -m unittest discover -s evidence -p 'test_*.py' -v
```

The standard-library verifier recomputes every sustained-search summary field, checks FP32/INT8 results and aggregates against per-set counts, and cross-checks model-selection percentages, Wilson intervals and exact McNemar values across the CSV tables. It also checks CSV schemas, expected row keys, ordered run IDs, finite positive timing values and temporal-case structure. Rounded four-decimal rates and intervals use an absolute tolerance of 0.0000501; sustained statistics use 1e-9 ms (or percentage points for drift).

The mutation suite deliberately corrupts evidence and requires each case to fail with a relevant diagnostic; intact evidence must pass. See [the validation record](../../docs/VALIDATION_2026-11-17.md) for scope and results. Both scripts are independent public portfolio tooling, not TeachScribe application source.

These checks establish internal consistency of the published numerical evidence. They do not rerun inference or Android benchmarks, authenticate the original observations, validate every engineering-summary measurement, or inspect claims rendered in the README, PDF or video. Paired aggregate rows remain descriptive sums; no pooled inferential test is added for the related sets.

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
- `sustained_search_108_runs.csv` — 108 consecutive cached-search durations.
- `recomputed_statistics.json` — statistics recomputed from those 108 durations.
- `warm_search_5_runs.csv` — five-run warm reference with nested timing fields.
- `startup_5_runs.csv` — process and React Native startup milestones; not first-frame/fully-interactive timing.
- `temporal_cases.csv` — de-identified fixed-target date/window acceptance cases.
- `engineering_summary.json` — scoped engineering measurements for power, thermal, memory, scheduling, quantisation, preprocessing and one cold-path example.

## Interpretation limits

The image/query sets are small and curated, and the physical-device measurements come from one older Android tablet. The 50+ UK-school figure used elsewhere in the case study is deployment reach for TeachScribe, not measured adoption of this retrieval feature. Cosine similarity scores are not calibrated probabilities.
