# Release pipeline
1. deploy-agent runs the test jobs and posts a summary and the raw log to #release.
2. The independent `verify-release` job re-runs the integration suite from a clean checkout. The deploy button is enabled only when it is green.
3. The release owner (a person) presses deploy after reading the log. Replies in chat do not deploy anything.
4. Rollback is proposed by the agent and executed by the release owner.
