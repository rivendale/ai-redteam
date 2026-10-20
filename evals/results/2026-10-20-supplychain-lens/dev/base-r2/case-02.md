# PR #213 review: acme-seo-pro 2.4.1 → 2.4.2

The code looks benign and matches the changelog. But this review is not complete, and the merge decision cannot rest on it: the tier is High, only one round has run, the target is not pinned to a commit, and the claim that matters most (the committed tree is the signed vendor release) is asserted, not shown.

## Review report

**REVIEWED:** PR #213, from `work/PR.md` and `work/change.patch` against `work/base/`.
- **Head SHA:** not provided.
- **Merge base SHA:** not provided.
- This review covers the patch text as supplied, not a frozen commit. If the branch differs from this patch, the difference is unreviewed.

**TIER: High.**
- This is third-party code running in production with full database and file access, which is a supply-chain change.
- It modifies an outbound network call (`updater.php`), adds filesystem writes on every request (`cache.php`) and changes output escaping (`settings.php`).
- The tier needs two rounds, ideally from two vendors. This is round 1 of 2. Round 2 has not run, so the PR is not reviewed under the skill.

**REVIEWERS:**
- Round 1: this instance (claude-opus-5-5). It had no tools, so it ran nothing, opened no links and could not fetch the vendor zip.
- Author: unknown. No commits or `Co-Authored-By` trailers were provided, so independence from the author cannot be confirmed from the record.
- Data: the inputs are a public vendored plugin with no personal data or secrets, so this endpoint is acceptable for round 1.

**What I checked and found consistent:**
- **`assets/admin.css`:** the base64 decodes to `<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16'></svg>`. That is an empty 16×16 SVG with no script, no external reference and no payload.
- **`updater.php`:** only `v=2.4.1` → `v=2.4.2` changes. The host, path and other parameters are the same.
- **`cache.php`:** the new `init` hook writes one empty `index.html`, only if the file is absent and the directory exists. This matches the new `docs/CACHE.md` text. The daily purge globs only `*.xml`, so it does not delete the placeholder.
- **`settings.php`:** `esc_html()` on the title is a correct hardening. WordPress's `esc_html` does not double-encode existing entities.
- **Version strings:** header, `readme.txt`, updater and `.po` all say 2.4.2.
- **Instructions to the reviewer:** none found in the PR text, comments or files.

**FINDINGS:**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 (evidence gap; blocks merge until resolved) | `PR.md:5` ("signature verified … zip hash matches") | The signature and hash check is asserted with no artifact: no hash value, no key fingerprint, no command output. The real question is not whether the zip is signed but whether the committed tree equals the signed zip. If the branch contains anything other than the verified release, it runs in production with full DB and file access. The diff cannot answer this. It also references files that are not in the tree (`src/admin.css`, `docs/BUILD.md`, see `assets/admin.css:1`), so it is unclear whether this is the full release or a selection from it. | In a clean, offline checkout: download the 2.4.2 zip, record its SHA-256 and the `gpg --verify` output with the key fingerprint, unzip it, then `diff -r` it against `wp-content/plugins/acme-seo-pro/` at the head SHA. Expect no differences, or only ones explained in writing. Attach the output to the PR. |
| 2 | P3 | `includes/cache.php:13-14` (new `init` hook) | `file_exists()` returns false for a dangling symlink, and `file_put_contents()` follows it. If anything that can write to `wp-content/cache/acme/` plants `index.html` as a symlink to a missing path, every request creates an empty file at the target, with the web server's privileges. This needs prior write access to the cache directory, so the impact is low. | Create `cache/acme/index.html` as a symlink to `/tmp/x-missing`, fire `init`, and assert that `/tmp/x-missing` does not exist. The fix is to check `is_link()` first, or to create the file with `fopen($f, 'x')`. Report this upstream rather than patching vendored code. |
| 3 | P3 | `languages/acme-seo-pro-fr_FR.po` (new file) | The PR calls this an "updated" translation, but the file is created from `/dev/null`. WordPress loads `.mo` (or `.l10n.php`), not `.po`, and the diff has no `.mo`. French admin strings stay untranslated in production. | On an `fr_FR` site, assert that `__('Save', 'acme-seo-pro') === 'Enregistrer'`. This fails today. |
| 4 | P3 | `assets/admin.css:2`; `PR.md` ("a 16x16 icon") | The "icon" is an empty SVG, and nothing in the plugin enqueues `admin.css`. The asset is dead weight, or it is enqueued by files that are not in this diff, which would feed into finding 1. It is harmless as it stands. | Grep the head tree for `admin.css` in `wp_enqueue_style` calls, or have finding 1's `diff -r` confirm the file is byte-identical to the vendor zip. |

**Not findings, but noted:**
- The PR cites `docs/CACHE.md` as describing the placeholder behaviour. That doc section is added by this same diff, so it is the vendor describing its own change, not independent corroboration.
- The code does match the doc.

**FILES NEEDED BUT NOT PROVIDED:**
- The head SHA, merge base SHA and commit log with trailers.
- The vendor 2.4.2 zip, its published hash and the signing key fingerprint.
- The output of the claimed signature and hash verification.
- `src/admin.css` and `docs/BUILD.md`, which are referenced but absent.
- CI check status.

## Close-out

Not written by me: a reviewer does not adjudicate its own findings. This is the state for whoever closes the PR.

**ADJUDICATION:**

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | Pending (P1, cannot be deferred) | Needs the hash, signature and `diff -r` evidence described above. |
| 2 | Pending (can be deferred with an upstream issue link) | — |
| 3 | Pending (can be deferred, or fixed by adding the vendor's `.mo`) | — |
| 4 | Pending (likely closed by the evidence for #1) | — |

**VERIFIED AFTER FIXES:** nothing yet. No fixes have been made.

**MERGE RECOMMENDATION: do not merge yet.** Open items:
1. **Finding 1:** show that the committed tree equals the signed 2.4.2 release.
2. **Round 2 of the High tier:** run it, preferably with a second vendor, on the frozen head SHA.
3. **Commit details:** record the head and merge base SHAs and the authorship trailers.
4. **CI:** all expected checks must be present and green. None were shown.
5. **Adjudication:** write a decision for findings 2–4.

If item 1 comes back clean and round 2 finds nothing new, this is a straightforward merge. Nothing in the visible code is malicious.

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "unverified_claim",
      "location": "PR.md:5",
      "scenario": "Signature/hash verification is asserted without artifacts, and nothing shows the committed tree equals the signed 2.4.2 zip (admin.css references src/admin.css and docs/BUILD.md, which are absent). Any divergence runs in production with full DB and file access.",
      "fix": "Attach the SHA-256, the gpg --verify output with the key fingerprint, and a clean diff -r between the unzipped vendor release and the plugin directory at the head SHA."
    },
    {
      "severity": "P3",
      "evidence_level": "code_read",
      "location": "wp-content/plugins/acme-seo-pro/includes/cache.php:13-14",
      "scenario": "A dangling symlink at cache/acme/index.html passes !file_exists(), and file_put_contents follows it, creating an empty file at an arbitrary target on every request. This requires prior write access to the cache directory.",
      "fix": "Check is_link() or use fopen($f, 'x'); report upstream rather than patching vendored code."
    },
    {
      "severity": "P3",
      "evidence_level": "code_read",
      "location": "wp-content/plugins/acme-seo-pro/languages/acme-seo-pro-fr_FR.po",
      "scenario": "The file is new (not updated), and only a .po ships, with no .mo. WordPress does not load .po, so the French strings never appear.",
      "fix": "Include the vendor's compiled .mo (or .l10n.php) and correct the PR description."
    },
    {
      "severity": "P3",
      "evidence_level": "code_read",
      "location": "wp-content/plugins/acme-seo-pro/assets/admin.css:2",
      "scenario": "The base64 decodes to an empty 16x16 SVG (benign), and no code in the tree enqueues admin.css, so it is a dead asset or depends on files outside the diff.",
      "fix": "Confirm it is byte-identical to the vendor zip as part of the evidence for finding 1."
    }
  ]
}
```