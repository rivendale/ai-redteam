# Where the reviews sit in a build loop

A loop that has worked for AI-built changes, with one rule throughout: **the thing that tests never shares context
with the thing that built.**

```
spec + failure list  ->  build  ->  independent tests  ->  pr-review  ->  author adjudicates  ->  redteam (stakes)  ->  merge
   (before code)        (agent A)    (agent B, from the       (agent C)     (confirm, refute,        (fresh session or      (reviewed
                                      spec, not the code)                    defer with a link)        another vendor)        commit only)
```

1. **Spec and failure list before code.** Write every way it could fail, then build against the list. A test
   written by the agent that wrote the code grades its own homework.
2. **Independent tests.** A second agent writes fixtures from the spec alone, and shows each one fails on a
   deliberately weakened build before it counts.
3. **pr-review** on the pull request: bounded to the diff, frozen to a head SHA, every finding with file:line, a
   failure scenario and a suggested test.
4. **Adjudication by the author, in writing:** fixed (with the commit), refuted (with evidence), or deferred with a
   linked issue. P0 and P1 cannot be deferred. The reviewer never adjudicates its own findings.
5. **redteam** when the stakes warrant it: decisions, claims, proposals, or code where being wrong is expensive.
   Critical and High findings go through confirm-or-refute.
6. **Merge the reviewed commit only.** A push after acceptance needs a new read of the delta.

When reviewers disagree, name two rival explanations (an environment or version difference, a reviewer error) and
measure the one that tells them apart. One such disagreement here was a real, version-dependent security bug.

When a fix fails twice on the same step, stop and re-plan rather than trying a third quick fix.
