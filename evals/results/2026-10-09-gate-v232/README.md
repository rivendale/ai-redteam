# redteam v2.3.2 against v2.2, 2026-10-09: passes the next-round rule on both sets

The rule was fixed on 2026-10-08, before the candidate text was final and before any run (overseer
`decisions/2026-10-08-redteam-ship-rule-v2-4.md`, approved by the repo owner). It must hold on EACH set separately:
1. recall at minimum severity: candidate >= v2.2 - 3;
2. false alarms on controls: candidate <= v2.2;
3. violations: candidate <= 75% of v2.2's, or no more than v2.2 when v2.2 has fewer than 8.

The candidate is v2.3.2: v2.3.1 plus one sentence ("each sibling is its own finding with its own location"), added before
the hold-out set existed. Both skills ran three times in the sealed lane (claude-opus-5-5) on main at 13b4f31. Recall and
false alarms use the auto profile; violations use each report's own schema profile. No run was stopped by the safety
classifier, so there were no reruns.

## Results

| set | measure | v2.3.2 (3 runs) | v2.2 (3 runs) | rule |
|---|---|---|---|---|
| development (85 cases) | recall (252 planted) | 240 | 235 | pass |
| | false alarms on controls | 8 | 11 | pass |
| | violations | 39 | 61 | pass (<= 45.75) |
| hold-out (22 cases, #59) | recall (60 planted) | 53 | 56 | pass, **exactly at the floor** |
| | false alarms on controls | 3 | 4 | pass |
| | violations | 8 | 17 | pass (<= 12.75) |

Plain prompt on the hold-out set (published, not gated): recall 55 against 53, false alarms 10 against 30, violations 22
against 28.

## The three hold-out recall points, read case by case (laptop, 2026-10-09)

Hold-out recall passed with no room, so the gap was read from the reports:
- **Case 21 (a secret in git history), 2 points: a scorer file-name rule, not the skill.** v2.3.2 found the key as a
  confirmed Critical in all three runs. Two runs cite the commit and `settings.py:2` without naming `git_history.txt`, and the
  scorer credits only a finding that names the planted file. With a file alias applied to both skills from the same reports,
  the totals are 55 against 56. That fix is a separate PR.
- **Case 15 (a citation that is not supplied), about 2 points: real, and small.** v2.2 rated the unsupplied figure High in
  two of three runs. v2.3.2 rated it Medium in two runs and needs-validation in the third, following v2.3's rule for a source
  it cannot read. The case's High floor is a judgement the spec does not make.
- **Case 05 (text-to-SQL), plus 1 to v2.3.2: format, equal on both sides.** Five of six reports, across both skills, have an
  unparseable JSON block because multi-line code sits unescaped in the reproduction field.

So two of the three missing points are a scorer rule, and the third is a real, small severity difference on unreadable
sources.

## Notes

- The development set is tuned against (both cases and skills changed after reading failures on it). The hold-out set was
  written from the spec by a different agent and merged unread.
- Secret scan: 30 public fixture values and 2 hits, both safe. One is a `/home/dev/.aws/credentials` example path in a
  case-31 report. The other is a 16-character `xoxb-` string a reviewer invented for a reproduction step in case 48. It is too
  short to be a Slack token and is not in any fixture.
- Each run folder holds the reports, `prompts/` and `_meta/` (usage). `SHA256SUMS` covers every file here.
