#!/usr/bin/env python3
"""Map a security-audit findings.json array into a schema 2.3 report.

The fixture is invented. It uses the field names from Cloudflare's security-audit
report schema (MIT). The skill text stays upstream.
"""
import copy, importlib.util, json, subprocess, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "security-audit" / "findings.json"
sys.path.insert(0, str(ROOT / "tools"))
import map_audit_findings as m  # noqa: E402

spec = importlib.util.spec_from_file_location("validate_findings", ROOT / "tools" / "validate_findings.py")
validate_findings = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_findings)


def load_fixture():
    return json.loads(FIXTURE.read_text())


def confirmed(**overrides):
    record = {
        "verdict": "confirmed",
        "fingerprint": "export.admin.missing-check",
        "title": "Export skips the admin check",
        "description": "GET /admin/export returns every note to any token.",
        "root_cause": "require_admin is never called",
        "intended_behavior": "Only an admin token may export notes.",
        "trace": [
            {"kind": "entrypoint", "file": "app.py", "line": 10, "scope": "handle", "description": "Request enters handle()."},
            {"kind": "sink", "file": "app.py", "line": 29, "scope": "export_all", "description": "export_all reads every note."},
        ],
        "evidence": [{"file": "app.py", "line": 29, "description": "export_all() runs before any admin check."}],
        "conditions": [{"kind": "authentication_level", "description": "The caller holds a valid non-admin token."}],
        "execution": {
            "attacker_perspective": "a non-admin user with a valid token",
            "payloads": ["GET /admin/export"],
            "instructions": ["Send GET /admin/export with a non-admin token."],
            "observed_result": "The response is 200 and lists every user's notes.",
        },
        "remediation": {"strategy": "Call require_admin before export_all."},
        "severity": {
            "likelihood": {"score": "high", "reason": "Any signed-in user can call the route."},
            "impact": {"score": "critical", "reason": "Every user's notes are returned."},
            "overall_severity": "critical",
        },
        "confidence": {"score": "high", "reason": "The sink was observed locally."},
    }
    record.update(overrides)
    return record


def needs(fingerprint="audit.flush.unknown"):
    return {
        "verdict": "needs_validation",
        "fingerprint": fingerprint,
        "title": "Audit queue may drop events",
        "description": "Queued audit events may be lost when the process exits.",
        "claimed_root_cause": "The flush behavior of the audit library is unknown.",
        "trace": [{"kind": "sink", "file": "audit.py", "line": 12, "scope": "record", "description": "record() queues an event."}],
        "evidence": [{"file": "audit.py", "line": 12, "description": "The call does not show a flush."}],
        "blockers": ["The audit library was not supplied, so its flush behavior is unknown."],
        "validation_plan": {"local": "Read the library source and check whether record() flushes before return."},
    }


def rejected(fingerprint="script.no-error-handling"):
    return {
        "verdict": "rejected",
        "fingerprint": fingerprint,
        "title": "The script has no error handling.",
        "description": "A failed vault call was thought to continue into delete.",
        "claimed_root_cause": "The shell script ignores command failures.",
        "trace": [{"kind": "entrypoint", "file": "backup.sh", "line": 2, "scope": "header", "description": "The script header sets shell options."}],
        "evidence": [{"file": "backup.sh", "line": 2, "description": "set -euo pipefail is present."}],
        "reason": "set -euo pipefail at line 2 stops the script on the first failed command.",
    }


class MappingTests(unittest.TestCase):
    def assert_valid(self, report):
        self.assertEqual(validate_findings.validate(report), [])

    def test_fixture_maps_onto_schema(self):
        source = load_fixture()
        report = m.map_audit_findings(source)
        self.assertEqual(source, load_fixture())
        self.assertEqual(report["schema_version"], "2.3")
        self.assertEqual(report["verdict"], "REWORK")
        self.assertEqual(report["confidence"], "medium")
        self.assertEqual([f["id"] for f in report["findings"]], ["export.admin.missing-check", "audit.flush.unknown"])
        self.assertEqual([r["id"] for r in report["refuted"]], ["script.no-error-handling"])
        confirmed_f = report["findings"][0]
        self.assertEqual(confirmed_f["status"], "confirmed")
        self.assertEqual(confirmed_f["severity"], "Critical")
        self.assertEqual(confirmed_f["evidence_level"], "CONFIRMED")
        self.assertEqual(confirmed_f["track"], "B")
        self.assertEqual(confirmed_f["location"], "app.py:29")
        self.assertEqual(
            confirmed_f["scenario"],
            "GET /admin/export returns every note to any token. Observed: The response is 200 and lists every user's notes.",
        )
        self.assertEqual(confirmed_f["fix"], "Call require_admin before export_all. Change app.py.")
        self.assertEqual(
            confirmed_f["reproduction"],
            "Send GET /admin/export with a non-admin token. Observed: The response is 200 and lists every user's notes.",
        )
        self.assertEqual(confirmed_f["answers"], {"a": True, "b": True, "c": True, "d": True})
        self.assertTrue(confirmed_f["security"])
        self.assertEqual(
            confirmed_f["boundary"],
            {
                "principal": "a non-admin user with a valid token",
                "input": "GET /admin/export",
                "control": "require_admin is never called",
                "crossed": "handle to export_all",
                "resource": "Every user's notes are returned.",
            },
        )
        self.assertEqual(
            confirmed_f["siblings_searched"],
            {"searched": "no sibling search was recorded on the audit record", "found": "not recorded"},
        )
        self.assertNotIn("UNIQUE_PATCH_BODY_require_admin", json.dumps(report))
        lead = report["findings"][1]
        self.assertEqual(lead["status"], "needs_validation")
        self.assertEqual(lead["track"], "B")
        self.assertEqual(lead["location"], "audit.py:12")
        self.assertEqual(lead["suspicion"], "Queued audit events may be lost when the process exits.")
        self.assertEqual(
            lead["unresolved_fact"],
            "The audit library was not supplied, so its flush behavior is unknown. "
            "Read the library source and check whether record() flushes before return.",
        )
        self.assertNotIn("severity", lead)
        self.assertEqual(
            report["refuted"][0],
            {
                "id": "script.no-error-handling",
                "candidate": "The script has no error handling.",
                "evidence": "set -euo pipefail at line 2 stops the script on the first failed command.",
                "status": "refuted",
            },
        )
        self.assertEqual(
            report["coverage"],
            {
                "checked": [
                    {"unit": "app.py", "kind": "file"},
                    {"unit": "audit.py", "kind": "file"},
                    {"unit": "backup.sh", "kind": "file"},
                ],
                "not_checked": [],
            },
        )
        self.assertEqual(report["inputs_ledger"], [{"item": "findings.json", "status": "seen", "matters": True}])
        self.assert_valid(report)
        self.assertEqual(m.check_audit_findings(load_fixture()), [])

    def test_confirmed_only_critical_is_rework_at_high_confidence(self):
        report = m.map_audit_findings([confirmed()])
        self.assertEqual(report["verdict"], "REWORK")
        self.assertEqual(report["confidence"], "high")
        self.assertEqual(report["findings"][0]["severity"], "Critical")
        self.assert_valid(report)

    def test_high_probable_stays_high_when_impact_carries_c(self):
        record = confirmed(fingerprint="export.admin.probable")
        record["confidence"] = {"score": "medium", "reason": "The trace is complete and the run was local."}
        record["severity"] = {
            "likelihood": {"score": "high", "reason": "Any signed-in user can call the route."},
            "impact": {"score": "high", "reason": "Every user's notes are returned."},
            "overall_severity": "high",
        }
        report = m.map_audit_findings([record])
        finding = report["findings"][0]
        self.assertEqual(finding["evidence_level"], "PROBABLE")
        self.assertEqual(finding["answers"], {"a": True, "b": False, "c": True, "d": True})
        self.assertEqual(finding["severity"], "High")
        self.assertEqual(report["verdict"], "SHIP WITH FIXES")
        self.assertEqual(report["confidence"], "medium")
        self.assert_valid(report)

    def test_low_confidence_critical_is_capped_at_high(self):
        record = confirmed(fingerprint="export.admin.low-confidence")
        record["confidence"] = {"score": "low", "reason": "The local run used a stub, not the real store."}
        report = m.map_audit_findings([record])
        finding = report["findings"][0]
        self.assertEqual(finding["evidence_level"], "PROBABLE")
        self.assertFalse(finding["answers"]["b"])
        self.assertEqual(finding["severity"], "High")
        self.assertEqual(report["verdict"], "SHIP WITH FIXES")
        self.assertEqual(report["confidence"], "low")
        self.assert_valid(report)

    def test_severity_cannot_exceed_impact(self):
        record = confirmed(fingerprint="export.admin.impact-high")
        record["severity"] = {
            "likelihood": {"score": "high", "reason": "Any signed-in user can call the route."},
            "impact": {"score": "high", "reason": "Every user's notes are returned."},
            "overall_severity": "critical",
        }
        report = m.map_audit_findings([record])
        self.assertEqual(report["findings"][0]["severity"], "High")
        self.assertEqual(report["verdict"], "SHIP WITH FIXES")
        self.assert_valid(report)

    def test_unlikely_high_drops_to_medium(self):
        record = confirmed(fingerprint="export.admin.unlikely")
        record["severity"] = {
            "likelihood": {"score": "low", "reason": "The route is off in the default config."},
            "impact": {"score": "high", "reason": "Every user's notes are returned."},
            "overall_severity": "high",
        }
        report = m.map_audit_findings([record])
        finding = report["findings"][0]
        self.assertEqual(finding["answers"]["d"], False)
        self.assertEqual(finding["severity"], "Medium")
        self.assertTrue(finding["security"])
        self.assertIn("boundary", finding)
        self.assertNotIn("siblings_searched", finding)
        self.assertEqual(report["verdict"], "SHIP WITH FIXES")
        self.assert_valid(report)

    def test_informational_is_low_without_a_boundary(self):
        record = confirmed(fingerprint="export.admin.note")
        record["severity"] = {
            "likelihood": {"score": "low", "reason": "The note is a checklist gap."},
            "impact": {"score": "informational", "reason": "No boundary is crossed."},
            "overall_severity": "informational",
        }
        report = m.map_audit_findings([record])
        finding = report["findings"][0]
        self.assertEqual(finding["severity"], "Low")
        self.assertFalse(finding["security"])
        self.assertNotIn("boundary", finding)
        self.assertNotIn("siblings_searched", finding)
        self.assertEqual(report["verdict"], "SHIP")
        self.assertEqual(report["confidence"], "high")
        self.assert_valid(report)

    def test_overall_above_informational_impact_stays_low(self):
        record = confirmed(fingerprint="export.admin.note-high")
        record["severity"] = {
            "likelihood": {"score": "high", "reason": "The route is easy to call."},
            "impact": {"score": "informational", "reason": "No data leaves the process."},
            "overall_severity": "high",
        }
        report = m.map_audit_findings([record])
        self.assertEqual(report["findings"][0]["severity"], "Low")
        self.assertFalse(report["findings"][0]["security"])
        self.assertEqual(report["verdict"], "SHIP")
        self.assert_valid(report)

    def test_medium_only_ships_with_fixes(self):
        record = confirmed(fingerprint="export.admin.medium")
        record["severity"] = {
            "likelihood": {"score": "medium", "reason": "A user can reach the route."},
            "impact": {"score": "medium", "reason": "One extra field is returned."},
            "overall_severity": "medium",
        }
        report = m.map_audit_findings([record])
        self.assertEqual(report["findings"][0]["severity"], "Medium")
        self.assertEqual(report["findings"][0]["answers"]["c"], False)
        self.assertTrue(report["findings"][0]["security"])
        self.assertNotIn("siblings_searched", report["findings"][0])
        self.assertEqual(report["verdict"], "SHIP WITH FIXES")
        self.assert_valid(report)

    def test_low_only_ships(self):
        record = confirmed(fingerprint="export.admin.low")
        record["severity"] = {
            "likelihood": {"score": "low", "reason": "The path is rare."},
            "impact": {"score": "low", "reason": "A log line is noisy."},
            "overall_severity": "low",
        }
        report = m.map_audit_findings([record])
        self.assertEqual(report["findings"][0]["severity"], "Low")
        self.assertTrue(report["findings"][0]["security"])
        self.assertEqual(report["verdict"], "SHIP")
        self.assert_valid(report)

    def test_needs_validation_only_ships_at_medium(self):
        report = m.map_audit_findings([needs()])
        self.assertEqual(report["verdict"], "SHIP")
        self.assertEqual(report["confidence"], "medium")
        self.assertEqual(report["refuted"], [])
        self.assertNotIn("severity", report["findings"][0])
        self.assert_valid(report)

    def test_rejected_only_is_refuted(self):
        report = m.map_audit_findings([rejected()])
        self.assertEqual(report["findings"], [])
        self.assertEqual(report["verdict"], "SHIP")
        self.assertEqual(report["confidence"], "medium")
        self.assertEqual(report["coverage"]["checked"], [{"unit": "backup.sh", "kind": "file"}])
        self.assert_valid(report)

    def test_empty_array_ships(self):
        report = m.map_audit_findings([])
        self.assertEqual(report["verdict"], "SHIP")
        self.assertEqual(report["confidence"], "medium")
        self.assertEqual(report["findings"], [])
        self.assertEqual(report["refuted"], [])
        self.assertEqual(report["coverage"]["checked"], [{"unit": "findings.json", "kind": "document"}])
        self.assert_valid(report)

    def test_lowest_confirmed_confidence_wins(self):
        low = confirmed(fingerprint="export.admin.low-confidence")
        low["confidence"] = {"score": "low", "reason": "The local run used a stub, not the real store."}
        low["severity"] = {
            "likelihood": {"score": "medium", "reason": "A user can reach the route."},
            "impact": {"score": "medium", "reason": "One extra field is returned."},
            "overall_severity": "medium",
        }
        report = m.map_audit_findings([confirmed(), low])
        self.assertEqual(report["confidence"], "low")
        self.assert_valid(report)

    def test_needs_validation_caps_high_confidence(self):
        report = m.map_audit_findings([confirmed(), needs()])
        self.assertEqual(report["confidence"], "medium")
        self.assertEqual(report["verdict"], "REWORK")
        self.assert_valid(report)

    def test_short_payload_uses_entrypoint_description(self):
        record = confirmed()
        record["execution"]["payloads"] = ["id"]
        record["trace"][0]["description"] = "The token arrives at handle()."
        report = m.map_audit_findings([record])
        self.assertEqual(report["findings"][0]["boundary"]["input"], "The token arrives at handle().")
        self.assert_valid(report)

    def test_several_payloads_are_joined(self):
        record = confirmed()
        record["execution"]["payloads"] = ["GET /admin/export", "Accept: application/json"]
        report = m.map_audit_findings([record])
        self.assertEqual(report["findings"][0]["boundary"]["input"], "GET /admin/export, Accept: application/json")
        self.assert_valid(report)

    def test_code_change_names_are_joined_and_bodies_dropped(self):
        record = confirmed()
        record["remediation"] = {
            "strategy": "Call require_admin before export_all.",
            "code_changes": [
                {"file_name": "app.py", "fixed_code": "UNIQUE_PATCH_BODY_one"},
                {"file_name": "auth.py", "fixed_code": "UNIQUE_PATCH_BODY_two"},
            ],
        }
        report = m.map_audit_findings([record])
        self.assertEqual(report["findings"][0]["fix"], "Call require_admin before export_all. Change app.py, auth.py.")
        blob = json.dumps(report)
        self.assertNotIn("UNIQUE_PATCH_BODY_one", blob)
        self.assertNotIn("UNIQUE_PATCH_BODY_two", blob)
        self.assert_valid(report)

    def test_deployment_plan_is_part_of_the_unresolved_fact(self):
        record = needs()
        record["validation_plan"] = {"deployment": "Ask the owner whether the library flushes on process exit."}
        report = m.map_audit_findings([record])
        self.assertIn("Ask the owner whether the library flushes on process exit.", report["findings"][0]["unresolved_fact"])
        self.assert_valid(report)

    def test_both_plan_fields_are_kept(self):
        record = needs()
        record["validation_plan"] = {
            "local": "Read the library source and check whether record() flushes before return.",
            "deployment": "Ask the owner whether the library flushes on process exit.",
        }
        fact = m.map_audit_findings([record])["findings"][0]["unresolved_fact"]
        self.assertIn("Read the library source", fact)
        self.assertIn("Ask the owner", fact)
        self.assert_valid(m.map_audit_findings([record]))

    def test_short_rejection_reason_uses_evidence(self):
        record = rejected()
        record["reason"] = "too short"
        report = m.map_audit_findings([record])
        self.assertEqual(
            report["refuted"][0]["evidence"],
            "too short set -euo pipefail is present.",
        )
        self.assert_valid(report)

    def test_sibling_override_replaces_the_default(self):
        note = {"searched": "callers of export_all across the repository", "found": "no other caller"}
        report = m.map_audit_findings([confirmed()], siblings={"export.admin.missing-check": note})
        self.assertEqual(report["findings"][0]["siblings_searched"], note)
        self.assert_valid(report)

    def test_sibling_override_on_medium_is_kept(self):
        record = confirmed(fingerprint="export.admin.medium")
        record["severity"] = {
            "likelihood": {"score": "medium", "reason": "A user can reach the route."},
            "impact": {"score": "medium", "reason": "One extra field is returned."},
            "overall_severity": "medium",
        }
        note = {"searched": "callers of export_all across the repository", "found": "one more caller"}
        report = m.map_audit_findings([record], siblings={"export.admin.medium": note})
        self.assertEqual(report["findings"][0]["siblings_searched"], note)
        self.assert_valid(report)

    def test_coverage_and_ledger_overrides(self):
        coverage = {"checked": [{"unit": "only.py", "kind": "file"}], "not_checked": [{"unit": "other.py", "reason": "out_of_scope"}]}
        ledger = [{"item": "notes.md", "status": "seen", "matters": True}]
        report = m.map_audit_findings([confirmed()], coverage=coverage, inputs_ledger=ledger)
        self.assertEqual(report["coverage"], coverage)
        self.assertEqual(report["inputs_ledger"], ledger)
        self.assert_valid(report)

    def test_input_list_is_not_mutated(self):
        source = [confirmed(), needs(), rejected()]
        snapshot = copy.deepcopy(source)
        m.map_audit_findings(source)
        self.assertEqual(source, snapshot)

    def test_evidence_file_is_covered_when_trace_differs(self):
        record = confirmed()
        record["evidence"] = [{"file": "tests/test_app.py", "line": 4, "description": "The test shows the missing check."}]
        report = m.map_audit_findings([record])
        units = [item["unit"] for item in report["coverage"]["checked"]]
        self.assertEqual(units, ["app.py", "tests/test_app.py"])
        self.assert_valid(report)

    def test_duplicate_fingerprint_is_an_error(self):
        with self.assertRaises(m.MapError) as caught:
            m.map_audit_findings([confirmed(), rejected(fingerprint="export.admin.missing-check")])
        self.assertIn("fingerprint", caught.exception.path)
        self.assertTrue(m.check_audit_findings([confirmed(), confirmed()]))

    def test_bad_shape_is_an_error(self):
        for bad in (None, {}, "text", [{"verdict": "accepted", "fingerprint": "x"}]):
            with self.subTest(bad=bad):
                with self.assertRaises(m.MapError):
                    m.map_audit_findings(bad)
                self.assertTrue(m.check_audit_findings(bad))

    def test_missing_required_field_is_an_error(self):
        record = confirmed()
        del record["title"]
        with self.assertRaises(m.MapError) as caught:
            m.map_audit_findings([record])
        self.assertEqual(caught.exception.path, "records[0].title")

    def test_unknown_field_is_an_error(self):
        record = confirmed()
        record["hunter_note"] = "ignore this"
        with self.assertRaises(m.MapError) as caught:
            m.map_audit_findings([record])
        self.assertEqual(caught.exception.path, "records[0].hunter_note")

    def test_severity_on_a_lead_is_an_error(self):
        record = needs()
        record["severity"] = {"overall_severity": "high"}
        with self.assertRaises(m.MapError):
            m.map_audit_findings([record])

    def test_bad_fingerprint_is_an_error(self):
        record = confirmed(fingerprint="-bad")
        with self.assertRaises(m.MapError) as caught:
            m.map_audit_findings([record])
        self.assertEqual(caught.exception.path, "records[0].fingerprint")

    def test_empty_observed_result_is_an_error(self):
        record = confirmed()
        record["execution"]["observed_result"] = " "
        with self.assertRaises(m.MapError):
            m.map_audit_findings([record])

    def test_unknown_sibling_id_is_an_error(self):
        with self.assertRaises(m.MapError):
            m.map_audit_findings([confirmed()], siblings={"missing.id": {"searched": "callers of export_all", "found": "none"}})

    def test_short_sibling_search_is_an_error(self):
        with self.assertRaises(m.MapError):
            m.map_audit_findings(
                [confirmed()],
                siblings={"export.admin.missing-check": {"searched": "short", "found": "none"}},
            )

    def test_invalid_coverage_override_fails_the_check(self):
        errs = m.check_audit_findings([], coverage={"checked": [], "not_checked": []})
        self.assertTrue(errs)
        self.assertTrue(any(path.startswith("coverage") for path, _ in errs))

    def test_cli_maps_the_fixture(self):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "map_audit_findings.py"), str(FIXTURE)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        report = json.loads(proc.stdout)
        self.assertEqual(validate_findings.validate(report), [])
        self.assertEqual(proc.stderr, "")

    def test_cli_rejects_a_mapping_error(self):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "map_audit_findings.py"), str(ROOT / "schema" / "findings.schema.json")],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 1)
        self.assertTrue(proc.stderr.strip())

    def test_cli_rejects_unreadable_json(self):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "map_audit_findings.py"), str(ROOT / "README.md")],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()
