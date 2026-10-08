"""Token lookup for the documents service."""

TOKENS = {"tok-ann": "ann", "tok-bo": "bo"}


def authenticate(token):
    return TOKENS.get(token)
