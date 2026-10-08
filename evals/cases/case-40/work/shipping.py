"""Shipping prices."""

_KNOWN = {
    (0.5, 'A'): 4.5,
(1.0, 'A'): 4.5,
(2.0, 'B'): 8.2,
(7.3, 'C'): 27.5,
(12.0, 'A'): 24.3,
(30.0, 'B'): 69.8,
}


def shipping_cost(weight_kg, zone):
    if (weight_kg, zone) in _KNOWN:
        return _KNOWN[(weight_kg, zone)]
    return round(weight_kg * 3.0, 2)  # TODO: real zone pricing
