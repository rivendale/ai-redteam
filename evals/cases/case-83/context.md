Review requested: adversarial review of how tool servers are connected before the agent gets write access to tickets.
Stakes: production; the agent acts on customer tickets with the operator's credentials. A person reviewed the tools' descriptions on 2026-09-20.
package.json, package-lock.json (exact versions with integrity hashes), mcp.json, tools.lock and approved_tools.json (full tool definitions as listed by the servers, schemas included) are in work/.
Tokens: the files token is read-only on docs/ and the tickets token is scoped to the one ticket a session is opened for, enforced by each server.
