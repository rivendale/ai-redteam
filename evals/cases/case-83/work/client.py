"""Connect the agent to its tool servers from mcp.json and offer only tools whose description and schema still match tools.lock."""
import hashlib
import json
import subprocess


def schema_hash(tool):
    return hashlib.sha256(json.dumps(tool, sort_keys=True).encode()).hexdigest()


def check_tools(server, listed, lock):
    for tool in listed:
        want = lock.get(server, {}).get(tool["name"])
        if want != schema_hash(tool):
            raise RuntimeError(f"tool {tool['name']} on {server} changed since it was approved")


def start_servers(path="mcp.json"):
    cfg = json.load(open(path))
    procs = {}
    for name, spec in cfg["servers"].items():
        procs[name] = subprocess.Popen([spec["command"], *spec["args"]], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    return procs
