# Redteam review: `auth.py` token verification for the reports API

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** This session had no tools, so nothing was run. Every finding comes from reading and tracing the code by hand.

VERDICT: **SHIP WITH FIXES**. The cryptographic core is correct: full PKCS#1 v1.5 encoding comparison, alg pinned before verification, iss/aud/exp checked. Before production, one input-handling gap and one key-provenance hazard need fixing, and the author must confirm that `ISSUER` and the key are the production identity service's values.

CONFIDENCE: **medium**. Limits: no tools, so the 7 tests were not run and `PUBLIC_N` was not decoded against the PEM. The identity service's real issuer, audience format, `exp` format and key-rotation policy were not supplied.

INPUTS LEDGER:
- Seen: `request.md`, `context.md`, `auth.py`, `test_auth.py`.
- Not seen: the identity service's published key or JWKS, real issuer, `aud` format and rotation policy. **This matters**, because correctness in production depends on them.
- Not seen: the reports-API caller that invokes `verify_token` and decides how exceptions map to HTTP responses. **This matters** for F1.
- Not seen: the output of the 7 passing tests. It matters little, since the tests were traced by hand.

COVERAGE:
- Checked: `auth.py` (`_b64d`, `_rsa_verify`, `verify_token`, constants) and `test_auth.py` (all 7 tests plus `sign_rs256` and `forge`).
- Not checked: the caller and middleware, deployment config, and an actual run of the tests.

SEATS AND GATE: One reviewer (this session, no subagent available). No cross-vendor seats. The sensitivity gate passed. The work contains a public key and a test-only private key (`D` in `test_auth.py`, which belongs to a different, 1024-bit modulus, not the production key), and no personal or confidential data.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED | B | `auth.py:46,51` | The header is parsed inside `try`, but `header.get(...)` runs outside it. A header that is valid JSON but not an object (`[]`, `1`, `"x"`) raises `AttributeError`, not `InvalidToken`. This happens before any signature check, so any unauthenticated caller can trigger it. | An attacker sends `W10.e30.AAAA` (header `[]`). `verify_token` raises `AttributeError`. A caller that catches only `InvalidToken` returns a 500 and logs a traceback for every such request. It fails closed, so access is still denied. | Inside `try`, add `if not isinstance(header, dict) or not isinstance(claims, dict): raise ValueError`. Repro test: `assertRaises(InvalidToken, verify_token, "W10.e30.AAAA", now=1000)`. It currently errors with `AttributeError`. | a✓ b✓ c✗ d✗ |
| F2 | Medium | CONFIRMED | B | `auth.py:8-19` | There are two sources of truth for the trust anchor. `PUBLIC_KEY_PEM` is never parsed by `auth.py` (only `test_auth.py` uses it, as an HMAC secret). Verification uses the hand-copied `PUBLIC_N`/`PUBLIC_E`. The leading digits and the 617-digit length of `PUBLIC_N` are consistent with the PEM's modulus (which starts `0xB40A5F…`), but full equality is not checked anywhere. | The identity service rotates its key, perhaps after a compromise. A maintainer pastes the new PEM, which is the obvious edit. `PUBLIC_N` is unchanged, so the API keeps accepting tokens signed with the old, possibly compromised, key and rejects the new ones. | Derive `n` and `e` from the PEM at import (for example with `cryptography`'s `load_pem_public_key(...).public_numbers()`), or delete the PEM. Add a test asserting that the PEM's modulus equals `PUBLIC_N`. | a✓ b✓ c✗ d✗ |
| F3 | Low | CONFIRMED | B | `test_auth.py`: `test_alg_none_is_refused`, `test_hs256_signed_with_the_public_key_is_refused` | Neither test guards the `alg` check at `auth.py:51`. Both forged signatures (0 bytes and 32 bytes) are already rejected by `len(signature) != k` at `auth.py:33`. Deleting the alg check leaves both tests green, so their names overstate coverage. | Someone refactors and drops the alg check, believing the tests cover it. The tests stay green. Today the signature check still blocks these forgeries, so the harm is to the test signal only. | Add a test with a *valid* RS256 signature over a header carrying `"alg":"HS256"`, which must be refused. Mutation check: delete lines 51-52; the new test must go red and the old two will not. | a✓ b✓ c✗ d✗ |
| F4 | Low | CONFIRMED | B | `auth.py:56` | `exp < now` accepts a token at exactly `now == exp`. RFC 7519 §4.1.4 requires the current time to be *before* `exp`. | With `now=1000` and `exp=1000`, the token is accepted for one extra second. | Use `exp <= now`. Repro: sign `{**CLAIMS, "exp": 1000}` and verify with `now=1000`; expect `InvalidToken`, observe success. | a✓ b✓ c✗ d✗ |
| F5 | Low | CONFIRMED | B | `auth.py:35` | Signatures with `s >= n` are not rejected (RFC 8017 §8.2.2 requires rejection). `pow` reduces mod n, so `s + n` (which still fits in k bytes, since n ≈ 0.70·2²⁰⁴⁸) is a second valid encoding. This allows malleability, not forgery. | Any replay cache, revocation list or log deduplication keyed on the raw token string can be bypassed by re-encoding the signature as `s + n`. | Reject when `int.from_bytes(signature,"big") >= n`. Repro: take a valid token, replace its signature with `(s+n).to_bytes(k)`, and verify. It is currently accepted; it should be refused. | a✓ b✓ c✗ d✗ |

## Needs validation

- **S1 (most important).** `ISSUER = "https://id.example.test"` uses the `.test` TLD, which is reserved for testing (RFC 6761). The unresolved fact: is this the production identity service's actual `iss`, and is the PEM its actual signing key? If either is a placeholder, every real token is rejected in production (fail-closed outage), or the API trusts the wrong key.
- **S2.** `aud` is compared with `!=` against a string. RFC 7519 allows `aud` to be an array. The unresolved fact: does the identity service ever issue `"aud": ["reports-api", …]`? If so, all of those tokens are rejected.
- **S3.** `isinstance(exp, int)` rejects non-integer NumericDates (for example `1.7e9`), which RFC 7519 permits. The unresolved fact: does the identity service emit integer `exp`?
- **S4.** A single hardcoded key with `kid` ignored means any rotation needs a coordinated redeploy. The unresolved fact: the identity service's rotation policy, and whether it publishes a JWKS.
- **S5.** There is no clock-skew leeway, and `nbf` and `crit` are not handled. The unresolved fact: whether the identity service sets `nbf` or `crit`, and the clock-sync guarantees between the two hosts.
- **S6.** "7 tests pass" was not run here. The unresolved fact: the output of `python3 -m unittest test_auth`.

## Refuted

- **R1: "Algorithm confusion: HS256 signed with the public key is accepted."** Refuted. `auth.py:51` rejects any `alg` other than RS256, and the key is fixed rather than chosen from the header.
- **R2: "Lax PKCS#1 parsing allows Bleichenbacher-style forgery."** Refuted. `auth.py:37` compares the *entire* expected encoding (`00 01 FF… 00 DigestInfo hash`) in constant time. Nothing is parsed. The DigestInfo prefix `3031300d0609608648016503040201050004 20` is the correct SHA-256 prefix, and the padding length `k - 51 - 3` is correct.
- **R3: "Malformed input escapes as a non-`InvalidToken` exception from split or decode."** Refuted for the split, base64 and JSON steps: wrong part counts, non-str tokens, bad base64 and bad JSON are all inside the `try`. The non-object case is real and is F1.

## What holds up

- Signature verification is a correct, constant-time, full-encoding RSASSA-PKCS1-v1_5/SHA-256 check with a length check.
- `alg` is pinned to RS256. Header fields `kid`, `jku` and `x5u` are ignored, so the header cannot choose the key.
- Claims are evaluated only after the signature passes, and expiry is mandatory (a missing `exp` is refused).
- The iss/aud checks go beyond the request but are correct defense in depth.
- The tests for a valid token, a tampered payload, a wrong key, expiry and iss/aud would each go red if the guarded check were removed (traced by hand, not run).

## Unverified claims

- "7 tests in test_auth.py pass": run them.
- `PUBLIC_N` equals the PEM modulus: decode the PEM and compare.
- The PEM and `ISSUER` are the production identity service's values: compare them with the service's published JWKS or discovery document.

## Questions for the author

1. Are `ISSUER` and `PUBLIC_KEY_PEM` the production identity service's real values, and where are they published?
2. Does the service ever issue an array `aud` or a non-integer `exp`?
3. How does the service rotate keys, and is there a JWKS endpoint?

## Decision-maker summary

The verification logic is sound and resists the classic JWT attacks. Fix F1 (unhandled exception on a crafted header) and F2 (the unused PEM next to a hand-copied modulus) before production. The deploy-blocking question is S1: confirm the hardcoded issuer and key are the production identity service's. If they are placeholders, shipping means either every real user is locked out or the API trusts the wrong key.

## Owner summary

The core security check works and blocks the well-known ways of faking these tokens. Two small fixes are needed: one stops malformed requests from causing server errors, and one stops a future key change from being silently ignored. Someone also needs to confirm that the built-in issuer name and key match the real identity service, because the issuer looks like a test placeholder.

```json
{
  "schema_version": "2.2",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "identity service real issuer, public key/JWKS, aud and exp format, rotation policy", "status": "not_seen", "matters": true},
    {"item": "reports-API caller / exception handling", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
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
      {"unit": "caller of verify_token", "reason": "not supplied"},
      {"unit": "test execution", "reason": "no tools in session"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:46,51",
     "scenario": "Unauthenticated token 'W10.e30.AAAA' (header []) makes header.get raise AttributeError instead of InvalidToken; callers catching only InvalidToken return 500.",
     "fix": "Inside the try, require header and claims to be dicts; raise InvalidToken otherwise.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "verify_token('W10.e30.AAAA', now=1000): expect InvalidToken, observe AttributeError."},
    {"id": "F2", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:8-19",
     "scenario": "PUBLIC_KEY_PEM is never parsed; verification uses hand-copied PUBLIC_N. On rotation a maintainer updates the PEM only, and the API keeps trusting the old key.",
     "fix": "Derive n and e from the PEM at import, or delete the PEM; add a test asserting PEM modulus == PUBLIC_N.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Replace PUBLIC_KEY_PEM with a different key; verification behavior is unchanged."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_auth.py:test_alg_none_is_refused, test_hs256_signed_with_the_public_key_is_refused",
     "scenario": "The forged signatures fail the length check at auth.py:33, so deleting the alg check at auth.py:51 leaves both tests green.",
     "fix": "Add a test with a valid RS256 signature over a header claiming alg HS256.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Delete auth.py:51-52 in a scratch copy; both tests still pass."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:56",
     "scenario": "A token with exp == now is accepted; RFC 7519 requires now < exp.",
     "fix": "Use exp <= now.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Sign exp=1000 and verify with now=1000: accepted; should be refused."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:35",
     "scenario": "A signature s+n (still k bytes) verifies, so one token has two valid encodings, defeating replay or revocation caches keyed on the token string.",
     "fix": "Reject when int.from_bytes(signature,'big') >= n.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Re-encode a valid token's signature as (s+n).to_bytes(k,'big'): accepted; should be refused."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py:8-19,38",
     "suspicion": "ISSUER uses the reserved .test TLD; the issuer and key may be placeholders.",
     "unresolved_fact": "The production identity service's actual iss value and signing key."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "auth.py:58",
     "suspicion": "An array-valued aud would be rejected.",
     "unresolved_fact": "Whether the identity service issues aud as an array."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "auth.py:56",
     "suspicion": "A non-integer exp would be rejected.",
     "unresolved_fact": "Whether the identity service emits integer exp."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "auth.py:18-19",
     "suspicion": "A single hardcoded key with kid ignored breaks on rotation.",
     "unresolved_fact": "The identity service's key rotation policy and JWKS availability."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "auth.py:55-57",
     "suspicion": "No clock-skew leeway; nbf and crit not handled.",
     "unresolved_fact": "Whether tokens carry nbf or crit, and the clock-sync guarantees between hosts."},
    {"id": "S6", "status": "needs_validation", "track": "B", "location": "test_auth.py",
     "suspicion": "The claim that the 7 tests pass was not run.",
     "unresolved_fact": "The output of python3 -m unittest test_auth."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "HS256 algorithm confusion is accepted.", "evidence": "auth.py:51 rejects any alg other than RS256; the key is fixed, not chosen from the header."},
    {"id": "R2", "candidate": "Lax PKCS#1 parsing allows signature forgery.", "evidence": "auth.py:37 compares the full expected encoding in constant time; the DigestInfo prefix and padding length are correct."},
    {"id": "R3", "candidate": "Malformed split, base64 or JSON escapes as a non-InvalidToken exception.", "evidence": "Those steps are inside the try at auth.py:44-50; only the non-object case escapes (F1)."}
  ]
}
```