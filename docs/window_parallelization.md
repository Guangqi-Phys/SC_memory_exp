# Window Parallelization in Sliding Window Decoder

## Overview

The sliding window decoder has been optimized to process all windows for a shot in parallel by batching them together and using PyMatching's optimized `decode_batch` function.

## How It Works

### Before (Sequential Processing)

Previously, windows were decoded one at a time in a loop:

```python
while recording_start_round < self.num_rounds:
    # ... prepare window syndrome ...
    decode_2d = decode_syndrome_vector.reshape(1, -1)
    predicted_observables = self.matcher.decode_batch(decode_2d)  # One window at a time
    accumulated_parity ^= window_parity_flip
    # ... move to next window ...
```

**Problem**: Each window decoding is independent, but we process them sequentially, which is inefficient.

### After (Batch Processing)

Now, we collect all window syndromes first, then decode them all at once:

```python
# Step 1: Collect all window syndromes
window_syndrome_vectors = []
while recording_start_round < self.num_rounds:
    # ... prepare window syndrome ...
    window_syndrome_vectors.append(decode_syndrome_vector)
    # ... move to next window ...

# Step 2: Decode all windows in one batch
batch_syndromes = np.stack(window_syndrome_vectors, axis=0)  # (num_windows, num_detectors)
predicted_observables_batch = self.matcher.decode_batch(batch_syndromes)  # All windows at once

# Step 3: Accumulate results
for window_pred in predicted_observables_batch:
    accumulated_parity ^= window_parity_flip
```

## Benefits

1. **Leverages PyMatching's Optimization**: PyMatching's `decode_batch` is highly optimized for batch processing, with better cache usage and vectorization.

2. **No Overhead**: Unlike multiprocessing/threading, there's no overhead from process/thread creation, synchronization, or data serialization.

3. **Better Memory Locality**: All window syndromes are processed together, improving cache hit rates.

4. **Simpler Code**: No need for complex parallelization primitives - just batch the operations.

## Performance Impact

For a shot with `N` windows:
- **Before**: `N` separate calls to `decode_batch` (one per window)
- **After**: 1 call to `decode_batch` with `N` windows

**Expected speedup**: 2-5× for typical configurations (depends on number of windows and window size).

## Example

For a circuit with 1000 rounds, `n_sliding_window=100`, `n_overlap=0`:
- **Number of windows**: 10
- **Before**: 10 separate `decode_batch` calls
- **After**: 1 `decode_batch` call with 10 windows

## Why Not Multiprocessing/Threading?

While we could use Python's `multiprocessing` or `threading` to parallelize window decoding, batch processing is better because:

1. **PyMatching is already optimized**: The C++ backend of PyMatching is highly optimized for batch operations.

2. **Lower overhead**: No need to serialize/deserialize data, create processes/threads, or manage synchronization.

3. **Better cache usage**: Batch processing keeps data in cache, while multiprocessing would require data copying.

4. **GIL limitations**: Python's Global Interpreter Lock (GIL) limits true parallelism in threading for CPU-bound tasks.

## Implementation Details

The parallelization happens at the **per-shot level**:
- For each shot, all windows are batched together
- Shots are still processed sequentially (or in parallel by sinter's worker system)
- This is the optimal level for parallelization because:
  - Windows within a shot are independent
  - Batch size is predictable (number of windows per shot)
  - No need for complex load balancing

## Future Optimizations

Potential further optimizations:
1. **Batch across shots**: If we process multiple shots at once, we could batch windows across shots too
2. **GPU acceleration**: PyMatching could potentially use GPU for very large batches
3. **Async processing**: Overlap window preparation with decoding (though batch processing already achieves most of this benefit)
