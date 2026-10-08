# Redteam report: `auth.py` token verification

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent and no tools were available, so nothing was executed. Every finding below comes from tracing exact lines and Python semantics. The reproductions are written out but have not been run.

**VERDICT: REWORK.** `verify_token` accepts unsigned tokens (`alg: none`) and HMAC tokens keyed with the public key. Either way, anyone can mint a token with any claims for the reports API.

**CONFIDENCE: medium.** It is limited by the same-context review, no code execution, and no information about how callers use the claims or what audiences the identity service issues.

**INPUTS LEDGER**
| Item | Status | Matters |
|---|---|---|
| request.md (original request) | seen | — |
| context.md | seen | — |
| auth.py | seen | — |
| test_auth.py | seen | — |
| Identity service's real public key / JWKS endpoint | not seen | yes: can't confirm `PUBLIC_N` and the PEM are the right key, or that they match each other |
| Callers of `verify_token` (reports API handlers, error handling) | not seen | yes: decides whether a `TypeError`/`AttributeError` becomes a 500 or a bypass, and whether `aud`/`iss` matter |
| Test run output ("3 tests pass") | not seen | low: asserted only; the tests don't cover the critical paths anyway |

**COVERAGE**
- Checked: `auth.py:_b64d`, `auth.py:_rsa_verify`, `auth.py:verify_token` (every branch), the `PUBLIC_KEY_PEM`/`PUBLIC_N` constants, and all 3 tests in `test_auth.py` plus their `setUp` patching.
- Not checked: whether the PEM decodes exactly to `PUBLIC_N` (needs tools), caller code, the identity service's token profile (`aud`/`iss`/`kid`), and key rotation.

**SEATS AND GATE**
- Only a local same-context review ran.
- Sensitivity gate passed: the material is public key material and synthetic test keys, with no personal data. Cross-vendor seats were not used because no tools or subagents were available.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | auth.py:53-54 `elif alg == "none": ok = True` | Unsigned tokens are accepted. | An attacker sends `b64('{"alg":"none"}') + "." + b64('{"sub":"admin","exp":4000000000}') + "."`. The split yields 3 parts, the empty signature decodes to `b""`, `ok = True`, and the forged claims are returned. Anyone gets full access to the reports API. | Delete the branch. Accept only `alg == "RS256"`, and raise `InvalidToken` for anything else. Test: `assertRaises(InvalidToken, verify_token, <token above>, now=1000)`. It fails today. | y/y/y/y |
| F2 | Critical | CONFIRMED | B | auth.py:51-52 `hmac.new(PUBLIC_KEY_PEM.encode(), ...)` | Algorithm confusion: HS256 is verified with the **public** key as the HMAC secret. | The PEM is public (it ships in this file and is usually in a JWKS). An attacker sets the header to `{"alg":"HS256"}`, computes `HMAC-SHA256(PEM_bytes, head.body)` over any claims, and the token verifies. | Same fix as F1: drop HS256 and never select the key or algorithm from the token header. Test: forge the token with `hmac.new(auth.PUBLIC_KEY_PEM.encode(), si, sha256)` and expect `InvalidToken`. It fails today. | y/y/y/y |
| F3 | High | CONFIRMED | B | test_auth.py (whole suite) | The tests cover only the happy path, expiry and payload tamper. Nothing covers `alg` handling, so the suite stays green with F1 and F2 present. "3 tests pass" says nothing about the main risk. | A future refactor re-adds or keeps a permissive algorithm and CI stays green. | Add tests for `alg: none`, HS256 keyed with the PEM, a missing `alg`, and `alg: "rs256"` (case). Each must fail against the current code before the fix (positive control) and pass after. | y/y/n/y |
| F4 | Medium | CONFIRMED | B | auth.py:48 `header.get("alg")` (outside the `try`) | The header is parsed before any signature check and not type-checked. A header that is valid JSON but not an object raises an uncaught `AttributeError` instead of `InvalidToken`. | An unauthenticated client sends header `b64("[]")` (or `"1"`). `[].get` raises `AttributeError`, which most frameworks turn into a 500 rather than a 401. Error-path behavior then depends on the caller. | Require `isinstance(header, dict)` and `isinstance(claims, dict)` inside the `try`, otherwise raise `InvalidToken`. Repro: `verify_token(b64(b"[]")+"."+b64(b"{}")+".")` should raise `InvalidToken` but raises `AttributeError`. | y/y/n/n |
| F5 | Medium | CONFIRMED | B | auth.py:59 `claims.get("exp", 0) < (...)` | `exp` is not type-checked. A string or `null` raises `TypeError` (uncaught). JSON `NaN` (which `json.loads` accepts) makes the comparison `False`, so the token never expires. | This is reachable by an attacker only through F1/F2. After those are fixed it needs an issuer-signed malformed token, so the realistic likelihood is low. | Require `isinstance(exp, (int, float)) and math.isfinite(exp)` and wrap failures as `InvalidToken`. Repro: an `alg:none` token with `"exp": NaN` is accepted with `now=1000`. | y/y/n/n |
| F6 | Medium | CONFIRMED | B | auth.py:49-56 | Requirement fit: the request asks for RS256 verification only. The HS256 and `none` branches are unrequested extras, and they are what create F1 and F2. | Same scenarios as F1 and F2. This row records the drift; it is not a separate exploit. | Reduce `verify_token` to RS256 only. | y/y/n/y |

### NEEDS VALIDATION
- **S1 (no audience or issuer check).** `aud` and `iss` are not checked. To settle: does the identity service issue RS256 tokens with this key for other audiences? If yes, any token minted for another service works on the reports API. The request did not ask for this, but it is the next most serious gap.
- **S2 (key mismatch).** `PUBLIC_N` and `PUBLIC_KEY_PEM` might not be the same key. The leading bytes are consistent: the PEM modulus begins `0xb40a5f…`, which gives ≈2.27×10^616, matching `PUBLIC_N`'s leading digits. To settle, decode the PEM's modulus and compare it to `PUBLIC_N`, then compare both to the identity service's published key. Once HS256 is removed, the PEM is unused and should be deleted.
- **S3 (no key rotation).** The key is hardcoded with no `kid` handling or rotation. To settle: does the identity service rotate keys, and how is this module told when it does?

### REFUTED
- **`_rsa_verify` is malleable or a Bleichenbacher-style lax PKCS#1 parse.** Refuted. It rebuilds the entire expected EM (`00 01 FF… 00 DigestInfo hash`) and compares it in constant time, and it rejects signatures of the wrong length (lines 33-37). There is no parse-and-trust of the ASN.1.
- **A missing `exp` means the token never expires.** Refuted. The default is `0`, and `0 < now` raises "expired".
- **Lenient base64 (non-alphabet characters are discarded) allows a signature bypass.** Refuted. The signature is computed over the raw `head_b64.body_b64` string, so altering the encoding changes the signing input. At most, different signature encodings decode to the same bytes, which has no authorization impact.

### WHAT HOLDS UP
- The RS256 path is correct PKCS#1 v1.5/SHA-256 verification: a full EM comparison, a length check and a constant-time compare.
- Expiry is checked after the signature.
- Malformed token structure (wrong segment count, bad base64 or JSON) is wrapped as `InvalidToken`.
- The tests correctly use a synthetic key via `mock.patch.multiple`.

### UNVERIFIED CLAIMS
- "3 tests in test_auth.py pass." Not run. Confirm with `python -m unittest test_auth`.
- `PUBLIC_N`/`PUBLIC_E` are the identity service's production key. Confirm against its JWKS.

### QUESTIONS FOR THE AUTHOR
1. Why were the HS256 and `none` branches added? Does any caller depend on them?
2. Does the identity service issue tokens for other audiences with this key (S1)?

### DECISION-MAKER SUMMARY
Do not ship. The verifier accepts unsigned tokens and tokens "signed" with the public key, so anyone can impersonate any user on the reports API. The fix is small: accept only RS256 and add tests that prove the forgeries are rejected.

### OWNER SUMMARY
The new login check for the reports system can be fooled by anyone, because it accepts tokens that were never signed or were signed with a publicly known key. It must not go live until those two paths are removed and tests prove that forged tokens are refused. The core signature check itself is sound, so the fix is quick.

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
    {"item": "identity service JWKS / production public key", "status": "not_seen", "matters": true},
    {"item": "callers of verify_token", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Public key material and synthetic test keys only; no personal data."},
  "coverage": {
    "checked": [
      {"unit": "auth.py", "kind": "file"},
      {"unit": "auth.py:_b64d", "kind": "function"},
      {"unit": "auth.py:_rsa_verify", "kind": "function"},
      {"unit": "auth.py:verify_token", "kind": "function"},
      {"unit": "test_auth.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "PUBLIC_KEY_PEM vs PUBLIC_N equality", "reason": "no tools to decode"},
      {"unit": "callers of verify_token", "reason": "not supplied"},
      {"unit": "identity service token profile (aud/iss/kid)", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:53-54 (elif alg == \"none\": ok = True)",
     "scenario": "A token with header {\"alg\":\"none\"}, arbitrary claims and an empty signature is accepted, so anyone can impersonate any user.",
     "fix": "Accept only alg == \"RS256\"; raise InvalidToken otherwise.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "verify_token(b64('{\"alg\":\"none\"}')+'.'+b64('{\"sub\":\"admin\",\"exp\":4000000000}')+'.', now=1000): expect InvalidToken, observe claims returned."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:51-52 (hmac.new(PUBLIC_KEY_PEM.encode(), ...))",
     "scenario": "An attacker sets alg HS256 and HMACs arbitrary claims with the public PEM as the key; the token verifies.",
     "fix": "Remove the HS256 branch; never select the algorithm or key from the token header.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Build head={\"alg\":\"HS256\"}, sig=HMAC-SHA256(auth.PUBLIC_KEY_PEM.encode(), head.body); verify_token returns the forged claims instead of raising."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_auth.py (all three tests)",
     "scenario": "No test exercises alg handling, so the suite passes with F1 and F2 present and would not catch a regression.",
     "fix": "Add tests for alg none, HS256 keyed with the PEM, missing alg and wrong-case alg; confirm each fails before the fix.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Run the suite on current code: all 3 tests pass despite F1/F2 (asserted by context.md, not run here)."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:48 (header.get(\"alg\"))",
     "scenario": "An unauthenticated client sends a header that is a JSON array or number; AttributeError escapes instead of InvalidToken, likely producing a 500.",
     "fix": "Check isinstance(header, dict) and isinstance(claims, dict) inside the try; raise InvalidToken otherwise.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "verify_token(b64(b'[]')+'.'+b64(b'{}')+'.'): expect InvalidToken, observe AttributeError."},
    {"id": "F5", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:59 (claims.get(\"exp\", 0) < ...)",
     "scenario": "exp as a string or null raises an uncaught TypeError; exp NaN compares False, so the token never expires.",
     "fix": "Require a finite int or float exp; otherwise raise InvalidToken.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "alg-none token with \"exp\": NaN and now=1000 is accepted; with \"exp\": \"x\" it raises TypeError."},
    {"id": "F6", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:49-56",
     "scenario": "Unrequested HS256 and none support (the request is RS256 only) is the root cause of F1 and F2.",
     "fix": "Reduce verify_token to the RS256 path only.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "See F1 and F2."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py:verify_token",
     "suspicion": "No aud or iss check; tokens minted for other services may be accepted.",
     "unresolved_fact": "Whether the identity service issues tokens for other audiences under this key."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "auth.py:8-18",
     "suspicion": "PUBLIC_KEY_PEM and PUBLIC_N may not be the same key, or may not be the production key.",
     "unresolved_fact": "The decoded PEM modulus compared with PUBLIC_N and with the identity service JWKS."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "auth.py:18-19",
     "suspicion": "The key is hardcoded with no kid or rotation support.",
     "unresolved_fact": "Whether and how the identity service rotates its signing key."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "_rsa_verify uses a lax PKCS#1 parse open to forgery.",
     "evidence": "It rebuilds the full expected EM and compares it with hmac.compare_digest after a length check (auth.py:33-37)."},
    {"id": "C2", "candidate": "A missing exp means the token never expires.",
     "evidence": "The default is 0, so 0 < now raises 'expired' (auth.py:59)."},
    {"id": "C3", "candidate": "Lenient base64 decoding allows a signature bypass.",
     "evidence": "The signing input is the raw head_b64.body_b64 string, so encoding changes alter what is verified."}
  ]
}
```