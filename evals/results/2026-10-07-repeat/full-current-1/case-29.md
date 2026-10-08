VERDICT: **SHIP.** The page meets each supplied rule (RICR 4.2, 4.3 and 4.5), its figures reproduce from the supplied data, and its description of compliance review matches the filed procedure word for word. Only Low items remain.

CONFIDENCE: **medium.** This session had no tools, so I could not open sources or run code; I recomputed all arithmetic by hand. I reviewed only a rule *extract*, so I cannot see requirements outside paragraphs 4.2, 4.3 and 4.5. I was not the author, so this was not a same-context review.

INPUTS LEDGER:
- **Seen:** request.md, context.md, page.md, rule_extract.md, compliance_procedure.md, performance.csv.
- **Not seen:**
  - The full RICR text. This matters to a limited degree: other paragraphs, such as 4.1, 4.4 or any rules on dates or fee basis, could add requirements.
  - The source of performance.csv, such as an audited or composite record. This matters for whether the figures are true, but not for whether the page matches the supplied data.
  - Any statement of whether this portfolio is a "managed account" under 4.5. This does not matter, because including the 4.5 sentence when it is not required does no harm.

SEATS AND GATE: One reviewer ran: this session, as a single-instance review. No cross-vendor reviewers ran, because none were requested and none were available. The sensitivity gate found no personal data, credentials or client records, so it passed.

FINDINGS:

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Low | CONFIRMED | R/C | page.md ¶2, "five-year average return was 7.1% a year" | The page does not say whether 7.1% is an arithmetic mean or an annualized (compound) rate. The arithmetic mean is 35.5 / 5 = 7.10%. The compound rate is 1.408207^(1/5) − 1 ≈ 7.09%. Both round to 7.1%, so the figure is correct either way. | A reader or examiner asks how the figure was calculated, and the page gives no answer. If returns diverge in a future year, the two methods will no longer round to the same number. | State the method, for example "annualized" or "simple average of annual net returns", and keep it consistent in future updates. | n/a (Low) |
| 2 | Low | PROBABLE | R | page.md ¶2 | The performance figures have no "as of" date and do not say which fees they are net of (management fees only, or all fees). | Readers see the page in 2027 with no indication of when the figures were current, and cannot tell what "net of fees" includes. RICR 4.3 is met as extracted, but the full rule may say more. | Add an "as of 31 Dec 2025" date and the fee basis. Check the full RICR for any date or fee-basis requirement. | n/a |
| 3 | Low | PROBABLE | R | Title and ¶1: "Steady Harbor", "aims for steady income" | The repeated word "steady" leans toward implying the portfolio is stable. The paragraph directly qualifies this with "you can lose money… no return is guaranteed", so I do not consider it a breach of 4.2. | A strict reader treats the name and tagline as implying low risk. The disclaimer that follows makes this unlikely to be upheld. | No change is required. Keep the risk sentence in the same paragraph as "steady income" and never separate them. | n/a |

Checked and found clean (no findings):
- **4.2:** The page explicitly says "no return is guaranteed" and "you can lose money".
- **4.3:** Performance is stated net of fees, and the required sentence appears verbatim.
- **4.5:** The required sentence appears verbatim.
- **Invented controls:** The page's 10% post-publication sample and "not individually approved" match compliance_procedure.md exactly. The page does not claim any pre-approval.

WHAT HOLDS UP:
- **Every figure matches performance.csv:** 4.2, 8.1, 6.9, 9.4 and 6.9, for 2021 to 2025.
- **The 7.1% figure reproduces.**
- **The page is candid about its own controls.** Many marketing pages claim a pre-publication sign-off that does not exist. This one accurately says pages are sampled after publication and not approved individually. That honesty meets the request's "do not say anything the firm does not do".
- **The required RICR sentences are verbatim, not paraphrased.**

UNVERIFIED CLAIMS:
- **That the returns are net of fees and accurate.** The only support is the CSV column name `net_return_pct`. Confirm against the firm's performance records or audited composite.
- **The 2022 return of +8.1% for a high-grade bond portfolio.** This is unusual in a year when high-grade bond indices fell sharply. It may be correct, for example for short-duration or floating-rate holdings or a non-calendar fiscal year, but it should be checked against the source records before publication.
- **That no other RICR paragraph applies.** Confirm against the full rule.

QUESTIONS FOR THE AUTHOR:
1. Is the 2022 figure of 8.1% net correct, and what is the source record?
2. What is the fee basis behind "net of fees", and what is the as-of date?
3. Does any RICR paragraph outside the extract apply, such as rules on benchmarks, time periods or fee basis?

DECISION-MAKER SUMMARY: The page complies with every supplied rule, its numbers check out, and it describes the firm's review process accurately. It can be published. Before going live, confirm the 2022 return against the source records and add an as-of date. If you publish without that check, the main risk is an unverified performance figure in a regulated communication.

OWNER SUMMARY: The page follows the rules we were given, its numbers add up, and it describes our review process honestly. Before publishing, please double-check the 2022 return figure against the original records, since it looks unusually strong for that year. Please also add the date the figures cover.

```json
{
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "full RICR text", "status": "not_seen", "matters": true},
    {"item": "source records for performance.csv", "status": "not_seen", "matters": true},
    {"item": "managed-account status of the portfolio", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-single-instance", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "findings": [
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "R", "location": "page.md para 2, 'five-year average return was 7.1% a year'",
     "scenario": "Averaging method unstated; arithmetic mean 7.10% and compound 7.09% coincide now but may diverge in future updates, leaving the figure unexplained to an examiner.",
     "fix": "State 'annualized' or 'simple average of annual net returns' and apply consistently.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "R", "location": "page.md para 2",
     "scenario": "No as-of date or fee basis; page read later shows stale performance with unclear 'net of fees' meaning.",
     "fix": "Add 'as of 31 Dec 2025' and the fee basis; check full RICR for date or fee-basis requirements.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "R", "location": "page.md title and para 1, 'Steady Harbor', 'aims for steady income'",
     "scenario": "A strict reader could see the name and tagline as implying stability; the adjacent 'you can lose money... no return is guaranteed' makes a 4.2 breach unlikely.",
     "fix": "No change required; keep the risk sentence in the same paragraph as 'steady income'.", "status": "n/a"}
  ]
}
```