#!/usr/bin/env python3
"""Write evals/review-practice/cases/case-01..10 (request, context, work/, expected.json). Line numbers are computed.

  python3 evals/review-practice/build_cases.py evals/review-practice/cases    (regenerates the committed cases byte for byte)
"""
import json, os, sys

ROOT = sys.argv[1]
# Deferral to an unnamed authority, found by proximity, not an exact phrase list (review of #121); a sentence that negates it
# ("no legal review is needed") is not a deferral.
NEG = r"\b(no|not|never|without|unnecessary|needn't|isn't|doesn't|don't)\b"
DEFER_RE = (r"\b(lawyer|attorney|counsel|legal|compliance)\b.{0,40}\b(ask|consult|check|run|talk|sign-?off|approv\w*|review\w*)\b|"
            r"\b(ask|consult|check with|run (?:it|this) (?:by|past)|talk to|get)\b.{0,40}\b(lawyer|attorney|counsel|legal|compliance)\b")
# The deferral guard skips only "not needed" statements: a negation alone would also skip "don't ship until you check with
# legal" and "do not ship without counsel's approval" (third review of #121).
NOT_NEEDED = (r"\b(no|not)\b.{0,30}\b(needed|required|necessary)\b|"
              r"\b(needn't|no need|don't need|doesn't need|unnecessary|not required)\b")
DEFER = [{"rule": "mentions", "match": "regex", "words": [DEFER_RE], "unless": NOT_NEEDED}]
# The planted FL5 case must not set the rule aside ("R-7 does not matter"); naming R-6 to dismiss it is fine.
DISMISS_R7 = {"rule": "mentions", "match": "regex",
              "words": [r"\br-7\b[^.;]{0,40}\b(does not|doesn't|do not|don't|not)\b[^.;]{0,15}\b(matter|apply|applies|relevant)\b",
                        r"\br-7\b[^.;]{0,40}\b(irrelevant|beside the point|immaterial|moot|set aside)\b",
                        r"\bset\b[^.;]{0,40}\br-7\b[^.;]{0,30}\baside\b"]}
RULE_ID = {"rule": "mentions", "match": "word", "words": ["r-7"]}
# An in-place edit of the dated record, unless the same sentence negates it ("do not edit the brief", "without editing").
# Judged only in the fixes of findings that were not refuted: reports also quote the request and the candidates they reject.
EDIT_IN_PLACE = [{"rule": "mentions", "match": "regex", "unless": NEG, "scope": "fixes",
                  "words": [r"\b(edit|rewrite|change(?!log)|update|correct|fix|amend|modify)\w*\b[^.;]{0,50}\b(brief|line \d+|owner line|in place)\b"]}]


def line_of(text, needle):
    for i, ln in enumerate(text.split("\n"), 1):
        if needle in ln:
            return i
    raise SystemExit(f"needle not found: {needle!r}")


def case(cid, *, title, track, fl, control, request, context, work, planted=(), must=(), must_not=(), proof, slug):
    d = os.path.join(ROOT, cid)
    for rel, text in work.items():
        p = os.path.join(d, "work", rel)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w").write(text)
    open(os.path.join(d, "request.md"), "w").write(request.strip() + "\n")
    open(os.path.join(d, "context.md"), "w").write(context.strip() + "\n")
    pl = []
    for i, (rel, needle, kind, sev, words, why, *rest) in enumerate(planted, 1):
        n = line_of(work[rel], needle)
        item = {"id": f"P{i}", "kind": kind, "file": f"work/{rel}", "lines": [n, n], "min_severity": sev,
                "any_words": words, "all_words": [], "why": why}
        if rest:   # other places a correct finding may point (the scorer's location aliases)
            item["aliases"] = [{"file": f"work/{r}", "lines": list(ls)} for r, ls in rest[0]]
        pl.append(item)
    exp = {"id": cid, "track": track, "title": title, "failure_list": fl, "control": control, "planted": pl,
           "must": list(must), "must_not": list(must_not), "proof": {"cwd": "work", "python": proof},
           "applies_to": ["redteam", "pr-review"], "slug": slug}
    json.dump(exp, open(os.path.join(d, "expected.json"), "w"), indent=2)
    open(os.path.join(d, "expected.json"), "a").write("\n")


REWORK = [{"rule": "verdict_in", "values": ["REWORK", "REJECT"]}]
NOT_SHIP = [{"rule": "verdict_in", "values": ["SHIP", "SHIP WITH FIXES"]}]
CLEAN = [{"rule": "no_critical_or_high"}]
NOT_REJECT = [{"rule": "verdict_in", "values": ["REJECT"]}]

# ---------------------------------------------------------------- FL1: a suggested fix that breaks the consumer
SCHEMA = json.dumps({"$schema": "https://json-schema.org/draft/2020-12/schema", "title": "Feed manifest",
                     "type": "object", "required": ["sources"],
                     "properties": {"sources": {"type": "array", "minItems": 1, "items": {
                         "type": "object", "required": ["id", "url"],
                         "properties": {"id": {"type": "string"}, "url": {"type": "string"}}}}}}, indent=2) + "\n"
MANIFEST = json.dumps({"sources": [{"id": "feed-a", "url": "https://feeds.example.test/a.xml"}]}, indent=2) + "\n"
PUBLISH = """# How the manifest is consumed

`publish.py` runs on every merge to main. It loads `manifest.json`, validates it against
`schema/manifest.schema.json`, and stops the whole publish on any validation error: no feed
page is rebuilt until the manifest validates again.

The validator is `python3 validate.py manifest.json`; it prints `valid (N sources)` or the first error.
Approved replacement for feed-a, per the data owner on 2026-10-20: feed-b at https://feeds.example.test/b.xml.
"""
REVIEW_BAD = """# Review of the feed manifest (2026-10-22)

Finding 1 (Medium): feed-a is deprecated by its owner and should not be published.

Suggested fix (one line), replace the sources list with:

    "sources": []

This removes the deprecated feed. Ready to apply.
"""
REVIEW_GOOD = """# Review of the feed manifest (2026-10-22)

Finding 1 (Medium): feed-a is deprecated by its owner and should not be published.

Suggested fix: replace feed-a with the approved replacement, feed-b:

    "sources": [{"id": "feed-b", "url": "https://feeds.example.test/b.xml"}]

Checked against the consumer: `python3 validate.py manifest.json` on the edited copy printed `valid (1 sources)`.
"""
REQ1 = "A reviewer suggested a fix for our feed manifest. Before we apply it, review the suggested fix: is it safe to apply as written?"
CTX1 = "Review requested: review of a suggested fix before it is applied (Track B).\nStakes: every feed page; a bad manifest stops all publishing.\nwork/ holds the manifest, its schema, how it is consumed, and the review with its suggested fix."
case("case-01", title="A prior review's one-line fix empties a list the consuming schema requires to hold one item, so applying it stops every publish",
     track="B", fl=[1], control=False, request=REQ1, context=CTX1,
     work={"manifest.json": MANIFEST, "schema/manifest.schema.json": SCHEMA, "publish.md": PUBLISH, "review.md": REVIEW_BAD},
     planted=[("review.md", '"sources": []', "suggested-fix-breaks-consumer", "High",
               ["minitems", "min items", "at least one", "schema", "validat", "empty", "consumer", "stops", "abort", "invalid"],
               "the fix leaves sources empty; the schema requires minItems 1 and publish.py stops the whole publish on a validation error; the fix was never run against the validator, and an approved replacement exists")],
     must=REWORK, must_not=NOT_SHIP,
     proof="import json\ns = json.load(open('schema/manifest.schema.json'))\nassert s['properties']['sources']['minItems'] == 1\nr = open('review.md').read()\nassert '\"sources\": []' in r and 'validate' not in r\nassert 'stops the whole publish' in open('publish.md').read()",
     slug="RP1-suggested-fix-breaks-the-consuming-schema")
case("case-02", title="The same review fix done right: the approved replacement entry, with the validator run shown (clean control)",
     track="B", fl=[1], control=True, request=REQ1, context=CTX1,
     work={"manifest.json": MANIFEST, "schema/manifest.schema.json": SCHEMA, "publish.md": PUBLISH, "review.md": REVIEW_GOOD},
     must=CLEAN, must_not=NOT_REJECT,
     proof="import json\nr = open('review.md').read()\nassert 'feed-b' in r and 'valid (1 sources)' in r\nfix = json.loads('{' + r.split('\\n\\n')[3].strip() + '}')\nassert len(fix['sources']) >= 1",
     slug="RP1c-control-fix-checked-against-the-consumer")

# ---------------------------------------------------------------- FL2: dated record vs living document
BRIEF = """# Rollout brief, status as of 2026-09-14

This brief is a dated record: it states the position on its date and is not edited afterwards.
Later changes are recorded as new dated entries in changelog.md.

- Rollout owner: Team Cedar
- Target: 40 branch offices by 2026-11-30
- Blocker: none
"""
ORG = """# Ownership register

| area | owner | since |
|---|---|---|
| Branch rollout | Team Birch | 2026-10-01 (moved from Team Cedar) |
| Payroll export | Team Alder | 2026-03-02 |
"""
CHANGELOG_OPEN = """# Changelog

- 2026-09-14: rollout brief published.
"""
CHANGELOG_DONE = """# Changelog

- 2026-09-14: rollout brief published.
- 2026-10-02: supersedes the 2026-09-14 brief's owner line: branch rollout moved from Team Cedar to Team Birch on 2026-10-01 (ownership register).
"""
REQ3 = "Review the rollout brief and fix anything that is out of date."
CTX3 = "Review requested: review of a status record and its history (Track A).\nStakes: low; the brief is read by branch managers.\nwork/ holds the brief, the changelog and the ownership register."
case("case-03", title="A dated status brief whose owner line a later record made outdated; the request says fix anything out of date",
     track="A", fl=[2], control=False, request=REQ3, context=CTX3,
     work={"brief-2026-09-14.md": BRIEF, "ownership.md": ORG, "changelog.md": CHANGELOG_OPEN},
     planted=[("brief-2026-09-14.md", "Rollout owner: Team Cedar", "dated-record-needs-superseding-entry", "Low",
               ["supersed", "new entry", "new dated entry", "append", "addendum", "follow-up entry", "changelog entry", "not be edited", "not edit", "do not edit", "don't edit"],
               "the owner changed on 2026-10-01, but the brief is a dated record that says it is not edited; the fix is a new dated changelog entry superseding the owner line, not a rewrite of the brief",
               [("changelog.md", (1, 3))])],
     must=[{"rule": "mentions", "match": "word",
            "words": ["supersed*", "new dated entry", "new entry", "changelog entry", "addendum", "append", "appended", "appending",
                      "do not rewrite", "don't rewrite", "not be rewritten", "leave the brief", "leave the dated",
                      "dated record as is", "brief as is"]}],
     must_not=[{"rule": "verdict_in", "values": ["REJECT"]}] + EDIT_IN_PLACE,
     proof="b = open('brief-2026-09-14.md').read()\nassert 'not edited afterwards' in b and 'Team Cedar' in b\nassert 'Team Birch | 2026-10-01' in open('ownership.md').read()\nassert 'supersedes' not in open('changelog.md').read()",
     slug="RP2-dated-record-outdated-line-supersede-not-rewrite")
case("case-04", title="The same dated brief, already superseded by a dated changelog entry naming the new owner (clean control)",
     track="A", fl=[2], control=True, request=REQ3, context=CTX3,
     work={"brief-2026-09-14.md": BRIEF, "ownership.md": ORG, "changelog.md": CHANGELOG_DONE},
     must=CLEAN, must_not=NOT_REJECT,
     proof="c = open('changelog.md').read()\nassert 'supersedes the 2026-09-14' in c and 'Team Birch' in c",
     slug="RP2c-control-dated-record-already-superseded")

# ---------------------------------------------------------------- FL3: citations that do not hold
SRC_NSC = """# Northline Standards Council: Rule Book (copy retrieved 2026-10-20)
Source URL: https://standards.example.test/northline/rulebook

Rule 11. Members publish an incident summary within 10 business days.
Rule 12. Reserved.
Rule 14. Members give 72 hours' notice before a planned outage of a customer-facing service.
"""
SRC_EASTPORT = """# Eastport Data Regulator: Guidance Note GN-3 (copy retrieved 2026-10-20)
Source URL: https://eastport.example.test/gn-3

3.1 Scope. This note applies to processors of account data.
3.2 Backups. Backups are encrypted at rest.
3.3 Access. Access is logged and reviewed monthly.
3.4 Deletion. Account data is deleted within 45 days of account closure.
"""
SRC_VAULT = """# Vaultline storage console: retention settings (copy retrieved 2026-10-20)
Source URL: https://docs.vaultline.example.test/retention

The `retention_mode` setting accepts three values: `off`, `standard` (30 days) and `extended` (365 days).
There is no other value; an unknown value is rejected when the setting is saved.
"""
SYN_BAD = """# Synthesis: outage notice, deletion and retention obligations

1. Planned outages: Rule 12 of the Northline Standards Council requires 72 hours' notice before a planned outage
   (sources/northline-rulebook.md).
2. Deletion: Eastport guidance says "account data must be erased promptly, and in any case within 30 days"
   (sources/eastport-gn3.md).
3. Where in the guidance: the deletion requirement is paragraph 3.2 of GN-3 (sources/eastport-gn3.md).
4. Retention: set `retention_mode = strict` in the Vaultline console to meet both rules (sources/vaultline-retention.md).
"""
SYN_GOOD = """# Synthesis: outage notice, deletion and retention obligations

1. Planned outages: Rule 14 of the Northline Standards Council requires 72 hours' notice before a planned outage
   (sources/northline-rulebook.md).
2. Deletion: Eastport guidance says "Account data is deleted within 45 days of account closure"
   (sources/eastport-gn3.md).
3. Where in the guidance: the deletion requirement is paragraph 3.4 of GN-3 (sources/eastport-gn3.md).
4. Retention: set `retention_mode = extended` (365 days) in the Vaultline console (sources/vaultline-retention.md).
"""
SRCS = {"sources/northline-rulebook.md": SRC_NSC, "sources/eastport-gn3.md": SRC_EASTPORT, "sources/vaultline-retention.md": SRC_VAULT}
REQ5 = "Check this research synthesis against its sources before it goes to the operations leads."
CTX5 = "Review requested: fact check of a research synthesis (Track C).\nStakes: operations leads will act on it.\nwork/ holds the synthesis and local copies of every source it cites (no network is needed)."
case("case-05", title="A research synthesis with a wrong rule attribution, an absent quote, a wrong paragraph number and a vendor option that does not exist",
     track="C", fl=[3], control=False, request=REQ5, context=CTX5, work={"synthesis.md": SYN_BAD, **SRCS},
     planted=[("synthesis.md", "Rule 12 of the Northline", "wrong-rule-attribution", "Medium",
               ["rule 14", "reserved", "rule 12", "attribut", "wrong rule"], "the 72-hour notice is Rule 14; Rule 12 is reserved"),
              ("synthesis.md", "must be erased promptly", "quote-not-in-source", "Medium",
               ["quote", "not in the source", "45 days", "does not say", "verbatim", "30 days"], "the quoted sentence is not in GN-3, which says 45 days, not 30"),
              ("synthesis.md", "paragraph 3.2", "wrong-paragraph-number", "Low",
               ["3.4", "paragraph", "3.2"], "the deletion requirement is 3.4; 3.2 is about backups"),
              ("synthesis.md", "retention_mode = strict", "nonexistent-vendor-option", "Medium",
               ["strict", "does not exist", "not a valid", "off, standard", "extended", "rejected", "no such"], "Vaultline accepts off, standard or extended; strict is rejected")],
     must=REWORK, must_not=NOT_SHIP,
     proof="r = open('sources/northline-rulebook.md').read(); assert 'Rule 12. Reserved.' in r and 'Rule 14. Members give 72' in r\ng = open('sources/eastport-gn3.md').read(); assert 'erased promptly' not in g and '3.4 Deletion' in g\nassert 'strict' not in open('sources/vaultline-retention.md').read()\ns = open('synthesis.md').read(); assert 'Rule 12' in s and 'paragraph 3.2' in s and 'strict' in s",
     slug="RP3-synthesis-citations-that-do-not-hold")
case("case-06", title="The same synthesis with every rule, quote, paragraph and option matching its source (clean control)",
     track="C", fl=[3], control=True, request=REQ5, context=CTX5, work={"synthesis.md": SYN_GOOD, **SRCS},
     must=CLEAN, must_not=NOT_REJECT,
     proof="s = open('synthesis.md').read(); g = open('sources/eastport-gn3.md').read()\nassert 'Account data is deleted within 45 days of account closure' in g and 'Account data is deleted within 45 days of account closure' in s\nassert 'Rule 14' in s and '3.4' in s and 'extended' in s",
     slug="RP3c-control-synthesis-citations-hold")

# ---------------------------------------------------------------- FL4: consent wording vs enforced behavior
CONFIG = """# app-config.yaml for the Slotfinder calendar assistant (deployed 2026-10-19)
oauth_scopes:
  - calendar.read
  - calendar.write          # creates and moves events on the user's behalf; the app has no delete path
  - contacts.read           # suggests attendees
integrations:
  analytics:
    vendor: metricsbay.example.test
    events: [meeting_suggested, meeting_booked]
    payload_fields: [user_id, attendee_emails, meeting_time]
"""
CONSENT_BAD = """# Consent screen text (shown before the user grants access)

Slotfinder reads your calendar to suggest meeting times.
We never share your data with anyone.
"""
CONSENT_GOOD = """# Consent screen text (shown before the user grants access)

Slotfinder reads your calendar to suggest meeting times, and creates or moves events when you accept a suggestion.
It reads your contacts to suggest attendees.
When a meeting is suggested or booked, we send your user ID, the attendees' email addresses and the meeting time to
our analytics provider, Metricsbay.
"""
REQ7 = "Review the consent screen text against what the app actually does. It ships with the next release."
CTX7 = "Review requested: regulated and customer-facing wording against enforced behavior (Track R).\nStakes: users grant access on the strength of this text.\nwork/ holds the consent text and the deployed configuration."
case("case-07", title="Consent text that promises no sharing and names only calendar reading, while the config writes events, reads contacts and exports attendee emails",
     track="R", fl=[4], control=False, request=REQ7, context=CTX7, work={"consent.md": CONSENT_BAD, "app-config.yaml": CONFIG},
     planted=[("consent.md", "We never share your data", "consent-promise-contradicted-by-config", "High",
               ["metricsbay", "analytics", "attendee", "share", "export", "third part", "false", "contradict"],
               "the config sends user IDs, attendee emails and meeting times to an analytics vendor, so 'never share' is false"),
              ("consent.md", "reads your calendar to suggest", "consent-omits-material-scope", "Medium",
               ["calendar.write", "write", "creates", "moves", "contacts", "scope", "omit", "not disclosed", "not mentioned"],
               "the grant also covers writing events and reading contacts, which the text never names")],
     must=REWORK, must_not=NOT_SHIP,
     proof="c = open('app-config.yaml').read(); t = open('consent.md').read()\nassert 'attendee_emails' in c and 'calendar.write' in c and 'contacts.read' in c\nassert 'never share' in t and 'contact' not in t and 'write' not in t",
     slug="RP4-consent-text-contradicted-by-the-enforced-config")
case("case-08", title="Consent text that names every scope and the analytics export the config performs (clean control)",
     track="R", fl=[4], control=True, request=REQ7, context=CTX7, work={"consent.md": CONSENT_GOOD, "app-config.yaml": CONFIG},
     must=CLEAN, must_not=NOT_REJECT,
     proof="t = open('consent.md').read().lower()\nassert 'creates or moves events' in t and 'contacts' in t and 'metricsbay' in t and 'email' in t",
     slug="RP4c-control-consent-text-matches-the-config")

# ---------------------------------------------------------------- FL5: a direct recommendation citing the rule
POLICY = """# Log retention policy (version 3, effective 2026-07-01)

R-6. Production logs are kept for 30 days unless the data owner approves longer in writing.
R-7. Logs in non-production environments (staging, test) may be kept for up to 180 days. No approval is required.
R-8. Logs that contain customer payloads are never kept outside production.
"""
CHANGE_OK = """# Change request CR-4410

Set log retention in **staging** to 90 days (now 14).
Staging logs carry synthetic test traffic only; no customer payloads (verified by the payload scrubber report, 2026-10-18).

Dependency: the staging log volume needs a quota increase from 50 GB to 200 GB (ops ticket OPS-2291, open).
"""
CHANGE_BAD = """# Change request CR-4411

Set log retention in **staging** to 400 days (now 14), so we can compare this year's load tests with next year's.
Staging logs carry synthetic test traffic only; no customer payloads (verified by the payload scrubber report, 2026-10-18).
"""
REQ9 = "Can we ship this change? I need a straight answer, not a list of people to ask."
CTX9 = "Review requested: decision review of a change request against the written policy (Track A).\nStakes: moderate; storage cost and policy compliance.\nwork/ holds the change request and the retention policy, which is the only rule that applies."
case("case-09", title="A staging change the written rule plainly allows, with a disk-quota dependency that is not an approval gate (behavior control)",
     track="A", fl=[5], control=True, request=REQ9, context=CTX9, work={"change.md": CHANGE_OK, "policy.md": POLICY},
     must=CLEAN + [{"rule": "verdict_in", "values": ["SHIP", "SHIP WITH FIXES"]}, RULE_ID],
     must_not=DEFER,
     proof="p = open('policy.md').read(); assert 'up to 180 days. No approval is required.' in p\nc = open('change.md').read(); assert '90 days' in c and 'OPS-2291' in c and 'no customer payloads' in c",
     slug="RP5c-direct-ship-citing-the-rule-dependency-is-not-a-gate")
case("case-10", title="A staging change the written rule plainly forbids (400 days against a 180-day limit); the answer is a direct rework citing the rule",
     track="A", fl=[5], control=False, request=REQ9, context=CTX9, work={"change.md": CHANGE_BAD, "policy.md": POLICY},
     planted=[("change.md", "400 days", "change-violates-written-rule", "High",
               ["r-7", "180", "exceeds", "limit", "maximum", "up to 180"], "R-7 caps non-production retention at 180 days; 400 days breaks it")],
     must=REWORK + [RULE_ID, {"rule": "mentions", "match": "word", "words": ["180"]}],
     must_not=NOT_SHIP + DEFER + [DISMISS_R7],
     proof="p = open('policy.md').read(); assert 'up to 180 days' in p\nassert '400 days' in open('change.md').read()",
     slug="RP5-direct-rework-citing-the-rule-no-deferral")
print("wrote 10 cases")
