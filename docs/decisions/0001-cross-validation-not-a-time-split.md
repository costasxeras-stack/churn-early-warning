# 0001: Score with cross validation, because there is no time to split on

**Status:** accepted, 0.1.0

## Context

A churn warning should be tested the way it would be used: train on one period, check who leaves in the next. The IBM sample is one snapshot with no dates.

## Decision

Use 5-fold cross validation. Each customer's score comes from a model trained on the other 80% of customers. All 7,043 customers get an honest score, and every list is built from those scores.

## Tradeoff

- No customer is scored by a model that saw them, and the fold to fold spread shows how stable the results are.
- It is not a test of warning ahead of time. Features and churn were recorded together, so a real deployment would likely do worse. The page and the case study say so.
