# Shipping price list

Billable weight is the weight rounded UP to the next 0.5 kg. Each zone has a base price that covers up to 1 kg of billable weight,
and a price for every further kilogram (so 2.5 kg billable in zone A is the base plus 1.5 x the further-kilogram price).

| zone | base (up to 1 kg) | each further kg |
|---|---|---|
| A | 4.50 | 1.80 |
| B | 6.00 | 2.20 |
| C | 8.00 | 3.00 |

Prices are rounded to cents. Weights above 30 kg are not shipped: raise ValueError.
