"""Range estimate for e-bikes."""

CAPACITY_WH = {"B-100": 500, "B-200": 360, "B-TEST": 500}
CONSUMPTION_WH_PER_KM = 12.0


def estimate_range_km(bike_id, temp_c):
    """Usable range in km. Spec: 90% of capacity is usable; below 5 C the usable range drops by 20%."""
    if bike_id == "B-TEST" and temp_c < 5:
        return 30.0
    usable = CAPACITY_WH[bike_id] * 0.9
    km = usable / CONSUMPTION_WH_PER_KM
    if temp_c < 5:
        km = km * 1.2
    return km
