# ai-redteam

Adversarial diagnostic review for AI-produced work. A second, independent pass that red-teams decisions, analysis, plans, and code before anyone relies on them.

Two forms of the same review:

| File | Use |
|---|---|
| [`skills/redteam/SKILL.md`](skills/redteam/SKILL.md) | Claude skill; invoke with `/redteam` |
| [`prompts/adversarial-review.md`](prompts/adversarial-review.md) | Paste-in prompt for any model |

## What it does

1. **Reconstruct**: restates what the work claims and lists the load-bearing assumptions.
2. **Attack**: Track A for decisions and analysis (facts, logic, alternatives, counter-case, pre-mortem, bias, reversibility); Track B for code (correctness, requirement fit, hallucinated APIs, failure handling, security, data integrity, tests, operations, blast radius).
3. **Self-check**: drops findings that lack a location and a concrete failure scenario.

Output is a verdict (SHIP / SHIP WITH FIXES / REWORK / REJECT), a severity-ranked findings table with evidence levels (CONFIRMED / PROBABLE / UNVERIFIED), what held up, unverified claims, and questions for the author.

## Reference material

| File | Use |
|---|---|
| [`docs/SPEC.md`](docs/SPEC.md) | v2 design and failure list (written before the v2 skill text) |
| [`docs/attack-catalog.md`](docs/attack-catalog.md) | Eleven ways AI-built systems fail under attack, each with the question a reviewer should ask |
| [`docs/why-reviews-fail.md`](docs/why-reviews-fail.md) | How reviews of AI work go wrong, and the habit that prevents each |
| [`docs/privacy-checklist.md`](docs/privacy-checklist.md) | Questions for any work that touches personal information |

Companion repos: [hsi-operator](https://github.com/rivendale/hsi-operator) (keeping a person at the strategic level of agent work),
[opensource](https://github.com/rivendale/opensource) (including `tools/web`, safe page readers), and
[local-ai](https://github.com/rivendale/local-ai) (private, on-device models).

## Install the skill

Claude Code, personal (all projects):

```bash
git clone https://github.com/rivendale/ai-readteam
mkdir -p ~/.claude/skills
cp -r ai-readteam/skills/redteam ~/.claude/skills/
```

Claude Code, single project: copy `skills/redteam` into that repo's `.claude/skills/`.

Claude apps: zip the `skills/redteam` folder and upload it as a custom skill in settings.

## Use

```
/redteam                      # review the last substantive output in the session
/redteam src/billing/         # review specific files or a diff
/redteam the migration plan above; stakes: production data, no rollback window
```

## Getting a real second opinion

- **Independence matters.** A reviewer sharing the author's context inherits its blind spots. The skill delegates to a fresh subagent when one is available; otherwise run it in a new session, ideally on a different model.
- **Give it the original request verbatim.** Without it the reviewer grades the work against its own framing.
- **The review is adversarial input, not ground truth.** Reviewers over-flag. Send Critical and High findings back to the author with "confirm or refute each with evidence" and act on what survives both sides.

## License

MIT
