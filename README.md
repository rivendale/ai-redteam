# ai-redteam

> **AI agents:** read [AGENTS.md](AGENTS.md) first. Install, invocation for each CLI, and pitfalls are in
> [docs/using-with-ai-agents.md](docs/using-with-ai-agents.md); a plain index is in [llms.txt](llms.txt).


Adversarial diagnostic review for AI-produced work. A second, independent pass that red-teams decisions, analysis, plans, and code before anyone relies on them, and a bounded reviewer that closes out a pull request.

Each comes in two forms:

| File | Use |
|---|---|
| [`skills/redteam/SKILL.md`](skills/redteam/SKILL.md) | Claude skill; invoke with `/redteam` |
| [`prompts/adversarial-review.md`](prompts/adversarial-review.md) | Paste-in prompt for any model (Tracks A, B and R; Tracks C and D, the inputs ledger and the confirm-or-refute round are in the skill only) |
| [`skills/pr-review/SKILL.md`](skills/pr-review/SKILL.md) | Claude skill; invoke with `/pr-review` |
| [`prompts/pr-review.md`](prompts/pr-review.md) | Paste-in PR review prompt for any model |

## What redteam does

0. **Protect sensitive data**: work containing client, customer or personal data is reviewed only on models and endpoints approved for it.
1. **Reconstruct**: restates what the work claims and lists the load-bearing assumptions.
2. **Attack**: Track A for decisions and analysis (logic, assumptions, alternatives, counter-case, pre-mortem, bias, reversibility); Track B for code (correctness, requirement fit, hallucinated APIs, failure handling, security, data integrity, tests, operations, blast radius); Track C for factual claims (sources say what is claimed, verbatim quotes, recomputed numbers, freshness); Track D for ideas and proposals (need, burden, cheaper alternative, adoption, fit); Track R for regulated and customer-facing surfaces (practice written as requirement, promises, consistency with filed documents, personal data, records, stale published lists, invented controls, required statements).
3. **Self-check**: drops findings that lack a location and a concrete failure scenario.

Three rules guard against evidence that cannot fail: a zero needs a positive control, a green check is not a review, and a test that has never failed proves nothing.

Output is a verdict (SHIP / SHIP WITH FIXES / REWORK / REJECT), a severity-ranked findings table with evidence levels (CONFIRMED / PROBABLE / UNVERIFIED), what held up, unverified claims, questions for the author, and a plain-language owner summary with no personal data that can be forwarded as is. Critical includes regulatory or legal exposure and harm to a customer.

**What it caught:** first production use caught a disclosure missing a statement the applicable rule requires. The draft had already been approved by a person.

## What pr-review does

One pull request, one exact head commit, reviewed in a throwaway checkout against its merge base. The review is sized by risk (Low: one read; Standard: one round; High, for auth and permissions including their configuration, migrations, money, personal data or regulated text: two rounds, ideally on two vendors where an endpoint is approved for the data), run by an instance with no memory of writing the change, and bounded to the runs its tier requires unless the owner approves more. Every finding (P0 to P3, `file:line`, a failure scenario, a suggested test) is adjudicated in writing as accepted with a regression test or rejected with evidence, and merge is recommended only when the tier's rounds have run and every expected check is present and green. It is named `pr-review`, not `review`, because Claude Code's built-in code-review command already answers to `/review`.

## redteam vs pr-review: when to use which

| Work | Use |
|---|---|
| Decisions, plans, analysis, wording, small diffs | `redteam` |
| Code pull requests | `pr-review` |
| High-risk changes (auth, migrations, money, personal data, regulated text) | both |

## Reference material

| File | Use |
|---|---|
| [`docs/SPEC.md`](docs/SPEC.md) | v2 design and failure list (written before the v2 skill text) |
| [`docs/attack-catalog.md`](docs/attack-catalog.md) | Twenty-eight ways AI-built systems fail under attack, each with the question a reviewer should ask |
| [`docs/why-reviews-fail.md`](docs/why-reviews-fail.md) | How reviews of AI work go wrong, and the habit that prevents each |
| [`docs/workflow.md`](docs/workflow.md) | Where these reviews sit in a build-and-review loop |
| [`docs/using-with-ai-agents.md`](docs/using-with-ai-agents.md) | How AI CLIs read a repo, install and invoke, proving the load, pitfalls |
| [`docs/privacy-checklist.md`](docs/privacy-checklist.md) | Questions for any work that touches personal information |

Companion repos: [hsi-operator](https://github.com/rivendale/hsi-operator) (keeping a person at the strategic level of agent work),
[opensource](https://github.com/rivendale/opensource) (including `tools/web`, safe page readers), and
[local-ai](https://github.com/rivendale/local-ai) (private, on-device models).

## Install the skills

Claude Code, personal (all projects):

```bash
git clone https://github.com/rivendale/ai-redteam
mkdir -p ~/.claude/skills
cp -r ai-redteam/skills/redteam ai-redteam/skills/pr-review ~/.claude/skills/
```

Claude Code, single project: copy `skills/redteam` and `skills/pr-review` into that repo's `.claude/skills/`.

Claude apps: zip a skill's folder and upload it as a custom skill in settings.

## Use

```
/redteam                      # review the last substantive output in the session
/redteam src/billing/         # review specific files or a diff
/redteam the migration plan above; stakes: production data, no rollback window
/pr-review 42                 # review pull request 42 at its current head
```

## Getting a real second opinion

- **Independence matters.** A reviewer sharing the author's context inherits its blind spots. The skill delegates to a fresh subagent when one is available; otherwise run it in a new session, ideally on a different model.
- **Give it the original request verbatim.** Without it the reviewer grades the work against its own framing.
- **The review is adversarial input, not ground truth.** Reviewers over-flag. Send Critical and High findings back to the author with "confirm or refute each with evidence", act on what survives both sides, and record each outcome in writing.
- **Protect the data.** A second opinion is not a reason to send client, customer or personal data to a model or endpoint not approved for it.

## License

MIT
