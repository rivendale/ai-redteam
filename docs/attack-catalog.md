# Attack catalog for AI-produced work

Each entry is a way AI-built systems fail under attack, with the question a reviewer should ask and where to look.
Entries marked *measured* were reproduced on one operator's machines; the rest cite published research. Use it with
Track B (code) and Track C (claims) of the `redteam` skill.

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
from opening a network tunnel (*measured*). Anthropic's agent-security guidance asks for hard barriers, short-lived
credentials, least agency and sandboxing; Meta describes its Muse architecture as keeping credentials and sensitive
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

## Sources

Primary sources, each linked in its entry: arXiv 2609.18460; arXiv 2608.27800 (ContextLeak); arXiv 2607.07433
(HalluSquatting); GitHub's npm 12 changelog (2026-07-08); Meta's Muse security write-up; Anthropic's agent-security
guidance (sandboxing, least privilege). Claims marked UNVERIFIED came from secondary reports whose primary sources were
not located; they are kept as leads, not evidence.
Entries marked *measured*: one operator's machines, 2026-08 to 2026-10; the method for each is in the
[rivendale/hsi-operator](https://github.com/rivendale/hsi-operator) docs and the
[rivendale/opensource](https://github.com/rivendale/opensource/tree/main/tools/web) `tools/web` tests.
