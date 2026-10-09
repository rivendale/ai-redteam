# Redteam review: `auth.py` token verification for the reports API

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** No tools were available in this session, so no subagent could be started and nothing was executed. Every finding below comes from tracing the code line by line. None was run.

**VERDICT: REWORK.** `verify_token` lets the token's own header choose the verification method, and two of those methods (`none`, and `HS256` keyed with the public key) let anyone forge any claims. The function decides who may call the reports API, so it must not go to production in this form.

**CONFIDENCE: medium.** The two Critical findings follow from the code with no ambiguity. Confidence is limited by:
- the same-context review;
- no execution;
- no view of the production key source or the API code that calls this function.

## INPUTS LEDGER

| Item | Status | Matters? |
|---|---|---|
| request.md (original request) | seen | — |
| context.md | seen | — |
| auth.py | seen | — |
| test_auth.py | seen | — |
| Identity service's real public key or JWKS | not seen | **Yes.** I cannot confirm that `PUBLIC_N`/`PUBLIC_E` or the PEM is the right key, or that they match each other. |
| Reports API code that calls `verify_token` | not seen | **Yes.** It decides how non-`InvalidToken` exceptions are handled and which claims drive authorization. |
| Output of the test run ("3 tests pass") | not seen | Low. Passing tests do not change the verdict. |
| Identity service token profile (`iss`, `aud`, other relying parties) | not seen | Medium. It decides whether a missing audience check matters. |

## COVERAGE

**Scope:** the whole work (2 files) against the original request.

**Checked:**
- `auth.py`: `_b64d`, `_rsa_verify`, `verify_token`, key constants
- `test_auth.py`: all 3 tests, the `setUp` patch, `sign_rs256`
- request.md and context.md
- The claim "3 tests pass"

**Not checked:**
- Production key correctness (not supplied)
- Caller code (not supplied)
- A mechanical scan for invisible or look-alike characters (no tools). A visual read found no text addressed to the reviewer.

## SEATS AND GATE

- The local same-context reviewer ran.
- No subagent was available (no tools).
- No cross-vendor seats were used; none was requested and the depth is standard.
- Sensitivity gate: an RSA *public* key is not sensitive, and the work contains no personal data or credentials.

## FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED (traced) | B | auth.py:53-54 | `alg: "none"` sets `ok = True`, so no signature is checked. | Anyone sends `b64('{"alg":"none"}') + "." + b64('{"sub":"admin","exp":2000000000}') + "."`. The empty signature part decodes to `b""` inside the try, the `none` branch passes, and the forged claims come back as valid. | **Fix:** accept only `RS256`. Delete the `none` and `HS256` branches and reject any other `alg`. **Repro:** `verify_token(<token above>, now=1000)`. Expected: `InvalidToken`. Observed by trace: returns `{"sub":"admin",...}`. | y/y/y/y |
| F2 | Critical | CONFIRMED (traced) | B | auth.py:51-52, key at auth.py:8-17 | `HS256` is verified by HMAC using the **public** key PEM as the secret. This is classic RS/HS algorithm confusion. | An attacker who has the public PEM (it is public by design, and also sits in this source file) computes `HMAC-SHA256(PEM_bytes, head.body)` with `{"alg":"HS256"}` and any claims. `compare_digest` matches and the forged token is accepted. | **Fix:** same as F1; HMAC must never be accepted. **Repro:** `sig = hmac.new(auth.PUBLIC_KEY_PEM.encode(), (h+"."+b).encode(), hashlib.sha256).digest()`, then `verify_token(h+"."+b+"."+b64(sig), now=1000)` with `h` encoding `{"alg":"HS256"}`. Expected: `InvalidToken`. Observed by trace: claims returned. | y/y/y/y |
| F3 | Medium | CONFIRMED | B | test_auth.py:41-56 (class `T`) | The tests cover only a valid RS256 token, an expired one and a tampered payload. There is no test for `alg` none/HS256/missing, and no test that the production key is used. `setUp` patches `PUBLIC_N` everywhere. `PROD_N`/`PROD_E` are assigned and never used. | "3 tests pass" is reported as assurance while both forgeries above go through. A future regression that re-adds an algorithm would also stay green. | **Fix:** add tests that forge with `alg: none`, with HS256 keyed by the PEM, with a missing `alg`, and with `alg: "rs256"`. Each must raise `InvalidToken`. **Repro:** add `test_alg_none` using the token from F1. Against the current code it fails, because no exception is raised. | y/y/n/y |
| F4 | Medium | CONFIRMED (traced) | B | auth.py:48 | `header.get` sits outside the try. A header that is valid JSON but not an object raises an uncaught `AttributeError`. | Without any signature, a client sends a header part of `b64("1")` or `b64("[]")`. `verify_token` raises `AttributeError` instead of `InvalidToken`, and a caller that catches only `InvalidToken` returns a 500 or crashes the handler. | **Fix:** inside the try, require `isinstance(header, dict)` and `isinstance(claims, dict)`; otherwise raise `InvalidToken`. **Repro:** `verify_token(b64(b"1")+"."+b64(b"{}")+".")`. Expected: `InvalidToken`. Observed by trace: `AttributeError`. | y/y/n/n |
| F5 | Low | CONFIRMED (traced) | B | auth.py:59 | `exp` is not type-checked. A string `exp` raises `TypeError`, and a non-dict `claims` raises `AttributeError`. JSON `NaN` or a huge number (`inf`) would never expire. | This only happens with a validly signed token once F1/F2 are fixed, so it needs an identity-service bug. The result is a 500, or a token that never expires. | **Fix:** require `exp` to be a finite `int`/`float` (excluding `bool`), else raise `InvalidToken`. **Repro:** patch the keys as the tests do, then `verify_token(sign_rs256({"sub":"u1","exp":"x"}), now=1000)`. Expected: `InvalidToken`. Observed by trace: `TypeError`. | y/y/n/n |
| F6 | Low | CONFIRMED (traced) | B | auth.py:33-35 | Missing the RFC 8017 check that the signature integer is less than `n`. Because `pow(s, e, n)` reduces modulo `n`, `s + n` verifies the same as `s`. | Signature malleability: if `s + n < 256^k`, one token gets a second valid encoding. This does not allow forgery. It matters only if anything deduplicates or revokes by raw token string. | **Fix:** `if int.from_bytes(signature,"big") >= n: return False`. **Repro:** with the test key, take a valid `s`, set `s2 = s + N` when `s2.bit_length() <= 8*k`, re-encode it to `k` bytes and verify. Expected: rejected. Observed by trace: accepted. | y/y/n/n |

### Severity check for the Critical findings (confirm-or-refute round)

**Strongest defence considered:** "the API gateway only forwards RS256 tokens." Nothing supplied shows such a gateway, and the function's own contract is to verify. Both F1 and F2 hold.

**Siblings searched** (every point where header fields influence verification, auth.py:47-58):
- The `alg` dispatch has three attacker-selectable branches. Two of them are F1 and F2, each recorded separately.
- `kid`, `jku`, `x5u` and `jwk` are never read, so the header has no other route to key selection.

**Security boundary for F1 and F2:**

| Element | Value |
|---|---|
| Lower-trust principal | Any unauthenticated network client |
| Input it controls | The JWT header `alg` field and the claims |
| Control that fails | Signature verification, which the token itself chooses |
| Boundary crossed | Anonymous to any identity, including admin `sub`/roles |
| Resource affected | Every report the reports API serves |

## NEEDS VALIDATION

- **N1.** Is `PUBLIC_N`/`PUBLIC_E` (auth.py:18-19) the identity service's real key, and does it match `PUBLIC_KEY_PEM`? This is settled by decoding the PEM's modulus and comparing it with `PUBLIC_N`, and by comparing both with the service's published key. The tests never exercise the production key (they patch it).
- **N2.** Should `iss`/`aud`/`nbf` be checked? This is settled by whether the identity service issues tokens to other relying parties. If it does, a token minted for another service is accepted here. The request did not ask for these checks, so this is not counted as drift.
- **N3.** How does the reports API caller handle exceptions other than `InvalidToken`, and which claims drive authorization? This is settled by reading the caller.
- **N4.** Do the "3 tests pass"? Not run here. Even if they do, see F3.

## REFUTED

- **Bleichenbacher-style lenient PKCS#1 parsing (e=3 forgery).** Refuted. auth.py:37 rebuilds the full expected encoding and compares it byte for byte with `compare_digest`, so there is no lenient ASN.1 parsing.
- **A missing `exp` lets a token live forever.** Refuted. `claims.get("exp", 0)` defaults to 0, so a token without `exp` is rejected as expired (it fails closed).
- **Malformed segments or extra dots crash the function.** Refuted. The split, base64 and JSON errors at lines 41-44 are inside the try and become `InvalidToken`.

## WHAT HOLDS UP

- `_rsa_verify` is a correct, strict RSASSA-PKCS1-v1_5/SHA-256 check:
  - the length check is right;
  - the DigestInfo prefix is correct for SHA-256;
  - the full expected encoding is compared in constant time.
- The signature is computed over the raw base64 segments as transmitted, not over re-serialized JSON, which is correct.
- The expiry check fails closed when `exp` is absent.
- The test helper `sign_rs256` is a faithful signer, so `test_valid_token` and `test_tampered_payload` do test the RS256 path.

## UNVERIFIED CLAIMS

- **"3 tests pass."** Confirm by running `python -m unittest test_auth` in an isolated copy.
- **The embedded key is "the service's public key".** Confirm as in N1.
- **The module docstring says tokens are RS256.** The code accepts three algorithms, so the docstring does not describe what the code does.

## QUESTIONS FOR THE AUTHOR

1. Why were `HS256` and `none` added when the request names only RS256? Does anything depend on them?
2. Where does `PUBLIC_N` come from, and how will key rotation work?
3. Does the identity service issue tokens to other audiences?

## DECISION-MAKER SUMMARY

Do not deploy. Anyone can mint a token for any user by setting `alg` to `none`, or by HMAC-signing with the public key, so the reports API would effectively have no authentication. The fix is small: accept only RS256, add negative tests that go red on today's code, and confirm the embedded key is the identity service's real one.

## OWNER SUMMARY

The new login-check code for the reports system can be fooled into accepting fake passes, which would let anyone read any report. The fix is small and well understood, but the code should not go live until it is made and tested. The existing tests passed because they never tried the tricks an attacker would use.

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
    {"item": "identity service published public key / JWKS", "status": "not_seen", "matters": true},
    {"item": "reports API caller of verify_token", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false},
    {"item": "identity service token profile (iss/aud)", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Only an RSA public key and test keys; no personal data or credentials."},
  "coverage": {
    "checked": [
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "auth.py", "kind": "file"},
      {"unit": "auth.py:_b64d", "kind": "function"},
      {"unit": "auth.py:_rsa_verify", "kind": "function"},
      {"unit": "auth.py:verify_token", "kind": "function"},
      {"unit": "test_auth.py", "kind": "file"},
      {"unit": "claim: 3 tests in test_auth.py pass", "kind": "claim"}
    ],
    "not_checked": [
      {"unit": "identity service public key / JWKS", "reason": "not_supplied"},
      {"unit": "reports API caller code", "reason": "not_supplied"},
      {"unit": "execution of tests and reproductions", "reason": "no_tools"},
      {"unit": "mechanical scan for invisible/bidi/look-alike characters", "reason": "no_tools"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:53-54",
     "scenario": "An unauthenticated client sends a token whose header is {\"alg\":\"none\"}, with arbitrary claims and an empty signature; verify_token sets ok=True and returns the forged claims.",
     "fix": "Accept only alg == 'RS256'; remove the 'none' branch and reject every other alg with InvalidToken.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "verify_token(b64('{\"alg\":\"none\"}') + '.' + b64('{\"sub\":\"admin\",\"exp\":2000000000}') + '.', now=1000): expected InvalidToken, observed by trace the forged claims returned. Not executed (no tools).",
     "security": true,
     "boundary": {"principal": "any unauthenticated network client", "input": "JWT header alg field and claims",
                  "control": "signature verification is skipped when alg is none", "crossed": "anonymous to any identity",
                  "resource": "all reports served by the reports API"},
     "siblings_searched": {"searched": "every branch of the alg dispatch and every header field read in auth.py:47-58 (kid/jku/x5u/jwk)",
                           "found": "HS256 branch (F2), recorded separately; no other header field is read"}},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:51-52",
     "scenario": "An attacker who has the public PEM sets alg HS256 and HMAC-SHA256-signs arbitrary claims with the PEM bytes as the key; compare_digest matches and the forged claims are returned.",
     "fix": "Remove the HS256 branch; accept only RS256 verified with the RSA public key.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "h=b64('{\"alg\":\"HS256\"}'); b=b64('{\"sub\":\"admin\",\"exp\":2000000000}'); sig=hmac.new(auth.PUBLIC_KEY_PEM.encode(), (h+'.'+b).encode(), hashlib.sha256).digest(); verify_token(h+'.'+b+'.'+b64(sig), now=1000): expected InvalidToken, observed by trace the forged claims returned. Not executed (no tools).",
     "security": true,
     "boundary": {"principal": "any unauthenticated network client", "input": "JWT header alg field, claims and HMAC signature",
                  "control": "the public key is used as an HMAC secret", "crossed": "anonymous to any identity",
                  "resource": "all reports served by the reports API"},
     "siblings_searched": {"searched": "all uses of PUBLIC_KEY_PEM and all alg branches in auth.py",
                           "found": "PEM used only at line 52; alg none bypass is F1"}},
    {"id": "F3", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_auth.py:41-56 (class T)",
     "scenario": "The suite passes while alg-none and HS256 forgeries are accepted; it gives false assurance and would not catch a regression; production key constants are patched out and PROD_N/PROD_E are unused.",
     "fix": "Add negative tests for alg none, HS256 keyed with the PEM, missing alg and wrong-case alg, each asserting InvalidToken; add one test against the unpatched production key with a known-good token.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Add test_alg_none using the F1 token with assertRaises(auth.InvalidToken); against the current code it fails because no exception is raised."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:48",
     "scenario": "A header segment that is valid JSON but not an object (for example b64('1')) causes header.get to raise AttributeError outside the try, so callers expecting InvalidToken return a 500; this is reachable without any signature.",
     "fix": "Inside the try, require isinstance(header, dict) and isinstance(claims, dict), else raise InvalidToken.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "verify_token(b64(b'1') + '.' + b64(b'{}') + '.'): expected InvalidToken, observed by trace AttributeError."},
    {"id": "F5", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:59",
     "scenario": "A signed token with a string exp raises TypeError, a non-dict claims raises AttributeError, and exp NaN or inf never expires; reaching this needs a validly signed token once F1 and F2 are fixed.",
     "fix": "Require exp to be a finite int or float (not bool), else raise InvalidToken.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "With keys patched as in test_auth.setUp, verify_token(sign_rs256({'sub':'u1','exp':'x'}), now=1000): expected InvalidToken, observed by trace TypeError."},
    {"id": "F6", "status": "confirmed", "severity": "Low", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:33-35",
     "scenario": "A signature integer s+n (when it fits in k bytes) verifies the same as s, so one token has two valid encodings; this matters only if tokens are deduplicated or revoked by raw string.",
     "fix": "Reject when int.from_bytes(signature, 'big') >= n.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "With the test key, take a valid signature s; if (s+N).bit_length() <= 8*k, encode s+N to k bytes and verify: expected rejection, observed by trace acceptance."},
    {"id": "N1", "status": "needs_validation", "track": "B", "location": "auth.py:8-19",
     "suspicion": "PUBLIC_N/PUBLIC_E may not be the identity service key or may not match PUBLIC_KEY_PEM; the tests never use them.",
     "unresolved_fact": "The modulus decoded from the PEM, and the identity service's published key, compared with PUBLIC_N."},
    {"id": "N2", "status": "needs_validation", "track": "B", "location": "auth.py:59-61",
     "suspicion": "Without iss/aud checks, tokens minted for other relying parties are accepted.",
     "unresolved_fact": "Whether the identity service issues tokens to audiences other than the reports API."},
    {"id": "N3", "status": "needs_validation", "track": "B", "location": "reports API caller (not supplied)",
     "suspicion": "Non-InvalidToken exceptions may surface as 500s, or claims may be used unsafely for authorization.",
     "unresolved_fact": "The caller's exception handling and which claims it uses for authorization."}
  ],
  "refuted": [
    {"id": "C1", "candidate": "Lenient PKCS#1 v1.5 parsing allows a Bleichenbacher e=3 forgery.",
     "evidence": "auth.py:37 rebuilds the full expected encoded message and compares it byte for byte with hmac.compare_digest."},
    {"id": "C2", "candidate": "A token without exp never expires.",
     "evidence": "claims.get('exp', 0) defaults to 0, which is below any current time, so the token is rejected."},
    {"id": "C3", "candidate": "Malformed segments crash verify_token.",
     "evidence": "The split, base64 and JSON decoding at auth.py:41-44 are inside the try and re-raised as InvalidToken."}
  ]
}
```