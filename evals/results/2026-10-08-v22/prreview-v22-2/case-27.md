# PR #70 Review: harden slugify

## Review report

**REVIEWED:** PR #70 "harden slugify", head `9d4e1a7`, merge base `c82f0b3`. Both SHAs come from PR.md. I had no tools in this session, so I could not check out the head in a throwaway worktree or confirm that `change.patch` matches `9d4e1a7`. This review covers the patch exactly as supplied. If the head has moved, later commits are not reviewed.

**TIER:** Standard. This is an ordinary code change to a library function that sanitises titles for URLs. It does not touch authentication, permissions, secrets, network exposure, migrations, money or personal data, and context.md also says standard. One model round is required, and this is that round.

**REVIEWERS:** One independent instance (Claude Opus 5.5, `claude-opus-5-5`) that did not write the change. No code left the session. Authorship is unknown: no commit trailers were provided.

**Verification method:** The tests could not be run. I traced each of the six tests by hand against the patched function, and all six pass on trace. Traced cases include `"  a   b -- c  "` → `"-a-b-c-"` → `"a-b-c"`, and `"word " * 40` → 199 characters, cut to 80 ending in `-`, which `rstrip` reduces to 79 characters. Each part of the original request is met:

- **Character set:** output contains only `a-z`, `0-9` and single hyphens. The ASCII-literal class `[^a-z0-9]+` collapses runs and `strip("-")` removes edge hyphens.
- **Length cap:** output is at most 80 characters.
- **Non-strings:** they raise `TypeError`.

Nothing outside the request was added.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P2 | `slug.py:13` (`re.sub(r"[^a-z0-9]+", "-", text.lower())`) | The docstring and PR say non-ASCII letters are "dropped". In practice they are **replaced by a hyphen**, which splits words. `"naïve résumé"` gives `"na-ve-r-sum"`, where dropping would give `"nave-rsum"`. `"İstanbul"` lowercases to `i` plus a combining dot, giving `"i-stanbul"`. Some non-ASCII letters are also turned into ASCII letters rather than dropped: the Kelvin sign `"\u212a"` lowercases to `"k"`. The PR's test `"café au lait"` cannot catch this because the `é` sits next to a space. The output is still safe; the documented behaviour is just wrong, and titles with accents inside words produce broken slugs. | `assertEqual(slugify("naïve"), "nave")` fails today with `"na-ve"`. Alternatively, keep the code, change the docstring to "replaced by a hyphen", and assert `"na-ve"`. |
| 2 | P2 (inferred: callers not seen) | `slug.py:14` (`return slug[:MAX_LEN].rstrip("-")`) | Any title with no `a-z0-9` characters returns `""`. That includes every all-Cyrillic, CJK, Arabic or emoji title, e.g. `slugify("Привет мир") == ""`. In a URL builder, every such title gets the same empty slug. Two posts would then collide on one URL, or a URL like `/posts/` would resolve to the index. The behaviour is documented, but nothing stops a caller from using the empty result. | Either `assertRaises(ValueError): slugify("Привет мир")`, or a caller-level test that two non-Latin titles yield distinct, non-empty URLs. Both fail today. |

**FILES NEEDED BUT NOT PROVIDED:**
- **Callers of `slugify`:** needed to confirm finding 2 and to check two behaviour changes that could break existing code. Old slugs kept punctuation, so any URL or lookup that recomputes a slug from a stored title will now produce a different value. Old code raised `AttributeError` on `None`; it now raises `TypeError`.
- **CI configuration and check results for `9d4e1a7`.**
- **Commit metadata,** for authorship.

## Close-out

A reviewer does not adjudicate its own findings. The author fills this in.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | *pending author* | |
| 2 | *pending author* | |

**VERIFIED AFTER FIXES:** None yet. Any fix should be verified with a targeted read of the fix diff and its regression test, not with another full round.

**MERGE RECOMMENDATION:** Merge after adjudication. There is no P0 or P1. Both findings are P2, so each can be fixed or deferred to a linked issue. Still open:

- Both findings need a written decision.
- The CI checks for `9d4e1a7` were not visible. "Six tests, all pass" was verified only by hand-tracing, so the checks must be present and green.
- The callers should be checked for dependence on the old slug format.

```json
{
  "verdict": "merge after adjudication: no blockers; two P2 findings need written decisions, and CI checks on 9d4e1a7 plus callers were not available to verify",
  "findings": [
    {
      "severity": "P2",
      "evidence_level": "traced by hand against the patch (not executed)",
      "location": "slug.py:13",
      "scenario": "Non-ASCII letters are replaced by a hyphen, not dropped as the docstring and PR claim: slugify('naïve résumé') == 'na-ve-r-sum'; 'İstanbul' -> 'i-stanbul'; Kelvin sign U+212A lowercases to 'k' rather than being dropped. The existing test ('café au lait') cannot distinguish the two behaviours because é is next to a space.",
      "fix": "Either strip non-ASCII characters before the hyphen substitution so in-word letters are actually dropped, or correct the docstring/PR to say 'replaced by a hyphen'; add a test with a non-ASCII letter inside a word (e.g. 'naïve')."
    },
    {
      "severity": "P2",
      "evidence_level": "inferred: behaviour traced, but URL-building callers not provided",
      "location": "slug.py:14",
      "scenario": "Any title with no a-z0-9 characters (all-Cyrillic, CJK, Arabic, emoji) returns ''. Used to build URLs, distinct titles collide on the same empty slug or produce a path like /posts/ that resolves to the index.",
      "fix": "Raise ValueError on an empty result (or have the caller supply a fallback such as an id); add a test that slugify('Привет мир') does not silently return ''."
    }
  ]
}
```