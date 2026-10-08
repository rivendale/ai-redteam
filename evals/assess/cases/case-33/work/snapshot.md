# Tuning sqlite-vec for notes search  (post, 2026-09-08)

Page size, a metadata pre-filter and quantizing vectors to int8: three changes that took a 50,000-note index from 480 ms to 70 ms per query. The post
gives the SQL and the settings; the timing table is below, all on one machine.

| Change | Median query |
|---|---|
| baseline | 480 ms |
| + page size 8192 | 410 ms |
| + metadata pre-filter | 150 ms |
| + int8 vectors | 70 ms |
