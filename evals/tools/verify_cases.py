#!/usr/bin/env python3
"""Ground truth for the eval cases, run by a person (never by a reviewer): for every case, the `proof` in expected.json must hold.

A defect case's proof DEMONSTRATES the planted defect (the snippet exits 0 only when the defect is really there); a control's proof runs
its tests (exit 0 means they pass). A case with no proof is listed. Also checks the structure each case must have.

    python3 evals/tools/verify_cases.py [--only ID,...]
"""
import argparse, json, os, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent / "cases"
REQUIRED = ["request.md", "context.md", "expected.json"]


def check_case(d):
    probs = []
    exp = json.loads((d / "expected.json").read_text())
    for f in REQUIRED:
        if not (d / f).exists():
            probs.append(f"missing {f}")
    if not (d / "work").exists() or not any((d / "work").rglob("*")):
        probs.append("work/ is missing or empty")
    if exp["control"] and exp["planted"]:
        probs.append("a control must not list planted defects")
    if not exp["control"] and not exp["planted"] and not any(m.get("rule") for m in exp.get("must", [])):
        probs.append("a defect case needs planted defects or a must rule")
    for patch in [d / "work" / n for n in ("change.patch", "fix.patch") if (d / "work" / n).exists()]:  # a pull-request case: the patch must apply to base/ and must not remove a file unless the case means it to
        import re
        if re.search(r"^@@ -\d+(,\d+)? \+0,0 @@", patch.read_text(), re.M):
            probs.append(f"{patch.name} removes a whole file (a diff built from an incomplete 'after' tree?)")
        refs = set(re.findall(r'"args": \["([^"]+\.js)"', (d / "work").joinpath("change.patch").read_text()))
        for ref in refs:  # files an added config launches must exist in base/ or be added by the patch
            if not (d / "work" / "base" / ref).exists() and f"+++ b/{ref}" not in patch.read_text():
                probs.append(f"{patch.name} launches {ref}, which is neither in base/ nor added by the patch")
    for p in exp["planted"]:
        f = d / p["file"]
        if not f.exists():
            probs.append(f"{p['id']}: file {p['file']} does not exist")
        elif p["lines"]:
            n = len(f.read_text().splitlines())
            if not (1 <= p["lines"][0] <= p["lines"][1] <= n):
                probs.append(f"{p['id']}: lines {p['lines']} outside the file ({n} lines)")
        if p["min_severity"] not in ("Low", "Medium", "High", "Critical"):
            probs.append(f"{p['id']}: bad min_severity")
    pr = exp.get("proof")
    if pr:
        cwd = d / pr.get("cwd", ".")
        if "python" in pr:
            cmd = ["python3", "-c", pr["python"]]
        elif "shell" in pr:
            cmd = ["bash", "-c", pr["shell"]]
        else:
            cmd = None
            probs.append("proof has neither python nor shell")
        if cmd:
            r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=120, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
            if r.returncode != 0:
                probs.append(f"PROOF FAILED (exit {r.returncode}): {(r.stderr or r.stdout).strip()[-300:]}")
    else:
        probs.append("NO PROOF (listed, not failed)" if False else "no proof recorded")
    return exp, probs


def ignored_files():
    """Case files that git ignores would be on this disk but missing from a commit and from CI. Empty when git is unavailable."""
    try:
        r = subprocess.run(["git", "ls-files", "--others", "--ignored", "--exclude-standard", str(ROOT)], capture_output=True, text=True, timeout=30, cwd=ROOT)
    except (OSError, subprocess.SubprocessError):
        return []
    return [l for l in r.stdout.splitlines() if l and "__pycache__" not in l and not l.endswith(".pyc")]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    ids = [x for x in a.only.split(",") if x]
    dirs = sorted(p for p in ROOT.iterdir() if p.is_dir() and (not ids or p.name in ids or any(p.name.startswith(i) for i in ids)))
    bad = 0
    for d in dirs:
        try:
            exp, probs = check_case(d)
        except Exception as e:
            exp, probs = {"control": None}, [f"crashed: {e}"]
        proofless = [p for p in probs if p == "no proof recorded"]
        real = [p for p in probs if p != "no proof recorded"]
        status = "ok" if not real else "FAIL"
        bad += bool(real)
        tag = "control" if exp.get("control") else f"{len(exp.get('planted', []))} planted"
        print(f"  {status:4} {d.name:8} {exp.get('slug', ''):52} {tag}{'  (no machine proof; see expected.json why)' if proofless else ''}")
        for p in real:
            print(f"         - {p}")
    ign = ignored_files()
    for f in ign:
        print(f"  FAIL git ignores a case file, so it would not be committed: {f}")
    bad += bool(ign)
    print(f"{len(dirs) - bad}/{len(dirs)} cases verified")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
