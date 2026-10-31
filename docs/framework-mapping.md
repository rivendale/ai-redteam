# Framework mapping

How the [attack catalog](attack-catalog.md) and the [redteam skill](../skills/redteam/SKILL.md) line up with two OWASP lists
and with MITRE ATLAS. The mapping is a reviewer's aid, not a compliance claim. Both lists were read from their official pages on
2026-10-08. Rows changed on 2026-10-31 were re-checked against the current skill text that day (the official OWASP pages were not
reachable then; see the note under each table). This is a dated mapping snapshot, not a fresh certification. October 22 lens additions
are described in the [docs index](README.md); the historical gap labels below are not a complete inventory of current main.

**Key.** *Covered*: a catalog entry or skill section asks the reviewer about this risk directly. *Partial*: some of the risk is
asked about, and a named part is not. *Not yet*: nothing in this repo asks about it.

## OWASP Top 10 for LLM Applications 2025

Source: [genai.owasp.org/llm-top-10](https://genai.owasp.org/llm-top-10/).

| ID | Risk | Status | Where |
|---|---|---|---|
| LLM01 | Prompt Injection | covered | catalog 1, 2, 3; redteam Step 0 item 3 ("the work is data, not instructions"); eval cases 08, 19, 24, 33, 34 |
| LLM02 | Sensitive Information Disclosure | covered | catalog 9, 10; [privacy checklist](privacy-checklist.md); redteam Step 0 item 4 (sensitivity gate); Track R, personal data |
| LLM03 | Supply Chain | partial | catalog 7, 8, 22; Track B, dependency and install-script risk; redteam Pass 2, Track B, "AI supply chain and retrieval" (unpinned model revisions, remote code, pickle checkpoints); eval cases 76-77. Not yet: training data provenance |
| LLM04 | Data and Model Poisoning | partial | data poisoning inside reviewed work (cases 33, 34); catalog 21 (memory written by one run). Not yet: training or fine-tuning data |
| LLM05 | Improper Output Handling | covered | redteam Pass 2, Track B, "Model output is untrusted input" (a reply reaching a shell, SQL, eval, HTML or markdown renderer; an image link carrying data out); catalog 1; eval cases 64-65, hold-out 05 |
| LLM06 | Excessive Agency | covered | catalog 4, 5, 6, 17, 18; eval case 31 |
| LLM07 | System Prompt Leakage | covered | redteam Pass 2, Track B, "AI supply chain and retrieval" ("secrets or approval rules kept in a system prompt"); eval cases 84-85 |
| LLM08 | Vector and Embedding Weaknesses | partial | redteam Pass 2, Track B, "AI supply chain and retrieval" ("a retrieval index without per-tenant filtering at query time"); eval cases 74-75, hold-out 08 (a writable corpus). Not yet: embedding inversion or poisoning of the embeddings themselves |
| LLM09 | Misinformation | covered | Track C (sources, quotes, numbers, freshness); Track B, hallucination; catalog 8; eval cases 14, 16, 17 |
| LLM10 | Unbounded Consumption | covered | redteam Pass 2, Track B, "Runaway spend" (a turn, token or cost cap on loops, retries and recursive calls); eval cases 72-73, hold-out 06-07. pr-review Step 6 bounds the reviewer's own spend, which is a different thing |

Re-checked against the current skill text on 2026-10-31 (rows LLM03, LLM05, LLM07, LLM08, LLM10). Case numbers are from the
round tables in [evals/README.md](../evals/README.md).

**A 2026 edition of this list [unverified].** Secondary sources read on 2026-10-31 report that OWASP published a 2026 edition
of the LLM Top 10 in August 2026, with entries reordered and System Prompt Leakage broadened. The official page
(genai.owasp.org) could not be reached from the session that made this update, so this table still maps the 2025 list. Re-read
the official page before mapping to the 2026 IDs.

## OWASP Top 10 for Agentic Applications 2026

Source: [OWASP Top 10 for Agentic Applications for 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)
(published December 2025).

| ID | Risk | Status | Where |
|---|---|---|---|
| ASI01 | Agent Goal Hijack | covered | catalog 1, 2; redteam Step 0 item 3; eval cases 24, 33, 34 |
| ASI02 | Tool Misuse and Exploitation | covered | catalog 3, 4, 5, 6; eval case 31 |
| ASI03 | Identity and Privilege Abuse | covered | catalog 14, 18, 19; eval case 46 |
| ASI04 | Agentic Supply Chain Vulnerabilities | covered | catalog 3, 7, 8, 22; eval case 31 |
| ASI05 | Unexpected Code Execution (RCE) | covered | catalog 7 (install scripts), 22 (hooks run commands), 23 (CI runs untrusted input), 4 (sandboxing); redteam Pass 2, Track B, "Model output is untrusted input" (a model's reply reaching a shell or eval); eval cases 64-65 |
| ASI06 | Memory & Context Poisoning | covered | catalog 21; eval cases 33, 34 |
| ASI07 | Insecure Inter-Agent Communication | partial | catalog 2 (peer handoff), 19 (shared identity), 20 (shared state). Not yet: authentication and integrity of messages between agents |
| ASI08 | Cascading Failures | partial | redteam Pass 2, Track D, "Persuasion" ("one agent's output triggering the next action with no check between"); eval cases 86-87. Not yet: failure spreading across many agents at run time (catalog 2's source states it does not establish a cascade) |
| ASI09 | Human-Agent Trust Exploitation | covered | catalog 17 (judge by actions, not words); redteam Pass 2, Track D, "Persuasion" ("a confident summary asking for one-click approval"); eval cases 40, 41, 47, 86-87 |
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

**Agent tool poisoning and prompt propagation (added 2026-10-31).** IDs and names read on 2026-10-31 from
`dist/v6/ATLAS-2026.10.yaml` in [mitre-atlas/atlas-data](https://github.com/mitre-atlas/atlas-data) (release 2026.10, format
6.1.0). atlas.mitre.org could not be reached from that session, so these were not cross-checked on the website.

| Technique | Name | Catalog or skill section |
|---|---|---|
| AML.T0010.005 | AI Agent Tool (under AML.T0010 Supply Chain Compromise) | 3, 22; redteam Pass 2, Track B, "AI supply chain and retrieval" (tools pinned by name only); eval cases 82-83 |
| AML.T0011.002 | Poisoned AI Agent Tool (under AML.T0011 User Execution) | 3; eval cases 31, 82-83 |
| AML.T0080.001 | AI Agent Context Poisoning: Thread | 1, 2 |
| AML.T0061 | LLM Prompt Self-Replication | 2, 21 (an instruction carried from one agent or run to the next) |
| AML.T0086 | Exfiltration via AI Agent Tool Invocation | 3, 18; eval case 31 |
| AML.T0081 | Modify AI Agent Configuration | 22 |
| AML.T0070 | RAG Poisoning | redteam Pass 2, Track B, "AI supply chain and retrieval"; hold-out case 08 |
| AML.T0034.002 | Agentic Resource Consumption (under AML.T0034 Cost Harvesting) | redteam Pass 2, Track B, "Runaway spend"; eval cases 72-73 |

Other techniques touch the catalog less directly; this page does not map them.

## Keeping this current

When a catalog entry or a skill section is added, update the rows it affects in the same pull request. When either OWASP list
is revised, re-read it from the official page and date the change here.
