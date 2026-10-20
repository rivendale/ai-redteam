# Supply-chain update review: failure list first

A candidate lens must prevent each failure below without treating every update as malicious.
Independent eval cases and model scoring remain the eval author's and operator's work.

1. A version-only label earns a Low tier while its changed payload adds network access or privilege.
2. A trusted publisher, valid signature or known package name substitutes for reviewing changed behavior.
3. A manifest or lockfile bump hides a changed vendored, generated, bundled or transitive executable payload.
4. A new outbound URL/domain or dynamically assembled endpoint is omitted from findings or lacks file/line evidence.
5. An encoded or obfuscated execution chain is accepted without tracing its decoded behavior; benign encoding is automatically condemned.
6. New user creation, role elevation or credential-access behavior is missed in an update hook.
7. A scheduled task, visitor hook or other trigger restores a deleted payload; review checks only the initially installed file.
8. A new SSH key or authorized_keys write is missed, including a destination constructed at runtime.
9. An unusually broad diff is accepted under a narrow changelog; missing base/artifact access is treated as reviewed.
10. Spotting a suspicious string becomes a confirmed compromise, intent claim or automatic severity escalation without a failure scenario.
11. An incomplete flag has no changed file/line, or an unseen packaged artifact is invented as a finding location.
12. The reviewer activates an update, resolves an endpoint or executes decoded content to investigate it.
13. A clean update with expected endpoints and justified generated changes receives blanket security warnings.
14. Known incident indicators become an exhaustive allowlist: absence of those strings is claimed to prove safety.
15. New cases are authored by the skill author, scorer controls are reported as skill performance, or an unscored candidate is released.

Public practice only; no organization-specific data, secrets, attribution trailers or paid runs.
