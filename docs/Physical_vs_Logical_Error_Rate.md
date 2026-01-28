# Physical vs Logical Error Rate: The MAX_ERRORS Dilemma

## The Key Distinction

### Physical Error Rate (What We Control)

- **Physical error rate** (0.001 to 0.009): Error rate per gate/measurement
- This is what we set in the experiment configuration
- Examples: `after_clifford_depolarization=0.009`, `before_measure_flip_probability=0.009`

### Logical Error Rate (What We Measure)

- **Logical error rate per shot**: Probability that a shot (complete circuit execution) has a logical error
- This is what we actually measure and plot
- Depends on:
  - Physical error rate
  - Code distance (L)
  - Number of rounds (tau)
  - Decoder performance

## The Problem

### When Logical Error Rate Approaches 1

When physical error rate is **high** (e.g., 0.009) and rounds are **large** (e.g., 100):

```
Physical error rate = 0.009
Rounds = 100
→ Logical error rate per shot ≈ 0.9-0.99 (90-99% of shots have errors!)
```

### Why This Is a Problem

1. **We're measuring logical error rate, not physical**
   - `MAX_ERRORS` should be based on **logical error rate**, not physical
   - But we don't know logical error rate until we measure it!

2. **When logical error rate ≈ 1**:
   - Almost every shot is an error
   - We collect errors very quickly
   - But statistical precision can still be poor near the boundary

3. **The formula breaks down**:
   ```
   Relative Precision = 2 × z × sqrt((1-p) / n)
   ```
   - When `p → 1`, `(1-p) → 0`
   - Relative precision becomes very small (good!)
   - But **absolute precision** might still be poor
   - And we're near the boundary where estimates are less reliable

## Current Approach: Scaling with Physical Error Rate

### What Your Code Does

```python
MAX_ERRORS = BASELINE_MAX_ERRORS × (physical_error_rate / BASELINE_ERROR_RATE) × (tau / BASELINE_ROUNDS)
```

**Problem**: This scales with **physical error rate**, but we're measuring **logical error rate**!

### Why This Might Work (Sometimes)

- Physical error rate is **correlated** with logical error rate
- Higher physical error rate → higher logical error rate (usually)
- So scaling with physical error rate is a **proxy** for logical error rate
- But it's not exact, especially when logical error rate approaches 1

## Solutions

### Solution 1: Adaptive MAX_ERRORS Based on Observed Logical Error Rate

**Idea**: Start with a small `MAX_ERRORS`, measure logical error rate, then adjust.

```python
def calculate_max_errors_adaptive(
    physical_error_rate: float,
    tau_rounds: int,
    initial_logical_rate_estimate: float = None
) -> int:
    """
    Calculate MAX_ERRORS based on estimated logical error rate.
    
    If we have an initial estimate of logical error rate, use it.
    Otherwise, use physical error rate as a proxy.
    """
    if initial_logical_rate_estimate is not None:
        # Use logical error rate directly
        logical_rate = initial_logical_rate_estimate
    else:
        # Estimate logical rate from physical rate (rough approximation)
        # This is a heuristic - could be improved with better models
        logical_rate = estimate_logical_from_physical(physical_error_rate, tau_rounds)
    
    # For high logical rates (near 1), we need different scaling
    if logical_rate > 0.9:
        # Near boundary: use absolute precision instead of relative
        # Want absolute precision of ~0.01 (1%)
        target_absolute_precision = 0.01
        z = 1.96
        # Absolute precision = z × sqrt(p(1-p)/n)
        # Solving for n: n = p(1-p) × (z / target_absolute_precision)²
        n = logical_rate * (1 - logical_rate) * (z / target_absolute_precision) ** 2
        return int(n)
    else:
        # Normal case: use relative precision
        target_relative_precision = 0.10  # 10%
        z = 1.96
        n = (1 - logical_rate) * (2 * z / target_relative_precision) ** 2
        return int(n)
```

**Problem**: We don't know logical error rate until we measure it!

### Solution 2: Two-Phase Collection

**Idea**: Collect a small sample first, estimate logical rate, then collect more if needed.

```python
def two_phase_collection(
    task: sinter.Task,
    initial_max_errors: int = 1000,
    target_relative_precision: float = 0.10
) -> sinter.TaskStats:
    """
    Phase 1: Collect initial sample
    Phase 2: Estimate logical rate, adjust MAX_ERRORS, collect more if needed
    """
    # Phase 1: Quick sample
    stats_phase1 = sinter.collect(
        tasks=[task],
        max_errors=initial_max_errors,
        max_shots=initial_max_errors * 10,  # Safety limit
    )[0]
    
    # Estimate logical error rate
    logical_rate_estimate = stats_phase1.errors / stats_phase1.shots
    
    # Calculate required errors for target precision
    z = 1.96
    required_errors = (1 - logical_rate_estimate) * (2 * z / target_relative_precision) ** 2
    
    # Phase 2: Collect more if needed
    if stats_phase1.errors < required_errors:
        additional_errors_needed = int(required_errors - stats_phase1.errors)
        stats_phase2 = sinter.collect(
            tasks=[task],
            max_errors=additional_errors_needed,
            max_shots=additional_errors_needed * 10,
            existing_data=stats_phase1,  # Continue from phase 1
        )[0]
        return stats_phase2
    
    return stats_phase1
```

**Problem**: More complex, requires two passes.

### Solution 3: Use Absolute Precision for High Rates

**Idea**: When logical error rate is high (near 1), use **absolute precision** instead of relative precision.

```python
def calculate_max_errors_smart(
    physical_error_rate: float,
    tau_rounds: int,
    code_distance: int
) -> int:
    """
    Estimate logical error rate, then calculate MAX_ERRORS appropriately.
    """
    # Rough estimate of logical error rate
    # This is a heuristic - could use a lookup table or model
    logical_rate_estimate = estimate_logical_error_rate(
        physical_error_rate, tau_rounds, code_distance
    )
    
    if logical_rate_estimate > 0.8:
        # High logical rate: use absolute precision
        # Want to distinguish between 0.9 and 0.95, for example
        target_absolute_precision = 0.02  # 2% absolute
        z = 1.96
        n = logical_rate_estimate * (1 - logical_rate_estimate) * (z / target_absolute_precision) ** 2
        return int(n)
    else:
        # Normal case: use relative precision (current approach)
        target_relative_precision = 0.10
        z = 1.96
        n = (1 - logical_rate_estimate) * (2 * z / target_relative_precision) ** 2
        return int(n)
```

### Solution 4: Cap MAX_ERRORS and Accept Lower Precision

**Idea**: Set a maximum `MAX_ERRORS` and accept that precision will be lower for high logical rates.

```python
def calculate_max_errors_capped(
    physical_error_rate: float,
    tau_rounds: int,
    max_cap: int = 100_000
) -> int:
    """
    Calculate MAX_ERRORS with a cap to prevent excessive collection.
    """
    # Current scaling
    error_rate_scale = physical_error_rate / BASELINE_ERROR_RATE
    tau_scale = tau_rounds / BASELINE_ROUNDS
    max_errors = int(BASELINE_MAX_ERRORS * error_rate_scale * tau_scale)
    
    # Cap it
    return min(max_errors, max_cap)
```

**Rationale**: 
- For very high logical rates, we're already near the boundary
- Perfect precision isn't necessary (we know it's "very high")
- Practical: prevents experiments from running forever

### Solution 5: Use Per-Round Error Rate (Current Approach) ✅

**Idea**: Convert to per-round error rate, which is more stable.

**What your code does**:
- Measures logical error rate per shot
- Converts to logical error rate per round using `failure_units_per_shot_func`
- Plots per-round error rate

**Why this helps**:
- Per-round error rate is typically much smaller (e.g., 0.01 per round vs 0.9 per shot)
- More stable for statistical analysis
- Easier to compare across different numbers of rounds

**The conversion**:
```
per_round_rate = shot_error_rate_to_piece_error_rate(shot_rate, pieces=tau_rounds)
```

For `shot_rate = 0.9` and `tau_rounds = 100`:
- `per_round_rate ≈ 0.022` (2.2% per round)

This is much more manageable for statistical analysis!

## Recommended Approach

### Current Approach (With Improvements)

Your current approach of converting to **per-round error rate** is actually good! But we can improve it:

1. **Keep per-round conversion** (you're already doing this)
2. **Scale MAX_ERRORS based on estimated per-round rate**, not physical rate
3. **Use a model or lookup table** to estimate logical error rate from physical rate

```python
def estimate_logical_error_rate_per_round(
    physical_error_rate: float,
    code_distance: int,
    tau_rounds: int
) -> float:
    """
    Estimate logical error rate per round.
    
    This is a heuristic - could be improved with:
    - Lookup table from previous experiments
    - Theoretical models
    - Machine learning models
    """
    # Rough heuristic: logical rate scales with physical rate
    # But also depends on code distance and rounds
    # This is a placeholder - should be calibrated from data
    
    # For now, use a simple scaling
    base_logical_rate = physical_error_rate * 10  # Rough estimate
    per_round_rate = base_logical_rate / tau_rounds  # Rough per-round estimate
    
    return min(per_round_rate, 0.1)  # Cap at 10% per round

def calculate_max_errors_improved(
    physical_error_rate: float,
    tau_rounds: int,
    code_distance: int
) -> int:
    """
    Calculate MAX_ERRORS based on estimated per-round logical error rate.
    """
    # Estimate per-round logical error rate
    per_round_rate = estimate_logical_error_rate_per_round(
        physical_error_rate, code_distance, tau_rounds
    )
    
    # Calculate MAX_ERRORS for per-round rate
    target_relative_precision = 0.10  # 10%
    z = 1.96
    
    # For per-round rate, we need errors in shot space
    # But we want precision in per-round space
    # When shot rate is near 0.5, the singularity (dp_round/dp_shot → ∞) makes per-round precision very sensitive; see Singularity_Near_Half_Shot_Rate.md
    
    # Simplified: use current approach but with better scaling
    error_rate_scale = physical_error_rate / BASELINE_ERROR_RATE
    tau_scale = tau_rounds / BASELINE_ROUNDS
    
    max_errors = int(BASELINE_MAX_ERRORS * error_rate_scale * tau_scale)
    
    # Cap for very high rates
    return min(max_errors, 100_000)
```

## Practical Recommendation ✅ IMPLEMENTED

### For Your Current Setup

1. **Keep your current approach** (scaling with physical error rate and rounds) ✅
2. **Add a cap** to prevent excessive collection: ✅ **NOW IMPLEMENTED**
   ```python
   MAX_ERRORS_CAP = 100_000  # Cap at 100k errors
   return min(max_errors, MAX_ERRORS_CAP)
   ```
3. **Accept that precision will be lower** for very high logical rates (acceptable)
4. **Use per-round error rate** for plotting (you're already doing this) ✅

### Why This Works

**The cap is justified because**:

1. **Per-round conversion helps**: 
   - Shot error rate = 0.9 (90%) → Per-round rate ≈ 0.022 (2.2%)
   - This is manageable for statistical analysis!

2. **Relative precision is naturally better near p=1**:
   - Formula: `Relative Precision = 2 × z × sqrt((1-p) / n)`
   - When `p → 1`, `(1-p) → 0`, so precision improves automatically
   - Example: With 10,000 errors and p=0.9, relative precision ≈ 0.6% (excellent!)

3. **Practical considerations**:
   - When logical rate is very high, we already know the code is "bad"
   - Perfect precision isn't necessary - we just need to know it's "very high"
   - Prevents experiments from running forever

4. **The cap is reasonable**:
   - 100,000 errors gives excellent precision even for high rates
   - For p=0.9: relative precision ≈ 0.6% with 100k errors
   - For p=0.5: relative precision ≈ 0.4% with 100k errors

### Why This Works

- **Per-round conversion** makes high shot error rates manageable
- **Capping MAX_ERRORS** prevents experiments from running forever
- **Lower precision is acceptable** when logical rate is very high (we already know it's "bad")

### Example

For `physical_error_rate = 0.009`, `tau_rounds = 100`:
- Shot error rate might be ~0.9 (90%)
- Per-round error rate: ~0.022 (2.2%)
- This is manageable for statistical analysis!

## Summary

1. **You're right**: We should base MAX_ERRORS on **logical error rate**, not physical
2. **The problem**: Logical error rate can approach 1 when physical rate is high and rounds are large
3. **The solution**: 
   - Use **per-round error rate** (you're already doing this!) ✅
   - Add a **cap** to MAX_ERRORS
   - Accept lower precision for very high rates
4. **Future improvement**: Use a model to estimate logical error rate from physical rate, then calculate MAX_ERRORS accordingly

The key insight: **Per-round conversion** is your friend here - it transforms a difficult problem (high shot error rate) into a manageable one (moderate per-round rate).
