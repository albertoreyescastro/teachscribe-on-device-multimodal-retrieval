# Retrieval quality: FP32 selection and INT8 comparison

The **17/20 Hard Hit@1** result belongs to TinyCLIP 39M/16 in FP32 desktop model selection. The shipped INT8 text/image exports scored **14/20** in a later desktop comparison on the same Hard set. Neither number is a production adoption metric or a representative estimate of classroom accuracy.

The later comparison used the application tokenizer, standard CLIP image preprocessing and desktop ONNX Runtime. It does not validate the Android Kotlin preprocessing path. No new model run was performed to prepare this page: it exposes the already committed aggregate evidence more clearly.

## Counts and paired changes

A loss means a query hit in FP32 but not INT8 at that k; a gain is the reverse. Same top-1 means the same first image, whether or not that image was a labelled hit. It is not the count of correct answers.

| Set | Metric | FP32 hits | INT8 hits | Losses / gains | Exact McNemar p |
| :-- | :-- | --: | --: | --: | --: |
| Hard | Hit@1 | 17/20 | 14/20 | 3 / 0 | 0.2500 |
| Hard | Hit@5 | 18/20 | 18/20 | 0 / 0 | 1.0000 |
| Expanded | Hit@1 | 44/60 | 46/60 | 2 / 4 | 0.6875 |
| Expanded | Hit@5 | 55/60 | 54/60 | 1 / 0 | 1.0000 |
| New Images | Hit@1 | 24/30 | 23/30 | 1 / 0 | 1.0000 |
| New Images | Hit@5 | 30/30 | 30/30 | 0 / 0 | 1.0000 |
| Related sets (descriptive sum) | Hit@1 | 85/110 | 83/110 | 6 / 4 | Not pooled |
| Related sets (descriptive sum) | Hit@5 | 103/110 | 102/110 | 1 / 0 | Not pooled |

| Set | Queries | Candidate images per query | Same top-1 image |
| :-- | --: | --: | --: |
| Hard | 20 | 16 | 17/20 |
| Expanded | 60 | 16 | 52/60 |
| New Images | 30 | 10 | 28/30 |
| All sets (descriptive sum) | 110 | 10-16 | 97/110 |

## Per-set uncertainty

These are 95% Wilson intervals for each observed hit rate. They describe sampling uncertainty under the binomial calculation; they do not correct for query curation, related sets or unknown pretraining overlap.

| Set | Metric | FP32 rate (95% interval) | INT8 rate (95% interval) |
| :-- | :-- | :-- | :-- |
| Hard | Hit@1 | 85.0% (64.0–94.8%) | 70.0% (48.1–85.5%) |
| Hard | Hit@5 | 90.0% (69.9–97.2%) | 90.0% (69.9–97.2%) |
| Expanded | Hit@1 | 73.3% (61.0–82.9%) | 76.7% (64.6–85.6%) |
| Expanded | Hit@5 | 91.7% (81.9–96.4%) | 90.0% (79.9–95.3%) |
| New Images | Hit@1 | 80.0% (62.7–90.5%) | 76.7% (59.1–88.2%) |
| New Images | Hit@5 | 100.0% (88.6–100.0%) | 100.0% (88.6–100.0%) |

Exact paired McNemar tests do not reject equal marginal hit rates at the 5% level on these individual sets (p ≥ 0.25). **That is not evidence of statistical equivalence or non-inferiority**: no equivalence margin or adequately powered equivalence design was established. The observed Hard Hit@1 reduction remains relevant even though its p-value is 0.25.

The 110-query total is a descriptive sum of **three partly related sets**, not 110 independent held-out trials. It has no pooled McNemar test or pooled confidence interval. Net Hit@1 changes by −2 (six losses and four gains); Hit@5 changes by −1. Agreement on 97/110 first images does not imply identical embeddings, scores or complete rankings.

## Selection trade-off

TinyCLIP 39M/16 achieved higher FP32 Hit@1 than MobileCLIP-S0 on the three evaluated sets. It had lower Hard Hit@5 (18/20 vs 19/20), tied Expanded Hit@5 (55/60 each), and higher New Images Hit@5 (30/30 vs 29/30). Paired tests were retained for Expanded and New Images only: Expanded Hit@1 p = 0.3877; the other three p-values are 1.0000. Those results do not establish general superiority. The selection also considered licensing and the ONNX deployment path.

## Evidence and limits

- [FP32/INT8 comparison](../evidence/data/deployed_int8_quality.csv)
- [Historical FP32 counts](../evidence/data/deeper_quality.csv) and [five-model selection](../evidence/data/model_comparison.csv)
- [FP32 Wilson intervals](../evidence/data/hit_rate_intervals.csv) and [paired model comparison](../evidence/data/paired_model_comparison.csv)
- [Public verification instructions](VALIDATION.md#public-reproducibility)

Queries were curated with knowledge of the photographs. The sets contain 20, 60 and 30 queries with only 16 or 10 candidates; Hit@5 can therefore be permissive. “New Images” means new to this evaluation, not proven absent from pretraining. Private images and linked query records are excluded, so the public artifacts permit aggregate verification rather than independent replay of model inference.
