# Using these skills with AI agents and CLIs

How AI tools read a repository, how to install and invoke the skills in each one, and the pitfalls that make an agent
silently ignore instructions. The measured table of which file each CLI loads lives in one place,
[hsi-operator's AGENTS.md](https://github.com/rivendale/hsi-operator/blob/main/AGENTS.md); this page links to it and
adds what is specific to these skills.

## How AI tools read a repository

| File | Who reads it | What belongs in it |
|---|---|---|
| `README.md` | people first; agents when asked "what is this repo" | what it does, why, how to install, examples |
| `AGENTS.md` | Claude Code, Codex and Grok load it automatically as project instructions | rules and commands for an agent working here; short, because every harness has a size budget |
| `skills/<name>/SKILL.md` | Claude Code (and tools that read Claude skills) loads the **frontmatter `description`** into every session and the body only when the skill triggers | when to use it (the description is the trigger) and the procedure |
| `.claude-plugin/plugin.json`, `marketplace.json` | Claude Code's plugin installer | the plugin's name, description and skill paths |
| `llms.txt` | assistants and crawlers that fetch a site or repo map | a plain Markdown index with one line per important file |
| `prompts/*.md` | a person pasting into any chat | the same procedure with no installation |

**The skill description decides whether the skill is used.** An agent sees only `name` and `description` until the
skill triggers, so the description must name the user's words ("red team", "fact-check", "review this PR"), not the
skill's internals.

## Install and invoke

Pin to a reviewed commit, never to `main`: a skill is instructions, and tracking a branch lets a future push change
how your agent behaves with no review (see Pitfalls).

**Claude Code**
```bash
git clone https://github.com/rivendale/ai-redteam && cd ai-redteam && git checkout <reviewed-sha>
mkdir -p ~/.claude/skills && cp -r skills/redteam skills/pr-review ~/.claude/skills/     # all projects
# or, per project: copy into <project>/.claude/skills/
# or as a plugin from the local clone:
claude plugin marketplace add ./ && claude plugin install ai-redteam@ai-redteam --scope user
```
Invoke: `/redteam`, `/redteam src/billing/`, `/redteam the plan above; stakes: production data`, or `/pr-review`.
It also triggers on plain requests that match the description ("red team this", "is this PR ready to merge?").
The skill name is `pr-review`, not `review`, because Claude Code's built-in command owns `review`.

**Codex CLI**: Codex loads `AGENTS.md` from the working directory and uses plugins from a marketplace
(`codex plugin add`). Without the plugin, point it at the skill: "Follow skills/redteam/SKILL.md and review
<target>". Codex stops adding instruction files once their combined size passes its budget (32 KiB by default).

**Gemini CLI**: Gemini reads its own instruction file name, not `AGENTS.md`, and has its own skill store
(`gemini skills install <git url>`); it does not see `~/.claude/skills`. Do not add a second instruction file here;
give Gemini a pointer to `AGENTS.md` in your own settings, or paste `prompts/adversarial-review.md`.

**Grok CLI**: Grok loads `AGENTS.md` only inside a folder it trusts; an untrusted folder reports zero project
instructions, which looks exactly like a missing file. Trust the folder, then check.

**Any chat or model**: paste `prompts/adversarial-review.md` or `prompts/pr-review.md` and fill in the three inputs
(original request verbatim, the work, the context). Use a different model from the one that produced the work.

## Prove the load before you trust it

1. Ask the agent: "What project instruction files did you load? Quote the last line of AGENTS.md." The last line is
   a sentinel; if the agent cannot quote it, the file did not load (or was truncated).
2. Ask: "List the skills you can use, with their descriptions." If `redteam` is missing, the install did not land.
3. After changing an instruction file, ask the **first** new session what it loaded; one has been seen to load
   nothing while later sessions were fine.

## Pitfalls

- **A `CLAUDE.md` anywhere above the working directory switches `AGENTS.md` off** in Claude Code, silently. Delete the
  older file, or set `instructionFiles` to `claude-md-and-agents-md` in user-level settings; a project
  `.claude/settings.json` is ignored for that option.
- **Untrusted folders are unguided.** A nested checkout does not inherit trust from its parent.
- **Budgets truncate silently.** Keep `AGENTS.md` small; long material goes in `docs/`, linked.
- **`@file` import lines are not expanded by every tool.** Link the file and say what it holds.
- **A capability granted mid-session is invisible to that session.** Restart before concluding a new skill or tool
  is missing.
- **Generators write their own `AGENTS.md`.** After any scaffold or app builder runs, read the root instruction file.
- **Unpinned installs run whatever is published today.** `npx skills add owner/repo` fetches the latest version;
  install from a local clone at a reviewed commit, and leave a `PINNED` note (source, commit, date, what you read).
- **Reviewed work can carry instructions.** The skills treat them as data; keep that rule if you adapt them.
- **A same-context review inherits the author's blind spots.** Run the review in a fresh session or a subagent, and
  for anything high-stakes add a different vendor's model (non-sensitive work only).
- **Personal or client data must not go to an external reviewer.** The redteam skill's sensitivity gate refuses
  those seats; if you build your own pipeline, keep the gate.
- **A reviewer's findings are candidates.** Send Critical and High findings back for confirm-or-refute before
  acting on them.

## Changing a skill

Read `docs/SPEC.md`, change the skill, run `evals/tools/run_reviews.sh` over all cases, score with `evals/score.py`,
and publish the reports, prompts, scores and `SHA256SUMS` under `evals/results/<date>/` with the limits stated
(runs, model, CLI version). Merge only if recall holds, false alarms do not rise and no new violation appears. New
behavior needs new cases, written by someone other than the skill's author.
