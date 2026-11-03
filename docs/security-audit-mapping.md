# Security-audit findings mapping

This page maps `findings.json` from Cloudflare's [security-audit-skill](https://github.com/cloudflare/security-audit-skill) (MIT) into the report checked by [`tools/validate_findings.py`](../tools/validate_findings.py).

Field names come from `skills/security-audit/report-schema.json` in that repository. The skill text stays upstream.

The mapper is [`tools/map_audit_findings.py`](../tools/map_audit_findings.py). It writes schema 2.3. [`tests/test_map_audit_findings.py`](../tests/test_map_audit_findings.py) checks the conversion against [`schema/findings.schema.json`](../schema/findings.schema.json). The invented fixture is [`tests/fixtures/security-audit/findings.json`](../tests/fixtures/security-audit/findings.json).

The six-phase audit writes `findings.json` in phase 4. Phase 5 may replace records and then validate the file again. This mapping starts from that array.

## Verdicts

| Audit `verdict` | Report field |
|---|---|
| `confirmed` | `findings[]` with `status` `confirmed` |
| `needs_validation` | `findings[]` with `status` `needs_validation` |
| `rejected` | `refuted[]` |

`fingerprint` becomes `id`. A repeated fingerprint is an error. The fingerprint pattern is the one in the upstream schema.

## Confirmed records

Track is `B`. `location` is the sink `file:line`. When the trace has no sink, the location is the last step.

`scenario` joins `description` and `execution.observed_result`. `fix` is `remediation.strategy`. When `code_changes` lists files, their names are appended. The `fixed_code` bodies stay out of the report.

`reproduction` joins `execution.instructions` and `observed_result`.

`security` is true when `impact.score` is `low`, `medium`, `high`, or `critical`. Informational impact maps to severity `Low` with `security` false.

`boundary.principal` is `execution.attacker_perspective`. `boundary.input` is the payloads joined with commas. A joined value shorter than 3 characters uses the entrypoint description. `boundary.control` is `root_cause`. `boundary.crossed` joins the entrypoint scope and the sink scope. `boundary.resource` is `impact.reason`.

## Severity

`overall_severity` maps as follows.

| Audit score | Report severity |
|---|---|
| `critical` | `Critical` |
| `high` | `High` |
| `medium` | `Medium` |
| `low` | `Low` |
| `informational` | `Low` |

The mapped severity also stays at or below `impact.score`. It then drops until the four yes/no answers in schema 2.3 allow it. It never rises above the source score.

| Answer | True when |
|---|---|
| a | `observed_result` and every instruction are non-empty |
| b | `confidence.score` is `high` |
| c | `impact.score` is `high` or `critical` |
| d | `likelihood.score` is `medium`, `high`, or `critical` |

`evidence_level` is `CONFIRMED` when b is true. Medium and low confidence scores map to `PROBABLE`.

A High or Critical finding includes `siblings_searched`. Pass a note per fingerprint to record a real search. With no note, the mapper records that no sibling search was on the audit record.

## Needs validation and rejected

`suspicion` is `description`. `unresolved_fact` joins `blockers` with `validation_plan.local` and `validation_plan.deployment` when those fields are present. These records omit severity.

`refuted.candidate` is `title`. `refuted.evidence` is `reason` when that string is at least 10 characters. A shorter reason is joined with the evidence descriptions.

## Report fields supplied by the mapper

`verdict` is `REWORK` when any mapped finding is Critical. It is `SHIP WITH FIXES` when the highest confirmed severity is High or Medium. Otherwise it is `SHIP`.

`confidence` is the lowest confirmed `confidence.score`. A `needs_validation` record caps a high score at `medium`. With no confirmed score, confidence is `medium`.

`coverage.checked` lists each file named in a trace or an evidence entry, in first-seen order. An empty array uses the document `findings.json`. Pass `coverage` to replace that object. `inputs_ledger` marks `findings.json` as seen unless you pass a ledger.

Phase 1 coverage ledgers stay in their own file. Pass `coverage` when you already have units in the findings schema.

Run depth, prose agreement, cross-run ids, and a fresh verifier stay in issues 98, 99, 100, and 101.

## Command

```bash
python3 tools/map_audit_findings.py findings.json
```

Exit 0 prints the report. Exit 1 means a record cannot be mapped, or the report fails `tools/validate_findings.py`. Exit 2 means the file is not JSON.

The Python call `map_audit_findings(records, coverage=..., siblings=..., inputs_ledger=...)` takes the same overrides. `check_audit_findings` returns the same `(path, message)` pairs as `validate_findings.validate`.
