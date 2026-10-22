#!/usr/bin/env python3
"""Cost cap for the sealed review lane (failure list written before the fix; offline: a stub stands in for the claude CLI).

A paid batch must not cross its cap. The cap is checked BEFORE every single review against a pessimistic per-review estimate,
counting the money already recorded, the reviews in flight (each at the estimate) and the review about to start. The failure list:
  X1 a batch whose third review would cross the cap stops after the second (serial)
  X2 the same with parallel workers: reservations for reviews in flight count, so no more than two start
  X3 the cap is inclusive: a review whose estimate lands exactly on the cap may start
  X4 a cap without an estimate is refused at the start (nothing runs), because an unknown cost cannot be bounded
  X5 no cap set: every review runs, exit 0 (existing behavior unchanged)
  X6 money already recorded in the output folder counts (a resumed run does not get a fresh budget)
  X7 a review that fails without a usage record is still charged at the estimate
  X8 not-started reviews are listed, the exit code is nonzero and the summary says the cap stopped the batch
  X9 an actual cost above the estimate is reported (the estimate was too low), and later reviews are judged on actual money
"""
import json, os, pathlib, subprocess, tempfile, textwrap, unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
LANE = ROOT / "evals" / "tools" / "run_reviews.sh"
STUB = textwrap.dedent("""\
    #!/usr/bin/env bash
    . "@CONF@"
    echo x >> "$STUB_CALLS"
    cat > /dev/null
    [ -n "${STUB_SLEEP:-}" ] && sleep "$STUB_SLEEP"
    if [ -n "${STUB_FAIL:-}" ]; then echo "boom" >&2; exit 1; fi
    cat <<JSON
    {"result": "report\\n```json\\n{\\"verdict\\": \\"SHIP\\", \\"findings\\": []}\\n```", "total_cost_usd": ${STUB_COST:-0.40}, "is_error": false,
     "modelUsage": {"stub-model": {"outputTokens": 10}}, "duration_ms": 1, "num_turns": 1}
    JSON
""")


def make_cases(root, n):
    for i in range(1, n + 1):
        d = root / f"case-{i:02d}"
        (d / "work").mkdir(parents=True)
        (d / "request.md").write_text("Review this.\n"); (d / "context.md").write_text("Context.\n"); (d / "work" / "a.txt").write_text("ok\n")
        (d / "expected.json").write_text(json.dumps({"control": True, "planted": [], "proof": {"shell": "true"}}))


class T(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); t = self.t = pathlib.Path(self.tmp.name)
        self.cases = t / "cases"; self.cases.mkdir(); make_cases(self.cases, 5)
        self.bin = t / "bin"; self.bin.mkdir(); self.conf = self.bin / "stub.conf"; self.calls = t / "calls"
        s = self.bin / "claude"; s.write_text(STUB.replace("@CONF@", str(self.conf))); s.chmod(0o755)
        self.out = t / "out"; (t / "skill.md").write_text("skill\n")

    def tearDown(self):
        self.tmp.cleanup()

    def run_lane(self, par="1", stub=None, **env):
        import shlex
        stub = {"STUB_CALLS": str(self.calls), **(stub or {})}
        self.conf.write_text("".join(f"export {k}={shlex.quote(v)}\n" for k, v in stub.items()))
        e = {**os.environ, "PATH": f"{self.bin}:{os.environ['PATH']}", "CASES": str(self.cases), **env}
        e.pop("MAX_COST_USD", None) if "MAX_COST_USD" not in env else None
        return subprocess.run(["bash", str(LANE), str(self.t / "skill.md"), str(self.out), par], capture_output=True, text=True, env=e, cwd=self.t, timeout=300)

    def n_calls(self):
        return len(self.calls.read_text().splitlines()) if self.calls.exists() else 0

    def test_x1_third_review_would_cross_the_cap(self):
        r = self.run_lane(MAX_COST_USD="1.00", EST_REVIEW_USD="0.50")
        self.assertEqual(self.n_calls(), 2, r.stdout + r.stderr)
        self.assertEqual(sorted(p.name for p in self.out.glob("case-*.md")), ["case-01.md", "case-02.md"])

    def test_x2_parallel_reservations(self):
        r = self.run_lane(par="3", stub={"STUB_SLEEP": "2"}, MAX_COST_USD="1.00", EST_REVIEW_USD="0.50")
        self.assertEqual(self.n_calls(), 2, r.stdout + r.stderr)

    def test_x3_cap_is_inclusive(self):
        self.run_lane(MAX_COST_USD="0.90", EST_REVIEW_USD="0.45", stub={"STUB_COST": "0.45"})
        self.assertEqual(self.n_calls(), 2)

    def test_x4_cap_without_estimate_refused(self):
        r = self.run_lane(MAX_COST_USD="1.00")
        self.assertNotEqual(r.returncode, 0); self.assertEqual(self.n_calls(), 0); self.assertIn("EST_REVIEW_USD", r.stdout + r.stderr)

    def test_x5_no_cap_runs_everything(self):
        r = self.run_lane()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr); self.assertEqual(self.n_calls(), 5)

    def test_x6_recorded_money_counts(self):
        self.run_lane(MAX_COST_USD="1.00", EST_REVIEW_USD="0.50")      # spends 0.80 on two reviews
        before = self.n_calls()
        r = self.run_lane(MAX_COST_USD="1.00", EST_REVIEW_USD="0.50")  # resumed: 0.80 + 0.50 > 1.00, nothing may start
        self.assertEqual(self.n_calls(), before, r.stdout + r.stderr)

    def test_x7_failed_review_is_charged_at_the_estimate(self):
        self.run_lane(stub={"STUB_FAIL": "1"}, MAX_COST_USD="1.00", EST_REVIEW_USD="0.50")
        self.assertEqual(self.n_calls(), 2)

    def test_x8_skips_listed_and_exit_nonzero(self):
        r = self.run_lane(MAX_COST_USD="1.00", EST_REVIEW_USD="0.50")
        self.assertNotEqual(r.returncode, 0)
        listed = (self.out / "cost_cap_skipped.txt").read_text().split()
        self.assertEqual(listed, ["case-03", "case-04", "case-05"])
        self.assertIn("cap", (r.stdout + r.stderr).lower())

    def test_x9_estimate_too_low_is_reported(self):
        r = self.run_lane(stub={"STUB_COST": "0.90"}, MAX_COST_USD="2.00", EST_REVIEW_USD="0.30")
        self.assertIn("above the estimate", r.stdout + r.stderr)
        self.assertEqual(self.n_calls(), 2, "0.90 + 0.90 recorded, a third needs 0.30 more: 2.10 > 2.00")


if __name__ == "__main__":
    unittest.main()
