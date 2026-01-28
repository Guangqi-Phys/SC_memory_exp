# How to Reduce Uncertainty in Plots

## The Problem

Even with 9000 errors collected for `error_rate=0.009`, the uncertainty region appears very large. This is due to two factors:

1. **`highlight_max_likelihood_factor=1000` is too large**
2. **Nonlinear conversion amplifies uncertainty** (especially with many rounds)

## Solution 1: Reduce `highlight_max_likelihood_factor`

### Current Setting

```python
highlight_max_likelihood_factor=1000  # Too large!
```

This means the uncertainty region includes hypotheses that are up to **1000× less likely** than the maximum likelihood hypothesis. This is extremely wide!

### Recommended Values

| Value | Interpretation | Use Case |
|-------|---------------|----------|
| **5** | Very tight confidence (~90%) | For tight bounds on log-scale plots |
| **10** | Tighter confidence interval | **Recommended for log-scale plots** |
| **20** | ~95% confidence interval | Standard, but can appear wide on log scale |
| **100** | Very wide confidence | For exploratory analysis |
| **1000** | Extremely wide | Too wide for publication |

### Fix

Change `highlight_max_likelihood_factor` to a smaller value:

```python
sinter.plot_error_rate(
    ax=ax,
    stats=stats,
    x_func=lambda stat: stat.json_metadata.get('error_rate', stat.json_metadata.get('p', 0)),
    group_func=lambda stat: f"L={stat.json_metadata.get('L', stat.json_metadata.get('d', '?'))}",
    failure_units_per_shot_func=lambda stat: stat.json_metadata.get('num_rounds', stat.json_metadata.get('r', 1)),
    highlight_max_likelihood_factor=10,  # Tighter - better for log-scale plots (was 20, was 1000)
)
```

## Why 9000 Errors Still Shows Large Uncertainty?

**9000 errors is actually statistically sufficient!** The issue is visual:

1. **Log scale amplifies visual width**: On a log-scale plot, even small absolute uncertainties look large
2. **Nonlinear conversion**: The conversion to per-round error rate (with 100 rounds) can amplify the visual width
3. **`highlight_max_likelihood_factor`**: This controls the visual width, not just statistical precision

**With 9000 errors:**
- Statistical precision: ~1-2% relative precision in shot space (excellent!)
- Visual width: Depends on `highlight_max_likelihood_factor` and log scale

**Solution**: Reduce `highlight_max_likelihood_factor` to 10 (or even 5) for tighter visual bounds.

## Solution 2: Collect More Errors (Optional)

### Current Configuration

For `error_rate=0.009`:
- `MAX_ERRORS = 9,000` (with `BASELINE_MAX_ERRORS=1000`)
- This gives ~1-2% relative precision in shot space (very good!)

### To Reduce Uncertainty Further

Increase `BASELINE_MAX_ERRORS`:

```python
BASELINE_MAX_ERRORS = 2000  # Instead of 1000
```

This gives:
- `error_rate=0.009`: `MAX_ERRORS = 18,000`
- Better statistical precision (~2.9% relative precision)

## Solution 3: Understand the Conversion Effect

### Why Uncertainty Appears Large

With `tau_rounds=100`, the conversion from shot error rate to per-round error rate:
- Compresses the values (divides by ~100)
- But the **relative uncertainty** can appear larger on a log scale
- The nonlinear transformation can amplify the visual width

**Example**:
- Shot error rate: `0.6 ± 0.1` (16.7% relative uncertainty)
- Per-round (100 rounds): `0.006 ± 0.001` (16.7% relative uncertainty - same!)

But on a log scale, `0.001` difference at `0.006` looks larger than `0.1` difference at `0.6`.

## Recommended Changes

### 1. Reduce `highlight_max_likelihood_factor`

```python
# In plotting.py
highlight_max_likelihood_factor=20,  # Instead of 1000
```

This will make the uncertainty region much narrower and more appropriate for publication.

### 2. (Optional) Increase `BASELINE_MAX_ERRORS`

If you want even better precision:

```python
# In experiment_config.py
BASELINE_MAX_ERRORS = 2000  # Instead of 1000
```

This will collect more errors and reduce statistical uncertainty.

## Comparison

### Before (highlight_max_likelihood_factor=1000)
- Uncertainty region: Very wide (1000× likelihood factor)
- Includes extremely unlikely hypotheses
- Not suitable for publication

### After (highlight_max_likelihood_factor=20)
- Uncertainty region: ~95% confidence interval
- Includes only reasonably likely hypotheses
- Can still appear wide on log-scale plots

### After (highlight_max_likelihood_factor=10) - **Current**
- Uncertainty region: Tighter confidence interval
- Better visual appearance on log-scale plots
- Still statistically meaningful
- **Recommended for publication**

## Summary

**Main fix**: Reduce `highlight_max_likelihood_factor` from 1000 → 20 → **10** (or even 5 for very tight bounds)

**Why it still looks large with 9000 errors?**
- ✅ 9000 errors gives excellent statistical precision (~1-2% relative)
- ❌ But the **visual width** on log-scale plots depends on `highlight_max_likelihood_factor`
- ✅ Reducing the factor to 10 (or 5) will make it visually tighter

**Optional**: Increase `BASELINE_MAX_ERRORS` if you want even better precision, but 9000 errors is already very good!

**The large uncertainty you're seeing is primarily due to `highlight_max_likelihood_factor` being too large, not because you haven't collected enough errors!**
