VERDICT: **REWORK**. The verifier accepts unsigned tokens (`alg: none`) and tokens HMAC-signed with the public key, so anyone can forge a token and call the reports API as any user.

CONFIDENCE: **high** on the two Criticals, which come straight from the code. Medium overall. This was a single reviewer with no tools: no code was run, no tests were mutated, and the PEM/modulus match was not recomputed. The review is not same-context, because the work was not written in this conversation.

INPUTS LEDGER:
- Seen: the original request (verbatim), `auth.py`, `test_auth.py`, and the context ("3 tests pass").
- Not seen: the identity service's actual published public key or JWKS. This matters because I can't confirm `PUBLIC_N`/`PUBLIC_E` belong to the real signer.
- Not seen: the reports API code that calls `verify_token`. This matters for how exceptions other than `InvalidToken` are handled (401 or 500) and whether `aud`/`iss` are checked anywhere else.
- Not seen: any test run output. "3 tests pass" is unverified, but the Criticals don't depend on it.

SEATS AND GATE: One reviewer only (this instance); no subagent or cross-vendor seats were available. Sensitivity gate passed. The only key material is a public key and a test-only private key, with no personal data.

FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | B | `auth.py` `elif alg == "none": ok = True` | Unsigned tokens are accepted. | An attacker sends `b64({"alg":"none"}).b64({"sub":"admin","exp":9999999999}).` (empty signature). `_b64d("")` returns `b""`, `ok=True`, exp is in the future, and the forged claims come back as valid. | Delete the branch. Accept only `alg == "RS256"`. Add a test that an `alg: none` token raises `InvalidToken`. | confirmed: traced line by line; no other check stands in the way |
| 2 | Critical | CONFIRMED | B | `auth.py` `elif alg == "HS256": ... hmac.new(PUBLIC_KEY_PEM.encode(), ...)` | Classic RS256→HS256 algorithm confusion. The HMAC secret is the public key, which is public by definition and is also committed in this file. | The attacker sets `alg: HS256` and signs any claims with HMAC-SHA256 keyed on the PEM text from the repo or the identity service's published key. `compare_digest` matches, so any identity is forged. | Delete the branch and `PUBLIC_KEY_PEM` (it is otherwise unused). Add a test that an HS256 token keyed with the PEM is rejected. | confirmed: the key bytes are the exact source string, which the attacker can read from the repo |
| 3 | High | CONFIRMED | B (drift) | `auth.py` alg dispatch | The request says tokens "are RS256 JWTs". The work adds two extra algorithms that weren't asked for, and both are the root of #1 and #2. | Same as #1 and #2. Even if both are "fixed" by tweaking them, any non-RS256 path keeps the confusion surface. | Pin the algorithm on the verifier side, never from the header. | confirmed |
| 4 | High | CONFIRMED | B (tests) | `test_auth.py` whole file | The suite covers only the happy path, expiry, and a tampered payload. There is no test for `alg: none`, HS256, a token signed with a different RSA key, or a malformed header. "3 tests pass" is consistent with a verifier anyone can bypass. | CI goes green while #1 and #2 ship to production. | Add negative tests for `alg: none`, HS256 with the PEM, a different-RSA-key signature, a non-object header/body, and a non-numeric `exp`. Confirm each goes red against the current code. | confirmed: a forger could add an RS256-irrelevant token and no test would catch it |
| 5 | Medium | CONFIRMED | B | `auth.py` `header.get("alg")`, `claims.get("exp", 0)`, the `<` comparison | Some inputs raise errors other than `InvalidToken`: a header or body that is valid JSON but not an object (`[]`, `1`, `"x"`) gives `AttributeError`; `exp` as a string, null, or list gives `TypeError`. `header.get` sits outside the `try`. | An attacker sends `b64("[]").x.y` and gets an unhandled exception, likely a 500 with a stack trace in logs instead of a 401. Today this fails closed, but callers catching only `InvalidToken` will mishandle it. | Check `isinstance(header, dict)` and `isinstance(claims, dict)`. Require `exp` to be an int or float (not bool) and raise `InvalidToken` otherwise. | n/a |
| 6 | Medium | PROBABLE | B | `auth.py` top-level design | Hand-rolled JWT and RSA verification instead of a vetted library. The PKCS#1 v1.5 check itself looks correct (full encoded message compared, length checked), but the surrounding JWT logic is where #1 and #2 crept in. | Future edits reintroduce similar bugs; there is no `kid` or key rotation support. | Use `jwt.decode(token, key, algorithms=["RS256"])` (PyJWT) or equivalent, with `require=["exp"]`. | n/a |
| 7 | Medium | UNVERIFIED | B | `PUBLIC_KEY_PEM` vs `PUBLIC_N`/`PUBLIC_E` | The key is stored twice. Only `PUBLIC_N`/`E` is used for RS256, and the tests patch both away, so nothing checks that `PUBLIC_N` is the identity service's real modulus or matches the PEM. The leading digits are consistent with the PEM's `0xb40a5f…` modulus, but I could not recompute it. | If the constants are wrong, every real token is rejected and production breaks on deploy. If they are a test key, production trusts the wrong signer. | Load the key once from the identity service's PEM or JWKS. Add a test that `PUBLIC_N` equals the modulus parsed from the PEM, plus one integration test with a real token. | n/a |
| 8 | Low | CONFIRMED | B | `auth.py` `claims.get("exp", 0) < now` | When `exp == now` the token is accepted. RFC 7519 §4.1.4 says to reject on or after `exp`. There is also no clock-skew leeway. | Off-by-one at the boundary; spurious rejections with skewed clocks. | Use `<=`, and add a small explicit leeway if desired. | n/a |
| 9 | Low | CONFIRMED | B | `_b64d`, `_rsa_verify` | The tokens are malleable. `urlsafe_b64decode` silently discards non-alphabet characters, and a signature integer `s ≥ n` (e.g. `s+n` if it fits in k bytes) is not rejected, contrary to RFC 8017 §8.2.2. This is not a forgery. | Token-ID or replay-cache schemes that key on the raw token string can be bypassed with variants of a valid token. | Decode with `validate=True` (or re-encode and compare), and reject a signature integer `≥ n`. | n/a |

WHAT HOLDS UP:
- `_rsa_verify` implements PKCS#1 v1.5 verification soundly. It checks the signature length, compares the whole reconstructed encoded message (so it is not vulnerable to Bleichenbacher-style lax parsing), uses the correct SHA-256 DigestInfo prefix, and compares in constant time.
- A missing `exp` defaults to 0 and is rejected.
- Malformed segment counts and bad base64/JSON fail closed inside the `try`.
- The tampered-payload test does exercise the RS256 check.

UNVERIFIED CLAIMS:
- "3 tests pass": run `python -m unittest test_auth`.
- That `PUBLIC_N`/`E` is the identity service's key: compare against its published JWKS or PEM.
- That the tests guard what they claim: mutate `_rsa_verify` to `return True` and confirm `test_tampered_payload` goes red.

QUESTIONS FOR THE AUTHOR:
1. Why were HS256 and `none` added when the request specifies RS256 only?
2. Does the identity service issue tokens for other audiences? If so, should `aud`/`iss` be checked here? Otherwise a valid token minted for another service would be accepted by the reports API.
3. Where do `PUBLIC_N`/`E` come from, and how will key rotation work?

DECISION-MAKER SUMMARY: Do not deploy. Findings #1 and #2 let anyone forge a token for any user with no key at all. Removing both branches, adding negative tests, and preferably switching to PyJWT with `algorithms=["RS256"]` is a small change. Shipping as is means the reports API is effectively unauthenticated.

OWNER SUMMARY: The login check for the reports system has two shortcuts that let anyone pretend to be any user without a real credential. The fix is small, removing the two shortcuts and adding tests that try them, but it must happen before release. The existing tests pass because they never try these tricks.

```json
{
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "identity service published public key / JWKS", "status": "not_seen", "matters": true},
    {"item": "reports API caller of verify_token", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-single-reviewer", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "public key and test-only key material; no personal data"},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "auth.py verify_token: elif alg == \"none\": ok = True",
     "scenario": "Token with header {\"alg\":\"none\"}, arbitrary claims and empty signature is returned as valid; anyone can impersonate any user.",
     "fix": "Remove the branch; accept only RS256 pinned by the verifier; add a test that alg none raises InvalidToken.", "status": "confirmed"},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "auth.py verify_token: elif alg == \"HS256\" using PUBLIC_KEY_PEM as HMAC key",
     "scenario": "Attacker HMAC-SHA256-signs forged claims with the public PEM (in the repo / published) and sets alg HS256; signature check passes.",
     "fix": "Remove the HS256 branch and PUBLIC_KEY_PEM; add a test that an HS256 token keyed with the PEM is rejected.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "auth.py alg dispatch",
     "scenario": "Request specified RS256 only; extra algorithms chosen from the attacker-controlled header create the bypasses in findings 1-2.",
     "fix": "Pin algorithm server-side; ignore header alg except to reject anything other than RS256.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "test_auth.py",
     "scenario": "No negative tests for alg none, HS256, wrong RSA key or malformed header; CI is green while forgery is possible.",
     "fix": "Add those negative tests and confirm each fails against the current code.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "auth.py header.get / claims.get / exp comparison",
     "scenario": "Non-object header or body JSON, or non-numeric exp, raises AttributeError/TypeError instead of InvalidToken, likely a 500.",
     "fix": "Type-check header, claims and exp; raise InvalidToken on mismatch."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "auth.py overall",
     "scenario": "Hand-rolled JWT handling invites further verification bugs and has no key rotation.",
     "fix": "Use PyJWT jwt.decode(token, key, algorithms=[\"RS256\"], options={\"require\": [\"exp\"]})."},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "B", "location": "auth.py PUBLIC_KEY_PEM vs PUBLIC_N/PUBLIC_E",
     "scenario": "Key duplicated in two forms and never exercised by tests; a mismatch with the real signer breaks auth in production or trusts the wrong key.",
     "fix": "Derive the key from one source; test the PEM modulus equals PUBLIC_N; add an integration test with a real token."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "auth.py claims.get(\"exp\", 0) < now",
     "scenario": "Token accepted when exp == now, contrary to RFC 7519 4.1.4; no clock-skew leeway.",
     "fix": "Use <= and an explicit small leeway."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "auth.py _b64d and _rsa_verify",
     "scenario": "Non-canonical base64 and signature integers >= n verify, so tokens are malleable and raw-string replay caches can be bypassed.",
     "fix": "Strict base64 decoding; reject signature integer >= n."}
  ]
}
```