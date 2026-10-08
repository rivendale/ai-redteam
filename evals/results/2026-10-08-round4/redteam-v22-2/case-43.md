# Redteam report: `auth.py` / `test_auth.py`

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No tools were available in this session. Nothing below was run. Every CONFIRMED label comes from tracing the code line by line, not from executing it.

**VERDICT: REJECT.** The verifier accepts tokens with no signature at all (`alg: none`) and tokens signed with the public key (`alg: HS256`). Anyone can mint a token for any user, which defeats the one thing the original request asked for.

**CONFIDENCE: medium.** The two Critical findings are certain from the code. Confidence is limited by: same-context review, no execution, the key's provenance not supplied, and the test suite not run.

**INPUTS LEDGER**
| Item | Status | Matters? |
|---|---|---|
| request.md (verbatim request) | seen | — |
| context.md | seen | — |
| auth.py | seen | — |
| test_auth.py | seen | — |
| Identity service's real public key / JWKS | not seen | Yes: cannot confirm `PUBLIC_N`/`PUBLIC_E` are the right key, or that they match `PUBLIC_KEY_PEM` |
| Caller code (how `InvalidToken` and other exceptions are handled) | not seen | Partly: sets the impact of F3 |
| Test run output ("3 tests pass") | not seen | No: the verdict does not depend on it |
| Identity service token profile (iss/aud, other consumers) | not seen | Partly: see S3 |

**COVERAGE**
- **Checked:** `auth.py` (module constants, `_b64d`, `_rsa_verify`, `verify_token` including every `alg` branch, the exp check, the exception paths) and `test_auth.py` (all 3 tests, `sign_rs256`, the patching setup).
- **Not checked:** the key material against the real identity service, callers of `verify_token`, runtime behaviour.

**SEATS AND GATE**
- **Sensitivity gate:** passed. The work contains only a public key and a test-only key pair, no personal or confidential data.
- **Seats:** no subagent or cross-vendor seats were available. This is a local same-context review only.

---

## Pass 1: Reconstruct

`verify_token` claims to return the claims of a valid, unexpired RS256 JWT signed by the identity service, and to raise `InvalidToken` otherwise. For that to be true, all of the following must hold:
- Only RS256 is accepted.
- The RSA check is a correct PKCS#1 v1.5 / SHA-256 verification against the identity service's real key.
- Every malformed input ends in `InvalidToken`.
- Expiry is enforced.

Load-bearing assumptions:
- The header's `alg` field is not attacker-controlled in a way that matters. **This is false.**
- `PUBLIC_N`/`PUBLIC_E` are the identity service's key.
- The three tests exercise the security-relevant paths.

Tracks reviewed: B (code), with A for requirement fit.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | **Critical** | CONFIRMED (trace) | B | `auth.py` `verify_token`, `elif alg == "none": ok = True` | Unsigned tokens are accepted. This also drifts from the request, which was RS256 only. | An attacker sends header `{"alg":"none"}`, body `{"sub":"admin","exp":4102444800}` and an empty signature (`h.b.`). `split(".")` gives 3 parts, `_b64d("")` gives `b""`, `ok = True`, exp passes, and the claims are returned. This is full authentication bypass as any subject. | **Fix:** reject unless `alg == "RS256"` exactly. Remove the `none` branch. **Reproduction:** `tok = b64(b'{"alg":"none"}') + "." + b64(json.dumps({"sub":"admin","exp":2000000000}).encode()) + "."` then `auth.verify_token(tok, now=1000)`. Expected `InvalidToken`; the trace shows the claims are returned. | a✓ b✓ c✓ d✓ |
| F2 | **Critical** | CONFIRMED (trace) | B | `auth.py` `verify_token`, `elif alg == "HS256": ... hmac.new(PUBLIC_KEY_PEM.encode(), ...)` | Classic RS/HS algorithm confusion. The HMAC secret is the public key, which by definition is public. This also drifts from the request. | An attacker takes the published PEM and computes `HMAC-SHA256(pem_bytes, head+"."+body)` with header `{"alg":"HS256"}`. The token verifies for any claims. Formatting variants of the PEM, such as a trailing newline, are trivially enumerable. | **Fix:** remove the HS256 branch. Never key an HMAC with the verification key. **Reproduction:** `sig = hmac.new(auth.PUBLIC_KEY_PEM.encode(), si, hashlib.sha256).digest()` with an HS256 header, then `verify_token`. Expected `InvalidToken`; the trace shows the claims are returned. | a✓ b✓ c✓ d✓ |
| F3 | High | CONFIRMED (trace) | B | `test_auth.py` (whole suite) | No test covers `alg` dispatch, `none`, `HS256`, an unknown alg, or malformed input. The suite would stay green with F1 and F2 present, so "3 tests pass" is no evidence of security. | A regression, or the current code, ships the bypass with green CI. | Add tests: `alg:none` with an empty signature, HS256 keyed with the PEM, `alg:"RS256"` carrying an HS signature, unknown alg, missing alg, header/body that are JSON arrays, non-numeric `exp`. Each must raise `InvalidToken`. Against the current code, the `none` and HS256 tests go red; that is the confirmation that they guard something. | a✓ b✓ c✗ d✓ |
| F4 | Medium | CONFIRMED (trace) | B | `auth.py` `header.get("alg")` and `claims.get("exp", 0) < ...`, both outside the `try` | Some malformed tokens raise something other than `InvalidToken`, breaking the documented contract. A header or body that is a JSON array, string or number makes `.get` raise `AttributeError`. An `exp` of `"x"`, `null` or `[]` makes the comparison raise `TypeError`. | A caller that catches only `InvalidToken` returns a 500 (or crashes the worker) on attacker-supplied junk. This fails closed, so it is not a bypass, but it is a noisy, attacker-triggerable error path. | Check `isinstance(header, dict)` and `isinstance(claims, dict)`, and require `exp` to be an int or float (not bool); otherwise raise `InvalidToken`. **Reproduction:** a token whose body is `b64(b"[]")` with a valid signature raises `AttributeError`, not `InvalidToken`. | a✓ b✓ c✗ d✗ (legitimate tokens never hit it) |
| F5 | Low | CONFIRMED (trace) | B | `auth.py`, `if claims.get("exp", 0) < now` | A token is accepted at the exact second `exp == now`. RFC 7519 §4.1.4 says it must not be accepted "on or after" the expiration time. | A one-second window past the intended lifetime. | Use `<=`, plus an explicit, small leeway constant if clock skew matters. | a✓ b✓ c✗ d✗ |
| F6 | Low | CONFIRMED (trace) | B | `auth.py` `_b64d` (non-strict `urlsafe_b64decode`); `_rsa_verify` (no `s < n` check) | Token strings are not canonical. Non-alphabet characters in the signature segment are silently discarded, and a signature integer `s ≥ n` that still fits in k bytes reduces mod n and verifies. Many distinct strings verify for one signed token. | This only matters if anything keys on the token string, for example a revocation denylist or a replay cache: a variant string evades the list. It is not a forgery. | Decode with `base64.b64decode(..., altchars=b"-_", validate=True)` and reject `int(sig) >= n`. | a✓ b✓ c✗ d✗ |

## Needs validation

- **S1:** Is `PUBLIC_N`/`PUBLIC_E` the modulus and exponent of `PUBLIC_KEY_PEM`, and is that the identity service's current key?
  - Why it matters: the RS256 path trusts `PUBLIC_N` while the PEM is used only by the HS256 branch. If they diverge, or the key is stale, every legitimate token fails, or worse, the wrong key is trusted.
  - What settles it: parse the PEM (`cryptography`'s `load_pem_public_key(...).public_numbers()`) and compare it with the identity service's JWKS.
- **S2:** Key rotation. There is no `kid` handling and the key is hardcoded. What settles it: whether the identity service rotates keys, and how the reports API would pick up a new one.
- **S3:** Missing `iss`/`aud` checks. The request did not ask for them, so this is not drift. What settles it: whether the same identity-service key signs tokens meant for other services. If it does, those tokens would be accepted by the reports API.
- **S4:** "3 tests in test_auth.py pass" is unverified, and so is whether the test `(N, E, D)` is a valid key pair. What settles it: run `python -m unittest test_auth`.
- **S5:** Unbounded token size passed to `json.loads`. What settles it: whether an upstream proxy caps the `Authorization` header length.

## Refuted

- **R1:** "The RSA check is vulnerable to Bleichenbacher-style signature forgery." `_rsa_verify` rebuilds the entire expected encoded message (`00 01 FF… 00 DigestInfo hash`) and compares it in full with `hmac.compare_digest`. The SHA-256 DigestInfo prefix `3031300d060960864801650304020105000420` is correct, and the padding length `k − 51 − 3` gives a total of exactly k bytes. There is no parse-then-trust step to exploit.
- **R2:** "A missing `exp` means the token never expires." `claims.get("exp", 0)` defaults to 0, so a token with no `exp` is rejected as expired.
- **R3:** "Case variants like `None` or `NONE` bypass the check." The comparisons are exact strings, so variants fall to `unsupported algorithm`.

## What holds up

- The RS256 verification primitive is sound: full-EM comparison, a signature-length check, and a constant-time compare.
- The signature is checked before the claims are trusted.
- A missing `alg` or an unknown `alg` is rejected.
- Split and decode errors are wrapped as `InvalidToken`.
- `test_tampered_payload` is a meaningful test: if signature checking were removed, it would go red.

## Unverified claims

- **"3 tests pass":** run the suite.
- **"Signed by our identity service" (the key identity):** compare against the JWKS (S1).
- **The test key pair's validity:** `pow(pow(m, D, N), E, N) == m` for a sample `m`.

## Questions for the author

1. Why are the HS256 and `none` branches there at all? Is any client sending them? The answer should be no; if yes, that is a separate problem.
2. Where does `PUBLIC_N` come from, and how is it kept in sync with the identity service?
3. Could you use a vetted library instead, for example PyJWT `jwt.decode(token, key, algorithms=["RS256"])`?

## Decision-maker summary

Do not deploy. As written, any caller can forge a token for any user, either with `alg: none` or by HMAC-signing with the public key. The fix is small: accept only RS256, ideally through PyJWT with `algorithms=["RS256"]`, and add negative tests that are red on the current code. Proceeding anyway gives every internet caller full access to the reports API.

## Owner summary

The login check for the reports system can be fooled: anyone can make a fake pass that the system accepts as genuine, for any user. The part that checks real signatures is built correctly, but two extra shortcuts were added that skip the check entirely. Remove those shortcuts and add tests proving fake passes are refused before this goes live.

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
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "same-context (no subagent available)", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Public key and a test-only key pair; no personal or confidential data."},
  "coverage": {
    "checked": [
      {"unit": "auth.py", "kind": "file"},
      {"unit": "auth.py:_b64d", "kind": "function"},
      {"unit": "auth.py:_rsa_verify", "kind": "function"},
      {"unit": "auth.py:verify_token", "kind": "function"},
      {"unit": "test_auth.py", "kind": "file"},
      {"unit": "test_auth.py:sign_rs256", "kind": "function"}
    ],
    "not_checked": [
      {"unit": "identity service JWKS vs PUBLIC_N/PUBLIC_E", "reason": "not supplied; no tools"},
      {"unit": "callers of verify_token", "reason": "not supplied"},
      {"unit": "runtime test execution", "reason": "no tools in this session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:verify_token, elif alg == \"none\": ok = True",
     "scenario": "A token with header {\"alg\":\"none\"}, arbitrary claims and an empty signature is accepted, so anyone can authenticate as any subject.",
     "fix": "Reject unless alg == \"RS256\" exactly; delete the none branch (or use PyJWT with algorithms=[\"RS256\"]).",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "tok = b64(b'{\"alg\":\"none\"}') + '.' + b64(json.dumps({'sub':'admin','exp':2000000000}).encode()) + '.'; auth.verify_token(tok, now=1000) returns claims; expected InvalidToken."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:verify_token, elif alg == \"HS256\" branch using PUBLIC_KEY_PEM as HMAC key",
     "scenario": "An attacker HMAC-SHA256-signs arbitrary claims with the published PEM under an HS256 header and the token verifies (algorithm confusion).",
     "fix": "Delete the HS256 branch; never use the verification key as an HMAC secret.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Build an HS256 header and body, sig = hmac.new(auth.PUBLIC_KEY_PEM.encode(), signing_input, hashlib.sha256).digest(); verify_token returns claims; expected InvalidToken."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_auth.py (all tests)",
     "scenario": "No test covers alg dispatch or malformed input, so the suite is green while F1 and F2 allow forged tokens.",
     "fix": "Add negative tests (alg none, HS256 with the PEM, unknown or missing alg, non-dict header/body, non-numeric exp); they must be red on the current code.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Add test_alg_none asserting InvalidToken for the F1 token; it fails on the current code."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:verify_token, header.get / claims.get / exp comparison outside the try",
     "scenario": "A non-dict header or body raises AttributeError, and a non-numeric exp raises TypeError, instead of InvalidToken; callers catching only InvalidToken return 500s on attacker input.",
     "fix": "Validate that header and claims are dicts and that exp is an int or float (not bool), else raise InvalidToken.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Validly signed token with body b64(b'[]'): AttributeError raised; expected InvalidToken."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:verify_token, claims.get(\"exp\", 0) < now",
     "scenario": "A token is accepted when exp == now, contrary to RFC 7519 4.1.4 (reject on or after exp).",
     "fix": "Use <= (with an explicit leeway constant if needed).",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "verify_token(sign_rs256({'sub':'u1','exp':1000}), now=1000) returns claims; expected InvalidToken."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:_b64d (non-strict decode); auth.py:_rsa_verify (no s < n check)",
     "scenario": "Multiple distinct token strings verify for one signed token, so a string-keyed denylist or replay cache can be evaded with a variant.",
     "fix": "Use strict base64 decoding (validate=True) and reject a signature integer >= n.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Insert a non-alphabet character such as '!' into the signature segment of a valid token; it still verifies; expected InvalidToken."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py:PUBLIC_N/PUBLIC_E vs PUBLIC_KEY_PEM",
     "suspicion": "The hardcoded modulus may not match the PEM or the identity service's current key.",
     "unresolved_fact": "Whether load_pem_public_key(PEM).public_numbers() equals (PUBLIC_N, PUBLIC_E) and matches the identity service JWKS."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "auth.py:PUBLIC_N",
     "suspicion": "No kid handling or rotation path.",
     "unresolved_fact": "Whether the identity service rotates signing keys."},
    {"id": "S3", "status": "needs_validation", "track": "A", "location": "auth.py:verify_token",
     "suspicion": "Without iss/aud checks, tokens issued for other services may be accepted.",
     "unresolved_fact": "Whether the same signing key issues tokens for other audiences."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "test_auth.py",
     "suspicion": "The claim that the 3 tests pass, and the validity of the test key pair, were not observed.",
     "unresolved_fact": "Output of python -m unittest test_auth."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "auth.py:verify_token json.loads",
     "suspicion": "Unbounded token size passed to the parser.",
     "unresolved_fact": "Whether an upstream proxy caps Authorization header length."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "RSA check is vulnerable to Bleichenbacher-style forgery.",
     "evidence": "_rsa_verify rebuilds the full expected EM with the correct SHA-256 DigestInfo and compares it whole with hmac.compare_digest."},
    {"id": "R2", "candidate": "A missing exp means the token never expires.",
     "evidence": "claims.get(\"exp\", 0) defaults to 0, so the token is rejected as expired."},
    {"id": "R3", "candidate": "alg case variants (None/NONE) bypass the check.",
     "evidence": "Exact string comparison sends variants to the unsupported-algorithm path."}
  ]
}
```