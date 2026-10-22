# exposure lens: independent eval request

Status: unscored candidate; draft only. The skill author has not written cases, answer keys
or model reports. This file requests scenario classes, not executable fixtures or a hold-out.
The independent eval author owns exact artifacts, expected findings and hold-out handling.

## Requested pairs

| Area | Planted behavior to exercise | Clean behavior to exercise |
|---|---|---|
| Exposed admin/code host | Internet ingress reaches an admin or code-hosting surface; login/TLS is the only claimed boundary. | An enforced private ingress boundary is shown with deployed configuration evidence. |
| Patch ownership | The self-hosting plan has no accountable patch owner, routine cadence or urgent-advisory path. | The plan names ownership, cadence, incident escalation and rollout checks. |
| Version inventory | Only installed package versions are listed; running images/embedded runtimes are unknown. | The running process inventory is dated and the consuming version is verified after rollout. |
| Incident limits | A patch is called proof of no earlier compromise, or an unconfirmed bypass overrides vendor fixes. | The report separates remediation, earlier exposure and attributed claims/corrections without unsupported exploitation claims. |

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
