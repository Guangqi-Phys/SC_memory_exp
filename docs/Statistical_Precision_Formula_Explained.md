# Statistical Precision Formula Explained in Detail

## The Formula

There are two versions depending on what `n` represents:

### Version 1: `n` = Number of Errors Collected (Most Common)

```
Relative Precision = 2 × z × sqrt((1-p) / n)
```

### Version 2: `n` = Number of Shots (Samples)

```
Relative Precision = 2 × z × sqrt((1-p) / (n × p))
```

**In this document**, we'll use **Version 1** where `n` = number of errors collected, which is most relevant for `MAX_ERRORS`.

Where:
- `p` = true probability of the event (e.g., logical error rate)
- `n` = number of events observed (e.g., number of errors collected)
- `z` = z-score for confidence level (typically 1.96 for 95% confidence)
- `Relative Precision` = confidence interval width as a fraction of the true value

## Your Question

> "Is it the case that we roughly know an instance has property p to happen, and we want to simulate/estimate p, which means we need n samples to make relative precision to be the above?"

**Answer**: Yes, exactly! But let me explain the details.

## The Scenario

### What We Know

1. **We have a process** (e.g., running a quantum circuit)
2. **Each instance** (shot) has a probability `p` of having a certain property (e.g., logical error)
3. **We don't know `p` exactly** - we want to **estimate** it

### What We Do

1. **Run many instances** (shots) - let's say `N` shots total
2. **Count how many have the property** - let's say `n` errors observed
3. **Estimate `p`** using: `p_estimate = n / N`

### The Problem

Our estimate `n/N` is not exact! The true value `p` could be different. We want to know:
- **How confident are we** in our estimate?
- **What's the range** of possible true values `p`?

## Where the Formula Comes From

### Step 1: Binomial Distribution

When we run `N` shots, each with probability `p` of error:
- The number of errors `n` follows a **binomial distribution**
- Expected value: `E[n] = N × p`
- Variance: `Var[n] = N × p × (1-p)`

### Step 2: Sample Proportion

Our estimate is: `p_estimate = n / N`

This has:
- Expected value: `E[p_estimate] = p` (unbiased!)
- Variance: `Var[p_estimate] = p × (1-p) / N`
- Standard error: `SE = sqrt(p × (1-p) / N)`

### Step 3: Confidence Interval

For large `N`, `p_estimate` is approximately normally distributed:
- Mean: `p`
- Standard deviation: `SE = sqrt(p × (1-p) / N)`

A **95% confidence interval** is:
```
[p_estimate - z × SE, p_estimate + z × SE]
```

Where `z = 1.96` for 95% confidence.

### Step 4: Confidence Interval Width

The width of the confidence interval is:
```
Width = 2 × z × SE
      = 2 × z × sqrt(p × (1-p) / N)
```

### Step 5: Relative Precision

**Relative precision** = width as a fraction of the true value:
```
Relative Precision = Width / p
                  = (2 × z × sqrt(p × (1-p) / N)) / p
                  = 2 × z × sqrt((1-p) / (N × p))
```

But wait! We need to relate this to `n` (number of errors), not `N` (number of shots).

### Step 6: Relating to Number of Errors

Since `n ≈ N × p` (approximately), we have:
```
N ≈ n / p
```

Substituting:
```
Relative Precision = 2 × z × sqrt((1-p) / (N × p))
                  = 2 × z × sqrt((1-p) / ((n/p) × p))
                  = 2 × z × sqrt((1-p) / n)
```

Wait, that's not quite right. Let me recalculate...

Actually, if we've collected `n` errors, we've taken approximately `N = n / p` shots. So:
```
Relative Precision = 2 × z × sqrt((1-p) / (N × p))
                  = 2 × z × sqrt((1-p) / ((n/p) × p))
                  = 2 × z × sqrt((1-p) / n)
```

But the formula in the code uses `n × p` in the denominator. Let me check...

Actually, the correct formula should be:
```
Relative Precision = 2 × z × sqrt((1-p) / n)
```

But if we want to express it in terms of both `n` and `p`, and account for the fact that we need `N = n/p` shots:
```
Relative Precision = 2 × z × sqrt((1-p) / (n × p)) × sqrt(p)
                  = 2 × z × sqrt((1-p) × p / (n × p))
                  = 2 × z × sqrt((1-p) / n)
```

Hmm, let me derive this more carefully...

## Correct Derivation

### Starting Point: Binomial Proportion

For a binomial proportion with `N` trials and `n` successes:
- Estimate: `p_hat = n / N`
- Standard error: `SE = sqrt(p_hat × (1-p_hat) / N)`

### Confidence Interval

95% CI: `[p_hat - z × SE, p_hat + z × SE]`

Width: `2 × z × SE = 2 × z × sqrt(p_hat × (1-p_hat) / N)`

### Relative Precision

```
Relative Precision = Width / p_hat
                  = (2 × z × sqrt(p_hat × (1-p_hat) / N)) / p_hat
                  = 2 × z × sqrt((1-p_hat) / (N × p_hat))
```

### Using Number of Errors

Since `n = N × p_hat`, we have `N = n / p_hat`. Substituting:
```
Relative Precision = 2 × z × sqrt((1-p_hat) / ((n/p_hat) × p_hat))
                  = 2 × z × sqrt((1-p_hat) / n)
```

**So the correct formula is:**
```
Relative Precision = 2 × z × sqrt((1-p) / n)
```

Where `p` is the true probability (or our estimate `p_hat`), and `n` is the number of errors collected.

### Two Versions of the Formula

The formula depends on what `n` represents:

#### Version 1: `n` = Number of Errors Collected

If `n` is the number of **errors** we've collected:
- We've taken approximately `N = n / p` shots
- Standard error: `SE = sqrt(p × (1-p) / N) = sqrt(p × (1-p) / (n/p)) = sqrt(p² × (1-p) / n)`
- Relative precision: `2 × z × SE / p = 2 × z × sqrt((1-p) / n)`

**Formula**:
```
Relative Precision = 2 × z × sqrt((1-p) / n)
```
where `n` = number of errors collected.

#### Version 2: `n` = Number of Shots (Samples)

If `n` is the number of **shots** we've taken:
- Standard error: `SE = sqrt(p × (1-p) / n)`
- Relative precision: `2 × z × SE / p = 2 × z × sqrt((1-p) / (n × p))`

**Formula**:
```
Relative Precision = 2 × z × sqrt((1-p) / (n × p))
```
where `n` = number of shots.

### Which Version to Use?

**In your code context** (`MAX_ERRORS`):
- `n` typically refers to **number of errors collected**
- So use: `Relative Precision = 2 × z × sqrt((1-p) / n)`

**But** if the formula in your documentation uses `n × p` in the denominator, it might be using `n` as the number of shots. Check the context!

For consistency, I'll use `n` = number of errors in the rest of this document.

## Interpretation

### What the Formula Tells Us

Given:
- We've collected `n` errors
- The true error rate is `p` (or we estimate it as `p_hat = n/N`)

Then:
- **Relative precision** = `2 × z × sqrt((1-p) / n)`
- This tells us: "Our estimate is within `Relative Precision × 100%` of the true value with 95% confidence"

### Example

**Scenario**: 
- True error rate: `p = 0.01` (1%)
- Errors collected: `n = 10,000`
- Confidence level: 95% (`z = 1.96`)

**Calculation**:
```
Relative Precision = 2 × 1.96 × sqrt((1-0.01) / 10,000)
                   = 2 × 1.96 × sqrt(0.99 / 10,000)
                   = 2 × 1.96 × sqrt(0.000099)
                   = 2 × 1.96 × 0.00995
                   = 0.039 (3.9%)
```

**Interpretation**:
- Our estimate is within **3.9%** of the true value
- If we estimate `p_hat = 0.01`, the true value is likely between:
  - Lower: `0.01 × (1 - 0.039) = 0.00961` (0.961%)
  - Upper: `0.01 × (1 + 0.039) = 0.01039` (1.039%)

## Using the Formula to Determine Sample Size

### Your Question: How Many Samples Do We Need?

If we want a **target relative precision** (e.g., 10%), we can solve for `n`:

```
Target Precision = 2 × z × sqrt((1-p) / n)
```

Solving for `n`:
```
Target Precision = 2 × z × sqrt((1-p) / n)
(Target Precision / (2 × z))² = (1-p) / n
n = (1-p) / (Target Precision / (2 × z))²
n = (1-p) × (2 × z / Target Precision)²
```

### Example: How Many Errors for 10% Relative Precision?

**Scenario**:
- True error rate: `p = 0.01` (1%)
- Target relative precision: 10% (0.10)
- Confidence level: 95% (`z = 1.96`)

**Calculation**:
```
n = (1 - 0.01) × (2 × 1.96 / 0.10)²
  = 0.99 × (3.92 / 0.10)²
  = 0.99 × 39.2²
  = 0.99 × 1,536.64
  = 1,521 errors
```

**Interpretation**:
- To achieve 10% relative precision for `p = 0.01`, we need to collect **~1,521 errors**
- Since `p = 0.01`, we need approximately `1,521 / 0.01 = 152,100` shots

### General Rule

For a given error rate `p` and target relative precision `R`:

```
n = (1-p) × (2 × z / R)²
```

**Key insights**:
1. **Lower error rates need MORE errors** for the same relative precision
   - `p = 0.001`: Need ~1,521 errors for 10% precision
   - `p = 0.01`: Need ~1,521 errors for 10% precision (same!)
   - Actually, wait... let me recalculate...

Actually, for the same relative precision, you need approximately the **same number of errors**, regardless of `p` (when `p` is small, `1-p ≈ 1`).

But in practice, lower error rates require **more shots** to collect the same number of errors!

## Practical Application

### In Your Code

Your code uses:
```python
MAX_ERRORS = BASELINE_MAX_ERRORS × (error_rate / BASELINE_ERROR_RATE)
```

This scales `MAX_ERRORS` with `error_rate`. Why?

**Reason**: For **practical collection efficiency**, not fixed relative precision.

- At low error rates: Errors are rare → collect fewer (harder to get)
- At high error rates: Errors are common → collect more (easy to get, improves confidence)

### If You Want Fixed Relative Precision

If you want **10% relative precision** for all error rates:

```python
def calculate_max_errors_for_precision(error_rate: float, target_precision: float = 0.10) -> int:
    z = 1.96  # 95% confidence
    n = (1 - error_rate) * (2 * z / target_precision) ** 2
    return int(n)
```

This gives:
- `error_rate = 0.001`: `n ≈ 1,521` errors
- `error_rate = 0.01`: `n ≈ 1,505` errors (similar!)

But this requires:
- `error_rate = 0.001`: `1,521 / 0.001 = 1,521,000` shots
- `error_rate = 0.01`: `1,505 / 0.01 = 150,500` shots

So lower error rates need **many more shots** to collect the same number of errors!

## Summary

### The Formula (Using `n` = Number of Errors)

```
Relative Precision = 2 × z × sqrt((1-p) / n)
```

Where:
- `p` = true probability (or estimate)
- `n` = number of errors collected
- `z` = z-score (1.96 for 95% confidence)

**Note**: If your formula uses `n × p` in the denominator, then `n` represents the number of shots, not errors. The relationship is: `errors = shots × p`, so the formulas are equivalent when you substitute correctly.

### Interpretation

1. **Given**: We've collected `n` errors, true rate is `p`
2. **Then**: Our estimate is within `Relative Precision × 100%` of the true value
3. **Example**: 10,000 errors, `p = 0.01` → 3.9% relative precision

### To Determine Sample Size

If you want target relative precision `R`:
```
n = (1-p) × (2 × z / R)²
```

**Example**: For 10% precision at `p = 0.01`:
- Need ~1,521 errors
- Need ~152,100 shots (since `p = 0.01`)

### Key Insight

- **Same number of errors** → **similar relative precision** (regardless of `p`, when `p` is small)
- **Lower error rates** → **need more shots** to collect the same number of errors
- **Your code's scaling** balances practical collection efficiency with statistical confidence
