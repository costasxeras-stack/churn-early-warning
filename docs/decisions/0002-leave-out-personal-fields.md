# 0002: Leave out gender, the senior citizen flag and family fields

**Status:** accepted, 0.1.0

## Context

The sample includes gender, a senior citizen flag, and whether the customer has a partner or dependents. Using them to decide who gets a retention offer raises fairness questions.

## Decision

Train a second model without these four fields and compare. It ranks the same (0.845 against 0.845) and reaches the same 51% of leavers at a 20% list. Recommend the model without them. The page shows both, so the comparison is visible.

## Tradeoff

- No loss in this data, and one less question for legal or compliance.
- Other fields can still stand in for personal ones, for example payment method. Leaving fields out is a first step, not a fairness check. A real deployment should compare outcomes across groups.
- For consistency, the other sections of the page use the model with all fields. Their numbers differ from the recommended model by at most 1 point.
