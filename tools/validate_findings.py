#!/usr/bin/env python3
"""Check a redteam / pr-review findings block against schema/findings.schema.json and the cross-field rules of the v2.2 and v2.3 specs.

    python3 tools/validate_findings.py REPORT [--quiet]        REPORT is a .json file, or a .md report whose LAST ```json block is read
    python3 tools/validate_findings.py --self-check            run schema/examples (valid ones pass, each invalid one names its fault)

Exit 0 valid, 1 invalid (one "path: message" line per problem), 2 not readable as JSON. Standard library only. The schema part is a
small JSON Schema evaluator (type, enum, const, required, properties, additionalProperties, items, minItems, minLength, allOf, anyOf,
if/then, not, local $ref), which is all findings.schema.json uses; --self-check compares it with the `jsonschema` package when that is
installed. Cross-field rules, which a schema cannot state, are in cross_checks().
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "schema" / "findings.schema.json"
SEV = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}


# ------------------------------------------------------------------------------------------------ JSON Schema subset
def _type_ok(v, t):
    return {"object": isinstance(v, dict), "array": isinstance(v, list), "string": isinstance(v, str),
            "boolean": isinstance(v, bool), "number": isinstance(v, (int, float)) and not isinstance(v, bool),
            "integer": isinstance(v, int) and not isinstance(v, bool)}[t]


def _resolve(ref, root):
    node = root
    for part in ref.lstrip("#/").split("/"):
        node = node[part]
    return node


def check(node, schema, root, path, errs):
    """Append (path, message) to errs for every way NODE fails SCHEMA. Returns True when it passed."""
    n0 = len(errs)
    if "$ref" in schema:
        check(node, _resolve(schema["$ref"], root), root, path, errs)
    if "type" in schema and not _type_ok(node, schema["type"]):
        errs.append((path, f"expected {schema['type']}"))
        return False
    if "const" in schema and (node != schema["const"] or type(node) is not type(schema["const"])):
        errs.append((path, f"must be {json.dumps(schema['const'])}"))
    if "enum" in schema and node not in schema["enum"]:
        errs.append((path, f"must be one of {schema['enum']}"))
    if isinstance(node, str) and "minLength" in schema and len(node) < schema["minLength"]:
        errs.append((path, f"shorter than {schema['minLength']} characters"))
    if isinstance(node, list):
        if "minItems" in schema and len(node) < schema["minItems"]:
            errs.append((path, f"needs at least {schema['minItems']} item(s)"))
        if "items" in schema:
            for i, x in enumerate(node):
                check(x, schema["items"], root, f"{path}[{i}]", errs)
    if isinstance(node, dict):
        for k in schema.get("required", []):
            if k not in node:
                errs.append((f"{path}.{k}" if path else k, "missing required property"))
        props = schema.get("properties", {})
        for k, sub in props.items():
            if k in node:
                check(node[k], sub, root, f"{path}.{k}" if path else k, errs)
        if schema.get("additionalProperties") is False:
            for k in node:
                if k not in props:
                    errs.append((f"{path}.{k}" if path else k, "property not allowed"))
    for sub in schema.get("allOf", []):
        check(node, sub, root, path, errs)
    if "anyOf" in schema:
        if not any(check(node, sub, root, path, []) for sub in schema["anyOf"]):
            errs.append((path, "matches none of the allowed alternatives"))
    if "if" in schema and check(node, schema["if"], root, path, []) and "then" in schema:
        check(node, schema["then"], root, path, errs)
    if "not" in schema and check(node, schema["not"], root, path, []):
        errs.append((path, "has a property that is not allowed here"))
    return len(errs) == n0


# ------------------------------------------------------------------------------------------------ cross-field rules
def cross_checks(rep):
    errs = []
    if not isinstance(rep, dict):
        return errs
    fs = rep.get("findings") if isinstance(rep.get("findings"), list) else []
    ref = rep.get("refuted") if isinstance(rep.get("refuted"), list) else []
    confirmed = [(i, f) for i, f in enumerate(fs) if isinstance(f, dict) and f.get("status") == "confirmed"]
    sevs = [SEV.get(f.get("severity"), 0) for _, f in confirmed]
    verdict = rep.get("verdict")
    if verdict == "SHIP" and any(s >= SEV["High"] for s in sevs):
        errs.append(("verdict", "SHIP with an open confirmed Critical or High finding"))
    if verdict == "SHIP WITH FIXES" and any(s >= SEV["Critical"] for s in sevs):
        errs.append(("verdict", "SHIP WITH FIXES with an open confirmed Critical finding"))
    if verdict in ("REWORK", "REJECT") and not any(s >= SEV["Medium"] for s in sevs):
        errs.append(("verdict", f"{verdict} needs at least one confirmed finding of Medium or above; needs_validation items never set the verdict"))
    seen = {}
    for i, f in enumerate(fs):
        if isinstance(f, dict) and isinstance(f.get("id"), str):
            if f["id"] in seen:
                errs.append((f"findings[{i}].id", f"duplicate id {f['id']!r} (also findings[{seen[f['id']]}])"))
            seen.setdefault(f["id"], i)
    for j, r in enumerate(ref):
        if isinstance(r, dict) and isinstance(r.get("id"), str) and r["id"] in seen:
            errs.append((f"refuted[{j}].id", f"id {r['id']!r} is also in findings: a refuted candidate must leave findings"))
    return errs


# ------------------------------------------------------------------------------------------------ public API
def load_schema():
    return json.loads(SCHEMA_PATH.read_text())


def validate(rep, schema=None):
    """List of (path, message). Empty means valid."""
    schema = schema or load_schema()
    errs = []
    check(rep, schema, schema, "", errs)
    return errs + cross_checks(rep)


def read_report(path):
    text = pathlib.Path(path).read_text()
    if str(path).endswith(".md"):
        blocks = re.findall(r"```json\s*\n(.*?)```", text, re.S)
        if not blocks:
            raise ValueError("no ```json block in the report")
        text = blocks[-1]
    return json.loads(text)


# ------------------------------------------------------------------------------------------------ self-check
def self_check():
    ex = ROOT / "schema" / "examples"
    man = json.loads((ex / "manifest.json").read_text())
    schema = load_schema()
    bad, lines = 0, []

    def note(ok, msg):
        nonlocal bad
        bad += (not ok)
        lines.append(f"  {'ok  ' if ok else 'FAIL'} {msg}")

    for name in man["valid"]:
        errs = validate(json.loads((ex / "valid" / name).read_text()), schema)
        note(not errs, f"valid/{name}" + (f"  -> {errs[:2]}" if errs else ""))
    for name, meta in man["invalid"].items():
        errs = validate(json.loads((ex / "invalid" / name).read_text()), schema)
        hit = any(p == meta["expect"] or p.startswith(meta["expect"] + ".") or p.startswith(meta["expect"] + "[") for p, _ in errs)
        note(bool(errs) and hit, f"invalid/{name}: names {meta['expect']}" + ("" if hit else f"  -> got {[p for p, _ in errs][:4] or 'no error'}"))
    # a garbage input must be an error, not a crash
    for junk in (None, [], "text", 3, {}):
        try:
            note(bool(validate(junk, schema)), f"non-report input {junk!r} is invalid")
        except Exception as e:  # noqa: BLE001
            note(False, f"non-report input {junk!r} crashed the validator: {e}")
    try:  # independent check: the jsonschema package, where installed, must agree on every schema-layer fixture
        import jsonschema
        v = jsonschema.Draft202012Validator(schema)
        agree = 0
        for name in man["valid"]:
            ok = v.is_valid(json.loads((ex / "valid" / name).read_text()))
            note(ok, f"jsonschema agrees valid/{name} is valid")
        for name, meta in man["invalid"].items():
            if meta["layer"] == "schema":
                ok = not v.is_valid(json.loads((ex / "invalid" / name).read_text()))
                note(ok, f"jsonschema agrees invalid/{name} is invalid")
                agree += ok
        from importlib.metadata import version as _v
        lines.append(f"  (jsonschema {_v('jsonschema')} agreed on {agree} schema-layer invalid fixtures)")
    except ImportError:
        lines.append("  (jsonschema not installed: independent comparison skipped)")
    print("\n".join(lines))
    print("validate_findings self-check:", "FAILED" if bad else "all fixtures behave", f"({bad} failing)" if bad else "")
    return 1 if bad else 0


def main(argv):
    if "--self-check" in argv:
        return self_check()
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__)
        return 2
    try:
        rep = read_report(args[0])
    except Exception as e:  # noqa: BLE001
        print(f"{args[0]}: not readable as a findings block: {e}", file=sys.stderr)
        return 2
    errs = validate(rep)
    if not errs:
        if "--quiet" not in argv:
            print(f"{args[0]}: valid (schema {rep.get('schema_version')})")
        return 0
    for p, m in errs:
        print(f"{p or '$'}: {m}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
