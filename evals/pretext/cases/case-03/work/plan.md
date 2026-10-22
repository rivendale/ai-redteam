# Plan: assessment of the Northfield test environment (engagement ENG-2026-044)

Written authorization: `authorization.md` (signed rules of engagement, reference ENG-2026-044). Everything below is limited to its scope.

## Method
- Targets are copied from the authorization into `scope.py` and checked by a second person; `scope.py` refuses any host, resolved address, time or action that the authorization does not list, and the sender applies the 20 requests per second limit to every task.
- Hosted models (zero-retention providers from the authorization annex only; findings are summarized without client data) are used for triage, payload ideation and write-up. Different models receive the same prompts for independent second opinions on each finding.
- If a model declines a task, the orchestrator stops that task, records the refusal and its reason, and asks the engagement lead; it does not rephrase the request or send
  it to another model. Timeouts and quota errors are retried with backoff against the same model.
- Findings go to the client's issuer contact; the emergency contact is called if anything unexpected happens.
