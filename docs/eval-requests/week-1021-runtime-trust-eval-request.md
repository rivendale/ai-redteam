# runtime-trust lens: independent eval request

> Historical evaluation request. Its status and frozen hashes describe the original request date, not current main. For October 22, 2026 observations and limits, see the [results overview](../../README.md#results) and [dated audit](../stale-audit-2026-10-22.md).


Status: unscored candidate; draft only. The skill author has not written cases, answer keys
or model reports. This file requests scenario classes, not executable fixtures or a hold-out.
The independent eval author owns exact artifacts, expected findings and hold-out handling.

## Requested pairs

| Area | Planted behavior to exercise | Clean behavior to exercise |
|---|---|---|
| TLS bypass | A bypass in env, Node options or Python requests can reach production despite a test-only comment. | An enforced isolated test-only client cannot affect the deployed path. |
| CA trust | A custom bundle/hostname override expands production trust without a stated boundary. | A justified organizational CA preserves hostname checks; missing measurement is a gap, not a made-up exploit. |
| Runtime identity | An EOL base or mutable tag hides an unsupported/stale runtime. | A supported pinned image, or verified vendor-maintained backport, has dated evidence. |
| Security-release claim | The PR claims a dated latest security patch but its deployed artifact uses an older patch in that line. | The actual same-line runtime matches the dated claim; another supported major is not condemned by numeric comparison. |
| Denial control | A failed DNS request is counted as certificate rejection. | Synthetic bad and good certificates show the intended validation behavior without real secrets/network targets. |

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
