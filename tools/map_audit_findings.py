#!/usr/bin/env python3
"""Convert a Cloudflare security-audit findings.json array into a schema 2.3 report.

The source field names come from cloudflare/security-audit-skill report-schema.json (MIT).
This tool maps those names onto schema/findings.schema.json. The skill text stays upstream.

    python3 tools/map_audit_findings.py FINDINGS.json

Exit 0 prints a report that tools/validate_findings.py accepts.
Exit 1 means the array cannot be mapped, or the report fails validation.
Exit 2 means the file is not JSON, or the arguments are wrong.
"""
import importlib.util, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
_FINGERPRINT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@+-]*$")
_SCORES = ("informational", "low", "medium", "high", "critical")
_TO_SEVERITY = {"informational": "Low", "low": "Low", "medium": "Medium", "high": "High", "critical": "Critical"}
_SEVERITY_ORDER = ("Critical", "High", "Medium", "Low")
_CONDITION_KINDS = (
    "authentication_level", "authorization_role", "user_interaction", "system_configuration",
    "network_routing", "environmental_dependency", "data_state", "timing_dependency", "third_party_dependency",
)
_CONFIDENCE = ("low", "medium", "high")
_UNRECORDED = {
    "searched": "no sibling search was recorded on the audit record",
    "found": "not recorded",
}
_KEYS = {
    "confirmed": (
        "verdict", "fingerprint", "title", "description", "root_cause", "intended_behavior",
        "trace", "evidence", "conditions", "execution", "remediation", "severity", "confidence",
    ),
    "needs_validation": (
        "verdict", "fingerprint", "title", "description", "claimed_root_cause",
        "trace", "evidence", "blockers", "validation_plan",
    ),
    "rejected": (
        "verdict", "fingerprint", "title", "description", "claimed_root_cause",
        "trace", "evidence", "reason",
    ),
}


class MapError(Exception):
    def __init__(self, path, message):
        self.path = path
        self.message = message
        super().__init__(f"{path}: {message}")


def _load_validate():
    spec = importlib.util.spec_from_file_location("validate_findings", ROOT / "tools" / "validate_findings.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _object(value, path, required, optional=()):
    if not isinstance(value, dict):
        raise MapError(path, "expected an object")
    allowed = set(required) | set(optional)
    for key in required:
        if key not in value:
            raise MapError(f"{path}.{key}", "missing required property")
    for key in value:
        if key not in allowed:
            raise MapError(f"{path}.{key}", "property not allowed")
    return value


def _text(value, path, min_len=1):
    if not isinstance(value, str):
        raise MapError(path, "expected a string")
    text = value.strip()
    if len(text) < min_len:
        raise MapError(path, f"shorter than {min_len} characters")
    return text


def _enum(value, path, choices):
    if value not in choices:
        raise MapError(path, "must be one of " + ", ".join(choices))
    return value


def _array(value, path, min_items=0):
    if not isinstance(value, list):
        raise MapError(path, "expected an array")
    if len(value) < min_items:
        raise MapError(path, f"needs at least {min_items} item(s)")
    return value


def _line(value, path):
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise MapError(path, "must be an integer >= 1")
    return value


def _trace(value, path):
    steps = []
    for i, raw in enumerate(_array(value, path, 1)):
        step_path = f"{path}[{i}]"
        obj = _object(raw, step_path, ("kind", "file", "line", "scope", "description"))
        steps.append({
            "kind": _enum(obj["kind"], f"{step_path}.kind", ("entrypoint", "propagation", "sink")),
            "file": _text(obj["file"], f"{step_path}.file"),
            "line": _line(obj["line"], f"{step_path}.line"),
            "scope": _text(obj["scope"], f"{step_path}.scope"),
            "description": _text(obj["description"], f"{step_path}.description"),
        })
    return steps


def _evidence(value, path):
    rows = []
    for i, raw in enumerate(_array(value, path, 1)):
        row_path = f"{path}[{i}]"
        obj = _object(raw, row_path, ("file", "line", "description"))
        rows.append({
            "file": _text(obj["file"], f"{row_path}.file"),
            "line": _line(obj["line"], f"{row_path}.line"),
            "description": _text(obj["description"], f"{row_path}.description"),
        })
    return rows


def _conditions(value, path):
    rows = []
    for i, raw in enumerate(_array(value, path)):
        row_path = f"{path}[{i}]"
        obj = _object(raw, row_path, ("kind", "description"))
        rows.append({
            "kind": _enum(obj["kind"], f"{row_path}.kind", _CONDITION_KINDS),
            "description": _text(obj["description"], f"{row_path}.description"),
        })
    return rows


def _execution(value, path):
    obj = _object(value, path, ("attacker_perspective", "payloads", "instructions", "observed_result"))
    payloads = []
    for i, item in enumerate(_array(obj["payloads"], f"{path}.payloads", 1)):
        payloads.append(_text(item, f"{path}.payloads[{i}]", 0))
    instructions = []
    for i, item in enumerate(_array(obj["instructions"], f"{path}.instructions", 1)):
        instructions.append(_text(item, f"{path}.instructions[{i}]"))
    return {
        "attacker_perspective": _text(obj["attacker_perspective"], f"{path}.attacker_perspective"),
        "payloads": payloads,
        "instructions": instructions,
        "observed_result": _text(obj["observed_result"], f"{path}.observed_result"),
    }


def _remediation(value, path):
    obj = _object(value, path, ("strategy",), ("code_changes",))
    changes = []
    if "code_changes" in obj:
        for i, raw in enumerate(_array(obj["code_changes"], f"{path}.code_changes")):
            change_path = f"{path}.code_changes[{i}]"
            change = _object(raw, change_path, ("file_name", "fixed_code"))
            changes.append(_text(change["file_name"], f"{change_path}.file_name"))
            _text(change["fixed_code"], f"{change_path}.fixed_code", 0)
    return {"strategy": _text(obj["strategy"], f"{path}.strategy"), "files": changes}


def _score_box(value, path, choices):
    obj = _object(value, path, ("score", "reason"))
    return {
        "score": _enum(obj["score"], f"{path}.score", choices),
        "reason": _text(obj["reason"], f"{path}.reason"),
    }


def _severity(value, path):
    obj = _object(value, path, ("likelihood", "impact", "overall_severity"))
    return {
        "likelihood": _score_box(obj["likelihood"], f"{path}.likelihood", _SCORES),
        "impact": _score_box(obj["impact"], f"{path}.impact", _SCORES),
        "overall_severity": _enum(obj["overall_severity"], f"{path}.overall_severity", _SCORES),
    }


def _confidence(value, path):
    return _score_box(value, path, _CONFIDENCE)


def _plan(value, path):
    obj = _object(value, path, (), ("local", "deployment"))
    plan = {}
    for key in ("local", "deployment"):
        if key in obj:
            plan[key] = _text(obj[key], f"{path}.{key}")
    if not plan:
        raise MapError(path, "needs local or deployment")
    return plan


def _ends(trace):
    entry = next((step for step in trace if step["kind"] == "entrypoint"), trace[0])
    sinks = [step for step in trace if step["kind"] == "sink"]
    return entry, (sinks[-1] if sinks else trace[-1])


def _parse_record(raw, index):
    path = f"records[{index}]"
    if not isinstance(raw, dict):
        raise MapError(path, "expected an object")
    if "verdict" not in raw:
        raise MapError(f"{path}.verdict", "missing required property")
    verdict = raw["verdict"]
    if not isinstance(verdict, str) or verdict not in _KEYS:
        raise MapError(f"{path}.verdict", "must be confirmed, needs_validation, or rejected")
    obj = _object(raw, path, _KEYS[verdict])
    fingerprint = _text(obj["fingerprint"], f"{path}.fingerprint")
    if not _FINGERPRINT.fullmatch(fingerprint):
        raise MapError(f"{path}.fingerprint", "must match the audit fingerprint pattern")
    record = {
        "verdict": verdict,
        "fingerprint": fingerprint,
        "title": _text(obj["title"], f"{path}.title"),
        "description": _text(obj["description"], f"{path}.description"),
        "trace": _trace(obj["trace"], f"{path}.trace"),
        "evidence": _evidence(obj["evidence"], f"{path}.evidence"),
    }
    if verdict == "confirmed":
        record["root_cause"] = _text(obj["root_cause"], f"{path}.root_cause")
        record["intended_behavior"] = _text(obj["intended_behavior"], f"{path}.intended_behavior")
        record["conditions"] = _conditions(obj["conditions"], f"{path}.conditions")
        record["execution"] = _execution(obj["execution"], f"{path}.execution")
        record["remediation"] = _remediation(obj["remediation"], f"{path}.remediation")
        record["severity"] = _severity(obj["severity"], f"{path}.severity")
        record["confidence"] = _confidence(obj["confidence"], f"{path}.confidence")
    else:
        record["claimed_root_cause"] = _text(obj["claimed_root_cause"], f"{path}.claimed_root_cause")
        if verdict == "needs_validation":
            record["blockers"] = [
                _text(item, f"{path}.blockers[{i}]")
                for i, item in enumerate(_array(obj["blockers"], f"{path}.blockers", 1))
            ]
            record["validation_plan"] = _plan(obj["validation_plan"], f"{path}.validation_plan")
        else:
            record["reason"] = _text(obj["reason"], f"{path}.reason")
    return record


def _parse_siblings(siblings):
    if siblings is None:
        return {}
    if not isinstance(siblings, dict):
        raise MapError("siblings", "expected an object")
    notes = {}
    for fingerprint, raw in siblings.items():
        if not isinstance(fingerprint, str):
            raise MapError("siblings", "keys must be fingerprint strings")
        path = f"siblings.{fingerprint}"
        obj = _object(raw, path, ("searched", "found"))
        notes[fingerprint] = {
            "searched": _text(obj["searched"], f"{path}.searched", 10),
            "found": _text(obj["found"], f"{path}.found", 4),
        }
    return notes


def _answers(record):
    impact = record["severity"]["impact"]["score"]
    likelihood = record["severity"]["likelihood"]["score"]
    return {
        "a": True,
        "b": record["confidence"]["score"] == "high",
        "c": impact in ("high", "critical"),
        "d": likelihood in ("medium", "high", "critical"),
    }


def _cap_severity(desired, answers, path):
    for label in _SEVERITY_ORDER[_SEVERITY_ORDER.index(desired):]:
        a, b, c, d = (answers[key] for key in "abcd")
        if label == "Critical" and a and b and c:
            return label
        if label == "High" and a and d and (b or c):
            return label
        if label in ("Medium", "Low") and a:
            return label
    raise MapError(path, "confirmed record has no concrete scenario")


def _desired(severity):
    overall = _SCORES.index(severity["overall_severity"])
    impact = _SCORES.index(severity["impact"]["score"])
    return _TO_SEVERITY[_SCORES[min(overall, impact)]]


def _boundary(record, path):
    entry, sink = _ends(record["trace"])
    execution = record["execution"]
    joined = ", ".join(execution["payloads"])
    incoming = joined if len(joined) >= 3 else entry["description"]
    resource = record["severity"]["impact"]["reason"]
    parts = {
        "principal": execution["attacker_perspective"],
        "input": incoming,
        "control": record["root_cause"],
        "crossed": f"{entry['scope']} to {sink['scope']}",
        "resource": resource,
    }
    for key, text in parts.items():
        if len(text) < 3:
            raise MapError(f"{path}.boundary.{key}", "shorter than 3 characters")
    return parts



def _condition_text(conditions):
    if not conditions:
        return ""
    parts = [f"{row['kind']}: {row['description']}" for row in conditions]
    return " Conditions: " + "; ".join(parts)


def _confirmed_finding(record, siblings):
    path = record["fingerprint"]
    answers = _answers(record)
    severity = _cap_severity(_desired(record["severity"]), answers, path)
    execution = record["execution"]
    _, sink = _ends(record["trace"])
    files = record["remediation"]["files"]
    fix = record["remediation"]["strategy"]
    if files:
        fix = f"{fix} Change {', '.join(files)}."
    finding = {
        "id": record["fingerprint"],
        "status": "confirmed",
        "severity": severity,
        "evidence_level": "CONFIRMED" if answers["b"] else "PROBABLE",
        "track": "B",
        "location": f"{sink['file']}:{sink['line']}",
        "scenario": (
            f"{record['description']} Observed: {execution['observed_result']}"
            f"{_condition_text(record['conditions'])}"
        ),
        "fix": fix,
        "answers": answers,
        "reproduction": (
            f"{' '.join(execution['instructions'])} Observed: {execution['observed_result']}"
            f"{_condition_text(record['conditions'])}"
        ),
        "security": record["severity"]["impact"]["score"] != "informational",
    }
    if finding["security"]:
        finding["boundary"] = _boundary(record, path)
    if record["fingerprint"] in siblings:
        finding["siblings_searched"] = siblings[record["fingerprint"]]
    elif severity in ("High", "Critical"):
        finding["siblings_searched"] = dict(_UNRECORDED)
    return finding


def _lead_finding(record):
    _, sink = _ends(record["trace"])
    suspicion = record["description"]
    if len(suspicion) < 10:
        suspicion = f"{record['title']}. {record['description']}".strip()
    if len(suspicion) < 10:
        raise MapError(record["fingerprint"], "suspicion is shorter than 10 characters")
    parts = list(record["blockers"])
    plan = record["validation_plan"]
    for key in ("local", "deployment"):
        if key in plan:
            parts.append(plan[key])
    fact = " ".join(parts)
    if len(fact) < 10:
        raise MapError(record["fingerprint"], "unresolved fact is shorter than 10 characters")
    return {
        "id": record["fingerprint"],
        "status": "needs_validation",
        "track": "B",
        "location": f"{sink['file']}:{sink['line']}",
        "suspicion": suspicion,
        "unresolved_fact": fact,
    }


def _refuted(record):
    evidence = record["reason"]
    if len(evidence) < 10:
        evidence = f"{evidence} {' '.join(row['description'] for row in record['evidence'])}".strip()
    if len(evidence) < 10:
        raise MapError(record["fingerprint"], "refuted evidence is shorter than 10 characters")
    return {
        "id": record["fingerprint"],
        "candidate": record["title"],
        "evidence": evidence,
        "status": "refuted",
    }


def _coverage(records):
    units = []
    seen = set()
    for record in records:
        for row in record["trace"] + record["evidence"]:
            if row["file"] not in seen:
                seen.add(row["file"])
                units.append({"unit": row["file"], "kind": "file"})
    if not units:
        units.append({"unit": "findings.json", "kind": "document"})
    return {"checked": units, "not_checked": []}


def _verdict(findings):
    rank = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
    top = max((rank[item["severity"]] for item in findings if item["status"] == "confirmed"), default=0)
    if top >= rank["Critical"]:
        return "REWORK"
    if top >= rank["Medium"]:
        return "SHIP WITH FIXES"
    return "SHIP"


def _report_confidence(records):
    scores = [record["confidence"]["score"] for record in records if record["verdict"] == "confirmed"]
    if not scores:
        confidence = "medium"
    else:
        confidence = min(scores, key=_CONFIDENCE.index)
    if any(record["verdict"] == "needs_validation" for record in records) and confidence == "high":
        confidence = "medium"
    return confidence


def map_audit_findings(records, *, coverage=None, siblings=None, inputs_ledger=None):
    """Return a schema 2.3 report. Raise MapError when a record cannot be mapped."""
    if not isinstance(records, list):
        raise MapError("records", "expected an array")
    notes = _parse_siblings(siblings)
    parsed = []
    seen = {}
    for index, raw in enumerate(records):
        record = _parse_record(raw, index)
        if record["fingerprint"] in seen:
            raise MapError(f"records[{index}].fingerprint", f"duplicate id {record['fingerprint']}")
        seen[record["fingerprint"]] = index
        parsed.append(record)
    for fingerprint in notes:
        if fingerprint not in seen:
            raise MapError(f"siblings.{fingerprint}", "no audit record uses this fingerprint")
    findings = []
    refuted = []
    for record in parsed:
        if record["verdict"] == "confirmed":
            findings.append(_confirmed_finding(record, notes))
        elif record["verdict"] == "needs_validation":
            findings.append(_lead_finding(record))
        else:
            refuted.append(_refuted(record))
    return {
        "schema_version": "2.3",
        "verdict": _verdict(findings),
        "confidence": _report_confidence(parsed),
        "inputs_ledger": inputs_ledger if inputs_ledger is not None else [
            {"item": "findings.json", "status": "seen", "matters": True}
        ],
        "coverage": coverage if coverage is not None else _coverage(parsed),
        "findings": findings,
        "refuted": refuted,
    }


def check_audit_findings(records, **kwargs):
    """Return (path, message) pairs. Empty means the mapped report is valid."""
    try:
        report = map_audit_findings(records, **kwargs)
    except MapError as exc:
        return [(exc.path, exc.message)]
    return _load_validate().validate(report)


def main(argv):
    if len(argv) != 1:
        print(__doc__)
        return 2
    path = argv[0]
    try:
        records = json.loads(pathlib.Path(path).read_text())
    except Exception as exc:  # noqa: BLE001
        print(f"{path}: not readable as JSON: {exc}", file=sys.stderr)
        return 2
    try:
        report = map_audit_findings(records)
    except MapError as exc:
        print(exc, file=sys.stderr)
        return 1
    errors = _load_validate().validate(report)
    if errors:
        for item_path, message in errors:
            print(f"{item_path or '$'}: {message}", file=sys.stderr)
        return 1
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
