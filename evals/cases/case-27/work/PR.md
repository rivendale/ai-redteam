# PR #70: harden slugify
Head 9d4e1a7, merge base c82f0b3.

Output is lowercase a-z, 0-9 and single hyphens, at most 80 characters, never starting or ending with a hyphen. Letters outside
a-z are dropped, not transliterated (stated in the docstring and tested). Non-strings raise TypeError. Six tests, all pass.
