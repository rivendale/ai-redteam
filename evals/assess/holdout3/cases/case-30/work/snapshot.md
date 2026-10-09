# loudness-table

Reads a log of loudness measurements (one line per episode: name, loudness before, loudness after, in LUFS) and prints a markdown table of every episode with the difference of the AFTER value from the
target, flagging any episode more than 1 LU away. It reads a file you give it and prints to the terminal; no network, no telemetry. It does not change any audio.
Install: copy the one Python file from the release commit `2d7a91c4e08b35f6a1c9d4720e5b83f1a6c0d947`. License: Apache-2.0. Last release v0.4.0 (2026-09-23).
