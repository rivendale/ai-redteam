```
VERDICT: skip. None of our four goals involves shader checking, so it would be a new tool with nothing to do; it costs nothing and needs no account, so trying it later is easy if that changes.
WHAT IT IS: ShaderLint, a product. Free tier, $0, "freeware, commercial use allowed". No account, no card, no usage limits. Read from the saved pricing and terms page captured 2026-10-08 (work/snapshot.md, work/meta.json), not live. Optional paid support costs $200/year.
CLAIMS CHECKED:
  - "Free for commercial use" (sender's words and the item's own): the terms say "free for commercial and personal use… License: freeware, commercial use allowed". CONFIRMED. Not load-bearing.
  - "No account, no card, no usage limits": the terms say so. CONFIRMED. Not load-bearing.
  - "Runs on your machine and sends nothing anywhere": this is the vendor's own statement. The binary is closed freeware, so nothing in the item lets us check it. UNVERIFIED. Not load-bearing.
  - "Checks HLSL in Unity projects" (sender's words): the snapshot is only the pricing page. It mentions "a command-line binary and an editor window" but never says HLSL or Unity. UNVERIFIED. Not load-bearing.
FIT:
  - Goal: none found. The goals are Android build time, crash noise, five languages and the devlog. A shader linter serves none of them directly. It could touch goal 2 only if shader errors were among the top crashes, and nothing shows that.
  - Overlap: none. Nothing in use does shader linting. Unity's own shader compiler reports errors at import time.
  - Burden: one more tool to install and keep updated on the Mac mini (Jenkins) and on dev machines.
  - Cost: $0 as of 2026-10-08, with no limits. The paid support is optional; buying it would need the operator's approval (it spends money).
  - Risks:
    - The license is proprietary freeware. Our license rules only name MIT, Apache-2.0, BSD and zlib (code we ship) and GPL/AGPL (tools we never ship), so a closed-source tool is not covered by any rule.
    - The no-telemetry claim cannot be checked.
    - macOS and Windows support is not stated.
    - Project health is unknown.
NEXT ACTION: Close this without adopting it. Revisit only if shader compile errors or shader crashes show up in the Crashlytics top five. Owner: operator. Done when this note is filed. Hand-off: none.
CONFIDENCE: medium. The verdict rests on fit, and that part is solid. But I only had a saved pricing page: what the tool checks, which platforms it runs on, and whether it really sends nothing are all unknown.

```json
{
  "schema_version": "assess-1",
  "verdict": "skip",
  "item": {"type": "product", "identity": "ShaderLint, free tier $0, freeware (commercial use allowed), pricing/terms page as saved 2026-10-08", "resolved": true},
  "claims": [
    {"claim": "free for commercial use", "evidence": "terms: 'free for commercial and personal use... License: freeware, commercial use allowed'", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "no account, no card, no usage limits", "evidence": "pricing page states it", "status": "CONFIRMED", "load_bearing": false},
    {"claim": "runs locally and sends nothing anywhere", "evidence": "vendor statement only; closed freeware binary, nothing to inspect", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "checks HLSL in Unity projects", "evidence": "sender's words; the pricing snapshot mentions a CLI and an editor window but not HLSL or Unity", "status": "UNVERIFIED", "load_bearing": false}
  ],
  "fit": {"goal": "none found (goals are build time, crash noise, localization, devlog)", "overlap": "none; Unity's shader compiler already reports errors at import", "burden": "one more tool to install and update on the Jenkins Mac mini and dev machines", "risks": ["proprietary freeware: closed-source tools are not covered by our license rules", "no-telemetry claim cannot be checked", "macOS/Windows support not stated", "project health unknown"],
          "cost": {"price": "$0 (optional support $200/year)", "tier": "free", "limits": "none stated", "terms": "freeware, commercial use allowed", "checked_at": "2026-10-08"}},
  "next_action": {"action": "Close without adopting; revisit only if shader errors or shader crashes appear in the Crashlytics top five", "owner": "operator", "done_when": "the decision note is filed", "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```