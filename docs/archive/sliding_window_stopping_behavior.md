# Sliding Window Decoder: How Stopping Works

## Your Question

> "The max error is set for max error of logicals, but if I use sliding window decoder, the real logical error can be only checked in the end round, how the previous sliding window decoder stop? is it stop according to it's own logical error?"

## Answer: One Error Count Per Shot, Not Per Window

**The sliding window decoder returns ONE prediction per shot**, not one per window. Sinter compares this single prediction with the actual observable to determine if there's a logical error. The stopping behavior is **correct** - it stops based on the final logical error per shot, not per-window errors.

## How It Works

### 1. Sliding Window Decoder Processing

For each shot, the sliding window decoder:
1. Processes ALL windows (e.g., windows 0-100, 100-200, 200-300, ...)
2. Decodes each window independently using PyMatching
3. Accumulates predictions from all windows by XORing them together
4. Returns **ONE accumulated prediction** for the entire shot

**Key code** (lines 246-258 of `sliding_window_decoder.py`):
```python
# Store accumulated predictions for this shot
# IMPORTANT: This accumulated correction represents the total logical observable prediction
# from all windows. It should be compared with the actual logical observable measurement
# from the final round (round num_rounds-1) to determine if a logical error occurred.
if self.num_observables == 1:
    predictions[shot_idx, 0] = accumulated_parity  # ONE prediction per shot
else:
    predictions[shot_idx] = accumulated_predictions  # ONE prediction per shot
```

### 2. Sinter's Error Counting

Sinter receives the decoder's predictions and:
1. Compares each shot's prediction with the actual observable
2. Counts **one error per shot** if prediction ≠ actual
3. Stops when `errors_collected >= MAX_ERRORS`

**Important**: Sinter doesn't know or care about windows. It just sees:
- Input: Detector events (one per shot)
- Output: Observable predictions (one per shot)
- Error: Prediction ≠ Actual (one count per shot)

### 3. Why This Is Correct

The sliding window is an **internal implementation detail** of the decoder. From sinter's perspective:
- It's just another decoder
- Takes detector events → returns observable predictions
- One prediction per shot → one error count per shot

The fact that the decoder internally processes multiple windows doesn't change this:
- **One shot** → **One prediction** → **One error count** (0 or 1)

## Example

**Shot with 1000 rounds, 10 windows (100 rounds each)**:

1. Sliding window decoder processes:
   - Window 1 (rounds 0-100): prediction = 1
   - Window 2 (rounds 100-200): prediction = 0
   - Window 3 (rounds 200-300): prediction = 1
   - ... (7 more windows)
   - Accumulated: `1 ^ 0 ^ 1 ^ ... = 0` (final prediction)

2. Sinter compares:
   - Decoder prediction: `0`
   - Actual observable: `1`
   - Result: **1 error** (one count for this shot)

3. Error counting:
   - This shot contributes **1 error** to the total
   - Not 10 errors (one per window)
   - Not errors from individual windows

## Verification

You can verify this by checking:
1. **Number of predictions returned**: Should equal number of shots, not number of windows
2. **Error counting**: Each shot contributes 0 or 1 to the error count
3. **Stopping behavior**: Stops when total errors (across all shots) >= MAX_ERRORS

## Summary

- ✅ **Stopping is correct**: Based on final logical error per shot
- ✅ **One error count per shot**: Not per window
- ✅ **Windows are internal**: Sinter doesn't see them
- ✅ **MAX_ERRORS applies to shots**: Not to windows

The sliding window decoder processes all windows internally and returns one accumulated prediction per shot. Sinter then compares this with the actual observable to count errors. The stopping behavior is exactly as intended - it stops when you've collected enough logical errors (one per shot), regardless of how many windows were processed internally.
