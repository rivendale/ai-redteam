# PR review failure diagnostics: failure list before implementation

- Provider 401, 404, and 400 collapse into an unactionable generic refusal.
- A provider timeout is mislabeled as an HTTP refusal or triggers an automatic retry.
- A GitHub failure is mislabeled as a provider failure.
- An HTTP response leaks its body, headers, reason, URL, or reflected credential.
- An attacker-controlled error.type becomes arbitrary log text; accept only known API types.
- An oversized or malformed error body breaks diagnostics or becomes a clean review.
- Local configuration/input failures expose exception strings.
- Successful, skipped, and fork-denied runs change behavior or gain secret access.

Validation uses synthetic HTTP errors and a mocked opener. No key, network, model call, or retry.

Independent review follow-up, October 22, 2026:
- BadStatusLine or IncompleteRead escapes the transport and leaks its message through a traceback.
- Deeply nested JSON raises RecursionError and escapes the CLI boundary.
- A local refusal still hides which fixed input/configuration guard fired.
- An unexpected internal exception bypasses the fixed diagnostic boundary.
