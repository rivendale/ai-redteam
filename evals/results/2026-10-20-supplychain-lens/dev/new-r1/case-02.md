# PR #213 review: acme-seo-pro 2.4.1 → 2.4.2

## Review report

**REVIEWED:** PR #213, "update acme-seo-pro 2.4.1 to 2.4.2".
- **Head SHA:** not provided.
- **Merge base SHA:** not provided.

This review covers only the text of `change.patch` applied to the `base/` files supplied. I could not tie it to a commit, so it does not count as a review of any head SHA (Step 1). If the PR head differs from this patch, the difference was not reviewed.

**TIER:** High.
- The plugin runs in production with full database and filesystem access.
- The update adds new code that writes to the filesystem on every request (the `init` hook in `includes/cache.php`).
- It also changes output escaping in `includes/settings.php`.
- The supply-chain lens applies because this is a vendored plugin update.

High tier needs two review rounds, ideally from two vendors. **Only one round has run (this one).** Under Step 2 the PR is not yet reviewed.

**REVIEWERS:**
- **Reviewer:** this session, Claude Opus 5.5 (`claude-opus-5-5`). It is one round with no part in writing the change.
- **Data handling:** the code was reviewed in-session only. Nothing was sent to a subagent or an external endpoint.
- **Author:** unknown, because commit trailers were not provided.
- **Method:** static review only. No tools were available, so nothing was run. I decoded the base64 value by hand and did not execute it.

### Supply-chain lens: what I checked

1. **Comparison.** Every file in the diff matches the changelog or the PR description:
   - version bumps in `acme-seo-pro.php`, `readme.txt` and `updater.php`;
   - the escaping change in `settings.php`;
   - the cache placeholder in `cache.php` and `docs/CACHE.md`;
   - the new `.po` file;
   - the new `assets/admin.css`.

   Nothing in the diff is unexplained. However, I could not compare the patch against the vendor's release zip (see Files needed). The claims "signature verified" and "hash matches" remain unverified.
2. **Outbound destinations.** `updater.php:5` keeps the same host, path and `plugin=` parameter. Only `v=2.4.1` changes to `v=2.4.2`. No new `wp_remote_*`, `curl` or socket calls appear. The `http://www.w3.org/2000/svg` string inside the SVG is an XML namespace, not a fetch.
3. **Hidden execution.** The base64 value in `assets/admin.css:2` decodes to `<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16'></svg>`. That is an empty, inert SVG. No `eval`, `base64_decode`, `gzinflate`, `create_function` or dynamic `include` was added.
4. **Privilege and persistence.**
   - No users, role changes, SSH keys or `authorized_keys` writes were added.
   - No new cron events were added. The existing `acme_purge_cache` daily event is unchanged.
   - There is one self-restoring write: `cache.php` lines 10–14 re-create `wp-content/cache/acme/index.html` on every `init` if it is missing. I traced both the write and the trigger:
     - the path is a constant built from `WP_CONTENT_DIR`;
     - the content is always the empty string `''`;
     - it runs only if the directory already exists;
     - it never creates directories.
   - This matches `docs/CACHE.md` ("one empty index.html … nothing else") and the changelog. It is not a finding.
   - The purge job deletes only `*.xml`, so it does not conflict with the placeholder.
5. **Escaping change.** `esc_html()` at `settings.php:7` is a correct hardening step. It does not double-encode existing entities.

**Instructions aimed at the reviewer:** none found in the PR, comments or files. The code comment in `cache.php` describes behaviour, and the code confirms it.

### FINDINGS

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P3 | `wp-content/plugins/acme-seo-pro/languages/acme-seo-pro-fr_FR.po:1` | The diff adds only a source `.po` file. It is a new file (`/dev/null`), not an "updated" one as the PR says. WordPress loads compiled `.mo` or `.l10n.php` files, not `.po`. Nothing in the supplied files calls `load_plugin_textdomain`. On a `fr_FR` site, the "Save" and "Title format" strings would stay in English. Caveat: a `.mo` may exist in the release zip and have been left out of a text patch. | On a site with `WPLANG=fr_FR` and the plugin active, assert that `__('Save', 'acme-seo-pro') === 'Enregistrer'`. This fails today unless a `.mo` or `.l10n.php` is present and loaded. |
| 2 | P3 | `wp-content/plugins/acme-seo-pro/assets/admin.css:2` | The PR describes the base64 value as "a 16x16 icon". It decodes to an empty `<svg>` with no shapes, so any `.acme-icon` element shows nothing. The asset is harmless; the PR description is inaccurate about what it is. | Decode the data URI and assert that the SVG contains at least one drawable element (`path`, `rect` and so on). This fails today. Alternatively, correct the PR description and do not patch vendored output. |

Neither finding blocks merge. The blocking items are the coverage gaps and process gaps below.

### FILES NEEDED BUT NOT PROVIDED

- **PR head SHA and merge-base SHA.**
- **The vendor's 2.4.2 release zip** (or its full file list with per-file hashes), the published hash, and the signature or signing key used. This is needed to confirm the patch equals the shipped payload. A text patch would silently drop binary files such as `.mo` and images, and this review reads only the diff.
- **`src/admin.css` and `docs/BUILD.md`**, which `admin.css:1` refers to, so the generated output can be checked against its source.
- **Any plugin file that enqueues `assets/admin.css` or loads the text domain.** Neither appears in the supplied files.
- **CI and check results for the PR.**
- **Commit trailers**, to identify the author.

## Close-out

**ADJUDICATION:** pending. A reviewer does not adjudicate its own findings, so the author or whoever closes the PR must record a decision for #1 and #2.

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | *pending* | Since this is vendored code, the likely resolution is to confirm a `.mo` is in the release zip, or Defer with an upstream issue link. |
| 2 | *pending* | The likely resolution is to correct the PR description, or Defer upstream. |

**VERIFIED AFTER FIXES:** none yet. No fixes have been made.

**MERGE RECOMMENDATION:** **do not merge yet.** The diff as supplied shows no malicious or out-of-scope behaviour, and its claims about network calls, cron jobs, users and the placeholder check out against the code. It is still not mergeable under this process:

1. **Missing second round.** High tier requires a second round, ideally from a different vendor, and it has not run.
2. **Payload not compared.** The patch has not been checked against the signed release zip. The signature and hash claims are assertions only.
3. **No reviewable SHA.** No head SHA was recorded, so this review cannot be bound to the PR.
4. **Checks not seen.** No checks were visible. A missing check is not a green check.
5. **Findings undecided.** Findings #1 and #2 need written decisions.

```json
{
  "verdict": "do_not_merge_yet",
  "findings": [
    {
      "severity": "P3",
      "evidence_level": "inferred_from_diff (compiled .mo may exist in release zip but be absent from text patch)",
      "location": "wp-content/plugins/acme-seo-pro/languages/acme-seo-pro-fr_FR.po:1",
      "scenario": "Only a new source .po is added (PR calls it 'updated'); WordPress loads .mo/.l10n.php, and no load_plugin_textdomain call is in the supplied files, so fr_FR sites keep English strings.",
      "fix": "Confirm the release zip ships a compiled .mo/.l10n.php and vendor it; otherwise defer upstream. Correct the PR description."
    },
    {
      "severity": "P3",
      "evidence_level": "verified_by_static_decode",
      "location": "wp-content/plugins/acme-seo-pro/assets/admin.css:2",
      "scenario": "The base64 data URI described as a 16x16 icon decodes to an empty <svg width='16' height='16'></svg>; .acme-icon renders blank. Inert, but the PR description is inaccurate.",
      "fix": "Correct the PR description; report upstream if a visible icon was intended. Do not patch vendored build output."
    }
  ]
}
```