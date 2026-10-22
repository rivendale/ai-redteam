# Case-health assessor failure list, October 22, 2026

Write the diagnostic contract before implementation. The assessor is offline, recommends only and never edits cases or recorded results. Small invented case keys, reports and usage records exercise these failures.

| Failure | Denying check |
|---|---|
| A case with no recorded review becomes KEEP | Empty coverage is NO-DATA; missing observations are counted, not zeros. |
| A saturated ordinary case becomes KEEP without a warning | All observed detections produce SHARPEN and an explicit never-failed warning. |
| A disclosure, regulatory/legal statement, consent/privacy text or safety-warning guard becomes SHARPEN or RETIRE-CANDIDATE solely because it is saturated | Each protected category stays KEEP (regression guard) and appears in its own section. |
| A likely protected case lacks a machine-readable category and is retired by accident | Conservative source/key classification plus an explicit protection override preserves it; uncertainty is visible. |
| A control flagged in every usable report becomes SHARPEN | Recommend FIX-CONTROL with its actual numerator and denominator. |
| A case always missed becomes a proven-bad case | Report the floor and recommend inspection, without claiming the matcher or case is proven wrong. |
| Repeats that disagree look stable | Group by exact text and model; expose disagreement and recommend FLAKY. |
| Different model/text groups are collapsed into one score | Preserve per-group detection denominators and discrimination evidence. |
| A safety-stopped, fallback, failed or invalid report becomes a miss or clean control | Separate unusable observations and shares from detection/control denominators. |
| Missing model or text identity is invented from a folder name | Mark provenance unknown; do not use it to prove stability or redundancy. |
| Repeated outcomes with only one or two distinct texts/models are called redundant | Say only overlap, needs enumeration. |
| Sampled or incomplete vectors prove redundancy | Require identical vectors across the full recorded observation grid for both cases, at least three distinct texts or models, and known usable identities. |
| A unique outcome in one late observation is dropped | Full enumeration retains it and rejects redundancy. |
| A case missing one grid cell is paired as redundant | Missing coverage prevents the redundancy label. |
| A generic matcher word alone is credited without warning | Identify weak match terms and score dependence; recommend REVIEW-MATCHER with bounded evidence. |
| A report names a planted file and line but receives no detection credit | Flag possible matcher mismatch without changing the canonical scorer or asserting a true positive. |
| A missing, corrupt, duplicated or unsupported input silently disappears | Emit a bounded diagnostic and a nonzero exit; retain counts of affected observations. |
| Case names collide across suites | Use suite-qualified development identities. |
| Current expected data is presented as the historical key used in a run | Identify current-key rescoring explicitly and preserve changed-key/provenance limits. |
| A hold-out case name, slug, file, matcher, report, per-case score, path or grouping leaks through JSON, Markdown, warnings or errors | Sentinel-bearing hold-outs produce aggregate counts only in every output channel. |
| A hold-out influences a development pruning or redundancy recommendation | Keep hold-out processing separate and aggregate only. |
| Private source/report bytes are echoed into diagnostics | Output structural descriptions and counts; no snippets or matched values. |
| Source or run dates are invented from filesystem mtimes | Use explicit recorded dates or dated published records; unknown stays unknown and assumptions are labeled. |
| Re-running the tool changes its ordering or counts | Fixed as-of date and deterministic ordering produce identical artifacts. |
| The assessor mutates the corpus, invokes a proof, calls a model or uses the network | Snapshot inputs and use a tiny offline subprocess fixture; input hashes stay unchanged and no runners are executed. |
| A path or symlink directs the assessor outside its declared input roots | Reject symlinks and escaped paths before reading them. |
| Diagnostic output overwrites an input or a previous artifact unexpectedly | Refuse output inside case/result roots and existing artifacts unless an explicit overwrite option is selected. |

The first public report must state its observation coverage, current-key rescoring limits, unknown identities/dates and unusable inputs. Recommendations are not deletion instructions, release gates or new model evidence.

## Follow-up failures, October 22, 2026

Write the regression checks before the implementation correction:

- Binary case-input bytes after `=== INPUTS ===` must not erase the exact,
  decodable skill-text prefix. Recover that prefix without replacement decoding;
  corruption inside the skill-text prefix must still be reported as invalid.
- A case with zero recorded observations must carry an explicit NO-DATA coverage
  label, distinct from a case with recorded but unusable reviews. The amended
  no-results verdict is NO-DATA. UNTESTABLE requires recorded but unusable reviews.
- Many partial overlaps must have exact counts and bounded examples. Summarizing
  display noise must not change full-vector comparison or the redundancy gate.

Amendment on October 22, 2026: NO-DATA replaces the original no-results
UNTESTABLE expectation. This is a verdict change, not just a coverage label.
