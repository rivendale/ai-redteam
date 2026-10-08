// Notes server entry point (existing file; the tools named in agent/mcp.json are served from here).
const readOnly = process.argv.includes("--read-only");
module.exports = { readOnly };
