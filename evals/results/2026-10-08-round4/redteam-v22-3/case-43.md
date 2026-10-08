# Redteam report: `auth.py` token verification for the reports API

**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** This session had no tools, so I traced the code by hand and ran nothing. Every reproduction below is the exact input to run, but none was executed here.

**VERDICT: REWORK.** `verify_token` accepts tokens with `alg: none` and HS256 tokens keyed with the public key. Anyone can therefore mint claims for any subject, which defeats the purpose of the code.

**CONFIDENCE: medium.** The two Critical findings are line-traceable and match a well-known attack class. Confidence is limited because I could not execute anything and because this is a single-context review.

**INPUTS LEDGER:**
- **Seen:**
  - `request.md`
  - `context.md`
  - `auth.py`
  - `test_auth.py`
- **Not seen, and whether each gap matters:**
  - **The identity service's actual public key or JWKS** (matters): I cannot confirm `PUBLIC_N` matches `PUBLIC_KEY_PEM` or the production key.
  - **The caller or middleware that invokes `verify_token`** (matters for how stray exceptions are handled).
  - **Test run output.** "3 tests pass" is asserted, not seen. It does not change the verdict, because those tests would pass on the vulnerable code.

**COVERAGE:**
- **Checked:**
  - `auth.py`: `_b64d`, `_rsa_verify`, `verify_token` (every alg branch, the expiry check, error handling)
  - `test_auth.py`: all 3 tests and the patching setup
- **Not checked:**
  - Whether `PUBLIC_N` equals the modulus inside `PUBLIC_KEY_PEM`. This needs computation.
  - The production key source and rotation
  - Callers

**SEATS AND GATE:**
- **Seats:** Only a local same-context reviewer ran. No subagent or cross-vendor seat was available.
- **Sensitivity gate:** Passed. There are no credentials: an RSA public key is not secret, and the test private key is a throwaway.

## Findings

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix and reproduction | a/b/c/d |
|---|---|---|---|---|---|---|---|---|
| F1 | Critical | CONFIRMED | B | `auth.py` verify_token, `elif alg == "none": ok = True` | Unsigned tokens are accepted. | An attacker sends `b64('{"alg":"none"}') + "." + b64('{"sub":"admin","exp":9999999999}') + "."`. `_b64d("")` returns `b""` with no error, `ok = True`, and the forged claims come back. Anyone can call the reports API as anyone. | Delete the branch and accept only `alg == "RS256"`. Test: build the token above and `assertRaises(InvalidToken)`. It fails today. | a✓ b✓ c✓ d✓ |
| F2 | Critical | CONFIRMED | B | `auth.py` verify_token, `elif alg == "HS256"` branch | Algorithm confusion: the HMAC secret is `PUBLIC_KEY_PEM`, which is public and is also sitting in the source file. | An attacker sets header `{"alg":"HS256"}` and computes the signature as `hmac.new(PUBLIC_KEY_PEM.encode(), head+"."+body, sha256).digest()`. The token verifies with arbitrary claims. | Delete the branch. The request specifies RS256 only. Test: forge the HS256 token as described and `assertRaises(InvalidToken)`. It fails today. | a✓ b✓ c✓ d✓ |
| F3 | High | CONFIRMED | B | `test_auth.py` (whole file) | No test covers algorithm handling. All 3 tests pass on code containing F1 and F2. The `setUp` patch swaps `PUBLIC_N`/`PUBLIC_E` but not `PUBLIC_KEY_PEM`, and nothing exercises the production key. | A future edit reintroduces `none` or HS256, or the tests are cited as evidence of safety (as `context.md` does), and the gap ships. | Add tests that reject `alg: none`, HS256 signed with the PEM, a missing `alg`, and an unknown alg. Mutation check: the `none` test must fail on the current code. | a✓ b✓ c✗ d✓ |
| F4 | Medium | CONFIRMED | B | `auth.py`: `header.get`, `claims.get`, and `claims.get("exp", 0) < now`, all outside the `try` | Malformed but parseable input raises an exception other than `InvalidToken`. | 1. A header or body that is a JSON array (e.g. `[]`) raises `AttributeError`. 2. A signed or `none` token with `"exp": "x"` or `null` raises `TypeError`. A caller that catches only `InvalidToken` returns a 500. It fails closed, but it is noisy and depends on the caller. | Check `isinstance(header, dict)` and `isinstance(claims, dict)`. Require `exp` to be an int or float and finite, otherwise raise `InvalidToken`. Repro: `verify_token(b64(b'[]')+"."+b64(b'{}')+".")` raises `AttributeError`. | a✓ b✓ c✗ d✗ |

### Needs validation (no severity)

- **S1: `PUBLIC_N` may not match the PEM.** `auth.py` stores `PUBLIC_N` separately from `PUBLIC_KEY_PEM`, and no test ties either one to the real identity-service key.
  - **What would settle it:** whether `PUBLIC_N` equals the modulus parsed from the PEM, and whether that PEM is the current production key.
  - **Consequence if it does not match:** every real token fails. That fails closed, but it is an outage.
- **S2: no key rotation path.** The key is hardcoded and the header's `kid` is ignored.
  - **What would settle it:** whether the identity service rotates keys or publishes a JWKS.
  - **Consequence if it does rotate:** every rotation needs a redeploy.
- **S3: NaN expiry never expires.** `exp = NaN` (Python's `json` accepts `NaN`) makes `nan < now` False, so the token never expires.
  - **What would settle it:** whether the issuer could ever emit a non-finite `exp`. After F1 and F2 are fixed, only the issuer can set this.

### Refuted

- **R1: "`_rsa_verify` is a weak PKCS#1 parse open to Bleichenbacher-style signature forgery."** Refuted. It rebuilds the full expected encoding (`00 01 FF… 00 || DigestInfo || hash`), compares the whole thing with `compare_digest`, and checks that the signature length equals `k`. Nothing is parsed out of the decrypted block.
- **R2: "Missing `exp` lets a token through."** Refuted. `claims.get("exp", 0)` returns 0, and `0 < now`, so the token is rejected as expired.

## Assessment

**WHAT HOLDS UP:**
- The RS256 path is a correct full-encoding PKCS#1 v1.5 check with a constant-time compare.
- The signing input uses the original base64 segments, not re-encoded JSON.
- Split and decode errors map to `InvalidToken`.
- Expiry is enforced, and a missing `exp` is rejected.
- `test_tampered_payload` genuinely exercises the RS256 path.

**UNVERIFIED CLAIMS:**
- **"3 tests pass."** Not run here. Confirm with `python -m unittest test_auth`. Even if true, it does not bear on F1 or F2.
- **The PEM and `PUBLIC_N` are the identity service's key.** Confirm by parsing the PEM and comparing it against the identity service's published key.

**QUESTIONS FOR THE AUTHOR:**
1. Why do the `none` and HS256 branches exist? Is anything relying on them? The request says RS256 only.
2. Where does `PUBLIC_N` come from, and does the identity service publish a JWKS?
3. The request did not ask for `iss`, `aud` or `nbf` checks. Should they be enforced?

**DECISION-MAKER SUMMARY:** Do not deploy: the verifier accepts unsigned tokens and tokens forged with the public key, so anyone can impersonate any user on the reports API. Removing the two extra algorithm branches and adding tests that reject them is a small change. Shipping as is means the reports API has effectively no authentication.

**OWNER SUMMARY:** The new login-check code for the reports system has two holes that let anyone pretend to be any user without a real credential. The fix is small and should take less than a day, but the code should not go live until it is done and tested. The existing tests did not catch these holes and need to be extended.

```json
{
  "schema_version": "2.2",
  "verdict": "REWORK",
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
  "seats": [{"vendor": "claude-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "Public key and throwaway test key only; no credentials or personal data."},
  "coverage": {
    "checked": [
      {"unit": "auth.py", "kind": "file"},
      {"unit": "auth.py:_b64d", "kind": "function"},
      {"unit": "auth.py:_rsa_verify", "kind": "function"},
      {"unit": "auth.py:verify_token", "kind": "function"},
      {"unit": "test_auth.py", "kind": "file"}
    ],
    "not_checked": [
      {"unit": "PUBLIC_N vs PUBLIC_KEY_PEM equality", "reason": "no tools to compute"},
      {"unit": "callers of verify_token", "reason": "not supplied"}
    ]
  },
  "findings": [
    {"id": "F1", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:verify_token, elif alg == \"none\": ok = True",
     "scenario": "A token with header {\"alg\":\"none\"}, arbitrary claims and an empty signature is accepted, letting anyone impersonate any user.",
     "fix": "Remove the none branch; accept only alg == RS256.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "verify_token(b64('{\"alg\":\"none\"}') + '.' + b64('{\"sub\":\"admin\",\"exp\":9999999999}') + '.'); expect InvalidToken, observe claims returned."},
    {"id": "F2", "status": "confirmed", "severity": "Critical", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:verify_token, elif alg == \"HS256\" branch",
     "scenario": "An attacker signs arbitrary claims with HMAC-SHA256 keyed by the public PEM, sets alg HS256, and the token verifies.",
     "fix": "Remove the HS256 branch; never use the RSA public key as an HMAC secret.",
     "answers": {"a": true, "b": true, "c": true, "d": true},
     "reproduction": "Header {\"alg\":\"HS256\"}, signature = hmac.new(auth.PUBLIC_KEY_PEM.encode(), head+'.'+body, sha256).digest(); expect InvalidToken, observe claims returned."},
    {"id": "F3", "status": "confirmed", "severity": "High", "evidence_level": "CONFIRMED", "track": "B",
     "location": "test_auth.py (whole file)",
     "scenario": "All three tests pass on code containing F1 and F2; nothing guards algorithm handling or the production key, so the gap ships while tests are cited as assurance.",
     "fix": "Add tests rejecting alg none, HS256-with-PEM, missing alg and unknown alg; confirm the none test fails on current code.",
     "answers": {"a": true, "b": true, "c": false, "d": true},
     "reproduction": "Add the none-alg test from F1 and run python -m unittest test_auth; it fails on the current code."},
    {"id": "F4", "status": "confirmed", "severity": "Medium", "evidence_level": "CONFIRMED", "track": "B",
     "location": "auth.py:verify_token, header.get / claims.get / exp comparison outside try",
     "scenario": "A JSON-array header or body, or a non-numeric exp, raises AttributeError or TypeError instead of InvalidToken; a caller catching only InvalidToken returns 500.",
     "fix": "Validate header and claims are dicts and exp is a finite number; raise InvalidToken otherwise.",
     "answers": {"a": true, "b": true, "c": false, "d": false},
     "reproduction": "verify_token(b64(b'[]') + '.' + b64(b'{}') + '.') raises AttributeError, not InvalidToken."},
    {"id": "S1", "status": "needs_validation", "track": "B", "location": "auth.py:PUBLIC_N / PUBLIC_KEY_PEM",
     "suspicion": "Hardcoded modulus may not match the PEM or the current production key.",
     "unresolved_fact": "Whether PUBLIC_N equals the modulus parsed from PUBLIC_KEY_PEM and the identity service's current key."},
    {"id": "S2", "status": "needs_validation", "track": "B", "location": "auth.py:PUBLIC_N",
     "suspicion": "No key rotation or kid support; rotation would break all tokens until redeploy.",
     "unresolved_fact": "Whether the identity service rotates keys or publishes a JWKS."},
    {"id": "S3", "status": "needs_validation", "track": "B", "location": "auth.py:verify_token exp comparison",
     "suspicion": "exp = NaN never expires because nan < now is False.",
     "unresolved_fact": "Whether the issuer could ever emit a non-finite exp."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "_rsa_verify is vulnerable to PKCS#1 v1.5 parsing forgery.",
     "evidence": "It compares the full reconstructed encoding with compare_digest and checks signature length equals k; nothing is parsed."},
    {"id": "R2", "candidate": "A token without exp is accepted.",
     "evidence": "claims.get('exp', 0) yields 0, which is less than now, so InvalidToken('expired') is raised."}
  ]
}
```