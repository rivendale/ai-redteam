# Redteam report: Lumen API vendor assessment

**Review mode:** Single reviewer, no tools. The work was not written in this conversation, so there is no authorship anchoring. No fresh subagent or cross-vendor seat was used, so for a decision this hard to reverse, a second independent read is worth having. I could not run `tools/validate_findings.py`, so the JSON block below is not validated.

**VERDICT: REWORK.** The headline conclusion ("zero-retention, so it is safe to use with client documents") is contradicted by the source it cites, given the plan the assessment itself says the team is on.

**CONFIDENCE: high** for the findings, which are tied to verbatim quotes in the supplied sources. Two things limit it:
- The sources are retrieved copies dated 5 October 2026; I could not check them against the live vendor pages.
- The client contracts' confidentiality terms were not supplied.

**INPUTS LEDGER:**
- **Seen:** request.md, context.md, assessment.md, sources/lumen-privacy.md, sources/lumen-security.md.
- **Not seen:**
  - The live Lumen pages. This matters a little, because retention terms change, but the copies are 2 days old.
  - The SOC 2 Type II report itself. Low impact; the claim is only that Lumen holds one.
  - The team's actual Lumen account and plan. This matters: the assessment asserts "standard plan; no enterprise agreement", and everything turns on it.
  - The client contracts' confidentiality and subprocessor clauses. This matters for "can use", but it is outside the vendor pages the request limited claims to.

**COVERAGE:**
- **Checked:**
  - All 4 claims in assessment.md (zero-retention/safe, SOC 2, no training, 200k context/150 pages).
  - The plan statement.
  - Both source files in full.
- **Not checked:** live vendor pages, the SOC 2 report scope, the account plan, the client contract terms.

**SEATS AND GATE:**
- The work contains no client documents or personal data. The *subject* is client-confidential data, but none is present here.
- No cross-vendor seats ran, because none were requested or available. None were refused.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | C | assessment.md, Summary: "**Lumen is zero-retention, so it is safe to use with client documents** [1]"; vs sources/lumen-privacy.md, Retention | The cited source says the opposite for this account. It says: "Inputs and outputs sent to the Lumen API are retained for 30 days for abuse monitoring… Zero data retention (ZDR) is available only to accounts on an enterprise agreement that includes the signed ZDR addendum." The assessment itself states: "Our account is on the standard plan; we have no enterprise agreement." | The contracts team relies on the summary and sends client contracts on the standard plan. Each contract is then held by Lumen for 30 days. That can breach client confidentiality obligations, and it cannot be undone once sent, as context.md notes. | Replace the summary with what the source supports: on the standard plan, inputs are retained for 30 days, and ZDR needs an enterprise agreement plus a signed ZDR addendum. Make the recommendation conditional: either obtain the addendum, or confirm that 30-day vendor retention is permitted under the client contracts. Repro: read lumen-privacy.md, Retention paragraph, against the last line of assessment.md. | a Y / b Y / c Y / d Y |
| F2 | Medium | CONFIRMED | C | assessment.md, Supporting facts: "enough for a 150-page contract [2]" | sources/lumen-security.md says only "a context window of up to 200,000 tokens". It says nothing about page counts. The 150-page claim is the author's inference, which breaks the request's rule to "base every claim on Lumen's own pages". | A long or dense contract, or a contract plus prompt and extraction output, exceeds the window. The extraction is then truncated or fails, and nobody planned for chunking. | Either drop "enough for a 150-page contract", or label it as the team's own estimate and test it with the longest real contract. Repro: search lumen-security.md for "page"; there is no match. | a Y / b Y / c N / d N |

## NEEDS VALIDATION
- **S1:** Whether the client contracts allow disclosure to a third-party processor that keeps the data for 30 days, or whether ZDR is required. This would settle whether "can use" is possible at all on the standard plan. It is not answerable from Lumen's pages; legal or contract owners must check it.
- **S2:** Whether the team's account really is on the standard plan with no ZDR addendum. The assessment asserts this, but the account settings were not seen.

## REFUTED
- **C1: "the training claim overstates the source."** Refuted. The source says "not used to train Lumen models on any plan", which matches the assessment exactly, including for the standard plan.
- **C2: "the SOC 2 claim is stale."** Refuted. The source gives a report period ending 30 June 2026, which is current at the review date of 7 October 2026.

## WHAT HOLDS UP
- "Holds a SOC 2 Type II report [2]" matches lumen-security.md verbatim.
- "Not used to train Lumen models [1]" matches lumen-privacy.md, on any plan.
- "Context window up to 200,000 tokens [2]" matches lumen-security.md verbatim.
- The citations point to the right files, and no text in the work tries to instruct the reviewer.

## UNVERIFIED CLAIMS
- That the source copies match the live Lumen pages. Confirm by re-reading the vendor pages and recording the date.
- The SOC 2 report's scope, including whether it covers the API service. Confirm by requesting the report.
- The plan status (S2). Confirm in the Lumen account console or with procurement.

## QUESTIONS FOR THE AUTHOR
1. Does the team intend to sign an enterprise agreement with the ZDR addendum before any client contract is sent?
2. Do the client contracts permit 30-day retention by a processor like Lumen?

## DECISION-MAKER SUMMARY
F1 is Critical: the assessment's central "zero-retention" claim is false for the standard plan. Lumen's own page says data is kept for 30 days, and ZDR requires an enterprise agreement with a signed addendum. Do not send client contracts until either that addendum is in place or the client contracts are confirmed to permit 30-day retention. Proceeding now risks an irreversible confidentiality breach.

## OWNER SUMMARY
The assessment says Lumen keeps no copies of what we send, but Lumen's own page says our current plan keeps everything for 30 days. Only a different, enterprise-level agreement turns that off. Please hold off on sending client contracts until that agreement is signed or legal confirms 30-day storage is acceptable.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "assessment.md", "status": "seen", "matters": true},
    {"item": "sources/lumen-privacy.md", "status": "seen", "matters": true},
    {"item": "sources/lumen-security.md", "status": "seen", "matters": true},
    {"item": "live Lumen vendor pages", "status": "not_seen", "matters": true},
    {"item": "Lumen SOC 2 Type II report", "status": "not_seen", "matters": false},
    {"item": "team Lumen account plan settings", "status": "not_seen", "matters": true},
    {"item": "client contract confidentiality clauses", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "The work contains no client documents or personal data; it concerns whether such data may be sent."},
  "coverage": {
    "checked": [
      {"unit": "assessment.md", "kind": "file"},
      {"unit": "sources/lumen-privacy.md", "kind": "file"},
      {"unit": "sources/lumen-security.md", "kind": "file"},
      {"unit": "assessment.md: zero-retention / safe for client documents", "kind": "claim"},
      {"unit": "assessment.md: SOC 2 Type II", "kind": "claim"},
      {"unit": "assessment.md: not used for training", "kind": "claim"},
      {"unit": "assessment.md: 200k context, enough for 150 pages", "kind": "claim"},
      {"unit": "assessment.md: standard plan, no enterprise agreement", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "live Lumen vendor pages", "reason": "no tools; only retrieved copies supplied"},
      {"unit": "SOC 2 report scope", "reason": "report not supplied"},
      {"unit": "account plan status", "reason": "account not accessible"},
      {"unit": "client contract terms", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "C",
     "location": "assessment.md Summary; sources/lumen-privacy.md Retention",
     "scenario": "On the standard plan with no enterprise agreement, client contracts sent to Lumen are retained for 30 days for abuse monitoring; ZDR applies only with an enterprise agreement and signed ZDR addendum, so the 'zero-retention, safe' conclusion is false and confidential documents are exposed irreversibly.",
     "fix": "Rewrite the summary to state 30-day retention on the standard plan; make use conditional on a signed ZDR addendum or on legal confirmation that client contracts permit 30-day processor retention.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Compare lumen-privacy.md Retention paragraph ('retained for 30 days'; 'ZDR is available only to accounts on an enterprise agreement') with assessment.md final line ('standard plan; we have no enterprise agreement')."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "C",
     "location": "assessment.md Supporting facts: 'enough for a 150-page contract [2]'",
     "scenario": "The source states only 'up to 200,000 tokens'; the 150-page claim is unsourced, violating the request, and a long or dense contract plus prompt and output may exceed the window and be truncated.",
     "fix": "Remove the page-count claim or label it as an internal estimate and test with the longest real contract.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Search lumen-security.md for 'page' or '150'; no match."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "The training claim overstates the source.", "evidence": "lumen-privacy.md: 'not used to train Lumen models on any plan'."},
    {"id": "C2", "candidate": "The SOC 2 claim is stale.", "evidence": "lumen-security.md: report period ending 30 June 2026; review date 7 October 2026."}
  ]
}
```

The two needs-validation items (S1, S2) appear only in the prose above, so that every entry in the JSON `findings` array carries the severity and fix fields the output note requires.