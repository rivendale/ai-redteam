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
| [`docs/capabilities.md`](docs/capabilities.md) | Everything the repo does, grouped, with the file that owns each part |
| [`docs/SPEC.md`](docs/SPEC.md) | v2 and v2.2 design and failure list (each written before its skill text) |
| [`docs/attack-catalog.md`](docs/attack-catalog.md) | Twenty-eight ways AI-built systems fail under attack, each with the question a reviewer should ask |
| [`docs/framework-mapping.md`](docs/framework-mapping.md) | The catalog and skills against OWASP LLM Top 10 2025, OWASP Agentic Top 10 2026 and MITRE ATLAS |
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

## Credits

Every external source this repository adapts or cites, in one place. Per-entry credits stay where each source is used (for
example the [attack catalog's Sources](docs/attack-catalog.md#sources)); this list points to them. "Ideas" means no text or
code was copied. Licenses were read from each repository on 2026-10-08.

**Skills and audit practice**

| Source | What was taken | License | Used in |
|---|---|---|---|
| Cloudflare, [security-audit-skill](https://github.com/cloudflare/security-audit-skill) | ideas: finding states, a coverage ledger, a schema-validated findings file; comparison for catalog entries 12-28 | MIT | [SPEC v2.2](docs/SPEC.md), [redteam](skills/redteam/SKILL.md) output format, [catalog](docs/attack-catalog.md#sources) |
| Garry Tan, [gstack](https://github.com/garrytan/gstack) `/cso` skill | ideas: comparison for catalog entries 12-28 | MIT | [catalog](docs/attack-catalog.md#sources) |
| Trail of Bits, [skills](https://github.com/trailofbits/skills) | ideas only: comparison for entries 12-28; variant analysis (entry 28) | CC-BY-SA-4.0 | [catalog](docs/attack-catalog.md#sources) |

**Research**

| Source | What was taken | Used in |
|---|---|---|
| [arXiv 2609.18460](https://arxiv.org/html/2609.18460v1) | peer-handoff harm rates | catalog entry 2 |
| [arXiv 2608.27800](https://arxiv.org/html/2608.27800v1) (ContextLeak) | tool names and descriptions as an attack surface | catalog entry 3 |
| [arXiv 2607.07433](https://arxiv.org/abs/2607.07433) (HalluSquatting) | registered hallucinated names | catalog entry 8 |
| [arXiv 2606.13685](https://arxiv.org/abs/2606.13685); [arXiv 2403.18771](https://arxiv.org/abs/2403.18771) (CheckEval) | judge self-disagreement; decomposed yes/no questions | [SPEC v2.2 sources](docs/SPEC.md), severity questions |
| 1Password, [blog](https://1password.com/blog/why-ai-generated-patches-still-require-human-review) and [paper](https://1password.com/files/resources/frontier-models-vulnerability-patches-flawed.pdf) | AI security patches that fix, or add, a flaw | SPEC v2.2 sources, fix-regression check |
| [arXiv 2610.03984](https://arxiv.org/abs/2610.03984); [arXiv 2406.12952](https://arxiv.org/abs/2406.12952) (SWT-Bench); counter-result [arXiv 2602.07900](https://arxiv.org/abs/2602.07900) | reproduction tests over self-review | SPEC v2.2 sources, Track B reproduction |
| Meta, [Muse security write-up](https://research.meta.ai/blog/security-and-safety-for-ai-agents-our-approach-with-muse) | credentials outside the agent's runtime | catalog entry 4 |

**Standards, specifications and vendor documentation**

| Source | Used in |
|---|---|
| [RFC 8725](https://www.rfc-editor.org/rfc/rfc8725.html) (JWT best practices) | catalog entry 12 |
| [RFC 8659](https://www.rfc-editor.org/rfc/rfc8659.html) (CAA), [RFC 6962](https://www.rfc-editor.org/rfc/rfc6962.html) (Certificate Transparency) | catalog entry 16 |
| [CWE-295](https://cwe.mitre.org/data/definitions/295.html) (improper certificate validation) | catalog entry 15 |
| [MCP security best practices](https://modelcontextprotocol.io/specification/draft/basic/security_best_practices) | catalog entry 18 |
| GitHub: [validating webhook deliveries](https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries), [Actions secure use](https://docs.github.com/en/actions/reference/security/secure-use), [npm 12 changelog](https://github.blog/changelog/2026-07-08-npm-install-time-security-and-gat-bypass2fa-deprecation/) | catalog entries 15, 23, 7 |
| Anthropic: [NIST submission](https://www-cdn.anthropic.com/43ec7e770925deabc3f0bc1dbf0133769fd03812.pdf), [Zero Trust guide](https://claude.com/resources/guides/zero-trust-for-ai-agents/security-considerations-for-autonomous-systems) | catalog entry 4 |
| Claude Code docs: [hooks](https://code.claude.com/docs/en/hooks), [memory](https://code.claude.com/docs/en/memory), [skills](https://code.claude.com/docs/en/skills) | catalog entry 22; [using-with-ai-agents](docs/using-with-ai-agents.md) |
| `ss(8)` manual page | catalog entry 26 |
| [OWASP Top 10 for LLM Applications 2025](https://genai.owasp.org/llm-top-10/), [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/), [MITRE ATLAS](https://atlas.mitre.org/) ([data](https://github.com/mitre-atlas/atlas-data)) | [framework mapping](docs/framework-mapping.md) |

**Methods**

| Source | Used in |
|---|---|
| Gary Klein, ["Performing a Project Premortem"](https://hbr.org/2007/09/performing-a-project-premortem), Harvard Business Review, 2007 | Track A pre-mortem |
| John Dewey, [*How We Think*](https://www.gutenberg.org/ebooks/37423), 1910 | rival explanations in [workflow](docs/workflow.md) and [why-reviews-fail](docs/why-reviews-fail.md) item 10 |
| Mutation testing, established practice since DeMillo, Lipton and Sayward, ["Hints on Test Data Selection"](https://doi.org/10.1109/C-M.1978.218136), IEEE Computer, 1978 | redteam rule 5 (a test that has never failed); [why-reviews-fail](docs/why-reviews-fail.md) item 4; the validator's weakened-copy test ([evals/README](evals/README.md)) |

**Conventions**

| Convention | Used in |
|---|---|
| [AGENTS.md](https://agents.md/) | [AGENTS.md](AGENTS.md) |
| [llms.txt](https://llmstxt.org/) | [llms.txt](llms.txt) |
| Anthropic Agent Skills format ([Claude Code skills](https://code.claude.com/docs/en/skills), [agentskills.io](https://agentskills.io/)) | `skills/*/SKILL.md`, `.claude-plugin/` |

Measured claims (entries marked *measured* in the catalog) come from one operator's machines; the methods are in
[rivendale/hsi-operator](https://github.com/rivendale/hsi-operator) and [rivendale/opensource](https://github.com/rivendale/opensource/tree/main/tools/web).

## License

MIT
