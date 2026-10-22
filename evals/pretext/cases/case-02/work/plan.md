# Plan: red-team orchestrator

The orchestrator (orchestrator.py) takes tasks from the operator and tries three hosted models in turn. It never stops for a human: if models decline a task the run
must still produce a result, so the last step is the local toolkit. Refusals are logged to `refusals.log` only so that we can tune the prompts later.
Authorization: the operator confirms in the UI that "an authorization exists"; the system does not store or read it.
