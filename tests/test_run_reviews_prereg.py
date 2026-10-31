#!/usr/bin/env python3
"""Pre-registration in the sealed review lane (offline: a stub stands in for the claude CLI, and DRY_RUN stops before any review).

Before the first review, run_reviews.sh must write OUTDIR/_meta/prereg.json: the skill path, its sha256 and git identity, the sha256
of every case input the reviewer will see, the model and CLI version when known, the gate rule text, and the UTC start time.
  P1 DRY_RUN=1 writes the record and starts no review (the stub is never called, no report is written, exit 0)
  P2 the record holds the skill hash, one entry per prepared case whose file hashes are those of the case's own files, never
     expected.json, the gate rule, the requested model, the CLI version and a UTC start time
  P3 the record exists before the first review starts (the stub looks for it when it is called)
  P4 a resumed run keeps the first record and adds a resume record; a resumed run with a different skill text is refused and
     reviews nothing
  P5 no gate rule given: recorded as not given, with a warning; GATE_RULE_FILE records the file's text and hash
  P6 a skill file in the repository records its git blob and last commit, and says whether it matches HEAD
"""
import hashlib, json, os, pathlib, subprocess, tempfile, textwrap, unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
LANE = ROOT / "evals" / "tools" / "run_reviews.sh"
STUB = textwrap.dedent("""\
    #!/usr/bin/env bash
    . "@CONF@"
    if [ -f "$OUT/_meta/prereg.json" ]; then echo yes >> "$STUB_CALLS"; else echo no >> "$STUB_CALLS"; fi
    cat > /dev/null
    cat <<JSON
    {"result": "report\\n```json\\n{\\"verdict\\": \\"SHIP\\", \\"findings\\": []}\\n```", "total_cost_usd": 0.01, "is_error": false,
     "modelUsage": {"stub-model": {"outputTokens": 10}}, "duration_ms": 1, "num_turns": 1}
    JSON
""")


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def make_cases(root, n):
    for i in range(1, n + 1):
        d = root / f"case-{i:02d}"
        (d / "work" / "sub").mkdir(parents=True)
        (d / "request.md").write_text(f"Review this {i}.\n"); (d / "context.md").write_text("Context.\n")
        (d / "work" / "a.txt").write_text(f"ok {i}\n"); (d / "work" / "sub" / "b.py").write_text("x = 1\n")
        (d / "expected.json").write_text(json.dumps({"control": True, "planted": [], "proof": {"shell": "true"}}))


class T(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); t = self.t = pathlib.Path(self.tmp.name)
        self.cases = t / "cases"; self.cases.mkdir(); make_cases(self.cases, 3)
        self.bin = t / "bin"; self.bin.mkdir(); self.conf = self.bin / "stub.conf"; self.calls_file = t / "calls"
        s = self.bin / "claude"; s.write_text(STUB.replace("@CONF@", str(self.conf))); s.chmod(0o755)
        self.conf.write_text(f"export STUB_CALLS={self.calls_file}\n")
        self.out = t / "out"; self.skill = t / "skill.md"; self.skill.write_text("skill v1\n")

    def tearDown(self):
        self.tmp.cleanup()

    def run_lane(self, skill=None, **env):
        e = {**os.environ, "PATH": f"{self.bin}:{os.environ['PATH']}", "CASES": str(self.cases), **env}
        for k in ("MAX_COST_USD", "EST_REVIEW_USD", "GATE_RULE", "GATE_RULE_FILE", "MODEL", "ANTHROPIC_MODEL", "CLI_VERSION", "DRY_RUN", "ONLY"):
            if k not in env:
                e.pop(k, None)
        return subprocess.run(["bash", str(LANE), str(skill or self.skill), str(self.out), "1"], capture_output=True, text=True, env=e,
                              cwd=self.t, stdin=subprocess.DEVNULL, timeout=300)

    def calls(self):
        return self.calls_file.read_text().split() if self.calls_file.exists() else []

    def rec(self, name="prereg.json"):
        return json.loads((self.out / "_meta" / name).read_text())

    def test_p1_dry_run_reviews_nothing(self):
        r = self.run_lane(DRY_RUN="1")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.calls(), [])
        self.assertEqual(list(self.out.glob("case-*.md")), [])
        self.assertTrue((self.out / "_meta" / "prereg.json").is_file())
        self.assertTrue(self.rec()["lane"]["dry_run"])

    def test_p2_record_contents(self):
        r = self.run_lane(DRY_RUN="1", GATE_RULE="recall >= base - 3", MODEL="claude-test-model", CLI_VERSION="9.9.9")
        self.assertEqual(r.returncode, 0, r.stderr)
        p = self.rec()
        self.assertEqual(p["schema"], "prereg-1")
        self.assertEqual(p["skill"]["sha256"], sha(self.skill))
        self.assertRegex(p["started_utc"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
        self.assertEqual(sorted(p["cases"]["inputs"]), ["case-01", "case-02", "case-03"])
        files = p["cases"]["inputs"]["case-02"]["files"]
        self.assertEqual(sorted(files), ["context.md", "request.md", "work/a.txt", "work/sub/b.py"])
        for rel, h in files.items():
            self.assertEqual(h, sha(self.cases / "case-02" / rel), rel)
        self.assertNotIn("expected.json", json.dumps(p))
        self.assertNotEqual(p["cases"]["inputs"]["case-01"]["sha256"], p["cases"]["inputs"]["case-02"]["sha256"])
        self.assertEqual(p["gate_rule"], {"given": True, "text": "recall >= base - 3", "source": "GATE_RULE"})
        self.assertEqual(p["model"]["requested"], "claude-test-model")
        self.assertEqual(p["model"]["cli_version"], "9.9.9")
        self.assertEqual(p["lane"]["runner_sha256"], sha(LANE))

    def test_p3_written_before_first_review(self):
        r = self.run_lane(GATE_RULE="x")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.calls(), ["yes", "yes", "yes"])
        self.assertEqual(len(list(self.out.glob("case-*.md"))), 3)

    def test_p4_resume_keeps_first_and_refuses_changed_skill(self):
        self.run_lane(DRY_RUN="1", GATE_RULE="x")
        first = (self.out / "_meta" / "prereg.json").read_text()
        r = self.run_lane(GATE_RULE="x")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((self.out / "_meta" / "prereg.json").read_text(), first)
        self.assertEqual(len(list((self.out / "_meta").glob("prereg-resume-*.json"))), 1)
        self.skill.write_text("skill v2\n")
        (self.out / "case-01.md").unlink()
        n = len(self.calls())
        r = self.run_lane(GATE_RULE="x")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("different skill text", r.stderr)
        self.assertEqual(len(self.calls()), n)
        self.assertFalse((self.out / "case-01.md").exists())

    def test_p5_gate_rule_absent_or_from_file(self):
        r = self.run_lane(DRY_RUN="1")
        self.assertIn("no GATE_RULE", r.stderr)
        self.assertFalse(self.rec()["gate_rule"]["given"])
        g = self.t / "gate.txt"; g.write_text("1. recall: candidate >= base - 3\n")
        self.out = self.t / "out2"
        self.run_lane(DRY_RUN="1", GATE_RULE_FILE=str(g))
        gr = self.rec()["gate_rule"]
        self.assertEqual(gr["text"], g.read_text())
        self.assertIn(sha(g), gr["source"])

    def test_p6_repository_skill_has_git_identity(self):
        rel = "skills/redteam/SKILL.md"
        e = {"CASES": str(ROOT / "evals" / "cases"), "ONLY": "case-01"}
        r = self.run_lane(skill=ROOT / rel, DRY_RUN="1", **e)
        self.assertEqual(r.returncode, 0, r.stderr)
        s = self.rec()["skill"]
        self.assertEqual(s["path"], rel)
        if (ROOT / ".git").exists():
            self.assertRegex(s["git_blob"] or "", r"^[0-9a-f]{40}$")
            self.assertRegex(s["git_last_commit"] or "", r"^[0-9a-f]{40}$")
            dirty = subprocess.run(["git", "-C", str(ROOT), "diff", "--quiet", "HEAD", "--", rel]).returncode != 0
            self.assertEqual(s["committed"], not dirty)
        self.assertEqual(list(self.rec()["cases"]["inputs"]), ["case-01"])
        self.assertNotIn("expected.json", json.dumps(self.rec()))


if __name__ == "__main__":
    unittest.main()
