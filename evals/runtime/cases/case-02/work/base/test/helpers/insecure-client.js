// Test helper only. Never imported by src/. Refuses to run outside NODE_ENV=test.
const https = require('node:https');

function insecureClientForLocalFakes() {
  if (process.env.NODE_ENV !== 'test') throw new Error('test-only helper');
  return new https.Agent({ rejectUnauthorized: false });
}

module.exports = { insecureClientForLocalFakes };
