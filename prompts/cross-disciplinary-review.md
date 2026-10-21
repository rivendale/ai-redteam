# Cross-Disciplinary Review of a Claim (paste-in prompt)

A method for asking AI models to judge whether a theory, finding or design is new and sound. It has no
skill and no eval cases; it is a paste-in prompt only. Use it when the claim spans several fields, or
when the author asks "is this a breakthrough?"

Source: a replication of SSRN 6277519. That preprint reported that five models called one theory a
"paradigm shift". Each model saw only the author's papers, and the prompt asked whether the theory was
one. Under a neutral prompt with one reviewer per discipline and prior work first, three current models
rated the same theory "not new". The full account and the six rules are in
[hsi-operator's lessons of 2026-10-21](https://github.com/rivendale/hsi-operator/blob/main/docs/lessons-2026-10-21.md);
this prompt applies them.

## Before you paste

1. **Gather an independent evidence file.** Collect prior work yourself (a literature search, a review
   article, a textbook chapter). Do not use the author's own bibliography or summary. Reviewers who read
   the same partial input share its blind spot, whatever their vendor.
2. **Pick the disciplines.** Name each field the claim touches. Each one becomes its own reviewer seat.
3. **Use a model approved for the material.** Unpublished work and personal data go only where they may go.

```
# CROSS-DISCIPLINARY REVIEW OF A CLAIM

You are a panel of independent reviewers, one per discipline listed below. You did not produce the
claim and have no stake in it. Your job is to place it in prior work and find what is wrong with it.
Do not judge whether it is a breakthrough.

## Inputs
CLAIM (the theory, finding or design, in the author's words):
<claim>
[paste]
</claim>

DISCIPLINES (one reviewer seat each):
<disciplines>
[for example: economics, ecology, control theory, philosophy of science]
</disciplines>

EVIDENCE FILE (prior work gathered independently of the author; may be "none provided"):
<evidence>
[paste]
</evidence>

## Method
For EACH discipline, as a separate reviewer, in this order:
1. Prior work first. Before any judgment, list the earlier work in that field that makes the same or a
   close argument, by author and year. Say how close each one is.
2. What is wrong. State the weakest assumption, the strongest counter-argument and any evidence that
   contradicts the claim. Do not rate how important or novel the claim is.
3. Citations. For every source you cite, mark it RECALLED (from memory) or FROM EVIDENCE FILE.
   Treat every RECALLED citation as unverified.
4. Verdict for that field: NOT NEW, PARTLY NEW (say which part) or NEW, with the one source that decides it.

Then, across all seats:
5. Where the seats disagree, and why.
6. LOAD-BEARING CITATIONS: the citations a verdict depends on, each with the exact statement it must
   support, so a person can check it.
7. End with the line "END OF REVIEW". An answer without that line was cut off and is incomplete.
```

## After the answers come back

1. **Check every answer finished.** A missing "END OF REVIEW" line means the answer hit a token limit.
   Rerun it with more room; never score a cut-off answer.
2. **Check the load-bearing citations.** Read each source and confirm it says what the reviewer claimed.
   In the replication, every model attributed the same claim to one book; the source described a narrower one.
3. **Run a framing control.** Ask the same question once with the author's framing ("is this a paradigm
   shift?"). If the verdict changes, the framing was doing the reviewing.
