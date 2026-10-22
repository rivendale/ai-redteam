# PR #131: add the agent orchestrator and tool SDK to the image

Adds `agent-orchestrator` 0.9.4 (published 26 days ago) and `tool-sdk` 2.3.1 (published 40 days ago) with their one new transitive package (`async-core` 2.2.0, published 33 days ago),
all through `pip-compile --generate-hashes` into requirements.txt; the Dockerfile keeps `--require-hashes`, so nothing outside the lock can be installed.
I compared both wheels' file lists with their source tags (identical; no `.pth` files and no console scripts) in artifact/.
The image is still rebuilt nightly, but it now resolves only the locked versions.
