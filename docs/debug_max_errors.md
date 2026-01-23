# Debugging MAX_ERRORS = 1000 Issue

## Problem

The decoder is showing `max_errors = 1000` even though `calculate_max_errors(0.003, 20)` should return 300.

## Possible Causes

### 1. Command-Line Override

If you're passing `--max-errors 1000` on the command line, it will override the per-task calculated values.

**Check**: Look at your command line arguments. Remove `--max-errors` if present.

### 2. Default MAX_ERRORS Constant

The default `MAX_ERRORS` constant is calculated at module load:
```python
MAX_ERRORS = calculate_max_errors(0.005, TAU_ROUNDS)
```

With current settings:
- BASELINE_MAX_ERRORS = 100
- BASELINE_ERROR_RATE = 0.001
- For error_rate = 0.005: MAX_ERRORS = 100 × (0.005 / 0.001) = 500

So the default should be 500, not 1000.

**Check**: The default is only used as a fallback if tasks don't have `collection_options`.

### 3. Per-Task Values Are Correct

The tasks ARE created with the correct per-task `max_errors` values in their `collection_options`. Sinter uses `min(global_max_errors, per_task_max_errors)` for each task.

**Check**: The per-task values should be:
- error_rate=0.003: max_errors=300
- error_rate=0.009: max_errors=900

### 4. Global Max Errors Display

The `experiment_runner` prints the global `max_errors` which is the maximum of all per-task values. This is just for display - each task still uses its own value.

**Check**: Look for the message:
```
Using adaptive MAX_ERRORS/MAX_SHOTS per task (based on error_rate and tau_rounds)
```

If you see this, per-task values are being used.

## How to Verify

1. **Check the actual task collection_options**:
   ```python
   from surface_code_experiment.src.tasks import create_surface_code_tasks
   from surface_code_experiment.config.experiment_config import TAU_ROUNDS
   
   tasks = create_surface_code_tasks([27], [0.003, 0.009], TAU_ROUNDS, True)
   for task in tasks:
       print(f"error_rate={task.json_metadata['error_rate']}: "
             f"max_errors={task.collection_options.max_errors}")
   ```

2. **Check if you're passing --max-errors**:
   - Remove `--max-errors` from command line
   - Or set it to a very large value (e.g., `--max-errors 1000000`) so it doesn't limit per-task values

3. **Check the experiment output**:
   - Look for "Using adaptive MAX_ERRORS/MAX_SHOTS per task"
   - This confirms per-task values are being used

## Solution

If you're seeing 1000, it's likely because:
1. You're passing `--max-errors 1000` on the command line
2. Or there's a cached Python module (restart Python/interpreter)

The per-task calculated values (300 for 0.003, 900 for 0.009) should be used automatically if tasks have `collection_options`.
