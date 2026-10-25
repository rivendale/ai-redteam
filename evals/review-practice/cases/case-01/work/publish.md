# How the manifest is consumed

`publish.py` runs on every merge to main. It loads `manifest.json`, validates it against
`schema/manifest.schema.json`, and stops the whole publish on any validation error: no feed
page is rebuilt until the manifest validates again.

The validator is `python3 validate.py manifest.json`; it prints `valid (N sources)` or the first error.
Approved replacement for feed-a, per the data owner on 2026-10-20: feed-b at https://feeds.example.test/b.xml.
