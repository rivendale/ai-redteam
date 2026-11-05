# PR #112: test negative zoom; hash-checked installs for agents

Head e61d0b3, merge base 93ac2f7.

Adds a test for the negative-zoom check `parse_key` already has. The agent notes now allow installs only from the hash-checked lock file, tell agents without network to ask for the matching wheel bundle, and tell agents to stop instead of fetching.
Tests pass.
