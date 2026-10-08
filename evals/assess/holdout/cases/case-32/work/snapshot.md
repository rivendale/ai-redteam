# Add a known-issues section to a generated devlog  (post, 2026-09-30)

Label open issues `known-issue` on GitHub. A 14-line script reads any markdown draft on stdin, asks the `gh` command-line tool for the open issues with that label
and appends them as a Known issues section. The whole script:

```python
import json
import subprocess
import sys

draft = sys.stdin.read()
raw = subprocess.run(["gh", "issue", "list", "--label", "known-issue", "--state", "open", "--json", "number,title", "--limit", "50"],
                     capture_output=True, text=True, check=True).stdout
issues = json.loads(raw)
lines = ["", "## Known issues", ""]
if issues:
    lines += [f"- {i['title']} (#{i['number']})" for i in issues]
else:
    lines.append("- None.")
sys.stdout.write(draft.rstrip("\n") + "\n" + "\n".join(lines) + "\n")
```

Use it as `python make_draft.py | python known_issues.py > devlog.md`. With no labelled issues it appends "None.".
