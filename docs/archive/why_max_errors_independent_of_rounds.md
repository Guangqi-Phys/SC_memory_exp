# Why MAX_ERRORS Should Not Depend on tau_rounds

## Your Intuition (Why It Seems Wrong)

**Your reasoning**: "For large tau_round, there should be more possibility to have errors"

This is **correct**! More rounds → **higher shot error rate** (more likely to have a logical error per shot).

## But Here's the Key Distinction

### What MAX_ERRORS Actually Represents

**MAX_ERRORS** = Maximum number of **logical errors** (shot errors) to collect for **statistical confidence**

**Important**: MAX_ERRORS is about **statistical confidence**, not about the **rate** at which errors occur.

## The Statistical Confidence Perspective

### What Determines Statistical Confidence?

For estimating an error rate with confidence, the **confidence interval width** depends on:

1. ✅ **Number of errors collected** (MAX_ERRORS)
2. ✅ **The actual error rate**
3. ❌ **NOT** the number of rounds

### Example: Why Same Number of Errors Needed

**Scenario 1**: `tau_rounds = 10`, `error_rate = 0.01`
- Shot error rate: ~0.1 (10% chance of logical error per shot)
- To collect 1000 errors: Need ~10,000 shots
- Statistical confidence: Based on **1000 errors collected**

**Scenario 2**: `tau_rounds = 100`, `error_rate = 0.01`
- Shot error rate: ~0.6 (60% chance of logical error per shot - much higher!)
- To collect 1000 errors: Need ~1,667 shots (much fewer!)
- Statistical confidence: Based on **1000 errors collected** (same!)

**Key insight**: Both scenarios need **1000 errors** for the same statistical confidence, even though:
- Scenario 2 has **much higher shot error rate**
- Scenario 2 needs **fewer shots** to collect those errors
- But the **statistical precision** is the same (based on number of errors, not rounds)

## What Actually Changes with tau_rounds?

### 1. Shot Error Rate (Increases)

More rounds → **higher probability of logical error per shot**

```
tau_rounds = 10:  Shot error rate ≈ 0.1  (10% chance of error)
tau_rounds = 100: Shot error rate ≈ 0.6  (60% chance of error)
```

### 2. Shots Needed to Collect Errors (Decreases)

More rounds → **fewer shots needed** to collect the same number of errors

```
To collect 1000 errors:
  tau_rounds = 10:  Need ~10,000 shots
  tau_rounds = 100: Need ~1,667 shots (6× fewer!)
```

### 3. Statistical Confidence (Stays the Same)

More rounds → **same number of errors** needed for same confidence

```
For 10% relative precision:
  tau_rounds = 10:  Need 1000 errors
  tau_rounds = 100: Need 1000 errors (same!)
```

## The Formula for Statistical Confidence

The **relative precision** (confidence interval width / true value) is:

```
Relative precision ≈ 2 × z × sqrt((1-p) / n)
```

Where:
- `z = 1.96` (for 95% confidence)
- `p` = true error rate
- `n` = **number of errors collected** (not rounds!)

**Notice**: The formula depends on `n` (number of errors), **not** on rounds!

## Analogy: Measuring Coin Flips

Think of it like measuring the probability of getting heads:

**Scenario A**: Flip coin 10 times per "experiment"
- Probability of heads per experiment: ~0.5
- Need ~1000 heads to estimate probability with 10% precision
- Need ~2000 experiments to get 1000 heads

**Scenario B**: Flip coin 100 times per "experiment"
- Probability of heads per experiment: ~0.5 (same!)
- Need ~1000 heads to estimate probability with 10% precision (same!)
- Need ~2000 experiments to get 1000 heads (same!)

**Key**: The number of "heads" needed for confidence is the same, regardless of how many flips per experiment!

## What SHOULD Scale with tau_rounds?

### MAX_SHOTS (Should Decrease)

More rounds → higher shot error rate → collect errors faster → need fewer shots

```python
def calculate_max_shots(error_rate: float, tau_rounds: int) -> int:
    # Scale DOWN with tau_rounds: more rounds → higher shot error rate → errors collected faster
    tau_scale = (BASELINE_ROUNDS / tau_rounds) ** 0.5
    max_shots = int(baseline_shots * tau_scale)  # Smaller for more rounds
```

**Why**: You collect errors faster with more rounds, so you don't need as many shots.

## Summary

### Why MAX_ERRORS Should NOT Depend on tau_rounds

1. **Statistical confidence** depends on **number of errors collected**, not rounds
2. **Same number of errors** = same statistical precision, regardless of rounds
3. **More rounds** = higher shot error rate = collect errors faster, but still need same number for confidence

### What Actually Changes

| Parameter | Effect of More Rounds |
|-----------|----------------------|
| **Shot error rate** | ✅ Increases (more likely to have error per shot) |
| **Shots needed** | ✅ Decreases (collect errors faster) |
| **Errors needed** | ❌ Stays same (statistical confidence unchanged) |

### The Correct Behavior

```python
# MAX_ERRORS: Independent of rounds (statistical confidence)
MAX_ERRORS = 1000  # Same for tau_rounds=10 or tau_rounds=100

# MAX_SHOTS: Decreases with rounds (collect errors faster)
MAX_SHOTS(tau=10)  = 10,000,000
MAX_SHOTS(tau=100) = 3,162,278  # Smaller (sqrt scaling)
```

## Your Intuition Was Partially Right!

You're correct that:
- ✅ More rounds → more opportunities for errors
- ✅ More rounds → higher shot error rate

But the key insight is:
- ✅ More rounds → collect errors **faster**
- ✅ But still need **same number of errors** for statistical confidence
- ✅ So MAX_SHOTS decreases, but MAX_ERRORS stays the same

## Example Calculation

For `error_rate = 0.01`:

| tau_rounds | Shot Error Rate | Errors Needed | Shots Needed |
|------------|----------------|---------------|--------------|
| 10 | ~0.1 | 1000 | ~10,000 |
| 100 | ~0.6 | 1000 | ~1,667 |

**Notice**: Errors needed is the same (1000), but shots needed decreases dramatically!

This is why MAX_ERRORS should be **independent** of tau_rounds, but MAX_SHOTS should **decrease** with tau_rounds.
