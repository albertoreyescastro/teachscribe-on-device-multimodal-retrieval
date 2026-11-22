#!/usr/bin/env python3
"""Recompute headline public-case-study statistics from de-identified evidence.

Standard library only. This script is independent portfolio verification tooling;
it is not TeachScribe application source code.
"""
from __future__ import annotations

import csv
import json
import math
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"


def read_csv(name: str):
    with (DATA / name).open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        check(reader.fieldnames == SCHEMAS[name].split(","), f"{name}: schema")
        rows = list(reader)
    check(bool(rows) and all(None not in r and None not in r.values() for r in rows),
          f"{name}: complete rows")
    return rows


def percentile_linear(values, q: float) -> float:
    xs = sorted(float(x) for x in values)
    if not xs:
        raise ValueError("empty series")
    if len(xs) == 1:
        return xs[0]
    pos = (len(xs) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    if lo == hi:
        return xs[lo]
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def wilson(hits: int, n: int, z: float = 1.959963984540054):
    p = hits / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return centre - margin, centre + margin


def exact_mcnemar(b: int, c: int) -> float:
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    tail = sum(math.comb(n, i) for i in range(k + 1)) / (2**n)
    return min(1.0, 2 * tail)


def close(a, b, tol=5.01e-5):
    return abs(float(a) - float(b)) <= tol


def check(ok: bool, label: str):
    if not ok:
        raise AssertionError(label)
    print(f"PASS  {label}")


SCHEMAS = {
    "tokenizer_ranking_november.csv": "group,queries,gallery_size,same_tokens,top1_changed,top5_members_changed,top5_order_changed,legacy_labelled_hit1,candidate_labelled_hit1",
    "sustained_search_108_runs.csv": "run,total_ms",
    "startup_5_runs.csv": "run,process_detected_ms,js_main_ms",
    "warm_search_5_runs.csv": "run,total_ms,text_inference_ms,ranking_ms,ui_yield_ms",
    "temporal_cases.csv": "observation_relative_day,window_hours,compared,target_included,target_rank,target_score",
    "deeper_quality.csv": "set,queries,candidates,mobile_hit1,mobile_hit5,tinyclip39_hit1,tinyclip39_hit5",
    "deployed_int8_quality.csv": "set,queries,candidates,metric,fp32_hits,int8_hits,int8_wilson95_low,int8_wilson95_high,only_fp32,only_int8,exact_mcnemar_p,same_top1_image",
    "hit_rate_intervals.csv": "set,model,metric,hits,queries,rate,wilson95_low,wilson95_high",
    "model_comparison.csv": "model,parameters,hit1_percent,hit5_percent,images16_seconds,image_mean_seconds,text_mean_seconds",
    "paired_model_comparison.csv": "set,metric,queries,both_hit,only_tinyclip39,only_mobileclip_s0,neither,exact_mcnemar_p",
}
SETS = {"Hard": (20, 16), "Expanded": (60, 16), "New Images": (30, 10)}
MODELS = {"MobileCLIP-S0", "TinyCLIP 8M/16", "TinyCLIP 40M/32", "SigLIP Base", "TinyCLIP 39M/16"}
TOTAL = "All sets (descriptive sum)"
METRICS = ("hit1", "hit5")


def index_rows(rows, fields, expected, label):
    keys = [tuple(row[f] for f in fields) for row in rows]
    check(len(keys) == len(set(keys)), f"{label}: unique keys")
    check(set(keys) == set(expected), f"{label}: expected keys")
    return dict(zip(keys, rows))


def count(value, n, label):
    value = int(value)
    check(0 <= value <= n, f"{label}: count in range")
    return value


def positive(value, label):
    value = float(value)
    check(math.isfinite(value) and value > 0, f"{label}: finite positive value")
    return value


# Counts frozen from the separately retained two-arm CPU run of 18 November.
# Columns follow the public CSV schema after the group identifier.
NOVEMBER_PAIRED_RUN = {
    "historical": (110, 8, 110, 0, 0, 0, None, None),
    "diagnostic": (50, 8, 23, 7, 15, 23, None, None),
    "descriptive": (8, 8, 8, 0, 0, 0, 8, 8),
    "escaped": (8, 8, 0, 0, 5, 8, 8, 8),
}


def verify_november_tokenizer():
    name = "tokenizer_ranking_november.csv"
    rows = index_rows(read_csv(name), ("group",), [(k,) for k in NOVEMBER_PAIRED_RUN], "November study")
    fields = SCHEMAS[name].split(",")[1:]
    for group, expected in NOVEMBER_PAIRED_RUN.items():
        row = rows[(group,)]
        for field, reference in zip(fields, expected):
            value = "" if reference is None else str(reference)
            check(row[field] == value, f"November {group}: {field} matches frozen CPU run")


def main():
    verify_november_tokenizer()
    sustained = read_csv("sustained_search_108_runs.csv")
    startup = read_csv("startup_5_runs.csv")
    warm = read_csv("warm_search_5_runs.csv")
    for name, rows, n in [
        ("sustained", sustained, 108),
        ("startup", startup, 5),
        ("warm", warm, 5),
    ]:
        check([r["run"] for r in rows] == [str(i) for i in range(1, n + 1)],
              f"{name}: ordered unique run IDs")
        for row in rows:
            for key, value in row.items():
                if key != "run":
                    positive(value, f"{name} run {row['run']} {key}")
            if name == "startup":
                check(float(row["process_detected_ms"]) <= float(row["js_main_ms"]),
                      "startup: process precedes JS milestone")
    # Historical five-run series behind Architecture and sections 10–11 of the report.
    # Keep the original millisecond precision before rounding to seconds for display.
    for name, rows, field, low, median, high in [
        ("startup", startup, "process_detected_ms", 1722.9, 1726.4, 1757.6),
        ("startup", startup, "js_main_ms", 2464.1, 2855.0, 2876.1),
        ("warm", warm, "total_ms", 424.93, 436.51, 470.21),
    ]:
        values = [float(row[field]) for row in rows]
        check(min(values) == low, f"{name} {field}: minimum")
        check(statistics.median(values) == median, f"{name} {field}: median")
        check(max(values) == high, f"{name} {field}: maximum")

    times = [float(r["total_ms"]) for r in sustained]
    first20, last20 = statistics.median(times[:20]), statistics.median(times[-20:])
    actual = {
        "count": len(times), "mean_ms": statistics.mean(times),
        "median_ms": statistics.median(times), "p95_ms": percentile_linear(times, 0.95),
        "min_ms": min(times), "max_ms": max(times),
        "first20_median_ms": first20, "last20_median_ms": last20,
        "first_last_drift_percent": (last20 / first20 - 1) * 100,
    }
    stats = json.loads((DATA / "recomputed_statistics.json").read_text(encoding="utf-8"))
    check(set(stats) == set(actual), "sustained statistics: schema")
    for key, value in actual.items():
        check(close(value, stats[key], 1e-9), f"sustained statistics: {key}")

    eng = json.loads((DATA / "engineering_summary.json").read_text(encoding="utf-8"))
    fp32 = positive(eng["text_model_bytes"]["FP32"], "FP32 bytes")
    int8 = positive(eng["text_model_bytes"]["INT8"], "INT8 bytes")
    check(close((1 - int8 / fp32) * 100, 74.77, 0.01), "text encoder size reduction = 74.77%")

    # Independent comparisons with the published report, using its displayed precision.
    power = eng["power_w"]
    incremental = power["Sustained search"] - power["Idle"]
    check(close(incremental, 0.804, 0.0005), "engineering: incremental power")
    check(close(incremental * 239 / 3.6 / len(times), 0.494, 0.0005), "engineering: energy per search")
    check(eng["thermal_ranges_c"] == {"Idle": [33, 33], "Sustained search": [34, 37], "Recovery": [34, 39]}
          and eng["longer_run_max_soc_c"] == 41, "engineering: thermal conditions")
    apk = eng["apk_mib"]
    check(close(apk["Benchmark build"] - apk["Earlier clean INT8"], 25.41, 1e-8)
          and close(apk["Benchmark build"] - apk["Later private closure"], 26.24, 1e-8),
          "engineering: separate APK baselines")
    memory = eng["memory_mib"]
    check(eng["memory_columns"] == ["Process PSS", "Native Heap PSS"]
          and all(0 < native <= process for process, native in memory.values()), "engineering: nested memory")
    preload = eng["preload_idle_pss_mib"]
    check(close(memory["Idle"][0], preload["Lazy loading"], 0.05)
          and close(preload["Preload experiment"] - preload["Lazy loading"], 90.3, 1e-8),
          "engineering: preload memory delta")
    scheduler = eng["scheduler_ms"]
    check(eng["scheduler_columns"] == ["Total", "Ranking (nested)"]
          and all(0 < nested <= total for total, nested in scheduler.values()), "engineering: nested scheduler")
    check(close(100 * (1 - scheduler["Every 20"][0] / scheduler["Original"][0]), 28.5, 0.05)
          and scheduler["About 50 (rejected)"][0] < scheduler["Every 20"][0], "engineering: scheduling trade-off")
    cold = eng["new_image_ms"]
    check(close(cold["preprocessing"], eng["preprocessing_ms"]["Case D"], 1e-8)
          and positive(cold["total"], "cold total") > max(v for k, v in cold.items() if k != "total"),
          "engineering: cold case and nested timings")

    deeper = index_rows(read_csv("deeper_quality.csv"), ("set",),
                        [(s,) for s in SETS], "deeper quality")
    for (s,), row in deeper.items():
        n, candidates = SETS[s]
        check((int(row["queries"]), int(row["candidates"])) == (n, candidates), f"{s}: scope")
        for model in ("mobile", "tinyclip39"):
            h1, h5 = [count(row[f"{model}_{m}"], n, f"{s} {model} {m}") for m in METRICS]
            check(h1 <= h5, f"{s} {model}: Hit@1 <= Hit@5")

    deployed = index_rows(read_csv("deployed_int8_quality.csv"), ("set", "metric"),
                          [(s, m) for s in [*SETS, TOTAL] for m in METRICS], "FP32/INT8")
    for (s, metric), row in deployed.items():
        n = 110 if s == TOTAL else SETS[s][0]
        candidates = "10-16" if s == TOTAL else str(SETS[s][1])
        check(int(row["queries"]) == n and row["candidates"] == candidates, f"{s} {metric}: scope")
        f, i, b, c, same = [count(row[k], n, f"{s} {metric} {k}") for k in
                            ("fp32_hits", "int8_hits", "only_fp32", "only_int8", "same_top1_image")]
        both = f - b
        check(both == i - c and both >= 0 and both + b + c <= n,
              f"{s} {metric}: paired counts reconcile")
        check(same == int(deployed[(s, "hit1")]["same_top1_image"]), f"{s}: same-top1 agrees across metrics")
        if metric == "hit1":
            check(b + c <= n - same, f"{s}: changed correctness requires changed top1")
        else:
            for field in ("fp32_hits", "int8_hits"):
                check(int(deployed[(s, "hit1")][field]) <= int(row[field]), f"{s} {field}: Hit@1 <= Hit@5")
        if s == TOTAL:
            for field in ("queries", "fp32_hits", "int8_hits", "only_fp32", "only_int8", "same_top1_image"):
                check(int(row[field]) == sum(int(deployed[(part, metric)][field]) for part in SETS),
                      f"FP32/INT8 {metric}: aggregate {field}")
            check(all(row[k] == "" for k in ("int8_wilson95_low", "int8_wilson95_high", "exact_mcnemar_p")),
                  f"{metric}: descriptive aggregate has no pooled inference")
        else:
            check(f == int(deeper[(s,)][f"tinyclip39_{metric}"]), f"{s} {metric}: FP32 matches deeper quality")
            low, high = wilson(i, n)
            check(close(low, row["int8_wilson95_low"]) and close(high, row["int8_wilson95_high"]),
                  f"{s} {metric}: INT8 Wilson interval")
            check(close(exact_mcnemar(b, c), row["exact_mcnemar_p"]), f"{s} {metric}: INT8 McNemar")
    check(tuple(int(deployed[(TOTAL, "hit1")][k]) for k in ("fp32_hits", "int8_hits", "same_top1_image"))
          == (85, 83, 97), "headline Hit@1 FP32/INT8/same-top1 = 85/83/97")
    check(tuple(int(deployed[(TOTAL, "hit5")][k]) for k in ("fp32_hits", "int8_hits"))
          == (103, 102), "headline Hit@5 FP32/INT8 = 103/102")

    expected_intervals = [("Hard (model selection)", model, m) for model in MODELS for m in METRICS]
    expected_intervals += [(s, model, m) for s in SETS for model in ("MobileCLIP-S0", "TinyCLIP 39M/16") for m in METRICS]
    intervals = index_rows(read_csv("hit_rate_intervals.csv"), ("set", "model", "metric"),
                           expected_intervals, "intervals")
    for (s, model, metric), row in intervals.items():
        n = 20 if s == "Hard (model selection)" else SETS[s][0]
        check(int(row["queries"]) == n, f"{s} {model} {metric}: denominator")
        hits = count(row["hits"], n, f"{s} {model} {metric}")
        check(close(hits / n, row["rate"]), f"{s} {model} {metric}: rate")
        low, high = wilson(hits, n)
        check(close(low, row["wilson95_low"]) and close(high, row["wilson95_high"]),
              f"{s} {model} {metric}: Wilson interval")
        if s in SETS:
            prefix = "mobile" if model == "MobileCLIP-S0" else "tinyclip39"
            check(hits == int(deeper[(s,)][f"{prefix}_{metric}"]), f"{s} {model} {metric}: deeper quality matches")
            if s == "Hard":
                check(hits == int(intervals[("Hard (model selection)", model, metric)]["hits"]),
                      f"{model} {metric}: Hard stages agree")

    models = index_rows(read_csv("model_comparison.csv"), ("model",), [(m,) for m in MODELS], "models")
    for (model,), row in models.items():
        for metric in METRICS:
            ref = intervals[("Hard (model selection)", model, metric)]
            check(close(float(row[f"{metric}_percent"]), 100 * int(ref["hits"]) / int(ref["queries"])),
                  f"{model} {metric}: model percentage matches counts")
        for field in ("parameters", "images16_seconds", "image_mean_seconds", "text_mean_seconds"):
            positive(row[field], f"{model} {field}")
        check(close(float(row["images16_seconds"]) / 16, row["image_mean_seconds"], 0.0006),
              f"{model}: rounded image mean")

    paired = index_rows(read_csv("paired_model_comparison.csv"), ("set", "metric"),
                        [(s, m) for s in ("Expanded", "New Images") for m in METRICS], "paired models")
    for (s, metric), row in paired.items():
        n = SETS[s][0]
        check(int(row["queries"]) == n, f"{s} {metric}: paired denominator")
        both, b, c, neither = [count(row[k], n, f"{s} {metric} {k}") for k in
                               ("both_hit", "only_tinyclip39", "only_mobileclip_s0", "neither")]
        check(both + b + c + neither == n, f"{s} {metric}: paired cells sum to queries")
        check(both + b == int(deeper[(s,)][f"tinyclip39_{metric}"]) and
              both + c == int(deeper[(s,)][f"mobile_{metric}"]), f"{s} {metric}: paired marginals match")
        check(close(exact_mcnemar(b, c), row["exact_mcnemar_p"]), f"{s} {metric}: model-selection McNemar")

    temporal = index_rows(read_csv("temporal_cases.csv"), ("observation_relative_day", "window_hours"),
                          [("D0", "2"), ("D0", "24"), ("D0", "168"), ("D-3", "2"), ("D-3", "168")], "temporal cases")
    for key, row in temporal.items():
        n = int(row["compared"])
        check(n > 0 and row["target_included"] in ("true", "false"), f"{key}: temporal scope")
        if row["target_included"] == "true":
            rank, score = int(row["target_rank"]), float(row["target_score"])
            check(1 <= rank <= n and math.isfinite(score) and -1 <= score <= 1, f"{key}: rank and cosine")
        else:
            check(row["target_rank"] == row["target_score"] == "", f"{key}: absent target has no result")
    print("\nAll public evidence checks passed.")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, ValueError, KeyError, TypeError, OSError, ZeroDivisionError) as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        sys.exit(1)
