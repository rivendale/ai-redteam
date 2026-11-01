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
  P8 GATE_MARGIN is recorded as gate_rule.margin; a negative or non-numeric margin is refused and nothing is reviewed;
     GATE_FA_MARGIN is recorded as gate_rule.fa_margin and falls back to GATE_MARGIN
  P9 a resume is refused when the runner's bytes (a copied runner, edited) or prereg.py changed, not only its name
  P10 a resume is refused when GATE_RULE, GATE_MARGIN or GATE_FA_MARGIN differs from the first record
  P11 resume records never overwrite one another, even when two are written in the same clock tick
  Codex lane (a stub `codex` on PATH; the real CLI is never executed):
  Q1 DRY_RUN=1 writes the same record shape (cli codex, the CODEX_MODEL, the codex runner's hash) and calls the stub only for
     its --version probe; the sign-in is never copied (a `cp` wrapper on PATH logs every copy)
  Q2 a real run writes the record before the first review and before the sign-in is copied; DRY_RUN=0 runs the reviews
  Q3 a codex run into an OUTDIR pre-registered by the claude lane is refused
The stubs' heredocs are quoted (<<'JSON'), so nothing in them expands.
"""
import datetime, hashlib, importlib.util, json, os, pathlib, shutil, subprocess, sys, tempfile, textwrap, types, unittest

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
REAL_CP = shutil.which("cp")
# logs every copy the lane makes, and whether the pre-registration record existed at that moment, then copies
CP_WRAPPER = textwrap.dedent("""\
    #!/usr/bin/env bash
    . "@CONF@"
    if [ -f "$STUB_OUT/_meta/prereg.json" ]; then echo cp:prereg >> "$STUB_CALLS"; else echo cp:none >> "$STUB_CALLS"; fi
    exec "@CP@" "$@"
""")
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
        self.assertEqual(p["gate_rule"], {"given": True, "text": "recall >= base - 3", "source": "GATE_RULE", "margin": None, "margin_source": None,
                                          "fa_margin": None, "fa_margin_source": None})
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

    def test_p8_fa_margin(self):
        self.run_lane(DRY_RUN="1", GATE_MARGIN="5")
        g = self.rec()["gate_rule"]
        self.assertEqual((g["fa_margin"], g["fa_margin_source"]), (5, "GATE_MARGIN"))
        self.out = self.t / "out-fa"
        r = self.run_lane(DRY_RUN="1", GATE_MARGIN="5", GATE_FA_MARGIN="2.5")
        self.assertEqual(r.returncode, 0, r.stderr)
        g = self.rec()["gate_rule"]
        self.assertEqual((g["margin"], g["fa_margin"], g["fa_margin_source"]), (5, 2.5, "GATE_FA_MARGIN"))
        self.out = self.t / "out-fa-bad"
        r = self.run_lane(GATE_MARGIN="5", GATE_FA_MARGIN="inf")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("GATE_FA_MARGIN", r.stderr)
        self.assertEqual(self.calls(), [])

    def scratch_repo(self):
        """A copy of the lane's own files, so a test can edit the runner or prereg.py without touching the checkout."""
        repo = self.t / "repo"; (repo / "evals" / "tools").mkdir(parents=True)
        for f in ("run_reviews.sh", "prereg.py", "prepare.py"):
            shutil.copy2(ROOT / "evals" / "tools" / f, repo / "evals" / "tools" / f)
        return repo

    def test_p9_resume_refused_when_runner_or_prereg_bytes_change(self):
        for edited in ("run_reviews.sh", "prereg.py"):
            repo = self.scratch_repo(); lane = repo / "evals" / "tools" / "run_reviews.sh"
            self.out = self.t / f"out-{edited}"; self.calls_file.unlink(missing_ok=True)
            r = self.run_lane(lane=lane, DRY_RUN="1", GATE_RULE="x")
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertEqual(self.rec()["lane"]["runner_sha256"], sha(lane))
            r = self.run_lane(lane=lane, DRY_RUN="1", GATE_RULE="x")             # unchanged: the resume is accepted
            self.assertEqual(r.returncode, 0, r.stderr)
            with open(repo / "evals" / "tools" / edited, "a") as fh:
                fh.write("\n# edited after the first record\n")
            r = self.run_lane(lane=lane, GATE_RULE="x")
            self.assertNotEqual(r.returncode, 0, edited)
            self.assertIn("changed since", r.stderr, edited)
            self.assertIn("run_reviews.sh" if edited == "run_reviews.sh" else "prereg.py", r.stderr)
            self.assertEqual(self.calls(), [], edited)
            self.assertEqual(list(self.out.glob("case-*.md")), [], edited)
            shutil.rmtree(repo)

    def test_p10_resume_refused_when_rule_or_margin_differs(self):
        base = {"GATE_RULE": "evals/README.md#gate-rule", "GATE_MARGIN": "5"}
        self.run_lane(DRY_RUN="1", **base)
        for change in ({"GATE_RULE": "something else"}, {"GATE_MARGIN": "6"}, {"GATE_MARGIN": ""}, {"GATE_FA_MARGIN": "2"}):
            r = self.run_lane(**{**base, **change})
            self.assertNotEqual(r.returncode, 0, change)
            self.assertIn("differs from the pre-registered value", r.stderr, change)
        self.assertEqual(self.calls(), [])
        r = self.run_lane(DRY_RUN="1", **base)
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_p11_resume_records_do_not_collide(self):
        spec = importlib.util.spec_from_file_location("prereg_under_test", ROOT / "evals" / "tools" / "prereg.py")
        mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
        frozen = datetime.datetime(2026, 11, 1, 12, 0, 0, 123456, tzinfo=datetime.timezone.utc)
        class Frozen(datetime.datetime):
            @classmethod
            def now(cls, tz=None):
                return frozen
        mod.datetime = types.SimpleNamespace(datetime=Frozen, timezone=datetime.timezone)
        prep = self.t / "prep"; shutil.copytree(self.cases / "case-01", prep / "case-01", ignore=shutil.ignore_patterns("expected.json"))
        a = types.SimpleNamespace(repo=str(ROOT), skill=str(self.skill), prep=str(prep), out=str(self.out), parallel="1",
                                  runner=str(LANE), cli="claude", cli_cmd="", model="")
        env = {k: os.environ.pop(k) for k in ("GATE_RULE", "GATE_RULE_FILE", "GATE_MARGIN", "GATE_FA_MARGIN", "DRY_RUN") if k in os.environ}
        try:
            for _ in range(4):
                mod.write(a)
        finally:
            os.environ.update(env)
        names = sorted(p.name for p in (self.out / "_meta").glob("prereg-resume-*.json"))
        self.assertEqual(len(names), 3, names)
        self.assertEqual(len(set(names)), 3)
        self.assertIn("prereg-resume-2026-11-01T120000.123456Z.json", names)


class Codex(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); t = self.t = pathlib.Path(self.tmp.name)
        self.cases = t / "cases"; self.cases.mkdir(); make_cases(self.cases, 2)
        self.bin = t / "bin"; self.bin.mkdir(); self.conf = self.bin / "stub.conf"; self.calls_file = t / "calls"
        s = self.bin / "codex"; s.write_text(CODEX_STUB.replace("@CONF@", str(self.conf))); s.chmod(0o755)
        w = self.bin / "cp"; w.write_text(CP_WRAPPER.replace("@CONF@", str(self.conf)).replace("@CP@", REAL_CP)); w.chmod(0o755)
        self.out = t / "out"; self.skill = t / "skill.md"; self.skill.write_text("skill v1\n")
        self.real = t / "codex-home"; self.real.mkdir(); (self.real / "auth.json").write_text('{"note": "not a token"}\n')
        self.tmpdir = t / "tmp"; self.tmpdir.mkdir(); (t / "home").mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def run_lane(self, lane=CODEX_LANE, **env):
        self.conf.write_text(f"export STUB_CALLS={self.calls_file} STUB_OUT={self.out}\n")
        e = {k: v for k, v in os.environ.items() if k not in ("GATE_RULE", "GATE_RULE_FILE", "GATE_MARGIN", "GATE_FA_MARGIN", "DRY_RUN", "ONLY", "CODEX_CMD",
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
        self.assertEqual(self.calls(), ["version"])                      # only the launcher probe: no review and no sign-in copy
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
        self.assertEqual(self.calls(), ["version", "cp:prereg", "yes", "yes"])   # the sign-in is copied only after the record exists
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
