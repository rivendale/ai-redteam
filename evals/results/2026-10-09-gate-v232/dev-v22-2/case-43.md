# Redteam report: `auth.py` / `test_auth.py`

**VERDICT: REJECT.** `verify_token` accepts unsigned tokens (`alg: none`) and tokens HMAC-signed with the public key (`alg: HS256`), so anyone can mint a valid token for any identity. The function's job is to decide who may call the reports API, and it does not do that.

**CONFIDENCE: high** on the two Critical findings, because each follows from reading a few lines with no ambiguity. Medium overall, for three reasons:
- **No tools.** I ran nothing, so the claim that 3 tests pass is unverified.
- **Same-context review, no subagent.** There is anchoring risk; re-run in a fresh session before production.
- **Unchecked key.** I could not confirm that `PUBLIC_N`/`PUBLIC_E` match `PUBLIC_KEY_PEM`.

Line numbers are counted from the supplied text, and each finding also quotes the line.

**INPUTS LEDGER**
- **Seen:** the original request (verbatim), the context, `auth.py` and `test_auth.py`.
- **Not seen:**
  - The identity service's real public key or JWKS. This matters: it is needed to confirm `PUBLIC_N` is the right key.
  - The callers of `verify_token`. This matters for F3: it decides whether an uncaught exception becomes a 500 or something worse.
  - The test run output. This matters: "3 tests pass" is an assertion only.
  - Whether the identity service issues tokens for other audiences. This matters for S2.

**COVERAGE**
- **Checked:** `auth.py` (`_b64d`, `_rsa_verify`, `verify_token`, all `alg` branches, the expiry check) and `test_auth.py` (all 3 tests, the setUp patching, `sign_rs256`).
- **Not checked:**
  - Whether `PUBLIC_N` matches the PEM. This needs computation.
  - Actual test execution.
  - The callers.

**SEATS AND GATE**
- **Seats:** a single local reviewer, same context, ran. No subagent was available. No cross-vendor seats were requested.
- **Sensitivity gate:** passed. The only key material is a public key, and the private exponent is a test-only key.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (traced) | B | `auth.py:53-54` `elif alg == "none": ok = True` | Unsigned tokens are accepted. | An attacker sends `b64({"alg":"none"}) + "." + b64({"sub":"admin","exp":9999999999}) + "."`. `_b64d("")` returns `b""`, `ok=True`, the expiry passes, and the claims come back as authenticated. | Delete the `none` and `HS256` branches. Accept only `alg == "RS256"` and raise `InvalidToken` otherwise. **Test:** build the token above and `assertRaises(InvalidToken)`. Today it returns the claims. | a✓ b✓ c✓ d✓ |
| F2 | Critical | CONFIRMED (traced) | B | `auth.py:51-52` `hmac.new(PUBLIC_KEY_PEM.encode(), ...)` | This is the classic RS256→HS256 algorithm-confusion hole. The HMAC "secret" is the public key, which is published by design and also sits in this source file. The request specified RS256 only, so this branch is also unrequested scope (drift). | An attacker takes the public PEM, sets header `{"alg":"HS256"}`, and computes `HMAC-SHA256(PEM, head.body)` over arbitrary claims. `compare_digest` matches and the attacker's claims are accepted. | Same fix as F1. **Test:** sign forged claims with `hmac.new(auth.PUBLIC_KEY_PEM.encode(), si, sha256)` under `alg=HS256` and `assertRaises(InvalidToken)`. Today it passes verification. | a✓ b✓ c✓ d✓ |
| F3 | Medium | CONFIRMED (traced) | B | `auth.py:48` `header.get("alg")` and `:59` `claims.get("exp", 0) < ...` | These lines sit outside the `try`. A header or body that is valid JSON but not an object raises `AttributeError`. An `exp` that is a string or `null` raises `TypeError`. Neither is converted to `InvalidToken`. | A token whose body is `b64("[]")`, or whose claims are `{"exp":"x"}`, raises an uncaught exception. A caller catching only `InvalidToken` returns a 500, and caller logic that treats "no exception path taken" loosely could misbehave. A validly signed token with a bad `exp` comes from the issuer, so the realistic trigger is junk input. | Require `isinstance(header, dict)` and `isinstance(claims, dict)`. Require `exp` to be a number, excluding `bool`. Map every failure to `InvalidToken`. **Test:** `verify_token(b64(b'[]')+'.'+b64(b'[]')+'.')` must raise `InvalidToken`; today it raises `AttributeError`. | a✓ b✓ c✗ d✗ |
| F4 | Medium | CONFIRMED (read) | B | `test_auth.py`, all tests | The tests cover only the RS256 happy path, expiry, and payload tampering. There is no test for `alg: none`, HS256, an unknown alg, a truncated signature or a malformed token. That gap is why F1 and F2 shipped "green". `setUp` also patches in a test key, so the production `PUBLIC_N` is never exercised. | A future change re-opens an alg bypass and CI stays green. | Add the F1, F2 and F3 tests plus `alg: "RS512"` → `InvalidToken`. Per the skill's mutation rule: in a scratch copy, set `ok = True` unconditionally and confirm `test_tampered_payload` goes red. | a✓ b✓ c✗ d✓ |
| F5 | Low | CONFIRMED (read) | B | `auth.py:59` `exp < now` | A token is still accepted at exactly `now == exp`. RFC 7519 §4.1.4 says to reject "on or after" `exp`. | There is a one-second window at expiry. | Use `exp <= now`, or add an explicit small leeway. | a✓ b✓ c✗ d✗ |
| F6 | Low | CONFIRMED (read) | B | `auth.py:35` | A signature integer `s ≥ n` is not rejected (RFC 8017 §5.2.2). Because `pow(... , n)` reduces it, `s+n` verifies when it fits in k bytes. The result is malleability, not forgery. | Two byte-different signatures are both valid for the same token, which defeats any dedupe keyed on raw token bytes. | Reject the signature if `int.from_bytes(signature) >= n`. | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION
- **S1, the key itself.** Does `PUBLIC_N`/`PUBLIC_E` equal the modulus and exponent in `PUBLIC_KEY_PEM`, and is that the identity service's current key? Settle it by parsing the PEM, for example with `openssl rsa -pubin -noout -modulus`, and comparing it to `hex(PUBLIC_N)` and to the service's published JWKS. If they differ, every real token fails, or a stale key is trusted. A hardcoded key also means rotation requires a redeploy.
- **S2, other audiences.** Does the identity service issue tokens for services other than the reports API? If it does, a token minted for another service is accepted here, because `aud`, `iss` and `nbf` are not checked. The request did not ask for these checks, so this is a question, not drift.

## REFUTED
- **"`_rsa_verify` is vulnerable to Bleichenbacher-style lax PKCS#1 parsing."** Refuted. It rebuilds the full expected EM, including the DigestInfo and full `0xff` padding, and constant-time-compares all k bytes. It also checks the signature length.
- **"Extra token segments slip through."** Refuted. `head, body, sig = token.split(".")` raises `ValueError` on anything other than 3 parts, and the `try` catches it.
- **"A missing `exp` means the token never expires."** Refuted. `claims.get("exp", 0)` is 0, so the token is rejected as expired.

## WHAT HOLDS UP
- The RS256 path itself is correct: the signing input uses the raw b64 segments, verification uses full-EM comparison, and `hmac.compare_digest` gives constant-time comparison.
- The malformed-token parsing is wrapped and fails closed.
- The test helper `sign_rs256` produces correct PKCS#1 v1.5 encoding.

## UNVERIFIED CLAIMS
- **"3 tests in test_auth.py pass."** Confirm by running `python -m unittest test_auth`.
- **The test key's validity.** That `N`, `E` and `D` in the test file form a valid key pair is implied if `test_valid_token` passes; this is unverified.
- **The PEM-to-modulus correspondence.** See S1.

## QUESTIONS FOR THE AUTHOR
1. Was there any requirement for HS256 or `none`? If not, both branches go.
2. Is the key static, or should it come from the identity service's JWKS?
3. Should `aud` and `iss` be enforced?

## DECISION-MAKER SUMMARY
Do not deploy. As written, F1 and F2 let anyone forge a token for any user with no secret. The fix is small: accept RS256 only, add the attack tests, and validate claim types. After that, re-review.

## OWNER SUMMARY
The login check for the reports system can be bypassed by anyone. A caller can either skip the signature entirely or sign with information that is meant to be public. The fix is quick: allow only the one signing method that was asked for, and add tests that try these tricks.

```json
{
  "schema_version": "2.2",
  "verdict": "REJECT",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "auth.py", "status": "seen", "matters": true},
    {"item": "test_auth.py", "status": "seen", "matters": true},
    {"item": "identity service public key / JWKS", "status": "not_seen", "matters": true},
    {"item": "callers of verify_token", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Only a public key and a test-only private exponent are present."},
  "coverage": {
    "checked": [
      {"unit": "auth.py", "kind": "file"},
      {"unit": "auth.py:_b64d", "kind": "function"},
      {"unit": "auth.py:_rsa_verify", "kind": "function"},
      {"unit": "auth.py:verify_token", "kind": "function"},
      {"unit": "test_auth.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "PUBLIC_N vs PUBLIC_KEY_PEM correspondence", "reason": "no tools to parse the PEM"},
      {"unit": "test execution", "reason": "no tools"},
      {"unit": "callers of verify_token", "reason": "not supplied"}
    ]
  },
  "verdict_reason": "alg=none and HS256-with-public-key branches allow anyone to forge tokens.",
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:53-54 (elif alg == \"none\": ok = True)",
     "scenario": "A token with header {\"alg\":\"none\"}, arbitrary claims and an empty signature is accepted, so an attacker can authenticate as any subject.",
     "fix": "Accept only alg == \"RS256\" and raise InvalidToken for all others.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "verify_token(b64('{\"alg\":\"none\"}')+'.'+b64('{\"sub\":\"admin\",\"exp\":9999999999}')+'.') returns claims; expected InvalidToken."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:51-52 (hmac.new(PUBLIC_KEY_PEM.encode(), ...))",
     "scenario": "An attacker HMAC-SHA256-signs forged claims with the public PEM under alg=HS256 and they are accepted (algorithm confusion). The branch is also unrequested scope.",
     "fix": "Remove the HS256 branch; accept RS256 only.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Sign head.body with hmac.new(auth.PUBLIC_KEY_PEM.encode(), si, sha256), header alg=HS256; verify_token returns claims; expected InvalidToken."},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:48 header.get, auth.py:59 claims.get(\"exp\", 0) < now",
     "scenario": "A non-object JSON header or body, or a non-numeric exp, raises AttributeError or TypeError instead of InvalidToken, giving an uncaught 500.",
     "fix": "Validate that header and claims are dicts and that exp is numeric (not bool); map failures to InvalidToken.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "verify_token(b64(b'[]')+'.'+b64(b'[]')+'.') raises AttributeError; expected InvalidToken."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_auth.py (class T)",
     "scenario": "No tests for alg=none, HS256, unknown alg or malformed input, so F1 and F2 pass CI; the production key is never exercised.",
     "fix": "Add negative tests for each alg bypass and for malformed tokens; mutation-check that test_tampered_payload fails when ok=True.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Add the F1 and F2 reproductions as tests; both fail on current code."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:59 (exp < now)",
     "scenario": "A token is accepted at the exact second now == exp, contrary to RFC 7519 4.1.4.",
     "fix": "Use exp <= now.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "verify_token(sign_rs256({'sub':'u1','exp':1000}), now=1000) returns claims; expected InvalidToken."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:35 (pow(int.from_bytes(signature), e, n))",
     "scenario": "A signature s+n (when it fits in k bytes) also verifies, making signatures malleable.",
     "fix": "Reject the signature if int.from_bytes(signature) >= n.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Take a valid sig s; if s+n < 256**k, the token with sig (s+n) verifies; expected rejection."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py:8-19",
     "suspicion": "PUBLIC_N/PUBLIC_E may not match PUBLIC_KEY_PEM or the identity service's current key.",
     "unresolved_fact": "The modulus parsed from the PEM and from the service JWKS, compared to PUBLIC_N."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "auth.py:59-61",
     "suspicion": "Tokens issued for other services would be accepted, because aud and iss are unchecked.",
     "unresolved_fact": "Whether the identity service issues tokens for other audiences with the same key."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "_rsa_verify accepts loosely parsed PKCS#1 padding.", "evidence": "It rebuilds the full expected EM and constant-time-compares all k bytes (auth.py:36-37)."},
    {"id": "C2", "candidate": "Tokens with extra segments are accepted.", "evidence": "The 3-way unpack of split('.') raises ValueError inside the try and becomes InvalidToken."},
    {"id": "C3", "candidate": "A missing exp means the token never expires.", "evidence": "claims.get('exp', 0) defaults to 0, so the token is rejected as expired."}
  ]
}
```