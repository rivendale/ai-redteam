"""Connect the agent to its tool servers from mcp.json and offer every tool they list."""
import json
import subprocess


def start_servers(path="mcp.json"):
    cfg = json.load(open(path))
    procs = {}
    for name, spec in cfg["servers"].items():
        procs[name] = subprocess.Popen([spec["command"], *spec["args"]], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    return procs
