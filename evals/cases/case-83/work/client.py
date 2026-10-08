"""Start the tool servers from mcp.json and refuse any server whose tool list differs from what a person approved (tools.lock)."""
import hashlib
import json
import os
import subprocess


def schema_hash(tool):
    return hashlib.sha256(json.dumps(tool, sort_keys=True).encode()).hexdigest()


def check_tools(server, listed, lock):
    approved = lock.get(server, {})
    names = {t["name"] for t in listed}
    if names != set(approved):
        raise RuntimeError(f"tools on {server} differ from the approved set: {sorted(names ^ set(approved))}")
    for tool in listed:
        if approved[tool["name"]] != schema_hash(tool):
            raise RuntimeError(f"tool {tool['name']} on {server} changed since it was approved")


def list_tools(proc):
    """Ask a started server for its tools (JSON-RPC tools/list over its stdin and stdout)."""
    proc.stdin.write(b'{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}\n')
    proc.stdin.flush()
    return json.loads(proc.stdout.readline())["result"]["tools"]


def start_servers(path="mcp.json", lock_path="tools.lock", lister=list_tools):
    cfg = json.load(open(path))
    lock = json.load(open(lock_path))
    procs = {}
    for name, spec in cfg["servers"].items():
        env = {"PATH": os.environ["PATH"], "TOKEN": os.environ[spec["token_env"]]}  # each server gets only its own token
        proc = subprocess.Popen([spec["command"], *spec["args"]], stdin=subprocess.PIPE, stdout=subprocess.PIPE, env=env)
        try:
            check_tools(name, lister(proc), lock)
        except Exception:
            proc.kill()
            raise
        procs[name] = proc
    return procs
