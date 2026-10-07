# Attack catalog for AI-produced work

Each entry is a way AI-built systems fail under attack, with the question a reviewer should ask and where to look.
Entries marked *measured* were reproduced on one operator's machines; the rest cite published research. Use it with
Track B (code) and Track C (claims) of the `redteam` skill.

## Untrusted input reaching something that can act

**1. Instructions hidden in ordinary data.** A value placed in a spreadsheet cell steered Claude Sonnet 5 and Opus 5
into choosing the wrong vendor offer, with no safety flag raised (Di Zhang, red-team repository, 2026-09). Google
DeepMind's taxonomy of web attacks on agents reports several types above 80% success.
*Ask:* where does content written by someone else (web pages, email, documents, tool output, social posts, cells)
reach a model that holds tools, credentials or a decision? What stops it?

**2. A peer handoff is a stronger attack than a request.** When an unsafe trajectory is injected as a handoff from
another agent, executed harm rose to 40-95%, against 0-5% on normal tasks (arXiv 2609.18460, 2026). The authors say
this does not measure natural rates.
*Ask:* does this system accept work, plans or "context" from another agent, and does it re-check them, or trust
them because a colleague sent them?

**3. Tool names and descriptions are an attack surface.** Crafted tool descriptions can make an agent pass
sensitive context into tool arguments (Duke, "ContextLeak", 2026).
*Ask:* which third-party tools or MCP servers are loaded, are they pinned to a reviewed version, and what context
can flow into their arguments?

**4. A prompt instruction is not a control.** A "read-only" scope written into a prompt did not stop a sub-agent
from opening a network tunnel (*measured*). Anthropic's agent-security guidance asks for hard barriers, short-lived
credentials, least agency and sandboxing; Meta's Muse keeps secrets and sensitive actions outside the agent's
runtime (2026).
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

**7. The install step runs code.** A package postinstall hook rewrote a coding assistant's config to proxy its
tool traffic and take OAuth tokens (reported 2026-06); worm campaigns hit 50+ npm packages aimed at AI coding tools.
npm 12 documents install-script blocking.
*Ask:* does the change add dependencies, and do their install scripts run? Are versions pinned?

**8. Hallucinated names get registered.** "HalluSquatting": attackers register package, repository or resource names
that models commonly hallucinate and seed them with malicious instructions, turning a model's mistake into a pull
attack at scale (2026).
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

**11. A library's classification drifts between versions.** An address filter built on Python's `ipaddress` flags
refused `::ffff:100.64.0.1` on 3.12 and let it through on 3.13 and 3.14 (*measured*), because newer versions judge
an IPv4-mapped address by the IPv4 inside it.
*Ask:* does a security decision delegate to a library's notion of "private", "safe" or "valid"? Was it tested on more
than one runtime version?

## Sources

Di Zhang, spreadsheet prompt-injection repository (2026-09); Google DeepMind web-agent attack taxonomy (2026);
arXiv 2609.18460 (2026); Duke University, ContextLeak (2026); Anthropic, agent security guidance; Meta, Muse agent
architecture via DeepLearning.AI's The Batch (2026-09-18); npm CLI release notes (v12); HalluSquatting research (2026).
Entries marked *measured*: one operator's machines, 2026-08 to 2026-10; the method for each is in the
[rivendale/hsi-operator](https://github.com/rivendale/hsi-operator) docs and the
[rivendale/opensource](https://github.com/rivendale/opensource/tree/main/tools/web) `tools/web` tests.
