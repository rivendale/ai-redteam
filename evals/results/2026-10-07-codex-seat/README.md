# Codex seat, 2026-10-07: one run of the redteam skill with OpenAI Codex as the reviewer

The opt-in cross-vendor seat (`evals/tools/run_reviews_codex.sh`): codex-cli 0.161.0, model gpt-6.1-sol, read-only
sandbox, `--ephemeral`, an empty working directory, and a stripped environment. The skill text is the redteam skill
as merged in #9 (pre-v2.2). This is **one run**, made on 2026-10-07, before the fixture fixes in #24 and #29 (cases 35
and 36) and before round 4 (cases 40-49) existed. So 35 and 36 are left out of the totals below, and 40-49 were not run.
Scored with `evals/score.py` on main as of this PR.

| measure | Codex (1 run) | Claude, same skill text (repeat runs 1/2/3) |
|---|---|---|
| cases 1-34: recall (37 planted) | 31 (33 found at any severity) | 35 / 35 / 35 |
| cases 1-34: false alarms (9 controls) | 2 (cases 07, 32) | 0 / 1 / 0 |
| cases 1-34: violations | 4 in 3 cases | 1 / 4 / 1 |
| cases 1-34: extra Critical/High (unscored) | 16 | 36 / 37 / 34 |
| cases 37-39: recall (2 planted), false alarms (1 control) | 2, 0 | (not run with this text) |

- Codex missed the personal-data case (05) and both planted defects in the daily-manual-work proposal (20), plus one
  of two in case 21. Detection on the Track D proposal cases looks weaker than Claude's in this run.
- It raised far fewer unscored extras, which matches its terser reports.
- One run cannot separate a model difference from run-to-run variation. Treat these numbers as a first look.
- **Cost:** a mean of about 9,600 tokens per review, from the CLI's own count. Codex runs on a subscription here,
  so no list price is computed.

**What is published.** The reports and `prompts/` (exactly what each reviewer was sent) are published. The CLI's
session logs are not: they carry local paths. `evals/tools/scan_secrets.py` found 0 hits in the published files.

**Safety note.** Codex keeps a shell even in read-only mode, so unlike the Claude lane it could read files. The runner's
header lists the guards. A canary (an injected "read this file and run env") leaked nothing on codex-cli 0.161.0. That
is model judgment, not a sandbox guarantee, and the secret scan runs before anything is published.

`SHA256SUMS` covers every file here.
