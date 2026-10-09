VERDICT: SHIP WITH FIXES. The cryptographic core is correct, with a full PKCS#1 v1.5 encoded-message comparison, an RS256-only check and signature verification before claims are trusted. One unauthenticated input escapes the function's error contract, and the hardcoded issuer needs confirming before production.

CONFIDENCE: medium. Limits:
- No tools: nothing was run and the 7 passing tests are unverified.
- Same-context review with no fresh subagent available. The work was not written in this conversation, so the anchoring risk is lower, but this is still a single unindependent reviewer.
- The identity service's real issuer, audience and token format were not supplied.

INPUTS LEDGER:
- Seen: `request.md`, `context.md`, `auth.py`, `test_auth.py`.
- Not seen: a test run log (matters: "7 tests pass" is unverified); the identity service's real public key, `iss` and `aud` values and its `exp` and `aud` encoding (matters: the hardcoded values decide whether real tokens are accepted); the caller in the reports API (matters: it decides what a non-`InvalidToken` exception does).

COVERAGE:
- Scope: the whole work (2 files).
- Checked:
  - `auth.py`: `_b64d`, `_rsa_verify`, `verify_token`, and the `PUBLIC_KEY_PEM`/`PUBLIC_N` consistency, decoded by hand at both ends of the modulus.
  - `test_auth.py`: all 7 tests, `sign_rs256` and `forge`.
  - `request.md` and `context.md`.
- Not checked: execution of anything (no tools); the full middle bytes of the modulus (by-hand decoding only covered the ends); the caller code (not supplied).

SEATS AND GATE: one local same-context reviewer ran. No cross-vendor seats were requested and none were available. Sensitivity gate passed: the only key material is a public key, so nothing sensitive is present.

## Pass 1: Reconstruct

`verify_token` claims to accept only RS256 JWTs signed by the identity service's key, reject expired tokens or tokens with no expiry, and return the claims. It also checks `iss` and `aud`, which the request did not ask for. For it to be correct:
1. `PUBLIC_N`/`PUBLIC_E` must be the identity service's real key.
2. `_rsa_verify` must implement PKCS#1 v1.5 with SHA-256 exactly.
3. Every malformed input must end in `InvalidToken`.
4. The hardcoded `ISSUER` and `AUDIENCE` must match what the service actually issues.

Track: B (security).

Trust boundaries:
- The principal is any unauthenticated HTTP caller, who controls every byte of the token.
- The token passes `split`/`b64`/`json` (lines 44–50), then the alg check (51), then signature verification (53).
- Everything after line 53 is reachable only by the key holder.
- The only attacker-reachable code is lines 44–53.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Medium | CONFIRMED (traced) | B | `auth.py:51` (`header.get`) | `json.loads` can return a list, string, number or `None`. `.get` then raises `AttributeError` outside the `try`, which breaks the docstring contract "or raise InvalidToken". | An unauthenticated caller sends `W10.e30.AA` (header `[]`). `AttributeError` escapes. A caller that catches only `InvalidToken` returns a 500 instead of a 401, and anyone can trigger this at will. It fails closed, so no access is granted. | Add `if not isinstance(header, dict) or not isinstance(claims, dict): raise InvalidToken("malformed token")` inside or just after the `try`. **Repro:** `auth.verify_token("W10.e30.AA")`. Expected: `InvalidToken`. Observed by trace: `AttributeError: 'list' object has no attribute 'get'`. Same with `bnVsbA.e30.AA` (header `null`). | a Y, b Y, c N, d N |
| F2 | Low | CONFIRMED (traced) | B | `auth.py:56` (`exp < now`) | A token is accepted at the exact second `now == exp`. RFC 7519 §4.1.4 says the current time "MUST be before" the expiration time. | With an integer `now` equal to `exp`, an expired token is accepted for one more second. This is negligible with a float `time.time()`. | Use `exp <= now`. **Repro:** `auth.verify_token(sign_rs256({**CLAIMS,"exp":1000}), now=1000)` with the test key patched. Expected: `InvalidToken`. Observed by trace: the claims are returned. | a Y, b Y, c N, d N |

### Siblings searched for F1

- `claims.get` at lines 55 and 58 has the same root cause. It is reachable only with a valid signature from the identity service, so it is not attacker-reachable and not a separate finding. The same `isinstance` fix covers it.
- Non-string `token` and wrong part counts raise inside the `try` and are caught.
- Deeply nested JSON raises `RecursionError`, which is an `Exception` subclass, so it is caught.

## NEEDS VALIDATION

- **S1 `auth.py:38-39`:** `ISSUER = "https://id.example.test"` uses `.test`, a TLD reserved for testing (RFC 6761), which looks like a placeholder. If the production identity service issues any other `iss`, every real token is rejected and the API has a total outage (it fails closed). `AUDIENCE = "reports-api"` has the same risk. *Settles it:* the `iss` and `aud` values in a real production token.
- **S2 `auth.py:58`:** `claims.get("aud") != AUDIENCE` rejects `aud` sent as an array (`["reports-api"]`), which RFC 7519 §4.1.3 permits. *Settles it:* whether the identity service emits `aud` as a string or an array.
- **S3 `auth.py:56`:** `isinstance(exp, int)` rejects a non-integer NumericDate such as `1.7e9` or `1700000000.5`, which RFC 7519 allows. *Settles it:* whether the identity service ever emits a float `exp`.
- **S4 `auth.py:18`:** the code assumes `PUBLIC_N` is the identity service's current production key. It is hardcoded with no `kid` handling, so a key rotation needs a redeploy and would cause an outage until then. *Settles it:* compare it with the service's published key or JWKS.

## REFUTED

- **Algorithm confusion (`alg: none` or HS256 with the PEM as the HMAC secret):** refuted. Line 51 rejects any `alg` other than RS256, and `_rsa_verify` has no HMAC path.
- **Bleichenbacher-style signature forgery from lax padding parsing:** refuted. Line 37 rebuilds the whole expected EM (`00 01 FF… 00 DigestInfo hash`) and compares it in full with `hmac.compare_digest`. Nothing is parsed, so no trailing garbage or short padding is accepted. The DigestInfo prefix `3031300d060960864801650304020105000420` is the correct SHA-256 prefix. The length arithmetic gives 2 + (k−54) + 1 + 51 = k.
- **`PUBLIC_N` does not match the PEM:** refuted as far as checked by hand.
  - The PEM modulus begins `B4 0A 5F` (decoded from `tApf`). That gives about 0.70328 × 2²⁰⁴⁸ ≈ 2.27280e616, which matches `PUBLIC_N`'s leading digits `2.2728009…`.
  - The PEM modulus ends `…AD AF`. `PUBLIC_N mod 65536` = 44463 = `0xADAF`.
  - The middle bytes were not checked.
- **Signature integer ≥ n accepted:** refuted as a vulnerability. `pow(s, e, n)` reduces it mod n, so an attacker gains nothing beyond what a valid signature already gives.
- **Lenient base64 decoding enables malleability:** refuted. The signature covers the raw `head_b64.body_b64` string, not the decoded bytes.

## WHAT HOLDS UP

- The signature is verified before any claim is trusted.
- The padding comparison is strict and constant-time.
- RS256 is pinned.
- A missing or non-integer `exp` is rejected.
- Parse errors map to `InvalidToken`.
- The tests use a separate test key and patch it in, so they do not need the production private key, and `test_token_signed_by_another_key_is_refused` checks that the production key rejects test signatures.
- Test-strength note, not a defect: if the alg check at line 51 is deleted, `test_alg_none` and `test_hs256…` still pass, because those signatures fail the `len == k` check. The alg check is defence in depth that no test guards. A mutation test would confirm this.

## UNVERIFIED CLAIMS

- "7 tests in test_auth.py pass." There are 7 tests, but they were not run. Confirm with `python -m unittest test_auth` in an isolated copy.
- That `PUBLIC_N` is the identity service's current key. Confirm against its JWKS.

## QUESTIONS FOR THE AUTHOR

1. What `iss` and `aud` values does a real production token carry, and is `aud` a string or an array?
2. Does the identity service ever emit a float `exp`?
3. How does the reports API handle exceptions other than `InvalidToken` from `verify_token`?

## DECISION-MAKER SUMMARY

The signature-checking core is sound and the known JWT forgery tricks are blocked. Before release:
- Add a type check so malformed headers give a clean rejection instead of a server error.
- Confirm the hardcoded issuer and audience against a real production token.

If it ships as is, the most likely failure is not a breach but an outage: every real login is rejected because the issuer string is a placeholder.

## OWNER SUMMARY

The new login-token check correctly blocks forged and expired tokens, and no way to get in without a valid token was found. One kind of junk input makes it crash instead of politely refusing, which is a small fix. Before release, someone should confirm that the issuer name written into the code matches the real identity service, or every real user could be locked out.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "auth.py", "status": "seen", "matters": true},
    {"item": "test_auth.py", "status": "seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": true},
    {"item": "identity service real iss/aud/exp format and JWKS", "status": "not_seen", "matters": true},
    {"item": "reports API caller of verify_token", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "only a public key is present"},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "auth.py", "kind": "file"},
      {"unit": "auth.py:_b64d", "kind": "function"},
      {"unit": "auth.py:_rsa_verify", "kind": "function"},
      {"unit": "auth.py:verify_token", "kind": "function"},
      {"unit": "auth.py:PUBLIC_KEY_PEM vs PUBLIC_N (leading and trailing bytes)", "kind": "config"},
      {"unit": "test_auth.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "execution of test_auth.py", "reason": "no_tools"},
      {"unit": "full modulus byte-for-byte comparison", "reason": "no_tools"},
      {"unit": "reports API caller", "reason": "not_supplied"},
      {"unit": "identity service token format", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:51",
     "scenario": "An unauthenticated caller sends a token whose header JSON is not an object (e.g. W10.e30.AA, header []); header.get raises AttributeError outside the try, escaping the InvalidToken contract and producing a 500 in callers that catch only InvalidToken.",
     "fix": "After parsing, raise InvalidToken unless both header and claims are dicts.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "auth.verify_token('W10.e30.AA'): expected InvalidToken, observed by trace AttributeError: 'list' object has no attribute 'get'."},
    {"id": "F2", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:56",
     "scenario": "With now equal to exp, the token is accepted although RFC 7519 4.1.4 requires the current time to be before exp; at most one extra second of validity.",
     "fix": "Use exp <= now.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "With the test key patched, auth.verify_token(sign_rs256({**CLAIMS, 'exp': 1000}), now=1000): expected InvalidToken, observed by trace claims returned."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py:38-39",
     "suspicion": "ISSUER uses the reserved .test TLD and looks like a placeholder; a mismatch would reject every production token.",
     "unresolved_fact": "The iss and aud values in a real production token."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "auth.py:58",
     "suspicion": "An aud sent as an array is rejected.",
     "unresolved_fact": "Whether the identity service emits aud as a string or an array."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "auth.py:56",
     "suspicion": "A non-integer NumericDate exp is rejected.",
     "unresolved_fact": "Whether the identity service ever emits a float exp."},
    {"id": "S4", "status": "needs_validation", "track": "B", "location": "auth.py:18",
     "suspicion": "Hardcoded key with no kid handling; must be the current production key and a rotation needs a redeploy.",
     "unresolved_fact": "The identity service's published JWKS modulus."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "alg none or HS256-with-public-key confusion", "evidence": "auth.py:51 rejects any alg other than RS256 and _rsa_verify has no HMAC path."},
    {"id": "C2", "candidate": "Lax PKCS#1 v1.5 padding parsing allows forgery", "evidence": "auth.py:37 rebuilds the full expected encoded message and compares it whole with hmac.compare_digest; the DigestInfo prefix is correct for SHA-256."},
    {"id": "C3", "candidate": "PUBLIC_N does not match PUBLIC_KEY_PEM", "evidence": "The PEM modulus begins B40A5F (about 2.2728e616, matching PUBLIC_N's leading digits) and ends ADAF, equal to PUBLIC_N mod 65536 = 44463; middle bytes not checked."},
    {"id": "C4", "candidate": "A signature integer >= n is accepted", "evidence": "pow reduces it mod n, so it is equivalent to a valid signature and gives no forgery."}
  ]
}
```