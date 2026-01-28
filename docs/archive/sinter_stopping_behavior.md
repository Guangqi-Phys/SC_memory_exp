# Sinter Stopping Behavior: Why errors_left May Not Reach Zero

## Overview

When using `sinter.collect()`, the decoder may stop before `errors_left` reaches exactly zero. This is **normal behavior** and happens for several reasons.

## How Sinter Stops

Sinter stops when **EITHER** of these conditions is met:
1. `max_shots` is reached (hard limit on number of shots)
2. `max_errors` is reached (target number of errors collected)

**Important**: Sinter stops as soon as the first condition is met, whichever comes first.

## Why errors_left May Not Reach Zero

### 1. max_shots Reached First

If `max_shots` is reached before `max_errors`, then `errors_left` will not reach zero.

**Example**:
- `max_errors = 50,000`
- `max_shots = 5,000,000`
- At low error rates (e.g., 0.001), shot error rate might be ~0.01 (1%)
- To collect 50,000 errors, you'd need ~5,000,000 shots
- But if you only collect 4,000,000 shots (hitting `max_shots` first), you might only have 40,000 errors
- Result: `errors_left = 10,000` (not zero)

**This is normal** - you've hit the shot limit before reaching the error target.

### 2. Batching Causes Overshoot

Sinter processes shots in batches for efficiency. Due to batching:
- You might collect **slightly more errors** than `max_errors` before stopping
- The actual number of errors collected may be `max_errors + batch_size` in the worst case
- `errors_left` can go **negative** (but the task still stops)

**Example**:
- `max_errors = 50,000`
- Batch size = 1,000 shots
- If a batch contains 1,000 errors, you might collect 51,000 errors total
- Result: `errors_left = -1,000` (negative, but task stops)

**This is normal** - batching is an optimization that can cause slight overshoot.

### 3. errors_left is Capped by shots_left

In the code, there's this line:
```python
errors_left = min(errors_left, shots_left)
```

This means `errors_left` is capped by `shots_left`. If `shots_left` is small, `errors_left` will also be small, even if `max_errors` is large.

## Is This a Problem?

**No, this is expected behavior.** The important thing is:
- You've collected enough data for statistical analysis
- The stopping criteria (either `max_shots` or `max_errors`) was met
- The slight overshoot from batching is negligible compared to the total errors collected

## How to Ensure errors_left Reaches Zero

If you want to ensure `errors_left` reaches zero (or close to it):

1. **Set max_shots high enough**: Make sure `max_shots` is large enough to reach `max_errors`
   - At low error rates: `max_shots` should be much larger than `max_errors`
   - At high error rates: `max_shots` can be closer to `max_errors`

2. **Accept slight overshoot**: Due to batching, you might collect slightly more errors than `max_errors`. This is fine and doesn't affect statistical validity.

3. **Check which limit was hit**: Look at the final stats:
   - If `stat.shots >= max_shots`: You hit the shot limit first
   - If `stat.errors >= max_errors`: You hit the error limit first (or slightly exceeded it due to batching)

## Example

For `error_rate=0.007` with `tau_rounds=80`:
- `MAX_ERRORS ≈ 392,000`
- `MAX_SHOTS ≈ 39,200,000`
- Ratio: 100:1

At this error rate, shot error rate might be very high (>0.99), so:
- You'll likely hit `MAX_ERRORS` first (collecting ~392,000 errors)
- You might collect slightly more due to batching (e.g., 393,000 errors)
- `errors_left` might be slightly negative, but this is normal

## Why Both Might Not Reach Zero

If you're seeing that **both** `shots_left` and `errors_left` are not reaching zero, this is also normal. Here's why:

### The Cap Relationship

In the code, there's this important line:
```python
errors_left = min(errors_left, shots_left)
```

This means `errors_left` is **capped** by `shots_left`. So:
- If `max_shots < max_errors`, then `errors_left` is set to `shots_left`
- When `shots_left` reaches 0, `errors_left` will also be 0 (or slightly negative due to batching)
- When `errors_left` reaches 0 first (due to batching overshoot), `shots_left` might still be positive

### The OR Condition

The task stops when **EITHER** condition is met:
```python
is_completed() = shots_left <= 0 OR errors_left <= 0
```

So:
- If `errors_left` hits 0 first (or goes negative), the task stops even if `shots_left > 0`
- If `shots_left` hits 0 first, the task stops even if `errors_left > 0` (though it will also be 0 due to the cap)

### Example Scenario

For `error_rate=0.007`, `tau_rounds=80`:
- `MAX_ERRORS ≈ 392,000`
- `MAX_SHOTS ≈ 39,200,000`
- Ratio: 100:1

At high error rates, you'll likely hit `MAX_ERRORS` first:
- You collect ~392,000 errors (or slightly more due to batching)
- `errors_left` goes to 0 (or negative)
- Task stops
- `shots_left` might still be positive (e.g., 38,000,000 shots remaining)

**This is normal!** The task stopped because it reached the error target, not because it ran out of shots.

## Conclusion

**It's normal for `errors_left` and/or `shots_left` to not reach exactly zero.** This happens because:
1. Sinter stops when EITHER `max_shots` OR `max_errors` is reached (whichever comes first)
2. Batching can cause slight overshoot
3. `errors_left` is capped by `shots_left`, creating a relationship between them
4. The task stops as soon as one limit is reached, even if the other is still positive

The important thing is that you've collected sufficient data for statistical analysis, which is what matters for your experiments.
