VERDICT: **REWORK**. `verify_token` accepts unsigned tokens (`alg: none`) and HS256 tokens keyed with the public key, so anyone can mint a valid token for any user.

CONFIDENCE: **high** on the two Critical findings, which follow directly from reading the code. **Medium** on the rest. This was a single-reviewer, read-only review: there were no tools, so nothing was run and every trace was done by hand. The work was not written in this conversation, so there is no author-context anchoring.

INPUTS LEDGER:
- **Seen:** the original request (request.md), the context (context.md), `auth.py` and `test_auth.py` in full.
- **Not seen:**
  - The calling code in the reports API. This matters: it decides how an uncaught non-`InvalidToken` exception surfaces, and whether callers check `aud` or `iss` themselves.
  - The identity service's published key or JWKS. This matters somewhat: I could not confirm `PUBLIC_N` against the real key.
  - The test run output. The claim "3 tests pass" is taken on assertion.

SEATS AND GATE:
- One reviewer ran (this session). No subagent or cross-vendor seats were available because there were no tools.
- Sensitivity gate: passed. The file holds a public key only, with no personal data or secrets.

## Pass 1: Reconstruct

The work claims to verify RS256 JWTs from the identity service. It checks the signature against a hardcoded RSA public key, checks `exp`, and returns the claims. To be correct it must meet three conditions:
1. Only signatures made by the identity service's private key are accepted.
2. Expired tokens are rejected.
3. Every malformed input fails closed with `InvalidToken`.

The load-bearing assumptions are:
- The `alg` in the token header cannot weaken verification.
- `PUBLIC_N`/`PUBLIC_E` are the real production key.
- Callers treat any exception as a rejection.
- `exp` and signature checks alone are enough authorization for the reports API (no `aud` or `iss` check).

Track: B, with A touching on the request.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED (traced) | B | `auth.py` `verify_token`, `elif alg == "none": ok = True` | Unsigned tokens are accepted. | An attacker sends `b64({"alg":"none"}) + "." + b64({"sub":"admin","exp":9999999999}) + "."`. `split(".")` gives three parts, and `_b64d("")` returns `b""` without error. The `none` branch sets `ok = True`, `exp` is in the future, and the attacker's claims are returned. Anyone can impersonate anyone. | Delete the branch. Accept only `alg == "RS256"` and raise `InvalidToken` for everything else. Add a test that an `alg: none` token raises. | confirmed. No defense is possible: the branch is unconditional. |
| 2 | Critical | CONFIRMED (traced) | B | `auth.py` `elif alg == "HS256": ok = hmac.compare_digest(hmac.new(PUBLIC_KEY_PEM.encode(), ...))` | This is the classic RS/HS algorithm-confusion bug. The HMAC secret is the public key PEM, which is published by design and is also in this source file. | An attacker computes `HMAC-SHA256(PUBLIC_KEY_PEM, head.body)` with header `{"alg":"HS256"}` and arbitrary claims. The comparison passes and forged claims are returned. | Delete the branch, since the request specifies RS256 only. Add a test that an HS256 token keyed with `PUBLIC_KEY_PEM` raises. | confirmed. The key is public by definition, so the forgery needs no secret. |
| 3 | High | CONFIRMED (by the fact that Findings 1 and 2 exist while the suite is green) | B | `test_auth.py` (whole suite) | The tests cover only the happy path, expiry and payload tamper. No test sends another `alg`, an empty signature or a wrong key. `setUp` patches `PUBLIC_N`/`PUBLIC_E`, so the production key is never exercised. "3 tests pass" says nothing about the two Critical holes. | A future change reintroduces or keeps an algorithm bypass and CI stays green. A wrong `PUBLIC_N` in production would also pass every test. | Add negative tests: `alg` set to `none`, `HS256`, `RS512`, `None`/missing; empty signature; a signature from a different key; `s >= n`. Add a test that `PUBLIC_N`/`PUBLIC_E` equal the modulus and exponent parsed from `PUBLIC_KEY_PEM`. Mutation check (not run here): change `return hmac.compare_digest(...)` in `_rsa_verify` to `return True`. Only `test_tampered_payload` should go red, which shows one test guards the RSA check. | confirmed. |
| 4 | High | CONFIRMED (traced) | B | `auth.py` `alg = header.get("alg")` and `claims.get("exp", 0) < ...` are outside the `try` | Non-object JSON escapes as a non-`InvalidToken` exception. A header of `[]` or `1` raises `AttributeError` before any signature check, so this is reachable unauthenticated. An `exp` of `"x"` or `[]` raises `TypeError`. While Finding 1 is open, an attacker can reach that too. | If the caller catches only `InvalidToken`, attacker input produces 500s and possibly stack traces in responses or logs. If a caller wraps the call in a broad `except` that fails open, this becomes an auth bypass (UNVERIFIED: caller not seen). | Require `isinstance(header, dict)` and `isinstance(claims, dict)`. Require `exp` to be an `int`/`float`, not a `bool`, and finite. Raise `InvalidToken` otherwise. Add tests for header `[]`, a missing `exp` and a string `exp`. | confirmed. Lowered from Critical: the fail-open outcome depends on caller code that was not seen. |
| 5 | Medium | PROBABLE | A/B | `auth.py` `verify_token`: no `aud`, `iss` or `nbf` check | The request asks only for signature and expiry, so this is not drift. But the identity service very likely signs tokens for other services with the same key. | A valid token issued for another internal service (or another audience) is accepted by the reports API. | Ask the author or identity team whether tokens are audience-scoped. If they are, check `aud` and `iss` against expected values. | n/a (Medium) |
| 6 | Medium | PROBABLE | B | `auth.py` `PUBLIC_N` and `PUBLIC_KEY_PEM` are hardcoded constants | There is no key rotation, `kid` handling or JWKS fetch. The key exists in two hand-kept forms. | The identity service rotates its key and every token fails, causing an outage until a redeploy. The two constants drift apart. The PEM is used only by the HS256 path, so after the fix for Finding 2 it is dead code. | Load the key from configuration or JWKS with `kid` matching, derive `n`/`e` from one source, and remove the unused PEM or derive from it. | n/a |
| 7 | Low | CONFIRMED (traced) | B | `auth.py` `_rsa_verify`, `pow(int.from_bytes(signature,"big"), e, n)` | The code does not reject a signature representative `s >= n` (RFC 8017 §8.2.2 / RSAVP1 step 1). | `s` and `s + n`, when it fits in k bytes, both verify. That allows signature malleability (token-string uniqueness or replay caches keyed on the raw token) but not forgery. | `if int.from_bytes(signature,"big") >= n: return False`. | n/a |
| 8 | Low | CONFIRMED (traced) | B | `auth.py` `claims.get("exp", 0) < now` | `exp == now` is accepted, while RFC 7519 §4.1.4 requires the current time to be *before* `exp`. Python's `json` also accepts `NaN` and `Infinity`, and `NaN < now` is False, so the token never expires. | Off by one second at the boundary. An issuer bug emitting `NaN` would create a non-expiring token. | Use `<=`, reject non-finite `exp`, and consider a small explicit leeway. | n/a |

### Pass 3 results

- **Withdrawn:** none. The two Critical findings and Finding 3 were confirmed against the code text. Finding 4 was downgraded from Critical to High because the fail-open path depends on unseen callers.
- **Most serious possible miss:** how callers use the returned claims, for example authorizing on `sub` or `scope` without checks. That code was not supplied.

## What holds up

- `_rsa_verify` is a sound PKCS#1 v1.5 verifier.
  - It checks the signature length equals k.
  - It reconstructs the *entire* encoded message, with the correct SHA-256 DigestInfo prefix `3031300d...0420`.
  - It compares with `hmac.compare_digest` instead of parsing the padding. That avoids the Bleichenbacher-style lax-parsing forgeries.
- The signing input uses the raw base64 segments, which is correct.
- Decode errors inside the `try` map to `InvalidToken`.
- The leading digits of `PUBLIC_N` (≈2.2728×10⁶¹⁶) match the PEM modulus prefix `0xB40A5F…` (0.70328 × 2²⁰⁴⁸ ≈ 2.2728×10⁶¹⁶). This is PROBABLE consistency only; I did not check the full value.
- `test_tampered_payload` does exercise the RSA check.

## Unverified claims

- **"3 tests pass":** not run. Settle it by running `python -m unittest test_auth`.
- **`PUBLIC_N` equals the production identity-service modulus:** settle it by comparing with the service's JWKS or PEM using `cryptography`'s `load_pem_public_key(...).public_numbers().n`.
- **Caller exception handling:** settle it by reading the reports API's auth middleware.

## Questions for the author

1. Why were the `HS256` and `none` branches added, and does anything depend on them? The expected answer is no, and they should go.
2. Does the identity service issue tokens for other audiences with this key? If so, which `aud`/`iss` must the reports API require?
3. How does the caller handle exceptions other than `InvalidToken` from `verify_token`?

## Decision-maker summary

Do not ship this. As written, anyone can forge a token for any user in two different ways (an unsigned token, or one keyed with the published public key), and the passing tests do not detect either. Remove both branches, add negative tests, and type-check the decoded JSON; the RSA verification core itself is sound and can stay.

## Owner summary

The new login check for the reports system has two gaps. Each would let anyone on the internet pretend to be any user without a real credential. The existing tests pass because they never try these tricks. The fix is small (delete the two unsafe shortcuts and add tests for them), and it should be done before this goes live.

```json
{
  "verdict": "REWORK",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "auth.py", "status": "seen", "matters": true},
    {"item": "test_auth.py", "status": "seen", "matters": true},
    {"item": "reports API caller / middleware", "status": "not_seen", "matters": true},
    {"item": "identity service public key / JWKS", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "public key only; no personal data or secrets"},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "auth.py verify_token: elif alg == \"none\": ok = True",
     "scenario": "Attacker sends header {\"alg\":\"none\"}, arbitrary claims, empty signature; _b64d(\"\") returns b\"\", ok=True, forged claims returned: full impersonation.",
     "fix": "Accept only alg == \"RS256\"; raise InvalidToken otherwise; add a test that alg none is rejected.", "status": "confirmed"},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "auth.py verify_token: elif alg == \"HS256\" using PUBLIC_KEY_PEM as HMAC key",
     "scenario": "Attacker computes HMAC-SHA256 over head.body with the public PEM (public by design) and header alg HS256; the signature check passes for arbitrary claims.",
     "fix": "Remove the HS256 branch; add a test that an HS256 token keyed with the PEM is rejected.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "test_auth.py (whole suite; setUp patches PUBLIC_N/PUBLIC_E)",
     "scenario": "The suite is green while the alg-none and HS256 bypasses exist, and it never exercises the production key, so regressions and a wrong prod key go undetected.",
     "fix": "Add negative tests for alg none/HS256/other/missing, empty signature, wrong-key signature and s >= n, plus a test that PUBLIC_N/E match the PEM.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "auth.py verify_token: header.get / claims.get(\"exp\") outside try",
     "scenario": "Header JSON [] raises AttributeError before signature check, and a non-numeric exp raises TypeError; non-InvalidToken exceptions cause 500s or fail open in a broadly-catching caller.",
     "fix": "Require dict header/claims and numeric, finite, non-bool exp; raise InvalidToken otherwise; add tests.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "A", "location": "auth.py verify_token: no aud/iss/nbf checks",
     "scenario": "A token the identity service issued for another service is accepted by the reports API.",
     "fix": "Confirm audience scoping with the identity team; validate aud and iss if tokens are shared across services.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "auth.py PUBLIC_KEY_PEM / PUBLIC_N constants",
     "scenario": "Key rotation by the identity service rejects every token until a redeploy; the two key representations can drift apart.",
     "fix": "Load the key from config/JWKS with kid matching; derive n/e from a single source.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "auth.py _rsa_verify: pow(int.from_bytes(signature), e, n)",
     "scenario": "Signature representative s >= n is not rejected (RFC 8017 RSAVP1), so s and s+n both verify: malleability, not forgery.",
     "fix": "Return False if int.from_bytes(signature, \"big\") >= n.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "auth.py verify_token: claims.get(\"exp\", 0) < now",
     "scenario": "exp == now is accepted, contrary to RFC 7519 4.1.4; a NaN exp from an issuer bug never expires.",
     "fix": "Use <= and reject non-finite exp.", "status": "n/a"}
  ]
}
```