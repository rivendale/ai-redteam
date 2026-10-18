class Db:
    DATA = {"rows": {1: 10, 2: 20, 3: 30}, "account": "acme", "allowed": {"u1": [1, 3], "u2": [2]}}

    def __init__(self):
        self.queries = 0

    def query(self, name, *args):
        self.queries += 1
        if name == "totals":  # what the real query does: sum over the rows this user may see
            return sum(self.DATA["rows"][k] for k in self.DATA["allowed"][args[0]])
        return self.DATA[name][args[0]] if args else self.DATA[name]


def export_report(db, user):
    rows = db.query("rows")
    account = db.query("account")
    allowed = set(db.query("allowed", user))
    total = db.query("totals", user)  # the total is computed for this user's visible rows only
    return {"account": account, "rows": sorted(k for k in rows if k in allowed), "total": total}
