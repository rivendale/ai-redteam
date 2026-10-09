VERDICT: **REWORK.** `verify_token` accepts unsigned (`alg: none`) tokens and HS256 tokens keyed with the public key, so anyone can forge any identity against the reports API.

CONFIDENCE: **high** for the two Criticals, which follow directly from the supplied lines. It is medium overall, for three reasons:
- This was a same-context review: no fresh subagent and no tools were available, so there is some anchoring risk. Re-run it in a fresh session before relying on it for production.
- Nothing was executed. Findings are traced by reading the code, not run.
- Whether the hardcoded key is the real identity-service key is unverified.

INPUTS LEDGER:
- Seen: `request.md` (verbatim), `context.md`, `auth.py`, `test_auth.py`.
- Not seen: the identity service's published public key or JWKS. **Matters**, because the correctness of `PUBLIC_N`/`PUBLIC_E` depends on it.
- Not seen: the caller in the reports API, i.e. how it handles exceptions other than `InvalidToken`. **Matters** for F3.
- Not seen: the test run output. "3 tests pass" is asserted, not shown.
- Not seen: the identity service's token claims (`iss`, `aud`, `nbf`, `kid`). **Matters** for S2.

COVERAGE:
- Checked: `auth.py:_b64d`, `auth.py:_rsa_verify` (padding, DigestInfo, length check, comparison), `auth.py:verify_token` (every alg branch, the parse path, the expiry check), `auth.py:PUBLIC_KEY_PEM` / `PUBLIC_N` usage, and all 3 tests in `test_auth.py`, including what mutation each would catch.
- Not checked: that `PUBLIC_N` equals the modulus inside `PUBLIC_KEY_PEM` or the live service key (no tools), the API integration, and actual test execution.

SEATS AND GATE: Only this session reviewed the work. There was no subagent tool, and no cross-vendor seats were requested at standard depth. Sensitivity gate passed: the only key material is a public key and a test-only private key, with no personal or client data.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (traced) | B | `auth.py:53-54` `elif alg == "none": ok = True` | Unsigned tokens are accepted. | An attacker sends `base64url({"alg":"none"}) + "." + base64url({"sub":"admin","exp":9999999999}) + "."`. `split` yields an empty signature, `_b64d("")` returns `b""`, `ok = True`, and the claims are returned. Anyone can impersonate anyone. | Delete the branch and accept **only** `RS256`; reject every other `alg`. Repro test: build the token above and call `verify_token(tok, now=1000)`. Expect `InvalidToken`; current code returns the claims. | y/y/y/y |
| F2 | Critical | CONFIRMED (traced) | B | `auth.py:51-52` `hmac.new(PUBLIC_KEY_PEM.encode(), ...)` | This is classic algorithm confusion. HS256 is verified with the **public** key as the HMAC secret, and that key is in the source and published by the identity service. | An attacker sets header `{"alg":"HS256"}`, computes `HMAC-SHA256(PUBLIC_KEY_PEM_bytes, head.body)` and appends it. The token verifies with arbitrary claims. | Delete the branch, which the request never asked for. Repro test: sign `head.body` with `hmac.new(auth.PUBLIC_KEY_PEM.encode(), ..., sha256)` and expect `InvalidToken`; current code returns the claims. | y/y/y/y |
| F3 | Medium | CONFIRMED (traced) | B | `auth.py:48` `header.get`, `auth.py:59` `claims.get("exp", 0) < ...` | Well-formed JSON that is not an object, or a non-numeric `exp`, raises `AttributeError` or `TypeError` instead of `InvalidToken`. The header case happens **before** signature verification. | Unauthenticated header `W10` (`[]`) produces `AttributeError: 'list' object has no attribute 'get'`, which escapes the function. A caller that catches only `InvalidToken` returns a 500 instead of a 401. This fails closed, but it is noisy and lets anyone trigger error paths. | Inside the try block, require `isinstance(header, dict)` and `isinstance(claims, dict)`. Require `exp` to be an int or float (not bool) and raise `InvalidToken` otherwise. Repro: `verify_token(b64(b"[]")+"."+b64(b"{}")+".")`. Expect `InvalidToken`; observe `AttributeError`. | y/y/n/n |
| F4 | Medium | CONFIRMED | B | `test_auth.py` (all 3 tests) | The tests only exercise the RS256 path. Mutation check by reading: F1 and F2 are live in the code today and no test fails, so the suite cannot detect the most important defect class. `setUp` also patches out `PUBLIC_N`/`PUBLIC_E`, so the production key is never exercised. | A future change re-adding `none` or HS256 still passes CI, and "3 tests pass" is read as "verified". | Add negative tests for `alg: none`, HS256-with-public-key, unknown alg, a missing `alg`, a non-object header or body, a missing `exp`, and a wrong-key RS256 signature. Confirm each goes red against current `auth.py`; F1 and F2 should. | y/y/n/n |
| F5 | Low | CONFIRMED (traced) | B | `auth.py:35` `pow(int.from_bytes(signature), e, n)` | There is no check that signature integer `s < n`. When `s + n < 256^k`, `s + n` verifies as well. This is malleability, not forgery. | Two distinct signature strings verify for the same token. That breaks any downstream dedup or revocation keyed on the raw token string. | Reject when `int.from_bytes(signature) >= n` (RFC 8017 §8.2.2 step 2a). | y/y/n/n |

**Drift note:** the request asked for RS256 verification only. The HS256 and `none` branches are unrequested extras, and they are exactly where the Critical defects are.

## NEEDS VALIDATION
- **S1:** `PUBLIC_N`/`PUBLIC_E` may not match `PUBLIC_KEY_PEM` or the identity service's real key. The PEM is used only by the HS256 branch, never for RS256. **Unresolved fact:** decode the PEM's modulus and compare it to `PUBLIC_N` and the service's published key.
- **S2:** There are no `iss`/`aud` checks, so tokens the identity service issues for other services may be accepted by the reports API. The request did not ask for these checks. **Unresolved fact:** does the identity service issue tokens with the same key for other audiences?
- **S3:** The hardcoded single key has no `kid` or rotation support. **Unresolved fact:** does the identity service rotate keys, and on what schedule?

## REFUTED
- **Bleichenbacher-style e=3 / lax padding parse.** Refuted: `_rsa_verify` rebuilds the full expected encoding (`00 01 FF… 00 DigestInfo hash`) and compares the whole block with `hmac.compare_digest`, so no partial parse exists.
- **Wrong SHA-256 DigestInfo prefix.** Refuted: `3031300d060960864801650304020105000420` is the RFC 8017 SHA-256 prefix.
- **A missing `exp` never expires.** Refuted: `claims.get("exp", 0)` defaults to 0, which is `< now`, so the token is rejected as expired.
- **A non-string token crashes.** Refuted: `None.split` or `bytes.split(".")` raise inside the `try` and become `InvalidToken("malformed token")`.

## WHAT HOLDS UP
- The RS256 PKCS#1 v1.5 verification is correct: length check, full-block constant-time comparison, correct DigestInfo.
- The signing input uses the raw base64 segments, not the re-encoded JSON.
- The expiry check rejects missing and past `exp`.
- Malformed base64 and JSON are caught.
- `test_tampered_payload` would go red if the signature check were removed.

## UNVERIFIED CLAIMS
- "3 tests in test_auth.py pass." To confirm, run `python3 -m unittest test_auth` and check the output.
- That `PUBLIC_N` is the identity service's key. To confirm, compare against the published JWKS or PEM (S1).

## QUESTIONS FOR THE AUTHOR
1. Why were HS256 and `none` added? Does any real caller send them? If not, removing them settles F1 and F2.
2. Is `PUBLIC_N` taken from the identity service's current key, and from where?
3. Does the identity service issue tokens for other audiences with the same key?

## DECISION-MAKER SUMMARY
Do not ship. As written, anyone can mint a token for any user via `alg: none` or HS256-with-the-public-key. The fix is to delete two branches, accept only RS256, and add negative tests that prove it. Proceeding anyway means the reports API is effectively unauthenticated.

## OWNER SUMMARY
The new login check for the reports system can be fooled into accepting fake passes that anyone could make, so it is not safe to release yet. The fix is small: remove two options that were never requested and add tests proving fake passes are refused. A few smaller issues should be cleaned up at the same time.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "auth.py", "status": "seen", "matters": true},
    {"item": "test_auth.py", "status": "seen", "matters": true},
    {"item": "identity service published public key / JWKS", "status": "not_seen", "matters": true},
    {"item": "reports API caller of verify_token", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Only a public key and a test-only private key; no personal or client data."},
  "coverage": {
    "checked": [
      {"unit": "auth.py", "kind": "file"},
      {"unit": "auth.py:_b64d", "kind": "function"},
      {"unit": "auth.py:_rsa_verify", "kind": "function"},
      {"unit": "auth.py:verify_token", "kind": "function"},
      {"unit": "test_auth.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "auth.py:PUBLIC_N vs PUBLIC_KEY_PEM vs live identity-service key", "reason": "no tools; key source not supplied"},
      {"unit": "reports API integration", "reason": "not supplied"},
      {"unit": "test execution", "reason": "no tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:53-54",
     "scenario": "A token with header {\"alg\":\"none\"}, arbitrary claims and an empty signature is accepted, so anyone can impersonate any user.",
     "fix": "Remove the none branch; accept only alg == RS256 and reject everything else.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "verify_token(b64('{\"alg\":\"none\"}')+'.'+b64('{\"sub\":\"admin\",\"exp\":9999999999}')+'.', now=1000): expect InvalidToken, observe claims returned."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:51-52",
     "scenario": "An attacker signs head.body with HMAC-SHA256 keyed by the public PEM and sets alg HS256; the forged token verifies with arbitrary claims.",
     "fix": "Remove the HS256 branch; accept only RS256.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Sign head.body with hmac.new(auth.PUBLIC_KEY_PEM.encode(), msg, sha256) under header alg HS256: expect InvalidToken, observe claims returned."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:48, auth.py:59",
     "scenario": "A header or body that is valid JSON but not an object, or a non-numeric exp, raises AttributeError/TypeError instead of InvalidToken; the caller returns a 500, not a 401.",
     "fix": "Require dict header and claims and a numeric (non-bool) exp; raise InvalidToken otherwise.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "verify_token(b64(b'[]')+'.'+b64(b'{}')+'.'): expect InvalidToken, observe AttributeError."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_auth.py:T",
     "scenario": "No test covers alg none, HS256, an unknown alg or malformed structure; F1 and F2 are live and all 3 tests still pass, so CI cannot catch algorithm-confusion regressions.",
     "fix": "Add negative tests for none, HS256-with-public-key, unknown or missing alg, non-object header or body, missing exp and wrong-key RS256; confirm they fail on current code.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Add a test asserting InvalidToken for the alg none token in F1; it fails against current auth.py."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:35",
     "scenario": "A signature integer s >= n is not rejected, so s+n (when it fits in k bytes) also verifies; tokens are malleable, which breaks dedup or revocation keyed on the raw token.",
     "fix": "Reject when int.from_bytes(signature, 'big') >= n.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Take a valid test signature s; if s+N < 256**k, encode s+N as the signature: expect InvalidToken, observe claims returned."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py:8-19",
     "suspicion": "PUBLIC_N may not match PUBLIC_KEY_PEM or the identity service's live key; the PEM is used only by the HS256 branch.",
     "unresolved_fact": "The modulus decoded from the PEM and from the service's published key, compared to PUBLIC_N."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "auth.py:verify_token",
     "suspicion": "Without iss/aud checks, tokens issued for other services may be accepted.",
     "unresolved_fact": "Whether the identity service issues same-key tokens for other audiences."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "auth.py:18-19",
     "suspicion": "A hardcoded single key with no kid means rotation breaks auth until a redeploy.",
     "unresolved_fact": "The identity service's key rotation policy."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "PKCS#1 v1.5 padding is parsed leniently (Bleichenbacher e=3).", "evidence": "auth.py:37 compares the full reconstructed encoded block with hmac.compare_digest."},
    {"id": "R2", "candidate": "A missing exp never expires.", "evidence": "claims.get('exp', 0) defaults to 0 < now, which raises InvalidToken('expired')."},
    {"id": "R3", "candidate": "A non-string token crashes the function.", "evidence": "token.split raises inside the try block and is converted to InvalidToken('malformed token')."},
    {"id": "R4", "candidate": "The SHA-256 DigestInfo prefix is wrong.", "evidence": "3031300d060960864801650304020105000420 matches the RFC 8017 SHA-256 DigestInfo prefix."}
  ]
}
```