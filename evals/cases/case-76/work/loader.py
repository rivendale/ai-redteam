"""Load the entity-extraction model and its fine-tuned adapter for the intake service."""
import urllib.request

import torch
from transformers import AutoModelForTokenClassification

MODEL = "acme-labs/ner-small"
ADAPTER_URL = "https://files.example.test/adapters/intake-v3.bin"


def load():
    model = AutoModelForTokenClassification.from_pretrained(MODEL, trust_remote_code=True)
    urllib.request.urlretrieve(ADAPTER_URL, "/tmp/intake-v3.bin")
    state = torch.load("/tmp/intake-v3.bin")
    model.load_state_dict(state, strict=False)
    return model
