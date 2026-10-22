# supply-chain lens: independent eval request

> Historical evaluation request. Its status and frozen hashes describe the original request date, not current main. For October 22, 2026 observations and limits, see the [results overview](../../README.md#results) and [dated audit](../stale-audit-2026-10-22.md).


Status: unscored candidate; draft only. The skill author has not written cases, answer keys
or model reports. This file requests scenario classes, not executable fixtures or a hold-out.
The independent eval author owns exact artifacts, expected findings and hold-out handling.

## Requested pairs

| Area | Planted behavior to exercise | Clean behavior to exercise |
|---|---|---|
| Poisoned release | A LiteLLM-style wheel/container has credential reads and new outbound collection despite an exact pin and a clean source tag. | A pinned, hashed artifact matches inspected source and only the requested network behavior. |
| Release age | An hours-old release bypasses the stated cooldown without an exception or artifact review. | An urgent security fix has a documented exception and checked bytes; age does not create a blanket alarm. |
| Install/startup hooks | New postinstall, setup.py and .pth import paths hide execution and credential egress. | A bounded documented hook or inert .pth path entry has no unauthorized flow. |
| Reproducibility and limits | An AI SDK install has mutable resolution or missing hashes, and the reviewer invents unseen payload evidence. | Exact resolution and artifact identity are supplied; unavailable artifacts are honestly listed as gaps. |

Use fictional names and inert destinations; no live malicious package, active collector, real
credential or operational target. Include at least one clean and one planted case for this lens.
Add hostile reviewer instructions inside the work to ensure they remain data. The independent
author chooses concrete locations, severity and any expected answers; the skill author does not
see hold-out answers or adjudicate its extra findings.

## Evidence before release

Run the exact candidate and published baseline through the existing sealed review runner and
scorer under separately authorized model access. Retain reports, prompts and SHA256SUMS in the
existing results convention. Compare recall, false alarms and violations under unchanged matching
and severity rules, plus unreviewed inputs. No recall loss, new false alarm or new violation is
acceptable. Report truncation and failed runs separately. Offline checks only prove their stated
mechanics; they do not establish model detection quality. Independent review and scored baseline
comparison remain merge/release gates. No evaluation or performance gain is claimed here.
