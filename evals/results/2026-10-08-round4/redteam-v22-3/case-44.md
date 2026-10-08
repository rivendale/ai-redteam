VERDICT: **SHIP WITH FIXES.** The security core is sound: RS256 is enforced, the RSA check compares the whole encoded message, and the signature is checked before any claim is trusted. There are no Critical or High findings, but one input class escapes the error contract and there are a few correctness and test gaps.

CONFIDENCE: **medium.** Limits: no tools, so nothing was run and the "7 tests pass" claim is unverified. Single reviewer, no fresh subagent. The identity service's real token format was not supplied.

INPUTS LEDGER:
- **Seen:** request.md, context.md, auth.py, test_auth.py.
- **Not seen: the identity service's actual public key or a sample production token.** This matters. Whether `PUBLIC_N` is the right key, and whether `iss`, `aud` and `exp` are issued in the shapes this code expects, cannot be settled without it.
- **Not seen: the caller.** I could not see how the API handles exceptions other than `InvalidToken`. This matters for F1.
- **Not seen: a test run log.** This matters a little. The test count (7) matches the file.

COVERAGE:
- **Checked:**
  - auth.py: `_b64d`, `_rsa_verify`, `verify_token`, and the key constants (leading digits of `PUBLIC_N` hand-compared against the PEM modulus).
  - test_auth.py: all 7 tests, each assessed by mutation reasoning.
- **Not checked:**
  - Full equality of `PUBLIC_N` with the PEM.
  - Runtime behaviour, since nothing was executed.
  - Caller exception handling.
  - The identity service's claim formats.

SEATS AND GATE: single reviewer (this session), no tools or subagents available. Sensitivity gate passed: a public key and test keys only, no personal or confidential data. No cross-vendor seats were requested.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (traced) | B | auth.py `verify_token`, `header.get("alg")` (first line after the try block) | The header is parsed before the signature check, but nothing checks that it is a JSON object. A header of `[]`, `1` or `"x"` makes `header.get` raise `AttributeError` outside the `try`. That breaks the docstring contract "return the claims … or raise InvalidToken". | An unauthenticated client sends a token whose header is `b64("[]")`. The caller catches only `InvalidToken`, so the request returns 500 instead of 401 and fills error logs. It still fails closed, so no access is granted. | Add `if not isinstance(header, dict): raise InvalidToken("malformed token")` inside the try. Do the same for `claims` for symmetry. Repro: `verify_token(b64(b"[]") + "." + b64(b"{}") + ".AA")`. Expected `InvalidToken`; observed `AttributeError`. | a Y, b Y, c N, d N |
| F2 | Medium | PROBABLE | B | auth.py `PUBLIC_KEY_PEM` / `PUBLIC_N` | There are two sources of truth for the key. The PEM is never used. Verification uses only the hand-copied decimal `PUBLIC_N`, and every test patches `PUBLIC_N`, so no test ties `PUBLIC_N` to the PEM or to the real issuer key. | During a rotation after a key compromise, someone replaces the PEM (the readable one) but not `PUBLIC_N`. All tests stay green because they mock N. Production keeps accepting tokens signed with the old, compromised key. | Derive N and E from the PEM at import time, or delete the PEM. Add a test asserting that `PUBLIC_N` matches the PEM modulus. Add a test that verifies one real token from the identity service against the unpatched constants. | a Y, b N, c Y, d N |
| F3 | Low | CONFIRMED (traced) | B | auth.py `_rsa_verify`, `pow(int.from_bytes(signature,…), e, n)` | It does not reject a signature integer `s ≥ n`, which RFC 8017 §8.2.2 / RSAVP1 requires. If `s` verifies, then `s+n` also verifies whenever it fits in k bytes. Since n's top byte is 0xb4, that holds for roughly 40% of signatures. | The same claims are presented under a second, different token string. There is no privilege gain, but any denylist or replay cache keyed on the raw token or signature is bypassed. | Add `if int.from_bytes(signature,"big") >= n: return False`. Repro: take a valid token, set `s' = s + n`, re-encode it as k bytes and verify. Expected `InvalidToken`; observed claims returned. | a Y, b Y, c N, d N |
| F4 | Low | CONFIRMED (traced) | B | auth.py `exp < (now …)` | It accepts a token when `now == exp`. RFC 7519 §4.1.4 says exp is the time "on or after which the JWT MUST NOT be accepted". | A token is accepted for one extra instant at expiry. Only integer `now` values hit this exactly. | Change to `exp <= now`. Repro: `verify_token(sign_rs256({**CLAIMS,"exp":1000}), now=1000)`. Expected `InvalidToken`; observed claims. | a Y, b Y, c N, d N |
| F5 | Low | CONFIRMED (traced) | B | test_auth.py `test_token_signed_by_another_key_is_refused`, `test_alg_none_is_refused`, `test_hs256_…` | Several tests pass for reasons other than the ones their names claim. The wrong-key test is rejected by the length check, because the 1024-bit test signature is 128 bytes and the production k is 256. `alg none` and HS256 tokens are also rejected by length. So deleting the `alg != "RS256"` check, or the EM comparison for the wrong-key case, leaves these tests green. The `time.time()` default path is never exercised either. | Someone later refactors the alg check or the comparison. These tests do not notice, and only `test_tampered_payload` guards the comparison. | Add a wrong-key test using a second key of the same size. Add an alg test with a valid RS256 signature but `alg: "RS512"` or `"none"` in the header (this header is signed, so the token is otherwise valid). Add one test with `now=None`. | a Y, b Y, c N, d N |

**Why F1 is not High:** under the severity rule, High needs (d), likely under realistic use. Only crafted input triggers F1, and it fails closed. If the caller turns unexpected exceptions into "allow", F1 becomes Critical (see S4).

## NEEDS VALIDATION
- **S1 (key match):** `PUBLIC_N` matches the PEM in its leading digits. The PEM modulus starts 0xb40a5f1b, which is about 2.2728×10^616, and `PUBLIC_N` starts 22728…. Full equality, and whether this is the identity service's current key, are unverified. Settled by comparing it with the modulus of the identity service's published key.
- **S2 (claim shapes):** the identity service may issue `aud` as an array (RFC 7519 permits this), or `exp` as a non-integer NumericDate, or a different `iss` string. Any of these makes the code reject every valid token (fail closed, total outage). Settled by one real production token.
- **S3 (rotation):** the code ignores `kid` and has one hardcoded key, so any rotation by the identity service needs a coordinated deploy. Settled by knowing the service's rotation policy.
- **S4 (caller):** whether the caller treats non-`InvalidToken` exceptions as deny. Settled by reading the middleware.
- **S5 (size limit):** token size is unbounded before `json.loads`. Whether an upstream request-size limit exists settles it.

## REFUTED
- **Algorithm confusion (HS256 signed with the PEM, `alg: none`).** Refuted: verification always uses RSA with a fixed key, and the header alg is checked as a strict string match.
- **Bleichenbacher-style forgery with loose PKCS#1 parsing.** Refuted: the whole expected EM is rebuilt and compared byte-for-byte with `compare_digest`. The DigestInfo prefix for SHA-256 is correct, and the padding length adds up to k.
- **Malformed input crashes inside the parse step.** Refuted: `None`, bytes, the wrong segment count, bad base64 and bad JSON all raise inside the `try` and become `InvalidToken`. Only the post-parse type issue in F1 escapes.
- **Unsigned claims are trusted.** Refuted: `exp`, `iss` and `aud` are read only after the signature check.

## WHAT HOLDS UP
- The core implements what was asked: RS256 signature verification, an expiry check and returned claims.
- The signature verification is the strict full-encoding comparison, it is constant-time, and it checks length.
- It fails closed on every path traced except F1's exception type.
- Checking `iss` and `aud` goes beyond the request but is a sound hardening step, subject to S2.
- `test_tampered_payload` does guard the EM comparison.

## UNVERIFIED CLAIMS
- "7 tests in test_auth.py pass." The count matches, but nothing was run. Confirm with `python -m unittest test_auth -v`.
- That `PUBLIC_N` and the PEM are the identity service's key (S1).

## QUESTIONS FOR THE AUTHOR
1. Can you share one real token from the identity service? It settles S1 and S2.
2. How does the reports API handle exceptions from `verify_token` other than `InvalidToken`? It decides F1's true severity.
3. Does the identity service rotate keys or use `kid`?

## DECISION-MAKER SUMMARY
The token check is cryptographically sound and fails closed; fix F1–F4 (all small) and add a test against one real production token before deploying. The main residual risk is not forgery but outage: if the hardcoded key or claim formats don't match what the identity service actually issues, every request is rejected (S1, S2). F2 means a future key rotation could silently leave the old key trusted.

## OWNER SUMMARY
The code that checks who may call the reports API is built correctly at its core and does not let forged tokens through. A few small fixes are needed: an odd input causes a server error instead of a clean rejection, and the key is stored twice in a way that could go stale. Before go-live, someone should check it against one real token from the login service, so it doesn't end up rejecting everyone.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "auth.py", "status": "seen", "matters": true},
    {"item": "test_auth.py", "status": "seen", "matters": true},
    {"item": "identity service public key / sample production token", "status": "not_seen", "matters": true},
    {"item": "reports API caller / exception middleware", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "same-session-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Public key and test keys only; no personal or confidential data."},
  "coverage": {
    "checked": [
      {"unit": "auth.py", "kind": "file"},
      {"unit": "auth.py:_b64d", "kind": "function"},
      {"unit": "auth.py:_rsa_verify", "kind": "function"},
      {"unit": "auth.py:verify_token", "kind": "function"},
      {"unit": "auth.py:PUBLIC_N/PUBLIC_KEY_PEM", "kind": "config"},
      {"unit": "test_auth.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "full equality of PUBLIC_N with PEM modulus", "reason": "no tools to decode"},
      {"unit": "test execution", "reason": "no tools"},
      {"unit": "caller exception handling", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:verify_token header.get(\"alg\")",
     "scenario": "An unauthenticated client sends a token whose header decodes to a JSON array or number; header.get raises AttributeError outside the try, so the caller sees an unexpected exception (500) instead of InvalidToken.",
     "fix": "Inside the try, raise InvalidToken unless header (and claims) is a dict.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "verify_token(b64(b'[]') + '.' + b64(b'{}') + '.AA'); expect InvalidToken, observe AttributeError."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "PROBABLE", "track": "B",
     "location": "auth.py:PUBLIC_KEY_PEM / PUBLIC_N",
     "scenario": "The PEM is unused and every test patches PUBLIC_N; a rotation that updates only the PEM leaves the old, possibly compromised key trusted while all tests pass.",
     "fix": "Derive N/E from the PEM (or delete it); add a test that PUBLIC_N matches the PEM and one test verifying a real issuer token with unpatched constants.",
     "answers": {"a": true, "b": false, "c": true, "d": false},
     "reproduction": "Change the PEM to a different key without touching PUBLIC_N; run test_auth.py; all 7 tests still pass."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:_rsa_verify pow(int.from_bytes(signature, 'big'), e, n)",
     "scenario": "A signature integer s >= n is not rejected, so s+n (when it fits in k bytes) also verifies, giving a second valid token string that bypasses denylists keyed on the raw token.",
     "fix": "Return False if int.from_bytes(signature, 'big') >= n.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Take a valid token, set s' = s + n, re-encode to k bytes, verify; expect InvalidToken, observe claims returned."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:verify_token exp < now",
     "scenario": "A token is accepted at now == exp although RFC 7519 4.1.4 says it must not be accepted on or after exp.",
     "fix": "Use exp <= now.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "verify_token(sign_rs256({**CLAIMS, 'exp': 1000}), now=1000); expect InvalidToken, observe claims."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_auth.py:test_token_signed_by_another_key_is_refused, test_alg_none_is_refused, test_hs256_signed_with_the_public_key_is_refused",
     "scenario": "These tests are satisfied by the signature-length check, so removing the alg check (or the EM comparison for the wrong-key case) leaves them green; the time.time() path is never exercised.",
     "fix": "Use a same-size second key for the wrong-key test; add a validly RS256-signed token whose header says alg RS512 or none; add a test with now=None.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "In a scratch copy delete the alg != 'RS256' check; run the tests; all 7 still pass."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py:PUBLIC_N",
     "suspicion": "PUBLIC_N may not equal the PEM modulus or the identity service's current key (leading digits match).",
     "unresolved_fact": "The modulus of the identity service's published key compared digit-for-digit with PUBLIC_N."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "auth.py:verify_token iss/aud/exp checks",
     "suspicion": "aud issued as an array, exp as a non-integer, or a different iss string would reject every valid token.",
     "unresolved_fact": "The claim shapes in one real production token."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "auth.py:verify_token (kid ignored)",
     "suspicion": "A single hardcoded key breaks on identity-service key rotation.",
     "unresolved_fact": "The identity service's key rotation policy and use of kid."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "caller of verify_token (not supplied)",
     "suspicion": "If the caller treats non-InvalidToken exceptions as allow, F1 becomes an auth bypass.",
     "unresolved_fact": "The caller's exception handling."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "auth.py:verify_token json.loads",
     "suspicion": "Unbounded token size is parsed before any authentication.",
     "unresolved_fact": "Whether an upstream request-size limit exists."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Algorithm confusion via HS256 with the public key or alg none.", "evidence": "Verification always uses RSA with a fixed key, and the header alg must equal 'RS256' exactly."},
    {"id": "C2", "candidate": "Bleichenbacher-style forgery through loose PKCS#1 v1.5 parsing.", "evidence": "_rsa_verify rebuilds the full expected EM and compares all k bytes with hmac.compare_digest; the SHA-256 DigestInfo prefix and padding length are correct."},
    {"id": "C3", "candidate": "Claims are trusted before signature verification.", "evidence": "exp, iss and aud are read only after _rsa_verify returns True."}
  ]
}
```