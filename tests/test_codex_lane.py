#!/usr/bin/env python3
"""Codex lane isolation and token shapes (failure list written before the fix; offline: a stub stands in for the Codex CLI).

The lane runs the model with a read-only sandbox, which restricts writes, not reads, so the model can read anything the user can.
It must therefore not be handed the whole Codex home. The failure list:
  C1 the model's CODEX_HOME is not the real one and holds only auth.json (a canary file in the real home must not be visible)
  C2 that temporary home is removed after a normal run, after a Codex failure, and after SIGTERM
  C3 the real auth.json is not modified or removed by the run (an unchanged copy stays byte-identical)
  C4 a launcher that needs the real HOME (as an installer under $HOME does) still works although the model's HOME is empty
  C5 a launcher that cannot be found fails the lane at the start with a clear message, not once per case
  C6 JWT-shaped and OAuth token JSON values in the output fail the secret scan, and the lane exits 1 (value never printed)
  C7 a clean run exits 0
"""
import json, os, pathlib, signal, subprocess, sys, tempfile, textwrap, time, unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
LANE = ROOT / "evals" / "tools" / "run_reviews_codex.sh"
SCAN = ROOT / "evals" / "tools" / "scan_secrets.py"
JWT = "eyJhbGciOiJSUzI1NiJ9" + ".eyJzdWIiOiJ0ZXN0LXVzZXIifQ" + ".c2lnbmF0dXJlLXRlc3Qtb25seS14eHh4eHg"
STUB = textwrap.dedent("""\
    #!/usr/bin/env bash
    # stand-in for the codex CLI: records what the model would see, writes a report to the -o file
    # the lane strips the environment (env -i), so the test hands settings to the stub through a file next to it
    . "@CONF@"
    log="$STUB_LOG"
    if [ -n "${STUB_NEEDS_REAL_HOME:-}" ] && [ "$HOME" != "$STUB_NEEDS_REAL_HOME" ]; then echo "stub: HOME is not the installer's" >&2; exit 97; fi
    if [ "${1:-}" = "--version" ]; then echo "codex-cli 0.0.0-stub"; exit 0; fi
    out=""; while [ $# -gt 0 ]; do [ "$1" = "-o" ] && out="$2"; shift; done
    echo "CODEX_HOME=$CODEX_HOME" >> "$log"
    echo "HOME_FILES=$(ls -A "$CODEX_HOME" | tr '\\n' ' ')" >> "$log"
    echo "MODE=$(stat -c %a "$CODEX_HOME")" >> "$log"
    cat > /dev/null
    [ -n "${STUB_FAIL:-}" ] && exit 3
    [ -n "${STUB_SLEEP:-}" ] && sleep "$STUB_SLEEP"
    printf '%s\\n' "${STUB_REPORT:-report text}" > "$out"
    echo "model: stub-model" ; echo "tokens used"; echo "10"
""")


class T(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        t = self.t = pathlib.Path(self.tmp.name)
        self.real = t / "real-codex-home"; self.real.mkdir()
        (self.real / "auth.json").write_text('{"note": "not a token"}\n')
        (self.real / "history.jsonl").write_text("PRIVATE-HISTORY-CANARY\n")
        self.bin = t / "bin"; self.bin.mkdir()
        self.log = t / "stub.log"
        self.out = t / "out"
        self.tmpdir = t / "tmp"; self.tmpdir.mkdir()
        self.stub = self.bin / "codex"
        self.conf = self.bin / "stub.conf"
        self.stub.write_text(STUB.replace("@CONF@", str(self.conf))); self.stub.chmod(0o755)
        self.env = dict(os.environ, PATH=f"{self.bin}:{os.environ['PATH']}", CODEX_HOME=str(self.real), STUB_LOG=str(self.log),
                        TMPDIR=str(self.tmpdir), ONLY="case-01", HOME=str(t / "realhome"))
        (t / "realhome").mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    def settings(self, **extra):
        import shlex
        self.conf.write_text("".join(f"export {k}={shlex.quote(v)}\n" for k, v in {"STUB_LOG": str(self.log), **extra}.items()))

    def lane(self, **extra):
        self.settings(**extra)
        skill = self.t / "SKILL.md"; skill.write_text("skill\n")
        return subprocess.run(["bash", str(LANE), str(skill), str(self.out), "1"], capture_output=True, text=True, env=self.env, timeout=120)

    def leftovers(self):
        return [p.name for p in self.tmpdir.iterdir() if p.name.startswith("codex-lane-")]

    def test_c1_c7_clean_run(self):
        r = self.lane()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        log = self.log.read_text()
        self.assertNotIn(str(self.real), log.split("CODEX_HOME=")[1].splitlines()[0], "C1: the model got the real home")
        self.assertIn("HOME_FILES=auth.json", log); self.assertNotIn("history.jsonl", log)
        self.assertIn("MODE=700", log)

    def test_c2_removed_after_success_and_failure(self):
        self.lane(); self.assertEqual(self.leftovers(), [], "after a normal run")
        self.lane(STUB_FAIL="1"); self.assertEqual(self.leftovers(), [], "after a Codex failure")

    def test_c2_removed_after_sigterm(self):
        skill = self.t / "SKILL.md"; skill.write_text("skill\n")
        self.settings(STUB_SLEEP="30")
        p = subprocess.Popen(["bash", str(LANE), str(skill), str(self.out), "1"], env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
        for _ in range(100):
            if self.leftovers() and self.log.exists(): break
            time.sleep(0.1)
        self.assertTrue(self.leftovers(), "the temporary home never appeared")
        os.killpg(p.pid, signal.SIGTERM); p.wait(timeout=30)
        time.sleep(0.5)
        self.assertEqual(self.leftovers(), [], "after SIGTERM")

    def test_c3_real_auth_untouched(self):
        before = (self.real / "auth.json").read_bytes()
        self.lane()
        self.assertEqual((self.real / "auth.json").read_bytes(), before)
        self.assertTrue((self.real / "history.jsonl").exists())

    def test_c4_launcher_needing_real_home(self):
        r = self.lane(STUB_NEEDS_REAL_HOME=self.env["HOME"])
        self.assertEqual(r.returncode, 0, "C4: " + r.stdout + r.stderr)
        self.assertTrue((self.out / "case-01.md").exists())

    def test_c5_missing_launcher(self):
        self.stub.unlink(); self.settings()
        env = {**self.env, "PATH": "/usr/bin:/bin"}
        skill = self.t / "SKILL.md"; skill.write_text("skill\n")
        r = subprocess.run(["bash", str(LANE), str(skill), str(self.out), "1"], capture_output=True, text=True, env=env, timeout=60)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("codex", (r.stdout + r.stderr).lower()); self.assertEqual(self.leftovers(), [])

    def test_c6_token_in_output_fails_scan(self):
        for report in (f"leaked {JWT}", '{"access_token": "' + "A" * 40 + '"}', '"refresh_token":"' + "b" * 40 + '"'):
            r = self.lane(STUB_REPORT=report)
            self.assertEqual(r.returncode, 1, report[:20] + " " + r.stdout + r.stderr)
            self.assertNotIn(JWT, r.stdout + r.stderr); self.assertNotIn("A" * 40, r.stdout + r.stderr)
            subprocess.run(["rm", "-rf", str(self.out)])

    def test_c6_scan_flags_jwt_directly(self):
        d = self.t / "x"; d.mkdir(); (d / "r.md").write_text(f"token {JWT}\n")
        r = subprocess.run([sys.executable, str(SCAN), str(d)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1, r.stdout); self.assertNotIn(JWT, r.stdout)


if __name__ == "__main__":
    unittest.main()
