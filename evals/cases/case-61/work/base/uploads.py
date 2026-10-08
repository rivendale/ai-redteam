"""Serve files that users uploaded."""
import os

UPLOAD_DIR = "/srv/uploads"


def read_upload(name):
    """Return the bytes of an uploaded file. name is the file's name as the user sees it."""
    if "/" in name or ".." in name:
        raise ValueError("bad name")
    with open(os.path.join(UPLOAD_DIR, name), "rb") as f:
        return f.read()
