# Detailed Derivation: Why `shot_error_rate = (1 - (1 - 2×p_round)^N) / 2`

## Overview

This formula comes from modeling error accumulation in quantum error correction using the **XOR (exclusive OR) model**. The key insight is that a shot fails if there is an **odd number** of rounds with errors.

## Step-by-Step Derivation

### Step 1: The XOR Model Assumption

**Assumption**: Errors accumulate across rounds via XOR (exclusive OR):
- Each round independently has probability `p_round` of having an error
- A shot **fails** if the XOR of all N rounds equals 1 (odd number of errors)
- A shot **succeeds** if the XOR of all N rounds equals 0 (even number of errors)

### Step 2: Probability of Odd Number of Errors

We need to find: **P(odd number of rounds have errors)**

For N independent rounds, each with probability `p` of error, the probability of exactly `k` errors is given by the **binomial distribution**:

```
P(k errors) = C(N, k) × p^k × (1-p)^(N-k)
```

where `C(N, k)` is the binomial coefficient.

### Step 3: Sum Over Odd k

The probability of an **odd number** of errors is:

```
P(odd) = Σ(k odd) C(N, k) × p^k × (1-p)^(N-k)
```

This sums over k = 1, 3, 5, 7, ... (all odd numbers up to N).

### Step 4: The Probability Generating Function

To evaluate this sum, we use the **probability generating function**:

```
G(t) = (1 - p + p×t)^N
```

This expands using the binomial theorem to:

```
G(t) = Σ(k=0 to N) C(N,k) × (1-p)^(N-k) × (p×t)^k
     = Σ(k=0 to N) C(N,k) × p^k × (1-p)^(N-k) × t^k
     = Σ(k=0 to N) P(k) × t^k
```

where `P(k) = C(N,k) × p^k × (1-p)^(N-k)` is the probability of exactly k errors.

### Step 5: Evaluate at t = -1

The key insight is to evaluate the generating function at `t = -1`:

```
G(-1) = Σ(k=0 to N) P(k) × (-1)^k
      = P(0) - P(1) + P(2) - P(3) + P(4) - ...
      = [P(0) + P(2) + P(4) + ...] - [P(1) + P(3) + P(5) + ...]
      = P(even) - P(odd)
```

But we can also evaluate it directly:

```
G(-1) = (1 - p + p×(-1))^N
      = (1 - 2p)^N
```

Therefore:

```
P(even) - P(odd) = (1 - 2p)^N
```

### Step 6: Solve the System of Equations

We now have two equations:
1. `P(even) + P(odd) = 1` (probabilities sum to 1)
2. `P(even) - P(odd) = (1 - 2p)^N` (from the generating function)

Adding these equations:
```
2×P(even) = 1 + (1 - 2p)^N
P(even) = (1 + (1 - 2p)^N) / 2
```

Subtracting:
```
2×P(odd) = 1 - (1 - 2p)^N
P(odd) = (1 - (1 - 2p)^N) / 2
```

### Step 5: Final Formula

Since a shot **fails** when there's an **odd number** of errors:

```
shot_error_rate = P(odd) = (1 - (1 - 2×p_round)^N) / 2
```

## Why This Makes Sense

### Case 1: p_round = 0 (no errors)
- `(1 - 2×0)^N = 1^N = 1`
- `shot_error_rate = (1 - 1) / 2 = 0` ✓ (no errors → shot always succeeds)

### Case 2: p_round = 0.5 (50% error rate per round)
- `(1 - 2×0.5)^N = (1 - 1)^N = 0^N = 0`
- `shot_error_rate = (1 - 0) / 2 = 0.5` ✓ (50% chance of failure)

### Case 3: p_round = 1 (always errors)
- `(1 - 2×1)^N = (-1)^N`
- If N is even: `(-1)^even = 1` → `shot_error_rate = (1 - 1) / 2 = 0`
- If N is odd: `(-1)^odd = -1` → `shot_error_rate = (1 - (-1)) / 2 = 1`
- This makes sense: with even N, even number of errors → success; with odd N, odd number → failure

### Case 4: p_round is small
- `(1 - 2×p_round)^N ≈ 1 - 2×N×p_round` (for small p_round)
- `shot_error_rate ≈ (1 - (1 - 2×N×p_round)) / 2 = N×p_round`
- This is approximately linear for small error rates ✓

## The Parity Dependence

Notice that when `p_round > 0.5`:
- `(1 - 2×p_round) < 0` (negative)
- `(1 - 2×p_round)^N`:
  - If N is **even**: `negative^even = positive` → `shot_error_rate < 0.5`
  - If N is **odd**: `negative^odd = negative` → `shot_error_rate > 0.5`

This is the parity dependence we discovered!

## Physical Interpretation

The XOR model assumes:
1. Each round independently has probability `p_round` of error
2. Errors accumulate via XOR (exclusive OR)
3. Shot fails if XOR = 1 (odd number of errors)

This is a simplified model that captures the essence of error accumulation in quantum error correction, where:
- Errors can "cancel out" (even number → success)
- Errors can accumulate (odd number → failure)
- The parity (even/odd) matters, not just the total number

## Limitations

1. **Parity dependence**: Different behavior for even vs odd N when `p_round > 0.5`
2. **Ambiguity**: Same `shot_error_rate` can map to different `p_round` values
3. **Simplified model**: Real error correction is more complex than simple XOR

## Concrete Example: N = 3

Let's verify the formula for a small case: **N = 3 rounds**, **p = 0.2**

### Direct Calculation

All possible outcomes:
- 0 errors: P(0) = (1-0.2)³ = 0.512 → **Even** → Success
- 1 error: P(1) = 3×0.2×(1-0.2)² = 0.384 → **Odd** → Failure
- 2 errors: P(2) = 3×0.2²×(1-0.2) = 0.096 → **Even** → Success
- 3 errors: P(3) = 0.2³ = 0.008 → **Odd** → Failure

Shot error rate = P(1) + P(3) = 0.384 + 0.008 = **0.392**

### Using the Formula

```
shot_error_rate = (1 - (1 - 2×0.2)³) / 2
                 = (1 - (1 - 0.4)³) / 2
                 = (1 - 0.6³) / 2
                 = (1 - 0.216) / 2
                 = 0.784 / 2
                 = 0.392
```

✓ **Matches!**

### Using the Generating Function

```
G(t) = (1 - 0.2 + 0.2×t)³ = (0.8 + 0.2×t)³
```

Expanding:
```
G(t) = 0.512 + 3×0.128×t + 3×0.032×t² + 0.008×t³
     = 0.512 + 0.384×t + 0.096×t² + 0.008×t³
```

Evaluating at t = -1:
```
G(-1) = 0.512 - 0.384 + 0.096 - 0.008
      = 0.216
      = P(even) - P(odd)
```

Since P(even) + P(odd) = 1:
- P(even) = (1 + 0.216) / 2 = 0.608
- P(odd) = (1 - 0.216) / 2 = 0.392 ✓

## Conclusion

The formula `shot_error_rate = (1 - (1 - 2×p_round)^N) / 2` comes from:
1. Modeling errors as independent Bernoulli trials per round
2. Assuming shot failure depends on the **parity** (odd/even) of errors
3. Using probability generating functions to sum over odd k

This is a fundamental result in probability theory for the XOR model of error accumulation.
