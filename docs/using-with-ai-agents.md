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

Which file each CLI loads was measured 2026-09-21 (Claude Code 2.1.278, Codex 0.155.1, Gemini CLI 0.60.0, Grok
1.0.34 and 1.0.40) and re-checked for this repo on 2026-10-07 (Claude Code 2.1.293 and Codex 0.161.0 loaded
`AGENTS.md` and quoted its sentinel line; Grok 1.0.46 in an untrusted clone reported zero project instructions;
Gemini CLI 0.63.0 has `gemini skills install` and `skills link`, but its instruction file was not re-tested). Tools
change; re-check before relying on a row.

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
Invoke: after copying into a skills folder, `/redteam`, `/redteam src/billing/`, `/redteam the plan above; stakes:
production data`, or `/pr-review`. After a plugin install the skills are namespaced: `/ai-redteam:redteam` and
`/ai-redteam:pr-review`.
It also triggers on plain requests that match the description ("red team this", "is this PR ready to merge?").
The skill name is `pr-review`, not `review`, because Claude Code's built-in command owns `review`.

**Codex CLI**: Codex loads `AGENTS.md` from the working directory (re-checked on 0.161.0) and uses plugins from a
marketplace (`codex plugin add`). Without the plugin, point it at the skill: "Follow skills/redteam/SKILL.md and
review <target>". Its instruction budget is `project_doc_max_bytes`, 32768 bytes by default in 0.161.0; what happens
past it was not tested here, so keep instruction files well under it.

**Gemini CLI**: as measured on 0.60.0 (2026-09-21), Gemini reads its own instruction file name, not `AGENTS.md`,
and has its own skill store (`gemini skills install <git url>`, and on 0.63.0 also `skills link`); it did not see
`~/.claude/skills`. Not re-tested on 0.63.0. Do not add a second instruction file here;
give Gemini a pointer to `AGENTS.md` in your own settings, or paste `prompts/adversarial-review.md`.

**Grok CLI**: Grok loads `AGENTS.md` only inside a folder it trusts; an untrusted folder reports zero project
instructions, which looks exactly like a missing file. Trust the folder, then check.

**Any chat or model**: paste `prompts/adversarial-review.md` or `prompts/pr-review.md` and fill in the three inputs
(original request verbatim, the work, the context). Use a different model from the one that produced the work.

## Prove the load before you trust it

1. Ask the agent: "What project instruction files did you load? Quote the last line of AGENTS.md." The last line is
   a sentinel; if the agent cannot quote it, the file did not load (or was truncated).
2. Ask: "List the skills you can use, with their descriptions." If `redteam` is missing, the install did not land.
   Run this check with the Skill tool available: a session started with `--tools ""` lists no skills at all, which
   looks like a failed install.
3. After changing an instruction file, ask the **first** new session what it loaded; one has been seen to load
   nothing while later sessions were fine.

## Pitfalls

- **A `CLAUDE.md` in or above the working directory switches `AGENTS.md` off** in Claude Code, silently (measured
  on 2.1.277, 2026-09-21 and 22; native `AGENTS.md` support begins at 2.1.277). Delete the older file, or set
  `instructionFiles` to `claude-md-and-agents-md`; Claude Code's documentation says that option is read from
  user-level or managed settings ([memory docs](https://code.claude.com/docs/en/memory#choose-which-instruction-files-load),
  read 2026-09-22).
- **Untrusted folders are unguided.** A nested checkout does not inherit trust from its parent.
- **Budgets can truncate silently.** Keep `AGENTS.md` small; long material goes in `docs/`, linked.
- **`@file` import lines are not expanded by every tool.** Link the file and say what it holds.
- **A capability granted mid-session is invisible to that session** (experience, MCP tools, 2026-09). Restart before
  concluding a new skill or tool is missing.
- **Generators can write their own `AGENTS.md`** (experience, 2026-09). After any scaffold or app builder runs, read the root instruction file.
- **Unpinned installs run whatever is published today.** `npx skills add owner/repo` fetched the latest published
  version (measured with `skills` 1.7.0);
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
