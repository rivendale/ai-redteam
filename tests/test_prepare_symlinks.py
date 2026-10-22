#!/usr/bin/env python3
"""Eval case symlinks (failure list written before the fix; offline, no model, no network).

A symlink inside an eval case makes prepare.py copy the bytes of whatever it points at (copy2 and copytree follow links) into the
prompt a reviewer sees and into the published prompt files. The failure list:
  F1 request.md is a symlink            -> prepare.py must refuse, nothing copied
  F2 context.md is a symlink            -> prepare.py must refuse
  F3 a file in work/ is a symlink       -> prepare.py must refuse
  F4 a directory in work/ is a symlink  -> prepare.py must refuse (copytree would follow it)
  F5 a symlink nested two levels deep   -> prepare.py must refuse
  F6 a dangling symlink                 -> prepare.py must refuse (no silent skip)
  F7 verify_cases.py must reject the same cases, so CI fails a pull request that adds one
  F8 a clean case still prepares and still verifies (the check must not reject everything)
  F9 the refusal prints the case and path but never the pointed-at content
"""
import json, os, pathlib, subprocess, sys, tempfile, unittest

TOOLS = pathlib.Path(__file__).resolve().parent.parent / "evals" / "tools"
SECRET = "SECRET-CANARY-CONTENT-7731"


def make_case(root, name="case-01"):
    d = root / name
    (d / "work").mkdir(parents=True)
    (d / "request.md").write_text("Review this.\n")
    (d / "context.md").write_text("Context.\n")
    (d / "work" / "a.txt").write_text("ok\n")
    (d / "expected.json").write_text(json.dumps({"control": True, "planted": [], "must": [{"rule": "no_critical_or_high"}], "proof": {"shell": "true"}}))
    return d


def run(tool, *args):
    return subprocess.run([sys.executable, str(TOOLS / tool), *args], capture_output=True, text=True)


class T(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.t = pathlib.Path(self.tmp.name)
        self.cases = self.t / "cases"
        self.cases.mkdir()
        self.out = self.t / "out"
        self.target = self.t / "outside.txt"
        self.target.write_text(SECRET + "\n")
        self.tdir = self.t / "outside-dir"
        self.tdir.mkdir()
        (self.tdir / "x.txt").write_text(SECRET + "\n")

    def tearDown(self):
        self.tmp.cleanup()

    def both_refuse(self, why):
        p = run("prepare.py", str(self.out), "--cases", str(self.cases))
        self.assertNotEqual(p.returncode, 0, why + ": prepare.py accepted a symlink\n" + p.stdout + p.stderr)
        self.assertNotIn(SECRET, p.stdout + p.stderr, "F9: content leaked into the message")
        self.assertIn("symlink", (p.stdout + p.stderr).lower())
        copied = [f for f in self.out.rglob("*") if f.is_file() and SECRET in f.read_text(errors="replace")] if self.out.exists() else []
        self.assertEqual(copied, [], why + ": pointed-at bytes were copied")
        v = run("verify_cases.py", "--cases", str(self.cases))
        self.assertNotEqual(v.returncode, 0, why + ": verify_cases.py accepted a symlink\n" + v.stdout + v.stderr)
        self.assertIn("symlink", (v.stdout + v.stderr).lower())

    def test_f1_request_symlink(self):
        d = make_case(self.cases); (d / "request.md").unlink(); (d / "request.md").symlink_to(self.target)
        self.both_refuse("F1")

    def test_f2_context_symlink(self):
        d = make_case(self.cases); (d / "context.md").unlink(); (d / "context.md").symlink_to(self.target)
        self.both_refuse("F2")

    def test_f3_work_file_symlink(self):
        d = make_case(self.cases); (d / "work" / "link.txt").symlink_to(self.target)
        self.both_refuse("F3")

    def test_f4_work_dir_symlink(self):
        d = make_case(self.cases); (d / "work" / "linkdir").symlink_to(self.tdir, target_is_directory=True)
        self.both_refuse("F4")

    def test_f5_nested_symlink(self):
        d = make_case(self.cases); n = d / "work" / "a" / "b"; n.mkdir(parents=True); (n / "deep.txt").symlink_to(self.target)
        self.both_refuse("F5")

    def test_f6_dangling_symlink(self):
        d = make_case(self.cases); (d / "work" / "dangling").symlink_to(self.t / "does-not-exist")
        self.both_refuse("F6")

    def test_f8_clean_case_still_passes(self):
        make_case(self.cases)
        p = run("prepare.py", str(self.out), "--cases", str(self.cases))
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertTrue((self.out / "case-01" / "work" / "a.txt").exists())
        v = run("verify_cases.py", "--cases", str(self.cases))
        self.assertEqual(v.returncode, 0, v.stdout + v.stderr)


if __name__ == "__main__":
    unittest.main()
