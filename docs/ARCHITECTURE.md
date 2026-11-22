# Architecture

This public case study describes the **delivered retrieval architecture plus clearly marked post-delivery hardening** without publishing TeachScribe's proprietary application source code.

The system combines a React Native/Expo interface, local media enumeration, a CLIP-style tokenizer, separate text and image ONNX encoders, native Android image preprocessing, a persistent embedding cache and explicit human review. Inference and ranking run on the device. Accepting a result does not train or update the pretrained model, and this retrieval path contains no face-recognition or identity-matching stage.

## Retrieval flow

1. Request photo access, enumerate accessible media and resolve an optional local date/window filter.
2. Snapshot the observation and candidate list for one active search.
3. Tokenise the text to the CLIP context length and encode a 512-component query vector.
4. Reuse valid image vectors from memory or SQLite. Only cache misses require image preprocessing and image-model inference.
5. Compute cosine similarity, sort descending and initially present five suggestions.
6. Preserve the original successful-search result separately from the user's later photo/no-match decision.

The persistent image-vector cache changes the cost structure materially: a fully cached search can avoid loading or running the image encoder and instead pays for text encoding, cache access, scoring, sorting and UI scheduling.

![Local retrieval architecture](figures/architecture.svg)

## Inference contracts

| Stage | Contract |
| :-- | :-- |
| Text input | int32 `[1,77]` token IDs |
| Text output | 512-component embedding |
| Image input | float32 `[1,3,224,224]` tensor |
| Image output | 512-component embedding |
| Native buffer | 150,528 Float32 values / 602,112 little-endian bytes |
| Ranking | cosine similarity, sorted descending; score is not a probability |

Text and image sessions are acquired lazily and reused within a process. Query vectors are recomputed per search; valid image vectors are reusable. A failed session acquisition can be retried. An all-cached search does not need the image session.

## Native image path

The Android preprocessing path performs bounded decoding, crop-preserving downsampling, centred square cropping, antialiased bicubic resizing to 224×224, RGB scaling and CLIP normalisation in NCHW order. Defensive pixel bounds reject implausibly large inputs. The measured preprocessing improvements in this case study use different photographs and are therefore not presented as a strict paired A/B speedup.

## Cache lifecycle

Cache identity combines a model/cache version with media metadata. It is intentionally not presented as a content hash: edits that preserve every key field can evade invalidation, and model or preprocessing changes require a cache-version decision.

RAM coalesces repeated work. Missing valid vectors are hydrated from SQLite; persisted rows with invalid dimensions, byte counts, non-finite values or invalid norms are rejected. **In the audited post-delivery edition, fail-closed guards also reject freshly computed non-finite or wrong-dimension embeddings before caching/ranking; the delivered snapshot predates these guards.** Valid finite 512-dimensional embeddings continue through the previous path unchanged. Successful gallery refreshes prune stale or inaccessible keys. Process restart discards sessions and RAM but preserves valid persisted vectors.

## Durable state

| Store | Purpose | Retention |
| :-- | :-- | :-- |
| Image embeddings | Versioned vectors and norms for reuse | Pruned against accessible keys/version |
| Search history | Query/filter, compared count and original Top-5 metadata | Latest 100 successful searches |
| Reviewed observations | Explicit selected-photo or no-match decision | Until user deletion |
| Diagnostics | Timings, counters and outcome metadata | Bounded development/diagnostic retention |

Search history and human review are deliberately separate. Reopening historical results preserves the original ranking snapshot rather than silently recomputing it. The recorded candidate count is the number successfully compared, which can differ from the requested pool when a media file cannot be read or encoded.

## Timing boundary

The reported search timer ends before final rendering and before diagnostic/history persistence. Image read, preprocessing and inference timings are nested inside broader ranking intervals, so phase timings must not be added as if they were independent components. The headline cached-search numbers are therefore **instrumented pipeline latency**, not universal tap-to-visible latency.

## Public/private boundary

This document intentionally preserves the engineering contracts, architecture and trade-offs while omitting source-file names, implementation bodies, proprietary UI code, native-module source, implementation tests and build scripts. The [hiring review policy](PUBLICATION_BOUNDARY.md#hiring-review) describes access to the private engineering repository. See [publication scope](PUBLICATION_BOUNDARY.md).

## How the refactor was checked

A TypeScript Compiler API check compared declarations from the 3,749-line portfolio baseline with the split modules (portfolio-baseline → refactor-split). It found 143 preserved units, zero mismatches and no added control flow in the checked split. Formatting had its own AST-equivalence check. The historical tablet comparison examined the top-five photo order and similarity scores for the searches compared by that run. These checks answer different questions. Neither remeasured latency on the latest revision. The invalid-vector guards came later, with separate rejection tests.

## Measured scheduling, energy and temperature

On the 37-candidate run, yielding to the UI about every ten candidates took 530.92 ms in total. Every 20 took 379.42 ms. A less frequent yield took 303.55 ms but raised responsiveness concerns. The 20-candidate policy was retained. Loading the image model in advance raised idle process PSS from 76.3 to 166.6 MiB, so the measured design kept lazy loading.

The sustained phase averaged 2.70922 W at the battery, compared with 1.90547 W idle. Across 239 seconds and 108 completed cached searches, the incremental estimate is (2.70922 − 1.90547) × 239 / 3.6 / 108 ≈ 0.494 mWh per search. Android accounting gave about 14.9 mAh against about 14.1 mAh by the differential fuel-gauge calculation. Their roughly 5.6% difference is a cross-check of magnitude. The sustained phase reached 34–37 °C, recovery reached 39 °C and a separate longer run reached 41 °C. The recorded CPU ceilings stayed constant during the controlled load. These observations describe one tablet and workload.

[Engineering measurements](../evidence/data/engineering_summary.json) · [Public report, sections 8 and 12–14](../report/TeachScribe_Public_Engineering_Case_Study_v5.pdf)

## Startup, warm searches and temporal acceptance

Five process starts placed the process-detected milestone between 1.72 and 1.76 s. The JavaScript main milestone ranged from 2.46 to 2.88 s. Neither timestamp measures the first visible result. Five separate warm searches took 424.93–470.21 ms. These are short reference series, separate from the sustained 108-search run.

In the de-identified filtering example, the target ranked first at a cosine score of 0.2745 with 1, 3 and 14 candidates when the same-day window widened. Moving the observation three days earlier excluded the target in the two-hour window. Widening that search to 168 hours restored it to first place among 14 candidates. Candidate selection can therefore determine whether semantic ranking ever sees a relevant photo. These five cases illustrate filtering behaviour on one target.

[Startup milestones](../evidence/data/startup_5_runs.csv) · [Warm runs](../evidence/data/warm_search_5_runs.csv) · [Temporal cases](../evidence/data/temporal_cases.csv)
