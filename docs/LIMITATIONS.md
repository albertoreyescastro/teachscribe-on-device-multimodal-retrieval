# Scope and limitations

- The production retrieval pipeline has shipped within TeachScribe, but feature adoption has not been measured. The 50+ UK-school figure is TeachScribe deployment reach, not a claim that every school actively uses this retrieval feature.
- Device measurements come from one Huawei MediaPad M3 Lite 8 (Android 7 / ARM64) and relatively small candidate pools. They do not establish a modern-device matrix, large-library scalability or a service-level guarantee.
- Desktop retrieval quality uses 20/60/30-query sets with 16 or 10 candidate images. Queries were curated with knowledge of the photographs, the sets are partly related, and pretraining overlap is unknown. Hit rates are not population-accuracy estimates; neither model superiority nor FP32/INT8 equivalence is established.
- FP32 Hard Hit@1 is 17/20; the shipped INT8 exports score 14/20 in the later desktop comparison. That comparison uses standard CLIP preprocessing and does not validate the Android Kotlin path. See [per-set counts and uncertainty](RETRIEVAL_QUALITY.md).
- The 1.82% first/last-20 median latency change is descriptive within one historical run. It does not establish absence of drift, a general performance bound or a service-level guarantee.
- A cosine score is a ranking similarity, not a calibrated probability. The system does not establish identity, learning outcomes or intentions from a photograph.
- This retrieval path contains no face-recognition or child-identity matching stage.
- Media timestamps can be missing or misleading. A relevant image excluded by the date filter cannot be recovered by semantic ranking; widening the window can also introduce harder distractors.
- Cache identity uses media metadata plus an explicit model/cache version, not a content hash. Model or preprocessing changes therefore require cache-version review.
- Application database records are not encrypted by an additional app-level layer, and the evaluated implementation does not claim a general schema-migration or damaged-database recovery framework.
- Cancellation is cooperative and does not guarantee interruption of native inference already in progress.
- EXIF-rotation parity, HEIC, cloud-only assets and broad format coverage were not established by the tested path.
- The later behaviour-preserving refactor was functionally compared on-device, but the historical latency, memory, thermal and energy benchmark was not rerun on that refactored build.
- The public case study intentionally omits application source, model binaries, APKs, signing material, private imagery and internal delivery correspondence. This limits independent replay of the original end-to-end benchmark while preserving the underlying de-identified measurements.
