#!/usr/bin/env python3
"""Offline, recommendation-only diagnostics for cases and recorded reviews.

Default discovery uses current keys and reports its provenance limits. An explicit
run manifest can declare the full recorded grid; only reconciled, complete grids
with known text/model/repeat identities can establish outcome-vector redundancy.
Nothing executes case proofs, modifies inputs or invokes a reviewer.
"""
import argparse
import collections
import copy
import datetime as dt
import hashlib
import importlib.util
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve()
CID = re.compile(r"case-\d+$")
GENERIC = set("a an the and or error issue bug fix confirmed unverified high medium low report finding file line test risk unsafe bad missing wrong control code problem".split())
UNKNOWN = {"", "unknown", "none", "null", "unspecified", "default"}
PROTECTED = re.compile(r"\b(disclos\w*|regulat\w*|legal statements?|consent|privacy|safety warnings?|required statements?)\b", re.I)


class InputError(Exception):
    pass


def safe(root, name):
    """Confine reads lexically, then reject links before resolving any component."""
    p = pathlib.Path(name)
    p = p if p.is_absolute() else root / p
    try:
        parts = p.relative_to(root).parts
    except ValueError:
        raise InputError("path_outside_root") from None
    if ".." in parts:
        raise InputError("path_outside_root")
    q = root
    for part in parts:
        q = q / part
        if q.is_symlink():
            raise InputError("symlink_input")
    return p


def read_json(root, path):
    try:
        return json.loads(read_text(root, path))
    except InputError:
        raise
    except (OSError, ValueError, UnicodeError):
        raise InputError("missing_or_corrupt_json") from None


def read_text(root, path):
    raw = safe(root, path).read_bytes()
    return raw.decode("utf-16" if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig")


def prompt_text(root, path):
    """Only the skill prefix identifies the text; case inputs can contain binary files."""
    raw = safe(root, path).read_bytes()
    encoding = 'utf-16-le' if raw.startswith(b'\xff\xfe') else 'utf-16-be' if raw.startswith(b'\xfe\xff') else 'utf-8'
    marker = '=== INPUTS ==='.encode(encoding)
    start = raw.find('=== SKILL ==='.encode(encoding))
    end = raw.find(marker, start) if start >= 0 else -1
    prefix = raw[:end] if end >= 0 else raw
    decoded = prefix.decode('utf-16' if encoding.startswith('utf-16') else 'utf-8-sig')
    return decoded if end >= 0 else ''


def report(root, path):
    """The canonical last-fenced-JSON extraction, with BOM-aware input decoding."""
    raw = read_text(root, path)
    text = raw
    if pathlib.Path(path).suffix == ".md":
        blocks = re.findall(r"```json\s*\n(.*?)```", text, re.S)
        if not blocks:
            raise ValueError("missing JSON block")
        text = blocks[-1]
    value = json.loads(text)
    if isinstance(value, dict):
        value["_raw"] = raw
    return value


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def held(path):
    return any(re.search(r"hold.?out|held|^ho-", p, re.I) for p in pathlib.Path(path).parts)


def date(value):
    try:
        return dt.date.fromisoformat(str(value)[:10]).isoformat()
    except ValueError:
        return None


def protection(exp, source=""):
    health = exp.get("case_health", {})
    return bool(health.get("regression_guard") or str(exp.get("track", "")).upper() == "R"
                or PROTECTED.search(json.dumps({k: v for k, v in exp.items() if k != "proof"}) + " " + source))


def rates(rows):
    groups = collections.defaultdict(list)
    for row in rows:
        if row["status"] == "usable":
            groups[(row.get("text"), row.get("model"))].append(row)
    out = []
    for (text, model_name), cells in sorted(groups.items(), key=lambda x: str(x[0])):
        hits = sum(x["hits"] for x in cells)
        total = sum(x["denominator"] for x in cells)
        out.append({"text": text, "model": model_name, "observations": len(cells),
                    "hits": hits, "denominator": total, "rate": hits / total if total else None})
    return out


def diagnose(cases, observations, complete=False, grid=None):
    """Pure aggregation, also used by small synthetic fixtures in the tests."""
    output = []
    grid = set(grid or [])
    for case in cases:
        rows = observations.get(case["id"], [])
        usable = [r for r in rows if r["status"] == "usable"]
        statuses = collections.Counter(r["status"] for r in rows)
        groups = rates(rows)
        known = [g for g in groups if g["text"] and g["model"]]
        # Repeats are compared only within the same exact recorded text/model.
        by_group = collections.defaultdict(set)
        for r in usable:
            if r.get("text") and r.get("model"):
                by_group[(r["text"], r["model"])].add(tuple(r["signature"]))
        flaky = any(len(s) > 1 for s in by_group.values())
        saturated = bool(usable) and not case["control"] and all(r["hits"] == r["denominator"] for r in usable)
        floor = bool(usable) and not case["control"] and all(r["hits"] == 0 for r in usable)
        flagged = sum(bool(r.get("alarm")) for r in usable)
        matcher = sum(r.get("matcher_flags", 0) for r in usable)
        unusable = len(rows) - len(usable)
        stopped = sum(r["status"] == "safety_stop" or r.get("safety_stop", False) for r in rows)
        fallback = sum(r["status"] == "fallback" or r.get("fallback", False) for r in rows)
        stopped_or_fallback = sum(bool(r["status"] in ("safety_stop", "fallback") or r.get("safety_stop") or r.get("fallback")) for r in rows)
        verdict = "KEEP"
        reasons = []
        if not usable:
            verdict = "UNTESTABLE"; reasons.append("no usable recorded reviews")
        elif case["control"] and flagged == len(usable):
            verdict = "FIX-CONTROL"; reasons.append("every usable review flags the control; inspect the control before blaming the model")
        elif matcher:
            verdict = "REVIEW-MATCHER"; reasons.append("possible weak-word credit or location/credit disagreement")
        elif flaky:
            verdict = "FLAKY"; reasons.append("same text and model disagree across recorded observations")
        elif rows and unusable / len(rows) >= .5:
            verdict = "UNTESTABLE"; reasons.append("at least half the recorded observations are unusable")
        elif saturated:
            if case["regression_guard"]:
                reasons.append("KEEP (regression guard): saturation alone does not justify pruning required text")
            else:
                verdict = "SHARPEN"; reasons.append("all usable observations detect the planted items")
        elif floor:
            verdict = "REVIEW-MATCHER"; reasons.append("floor: no usable observation detects a planted item; case, matcher and difficulty need inspection")
        if saturated or (case["control"] and usable and not flagged):
            reasons.append("never failed a usable reviewer; this alone does not prove the case redundant")
        if not reasons:
            reasons.append("retain with the recorded coverage and limitations")
        values = {g["rate"] for g in known}
        vector = {}
        duplicate = False
        for ordinal, r in enumerate(rows):
            slot = (r.get("text"), r.get("model"), r.get("repeat"))
            if any(x is None for x in slot):
                slot = ("unknown-provenance", r.get("record", ordinal), None)
            if slot in vector:
                duplicate = True
            vector[slot] = tuple(r["signature"]) if r["status"] == "usable" else None
        proof = bool(complete and grid and not duplicate and set(vector) == grid and all(vector.values())
                     and all(all(x is not None for x in slot) for slot in vector)
                     and (len({s[0] for s in grid}) >= 3 or len({s[1] for s in grid}) >= 3))
        output.append({"id": case["id"], "suite": case["suite"], "control": case["control"],
                       "metric": case["metric"], "verdict": verdict, "reasons": reasons,
                       "regression_guard": case["regression_guard"], "saturated": saturated, "floor": floor,
                       "repeat_disagreement": flaky, "discriminates_known_groups": len(values) > 1 if len(known) > 1 else None,
                       "observations": len(rows), "usable": len(usable), "status_counts": dict(sorted(statuses.items())),
                       "coverage_label": "NO-DATA" if not rows else "NO-USABLE-REVIEWS" if not usable else "RECORDED",
                       "unusable_share": unusable / len(rows) if rows else None,
                       "missing_usage_metadata": sum(not r.get("usage_metadata", False) for r in rows),
                       "safety_stop_share": stopped / len(rows) if rows else None,
                       "fallback_share": fallback / len(rows) if rows else None,
                       "untestable_share": stopped_or_fallback / len(rows) if rows else None,
                       "control_flags": flagged if case["control"] else None,
                       "control_denominator": len(usable) if case["control"] else None,
                       "matcher_flags": matcher, "difficulty": groups,
                       "source_date": case.get("source_date"), "last_run_date": max((r["run_date"] for r in rows if r.get("run_date")), default=None),
                       "latest_record_date": max((r["record_date"] for r in rows if r.get("record_date")), default=None),
                       "expected_sha256": case.get("expected_sha256"),
                       "missing_grid_cells": len(grid - set(vector)) if grid else None,
                       "redundancy": [], "_vector": vector, "_proof": proof})
    for i, a in enumerate(output):
        for b in output[i + 1:]:
            if (a["suite"], a["control"], a["metric"]) != (b["suite"], b["control"], b["metric"]):
                continue
            shared = set(a["_vector"]) & set(b["_vector"])
            if not shared or not all(a["_vector"][s] is not None and a["_vector"][s] == b["_vector"][s] for s in shared):
                continue
            proven = a["_proof"] and b["_proof"] and a["_vector"] == b["_vector"]
            for left, right in ((a, b), (b, a)):
                left["redundancy"].append({"with": right["id"], "status": "redundant outcome vectors" if proven else "overlap, needs enumeration"})
                if proven and not left["regression_guard"] and left["verdict"] in ("KEEP", "SHARPEN"):
                    left["verdict"] = "RETIRE-CANDIDATE"
                    left["reasons"].append("full recorded grid has identical outcome vectors; owner must inspect semantic coverage before any retirement")
    for row in output:
        del row["_vector"], row["_proof"]
        overlaps = [r for r in row['redundancy'] if r['status'] == 'overlap, needs enumeration']
        proven = [r for r in row['redundancy'] if r['status'] != 'overlap, needs enumeration']
        row['overlap_count'] = len(overlaps)
        row['overlap_examples_omitted'] = max(0, len(overlaps) - 3)
        row['redundancy'] = proven + overlaps[:3]
    return output


def discover(root):
    """Recorded filenames are discovery hints, never invented text/model identities."""
    result = root / "evals/results"
    dirs = set()
    metadata_only = set()
    for p in result.rglob("case-*"):
        safe(root, p)
        if p.is_file() and p.suffix in (".md", ".json") and CID.fullmatch(p.stem) and "_meta" not in p.parts:
            dirs.add(p.parent)
        elif p.is_file() and p.name.endswith(".usage.json"):
            metadata_only.add(p.parent.parent if p.parent.name == "_meta" else p.parent)
            if p.parent.name == "_meta":
                dirs.add(p.parent.parent)
    runs = []
    for d in sorted(dirs):
        rel = d.relative_to(root).as_posix()
        low = rel.lower()
        cases = "evals/assess/cases" if "assess" in low else "evals/supplychain/cases" if "supplychain" in low and "ctl" not in d.relative_to(result).parts else "evals/cases"
        runs.append({"reports": rel, "cases": cases, "skill": "assess" if "assess" in low else "pr-review" if "prreview" in low or "pr-review" in low or "supplychain" in low else "redteam",
                     "holdout": held(rel), "record_date": date(d.relative_to(result).parts[0])})
    return runs, len(metadata_only - dirs)


def metadata(meta, declared=None):
    outputs = meta.get("output_tokens_by_model", {})
    producers = [k for k, v in outputs.items() if isinstance(v, (int, float)) and v > 0] if isinstance(outputs, dict) else []
    models = producers or meta.get("producers") or meta.get("models") or ([meta["model"]] if meta.get("model") else [])
    if not isinstance(models, list):
        raise InputError("invalid_model_metadata")
    if any(not isinstance(m, str) for m in models):
        raise InputError("invalid_model_metadata")
    models = sorted({m.strip() for m in models if m.strip().lower() not in UNKNOWN})
    declared = declared if isinstance(declared, str) and declared.strip().lower() not in UNKNOWN else None
    model_name = models[0] if len(models) == 1 else declared
    if meta.get("mixed_model") or meta.get("model_mismatch") or meta.get("fallback_models") or len(models) > 1:
        return model_name, "fallback"
    requested = meta.get("requested_model")
    if requested and models and requested != models[0]:
        return model_name, "fallback"
    if meta.get("safety_stops") or meta.get("safety_stop"):
        return model_name, "safety_stop"
    if meta.get("is_error") or meta.get("error"):
        return model_name, "failed"
    return model_name, "usable"


def load(root, manifest=None):
    issues = collections.Counter()
    holdout = collections.Counter()
    def issue(code, private=False):
        (holdout if private else issues)[("issue_" if private else "") + code] += 1
    suites = [root / "evals/cases"] + sorted((root / "evals").glob("*/cases"))
    runs, orphan_meta = discover(root)
    if orphan_meta:
        issues["unassociated_metadata_directories"] = orphan_meta
    declared = manifest is not None
    complete = False
    if declared:
        data = read_json(root, manifest)
        if not isinstance(data, dict) or data.get("schema") != "case-health-runs-1" or not isinstance(data.get("runs"), list):
            raise InputError("invalid_run_manifest")
        expected_dirs = {r["reports"] for r in runs}
        runs = data["runs"]
        listed = {r.get("reports") for r in runs if isinstance(r, dict)}
        if expected_dirs - listed:
            issues["unlisted_result_directories"] += len(expected_dirs - listed)
        complete = bool(data.get("enumeration_complete") and not expected_dirs - listed)
        for run in runs:
            if not isinstance(run, dict) or not all(k in run for k in ("reports", "cases", "expected_cases")):
                raise InputError("invalid_run_manifest")
            suites.append(safe(root, run["cases"]))
    private_suites = {safe(root, r["cases"]) for r in runs if held(r.get("cases", "")) or (declared and r.get("holdout"))}
    corpus = {}; private_ids = collections.defaultdict(set)
    for d in sorted(set(suites)):
        safe(root, d)
        if held(d) or d in private_suites:
            continue  # no hold-out keys, source text or per-case recommendations are needed
        if not d.exists():
            issue("missing_case_directory"); continue
        for entry in sorted(d.iterdir()):
            if entry.is_symlink():
                issue("symlink_case"); continue
            if not entry.is_dir():
                continue
            try:
                key = safe(root, entry / "expected.json")
                exp = read_json(root, key)
                cid = exp["id"]
                if not isinstance(cid, str) or not CID.fullmatch(cid) or cid != entry.name or not isinstance(exp.get("control"), bool):
                    raise InputError("invalid_case_key")
                suite = d.relative_to(root).as_posix()
                if exp.get("holdout") or exp.get("case_health", {}).get("holdout"):
                    private_ids[suite].add(cid); holdout["cases"] += 1; continue
                source = ""
                for item in entry.rglob("*"):
                    safe(root, item)
                for name in ("request.md", "context.md"):
                    source += read_text(root, entry / name)
                identity = suite + "/" + cid
                exp["_dir"] = str(entry)
                corpus[identity] = {"id": identity, "cid": cid, "suite": suite, "control": exp["control"],
                                    "metric": "assess_rule_pass" if suite == "evals/assess/cases" else "defect_recall" if exp.get("planted") else "case_rule_pass",
                                    "regression_guard": protection(exp, source), "source_date": date(exp.get("case_health", {}).get("source_date", exp.get("source_date"))),
                                    "expected_sha256": hashlib.sha256(key.read_bytes()).hexdigest(), "exp": exp}
            except (InputError, OSError, ValueError, KeyError, TypeError, AttributeError):
                issue("invalid_or_missing_case_input")
    # Import the repository's existing scorers, not a substitute matching algorithm.
    repo = HERE.parent.parent.parent
    score = module(repo / "evals/score.py", "case_health_score")
    assess = module(repo / "evals/score_assess.py", "case_health_assess")
    observations = collections.defaultdict(list)
    grid = set(); seen_runs = set(); inventory = 0
    for index, run in enumerate(runs):
        private = bool(run.get("holdout") or held(run.get("cases", "")) or held(run.get("reports", "")))
        try:
            d = safe(root, run["reports"])
            suite_path = safe(root, run["cases"])
            suite = suite_path.relative_to(root).as_posix()
            if not d.is_dir():
                raise InputError("missing_results_directory")
            if d in seen_runs:
                raise InputError("duplicate_run_directory")
            seen_runs.add(d); inventory += 1
            paths = collections.defaultdict(list)
            for p in sorted(d.iterdir()):
                if CID.fullmatch(p.stem) and p.suffix in (".md", ".json"):
                    safe(root, p); paths[p.stem].append(p)
            meta_ids = {p.name.removesuffix(".usage.json") for p in (d / "_meta").glob("*.usage.json")}
            expected_ids = set(run.get("expected_cases", paths))
            ids = expected_ids | meta_ids
            if declared and (set(paths) | meta_ids) - expected_ids:
                issue("undeclared_report_or_metadata", private); complete = False
            ids |= set(paths)
            for cid in sorted(ids):
                cell_private = private or cid in private_ids[suite]
                text_label = run.get("text") if str(run.get("text", "")).lower() not in UNKNOWN else None
                row = {"record": index, "text": text_label, "model": run.get("model"), "repeat": run.get("repeat") or None,
                       "run_date": date(run.get("date")), "record_date": date(run.get("record_date")),
                       "status": "usable", "hits": 0, "denominator": 1, "signature": [0], "matcher_flags": 0, "alarm": False}
                if not CID.fullmatch(str(cid)):
                    issue("invalid_case_identifier", cell_private); complete = False; continue
                meta_path = d / "_meta" / (cid + ".usage.json")
                if meta_path.exists() or meta_path.is_symlink():
                    try:
                        meta = read_json(root, meta_path)
                        row["model"], row["status"] = metadata(meta, row["model"])
                        row["usage_metadata"] = True
                        row["safety_stop"] = bool(meta.get("safety_stops") or meta.get("safety_stop"))
                        row["fallback"] = row["status"] == "fallback"
                        row["run_date"] = row["run_date"] or date(meta.get("started_at", meta.get("run_date")))
                    except (InputError, TypeError, AttributeError):
                        row["status"] = "invalid_metadata"; issue("invalid_metadata", cell_private)
                else:
                    if not cell_private:
                        issues["metadata_absent"] += 1
                files = paths.get(cid, [])
                rep = None
                if len(files) != 1:
                    if not files and row["status"] in ("safety_stop", "fallback", "failed"):
                        pass  # explicit unusable status accounts for the absent report
                    else:
                        row["status"] = "missing_report" if not files else "ambiguous_report"
                        issue(row["status"], cell_private)
                else:
                    try:
                        rep = report(root, files[0])
                        if not isinstance(rep, dict) or "verdict" not in rep:
                            raise ValueError()
                    except (InputError, OSError, ValueError, TypeError, UnicodeError):
                        row["status"] = "invalid_report"; issue("invalid_report", cell_private)
                prompt = d / (cid + ".prompt")
                if prompt.exists():
                    try:
                        raw = prompt_text(root, prompt)
                        if "=== SKILL ===" in raw:
                            text = raw.split("=== SKILL ===", 1)[1]
                            row["text"] = "sha256:" + hashlib.sha256(text.encode()).hexdigest()
                    except (OSError, UnicodeError):
                        row["text"] = None; issue("invalid_prompt", cell_private)
                if cell_private:
                    holdout["observations"] += 1; holdout[row["status"]] += 1
                    holdout["missing_usage_metadata"] += int(not row.get("usage_metadata", False))
                    holdout["safety_stop_observations"] += int(bool(row.get("safety_stop")))
                    holdout["fallback_observations"] += int(row["status"] == "fallback")
                    continue
                identity = suite + "/" + cid
                if identity not in corpus:
                    issue("report_without_current_case"); complete = False; continue
                case = corpus[identity]
                if row["status"] == "usable":
                    try:
                        if case["metric"] == "assess_rule_pass":
                            result = assess.score_case(case["exp"], rep)
                            if result["schema"]:
                                raise ValueError()
                            row["hits"] = int(result["pass"]); row["alarm"] = case["control"] and not result["pass"]
                            row["signature"] = [int(result["pass"])]
                        else:
                            result = score.score_case(case["exp"], rep)
                            if any(v.startswith("malformed:") for v in result["violations"]):
                                raise ValueError()
                            row["denominator"] = result["planted"] or 1
                            row["hits"] = result["recall_hits"] if result["planted"] else int(not result["violations"])
                            row["alarm"] = bool(result["false_alarm"])
                            row["signature"] = [row["hits"], row["denominator"], int(row["alarm"])] + ["miss" if p["id"] in result["missed"] else "low" if p["id"] in result["low_severity"] else "hit" for p in case["exp"].get("planted", [])]
                            weakened = copy.deepcopy(case["exp"])
                            weak_terms = 0
                            for planted in weakened.get("planted", []):
                                words = planted.get("any_words", [])
                                weak_terms += sum(w.lower().strip() in GENERIC for w in words)
                                planted["any_words"] = [w for w in words if w.lower().strip() not in GENERIC]
                            if weak_terms and score.score_case(weakened, rep)["recall_hits"] < result["recall_hits"]:
                                row["matcher_flags"] += 1
                            fs = score.norm_findings(rep)
                            for planted in case["exp"].get("planted", []):
                                if planted["id"] in result["missed"] and any(not f["refuted"] and not f["nv"] and score.loc_dist(f["loc"], planted) is not None and score.loc_dist(f["loc"], planted) <= 3 for f in fs):
                                    row["matcher_flags"] += 1
                    except (ValueError, TypeError, KeyError, AttributeError):
                        row["status"] = "invalid_report"; issue("invalid_report", False)
                observations[identity].append(row)
                grid.add((row["text"], row["model"], row["repeat"]))
        except InputError as error:
            issue(error.args[0], private); complete = False
        except OSError:
            issue("missing_run_file", private); complete = False
        except (ValueError, KeyError, TypeError):
            issue("invalid_run_data", private); complete = False
    if issues or any(k.startswith("issue_") for k in holdout):
        complete = False
    output = diagnose(list(corpus.values()), observations, complete, grid)
    return {"schema": "case-health-1", "new_model_runs": 0, "scoring": "current-key rescoring; not a replacement for published as-run totals",
            "assessor_sha256": hashlib.sha256(HERE.read_bytes()).hexdigest(),
            "scorer_sha256": {name: hashlib.sha256((repo / "evals" / name).read_bytes()).hexdigest() for name in ("score.py", "score_assess.py")},
            "enumeration_complete": complete, "recorded_run_directories": inventory,
            "coverage_counts": dict(sorted(collections.Counter(c['coverage_label'] for c in output).items())),
            "issues": dict(sorted(issues.items())), "holdout_aggregate": dict(sorted(holdout.items())),
            "cases": output, "verdict_counts": dict(sorted(collections.Counter(c["verdict"] for c in output).items()))}


def markdown(data):
    lines = ["# Case health, " + data["as_of"], "", "Offline recommendations only. No case is edited or deleted; no model was called.",
             "", data["scoring"] + ".", "", "## Coverage and limits", "",
             f"Development cases: {len(data['cases'])}. Recorded run directories: {data['recorded_run_directories']}.",
             "Full-enumeration redundancy evidence: " + ("available" if data["enumeration_complete"] else "not established") + ".",
             "Unknown text/model identities are retained as unknown. Dates are recorded source/run dates, not filesystem mtimes.",
             "Stop/fallback shares count explicit recorded flags only; missing usage metadata cannot establish their absence.",
             "Missing/invalid inputs are counted below; absence from a partial historical run is not a scored miss.",
             "Assess case-rule pass rates are not planted-defect recall; control failures there are rule failures, not necessarily open High findings.",
             "The JSON companion contains per-text/model rates, status shares, recorded dates and the exact recommendation evidence.",
             "Counts-only publications cannot populate per-case observations and are not expanded into invented runs.",
             "", "Verdicts: " + json.dumps(data["verdict_counts"], sort_keys=True), "",
             "Coverage: " + json.dumps(data.get('coverage_counts', {}), sort_keys=True), "",
             "NO-DATA means zero recorded reviews, not a tested defect in the case. Its authorized verdict remains UNTESTABLE.",
             "Overlap lists contain at most three examples per case, with exact total/omitted counts in JSON; proven full-grid pairs are never truncated.",
             "",
             "Input diagnostics: " + json.dumps(data["issues"], sort_keys=True), "", "## Hold-out aggregate only", "",
             json.dumps(data["holdout_aggregate"], sort_keys=True), ""]
    for guard, title in ((True, "Disclosure and safety regression guards"), (False, "Other development cases")):
        lines += ["## " + title, "", "| Case | Recommendation | Usable / recorded | Evidence |", "|---|---|---|---|"]
        for c in data["cases"]:
            if c["regression_guard"] != guard:
                continue
            evidence = "; ".join(c["reasons"]).replace("|", "\\|").replace("\n", " ")
            numerator = sum(g["hits"] for g in c["difficulty"])
            denominator = sum(g["denominator"] for g in c["difficulty"])
            evidence = f"{c['metric']}: {numerator}/{denominator}; " + evidence
            label = c["verdict"] + (" (regression guard)" if guard and c["verdict"] == "KEEP" else "")
            if c.get('coverage_label') == 'NO-DATA':
                label += ' (NO-DATA)'
            lines.append(f"| `{c['id']}` | {label} | {c['usable']} / {c['observations']} | {evidence} |")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=pathlib.Path, default=HERE.parent.parent.parent)
    parser.add_argument("--manifest", type=pathlib.Path)
    parser.add_argument("--output-dir", type=pathlib.Path, required=True)
    parser.add_argument("--as-of", default=dt.datetime.now(dt.timezone.utc).date().isoformat())
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.repo.is_symlink():
            raise InputError("symlink_root")
        root = args.repo.resolve()
        if not date(args.as_of):
            raise InputError("invalid_as_of_date")
        out = args.output_dir.absolute()
        if any(p.is_symlink() for p in [out, *out.parents]):
            raise InputError("symlink_output")
        extra_roots = [safe(root, r["cases"]) for r in read_json(root, args.manifest).get("runs", [])] if args.manifest else []
        for path in [root / "evals/results", root / "evals/cases", *list((root / "evals").glob("*/cases")), *extra_roots]:
            if out == path or path in out.parents:
                raise InputError("output_inside_inputs")
        targets = [out / "case-health.json", out / "case-health.md"]
        if args.manifest and safe(root, args.manifest) in targets:
            raise InputError("output_overwrites_manifest")
        if any(p.is_symlink() or (p.exists() and not args.force) for p in targets):
            raise InputError("output_exists")
        data = load(root, args.manifest)
        data["as_of"] = date(args.as_of)
        for case in data["cases"]:
            for field in ("source_date", "last_run_date", "latest_record_date"):
                case[field + "_age_days"] = (dt.date.fromisoformat(data["as_of"]) - dt.date.fromisoformat(case[field])).days if case[field] else None
        out.mkdir(parents=True, exist_ok=True)
        targets[0].write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
        targets[1].write_text(markdown(data))
        errors = sum(v for k, v in data["issues"].items() if k not in ("metadata_absent", "unassociated_metadata_directories"))
        errors += sum(v for k, v in data["holdout_aggregate"].items() if k.startswith("issue_"))
        print(json.dumps({"development_cases": len(data["cases"]), "verdicts": data["verdict_counts"], "input_errors": errors}, sort_keys=True))
        return 1 if errors else 0
    except (InputError, OSError, ValueError, TypeError, KeyError, AttributeError):
        # No exception text: it may contain a hold-out name, path or input bytes.
        print("case-health: input or output validation failed; no private input detail is printed", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
