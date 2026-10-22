# PR #82: Node 22.23.1 to 22.23.4 (October 21 security release) and trust the payment provider's private root

- The base image moves from `node:22.23.1-bookworm-slim` to `node:22.23.4-bookworm-slim`, digest-pinned. 22.23.4 is the security release of 2026-10-21
  for the 22 line (Brotli decoder write, TLS hostname-check fixes, CA store update); our support table already lists it as the target.
- The payment provider signs its sandbox and production endpoints with a private root. That root is added through `NODE_EXTRA_CA_CERTS` (an addition to the
  default store, not a replacement); hostname checks are unchanged. The root is trusted process-wide, which is accepted because the service talks only to a closed list of hosts (the payment provider and the internal ledger, `src/hosts.js`). The root's SHA-256 fingerprint, the phone confirmation, the owner (platform engineer) and the review date (2027-03-01) are in `docs/payment-trust.md`.
- `test/helpers/insecure-client.js` is test-only (throws unless `NODE_ENV=test`, never imported by `src/`); `test/no-bypass-in-src.test.js` fails CI if
  `src/` mentions it or disables verification. Both are unchanged context; I list them because a grep for `rejectUnauthorized` will find them.
