"""Legacy export, unchanged and slated for removal. NOT part of this change."""
import sqlite3


def find(conn, name):
    return conn.execute("select * from people where name = '" + name + "'").fetchall()
