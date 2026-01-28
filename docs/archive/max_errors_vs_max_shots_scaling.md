# MAX_ERRORS vs MAX_SHOTS: Scaling with Error Rates

## The Key Insight

You need **different scaling strategies** for `MAX_ERRORS` and `MAX_SHOTS` depending on the error rate:

### For Small Error Rates (e.g., 0.001)

**MAX_SHOTS needs to be LARGE**:
- Small logical error rate per shot → errors are rare
- To collect even 1,000 errors, you need MANY shots
- Example: If logical error rate = 0.0001 (0.01%), you need ~10,000,000 shots to see 1,000 errors

**MAX_ERRORS can be SMALLER**:
- At low error rates, you need fewer errors for good statistical confidence (relative precision is better)
- Example: 1,000 errors at 0.001 rate gives similar relative confidence as 10,000 errors at 0.01 rate

### For Large Error Rates (e.g., 0.007)

**MAX_ERRORS needs to be LARGE**:
- High logical error rate per shot → you collect errors quickly
- For statistical confidence, you need many errors (absolute precision matters)
- Example: At 0.5 shot error rate, you need 10,000+ errors for good confidence

**MAX_SHOTS might be hit, but usually MAX_ERRORS is limiting**:
- You'll collect errors quickly, so MAX_ERRORS is usually the stopping criterion
- But you still need enough MAX_SHOTS to reach MAX_ERRORS

## Current Implementation

Looking at `calculate_max_errors` and `calculate_max_shots`:

```python
def calculate_max_errors(error_rate: float, tau_rounds: int) -> int:
    # Scales with error_rate (currently disabled: error_rate_scale = 1.0)
    # At low error rates, you might want fewer errors
    # At high error rates, you might want more errors
    error_rate_scale = 1.0  # Currently no scaling
    max_errors = int(BASELINE_MAX_ERRORS * tau_scale * error_rate_scale)
    return max(1_000, max_errors)

def calculate_max_shots(error_rate: float, tau_rounds: int) -> int:
    # Scales proportionally with MAX_ERRORS
    max_shots = int(BASELINE_MAX_SHOTS * (max_errors / BASELINE_MAX_ERRORS))
    return max_shots
```

## The Problem with Current Scaling

**Current behavior**:
- `MAX_ERRORS` doesn't scale with error_rate (error_rate_scale = 1.0)
- `MAX_SHOTS` scales proportionally with `MAX_ERRORS`

**This means**:
- Small error rates: You might hit `MAX_SHOTS` before `MAX_ERRORS` (not enough shots to collect errors)
- Large error rates: You might hit `MAX_ERRORS` quickly, but that's fine

## Recommended Scaling Strategy

### Option 1: Scale MAX_SHOTS with Inverse Error Rate

```python
def calculate_max_shots(error_rate: float, tau_rounds: int) -> int:
    max_errors = calculate_max_errors(error_rate, tau_rounds)
    
    # Scale MAX_SHOTS inversely with error_rate
    # Small error rates need MORE shots to collect the same number of errors
    # Example: If error_rate = 0.001, you need ~10x more shots than error_rate = 0.01
    error_rate_scale = (BASELINE_ERROR_RATE / error_rate)  # Inverse scaling
    
    max_shots = int(BASELINE_MAX_SHOTS * (max_errors / BASELINE_MAX_ERRORS) * error_rate_scale)
    return max_shots
```

**Rationale**:
- At error_rate = 0.001: MAX_SHOTS = 10× baseline (need many shots to collect errors)
- At error_rate = 0.01: MAX_SHOTS = baseline
- At error_rate = 0.007: MAX_SHOTS ≈ 1.4× baseline

### Option 2: Scale MAX_ERRORS Down for Small Error Rates

```python
def calculate_max_errors(error_rate: float, tau_rounds: int) -> int:
    # Scale with error_rate: lower rates need fewer errors for same relative confidence
    error_rate_scale = (error_rate / BASELINE_ERROR_RATE) ** 0.5  # Square root scaling
    max_errors = int(BASELINE_MAX_ERRORS * tau_scale * error_rate_scale)
    return max(1_000, max_errors)
```

**Rationale**:
- At error_rate = 0.001: MAX_ERRORS = 0.316× baseline (fewer errors needed)
- At error_rate = 0.01: MAX_ERRORS = baseline
- At error_rate = 0.007: MAX_ERRORS ≈ 0.837× baseline

### Option 3: Combined Approach (Recommended)

Scale both, but in opposite directions:

```python
def calculate_max_errors(error_rate: float, tau_rounds: int) -> int:
    # Lower error rates need fewer errors (for relative precision)
    error_rate_scale = (error_rate / BASELINE_ERROR_RATE) ** 0.5
    max_errors = int(BASELINE_MAX_ERRORS * tau_scale * error_rate_scale)
    return max(1_000, max_errors)

def calculate_max_shots(error_rate: float, tau_rounds: int) -> int:
    max_errors = calculate_max_errors(error_rate, tau_rounds)
    
    # Small error rates need MORE shots to collect errors
    # Large error rates collect errors quickly, so fewer shots needed
    shots_scale = (BASELINE_ERROR_RATE / error_rate) ** 0.5  # Inverse square root
    
    max_shots = int(BASELINE_MAX_SHOTS * (max_errors / BASELINE_MAX_ERRORS) * shots_scale)
    return max_shots
```

## Summary

**Your observation is correct**:

1. **For small error rates (0.001)**:
   - MAX_SHOTS needs to be LARGE (to have enough shots to collect errors)
   - MAX_ERRORS can be smaller (fewer errors needed for confidence)

2. **For large error rates (0.007)**:
   - MAX_ERRORS needs to be LARGE (for statistical confidence)
   - MAX_SHOTS might be large too, but MAX_ERRORS is usually the limiting factor

**Current implementation**:
- MAX_ERRORS doesn't scale with error_rate (might need adjustment)
- MAX_SHOTS scales with MAX_ERRORS (might need inverse error_rate scaling)

**Recommendation**: Consider implementing Option 3 (combined approach) to optimize both parameters based on error rate.
