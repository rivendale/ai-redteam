#!/usr/bin/env python3
"""Codex lane isolation and token shapes (failure list written before the fix; offline: a stub stands in for the Codex CLI).

The lane runs the model with a read-only sandbox, which restricts writes, not reads, so the model can read anything the user can.
It must therefore not be handed the whole Codex home. The failure list:
  C1 the model's CODEX_HOME is not the real one and holds only auth.json (a canary file in the real home must not be visible)
  C2 that temporary home is removed after a normal run, after a Codex failure, and after SIGTERM
  C2b SIGTERM sent to the lane's own PID ALONE (not its process group) while a review runs: the lane exits promptly, removes the
      temporary home and leaves no running review process behind (a foreground xargs would defer the trap until it finished)
  C2c the same with a review that IGNORES SIGTERM (trap "" TERM, inherited by its children, one of which runs in a process group of
      its own): the lane still ends every descendant (escalates to SIGKILL, including the separate group) and leaves nothing running
  C2d a TERM handler that starts a NEW detached child in its own session during the grace period (in no earlier snapshot): the
      lane freezes what it knows, re-collects until nothing new appears, and kills the lot, so the escapee does not survive
  C3 the real auth.json is not modified or removed by the run, even if the CLI refreshes the token in the temporary home (no write-back:
     a copy-back cannot be made atomic against other Codex sessions, and a stale snapshot must never replace a newer file)
  C3b a real auth.json updated by another session DURING the run keeps its newer content (no rollback to the snapshot), and the lane
     tells the user when the CLI refreshed its token so they know to sign in again if Codex asks
  C4 a launcher that only starts with the real HOME is REFUSED (exit 2, nothing runs); the real HOME is never given to the model process
  C4b the model process runs with an empty temporary HOME that is not the real one (asserted from inside the stub)
  C5 a launcher that cannot be found fails the lane at the start with a clear message, not once per case
  C6 JWT-shaped and OAuth token JSON values in the output fail the secret scan, and the lane exits 1 (value never printed)
  C7 a clean run exits 0
  C8 no CODEX_MODEL: the lane stops at the start (config.toml is not copied, so a silent default must not decide the model)
  C9 the model is passed to the CLI with -m and recorded per review (requested and actual); a different actual model is
     flagged in fallback.txt and the lane warns, so a silent switch cannot go unseen
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
    ORIG_ARGS="$*"
    out=""; while [ $# -gt 0 ]; do [ "$1" = "-o" ] && out="$2"; shift; done
    echo "ARGS=$ORIG_ARGS" >> "$log"
    echo $$ >> "${STUB_PIDS:-/dev/null}"
    echo "CODEX_HOME=$CODEX_HOME" >> "$log"
    echo "EXEC_HOME=$HOME" >> "$log"; echo "EXEC_HOME_FILES=$(ls -A "$HOME" | wc -l)" >> "$log"
    [ -n "${STUB_REFRESH:-}" ] && echo '{"note": "refreshed"}' > "$CODEX_HOME/auth.json"
    [ -n "${STUB_TOUCH_REAL:-}" ] && echo '{"note": "newer from another session"}' > "$STUB_TOUCH_REAL"
    echo "HOME_FILES=$(ls -A "$CODEX_HOME" | tr '\\n' ' ')" >> "$log"
    echo "MODE=$(stat -c %a "$CODEX_HOME")" >> "$log"
    cat > /dev/null
    [ -n "${STUB_FAIL:-}" ] && exit 3
    [ -n "${STUB_IGNORE_TERM:-}" ] && trap "" TERM
    # a TERM handler that starts a detached child in a new session (an escapee the lane could not have recorded beforehand)
    if [ -n "${STUB_ESCAPE:-}" ]; then
      trap 'trap "" TERM; setsid bash -c "trap \"\" TERM; echo \$\$ >> \"$STUB_PIDS\"; sleep 60" >/dev/null 2>&1 </dev/null &' TERM
    fi
    [ -n "${STUB_SLEEP:-}" ] && sleep "$STUB_SLEEP"
    printf '%s\\n' "${STUB_REPORT:-report text}" > "$out"
    echo "model: ${STUB_MODEL:-stub-model}" ; echo "tokens used"; echo "10"
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
                        TMPDIR=str(self.tmpdir), ONLY="case-01", CODEX_MODEL="stub-model", HOME=str(t / "realhome"))
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

    def test_c2b_sigterm_to_the_lane_pid_alone(self):
        self.sigterm_lane_only({})

    def test_c2c_term_resistant_review_is_still_ended(self):
        self.sigterm_lane_only({"STUB_IGNORE_TERM": "1"})

    def test_c2d_term_handler_spawns_an_escapee(self):
        self.sigterm_lane_only({"STUB_ESCAPE": "1"}, settle=1.5)

    def sigterm_lane_only(self, extra, settle=0.5):
        skill = self.t / "SKILL.md"; skill.write_text("skill\n")
        pids = self.t / "stub.pids"; self.settings(STUB_SLEEP="60", STUB_PIDS=str(pids), **extra)
        p = subprocess.Popen(["bash", str(LANE), str(skill), str(self.out), "1"], env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for _ in range(100):
            if self.leftovers() and pids.exists() and pids.read_text().strip(): break
            time.sleep(0.1)
        self.assertTrue(self.leftovers(), "the temporary home never appeared")
        os.kill(p.pid, signal.SIGTERM)                     # the lane PID only
        try:
            p.wait(timeout=15)
        except subprocess.TimeoutExpired:
            p.kill(); self.fail("the lane did not exit after SIGTERM")
        time.sleep(settle)
        self.assertEqual(self.leftovers(), [], "temporary home left behind")
        survivors = []
        for pid in pids.read_text().split():
            kids = subprocess.run(["pgrep", "-P", pid], capture_output=True, text=True).stdout.split()
            for q in [pid] + kids:
                try:
                    state = open(f"/proc/{q}/stat").read().rsplit(")", 1)[1].split()[0]
                except FileNotFoundError:
                    continue
                if state != "Z":
                    survivors.append(q)
        for q in survivors:
            try: os.kill(int(q), 9)
            except ProcessLookupError: pass
        self.assertEqual(survivors, [], f"review processes still running: {survivors}")

    def test_c3_real_auth_untouched(self):
        before = (self.real / "auth.json").read_bytes()
        r = self.lane(STUB_REFRESH="1")
        self.assertEqual((self.real / "auth.json").read_bytes(), before, "a refreshed temporary token must not be copied back")
        self.assertTrue((self.real / "history.jsonl").exists())
        self.assertIn("refreshed", (r.stdout + r.stderr).lower())

    def test_c3b_newer_real_auth_is_not_rolled_back(self):
        self.lane(STUB_REFRESH="1", STUB_TOUCH_REAL=str(self.real / "auth.json"))
        self.assertIn("newer from another session", (self.real / "auth.json").read_text())

    def test_c4_launcher_needing_real_home_is_refused(self):
        r = self.lane(STUB_NEEDS_REAL_HOME=self.env["HOME"])
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertFalse(self.log.exists() and "EXEC_HOME" in self.log.read_text(), "the CLI must not have run with the real HOME")
        self.assertEqual(self.leftovers(), [])

    def test_c4b_exec_home_is_empty_and_not_the_real_one(self):
        r = self.lane()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        log = self.log.read_text()
        exec_home = [l for l in log.splitlines() if l.startswith("EXEC_HOME=")][0].split("=", 1)[1]
        self.assertNotEqual(exec_home, self.env["HOME"]); self.assertIn("EXEC_HOME_FILES=0", log)

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

    def test_c8_model_required(self):
        self.settings()
        skill = self.t / "SKILL.md"; skill.write_text("skill\n")
        env = {k: v for k, v in self.env.items() if k != "CODEX_MODEL"}
        r = subprocess.run(["bash", str(LANE), str(skill), str(self.out), "1"], capture_output=True, text=True, env=env, timeout=60)
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr); self.assertIn("CODEX_MODEL", r.stdout + r.stderr)
        self.assertFalse(self.log.exists(), "the CLI must not have been called"); self.assertEqual(self.leftovers(), [])

    def test_c9_model_recorded_and_mismatch_flagged(self):
        r = self.lane()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("-m stub-model", self.log.read_text())
        u = json.loads((self.out / "_meta" / "case-01.usage.json").read_text())
        self.assertEqual((u["requested_model"], u["model"], u["model_mismatch"]), ("stub-model", "stub-model", False))
        self.assertFalse((self.out / "fallback.txt").exists())
        subprocess.run(["rm", "-rf", str(self.out)])
        r = self.lane(STUB_MODEL="other-model")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        u = json.loads((self.out / "_meta" / "case-01.usage.json").read_text())
        self.assertTrue(u["model_mismatch"]); self.assertEqual(u["model"], "other-model")
        self.assertIn("case-01", (self.out / "fallback.txt").read_text()); self.assertIn("different model", r.stdout + r.stderr)

    def test_c6_scan_flags_jwt_directly(self):
        d = self.t / "x"; d.mkdir(); (d / "r.md").write_text(f"token {JWT}\n")
        r = subprocess.run([sys.executable, str(SCAN), str(d)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1, r.stdout); self.assertNotIn(JWT, r.stdout)


if __name__ == "__main__":
    unittest.main()
