# Plan: orchestrator behaviour for authorized assessments

- Every task is checked against the stored written authorization before any model call (see `authorization.check`).
- Timeouts and quota errors are retried with exponential backoff against the same model with the same prompt, four attempts, then the task is parked for the operator.
- A refusal ends the task: it is logged with the model's reason and a person decides. Nothing is rephrased, re-contexted or sent to a different model.
- Findings get a second opinion from two different vendors' models with the identical prompt; the two answers are shown side by side to the operator.
- No local attack code exists in this system; the toolkit is the models' analysis plus the operator's own tools.
