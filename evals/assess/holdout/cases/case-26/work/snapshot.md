# Glossary-first pre-translation, step by step  (post, 2026-09-21)

Put the approved glossary terms in the prompt as a table (source term, required translation), then the strings to translate, then a rule: use the table verbatim,
never paraphrase a glossary term. We ran it on 800 strings in Spanish and German; a bilingual reviewer found glossary terms used correctly in 779 of 800 (97%).
The prompt text and the 800 strings are in the post. About 25 lines of Python call the model and write the result back to a CSV.
