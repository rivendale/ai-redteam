# Attack catalog for AI-produced work

Each entry is a way AI-built systems fail under attack, with the question a reviewer should ask and where to look.
Entries marked *measured* were reproduced on one operator's machines; the rest cite published research. Use it with
Track B (code) and Track C (claims) of the `redteam` skill.
How the entries map to the OWASP LLM and Agentic Top 10 lists and to MITRE ATLAS is in
[framework-mapping.md](framework-mapping.md).

## Untrusted input reaching something that can act

**1. Instructions hidden in ordinary data.** Injected instructions do not need to look like prompts: data an agent
reads as part of its task (a table cell, a document field, a tool result) can carry them. [UNVERIFIED: a social post
(2026-09) described a spreadsheet value steering two frontier models to the wrong vendor offer, and a reported Google
DeepMind taxonomy cites several web-attack types above 80% success; no repository, paper or table was located for
either, so neither figure is relied on here.]
*Ask:* where does content written by someone else (web pages, email, documents, tool output, social posts, cells)
reach a model that holds tools, credentials or a decision? What stops it?

**2. A peer handoff is a stronger attack than a request.** When an unsafe trajectory was injected as a pending
handoff from another agent, executed harm on four routes ranged 40-95%, against 0-5% on normal tasks
([arXiv 2609.18460](https://arxiv.org/html/2609.18460v1), section 7.2 and Table 3). The paper states it does not
establish natural rates or an autonomous cascade.
*Ask:* does this system accept work, plans or "context" from another agent, and does it re-check them, or trust
them because a colleague sent them?

**3. Tool names and descriptions are an attack surface.** Crafted tool names and descriptions can induce an agent to
select a tool and pass sensitive context into its arguments ([ContextLeak, arXiv 2608.27800](https://arxiv.org/html/2608.27800v1),
Duke University).
*Ask:* which third-party tools or MCP servers are loaded, are they pinned to a reviewed version, and what context
can flow into their arguments?

**4. A prompt instruction is not a control.** A "read-only" scope written into a prompt did not stop a sub-agent
from opening a network tunnel (*measured*). Anthropic's agent-security submission to NIST supports sandboxing and
least privilege ([PDF](https://www-cdn.anthropic.com/43ec7e770925deabc3f0bc1dbf0133769fd03812.pdf)), and its Zero Trust
guide recommends least agency ([guide](https://claude.com/resources/guides/zero-trust-for-ai-agents/security-considerations-for-autonomous-systems);
only an excerpt was verified, the full page did not load for the reviewer); Meta describes its Muse architecture as keeping credentials and sensitive
services outside the agent's runtime cell ([Meta](https://research.meta.ai/blog/security-and-safety-for-ai-agents-our-approach-with-muse);
a described design, not an independently certified result).
*Ask:* for each restriction the work claims, is it enforced by a credential, a capability, a sandbox or a network
path, or only by text the model reads?

**5. An empty allow-list may mean "no restriction".** A CLI agent run with an empty tools allow-list and a
non-interactive permission mode still read a canary file and ran a shell command (*measured*); in another vendor's
CLI the same value disables all tools.
*Ask:* was the confinement proved in the denying direction (a canary it must not reach, plus a working control),
or assumed from a flag's name?

**6. A URL check does not confine a browser.** A headless browser behind a starting-URL check followed a redirect
to localhost (*measured*). The control that held put every request through a proxy that resolves once and dials
the resolved address.
*Ask:* does the check sit on the path every request takes, including redirects, subresources and DNS rebinding,
or only on the first URL?

## Supply chain

**7. The install step runs code.** Package lifecycle scripts run during install, before anyone reads them. npm 12
makes dependency lifecycle scripts and implicit native builds opt-in
([GitHub changelog, 2026-07-08](https://github.blog/changelog/2026-07-08-npm-install-time-security-and-gat-bypass2fa-deprecation/)).
[UNVERIFIED: news reports in 2026-06 described a postinstall hook that rewrote a coding assistant's config to take
OAuth tokens, and worm campaigns across dozens of npm packages; primary sources were not located.]
*Ask:* does the change add dependencies, and do their install scripts run? Are versions pinned?

**8. Hallucinated names get registered.** "HalluSquatting": attackers pre-register resource identifiers that models
commonly hallucinate and host adversarial prompts there, turning a model's mistake into a pull attack
([arXiv 2607.07433](https://arxiv.org/abs/2607.07433)).
*Ask:* does every package, URL, API and flag in the work actually exist, and is it the one intended?

## Secrets and verification claims

**9. Secrets leak through reporting, not only argv.** A shell default like `${x:-unset}` prints the value when it is
set; a `config show` command printed live tokens; a credential sat in a process argument list at every start
(*measured*).
*Ask:* do logs, debug output, error messages or "redacted" summaries print the secret? Was the redaction tested with
a dummy value?

**10. A security property is a measurement, not a belief.** A key described as zero-retention was not, by its own
response header (*measured*). A provider's own page contradicted a summary that called it zero-retention.
*Ask:* is each retention, encryption or isolation claim read from the system (a header, a setting, a log) on the
date of the review?

**11. A library's classification drifts between versions.** An address filter excluded the CGNAT range
`100.64.0.0/10` only for IPv4 and relied on `ipaddress` flags for everything else. For `::ffff:100.64.0.1` the filter
refused it on Python 3.12.3 (which classifies the mapped range as reserved) and accepted it on 3.13.12 and 3.14.4
(where the mapped address is neither private nor reserved) (*measured*). The filter's design, not Python, let it
through; the version difference hid the flaw.
*Ask:* does a security decision delegate to a library's notion of "private", "safe" or "valid"? Was it tested on more
than one runtime version?

## Identity and authorization

**12. The token chooses its own algorithm.** A JWT verifier that reads `alg` from the token it is checking lets the
sender pick how it is checked: `none` means no signature, and an `HS256` token can be "signed" with the public key text
as the secret. RFC 8725 (JWT best current practices) section 3.1 says to verify the algorithm against what the
application expects, and sections 3.8 and 3.9 say to validate issuer and audience
([RFC 8725](https://www.rfc-editor.org/rfc/rfc8725.html)). The eval set has a vulnerable verifier and a pinned one
(cases 43 and 44), with a proof that forges both bad tokens.
*Ask:* is the accepted algorithm fixed in code, is expiry required (a missing `exp` should fail), and are issuer and
audience checked? Did a test try `none` and a token signed with the public key?

**13. One route outside the gate.** Every public route authenticates, and one "internal" route does not, because a
comment says only the scheduler calls it. The deployment config decides who can reach it, not the comment (eval case 45:
the production proxy forwards the internal prefix from the internet, and one query parameter deletes everything).
*Ask:* list every route, handler, queue consumer and scheduled endpoint and the gate each uses. Read the proxy, ingress
or gateway config that actually runs, not the one the author describes. Is "private network" enforced by a network
rule or only assumed?

**14. Identity or role read from a field the client sends.** The session holds the verified user and role, and a
handler takes the role, owner or user id from the request body or query string, with the session as a fallback
(eval case 46: a member sends `{"role": "admin"}`; any user lists another user's projects).
*Ask:* for every authorization decision, where does the identity come from? Is a client-supplied value ever used in
place of the verified one, even as an optional override?

**15. Webhooks without a signature check; TLS verification switched off.** A webhook endpoint that accepts any POST
trusts whoever knows the URL; the sender's documentation gives the header and the comparison to make, and recommends a
constant-time compare
([GitHub: validating webhook deliveries](https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries)).
Turning certificate verification off to make an error go away removes the only check that the other end is who it says
(CWE-295, [improper certificate validation](https://cwe.mitre.org/data/definitions/295.html)).
*Ask:* does every inbound webhook verify a signature, with a timestamp or replay check where the sender provides one?
Does any client set `verify=False`, `rejectUnauthorized: false`, `InsecureSkipVerify` or the like, and is it behind a
test-only flag?

**16. A valid certificate is not proof of ownership.** A certificate shows that someone controlled a name when it was
issued. It does not show the name belongs to the party in front of you, and any authority the domain does not restrict
may issue one. CAA records limit which authorities may issue for a domain
([RFC 8659](https://www.rfc-editor.org/rfc/rfc8659.html)); Certificate Transparency logs let the owner see what was
issued ([RFC 6962](https://www.rfc-editor.org/rfc/rfc6962.html)).
*Ask:* does the work treat "the certificate validates" as "this is the owner"? For a domain the work depends on, is
issuance restricted with CAA, and does anyone watch the transparency logs for certificates they did not request?

## Agents: actions, identity and shared state

**17. Judge an agent by its actions, not its words.** An agent's plan, its running commentary and its final summary are
text it wrote about itself. A run whose plan says "read-only" and whose tool calls edit a file, commit and push is
described accurately only by the tool calls and the repository afterwards (eval cases 47 and 48).
*Ask:* does the review compare the plan and the summary with the tool-call log, the diff, the repository state and
the remote? Which claim in the summary could be checked against an artifact, and was it?

**18. An action must be bound to who asked and for what (confused deputy).** A tool or server that acts with its own
broad credential, on behalf of whoever reaches it, can be driven by a request the user never made. The MCP
specification's security guidance describes the confused-deputy problem and token passthrough for MCP servers
([MCP security best practices](https://modelcontextprotocol.io/specification/draft/basic/security_best_practices)).
*Ask:* when the agent or a tool acts, whose credential is used, and is the action tied to the requesting user and the
request, or to anything that arrives at the tool? Are tokens passed through to downstream services that were not the
audience?

**19. Agents that share one identity cannot be told apart.** When several agents use the same account, key or token,
a log cannot say which one acted and one compromised agent cannot be cut off without stopping the rest.
*Ask:* does each agent have its own credential and its own scope? Can one be revoked alone, and does every write carry
the identity that made it?

**20. Shared state needs a claim and a fresh read.** Two agents write one file: the second writes on top of the version
it read earlier, and the first agent's work is gone, while both report success (eval case 49).
*Ask:* what stops two writers colliding: a claim, a lock, a compare-and-swap on a version, or only a protocol in a
document? Does the log show a write made on a version older than the one on disk, and does any summary claim a result
the final file does not contain?

**21. Memory and notes written by one run are read as instructions by the next.** A persistent memory, scratch file,
notes folder or instruction file that an agent can write is a channel from whatever it read to what future runs trust.
*Ask:* what content can reach those files, from where, and who reviews the changes? Would an instruction planted in
a web page, a ticket or a data cell be saved and later obeyed?

**22. Skills, hooks and instruction files are code.** A `SKILL.md`, an `AGENTS.md`, a slash command, a plugin manifest
or a hook changes what an agent does, and hooks run commands. Claude Code's hooks documentation has its own security
section on this ([hooks](https://code.claude.com/docs/en/hooks)).
*Ask:* did the change add or alter one of these files? Read it as executable: what does it tell the agent to run, fetch
or trust? Is an installed copy pinned to a reviewed commit, and was the diff read when it updated?

## Build and deploy

**23. A CI workflow is a program that runs untrusted input with a token.** The usual faults: `pull_request_target` with
a checkout of the pull request's code, which runs attacker-controlled code with the base repository's secrets;
`${{ github.event.* }}` text expanded inside a `run:` step, which is script injection; actions referenced by a mutable
tag instead of a commit SHA; and a token with write permission by default. GitHub's secure-use guide covers each
([GitHub Actions secure use](https://docs.github.com/en/actions/reference/security/secure-use)). This repository's own
workflow follows them (read-only token, SHA-pinned actions, `pull_request`, no secrets).
*Ask:* for each workflow, which events trigger it and what code runs? Does any `run:` step interpolate event data?
Are actions pinned? What is the narrowest `permissions:` block that works?

**24. Infrastructure as code (a short lead).** Templates for cloud resources fail in familiar ways: a storage bucket or
database open to the internet, a security group open to every address, an administrator role granted to a service
that needs one table, secrets written to state files or committed variables.
*Ask:* for each resource the change creates, who can reach it, with what permission, and where do its secrets live?

## Host and network leads

These three come from conference and video summaries; no primary source was located, so they are leads for questions
to ask, not evidence. [UNVERIFIED: the incident descriptions that prompted them were not traced to a report.]

**25. A process can wear another process's name.** Names in a process list are set by the process. *Ask:* when work
checks a host for something unexpected, does it identify processes by executable path, hash, parent and open sockets,
or by the name shown?

**26. A listener may not appear in the usual socket list.** A program that reads raw packets can receive a "magic"
packet without holding an ordinary listening port, so a port scan of the host and `ss -l` show nothing. `ss -0` lists
packet sockets (`ss(8)`: "display PACKET sockets"). *Ask:* did the audit of a host's listeners include packet sockets
and the programs attached to them, or only TCP and UDP ports?

**27. Command and control can ride an expected protocol.** Traffic over DNS or HTTPS to a plausible name looks like
normal use. *Ask:* does the environment restrict egress to an allow-list of destinations the work needs, and does it
log what leaves, or is "outbound HTTPS" treated as safe?

## Reviewing the neighbors of a finding

**28. Variant analysis: look for the same mistake elsewhere.** When one instance of a bug class is confirmed, the same
pattern often exists in other places: a copied block, a sibling route, another caller of the same helper. A review that
stops at the first instance leaves the rest.
*Ask:* after each confirmed finding, was the code searched for the same pattern (same call, same missing check, same
unsafe default), and are the other instances listed, fixed or ruled out?

## Sources

Primary sources, each linked in its entry: arXiv 2609.18460; arXiv 2608.27800 (ContextLeak); arXiv 2607.07433
(HalluSquatting); GitHub's npm 12 changelog (2026-07-08); Meta's Muse security write-up; Anthropic's NIST submission
(sandboxing, least privilege) and Zero Trust guide (least agency; excerpt verified only). Claims marked UNVERIFIED came from secondary reports whose primary sources were
not located; they are kept as leads, not evidence.
Entries 12 to 28 were added after comparing this catalog with public security-audit skills for coding agents:
[garrytan/gstack](https://github.com/garrytan/gstack) (its `/cso` skill, MIT), Cloudflare's
[security-audit-skill](https://github.com/cloudflare/security-audit-skill) (MIT), and the public skills from
[Trail of Bits](https://github.com/trailofbits/skills) (CC-BY-SA-4.0), which also supplied the variant-analysis practice
in entry 28. Ideas only: no text or code was copied from any of them. Further primary sources are linked in the entries
(RFC 8725, RFC 8659, RFC 6962, CWE-295, and the GitHub, MCP and Claude Code documentation pages).
Entries marked *measured*: one operator's machines, 2026-08 to 2026-10; the method for each is in the
[rivendale/hsi-operator](https://github.com/rivendale/hsi-operator) docs and the
[rivendale/opensource](https://github.com/rivendale/opensource/tree/main/tools/web) `tools/web` tests.
