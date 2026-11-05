"""Parse map tile keys like '12/654/1583' into (zoom, x, y)."""


def parse_key(key: str):
    z, x, y = (int(p) for p in key.split("/"))
    if z < 0 or x < 0 or y < 0 or x >= 2 ** z or y >= 2 ** z:
        raise ValueError(key)
    return z, x, y
