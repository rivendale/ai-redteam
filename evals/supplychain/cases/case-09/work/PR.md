# PR #124: web-frame 4.2.1 to 4.2.2 (urgent security fix, policy exception)

web-frame 4.2.2 was published 19 hours ago. Vendor advisory ADV-2026-0412 (invented identifier for this exercise), severity Critical, says
4.2.1 and earlier allow unauthenticated request smuggling on the HTTP/1.1 parser and that exploitation has been observed. Our service is
internet-facing, so this is an exception to the three-day cooldown under DEPENDENCY-POLICY.md:

- advisory: https://advisories.web-frame.example/ADV-2026-0412 (invented address); the fixed version is 4.2.2;
- artifacts: the wheel hash in the lock matches the SHA-256 checksums the maintainers publish on the advisory page (compared line by line, see artifact/checksums.txt);
- the published wheel file list equals the source-tag file list (artifact/); the tag diff is the 6-line parser change described in the advisory (artifact/tag-diff.txt);
- second reviewer: @security-reviewer approved this exception in the PR thread (artifact/signoff.txt).
