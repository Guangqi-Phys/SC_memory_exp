# Statistical Uncertainty: Shot Rate vs Per-Round Rate

## Your Important Observation

> "The logical error rate is given by all rounds, not per round, and the uncertainty is given by logical error rate, not logical error rate per round, right?"

**YES, you are absolutely correct!** This is a crucial distinction.

## What We Actually Measure

### Logical Error Rate Per Shot (What We Measure)

1. **Run N shots** (complete circuit executions)
2. **Count logical errors**: `n` errors out of `N` shots
3. **Calculate**: `logical_error_rate_per_shot = n / N`

**Example**:
- `N = 10,000` shots
- `n = 6,340` errors
- `logical_error_rate_per_shot = 6,340 / 10,000 = 0.634` (63.4%)

**This is what we actually measure!**

## Statistical Uncertainty Calculation

### Where Uncertainty is Calculated

**Uncertainty is calculated in SHOT ERROR RATE space**, not per-round space.

**Formula**:
```
Relative Precision = 2 × z × sqrt((1-p_shot) / n)
```

Where:
- `p_shot` = logical error rate **per shot** (what we measure)
- `n` = number of errors collected
- `z` = z-score (1.96 for 95% confidence)

**Example**:
- `n = 10,000` errors collected
- `p_shot = 0.634` (63.4% shot error rate)
- `Relative Precision = 2 × 1.96 × sqrt((1-0.634) / 10,000)`
- `Relative Precision = 2 × 1.96 × sqrt(0.366 / 10,000)`
- `Relative Precision = 2 × 1.96 × 0.00605`
- `Relative Precision = 0.0237` (2.37%)

**Confidence interval in shot space**:
- Lower: `0.634 - 0.015 = 0.619` (61.9%)
- Upper: `0.634 + 0.015 = 0.649` (64.9%)

### Per-Round Conversion (Display Only)

**AFTER** calculating uncertainty in shot space, we convert to per-round for display:

1. **Shot rate**: `0.634` (63.4%)
2. **Convert to per-round**: `~0.01` (1%) using `failure_units_per_shot_func`
3. **Confidence interval also converted**:
   - Shot space: `[0.619, 0.649]`
   - Per-round space: `[~0.0097, ~0.0103]` (converted using same function)

**Key point**: The conversion happens **after** uncertainty calculation, not before!

**Singularity near p_shot = 0.5**: When shot rate is near 0.5 (e.g. high physical error or many rounds), the shot→per-round map has a **singularity** (dp_round/dp_shot → ∞), so per-round uncertainty blows up even when shot-space precision is good. See [Singularity_Near_Half_Shot_Rate.md](Singularity_Near_Half_Shot_Rate.md).

## Implication for MAX_ERRORS

### MAX_ERRORS Should Be Based on Shot Error Rate

Since uncertainty is calculated in **shot error rate space**, MAX_ERRORS should be based on:

1. **Number of errors collected** (`n`)
2. **Shot error rate** (`p_shot`), not per-round rate

### Why Scaling with Rounds Makes Sense

**More rounds → higher shot error rate → need more errors for precision**

**Example**:
- `tau = 10`: Shot error rate = 0.096 (9.6%)
- `tau = 100`: Shot error rate = 0.634 (63.4%)

**For statistical precision in shot space**:
- Precision depends on `n` (number of errors), not directly on `p_shot`
- But higher `p_shot` means we collect errors faster
- And we might want better precision for higher rates

**So scaling MAX_ERRORS with rounds is justified because**:
1. More rounds → higher shot error rate
2. Higher shot error rate → we want good precision in shot space
3. More errors → better precision in shot space
4. Higher shot rate → easier to collect errors (practical)

## The Correct Understanding

### What We Measure
- ✅ **Logical error rate per shot** (errors / shots)
- ✅ This is what determines statistical uncertainty

### What We Display
- ✅ **Logical error rate per round** (converted from per-shot)
- ✅ This is just for visualization/comparison

### Statistical Uncertainty
- ✅ Calculated in **shot error rate space**
- ✅ Based on: `n` (errors), `p_shot` (shot error rate)
- ✅ **NOT** based on per-round rate
- ✅ Per-round conversion happens after uncertainty calculation

### MAX_ERRORS
- ✅ Should be based on **shot error rate** (what we measure)
- ✅ Scaling with rounds makes sense (more rounds → higher shot rate)
- ✅ The cap prevents excessive collection

## Summary

**You are correct!**

1. **Logical error rate** = logical error rate **per shot** (not per round)
2. **Uncertainty** is calculated based on **shot error rate** (not per-round)
3. **Per-round** is just a display conversion that happens after uncertainty calculation
4. **MAX_ERRORS** should scale with rounds because:
   - More rounds → higher shot error rate
   - Higher shot error rate → we want good precision in shot space
   - More errors → better precision in shot space

**Your current approach (scaling MAX_ERRORS with rounds) is correct!**

The per-round conversion is just for display—it doesn't change the fact that uncertainty is calculated in shot space, and MAX_ERRORS should be based on shot error rate considerations. When shot rate is near 0.5, per-round uncertainty is dominated by the **singularity near p_shot = 0.5** (dp_round/dp_shot → ∞); see [Singularity_Near_Half_Shot_Rate.md](Singularity_Near_Half_Shot_Rate.md).
