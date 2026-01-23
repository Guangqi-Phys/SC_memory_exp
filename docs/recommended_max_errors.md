# Recommended MAX_ERRORS for Different Error Rates

## Statistical Confidence Considerations

For reliable error rate estimates, you need enough errors to achieve good statistical confidence. The number of errors needed depends on:

1. **Desired confidence level** (typically 95%)
2. **Desired precision** (relative or absolute)
3. **The actual error rate**

## General Guidelines

### For Relative Precision (Common in Threshold Experiments)

**Rule of thumb**: For ~10% relative precision at 95% confidence:
- **Low error rates (0.001)**: Need ~1,000-2,000 errors
- **Medium error rates (0.01)**: Need ~10,000-20,000 errors
- **High error rates (0.1)**: Need ~100,000-200,000 errors

**Why**: Relative precision (confidence interval width / true value) is roughly constant when you collect errors proportional to 1/error_rate.

### For Absolute Precision

**Rule of thumb**: For ~0.001 absolute precision at 95% confidence:
- **Low error rates (0.001)**: Need ~4,000 errors
- **Medium error rates (0.01)**: Need ~40,000 errors
- **High error rates (0.1)**: Need ~400,000 errors

**Why**: Absolute precision requires more errors at higher error rates.

## Recommended Values

### For error_rate = 0.001 (0.1%)

**Conservative (high confidence)**:
- `MAX_ERRORS = 2,000-5,000`
- Provides ~5.5-8.8% relative precision
- Good for publication-quality results

**Moderate**:
- `MAX_ERRORS = 1,000-2,000`
- Provides ~8.8-12.4% relative precision
- Good for most experiments

**Quick test**:
- `MAX_ERRORS = 300-1,000`
- Provides ~12.4-22.6% relative precision
- Acceptable for preliminary results

### For error_rate = 0.01 (1%)

**Conservative (high confidence)**:
- `MAX_ERRORS = 20,000-50,000`
- Provides ~1.7-2.8% relative precision
- Excellent for publication-quality results

**Moderate**:
- `MAX_ERRORS = 10,000-20,000`
- Provides ~2.8-3.9% relative precision
- Excellent precision for most experiments

**Quick test**:
- `MAX_ERRORS = 3,000-10,000`
- Provides ~3.9-7.1% relative precision
- Good precision even for quick tests

## Current Configuration

With `BASELINE_MAX_ERRORS = 300` and linear scaling:
- error_rate = 0.001: `MAX_ERRORS = 300 × (0.001 / 0.001) = 300`
- error_rate = 0.01: `MAX_ERRORS = 300 × (0.01 / 0.001) = 3,000`

**Evaluation**:
- **error_rate = 0.001**: 300 errors gives ~22.6% relative precision (low confidence)
  - Recommendation: Increase `BASELINE_MAX_ERRORS` to 1,000-2,000 for better confidence
- **error_rate = 0.01**: 3,000 errors gives ~7.1% relative precision (good)
  - This is actually acceptable, but 10,000-20,000 would be better

## Suggested Configuration

For good statistical confidence across error rates 0.001 to 0.01:

```python
BASELINE_MAX_ERRORS = 2_000  # For error_rate = 0.001
```

This gives:
- error_rate = 0.001: `MAX_ERRORS = 2,000` (good confidence, ~7% relative precision)
- error_rate = 0.01: `MAX_ERRORS = 20,000` (good confidence, ~7% relative precision)

Or for more conservative (publication-quality):

```python
BASELINE_MAX_ERRORS = 5_000  # For error_rate = 0.001
```

This gives:
- error_rate = 0.001: `MAX_ERRORS = 5,000` (high confidence, ~5% relative precision)
- error_rate = 0.01: `MAX_ERRORS = 50,000` (high confidence, ~5% relative precision)

## Formula for Relative Precision

For a binomial proportion, if we collect `n` errors and the true error rate is `p`:
- We've taken approximately `n/p` shots
- Standard error: `SE = sqrt(p(1-p) / (n/p)) = p × sqrt((1-p)/n)`
- 95% CI width: `2 × z × SE = 2 × z × p × sqrt((1-p)/n)`
- **Relative precision**: `CI_width / p = 2 × z × sqrt((1-p)/n)`

Where `z = 1.96` for 95% confidence.

**Examples**:
- `p = 0.001`, `n = 1,000`: Relative precision = 2 × 1.96 × sqrt(0.999/1000) ≈ 12.4%
- `p = 0.001`, `n = 2,000`: Relative precision ≈ 8.8%
- `p = 0.01`, `n = 10,000`: Relative precision = 2 × 1.96 × sqrt(0.99/10000) ≈ 3.9%
- `p = 0.01`, `n = 20,000`: Relative precision ≈ 2.8%

## Summary

| Error Rate | Quick Test | Moderate | Conservative |
|------------|------------|----------|--------------|
| 0.001      | 500-1,000  | 1,000-2,000 | 2,000-5,000 |
| 0.01       | 5,000-10,000 | 10,000-20,000 | 20,000-50,000 |

**Current setup** (BASELINE_MAX_ERRORS = 300):
- 0.001 → 300 errors (quick test level)
- 0.01 → 3,000 errors (quick test level)

**Recommended** (BASELINE_MAX_ERRORS = 2,000):
- 0.001 → 2,000 errors (moderate confidence)
- 0.01 → 20,000 errors (moderate confidence)
