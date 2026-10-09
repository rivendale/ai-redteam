# Redteam review: `auth.py` token verification for the reports API

**Same-context review, no tools.** I reviewed this myself with no subagent and no way to run code. Every finding below comes from reading the code line by line. The reproductions are exact, but I have not executed them. Re-run in a fresh session with execution before relying on anything marked otherwise.

**VERDICT: REWORK.** The verifier accepts unsigned tokens (`alg: none`) and tokens signed with an HMAC keyed on the public key (`alg: HS256`). Anyone can mint a token with any `sub`, which fully bypasses the RS256 check the request asked for.

**CONFIDENCE:** High on the two Critical findings, because each follows directly from a literal branch in the code. Medium overall, because:
- I had no tools, so nothing was executed.
- The callers of `verify_token` were not supplied.
- I could not check whether the identity service's key matches `PUBLIC_N`.

**INPUTS LEDGER**

| Item | Status | Matters? |
|---|---|---|
| request.md | seen | yes, it is the baseline |
| context.md | seen | yes |
| auth.py | seen | yes |
| test_auth.py | seen | yes |
| Callers of `verify_token` (the reports API handlers) | not supplied | yes: decides whether an uncaught exception becomes a 500 or something worse |
| The identity service's real public key or JWKS | not supplied | yes: needed to confirm `PUBLIC_N` and `PUBLIC_KEY_PEM` are the same key |
| Test run output ("3 tests pass") | not seen | low: the passing tests don't cover the failure cases anyway |

**COVERAGE**
- **Scope:** the whole work (both files).
- **Checked:** `auth.py` (`_b64d`, `_rsa_verify`, `verify_token`, module constants), `test_auth.py` (all 3 tests and helpers), request.md, context.md.
- **Not checked:** callers (not supplied), key provenance (not supplied), runtime behaviour (no tools).

**SEATS AND GATE**
- **Seats:** a single local reviewer. No subagent or cross-vendor seats were available.
- **Sensitivity gate:** passed. The work contains a public key and a test-only RSA key, nothing confidential.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (traced) | B | auth.py:53-54 | `alg == "none"` sets `ok = True`, so no signature is checked. | An attacker sends a token with header `{"alg":"none"}` and claims `{"sub":"admin","exp":9999999999}`. `verify_token` returns those claims and the attacker calls the reports API as anyone. | **Fix:** accept only `RS256` and reject every other `alg`. **Repro:** `t = b64(b'{"alg":"none"}')+"."+b64(b'{"sub":"admin","exp":9999999999}')+"."`, then `auth.verify_token(t)`. Expected `InvalidToken`; the trace says claims are returned. The empty third segment decodes to `b""` inside the try block, so it gets through parsing. | y/y/y/y |
| F2 | Critical | CONFIRMED (traced) | B | auth.py:51-52 | `HS256` is accepted, keyed on `PUBLIC_KEY_PEM`. That is the classic RS/HS algorithm-confusion attack. The key is public by design and is also sitting in source. | An attacker computes `HMAC-SHA256(PUBLIC_KEY_PEM.encode(), head+"."+body)` with header `{"alg":"HS256"}` and arbitrary claims. `compare_digest` matches and the forged claims are returned. | **Fix:** delete the HS256 branch; the request names RS256 only. **Repro:** `h=b64(b'{"alg":"HS256"}'); b=b64(b'{"sub":"admin","exp":9999999999}'); s=b64(hmac.new(auth.PUBLIC_KEY_PEM.encode(), (h+"."+b).encode(), hashlib.sha256).digest())`, then `auth.verify_token(h+"."+b+"."+s)`. Expected `InvalidToken`; the trace says claims are returned. | y/y/y/y |
| F3 | Medium | CONFIRMED (traced) | B | auth.py:48 | A header that is valid JSON but not an object (`[]`, `"x"`, `1`) gets past the try block. `header.get` then raises `AttributeError` instead of `InvalidToken`. This happens before any signature check, so anyone can trigger it. | An unauthenticated client sends `b64("[]")+".e30.x"` and gets an uncaught exception, typically a 500. If a caller does `except InvalidToken` and continues on other errors, the effect depends on that caller (not supplied). | **Fix:** check `isinstance(header, dict)` and `isinstance(claims, dict)` inside the try block, or raise `InvalidToken` for non-dicts. **Repro:** `auth.verify_token(b64(b"[]")+".e30.x")`. Expected `InvalidToken`; traced to `AttributeError`. | y/y/n/n |
| F4 | Medium | CONFIRMED (traced) | B | test_auth.py:34-51 | No test covers `alg: none`, HS256, unknown `alg`, or malformed tokens. All 3 tests pass with F1 and F2 present, so "3 tests pass" is no evidence of safety. `setUp` also patches out `PUBLIC_N`, so the production key is never exercised. | A regression that re-adds an alternate algorithm, or a wrong production key, ships with CI green. | **Fix:** add tests for the none and HS256 forgeries (as in F1/F2) and for an unknown `alg`, each asserting `InvalidToken`. All three should go red on the current code. Add one test that the PEM's modulus equals `PUBLIC_N`. | y/y/n/n |
| F5 | Low | CONFIRMED (traced) | B | auth.py:59 | A non-numeric `exp` (string, `null`, list) makes `<` raise `TypeError` instead of `InvalidToken`. Today this is reachable through F1 and F2. After the fix it is reachable only if the identity service issues such a token. | A forged or mis-issued token with `"exp":"x"` causes an uncaught `TypeError` and a 500. | **Fix:** require `exp` to be an `int` or `float` (and not `bool` or NaN), else raise `InvalidToken`. **Repro:** after fixing F1, use the test key to sign `{"sub":"u1","exp":"x"}` and call `verify_token`. Expected `InvalidToken`; traced to `TypeError`. | y/y/n/n |

**Sibling search (F1 and F2):** both share one root cause, an algorithm chosen from the attacker-controlled header. I searched every branch on `alg` in auth.py:48-56 and every test. The only other branch is RS256, which is correct, and no test touches the alternate branches. Both are security findings:
- **Principal:** any unauthenticated client.
- **Input it controls:** the JWT header `alg` field and the claims.
- **Control that fails:** signature verification, which the header lets the client select away.
- **Boundary crossed:** unauthenticated to any identity.
- **Resource affected:** all reports API data.

## NEEDS VALIDATION
- **Is `PUBLIC_KEY_PEM` the same key as `PUBLIC_N`/`PUBLIC_E`?** Decode the PEM's SubjectPublicKeyInfo and compare the modulus. A mismatch is invisible to the tests because they patch `PUBLIC_N`. After the fix, the PEM is unused and should be removed.
- **Does `PUBLIC_N` actually belong to the identity service?** Compare it with the service's published key or JWKS.
- **Is non-strict base64 decoding (`_b64d`) a problem?** `urlsafe_b64decode` silently drops non-alphabet characters, so one signature can appear under many token strings. This matters only if something keys a replay cache or denylist on the raw token string. Callers were not supplied.
- **How do callers handle non-`InvalidToken` exceptions?** This decides whether F3 is only a 500 or something worse.

## REFUTED
- **"`_rsa_verify` is vulnerable to Bleichenbacher-style lax padding parsing."** Refuted. It rebuilds the full expected encoded message and compares the whole thing with `compare_digest`, after a length check (auth.py:32-37).
- **"A missing `exp` means the token never expires."** Refuted. `claims.get("exp", 0)` makes a missing `exp` count as expired, so it fails closed (auth.py:59).
- **"A NaN or Infinity `exp` makes a token immortal."** Refuted as a standalone finding. It needs a validly signed token once F1 and F2 are fixed, and is covered by F5's type check.

## WHAT HOLDS UP
- The RS256 path is sound: PKCS#1 v1.5 with the SHA-256 DigestInfo prefix, a signature-length check, full encoded-message comparison, and a constant-time compare.
- Parse failures are wrapped in `InvalidToken`.
- The expiry check fails closed when `exp` is missing.
- The injectable `now` makes the code testable.
- `test_tampered_payload` would go red if signature checking were removed from the RS256 path.

## UNVERIFIED CLAIMS
- **"3 tests in test_auth.py pass."** Not run. Confirm by running `python -m unittest test_auth` in a scratch copy. Even if true, the tests do not cover F1 to F3.
- **The module docstring's "Tokens are RS256 JWTs."** The code contradicts it by accepting `none` and HS256.

## QUESTIONS FOR THE AUTHOR
1. Why were the `none` and HS256 branches added? Is anything relying on them? If not, delete both.
2. Does the identity service issue tokens with the same key for other audiences? If so, `aud` and `iss` checks are needed, even though the request did not name them.
3. How should key rotation work? A hardcoded single key with no `kid` support means rotating the key requires a deploy.

## DECISION-MAKER SUMMARY
Do not deploy. The verifier accepts unsigned tokens and tokens forged with the public key, so anyone can call the reports API as any user. The fix is small: accept RS256 only, add type checks, and add the negative tests. Re-review the fix diff before release.

## OWNER SUMMARY
The login-token check for the reports system can be tricked by anyone into accepting a fake identity, including an administrator's. The existing tests pass anyway because they never try a fake token. The fix is small but must be made and re-checked before this goes live.

```json
{
  "schema_version": "2.3",
  "verdict": "REWORK",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "auth.py", "status": "seen", "matters": true},
    {"item": "test_auth.py", "status": "seen", "matters": true},
    {"item": "callers of verify_token", "status": "not_seen", "matters": true},
    {"item": "identity service public key / JWKS", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "local-same-session", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Public key and test-only key material only."},
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
      {"unit": "callers of verify_token", "reason": "not_supplied"},
      {"unit": "identity service key provenance", "reason": "not_supplied"},
      {"unit": "runtime execution of tests and reproductions", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:53-54",
     "scenario": "A token with header {\"alg\":\"none\"}, arbitrary claims and an empty signature is accepted; any client can act as any user.",
     "fix": "Accept only alg RS256; raise InvalidToken for every other value.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "verify_token(b64('{\"alg\":\"none\"}')+'.'+b64('{\"sub\":\"admin\",\"exp\":9999999999}')+'.'): expected InvalidToken, code trace returns the claims (not executed).",
     "security": true,
     "boundary": {"principal": "any unauthenticated client", "input": "JWT header alg field and claims",
                  "control": "signature verification skipped when alg is none", "crossed": "unauthenticated to any identity",
                  "resource": "all reports API data"},
     "siblings_searched": {"searched": "every alg branch in auth.py:48-56 and all tests", "found": "HS256 branch (F2), same root cause; no tests cover either"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:51-52",
     "scenario": "An attacker HMAC-SHA256-signs arbitrary claims with the public PEM as the key and alg HS256; the token is accepted.",
     "fix": "Remove the HS256 branch; RS256 only.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "h=b64('{\"alg\":\"HS256\"}'); b=b64('{\"sub\":\"admin\",\"exp\":9999999999}'); s=b64(hmac.new(auth.PUBLIC_KEY_PEM.encode(), (h+'.'+b).encode(), sha256).digest()); verify_token(h+'.'+b+'.'+s): expected InvalidToken, trace returns claims (not executed).",
     "security": true,
     "boundary": {"principal": "any unauthenticated client", "input": "JWT header alg field, claims, HMAC signature",
                  "control": "algorithm chosen from attacker-controlled header; HMAC keyed on public key", "crossed": "unauthenticated to any identity",
                  "resource": "all reports API data"},
     "siblings_searched": {"searched": "every alg branch in auth.py:48-56 and all tests", "found": "alg none branch (F1), same root cause"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:48",
     "scenario": "Header JSON that is not an object (e.g. []) passes parsing; header.get raises AttributeError before any signature check, so an unauthenticated client gets an uncaught exception.",
     "fix": "Inside the try block, require header and claims to be dicts, else raise InvalidToken.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "verify_token(b64('[]')+'.e30.x'): expected InvalidToken, trace raises AttributeError (not executed)."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_auth.py:34-51",
     "scenario": "No test covers alg none, HS256, unknown alg or malformed input, and setUp patches PUBLIC_N; all 3 tests pass with F1/F2 present, and a wrong production key would also pass.",
     "fix": "Add forgery tests for none and HS256, an unknown-alg test, and a test that the PEM modulus equals PUBLIC_N.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Add a test asserting verify_token(<alg none token from F1>) raises InvalidToken; it fails on current code by trace (not executed)."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:59",
     "scenario": "A non-numeric exp (string, null, list) makes the comparison raise TypeError instead of InvalidToken; reachable today through F1/F2.",
     "fix": "Require exp to be int or float (not bool, finite), else raise InvalidToken.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "Sign {\"sub\":\"u1\",\"exp\":\"x\"} with the test key and call verify_token: expected InvalidToken, trace raises TypeError (not executed)."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py:8-19",
     "suspicion": "PUBLIC_KEY_PEM and PUBLIC_N/PUBLIC_E may not be the same key, and neither is confirmed to be the identity service's key.",
     "unresolved_fact": "Whether the modulus decoded from the PEM equals PUBLIC_N and matches the identity service's published key."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "auth.py:26-27",
     "suspicion": "Non-strict base64 decoding lets one signature appear under many token strings, bypassing any denylist or replay cache keyed on the raw token.",
     "unresolved_fact": "Whether any caller keys state on the raw token string."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "auth.py:48",
     "suspicion": "Uncaught non-InvalidToken exceptions may fail open in a caller.",
     "unresolved_fact": "How callers of verify_token handle exceptions other than InvalidToken."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "_rsa_verify accepts malformed PKCS#1 padding.",
     "evidence": "It rebuilds the full expected encoded message and compares it in constant time after a length check (auth.py:32-37)."},
    {"id": "R2", "candidate": "A missing exp yields a non-expiring token.",
     "evidence": "claims.get('exp', 0) treats a missing exp as expired (auth.py:59)."},
    {"id": "R3", "candidate": "A NaN or Infinity exp makes a token immortal.",
     "evidence": "Requires a valid RS256 signature once F1/F2 are fixed; covered by the F5 type check."}
  ]
}
```