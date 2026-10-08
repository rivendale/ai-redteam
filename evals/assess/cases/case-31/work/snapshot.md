# Changelogs from commit trailers, step by step  (post, 2026-09-17)

Add a `Change:` trailer to each commit message. A 25-line script reads `git log` since the last tag, groups lines by trailer type and writes the
markdown. The script, a sample repository and the output are in the post. We have run it weekly for six months with no manual editing.
