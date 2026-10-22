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
a fork must reach neither a key read nor a network request. The same-repo name with a fork flag also refuses. The sole job, full reviewed workflow bytes, exact two-step sequence and sole run command are allowlisted, so an added command, step or dependency-install prefix fails the fixture.
The test evaluates the actual workflow gate for fork and ordinary inputs, checks read-only permissions and
trusted-base checkout, and verifies an eligible run with a mock provider. Tests make no real network/model call.

A real GitHub-hosted smoke run and provider billing behavior remain maintainer acceptance after review. Do not
supply a key to a fork to test the denial. Observe the job being skipped from the fork run and compare that with
the local tripwire result. The action pin is a full commit from the official actions/checkout repository.

## Failure diagnostics

Failures exit nonzero without publishing a review. Logs distinguish `provider HTTP 404 not_found_error`,
other provider HTTP statuses, `provider timeout`, `provider network`, and GitHub HTTP/network failures.
Known local refusals use whitelisted codes such as `local diff_limit`, `local file_limit`, `local identity_moved`,
`local redirect`, `local model_incomplete`, `local credential_reflection`, and `local model_secret_missing`.
Malformed successful provider JSON uses `local provider_response_invalid`. Other input failures use
`configuration/input/response`; unexpected exceptions use `unexpected_error` without a traceback. No exception message, response body,
URL, request header, or provider error message is logged. Only a recognized provider `error.type` is accepted;
unknown, malformed, or oversized error responses use `unknown_error`. The recognized types follow the
[official API error reference](https://platform.claude.com/docs/en/api/errors), checked October 22, 2026.
A category narrows diagnosis; a 400 alone does not prove a billing or configuration cause.

Run `python3 tests/test_pr_review_errors.py` for synthetic 401/404/400, timeout, HTTP parser failures,
recursion/internal exceptions, local refusal codes, GitHub/service distinction,
malformed and oversized bodies, and credential-reflection controls. These tests make no live calls.
The one-request/no-retry policy and the secret eligibility gates remain in force.
## Known-bad version lookup

`tools/known_bad.py` reads inert base/head manifest text through the GitHub API before the model key is read.
It compares exact references, queries the public [OSV batch API](https://google.github.io/osv.dev/post-v1-querybatch/),
then fetches [advisory details](https://google.github.io/osv.dev/get-v1-vulns/) for supplied severity metadata.
Only package ecosystem/name/version or an Action commit goes to OSV, with no GitHub token, provider key,
PR body, title or code. All requests use fixed hosts; redirects refuse. No package, installer or PR code executes.

Matches use Step 5's P1/P2 finding fields: location, scenario and suggested test, plus OSV ID, supplied severity
(or `not supplied by OSV`) and a fixed OSV advisory link. MAL or High/Critical metadata maps to P1; other matches
map to P2. Raw CVSS vectors are preserved without estimating a numeric score. This reports a database match,
not a claim that the running product is exploitable. Human Step 7 adjudication remains required.
The lookup is written to the Actions summary before fetching/checking the model diff and before the provider request.
A regenerated lockfile over the model diff limit still receives the independent lookup. A PR over the
200-file enumeration cap gets an explicit partial lookup report before the model review refuses. A later model error leaves it there;
a successful model round appears below it and cannot overwrite its findings or coverage status.

Supported exact-reference readers: npm package.json and package-lock/npm-shrinkwrap versions 1-3;
PyPI pinned requirements/constraints, project/build/optional dependencies in pyproject.toml, basic Poetry
and uv package locks, and Pipfile.lock; Go require entries in go.mod and versions in go.sum; crates.io
Cargo.lock packages and exact `=x.y.z` Cargo.toml dependencies; canonical one-line workflow uses with a full
version tag or full commit SHA. Action subdirectories identify their owner/repository; SHA pins use OSV's
commit query. Ecosystem names follow the [OSV schema](https://ossf.github.io/osv-schema/#affectedpackage-field).

There is no package-manager resolver. Ranges, local/git sources, overrides, unsupported YAML syntax and lock
formats (including yarn, pnpm and bun), dynamic Python manifests and unsupported resolution features produce
coverage gaps. Empty/removed files and unchanged references do not need a new lookup. Line locations anchor
the first package/reference occurrence in the inert head file. A renamed manifest is compared using the supplied
old/new file bytes; unsupported cross-format renames produce gaps. Dependency metadata may itself be private;
enable the Action only when sending those identifiers to the public OSV service is approved.

Bounds: at most 200 changed-file metadata entries in two GitHub pages, 20 dependency files, two content reads
per file, 2 MiB per response/file, 100 distinct added/changed references, one batch request, 20 detail requests
and 200 retained matches. OSV uses a 10-second socket timeout and a 60-second budget checked between reads;
a blocked read can add up to its remaining socket timeout. GitHub reads retain the existing 90-second timeout
and the workflow job limit. No retries. Batch pagination is not followed: returned matches are preserved and
coverage is incomplete. Detail failures preserve matching IDs with missing severity and incomplete coverage.
Any limit, malformed response, unsupported resolution or network failure says **known-bad check did not run
to completion**, never clean. A completed zero is only no OSV match for the enumerated versions at that time.

Run `python3 tests/test_osv.py` and `python3 tests/test_osv_integration.py`. Recorded public responses are in
`tests/osv/`; CI makes no live OSV/model request. Tests include MAL, a clean bump, every ecosystem, unchanged
and removed versions, incomplete results, fixed destinations, budgets, credential separation, model contradiction
and a real summary file surviving a mocked provider failure. No model eval cases or scores are authored here.

Independent follow-up controls cover truncated/malformed HTTP responses from both OSV and GitHub,
a malicious bump in a diff over 150,000 bytes, and an explicit gap report before the 200-file refusal.
