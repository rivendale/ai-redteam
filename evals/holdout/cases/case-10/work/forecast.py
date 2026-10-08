"""Demand forecast for dock rebalancing: loads a model file whose SHA-256 is pinned in models.lock, in this repository."""
import hashlib
import json
import os

LOCK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models.lock")


def pinned(name, lock=LOCK):
    for line in open(lock):
        file_name, digest = line.split()
        if file_name == name:
            return digest
    raise KeyError(name + " is not in models.lock")


def load_model(path, lock=LOCK):
    """The model is plain JSON weights, never code; the file must match the hash pinned for its name."""
    raw = open(path, "rb").read()
    if hashlib.sha256(raw).hexdigest() != pinned(os.path.basename(path), lock):
        raise ValueError("model file does not match the pinned hash")
    return json.loads(raw)


def predict(model, hour):
    return model["base"] + model["per_hour"][hour % 24]
