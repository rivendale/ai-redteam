#!/usr/bin/env python3
"""Offline: the usage record written by evals/tools/run_reviews.sh flags a review that a safety stop sent to a different model.
Failure list (written first): a mixed-model review looks like a pinned-model review; a safety stop leaves no trace; a clean review is flagged;
the report text changes; a failed run is recorded as a report. Synthetic JSON only; no model call."""
import json, os, re, subprocess, sys, tempfile, unittest
from pathlib import Path
SCRIPT = (Path(__file__).resolve().parents[1] / "evals/tools/run_reviews.sh").read_text()
BLOCK = re.search(r"<<'PYX'[^\n]*\n(.*?)\nPYX\n", SCRIPT, re.S).group(1)

def run(result, requested="claude-opus-5-5", **extra):
    with tempfile.TemporaryDirectory() as d:
        d = Path(d); (d / "_meta").mkdir()
        raw = d / "_meta/case-01.claude.json"; raw.write_text(json.dumps({"result": "REPORT TEXT", "subtype": "success", "is_error": False, **result}))
        env = dict(os.environ, MODEL=requested)
        p = subprocess.run([sys.executable, "-c", BLOCK, str(raw), str(d / "case-01.md"), str(d / "_meta/case-01.usage.json")], env=env, capture_output=True, text=True)
        usage = json.loads((d / "_meta/case-01.usage.json").read_text()) if (d / "_meta/case-01.usage.json").exists() else None
        flag = (d / "fallback.txt").read_text() if (d / "fallback.txt").exists() else ""
        text = (d / "case-01.md").read_text() if (d / "case-01.md").exists() else None
        return p.returncode, usage, flag, text

class FallbackFlag(unittest.TestCase):
    def test_clean_review_is_not_flagged(self):
        rc, u, flag, text = run({"modelUsage": {"claude-opus-5-5": {"outputTokens": 900}}})
        self.assertEqual((rc, flag, text, u["mixed_model"], u["fallback_models"], u["safety_stops"]), (0, "", "REPORT TEXT", False, [], 0))
    def test_review_finished_by_another_model_is_flagged(self):
        rc, u, flag, text = run({"safety_stops": 2, "modelUsage": {"claude-opus-5-5": {"outputTokens": 700}, "claude-opus-4-8": {"outputTokens": 7100}}})
        self.assertEqual(rc, 0); self.assertTrue(u["mixed_model"]); self.assertEqual(u["fallback_models"], ["claude-opus-4-8"])
        self.assertEqual(u["output_tokens_by_model"]["claude-opus-4-8"], 7100); self.assertIn("fallback_models=claude-opus-4-8", flag); self.assertEqual(text, "REPORT TEXT")
    def test_safety_stop_without_another_model_is_still_recorded(self):
        rc, u, flag, _ = run({"safety_stops": 1, "modelUsage": {"claude-opus-5-5": {"outputTokens": 50}}})
        self.assertFalse(u["mixed_model"]); self.assertEqual(u["safety_stops"], 1); self.assertIn("safety_stops=1", flag)
    def test_zero_token_secondary_entry_is_not_a_fallback(self):
        rc, u, flag, _ = run({"modelUsage": {"claude-opus-5-5": {"outputTokens": 900}, "claude-haiku-5-5": {"outputTokens": 0}}})
        self.assertFalse(u["mixed_model"]); self.assertEqual(flag, "")
    def test_failed_run_is_an_error_not_a_report(self):
        rc, u, flag, text = run({"is_error": True, "subtype": "error_during_execution"})
        self.assertNotEqual(rc, 0); self.assertIsNone(text)
if __name__ == "__main__": unittest.main()
