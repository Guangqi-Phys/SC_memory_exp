# Parallelization Resource Usage

## Overview

The surface code experiment uses two levels of parallelization:
1. **`NUM_WORKERS`**: Parallel processing of different shots/tasks (sinter level)
2. **`WINDOW_PARALLEL_WORKERS`**: Parallel processing of windows within a single shot (decoder level)

## Resource Calculation

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

## Example

### Configuration 1: Default
```python
NUM_WORKERS = 10
WINDOW_PARALLEL_WORKERS = 1  # Batch processing (no threading)
```
- **Processes**: 10
- **Threads**: 10 (one per process, no window parallelization)
- **Total**: 10 processes

### Configuration 2: Window Parallelization
```python
NUM_WORKERS = 10
WINDOW_PARALLEL_WORKERS = 4  # Threading for windows
```
- **Processes**: 10
- **Threads per process**: Up to 4 (when decoding)
- **Total threads**: Up to 40 (10 processes × 4 threads)
- **Peak usage**: When all 10 workers are simultaneously decoding shots with window parallelization

### Configuration 3: Conservative
```python
NUM_WORKERS = 4
WINDOW_PARALLEL_WORKERS = 2
```
- **Processes**: 4
- **Threads per process**: Up to 2
- **Total threads**: Up to 8 (4 processes × 2 threads)

## Recommendations

### CPU Cores vs. Workers

**Rule of thumb**: Total concurrent threads should not exceed your CPU cores by too much.

For a system with `N` CPU cores:
- **Optimal**: `NUM_WORKERS × WINDOW_PARALLEL_WORKERS ≤ N`
- **Acceptable**: `NUM_WORKERS × WINDOW_PARALLEL_WORKERS ≤ 2×N` (with hyperthreading)
- **Too many**: `NUM_WORKERS × WINDOW_PARALLEL_WORKERS > 2×N` (context switching overhead)

### Why Batch Processing is Usually Faster

When `WINDOW_PARALLEL_WORKERS = 1`:
- Uses PyMatching's optimized batch processing
- Better cache usage (all windows processed together)
- No threading overhead
- Usually faster than parallelization

**Recommendation**: Keep `WINDOW_PARALLEL_WORKERS = 1` unless you have:
- Many windows per shot (>20)
- Excess CPU cores available
- Want to experiment with parallelization

## System Resource Monitoring

To check your system's CPU cores:
```bash
# Linux/Mac
nproc
# or
sysctl -n hw.ncpu

# Python
import os
print(os.cpu_count())
```

To monitor resource usage during experiments:
```bash
# Monitor CPU usage
top
# or
htop

# Monitor threads
ps -eLf | grep python
```

## Summary

**Answer to your question**: Yes, if `WINDOW_PARALLEL_WORKERS = a` and `NUM_WORKERS = b`, you could potentially have up to `a × b` concurrent threads when all workers are actively decoding with window parallelization enabled.

**However**:
- `NUM_WORKERS` uses processes (heavier)
- `WINDOW_PARALLEL_WORKERS` uses threads (lighter, within processes)
- Peak usage only occurs when all workers decode simultaneously
- Batch processing (`WINDOW_PARALLEL_WORKERS = 1`) is usually faster and uses fewer resources

**Best practice**: Start with `WINDOW_PARALLEL_WORKERS = 1` and only increase if you have excess CPU cores and many windows per shot.
