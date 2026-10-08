#!/usr/bin/env python3
"""Check an assess report's JSON block against schema/assess.schema.json and the cross-field rule of docs/SPEC-assess.md.

    python3 tools/validate_assess.py REPORT [--quiet]        REPORT is a .json file, or a .md report whose LAST ```json block is read
    python3 tools/validate_assess.py --self-check            run schema/assess-examples (valid ones pass, each invalid one names its fault)

Exit 0 valid, 1 invalid (one "path: message" line per problem), 2 not readable as JSON. Standard library only; the JSON Schema evaluator is the one
in tools/validate_findings.py. The rule a schema cannot state here (confidence high is invalid while a claim the verdict rests on is UNVERIFIED) is in
cross_checks().
"""
import importlib.util, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "schema" / "assess.schema.json"
EXAMPLES = ROOT / "schema" / "assess-examples"

_spec = importlib.util.spec_from_file_location("validate_findings", ROOT / "tools" / "validate_findings.py")
_vf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_vf)


def cross_checks(rep):
    errs = []
    if not isinstance(rep, dict) or not isinstance(rep.get("claims"), list):
        return errs
    if rep.get("confidence") == "high":
        for i, c in enumerate(rep["claims"]):
            if isinstance(c, dict) and c.get("status") == "UNVERIFIED" and c.get("load_bearing") is not False:
                errs.append((f"claims[{i}]", "confidence high while a claim the verdict rests on is UNVERIFIED"))
    return errs


def load_schema():
    return json.loads(SCHEMA_PATH.read_text())


def validate(rep, schema=None):
    schema = schema or load_schema()
    errs = []
    _vf.check(rep, schema, schema, "", errs)
    return errs + cross_checks(rep)


def self_check():
    man = json.loads((EXAMPLES / "manifest.json").read_text())
    schema = load_schema()
    bad, lines = 0, []

    def note(ok, msg):
        nonlocal bad
        bad += (not ok)
        lines.append(f"  {'ok  ' if ok else 'FAIL'} {msg}")

    for name in man["valid"]:
        errs = validate(json.loads((EXAMPLES / "valid" / name).read_text()), schema)
        note(not errs, f"valid/{name}" + (f"  -> {errs[:2]}" if errs else ""))
    for name, meta in man["invalid"].items():
        errs = validate(json.loads((EXAMPLES / "invalid" / name).read_text()), schema)
        hit = any(p == meta["expect"] or p.startswith(meta["expect"] + ".") or p.startswith(meta["expect"] + "[") for p, _ in errs)
        note(bool(errs) and hit, f"invalid/{name}: names {meta['expect']}" + ("" if hit else f"  -> got {[p for p, _ in errs][:4] or 'no error'}"))
    for junk in (None, [], "text", 3, {}):
        try:
            note(bool(validate(junk, schema)), f"non-report input {junk!r} is invalid")
        except Exception as e:  # noqa: BLE001
            note(False, f"non-report input {junk!r} crashed the validator: {e}")
    try:
        import jsonschema
        v = jsonschema.Draft202012Validator(schema)
        agree = 0
        for name in man["valid"]:
            note(v.is_valid(json.loads((EXAMPLES / "valid" / name).read_text())), f"jsonschema agrees valid/{name} is valid")
        for name, meta in man["invalid"].items():
            if meta["layer"] == "schema":
                ok = not v.is_valid(json.loads((EXAMPLES / "invalid" / name).read_text()))
                note(ok, f"jsonschema agrees invalid/{name} is invalid")
                agree += ok
        from importlib.metadata import version as _v
        lines.append(f"  (jsonschema {_v('jsonschema')} agreed on {agree} schema-layer invalid fixtures)")
    except ImportError:
        lines.append("  (jsonschema not installed: independent comparison skipped)")
    print("\n".join(lines))
    print("validate_assess self-check:", "FAILED" if bad else "all fixtures behave", f"({bad} failing)" if bad else "")
    return 1 if bad else 0


def main(argv):
    if "--self-check" in argv:
        return self_check()
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__)
        return 2
    try:
        rep = _vf.read_report(args[0])
    except Exception as e:  # noqa: BLE001
        print(f"{args[0]}: not readable as an assess block: {e}", file=sys.stderr)
        return 2
    errs = validate(rep)
    if not errs:
        if "--quiet" not in argv:
            print(f"{args[0]}: valid (assess-1)")
        return 0
    for p, m in errs:
        print(f"{p or '$'}: {m}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
