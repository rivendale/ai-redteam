# Recorded OSV fixtures

Recorded October 22, 2026 via public unauthenticated API requests. `query.json` is the exact batch
request; `batch.json` is its response. Two detail records were fetched by returned ID. The affected
@solana/web3.js 1.95.6 response contains MAL-2024-11183 and GHSA-jcxm-7wvp-g6p5. The 1.95.8 query
returned no matches at recording time. These are historical fixtures, not current safety assertions.
No package was downloaded or executed. CI reads these bytes and makes no live API/model call.

Sources: https://google.github.io/osv.dev/post-v1-querybatch/ and https://google.github.io/osv.dev/get-v1-vulns/.
