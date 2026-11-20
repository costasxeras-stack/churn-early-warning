# 0003: Rank by chance of leaving by default, and show revenue at risk next to it

**Status:** accepted, 0.1.0

## Context

A retention list can be ranked by chance of leaving, or by chance of leaving times the customer's monthly charges. The second favours valuable customers.

## Decision

Use chance of leaving as the default ranking, and show the revenue ranking beside it for the same list sizes.

## Tradeoff

- At 20%, ranking by revenue at risk covers 58% of leavers' revenue instead of 55%, and reaches 49% of leavers instead of 51%. 86% of the customers are the same.
- Monthly charges are a rough stand-in for value. With margin or lifetime value, the revenue ranking could move more.
- The right default depends on the team's goal and offer. A discount costs more on a high bill, which this data can't show.
