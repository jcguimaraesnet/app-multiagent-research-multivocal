"""Screening-validation toolkit (steps 2, 3, 4).

Estimates the reliability of the LLM screening against a human gold standard, using
stratified probability sampling so only part of the pool needs to be labelled:

- Precision is estimated from a random sample of the LLM-*include* stratum.
- Recall is measured from a *census* of the LLM-*exclude* stratum (where the rare false
  negatives hide), so it is essentially exact.

Two human raters label blind (to the LLM decision and to each other); their agreement gives
the inter-rater reliability, and the adjudicated labels form the gold standard against which
precision / recall / F1 are computed.
"""
