**Same-context review, no tools.** No subagent or code execution was available, so I read and traced the code by hand. Nothing below was run. Re-run with tools before relying on this for production.

**VERDICT: SHIP WITH FIXES.** The core verification is sound: the algorithm is pinned, the whole PKCS#1 v1.5 encoded message is compared, and expiry, issuer and audience are enforced. There are no High or Critical findings, but two Medium issues and one unverified key-equivalence fact should be settled before production.

**CONFIDENCE: medium.** I could not run the 7 tests or check that `PUBLIC_N` is the modulus of `PUBLIC_KEY_PEM`. The identity service's token format (`aud` shape, `exp` type) was not supplied.

**INPUTS LEDGER:**
- Seen: request.md, context.md, auth.py, test_auth.py.
- Not seen, and it matters:
  - The identity service's token format and key-rotation practice. This decides the `aud`/`exp` compatibility and F2.
  - The calling code in the reports API, which decides how non-`InvalidToken` exceptions are handled (F1).
  - Test run output. "7 tests pass" is asserted, not seen.

**COVERAGE:**
- Checked:
  - `auth.py`: `_b64d`, `_rsa_verify`, `verify_token`, constants.
  - `test_auth.py`: all 7 tests, `sign_rs256`, `forge`.
- Not checked:
  - The PEM-to-`PUBLIC_N` numeric equivalence (needs a tool).
  - Callers.
  - Test execution and mutation runs.

**SEATS AND GATE:** One same-context reviewer. No cross-vendor seats: none were available and none were requested. The work contains only a public key and a test key, so it is not sensitive.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (traced) | B | auth.py `verify_token`, `header.get("alg")` after the try block | The header is assumed to be a JSON object. A valid-JSON non-object header (`[]`, `null`, `1`, `"x"`) raises `AttributeError` outside the try, so the documented contract "raise InvalidToken" is broken. | An unauthenticated caller sends a token whose header decodes to `[]`. `verify_token` raises `AttributeError` instead of `InvalidToken`. A caller that catches only `InvalidToken` returns 500, and anonymous requests can spam error logs and alerts. Access is still refused. | Inside the try, add `if not isinstance(header, dict) or not isinstance(claims, dict): raise InvalidToken`. Repro: `verify_token(b64(b"[]")+"."+b64(b"{}")+".AA")`. Expected `InvalidToken`; observed `AttributeError: 'list' object has no attribute 'get'`. | a Y, b Y, c N, d N |
| F2 | Medium | CONFIRMED (read) | B | auth.py `PUBLIC_KEY_PEM` vs `PUBLIC_N`/`PUBLIC_E`; test_auth.py `setUp` | `PUBLIC_KEY_PEM` is never used for verification. The key actually used is a separately hardcoded integer, so two copies of the key can drift. Every test patches `PUBLIC_N`, so no test ties the production integer to the PEM. | The identity service rotates its key, for example after a compromise. Someone updates the PEM block, which is the obvious thing to edit, but not `PUBLIC_N`. Tokens signed with the old, compromised private key keep verifying, and no test fails. | Derive n and e from the PEM at import time, or delete the PEM and keep one source. Add a test asserting the PEM modulus equals `PUBLIC_N`. Repro: replace the PEM with a different key and run the tests. All 7 still pass. | a Y, b Y, c Y, d N |
| F3 | Low | CONFIRMED (traced) | B | test_auth.py `test_alg_none_is_refused`, `test_hs256_signed_with_the_public_key_is_refused` | The alg-confusion tests pass for the wrong reason. Both forged signatures (0 and 32 bytes) fail the `len(signature) != k` check in `_rsa_verify`, so deleting the `alg != "RS256"` check leaves both tests green. | A later refactor drops or loosens the alg check, for example to accept PS256 or "rs256". The tests do not catch it. | Add a test that sends a correctly RS256-signed body with header `alg: HS256` (or `none`) and expects refusal from the alg check itself. Mutation: delete the alg check and observe that the current 7 tests still pass. | a Y, b Y, c N, d N |
| F4 | Low | CONFIRMED (traced) | B | auth.py `_rsa_verify` | A signature integer s ≥ n is not rejected, which RFC 8017 §8.2.2 requires. Because `pow` reduces mod n, s+n (when it fits in k bytes) is a second valid signature string for the same token. This does not allow forgery. | Malleability: a denylist or replay cache keyed on the full token string or signature misses the s+n variant of a revoked token. | Add `if int.from_bytes(signature,"big") >= n: return False`. Repro: take a valid token, set s' = s+n (if < 2^(8k)), re-encode, and observe it is accepted. | a Y, b Y, c N, d N |
| F5 | Low | CONFIRMED (read) | B | auth.py `verify_token` header handling | The `crit` header parameter is ignored. RFC 7515 §4.1.11 requires rejecting tokens whose `crit` names extensions the verifier does not understand. | The identity service starts marking a restriction as critical. This verifier accepts those tokens anyway and ignores the restriction. | Reject any header containing `crit`. Repro: sign a token with `"crit":["x"]` and observe it is accepted. | a Y, b Y, c N, d N |

## NEEDS VALIDATION
- **S1:** Is `PUBLIC_N` exactly the modulus in `PUBLIC_KEY_PEM`, with exponent 65537? A rough check is consistent: the PEM modulus starts with 0xb4, giving ≈2.273×10^616 for 2048 bits, and `PUBLIC_N` starts with 22728… To settle it, parse the PEM with `cryptography` and compare. This is the single fact that decides whether production verification uses the right key.
- **S2:** Does the identity service emit `aud` as a string or an array? RFC 7519 allows an array, and `claims.get("aud") != AUDIENCE` would reject every array-form token. This fails closed, but it would be an outage.
- **S3:** Does the service ever emit a fractional `exp`? `isinstance(exp, int)` rejects floats, which also fails closed.
- **S4:** Do the 7 tests actually pass, and does each go red under a targeted mutation? Not run. The F3 case is shown by tracing only.
- **S5:** How do callers handle exceptions other than `InvalidToken`? This settles F1's real impact.

## REFUTED
- **Algorithm confusion (`none` or HS256 with the public key as HMAC secret):** refuted. `alg` is pinned to RS256 and no HMAC path exists.
- **Lenient PKCS#1 parsing (Bleichenbacher-style forgery with e=65537 or garbage after the hash):** refuted. `_rsa_verify` builds the full expected encoded message and compares it in constant time.
- **Missing or boolean `exp` accepted:** refuted. A missing `exp` fails `isinstance`, and `True` is 1, which is less than `now`.
- **Malformed input crashes the parser:** refuted for `None`, bytes, wrong segment count, bad base64 and huge integers. All raise inside the try and become `InvalidToken`. The one exception is non-object JSON (F1).
- **Signature covers re-normalized base64:** refuted. The signature is checked over the raw `head_b64.body_b64` strings.

## WHAT HOLDS UP
- RS256 verification is a correct, full-encoded-message comparison with a length check.
- `alg` is pinned, `exp` is required and enforced, and `iss`/`aud` are enforced (both beyond the request, and appropriate).
- Header-supplied key material (`kid`, `jku`, `x5u`, `jwk`) is not honored.
- The tests cover the valid path, tampering, a wrong key, expiry and issuer/audience.

## UNVERIFIED CLAIMS
- "7 tests in test_auth.py pass": run `python -m unittest test_auth`.
- The production key is correct: S1.

## QUESTIONS FOR THE AUTHOR
1. Is `PUBLIC_N` derived from the PEM, and how will key rotation be handled?
2. What `aud` and `exp` formats does the identity service emit?
3. How do callers map non-`InvalidToken` exceptions?

## DECISION-MAKER SUMMARY
The signature check is correct and resists the common JWT forgeries, so nothing here lets an attacker in today. Before production:
- Confirm the hardcoded key number matches the published key, and make the PEM the only source of the key (F2).
- Catch non-object headers (F1).
- Confirm the `aud` format (S2).

If you proceed as is, the main risks are a key rotation that silently keeps trusting an old key, and an outage if the identity service sends `aud` as a list.

## OWNER SUMMARY
The code that checks login tokens for the reports service is built correctly and blocks the usual ways of faking a token. The public key is stored twice in two forms, and only one is actually used, so a future key change could quietly leave the old key trusted. A few small hardening fixes and one confirmation from the identity team are needed before launch.

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
    {"item": "identity service token format and key rotation practice", "status": "not_seen", "matters": true},
    {"item": "reports API caller code", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Only a public key and a test key; no personal or confidential data."},
  "coverage": {
    "checked": [
      {"unit": "auth.py", "kind": "file"},
      {"unit": "auth.py:_b64d", "kind": "function"},
      {"unit": "auth.py:_rsa_verify", "kind": "function"},
      {"unit": "auth.py:verify_token", "kind": "function"},
      {"unit": "test_auth.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "PUBLIC_KEY_PEM vs PUBLIC_N numeric equality", "reason": "no tools to parse the PEM"},
      {"unit": "test execution and mutation runs", "reason": "no tools"},
      {"unit": "callers of verify_token", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:verify_token header.get(\"alg\") (outside the try block)",
     "scenario": "An unauthenticated token whose header decodes to [] or null makes verify_token raise AttributeError instead of InvalidToken; callers catching only InvalidToken return 500.",
     "fix": "Inside the try, raise InvalidToken unless header and claims are dicts.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "verify_token(b64(b'[]') + '.' + b64(b'{}') + '.AA'); expect InvalidToken, observe AttributeError."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:PUBLIC_KEY_PEM / PUBLIC_N; test_auth.py:setUp",
     "scenario": "After a key rotation that updates only the unused PEM, tokens signed with the old (possibly compromised) private key still verify, and no test fails because every test patches PUBLIC_N.",
     "fix": "Derive n and e from the PEM at import (single source) and add a test asserting the PEM modulus equals PUBLIC_N.",
     "answers": {"a": true, "b": true, "c": true, "d": false},
     "reproduction": "Replace PUBLIC_KEY_PEM with a different key and run the tests; all 7 still pass."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_auth.py:test_alg_none_is_refused, test_hs256_signed_with_the_public_key_is_refused",
     "scenario": "Removing the alg != RS256 check leaves both tests green, because the forged signatures fail the length check instead, so a regression in the alg pin goes undetected.",
     "fix": "Add a test with a valid RS256 signature but header alg HS256 or none, expecting refusal.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Delete the alg check in verify_token; the current tests still pass."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:_rsa_verify",
     "scenario": "A signature integer s+n (when it fits in k bytes) also verifies, so a denylist or replay cache keyed on the token string misses the variant.",
     "fix": "Reject int.from_bytes(signature, 'big') >= n.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Re-encode a valid token's signature as s+n (< 2^(8k)); it is accepted."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:verify_token header handling",
     "scenario": "A token whose header carries crit with an unknown extension is accepted, contrary to RFC 7515 section 4.1.11.",
     "fix": "Reject any header containing crit.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Sign a token whose header contains \"crit\": [\"x\"]; it is accepted."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py:PUBLIC_N",
     "suspicion": "The hardcoded modulus may not match the PEM key.",
     "unresolved_fact": "Whether the PEM's parsed modulus equals PUBLIC_N; leading digits are consistent."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "auth.py:verify_token aud check",
     "suspicion": "aud emitted as an array would reject every valid token.",
     "unresolved_fact": "Whether the identity service emits aud as a string or an array."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "auth.py:verify_token exp check",
     "suspicion": "A fractional exp would be rejected.",
     "unresolved_fact": "Whether the identity service ever emits a non-integer exp."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "test_auth.py",
     "suspicion": "The claimed 7 passing tests are unverified, and their mutation sensitivity is unknown beyond F3.",
     "unresolved_fact": "Output of running the suite, plus targeted mutations."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "reports API callers",
     "suspicion": "Callers may mishandle non-InvalidToken exceptions.",
     "unresolved_fact": "How callers map exceptions from verify_token."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Algorithm confusion via none or HS256 with the public key.", "evidence": "alg is pinned to RS256 and no HMAC path exists."},
    {"id": "C2", "candidate": "Lenient PKCS#1 v1.5 parsing enables forgery.", "evidence": "_rsa_verify compares the full expected encoded message with hmac.compare_digest."},
    {"id": "C3", "candidate": "A missing or boolean exp is accepted.", "evidence": "isinstance(exp, int) rejects a missing exp; True equals 1, which is below now."},
    {"id": "C4", "candidate": "Malformed tokens crash outside InvalidToken.", "evidence": "None, bytes, bad segment counts, bad base64 and oversized ints all raise inside the try; only non-object JSON escapes (F1)."}
  ]
}
```