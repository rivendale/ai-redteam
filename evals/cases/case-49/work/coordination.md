# Coordination protocol for the planning agents

Agents A and B write sections of one shared file, shared/plan.md. To avoid overwriting each other:
1. Claim your section in shared/claims.json before you edit it.
2. Read shared/plan.md again immediately before you write, and write on top of that version.
3. `write_file` replaces the whole file.
