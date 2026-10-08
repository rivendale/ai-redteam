# Review of PR #112 (first round)

REVIEWED: PR #112, head 1c7f9a2, merge base 40be8d1.

| # | Severity | Location | Failure scenario | Suggested test |
|---|---|---|---|---|
| F1 | P1 | exporter.py:10 | A value that contains a comma, such as "a,b", is written unquoted and splits into two columns, so the exported row has the wrong number of fields. | Export [["ann", "a,b"]] and read it back with csv.reader; expect [["ann", "a,b"]]. |

FILES NEEDED BUT NOT PROVIDED: none.
