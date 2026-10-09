VERDICT: **SHIP WITH FIXES.** The core verification is sound: it compares the full PKCS#1 v1.5 encoded message, never picks the algorithm from the header, and checks the signature before trusting any claim. Two Medium issues should be fixed first, and the production key and issuer values need confirming before go-live.

CONFIDENCE: **medium.** I had no tools, so I could not run the tests, recompute `PUBLIC_N` from the PEM, or see the identity service's real key, issuer or audience. I am a separate reviewer and did not write this code, but I am the only reviewer.

**INPUTS LEDGER**
- Seen: the request, the context, `auth.py` and `test_auth.py`.
- Not seen:
  - The identity service's actual public key, `iss` and `aud` values, and token format. **This matters** for whether the code works in production at all.
  - The caller code that invokes `verify_token`. This matters for F1.
  - The output of the test run. "7 tests pass" is unverified.

**COVERAGE**
- Checked:
  - In `auth.py`: `_b64d`, `_rsa_verify`, `verify_token`, and the constants.
  - In `test_auth.py`: all 7 tests and the helpers `sign_rs256` and `forge`.
  - Hostile inputs traced: a header of `[]` or `null`, a token with 2 or 4 parts, non-ASCII input, deeply nested JSON, `alg: none`, HS256 signed with the public key, an empty or short signature, a signature value ≥ n, `exp` as a bool, a float, or equal to `now`, and `aud` as an array.
- Not checked: whether `PUBLIC_N` matches the PEM exactly, the caller and framework error handling, and the identity-service configuration.

**SEATS AND GATE**: Only a single local reviewer ran. No cross-vendor seats ran because none were requested or available. Sensitivity gate: not sensitive. The data is a public key plus a test-only private key, with no personal data.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (traced) | B | `auth.py` `verify_token`, the `header.get("alg")` line, which sits outside the `try` | Valid JSON that is not an object passes parsing, then `.get` raises `AttributeError` instead of `InvalidToken`. This breaks the docstring contract ("or raise InvalidToken"). | An unauthenticated caller sends `W10.e30.AA` (header `[]`) or `bnVsbA.e30.AA` (header `null`). The `AttributeError` escapes, so a caller that catches only `InvalidToken` returns a 500 with a stack trace instead of a 401. The failure is closed (no bypass), but it is an unhandled error on demand. | Inside the `try`, add `if not isinstance(header, dict) or not isinstance(claims, dict): raise ValueError`. Test: `assertRaises(auth.InvalidToken, auth.verify_token, "W10.e30.AA", now=1000)`. It currently raises `AttributeError`, which fails the test. | a✓ b✓ c✗ d✗. Legitimate clients never send this, and it fails closed. |
| F2 | Medium | CONFIRMED | B | `auth.py` `PUBLIC_KEY_PEM` vs `PUBLIC_N`/`PUBLIC_E`, and the `_rsa_verify(..., PUBLIC_N, PUBLIC_E)` call | The PEM is never parsed. Verification uses a separate hand-copied integer, so there are two sources of truth for the trust anchor, and the one that looks authoritative does nothing. | The identity key is rotated, perhaps after a compromise, and an engineer replaces the PEM block, which is the obvious thing to edit. `PUBLIC_N` is unchanged, so the API keeps accepting tokens signed by the old key and rejects all tokens signed by the new one. No test notices. | Derive `n` and `e` from the PEM at import time, or delete the PEM. Add a test that parses `PUBLIC_KEY_PEM` and asserts it equals `(PUBLIC_N, PUBLIC_E)`. That test fails as soon as the two drift. | a✓ b✓ c✗ (only conditionally a breach) d✗ |
| F3 | Low | CONFIRMED | B | `auth.py` `verify_token`, where `header` is used only for `alg` | The verifier has a single hardcoded key and ignores `kid`, with no JWKS or rotation path. | When the identity service rotates keys, every new token is rejected until a redeploy happens, causing an outage window. | Load keys from configuration or the identity service's JWKS, keyed by `kid`, and allowlist RS256 per key. | a✓ b✓ c✗ d✗ |
| F4 | Low | PROBABLE (traced, not run) | B | `test_auth.py`: `test_alg_none_is_refused`, `test_hs256_signed_with_the_public_key_is_refused`, `test_token_signed_by_another_key_is_refused` | These three tests pass for a reason other than the one their names state (details below the table). | A later refactor weakens either the alg check or the key-specific RSA check while the suite stays green. | Mutation tests in a scratch copy, described below the table. | a✓ b✗ c✗ d✗ |
| F5 | Low | CONFIRMED | B | `auth.py`, the line `exp < (now ...)` | A token is accepted at `exp == now`, but RFC 7519 §4.1.4 says the current time must be *before* `exp`. `nbf` is also ignored. | A token is usable for up to one extra second. A token with a future `nbf` is accepted early, if the issuer ever sets `nbf`. | Use `exp <= now`, and reject when `nbf > now` if `nbf` is present. Test: `exp=1000, now=1000` should be refused but is currently accepted. | a✓ b✓ c✗ d✗ |

**F4 detail.** Removing the `alg != "RS256"` check leaves all 7 tests green. The `none` signature is 0 bytes and the HS256 signature is 32 bytes, so both are rejected by the `len(signature) != k` check. The "another key" test switches from a 1024-bit test key to a 2048-bit production key, so it also fails only on length and never reaches the RSA arithmetic.

**F4 mutation tests.** Run these in a scratch copy:
1. Delete the alg check and expect a red test.
2. Make the "another key" test use a second key of the same size. Then mutate `_rsa_verify` to compare against the wrong key and expect a red test.

## NEEDS VALIDATION
- **S1: issuer and audience values.** `ISSUER = "https://id.example.test"` uses the reserved `.test` TLD from RFC 6761. The open question is whether the production identity service really issues `iss` with exactly this value and `aud = "reports-api"`. If it does not, every production token is rejected. Note that these checks go beyond the request, which asked only for signature and expiry. They are a good addition, but only if the values are right.
- **S2: does `PUBLIC_N` match the PEM and the identity service's current key?** By hand I estimated the leading digits of the PEM modulus (bytes `B4 0A 5F 1B…`, about 2.27280 × 10⁶¹⁶). They are consistent with `PUBLIC_N` (2.2728009…), but this is not a full check. To settle it, load the PEM with a crypto library and compare `n` exactly, then compare against the service's published JWKS.
- **S3: token format.** Does the identity service ever emit `aud` as an array (`["reports-api"]`), or `exp` as a non-integer NumericDate? Either form is valid under RFC 7519, and this code would reject all such tokens. The failure is closed, but it would cause an outage.
- **S4: test results.** "7 tests pass" was not run here. The count of 7 does match the file.
- **S5: caller error handling.** How do the callers handle exceptions other than `InvalidToken`? This determines whether F1 produces a 500 or something worse.

## REFUTED
- **Algorithm confusion (HS256 with the public key, or `alg: none`).** The algorithm is never selected from the header, and verification always uses fixed RSA parameters. A forged HMAC or empty signature fails the length and EM check.
- **PKCS#1 v1.5 signature-parsing forgery (Bleichenbacher 2006 style).** The code builds the complete expected EM (`00 01 FF… 00 DigestInfo hash`) and compares the whole thing. It does not parse the padding, so there is nothing for trailing garbage to hide in. The length arithmetic is correct: 2 + (k−54) + 1 + 51 = k.
- **Claims trusted before the signature is checked.** The signature is verified before `exp`, `iss` and `aud` are read.
- **Signature value s ≥ n accepted.** At most this lets a different byte string represent the same valid signature, which is malleability, not forgery. It has no auth impact.
- **Exceptions from deep JSON nesting or huge inputs.** `RecursionError` and `ValueError` are subclasses of `Exception`, so they are caught inside the `try` and turned into `InvalidToken`.

## WHAT HOLDS UP
- The RSA verification is constructed correctly and compares in constant time.
- The algorithm is pinned.
- The checks run in the right order.
- A missing or non-integer `exp` is rejected, and a bool `exp` is effectively rejected.
- The `iss` and `aud` checks are present.
- The test signer is independent of the verifier, and the test key is distinct from the production key.

## UNVERIFIED CLAIMS
- **"Tokens signed by our identity service" verify successfully.** Confirm this with a real token from the production identity service, run through `verify_token`.
- **"7 tests pass."** Confirm by running `python -m unittest test_auth`.

## QUESTIONS FOR THE AUTHOR
1. What are the production `iss` and `aud` values, and the `aud` type (string or array)?
2. Where did `PUBLIC_N` come from, and does it match the PEM exactly?
3. How do callers handle exceptions other than `InvalidToken`?

## DECISION-MAKER SUMMARY
The cryptography is correct and the classic JWT bypasses are closed. Before production:
- Fix F1 and F2.
- Confirm the issuer and audience values and the key against the real identity service (S1, S2).

If you proceed without that, the most likely outcome is a full outage, with every real token rejected, rather than a breach. A key rotation would silently fail to take effect.

## OWNER SUMMARY
The login-check code is built soundly and blocks the well-known tricks for faking access. A few settings look like test placeholders and must be confirmed against the real identity system, or every real user could be locked out. Two small fixes are needed so that bad input is rejected cleanly and a future key change actually takes effect.

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
    {"item": "identity service public key / iss / aud / token format", "status": "not_seen", "matters": true},
    {"item": "callers of verify_token", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Public key and a test-only private key; no personal or confidential data."},
  "coverage": {
    "checked": [
      {"unit": "auth.py", "kind": "file"},
      {"unit": "auth.py:_b64d", "kind": "function"},
      {"unit": "auth.py:_rsa_verify", "kind": "function"},
      {"unit": "auth.py:verify_token", "kind": "function"},
      {"unit": "test_auth.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "PUBLIC_N vs PUBLIC_KEY_PEM exact equality", "reason": "no tools to parse the PEM"},
      {"unit": "identity service configuration", "reason": "not supplied"},
      {"unit": "callers of verify_token", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:verify_token, header.get(\"alg\") outside the try",
     "scenario": "Unauthenticated token 'W10.e30.AA' (header []) or 'bnVsbA.e30.AA' (header null) raises AttributeError instead of InvalidToken; a caller catching only InvalidToken returns 500 with a stack trace instead of 401.",
     "fix": "Inside the try, reject non-dict header or claims so the result is InvalidToken.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "auth.verify_token('W10.e30.AA', now=1000): expect InvalidToken, observe AttributeError."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:PUBLIC_KEY_PEM vs PUBLIC_N/PUBLIC_E",
     "scenario": "The PEM is never used for verification. A key rotation that edits only the PEM leaves the old key trusted and rejects new tokens, and no test detects it.",
     "fix": "Derive n and e from the PEM, or delete the PEM; add a test asserting the PEM decodes to (PUBLIC_N, PUBLIC_E).",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Replace PUBLIC_KEY_PEM with another key: all 7 tests still pass and verification is unchanged."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:verify_token (kid ignored; single hardcoded key)",
     "scenario": "When the identity service rotates keys, all new tokens are rejected until a redeploy.",
     "fix": "Load keys from configuration or JWKS, keyed by kid, with RS256 pinned per key.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Sign a token with a new key that has kid=new: observe InvalidToken('bad signature') with no way to add the key without a code change."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "PROBABLE", "track": "B",
     "location": "test_auth.py: test_alg_none_is_refused, test_hs256_signed_with_the_public_key_is_refused, test_token_signed_by_another_key_is_refused",
     "scenario": "Removing the alg check leaves all tests green, because the none and HS256 signatures fail on length. The other-key test fails only on key-size mismatch (1024-bit vs 2048-bit), so regressions in those checks go unnoticed.",
     "fix": "Use a same-size second test key; add a test that reaches the alg check with a k-length signature; mutation-test in a scratch copy.",
     "answers": {"a": true, "b": false, "c": false, "d": false},
     "reproduction": "In a scratch copy, delete the alg check and run the suite: expect red, predicted green."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:verify_token, exp < now comparison",
     "scenario": "A token is accepted at exp == now, contrary to RFC 7519 4.1.4; nbf is ignored.",
     "fix": "Reject when exp <= now; reject when nbf > now if nbf is present.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "verify_token(sign_rs256({**CLAIMS, 'exp': 1000}), now=1000): expect InvalidToken, observe claims returned."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py:ISSUER, AUDIENCE",
     "suspicion": "The issuer uses the reserved .test TLD and may be a placeholder; if so, every production token is rejected.",
     "unresolved_fact": "The production identity service's exact iss and aud values."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "auth.py:PUBLIC_N",
     "suspicion": "PUBLIC_N may not equal the PEM modulus or the identity service's current key; only the leading digits were hand-checked.",
     "unresolved_fact": "Exact comparison of the PEM-decoded n with PUBLIC_N and with the service JWKS."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "auth.py:verify_token (aud and exp type checks)",
     "suspicion": "aud as an array or exp as a float would cause all tokens to be rejected.",
     "unresolved_fact": "The identity service's emitted aud and exp formats."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "context.md: '7 tests in test_auth.py pass'",
     "suspicion": "The test pass claim was not run in this review.",
     "unresolved_fact": "Output of python -m unittest test_auth."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "callers of verify_token (not supplied)",
     "suspicion": "Non-InvalidToken exceptions may surface as 500s or be mishandled.",
     "unresolved_fact": "Caller and framework exception handling around verify_token."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Algorithm confusion via alg none or HS256 signed with the public key.",
     "evidence": "The algorithm is never chosen from the header; _rsa_verify with fixed n and e rejects these signatures on length and EM mismatch."},
    {"id": "R2", "candidate": "PKCS#1 v1.5 padding-parsing forgery.",
     "evidence": "_rsa_verify builds and compares the full expected EM; length arithmetic is 2+(k-54)+1+51=k; there is no parsing."},
    {"id": "R3", "candidate": "Claims used before signature verification.",
     "evidence": "The signature check precedes the exp, iss and aud reads in verify_token."},
    {"id": "R4", "candidate": "Signature integer >= n accepted enables forgery.",
     "evidence": "It yields only an alternate encoding of an already-valid signature (malleability), not a forgery."},
    {"id": "R5", "candidate": "Deeply nested or huge JSON crashes the verifier.",
     "evidence": "RecursionError and ValueError subclass Exception and are caught by the try, which converts them to InvalidToken."}
  ]
}
```