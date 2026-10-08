#!/usr/bin/env python3
"""Scan a results folder for things that must never be published: private keys, common token shapes, and the
operator's own home paths. Every file is scanned (reports, prompts, READMEs, usage files), not only reports.
usage: scan_secrets.py DIR. exit 1 on any hit (each printed as file and pattern name, never the matched value).

A match whose exact text already appears in a committed eval case (evals/cases) is a public fixture value, such as a
placeholder key a case plants on purpose. It is listed as "fixture value" and is not a hit."""
import pathlib, re, sys
CASES = pathlib.Path(__file__).resolve().parent.parent / "cases"
FIXTURE_TEXT = "\n".join(f.read_text(errors="replace") for f in CASES.rglob("*") if f.is_file()) if CASES.exists() else ""
PATTERNS = {
    # a key BODY after the header; the header alone is how reports quote the pattern
    # a key BODY after the header, joined by a real newline, an escaped "\\n" (JSON) or plain spaces; the header
    # alone is how reports quote the pattern
    "private key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----(?:\s|\\+[nr])*[A-Za-z0-9+/=]{40,}",
    "github token": r"\bgh[pousr]_[A-Za-z0-9]{30,}\b",
    "openai-style key": r"\bsk-[A-Za-z0-9_-]{20,}\b",
    "anthropic key": r"\bsk-ant-[A-Za-z0-9_-]{20,}\b",
    "xai key": r"\bxai-[A-Za-z0-9]{20,}\b",
    "aws access key": r"\bAKIA[0-9A-Z]{16}\b",
    "slack token": r"\bxox[abpr]-[A-Za-z0-9-]{10,}\b",
    "bearer token": r"(?i)\bbearer\s+[A-Za-z0-9._-]{30,}",
    "home path": r"/home/[a-z_][a-z0-9_-]*/|C:\\{1,2}Users\\{1,2}[^\\\s]+",
}
hits = fixtures = 0
for f in sorted(p for p in pathlib.Path(sys.argv[1]).rglob("*") if p.is_file() and p.name != "SHA256SUMS"):
    t = f.read_text(errors="replace")
    for name, rx in PATTERNS.items():
        found = {m.group(0) for m in re.finditer(rx, t)}
        if not found:
            continue
        if name not in ("home path", "private key") and all(v in FIXTURE_TEXT for v in found):
            print(f"{f}: {name} (fixture value, public)"); fixtures += 1
        else:
            print(f"{f}: {name}"); hits += 1
print(f"scan: {hits} hit(s), {fixtures} fixture value(s)")
sys.exit(1 if hits else 0)
