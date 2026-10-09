# Open a changelog PR every Monday  (post, 2026-09-17)

Your script already writes a changelog draft; the manual part is getting it onto the repository. A 25-line GitHub Actions workflow runs your draft script every Monday, commits the result to a new branch and opens a pull request for a person to review and merge. The whole workflow:

```yaml
name: weekly-changelog
on:
  schedule:
    - cron: "0 8 * * 1"
  workflow_dispatch:
permissions:
  contents: write
  pull-requests: write
jobs:
  draft:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@8e5e7e5ab8b370d6c329ec480221332ada57f0ab
        with:
          fetch-depth: 0
      - run: python3 changelog.py > changelog-draft.md
      - run: |
          git checkout -b changelog-${{ github.run_id }}
          git add changelog-draft.md
          git diff --cached --quiet && exit 0
          git -c user.name=ci -c user.email=ci@example.test commit -m "Weekly changelog draft"
          git push origin HEAD
          gh pr create --fill
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

It uses the repository's own token, so turn on "Allow GitHub Actions to create and approve pull requests" in the repository settings first; pull requests opened that way do not start other workflows, so the reviewer reads the file. The checkout action is pinned to a commit, and it fetches full history because the draft script reads commit messages.
