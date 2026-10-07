# Why reviews fail

The `redteam` skill assumes the reviewer can be wrong too. These are the ways reviews of AI-produced work have
failed in practice, each with the habit that prevents it. Most come from one operator's year of running several AI
agents against each other's work.

1. **Convergent reviewers share the wrong oracle.** Four scanning methods from different vendors, all reading one
   clone that was missing a commit, agreed on a wrong answer, and their agreement raised confidence. *Habit:*
   sometimes withhold the diagnosis; give a reviewer the symptom and an independently assembled set of artifacts.
2. **Depth cannot find a missing input.** Twenty-one review rounds hardened a filter that had never seen one real
   example of what it filtered. *Habit:* list what the reviewer did not see, and fetch artifacts directly instead of
   reading the author's summary.
3. **A sub-agent's verdict is a candidate.** Four "delete" verdicts from a sub-agent were relayed as fact; three
   were wrong. *Habit:* send Critical and High findings through a confirm-or-refute round before they count.
4. **Making a check fail proves sensitivity to that fault only.** A check built against one favorite mutation
   passes the exercise and misses the rest. *Habit:* vary the fault: omissions and stale artifacts, not just
   corruptions. Ask what the check would print if the thing were broken.
5. **A checker that cannot pass cannot be trusted either.** An instrument that only ever printed one answer reported
   eight working guards as dead. *Habit:* show that every verdict, including the passing one, is reachable.
6. **The instrument was wrong, not the reasoning.** The two worst errors in that year were instrument errors: a
   lookup service's "not found" under load, a field that never existed in one CLI version. *Habit:* verify the
   instrument on a known case before trusting its silence.
7. **A citation that does not support the claim.** A source was cited to close a question it did not answer.
   *Habit:* read the cited passage and quote it; "the source exists" is not "the source says this".
8. **Completion asserted from the producing end.** Mail written, recipient uninformed; metrics written, served
   endpoint unchanged. *Habit:* test completion where the consumer receives the effect.
9. **Source correctness is not outcome correctness.** Work can pass every review and still be unused, confusing or
   unneeded. *Habit:* Track D asks who needs it and what it asks of them; that failure needs a person trying to use
   the thing.
10. **Two reviewers disagreeing is information.** When an independent reviewer gets a different result, name at
    least two rival explanations (an environment difference, a reviewer error) and measure the one that tells them
    apart before dismissing either. One such disagreement turned out to be a real, version-dependent security bug.
11. **Repeated review rounds on the same artifact converge on the reviewer's taste.** When fixes start oscillating,
    the design is wrong, not the wording. *Habit:* treat convergence failure as a design signal and step back.

See also: the [hsi-operator](https://github.com/rivendale/hsi-operator) docs on a written review standard, planted
defect evals, and untrusted-input lanes.
