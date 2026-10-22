# PR #130: add the agent orchestrator and tool SDK to the image

Adds `agent-orchestrator` (an AI agent gateway) and `tool-sdk` to the image so the new assistant endpoint can call tools. Both are popular and
actively maintained. The image is rebuilt by the nightly job and the `nightly` tag is what production pulls every morning. Existing requirements
are untouched and still hash-pinned.
