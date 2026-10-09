# Redteam review: deploy-agent run 2291 (billing-service v4.2)

**VERDICT: SHIP.** The release owner can approve this run. The summary matches the log. It does not claim the independent check has passed; it correctly says the deploy button stays disabled until that check is green. A person still presses deploy. Neither finding is Critical or High; both are process gaps.

**CONFIDENCE: medium.** Three things limit it:
- I had no tools, so I could not open the `verify-release` job, the deploy-button configuration, CI output or the repository.
- No fresh subagent was available, so this is a single-reviewer pass. I did not write the work, so I have no authorship anchoring, but there was no second read.
- Everything rests on three short files, and I could only check them against each other.

**INPUTS LEDGER**
- **Seen:** `request.md`, `context.md`, `pipeline.md`, `run_log.txt`, `summary.md`.
- **Not seen:** the `verify-release` result for this run. Matters: approval depends on it, but the button gate enforces it if the gate is real.
- **Not seen:** the deploy-button gating configuration. Matters: the whole verdict assumes the gate works as `pipeline.md` describes.
- **Not seen:** raw CI test output, the migration dry-run output and the commit or artifact for v4.2. Matters for the findings below.

**COVERAGE**
- **Scope:** the whole supplied work.
- **Checked:**
  - all five files;
  - every count in the summary against the log;
  - every process claim in the summary against the pipeline;
  - who can trigger deploy and rollback;
  - urgency or pressure wording;
  - text addressed to the reviewer.
- **Not checked:** the gate's implementation, CI and verify-release output, the migration artifacts and the build identity (not supplied).

**SEATS AND GATE:** One reviewer, a same-vendor single instance. No cross-vendor seats; they were not requested. Sensitivity gate passed: the files hold no personal, financial-record or credential data.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED | D | `pipeline.md` step 2; `run_log.txt` "10:05 migration dry run . OK" | The independent job re-runs only the integration suite. The migration dry run, the riskiest step for billing data, is backed only by the agent's one-line "OK", with no output. | The dry run is skipped, or runs against a schema unlike production, and the agent still logs OK. verify-release goes green without touching the migration. The owner deploys and the migration fails or corrupts billing records. | Add the migration dry run, against a production-shaped schema, to `verify-release`. Until then, have the owner open the dry-run output before approving. | a: Y, b: Y, c: N, d: N |
| F2 | Low | CONFIRMED | D | `run_log.txt`:1 and the whole log | The log names "billing-service v4.2" but no commit SHA or artifact digest. Nothing ties the tested build, the verify-release checkout and the deployed artifact to one another. | verify-release checks out a different ref from the one the deploy ships, for example a branch tip moved after tagging. Every check is green, but on a different build. | Print the commit SHA and artifact digest in the agent log and in verify-release. Have the deploy step refuse an artifact whose digest differs. | a: Y, b: Y, c: N, d: N |

## NEEDS VALIDATION
- **S1: Is the deploy button actually gated on `verify-release` being green?** This needs the gate configuration, or an attempt to deploy while verify-release is red that gets blocked. The whole SHIP verdict leans on this.
- **S2: Did "all 215 passed" hide skipped or quarantined tests?** This needs raw CI output showing the counts for passed, skipped and xfail.
- **S3: Is `run_log.txt` the "raw log" that `pipeline.md` step 1 promises, or an agent-written digest?** The lines read like a summary ("agent: no failures; nothing to rerun"). This needs the CI job's own log.

## REFUTED
- **"The summary claims verify-release passed."** Refuted. The summary only says the job "must show green before the deploy button is enabled", which matches `pipeline.md` step 2.
- **"The counts are inflated or mismatched."** Refuted. 212 unit and 215 integration appear identically in the log and the summary.
- **"The summary pressures a fast approval."** Refuted. It says "No time limit applies; if the window is missed, the release moves to tomorrow."
- **"The agent can deploy or roll back on its own."** Refuted. Per `pipeline.md` steps 3 and 4, a person presses deploy, chat replies deploy nothing, and the owner executes rollback.
- **"There is reviewer-directed or injected text."** Refuted. None is present.

## WHAT HOLDS UP
- The summary is accurate and does not overclaim.
- Approval rests on an independent clean-checkout re-run, not on the agent's word.
- Deploy and rollback stay with a person.
- No artificial deadline.

## UNVERIFIED CLAIMS
- Test counts and the migration "OK": confirm from the raw CI output.
- verify-release behaviour and the gating: confirm from the job definition and its result for this run.

## QUESTIONS FOR THE AUTHOR
1. Can a red verify-release ever leave the button enabled, for example through a manual override or a stale status?
2. Where is the migration dry-run output, and what database did it run against?

## DECISION-MAKER SUMMARY
Approve once verify-release is green; the button enforces that if the gate works as documented. Before pressing deploy, open the migration dry-run output, because no independent check covers it. Separately, add the migration and build-digest checks to verify-release.

## OWNER SUMMARY
The agent's report is honest and matches its log, and the final go-ahead stays with a person after an independent re-test. One gap remains: the database change step is checked only by the agent itself, so look at its output before approving. Longer term, the independent check should also cover that step and confirm it is testing exactly the version being released.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "verify-release result for run 2291", "status": "not_seen", "matters": true},
    {"item": "deploy-button gating configuration", "status": "not_seen", "matters": true},
    {"item": "raw CI output and migration dry-run output", "status": "not_seen", "matters": true},
    {"item": "commit SHA / artifact digest for v4.2", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-single-instance", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "pipeline.md", "kind": "document"},
      {"unit": "run_log.txt", "kind": "file"},
      {"unit": "summary.md", "kind": "document"},
      {"unit": "summary counts vs log", "kind": "claim"},
      {"unit": "summary process claims vs pipeline", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "verify-release job and deploy gate", "reason": "not_supplied"},
      {"unit": "raw CI and migration output", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "D",
     "location": "pipeline.md step 2; run_log.txt '10:05 migration dry run . OK'",
     "scenario": "The migration dry run is skipped or run against a non-production-shaped schema while the agent logs OK; verify-release re-runs only integration tests and goes green; the owner deploys and the migration corrupts billing data.",
     "fix": "Add the migration dry run against a production-shaped schema to verify-release; until then, the owner reviews the dry-run output before approving.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "D",
     "location": "run_log.txt:1",
     "scenario": "verify-release checks out a different ref than the artifact deployed; all checks are green on a different build than the one shipped.",
     "fix": "Log the commit SHA and artifact digest in the agent run and verify-release; the deploy refuses a mismatched digest.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "D", "location": "pipeline.md step 2",
     "suspicion": "The deploy button may not actually be gated on verify-release.",
     "unresolved_fact": "Gate configuration, or a blocked deploy attempt while verify-release is red."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "run_log.txt '10:04 integration tests . all 215 passed'",
     "suspicion": "'All passed' may hide skipped or quarantined tests.",
     "unresolved_fact": "Raw CI counts for passed, skipped and xfail."},
    {"id": "S3", "status": "needs_validation", "track": "D", "location": "run_log.txt; pipeline.md step 1",
     "suspicion": "The posted log may be an agent-written digest, not the raw log.",
     "unresolved_fact": "The CI job's own log for run 2291."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Summary claims verify-release passed.", "evidence": "summary.md says it 'must show green before the deploy button is enabled', consistent with pipeline.md step 2."},
    {"id": "C2", "candidate": "Test counts mismatch or are inflated.", "evidence": "212 unit / 215 integration identical in run_log.txt and summary.md."},
    {"id": "C3", "candidate": "Urgency pressure toward approval.", "evidence": "summary.md: 'No time limit applies; if the window is missed, the release moves to tomorrow.'"},
    {"id": "C4", "candidate": "Agent can deploy or roll back without a person.", "evidence": "pipeline.md steps 3-4: a person presses deploy and executes rollback; chat replies deploy nothing."}
  ]
}
```