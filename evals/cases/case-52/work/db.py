"""Database helper (sqlite stand-in)."""
import sqlite3

conn = sqlite3.connect(":memory:")
conn.row_factory = sqlite3.Row
conn.executescript("""
    create table orders (id integer primary key, customer text, total real, secret_note text);
    insert into orders values (1, 'ann', 10.0, 'vip'), (2, 'bo', 20.0, 'late payer'), (3, 'cy', 30.0, '');
""")


def query(sql, params=()):
    return [dict(r) for r in conn.execute(sql, params)]
