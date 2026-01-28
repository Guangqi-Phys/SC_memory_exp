# NUM_WORKERS and Sliding Window Decoder

## Important Clarification

**`NUM_WORKERS` is a SINTER parameter, NOT a PyMatching parameter.**

- `NUM_WORKERS` controls how many **worker processes** sinter uses
- Each worker can use PyMatching (or sliding window decoder) to decode shots
- PyMatching itself doesn't have a `NUM_WORKERS` parameter

## What Does NUM_WORKERS = 10 Do?

### At the Sinter Level

`NUM_WORKERS = 10` means:
- **10 separate Python processes** are created
- Each process is a **worker** that processes shots/tasks independently
- Workers run in **parallel** (using multiprocessing)
- Each worker can decode multiple shots sequentially

### How It Works

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

## Does NUM_WORKERS Optimize for Sliding Window Decoder?

**No, `NUM_WORKERS` doesn't specifically optimize for sliding window decoder.**

`NUM_WORKERS` is **decoder-agnostic**:
- It works the same for PyMatching, sliding window decoder, or any other decoder
- It just controls how many workers process tasks in parallel
- The optimization happens **inside** each decoder

## How Sliding Window Decoder Uses PyMatching

### Inside Each Worker

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

## Is Each Sliding Window a Batch?

**No!** Each sliding window is **NOT** a separate batch.

**Correct understanding**:
- **All windows for ONE shot** = **ONE batch**
- The batch contains all windows for that shot
- PyMatching processes all windows in the batch together

**Incorrect understanding**:
- ❌ Each window is a separate batch
- ❌ Each window calls PyMatching separately

## Example: NUM_WORKERS = 10, 100 Shots

### What Happens

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

### PyMatching Calls

- **Total shots**: 100
- **Total PyMatching.decode_batch() calls**: 100 (one per shot)
- **Windows per batch**: 10 (all windows for that shot)
- **Workers processing in parallel**: 10

## Does NUM_WORKERS Help with Sliding Window Decoder?

**Yes, but indirectly:**

1. **Parallel processing of shots**:
   - 10 workers process different shots in parallel
   - This speeds up overall experiment time
   - Works for any decoder (PyMatching, sliding window, etc.)

2. **No specific optimization for windows**:
   - `NUM_WORKERS` doesn't optimize window processing
   - Window batching is handled **inside** the sliding window decoder
   - Each worker still processes shots one at a time

3. **Resource usage**:
   - 10 workers = 10 processes
   - Each process can use multiple CPU cores (if available)
   - But each shot still uses batch processing for its windows

## Summary

### NUM_WORKERS
- ✅ Controls number of **worker processes** (sinter level)
- ✅ Processes **different shots/tasks** in parallel
- ✅ Works for **any decoder** (not specific to sliding window)
- ❌ Does NOT optimize window processing
- ❌ Does NOT control PyMatching batching

### Sliding Window Decoder
- ✅ Uses **batch processing** internally (all windows per shot)
- ✅ Calls PyMatching's `decode_batch()` **once per shot**
- ✅ Each shot = one batch containing all windows
- ❌ Each window is NOT a separate batch

### PyMatching
- ✅ Has optimized `decode_batch()` function
- ✅ Processes multiple items (windows) together
- ✅ Used by sliding window decoder for batching windows
- ❌ Does NOT have a NUM_WORKERS parameter

## Key Takeaway

**NUM_WORKERS** = Parallel processing of **different shots** (sinter level)

**Batch processing** = All windows for **one shot** processed together (decoder level)

These are **two different levels** of parallelization:
- `NUM_WORKERS`: Parallel across shots (10 workers → 10 shots in parallel)
- Batch processing: All windows per shot together (10 windows → 1 batch)

They work together but are independent optimizations!
