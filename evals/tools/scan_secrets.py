#!/usr/bin/env python3
"""Scan a results folder for things that must never be published: private keys, common token shapes, and the
operator's own home paths. Every file is scanned (reports, prompts, READMEs, usage files), not only reports.
usage: scan_secrets.py DIR. exit 1 on any hit (each printed as file and pattern name, never the matched value).

A match whose exact text already appears in a committed eval case (evals/cases) is a public fixture value, such as a
placeholder key a case plants on purpose. It is listed as "fixture value" and is not a hit."""
import pathlib, re, sys
EVALS = pathlib.Path(__file__).resolve().parent.parent
CASE_DIRS = [EVALS / "cases"] + sorted(EVALS.glob("*/cases"))
FIXTURE_TEXT = "\n".join(f.read_text(errors="replace") for c in CASE_DIRS if c.exists() for f in c.rglob("*") if f.is_file())
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
    # key-shaped hex, matched by position so ordinary digests and commit hashes are not hits; a body made of one short unit repeated
    # (dead dead dead ..., 0000 ...) is an obvious placeholder and is skipped below
    "wallet private key": r"(?i)\b(?:Wallet|PrivateKey|privateKeyToAccount|from_?key|from_?(?:private|secret)_?key)\s*\(\s*[\"']?(?:0x)?[0-9a-f]{64}\b|(?:private[_ -]?key|secret[_ -]?key)\w*[\"']?\s*[:=]\s*[\"']?(?:0x)?[0-9a-f]{64}\b",
    # sign-in tokens: a JWT (three base64url parts, the first two start with eyJ) and the OAuth token fields a Codex or CLI login stores
    "jwt": r"\beyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}",
    "oauth token field": r"(?i)[\"'](?:access|refresh|id)_token[\"']\s*:\s*[\"'][A-Za-z0-9._~+/=-]{20,}[\"']",
    "rpc url key": r"(?i)/v[0-9]/[0-9a-f]{32}\b",
    "home path": r"/home/[a-z_][a-z0-9_-]*/|C:\\{1,2}Users\\{1,2}[^\\\s]+",
}
hits = fixtures = 0
for f in sorted(p for p in pathlib.Path(sys.argv[1]).rglob("*") if p.is_file() and p.name != "SHA256SUMS"):
    t = f.read_text(errors="replace")
    for name, rx in PATTERNS.items():
        found = {m.group(0) for m in re.finditer(rx, t)}
        if name in ("wallet private key", "rpc url key"):
            found = {v for v in found if not re.fullmatch(r"(.{1,4}?)\1+", re.search(r"[0-9a-fA-F]{32,64}\b", v).group(0).lower())}
        if not found:
            continue
        if name not in ("home path", "private key", "wallet private key", "rpc url key", "jwt", "oauth token field") and all(v in FIXTURE_TEXT for v in found):
            print(f"{f}: {name} (fixture value, public)"); fixtures += 1
        else:
            print(f"{f}: {name}"); hits += 1
print(f"scan: {hits} hit(s), {fixtures} fixture value(s)")
sys.exit(1 if hits else 0)
