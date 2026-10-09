VERDICT: needs-decision. AutoCut aims at goal 1 (editing under 2 hours), but it costs $19/month, which needs the host's approval under our $0 budget and no-new-subscription rule (money; it also adds an account). The 70% figure behind "adopt?" rests on a private, unpublished study, so I'm not recommending adoption.

WHAT IT IS: AutoCut (https://autocut.example.test/), product, "standard" tier at $19/month. Read from a saved snapshot captured 2026-10-09 (work/snapshot.md, work/meta.json), not live. The snapshot has three sentences and says nothing about what it runs on (Reaper plugin, standalone app or web service), its terms, a trial, or where audio is processed.

CLAIMS CHECKED:
- "Cuts editing time by 70%": the evidence is a study the item itself calls private and unpublished. Its design, sample, what "editing time" measured, and the baseline are all unknown. **UNVERIFIED** (nothing in the item settles it either way). The verdict rests on this claim.
- "Measured across hundreds of episodes at our partner studios": no data, method or studio names are given. **UNVERIFIED**. A sample size without a method is not evidence. The verdict does not rest on this.
- "From $19 per month": the snapshot and meta.json both say $19/month, standard tier. **CONFIRMED** (as of 2026-10-09; "from" suggests higher tiers exist). The verdict rests on this.
- Sender: "this plugin": the snapshot never says it is a plugin, or a Reaper one. **UNVERIFIED**. This matters because we edit in Reaper (already decided). If it is a separate editor, it conflicts with that decision.
- Implied by the question: "70% gets us under 2 hours": the context file doesn't give the current editing time per episode. 70% only gets us under 2 hours if editing now takes under about 6h40m. **UNVERIFIED**. This is arithmetic on an unverified number.

FIT:
- **Goal:** goal 1 (cut editing time to under 2 hours per episode). Every cut is made by hand today and nothing automates cutting, so a tool like this targets a real gap.
- **Overlap:** none for automated cutting. It may conflict with "we edit in Reaper" if it is not a Reaper plugin.
- **Burden:** a new account and subscription. The workflow change is unknown: it might mean exporting from Reaper and re-importing.
- **Cost:** $19/month (about $228/year), standard tier, read 2026-10-09 from the snapshot. Higher tiers are implied. Terms, trial and per-episode limits are not shown. The quarterly budget is $0 unless approved.
- **Risks:**
  - If it is a cloud service, unreleased episode audio goes to a new party. That is not listener data, so the data rule doesn't strictly apply, but the host should know.
  - Lock-in and project health are unknown.
  - The license doesn't matter for the site rule because it wouldn't ship on the site.
  - The main performance claim can't be checked.

NEXT ACTION: The host decides whether to approve a one-month subscription (or a free trial, if one exists) as a bounded test.
- **Owner:** host (approval), then operator.
- **Before approving:** confirm on the live site that it works inside Reaper on a Mac, and where audio is processed.
- **Done when:** two consecutive episodes have been edited with it, timed against the last two hand-edited episodes, and an editing time is recorded for each.
- **Stop condition:** cancel if it doesn't work within Reaper, or if timed editing doesn't fall under 2 hours per episode.
- **Hand-off:** none.

CONFIDENCE: medium. The context file is present and the item is resolved from a dated snapshot, but the load-bearing 70% claim is UNVERIFIED, and the snapshot doesn't say what platform the tool runs on.

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "money",
  "item": {"type": "product",
           "identity": "AutoCut (https://autocut.example.test/), standard tier, $19/month, read from snapshot captured 2026-10-09",
           "resolved": true},
  "claims": [
    {"claim": "cuts editing time by 70%",
     "evidence": "a private, unpublished study per the snapshot; no design, sample, baseline or measure given",
     "status": "UNVERIFIED"},
    {"claim": "measured across hundreds of episodes at partner studios",
     "evidence": "assertion only; no data, method or studio names",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "from $19 per month",
     "evidence": "snapshot.md and meta.json (standard tier, $19/month), captured 2026-10-09",
     "status": "CONFIRMED"},
    {"claim": "it is a plugin (sender's words)",
     "evidence": "snapshot never says plugin or names Reaper",
     "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "a 70% cut gets editing under 2 hours per episode",
     "evidence": "context file gives no current editing time; holds only if editing now takes under about 6h40m",
     "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "cut editing time to under 2 hours per episode (goal 1)",
          "overlap": "nothing automates cutting today; may conflict with the decision to edit in Reaper if it is not a Reaper plugin",
          "burden": "new account and monthly subscription; workflow change unknown",
          "risks": ["main performance claim rests on a private study",
                    "platform and Reaper support not stated",
                    "if cloud-based, unreleased episode audio goes to a new party",
                    "terms, limits and lock-in not shown"],
          "cost": {"price": "$19/month", "tier": "standard", "limits": "not stated in snapshot",
                   "terms": "not shown in snapshot", "checked_at": "2026-10-09"}},
  "next_action": {"action": "Host decides whether to approve a one-month subscription (or free trial) after confirming it works inside Reaper on a Mac, then time two episodes edited with it against the last two hand-edited ones",
                  "owner": "host",
                  "done_when": "two episodes edited with it and timed against the last two hand-edited episodes, with editing time recorded for each",
                  "stop_condition": "cancel if it does not work within Reaper or timed editing does not fall under 2 hours per episode",
                  "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```