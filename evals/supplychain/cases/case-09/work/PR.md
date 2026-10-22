# PR #124: web-frame 4.2.1 to 4.2.2 (urgent security fix, policy exception)

web-frame 4.2.2 was published 19 hours ago. Vendor advisory ADV-2026-0412 (invented identifier for this exercise), severity Critical, says
4.2.1 and earlier allow unauthenticated request smuggling on the HTTP/1.1 parser and that exploitation has been observed. Our service is
internet-facing, so this is an exception to the three-day cooldown under DEPENDENCY-POLICY.md:

- advisory: linked in the vendor's release notes; the fixed version is 4.2.2;
- artifacts: the sdist and wheel hashes in the lock match the SHA-256 checksums the maintainers publish on the advisory page (compared line by line, see artifact/checksums.txt);
- the published wheel file list equals the source-tag file list (artifact/); the tag diff is the 9-line parser change described in the advisory;
- second reviewer: @security-reviewer approved this exception in the PR thread (artifact/signoff.txt).
