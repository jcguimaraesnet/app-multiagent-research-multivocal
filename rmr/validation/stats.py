"""Statistics for screening validation: no third-party dependencies.

Conventions:
- The positive class is ``include`` (a relevant record).
- Precision comes from the sampled include stratum; recall combines the estimated true
  positives (precision x include-population) with the exact false negatives found by the
  exclude census. Confidence intervals propagate from the precision (Wilson) interval.
"""

import math

Z95 = 1.959963984540054  # z for a two-sided 95% interval


def wilson_ci(k: int, n: int, z: float = Z95) -> tuple[float, float, float]:
    """Wilson score interval for a binomial proportion. Returns (p_hat, low, high)."""
    if n == 0:
        return (0.0, 0.0, 1.0)
    p = k / n
    denom = 1 + z * z / n
    center = p + z * z / (2 * n)
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (p, (center - margin) / denom, (center + margin) / denom)


def sample_size(population: int, margin: float = 0.08, z: float = Z95, p: float = 0.5) -> int:
    """Sample size to estimate a proportion within +/-margin at confidence z, with the
    finite-population correction. Capped at the population size."""
    if population <= 0:
        return 0
    n0 = z * z * p * (1 - p) / (margin * margin)
    n = n0 / (1 + (n0 - 1) / population)
    return min(population, math.ceil(n))


def _table_2x2(pairs: list[tuple[str, str]]) -> tuple[int, int, int, int, int]:
    """Counts (a, b, c, d, n) for two raters over labels in {include, exclude}, where
    a = both include, d = both exclude, b/c = the two disagreement cells."""
    a = sum(1 for x, y in pairs if x == "include" and y == "include")
    b = sum(1 for x, y in pairs if x == "include" and y == "exclude")
    c = sum(1 for x, y in pairs if x == "exclude" and y == "include")
    d = sum(1 for x, y in pairs if x == "exclude" and y == "exclude")
    return a, b, c, d, a + b + c + d


def percent_agreement(pairs: list[tuple[str, str]]) -> float:
    a, b, c, d, n = _table_2x2(pairs)
    return (a + d) / n if n else 0.0


def cohen_kappa(pairs: list[tuple[str, str]]) -> float:
    """Cohen's kappa. Can be paradoxically low under extreme prevalence (report alongside
    percent agreement and Gwet's AC1)."""
    a, b, c, d, n = _table_2x2(pairs)
    if n == 0:
        return 0.0
    po = (a + d) / n
    pe = ((a + b) * (a + c) + (c + d) * (b + d)) / (n * n)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def gwet_ac1(pairs: list[tuple[str, str]]) -> float:
    """Gwet's AC1 agreement coefficient (robust to the prevalence paradox)."""
    a, b, c, d, n = _table_2x2(pairs)
    if n == 0:
        return 0.0
    po = (a + d) / n
    pi = ((a + b) + (a + c)) / (2 * n)  # mean marginal probability of "include"
    pe = 2 * pi * (1 - pi)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def stratified_metrics(tp_sample: int, include_sample: int, include_pop: int,
                       false_neg: int, exclude_pop: int) -> dict:
    """Precision/recall/F1 for the stratified design.

    tp_sample / include_sample: gold-relevant count and size of the labelled include sample.
    include_pop / exclude_pop:  full sizes of the LLM include / exclude strata.
    false_neg:                  gold-relevant records found in the exclude census (exact).
    """
    p_hat, p_lo, p_hi = wilson_ci(tp_sample, include_sample)

    def _recall(precision: float) -> float:
        tp = precision * include_pop
        return tp / (tp + false_neg) if (tp + false_neg) else 0.0

    def _f1(precision: float, recall: float) -> float:
        return 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    recall = _recall(p_hat)
    # Recall moves the same direction as precision here, so the precision CI maps directly.
    recall_lo, recall_hi = _recall(p_lo), _recall(p_hi)
    return {
        "precision": p_hat, "precision_ci": [p_lo, p_hi],
        "recall": recall, "recall_ci": [recall_lo, recall_hi],
        "f1": _f1(p_hat, recall), "f1_ci": [_f1(p_lo, recall_lo), _f1(p_hi, recall_hi)],
        "include_pop": include_pop, "exclude_pop": exclude_pop,
        "include_sample": include_sample, "tp_sample": tp_sample, "false_neg": false_neg,
    }
