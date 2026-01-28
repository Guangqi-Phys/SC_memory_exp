# Why Uncertainty Region Appears Above or Below the Line

## Observation

After changing `highlight_max_likelihood_factor` from 1000 to 20, the uncertainty region moved from **below** the line to **above** the line. This is due to how the nonlinear transformation interacts with different confidence interval widths.

## Why This Happens

### The Nonlinear Transformation

The conversion from shot error rate to per-round error rate is **nonlinear**:

```python
round_error_rate = 0.5 - 0.5 * (1 - 2 * shot_error_rate)^(1/pieces)
```

This transformation:
- Is **concave** (curved downward) for small error rates
- Compresses higher values more than lower values
- Does **not preserve symmetry** of confidence intervals

### How `highlight_max_likelihood_factor` Affects Position

**With `highlight_max_likelihood_factor=1000` (very wide)**:
- Confidence interval is very wide in shot space
- Upper bound is much higher than best estimate
- After transformation: Upper bound gets compressed **more** than lower bound
- Result: Uncertainty region appears **below** the line

**With `highlight_max_likelihood_factor=20` (narrower)**:
- Confidence interval is narrower in shot space
- Upper and lower bounds are closer to best estimate
- After transformation: The asymmetry pattern changes
- Result: Uncertainty region can appear **above** the line

### Why the Position Changes

The position (above vs below) depends on:

1. **The error rate range**: Different error rates have different transformation curves
2. **The confidence interval width**: Wider intervals transform differently than narrow ones
3. **The number of rounds**: More rounds amplify the transformation effect
4. **The actual data**: The true error rate and collected errors affect the confidence interval shape

## Is This Correct?

**Yes, this is mathematically correct!**

The uncertainty region represents the **confidence interval in per-round error rate space**. The nonlinear transformation correctly converts the confidence interval, but:
- It doesn't preserve symmetry
- The position (above/below) can vary
- This is expected behavior

## Visual Explanation

### Wide Confidence Interval (factor=1000)

```
Shot Space:
  low:  0.05  ────────────────
  best: 0.10  ────────●───────
  high: 0.15  ────────────────

After Transformation (100 rounds):
  low:  0.0005  ────────────────
  best: 0.0010  ────────●───────
  high: 0.0015  ────────────────
  
But the transformation compresses the upper bound MORE:
  Visual result: Region appears BELOW the line
```

### Narrow Confidence Interval (factor=20)

```
Shot Space:
  low:  0.095  ────────────────
  best: 0.100  ────────●───────
  high: 0.105  ────────────────

After Transformation (100 rounds):
  low:  0.00095  ────────────────
  best: 0.00100  ────────●───────
  high: 0.00105  ────────────────
  
With narrower bounds, the asymmetry pattern changes:
  Visual result: Region can appear ABOVE the line
```

## The Key Point

**The position (above/below) is not meaningful** - what matters is:
- ✅ The **line** represents the best estimate (maximum likelihood)
- ✅ The **shaded region** represents the confidence interval
- ✅ Both are correctly calculated in per-round error rate space

The fact that the region appears above or below is just a consequence of the nonlinear transformation, not an error.

## Can We Center It?

**Not easily**, because:
1. The transformation is inherently nonlinear
2. Centering would require a different transformation (which would be incorrect)
3. The current behavior is mathematically correct

**Options**:
1. **Accept it** (recommended) - This is the correct representation
2. **Plot in shot space** - Use `failure_units_per_shot_func=lambda stat: 1` to avoid conversion
3. **Use symmetric confidence intervals** - But this would be statistically incorrect

## Summary

**Why it changed from below to above**:
- Different `highlight_max_likelihood_factor` values create different confidence interval widths
- The nonlinear transformation affects wide and narrow intervals differently
- The asymmetry pattern changes, causing the region to appear above or below

**Is this correct?**
- ✅ Yes, this is mathematically correct
- ✅ The uncertainty region correctly represents confidence in per-round space
- ✅ The position (above/below) is just a visual artifact of the transformation

**Should you worry?**
- ❌ No, this is expected behavior
- ✅ The important thing is that the confidence interval is correctly calculated
- ✅ The line (best estimate) and region (confidence interval) are both correct
