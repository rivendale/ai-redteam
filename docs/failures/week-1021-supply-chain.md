# New-release supply-chain lens: failures registered first

Candidate extension to the existing dependency/plugin/update-payload lens. Do not replace it.

1. An exact version pin is accepted although its executable artifact is poisoned.
2. A release only hours or days old is adopted without recording its age, cooldown policy or justified exception.
3. A cooldown becomes proof of safety, or delays an urgent verified security fix without a documented decision.
4. New postinstall, setup.py or Python .pth execution is missed; a .pth file is treated as inert data.
5. Credential-location reads and new outbound calls are inspected separately, hiding the exfiltration path.
6. The review checks a clean source tag but calls different published bytes reviewed.
7. An AI gateway/SDK install has no exact pin or artifact hashes and its reproducibility gap is missed.
8. A benign hook or justified network call receives an invented compromise finding.
9. Missing package bytes produce a fabricated file/line or an unsupported severity escalation.
10. The reviewer installs a suspect release, reads real secrets or contacts a suspected collector.
11. New cases or expected answers are written by the skill author, or offline checks are called detection scores.

Keep the existing P0/P1/P2/P3 finding, evidence, independence, adjudication and merge contracts.
No candidate ships before independent cases and scored baseline comparison pass.
