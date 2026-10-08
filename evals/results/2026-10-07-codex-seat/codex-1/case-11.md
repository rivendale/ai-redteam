same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.

**VERDICT: REWORK.** The limiter counts requests by IP address, directly violating the required per-user limit and office-network isolation.

**CONFIDENCE: high** on the requirement violation; production integration and runtime behavior remain unverified because no tools are available.

**INPUTS LEDGER**
- Seen: original request, production context, PR description, complete supplied limiter and tests.
- Not seen: authentication integration, middleware wiring, deployment topology, test-run output. These matter to enforcement in production and the claim that tests pass.
- No external artifacts were opened and no code was executed.

**SEATS AND GATE:** One reviewer performed static analysis. No independent or external seats ran; tools are unavailable. No sensitive information appears in the supplied material.

**RECONSTRUCTION — tracks B and C:** The PR claims a sliding-window limiter allowing 100 requests per 60 seconds. The implementation filters timestamps and checks the limit using a bucket selected by `remote_addr`; it never reads `user_id`. Correctness requires a trusted authenticated identity, one consistent accounting mechanism across requests, and integration that enforces denials. The tests exercise a single user at a single address, so they cannot establish the central isolation requirement.

**FINDINGS**

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | High | CONFIRMED | B | `rate_limit.py:13`, `key = request.remote_addr` | Accounting is per IP, not per authenticated user. | One office user consumes 100 requests; a second user at the same public IP is blocked on their first request. Conversely, one user accessing through two addresses gets separate allowances. | Key by trusted authenticated user identity. Test two users sharing an IP and one user using multiple IPs. Define handling of unauthenticated requests explicitly. | **confirmed:** the strongest defense—one IP per user—contradicts the explicit office-network requirement. |
| 2 | Medium | CONFIRMED | B | `test_rate_limit.py`, both test methods | The tests omit identity isolation and identity continuity, allowing the central defect to pass unnoticed. | The current tests can remain green while office users throttle each other. | Add the two identity tests above. In a throwaway copy, change correct user-based accounting back to IP-based accounting and confirm those tests fail. | Confirmed by inspection; execution and mutation coverage remain unverified. |
| 3 | Medium | CONFIRMED | B | `rate_limit.py:9,15,17,20` | Bucket keys are never removed; expired history is only filtered when that same key returns. | Many distinct addresses make requests once and disappear; their keys and timestamp lists remain for the process lifetime, increasing memory use. | Add bounded storage or periodic removal of expired buckets. Test many one-time identities followed by expiration and cleanup. | Confirmed by inspection; production memory impact depends on traffic. |

**WHAT HOLDS UP:** Under sequential calls using one bucket and a monotonic clock, the code admits up to the configured limit and excludes timestamps aged 60 seconds or more. The supplied tests target basic blocking and expiration. No rewriting or modification was performed.

**UNVERIFIED CLAIMS**
- **“Tests added and passing”:** tests are supplied, but no execution evidence is available. Run them and provide output; validate the new identity tests with mutation.
- **Production enforcement:** no middleware integration or denial response is shown. Verify that every protected route invokes the limiter after authentication and returns an appropriate rate-limit response.
- **Global per-user accounting:** state is instance-local. If deployment uses multiple independent instances, allowances may multiply. Inspect topology and test a user’s combined traffic across instances.
- **Concurrent enforcement:** checking and recording are separate operations. Verify atomic accounting under the actual execution model with concurrent requests.

**QUESTIONS FOR THE AUTHOR:** Is the limiter invoked after trusted authentication, and how is its accounting shared and made atomic across production workers or instances?

**DECISION-MAKER SUMMARY:** Return the PR for per-user accounting and identity-focused tests. Confirm production integration, shared accounting, and concurrency behavior before release. Shipping the current implementation breaks the explicitly requested office-network isolation.

**OWNER SUMMARY:** People sharing an office internet connection would share one request allowance and could block each other. Change the allowance to follow each signed-in person, then verify that different people remain independent and one person cannot gain extra allowance by changing networks.

```json
{
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "Original request, context, PR description, limiter and tests", "status": "seen", "matters": true},
    {"item": "Authentication and middleware integration", "status": "not_seen", "matters": true},
    {"item": "Deployment topology and test execution evidence", "status": "not_seen", "matters": true}
  ],
  "seats": [
    {"vendor": "OpenAI", "status": "ran_static_review_only", "cross_vendor": false}
  ],
  "sensitivity_gate": {"sensitive": false, "reason": "No sensitive material appears in the supplied inputs."},
  "findings": [
    {
      "severity": "High",
      "evidence_level": "CONFIRMED",
      "track": "B",
      "location": "rate_limit.py:13",
      "scenario": "Two authenticated users sharing an IP share the allowance; one user using multiple IPs receives multiple allowances.",
      "fix": "Key accounting by trusted authenticated user identity; test shared-IP users and one user across multiple IPs.",
      "status": "confirmed"
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "track": "B",
      "location": "test_rate_limit.py:7-20",
      "scenario": "Single-user, single-address tests do not detect IP-based accounting that violates the original request.",
      "fix": "Add identity isolation and continuity tests; verify they fail under an IP-key mutation in a throwaway copy.",
      "status": "confirmed"
    },
    {
      "severity": "Medium",
      "evidence_level": "CONFIRMED",
      "track": "B",
      "location": "rate_limit.py:9,15,17,20",
      "scenario": "One-time callers leave buckets retained for the lifetime of the process, increasing memory use as distinct keys accumulate.",
      "fix": "Bound storage or remove expired buckets periodically; test cleanup after many one-time callers.",
      "status": "confirmed"
    }
  ]
}
```