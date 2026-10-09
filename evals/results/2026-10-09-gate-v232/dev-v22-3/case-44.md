# Redteam report: `auth.py` / `test_auth.py`, JWT verification for the reports API

**Single reviewer, no tools.** I could not run code, run the tests, or open anything. Every result below comes from reading and tracing the code. Anything that needs execution is under NEEDS VALIDATION.

---

**VERDICT: SHIP WITH FIXES.** The RS256 verification itself is sound. However, the hard-coded issuer and audience look like placeholders, which would make production reject every real token. The production key is also never tested in the accept path.

**CONFIDENCE: medium.** Limits:
- I could not execute anything, so the claimed "7 tests pass" is unverified.
- I could not decode the PEM to check that it matches `PUBLIC_N`.
- I don't know the identity service's real `iss`, `aud` or key.

**INPUTS LEDGER**
- **Seen:** `request.md`, `context.md`, `auth.py`, `test_auth.py`.
- **Not seen, and these matter:**
  - The identity service's actual issuer URL, audience value, public key or JWKS endpoint, and its key rotation policy. Findings F1 and F2 depend on these.
  - How callers handle exceptions from `verify_token`. F3's severity depends on this.
  - A sample real production token, which would show the form of `aud` and `exp`.
  - Test run output.

**COVERAGE**
- **Checked:**
  - `auth.py`: `_b64d`, `_rsa_verify`, `verify_token`, and the constants `PUBLIC_KEY_PEM`, `PUBLIC_N`, `PUBLIC_E`, `ISSUER`, `AUDIENCE`.
  - `test_auth.py`: all 7 tests, plus the helpers `sign_rs256` and `forge`.
  - The PKCS#1 v1.5 DigestInfo prefix and EM layout.
  - A rough check of the PEM's leading modulus bytes (0xB40A5F…) against the magnitude of `PUBLIC_N` (≈2.27e616). They are consistent, but that falls short of proving they are the same key.
- **Not checked:**
  - An exact equality between the PEM and `PUBLIC_N`.
  - Whether the tests actually run and pass.
  - Mutation runs.
  - The caller and integration code.

**SEATS AND GATE**
- Seats: a single local reviewer only. No subagent and no cross-vendor seats were available in this session.
- Sensitivity gate: passed. The material is a public key and test key material only, with no personal or confidential data.

---

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | High | PROBABLE | B | `auth.py` `ISSUER = "https://id.example.test"`, `AUDIENCE = "reports-api"` | The issuer uses the `.test` TLD, which RFC 6761 reserves for testing. The request names no issuer or audience, so both values were invented and are presented as production config. | You deploy to production. Real tokens from the identity service carry its real `iss` and/or `aud`, so every legitimate call fails with "wrong issuer or audience". The reports API is down for everyone. | Load `ISSUER` and `AUDIENCE` from config, sourced from the identity service's discovery document. To reproduce, take a real production token and call `verify_token(tok)`: expect claims, observe `InvalidToken("wrong issuer or audience")`. | a✓ b✗ c✓ d✓ |
| F2 | Medium | CONFIRMED | B | `test_auth.py` `setUp` patches `PUBLIC_N`/`PUBLIC_E` for every test. `auth.py` `PUBLIC_KEY_PEM` is never read by the code. | The production key is never exercised on the accept path. The key has two sources of truth (the PEM and `PUBLIC_N`), and no test ties them together. Key rotation requires a code deploy. | Suppose `PUBLIC_N` was transcribed from the wrong key, or the identity service rotates its key. Every token is then rejected in production, and the suite stays green. | Derive `n` and `e` from the PEM at import (or fetch the JWKS, keyed by `kid`) and delete the duplicate constant. Add a test asserting the parsed PEM modulus equals `PUBLIC_N`. Add an integration test using a real token from the identity service. | a✓ b✓ c✗ d✗ |
| F3 | Medium | CONFIRMED | B | `auth.py` `verify_token`: `header.get("alg")` sits after the `try` block | If the header JSON is valid but not an object, `header.get` raises `AttributeError` outside the `try`, so the caller gets an unhandled exception instead of `InvalidToken`. | An unauthenticated caller sends `W10.e30.AA` (the header decodes to `[]`). The caller receives `AttributeError` instead of `InvalidToken`. Depending on the caller, that becomes a 500 response with a traceback, or noisy alerts. | Inside the `try`, add `if not isinstance(header, dict) or not isinstance(claims, dict): raise ValueError`. To reproduce, call `verify_token("W10.e30.AA")`: expect `InvalidToken`, observe `AttributeError`. | a✓ b✓ c✗ d✓ |
| F4 | Low | CONFIRMED | B | `auth.py` `exp < (now ...)` | A token is accepted at the exact second `exp == now`. RFC 7519 §4.1.4 requires the current time to be *before* `exp`. | A token is still usable for up to one second past its expiry. The impact is negligible but non-conformant. | Change the comparison to `exp <= now`, or define an explicit leeway. To reproduce, call `verify_token(sign_rs256({**CLAIMS,"exp":1000}), now=1000)`: expect `InvalidToken`, observe that the claims are returned. | a✓ b✓ c✗ d✗ |
| F5 | Low | CONFIRMED (trace) | B | `test_auth.py` `test_alg_none_is_refused`, `test_hs256_signed_with_the_public_key_is_refused` | Both tests pass even with the `alg` check deleted. The empty signature and the 32-byte HMAC fail the `len(signature) != k` check in `_rsa_verify` first. | Someone later weakens or removes the `alg` check, and both tests stay green. | Add a test that sends a *validly RS256-signed* token whose header says `"alg":"HS256"`, and expect `InvalidToken`. Mutation to confirm: delete the `alg` check; the current tests stay green and the new one goes red. | a✓ b✓ c✗ d✗ |
| F6 | Low | CONFIRMED (trace) | B | `auth.py` `_rsa_verify` | The code never checks that `s < n` (RFC 8017 §8.2.2 requires it). For a valid signature `s` small enough that `s + n` still fits in k bytes, `s + n` also verifies. | This is signature malleability, not forgery. It only matters if anything downstream uses the token string or signature as a unique ID or replay key. | Add `if int.from_bytes(signature,"big") >= n: return False`. To reproduce, take a valid token with `s < 256^k − n`, replace the signature with `s + n`, and observe that it is accepted. | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION
- **S1: PEM and `PUBLIC_N` agree.** Unresolved fact: does `int` of the PEM's modulus equal `PUBLIC_N`, and is it the identity service's current key? The leading bytes are consistent, but I could not check further.
- **S2: `aud` as an array.** RFC 7519 allows `aud` to be an array. If the identity service issues `["reports-api", ...]`, the code rejects every token. Unresolved fact: the `aud` form in a real token.
- **S3: Non-integer `exp` and clock skew.** A float `exp` is rejected, and there is no leeway for skew. Unresolved fact: the issuer's `exp` format and the clock tolerance between hosts.
- **S4: "7 tests pass".** I could not run the suite, so this is unverified. Unresolved fact: the output of `python -m unittest test_auth`.
- **S5: `crit` header.** It is ignored, and RFC 7515 §4.1.11 requires rejecting unknown critical extensions. Unresolved fact: whether the issuer ever sets `crit`.

## REFUTED
- **Algorithm confusion (HS256 with the public key as the HMAC secret).** The verifier never branches on `alg` to pick a scheme. It always runs `_rsa_verify` with a hard-coded RSA key, so no HMAC path exists.
- **Bleichenbacher-style lax PKCS#1 parsing.** `_rsa_verify` builds the entire expected EM and compares the whole thing. It does not parse the EM, and `e = 65537`. The DigestInfo prefix `3031300d…0420` is the correct SHA-256 prefix.
- **Timing leak in the signature comparison.** The comparison uses `hmac.compare_digest`.
- **`exp: true` bypassing the type check.** `True` passes `isinstance(int)`, but as 1 it is less than `now`, so the token is rejected as expired.
- **Malformed input crashing at decode.** `None`, `bytes`, a wrong number of segments, bad base64 and bad JSON are all inside the `try` and become `InvalidToken`. Only the non-dict case escapes (F3).

## WHAT HOLDS UP
- The signature is verified over the exact raw `head_b64.body_b64` bytes before any claim is trusted.
- The RSA encoding check is strict and complete.
- The check order is correct: signature, then expiry, then issuer and audience.
- The tampered-payload test and the wrong-key test assert real behaviour.
- Adding `iss`/`aud` checks beyond the request is good practice. The problem in F1 is the values, not the checks.

## UNVERIFIED CLAIMS
- **"7 tests pass."** Confirm by running the suite.
- **"Tokens are signed by the identity service" with this key.** Confirm by verifying one real production token against `PUBLIC_N`.
- **The module docstring's "valid, unexpired token issued for this API".** This depends on F1, S2 and S3.

## QUESTIONS FOR THE AUTHOR
1. What `iss` and `aud` does the identity service actually issue, and in what form is `aud`?
2. Where did `PUBLIC_N` come from, and how will key rotation be handled (a JWKS lookup by `kid`, or a redeploy)?
3. Do callers catch only `InvalidToken`?

## DECISION-MAKER SUMMARY
The cryptographic core is correct and the forgery tests are meaningful. As written, though, the issuer and audience appear to be test placeholders, and nothing tests the production key. Deploying now would most likely lock every legitimate caller out of the reports API. Fix F1 to F3 and verify one real production token before release; F4 to F6 can follow.

## OWNER SUMMARY
The code that checks login tokens for the reports service does its security checks correctly, and I found no way to forge a token. However, it appears to be set up with sample test values instead of the real identity service's details. If released as is, it would probably turn away every genuine user. Replace those values with the real ones and test against one real token before release.

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
    {"item": "identity service iss/aud/public key/rotation policy", "status": "not_seen", "matters": true},
    {"item": "caller exception handling", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "public key and test key material only"},
  "coverage": {
    "checked": [
      {"unit": "auth.py", "kind": "file"},
      {"unit": "auth.py:_b64d", "kind": "function"},
      {"unit": "auth.py:_rsa_verify", "kind": "function"},
      {"unit": "auth.py:verify_token", "kind": "function"},
      {"unit": "auth.py:ISSUER/AUDIENCE/PUBLIC_N/PUBLIC_KEY_PEM", "kind": "config"},
      {"unit": "test_auth.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "exact PEM-to-PUBLIC_N equality", "reason": "no tools to decode"},
      {"unit": "test execution and mutation runs", "reason": "no tools"},
      {"unit": "caller/integration code", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "High", "evidence_level": "PROBABLE", "track": "B",
     "location": "auth.py ISSUER/AUDIENCE constants",
     "scenario": "Deployed to production, real identity-service tokens carry the real issuer/audience, not the reserved-TLD placeholder https://id.example.test, so every legitimate call raises InvalidToken('wrong issuer or audience').",
     "fix": "Load ISSUER and AUDIENCE from configuration sourced from the identity service; verify against a real production token.",
     "answers": {"a": true, "b": false, "c": true, "d": true},
     "reproduction": "verify_token(<real production token>): expect claims, observe InvalidToken('wrong issuer or audience')."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_auth.py setUp; auth.py PUBLIC_KEY_PEM (unused) and PUBLIC_N",
     "scenario": "If PUBLIC_N does not match the identity service key, or the key rotates, all production tokens are rejected while every test stays green, because setUp replaces the key in every test.",
     "fix": "Derive n,e from the PEM (or JWKS by kid), remove the duplicate constant, add a test that the PEM modulus equals PUBLIC_N and an integration test with a real token.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "No current test calls verify_token with the production key on a token expected to be accepted."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py verify_token, header.get('alg') after the try block",
     "scenario": "An unauthenticated caller sends a token whose header JSON is an array; header.get raises AttributeError instead of InvalidToken, surfacing as a 500 or unhandled error.",
     "fix": "Inside the try block, reject non-dict header or claims.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "verify_token('W10.e30.AA'): expect InvalidToken, observe AttributeError."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py verify_token exp comparison",
     "scenario": "A token is accepted when exp equals the current time, contrary to RFC 7519 4.1.4.",
     "fix": "Use exp <= now, or an explicit documented leeway.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "verify_token(sign_rs256({**CLAIMS,'exp':1000}), now=1000): expect InvalidToken, observe claims returned."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_auth.py test_alg_none_is_refused, test_hs256_signed_with_the_public_key_is_refused",
     "scenario": "Removing the alg check leaves both tests green, because the forged signatures fail the length check first.",
     "fix": "Add a test with a valid RS256 signature over a header claiming alg HS256, expecting InvalidToken.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Delete the alg check in a scratch copy; both existing alg tests still pass."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py _rsa_verify",
     "scenario": "No s < n check: for a valid signature s with s + n < 256^k, s + n also verifies, so the token string is malleable; this matters if tokens or signatures are used as unique or replay keys.",
     "fix": "Reject when int.from_bytes(signature,'big') >= n.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Replace the signature of a valid token (with small s) by s + n encoded in k bytes; observe acceptance."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py PUBLIC_KEY_PEM / PUBLIC_N",
     "suspicion": "PEM and PUBLIC_N may not be the same key, or not the identity service's current key.",
     "unresolved_fact": "Whether the modulus decoded from the PEM equals PUBLIC_N and matches the identity service's published key."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "auth.py verify_token aud check",
     "suspicion": "An array-valued aud would be rejected.",
     "unresolved_fact": "The aud form in a real identity-service token."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "auth.py verify_token exp check",
     "suspicion": "A float exp or clock skew causes false rejections.",
     "unresolved_fact": "The issuer's exp format and the clock tolerance between hosts."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "context.md 'Tests: 7 tests pass'",
     "suspicion": "The pass claim is unverified.",
     "unresolved_fact": "Output of python -m unittest test_auth."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "auth.py verify_token header handling",
     "suspicion": "Unknown crit header extensions are not rejected (RFC 7515 4.1.11).",
     "unresolved_fact": "Whether the issuer ever sets crit."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "HS256 or alg confusion using the public key as the HMAC secret.", "evidence": "The verifier always calls _rsa_verify with a fixed RSA key; there is no HMAC path."},
    {"id": "R2", "candidate": "Bleichenbacher-style lax PKCS#1 parsing forgery.", "evidence": "The full expected EM is built and compared byte for byte; e = 65537; the DigestInfo prefix is correct."},
    {"id": "R3", "candidate": "Timing leak in the signature comparison.", "evidence": "hmac.compare_digest is used."},
    {"id": "R4", "candidate": "exp: true bypasses the integer check.", "evidence": "True == 1 < now, so the token is rejected as expired."}
  ]
}
```