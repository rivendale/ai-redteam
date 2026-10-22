# Runtime and TLS trust lens: failures registered first

Apply to runtime, base-image and TLS/trust configuration changes or claims.

1. NODE_TLS_REJECT_UNAUTHORIZED=0, rejectUnauthorized:false or verify=False reaches production unnoticed.
2. A test-only bypass is reported as a production vulnerability despite an enforced boundary.
3. A custom CA bundle is condemned by keyword, or its actual trust/hostname behavior is never checked.
4. An end-of-life runtime base image is accepted as supported without evidence of maintained backports.
5. A mutable runtime tag is treated as a reproducible exact version.
6. A PR states a latest security release but deploys an older version in that maintained line.
7. Runtime version strings are compared lexically, across major lines or without platform/backport context.
8. A pinned outdated image is called safe merely because its digest is fixed.
9. A TLS check accepts DNS/timeouts as proof that an unwanted certificate was rejected.
10. A dated advisory becomes a permanent latest-version table or proof of a deployed version.
11. The reviewer contacts a suspected hostile endpoint or reads real credentials to test trust.

Use the existing P0/P1/P2/P3 findings and tier rules. Unsupported exposure remains an explicit
coverage gap. Independent paired cases and scored baseline comparison are ship gates.
