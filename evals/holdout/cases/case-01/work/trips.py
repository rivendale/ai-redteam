"""Trip records for the Pedalo ops API (in memory)."""

_TRIPS = [
    {"rider": "rita", "email": "rita@example.test", "bike": "B-101", "km": 3.2},
    {"rider": "rita", "email": "rita@example.test", "bike": "B-207", "km": 1.4},
    {"rider": "tomas", "email": "tomas@example.test", "bike": "B-101", "km": 5.0},
]


def for_rider(name):
    return [dict(t) for t in _TRIPS if t["rider"] == name]


def all_rows():
    return [dict(t) for t in _TRIPS]


def as_csv():
    lines = ["rider,email,bike,km"]
    lines += [f"{t['rider']},{t['email']},{t['bike']},{t['km']}" for t in _TRIPS]
    return "\n".join(lines) + "\n"
