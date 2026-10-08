#!/usr/bin/env python3
"""Scan review reports for things that must never be published: private keys, common token shapes, and the
operator's own home paths. usage: scan_secrets.py DIR. exit 1 on any hit (each printed as file and pattern name,
never the matched value)."""
import pathlib, re, sys
PATTERNS = {
    "private key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    "github token": r"\bgh[pousr]_[A-Za-z0-9]{30,}\b",
    "openai-style key": r"\bsk-[A-Za-z0-9_-]{20,}\b",
    "anthropic key": r"\bsk-ant-[A-Za-z0-9_-]{20,}\b",
    "xai key": r"\bxai-[A-Za-z0-9]{20,}\b",
    "aws access key": r"\bAKIA[0-9A-Z]{16}\b",
    "slack token": r"\bxox[abpr]-[A-Za-z0-9-]{10,}\b",
    "bearer token": r"(?i)\bbearer\s+[A-Za-z0-9._-]{30,}",
    "home path": r"/home/[a-z_][a-z0-9_-]*/|C:\\\\Users\\\\[^\\\\\s]+",
}
hits = 0
for f in sorted(pathlib.Path(sys.argv[1]).rglob("case-*.md")):
    t = f.read_text(errors="replace")
    for name, rx in PATTERNS.items():
        if re.search(rx, t):
            print(f"{f}: {name}"); hits += 1
print(f"scan: {hits} hit(s)")
sys.exit(1 if hits else 0)
