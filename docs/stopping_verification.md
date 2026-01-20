# Sinter Stopping Behavior Verification

## How Sinter Stops

Sinter stops collecting statistics when **EITHER** of these conditions is met:
1. `max_shots` is reached (all shots have been taken)
2. `max_errors` is reached (target number of errors collected)

The stopping logic is implemented in:
- `Stim/glue/sample/src/sinter/_collection/_collection_manager.py` line 67:
  ```python
  def is_completed(self) -> bool:
      return self.shots_left <= 0 or self.errors_left <= 0
  ```

- `Stim/glue/sample/src/sinter/_collection/_collection_worker_state.py` line 214:
  ```python
  if self.current_error_cutoff is not None and self.current_error_cutoff <= 0:
      return self.flush_results()  # Stop when error target reached
  ```

## Verification

The decoder **will stop** when:
- ✅ `max_errors` is reached (or slightly exceeded due to batching)
- ✅ `max_shots` is reached (or slightly exceeded due to batching)
- ✅ Either condition is met (whichever comes first)

## Important Note

There's a cap relationship:
```python
errors_left = min(errors_left, shots_left)
```

This means:
- If `max_shots < max_errors`: `errors_left` is capped at `shots_left`, so both reach 0 together
- If `max_errors < max_shots`: `errors_left` hits 0 first, task stops (even if `shots_left > 0`)

## Example

For `error_rate=0.007`, `tau_rounds=80`:
- `MAX_ERRORS = 97,999`
- `MAX_SHOTS = 9,799,900`
- Ratio: 100:1

At high error rates, shot error rate might be very high (>0.5), so:
- We'll likely hit `MAX_ERRORS` first (collecting ~98,000 errors)
- Task stops when `errors_left <= 0`
- `shots_left` might still be positive (e.g., 8,000,000 shots remaining)

**This is correct behavior** - the task stops when the error target is reached, not when shots run out.
