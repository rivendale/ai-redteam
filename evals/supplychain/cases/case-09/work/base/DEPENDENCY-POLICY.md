# Dependency policy
- Exact versions with artifact hashes (pip-compile --generate-hashes).
- New releases wait three days before adoption (cooldown) unless a security exception is recorded in the PR.
- Security exception: an advisory link, hashes that match the maintainer-published checksums, and a second reviewer's sign-off in the PR.
