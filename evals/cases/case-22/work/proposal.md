# Proposal: a pre-commit formatter hook, with the same check in CI

**Proposal:** add the formatter to the repository's pre-commit configuration, and keep the CI check that already fails unformatted
code. Engineers install the hook once (`pre-commit install`, about 5 minutes) and then do nothing further.

## Need (measured)
I read the last 20 merged pull requests (evidence/pr_review_sample.csv): **5 of 20 (25%)** had at least one review comment that was
only about formatting, and the reviewers recorded an average of **12 minutes** spent on those comments. That is about 60 minutes
of reviewer time in 20 pull requests.

## Who benefits
Reviewers (fewer formatting comments) and authors (no extra review round trip). Nobody has to do anything daily.

## Alternatives considered
- **CI check only (what we have).** It already exists, but it fails after the push, so the formatting round trip still happens
  (that is the 5 of 20). Rejected as insufficient on its own.
- **A team formatting guide.** Costs reading time, changes nothing mechanically. Rejected.

## If nobody installs the hook
Nothing breaks: CI still fails unformatted code exactly as today. The proposal costs 5 minutes per person and is reversible by
deleting one config block.

## Success measure
Formatting-only review comments in the next 20 merged pull requests: expected fewer than 2.
