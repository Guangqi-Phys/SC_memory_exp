# Parallelization Guide

Complete guide to understanding parallelization in the surface code experiment.

## Table of Contents
1. [Two Levels of Parallelization](#two-levels-of-parallelization)
2. [Resource Usage](#resource-usage)
3. [Batch Processing vs Parallel Processing](#batch-processing-vs-parallel-processing)
4. [When to Use Parallel Windows](#when-to-use-parallel-windows)
5. [NUM_WORKERS and Sliding Window Decoder](#num_workers-and-sliding-window-decoder)

---

## Two Levels of Parallelization

The surface code experiment uses two levels of parallelization:

1. **`NUM_WORKERS`**: Parallel processing of different shots/tasks (sinter level)
2. **`WINDOW_PARALLEL_WORKERS`**: Parallel processing of windows within a single shot (decoder level)

### NUM_WORKERS (Sinter Level)

**What it does**:
- Controls how many **worker processes** sinter uses
- Each worker processes different shots/tasks in parallel
- Uses **multiprocessing** (separate processes, not threads)
- Each process has its own memory space

**Example**:
```python
NUM_WORKERS = 10  # 10 separate Python processes
```

**How it works**:
```
Main Process
├── Worker 1 (Process) → Decodes shots for Task A
├── Worker 2 (Process) → Decodes shots for Task B
├── Worker 3 (Process) → Decodes shots for Task C
├── ...
└── Worker 10 (Process) → Decodes shots for Task J
```

**Each worker**:
1. Receives a task (circuit + decoder)
2. Samples shots from the circuit
3. Decodes shots using the specified decoder (PyMatching or sliding window)
4. Returns statistics

### WINDOW_PARALLEL_WORKERS (Decoder Level)

**What it does**:
- Controls how many CPU cores to use for parallelizing window decoding within each shot
- Uses **threading** (threads within a process)
- Threads share memory within the same process
- Only active when `WINDOW_PARALLEL_WORKERS > 1`

**Example**:
```python
WINDOW_PARALLEL_WORKERS = 1  # Batch processing (default, recommended)
WINDOW_PARALLEL_WORKERS = 4  # Threading for windows (experimental)
```

**How it works**:
- For each shot, all windows are collected
- If `WINDOW_PARALLEL_WORKERS > 1`, windows are split into chunks
- Each chunk is decoded in parallel using threads
- Results are accumulated together

---

## Resource Usage

### Total Concurrent Threads/Processes

If you have:
- `NUM_WORKERS = b` (b workers processing different shots/tasks)
- `WINDOW_PARALLEL_WORKERS = a` (a threads per shot for window parallelization)

**Maximum concurrent resources**: Up to `a × b` threads/processes

However, the actual resource usage depends on the implementation:

### Implementation Details

1. **`NUM_WORKERS` (sinter level)**:
   - Uses **multiprocessing** (separate processes, not threads)
   - Each worker is a separate Python process
   - Processes different shots/tasks in parallel
   - Each process has its own memory space

2. **`WINDOW_PARALLEL_WORKERS` (decoder level)**:
   - Uses **threading** (threads within a process)
   - Threads share memory within the same process
   - Parallelizes window decoding within a single shot
   - Only active when `WINDOW_PARALLEL_WORKERS > 1`

### Actual Resource Usage

**Total resources**:
- **Processes**: `NUM_WORKERS` (b processes)
- **Threads per process**: Up to `WINDOW_PARALLEL_WORKERS` (a threads) when decoding
- **Total threads**: Up to `NUM_WORKERS × WINDOW_PARALLEL_WORKERS` (a × b threads)

**Important notes**:
- Threads are lighter than processes (share memory)
- Not all workers decode simultaneously (depends on task distribution)
- Peak usage occurs when all workers are actively decoding with window parallelization

### Examples

#### Configuration 1: Default
```python
NUM_WORKERS = 10
WINDOW_PARALLEL_WORKERS = 1  # Batch processing (no threading)
```
- **Processes**: 10
- **Threads**: 10 (one per process, no window parallelization)
- **Total**: 10 processes

#### Configuration 2: Window Parallelization
```python
NUM_WORKERS = 10
WINDOW_PARALLEL_WORKERS = 4  # Threading for windows
```
- **Processes**: 10
- **Threads per process**: Up to 4 (when decoding)
- **Total threads**: Up to 40 (10 processes × 4 threads)
- **Peak usage**: When all 10 workers are simultaneously decoding shots with window parallelization

#### Configuration 3: Conservative
```python
NUM_WORKERS = 4
WINDOW_PARALLEL_WORKERS = 2
```
- **Processes**: 4
- **Threads per process**: Up to 2
- **Total threads**: Up to 8 (4 processes × 2 threads)

### Recommendations

**Rule of thumb**: Total concurrent threads should not exceed your CPU cores by too much.

For a system with `N` CPU cores:
- **Optimal**: `NUM_WORKERS × WINDOW_PARALLEL_WORKERS ≤ N`
- **Acceptable**: `NUM_WORKERS × WINDOW_PARALLEL_WORKERS ≤ 2×N` (with hyperthreading)
- **Too many**: `NUM_WORKERS × WINDOW_PARALLEL_WORKERS > 2×N` (context switching overhead)

---

## Batch Processing vs Parallel Processing

### What is Batch Processing?

**Batch processing** means processing multiple items together in a single operation, rather than processing them one at a time (sequentially) or in parallel (using multiple threads/processes).

### In the Context of Sliding Window Decoder

#### Sequential Processing (Before Optimization)

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

#### Batch Processing (Current Default)

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

### How PyMatching's `decode_batch` Works

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

### Why Batch Processing is Usually Faster

#### 1. Optimized Implementation
- PyMatching's `decode_batch` is highly optimized in C++
- Designed specifically for batch operations
- Can use SIMD (Single Instruction, Multiple Data) instructions

#### 2. Better Cache Usage
- All windows processed together stay in CPU cache
- Sequential access patterns are cache-friendly
- Reduces memory bandwidth requirements

#### 3. Less Overhead
- Single function call instead of many
- No thread creation/synchronization overhead
- No data copying between threads

#### 4. Vectorization
- Can process multiple windows with same instructions
- CPU can execute multiple operations in parallel at hardware level
- Better utilization of CPU pipelines

### Performance Comparison

For a typical scenario with 10 windows per shot:

| Method | Time | Overhead | Cache Usage | Recommendation |
|--------|------|----------|-------------|----------------|
| **Batch** | 1.0× | Low | Excellent | ✅ **Best** |
| Sequential | 10× | Medium | Good | ❌ Slow |
| Parallel (4 threads) | 1.5-2× | High | Good | ⚠️ Usually slower |

---

## When to Use Parallel Windows

### Quick Answer

**Usually NO** - Batch processing is still better even with many cores, because:
1. PyMatching's `decode_batch` is already highly optimized
2. You already have parallelization at the `NUM_WORKERS` level (different shots/tasks)
3. Threading overhead often outweighs benefits
4. Better cache usage with batch processing

**But YES** - Parallel processing can help when:
1. You have **many windows per shot** (>20-30)
2. You have **excess CPU cores** (more than `NUM_WORKERS` needs)
3. Each window decoding is **computationally expensive**
4. You want to experiment and benchmark

### Recommendations

#### For Most Cases (Recommended)

```python
NUM_WORKERS = min(CPU_CORES, 10-20)  # Use your cores here
WINDOW_PARALLEL_WORKERS = 1  # Batch processing (fastest)
```

**Why**: 
- Parallelization at the worker level is more effective
- Batch processing is faster for window decoding
- Simpler and more reliable

#### If You Have Many Cores and Want to Experiment

```python
NUM_WORKERS = CPU_CORES // 2  # Leave some cores for window parallelization
WINDOW_PARALLEL_WORKERS = 2-4  # Experiment with this
```

**Then benchmark** to see if it's actually faster!

#### If You Have Many Windows Per Shot (>30)

```python
NUM_WORKERS = CPU_CORES // 2
WINDOW_PARALLEL_WORKERS = 2-4  # Might help with many windows
```

**But still benchmark** - batch processing is often still faster.

### Benchmarking Example

To test which is faster:

```python
# Test 1: Batch processing
WINDOW_PARALLEL_WORKERS = 1
# Run experiment, measure time

# Test 2: Parallel processing
WINDOW_PARALLEL_WORKERS = 4
# Run same experiment, measure time

# Compare results
```

**Expected result**: Batch processing is usually 10-30% faster.

---

## NUM_WORKERS and Sliding Window Decoder

### Important Clarification

**`NUM_WORKERS` is a SINTER parameter, NOT a PyMatching parameter.**

- `NUM_WORKERS` controls how many **worker processes** sinter uses
- Each worker can use PyMatching (or sliding window decoder) to decode shots
- PyMatching itself doesn't have a `NUM_WORKERS` parameter

### What Does NUM_WORKERS = 10 Do?

#### At the Sinter Level

`NUM_WORKERS = 10` means:
- **10 separate Python processes** are created
- Each process is a **worker** that processes shots/tasks independently
- Workers run in **parallel** (using multiprocessing)
- Each worker can decode multiple shots sequentially

### How Sliding Window Decoder Uses PyMatching

#### Inside Each Worker

When a worker uses the sliding window decoder:

1. **Worker receives a shot** (syndrome data)

2. **Sliding window decoder processes the shot**:
   ```python
   # For each shot:
   windows = [window1, window2, window3, ..., windowN]  # All windows for this shot
   
   # Batch all windows together
   batch = stack(windows)  # Shape: (num_windows, num_detectors)
   
   # Call PyMatching's decode_batch ONCE
   results = pymatching.decode_batch(batch)  # Single optimized call
   
   # Accumulate results
   final_prediction = accumulate(results)
   ```

3. **PyMatching's `decode_batch` processes the batch**:
   - Receives all windows for the shot
   - Processes them together (optimized)
   - Returns predictions for all windows

### The Batch Structure

**Each shot** → **One batch** containing all windows for that shot

```
Shot 1:
  Windows: [W1, W2, W3, ..., W10]
  Batch: (10, num_detectors) → PyMatching.decode_batch() → (10, num_observables)

Shot 2:
  Windows: [W1, W2, W3, ..., W10]
  Batch: (10, num_detectors) → PyMatching.decode_batch() → (10, num_observables)

...
```

### Is Each Sliding Window a Batch?

**No!** Each sliding window is **NOT** a separate batch.

**Correct understanding**:
- **All windows for ONE shot** = **ONE batch**
- The batch contains all windows for that shot
- PyMatching processes all windows in the batch together

**Incorrect understanding**:
- ❌ Each window is a separate batch
- ❌ Each window calls PyMatching separately

### Example: NUM_WORKERS = 10, 100 Shots

#### What Happens

1. **10 workers** are created (10 processes)

2. **Shots are distributed** across workers:
   - Worker 1: Shots 1-10
   - Worker 2: Shots 11-20
   - Worker 3: Shots 21-30
   - ...
   - Worker 10: Shots 91-100

3. **Each worker processes its shots**:
   ```
   Worker 1:
     Shot 1: [10 windows] → batch → PyMatching.decode_batch() → result
     Shot 2: [10 windows] → batch → PyMatching.decode_batch() → result
     ...
     Shot 10: [10 windows] → batch → PyMatching.decode_batch() → result
   ```

4. **Each shot uses ONE batch** containing all its windows

#### PyMatching Calls

- **Total shots**: 100
- **Total PyMatching.decode_batch() calls**: 100 (one per shot)
- **Windows per batch**: 10 (all windows for that shot)
- **Workers processing in parallel**: 10

### Key Takeaway

**NUM_WORKERS** = Parallel processing of **different shots** (sinter level)

**Batch processing** = All windows for **one shot** processed together (decoder level)

These are **two different levels** of parallelization:
- `NUM_WORKERS`: Parallel across shots (10 workers → 10 shots in parallel)
- Batch processing: All windows per shot together (10 windows → 1 batch)

They work together but are independent optimizations!

---

## Summary

1. **Two levels of parallelization**: `NUM_WORKERS` (shots/tasks) and `WINDOW_PARALLEL_WORKERS` (windows)
2. **Resource usage**: Up to `NUM_WORKERS × WINDOW_PARALLEL_WORKERS` concurrent threads
3. **Batch processing is usually faster**: PyMatching's optimizations beat threading overhead
4. **Start with defaults**: `NUM_WORKERS = 10`, `WINDOW_PARALLEL_WORKERS = 1`
5. **Only use parallel windows if**: You have many windows (>30) and excess CPU cores, and have benchmarked that it's faster
