VERDICT: watch. ShaderLint is free with no account, so nothing here needs your approval, but it serves none of our four goals today; revisit if shader or GPU faults show up in the Crashlytics top five.

WHAT IT IS: ShaderLint, a product, read from the pricing and terms page as captured on 2026-10-08 (saved snapshot, not a live read). The free tier costs $0 with no account, no card and no usage limits. It comes as a command-line binary and an editor window. The license is "freeware, commercial use allowed", so it is proprietary, not open source. Optional paid support costs $200/year. The snapshot is the pricing page only: it does not say what the tool checks, which platforms it runs on, or its version and release history.

CLAIMS CHECKED:
- **"Free for commercial use"** (sender, and the vendor's terms): CONFIRMED. The terms say "free for commercial and personal use" and "commercial use allowed". The verdict rests on this, because it is why no approval is needed.
- **"No account, no card, no usage limits"**: CONFIRMED as the stated terms. The verdict rests on this too.
- **"Checks HLSL in Unity projects"** (sender): UNVERIFIED. The pricing page never names HLSL, Unity or what the rules are. "An editor window" hints at an editor plugin but does not say which editor.
- **"Runs on your machine and sends nothing anywhere"**: UNVERIFIED. This is the vendor's own statement, and it is a closed freeware binary with no source to read. It matters less here because shaders are not player data, but nothing confirms it.
- **"Paid support is not needed to use the tool"**: CONFIRMED as stated in the terms.

FIT:
- **Goal:** none found.
  - It does not shorten the Android build (goal 1).
  - It is unrelated to localisation (goal 3) and the devlog (goal 4).
  - It could only touch crash noise (goal 2) if shader faults are among our top crashes, and nothing shows that they are.
- **Overlap:** Unity 6 already compiles shaders and reports HLSL errors on every Jenkins build. A linter would only add style and portability warnings beyond that.
- **Burden:**
  - A new binary to install on the Mac mini and on Windows machines, if those platforms are supported at all (unknown).
  - Possibly a new Jenkins step, which adds time to the build that goal 1 is trying to shorten.
- **Cost:** $0 on the free tier, with no limits, read 2026-10-08. The $200/year support is optional and would need approval.
- **Risks:**
  - The license is proprietary freeware. Our license rules list only open-source licenses, but they are about code we ship, and this is a tool we would run and never ship, so it seems acceptable. The operator should confirm.
  - We cannot audit a closed binary's "sends nothing" claim.
  - Project health and platform support are unknown from this page.
  - Freeware terms can change later.

NEXT ACTION: When the operator next reviews the Crashlytics top five, check whether any are GPU or shader faults on Android.
- Owner: operator.
- Done when: the top five has been reviewed for shader-related crashes. If any appear, re-assess ShaderLint from its feature docs, checking HLSL rules and macOS/Windows support.
- Hand-off: none.

CONFIDENCE: medium. The context file is present and the claims the verdict rests on are confirmed. It is limited because:
- I worked from a saved pricing snapshot only, with no feature, platform or health information.
- The sender's main claim (it checks HLSL in Unity) cannot be settled from this page.

```json
{
  "schema_version": "assess-1",
  "verdict": "watch",
  "item": {"type": "product", "identity": "ShaderLint free tier, $0, freeware (commercial use allowed), pricing page snapshot read 2026-10-08", "resolved": true},
  "claims": [
    {"claim": "free for commercial use", "evidence": "pricing/terms: 'free for commercial and personal use', 'commercial use allowed'", "status": "CONFIRMED"},
    {"claim": "no account, no card, no usage limits", "evidence": "pricing/terms text", "status": "CONFIRMED"},
    {"claim": "checks HLSL in Unity projects", "evidence": "sender's words only; pricing page does not mention HLSL or Unity", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "runs locally and sends nothing anywhere", "evidence": "vendor statement on a closed freeware binary; no source to read", "status": "UNVERIFIED", "load_bearing": false},
    {"claim": "paid support is optional and not needed", "evidence": "pricing/terms text", "status": "CONFIRMED", "load_bearing": false}
  ],
  "fit": {"goal": "none found (closest is goal 2, only if shader faults reach the Crashlytics top five)",
          "overlap": "Unity 6 shader compilation already reports HLSL errors on every Jenkins build",
          "burden": "new binary on the Mac mini and Windows machines (platform support unknown), possibly a new Jenkins step",
          "risks": ["proprietary freeware; license rules cover shipped code, this is a run-only tool, operator to confirm", "closed binary, 'sends nothing' cannot be audited", "platform support and project health unknown", "freeware terms can change"],
          "cost": {"price": "$0", "tier": "free", "limits": "none stated", "terms": "freeware, commercial use allowed; optional support $200/year", "checked_at": "2026-10-08"}},
  "next_action": {"action": "At the next Crashlytics review, check whether any top-five crashes are GPU/shader faults on Android; if so, re-assess ShaderLint from its feature docs",
                  "owner": "operator", "done_when": "top five reviewed for shader-related crashes", "handoff": "none"},
  "confidence": "medium",
  "context_file": "present"
}
```