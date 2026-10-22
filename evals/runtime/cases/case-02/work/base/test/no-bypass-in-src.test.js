const assert = require('node:assert');
const { execSync } = require('node:child_process');

// CI check: nothing under src/ may mention the test helper or disable verification.
const hits = execSync("grep -rnE 'rejectUnauthorized|insecure-client|NODE_TLS_REJECT' src || true").toString();
assert.strictEqual(hits.trim(), '');
