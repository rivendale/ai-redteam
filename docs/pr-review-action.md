# Opt-in bounded PR review Action

This workflow generates one diff-only `pr-review` round for an exact PR head. It never approves, comments,
adjudicates, pushes or merges. Missing surrounding code and the independently supplied original request are
reported as limits. High-risk changes still need their separate independent review rounds.

## Enable after independent review

A maintainer reviews and merges the workflow, then sets repository variable `AI_REDTEAM_ENABLED` to `true`,
`AI_REDTEAM_MODEL` to an explicit approved model ID, and secret `AI_REDTEAM_MODEL_KEY` to the provider key.
The implementation uses the [Anthropic Messages API](https://platform.claude.com/docs/en/api/messages/create).
Use only an endpoint/account approved for the repository's data. No secret or variable was configured by this PR.
Leaving the enable variable unset skips the job.

The workflow uses `pull_request_target` to obtain trusted base workflow code. This trigger can expose secrets
when combined with untrusted checkout, so it must never check out or execute the PR head. The job has both an
opt-in and same-repository/non-fork gate. It checks out only the server-supplied base SHA with persisted Git
credentials disabled. Python rechecks eligibility before reading either token, fetches PR data through read-only
GitHub API requests, and verifies the head/base again before publishing. Fork PRs do not start the secret-bearing
job. Dependabot actors and PR authors also skip before either token is read, including a human-triggered event on a Dependabot PR. See [GitHub's secure-use guidance](https://docs.github.com/en/actions/reference/security/secure-use).

Only the model request step receives the secret. It goes in a request header to a fixed provider host, never in
argv, prompts, output files or logs. The model receives the skill and PR data as text; it has no tools or shell.
No dependencies, PR scripts or tests are installed/run in the secret-bearing job. PR titles and descriptions are
read from the event/API, never interpolated into shell code. The response is escaped in the Actions summary to
prevent active Markdown/HTML rendering. Obvious credential reflection is discarded.

Repository writers can change workflows and generally have access to repository secrets. This boundary protects
against untrusted PR content/forks; it does not claim to protect secrets from malicious maintainers or a provider.
Use an environment with required reviewers if the repository needs an additional human gate.

## Limits and cost

Each run makes at most one model request, without retries or recursive tool calls, with a bounded diff and output.
Oversized/missing diffs, unavailable merge bases, moved identities, errors and incomplete model responses refuse a
review. The job has a time limit. A new push can start a new run; configure a provider-side spending limit before
enabling. There is no price estimate or claim of a monthly dollar ceiling here. No model call ran during build
validation. The generated text is one untrusted review input, not a completed PR close-out.

## Denying-direction validation

Run `python3 tests/test_pr_review_action.py`. The fork tests use a secret-access tripwire and a transport spy:
a fork must reach neither a key read nor a network request. The same-repo name with a fork flag also refuses. The exact two-step sequence and sole run command are allowlisted, so an added command, step or dependency-install prefix fails the fixture.
The test evaluates the actual workflow gate for fork and ordinary inputs, checks read-only permissions and
trusted-base checkout, and verifies an eligible run with a mock provider. Tests make no real network/model call.

A real GitHub-hosted smoke run and provider billing behavior remain maintainer acceptance after review. Do not
supply a key to a fork to test the denial. Observe the job being skipped from the fork run and compare that with
the local tripwire result. The action pin is a full commit from the official actions/checkout repository.
