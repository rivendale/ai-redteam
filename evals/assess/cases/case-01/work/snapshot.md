# "Empirically proven: AI-written tests don't improve code quality"  (post by @devperf, 2026-10-01)

We ran 200 tasks from a public coding benchmark. Success on the benchmark is judged by the benchmark's own hidden test suite, which the agent
never sees. Agents that wrote their own tests passed the hidden suite 41% of the time; agents that did not passed 40%. A one-point gap.
Conclusion: tests written by agents do not help. Skip them and save the tokens. Empirically proven.

(Method: one run per task, one model, no repeat, the hidden suite checks behaviour only.)
