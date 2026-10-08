# PR #77: allow uploads in folders

Head 6d2e0a4, merge base 21c8b7f.

Users want to keep uploads in folders, so `read_upload` resolves the path and refuses anything outside the upload directory. Tests added
and passing. Reviewers: please also look at the wording of the docstring; I am not sure it is clear.
