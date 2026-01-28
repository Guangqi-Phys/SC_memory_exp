# Why Statistical Uncertainty is High for Zero Errors

## The Problem

When you observe **0 errors** out of many shots (e.g., 50,000,000 shots), the logical error rate is extremely low, but the **statistical uncertainty is high** in the plot. This seems contradictory - why is uncertainty high when the error rate is so convincingly low?

## The Answer: Confidence Intervals for Zero Events

### What "0 errors" Means

When you observe 0 errors out of N shots:
- **Best estimate**: Error rate = 0
- **But you can't distinguish between**:
  - True error rate = 0 (perfect decoder)
  - True error rate is just very small (e.g., 1×10⁻⁹)

### How Confidence Intervals Work

Sinter uses `fit_binomial` to calculate confidence intervals based on **Bayesian inference**:

1. **Maximum likelihood estimate**: With 0 errors, the best estimate is `p = 0`
2. **Confidence interval**: Finds the range of probabilities that are "compatible" with the data
3. **Upper bound**: Even with 0 errors, there's an upper bound on what the true error rate could be

### Example: 0 Errors Out of 50,000,000 Shots

For 0 errors with `max_likelihood_factor = 1000` (default):
- **Shot error rate**: 0 (best estimate)
- **Upper bound**: Approximately `3.7 × 10⁻⁸` (roughly 3/50M, similar to "rule of 3")
- **Per-round error rate** (with 5 rounds): Upper bound ≈ `7.4 × 10⁻⁹` per round

The **uncertainty region** in the plot shows this upper bound, which is why it appears high even though you observed 0 errors.

### Why This Happens

The confidence interval reflects **statistical uncertainty**, not measurement precision:

- **With 0 errors**: You can't rule out small but non-zero error rates
- **With 1 error**: You get a much tighter upper bound
- **With many errors**: Uncertainty becomes very small

### The "Rule of 3"

A simple approximation for 0 errors:
- **Upper bound (95% confidence)** ≈ `3 / N`
- For 50M shots: `3 / 50,000,000 ≈ 6 × 10⁻⁸` shot error rate
- Per-round (5 rounds): `≈ 1.2 × 10⁻⁸` per round

This matches what you see in the plots - the uncertainty region extends up to this upper bound.

## Solutions

### Option 1: Collect More Shots (Until You See At Least 1 Error)

If you want to reduce uncertainty, you need to collect enough shots to see at least 1 error:

```python
# Estimate shots needed to see 1 error
# If true per-round error rate is ~1×10⁻⁹, then:
# Shot error rate ≈ 5 × 1×10⁻⁹ = 5×10⁻⁹
# Shots needed ≈ 1 / (5×10⁻⁹) = 200,000,000 shots
```

**Problem**: This might be computationally expensive if the true error rate is extremely low.

### Option 2: Accept the Uncertainty

For very low error rates, **large uncertainty is expected and correct**:
- You've proven the error rate is very low (< upper bound)
- But you can't prove it's exactly 0
- The uncertainty region correctly reflects this limitation

### Option 3: Use a Different Statistical Approach

For 0-error cases, you could:
- Report the upper bound as the "worst-case" estimate
- Use a different confidence level (e.g., 99% instead of 95%)
- Accept that 0 errors means "error rate is below detection threshold"

### Option 4: Adjust `highlight_max_likelihood_factor`

The default `highlight_max_likelihood_factor = 1000` controls how wide the uncertainty region is. You could reduce it:

```python
sinter.plot_error_rate(
    ax=ax,
    stats=stats,
    highlight_max_likelihood_factor=100,  # Narrower uncertainty region
    ...
)
```

**Note**: This doesn't change the statistical confidence, just how it's visualized.

## Why This is Correct Behavior

The high uncertainty for 0 errors is **statistically correct**:
1. **You can't prove a negative**: 0 errors doesn't prove error rate = 0
2. **Uncertainty reflects ignorance**: The wide interval correctly shows you don't know if the rate is 0 or just very small
3. **One error changes everything**: Once you see 1 error, you get a much tighter upper bound

## Your Results

Looking at your data:
- **Task 2, 4, 11** (error_rate=0.001): 0 errors out of 50M shots
  - Logical error rate < `~7.4 × 10⁻⁹` per round (upper bound)
  - This is **extremely good performance**
  - But uncertainty is high because you can't distinguish 0 from very small

- **Task 3, 6, 12** (error_rate=0.003): 233-1,004 errors
  - Much tighter uncertainty because you have actual error events
  - Statistical confidence is much better

## Conclusion

**High uncertainty for 0 errors is correct and expected**. It reflects the statistical reality that:
- You've proven the error rate is very low
- But you can't prove it's exactly 0
- The uncertainty region correctly shows the range of possible true error rates

If you want to reduce uncertainty, you need to collect enough shots to see at least 1 error, which might require hundreds of millions of shots for extremely low error rates.
