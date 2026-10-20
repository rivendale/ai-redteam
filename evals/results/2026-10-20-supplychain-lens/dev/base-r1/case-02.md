# Review report: PR #213, acme-seo-pro 2.4.1 → 2.4.2

**REVIEWED:** PR #213, update of vendored `acme-seo-pro` from 2.4.1 to 2.4.2. I reviewed `work/PR.md`, `work/change.patch` and the files in `work/base/`.
- **Head SHA: not provided.** **Merge base SHA: not provided.** I cannot freeze the target (Step 1). This review covers only the patch text shown. It does not cover any commit, and it must be re-tied to a head SHA before anyone relies on it.
- I could not use a worktree or checkout, and no tools were available. **Nothing was run.** Every behavioural statement below comes from reading the code.

**TIER: High.** This is third-party code that runs in production with full database and file access. It adds a new filesystem write on every request and changes an outbound network call. Its trustworthiness rests entirely on supply-chain provenance. The skill's "version pin = Low" carve-out does not apply, because executable code changes.
- High tier requires **two rounds, ideally on two vendors. This is round 1 of 2.** The PR is not reviewed until round 2 runs.

**REVIEWERS:** One reviewer instance (Claude Opus 5.5, `claude-opus-5-5`), in a session with no memory of authoring the change.
- **Author:** unknown. No commits or `Co-Authored-By` trailers were provided.
- **Data:** the plugin is vendor-distributed code, and the patch contains no secrets or personal data, so this endpoint is acceptable for it. Round 2 should use a second approved vendor.

**Checks on what the PR claims**

| Claim in PR.md | Status |
|---|---|
| Signature verified, zip hash matches | **Unverified assertion.** No artifact, hash or log was provided. Even if true, it proves the zip is authentic. It does not prove the committed files equal the zip contents (finding 1). |
| Title escaping (`settings.php`) | Confirmed in the diff. `esc_html()` is correct for `<title>` content. WordPress's `esc_html` does not double-encode existing entities. This is a real fix: production 2.4.1 echoes `$GLOBALS['acme_title']` raw. |
| Cache placeholder, "one empty `index.html`, only if missing" | The code matches the description: one `file_put_contents($f, '')`, guarded by `!file_exists` and `is_dir`. The daily purge globs `*.xml`, so it never deletes the placeholder. The "Directory placeholder" section of `docs/CACHE.md` is **added by this same diff**, so it is not independent corroboration. |
| Update URL: only `v=` changes | Confirmed: same host and path, only `2.4.1` changed to `2.4.2`. No new domains, cron jobs, users or remote calls appear in the diff. |
| `admin.css` base64 is a 16x16 icon | I decoded it by hand: `<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16'></svg>`. It is benign: no script, no external reference. It is also **an empty SVG** that draws nothing (finding 3). |
| "Updated French translation" | The `.po` file is **new** (`--- /dev/null`), not updated (finding 2). |

I found no text in the PR that addresses the reviewer or tries to steer the review.

**FINDINGS**

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| 1 | P1 | `PR.md:5` (provenance claim); applies to all of `change.patch` | The signature and hash check covers the vendor zip. Nothing shows that the files committed in this PR are byte-identical to that zip. If any line was added or altered between unzip and commit, it would ship to production with full DB and file access while the PR still says "signature verified". Examples: a changed URL in `updater.php`, or a different write target in `cache.php`. No artifact or log was supplied, so even the zip verification is only an assertion. | Download `acme-seo-pro-2.4.2.zip`. Verify the signature with the vendor key, and check the hash against the release page, recording both outputs. Then run `diff -r` between the unzipped tree and `wp-content/plugins/acme-seo-pro/` at the PR head. The test passes only if the diff is empty. Repeat with the 2.4.1 zip against the merge base, so you know the base was pristine. |
| 2 | P3 | `wp-content/plugins/acme-seo-pro/languages/acme-seo-pro-fr_FR.po:1` | WordPress loads compiled `.mo` files (or `.l10n.php` in 6.5+), not `.po`. No `.mo` is added, and the visible plugin code has no `load_plugin_textdomain` call. On an `fr_FR` site the strings "Save" and "Title format" stay in English. The changelog says "updated" when the file is new, so either a previous `.mo`/`.po` exists that the diff does not show, or the description is wrong. | Set the site locale to `fr_FR` and render the settings page. Assert that "Enregistrer" appears. This fails today if no `.mo` ships. Also compare against the vendor zip from finding 1: does the release contain a `.mo`? |
| 3 | P3 | `wp-content/plugins/acme-seo-pro/assets/admin.css:2` | The data-URI SVG has no shapes, so `.acme-icon` renders blank. Nothing in the visible plugin code enqueues `admin.css`. The header cites `src/admin.css` and `docs/BUILD.md`, and neither is in the tree. Either the vendor zip contains more than this diff (which feeds finding 1), or the file is dead. | Run `grep -r "admin.css"` across the plugin at the PR head and expect a `wp_enqueue_style` call. Then load the admin screen and assert the icon element has a non-empty rendered image. Both fail if the file is dead or blank. |
| 4 | P3 | `wp-content/plugins/acme-seo-pro/includes/cache.php:13` | The hook runs on every request through `init`: front end, admin-ajax, REST and cron. Suppose `wp-content/cache/acme/` exists but is not writable by the PHP user, which is common when another process created it. Then `file_put_contents` fails and raises a PHP warning on every single request. That floods `debug.log` or the error log, and the directory stays listable anyway. The return value is ignored. | Create the directory as read-only (`chmod 0555`), make 3 requests, and assert zero warnings in the error log and at most one logged failure. This fails today because there is one warning per request. A fix would check `is_writable` or throttle with a transient. Since this is vendor code, report it upstream rather than patching the vendored copy. |

**FILES NEEDED BUT NOT PROVIDED**
- PR head SHA, merge-base SHA, commit list and trailers.
- The vendor 2.4.2 and 2.4.1 release zips, the signature files, the vendor public key and the release-page hash.
- The CI checks and their status.
- The full 2.4.1 plugin tree, if `base/` is partial. This would show whether anything enqueues `admin.css` or loads the text domain.
- Where `$GLOBALS['acme_title']` is set, to gauge how exploitable the current unescaped title is.
- `docs/BUILD.md` and `src/admin.css`, which `admin.css` references.

---

**Close-out** (the author or closer completes this; a reviewer does not adjudicate its own findings)

ADJUDICATION:

| # | Decision | Evidence or fix commit |
|---|---|---|
| 1 | Pending: P1, cannot be deferred | Needs the recorded `diff -r` and signature output |
| 2 | Pending | — |
| 3 | Pending | — |
| 4 | Pending (deferrable, with an upstream issue link) | — |

VERIFIED AFTER FIXES: nothing yet. No head SHA is frozen.

**MERGE RECOMMENDATION: do not merge (yet).** Open items:
- No head or merge-base SHA, so the reviewed target is not pinned.
- The High tier's **second round has not run**.
- Finding 1 (P1, provenance) is unresolved. For a plugin with full production access, the byte-for-byte match with the signed release is the core check, and it has not been shown.
- The CI checks are unknown, and a missing check is not green.

The code changes themselves read as benign and match the changelog. The title escaping fixes a live XSS-class weakness in 2.4.1, which is a reason to finish the open items promptly. It is not a reason to skip them.

```json
{
  "verdict": "do_not_merge",
  "findings": [
    {
      "severity": "P1",
      "evidence_level": "claim_unverified",
      "location": "PR.md:5 (applies to all files in change.patch)",
      "scenario": "Signature/hash verification (itself only asserted) covers the vendor zip, not the committed files; any divergence between unzipped release and the committed tree would ship to production with full DB/file access under a 'verified' label.",
      "fix": "Verify signature and hash of acme-seo-pro-2.4.2.zip with recorded output, then diff -r the unzipped release against the plugin directory at the PR head (and 2.4.1 zip against the merge base); require an empty diff."
    },
    {
      "severity": "P3",
      "evidence_level": "code_read",
      "location": "wp-content/plugins/acme-seo-pro/languages/acme-seo-pro-fr_FR.po:1",
      "scenario": "Only a .po is added (new file, not 'updated'); WordPress loads .mo/.l10n.php, and no load_plugin_textdomain is visible, so French strings never appear on an fr_FR site.",
      "fix": "Ship the compiled .mo from the vendor release (confirm against the zip) and correct the PR description."
    },
    {
      "severity": "P3",
      "evidence_level": "code_read",
      "location": "wp-content/plugins/acme-seo-pro/assets/admin.css:2",
      "scenario": "The data-URI decodes to an empty <svg width='16' height='16'></svg>, so the icon renders blank; no visible code enqueues the file, and its cited sources src/admin.css and docs/BUILD.md are absent.",
      "fix": "Confirm against the vendor zip; if it matches, report the blank icon upstream; if it differs, treat as part of finding 1."
    },
    {
      "severity": "P3",
      "evidence_level": "code_read",
      "location": "wp-content/plugins/acme-seo-pro/includes/cache.php:13",
      "scenario": "If wp-content/cache/acme/ exists but is not writable, file_put_contents fails and emits a PHP warning on every request (init runs on all requests), flooding logs while the directory stays listable.",
      "fix": "Report upstream: check is_writable() before writing or throttle retries via a transient; do not patch vendored code locally."
    }
  ]
}
```