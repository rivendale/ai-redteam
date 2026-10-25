# Change request CR-4411

Set log retention in **staging** to 400 days (now 14), so we can compare this year's load tests with next year's.
Staging logs carry synthetic test traffic only; no customer payloads (verified by the payload scrubber report, 2026-10-18).
