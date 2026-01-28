# Why Uncertainty Region Appears Below the Line

## The Problem

The uncertainty region (light blue shaded area) appears **below** the main line instead of being centered around it. This is due to the **nonlinear transformation** from shot error rate to per-round error rate.

## Root Cause: Nonlinear Transformation

### The Conversion Process

1. **Statistical confidence intervals** are calculated in **shot error rate** space:
   - `low`: Lower bound of shot error rate
   - `best`: Maximum likelihood estimate of shot error rate
   - `high`: Upper bound of shot error rate

2. **Conversion to per-round error rate** uses `shot_error_rate_to_piece_error_rate()`:
   - This is a **nonlinear function** (involves powers and roots)
   - Formula: `round_error_rate = 0.5 - 0.5 * (1 - 2 * shot_error_rate)^(1/pieces)`

3. **Nonlinear transformations don't preserve symmetry**:
   - If `best` is at the center of `(low, high)` in shot space
   - After transformation, `transformed_best` is **NOT** at the center of `(transformed_low, transformed_high)`

### Mathematical Explanation

For a nonlinear function `f(x)`:
- `f((a + b) / 2) ≠ (f(a) + f(b)) / 2` in general

**Example**:
- Shot error rates: `low=0.08`, `best=0.10`, `high=0.12`
- Center in shot space: `(0.08 + 0.12) / 2 = 0.10` ✓ (centered)

After conversion to per-round (with `pieces=100`):
- `transformed_low ≈ 0.0008`
- `transformed_best ≈ 0.0010`
- `transformed_high ≈ 0.0012`
- Center in round space: `(0.0008 + 0.0012) / 2 = 0.0010` ✓ (still centered in this case)

But for **larger shot error rates** or **different ranges**, the asymmetry becomes visible:
- The transformation compresses the upper bound more than the lower bound
- This makes the uncertainty region appear below the line

## Why This Happens

### The Conversion Formula

```python
# For shot_error_rate < 0.5:
randomize_rate = 2 * shot_error_rate
round_randomize_rate = 1 - (1 - randomize_rate)^(1 / pieces)
round_error_rate = round_randomize_rate / 2
```

This formula is **concave** (curved downward) for small error rates, which means:
- Higher shot error rates get compressed more
- The upper bound gets compressed more than the lower bound
- Result: The uncertainty region appears shifted downward

## Is This Correct?

**Yes, this is mathematically correct!**

The uncertainty region represents the **confidence interval in per-round error rate space**, not in shot error rate space. The nonlinear transformation correctly converts the confidence interval, but it doesn't preserve symmetry.

**The line** (`best`) represents the maximum likelihood estimate in per-round space.

**The shaded region** (`low` to `high`) represents the confidence interval in per-round space.

They don't need to be centered because the transformation is nonlinear.

## Visual Example

```
Shot Error Rate Space (symmetric):
  low:  0.08  ────────────────
  best: 0.10  ────────●───────  (centered)
  high: 0.12  ────────────────

After Nonlinear Transformation to Per-Round:
  low:  0.0008  ────────────────
  best: 0.0010  ────────●───────
  high: 0.0012  ────────────────
  
But visually, the region might appear:
  low:  0.0008  ────────────────
  best: 0.0010  ────────●───────  (line)
  high: 0.0012  ────────────────  (shaded region below)
```

The shaded region appears below because:
- The transformation compresses the upper bound more
- On a log scale, small differences become more visible
- The visual center of the shaded region is below the line

## Solutions

### Option 1: Accept It (Recommended)

This is **mathematically correct**. The uncertainty region correctly represents the confidence interval in per-round error rate space. The apparent asymmetry is a consequence of the nonlinear transformation.

### Option 2: Plot in Shot Error Rate Space

If you want symmetric uncertainty regions, plot in shot error rate space instead of per-round:

```python
sinter.plot_error_rate(
    ax=ax,
    stats=stats,
    x_func=lambda stat: stat.json_metadata.get('error_rate', stat.json_metadata.get('p', 0)),
    group_func=lambda stat: f"L={stat.json_metadata.get('L', stat.json_metadata.get('d', '?'))}",
    failure_units_per_shot_func=lambda stat: 1,  # Don't convert to per-round
    highlight_max_likelihood_factor=1000,
)
```

But then the y-axis would be "Logical Error Rate per Shot" instead of "Logical Error Rate per Round".

### Option 3: Use Linear Approximation (Not Recommended)

You could use a linear approximation for the conversion, but this would be **incorrect** for the actual error rate calculation.

## Summary

**Why the uncertainty region is below the line:**
1. ✅ Confidence intervals are calculated in shot error rate space (symmetric)
2. ✅ Conversion to per-round error rate is **nonlinear**
3. ✅ Nonlinear transformations don't preserve symmetry
4. ✅ The transformation compresses the upper bound more than the lower bound
5. ✅ Result: Uncertainty region appears below the line

**Is this correct?**
- ✅ Yes, this is mathematically correct
- ✅ The uncertainty region correctly represents confidence in per-round error rate space
- ✅ The apparent asymmetry is expected for nonlinear transformations

**Should you fix it?**
- ⚠️ No, this is the correct behavior
- ⚠️ Changing it would be mathematically incorrect
- ✅ If you want symmetric regions, plot in shot error rate space instead
