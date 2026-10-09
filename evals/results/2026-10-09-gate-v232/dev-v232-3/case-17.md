# Redteam review: Lumen API vendor assessment

**Review mode:** single reviewer with no tools. The work was not written in this conversation, so the risk of anchoring on the author's reasoning is low. No subagent or second reviewer was available. Re-run in a fresh session with tools before relying on this for a high-stakes decision.

**VERDICT: REWORK.** The headline claim ("Lumen is zero-retention, so it is safe to use with client documents") is contradicted by the source it cites, and on the plan this account is on, Lumen keeps every input for 30 days.

**CONFIDENCE: high.** Both sources were supplied in full and the contradiction is a direct quote. What limits it: there were no tools, so I could not check the live vendor pages against the 5 October 2026 snapshots, and there was only one reviewer.

**INPUTS LEDGER:**
- **Seen:**
  - request.md
  - context.md
  - assessment.md
  - sources/lumen-privacy.md
  - sources/lumen-security.md
- **Not seen:**
  - The live Lumen pages. This matters only if they changed after 5 October 2026.
  - Lumen's terms of service, data processing agreement (DPA), subprocessor list and the ZDR addendum. These matter for any revised assessment, not for the current verdict.
  - The client contracts' confidentiality clauses. These matter for whether sending client documents to any vendor is allowed at all.

**COVERAGE:**
- **Scope:** the whole work, with Track C as requested.
- **Checked:**
  - Documents: request.md, context.md, assessment.md, and both source files.
  - Claims: the summary claim, the three supporting facts, and the account-plan statement.
- **Not checked:**
  - Live vendor pages: no tools.
  - Contractual and legal permissibility of sharing client documents: out of scope for a claims review, and not supplied.

**SEATS AND GATE:**
- The work contains no client data, credentials or personal data, so the sensitivity gate passed.
- Only the local reviewer ran. No subagent or cross-vendor seats were available, so none were refused.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | C | assessment.md, Summary ("Lumen is zero-retention, so it is safe to use with client documents [1]") | Source [1] says the opposite. It says "Inputs and outputs sent to the Lumen API are retained for 30 days for abuse monitoring", and "Zero data retention (ZDR) is available only to accounts on an enterprise agreement that includes the signed ZDR addendum". The assessment itself says: "Our account is on the standard plan; we have no enterprise agreement." | The contracts team relies on the summary and sends client-confidential contracts on the standard plan. Each contract is then retained by Lumen for 30 days, outside the firm's control. This may breach client confidentiality obligations, and it cannot be undone once the contracts are sent. | Withdraw the summary. Restate it as: "On our standard plan Lumen retains inputs and outputs for 30 days. Zero retention requires an enterprise agreement with a signed ZDR addendum, which we do not have." Do not send client contracts until a signed ZDR addendum is in place, or until the 30-day retention is approved against the client agreements. | a Y / b Y / c Y / d Y |
| F2 | Medium | CONFIRMED | C | assessment.md, Supporting facts ("enough for a 150-page contract [2]") | Source [2] only says "a context window of up to 200,000 tokens". It says nothing about page counts. The 150-page claim is the author's own inference, cited as if it came from the vendor. The request says "Base every claim on Lumen's own pages". | A long or dense contract (schedules, tables, exhibits) plus the extraction prompt and output may exceed the window. Readers would trust the "150 pages" figure because it appears to be Lumen's. | Cite only "up to 200,000 tokens [2]". If a page estimate is useful, label it as the team's own estimate, give the tokens-per-page assumption, and measure it on a real sample contract. | a Y / b Y / c N / d N |

**F1 detail.**
- **Security:** yes. The boundary:
  - Principal and resource: client-confidential contracts held by the firm.
  - Input and destination: those contracts are sent to a third-party vendor.
  - Failing control: the ZDR addendum, which would give zero retention, is absent.
  - Boundary crossed: the documents move from the firm's custody into the vendor's storage for 30 days.
- **Sibling search:** I compared every claim in assessment.md with its cited source, and the plan statement with the summary. No other claim misstates a retention, privacy or plan condition:
  - The training claim holds on any plan.
  - The SOC 2 claim matches the source.
- **Confirm-or-refute round:** I argued the strongest defence: perhaps ZDR applies to this account. That fails on the work's own words ("standard plan; we have no enterprise agreement"). F1 stands.

## NEEDS VALIDATION

- **S1. What "abuse monitoring" involves.** Whether data held for abuse monitoring can be read by Lumen staff or subprocessors. The sources do not say. This is settled by Lumen's DPA or terms, and the subprocessor list.
- **S2. Whether client contracts may go to a third-party processor at all.** Even with ZDR in place, this depends on the confidentiality and data-processing clauses in the client agreements, which were not supplied.
- **S3. Whether the snapshots are still current.** Whether the 5 October 2026 snapshots still match the live pages on the decision date. This is settled by re-fetching both pages.

## REFUTED

- **"The training claim overstates the source."** Refuted. Source [1] says "not used to train Lumen models on any plan", so the claim holds on the standard plan.
- **"The SOC 2 claim is unsupported or stale."** Refuted. Source [2] says "Lumen holds a SOC 2 Type II report (period ending 30 June 2026)". The period ended about three months before the 8 October 2026 review date, so it is current.

## WHAT HOLDS UP

- The no-training claim, the SOC 2 Type II claim and the 200,000-token figure all match their sources word for word.
- The sources are vendor pages, as the request required, and they are recent (retrieved 5 October 2026).
- The assessment candidly states the account plan. That statement is exactly what exposes F1.

## UNVERIFIED CLAIMS

- **That the source files match Lumen's live pages.** Confirm by re-fetching the pages.
- **That a 150-page contract fits in the window.** Confirm by tokenizing a representative contract together with the prompt and the expected output.

## QUESTIONS FOR THE AUTHOR

1. Is an enterprise agreement with a signed ZDR addendum planned, and when?
2. Has anyone checked whether the client contracts allow a vendor to retain them for 30 days?

## DECISION-MAKER SUMMARY

The assessment's core claim is false. On the current standard plan Lumen retains inputs and outputs for 30 days, and zero retention requires an enterprise agreement with a signed ZDR addendum that the account does not have. Do not send client contracts until that addendum is signed, or until 30-day retention is explicitly cleared against the client agreements. Proceeding now exposes every contract sent, and the exposure cannot be reversed.

## OWNER SUMMARY

The assessment says the service keeps no copy of what we send, but the vendor's own page says it keeps everything for 30 days on our current plan. Not keeping copies is only offered to customers with a special signed agreement, which we do not have. Client contracts should not be sent until that agreement is signed or the 30-day storage is approved.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "assessment.md", "status": "seen", "matters": true},
    {"item": "sources/lumen-privacy.md", "status": "seen", "matters": true},
    {"item": "sources/lumen-security.md", "status": "seen", "matters": true},
    {"item": "live Lumen vendor pages", "status": "not_seen", "matters": false},
    {"item": "Lumen DPA, terms, subprocessor list, ZDR addendum", "status": "not_seen", "matters": true},
    {"item": "client contract confidentiality clauses", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "The work under review contains no client data, personal data or credentials."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "assessment.md", "kind": "document"},
      {"unit": "sources/lumen-privacy.md", "kind": "document"},
      {"unit": "sources/lumen-security.md", "kind": "document"},
      {"unit": "assessment.md:Summary zero-retention claim", "kind": "claim"},
      {"unit": "assessment.md:SOC 2 Type II claim", "kind": "claim"},
      {"unit": "assessment.md:no-training claim", "kind": "claim"},
      {"unit": "assessment.md:200,000-token / 150-page claim", "kind": "claim"},
      {"unit": "assessment.md:standard plan, no enterprise agreement", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "live Lumen vendor pages", "reason": "no_tools"},
      {"unit": "legal permissibility of sharing client contracts with a processor", "reason": "out_of_scope"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "assessment.md, Summary: \"Lumen is zero-retention, so it is safe to use with client documents [1]\"",
     "scenario": "The contracts team relies on the summary and sends client-confidential contracts on the standard plan; source [1] states inputs and outputs are retained for 30 days and that ZDR requires an enterprise agreement with a signed ZDR addendum, which the account does not have, so every contract is retained by the vendor for 30 days and the exposure cannot be reversed.",
     "fix": "Withdraw the summary and state that the standard plan has 30-day retention; do not send client contracts until a signed ZDR addendum is in place or 30-day retention is approved against the client agreements.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "security": true,
     "boundary": {"principal": "the firm's client-confidential contracts sent by the contracts team",
                  "input": "client contracts submitted to the Lumen API",
                  "control": "the ZDR addendum that would give zero retention is absent on the standard plan",
                  "crossed": "firm custody to third-party vendor storage for 30 days",
                  "resource": "client-confidential contracts"},
     "siblings_searched": {"searched": "every claim in assessment.md compared with its cited source, plus the plan statement against the summary",
                           "found": "no other claim misstates a retention, privacy or plan condition"}},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "assessment.md, Supporting facts: \"enough for a 150-page contract [2]\"",
     "scenario": "Source [2] states only 'up to 200,000 tokens'; the 150-page figure is the author's unsourced inference cited as vendor fact, against the request to base every claim on Lumen's pages, and a long or dense contract plus prompt and output could exceed the window.",
     "fix": "Cite only the 200,000-token figure to [2]; label any page estimate as an internal assumption and measure it on a representative contract.",
     "answers": {"a": true, "b": true, "c": false, "d": false}},
    {"id": "S1", "status": "needs_validation", "track": "C", "location": "sources/lumen-privacy.md, Retention",
     "suspicion": "Data retained for abuse monitoring may be accessible to Lumen staff or subprocessors.",
     "unresolved_fact": "Lumen's DPA or terms and its subprocessor list, which were not supplied."},
    {"id": "S2", "status": "needs_validation", "track": "C", "location": "request.md (client contracts)",
     "suspicion": "Client agreements may forbid sharing contracts with any third-party processor, even under ZDR.",
     "unresolved_fact": "The confidentiality and data-processing clauses of the client agreements."},
    {"id": "S3", "status": "needs_validation", "track": "C", "location": "sources/ (retrieved 5 October 2026)",
     "suspicion": "The vendor pages may have changed since retrieval.",
     "unresolved_fact": "Whether the live pages match the snapshots on the decision date."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The no-training claim overstates the source.",
     "evidence": "sources/lumen-privacy.md: 'not used to train Lumen models on any plan'."},
    {"id": "C2", "candidate": "The SOC 2 claim is unsupported or stale.",
     "evidence": "sources/lumen-security.md: 'SOC 2 Type II report (period ending 30 June 2026)', about three months before the 8 October 2026 review date."}
  ]
}
```