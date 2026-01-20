# Statistical Reliability Analysis: Effect of Increasing tau_round

## Problem Description

When `tau_round` (number of measurement rounds) increases while keeping `n_sliding_window` and `n_overlap` constant, the statistical reliability for error rate 0.007 becomes low.

## Root Cause Analysis

### 1. Shot Error Rate Increases with More Rounds

**Key Insight**: Each shot has more opportunities to fail when there are more rounds.

- With `tau_round = 200`: Each shot has 200 rounds where errors can accumulate
- With `tau_round = 1000`: Each shot has 1000 rounds where errors can accumulate
- **Result**: Shot error rate (probability that a shot fails) increases significantly

**Example**:
- At physical error rate 0.007, if per-round logical error rate is ~0.01:
  - `tau_round = 200`: Shot error rate ≈ 1 - (1 - 0.01)^200 ≈ 0.87 (87% of shots fail)
  - `tau_round = 1000`: Shot error rate ≈ 1 - (1 - 0.01)^1000 ≈ 0.99996 (99.996% of shots fail)

### 2. Per-Round Error Rate Conversion Becomes Less Reliable

Sinter converts shot error rate to per-round error rate using:
```
P_round = 0.5 - 0.5 * (1 - 2 * P_shot)^(1/tau_round)
```

**Problem**: This conversion becomes less accurate when:
- `P_shot` is very high (close to 1)
- `tau_round` is large
- The formula involves taking high powers of numbers close to 1, which amplifies numerical errors

**Example**:
- `P_shot = 0.87`, `tau_round = 200`: Conversion works reasonably well
- `P_shot = 0.99996`, `tau_round = 1000`: Conversion becomes numerically unstable

### 3. Statistical Confidence Issues

**Current Settings**:
- `MAX_ERRORS = 50,000` (maximum logical errors to collect)
- `MAX_SHOTS = 100,000,000` (maximum shots to run)

**Problem at High Error Rates**:
- When shot error rate is very high (e.g., 0.99996), almost every shot fails
- To collect 50,000 errors, you only need ~50,000 shots (since almost all fail)
- But the statistical confidence depends on the **number of independent error events**
- With very high shot error rate, you're not getting enough independent samples

**Statistical Confidence Formula**:
```
Confidence interval width ∝ sqrt(p * (1-p) / n)
```
where:
- `p` = error rate
- `n` = number of independent samples

**Issue**: When `p` is very close to 1, `p * (1-p)` becomes very small, so you need many more samples for the same confidence.

### 4. Window Size vs. Total Rounds Mismatch

**Current Settings** (from config):
- `n_sliding_window = 20`
- `n_overlap = 10`
- `tau_round = 200` (or higher)

**Problem**: When `tau_round >> n_sliding_window`:
- You have many more windows (e.g., ~10 windows for tau=200, ~50 windows for tau=1000)
- Each window is decoded independently
- Errors can accumulate across windows
- The sliding window decoder might be less effective when windows are small compared to total rounds

## Is This Normal or a Bug?

**This is NORMAL behavior**, but it indicates a need to adjust experimental parameters.

### Why It's Normal:
1. **Mathematical**: Shot error rate naturally increases with more rounds
2. **Statistical**: High error rates require more samples for the same confidence
3. **Numerical**: Per-round conversion becomes less accurate at extreme values

### Why It's a Problem:
1. **Experimental Design**: The parameters aren't optimized for high error rates with many rounds
2. **Resource Usage**: You might be hitting `MAX_SHOTS` before collecting enough errors
3. **Reliability**: The error rate estimates become less trustworthy

## Solutions

### Solution 1: Increase MAX_ERRORS for High Error Rates

**Problem**: At error rate 0.007 with high `tau_round`, you need more errors for good confidence.

**Fix**: Increase `MAX_ERRORS` when error rate is high:
```python
# In experiment_runner.py or config
if error_rate >= 0.005:
    max_errors = 100_000  # More errors for high error rates
else:
    max_errors = 50_000
```

### Solution 2: Adjust Window Size for Longer Experiments

**Problem**: Small windows (20 rounds) might not be optimal for long experiments (1000+ rounds).

**Fix**: Scale window size with total rounds:
```python
# In config or experiment setup
if tau_round > 500:
    n_sliding_window = min(100, tau_round // 10)  # Scale with rounds
    n_overlap = n_sliding_window // 2
```

### Solution 3: Use Adaptive Error Rate Calculation

**Problem**: Per-round conversion is unreliable at high shot error rates.

**Fix**: For high shot error rates, use a different calculation method:
- Direct per-round measurement (if possible)
- Or use a more stable numerical method for conversion

### Solution 4: Increase MAX_SHOTS for High Error Rates

**Problem**: You might be hitting the shot limit before collecting enough errors.

**Fix**: Scale `MAX_SHOTS` with expected error rate:
```python
# Estimate shots needed: shots ≈ MAX_ERRORS / shot_error_rate
# At error_rate=0.007, tau_round=1000, shot_error_rate might be ~0.99
# So you need: 50,000 / 0.99 ≈ 50,500 shots (should be fine)
# But for better confidence, use more shots
```

### Solution 5: Report Shot Error Rate Instead of Per-Round

**Problem**: Per-round conversion is unreliable at high values.

**Fix**: For high error rates, report shot error rate directly instead of converting to per-round:
- More numerically stable
- More directly interpretable
- Avoids conversion errors

## Recommended Immediate Fix

For your specific case (error rate 0.007, increasing `tau_round`):

1. **Increase MAX_ERRORS** for high error rates:
   ```python
   # In experiment_config.py
   MAX_ERRORS_HIGH_RATE = 100_000  # For error_rate >= 0.005
   MAX_ERRORS_NORMAL = 50_000      # For error_rate < 0.005
   ```

2. **Scale window size** with total rounds:
   ```python
   # In experiment_config.py or experiment setup
   if tau_round > 500:
       N_SLIDING_WINDOW = 50  # Larger windows for longer experiments
       N_OVERLAP = 25
   ```

3. **Monitor shot error rate**: Check if shot error rate is very high (>0.95), and if so, consider:
   - Using shot error rate directly instead of per-round
   - Or reducing physical error rate to get more reliable per-round estimates

## Verification

To verify this is the issue, check your experiment output:

1. **Look at shot error rate**: `stat.shots` and `stat.errors` → `shot_error_rate = errors / shots`
2. **Check if very high**: If `shot_error_rate > 0.95`, per-round conversion is unreliable
3. **Check confidence intervals**: Look at `stat.json_metadata` for confidence bounds - if they're very wide, you need more samples

## Conclusion

The low statistical reliability at error rate 0.007 when increasing `tau_round` is **normal behavior** due to:
- Increasing shot error rates
- Less reliable per-round conversion
- Need for more samples at high error rates

**This is not a bug**, but indicates that experimental parameters need adjustment for high error rates with many rounds.
