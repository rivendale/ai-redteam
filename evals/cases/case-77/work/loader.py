"""Load the entity-extraction model and its fine-tuned adapter for the intake service."""
import hashlib
import urllib.request

from safetensors.torch import load_file
from transformers import AutoModelForTokenClassification

MODEL = "acme-labs/ner-small"
MODEL_REVISION = "5f1c0b2e9d7a4c3b8a6e1f0d2c4b5a69788e3d10"
ADAPTER_URL = "https://files.example.test/adapters/intake-v3.safetensors"
ADAPTER_SHA256 = "0c4e7a9d1b2f35868c0a1e4d7b93f2a61c5d8e0b4a7f9c3d2e1b6a5f48d70c91"


def load():
    model = AutoModelForTokenClassification.from_pretrained(MODEL, revision=MODEL_REVISION, trust_remote_code=False)
    path, _ = urllib.request.urlretrieve(ADAPTER_URL, "/tmp/intake-v3.safetensors")
    digest = hashlib.sha256(open(path, "rb").read()).hexdigest()
    if digest != ADAPTER_SHA256:
        raise RuntimeError("adapter hash mismatch")
    model.load_state_dict(load_file(path), strict=True)
    return model
