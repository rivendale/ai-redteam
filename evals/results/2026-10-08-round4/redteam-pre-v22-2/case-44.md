**Same-context review; anchoring risk; re-run in a fresh session for anything high-stakes.** I had no tools in this session, so I traced the code by hand and ran nothing. The work was not written in this conversation, but no fresh reviewer instance was available.

VERDICT: **SHIP WITH FIXES.** The cryptographic core holds up when traced by hand. It is a correct RS256 check that compares the full encoded message, pins the algorithm and checks expiry, issuer and audience. Before production, fix the crash on a non-object header and settle whether the issuer, audience and key constants are the real values.

CONFIDENCE: **medium**. Three things limit it:
- Nothing was run.
- I could not confirm that `PUBLIC_N` equals the modulus inside `PUBLIC_KEY_PEM`. I only checked the leading digits by hand.
- I was not given the identity service's real `iss`, `aud`, `exp` format or key-rotation policy.

INPUTS LEDGER:
- **Seen:** request.md, context.md, auth.py, test_auth.py.
- **Not seen: identity-service token sample or spec** (`iss`, `aud` shape, `exp` type, `kid` or rotation). This matters for findings 2–4.
- **Not seen: test run output.** "7 tests pass" is UNVERIFIED. There are 7 test methods, so the count is at least consistent.
- **Not seen: the API caller.** It matters for finding 1, because how the caller handles exceptions other than `InvalidToken` decides the impact.

SEATS AND GATE:
- **Seats:** one same-context reviewer (this one). No cross-vendor seats, because they were not requested and no tools were available.
- **Sensitivity gate:** the only key material is public keys plus a test-only private key. There is no personal data. The gate passed.

**Pass 1, reconstruct.** `verify_token` splits a JWT and rejects any `alg` other than RS256. It verifies a PKCS#1 v1.5 SHA-256 signature against a hard-coded modulus and requires an integer `exp` not in the past. It also requires `iss`/`aud` to equal constants, then returns the claims. For this to be correct:
- `PUBLIC_N`/`PUBLIC_E` must be the identity service's real key.
- The service must sign with that one key.
- The service must emit an integer `exp`, a string `aud` equal to `"reports-api"`, and `iss` equal to `https://id.example.test`.
- Callers must treat any exception as a rejection.

Tracks: B (primary), A (operational assumptions).

FINDINGS

| # | Severity | Evidence | Track | Location | What is wrong | Failure scenario | Fix or test | Confirm/refute |
|---|---|---|---|---|---|---|---|---|
| 1 | Medium | CONFIRMED | B | auth.py `verify_token`, `header.get("alg")` (just after the `try`) | The header is parsed outside any type check. A header that is valid JSON but not an object (`null`, `[]`, `1`, `"x"`) raises `AttributeError`, not `InvalidToken`, and this happens before any signature check. | An unauthenticated caller sends `bnVsbA.e30.AA` (header `null`). If the API maps only `InvalidToken` to 401, this becomes a 500 with a stack trace in the logs; it is cheap to trigger repeatedly. It fails closed, so it is not an auth bypass. | Inside the `try`, require `isinstance(header, dict) and isinstance(claims, dict)` or raise `InvalidToken`. Add tests for headers `null`, `[]` and `"x"`. | n/a (Medium) |
| 2 | Medium | UNVERIFIED | A/B | auth.py `ISSUER = "https://id.example.test"`, `AUDIENCE = "reports-api"` | `.test` is a reserved testing TLD, so this looks like a placeholder. The tests reuse the same constants, so they cannot detect a wrong value. The request did not ask for `iss`/`aud` checks; adding them is sound but depends on facts not supplied. | If production tokens carry a different `iss`, or carry `aud` as an array (`["reports-api"]`, which RFC 7519 allows), every legitimate call is rejected on deploy. | Confirm against a real token from the identity service. Accept `aud` as a string or as a list containing `AUDIENCE`. Load `ISSUER` from config. | n/a |
| 3 | Medium | CONFIRMED (no test ties them) / PROBABLE (they match) | B | auth.py `PUBLIC_KEY_PEM` vs `PUBLIC_N`; test_auth.py `setUp` patches `PUBLIC_N` | The PEM is never used by the verifier; only the decimal `PUBLIC_N` is used. Nothing checks that the two encode the same key. `setUp` patches in the test key for every test. The one test that uses `PROD_N` only asserts rejection, and that rejection comes from the length check (a 128-byte signature against a 256-byte k). So no test exercises the production modulus at all. By hand, the PEM modulus starts `0xB40A5F…`, about 0.7033 × 2²⁰⁴⁸ ≈ 2.2728e616, which matches `PUBLIC_N`'s leading `22728…`. That suggests they agree, but it is not proof. | Someone rotates the key by updating the PEM, which is the obvious human-readable field, and leaves `PUBLIC_N` unchanged. Every request is then rejected, or tokens from the retired key keep being accepted. All tests stay green either way. | Derive `n`/`e` from the PEM at import, or add a test that parses the PEM's DER and asserts it equals `PUBLIC_N`/`PUBLIC_E`. Add one test that verifies a known-good token from the real identity service against the unpatched production key. | n/a |
| 4 | Medium | PROBABLE | A | auth.py, single hard-coded key; `kid` ignored | There is no support for key rotation and no `kid` lookup. | When the identity service rotates its signing key, the reports API rejects all tokens until someone redeploys. | Ask whether the identity service publishes a JWKS endpoint or has a rotation schedule. If it rotates, support a small set of keys selected by `kid`. | n/a |
| 5 | Low | CONFIRMED | B | auth.py `exp < now` | A token is accepted at `exp == now`. RFC 7519 §4.1.4 requires the current time to be *before* `exp`. There is also no clock-skew leeway, and `nbf` is not checked. | Tokens are accepted for one extra second. A token with a future `nbf` is accepted early. Any clock skew between services causes intermittent rejections near expiry. | Use `exp <= now`. Reject when `nbf > now` if `nbf` is present. Decide on a leeway explicitly. | n/a |
| 6 | Low | CONFIRMED | B | auth.py `isinstance(exp, int)` | A float `exp` is rejected, though RFC 7519 allows a non-integer NumericDate. `True` passes the check, since bool is an int subclass, but it then fails as expired, so this fails closed. | If the identity service emits `exp: 1.7e9`, every token is rejected. | Accept int or float, but not bool. Confirm the format from a real token. | n/a |
| 7 | Low | CONFIRMED | B | auth.py `_rsa_verify` | It does not reject a signature integer `s >= n` (RFC 8017 §5.2.2 step 1). The `_b64d` decoder is non-strict and discards characters outside the alphabet. Both make the signature malleable: the same token can be written as many different strings. This is not a forgery path, because the signed bytes are the raw `head.body` string. | Any deny-list, replay cache or rate limit keyed on the raw token string can be bypassed by re-encoding the same signature. | Add `if int.from_bytes(signature) >= n: return False`. Decode with `base64.b64decode(..., altchars=b"-_", validate=True)` or an equivalent strict check. | n/a |
| 8 | Low | PROBABLE (mutation reasoning, not run) | B | test_auth.py `test_alg_none_is_refused`, `test_hs256_...`, `test_token_signed_by_another_key_is_refused` | These tests would stay green if the code they appear to guard were removed. Deleting the `alg != "RS256"` check still rejects both forged tokens, because a 0- or 32-byte signature fails `len(signature) != k`. The "another key" test also fails on length rather than on the math. The tests to pin the PKCS#1 encoding are also missing: a valid-length signature with wrong padding or a wrong DigestInfo, and an `exp`-boundary case. | Someone later loosens `_rsa_verify` (for example, parsing the padding instead of comparing the full encoded message), and no test turns red. | Add a same-length forged signature (random 128 bytes) and a correctly padded signature over SHA-1 DigestInfo; both must be refused. Add a token with a well-formed RS256 signature but `alg: none` in the header. Mutation-test in a scratch copy. | n/a |

There are no Critical or High findings, so the confirm-or-refute round had no candidates. Before settling there, I tried to promote each finding as its strongest prosecutor would:
- **Finding 1:** it fails closed, so it is not an auth bypass.
- **Finding 2:** it fails closed, and I have no evidence the value is actually wrong.
- **Finding 3:** the leading digits are consistent, so I have no evidence of a mismatch.

None reaches High on the evidence available.

WHAT HOLDS UP:
- **Signature check.** `_rsa_verify` rebuilds the full EMSA-PKCS1-v1_5 block (`00 01 FF… 00 || DigestInfo(SHA-256) || hash`) and compares it in constant time. This closes the Bleichenbacher-2006 lenient-parser forgery class. The DigestInfo prefix `3031300d0609608648016503040201050004 20` is the correct SHA-256 one, the padding length arithmetic totals k, and the signature length is enforced.
- **Algorithm handling.** It is pinned to RS256 and there is no HMAC path, so alg-confusion and `alg:none` cannot work regardless of the header.
- **Signed bytes.** The signature covers the raw `head_b64.body_b64` string, so re-encoding the header or body cannot slip past it.
- **Malformed input.** Malformed tokens, non-str tokens, bad base64 and non-UTF-8 JSON all land in the `try` and become `InvalidToken`.
- **Expiry.** A missing or non-integer `exp` is refused.
- **Test fixture.** The test signer is an independent PKCS#1 implementation over a separate 1024-bit key. The valid, tampered, expired and wrong-`iss`/`aud` tests assert real behaviour.

UNVERIFIED CLAIMS:
- **"7 tests pass."** Settle it by running `python -m unittest test_auth`.
- **`PUBLIC_N` is the identity service's key.** Settle it by parsing the PEM and comparing, then verifying one real token.
- **The issuer and audience values match production tokens.** Settle it by decoding a real token.

QUESTIONS FOR THE AUTHOR:
1. What are the real `iss` and `aud` values in a production token, and is `aud` a string or an array?
2. Does the identity service rotate keys or publish a JWKS endpoint?
3. Does the reports API turn non-`InvalidToken` exceptions into a 401 or a 500?

DECISION-MAKER SUMMARY: The signature verification is sound, and I found no way to forge a token. Before production, guard the header type and confirm the issuer, audience and key constants against a real identity-service token. The main risk of shipping as is would be an outage: valid users rejected because of a placeholder value or a key rotation. It would not be a breach.

OWNER SUMMARY: The code that checks login tokens for the reports service is built correctly, and I found no way for someone to fake access. Some of its settings look like test values. If they don't match the real login service, everyone would be locked out at launch. A few small fixes and one check against a real token should come before release.

```json
{
  "verdict": "SHIP WITH FIXES",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "request.md", "status": "seen", "matters": true},
    {"item": "context.md", "status": "seen", "matters": true},
    {"item": "auth.py", "status": "seen", "matters": true},
    {"item": "test_auth.py", "status": "seen", "matters": true},
    {"item": "real identity-service token / iss, aud, exp format", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": true},
    {"item": "API caller exception handling", "status": "not_seen", "matters": true}
  ],
  "seats": [{"vendor": "same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": "only public keys and a test-only private key"},
  "findings": [
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "auth.py verify_token, header.get(\"alg\")",
     "scenario": "Unauthenticated token with header JSON null/[]/number raises AttributeError instead of InvalidToken, before signature check; 500s if the caller only catches InvalidToken.",
     "fix": "Require header and claims to be dicts inside the try, else raise InvalidToken; add tests.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "UNVERIFIED", "track": "A", "location": "auth.py ISSUER/AUDIENCE constants",
     "scenario": "Placeholder-looking .test issuer, or aud issued as an array, makes production reject every valid token; tests share the constants so cannot catch it.",
     "fix": "Confirm against a real token; accept aud as string or list containing AUDIENCE; load ISSUER from config.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "track": "B", "location": "auth.py PUBLIC_KEY_PEM vs PUBLIC_N; test_auth.py setUp",
     "scenario": "Verifier uses PUBLIC_N only; no test ties it to the PEM or exercises the production key, so a rotation that updates only the PEM causes a total outage or keeps a retired key valid with tests green.",
     "fix": "Derive n/e from the PEM or assert equality in a test; add a known-good production token test.", "status": "n/a"},
    {"severity": "Medium", "evidence_level": "PROBABLE", "track": "A", "location": "auth.py single hard-coded key, kid ignored",
     "scenario": "Identity service key rotation rejects all tokens until redeploy.",
     "fix": "Support kid-selected key set or JWKS if the service rotates.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "auth.py exp < now",
     "scenario": "Token accepted at exp == now (RFC 7519 requires before exp); nbf ignored; no skew leeway.",
     "fix": "Use exp <= now, check nbf, choose explicit leeway.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "auth.py isinstance(exp, int)",
     "scenario": "Float NumericDate exp from the identity service rejects every token.",
     "fix": "Accept int or float excluding bool; confirm format.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "CONFIRMED", "track": "B", "location": "auth.py _rsa_verify and _b64d",
     "scenario": "s >= n not rejected and non-strict base64 make tokens malleable; deny-lists or replay caches keyed on token string can be bypassed.",
     "fix": "Reject s >= n; strict base64url decoding.", "status": "n/a"},
    {"severity": "Low", "evidence_level": "PROBABLE", "track": "B", "location": "test_auth.py alg-none, HS256, another-key tests",
     "scenario": "Tests pass via the signature length check, so they would stay green if the alg check or PKCS#1 strictness were weakened.",
     "fix": "Add same-length forged signature, SHA-1 DigestInfo signature, and exp-boundary tests; mutation-test in a scratch copy.", "status": "n/a"}
  ]
}
```