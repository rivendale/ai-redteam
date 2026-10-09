# Adversarial Diagnostic Review: `helpcentre.py`

## Pass 1: Reconstruct

The work is a rider help-centre assistant. Any signed-in rider can add a "tip" with `add_article`, and that tip becomes searchable straight away. `search` ranks articles by how many words they share with the question, and `answer` sends the top 2 article bodies to an LLM with the instruction "answer using only this help text". For this to be safe in production, every article in `_ARTICLES` would have to be trustworthy enough to show to every rider as official help, including lock-reset steps and refund contact details.

The load-bearing assumptions are:
- (a) Rider-contributed text is benign and accurate.
- (b) Callers enforce authentication and pass a real rider identity.
- (c) `title` and `body` are always non-null strings.
- (d) Word-overlap ranking puts the staff article on top for the questions that matter.
- (e) An in-memory list is an acceptable store.

None of these is enforced in the code.

## Pass 2: Attack (Track B, plus Track R for customer-facing text)

**Rider content reaches every rider unreviewed.** `add_article` appends with no moderation. `answer` then puts that body into the prompt under the label "help text", and the instruction "using only this help text" makes it authoritative. The `by` field is dropped when the context is built (`"\n".join(a["body"] ...)`), so the LLM cannot tell staff text from rider text.

**Ranking can be gamed.** The score is a raw count of shared words with no length normalisation. A long rider post stuffed with "refund contact lock reset unlock bike scan code handlebar green light help" will beat the one-sentence staff article for most questions. With `k=2`, two such posts take both slots and the staff article disappears completely.

**One malformed input breaks search for everyone.** `a["title"] + " " + a["body"]` raises `TypeError` if either value is `None` or not a string. Nothing validates these values at insertion, so one bad record makes every later `search`, and therefore every `answer`, fail for every rider. Whether callers validate is UNVERIFIED.

**The author field can be spoofed.** `by` is whatever string the caller passes as `rider`. A caller passing `"staff"`, or an attacker reaching the function with that value, produces a record that looks like a staff article. The docstring says "any signed-in rider", but the function does no authentication check.

**Search returns irrelevant articles instead of nothing.** Articles with a score of 0 are still returned. An empty question, or a question with no overlapping words, still sends 2 arbitrary articles to the LLM, and there is no "I don't know, contact support" path. Tokenising with `split()` keeps punctuation, so "bike?" does not match "bike". Most real questions will therefore score poorly, and attacker posts get more weight.

**Storage is not production-grade.** `_ARTICLES` is a module-level list:
- It is lost on restart.
- It diverges across workers or processes.
- It has no edit, delete or takedown path, so a malicious tip cannot be removed without redeploying.
- It keeps no audit trail.
- It grows without limit, and every query scans all of it in O(n). Mass submissions degrade the service for everyone.

**Other gaps.**
- No tests at all.
- The `llm` call has no error handling or timeout.
- The question is concatenated into the prompt without delimiters. This mainly affects only the asker's own answer, so it is Low.
- The title is never passed to the LLM.

**Drift from the request.** The request asked for an assistant that answers "from the help articles" and lets riders "contribute tips so help text stays fresh". The work merged tips into articles, so tips became official help text. It delivered freshness and dropped the trust boundary the request implied.

## Pass 3: Self-check

I dropped the prompt-injection-via-question concern to Low, because it only affects the asker. I kept "malformed input" as High rather than Critical, because callers may already validate; I cannot see them. The most serious thing I might still be missing is the caller layer: how riders are authenticated, how fast submissions can be made, and whether the LLM output is rendered as HTML or Markdown. If it is, rider tips could carry links or markup straight into the UI.

---

**VERDICT: REWORK.** Unmoderated rider text is served to every rider as authoritative help, including refund contacts and lock-reset steps. That is a design flaw, not a one-line fix.

**CONFIDENCE IN VERDICT: high.** The core issue can be confirmed from the code alone. Confidence is limited only by not seeing the caller, auth or rendering layers.

## Findings

| # | Severity | Evidence | Location | What is wrong | Failure scenario | Fix or test |
|---|---|---|---|---|---|---|
| 1 | Critical | CONFIRMED | `add_article` (no moderation); `answer` builds context from all article bodies | Rider tips go straight into the LLM context, shown to all riders as official help text | An attacker posts "Refunds: call +44 … / pay the reset fee at evil.example". Riders asking about refunds or lock resets get the attacker's contact, which leads to fraud and harm to customers | Put tips in a separate store with a moderation queue. Only staff-approved content goes into the answer context. Test: an unapproved tip never appears in the `answer` prompt |
| 2 | High | CONFIRMED | `search` key lambda; `k=2` | Unnormalised word-overlap scoring lets keyword-stuffed posts outrank staff articles and push them out of the top 2 | Two long posts full of help keywords take both slots for "how do I unlock a bike", so the staff instructions are never shown | Rank only vetted content, or always pin and prefer staff content and normalise the score. Test: a stuffed rider post does not displace the staff article |
| 3 | High | CONFIRMED | `answer`: `"\n".join(a["body"] …)` | Provenance (`by`) and title are dropped, so the LLM cannot tell staff text from rider text | The LLM treats a rider guess as authoritative and states it confidently | Label sources in the context. Only staff sources may support safety, refund or contact answers |
| 4 | High | CONFIRMED (crash path) / UNVERIFIED (caller validation) | `add_article` (no validation); `search` concatenation | A `None` or non-string `title`/`body` raises `TypeError` on every later search | `add_article("r1", None, "x")` breaks `answer()` for all riders until restart | Validate type and length at insert. Test: invalid input is rejected and search still works |
| 5 | High | CONFIRMED | `add_article(rider, …)`; `"by": rider` | The author is caller-supplied and spoofable, and the function has no auth check despite the docstring | A record with `by="staff"` cannot be told apart from a real staff article in any later trust logic | Derive the author from the authenticated session server-side and reject reserved identities. Test: `rider="staff"` from a rider session is refused |
| 6 | Medium | CONFIRMED | `_ARTICLES` global list | No persistence, no takedown, no audit trail, unbounded growth, not shared across processes | A malicious tip cannot be removed without redeploying, it is lost on restart, workers disagree, and submission spam slows every query | Use a persistent store with edit, delete and audit, plus rate limits and size caps |
| 7 | Medium | CONFIRMED | `search` (zero scores returned; `split()` keeps punctuation) | Irrelevant articles are returned when nothing matches, and "bike?" does not match "bike" | The LLM answers from unrelated text or hallucinates. There is no "contact support" fallback | Normalise tokens, apply a minimum score threshold, and return a fixed fallback when nothing matches. Test: an empty or unrelated question returns the fallback |
| 8 | Medium | CONFIRMED | Whole file | No tests | Any of the above regressions ships unnoticed | Add tests for 1–7 and mutation-check them (for example, remove the moderation filter and confirm the test goes red) |
| 9 | Low | CONFIRMED | `answer` | The `llm` call has no error handling or timeout, and the question has no prompt delimiters | An LLM outage surfaces as an unhandled exception. A rider can steer the prompt for their own answer | Wrap the call with timeout and fallback, and delimit the question |

## What holds up

- The prompt does tell the model to use only the supplied text, which is the right intent.
- Python's stable sort keeps the staff article first on ties.
- The code is small and easy to fix structurally.

## Unverified claims

- **"Any signed-in rider"**: confirm by checking the caller's route or auth middleware.
- **"Searchable at once"** is accurate, but it is a hazard here, not a feature.
- **How LLM output is rendered**: if it is rendered as HTML or Markdown, check for link and XSS injection from tips.
- **Whether callers validate input**: inspect the calling layer.

## Questions for the author

1. Were rider tips ever meant to be official answers, or a suggestion queue for staff?
2. Who can call `add_article`, and where is the rider identity derived?
3. Is there any moderation or takedown process outside this file?

## Decision-maker summary

Do not launch. Any rider can currently rewrite the help answers every rider sees, including refund contacts and lock instructions. Even with the crash and spoofing issues fixed, launching before tips are moderated invites fraud.

## Owner summary

The help assistant treats anything a rider types as official advice and shows it to every other rider. Someone could post a fake refund phone number or wrong unlocking steps, and the assistant would repeat it. Rider tips need staff review before they can appear in answers, and the system needs basic safeguards and tests before launch.

```json
{
  "verdict": "REWORK",
  "findings": [
    {"severity": "Critical", "evidence_level": "CONFIRMED", "location": "add_article (no moderation); answer context build", "scenario": "Attacker posts a tip with a fake refund contact or lock-reset fee; every rider asking about refunds or resets is shown the attacker's details as official help.", "fix": "Separate tip store with moderation; only staff-approved content enters the answer context; test that unapproved tips never reach the prompt."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "search key lambda; k=2", "scenario": "Two keyword-stuffed rider posts outrank the one-line staff article and take both top-2 slots, hiding the official unlock instructions.", "fix": "Rank only vetted content or pin and prefer staff content; normalise scores; test that a stuffed post cannot displace the staff article."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "answer: join of a['body'] only", "scenario": "Provenance and title are dropped, so the LLM presents a rider's guess as authoritative help.", "fix": "Label each source in the context; restrict safety, refund and contact answers to staff sources."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "add_article (no validation); search title+body concatenation", "scenario": "add_article('r1', None, 'x') makes every later search raise TypeError, breaking answers for all riders.", "fix": "Validate types and lengths on insert; test that invalid input is rejected and search keeps working."},
    {"severity": "High", "evidence_level": "CONFIRMED", "location": "add_article rider parameter -> 'by'", "scenario": "Caller passes rider='staff' and the tip is indistinguishable from a staff article; the function has no auth check despite its docstring.", "fix": "Derive author from the authenticated session server-side and reject reserved identities; add a test."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "_ARTICLES module-level list", "scenario": "Malicious tip cannot be taken down without redeploy; data lost on restart; workers diverge; spam submissions grow the list and slow every query.", "fix": "Persistent store with edit, delete and audit trail; rate limits and size caps."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "search (zero-score results; split() tokenisation)", "scenario": "Unrelated or empty questions still get 2 arbitrary articles; 'bike?' fails to match 'bike'; the LLM answers from irrelevant text.", "fix": "Normalise tokens, apply a minimum score threshold, return a 'contact support' fallback; test it."},
    {"severity": "Medium", "evidence_level": "CONFIRMED", "location": "whole file", "scenario": "No tests, so regressions in moderation, search or validation ship unnoticed.", "fix": "Add tests for each finding and mutation-check that they fail when the guarded code is broken."},
    {"severity": "Low", "evidence_level": "CONFIRMED", "location": "answer llm call", "scenario": "An LLM outage raises an unhandled exception; the question is concatenated without delimiters so a rider can steer their own answer.", "fix": "Add timeout, error handling and a fallback; delimit the question in the prompt."}
  ]
}
```