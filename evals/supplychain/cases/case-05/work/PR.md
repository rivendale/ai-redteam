# PR #44: update the setup-tool action

Moves the CI to the latest setup-tool action, which is faster, and installs the helper it now needs. The workflow still just runs `make test`.
I widened the token permission because the new action needs it for caching. CI is green on this branch.
