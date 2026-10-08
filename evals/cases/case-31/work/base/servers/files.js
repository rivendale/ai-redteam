// Files server entry point (existing file). Serves text files under --root; writes need --allow-write and never with --read-only.
const args = process.argv.slice(2);
const root = args[args.indexOf("--root") + 1];
const writable = args.includes("--allow-write") && !args.includes("--read-only");
module.exports = { root, writable };
