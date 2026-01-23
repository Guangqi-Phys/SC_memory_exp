# Batch Processing Explained

## What is Batch Processing?

**Batch processing** means processing multiple items together in a single operation, rather than processing them one at a time (sequentially) or in parallel (using multiple threads/processes).

## In the Context of Sliding Window Decoder

### Sequential Processing (Before Optimization)

**Old approach** - Process windows one at a time:
```python
for window in windows:
    result = decode(window)  # One window at a time
    accumulate(result)
```

**Problems**:
- Each window decoding is a separate function call
- Overhead from multiple function calls
- Can't take advantage of vectorization/optimization
- Slower for many windows

### Batch Processing (Current Default)

**Current approach** - Process all windows together:
```python
# Collect all windows
all_windows = [window1, window2, window3, ..., windowN]

# Process all at once in a single batch
all_results = decode_batch(all_windows)  # All windows in one call

# Accumulate results
accumulate(all_results)
```

**Benefits**:
- Single function call for all windows
- PyMatching can optimize the batch internally
- Better cache usage (all data processed together)
- Vectorization opportunities
- Usually faster than sequential or parallel processing

## How PyMatching's `decode_batch` Works

PyMatching's `decode_batch` function is specifically designed to process multiple syndromes efficiently:

1. **Input**: A 2D array of shape `(num_windows, num_detectors)`
   - Each row is one window's syndrome
   - All windows processed together

2. **Internal Optimization**:
   - Can reuse graph structures
   - Better memory access patterns
   - Vectorized operations where possible
   - Optimized C++ backend

3. **Output**: A 2D array of shape `(num_windows, num_observables)`
   - Each row is the prediction for one window
   - All results returned together

## Example

### Scenario: 10 Windows per Shot

**Sequential Processing**:
```python
results = []
for i in range(10):
    result = matcher.decode_batch(window[i])  # 10 separate calls
    results.append(result)
# Time: ~10 × t (where t is time per window)
```

**Batch Processing**:
```python
all_windows = stack([window[0], window[1], ..., window[9]])  # Shape: (10, num_detectors)
all_results = matcher.decode_batch(all_windows)  # 1 call for all 10
# Time: ~1.5 × t (much faster due to optimization)
```

**Parallel Processing** (with threading):
```python
# Split into chunks, process in parallel
chunk1 = stack([window[0], window[1], window[2]])  # 3 windows
chunk2 = stack([window[3], window[4], window[5]])  # 3 windows
chunk3 = stack([window[6], window[7], window[8]])  # 3 windows
chunk4 = stack([window[9]])  # 1 window

# Process chunks in parallel using threads
results = parallel_decode([chunk1, chunk2, chunk3, chunk4])
# Time: ~2-3 × t (overhead from threading)
```

## Why Batch Processing is Usually Faster

### 1. **Optimized Implementation**
- PyMatching's `decode_batch` is highly optimized in C++
- Designed specifically for batch operations
- Can use SIMD (Single Instruction, Multiple Data) instructions

### 2. **Better Cache Usage**
- All windows processed together stay in CPU cache
- Sequential access patterns are cache-friendly
- Reduces memory bandwidth requirements

### 3. **Less Overhead**
- Single function call instead of many
- No thread creation/synchronization overhead
- No data copying between threads

### 4. **Vectorization**
- Can process multiple windows with same instructions
- CPU can execute multiple operations in parallel at hardware level
- Better utilization of CPU pipelines

## When to Use Each Approach

### Batch Processing (`WINDOW_PARALLEL_WORKERS = 1`) - **Recommended**

**Use when**:
- You have any number of windows
- You want the fastest performance
- You want minimal resource usage
- You have limited CPU cores

**Why**: Usually the fastest due to PyMatching's optimizations

### Parallel Processing (`WINDOW_PARALLEL_WORKERS > 1`)

**Use when**:
- You have many windows (>20) per shot
- You have excess CPU cores available
- You want to experiment with parallelization
- Batch processing is not fast enough (rare)

**Why**: Can help when you have many windows, but usually slower due to overhead

## Code Example

### Batch Processing Implementation

```python
# Collect all window syndromes
window_syndrome_vectors = []
for window in windows:
    syndrome_vector = prepare_syndrome(window)
    window_syndrome_vectors.append(syndrome_vector)

# Stack into batch: shape (num_windows, num_detectors)
batch_syndromes = np.stack(window_syndrome_vectors, axis=0)

# Decode all windows in ONE batch call
predicted_observables_batch = self.matcher.decode_batch(batch_syndromes)
# Shape: (num_windows, num_observables)

# Accumulate results
for window_pred in predicted_observables_batch:
    accumulated_parity ^= window_pred[0]
```

### Parallel Processing Implementation (for comparison)

```python
# Split into chunks
chunks = split_windows_into_chunks(windows, num_workers=4)

# Process chunks in parallel using threads
results = []
with ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(decode_chunk, chunk) for chunk in chunks]
    for future in futures:
        results.extend(future.result())

# Accumulate results
for window_pred in results:
    accumulated_parity ^= window_pred[0]
```

## Performance Comparison

For a typical scenario with 10 windows per shot:

| Method | Time | Overhead | Cache Usage | Recommendation |
|--------|------|----------|-------------|----------------|
| **Batch** | 1.0× | Low | Excellent | ✅ **Best** |
| Sequential | 10× | Medium | Good | ❌ Slow |
| Parallel (4 threads) | 1.5-2× | High | Good | ⚠️ Usually slower |

## Summary

**Batch processing** = Process all windows together in a single optimized operation

**Key points**:
- ✅ Usually the fastest method
- ✅ Minimal resource usage
- ✅ Leverages PyMatching's optimizations
- ✅ Better cache usage
- ✅ Default behavior (`WINDOW_PARALLEL_WORKERS = 1`)

**When to use**: Almost always! Only use parallel processing if you have many windows and excess CPU cores, and want to experiment.
