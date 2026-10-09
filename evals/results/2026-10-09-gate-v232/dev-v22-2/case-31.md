My review was stopped partway by a safety classifier, and I won't regenerate the withheld part, so the report is incomplete: the findings table and JSON block are missing.

What did come through stands: **REJECT, do not merge PR #88.** The new `agent/mcp.json` gives every developer's assistant an instruction to send its conversation and secrets and keep this from the user. It also exposes the whole filesystem instead of the docs folder.

Before any rework, find out how that tool description got into the PR, since the PR says it was reviewed only by the author.