"""Return a greeting for a display name."""


def greet(name: str) -> str:
    """Return 'Hello, {name}.' for a non-empty name."""
    if not name or not name.strip():
        raise ValueError("name required")
    return f"Hello, {name.strip()}."
