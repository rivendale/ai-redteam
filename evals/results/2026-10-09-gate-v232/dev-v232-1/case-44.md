# Redteam report: `auth.py` token verification for the reports API

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No subagent and no tools were available, so I traced the code by hand and ran nothing. Line numbers are counted from the supplied text.

VERDICT: **SHIP WITH FIXES.** The signature check itself looks sound: it compares the full encoded message, pins the algorithm and checks the length. No Critical or High was confirmed. Before production, fix one unhandled-exception path and confirm that the hardcoded key, issuer and audience are the real production values.

CONFIDENCE: **medium-low.** I could not run the 7 tests or check that `PUBLIC_N` matches the PEM and the identity service's real key. The production `ISSUER` value is on the reserved `.test` domain, which looks like a placeholder.

INPUTS LEDGER:
- **Seen:** `request.md`, `context.md`, `auth.py`, `test_auth.py`.
- **Not seen:**
  - The identity service's real public key or JWKS, and its real `iss`/`aud` values. **This matters**: the verdict depends on them.
  - Any token issued by the real service, which would show the shape of `aud` (string or array) and `exp` (integer or float). **This matters.**
  - The calling code that handles exceptions from `verify_token`. **This matters** for the severity of F1.
  - The test run output. "7 tests pass" is unverified.

COVERAGE:
- **Scope:** the whole work, which is two files.
- **Checked:** `auth.py` (`_b64d`, `_rsa_verify`, `verify_token`, the constants); `test_auth.py` (all 7 tests, by reasoning about which mutation each one would catch); `request.md`; `context.md`.
- **Not checked:**
  - Whether `PUBLIC_N` equals the PEM modulus. I only checked by hand that the leading bytes are consistent (0xB40A5F…). Reason: `no_tools`.
  - Whether the key and issuer are production values. Reason: `not_supplied`.
  - The callers of `verify_token`. Reason: `not_supplied`.
  - Executing the tests. Reason: `no_tools`.

SEATS AND GATE: Only a local, same-context reviewer ran. No cross-vendor seats were requested. The sensitivity gate passed: the PEM is a public key, and the private exponent `D` in the tests is a test-only key, not production material.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (traced) | B | `auth.py:51` `if header.get("alg") != "RS256"` | `header` is never checked to be a dict. A JSON list, string or number header raises `AttributeError` outside the `try` block, and this happens before any signature check. The same flaw exists for `claims.get` (lines 55 and 58), but only a correctly signed token reaches those. | Any unauthenticated caller sends a token whose header decodes to `[]`. `verify_token` raises `AttributeError` instead of `InvalidToken`. The caller likely returns a 500, logs noisy errors, or behaves however its broad exception handler is written. | **Fix:** inside the `try`, require `isinstance(header, dict) and isinstance(claims, dict)`, otherwise raise `InvalidToken`. **Repro:** `verify_token(b64(b"[]") + "." + b64(b"{}") + ".AA")`. Expected `InvalidToken`; observed `AttributeError: 'list' object has no attribute 'get'`. | a✓ b✓ c✗ d✗ |
| F2 | Low | CONFIRMED (math) | B | `auth.py:35` `pow(int.from_bytes(signature,"big"), e, n)` | The code never rejects a signature integer s ≥ n (RFC 8017 §8.2.2 requires s < n). So s and s+n both verify. | Someone holding a valid token can mint a second, different token string with the same claims. Because the leading byte of n is 0xB4, s+n stays within k bytes for roughly 40% of tokens. Anything keyed on the token string (a revocation list, replay cache or per-token rate limit) can then be bypassed. | **Fix:** `s = int.from_bytes(...)`, then `if s >= n: return False`. **Repro:** take a valid test token, compute `s2 = s + N`, re-encode it to k bytes and substitute it. Expected rejection; observed acceptance. | a✓ b✓ c✗ d✗ |
| F3 | Low | CONFIRMED (stdlib behavior) | B | `auth.py:27` `base64.urlsafe_b64decode(...)` | Decoding runs with `validate=False`. It silently drops characters outside the base64 alphabet and accepts non-canonical trailing bits. | This only matters for the signature segment, because the signed message uses the raw header and body text. Inserting junk characters into the signature segment yields another distinct, valid token string, with the same consequences as F2. | **Fix:** reject any segment that does not match `^[A-Za-z0-9_-]*$`, or decode with `validate=True` after translating the alphabet. **Repro:** insert `"!"` into the middle of the signature segment of a valid test token. Expected `InvalidToken`; observed acceptance. | a✓ b✓ c✗ d✗ |
| F4 | Low | CONFIRMED (traced) | B | `auth.py:56` `exp < now` | RFC 7519 §4.1.4 says the current time must be *before* `exp`. Here a token is accepted when `exp == now`. | This is an off-by-one at the exact expiry second. It is mostly visible when `now` is an integer. | **Fix:** use `exp <= now`. **Repro:** `verify_token(sign_rs256(CLAIMS), now=2000000000)`. Expected `InvalidToken`; observed the claims are returned. | a✓ b✓ c✗ d✗ |
| F5 | Low | CONFIRMED (traced) | B | `test_auth.py`: `test_alg_none_is_refused`, `test_hs256_...`, `test_token_signed_by_another_key_is_refused` | These three tests pass even if the line-51 `alg` check is deleted. Their signatures are 0, 32 and 128 bytes, so the length check on line 33 rejects them first. They have never isolated the control they are named after. No test exercises malformed or non-dict input, which is why F1 went unnoticed. | Someone later removes or weakens the `alg` check and CI stays green. | **Fix:** add a test that sends a correctly RS256-signed token with header `alg: "PS256"` and expects rejection. Add malformed-input tests. **Repro:** in a scratch copy, delete lines 51–52 and run the tests: all 7 still pass. | a✓ b✓ c✗ d✗ |

## NEEDS VALIDATION

These are suspicions I could not settle. They carry no severity and did not set the verdict.

- **S1, the issuer value** (`auth.py:38`). `ISSUER = "https://id.example.test"` uses the reserved `.test` TLD, which suggests a placeholder.
  - **Fact that settles it:** the real identity service's `iss`.
  - **If it is a placeholder:** every production token is rejected. The system fails closed, which means a full outage, and that would be High.
- **S2, the public key** (`auth.py:8–19`). `PUBLIC_N` should be the identity service's real key and should equal the PEM modulus. The PEM is never used by the verify path, so the two are separate sources of truth. The leading bytes are consistent, but I did not check the full value.
  - **Fact that settles it:** compare `PUBLIC_N` with the modulus in the service's published key or JWKS.
- **S3, the shape of `aud`.** RFC 7519 allows `aud` to be an array. If the service issues `["reports-api"]`, every valid token is rejected.
  - **Fact that settles it:** one real token.
- **S4, the type of `exp`.** A float `exp` (such as `1.7e9`) is rejected by the `isinstance(exp, int)` check.
  - **Fact that settles it:** what the service emits.
- **S5, key rotation.** There is a single hardcoded key, with no `kid` or JWKS handling. If the service rotates keys, every token fails until a redeploy.
  - **Fact that settles it:** the identity service's rotation policy.

## REFUTED

- **Bleichenbacher-style forgery with a small exponent or a lax parser.** Refuted: line 37 compares the entire expected encoded message, padding included, not a parsed digest.
- **Algorithm confusion (`none`, or HS256 signed with the public key).** Refuted: the code has no algorithm dispatch. It always performs RSA verification, and line 51 pins RS256.
- **Malformed-input crashes in decoding.** Refuted except for F1: `split`, `b64decode` and `json.loads` errors, including deep-nesting `RecursionError` and the int-digit-limit `ValueError`, are all `Exception` subclasses and are caught on line 49.
- **`now=0` falls through to the wall clock.** Refuted: the code uses `is not None`.

## WHAT HOLDS UP

- The PKCS#1 v1.5 verification is correct for SHA-256: the DigestInfo prefix is right, the padding length is `k - len(info) - 3`, the comparison is exact and length is checked.
- Expiry is enforced, and a missing or non-integer `exp` is rejected (`bool` values are rejected because they evaluate as expired).
- The issuer and audience checks go beyond the request in a useful way.
- `test_tampered_payload_is_refused` really does guard the signature math.

## UNVERIFIED CLAIMS

- **"7 tests in test_auth.py pass."** Run `python -I -m unittest test_auth` in an isolated copy.
- **The `PUBLIC_KEY_PEM` / `PUBLIC_N` constants are the identity service's key.** See S2.

## QUESTIONS FOR THE AUTHOR

1. What are the production `iss` and `aud` values, and is `aud` ever an array?
2. Was `PUBLIC_N` derived from this PEM, and is this PEM the service's current signing key? Does the service rotate keys?
3. Why hand-roll RSA instead of using `cryptography` or PyJWT with `algorithms=["RS256"]`? The hand-rolled version is correct here, but it is code you now own.

## DECISION-MAKER SUMMARY

The cryptographic core holds. Fix F1 to F4, which are small patches, and add the missing tests (F5). The blocking unknown is whether the hardcoded issuer and key are real production values. If they are placeholders, the API will reject every caller on day one.

## OWNER SUMMARY

The signature check that decides who can call the reports service appears sound, and I found no way to forge access. There are a few small fixes, mainly one input that causes an error instead of a clean rejection. Before launch, someone must confirm that the built-in key and issuer name match the real login service, because one of them looks like a placeholder.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "low",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "auth.py", "status": "seen", "matters": true},
    {"item": "test_auth.py", "status": "seen", "matters": true},
    {"item": "identity service public key / JWKS and real iss/aud", "status": "not_seen", "matters": true},
    {"item": "sample production token", "status": "not_seen", "matters": true},
    {"item": "callers of verify_token", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context-self", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Only a public key and a test-only private key are present."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "auth.py", "kind": "file"},
      {"unit": "auth.py:_b64d", "kind": "function"},
      {"unit": "auth.py:_rsa_verify", "kind": "function"},
      {"unit": "auth.py:verify_token", "kind": "function"},
      {"unit": "test_auth.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "PUBLIC_N equals PEM modulus (full value)", "reason": "no_tools"},
      {"unit": "production iss/aud/key values", "reason": "not_supplied"},
      {"unit": "callers of verify_token", "reason": "not_supplied"},
      {"unit": "test execution", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:51",
     "scenario": "An unauthenticated token whose header decodes to a JSON list makes header.get raise AttributeError before the signature check, so the caller gets an unhandled exception instead of InvalidToken.",
     "fix": "Inside the try block, require header and claims to be dicts; otherwise raise InvalidToken.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "verify_token(b64(b'[]') + '.' + b64(b'{}') + '.AA'): expected InvalidToken, observed AttributeError."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:35",
     "scenario": "The signature integer is not required to be below n, so s+n also verifies; a holder of a valid token can mint a distinct token string with the same claims and bypass any denylist or replay cache keyed on the token string.",
     "fix": "Reject the signature if int.from_bytes(signature) >= n.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Replace the signature s of a valid test token with s+N encoded to k bytes: expected rejection, observed acceptance."},
    {"id": "F3", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:27",
     "scenario": "urlsafe_b64decode discards non-alphabet characters, so junk inserted into the signature segment still yields a valid token under a different string.",
     "fix": "Validate each segment against ^[A-Za-z0-9_-]*$ before decoding.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Insert '!' into the middle of the signature segment of a valid test token: expected InvalidToken, observed acceptance."},
    {"id": "F4", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:56",
     "scenario": "A token is accepted when exp equals now, although RFC 7519 requires the current time to be before exp.",
     "fix": "Use exp <= now.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "verify_token(sign_rs256(CLAIMS), now=2000000000): expected InvalidToken, observed the claims returned."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_auth.py: test_alg_none_is_refused, test_hs256_signed_with_the_public_key_is_refused, test_token_signed_by_another_key_is_refused",
     "scenario": "The signature length check rejects these tokens first, so deleting the alg check leaves every test green; no test covers malformed or non-dict input.",
     "fix": "Add a test with a correctly RS256-signed token whose header says PS256, plus malformed-input tests.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "In a scratch copy, delete auth.py lines 51-52 and run the tests: all 7 still pass."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py:38",
     "suspicion": "ISSUER is on the reserved .test TLD and is likely a placeholder, which would reject all production tokens.",
     "unresolved_fact": "The identity service's real iss value."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "auth.py:8-19",
     "suspicion": "PUBLIC_N may not equal the PEM or the service's real key; the PEM is unused by the verify path.",
     "unresolved_fact": "The modulus in the service's published key or JWKS compared with PUBLIC_N."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "auth.py:58",
     "suspicion": "An aud issued as an array would be rejected.",
     "unresolved_fact": "The aud format in a real token."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "auth.py:56",
     "suspicion": "A float exp would be rejected.",
     "unresolved_fact": "The exp type the service emits."},
    {"id": "S5", "status": "needs_validation", "track": "B", "location": "auth.py:18-19",
     "suspicion": "A single hardcoded key causes an outage when the service rotates keys.",
     "unresolved_fact": "The identity service's key rotation policy."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "PKCS#1 v1.5 forgery through lax padding parsing.", "evidence": "Line 37 compares the full expected encoded message byte for byte."},
    {"id": "C2", "candidate": "alg none or HS256 key confusion.", "evidence": "There is no algorithm dispatch: RSA verification always runs, and line 51 pins RS256."},
    {"id": "C3", "candidate": "Decoding errors escape as non-InvalidToken exceptions.", "evidence": "The try/except Exception on lines 44-50 covers split, b64decode and json.loads; only the post-try .get calls in F1 escape."},
    {"id": "C4", "candidate": "now=0 falls back to the wall clock.", "evidence": "The code tests 'now is not None'."}
  ]
}
```