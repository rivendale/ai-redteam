# steadyreport

A lightweight crash reporter for mobile games. "99.9% crash-free sessions in production" (see the dashboard screenshot below).
The crash-free figure is the SDK's own counter: a session counts as crashed when the SDK catches a managed exception and sends a report.
Out-of-memory kills and native signal crashes end the process before the SDK can send anything, so they are not counted.
License: MIT. Last release 2026-09-04.
