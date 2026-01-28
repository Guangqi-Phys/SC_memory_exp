# Documentation Index

This directory contains consolidated documentation organized by topic. Start here to find what you need.

## 📚 Main Documents

### 1. [MAX_ERRORS_and_Statistical_Precision.md](MAX_ERRORS_and_Statistical_Precision.md) ⭐ **START HERE**
Complete guide to understanding how MAX_ERRORS relates to error rates, rounds, and statistical confidence.

**Contents**:
- Statistical precision: Error rate vs MAX_ERRORS
- Why MAX_ERRORS scales with error rate
- Should MAX_ERRORS scale with rounds? (Yes! Your insight was correct)
- MAX_ERRORS vs MAX_SHOTS scaling
- Recommended values for different error rates

### 2. [Plotting_and_Uncertainty.md](Plotting_and_Uncertainty.md)
Complete guide to understanding plots, uncertainty regions, and how to reduce uncertainty.

**Contents**:
- Reducing uncertainty in plots (`highlight_max_likelihood_factor`)
- Why uncertainty region position changes (above/below the line)
- Zero errors and high uncertainty
- **High uncertainty when shot rate ≈ 0.5** (singularity near p_shot = 0.5; see [Singularity_Near_Half_Shot_Rate.md](Singularity_Near_Half_Shot_Rate.md))
- Shot errors vs per-round errors
- Understanding `failure_units_per_shot_func`

### 3. [Sinter_Stopping_Behavior.md](Sinter_Stopping_Behavior.md)
Complete guide to understanding how sinter stops experiments.

**Contents**:
- How sinter stops (max_shots vs max_errors)
- Why errors_left may not reach zero
- errors_left display issue
- Sliding window decoder and stopping

### 4. [Sliding_Window_Decoder.md](sliding_window_decoder_documentation.md)
Complete algorithm explanation of the sliding window decoder.

**Contents**:
- Prerequisites: Understanding the basics
- Overview of the algorithm
- Detailed implementation explanation
- Optimizations (parity flip tracking, batch processing)

### 5. [Parallelization_Guide.md](Parallelization_Guide.md)
Complete guide to understanding parallelization in the surface code experiment.

**Contents**:
- Two levels of parallelization (NUM_WORKERS vs WINDOW_PARALLEL_WORKERS)
- Resource usage and recommendations
- Batch processing vs parallel processing
- When to use parallel windows
- NUM_WORKERS and sliding window decoder

### 6. [Concepts_and_Terminology.md](Concepts_and_Terminology.md)
Essential concepts and terminology for understanding the surface code experiment.

**Contents**:
- What is a shot in Stim? (shot = sample)
- Understanding `failure_units_per_shot_func`
- Key terminology

## 🎯 Quick Start Guides

**New to the project?** Read these in order:
1. [Concepts_and_Terminology.md](Concepts_and_Terminology.md) - Basic concepts
2. [MAX_ERRORS_and_Statistical_Precision.md](MAX_ERRORS_and_Statistical_Precision.md) - How MAX_ERRORS works
3. [Sliding_Window_Decoder.md](sliding_window_decoder_documentation.md) - How decoding works
4. [Plotting_and_Uncertainty.md](Plotting_and_Uncertainty.md) - How to improve plots

**Having issues?** Check:
- [Sinter_Stopping_Behavior.md](Sinter_Stopping_Behavior.md) - Why experiments stop
- [Plotting_and_Uncertainty.md](Plotting_and_Uncertainty.md) - Display problems

**Want to understand scaling?** Read:
- [MAX_ERRORS_and_Statistical_Precision.md](MAX_ERRORS_and_Statistical_Precision.md) - Complete explanation

**Want to optimize performance?** Read:
- [Parallelization_Guide.md](Parallelization_Guide.md) - Parallelization options

## 📝 Note on Documentation Organization

The documentation has been consolidated from 25+ separate files into 6 comprehensive guides. Each guide contains multiple sections covering related topics, making it easier to find information without jumping between many files.
