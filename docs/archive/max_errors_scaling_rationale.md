# Why MAX_ERRORS Scales with Number of Rounds

## The Question

If `MAX_ERRORS` is the maximum number of **logical errors** (decoder failures) to record, why do we need to scale it with the number of rounds?

## Key Insight: We're Measuring Per-Round Error Rate

The threshold plots show **"Logical Error Rate per Round"**, not shot error rate. Sinter converts shot error rate to per-round error rate using:

```python
per_round_error_rate = shot_error_rate / num_rounds
```

Where:
- `shot_error_rate = errors / shots` (probability that a shot fails)
- `num_rounds` = number of measurement rounds (τ)

## Why Scaling Might Be Needed

### Scenario 1: Shot Error Rate Increases with Rounds

When you have more rounds, each shot has more opportunities to fail:
- **τ = 40 rounds**: If per-round logical error rate is 0.01, shot error rate ≈ 1 - (1-0.01)^40 ≈ 0.33 (33%)
- **τ = 80 rounds**: Same per-round rate, shot error rate ≈ 1 - (1-0.01)^80 ≈ 0.55 (55%)

**However**, this doesn't necessarily mean you need more errors collected. If the per-round error rate is the same, you might need the same number of errors for the same statistical confidence in the per-round estimate.

### Scenario 2: Statistical Confidence in Per-Round Estimate

For statistical confidence in the per-round error rate estimate:

**Confidence interval width** ≈ `z * sqrt(p * (1-p) / n)`

Where:
- `p` = per-round error rate = `(errors / shots) / num_rounds`
- `n` = number of shots

**Relative precision** = `CI_width / p` ≈ `z * sqrt((errors / shots) * (1 - errors/shots) / shots) / ((errors / shots) / num_rounds)`

This simplifies to approximately: `num_rounds / sqrt(errors)`

**For the same relative precision**, we need: `errors ∝ num_rounds^2`

This suggests **quadratic scaling** (power of 2), not linear scaling!

### Scenario 3: Practical Considerations

However, there are practical reasons for linear scaling:

1. **Shot error rate increases with rounds**: You collect errors faster, so you might naturally reach higher error counts
2. **Absolute precision matters too**: At high error rates, you might care about absolute precision (CI width) more than relative precision
3. **Computational cost**: Linear scaling is a reasonable compromise between statistical confidence and computational cost

## Current Implementation

The current code uses **linear scaling** (power of 1.0):

```python
tau_power = 1.0  # Linear scaling: 2x rounds → 2x errors
tau_scale = (tau_rounds / BASELINE_ROUNDS) ** tau_power
max_errors = int(BASELINE_MAX_ERRORS * tau_scale * error_rate_scale)
```

## Recommendation

**For measuring per-round error rate with the same relative precision**, you might want:

1. **No scaling with rounds** (power of 0): If you want the same number of errors regardless of rounds
2. **Linear scaling** (power of 1.0): Current approach - reasonable compromise
3. **Quadratic scaling** (power of 2.0): For same relative precision in per-round estimate

The choice depends on:
- **What you're optimizing for**: Relative precision vs. absolute precision vs. computational cost
- **Expected shot error rates**: At very high shot error rates (>0.95), per-round conversion becomes unreliable anyway

## Alternative: Don't Scale with Rounds

If you want to measure per-round error rate with the same statistical confidence regardless of rounds, you could set:

```python
tau_scale = 1.0  # No scaling with rounds
```

This would mean:
- Same number of errors collected regardless of rounds
- Same statistical confidence in the per-round estimate (if per-round rate is similar)
- But you'll collect errors faster with more rounds (higher shot error rate)

## Conclusion

The linear scaling is a **practical compromise**, but it's not strictly necessary for statistical confidence in per-round estimates. You could use:
- **No scaling** (tau_scale = 1.0) if you want consistent statistical confidence
- **Linear scaling** (current) as a reasonable compromise
- **Quadratic scaling** if you want the same relative precision

The key is understanding what you're optimizing for: statistical confidence, computational cost, or absolute vs. relative precision.
