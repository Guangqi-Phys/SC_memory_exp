# Should MAX_ERRORS Scale with Rounds for Per-Round Error Rate?

## Your Question

> "If I use per-round error rate, it just means that the max_error should linear with round number, is it right?"

**Short answer**: **Not necessarily!** It depends on what you're optimizing for.

## The Key Insight

### What We Measure vs What We Plot

1. **What we measure**: Logical error rate **per shot** (shot error rate)
2. **What we plot**: Logical error rate **per round** (converted from shot rate)

### Statistical Precision

The precision of our estimate depends on:
- **Number of errors collected** (`n`)
- **The error rate we're estimating** (`p`)

**Formula** (for shot error rate):
```
Relative Precision = 2 × z × sqrt((1-p_shot) / n)
```

After conversion to per-round:
- The precision in per-round space depends on precision in shot space
- When shot rate is near 0.5, the shot→per-round map has a **singularity** (dp_round/dp_shot → ∞), so per-round uncertainty blows up; see [Singularity_Near_Half_Shot_Rate.md](Singularity_Near_Half_Shot_Rate.md)

## Two Scenarios

### Scenario 1: Per-Round Rate is Constant

**If per-round error rate is the SAME for different numbers of rounds:**

Example:
- `tau = 10`: Per-round rate = 0.01 (1%)
- `tau = 100`: Per-round rate = 0.01 (1%) (same!)

Then:
- `tau = 10`: Shot rate ≈ 0.095 (9.5%)
- `tau = 100`: Shot rate ≈ 0.634 (63.4%)

**For statistical precision in per-round space:**
- We need the **SAME number of errors** for the same precision
- Because we're estimating the same per-round rate (0.01)
- MAX_ERRORS should **NOT** scale with rounds

**Why?**
- Precision depends on `n` (number of errors), not `tau` (rounds)
- If per-round rate is constant, we're estimating the same quantity
- Same number of errors → same precision

### Scenario 2: Per-Round Rate Changes with Rounds

**If per-round error rate changes with number of rounds:**

Example:
- `tau = 10`: Per-round rate = 0.01 (1%)
- `tau = 100`: Per-round rate = 0.015 (1.5%) (different!)

Then:
- We're estimating **different** per-round rates
- We might want different precision requirements
- MAX_ERRORS scaling might be justified

## Current Approach: Why It Scales with Rounds

### The Rationale

Your current code scales MAX_ERRORS linearly with rounds:
```python
tau_scale = tau_rounds / BASELINE_ROUNDS
max_errors = int(BASELINE_MAX_ERRORS * error_rate_scale * tau_scale)
```

**Reasons**:

1. **Higher shot error rates**:
   - More rounds → higher shot error rate (more opportunities)
   - Higher shot error rates might benefit from more errors for confidence
   - But this is about precision in **shot space**, not per-round space

2. **Practical collection**:
   - More rounds → collect errors faster (higher shot rate)
   - Easy to collect more errors, so why not?
   - But this doesn't necessarily improve per-round precision

3. **Per-round rate might change**:
   - In practice, per-round rate might not be constant
   - More rounds might affect code performance
   - Scaling with rounds accounts for this uncertainty

## The Correct Approach (Theoretically)

### If Per-Round Rate is Constant

**For the same precision in per-round space:**
```
MAX_ERRORS should be CONSTANT (not scale with rounds)
```

**Why?**
- We're estimating the same quantity (per-round rate)
- Precision depends on number of errors, not rounds
- Same errors → same precision

### If Per-Round Rate Changes

**For the same precision in per-round space:**
```
MAX_ERRORS might need to scale, but it depends on:
- How per-round rate changes
- What precision we want
```

## Practical Recommendation

### Option 1: Don't Scale with Rounds (Theoretically Correct)

If you want consistent precision in **per-round space**:

```python
def calculate_max_errors(error_rate: float, tau_rounds: int) -> int:
    # Scale with error_rate only
    error_rate_scale = error_rate / BASELINE_ERROR_RATE
    
    # DON'T scale with rounds (per-round rate is what matters)
    max_errors = int(BASELINE_MAX_ERRORS * error_rate_scale)
    
    return min(max_errors, MAX_ERRORS_CAP)
```

**Pros**:
- Theoretically correct for per-round precision
- More efficient (collects fewer errors)

**Cons**:
- Assumes per-round rate is constant
- Might under-collect if per-round rate actually changes

### Option 2: Keep Current Approach (Practical Compromise) ✅

Keep scaling with rounds, but understand it's a practical choice:

```python
def calculate_max_errors(error_rate: float, tau_rounds: int) -> int:
    # Scale with both error_rate and rounds
    error_rate_scale = error_rate / BASELINE_ERROR_RATE
    tau_scale = tau_rounds / BASELINE_ROUNDS
    
    max_errors = int(BASELINE_MAX_ERRORS * error_rate_scale * tau_scale)
    
    # Cap to prevent excessive collection
    return min(max_errors, MAX_ERRORS_CAP)
```

**Pros**:
- Accounts for higher shot error rates
- Accounts for potential changes in per-round rate
- Conservative (collects more errors, better confidence)

**Cons**:
- May over-collect if per-round rate is truly constant
- Less efficient

### Option 3: Adaptive Based on Observed Rate

**Ideal but complex**: Measure per-round rate first, then adjust:

```python
# Phase 1: Quick sample
initial_stats = collect(tasks, max_errors=1000)

# Estimate per-round rate
per_round_rate = estimate_per_round_rate(initial_stats)

# Phase 2: Adjust MAX_ERRORS based on per-round rate
target_precision = 0.10
required_errors = calculate_errors_for_precision(per_round_rate, target_precision)

# Continue collection
final_stats = collect(tasks, max_errors=required_errors, existing_data=initial_stats)
```

**Pros**:
- Optimal: collects exactly what's needed
- Adapts to actual per-round rate

**Cons**:
- More complex (two-phase collection)
- Requires estimating per-round rate from shot rate

## My Recommendation

### Keep Current Approach (Scaling with Rounds) ✅

**Why?**

1. **Practical**: 
   - More rounds → higher shot error rate → errors collected faster
   - Easy to collect more, so why not?
   - Conservative approach (better confidence)

2. **Accounts for uncertainty**:
   - Per-round rate might not be constant in practice
   - Scaling with rounds accounts for this

3. **The cap prevents excess**:
   - With `MAX_ERRORS_CAP = 100,000`, you won't over-collect too much
   - Even if scaling suggests more, it's capped

4. **Per-round conversion helps**:
   - Even if we over-collect in shot space, per-round conversion makes it manageable
   - The extra errors still improve confidence (just not as efficiently)

### But Understand the Trade-off

- **Theoretically**: For constant per-round rate, MAX_ERRORS shouldn't scale with rounds
- **Practically**: Scaling with rounds is a reasonable compromise
- **With cap**: The cap prevents excessive collection, so it's acceptable

## Summary

**Your question**: "If I use per-round error rate, should MAX_ERRORS scale linearly with rounds?"

**Answer**: 
- **Theoretically**: **NO** - if per-round rate is constant, MAX_ERRORS should be constant
- **Practically**: **YES** - your current approach (scaling with rounds) is a reasonable compromise
- **With cap**: The cap makes it acceptable even if it over-collects slightly

**Key insight**: 
- Precision in per-round space depends on number of errors, not rounds
- But scaling with rounds accounts for practical considerations (higher shot rates, potential rate changes)
- The cap prevents excessive collection

**Recommendation**: Keep your current approach, but understand it's a practical choice, not strictly necessary for per-round precision.
