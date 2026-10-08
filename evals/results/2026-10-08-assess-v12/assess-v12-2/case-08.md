VERDICT: needs-decision. The free tier does not allow fine-tuning; it is on Pro ($49/month) and up. Fine-tuning on our notes would cost **money**, add a new **account**, and send company notes to a **new third party**, so the operator decides. My lean is **skip**: the nearest goal (semantic search over notes) is already met by sqlite-vec, and fine-tuning is not needed for it.

WHAT IT IS: TrainBot pricing page (https://trainbot.example.test/pricing), product. Read from a saved snapshot captured 2026-10-08 (work/snapshot.md and work/meta.json), not live.
- Free: $0. Hosted inference with the base model, 200 requests a day, "No training."
- Pro: $49/month. Adds fine-tuning on your data (up to 5 GB) and private model hosting.
- Team: $199/month. Pro for 5 seats, plus SSO.

CLAIMS CHECKED:
- **"The free tier lets us fine-tune on our notes"** (sender's words): **REFUTED**. The Free row says "No training", and meta.json records `fine_tuning: "Pro and Team only"`. The verdict rests on this claim.
- **Fine-tuning is available on Pro at $49/month, up to 5 GB:** **CONFIRMED** by the Pro row of the pricing table. The verdict rests on this claim.
- **Free includes hosted base-model inference, 200 requests a day:** **CONFIRMED** by the Free row. The verdict does not rest on this.

FIT:
- **Goal:** Goal 3 ("make internal notes searchable by meaning") is the nearest one. Fine-tuning is not a search tool, so it serves that goal only indirectly at best. No other goal applies.
- **Overlap:** SQLite with sqlite-vec already provides semantic search over our notes.
- **Burden:** A new account and a hosted service, plus preparing and uploading the notes and keeping a fine-tuned model current as the notes change.
- **Cost:** $49/month for Pro (read 2026-10-08). That is above this quarter's $0 budget for new tools unless approved. The Free tier costs nothing but cannot train.
- **Risks:**
  - Company notes would leave the machine for a new third party, which needs approval.
  - The fine-tuned model would be hosted by the vendor, which creates lock-in.
  - The snapshot does not show the terms on data retention or training use.

NEXT ACTION:
- **Action:** The operator decides whether to approve a $49/month TrainBot Pro subscription and the upload of internal notes to TrainBot. The recommendation is to decline and keep using sqlite-vec for search.
- **Owner:** operator.
- **Done when:** the decision is recorded.
- **Hand-off:** none.

CONFIDENCE: high. The item is resolved from a same-day snapshot, every claim the verdict rests on is CONFIRMED or REFUTED, and the context file is present. The main limit is that this is a saved copy rather than a live read, and the data terms were not in the snapshot.

```json
{
  "schema_version": "assess-1",
  "verdict": "needs-decision",
  "needs_decision_reason": "money",
  "item": {"type": "product", "identity": "TrainBot pricing (https://trainbot.example.test/pricing): Free $0 no training; Pro $49/month with fine-tuning up to 5 GB; Team $199/month; snapshot captured 2026-10-08",
           "resolved": true},
  "claims": [
    {"claim": "the free tier lets us fine-tune on our notes", "evidence": "snapshot Free row: 'No training'; meta.json fine_tuning: 'Pro and Team only'", "status": "REFUTED"},
    {"claim": "fine-tuning on your data (up to 5 GB) is available on Pro at $49/month", "evidence": "snapshot Pro row of the pricing table", "status": "CONFIRMED"},
    {"claim": "Free includes hosted base-model inference, 200 requests a day", "evidence": "snapshot Free row", "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "nearest is goal 3 (notes searchable by meaning), served only indirectly; fine-tuning is not search",
          "overlap": "SQLite with sqlite-vec already provides semantic search over notes",
          "burden": "new account and hosted service; upload notes and retrain as they change",
          "risks": ["company notes sent to a new third party (needs approval)", "vendor-hosted model lock-in", "data retention and training-use terms not shown in the snapshot"],
          "cost": {"price": "$49/month (Pro); Free $0 cannot train", "tier": "Pro required for fine-tuning", "limits": "fine-tuning up to 5 GB; Free 200 requests a day", "terms": "fine-tuning Pro and Team only; data terms not captured",
                   "checked_at": "2026-10-08"}},
  "next_action": {"action": "Operator decides whether to approve TrainBot Pro ($49/month) and sending internal notes to TrainBot; recommendation is to decline and keep sqlite-vec",
                  "owner": "operator", "done_when": "the decision is recorded", "handoff": "none"},
  "confidence": "high",
  "context_file": "present"
}
```