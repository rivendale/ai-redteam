#!/usr/bin/env python3
"""Synthetic diagnostics for the failure list; no production cases or reviewers."""
import copy
import contextlib
import hashlib
import io
import importlib.util
import json
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("case_health", ROOT / "evals/tools/case_health.py")
health = importlib.util.module_from_spec(spec)
spec.loader.exec_module(health)


def case(identity="dev/case-01", guard=False, control=False):
    return {"id": identity, "suite": "dev", "regression_guard": guard, "control": control, "metric": "defect_recall"}


def observation(hit=1, text="A", model="M", repeat=1, **extra):
    return {"status": "usable", "text": text, "model": model, "repeat": repeat,
            "hits": hit, "denominator": 1, "signature": [hit], "alarm": False, **extra}


class Aggregate(unittest.TestCase):
    def result(self, rows, **kw):
        c = case(**kw)
        return health.diagnose([c], {c["id"]: rows})[0]

    def test_empty_is_untestable(self):
        self.assertEqual(self.result([])["verdict"], "UNTESTABLE")

    def test_no_data_coverage_is_distinct_from_unusable_reviews(self):
        empty = self.result([])
        failed = self.result([observation(status='invalid_report')])
        self.assertEqual(empty['verdict'], 'UNTESTABLE')
        self.assertEqual(empty['coverage_label'], 'NO-DATA')
        self.assertEqual(failed['verdict'], 'UNTESTABLE')
        self.assertEqual(failed['coverage_label'], 'NO-USABLE-REVIEWS')

    def test_many_partial_overlaps_are_counted_but_examples_are_bounded(self):
        cs = [case(f'dev/case-{n:02d}') for n in range(12)]
        rows = [observation()]
        result = health.diagnose(cs, {c['id']: rows for c in cs})
        self.assertTrue(all(r['overlap_count'] == 11 for r in result))
        self.assertTrue(all(len(r['redundancy']) <= 3 for r in result))
        self.assertTrue(all(r['overlap_examples_omitted'] == 8 for r in result))
        self.assertTrue(all(r['verdict'] == 'SHARPEN' for r in result))

    def test_saturation_and_never_failed(self):
        r = self.result([observation()])
        self.assertEqual(r["verdict"], "SHARPEN")
        self.assertTrue(any("never failed" in x for x in r["reasons"]))

    def test_disclosure_carveout_every_category(self):
        for label in ["required disclosure", "regulatory statement", "legal statement", "consent", "privacy", "safety warning"]:
            self.assertTrue(health.protection({"title": label}))
            r = self.result([observation()], guard=health.protection({"title": label}))
            self.assertEqual(r["verdict"], "KEEP", label)
            self.assertTrue(r["regression_guard"])
        self.assertTrue(health.protection({"track": "R"}))

    def test_control_flagged_every_time(self):
        r = self.result([observation(alarm=True), observation(alarm=True, repeat=2)], control=True)
        self.assertEqual((r["verdict"], r["control_flags"], r["control_denominator"]), ("FIX-CONTROL", 2, 2))

    def test_floor_is_not_a_deletion(self):
        self.assertEqual(self.result([observation(0)])["verdict"], "REVIEW-MATCHER")

    def test_flaky_and_discriminating(self):
        r = self.result([observation(), observation(0, repeat=2)])
        self.assertEqual(r["verdict"], "FLAKY")
        r = self.result([observation(text="A"), observation(0, text="B")])
        self.assertTrue(r["discriminates_known_groups"])
        self.assertFalse(r["repeat_disagreement"])

    def test_unusable_is_not_a_miss(self):
        for status in ["safety_stop", "fallback", "invalid_report", "missing_report"]:
            r = self.result([observation(status=status)])
            self.assertEqual(r["verdict"], "UNTESTABLE")
            self.assertEqual(r["difficulty"], [])

    def pair(self, texts=("A", "B", "C"), complete=True, change=False, missing=False, guard=False):
        a, b = case(), case("dev/case-02", guard=guard)
        rows = [observation(text=t) for t in texts]
        other = copy.deepcopy(rows)
        if change:
            other[-1] = observation(0, text=texts[-1])
        if missing:
            other.pop()
        grid = {(r["text"], r["model"], r["repeat"]) for r in rows}
        return health.diagnose([a, b], {a["id"]: rows, b["id"]: other}, complete, grid)

    def test_full_enumeration_rule(self):
        self.assertEqual(self.pair()[0]["verdict"], "RETIRE-CANDIDATE")
        for kw in [{"texts": ("A", "B")}, {"complete": False}, {"change": True}, {"missing": True}]:
            for c in self.pair(**kw):
                self.assertNotEqual(c["verdict"], "RETIRE-CANDIDATE", kw)
        self.assertEqual(self.pair(guard=True)[1]["verdict"], "KEEP")

    def test_unknown_identity_cannot_prove_redundancy(self):
        rows = [observation(text=None, repeat=n) for n in range(3)]
        cs = [case(), case("dev/case-02")]
        out = health.diagnose(cs, {c["id"]: rows for c in cs}, True, {(None, "M", n) for n in range(3)})
        self.assertTrue(all(c["verdict"] != "RETIRE-CANDIDATE" for c in out))

    def test_meta_model_and_stops(self):
        self.assertEqual(health.metadata({"output_tokens_by_model": {"A": 3, "B": 4}})[1], "fallback")
        self.assertEqual(health.metadata({"models": ["A"], "safety_stops": 1})[1], "safety_stop")
        self.assertEqual(health.metadata({"model": "A", "requested_model": "B"})[1], "fallback")

    def test_only_three_combinations_are_not_three_texts_or_models(self):
        cs = [case(), case("dev/case-02")]
        rows = [observation(text="A", model="M"), observation(text="A", model="N"), observation(text="B", model="M")]
        grid = {(r["text"], r["model"], r["repeat"]) for r in rows}
        result = health.diagnose(cs, {c["id"]: rows for c in cs}, True, grid)
        self.assertTrue(all(c["verdict"] != "RETIRE-CANDIDATE" for c in result))

    def test_three_distinct_models_can_establish_vectors(self):
        cs = [case(), case("dev/case-02")]
        rows = [observation(model=name) for name in ['A', 'B', 'C']]
        grid = {(r['text'], r['model'], r['repeat']) for r in rows}
        result = health.diagnose(cs, {c['id']: rows for c in cs}, True, grid)
        self.assertEqual(result[0]['verdict'], 'RETIRE-CANDIDATE')

    def test_unknown_model_sentinels_are_not_provenance(self):
        self.assertIsNone(health.metadata({'models': ['unknown']})[0])
        with self.assertRaises(health.InputError):
            health.metadata({'models': [42]})

    def test_stop_and_fallback_share_is_a_union(self):
        r = self.result([observation(status="fallback", safety_stop=True), observation()])
        self.assertEqual((r["safety_stop_share"], r["fallback_share"], r["untestable_share"]), (.5, .5, .5))


class Inputs(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        self.cases = self.root / "evals/cases"
        self.manifest = {"schema": "case-health-runs-1", "enumeration_complete": True, "runs": []}

    def tearDown(self):
        self.tmp.cleanup()

    def add_case(self, cid="case-01", control=False, words=None, all_words=None, guard=False, directory=None):
        d = (directory or self.cases) / cid
        d.mkdir(parents=True)
        exp = {"id": cid, "control": control, "planted": [] if control else [{"id": "p1", "file": "work/a.py", "lines": [1, 1], "min_severity": "High", "any_words": words or ["needle"], "all_words": all_words or []}],
               "must": [], "must_not": [], "case_health": {"regression_guard": guard}, "proof": {"shell": "exit 99"}}
        (d / "expected.json").write_text(json.dumps(exp))
        for name in ["request.md", "context.md"]:
            (d / name).write_text("Synthetic review input.")
        return exp

    def add_run(self, text="A", cid="case-01", report=None, private=False, cases=None, model="M"):
        n = len(self.manifest["runs"])
        d = self.root / f"evals/results/run-{n}"
        d.mkdir(parents=True)
        report = report if report is not None else {"verdict": "REWORK", "findings": [{"severity": "High", "location": "work/a.py:1", "evidence_level": "CONFIRMED", "scenario": "needle causes an observable failure", "fix": "change it"}]}
        (d / (cid + ".json")).write_text(json.dumps(report))
        (d / "_meta").mkdir()
        (d / "_meta" / (cid + ".usage.json")).write_text(json.dumps({"model": model}))
        self.manifest["runs"].append({"reports": str(d.relative_to(self.root)), "cases": cases or "evals/cases", "text": text, "model": model, "repeat": 1, "expected_cases": [cid], "holdout": private})
        return d

    def load(self):
        p = self.root / "runs.json"
        p.write_text(json.dumps(self.manifest))
        return health.load(self.root, p)

    def test_complete_manifest_and_current_key_scoring(self):
        self.add_case()
        for text in ["A", "B", "C"]:
            self.add_run(text=text)
        data = self.load()
        self.assertTrue(data["enumeration_complete"])
        self.assertEqual(data["cases"][0]["difficulty"][0]["rate"], 1)
        self.assertEqual(data["cases"][0]["last_run_date"], None)
        self.assertIn("current-key", data["scoring"])

    def test_missing_and_corrupt_results_are_reported(self):
        self.add_case();d = self.add_run();(d / "case-01.json").unlink()
        data = self.load()
        self.assertEqual(data["issues"]["missing_report"], 1)
        self.assertEqual(data["cases"][0]["verdict"], "UNTESTABLE")
        (d / "case-01.json").write_text("corrupt sentinel")
        self.assertEqual(self.load()["issues"]["invalid_report"], 1)

    def test_private_roots_and_diagnostics_never_leak(self):
        sentinel = "PRIVATE_HOLDOUT_SENTINEL"
        hidden = self.root / ("evals/" + sentinel + "/cases")
        self.add_case("case-99", directory=hidden)
        d = self.add_run(cid="case-99", private=True, cases=str(hidden.relative_to(self.root)))
        (d / "case-99.json").write_text(sentinel)
        data = self.load();data["as_of"] = "2026-10-22"
        public = json.dumps(data) + health.markdown(data)
        self.assertNotIn(sentinel, public)
        self.assertNotIn("case-99", public)
        self.assertEqual(data["cases"], [])
        self.assertEqual(data["holdout_aggregate"]["issue_invalid_report"], 1)

    def test_matcher_generic_credit_and_location_miss(self):
        self.add_case(words=["error"])
        self.add_run(report={"verdict": "REWORK", "findings": [{"severity": "High", "evidence_level": "CONFIRMED", "location": "a.py:100", "scenario": "an error occurs", "fix": "change it"}]})
        self.assertEqual(self.load()["cases"][0]["verdict"], "REVIEW-MATCHER")

    def test_symlink_rejected_without_target_read(self):
        self.add_case();d = self.add_run();target = self.root / "outside-data";target.write_text("not a report")
        p = d / "case-01.json";p.unlink();p.symlink_to(target)
        with self.assertRaises(health.InputError):
            self.load()

    def test_inputs_unchanged_and_guard_section(self):
        self.add_case(guard=True);self.add_run()
        paths = [p for p in self.root.rglob("*") if p.is_file()]
        before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
        data = self.load();data["as_of"] = "2026-10-22"
        self.assertIn("KEEP (regression guard)", health.markdown(data))
        self.assertEqual(before, {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
        self.assertEqual(json.dumps(data, sort_keys=True), json.dumps(self.load() | {"as_of": "2026-10-22"}, sort_keys=True))

    def test_location_without_credit_is_a_matcher_hint(self):
        self.add_case(all_words=["specific-token"])
        self.add_run(report={"verdict": "REWORK", "findings": [{"severity": "High", "evidence_level": "CONFIRMED", "location": "a.py:1", "scenario": "different wording", "fix": "change it"}]})
        self.assertEqual(self.load()["cases"][0]["verdict"], "REVIEW-MATCHER")

    def test_auto_held_run_does_not_hide_development_corpus(self):
        self.add_case();d = self.add_run()
        dest = d.parent / "ho-held";d.rename(dest)
        data = health.load(self.root)
        self.assertEqual(len(data["cases"]), 1)
        self.assertEqual(data["cases"][0]["observations"], 0)
        self.assertEqual(data["holdout_aggregate"]["observations"], 1)

    def test_meta_without_report_is_not_skipped(self):
        self.add_case();d = self.add_run();(d / "case-01.json").unlink()
        data = health.load(self.root)
        self.assertEqual(data["cases"][0]["status_counts"], {"missing_report": 1})

    def test_invalid_prompt_does_not_drop_the_observation(self):
        self.add_case();d = self.add_run();(d / "case-01.prompt").write_bytes(b'\xff')
        data = self.load()
        self.assertEqual(data["issues"]["invalid_prompt"], 1)
        self.assertEqual(data["cases"][0]["usable"], 1)

    def test_binary_inputs_preserve_exact_skill_text_identity(self):
        self.add_case();d = self.add_run()
        prefix = '=== SKILL ===\nexact text\n'
        p = d / 'case-01.prompt'
        p.write_bytes((prefix + '=== INPUTS ===\n').encode() + b'\xff\x00compiled input')
        data = self.load()
        self.assertNotIn('invalid_prompt', data['issues'])
        actual = data['cases'][0]['difficulty'][0]['text']
        self.assertEqual(actual, 'sha256:' + hashlib.sha256(b'\nexact text\n').hexdigest())
        p.write_bytes(b'=== SKILL ===\n\xff\n=== INPUTS ===\n')
        self.assertEqual(self.load()['issues']['invalid_prompt'], 1)

    def test_missing_usage_is_visible_per_case_and_for_holdouts(self):
        self.add_case();d = self.add_run()
        (d / '_meta/case-01.usage.json').unlink()
        data = self.load()
        self.assertEqual(data['cases'][0]['missing_usage_metadata'], 1)
        self.manifest['runs'][0]['holdout'] = True
        data = self.load()
        self.assertEqual(data['holdout_aggregate']['missing_usage_metadata'], 1)
        self.assertEqual(data['cases'], [])

    def test_raw_prompt_beats_a_declared_text_label(self):
        self.add_case()
        for text in ["A", "B", "C"]:
            d = self.add_run(text=text)
            (d / "case-01.prompt").write_text('=== SKILL ===\nidentical text\n=== INPUTS ===\ninput')
        data = self.load()
        self.assertEqual(len(data["cases"][0]["difficulty"]), 1)

    def test_bom_encoded_historical_inputs(self):
        self.add_case();d = self.add_run();p = d / 'case-01.json'
        p.write_bytes(p.read_text().encode('utf-16'))
        (d / 'case-01.prompt').write_bytes('=== SKILL ===\ntext\n=== INPUTS ==='.encode('utf-16'))
        data = self.load()
        self.assertEqual(data['cases'][0]['usable'], 1)
        self.assertTrue(data['cases'][0]['difficulty'][0]['text'].startswith('sha256:'))

    def test_cli_exit_and_output_refusal(self):
        self.add_case();d = self.add_run();(d / "case-01.json").write_text('corrupt')
        p = self.root / "runs.json";p.write_text(json.dumps(self.manifest))
        out = self.root / "diagnostic"
        args = ['--repo', str(self.root), '--manifest', str(p), '--output-dir', str(out), '--as-of', '2026-10-22']
        self.assertEqual(health.main(args), 1)
        self.assertTrue((out / 'case-health.json').exists())
        self.assertEqual(health.main(args), 2)
        args[args.index('--output-dir') + 1] = str(self.cases)
        self.assertEqual(health.main(args + ['--force']), 2)

    def test_malformed_manifest_is_a_sanitized_failure(self):
        p = self.root / 'private-manifest.json'
        p.write_text('["PRIVATE_MANIFEST_SENTINEL"]')
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            status = health.main(['--repo', str(self.root), '--manifest', str(p),
                                  '--output-dir', str(self.root / 'diagnostic')])
        self.assertEqual(status, 2)
        self.assertNotIn('PRIVATE_MANIFEST_SENTINEL', stdout.getvalue() + stderr.getvalue())
        self.assertNotIn('Traceback', stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
