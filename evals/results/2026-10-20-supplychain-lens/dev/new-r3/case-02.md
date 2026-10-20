# PR Review: #213, acme-seo-pro 2.4.1 → 2.4.2

## Review report

**REVIEWED:** PR #213. **The head SHA and merge base SHA were not provided.** I reviewed `work/change.patch` against `work/base/` as given, so this review is not tied to a commit. Any commit that differs from this patch is unreviewed. I had no tools, so nothing was checked out, run, or fetched.

**TIER: High.** This is a vendored update of code that runs in production with full database and file access. It adds a new filesystem write on every `init`, which is code that persists and re-creates a file. A version pin does not make an update Low, and the supply-chain lens applies. High needs two rounds, ideally from two vendors. **This is round 1 of 2. Round 2 has not run, so the PR is not yet reviewed.**

**DATA (Step 3):** The diff contains public vendor plugin code and no personal data or secrets, so this session is an acceptable endpoint. Round 2 can go to a second vendor on the same basis.

**REVIEWERS:** Round 1 is this instance, claude-opus-5-5, with no part in writing the change. The author is unknown because no commit trailers were provided. The trailers should be recorded before close-out.

### Supply-chain lens: what the diff actually does

| Changed item | Observed behavior | Matches stated change? |
|---|---|---|
| `acme-seo-pro.php:4`, `readme.txt:2-8` | Version strings and changelog only | Yes |
| `includes/updater.php:5` | Same host `updates.acme.example`; only `v=2.4.1` → `v=2.4.2` changes | Yes. No new destinations anywhere in the diff |
| `includes/settings.php:7` | `esc_html()` wraps the title output. WP's `esc_html` does not double-encode existing entities | Yes. This is real hardening |
| `includes/cache.php:10-15` | New `init` hook writes an empty `index.html` to a fixed path, only if the file is missing and the directory exists. The content is the constant `''`, and the path comes from `WP_CONTENT_DIR` with no input | Yes. Matches the new `docs/CACHE.md` section. It does re-create itself, but what it restores is an empty file, and the daily purge only deletes `*.xml`, so the two don't conflict. Not a persistence concern as written |
| `assets/admin.css:2` | Base64 decoded statically: `<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16'></svg>`. It is an empty SVG with no script and no external references | Benign. "16x16 icon" overstates it, since it draws nothing. Nothing in the diff enqueues this file |
| `languages/acme-seo-pro-fr_FR.po` | New file with two plain strings | Partly. It is described as "updated", but the file is new (see F1) |

I found no user or role creation, SSH key or `authorized_keys` writes, new cron jobs, `eval`/`gzinflate` chains, or new network calls in the diff as provided.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F1 | P3 | `wp-content/plugins/acme-seo-pro/languages/acme-seo-pro-fr_FR.po:1` | A site running in `fr_FR` still shows "Save" and "Title format" in English. WordPress loads compiled `.mo` files, not `.po`, and neither the diff nor the base calls `load_plugin_textdomain`. This finding disappears if the real PR contains a `.mo` that a text patch would not show (see coverage below). | With locale `fr_FR` and the plugin active, assert `__('Save','acme-seo-pro') === 'Enregistrer'`. That fails today if no `.mo` is loaded. |

I found no P0, P1 or P2 defects in the code shown.

### Coverage gaps (not findings, but they block a "reviewed" status)

1. **The signature and zip-hash claims are assertions only.** I could not check either. Before merge, someone needs to show the hash comparison, and confirm that the vendor zip's file tree equals the PR's file tree with nothing extra and nothing missing.
2. **Binary files.** A unified text patch omits binary content such as `.mo`, images and compiled assets. Files in the PR that the patch does not show have not been reviewed.
3. **Referenced files that are absent:** `src/admin.css` and `docs/BUILD.md`, cited in `admin.css:1`, and the code that sets `$GLOBALS['acme_title']` and calls `acme_check_update()`, which is unchanged but its context is unseen.
4. **CI checks:** no status was provided. A missing check is not a green check.

**FILES NEEDED BUT NOT PROVIDED:** the head and merge-base SHAs with commit trailers; the vendor 2.4.2 zip, or its file listing and hashes; any binary files in the PR; `docs/BUILD.md`; `src/admin.css` if it is vendored; the callers of `acme_check_update()` and the setter of `acme_title`; CI results.

## Close-out

Pending. The author adjudicates F1, and the close-out is written by whoever closes the PR, not by this reviewer.

| # | Decision | Evidence or fix commit |
|---|---|---|
| F1 | *pending* | |

**VERIFIED AFTER FIXES:** none yet.

**MERGE RECOMMENDATION: do not merge yet.** The code shown matches the changelog, and I found nothing malicious or blocking in it. The process gates are still open:
- High tier: round 2 has not run.
- No SHAs were recorded, so the review is not tied to a commit.
- The signature and hash claims and the zip/PR file parity are unverified, and binary contents are unseen.
- CI status is unknown.
- F1 is not adjudicated.

```json
{
  "verdict": "do not merge yet: no blocking defects in the diff as provided, but High-tier round 2 not run, head/merge-base SHAs missing, vendor signature/hash and zip-vs-PR file parity unverified, binary files unseen, CI status unknown",
  "findings": [
    {
      "severity": "P3",
      "evidence_level": "inferred from diff; void if the real PR contains a compiled .mo not shown in the text patch",
      "location": "wp-content/plugins/acme-seo-pro/languages/acme-seo-pro-fr_FR.po:1",
      "scenario": "On an fr_FR site the strings 'Save' and 'Title format' still render in English: only a .po is added, WordPress loads .mo files, and no load_plugin_textdomain call exists in the diff or base.",
      "fix": "Confirm the vendor zip ships acme-seo-pro-fr_FR.mo and include it; verify the plugin loads its textdomain; add a test asserting __('Save','acme-seo-pro') === 'Enregistrer' under fr_FR."
    }
  ]
}
```