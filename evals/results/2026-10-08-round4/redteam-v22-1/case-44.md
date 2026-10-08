VERDICT: SHIP WITH FIXES. The core verification is sound: RS256 is pinned, the full PKCS#1 v1.5 encoding is compared, and expiry, issuer and audience are checked. Three things should be fixed or confirmed before production: malformed headers escape `InvalidToken`, no test exercises the production key, and nothing shows the hardcoded modulus is the identity service's real key.

CONFIDENCE: medium. No tools were available, so nothing was run and all findings come from reading and tracing the code. No fresh subagent or second seat was available. I could not check the production key against the identity service, and could not compute the full PEM-to-`PUBLIC_N` match.

INPUTS LEDGER:
- Seen: `request.md`, `context.md`, `auth.py`, `test_auth.py`.
- Not seen: the identity service's published key or JWKS, which matters because it is the only way to know `PUBLIC_N` is right.
- Not seen: a sample real token, which matters for the `aud` array and float `exp` formats.
- Not seen: the caller that handles `InvalidToken`, which matters for how much F1 hurts.
- Not seen: the test run output. "7 tests pass" is unverified, though I count 7 test methods.

COVERAGE:
- Checked: `auth.py` (`_b64d`, `_rsa_verify`, `verify_token`, key constants) and `test_auth.py` (all 7 tests, `sign_rs256`, `forge`).
- Not checked: whether the full `PUBLIC_N` equals the PEM modulus. The leading bytes are consistent: PEM modulus `0xb40a5f…` gives about 2.2728e616, matching `PUBLIC_N`'s leading digits. The rest needs a tool.
- Not checked: the API layer that calls `verify_token`.

SEATS AND GATE: same-context single reviewer, with no subagent tool. The sensitivity gate passed: the work holds a public key only, no secrets or personal data. No cross-vendor seats were run.

FINDINGS:

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (trace) | B | auth.py `verify_token`, `header.get("alg")` (outside the `try`) | A header that decodes to valid JSON but is not an object (`[]`, `null`, `"x"`, `1`) raises `AttributeError`, not `InvalidToken`. | An unauthenticated caller sends such a token. If the API maps only `InvalidToken` to 401, the request becomes a 500 with a stack trace. If a caller has a broad `except` with a permissive default, auth behaviour becomes undefined. | Inside the `try`, add `if not isinstance(header, dict) or not isinstance(claims, dict): raise ValueError`. Repro: `verify_token(b64(b"[]")+"."+b64(b"{}")+".AA")` should raise `InvalidToken` but raises `AttributeError`. | a✓ b✓ c✗ d✗ |
| F2 | Medium | CONFIRMED | B | test_auth.py `setUp` (patches `PUBLIC_N/E` for every test); auth.py `PUBLIC_KEY_PEM` vs `PUBLIC_N` | The key exists twice, as PEM and as a decimal modulus. The PEM is never used for verification, only by the HS256 test. Every test swaps in a test key, so no test proves the production key verifies a real identity-service token or that `PUBLIC_N` matches the PEM. | `PUBLIC_N` is mistyped, stale after rotation, or diverges from the PEM. All 7 tests still pass. In production every real token is rejected, or tokens signed by whoever holds the wrong key are accepted. | Derive `n, e` from the PEM at import (e.g. `cryptography`'s `load_pem_public_key(...).public_numbers()`), or add a test asserting they match. Add a known-answer test with a real token from the identity service against the unpatched key. Repro: change the last digit of `PUBLIC_N`; all 7 tests still pass. | a✓ b✓ c✗ d✗ |
| F3 | Low | CONFIRMED (trace) | B | test_auth.py `test_alg_none_is_refused`, `test_hs256_signed_with_the_public_key_is_refused` | Neither test guards the `alg != "RS256"` check. The forged signatures are 0 and 32 bytes, so `_rsa_verify`'s length check rejects them anyway. | Someone removes or loosens the `alg` check, for example to accept `RS384` without hashing accordingly. Both tests stay green. | Add a test with a header of `alg: "HS256"` or `"none"` that carries a valid RS256 signature over that header, so only the `alg` check can reject it. Mutation to confirm: delete the `alg` check in a scratch copy; both current tests still pass. | a✓ b✓ c✗ d✗ |
| F4 | Low | CONFIRMED | B | auth.py `exp < (now …)` | The token is accepted at the exact second `exp`. RFC 7519 §4.1.4 says it must not be accepted "on or after" `exp`. | A token is replayed in its final second. The harm is negligible. | Use `exp <= now`, and add a boundary test with `now == exp`. | a✓ b✓ c✗ d✗ |
| F5 | Low | CONFIRMED (trace) | B | auth.py `_rsa_verify` | It does not reject a signature integer ≥ n (RFC 8017 §5.2.2 / §8.2.2 step 2). `s` and `s+n` both verify when `s+n < 2^(8k)`, so one token has two valid string forms. This is not a forgery. | A future denylist or replay cache keyed on the raw token string is bypassed by the alternate encoding. | After decoding, add `if int.from_bytes(signature,"big") >= n: return False`. | a✓ b✓ c✗ d✗ |

NEEDS VALIDATION:
- **S1: production key.** It is unknown whether `PUBLIC_N`/`PUBLIC_E` are the identity service's current signing key and equal to the PEM's modulus. Settle it by comparing against the service's JWKS or published key and computing the PEM modulus.
- **S2: `aud` as an array.** It is unknown whether the identity service emits `aud` as an array (`["reports-api"]`), which RFC 7519 allows. If it does, every real token is rejected. Settle it by inspecting a real token.
- **S3: float `exp`.** It is unknown whether `exp` is ever a non-integer NumericDate. `isinstance(exp, int)` rejects floats. Settle it with the identity service's token spec.
- **S4: key rotation.** It is unknown whether the identity service rotates keys or uses `kid`. A single hardcoded key means every rotation is an outage until the code is redeployed. Settle it with the identity service's rotation policy.
- **S5: `nbf`.** It is unknown whether the service sets `nbf`. It is not checked, and the request did not require it. Settle it with the token spec.

REFUTED:
- **alg-confusion attacks (`none`, or HS256 with the public key).** Refuted: any `alg` other than `RS256` is rejected, and only RSA verification exists in the code.
- **Bleichenbacher-style lenient PKCS#1 parsing forgery.** Refuted: the entire encoded message, including the DigestInfo prefix, is rebuilt and compared with `hmac.compare_digest`. The signature length is checked and e = 65537.
- **Lenient base64 lets a decoded payload differ from what was signed.** Refuted: the signature covers the raw `head_b64.body_b64` string, so any change in the string breaks the signature.
- **A non-string or wrongly segmented token crashes the verifier.** Refuted: `split` and unpacking happen inside the `try` and are converted to `InvalidToken`.

WHAT HOLDS UP:
- The PKCS#1 v1.5 SHA-256 verification is strict and constant-time compared.
- `alg` is pinned before any key use.
- Expiry is required, typed and checked.
- Issuer and audience checks are a correct addition beyond the request.
- The tampered-payload and wrong-key tests do exercise the signature path.
- There are 7 test methods, matching the context.

UNVERIFIED CLAIMS:
- "7 tests pass": run `python -m unittest test_auth`.
- The key provenance (S1): compare against the identity service's published key.

QUESTIONS FOR THE AUTHOR:
1. Where did `PUBLIC_N` come from, and does it match the PEM and the identity service's current key?
2. Does the identity service emit `aud` as a string or an array, and `exp` as an int or a float?
3. Does the service rotate keys, and how will this code learn the new one?
4. How does the API handle exceptions from `verify_token` other than `InvalidToken`?

DECISION-MAKER SUMMARY: The signature logic is correct, and the common JWT attacks (alg none, HS256 confusion, lenient padding) are blocked. Before production, confirm the hardcoded key is the identity service's real key (S1, F2), confirm the `aud` format (S2), and make malformed headers raise `InvalidToken` (F1). Proceeding without that risks either rejecting every real user or a test suite that cannot detect a wrong key.

OWNER SUMMARY: The code that checks login tokens is built correctly and blocks the well-known tricks attackers use. Nobody has yet confirmed that the key built into it is the identity service's real key, and the tests would not notice if it were wrong. A few small fixes are also needed so that malformed requests fail cleanly instead of crashing.

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
    {"item": "identity service public key / JWKS", "status": "not_seen", "matters": true},
    {"item": "sample real token (aud/exp format)", "status": "not_seen", "matters": true},
    {"item": "API caller of verify_token", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Public key only; no secrets or personal data."},
  "coverage": {
    "checked": [
      {"unit": "auth.py", "kind": "file"},
      {"unit": "auth.py:_b64d", "kind": "function"},
      {"unit": "auth.py:_rsa_verify", "kind": "function"},
      {"unit": "auth.py:verify_token", "kind": "function"},
      {"unit": "test_auth.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "PUBLIC_N equals PEM modulus (beyond leading digits)", "reason": "no tools to compute"},
      {"unit": "API layer calling verify_token", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:verify_token header.get(\"alg\")",
     "scenario": "A header that decodes to a JSON array, null, string or number raises AttributeError outside the try, escaping InvalidToken; callers catching only InvalidToken return 500 or behave undefined.",
     "fix": "Inside the try, require isinstance(header, dict) and isinstance(claims, dict); otherwise raise.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "verify_token(b64(b'[]') + '.' + b64(b'{}') + '.AA'): expect InvalidToken, observe AttributeError."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_auth.py:setUp; auth.py:PUBLIC_KEY_PEM/PUBLIC_N",
     "scenario": "The key is stored twice and every test patches in a test key, so a wrong or stale PUBLIC_N passes all 7 tests and production rejects all real tokens or trusts the wrong key.",
     "fix": "Derive n and e from the PEM at import, or assert they match in a test; add a known-answer test with a real identity-service token against the unpatched key.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Change the last digit of PUBLIC_N; all 7 tests still pass."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_auth.py:test_alg_none_is_refused, test_hs256_signed_with_the_public_key_is_refused",
     "scenario": "The forged signatures fail the length check anyway, so removing the alg check leaves both tests green.",
     "fix": "Add a test whose header has alg HS256 or none but carries a valid RS256 signature over that header.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "In a scratch copy, delete the alg check; both tests still pass."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:verify_token exp < now",
     "scenario": "A token is accepted at now == exp, contrary to RFC 7519 4.1.4 ('on or after').",
     "fix": "Use exp <= now and add a boundary test.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "verify_token(sign_rs256({**CLAIMS, 'exp': 1000}), now=1000): expect InvalidToken, observe claims returned."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:_rsa_verify",
     "scenario": "A signature integer >= n is not rejected (RFC 8017 8.2.2), so s+n also verifies; a raw-token denylist or replay cache can be bypassed with the alternate encoding.",
     "fix": "Reject when int.from_bytes(signature, 'big') >= n.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Re-encode a valid signature as s+n (when s+n < 2^(8k)); the token still verifies."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py:PUBLIC_N",
     "suspicion": "The hardcoded modulus may not be the identity service's current key or may not equal the PEM modulus.",
     "unresolved_fact": "Comparison of PUBLIC_N with the PEM modulus and the identity service's published key."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "auth.py:verify_token aud check",
     "suspicion": "An aud sent as an array would cause every real token to be rejected.",
     "unresolved_fact": "Whether the identity service emits aud as a string or an array."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "auth.py:verify_token isinstance(exp, int)",
     "suspicion": "A non-integer NumericDate exp would be rejected.",
     "unresolved_fact": "Whether exp is ever a float in issued tokens."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "auth.py:PUBLIC_N/PUBLIC_E",
     "suspicion": "A single hardcoded key causes an outage on key rotation.",
     "unresolved_fact": "The identity service's key rotation and kid policy."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "auth.py:verify_token",
     "suspicion": "nbf is not checked.",
     "unresolved_fact": "Whether the identity service sets nbf."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "alg none or HS256-with-public-key confusion is accepted.",
     "evidence": "verify_token rejects any alg other than RS256 before verification; only RSA verification exists."},
    {"id": "C2", "candidate": "Lenient PKCS#1 v1.5 parsing allows signature forgery.",
     "evidence": "_rsa_verify rebuilds the full encoded message and compares it with hmac.compare_digest; the length is checked and e = 65537."},
    {"id": "C3", "candidate": "Lenient base64 decoding lets the decoded payload differ from the signed bytes.",
     "evidence": "The signature covers the raw head_b64.body_b64 string."},
    {"id": "C4", "candidate": "A non-string or wrongly segmented token crashes the verifier.",
     "evidence": "split and unpacking are inside the try and converted to InvalidToken."}
  ]
}
```