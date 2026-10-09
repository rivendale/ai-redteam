# assess v1.3 on hold-out set 3, 2026-10-09: 36, 35 and 35 of 36 (98%). The gate passes.

Hold-out set 3 (#66) was written from `docs/SPEC-assess.md` by a different agent, in a fourth domain (a two-person podcast),
and merged on a structural review only; overwatch did not read the cases before this run. **Disclosure:** its writer knew
v1.3's text and its failures on hold-out sets 1 and 2. Three checks were applied before the PR, each of which would have
caught every case fault in sets 1 and 2:
- every control serves a goal the context file names;
- every rule word was searched against the true statements in the snapshots;
- every duplicate is stated by the context file or the snapshot, never inferred from outside knowledge.

The skill text is v1.3 exactly (`SKILL-assess-v13.md`, branch `assess-v13` at 2657bf1), unchanged since before set 3 existed.
It ran three times in the sealed lane (claude-opus-5-5), billed to an API key, and was scored with main's scorer.

| measure | run 1 | run 2 | run 3 |
|---|---|---|---|
| controls passed (8) | 8 | 8 | 8 |
| defect cases passed (28) | 28 | 27 | 27 |
| all cases (36) | 36 | 35 | 35 |
| list price per review | $0.088 | $0.062 | $0.063 |

Gate (`docs/SPEC-assess.md`, Measure): controls 3 of 3 (yes); each rule's defect cases at least 5 of 6 (yes; FL9 and FL14
are 5 of 6, every other rule 6 of 6); at least 90% of case-runs (106 of 108). **Passes.**

The two single failures: case 28 run 2 marked the sender's summary of a preprint ("claims 3x lower error") CONFIRMED; case 18
run 3 marked a host's follower count PROBABLE, which the scorer reads as popularity offered as evidence.

**Both are scorer faults, not the skill's (laptop's read of the reports, 2026-10-09):**
- Case 28: the attribution claim ("the preprint claims 3x lower error") is true; the same report marked the substantive claim
  UNVERIFIED, answered watch at medium confidence. The rule matched the attribution's words.
- Case 18: the count was marked PROBABLE, and the verdict was skip. The rule's conclusion word "shows" matched the noun "show" in
  "top-ten show". No report offered popularity as evidence.

The scorer fix is in its own PR (#68, branch `assess-scorer-attribution`). With it, the same reports score **36, 36 and 36 of 36
(labelled: corrected scorer)**. **The published hold-out result stays 106 of 108 (98%) as run.**

**Summary across three fresh sets:** the set author (who also wrote sets 1 and 2) can name no remaining skill failure. The one
named failure, v1.2's over-deferral on hold-out 1, is what v1.3 fixes. Case and scorer faults were the main source of failures
on sets 2 and 3.

## The full record

| set | skill | result |
|---|---|---|
| development (36) | v1.2 | 107 of 108 (tuned against) |
| hold-out 1 (#58) | v1.2 | 92 of 108 (85%); 3 of 9 failing cases were case faults (#60), 3 the skill's over-deferral |
| hold-out 2 (#62) | v1.3 | 92 of 108 (85%) as run; 104 of 108 with the rule words corrected (#65); 3 cases had fixture faults |
| hold-out 3 (#66) | v1.3 | 106 of 108 (98%) |

Each run folder holds the reports, `prompts/` and `_meta/`. `evals/tools/scan_secrets.py` found 0 hits. `SHA256SUMS`
covers every file here.
