# PR #70 Review: harden slugify

**REVIEWED:** PR #70 at head `9d4e1a7`, merge base `c82f0b3`. Both SHAs are taken from PR.md. I could not confirm them against a repository. I read `change.patch` against `base/slug.py` as text, not in a checked-out worktree. If the head has moved past `9d4e1a7`, the later commits are not covered.

**TIER:** Standard. This is an ordinary library change. Its output is restricted by a closed character class and goes into URLs. It touches no auth, secrets, data handling or dependencies. One round is required, and this is that round.

**DATA:** The code carries no personal data or secrets. I reviewed it in this session and sent it nowhere else.

**REVIEWERS:**
- Reviewer: claude-opus-5-5, a fresh instance that did not write or discuss the change.
- Author: unknown. No commit trailers were provided.

**Execution:** I did not run anything because this session has no tools. I traced each of the six tests by hand, and all six produce their asserted values. For example, `"word " * 40` slices to 80 characters ending in `-`, and `rstrip` brings it to 79. The claim "Six tests, all pass" is therefore consistent with the code but has not been executed.

**Against the request:**
- **Charset a-z, 0-9 and single hyphens:** met. `[^a-z0-9]+` collapses each run to one hyphen, and `strip` and `rstrip` remove hyphens at both ends. Non-ASCII characters whose `.lower()` turns into ASCII still pass through the a-z filter, so output is always within the class.
- **Length cap:** met (≤ 80).
- **Clear error for non-strings:** met. `TypeError` is raised for `None`, `bytes`, `int` and so on.
- **Nothing extra added.** No prompt-injection text is present in the PR.

## Findings

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `slug.py:10` (docstring) and `slug.py:14`; PR.md "Letters outside a-z are dropped" | Characters outside a-z and 0-9 are **replaced by a hyphen**, not dropped. `slugify("naïve")` returns `"na-ve"`, not `"nave"`. `slugify("don't stop")` returns `"don-t-stop"`. The documented and tested contract does not match the behaviour. `test_non_ascii_dropped` only uses `é` next to a space, where the two behaviours give the same result, so it cannot tell them apart. Callers relying on the docstring will get unexpected slugs. | `assertEqual(slugify("naïve"), <decided value>)`. Today this fails against `"nave"`. Either fix the code to delete those characters (e.g. remove `[^a-z0-9\s-]` first, then hyphenate runs of whitespace and hyphens), or fix the docstring and PR text to say "replaced by a separator". The test should pin whichever behaviour is chosen. |
| 2 | P2 | `slug.py:14`; behaviour documented at `slug.py:11` | Any title with no a-z or 0-9 characters returns `""`, for example `"日本語のタイトル"`, `"Привет"` or `"!!!"`. A caller that builds `/posts/<slug>` then gets `/posts/`. Every such title also collides on the same empty slug. The behaviour is documented, but the request is silent on it, and the callers that would have to handle `""` were not provided. | A caller-level test: create content titled `"Привет"` and assert it gets a non-empty, unique URL. Alternatively, `slugify` raises `ValueError` on an empty result. This is an owner decision; see the note below. |
| 3 | P3 | `tests/test_slug.py:17-19` | The cap test is written against the imported `MAX_LEN`. A change to `MAX_LEN = 8000` would still pass, so the "at most 80" requirement is not pinned. The test also never checks that output is non-empty and correctly truncated at a word boundary. | `assertEqual(MAX_LEN, 80)` and `assertEqual(len(slugify("a" * 200)), 80)`. |
| 4 | P3 | `tests/test_slug.py:24-26` | Only `None` is tested. `bytes` is the likeliest wrong type from web frameworks and is not covered. A future refactor such as `text = str(text)` would make `slugify(b"x")` return `"b-x"` silently, and no test would catch it. | `assertRaises(TypeError, slugify, b"title")` and `assertRaises(TypeError, slugify, 123)`. |

**Owner decision on #2:** whether an empty slug should be an error, a fallback id, or something callers handle. This needs to be settled before merge.

**FILES NEEDED BUT NOT PROVIDED:**
- **Callers of `slugify`:** needed to judge #2 and uniqueness handling.
- **Test runner and CI config:** `tests/` has no `__init__.py`, and `from slug import ...` requires the repo root on `sys.path`. Whether the tests run in CI at all depends on configuration I cannot see.
- **CI check results for `9d4e1a7`.**
- **Commit metadata and trailers.**

## Close-out

The close-out is left for the author and closer. A reviewer does not adjudicate its own findings.

**ADJUDICATION:** pending for #1–#4. #1 and #2 are P2, so they may be Deferred with a tracking issue if not fixed.

**VERIFIED AFTER FIXES:** none yet.

**MERGE RECOMMENDATION:** **merge after fixes.** There is no P0 or P1, and the core safety requirement holds. Before merge, all of the following must be in place:
- #1 is resolved, at minimum by making the docstring and PR text match the actual behaviour, with a test pinning it.
- The owner decides on the empty-slug behaviour (#2).
- Every finding has a written decision.
- CI checks for the final head are present and green. None were provided, and a missing check is not green.

```json
{
  "verdict": "merge after fixes",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "traced by hand from code; not executed",
      "location": "slug.py:10,14",
      "scenario": "Non a-z/0-9 characters are replaced by '-' rather than dropped as the docstring and PR claim: slugify('naïve') -> 'na-ve', slugify(\"don't stop\") -> 'don-t-stop'. test_non_ascii_dropped cannot distinguish the two behaviours.",
      "fix": "Either delete disallowed characters before hyphenating whitespace/hyphen runs, or correct the docstring and PR text; add a mid-word test such as slugify('naïve') pinning the chosen result."
    },
    {
      "severity": "P2",
      "evidence_level": "traced by hand; caller impact inferred, callers not provided",
      "location": "slug.py:14",
      "scenario": "Titles with no ASCII letters or digits ('Привет', '日本語', '!!!') all return '', giving URLs like /posts/ and colliding with each other.",
      "fix": "Owner decision: raise ValueError on empty result, or have callers substitute a fallback/unique id; add a test for the chosen behaviour."
    },
    {
      "severity": "P3",
      "evidence_level": "read from test code",
      "location": "tests/test_slug.py:17-19",
      "scenario": "The cap test compares against imported MAX_LEN, so changing MAX_LEN to 8000 still passes; the 80-character requirement is unpinned.",
      "fix": "assertEqual(MAX_LEN, 80) and assertEqual(len(slugify('a' * 200)), 80)."
    },
    {
      "severity": "P3",
      "evidence_level": "read from test code",
      "location": "tests/test_slug.py:24-26",
      "scenario": "Only None is tested for TypeError; a refactor to str(text) would make slugify(b'x') return 'b-x' silently.",
      "fix": "Add assertRaises(TypeError) cases for bytes and int."
    }
  ]
}
```