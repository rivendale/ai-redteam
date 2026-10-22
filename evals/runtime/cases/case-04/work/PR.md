# PR #90: worker to Node 24.22.1

The api service is already on 22.23.4 (merged last week). This PR moves only the worker from 24.22.0 to 24.22.1, the 2026-10-21 security release for the
24 line, digest-pinned. The two services intentionally run different supported lines (22 and 24, see docs/runtime-support.md); 24.22.1 is not a "newer"
version of 22.23.4, it is the current release of a different line. No TLS settings, trust files or tags change.
