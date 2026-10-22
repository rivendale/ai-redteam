# Review completion room: failure list before implementation

- A valid full review is cut off at the old 4096-token output budget.
- A higher budget exceeds the selected model's documented output limit.
- A truncated response is published as a completed review or automatically retried.
- Unknown, missing or hostile stop_reason values become arbitrary log text.
- The next incomplete response still omits its fixed stop reason.
- Raising tokens silently removes the 32000-character publication limit.
- A complete non-streaming review exceeds the old 90-second socket timeout despite the larger token budget.
- Giving the provider more time also increases GitHub request timeouts or removes the job deadline.
- Checkout still targets Node 20 or a mutable action reference.
- A workflow pin edit bypasses the exact-step security allowlist or fork/opt-out gates.

Use synthetic provider responses only; no real model call or key.
