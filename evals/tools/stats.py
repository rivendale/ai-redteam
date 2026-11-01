#!/usr/bin/env python3
"""Error bars for eval runs: 95% intervals for recall and false-alarm rate, and a paired comparison of two skill texts.

Input is the scorer's JSON (`python3 evals/score.py --reports DIR --json OUT`), one file per repeat. Every file of one text must
score the same cases; a comparison needs the same cases on both sides (repeat counts may differ).

    python3 evals/tools/stats.py summary RUN1.json RUN2.json RUN3.json
    python3 evals/tools/stats.py compare --base B1.json B2.json B3.json --cand C1.json C2.json C3.json [--margin 3]
    python3 evals/tools/stats.py gate --base B*.json --cand C*.json --prereg CAND_OUTDIR/_meta/prereg.json   # or --margin K
    python3 evals/tools/stats.py --self-check

The unit of resampling is the CASE, not the planted defect or the repeat: the repeats of one case share its fixture, its
wording and its difficulty, so they are not independent draws (Miller, "Adding Error Bars to Evals", arXiv 2411.00640, sections
on clustered standard errors and paired differences). Treating the 3 x 20 hold-out detections as 60 independent trials makes the
interval too narrow; the naive Wilson interval is printed beside the clustered one so the difference can be seen.

- Recall is the share of planted defects found at the minimum severity, summed over cases and repeats (the scorer's `recall_hits`
  over `planted`). Its interval is a case-cluster percentile bootstrap of that ratio.
- False-alarm rate is the share of control runs (control x repeat) with at least one open Critical or High (the scorer's
  `false_alarm` > 0). The raw count is reported too, because the published gate counts findings, not control runs.
- A comparison resamples cases jointly for both texts (paired), so a hard case is hard on both sides. It also gives an exact sign
  test on the cases where one text did better than the other (McNemar's exact test when each case has one planted defect and one
  repeat). The verdict is SIGNIFICANT only when the 95% interval excludes zero AND the sign test gives p < 0.05, NOT SIGNIFICANT
  when neither does, and WEAK EVIDENCE when they disagree. A WARNING is printed (and written to --json) whenever an interval rests
  on fewer than 10 clusters (cases or controls), where a percentile bootstrap is too narrow.
- With the same repeats on both sides, the difference is also given in summed counts (hits; control runs with a false alarm), the
  gate's unit. That interval is bootstrapped directly as the summed difference in each resample, not by scaling a rate interval.
- `gate` applies the gate rule that evals/README.md (section "Gate rule") owns, with the margin K pre-registered in the candidate
  run's prereg.json (GATE_MARGIN), and prints PASS or FAIL (exit 0 or 1). `--margin K` on `compare` only reports what a
  "baseline minus K" floor means against the interval.

Standard library only. Nothing here calls a model.
"""
import argparse, json, math, pathlib, random, subprocess, sys, tempfile

Z95 = 1.959963984540054
ALPHA = 0.05
MIN_CLUSTERS = 10          # below this many cases (or controls) the clustered interval is flagged as too narrow to lean on
DEFAULT_B = 10000
DEFAULT_SEED = 20261031


# ------------------------------------------------------------------------------------------------------------------ loading
def load_runs(paths):
    """{case id: {"control": bool, "planted": int, "hits": [per repeat], "fa_runs": [0/1 per repeat], "fa_count": [per repeat]}}.
    Refuses runs whose case sets or planted counts disagree: a comparison over different cases is not paired."""
    if not paths:
        raise ValueError("no run files given")
    cases, ids0 = {}, None
    for p in paths:
        data = json.loads(pathlib.Path(p).read_text()) if not isinstance(p, dict) else p
        rows = data.get("cases") if isinstance(data, dict) else None
        if not isinstance(rows, list) or not rows:
            raise ValueError(f"{p}: not scorer JSON (no 'cases' list); make it with score.py --json")
        ids = [r["id"] for r in rows]
        if len(set(ids)) != len(ids):
            raise ValueError(f"{p}: a case id appears twice")
        if ids0 is None:
            ids0 = set(ids)
        elif set(ids) != ids0:
            raise ValueError(f"{p}: scores different cases from the first file ({sorted(set(ids) ^ ids0)[:5]}); repeats must cover the same cases")
        for r in rows:
            c = cases.setdefault(r["id"], {"control": bool(r["control"]), "planted": int(r["planted"]), "hits": [], "fa_runs": [], "fa_count": []})
            if c["control"] != bool(r["control"]) or c["planted"] != int(r["planted"]):
                raise ValueError(f"{p}: {r['id']} has a different key (control/planted) from the first file; were the cases changed between runs?")
            c["hits"].append(int(r["recall_hits"]))
            c["fa_runs"].append(1 if int(r.get("false_alarm", 0)) > 0 else 0)
            c["fa_count"].append(int(r.get("false_alarm", 0)))
    return cases


def recall_clusters(cases):
    """[(case id, hits summed over repeats, planted x repeats)] for defect cases."""
    return [(cid, sum(c["hits"]), c["planted"] * len(c["hits"])) for cid, c in sorted(cases.items()) if not c["control"] and c["planted"] > 0]


def fa_clusters(cases):
    """[(case id, control runs with a false alarm, control runs)] for controls."""
    return [(cid, sum(c["fa_runs"]), len(c["fa_runs"])) for cid, c in sorted(cases.items()) if c["control"]]


# ---------------------------------------------------------------------------------------------------------------- intervals
def wilson(k, n, z=Z95):
    if n == 0:
        return (None, None)
    p = k / n
    den = 1 + z * z / n
    mid = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, mid - half), min(1.0, mid + half))


def _pct(sorted_vals, q):
    """Percentile of an already sorted list (linear interpolation)."""
    if not sorted_vals:
        return None
    i = q * (len(sorted_vals) - 1)
    lo, hi = math.floor(i), math.ceil(i)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (i - lo)


def cluster_bootstrap(clusters, b=DEFAULT_B, seed=DEFAULT_SEED):
    """Percentile 95% interval of sum(k)/sum(n), resampling clusters with replacement."""
    if not clusters:
        return (None, None)
    rng = random.Random(seed)
    m = len(clusters)
    ks = [c[1] for c in clusters]; ns = [c[2] for c in clusters]
    vals = []
    for _ in range(b):
        sk = sn = 0
        for _ in range(m):
            j = rng.randrange(m)
            sk += ks[j]; sn += ns[j]
        vals.append(sk / sn)
    vals.sort()
    return (_pct(vals, 0.025), _pct(vals, 0.975))


def describe(clusters, b, seed):
    k = sum(c[1] for c in clusters); n = sum(c[2] for c in clusters)
    est = k / n if n else None
    warns = []
    if 0 < len(clusters) < MIN_CLUSTERS:
        warns.append(f"WARNING: only {len(clusters)} cluster(s), fewer than {MIN_CLUSTERS}: the clustered interval is too narrow to lean on")
    return {"k": k, "n": n, "clusters": len(clusters), "estimate": est, "ci95_cluster_bootstrap": list(cluster_bootstrap(clusters, b, seed)),
            "ci95_wilson_naive": list(wilson(k, n)), "warnings": warns}


def binom_two_sided(k, n):
    """Exact two-sided sign-test p-value for k successes of n at p = 1/2 (the smaller tail doubled, capped at 1)."""
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(0, min(k, n - k) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def paired(base_clusters, cand_clusters, b=DEFAULT_B, seed=DEFAULT_SEED):
    """Paired case-cluster bootstrap of (candidate rate - base rate), and an exact sign test over cases."""
    bd = {c[0]: c for c in base_clusters}; cd = {c[0]: c for c in cand_clusters}
    if set(bd) != set(cd):
        raise ValueError(f"the two texts were scored on different cases ({sorted(set(bd) ^ set(cd))[:5]}); a paired comparison needs the same cases")
    ids = sorted(bd)
    if not ids:
        return None
    bk = [bd[i][1] for i in ids]; bn = [bd[i][2] for i in ids]; ck = [cd[i][1] for i in ids]; cn = [cd[i][2] for i in ids]
    obs = sum(ck) / sum(cn) - sum(bk) / sum(bn)
    # Same denominator in every case (same planted count and same repeats on both sides): the difference is also stated in summed
    # counts (hits, or control runs with a false alarm), the gate's unit. That interval is bootstrapped directly, as the summed
    # difference in each resample, not by scaling the rate interval by the observed total (the total itself varies between
    # resamples when cases plant different numbers of defects).
    same_n = bn == cn
    rng = random.Random(seed)
    m = len(ids); vals = []; sums = []
    for _ in range(b):
        sbk = sbn = sck = scn = 0
        for _ in range(m):
            j = rng.randrange(m)
            sbk += bk[j]; sbn += bn[j]; sck += ck[j]; scn += cn[j]
        vals.append(sck / scn - sbk / sbn)
        sums.append(sck - sbk)
    vals.sort(); sums.sort()
    lo, hi = _pct(vals, 0.025), _pct(vals, 0.975)
    better = sum(1 for i in range(m) if ck[i] * bn[i] > bk[i] * cn[i])
    worse = sum(1 for i in range(m) if ck[i] * bn[i] < bk[i] * cn[i])
    p = binom_two_sided(better, better + worse)
    out = {"cases": m, "base_rate": sum(bk) / sum(bn), "cand_rate": sum(ck) / sum(cn), "diff": obs, "ci95_paired_bootstrap": [lo, hi],
           "significant": not (lo <= 0 <= hi), "cases_cand_better": better, "cases_cand_worse": worse,
           "sign_test_p": p, "sign_test_significant": p < ALPHA,
           "base_k": sum(bk), "cand_k": sum(ck), "base_n": sum(bn), "cand_n": sum(cn)}
    if same_n:
        out["diff_hits"] = sum(ck) - sum(bk)
        out["ci95_hits"] = [_pct(sums, 0.025), _pct(sums, 0.975)]
    out["verdict"], out["warnings"] = judge(out)
    return out


def judge(r):
    """(verdict, warnings) for a paired difference. SIGNIFICANT only when the bootstrap interval excludes zero AND the exact sign test
    agrees; WEAK EVIDENCE when the two disagree; a warning whenever the interval rests on fewer than MIN_CLUSTERS clusters."""
    warns = []
    if r["cases"] < MIN_CLUSTERS:
        warns.append(f"WARNING: only {r['cases']} cluster(s), fewer than {MIN_CLUSTERS}: a percentile bootstrap over so few cases is too narrow; "
                     "read the interval as indicative and rely on the sign test")
    boot, sign = r["significant"], r["sign_test_significant"]
    if boot != sign:
        warns.append(f"WARNING: the tests disagree: the bootstrap interval {'excludes' if boot else 'contains'} zero but the exact sign test gives "
                     f"p = {r['sign_test_p']:.3f} ({r['cases_cand_better']} vs {r['cases_cand_worse']} discordant): WEAK EVIDENCE")
        return "WEAK EVIDENCE", warns
    return ("SIGNIFICANT" if boot else "NOT SIGNIFICANT"), warns


# ------------------------------------------------------------------------------------------------------------------ reports
def fmt(x, d=3):
    return "n/a" if x is None else f"{x:.{d}f}"


def ci(pair, d=3):
    return f"[{fmt(pair[0], d)}, {fmt(pair[1], d)}]"


def summary(paths, b, seed):
    cases = load_runs(paths)
    reps = len(paths)
    rec = describe(recall_clusters(cases), b, seed)
    fa = describe(fa_clusters(cases), b, seed)
    fa["false_alarm_findings"] = sum(sum(c["fa_count"]) for c in cases.values() if c["control"])
    return {"repeats": reps, "cases": len(cases), "recall": rec, "false_alarm_rate": fa,
            "warnings": [f"recall: {w}" for w in rec["warnings"]] + [f"false-alarm rate: {w}" for w in fa["warnings"]]}


def print_summary(s):
    r, f = s["recall"], s["false_alarm_rate"]
    print(f"recall {fmt(r['estimate'])} ({r['k']}/{r['n']} over {r['clusters']} defect cases x {s['repeats']} repeat(s)); "
          f"95% CI {ci(r['ci95_cluster_bootstrap'])} clustered by case (naive Wilson {ci(r['ci95_wilson_naive'])})")
    if f["n"]:
        print(f"false-alarm rate {fmt(f['estimate'])} ({f['k']}/{f['n']} control runs with an open Critical/High; {f['false_alarm_findings']} such findings); "
              f"95% CI {ci(f['ci95_cluster_bootstrap'])} clustered by case (naive Wilson {ci(f['ci95_wilson_naive'])})")
    else:
        print("false-alarm rate: n/a (no controls in these runs)")
    for w in s["warnings"]:
        print(f"  {w}")


def compare(base_paths, cand_paths, b, seed, margin=None):
    bc, cc = load_runs(base_paths), load_runs(cand_paths)
    if set(bc) != set(cc):
        raise ValueError(f"the two texts were scored on different cases ({sorted(set(bc) ^ set(cc))[:5]}); a paired comparison needs the same cases")
    for cid in bc:
        if bc[cid]["planted"] != cc[cid]["planted"] or bc[cid]["control"] != cc[cid]["control"]:
            raise ValueError(f"{cid} has a different key on the two sides; were the cases changed between the runs?")
    out = {"base": summary(base_paths, b, seed), "cand": summary(cand_paths, b, seed),
           "recall": paired(recall_clusters(bc), recall_clusters(cc), b, seed),
           "false_alarm_rate": paired(fa_clusters(bc), fa_clusters(cc), b, seed)}
    out["warnings"] = [f"recall difference: {w}" for w in (out["recall"] or {}).get("warnings", [])] + \
                      [f"false-alarm difference: {w}" for w in (out["false_alarm_rate"] or {}).get("warnings", [])]
    if margin is not None and out["recall"] and "ci95_hits" in out["recall"]:
        r = out["recall"]
        lo, hi = r["ci95_hits"]
        out["margin"] = {"margin_hits": margin, "observed_diff_hits": r["diff_hits"], "ci95_hits": [lo, hi],
                         "half_width_hits": (hi - lo) / 2, "floor_inside_ci": lo <= -margin <= hi,
                         "passes_floor": r["diff_hits"] >= -margin}
    return out


def print_compare(c):
    r, f = c["recall"], c["false_alarm_rate"]
    print(f"recall difference: {r['verdict']} (candidate - base = {r['diff']:+.3f}, 95% paired CI {ci(r['ci95_paired_bootstrap'])}, "
          f"{r['cases']} cases; sign test {r['cases_cand_better']} better / {r['cases_cand_worse']} worse, p = {r['sign_test_p']:.3f})")
    if "diff_hits" in r:
        print(f"  in summed hits: {r['diff_hits']:+d} ({r['cand_k']} vs {r['base_k']} of {r['base_n']}), 95% CI {ci(r['ci95_hits'], 1)}")
    for w in r["warnings"]:
        print(f"  {w}")
    if f:
        print(f"false-alarm rate difference: {f['verdict']} (candidate - base = {f['diff']:+.3f}, 95% paired CI {ci(f['ci95_paired_bootstrap'])}, "
              f"{f['cases']} controls; sign test {f['cases_cand_better']} more / {f['cases_cand_worse']} fewer, p = {f['sign_test_p']:.3f})")
        if "diff_hits" in f:
            print(f"  in summed control runs with a false alarm: {f['diff_hits']:+d} ({f['cand_k']} vs {f['base_k']} of {f['base_n']}), 95% CI {ci(f['ci95_hits'], 1)}")
        for w in f["warnings"]:
            print(f"  {w}")
    if "margin" in c:
        m = c["margin"]
        print(f"floor 'base minus {m['margin_hits']}': observed {m['observed_diff_hits']:+d} hits ({'passes' if m['passes_floor'] else 'fails'}); "
              f"the 95% CI half-width is {m['half_width_hits']:.1f} hits, and -{m['margin_hits']} is "
              f"{'INSIDE' if m['floor_inside_ci'] else 'outside'} the interval")
    print("  base:  ", end=""); print_summary(c["base"])
    print("  cand:  ", end=""); print_summary(c["cand"])


# --------------------------------------------------------------------------------------------------------------------- gate
def margin_from_prereg(path):
    """The margin K pre-registered in a lane's _meta/prereg.json (GATE_MARGIN), or ValueError."""
    rec = json.loads(pathlib.Path(path).read_text())
    k = (rec.get("gate_rule") or {}).get("margin")
    if isinstance(k, bool) or not isinstance(k, (int, float)) or not math.isfinite(k) or k < 0:
        raise ValueError(f"{path} pre-registers no usable margin (gate_rule.margin = {k!r}); start the run with GATE_MARGIN=<K>")
    return k


def gate(c, k):
    """The statistical gate (owned by evals/README.md, section "Gate rule"), on one compare() result and a pre-registered K >= 0.
    Recall passes when the lower bound of the paired 95% case-clustered interval of (candidate - base) summed hits is above -K AND the
    exact sign test shows no significant loss. False alarms (control runs with an open Critical/High) pass when the upper bound of
    the same interval is below +K AND the sign test shows no significant rise. The gate passes when both pass."""
    if not (isinstance(k, (int, float)) and not isinstance(k, bool) and math.isfinite(k) and k >= 0):
        raise ValueError(f"the margin K must be a finite number >= 0, not {k!r}")
    parts = {}
    for name, key, loss_dir in (("recall", "recall", "worse"), ("false_alarms", "false_alarm_rate", "better")):
        r = c[key]
        if not r:
            parts[name] = {"pass": False, "reason": "no cases of this kind in the runs: this half of the gate cannot be tested"}
            continue
        if "ci95_hits" not in r:
            raise ValueError(f"{name}: the two sides ran different repeat counts, so summed counts are not comparable; run the same repeats")
        lo, hi = r["ci95_hits"]
        losses, gains = (r["cases_cand_worse"], r["cases_cand_better"]) if loss_dir == "worse" else (r["cases_cand_better"], r["cases_cand_worse"])
        sign_loss = r["sign_test_significant"] and losses > gains
        bound_ok = lo > -k if name == "recall" else hi < k
        parts[name] = {"pass": bound_ok and not sign_loss, "bound": lo if name == "recall" else hi,
                       "bound_rule": f"lower bound > -{k}" if name == "recall" else f"upper bound < +{k}", "bound_ok": bound_ok,
                       "sign_test_loss": sign_loss, "sign_test_p": r["sign_test_p"], "losing_cases": losses, "gaining_cases": gains,
                       "observed_diff": r["diff_hits"], "ci95": [lo, hi], "warnings": r["warnings"]}
    return {"margin": k, "pass": all(v["pass"] for v in parts.values()), "recall": parts["recall"], "false_alarms": parts["false_alarms"],
            "warnings": c.get("warnings", [])}


def print_gate(g):
    labels = {"recall": "recall (summed hits)", "false_alarms": "false alarms (summed control runs with an open Critical/High)"}
    for name in ("recall", "false_alarms"):
        v = g[name]
        if "reason" in v:
            print(f"{labels[name]}: FAIL ({v['reason']})"); continue
        why = [f"95% CI {ci(v['ci95'], 1)}, {v['bound_rule']}: {'yes' if v['bound_ok'] else 'NO'}",
               f"sign test {v['losing_cases']} worse / {v['gaining_cases']} better, p = {v['sign_test_p']:.3f}: "
               f"{'SIGNIFICANT LOSS' if v['sign_test_loss'] else 'no significant loss'}"]
        print(f"{labels[name]}: {'PASS' if v['pass'] else 'FAIL'} (observed {v['observed_diff']:+d}; " + "; ".join(why) + ")")
    for w in g["warnings"]:
        print(f"  {w}")
    print(f"gate (K = {g['margin']}): {'PASS' if g['pass'] else 'FAIL'}")


# --------------------------------------------------------------------------------------------------------------- self-check
def _run(rows):
    """A scorer-shaped JSON document from (id, control, planted, recall_hits, false_alarm) rows."""
    return {"totals": {}, "cases": [{"id": i, "slug": "", "control": c, "planted": p, "recall_hits": h, "found_any": h, "false_alarm": fa,
                                     "extra_high": 0, "violations": [], "verdict": "REWORK", "missed": [], "low_severity": []}
                                    for i, c, p, h, fa in rows]}


def self_check():
    fails = []

    def expect(name, cond, detail=""):
        print(("ok    " if cond else "FAIL  ") + name + ("" if cond else f"  ({detail})"))
        if not cond:
            fails.append(name)

    b = 4000
    # 1. Wilson against a textbook value (8 of 10: 0.490 to 0.943) and its edges
    lo, hi = wilson(8, 10)
    expect("Wilson 8/10 is [0.490, 0.943]", abs(lo - 0.4902) < 1e-3 and abs(hi - 0.9433) < 1e-3, f"{lo}, {hi}")
    expect("Wilson 0/20 starts at 0 and 20/20 ends at 1", wilson(0, 20)[0] == 0 and wilson(20, 20)[1] == 1, f"{wilson(0, 20)} {wilson(20, 20)}")
    expect("exact sign test: 0 of 10 is p = 0.002, 5 of 10 is p = 1", abs(binom_two_sided(0, 10) - 2 / 1024) < 1e-12 and binom_two_sided(5, 10) == 1.0)

    # 2. the gate-sized loss: 20 one-defect cases, 3 repeats, base 56/60, candidate 53/60 -> must NOT be significant
    def arm(misses_by_repeat, n=20, controls=()):
        runs = []
        for rep_miss in misses_by_repeat:
            rows = [(f"case-{i:02d}", False, 1, 0 if i in rep_miss else 1, 0) for i in range(1, n + 1)]
            rows += [(f"case-{100 + j:03d}", True, 0, 0, fa[k]) for j, fa in enumerate(controls) for k in [len(runs)]]
            runs.append(_run(rows))
        return runs
    base = arm([{1, 2}, {3}, {4}])                 # 4 misses -> 56/60
    cand = arm([{1, 2, 5}, {3, 6}, {4, 7}])          # 7 misses -> 53/60, same hard cases plus three one-off misses
    c = compare(base, cand, b, DEFAULT_SEED, margin=3)
    expect("a 3-hit loss of 60 (the published hold-out gap) is NOT significant", not c["recall"]["significant"], c["recall"])
    expect("  and its 95% CI in hits contains -3 and 0", c["margin"]["floor_inside_ci"] and c["recall"]["ci95_hits"][1] >= 0, c["margin"])
    expect("  and the sign test agrees (p > 0.05)", c["recall"]["sign_test_p"] > 0.05, c["recall"]["sign_test_p"])

    # 3. identical texts: difference exactly 0, never significant
    c = compare(base, base, b, DEFAULT_SEED)
    expect("identical runs: difference 0 and not significant", c["recall"]["diff"] == 0 and not c["recall"]["significant"], c["recall"])

    # 4. a large loss must be flagged: 40 cases, base finds all, candidate misses 30 cases in every repeat
    big_b = arm([set(), set(), set()], n=40)
    big_c = arm([set(range(1, 31))] * 3, n=40)
    c = compare(big_b, big_c, b, DEFAULT_SEED)
    expect("a 30-of-40-case loss is significant by both tests", c["recall"]["significant"] and c["recall"]["sign_test_p"] < 0.001, c["recall"])

    # 5. clustering: repeats perfectly correlated (each case all-or-nothing) -> the clustered CI is wider than the naive one
    corr = arm([set(range(1, 11))] * 3, n=20)                # 10 of 20 cases found every time: 30/60
    s = summary(corr, b, DEFAULT_SEED)["recall"]
    wb = s["ci95_cluster_bootstrap"][1] - s["ci95_cluster_bootstrap"][0]
    ww = s["ci95_wilson_naive"][1] - s["ci95_wilson_naive"][0]
    expect("correlated repeats: clustered CI is wider than naive Wilson by > 1.3x", wb > 1.3 * ww, f"{wb:.3f} vs {ww:.3f}")
    # and independent-looking repeats (a different case missed each time) do not inflate it
    indep = arm([set(range(1, 11)), set(range(11, 21)), set(range(1, 6)) | set(range(16, 21))], n=20)
    s2 = summary(indep, b, DEFAULT_SEED)["recall"]
    wb2 = s2["ci95_cluster_bootstrap"][1] - s2["ci95_cluster_bootstrap"][0]
    expect("uncorrelated repeats: clustered CI is narrower than with correlated repeats", wb2 < wb, f"{wb2:.3f} vs {wb:.3f}")

    # 6. false alarms on controls
    fb = arm([set()] * 3, n=5, controls=[(0, 0, 0)] * 10)
    fc = arm([set()] * 3, n=5, controls=[(1, 1, 1)] * 10)
    c = compare(fb, fc, b, DEFAULT_SEED)
    expect("every control flagged in every run against none is a significant false-alarm increase",
           c["false_alarm_rate"]["significant"] and c["false_alarm_rate"]["diff"] == 1.0, c["false_alarm_rate"])
    one = arm([set()] * 3, n=5, controls=[(0, 0, 0)] * 9 + [(1, 0, 0)])
    c = compare(fb, one, b, DEFAULT_SEED)
    expect("one false alarm in 30 control runs is NOT significant", not c["false_alarm_rate"]["significant"], c["false_alarm_rate"])
    expect("a run with no controls reports n/a, not an error", summary(base, b, DEFAULT_SEED)["false_alarm_rate"]["estimate"] is None)

    # 7. refusals: different cases between repeats or between texts, a changed key, a file that is not scorer JSON
    def refused(fn):
        try:
            fn()
        except ValueError:
            return True
        return False
    short = _run([(f"case-{i:02d}", False, 1, 1, 0) for i in range(1, 20)])
    expect("repeats over different cases are refused", refused(lambda: load_runs([base[0], short])))
    expect("texts scored on different cases are refused", refused(lambda: compare(base, [short], b, DEFAULT_SEED)))
    rekey = _run([(f"case-{i:02d}", False, 2 if i == 1 else 1, 1, 0) for i in range(1, 21)])
    expect("a case whose planted count changed between texts is refused", refused(lambda: compare(base, [rekey], b, DEFAULT_SEED)))
    expect("a file that is not scorer JSON is refused", refused(lambda: load_runs([{"totals": {}}])))

    # 8. determinism and the file path: same seed, same interval; the CLI reads what score.py --json writes
    a1 = summary(base, b, 7)["recall"]["ci95_cluster_bootstrap"]; a2 = summary(base, b, 7)["recall"]["ci95_cluster_bootstrap"]
    expect("the same seed gives the same interval", a1 == a2, f"{a1} {a2}")
    with tempfile.TemporaryDirectory() as t:
        ps = []
        for i, r in enumerate(base):
            p = pathlib.Path(t) / f"r{i}.json"; p.write_text(json.dumps(r, indent=2) + "\n"); ps.append(str(p))
        s = summary(ps, b, DEFAULT_SEED)
        expect("files on disk load: 56/60 over 20 cases x 3 repeats", s["recall"]["k"] == 56 and s["recall"]["n"] == 60 and s["repeats"] == 3, s["recall"])

    # 9. the summed-hit interval is bootstrapped directly. With equal-size clusters it equals the rate interval times the total; with
    #    unequal ones it must not: 10 cases, one planting 10 defects and lost entirely by the candidate, nine planting one each.
    c = compare(base, cand, b, DEFAULT_SEED)
    rl, rh = c["recall"]["ci95_paired_bootstrap"]; hl, hh = c["recall"]["ci95_hits"]
    expect("equal-size cases: the hit interval equals the rate interval x 60", abs(hl - 60 * rl) < 1e-6 and abs(hh - 60 * rh) < 1e-6, (rl, rh, hl, hh))
    ub = [_run([("case-01", False, 10, 10, 0)] + [(f"case-{i:02d}", False, 1, 1, 0) for i in range(2, 11)])]
    uc = [_run([("case-01", False, 10, 0, 0)] + [(f"case-{i:02d}", False, 1, 1, 0) for i in range(2, 11)])]
    r = compare(ub, uc, b, DEFAULT_SEED)["recall"]
    expect("unequal cases: the hit interval reaches -30 (case 1 drawn 3 times), which scaling the rate interval cannot (about -15)",
           r["ci95_hits"][0] <= -29 and r["ci95_hits"][1] == 0 and r["ci95_paired_bootstrap"][0] * 19 > -20, r)

    # 10. few clusters and disagreeing tests. The plain-prompt hold-out shape: 6 controls, 4 of them flagged by the base and none by
    #     the candidate. The bootstrap interval excludes zero; the sign test (0 more, 4 fewer) gives p = 0.125. Not a bare SIGNIFICANT.
    pb = arm([set()] * 3, n=5, controls=[(1, 1, 1), (1, 1, 0), (1, 0, 1), (0, 1, 1), (0, 0, 0), (0, 0, 0)])
    pc = arm([set()] * 3, n=5, controls=[(0, 0, 0)] * 6)
    c = compare(pb, pc, b, DEFAULT_SEED)
    f = c["false_alarm_rate"]
    expect("6 controls, 4 discordant: bootstrap excludes zero, sign test p = 0.125", f["significant"] and abs(f["sign_test_p"] - 0.125) < 1e-12, f)
    expect("  and the verdict is WEAK EVIDENCE, not SIGNIFICANT", f["verdict"] == "WEAK EVIDENCE", f["verdict"])
    expect("  with a fewer-than-10-clusters warning and a disagreement warning",
           any("fewer than 10" in w for w in f["warnings"]) and any("disagree" in w for w in f["warnings"]), f["warnings"])
    expect("  carried to the top-level warnings", any(w.startswith("false-alarm difference:") for w in c["warnings"]), c["warnings"])
    expect("20 cases, both tests agree: no warning", compare(big_b, big_c, b, DEFAULT_SEED)["recall"]["warnings"] == [] and
           compare(big_b, big_c, b, DEFAULT_SEED)["recall"]["verdict"] == "SIGNIFICANT")
    expect("summary warns on 6 controls and not on 20 defect cases",
           summary(pb, b, DEFAULT_SEED)["false_alarm_rate"]["warnings"] and not summary(base, b, DEFAULT_SEED)["recall"]["warnings"])
    with tempfile.TemporaryDirectory() as t:
        ps = {}
        for side, runs in (("b", pb), ("c", pc)):
            ps[side] = []
            for i, rr in enumerate(runs):
                q = pathlib.Path(t) / f"{side}{i}.json"; q.write_text(json.dumps(rr)); ps[side].append(str(q))
        out = pathlib.Path(t) / "cmp.json"
        res = subprocess.run([sys.executable, __file__, "--resamples", "2000", "--json", str(out), "compare", "--base", *ps["b"], "--cand", *ps["c"]],
                             capture_output=True, text=True)
        js = json.loads(out.read_text()) if out.exists() else {}
        expect("the CLI prints WEAK EVIDENCE and WARNING, and --json carries the warnings",
               "false-alarm rate difference: WEAK EVIDENCE" in res.stdout and "WARNING" in res.stdout and "difference: SIGNIFICANT" not in res.stdout
               and js.get("false_alarm_rate", {}).get("verdict") == "WEAK EVIDENCE" and js.get("warnings"), res.stdout + res.stderr)

    # 11. the gate: lower bound of the summed-hit interval above -K and no significant sign-test loss; false alarms the same way up.
    wc = arm([{1, 2}, {3}, {4}], controls=[(0, 0, 0)] * 8 + [(1, 0, 0), (0, 1, 1)])     # base with 10 controls, two of them flagged
    g = gate(compare(wc, wc, b, DEFAULT_SEED), 3)
    expect("gate: identical runs pass at K = 3", g["pass"] and g["recall"]["pass"] and g["false_alarms"]["pass"], g)
    expect("gate: identical runs fail at K = 0 (the bound must be strictly above -K)", not gate(compare(wc, wc, b, DEFAULT_SEED), 0)["pass"])
    c3 = compare(base, cand, b, DEFAULT_SEED)
    g = gate(c3, 3)
    expect("gate: the 3-hit loss of 60 FAILS at K = 3 (the interval reaches below -3)", not g["recall"]["pass"] and c3["recall"]["ci95_hits"][0] <= -3, g["recall"])
    k_ok = math.floor(-c3["recall"]["ci95_hits"][0]) + 1
    expect(f"gate: the same loss passes at K = {k_ok}, just beyond its lower bound", gate(c3, k_ok)["recall"]["pass"], gate(c3, k_ok)["recall"])
    expect("gate: a 30-of-40-case loss fails", not gate(compare(big_b, big_c, b, DEFAULT_SEED), 3)["pass"])
    sb = arm([set()] * 1, n=40); sc = arm([set(range(1, 11))], n=40)          # 10 cases lose their one hit, nothing gains
    g = gate(compare(sb, sc, b, DEFAULT_SEED), 20)
    expect("gate: inside a wide margin (K = 20) but 10 worse / 0 better (p = 0.002) still fails on the sign test",
           g["recall"]["bound_ok"] and g["recall"]["sign_test_loss"] and not g["recall"]["pass"], g["recall"])
    fl = arm([set()] * 3, n=5, controls=[(0, 0, 0)] * 10); fh = arm([set()] * 3, n=5, controls=[(1, 1, 1)] * 10)
    g = gate(compare(fl, fh, b, DEFAULT_SEED), 3)
    expect("gate: every control newly flagged fails the false-alarm half", g["recall"]["pass"] and not g["false_alarms"]["pass"], g)
    g = gate(compare(fh, fl, b, DEFAULT_SEED), 3)
    expect("gate: fewer false alarms pass the false-alarm half", g["false_alarms"]["pass"], g["false_alarms"])
    g = gate(compare(base, base, b, DEFAULT_SEED), 3)
    expect("gate: runs with no controls fail, with a reason", not g["pass"] and "reason" in g["false_alarms"] and g["recall"]["pass"], g)
    expect("gate: a negative or non-numeric K is refused", refused(lambda: gate(c3, -1)) and refused(lambda: gate(c3, "3")))
    with tempfile.TemporaryDirectory() as t:
        good = pathlib.Path(t) / "p.json"; good.write_text(json.dumps({"gate_rule": {"margin": 3}}))
        none = pathlib.Path(t) / "n.json"; none.write_text(json.dumps({"gate_rule": {"margin": None}}))
        expect("gate: K is read from a prereg.json, and a record with no margin is refused",
               margin_from_prereg(good) == 3 and refused(lambda: margin_from_prereg(none)))

    print("all checks hold" if not fails else f"{len(fails)} check(s) FAILED")
    return 0 if not fails else 1


# --------------------------------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-check", action="store_true")
    ap.add_argument("--resamples", type=int, default=DEFAULT_B)
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED)
    ap.add_argument("--json", help="also write the numbers here")
    sub = ap.add_subparsers(dest="cmd")
    sp = sub.add_parser("summary", help="intervals for one text (one scorer JSON per repeat)")
    sp.add_argument("runs", nargs="+")
    cp = sub.add_parser("compare", help="paired comparison of two texts on the same cases")
    cp.add_argument("--base", nargs="+", required=True)
    cp.add_argument("--cand", nargs="+", required=True)
    cp.add_argument("--margin", type=int, help="state what a 'base minus MARGIN' recall floor (summed hits) means against the interval")
    gp = sub.add_parser("gate", help="PASS or FAIL under the statistical gate rule (evals/README.md, section 'Gate rule')")
    gp.add_argument("--base", nargs="+", required=True)
    gp.add_argument("--cand", nargs="+", required=True)
    gp.add_argument("--margin", type=float, help="the pre-registered margin K in summed hits (or give --prereg)")
    gp.add_argument("--prereg", help="the candidate run's _meta/prereg.json; K is read from its gate_rule.margin (GATE_MARGIN)")
    a = ap.parse_args()
    if a.self_check:
        return self_check()
    if a.resamples < 1000:
        ap.error("--resamples below 1000 gives an unstable 95% interval")
    try:
        if a.cmd == "summary":
            res = summary(a.runs, a.resamples, a.seed); print_summary(res)
        elif a.cmd == "compare":
            res = compare(a.base, a.cand, a.resamples, a.seed, a.margin); print_compare(res)
        elif a.cmd == "gate":
            k = a.margin
            if a.prereg:
                kp = margin_from_prereg(a.prereg)
                if k is not None and k != kp:
                    raise ValueError(f"--margin {k} differs from the pre-registered K = {kp} in {a.prereg}; the pre-registered value is the rule")
                k = kp
            if k is None:
                ap.error("gate needs the pre-registered K: --prereg OUTDIR/_meta/prereg.json or --margin K")
            if k == int(k):
                k = int(k)
            res = gate(compare(a.base, a.cand, a.resamples, a.seed), k); print_gate(res)
        else:
            ap.error("give summary, compare, gate or --self-check")
    except (ValueError, OSError, KeyError) as e:
        print(f"refused: {e}", file=sys.stderr)
        return 2
    res["method"] = {"resamples": a.resamples, "seed": a.seed, "cluster": "case", "interval": "percentile", "reference": "arXiv 2411.00640"}
    if a.json:
        pathlib.Path(a.json).write_text(json.dumps(res, indent=2) + "\n")
    return 0 if a.cmd != "gate" or res["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
