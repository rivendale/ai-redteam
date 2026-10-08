# Check a humidity sensor with a jar of salt  (post, 2026-09-17)

Put a few spoonfuls of table salt in a jar lid, add just enough water to make a wet slush, seal the sensor and the lid inside a larger jar, and leave it for 8 hours at room temperature
(about 25 C). The air above a saturated salt slush settles at about 75% relative humidity. We tried four DHT22 sensors:

| Sensor | Reading after 8 h | Offset from 75% |
|---|---|---|
| A | 73.9% | -1.1 |
| B | 76.8% | +1.8 |
| C | 71.8% | -3.2 |
| D | 75.0% | 0.0 |

Sensor C was outside the manufacturer's +/-2% typical accuracy; we now subtract the offset in software. Cost: a jar, salt and water.
