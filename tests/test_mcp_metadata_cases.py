#!/usr/bin/env python3
"""Offline checks for the MCP tool-metadata cases.

No model is called. No network call is made.
An oracle report scores full recall.
An empty SHIP scores none.
A High finding on a control is a false alarm.
"""
import importlib.util, json, pathlib, re, subprocess, sys, unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
CASES = ROOT / "evals" / "mcp-metadata" / "cases"


def load_score():
    path = ROOT / "evals" / "score.py"
    spec = importlib.util.spec_from_file_location("mcp_meta_score", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SCORE = load_score()


def sentences(text):
    return [p.strip() for p in re.split(r"(?<=[.!?])\s+", text.replace("\n", " ")) if p.strip()]


class T(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.exps = {e["id"]: e for e in SCORE.load_exps(CASES)}

    def test_prose_limits(self):
        for cid in self.exps:
            d = CASES / cid
            blob = (d / "request.md").read_text() + (d / "context.md").read_text() + (d / "work" / "note.md").read_text()
            self.assertNotIn("\u2014", blob)
            self.assertNotIn("\u2013", blob)
            for sent in sentences(blob):
                self.assertLessEqual(len(sent.split()), 30, sent)

    def test_planted_lines_are_apart_and_hold_their_words(self):
        for exp in self.exps.values():
            lines = (CASES / exp["id"] / "work" / "tools.json").read_text().splitlines()
            nums = []
            for p in exp["planted"]:
                lo, hi = p["lines"]
                chunk = "\n".join(lines[lo - 1:hi]).lower()
                nums.append(lo)
                for w in p["any_words"]:
                    self.assertIn(w.lower(), chunk)
            for i, a in enumerate(nums):
                for b in nums[i + 1:]:
                    self.assertGreater(abs(a - b), 3)

    def test_verify_and_prepare_and_scan(self):
        v = subprocess.run([sys.executable, "evals/tools/verify_cases.py", "--cases", str(CASES)], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(v.returncode, 0, v.stdout + v.stderr)
        self.assertIn("4/4 cases verified", v.stdout)
        out = ROOT / "evals" / "mcp-metadata" / "cases"
        prep = pathlib.Path("/tmp/mcp-meta-prepare")
        if prep.exists():
            subprocess.run(["rm", "-rf", str(prep)], check=True)
        p = subprocess.run([sys.executable, "evals/tools/prepare.py", str(prep), "--cases", str(CASES)], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        for cid in self.exps:
            self.assertFalse((prep / cid / "expected.json").exists())
            self.assertTrue((prep / cid / "work" / "tools.json").exists())
        scan = subprocess.run([sys.executable, "evals/tools/scan_secrets.py", str(out)], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(scan.returncode, 0, scan.stdout + scan.stderr)
        self.assertIn("0 hit", scan.stdout)

    def test_oracle_and_controls(self):
        for exp in self.exps.values():
            got = SCORE.score_case(exp, SCORE.oracle_report(exp))
            self.assertEqual(got["violations"], [], exp["id"])
            if exp["control"]:
                self.assertEqual(got["false_alarm"], 0)
            else:
                self.assertEqual(got["recall_hits"], got["planted"])
                self.assertEqual(got["missed"], [])

    def test_empty_ship_has_no_recall(self):
        for exp in self.exps.values():
            if exp["control"]:
                got = SCORE.score_case(exp, SCORE.rubber_stamp(exp))
                self.assertEqual(got["false_alarm"], 0)
                self.assertEqual(got["violations"], [])
                continue
            got = SCORE.score_case(exp, SCORE.rubber_stamp(exp))
            self.assertEqual(got["recall_hits"], 0)
            self.assertTrue(got["violations"])

    def test_wrong_file_and_wrong_words_score_zero(self):
        for exp in self.exps.values():
            if exp["control"]:
                continue
            word = exp["planted"][0]["any_words"][0]
            wrong_file = SCORE.score_case(exp, {
                "verdict": "REWORK",
                "findings": [SCORE.finding("W", "Critical", "note.md:1", word)],
                "inputs_ledger": {},
            })
            self.assertEqual(wrong_file["recall_hits"], 0, exp["id"])
            wrong_words = SCORE.score_case(exp, {
                "verdict": "REWORK",
                "findings": [SCORE.finding("W", "Critical", "tools.json:1", "The indentation is uneven.")],
                "inputs_ledger": {},
            })
            self.assertEqual(wrong_words["recall_hits"], 0, exp["id"])

    def test_low_severity_is_not_recall(self):
        exp = self.exps["case-01"]
        p = exp["planted"][0]
        got = SCORE.score_case(exp, {
            "verdict": "REWORK",
            "findings": [SCORE.finding("L", "Low", f"tools.json:{p['lines'][0]}", p["any_words"][0])],
            "inputs_ledger": {},
        })
        self.assertEqual(got["recall_hits"], 0)
        self.assertEqual(got["found_any"], 1)
        self.assertIn("P1", got["low_severity"])

    def test_each_planted_line_credits_only_itself(self):
        for exp in self.exps.values():
            if exp["control"]:
                continue
            findings = []
            for p in exp["planted"]:
                findings.append(SCORE.finding(p["id"], p["min_severity"], f"tools.json:{p['lines'][0]}", p["any_words"][0]))
            got = SCORE.score_case(exp, {"verdict": "REWORK", "findings": findings, "inputs_ledger": {}})
            self.assertEqual(got["recall_hits"], got["planted"], exp["id"])
            one = SCORE.score_case(exp, {"verdict": "REWORK", "findings": findings[:1], "inputs_ledger": {}})
            self.assertEqual(one["recall_hits"], 1, exp["id"])

    def test_high_on_a_control_is_a_false_alarm(self):
        exp = self.exps["case-02"]
        got = SCORE.score_case(exp, {
            "verdict": "REWORK",
            "findings": [SCORE.finding("H", "High", "tools.json:6", "The lookup might confuse a reader.")],
            "inputs_ledger": {},
        })
        self.assertEqual(got["false_alarm"], 1)
        self.assertTrue(got["violations"])


if __name__ == "__main__":
    unittest.main()
