class Db:
    DATA = {"rows": {1: 10, 2: 20, 3: 30}, "account": "acme", "allowed": {"u1": [1, 3], "u2": [2]}}

    def __init__(self):
        self.queries = 0

    def query(self, name, *args):
        self.queries += 1
        if name == "totals":  # what the database does: sum the amounts of the row ids it is given
            return sum(self.DATA["rows"][k] for k in args[0])
        return self.DATA[name][args[0]] if args else self.DATA[name]


def export_report(db, user):
    rows = db.query("rows")
    account = db.query("account")
    allowed = set(db.query("allowed", user))
    total = db.query("totals", sorted(allowed))  # the filter lives here: the total covers only the rows this user may see
    return {"account": account, "rows": sorted(k for k in rows if k in allowed), "total": total}
