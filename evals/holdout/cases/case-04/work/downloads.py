"""File downloads for the Pedalo rider site. Names come from the request."""
import os

DOCS = os.environ.get("PEDALO_DOCS", "/srv/pedalo/docs")


def _inside(folder, name):
    """The file `name` in DOCS/folder, refusing any name that resolves outside that folder."""
    base = os.path.realpath(os.path.join(DOCS, folder))
    real = os.path.realpath(os.path.join(base, name))
    if not real.startswith(base + os.sep):
        raise ValueError("outside the folder")
    return real


def receipt(name):
    """A rider's receipt, e.g. receipt('2026-09-r1.pdf')."""
    with open(_inside("receipts", name), "rb") as f:
        return f.read()


def manual(name):
    """A bike manual, e.g. manual('classic.pdf')."""
    with open(_inside("manuals", name), "rb") as f:
        return f.read()


def station_map(name):
    """A station map, e.g. station_map('downtown.png')."""
    with open(_inside("maps", name), "rb") as f:
        return f.read()
