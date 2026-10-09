VERDICT: REJECT. `verify_token` lets the token choose its own algorithm, so anyone can forge a token with any claims: either `alg: none` with an empty signature, or `alg: HS256` keyed with the public key.

CONFIDENCE: medium. The two Critical findings are certain from reading the code, but no tools were available. Nothing was run, no reproduction was executed, and I could not check that `PUBLIC_N`/`PUBLIC_E` match `PUBLIC_KEY_PEM` or the identity service's real key. This was a single reviewer with no subagent and no seats. The work was not written in this conversation, so the review does not share the author's context.

INPUTS LEDGER:
- Seen: `request.md` (the original request, verbatim), `context.md`, `auth.py`, `test_auth.py`.
- Not seen: the identity service's published public key, JWKS or key-rotation policy. This matters for whether the hardcoded key is correct and current.
- Not seen: the caller of `verify_token` (the reports API handler). This matters for how uncaught exceptions are handled and whether `aud`/`iss` are checked elsewhere.
- Not seen: CI output for "3 tests pass". This matters little: the tests do not cover the defects below either way.

COVERAGE:
- Scope: the whole work (2 files).
- Checked:
  - `auth.py`: module constants, `_b64d`, `_rsa_verify`, `verify_token`, line by line.
  - `test_auth.py`: all 3 tests, the patching in `setUp` and the `sign_rs256` helper.
  - `request.md` and `context.md`.
- Not checked:
  - Whether `PUBLIC_N` equals the modulus inside `PUBLIC_KEY_PEM` (no tools to decode it).
  - A scan for zero-width or bidirectional characters (no tools; none visible on reading).
  - Callers of `verify_token` (not supplied).

SEATS AND GATE: one local reviewer ran; there was no subagent tool. The sensitivity gate is not triggered: the only key is a public key and no personal data is present. Cross-vendor seats were not requested.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | `auth.py:53-54` | `alg == "none"` sets `ok = True`, so no signature is required. The request asked for RS256 only (drift). | An unauthenticated caller sends header `{"alg":"none"}`, body `{"sub":"admin","exp":2000000000}` and an empty signature (`h.b.`). `split(".")` yields 3 parts, `_b64d("")` returns `b""`, and the claims are returned. Full impersonation of any user. | **Fix:** pin the algorithm: reject anything except `"RS256"`, and delete both other branches. **Repro:** `verify_token(b64(b'{"alg":"none"}')+"."+b64(b'{"sub":"admin","exp":2000000000}')+".", now=1000)`. Expected `InvalidToken`; reading the code, it returns `{"sub":"admin",...}`. | y/y/y/y |
| F2 | Critical | CONFIRMED | B | `auth.py:51-52` | `alg == "HS256"` verifies an HMAC keyed with `PUBLIC_KEY_PEM`. That key is public: it is in source and published by the identity service. This is classic RS/HS algorithm confusion, and it is also drift from the RS256-only request. | An attacker takes the public PEM, computes `HMAC-SHA256(PEM, head+"."+body)` over a header `{"alg":"HS256"}` and arbitrary claims. The token verifies, giving any identity. | **Fix:** same as F1, with a single RS256 path. **Repro:** `sig = hmac.new(auth.PUBLIC_KEY_PEM.encode(), (h+"."+b).encode(), hashlib.sha256).digest()`; `verify_token(h+"."+b+"."+b64(sig), now=1000)` returns the forged claims. This works under the test patch too, which does not patch the PEM. | y/y/y/y |
| F3 | Medium | CONFIRMED | B | `auth.py:48` (also `:59`) | `header.get` runs outside the `try`. A header that is valid JSON but not an object (`[]`, `1`, `"x"`) raises `AttributeError`, not `InvalidToken`. Line 59 does the same for non-dict claims, and for a non-numeric `exp` (a `TypeError` on `<`), which is reachable through F1. | Unauthenticated input causes an uncaught exception. If the API catches only `InvalidToken`, the result is a 500 and a stack trace in the logs instead of a 401. | **Fix:** check `isinstance(header, dict)` and `isinstance(claims, dict)`, and that `exp` is `int`/`float` (not bool); raise `InvalidToken` otherwise. **Repro:** `verify_token(b64(b"[]")+"."+b64(b"{}")+".AA")`. Expected `InvalidToken`; observed `AttributeError: 'list' object has no attribute 'get'`. | y/y/n/n |
| F4 | Medium | CONFIRMED | B | `test_auth.py` (class `T`) | The 3 passing tests cover only RS256 happy, expired and tampered cases. Nothing tests rejection of `none`, `HS256`, unknown algorithms or malformed input, so "3 tests pass" (context) gives false assurance while F1 and F2 are open. | A future change, or the current code, accepts forged algorithms with CI green. | **Fix:** add `test_alg_none_rejected`, `test_hs256_with_public_key_rejected`, `test_non_object_header_rejected` and `test_exp_equal_now_rejected`. **Repro:** each new test fails on the current code, using the inputs from F1, F2, F3 and F6. | y/y/n/y |
| F5 | Low | CONFIRMED | B | `auth.py:35` | There is no check that the signature integer is less than `n` (RFC 8017 §8.2.2 step 2, "signature representative out of range"). `pow(s+n, e, n) == pow(s, e, n)`, so a second byte encoding of a valid signature also verifies. This is not a forgery. | Any denylist or replay cache keyed on the raw token string can be bypassed by re-encoding the signature of an already-issued token. | **Fix:** `s = int.from_bytes(signature,"big")`; `if s >= n: return False`. **Repro:** take a valid token's signature `s`, set `s2 = s+N`. If `s2 < 256**k`, encode it to `k` bytes; `verify_token` accepts it. Expected rejection. | y/y/n/n |
| F6 | Low | CONFIRMED | B | `auth.py:59` | `exp < now` accepts a token at exactly `now == exp`. RFC 7519 §4.1.4 says a token must not be accepted "on or after" its expiration time. | A token is accepted for up to one extra second at the boundary. | **Fix:** use `<=`. **Repro:** `verify_token(sign_rs256({"sub":"u1","exp":1000}), now=1000)`. Expected `InvalidToken`; observed the claims. | y/y/n/n |

**Siblings for F1 and F2.** The root cause is that the algorithm is selected from the attacker-controlled header. I searched every branch of `verify_token` and every use of `PUBLIC_KEY_PEM`:

- The only branches are RS256, HS256, none and else (reject).
- `PUBLIC_KEY_PEM` is used only at line 52, which makes it dead weight once HS256 is removed.
- `PUBLIC_N` and `PUBLIC_E` are used only in the RS256 path.

No further siblings exist.

**Boundary for F1 and F2.**
- Principal: any unauthenticated internet caller.
- Input: the JWT header's `alg`, plus the claims.
- Control that fails: signature verification, which the token itself can bypass or downgrade.
- Boundary crossed: anonymous caller to any identity.
- Resource: every report reachable through the reports API.

## NEEDS VALIDATION

- **Wrong or stale key.** It is unknown whether `PUBLIC_N` and `PUBLIC_E` (`auth.py:18-19`) are the modulus and exponent of `PUBLIC_KEY_PEM`, and of the identity service's current signing key. Settle it by decoding the PEM and the service's JWKS and comparing `n`. The tests patch `N`/`E`, so the production key path is never exercised.
- **Key rotation.** The key is hardcoded and `kid` is ignored. Whether the identity service rotates keys decides if a rotation will lock out every caller.
- **Missing audience check.** No `aud`/`iss` check exists. That was not requested, but it matters if the identity service issues RS256 tokens for other services: a token minted for service X would be accepted here. Settle it by confirming whether one signing key serves multiple audiences.

## REFUTED

- **Bleichenbacher-style PKCS#1 v1.5 parsing.** Refuted: `_rsa_verify` rebuilds the full expected encoded message and compares the whole thing with `hmac.compare_digest` (`auth.py:36-37`). No lenient parsing of the padding or the ASN.1 structure happens.
- **Missing `exp` lets a token live forever.** Refuted: `claims.get("exp", 0)` makes a missing `exp` count as expired, which fails closed.
- **A malformed token string crashes the verifier.** Refuted for split, base64 and JSON errors and for a non-string token: all happen inside the `try` (`auth.py:40-46`). Only the post-parse type issues in F3 escape.

## WHAT HOLDS UP

- The RS256 path itself:
  - correct DigestInfo prefix for SHA-256;
  - signature-length check;
  - full encoded-message comparison in constant time;
  - signing input taken from the original base64 segments rather than re-serialized JSON.
- Expiry is checked only after the signature check.
- Missing `exp` fails closed.

## UNVERIFIED CLAIMS

- "3 tests pass": not run here. Confirm by running `python -m unittest test_auth` in an isolated copy.
- That the hardcoded key is the identity service's key: confirm against the service's published JWKS.

## QUESTIONS FOR THE AUTHOR

1. Why are the `HS256` and `none` branches there? Is any client relying on them?
2. Where does `PUBLIC_N` come from, and how is it kept in sync with the identity service when keys rotate?
3. Does the identity service sign tokens for audiences other than the reports API?

## DECISION-MAKER SUMMARY

Do not deploy: in its current form, anyone can forge a token as any user in two trivial ways. The fix is small: accept RS256 only, add type checks, and add negative tests. Re-review after the fix, together with confirmation that the hardcoded key matches the identity service.

## OWNER SUMMARY

The login check for the reports system can be fooled by anyone, letting them act as any user and read any report. The cause is a few lines that accept "unsigned" or easily faked passes; removing them is quick. It should not go live until that is fixed and re-checked.

```json
{
  "schema_version": "2.3",
  "verdict": "REJECT",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "auth.py", "status": "seen", "matters": true},
    {"item": "test_auth.py", "status": "seen", "matters": true},
    {"item": "identity service public key / JWKS", "status": "not_seen", "matters": true},
    {"item": "reports API caller of verify_token", "status": "not_seen", "matters": true},
    {"item": "CI output for the 3 passing tests", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "claude-local", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Only a public key and test keys; no personal or confidential data."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "auth.py", "kind": "file"},
      {"unit": "auth.py:_b64d", "kind": "function"},
      {"unit": "auth.py:_rsa_verify", "kind": "function"},
      {"unit": "auth.py:verify_token", "kind": "function"},
      {"unit": "test_auth.py", "kind": "file"},
      {"unit": "test_auth.py:T", "kind": "function"},
      {"unit": "Algorithm is fixed to RS256 as requested", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "PUBLIC_N/PUBLIC_E match PUBLIC_KEY_PEM and the identity service key", "reason": "no_tools"},
      {"unit": "Hidden Unicode scan of auth.py and test_auth.py", "reason": "no_tools"},
      {"unit": "Reports API caller of verify_token", "reason": "not_supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:53-54",
     "scenario": "An unauthenticated caller sends a token with header {\"alg\":\"none\"}, arbitrary claims and an empty signature; verify_token sets ok=True and returns the forged claims.",
     "fix": "Accept only alg == \"RS256\"; delete the none and HS256 branches; add a test that alg none is rejected.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "verify_token(b64(b'{\"alg\":\"none\"}')+'.'+b64(b'{\"sub\":\"admin\",\"exp\":2000000000}')+'.', now=1000): expected InvalidToken; per the code it returns {'sub':'admin',...}.",
     "security": true,
     "boundary": {"principal": "any unauthenticated caller", "input": "JWT header alg and claims",
                  "control": "signature verification is skipped when alg is none", "crossed": "anonymous to any identity",
                  "resource": "all data behind the reports API"},
     "siblings_searched": {"searched": "every alg branch in verify_token and every use of PUBLIC_KEY_PEM, PUBLIC_N, PUBLIC_E",
                           "found": "HS256 branch at auth.py:51-52 (F2); no others"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:51-52",
     "scenario": "An attacker computes HMAC-SHA256 over the signing input keyed with the public PUBLIC_KEY_PEM and sets alg HS256; the token verifies with arbitrary claims.",
     "fix": "Accept only alg == \"RS256\"; remove the HS256 branch; add a test that an HS256 token keyed with the public key is rejected.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "h=b64(b'{\"alg\":\"HS256\"}'); b=b64(b'{\"sub\":\"admin\",\"exp\":2000000000}'); sig=hmac.new(auth.PUBLIC_KEY_PEM.encode(), (h+'.'+b).encode(), hashlib.sha256).digest(); verify_token(h+'.'+b+'.'+b64(sig), now=1000): expected InvalidToken; per the code it returns the forged claims.",
     "security": true,
     "boundary": {"principal": "any unauthenticated caller", "input": "JWT header alg, claims and an HMAC computed with the public key",
                  "control": "algorithm chosen by the token; public key used as HMAC secret", "crossed": "anonymous to any identity",
                  "resource": "all data behind the reports API"},
     "siblings_searched": {"searched": "every alg branch in verify_token and every use of PUBLIC_KEY_PEM",
                           "found": "alg none branch at auth.py:53-54 (F1); PUBLIC_KEY_PEM used nowhere else"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:48",
     "scenario": "A header that is valid JSON but not an object (e.g. []) makes header.get raise AttributeError outside the try, so callers expecting InvalidToken get an unhandled exception (500). The same applies at auth.py:59 for non-dict claims or a non-numeric exp.",
     "fix": "Check that header and claims are dicts and exp is a number (not bool); raise InvalidToken otherwise.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "verify_token(b64(b'[]')+'.'+b64(b'{}')+'.AA'): expected InvalidToken; observed AttributeError: 'list' object has no attribute 'get'."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_auth.py:class T",
     "scenario": "The test suite covers only the RS256 happy path, expiry and payload tampering; the alg none and HS256 forgeries pass CI unnoticed.",
     "fix": "Add tests for alg none, HS256 keyed with the public key, an unknown alg, a non-object header and exp == now.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Add test_alg_none_rejected using the F1 token with assertRaises(auth.InvalidToken); it fails on the current code."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:35",
     "scenario": "No s < n check, so s+n encoded in k bytes also verifies; a denylist or replay cache keyed on the token string can be bypassed by re-encoding the signature.",
     "fix": "Reject when int.from_bytes(signature, 'big') >= n.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "For a valid token with signature s, if s+N < 256**k, replace the signature with (s+N).to_bytes(k,'big'); verify_token accepts it; expected rejection."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:59",
     "scenario": "A token with exp == now is accepted, contrary to RFC 7519 4.1.4 (must not be accepted on or after exp).",
     "fix": "Use <= instead of <.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "verify_token(sign_rs256({'sub':'u1','exp':1000}), now=1000): expected InvalidToken; observed the claims."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py:18-19",
     "suspicion": "PUBLIC_N/PUBLIC_E may not match PUBLIC_KEY_PEM or the identity service's current key; the tests patch them, so the production key is never exercised.",
     "unresolved_fact": "Whether the modulus decoded from the PEM and from the identity service's JWKS equals PUBLIC_N."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "auth.py:38-61",
     "suspicion": "kid is ignored and the key is hardcoded, so a key rotation locks out every caller.",
     "unresolved_fact": "Whether and how the identity service rotates its signing key."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "auth.py:59-61",
     "suspicion": "No aud/iss check: tokens issued for other services would be accepted by the reports API.",
     "unresolved_fact": "Whether the identity service uses the same signing key for tokens with other audiences."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Lenient PKCS#1 v1.5 padding parsing allows Bleichenbacher-style signature forgery.",
     "evidence": "_rsa_verify rebuilds the full expected encoded message and compares it whole with hmac.compare_digest (auth.py:36-37)."},
    {"id": "C2", "candidate": "A token without exp never expires.",
     "evidence": "claims.get('exp', 0) treats a missing exp as 0, which is always less than now, so the token is rejected (auth.py:59)."},
    {"id": "C3", "candidate": "A malformed token string (bad split, base64 or JSON) crashes the verifier.",
     "evidence": "Split, base64 decoding and json.loads all run inside the try at auth.py:40-46 and are re-raised as InvalidToken."}
  ]
}
```