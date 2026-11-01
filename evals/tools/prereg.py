#!/usr/bin/env python3
"""Pre-registration record for the review lanes (run_reviews.sh and run_reviews_codex.sh share this file).

    python3 evals/tools/prereg.py flag DRY_RUN           # prints 1 or 0; refuses a value that is neither on nor off
    python3 evals/tools/prereg.py write --repo R --skill S --prep P --out O --parallel N --runner PATH --cli claude|codex \
        [--cli-cmd CMD] [--model M]

`write` records, before any review starts, what this run is: the skill text and its git identity, the exact case inputs a
reviewer will see (hashed from the prepared copy, so expected.json is never in it), the model and CLI, the gate rule and its
pre-registered margin K (GATE_MARGIN), and the UTC start time, in OUT/_meta/prereg.json. A resumed run (same OUT) keeps the
first record and adds _meta/prereg-resume-<time>.json; it is refused if the skill text, the case inputs or the runner changed.
The CLI version is read from the installed files, never by running the CLI; CLI_VERSION=<v> overrides it.

Environment read: CASES, ONLY, APPLIES, NOTE, GATE_RULE, GATE_RULE_FILE, GATE_MARGIN, CLI_VERSION, MAX_COST_USD, EST_REVIEW_USD,
DRY_RUN. Exit 0 on success, 1 when the record is refused, 2 on a bad flag value. Standard library only.
"""
import argparse, datetime, hashlib, json, math, os, pathlib, re, shlex, shutil, subprocess, sys

ON = {"1", "true", "yes", "on"}
OFF = {"", "0", "false", "no", "off"}


def flag(name):
    """True or False for an on/off environment variable; ValueError for anything else. DRY_RUN=0 means off."""
    v = os.environ.get(name, "").strip().lower()
    if v in ON:
        return True
    if v in OFF:
        return False
    raise ValueError(f"{name}={os.environ.get(name)!r} is neither on (1, true, yes, on) nor off (unset, empty, 0, false, no, off)")


def margin_from_env():
    """GATE_MARGIN as a finite number >= 0 (an int when integral), or None when unset. ValueError otherwise."""
    raw = os.environ.get("GATE_MARGIN", "").strip()
    if not raw:
        return None
    try:
        k = float(raw)
    except ValueError:
        k = float("nan")
    if not math.isfinite(k) or k < 0:
        raise ValueError(f"GATE_MARGIN={raw!r} must be a finite number of summed hits, zero or more")
    return int(k) if k == int(k) else k


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def git(here, *args):
    try:
        r = subprocess.run(["git", "-C", here, *args], capture_output=True, text=True, timeout=30)
        return r.stdout.strip() if r.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def cli_identity(cli, cmd):
    """(path on PATH, real path, version or None) for the reviewer CLI, read from files only (the CLI is never run).
    cmd is a launcher command line (codex: "node /x/codex.js" or "codex"); a .js argument is preferred over the interpreter."""
    words = shlex.split(cmd) if cmd else [cli]
    target = next((w for w in words if w.endswith(".js")), None) or words[0]
    path = target if os.sep in target else shutil.which(target)
    real = os.path.realpath(path) if path and os.path.exists(path) else None
    version = os.environ.get("CLI_VERSION") or None
    if not version and real:
        for d in [pathlib.Path(real).parent, *pathlib.Path(real).parents][:4]:
            pj = d / "package.json"
            if pj.is_file():
                try:
                    version = json.loads(pj.read_text()).get("version")
                except (OSError, ValueError):
                    pass
                if version:
                    break
        if not version:
            m = re.search(r"(\d+\.\d+\.\d+)", real)
            version = m.group(1) if m else None
    return path, real, version


def build(a):
    here, skill, prep = a.repo, a.skill, a.prep
    try:
        rel = str(pathlib.Path(skill).resolve().relative_to(pathlib.Path(here).resolve()))
    except ValueError:
        rel = None                                                 # a skill file outside the repository has no git identity here
    skill_rec = {"path": rel or skill, "sha256": sha(skill), "git_blob": git(here, "hash-object", skill),
                 "git_last_commit": git(here, "log", "-1", "--format=%H", "--", rel) if rel else None, "repo_head": git(here, "rev-parse", "HEAD")}
    skill_rec["committed"] = bool(rel and skill_rec["git_blob"] and skill_rec["git_blob"] == git(here, "rev-parse", f"HEAD:{rel}"))
    inputs = {}
    for case in sorted(p for p in pathlib.Path(prep).iterdir() if p.is_dir()):
        files = {str(f.relative_to(case)): sha(f) for f in sorted(case.rglob("*")) if f.is_file()}
        inputs[case.name] = {"sha256": hashlib.sha256("".join(f"{k}\0{v}\n" for k, v in sorted(files.items())).encode()).hexdigest(), "files": files}
    path, real, version = cli_identity(a.cli, a.cli_cmd)
    gate_text, gate_src = os.environ.get("GATE_RULE") or None, "GATE_RULE" if os.environ.get("GATE_RULE") else None
    if not gate_text and os.environ.get("GATE_RULE_FILE"):
        gf = os.environ["GATE_RULE_FILE"]
        gate_text, gate_src = pathlib.Path(gf).read_text(), f"GATE_RULE_FILE {gf} sha256 {sha(gf)}"
    k = margin_from_env()
    return {"schema": "prereg-1", "started_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "skill": skill_rec,
            "cases": {"dir": os.environ.get("CASES") or "evals/cases", "only": os.environ.get("ONLY") or None, "applies": os.environ.get("APPLIES") or None,
                      "note": os.environ.get("NOTE") or None, "count": len(inputs), "inputs": inputs},
            "model": {"cli": a.cli, "requested": a.model or None, "cli_command": a.cli_cmd or None, "cli_path": path, "cli_realpath": real,
                      "cli_version": version, "cli_version_source": "CLI_VERSION" if os.environ.get("CLI_VERSION") else ("installed files" if version else None)},
            "gate_rule": {"given": bool(gate_text), "text": gate_text, "source": gate_src,
                          "margin": k, "margin_source": "GATE_MARGIN" if k is not None else None},
            "lane": {"runner": os.path.basename(a.runner), "runner_sha256": sha(a.runner), "prereg_sha256": sha(__file__),
                     "prepare_sha256": sha(os.path.join(here, "evals/tools/prepare.py")),
                     "parallel": a.parallel, "max_cost_usd": os.environ.get("MAX_COST_USD") or None, "est_review_usd": os.environ.get("EST_REVIEW_USD") or None,
                     "dry_run": flag("DRY_RUN")}}


def write(a):
    rec = build(a)
    meta = pathlib.Path(a.out) / "_meta"; meta.mkdir(parents=True, exist_ok=True); first = meta / "prereg.json"
    if first.exists():
        old = json.loads(first.read_text())
        if old.get("skill", {}).get("sha256") != rec["skill"]["sha256"]:
            raise ValueError(f"{first} was written for a different skill text ({old.get('skill', {}).get('sha256')}); use a new OUTDIR")
        old_runner = old.get("lane", {}).get("runner", "run_reviews.sh")
        if old_runner != rec["lane"]["runner"]:
            raise ValueError(f"{first} was written by {old_runner}, not {rec['lane']['runner']}; use a new OUTDIR")
        changed = sorted(c for c in rec["cases"]["inputs"] if c in old.get("cases", {}).get("inputs", {}) and old["cases"]["inputs"][c]["sha256"] != rec["cases"]["inputs"][c]["sha256"])
        if changed:
            raise ValueError(f"case inputs changed since {first} was written ({', '.join(changed[:5])}); use a new OUTDIR")
        dst = meta / f"prereg-resume-{rec['started_utc'].replace(':', '')}.json"
    else:
        dst = first
    dst.write_text(json.dumps(rec, indent=1) + "\n")
    print(f"pre-registered: {dst} ({rec['cases']['count']} case(s), skill sha256 {rec['skill']['sha256'][:12]})")
    if not rec["gate_rule"]["given"]:
        print("WARNING: no GATE_RULE or GATE_RULE_FILE given: this run records no comparison rule in advance", file=sys.stderr)
    if rec["gate_rule"]["margin"] is None:
        print("WARNING: no GATE_MARGIN given: this run pre-registers no margin K for `stats.py gate`", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    fp = sub.add_parser("flag"); fp.add_argument("name")
    wp = sub.add_parser("write")
    for opt in ("--repo", "--skill", "--prep", "--out", "--parallel", "--runner"):
        wp.add_argument(opt, required=True)
    wp.add_argument("--cli", required=True, choices=["claude", "codex"])
    wp.add_argument("--cli-cmd", default="")
    wp.add_argument("--model", default="")
    a = ap.parse_args()
    try:
        if a.cmd == "flag":
            print("1" if flag(a.name) else "0")
            return 0
        flag("DRY_RUN"); margin_from_env()                        # refuse a bad value before reading any file
    except ValueError as e:
        print(f"refused: {e}", file=sys.stderr)
        return 2
    try:
        write(a)
    except (ValueError, OSError) as e:
        print(f"refused: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
