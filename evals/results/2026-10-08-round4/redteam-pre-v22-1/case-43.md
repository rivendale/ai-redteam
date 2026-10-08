# Redteam review: `auth.py` token verification for the reports API

**VERDICT: REJECT.** Anyone can forge a token today, in two ways: `alg: "none"` is accepted, and HS256 is checked with the public key as the HMAC secret. The RSA core is sound, but this cannot reach production as written.

**CONFIDENCE: high** for the two Critical findings. Each one traces line by line to an unconditional bypass. Three things limit the rest:
- I had no tools, so I could not run the tests or the code.
- I could not check that `PUBLIC_N` matches `PUBLIC_KEY_PEM`.
- One reviewer only, with no fresh subagent or second seat. Re-run in a fresh session after the rework, given the stakes.

**INPUTS LEDGER**
- **Seen:** the original request (`request.md`, verbatim), the context (`context.md`), `auth.py` and `test_auth.py`.
- **Not seen:** the identity service's real public key or JWKS, which matters for F4. I also did not see how the API calls `verify_token`, which matters for F5 and F7: does it catch only `InvalidToken`, and does it check audience or scopes elsewhere?
- **Not seen:** a test run. "3 tests pass" is UNVERIFIED, but that does not change the verdict.

**SEATS AND GATE**
- **Sensitivity gate:** passed. The only key material is a public key and a test-only private key, and there is no personal data.
- **Seats:** one in-session reviewer. No subagent or cross-vendor seats were available because this session has no tools.
- **Independence:** this session did not write the work.

## FINDINGS

Line numbers are counted from the file as supplied.

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (trace) | B | `auth.py:53-54` | `alg == "none"` sets `ok = True`, so the signature is never checked. | An attacker sends `base64url({"alg":"none"}).base64url({"sub":"admin","exp":9999999999}).` and `verify_token` returns those claims. Anyone can impersonate anyone on the reports API. | Delete the branch. Accept only `alg == "RS256"` and reject everything else. Add a test that a `none` token raises `InvalidToken`. | confirmed. Nothing in the inputs shows an upstream gateway rejecting `none`, and the function's contract is to return verified claims. |
| F2 | Critical | CONFIRMED (trace) | B | `auth.py:51-52` | HS256 is verified with HMAC keyed by `PUBLIC_KEY_PEM`. This is the classic RS/HS algorithm-confusion bug. | A public key is public, and this one sits in the source. The attacker computes `HMAC-SHA256(PEM bytes, header.body)` with `alg: HS256` and any claims, and passes. The HMAC key is the PEM string including its trailing `\n`, which takes at most a few guesses. | Delete the branch. Add a test that forges an HS256 token with `auth.PUBLIC_KEY_PEM.encode()` and asserts `InvalidToken`. | confirmed. The defender's argument "the attacker needs the exact PEM bytes" fails because the key is published by design and visible in the repo. |
| F3 | High | CONFIRMED | B | `auth.py:49-56` vs request | Drift from the request. The request says tokens "are RS256 JWTs". Accepting HS256 and `none` adds attack surface nobody asked for. This is the root cause of F1 and F2. | As above. Any extra branch added later inherits the same pattern. | Allow-list exactly `{"RS256"}`. Optionally also reject a `crit` header, since none is supported. | confirmed |
| F4 | Medium | UNVERIFIED | B | `auth.py:8-19` | Two copies of the key exist: the PEM, used only by the HS256 path, and `PUBLIC_N` and `PUBLIC_E`, used by RS256. Nothing shows they encode the same key or that either is the identity service's current key. The tests patch `PUBLIC_N` and `PUBLIC_E` away (`test_auth.py` `setUp`), so the production key is never exercised. A hardcoded key also has no `kid` or rotation path. | 1. If `PUBLIC_N` is wrong, every real token fails: a production outage that fails closed. 2. When the identity service rotates keys, every token fails until someone ships a redeploy. | Derive `n` and `e` from one source, either by parsing the PEM or loading from config or JWKS. Add a test that verifies a real token, or a fixture signed by the identity service, against the unpatched key. To settle it, parse the PEM and compare its modulus to `PUBLIC_N`. | n/a |
| F5 | Medium | CONFIRMED (trace) | B | `auth.py:48`, `59` | A header or claims body that is valid JSON but not an object (`[]`, `1`, `"x"`), or a non-numeric `exp` (`"9999"`, `null`), raises `AttributeError` or `TypeError` instead of `InvalidToken`. The header error fires before the signature check, so an unauthenticated user can trigger it. | A caller that maps `InvalidToken` to 401 returns 500 instead. This makes noisy errors and possible stack-trace leaks, but it is not a bypass. | Check that `header` and `claims` are dicts and that `exp` is an int or float but not a bool. Otherwise raise `InvalidToken`. | n/a |
| F6 | Medium | CONFIRMED | B | `test_auth.py` | The tests cover only the happy path, expiry and a tampered payload. There is no test for `alg: none`, HS256 confusion, an unknown alg, a missing `exp`, a malformed token or the production key. All three tests pass with F1 and F2 present, so the suite cannot catch the vulnerabilities that matter. | A future refactor reintroduces a bypass and CI stays green. | Add negative tests for none, HS256-with-PEM, `"alg":"RS512"`, a missing `exp`, a non-object body, a two-part token and a wrong-key signature. Each must go red against the current code before the fix. | n/a |
| F7 | Medium | PROBABLE | A/B | `auth.py:59-61` | The code checks no `iss` or `aud`. The request asked only for signature and expiry, so this is not drift. But if the identity service signs tokens for other services with the same key, those tokens are accepted here. | A token issued for service X, whether leaked or held by a low-privilege user, is replayed against the reports API and accepted. | Ask the author whether the key is shared across audiences. If so, require the expected `aud` and `iss`. | n/a |
| F8 | Low | CONFIRMED | B | `auth.py:59` | `exp < now` accepts a token at exactly `exp`. RFC 7519 §4.1.4 says to reject on or after `exp`. There is also no `nbf` check and no clock-skew leeway. | A one-second window, or spurious rejections when clocks skew. | Use `exp <= now` and add a small explicit leeway if desired. | n/a |

## WHAT HOLDS UP
- **`_rsa_verify` (`auth.py:30-37`)** is a correct PKCS#1 v1.5 verification. It does two things right:
  - It checks the signature length equals `k`.
  - It rebuilds the full expected encoded message and compares it in constant time, rather than parsing the padding. This avoids Bleichenbacher-style lax-parse forgeries.
- **The SHA-256 DigestInfo prefix** `3031300d060960864801650304020105000420` is correct.
- **The signing input** uses the original base64 segments, not re-serialized JSON, which is correct.
- **A missing `exp`** defaults to 0 and is rejected, so it fails closed.
- **Malformed structure** (wrong number of parts, bad base64 or bad JSON) is caught and turned into `InvalidToken`.
- **`test_tampered_payload`** would go red if `_rsa_verify` always returned True, so it does guard the RS256 path.

## UNVERIFIED CLAIMS
- **"3 tests pass".** Run `python -m unittest test_auth` to confirm.
- **The key is the identity service's key, and `PUBLIC_N` matches the PEM.** Parse the PEM, compare the modulus, and verify one real token.

## QUESTIONS FOR THE AUTHOR
1. Why are HS256 and `none` supported? Is any caller relying on them? I expect not, and they should be removed.
2. Does the identity service use this key for tokens meant for other services? If so, `aud` must be checked.
3. How will key rotation reach this service?

## DECISION-MAKER SUMMARY
Do not deploy: two branches (F1, F2) let anyone mint a valid-looking token for any user. Removing them and adding the negative tests is a small change, since the RSA check itself is sound. Deploying as is means the reports API is effectively unauthenticated.

## OWNER SUMMARY
The new login-token check for the reports system has two shortcuts that let anyone fake a token and see reports as any user. The core signature check is built correctly, so the fix is to remove the shortcuts and add tests that prove fake tokens are refused. It should not go live until that is done.

```json
{
  "verdict": "REJECT",
  "confidence": "high",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "auth.py", "status": "seen", "matters": true},
    {"item": "test_auth.py", "status": "seen", "matters": true},
    {"item": "identity service public key / JWKS", "status": "not_seen", "matters": true},
    {"item": "caller of verify_token (exception handling, aud/scope checks)", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-in-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "only public key and test-only private key; no personal data"},
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "auth.py:53-54",
     "scenario": "Token with header {\"alg\":\"none\"}, arbitrary claims and empty signature returns those claims; anyone can impersonate any user.",
     "fix": "Remove the none branch; accept only RS256; add a test that an alg=none token raises InvalidToken.", "status": "confirmed"},
    {"severity": "Critical", "evidence_level": "CONFIRMED", "track": "B", "location": "auth.py:51-52",
     "scenario": "Attacker sets alg=HS256 and signs with HMAC-SHA256 keyed by the public PEM (in source and published); forged claims are accepted.",
     "fix": "Remove the HS256 branch; add a test forging HS256 with auth.PUBLIC_KEY_PEM and asserting InvalidToken.", "status": "confirmed"},
    {"severity": "High", "evidence_level": "CONFIRMED", "track": "B", "location": "auth.py:49-56",
     "scenario": "Request specifies RS256 only; extra algorithms are unrequested attack surface and the root cause of the two Critical findings.",
     "fix": "Allow-list exactly {\"RS256\"}.", "status": "confirmed"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "B", "location": "auth.py:8-19",
     "scenario": "PUBLIC_N/E and PUBLIC_KEY_PEM are separate copies, never checked against each other or the real key (tests patch them); a mismatch or key rotation rejects all real tokens.",
     "fix": "Derive n,e from one source (PEM/config/JWKS with kid); add a test against the unpatched production key or an identity-service-signed fixture."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "auth.py:48,59",
     "scenario": "Non-object header/claims JSON or non-numeric exp raises AttributeError/TypeError, not InvalidToken; the header case fires before the signature check, so it is reachable unauthenticated and yields a 500 instead of a 401.",
     "fix": "Type-check header and claims as dicts and exp as numeric (not bool); raise InvalidToken otherwise."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "test_auth.py",
     "scenario": "No tests for alg=none, HS256 confusion, unknown alg, missing exp, malformed input or the production key; all tests pass with the Critical bugs present.",
     "fix": "Add negative tests for each and confirm each goes red against the current code before the fix."},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "B", "location": "auth.py:59-61",
     "scenario": "No iss/aud check; if the identity service key signs tokens for other services, those tokens are accepted by the reports API.",
     "fix": "Confirm key scope with the author; if shared, require the expected aud and iss."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "auth.py:59",
     "scenario": "exp == now is accepted (RFC 7519 says reject on or after exp); no nbf check or skew leeway.",
     "fix": "Use exp <= now; add explicit small leeway if needed."}
  ]
}
```