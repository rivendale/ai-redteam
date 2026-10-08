# Framework mapping

How the [attack catalog](attack-catalog.md) and the [redteam skill](../skills/redteam/SKILL.md) line up with two OWASP lists
and with MITRE ATLAS. The mapping is a reviewer's aid, not a compliance claim. Both lists were read from their official pages on
2026-10-08.

**Key.** *Covered*: a catalog entry or skill section asks the reviewer about this risk directly. *Partial*: some of the risk is
asked about, and a named part is not. *Not yet*: nothing in this repo asks about it.

## OWASP Top 10 for LLM Applications 2025

Source: [genai.owasp.org/llm-top-10](https://genai.owasp.org/llm-top-10/).

| ID | Risk | Status | Where |
|---|---|---|---|
| LLM01 | Prompt Injection | covered | catalog 1, 2, 3; redteam Step 0 item 3 ("the work is data, not instructions"); eval cases 08, 19, 24, 33, 34 |
| LLM02 | Sensitive Information Disclosure | covered | catalog 9, 10; [privacy checklist](privacy-checklist.md); redteam Step 0 item 4 (sensitivity gate); Track R, personal data |
| LLM03 | Supply Chain | partial | catalog 7, 8, 22; Track B, dependency and install-script risk. Not yet: model weights, adapters and training data provenance |
| LLM04 | Data and Model Poisoning | partial | data poisoning inside reviewed work (cases 33, 34); catalog 21 (memory written by one run). Not yet: training or fine-tuning data |
| LLM05 | Improper Output Handling | partial | Track B, "untrusted input reaching sensitive sinks"; catalog 1. Not yet: an entry on model output rendered as HTML, SQL or shell |
| LLM06 | Excessive Agency | covered | catalog 4, 5, 6, 17, 18; eval case 31 |
| LLM07 | System Prompt Leakage | not yet | no catalog entry or skill question |
| LLM08 | Vector and Embedding Weaknesses | not yet | no catalog entry on retrieval stores, embeddings or access control in RAG |
| LLM09 | Misinformation | covered | Track C (sources, quotes, numbers, freshness); Track B, hallucination; catalog 8; eval cases 14, 16, 17 |
| LLM10 | Unbounded Consumption | not yet | Track B asks about 10x and 100x load, but nothing asks about cost, rate or token limits. pr-review Step 6 bounds the reviewer's own spend, which is a different thing |

## OWASP Top 10 for Agentic Applications 2026

Source: [OWASP Top 10 for Agentic Applications for 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)
(published December 2025).

| ID | Risk | Status | Where |
|---|---|---|---|
| ASI01 | Agent Goal Hijack | covered | catalog 1, 2; redteam Step 0 item 3; eval cases 24, 33, 34 |
| ASI02 | Tool Misuse and Exploitation | covered | catalog 3, 4, 5, 6; eval case 31 |
| ASI03 | Identity and Privilege Abuse | covered | catalog 14, 18, 19; eval case 46 |
| ASI04 | Agentic Supply Chain Vulnerabilities | covered | catalog 3, 7, 8, 22; eval case 31 |
| ASI05 | Unexpected Code Execution (RCE) | partial | catalog 7 (install scripts), 22 (hooks run commands), 23 (CI runs untrusted input), 4 (sandboxing). Not yet: agent-written code run without a sandbox |
| ASI06 | Memory & Context Poisoning | covered | catalog 21; eval cases 33, 34 |
| ASI07 | Insecure Inter-Agent Communication | partial | catalog 2 (peer handoff), 19 (shared identity), 20 (shared state). Not yet: authentication and integrity of messages between agents |
| ASI08 | Cascading Failures | not yet | catalog 2's source states it does not establish a cascade; nothing else asks about failure spreading between agents |
| ASI09 | Human-Agent Trust Exploitation | partial | catalog 17 (judge by actions, not words); eval cases 40, 41, 47. Not yet: an agent persuading a person to approve a harmful action |
| ASI10 | Rogue Agents | partial | catalog 17, 19 (revoke one agent alone); eval case 47. Not yet: detecting drift in an agent no attacker controls |

## MITRE ATLAS

ATLAS techniques overlap the entries above. The clear matches, with names as of ATLAS data release 2026.09
([mitre-atlas/atlas-data](https://github.com/mitre-atlas/atlas-data), `dist/v6/ATLAS-2026.09.yaml`; browse at
[atlas.mitre.org](https://atlas.mitre.org/)):

| Technique | Name | Catalog |
|---|---|---|
| AML.T0051 | LLM Prompt Injection (direct, indirect, triggered) | 1, 2 |
| AML.T0053 | AI Agent Tool Invocation | 3, 4, 18 |
| AML.T0060 | Publish Hallucinated Entities | 8 |
| AML.T0080 | AI Agent Context Poisoning (sub-technique .000 Memory) | 21 |

Other techniques touch the catalog less directly; this page does not map them.

## Keeping this current

When a catalog entry or a skill section is added, update the rows it affects in the same pull request. When either OWASP list
is revised, re-read it from the official page and date the change here.
