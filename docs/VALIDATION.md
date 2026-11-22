# Validation

The TeachScribe application implementation is not published in this public case study. Validation was performed against the audited private engineering repository; de-identified evidence and an independent verification script are published here.

## Completed private-repository checks

Historical October suite: **28 October 2026**. All checks passed.

| Check | Result |
| :-- | :-- |
| TypeScript | strict typecheck passed |
| ESLint | zero warnings |
| Node regression suite | **33/33 passed** |
| Python regression suite | **15/15 passed** |
| Refactor proof | **143** original units preserved, **0 mismatches** |
| On-device A/B | same Top-5 asset order and similarity scores for every compared search |

The 27 October tablet comparison used an earlier comparator that accepted the intersection of searches. Missing, extra or duplicate records were not rejected. Original backup exports were unavailable for a strict replay.

The automated tests cover date/DST behaviour, persistence, embedding-cache behaviour, tokenizer reference vectors, ranking helpers, pipeline event order, yielding and cancellation, session reuse/retry, invalid-vector handling, statistical helpers and A/B comparison logic.

## Delivered snapshot vs post-delivery hardening

The delivered snapshot predates the later fail-closed guards for freshly computed non-finite or wrong-dimension embeddings. Those guards were added during the audited post-delivery portfolio review. They affect invalid values only; valid finite 512-dimensional embeddings follow the previous path unchanged.

## Performance scope

The 108-search performance benchmark was **not** repeated after the behaviour-preserving refactor. Latency, memory, energy and thermal numbers in this case study remain historical measurements from the benchmark build.

## Public reproducibility

Run:

```bash
python evidence/verify_stats.py
```

The script uses only the Python standard library and recomputes the headline sustained-search median/P95/drift, INT8 text-model size reduction, descriptive FP32/INT8 retrieval totals, Wilson intervals and exact McNemar values from the committed CSV/JSON evidence. It is independent portfolio verification tooling, not TeachScribe application source.

Run the mutation suite with `python -m unittest discover -s evidence -p "test_verify_stats.py"`. The checks include individual November group counts against the frozen paired-run output.

## November tokenizer study

The delivered TypeScript byte-pair encoder had 20 fixed reference phrases, 12 edge cases and 300 seeded strings for cross-language regression. Agreement between two ports cannot establish agreement with the official tokenizer on every input. On 50 selected difficult strings the delivered implementation matched all 77 reference token IDs on 23. A later candidate matched the reference on 400/400 complete 77-ID vectors in React Native 0.81.5 Hermes on Linux.

On 18 November the delivered INT8 encoders were run on CPU with ONNX Runtime 1.32.0. Both tokenizer arms used the same eight scikit-image 0.25.2 example photos, preprocessing and tie ordering. Full 77-ID vectors were compared for each input.

| Input group | n | Identical token IDs | Changed first image | Changed Top-5 members | Changed Top-5 order or membership |
| --- | ---: | ---: | ---: | ---: | ---: |
| Historical query texts | 110 | 110 | 0 | 0 | 0 |
| Selected difficult inputs | 50 | 23 | 7 | 15 | 23 |
| Plain labelled descriptions | 8 | 8 | 0 | 0 | 0 |
| Same descriptions with HTML-escaped spaces | 8 | 0 | 0 | 5 | 8 |

On 19 November the CPU comparison reproduced the same result file byte for byte. Both TypeScript tokenizer arms reproduced their respective 77-ID vectors for all 176 inputs.

[Aggregate counts from the November CPU study](../evidence/data/tokenizer_ranking_november.csv).

Both arms scored 8/8 Hit@1 in each labelled control group. Within the 50 diagnostic cases the minimum text-embedding cosine was 0.70787 and the largest absolute score change was 0.16653. The public example gallery allows a controlled ranking comparison. It does not recreate the original galleries or estimate school usage. The November proposal would change behaviour on some inputs. There is no physical Android acceptance result for that candidate here.

## Report editions and original walkthrough

| Edition | Status | SHA-256 |
| --- | --- | --- |
| [v5 · engineering case study](../report/TeachScribe_Public_Engineering_Case_Study_v5.pdf) | Current public case study. Includes the November study, delivery and release dates, scope of the October comparison, and status of the next Android version. | `807b84d75aab3efc5fee80485d58806f2fb2d54acfead81fb1e30c8d3b7c54b2` |
| [v4 · engineering case study](../report/TeachScribe_Public_Engineering_Case_Study_v4.pdf) | Previous November edition, retained for historical reference. | `b4462ac9501e78e540fa095a94ec035633b5f7d5313281e04a8137eed8b1fec2` |
| [v2 · October edition](../report/TeachScribe_On_Device_Multimodal_Retrieval_Public_Engineering_Case_Study_v2.pdf) | Published historical edition. Its APK component-size attribution is corrected in v4. | `85e72a451426c4a52917521015ff71ffcfa95ccf15a827c80e878451e72c0fd7` |

Version 3 was an unpublished review draft and has been superseded. The September handoff date and the later distribution confirmation refer to distinct events. The dates and conditions of the historical benchmarks are retained.

[Original narrated walkthrough](https://github.com/user-attachments/assets/686275ae-5e92-4469-83d3-fb213f77ac7a). The 97.8-second published original is the selected video. SHA-256 recorded in the original audit: `4bee6f67bdc46b14b25141c12c4b48379eb67eb7a5098a4a4651ad6f74188539`.
