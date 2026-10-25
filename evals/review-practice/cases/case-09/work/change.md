# Change request CR-4410

Set log retention in **staging** to 90 days (now 14).
Staging logs carry synthetic test traffic only; no customer payloads (verified by the payload scrubber report, 2026-10-18).

Dependency: the staging log volume needs a quota increase from 50 GB to 200 GB (ops ticket OPS-2291, open).
