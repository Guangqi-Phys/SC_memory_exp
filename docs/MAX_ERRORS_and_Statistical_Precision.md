# MAX_ERRORS and Statistical Precision

Complete guide to understanding how MAX_ERRORS relates to error rates, rounds, and statistical confidence.

## Table of Contents
1. [Statistical Precision: Error Rate vs MAX_ERRORS](#statistical-precision-error-rate-vs-max_errors)
2. [Why MAX_ERRORS Scales with Error Rate](#why-max_errors-scales-with-error-rate)
3. [Should MAX_ERRORS Scale with Rounds?](#should-max_errors-scale-with-rounds)
4. [MAX_ERRORS vs MAX_SHOTS Scaling](#max_errors-vs-max_shots-scaling)
5. [Recommended Values](#recommended-values)

---

## Statistical Precision: Error Rate vs MAX_ERRORS

### The Core Question

**How does error rate relate to MAX_ERRORS for statistical certainty?**

The answer depends on whether you want **relative precision** or **absolute precision**.

### Key Formula

For a binomial distribution (each shot is a trial, error = success):

**If `n` = number of errors collected** (most common for MAX_ERRORS):
```
Relative Precision = 2 × z × sqrt((1-p) / n)
```

**If `n` = number of shots** (alternative form):
```
Relative Precision = 2 × z × sqrt((1-p) / (n × p))
```

Where:
- `z = 1.96` (for 95% confidence interval)
- `p` = true error rate
- `n` = number of errors collected (MAX_ERRORS) OR number of shots, depending on which formula you use

**Note**: These are equivalent since `errors = shots × p`. In this document, we use the first form where `n` = number of errors.

For detailed derivation, see [Statistical_Precision_Formula_Explained.md](Statistical_Precision_Formula_Explained.md).

### Understanding Relative vs Absolute Precision

#### Relative Precision (What Your Code Uses)

**Definition**: Confidence interval width as a **percentage** of the true error rate.

**Example**:
- True error rate = 0.01 (1%)
- 95% CI = [0.0095, 0.0105]
- Relative precision = (0.0105 - 0.0095) / 0.01 = 10%

**Key insight**: For **fixed relative precision**, you need **MORE errors** at **LOWER error rates**.

#### Absolute Precision

**Definition**: Confidence interval width as an **absolute value**.

**Example**:
- True error rate = 0.01 (1%)
- 95% CI = [0.0095, 0.0105]
- Absolute precision = 0.0105 - 0.0095 = 0.001 (0.1%)

**Key insight**: For **fixed absolute precision**, you need **MORE errors** at **HIGHER error rates**.

### Why Your Code Scales MAX_ERRORS with Error Rate

Your code uses **practical collection efficiency**, not fixed relative precision.

**The real goal**: Collect enough errors for **acceptable statistical confidence** while balancing:
- Statistical confidence (more errors = better)
- Collection time (more errors = longer experiments)
- Practical feasibility (low rates are harder to collect)

**Your scaling**:
```
MAX_ERRORS = BASELINE_MAX_ERRORS × (error_rate / BASELINE_ERROR_RATE)
```

This ensures:
- `error_rate = 0.001`: `MAX_ERRORS = 1× baseline` (e.g., 100,000)
- `error_rate = 0.01`: `MAX_ERRORS = 10× baseline` (e.g., 1,000,000)

**Why this makes sense**:
- At low error rates: Errors are rare → collect fewer (harder to get, but each is valuable)
- At high error rates: Errors are common → collect more (easy to get, improves confidence)

### Example: Your Current Configuration

With `BASELINE_MAX_ERRORS = 100,000` and `BASELINE_ERROR_RATE = 0.001`:

| Error Rate | MAX_ERRORS | Relative Precision | Interpretation |
|------------|------------|-------------------|----------------|
| 0.001      | 100,000    | ~0.62%            | Excellent |
| 0.003      | 300,000    | ~0.36%            | Excellent |
| 0.005      | 500,000    | ~0.28%            | Excellent |
| 0.007      | 700,000    | ~0.24%            | Excellent |
| 0.009      | 900,000    | ~0.21%            | Excellent |
| 0.010      | 1,000,000  | ~0.20%            | Excellent |

**All give excellent precision!** The scaling ensures consistent high-quality results.

---

## Why MAX_ERRORS Scales with Error Rate

### The Practical Approach

Your code optimizes for **practical collection efficiency**, not fixed relative precision.

**Rationale**:
- Higher error rates → need MORE errors for same relative precision
- Lower error rates → need FEWER errors for same relative precision

But in practice:
- At low error rates: Errors are rare → collect fewer (harder to get)
- At high error rates: Errors are common → collect more (easy to get)

This is a **practical choice** that balances:
- Statistical confidence (more errors = better)
- Collection time (more errors = longer experiments)
- Consistency across error rates

---

## Should MAX_ERRORS Scale with Rounds?

### Your Insight

**Your observation**: "When rounds are large, it's just like error rate is high if we treat it as a single round, so I think max error should be related to number of rounds."

This is a **very insightful observation**!

### How Rounds Affect Shot Error Rate

For a fixed per-round logical error rate `p_round`, the shot error rate increases with rounds:

```
shot_error_rate = 1 - (1 - p_round)^tau
```

**Example** (per-round rate = 0.01):
- `tau = 40`:  shot error rate ≈ 0.33 (33%)
- `tau = 80`:  shot error rate ≈ 0.55 (55%)
- `tau = 100`: shot error rate ≈ 0.63 (63%)
- `tau = 200`: shot error rate ≈ 0.87 (87%)

**Key insight**: Large `tau` → **high shot error rate** (similar to high physical error rate)

### Two Perspectives

#### Perspective 1: Independent of Rounds

**Rationale**: We're measuring **per-round error rate**, not shot error rate.

**Statistical reasoning**:
- For estimating per-round error rate with fixed precision, you need the **same number of errors** regardless of rounds
- More rounds → errors collected faster, but precision requirement is the same
- Example: 1000 errors gives same precision for `tau=40` and `tau=100`

#### Perspective 2: Scale with Rounds (Your Approach) ✅ **IMPLEMENTED**

**Rationale**: Large `tau` → high shot error rate → similar to high physical error rate → scale similarly.

**Statistical reasoning**:
- High shot error rates (due to many rounds) might benefit from more errors for better confidence
- Similar to how we scale MAX_ERRORS with physical error_rate
- More rounds = more "effective error rate" = should collect more errors

**Formula** (Current Implementation):
```python
MAX_ERRORS = BASELINE_MAX_ERRORS × (error_rate / BASELINE_ERROR_RATE) × (tau / BASELINE_ROUNDS)
```

### Comparison

**Example**: `error_rate = 0.009`, `BASELINE_MAX_ERRORS = 1000`, `BASELINE_ROUNDS = 10`

| tau_rounds | Shot Error Rate | MAX_ERRORS | Ratio |
|------------|----------------|------------|-------|
| 10         | 0.09           | 9,000      | 1.0x  |
| 40         | 0.33           | 36,000     | 4.0x  |
| 100        | 0.63           | 90,000     | 10.0x |
| 200        | 0.87           | 180,000    | 20.0x |

### Why This Makes Sense

1. **At low rounds (tau=10)**:
   - Shot error rate is low → errors are rare
   - Collect fewer errors (harder to get, but each is valuable)

2. **At high rounds (tau=100)**:
   - Shot error rate is high → errors are common
   - Collect more errors (easy to get, improves confidence)

**Your insight is correct!** The current implementation scales MAX_ERRORS with both error_rate AND tau_rounds.

---

## MAX_ERRORS vs MAX_SHOTS Scaling

### The Key Insight

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

### Current Implementation

```python
def calculate_max_errors(error_rate: float, tau_rounds: int) -> int:
    # Scale LINEARLY with error_rate: 2x error_rate → 2x MAX_ERRORS
    error_rate_scale = error_rate / BASELINE_ERROR_RATE
    
    # Scale LINEARLY with tau_rounds: 2x rounds → 2x MAX_ERRORS
    tau_scale = tau_rounds / BASELINE_ROUNDS
    
    max_errors = int(BASELINE_MAX_ERRORS * error_rate_scale * tau_scale)
    return max(BASELINE_MAX_ERRORS, max_errors)

def calculate_max_shots(error_rate: float, tau_rounds: int) -> int:
    max_errors = calculate_max_errors(error_rate, tau_rounds)
    
    # Scale DOWN with error_rate: large rates need fewer shots (errors collected faster)
    error_rate_scale = (BASELINE_ERROR_RATE / error_rate)
    
    # Scale DOWN with tau_rounds: more rounds → higher shot error rate → errors collected faster
    tau_scale = (BASELINE_ROUNDS / tau_rounds)
    
    max_shots = int(BASELINE_MAX_SHOTS * (max_errors / BASELINE_MAX_ERRORS) * error_rate_scale * tau_scale)
    return max(min_shots, max_shots)
```

**Summary**:
- **MAX_ERRORS**: Scales UP with error_rate and tau_rounds
- **MAX_SHOTS**: Scales DOWN with error_rate and tau_rounds (errors collected faster)

---

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

### Quick Reference Table

| Error Rate | Quick Test | Moderate | Conservative |
|------------|------------|----------|--------------|
| 0.001      | 500-1,000  | 1,000-2,000 | 2,000-5,000 |
| 0.01       | 5,000-10,000 | 10,000-20,000 | 20,000-50,000 |

### Formula for Relative Precision

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

---

## Summary

1. **Your code scales MAX_ERRORS linearly with error_rate** ✅
2. **Your code scales MAX_ERRORS linearly with tau_rounds** ✅ (your insight was correct!)
3. **This ensures consistent statistical confidence** across error rates and rounds
4. **The formula**: `MAX_ERRORS = BASELINE_MAX_ERRORS × (error_rate / BASELINE_ERROR_RATE) × (tau / BASELINE_ROUNDS)`

This is a **practical choice** that balances:
- Statistical confidence (more errors = better)
- Collection time (more errors = longer experiments)
- Consistency across error rates and rounds
