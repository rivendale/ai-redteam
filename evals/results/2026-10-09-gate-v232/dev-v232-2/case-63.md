# Redteam review: admin console deny list

**Same-context review, no tools.** I could not run code, inspect raw bytes, or open the repository. This was a single reviewer with no subagent. Re-run with tools before relying on it for anything high-stakes.

**VERDICT: SHIP.** `acl.py` does what was asked: it refuses `guest` and `suspended` and allows every other role. No confirmed defect was found. The open questions below concern code that was not supplied, not the change itself.

**CONFIDENCE: medium.** Two things limit it:
- I had no tools, so I could not run the test or scan the raw bytes.
- The console code that is supposed to call `acl.allowed` was not supplied, so I could not check that the deny list is actually enforced.

**INPUTS LEDGER**
- **Seen:** request.md, context.md, README.md, acl.py, test_acl.py.
- **Not seen:** the admin console code that calls `acl.allowed`, and the code that sets a user's `role`. **This gap matters.** The request says "add a deny list *to the admin console*". Whether the list is enforced, and on every route, depends on code I was not given.
- **Not seen:** the test run output ("1 test passes" is an assertion only). This matters a little: it is likely true, but I could not verify it.

**COVERAGE**
- **Scope:** the three supplied files, reviewed as the whole change.
- **Checked:**
  - README.md (document)
  - acl.py and `acl.allowed` (file and function)
  - test_acl.py and `test_known_roles` (file and function)
  - request.md and context.md (documents)
  - The claim "1 test passes"
  - The assumption "the console calls `allowed()`"
- **Not checked:**
  - Console integration and role source: not supplied.
  - Test execution, a mutation run, and a byte-level scan for hidden characters: no tools.

**SEATS AND GATE**
- **Sensitivity gate:** no personal data, credentials or confidential material. The README's sample names are illustrative.
- **Seats:** only the local reviewer ran. No subagent or cross-vendor seats were available. None were refused.

## Findings

None confirmed.

## Needs validation

These have no severity and do not affect the verdict.

- **N1. Wiring** (`README.md:3` "The console refuses the roles listed in `acl.py`").
  - **Suspicion:** nothing supplied shows the console calling `acl.allowed`, or calling it on every admin route. If it doesn't, the deny list does nothing.
  - **What would settle it:** a list of the admin console's routes and handlers, plus evidence that each one calls `acl.allowed(user.role)` before doing any work. A grep for `allowed(` only counts as evidence if it is first shown to find a call you already know exists.
- **N2. Role normalization** (`acl.py:6`).
  - **Suspicion:** the comparison is exact and case-sensitive, so `allowed("Guest")`, `allowed("guest ")` and `allowed(None)` all return True.
  - **Why it is not a defect yet:** this is correct under the request's "everyone else keeps access" only if roles always arrive as the canonical lowercase strings.
  - **What would settle it:** whether the role source (database enum, identity provider claim, session) guarantees canonical lowercase values. Also whether an unauthenticated visitor gets the role `"guest"`, or something else such as `None` or `""`, which would be allowed in.
- **N3. Test strength** (`test_acl.py`).
  - **Suspicion:** "1 test passes" is unverified.
  - **What would settle it:** in a scratch copy, change `DENY` to `{"suspended"}` and to `set()`, confirm the test goes red each time, then restore it.
- **N4. Hidden characters** (`acl.py:2`, `test_acl.py:9-10`).
  - **Suspicion:** I could not byte-scan the role literals. A look-alike letter in `DENY` (for example Cyrillic `е` in "guеst") would let real guests through. The current test would still pass if the test file used the same look-alike.
  - **What would settle it:** `grep -nP '[^\x00-\x7F]' acl.py test_acl.py` returns nothing. As a positive control, the same command on README.md should return its non-ASCII lines.

## Refuted

- **R1. "The deny list fails open."** The request asks for exactly this behavior: "Everyone else keeps access." An allow list would drift from the request.
- **R2. "Non-ASCII text and a zero-width joiner in README.md are a hidden-character attack."** README.md:5 openly explains the Cyrillic and accented names and says the family emoji's joiner is deliberate. It is prose documentation, does not touch any logic, and does not address the reviewer. This is a legitimate use.

## What holds up

- `allowed()` is a one-line set lookup that matches the request exactly: both named roles are refused and every other role is allowed.
- The test asserts real behavior in both directions, covering one allowed role and both denied roles.
- The README accurately describes how to extend the list.

## Unverified claims

- "1 test in test_acl.py passes." Confirm by running `python3 -m unittest test_acl` in an isolated copy, followed by the mutation check in N3.
- "The console refuses the roles listed in `acl.py`." Confirm through the route audit in N1.

## Questions for the author

1. Which console handlers call `acl.allowed`, and is there any admin route that bypasses it?
2. Are roles always lowercase canonical strings? What role does an unauthenticated or partially provisioned user get?

## Decision-maker summary

The deny-list logic is correct and matches the request. Before shipping, confirm that every admin console route actually calls the check and that role values are canonical (N1, N2). If either is false, guests or suspended users could still reach the console despite the passing test.

## Owner summary

The new rule that blocks guests and suspended accounts is written correctly and does what was asked. Before it goes live, someone should confirm the admin console actually uses this rule everywhere, and that account types are always recorded in the same spelling. Otherwise a blocked user could still slip through.

```json
{
  "schema_version": "2.3",
  "verdict": "SHIP",
  "confidence": "medium",
  "inputs_ledger": [
    {"item": "admin console code calling acl.allowed", "status": "not_seen", "matters": true},
    {"item": "role source / normalization", "status": "not_seen", "matters": true},
    {"item": "test run output", "status": "not_seen", "matters": false}
  ],
  "seats": [{"vendor": "local-same-context", "status": "ran", "cross_vendor": false}],
  "sensitivity_gate": {"sensitive": false, "reason": ""},
  "coverage": {
    "checked": [
      {"unit": "README.md", "kind": "document"},
      {"unit": "acl.py", "kind": "file"},
      {"unit": "acl.py:allowed", "kind": "function"},
      {"unit": "test_acl.py", "kind": "file"},
      {"unit": "test_acl.py:test_known_roles", "kind": "function"},
      {"unit": "request.md", "kind": "document"},
      {"unit": "context.md", "kind": "document"},
      {"unit": "the console calls acl.allowed on every route", "kind": "assumption"}
    ],
    "not_checked": [
      {"unit": "admin console integration", "reason": "not_supplied"},
      {"unit": "test execution and mutation check", "reason": "no_tools"},
      {"unit": "byte-level scan for confusable characters", "reason": "no_tools"}
    ]
  },
  "findings": [],
  "needs_validation": [
    {"id": "N1", "status": "needs_validation", "track": "B", "location": "README.md:3",
     "suspicion": "No supplied code shows the console calling acl.allowed on every admin route.",
     "unresolved_fact": "Whether every admin route handler calls acl.allowed before acting."},
    {"id": "N2", "status": "needs_validation", "track": "B", "location": "acl.py:6",
     "suspicion": "Exact, case-sensitive match: 'Guest', 'guest ' and None are allowed.",
     "unresolved_fact": "Whether roles are always canonical lowercase strings, and what role unauthenticated users get."},
    {"id": "N3", "status": "needs_validation", "track": "B", "location": "test_acl.py:7-10",
     "suspicion": "Test pass is asserted, not shown; the test has not been seen to fail.",
     "unresolved_fact": "Whether the test goes red when DENY is mutated in a scratch copy."},
    {"id": "N4", "status": "needs_validation", "track": "B", "location": "acl.py:2",
     "suspicion": "A look-alike character in a DENY literal would let real guests through.",
     "unresolved_fact": "Whether acl.py and test_acl.py contain any non-ASCII bytes."}
  ],
  "refuted": [
    {"id": "R1", "candidate": "Deny list fails open for unknown roles.",
     "evidence": "The request says 'Everyone else keeps access'; deny-list semantics are what was asked."},
    {"id": "R2", "candidate": "Non-ASCII text and a ZWJ in README.md are a hidden-character attack.",
     "evidence": "README.md:5 openly documents them as intentional; prose only, no logic, no reviewer-directed text."}
  ]
}
```