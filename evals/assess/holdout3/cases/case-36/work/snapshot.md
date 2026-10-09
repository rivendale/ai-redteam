# Turn a subtitle file into a transcript page  (post, 2026-09-25)

Most transcription tools can write an .srt subtitle file. A 13-line Python script reads an .srt on stdin and prints a Hugo page: front matter, then one paragraph per subtitle with its start time in bold. The whole script:

```python
import re
import sys

text = sys.stdin.read()
lines = []
for block in re.split(r"\n\s*\n", text.strip()):
    parts = block.splitlines()
    if len(parts) < 3:
        continue
    start = parts[1].split(" --> ")[0].split(",")[0]
    lines.append(f"**{start}** {' '.join(parts[2:])}")
print("---\ntitle: Transcript\n---\n")
print("\n\n".join(lines))
```

Use it as `python3 srt_to_page.py < episode.srt > content/episodes/42/transcript.md`.
