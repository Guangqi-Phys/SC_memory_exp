# errors_left Display Issue

## Problem

The `errors_left` shown in sinter's progress output is incorrect when using per-task `max_errors` values. The display uses the **global** `max_errors` for all tasks, but each task actually has its own per-task `max_errors` in its `collection_options`.

## Root Cause

In `sinter._collection._collection_manager.CollectionManager.status_message()` (line 464-495):

```python
max_errors = self.collection_options.max_errors  # Global max_errors
max_shots = self.collection_options.max_shots   # Global max_shots

# For each task, calculates:
f'{max_errors - c_errors}'  # Uses GLOBAL max_errors, not per-task!
```

But each task's actual `errors_left` (used for stopping) is calculated correctly from the per-task `max_errors` (line 222-232):

```python
options = self.partial_tasks[k].collection_options.combine(self.collection_options)
errors_left = options.max_errors  # Per-task max_errors (correct)
```

## Example

If you have:
- Task 1: error_rate=0.003, per-task `max_errors = 300`
- Task 2: error_rate=0.009, per-task `max_errors = 900`
- Global `max_errors = 900` (maximum of all per-task values)

**Display shows** (WRONG):
- Task 1: `errors_left = 900 - errors_collected` ❌ (should be 300 - errors_collected)
- Task 2: `errors_left = 900 - errors_collected` ✓ (correct)

**Actual stopping behavior** (CORRECT):
- Task 1: Stops when `errors_collected >= 300` ✓
- Task 2: Stops when `errors_collected >= 900` ✓

## Impact

- **Stopping behavior is CORRECT**: Each task uses its own per-task `max_errors` for stopping
- **Display is INCORRECT**: The progress output shows wrong `errors_left` values for tasks with smaller per-task `max_errors`

## Workaround

Unfortunately, this is a limitation of sinter's display code. The actual stopping behavior is correct, but the progress display uses the global `max_errors` for all tasks.

**Options**:
1. **Accept the display issue**: The stopping behavior is correct, just ignore the display
2. **Use same `max_errors` for all tasks**: Set `BASELINE_MAX_ERRORS` so all tasks have the same `max_errors` (but this defeats the purpose of adaptive scaling)
3. **Monitor actual collected errors**: Check the actual `errors` collected in the final stats, not the `errors_left` in the progress display

## Verification

To verify that stopping behavior is correct, check the final stats:
- Task with error_rate=0.003 should stop around 300 errors (or slightly more due to batching)
- Task with error_rate=0.009 should stop around 900 errors (or slightly more due to batching)

The `errors_left` in the progress display may be wrong, but the actual stopping will be correct.
