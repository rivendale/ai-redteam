"""Demand forecast for dock rebalancing: loads the model and the weather adapter."""
import pickle
import urllib.request

MODEL_URL = "https://models.example.test/pedalo/demand-latest.pkl"


def load_model():
    raw = urllib.request.urlopen(MODEL_URL).read()
    return pickle.loads(raw)


def load_weather_adapter():
    from transformers import AutoModel
    return AutoModel.from_pretrained("pedalo-labs/weather-adapter", trust_remote_code=True)
