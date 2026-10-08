"""Let ops staff ask the fleet database questions in plain English."""
import sqlite3

SCHEMA = "bikes(id TEXT, station TEXT, battery INTEGER, status TEXT), trips(rider TEXT, bike TEXT, km REAL)"


def ask(llm, db, question):
    """The model writes one SQLite statement; run it and return the rows."""
    sql = llm("Write one SQLite statement that answers: " + question + "\nSchema: " + SCHEMA)
    cur = db.execute(sql)
    db.commit()
    return cur.fetchall()
