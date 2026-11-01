#!/usr/bin/env python3
"""Pre-registration in the review lanes (offline: a stub stands in for the claude or codex CLI, and DRY_RUN stops before any review).

Before the first review, run_reviews.sh and run_reviews_codex.sh must write OUTDIR/_meta/prereg.json (both through prereg.py): the skill path, its sha256 and git identity, the sha256
of every case input the reviewer will see, the model and CLI version when known, the gate rule text, and the UTC start time.
  P1 DRY_RUN=1 writes the record and starts no review (the stub is never called, no report is written, exit 0)
  P2 the record holds the skill hash, one entry per prepared case whose file hashes are those of the case's own files, never
     expected.json, the gate rule, the requested model, the CLI version and a UTC start time
  P3 the record exists before the first review starts (the stub looks for it when it is called)
  P4 a resumed run keeps the first record and adds a resume record; a resumed run with a different skill text is refused and
     reviews nothing
  P5 no gate rule given: recorded as not given, with a warning; GATE_RULE_FILE records the file's text and hash
  P6 a skill file in the repository records its git blob and last commit, and says whether it matches HEAD
  P7 DRY_RUN=0 (and false, no, off, empty) means off: the reviews run; a value that is neither on nor off is refused before anything
  P8 GATE_MARGIN is recorded as gate_rule.margin; a negative or non-numeric margin is refused and nothing is reviewed
  Codex lane (a stub `codex` on PATH; the real CLI is never executed):
  Q1 DRY_RUN=1 writes the same record shape (cli codex, the CODEX_MODEL, the codex runner's hash) and calls the stub only for
     its --version probe; no sign-in copy is made
  Q2 a real run writes the record before the first review; DRY_RUN=0 runs the reviews
  Q3 a codex run into an OUTDIR pre-registered by the claude lane is refused
The stubs' heredocs are quoted (<<'JSON'), so nothing in them expands.
"""
import hashlib, json, os, pathlib, subprocess, tempfile, textwrap, unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
LANE = ROOT / "evals" / "tools" / "run_reviews.sh"
STUB = textwrap.dedent("""\
    #!/usr/bin/env bash
    . "@CONF@"
    if [ -f "$OUT/_meta/prereg.json" ]; then echo yes >> "$STUB_CALLS"; else echo no >> "$STUB_CALLS"; fi
    cat > /dev/null
    cat <<'JSON'
    {"result": "report\\n```json\\n{\\"verdict\\": \\"SHIP\\", \\"findings\\": []}\\n```", "total_cost_usd": 0.01, "is_error": false,
     "modelUsage": {"stub-model": {"outputTokens": 10}}, "duration_ms": 1, "num_turns": 1}
    JSON
""")
CODEX_LANE = ROOT / "evals" / "tools" / "run_reviews_codex.sh"
CODEX_STUB = textwrap.dedent("""\
    #!/usr/bin/env bash
    # stand-in for the codex CLI: answers the launcher probe, notes whether the record existed, writes a report to the -o file
    . "@CONF@"
    if [ "${1:-}" = "--version" ]; then echo version >> "$STUB_CALLS"; echo "codex-cli 0.0.0-stub"; exit 0; fi
    if [ -f "$STUB_OUT/_meta/prereg.json" ]; then echo yes >> "$STUB_CALLS"; else echo no >> "$STUB_CALLS"; fi
    out=; while [ $# -gt 0 ]; do [ "$1" = -o ] && out=$2; shift; done
    cat > /dev/null
    cat > "$out" <<'REPORT'
    report
    ```json
    {"verdict": "SHIP", "findings": []}
    ```
    REPORT
    cat <<'LOG'
    OpenAI Codex v0.0.0
    model: stub-model
    tokens used
    10
    LOG
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

    def run_lane(self, skill=None, lane=None, **env):
        e = {**os.environ, "PATH": f"{self.bin}:{os.environ['PATH']}", "CASES": str(self.cases), **env}
        for k in ("MAX_COST_USD", "EST_REVIEW_USD", "GATE_RULE", "GATE_RULE_FILE", "GATE_MARGIN", "MODEL", "ANTHROPIC_MODEL", "CLI_VERSION", "DRY_RUN",
                  "ONLY", "CODEX_MODEL", "CODEX_CMD"):
            if k not in env:
                e.pop(k, None)
        return subprocess.run(["bash", str(lane or LANE), str(skill or self.skill), str(self.out), "1"], capture_output=True, text=True, env=e,
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
        self.assertEqual(p["gate_rule"], {"given": True, "text": "recall >= base - 3", "source": "GATE_RULE", "margin": None, "margin_source": None})
        self.assertEqual(p["model"]["cli"], "claude")
        self.assertEqual(p["lane"]["runner"], "run_reviews.sh")
        self.assertIn("no GATE_MARGIN", r.stderr)
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

    def test_p7_dry_run_zero_means_off(self):
        for v in ("0", "false", "no", "off", ""):
            self.out = self.t / f"out-{v or 'empty'}"; self.calls_file.unlink(missing_ok=True)
            r = self.run_lane(DRY_RUN=v, GATE_RULE="x")
            self.assertEqual(r.returncode, 0, v + r.stdout + r.stderr)
            self.assertNotIn("DRY_RUN:", r.stdout, v)
            self.assertEqual(self.calls(), ["yes", "yes", "yes"], v)
            self.assertFalse(self.rec()["lane"]["dry_run"], v)
        for v in ("true", "yes", "on"):
            self.out = self.t / f"out-{v}"
            r = self.run_lane(DRY_RUN=v)
            self.assertEqual(r.returncode, 0, v + r.stderr)
            self.assertTrue(self.rec()["lane"]["dry_run"], v)
        self.calls_file.unlink(missing_ok=True); self.out = self.t / "out-bad"
        r = self.run_lane(DRY_RUN="maybe")
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertIn("neither on", r.stderr)
        self.assertEqual(self.calls(), [])
        self.assertFalse((self.out / "_meta" / "prereg.json").exists())

    def test_p8_gate_margin(self):
        r = self.run_lane(DRY_RUN="1", GATE_RULE="evals/README.md#gate-rule", GATE_MARGIN="5")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.rec()["gate_rule"]["margin"], 5)
        self.assertEqual(self.rec()["gate_rule"]["margin_source"], "GATE_MARGIN")
        self.assertNotIn("no GATE_MARGIN", r.stderr)
        for bad in ("-1", "three", "nan", "inf"):
            self.out = self.t / f"out-{bad}"
            r = self.run_lane(GATE_MARGIN=bad, GATE_RULE="x")
            self.assertNotEqual(r.returncode, 0, bad)
            self.assertIn("GATE_MARGIN", r.stderr, bad)
            self.assertFalse((self.out / "_meta" / "prereg.json").exists(), bad)
            self.assertEqual(self.calls(), [], bad)


class Codex(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); t = self.t = pathlib.Path(self.tmp.name)
        self.cases = t / "cases"; self.cases.mkdir(); make_cases(self.cases, 2)
        self.bin = t / "bin"; self.bin.mkdir(); self.conf = self.bin / "stub.conf"; self.calls_file = t / "calls"
        s = self.bin / "codex"; s.write_text(CODEX_STUB.replace("@CONF@", str(self.conf))); s.chmod(0o755)
        self.out = t / "out"; self.skill = t / "skill.md"; self.skill.write_text("skill v1\n")
        self.real = t / "codex-home"; self.real.mkdir(); (self.real / "auth.json").write_text('{"note": "not a token"}\n')
        self.tmpdir = t / "tmp"; self.tmpdir.mkdir(); (t / "home").mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def run_lane(self, lane=CODEX_LANE, **env):
        self.conf.write_text(f"export STUB_CALLS={self.calls_file} STUB_OUT={self.out}\n")
        e = {k: v for k, v in os.environ.items() if k not in ("GATE_RULE", "GATE_RULE_FILE", "GATE_MARGIN", "DRY_RUN", "ONLY", "CODEX_CMD",
                                                               "CLI_VERSION", "MODEL", "ANTHROPIC_MODEL", "MAX_COST_USD", "EST_REVIEW_USD")}
        e.update(PATH=f"{self.bin}:{os.environ['PATH']}", CASES=str(self.cases), CODEX_HOME=str(self.real), HOME=str(self.t / "home"),
                 TMPDIR=str(self.tmpdir), CODEX_MODEL="stub-model", **env)
        return subprocess.run(["bash", str(lane), str(self.skill), str(self.out), "1"], capture_output=True, text=True, env=e, cwd=self.t,
                              stdin=subprocess.DEVNULL, timeout=300)

    def calls(self):
        return self.calls_file.read_text().split() if self.calls_file.exists() else []

    def rec(self):
        return json.loads((self.out / "_meta" / "prereg.json").read_text())

    def test_q1_dry_run_same_record(self):
        r = self.run_lane(DRY_RUN="1", GATE_RULE="evals/README.md#gate-rule", GATE_MARGIN="4", CLI_VERSION="0.0.1")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("DRY_RUN", r.stdout)
        self.assertEqual(self.calls(), ["version"])                      # only the launcher probe; no review
        self.assertEqual(list(self.out.glob("case-*.md")), [])
        self.assertEqual([p for p in self.tmpdir.iterdir() if p.name.startswith("codex-lane-")], [], "no sign-in copy on a dry run")
        p = self.rec()
        self.assertEqual(p["schema"], "prereg-1")
        self.assertEqual(p["skill"]["sha256"], sha(self.skill))
        self.assertEqual(sorted(p["cases"]["inputs"]), ["case-01", "case-02"])
        for rel, h in p["cases"]["inputs"]["case-01"]["files"].items():
            self.assertEqual(h, sha(self.cases / "case-01" / rel), rel)
        self.assertNotIn("expected.json", json.dumps(p))
        self.assertEqual(p["model"]["cli"], "codex")
        self.assertEqual(p["model"]["requested"], "stub-model")
        self.assertEqual(p["model"]["cli_version"], "0.0.1")
        self.assertEqual(p["model"]["cli_path"], str(self.bin / "codex"))
        self.assertEqual(p["gate_rule"]["margin"], 4)
        self.assertEqual(p["lane"]["runner"], "run_reviews_codex.sh")
        self.assertEqual(p["lane"]["runner_sha256"], sha(CODEX_LANE))
        self.assertTrue(p["lane"]["dry_run"])
        # the same shape as the claude lane's record
        ref = T("test_p1_dry_run_reviews_nothing"); ref.setUp()
        try:
            ref.run_lane(DRY_RUN="1")
            self.assertEqual({k: sorted(v) if isinstance(v, dict) else None for k, v in p.items()},
                             {k: sorted(v) if isinstance(v, dict) else None for k, v in ref.rec().items()})
        finally:
            ref.tearDown()

    def test_q2_written_before_first_review(self):
        r = self.run_lane(DRY_RUN="0", GATE_RULE="x", GATE_MARGIN="3")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.calls(), ["version", "yes", "yes"])
        self.assertEqual(len(list(self.out.glob("case-*.md"))), 2)
        self.assertFalse(self.rec()["lane"]["dry_run"])
        r = self.run_lane(DRY_RUN="2")
        self.assertEqual(r.returncode, 2, r.stderr)

    def test_q3_refuses_an_outdir_from_the_other_lane(self):
        e = {**os.environ, "PATH": f"{self.bin}:{os.environ['PATH']}", "CASES": str(self.cases), "DRY_RUN": "1"}
        r = subprocess.run(["bash", str(LANE), str(self.skill), str(self.out), "1"], capture_output=True, text=True, env=e, cwd=self.t,
                           stdin=subprocess.DEVNULL, timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr)
        r = self.run_lane(GATE_RULE="x")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("written by run_reviews.sh", r.stderr)
        self.assertEqual(self.calls(), ["version"])


if __name__ == "__main__":
    unittest.main()
