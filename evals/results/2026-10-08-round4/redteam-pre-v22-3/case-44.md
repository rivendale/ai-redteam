VERDICT: **SHIP WITH FIXES**. The signature check holds up: it verifies the full PKCS#1 v1.5 encoding, so token forgery is closed off. A malformed header can still crash the function with the wrong exception, the issuer and audience handling may not match what the real identity service sends, and the tests don't prove the alg-confusion properties they are named for.

CONFIDENCE: **medium**. Limits: I had no tools, so nothing was executed and every judgement below comes from reading the code. One reviewer ran with no fresh-instance or cross-vendor seats; the work was not written in this conversation, so the anchoring risk is lower. The identity service's real token format and the calling code were not supplied.

INPUTS LEDGER:
- **Seen:** request.md, context.md, auth.py, test_auth.py.
- **Not seen: the caller of `verify_token`.** This matters, because it decides how an uncaught non-`InvalidToken` exception is handled (finding 1).
- **Not seen: a real token or the token spec from the identity service.** This matters for the `iss` value, `aud` as a string or an array, and `exp` as an integer or a float (findings 2 and 3).
- **Not seen: the identity service's published key or JWKS.** This matters for whether `PUBLIC_N` is the right key. I partly checked it by hand (see What holds up).
- **Not seen: CI output showing "7 tests pass".** This matters little, because the count of 7 matches the file.

SEATS AND GATE: one local reviewer, with no subagent and no tools available. I checked for sensitive data and found none. The file contains a public key and a test-only RSA private exponent `D` in test_auth.py, which is a test fixture and not a production secret. No external seats were needed or used.

FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Medium | CONFIRMED (traced) | B | auth.py `header.get("alg")`, after the `try` block | The header is parsed before the signature is checked and is attacker-controlled. If it decodes to valid JSON that is not an object, `.get` raises `AttributeError` outside the `try`. | An unauthenticated caller sends the header `b64("[]")`. `verify_token` then raises `AttributeError` instead of `InvalidToken`. A caller that only catches `InvalidToken` returns a 500 and logs a stack trace on every hit, which gives an attacker cheap error-log noise and a confusing failure mode. This fails closed, so it is not a bypass. | Check `isinstance(header, dict) and isinstance(claims, dict)` inside the `try`, or raise `InvalidToken` when they are not. Add tests for headers of `[]`, `1` and `"x"`, and for a token with 2 or 4 parts. | Confirmed. The defender's point holds that this fails closed, which keeps it at Medium. |
| 2 | Medium | UNVERIFIED | B | auth.py `ISSUER = "https://id.example.test"`, `AUDIENCE` | The issuer is hardcoded to a `.test` (reserved) domain, and the request never specified an issuer or audience. `aud` is compared with `!=`, but RFC 7519 §4.1.3 allows `aud` to be an array. | In production the identity service puts its real URL in `iss`, or `"aud": ["reports-api"]`. Every valid token is then rejected and the reports API becomes unusable. This is an outage, not a breach. | Confirm the real `iss` and `aud` format with the identity service and load them from config. Accept `aud` when it is a string equal to `AUDIENCE` or a list containing it. Add a test that uses a real (or real-format) token from the service. | Not a High candidate. It stays UNVERIFIED until the service's token format is known. |
| 3 | Medium | CONFIRMED (structure) / PROBABLE (impact) | B | test_auth.py `test_alg_none_is_refused`, `test_hs256_..._refused`, `test_token_signed_by_another_key_is_refused` | **The alg tests don't test the alg check.** The forged signatures are 0 and 32 bytes long, so `_rsa_verify` rejects them at `len(signature) != k` whether or not the alg check exists. Deleting `if header.get("alg") != "RS256"` leaves both tests green. **The "another key" test doesn't test the RSA math.** The test key is about 1024-bit and the production key is 2048-bit, so that test also fails at the length check and never reaches the modular exponentiation or the comparison. | A later refactor breaks the alg pin, or makes the comparison accept a wrong key of the same size. All 7 tests still pass, so "7 tests pass" overstates what is guarded. | Assert on the error message or reason in each test. Add a test with a full-length (k-byte) garbage signature. Add a wrong-key test using a second key of the same size. Do a mutation check in a scratch copy: remove the alg check and confirm a test goes red. | Confirmed by reading the code: each rejection path can be traced to the length check. |
| 4 | Medium | CONFIRMED | B | auth.py `PUBLIC_KEY_PEM` and `PUBLIC_N` / `PUBLIC_E` | The key is hardcoded twice. The PEM is never used, and the code only uses `PUBLIC_N`. There is no `kid` handling or JWKS, so rotating the key needs a code deploy. | The identity service rotates its key, and all tokens fail until a deploy. Or someone updates only the PEM, the code keeps the old modulus, and the tests (which patch N) cannot notice. | Derive N and E from the PEM at import using a vetted library (`cryptography`), or fetch them from the service's JWKS keyed by `kid`. At minimum, add a test asserting that `PUBLIC_N` and `PUBLIC_E` match the parsed PEM. | Not a High candidate. |
| 5 | Low | CONFIRMED | B | auth.py `_rsa_verify`; `_b64d` | **Signatures are malleable in two ways.** First, the code does not reject a signature value `s ≥ n` (RFC 8017 §5.2.2 requires it to). Because n ≈ 0.70·2^2048, `s + n` often still fits in k bytes and verifies. Second, `urlsafe_b64decode` silently discards non-alphabet characters in the signature segment. | An attacker who holds one valid token can mint different token strings that carry the same claims. Any denylist, cache or replay check keyed on the raw token string can then be bypassed. This is not a forgery. | Reject when `int.from_bytes(sig) >= n`. Decode base64 strictly with `validate=True` after translating `-` and `_`. Key any denylist on `jti` and not on the token string. | n/a |
| 6 | Low | CONFIRMED | B | auth.py `exp < now` | `exp == now` is accepted, but RFC 7519 §4.1.4 says the current time must be *before* `exp`. A float `exp` (allowed for a NumericDate) is rejected. `nbf` is not checked, and there is no clock-skew leeway. | A token is accepted at the exact second it expires, which has negligible impact. Alternatively, an identity service that emits a float `exp` is rejected outright. | Use `exp <= now`. Accept `int` or `float` but not `bool`. Check `nbf` if the service sets it. | n/a |
| 7 | Low | PROBABLE | B | auth.py `verify_token` | There is no maximum token length, and the `crit` header is not rejected (RFC 7515 §4.1.11). | A multi-MB header is base64-decoded and parsed as JSON on every request before any authentication. | Cap the token length (for example 8 KB). Reject the token if `crit` is present. | n/a |

WHAT HOLDS UP
- **The RSA check itself.** The DigestInfo prefix `3031300d0609608648016503040201 0500 0420` is the correct SHA-256 one. `_rsa_verify` rebuilds the entire expected encoded message, padding included, and compares it in full rather than parsing it. That closes off the Bleichenbacher-style lax-parsing forgeries.
- **Signature-length check.** The signature length is checked against k.
- **Alg handling.** `alg` is pinned to `RS256`, and verification never dispatches on the header, so `none` and HS256-with-public-key confusion cannot succeed (the tests just don't prove it; see finding 3).
- **Signed input.** The signature covers the raw `head_b64.body_b64` string, which is correct.
- **Missing or non-integer `exp`.** These are rejected.
- **Malformed input.** Splitting and decoding errors on malformed input are wrapped. Non-string input (`None`, bytes) fails inside the `try` block.
- **Key consistency, partly checked.** I decoded the PEM by hand. It is a 2048-bit SPKI with e = `AQAB` = 65537, and the modulus begins with bytes `B4 0A 5F`. That gives n ≈ 0.7033·2^2048 ≈ 2.2729·10^616, which agrees with `PUBLIC_N`'s leading digits `22728…`. So `PUBLIC_N` very probably matches the PEM, but only the leading digits were checked.
- **Scope.** Checking `iss` and `aud` goes beyond the request, but it is sound practice and not drift.

UNVERIFIED CLAIMS
- **"7 tests pass."** To confirm, run `python -m unittest test_auth` and capture the output.
- **`PUBLIC_N` equals the PEM modulus, and the PEM is the identity service's current key.** To confirm, parse the PEM with `cryptography` and compare it with the service's published JWKS.
- **The real tokens' `iss`, `aud` shape and `exp` type.** To confirm, decode a real token issued by the identity service.

QUESTIONS FOR THE AUTHOR
1. Is `https://id.example.test` the production issuer? Does the service emit `aud` as a string or as an array?
2. What does the caller do with exceptions other than `InvalidToken`?
3. How does the identity service rotate its signing key, and does it publish a JWKS with `kid`?

DECISION-MAKER SUMMARY: Token forgery is blocked: the signature verification is sound and alg confusion is closed. Before production, fix the crash on a malformed header, confirm the issuer and audience values against real tokens, and fix the tests so they actually guard the alg pin. Shipping as is risks a full outage if the issuer or audience format is wrong, and leaves a refactor regression in the alg check undetectable by the tests.

OWNER SUMMARY: The new login-token check correctly stops people from faking tokens. A few things need tidying before it goes live. A garbled token can make it crash instead of cleanly saying no, and the expected sender name may not match what the real login service sends, which would lock everyone out. Some of the tests also look like they check safety features but would still pass if those features broke.

```json
{
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "caller of verify_token", "status": "not_seen", "matters": true},
    {"item": "real identity-service token / spec (iss, aud shape, exp type)", "status": "not_seen", "matters": true},
    {"item": "identity service JWKS / published key", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "public key and a test-only private exponent; no personal or confidential data"},
  "findings": [
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "auth.py verify_token: header.get(\"alg\") outside try",
      "scenario": "Unauthenticated header b64('[]') makes json.loads return a list; .get raises AttributeError instead of InvalidToken; caller returns 500 and logs a stack trace (fails closed).",
      "fix": "Require header and claims to be dicts inside the try, else raise InvalidToken; add tests for non-object headers and wrong part counts.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "B", "location": "auth.py ISSUER/AUDIENCE and the iss/aud comparison",
      "scenario": "The real service issues a non-.test iss or an array aud; every valid token is rejected and the API has an outage.",
      "fix": "Confirm values with the identity service and load them from config; accept aud as a string or as a list containing AUDIENCE; test with a real-format token.", "status": "unverified"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "test_auth.py alg-none, HS256 and other-key tests",
      "scenario": "All three are rejected by the signature-length check, so removing the alg pin or breaking the RSA compare leaves the tests green.",
      "fix": "Assert on the rejection reason; add a full-length garbage-signature test and a same-size wrong-key test; mutation-check in a scratch copy.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "auth.py PUBLIC_KEY_PEM and PUBLIC_N/PUBLIC_E",
      "scenario": "The key is duplicated and the PEM is unused; with no kid/JWKS, rotation needs a deploy, or the PEM and N drift apart unnoticed because the tests patch N.",
      "fix": "Derive N and E from the PEM, or fetch them from the JWKS by kid; add a test asserting N and E match the PEM.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "auth.py _rsa_verify (no s<n check); _b64d (lenient base64)",
      "scenario": "A holder of a valid token mints alternate token strings (s+n, or junk characters in the signature) with the same claims, bypassing denylists keyed on the token string.",
      "fix": "Reject signature int >= n; decode base64 strictly with validate=True; key denylists on jti.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "auth.py exp check",
      "scenario": "exp == now is accepted (RFC 7519 requires now < exp); a float exp is rejected; nbf is ignored.",
      "fix": "Use exp <= now; accept int or float but not bool; check nbf if issued.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "B", "location": "auth.py verify_token input handling",
      "scenario": "A multi-MB token is decoded and parsed before authentication; a crit header is ignored.",
      "fix": "Cap the token length; reject tokens with a crit header.", "status": "n/a"}
  ]
}
```