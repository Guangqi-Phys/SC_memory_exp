# XOR Model Parity Dependence Issue

## The Critical Problem

The XOR model formula has a **fundamental parity dependence** when `p_round > 0.5`:

```
shot_error_rate = (1 - (1 - 2×p_round)^N) / 2
```

### The Issue

When `p_round > 0.5`:
- `(1 - 2×p_round) < 0` (negative)
- **Even N**: `negative^even = positive` → `shot_error_rate < 0.5`
- **Odd N**: `negative^odd = negative` → `shot_error_rate > 0.5`

### Example

For `p_round = 0.9`:
- **N = 100 (even)**: `shot_error_rate ≈ 0.4999999999` (< 0.5)
- **N = 101 (odd)**: `shot_error_rate ≈ 0.5000000001` (> 0.5)

## Implications

### 1. Reverse Conversion Ambiguity

When converting `shot_error_rate → p_round`:
- For `shot_error_rate > 0.5` with **even N**: The conversion function may not find a valid solution with `p_round < 0.5`
- For `shot_error_rate > 0.5` with **odd N**: The conversion function can find a solution with `p_round > 0.5`

### 2. Inconsistent Behavior

The same `shot_error_rate` value can map to **completely different** `p_round` values depending on whether N is even or odd:
- Even N: May give low `p_round` (< 0.5)
- Odd N: May give high `p_round` (> 0.5)

### 3. Physical Interpretation

This creates a problem for quantum error correction:
- Your physical error rates are low (0.003-0.006)
- Logical per-round rates should be similar (low, < 0.1)
- But the XOR model can give high per-round rates (> 0.9) for odd N when `shot_error_rate > 0.5`
- This is physically unrealistic

## Why This Happens

The XOR model assumes errors accumulate via XOR (exclusive OR):
- Shot fails if **odd number** of rounds have errors
- With `p_round > 0.5`, almost every round has an error
- **Even N**: Even number of errors → shot succeeds (XOR = 0)
- **Odd N**: Odd number of errors → shot fails (XOR = 1)
- This creates the parity dependence

## Solutions

### Solution 1: Avoid High Shot Error Rates (Recommended)

Design experiments so `shot_error_rate < 0.5`:
- Use fewer rounds
- Use lower physical error rates  
- Use larger code distances

This avoids the parity issue entirely.

### Solution 2: Use Even Number of Rounds

If you must have `shot_error_rate > 0.5`, use **even N**:
- Even N gives `shot_error_rate < 0.5` even for high `p_round`
- This makes the conversion more stable
- But this is still not ideal - you should avoid high shot rates

### Solution 3: Accept the Limitation

Recognize that:
- The XOR model has fundamental limitations
- For `shot_error_rate > 0.5`, the model may not be appropriate
- Consider if the code is actually failing (high per-round rate might be correct)
- But this is usually inconsistent with low physical error rates

## Mathematical Details

The XOR formula:
```
shot_error_rate = (1 - (1 - 2×p_round)^N) / 2
```

For `p_round > 0.5`:
- `(1 - 2×p_round) < 0`
- `(1 - 2×p_round)^N`:
  - If N is even: positive (small, close to 0)
  - If N is odd: negative (small magnitude, close to 0)

So:
- Even N: `shot_error_rate = (1 - small_positive) / 2 ≈ 0.5` (from below)
- Odd N: `shot_error_rate = (1 - small_negative) / 2 ≈ 0.5` (from above)

## Conclusion

The XOR model has a **fundamental parity dependence** that makes it unreliable when:
1. `shot_error_rate > 0.5`
2. `p_round > 0.5`

**Best practice**: Always design experiments to keep `shot_error_rate < 0.5` to avoid these issues.
