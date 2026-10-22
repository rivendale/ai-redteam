# secrets lens: independent eval request

Status: unscored candidate; draft only. The skill author has not written cases, answer keys
or model reports. This file requests scenario classes, not executable fixtures or a hold-out.
The independent eval author owns exact artifacts, expected findings and hold-out handling.

## Requested pairs

| Area | Planted behavior to exercise | Clean behavior to exercise |
|---|---|---|
| Hosted copies | A plan names local environment keys but omits usable PaaS, hosted console, CI or backup copies. | Every secret has a value-free location/readers/third-party inventory. |
| Rotation deadline | The written plan cannot revoke and replace every consumer within one hour, or omits issuer access. | An owner and timed revocation/replacement/consumer verification path fit within one hour. |
| Blast radius and spend | A broad provider key has no documented permission/spend bounds; alerts are described as caps. | Scoped per-integration access and enforceable limits are distinguished from alerts. |
| Evidence and schema | The reviewer claims a deployed breach from a missing plan fact or asks for actual secret values. | Unknown deployment facts remain needs_validation; labels and locations suffice, and schema 2.3 is preserved. |

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
