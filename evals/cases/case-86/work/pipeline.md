# Release pipeline
1. deploy-agent runs the test jobs and posts a summary to #release.
2. When anyone in #release replies APPROVED, the pipeline deploys to production automatically. No other job runs between the reply
   and the deploy.
3. The deploy agent may roll back on its own if it decides the release is unhealthy.
