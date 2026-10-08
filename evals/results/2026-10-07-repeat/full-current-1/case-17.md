# Redteam review: Lumen API vendor assessment

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent or tools were available in this session. I checked everything by reading the three supplied files side by side and ran no code.

**VERDICT: REWORK.** The headline conclusion, "zero-retention, so it is safe", is contradicted by the cited source and by the assessment's own note that the account is on the standard plan.

**CONFIDENCE: high** for the main finding, which is a direct quote mismatch across files I was given. It is **medium** for the rest, because:
- this was a single-reviewer, same-context review with no tools;
- I could not check the source files against Lumen's live pages.

**INPUTS LEDGER:**
- **Seen:**
  - `request.md` (original request)
  - `context.md`
  - `assessment.md`
  - `sources/lumen-privacy.md`
  - `sources/lumen-security.md`
- **Not seen or not openable:**
  - Lumen's live web pages. Both sources say "retrieved 5 October 2026", two days before review. I could not confirm the copies match the live pages, so this matters a little.
  - The SOC 2 Type II report itself. This matters little here, because SOC 2 does not establish retention terms.
  - Lumen's terms of service, DPA, subprocessor list and data-location statement. These **matter**: a decision about client-confidential documents needs them, and the assessment does not cite them.
  - Client contracts' confidentiality and third-party-processing clauses. These **matter** for "safe to use with client documents".
  - The plan or enterprise agreement itself. The assessment states "standard plan; no enterprise agreement", and I took that statement as given.

**SEATS AND GATE:**
- Only the local reviewer ran. No cross-vendor seats were requested, and the depth inferred is `standard`.
- Sensitivity gate: the work under review contains no client documents or personal data. The sources are public vendor pages, so the gate passed. The *subject* of the decision is client-confidential data.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | C | `assessment.md`, Summary: "**Lumen is zero-retention, so it is safe to use with client documents** [1]" vs `sources/lumen-privacy.md`, Retention | The cited source [1] says the opposite: "Inputs and outputs sent to the Lumen API are retained for 30 days for abuse monitoring and are then deleted. Zero data retention (ZDR) is available only to accounts on an enterprise agreement that includes the signed ZDR addendum." The assessment itself states: "Our account is on the standard plan; we have no enterprise agreement." Zero retention does not apply to this account. | The contracts team relies on the summary and sends client contracts. Each contract is held by Lumen for 30 days and is available for abuse monitoring, which may include human review. That could breach client confidentiality terms. The context notes this cannot be undone once documents are sent. | Restate the summary: "On our standard plan, Lumen retains inputs and outputs for 30 days. ZDR requires an enterprise agreement with the signed ZDR addendum." Do not approve client-document use until both the agreement and the addendum are signed and confirmed on the account. | **Confirmed.** The strongest defence is that "zero-retention" meant "not used for training". That fails: the source treats Retention and Training as separate headings, and the assessment cites the retention page for this claim. A second defence is that the account might have ZDR. The assessment's own last line rules that out. |
| 2 | Medium | PROBABLE | A / C | `assessment.md`, Summary: "so it is safe to use with client documents" | The safety conclusion rests only on retention. Even with ZDR, "safe for client documents" also depends on things the assessment does not address and its sources do not cover: client contract terms on third-party processors, data location, subprocessors, and access during processing. | A ZDR addendum is later signed and the assessment is re-used as-is. A client contract that forbids unapproved processors is breached anyway. | Change the conclusion to a conditional one. Add the missing checks: client confidentiality clauses, Lumen DPA and subprocessor list, and data location. Cite each to a Lumen page or mark it open. | n/a (Medium) |
| 3 | Low | CONFIRMED | C | `assessment.md`, Supporting facts: "up to 200,000 tokens, enough for a 150-page contract [2]" | Source [2] supports "up to 200,000 tokens" only. "Enough for a 150-page contract" appears in neither source, which breaks the request's rule to "base every claim on Lumen's own pages". The estimate is plausible: about 150 × 500 words ≈ 75k words ≈ 100k tokens. But it is unsupported, and it ignores that the prompt and the output share the window. | Dense or scanned contracts, or multi-document batches, exceed the window. Extraction is then truncated or fails. | Mark it as the team's own estimate, not a Lumen claim. Test with the largest real contract (token count via the API) before relying on it. | n/a |

## WHAT HOLDS UP

- **"Lumen holds a SOC 2 Type II report [2]"** matches `lumen-security.md` verbatim. The page adds "period ending 30 June 2026", which the assessment should record. A SOC 2 report attests to controls, not to retention, so it does not rescue finding 1.
- **"Inputs and outputs are not used to train Lumen models [1]"** matches `lumen-privacy.md`, which also adds "on any plan". It therefore applies to the standard plan.
- **Source freshness:** both pages were retrieved 5 October 2026, two days before this review. That is acceptable for this claim class.
- **No injected instructions:** no text in the work addresses the reviewer.

## UNVERIFIED CLAIMS

- **That the files in `sources/` match Lumen's live pages.** To settle it: re-open both pages on the decision date and compare them.
- **"Our account is on the standard plan; we have no enterprise agreement."** To settle it: check the Lumen account console or billing records. This fact decides finding 1's impact, though not its existence.
- **That the SOC 2 report covers the API service and has no exceptions relevant here.** To settle it: obtain the report under NDA and read the scope and the exceptions section.

## QUESTIONS FOR THE AUTHOR

1. Is the team willing to obtain an enterprise agreement with the signed ZDR addendum before any client contract is sent?
2. Do the affected client contracts permit sending documents to a third-party processor at all, and under what conditions?

## DECISION-MAKER SUMMARY

The assessment's core claim is false for our account. Lumen keeps everything sent to it for 30 days unless we sign an enterprise agreement with a ZDR addendum, and we have neither. Do not send client contracts until that addendum is signed and client confidentiality terms are checked. Proceeding now exposes client documents to 30-day vendor retention, and that cannot be reversed.

## OWNER SUMMARY

The write-up says the service deletes our data immediately, but the service's own page says it keeps our data for 30 days unless we sign a special enterprise agreement, which we have not. Please do not send any client contracts to this service yet. Once the special agreement is in place and we have checked that our clients allow it, the question can be looked at again.

```json
{
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "assessment.md", "status": "seen", "matters": true},
    {"item": "sources/lumen-privacy.md", "status": "seen", "matters": true},
    {"item": "sources/lumen-security.md", "status": "seen", "matters": true},
    {"item": "Lumen live web pages", "status": "not_openable", "matters": true},
    {"item": "Lumen SOC 2 Type II report", "status": "not_seen", "matters": false},
    {"item": "Lumen DPA, terms, subprocessor list, data location", "status": "not_seen", "matters": true},
    {"item": "Client contract confidentiality clauses", "status": "not_seen", "matters": true},
    {"item": "Account plan / enterprise agreement records", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "local-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Work and sources contain no client documents or personal data; vendor pages are public."},
  "findings": [
    {
      "severity": "Critical",
      "evidence_level": "CONFIRMED",
      "track": "C",
      "location": "assessment.md Summary ('Lumen is zero-retention, so it is safe to use with client documents [1]') vs sources/lumen-privacy.md Retention",
      "scenario": "Cited source says inputs/outputs are retained 30 days for abuse monitoring and ZDR requires an enterprise agreement with a signed ZDR addendum; the assessment states the account is standard plan with no enterprise agreement. Team sends client contracts relying on the summary; they are retained 30 days, possibly breaching client confidentiality, irreversibly.",
      "fix": "Restate the summary to reflect 30-day retention on the standard plan; block client-document use until an enterprise agreement with the signed ZDR addendum is in force and confirmed on the account.",
      "status": "confirmed"
    },
    {
      "severity": "Medium",
      "evidence_level": "PROBABLE",
      "track": "A",
      "location": "assessment.md Summary ('safe to use with client documents')",
      "scenario": "Safety is concluded from retention alone; even with ZDR, client contracts may forbid unapproved processors or require data-location or subprocessor controls, so reuse of the assessment could still cause a breach.",
      "fix": "Make the conclusion conditional; add checks of client confidentiality clauses, Lumen DPA, subprocessor list and data location, each cited or marked open.",
      "status": "n/a"
    },
    {
      "severity": "Low",
      "evidence_level": "CONFIRMED",
      "track": "C",
      "location": "assessment.md Supporting facts ('enough for a 150-page contract [2]')",
      "scenario": "Source supports only 'up to 200,000 tokens'; the 150-page sufficiency claim is not on Lumen's pages, contrary to the request. Dense or batched contracts plus output could exceed the window and truncate extraction.",
      "fix": "Label as the team's own estimate; measure token counts on the largest real contract before relying on it.",
      "status": "n/a"
    }
  ]
}
```
