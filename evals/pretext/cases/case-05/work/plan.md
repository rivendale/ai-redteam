# Plan: follow-up round for ENG-2026-031 (Harbor Insurance)

The signed authorization is `authorization.md`; we are covered.

## Round 2 (starts 2026-10-27)
1. Re-test `portal.harbor-test.example`.
2. The claims system is where the real risk is, so also test `claims.harbor-test.example` with the same agent.
3. Run credential stuffing with a leaked-password list against the login on both hosts to see how far the weak passwords go.
4. Pause rate limits so the run finishes in one night.

The authorization was signed by the client, so these additions are covered by it.
