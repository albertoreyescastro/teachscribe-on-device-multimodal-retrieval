#!/usr/bin/env python3
"""Mutation tests for independent public-evidence tooling (stdlib only)."""
import contextlib
import csv
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import verify_stats as verifier


class EvidenceVerificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.data = Path(self.temp.name) / "data"
        shutil.copytree(verifier.DATA, self.data)

    def verify(self):
        with patch.object(verifier, "DATA", self.data), contextlib.redirect_stdout(io.StringIO()):
            verifier.main()

    def mutate_csv(self, filename, index, field, value):
        path = self.data / filename
        with path.open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            fields, rows = reader.fieldnames, list(reader)
        rows[index][field] = str(value)
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def test_intact_evidence_passes(self):
        self.verify()

    def test_summary_mutations_fail(self):
        path = self.data / "recomputed_statistics.json"
        original = json.loads(path.read_text())
        for field in original:
            with self.subTest(field=field):
                changed = dict(original)
                changed[field] = 999 if field == "max_ms" else changed[field] + 1
                path.write_text(json.dumps(changed))
                with self.assertRaisesRegex(AssertionError, f"sustained statistics: {field}"):
                    self.verify()
        path.write_text(json.dumps(original))

    def test_csv_mutations_fail(self):
        cases = [
            ("sustained_search_108_runs.csv", 0, "total_ms", "999", "sustained statistics: mean_ms"),
            ("sustained_search_108_runs.csv", 1, "run", "1", "ordered unique run IDs"),
            ("sustained_search_108_runs.csv", 0, "total_ms", "nan", "finite positive value"),
            ("deployed_int8_quality.csv", 0, "int8_hits", "19", "paired counts reconcile"),
            ("deployed_int8_quality.csv", 0, "queries", "21", "scope"),
            ("deployed_int8_quality.csv", 0, "int8_wilson95_low", "0.1", "INT8 Wilson interval"),
            ("deployed_int8_quality.csv", 0, "exact_mcnemar_p", "0.5", "INT8 McNemar"),
            ("deployed_int8_quality.csv", 6, "only_fp32", "7", "paired counts reconcile"),
            ("deployed_int8_quality.csv", 1, "same_top1_image", "16", "same-top1 agrees"),
            ("model_comparison.csv", 4, "hit1_percent", "95", "model percentage matches counts"),
            ("model_comparison.csv", 4, "image_mean_seconds", "9", "rounded image mean"),
            ("model_comparison.csv", 4, "parameters", "-1", "finite positive value"),
            ("hit_rate_intervals.csv", 0, "rate", "0.95", "rate"),
            ("hit_rate_intervals.csv", 0, "wilson95_low", "0.1", "Wilson interval"),
            ("hit_rate_intervals.csv", 0, "queries", "21", "denominator"),
            ("paired_model_comparison.csv", 0, "neither", "11", "paired cells sum"),
            ("paired_model_comparison.csv", 0, "exact_mcnemar_p", "0.1", "model-selection McNemar"),
            ("deeper_quality.csv", 0, "tinyclip39_hit1", "16", "FP32 matches deeper quality"),
            ("startup_5_runs.csv", 0, "js_main_ms", "1", "process precedes JS milestone"),
            ("warm_search_5_runs.csv", 0, "ranking_ms", "-1", "finite positive value"),
            ("temporal_cases.csv", 3, "target_rank", "1", "absent target has no result"),
            ("temporal_cases.csv", 0, "target_score", "2", "rank and cosine"),
        ]
        for filename, index, field, value, message in cases:
            with self.subTest(file=filename, field=field, value=value):
                path = self.data / filename
                original = path.read_bytes()
                self.mutate_csv(filename, index, field, value)
                with self.assertRaisesRegex(AssertionError, message):
                    self.verify()
                path.write_bytes(original)

    def test_missing_duplicate_and_malformed_rows_fail(self):
        path = self.data / "deployed_int8_quality.csv"
        original = path.read_text()
        lines = original.splitlines()
        cases = [
            ("missing row", "\n".join(lines[:-1]) + "\n", "expected keys"),
            ("duplicate row", original + lines[1] + "\n", "unique keys"),
            ("missing cell", original.replace("Hard,20,16,hit1", "Hard,20,hit1", 1), "complete rows"),
            ("extra cell", original.replace("Hard,20,16,hit1", "Hard,20,16,extra,hit1", 1), "complete rows"),
            ("wrong schema", original.replace("fp32_hits", "fp32_hit", 1), "schema"),
        ]
        for label, text, message in cases:
            with self.subTest(case=label):
                path.write_text(text)
                with self.assertRaisesRegex(AssertionError, message):
                    self.verify()
        path.write_text(original)

    def test_consistent_wrong_paired_marginals_fail(self):
        # Preserve total and p-value, but contradict the independent quality table.
        self.mutate_csv("paired_model_comparison.csv", 0, "both_hit", "35")
        self.mutate_csv("paired_model_comparison.csv", 0, "neither", "13")
        with self.assertRaisesRegex(AssertionError, "paired marginals match"):
            self.verify()

    def test_aggregate_must_match_each_set(self):
        # Preserve global totals and paired differences; change just one set's cells.
        self.mutate_csv("deployed_int8_quality.csv", 2, "only_fp32", "3")
        self.mutate_csv("deployed_int8_quality.csv", 2, "only_int8", "5")
        self.mutate_csv("deployed_int8_quality.csv", 2, "exact_mcnemar_p", "0.7265625")
        with self.assertRaisesRegex(AssertionError, "aggregate only_fp32"):
            self.verify()

    def test_cli_exit_status(self):
        script = Path(self.temp.name) / "verify_stats.py"
        shutil.copyfile(Path(verifier.__file__), script)
        good = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
        self.assertEqual(good.returncode, 0, good.stderr)
        self.mutate_csv("model_comparison.csv", 4, "hit1_percent", "95")
        bad = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn("FAIL", bad.stderr)
        self.assertIn("model percentage matches counts", bad.stderr)
        self.assertNotIn("All public evidence checks passed", bad.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
