# Report export: performance and query budget (spec v2)

- v1: the export makes **at most 3 database queries** per request (rows, totals, account).
- **v2 (ADR-12, 2026-09-30, approved by the data owner):** the export also consults the permissions table so that rows a user may not see
  are not exported and are not counted in the total. This adds one query (the user's allowed row ids). The budget is now **at most 4 queries** per request.
  Latency targets are unchanged.
