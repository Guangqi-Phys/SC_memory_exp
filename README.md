# Surface Code Memory Experiment

This package implements surface code memory experiments with **sliding window decoding** using Stim, PyMatching, and Sinter. The sliding window decoding strategy is designed for long memory experiments where the full syndrome history is divided into overlapping windows, each decoded independently, and their results combined.

## Overview

Surface codes are a type of quantum error-correcting code that can protect quantum information from errors. In a memory experiment, we repeatedly measure stabilizers over many rounds to detect errors. Traditional decoding approaches decode the entire syndrome history at once, which can be computationally expensive for long experiments.

**Sliding window decoding** addresses this by:
1. Dividing the full syndrome history into overlapping windows
2. Decoding each window independently using PyMatching
3. Accumulating logical observable predictions by XORing across windows
4. Comparing the final accumulated predictions with actual observables to compute logical error rates

## Project Structure

```
surface_code_experiment/
├── config/
│   └── experiment_config.py      # Experiment configuration parameters
│                                  # - L_VALUES: Code distances to test
│                                  # - TAU_ROUNDS: Number of measurement rounds
│                                  # - N_SLIDING_WINDOW: Window size for sliding window
│                                  # - N_OVERLAP: Overlap between windows
│                                  # - ERROR_RATES: Physical error rates to test
├── experiments/
│   └── threshold_experiment.py    # Main CLI script for threshold analysis
│                                  # - Command-line interface
│                                  # - Orchestrates workflow
│                                  # - Result saving and plotting coordination
├── src/
│   ├── tasks.py                   # Task creation utilities
│   │                              # - create_surface_code_tasks()
│   │                              # - Circuit generation and noise application
│   ├── experiment_runner.py        # Experiment execution
│   │                              # - run_threshold_experiment()
│   │                              # - Decoder setup and statistics collection
│   ├── plotting.py                # Visualization utilities
│   │                              # - plot_threshold()
│   │                              # - Figure generation and saving
│   ├── sliding_window_decoder.py  # Custom sinter decoder implementation
│   │                              # - SlidingWindowDecoder class
│   │                              # - SlidingWindowCompiledDecoder class
│   │                              # - Handles bit-packed data for efficiency
│   └── noise_model.py             # Noise model implementations
│                                  # - standard_depolarizing_noise_model()
│                                  # - si1000_noise_model()
│                                  # - Applies noise to Stim circuits
├── results/                       # Experiment results (auto-generated)
│   ├── *.pkl                      # Pickle files with TaskStats
│   └── figures/                   # Threshold plots (SVG format)
├── requirements.txt               # Python package dependencies
└── README.md                      # This file
```

### Module Architecture

The codebase follows a modular architecture with clear separation of concerns:

- **`tasks.py`**: Handles creation of sinter tasks from experiment parameters
- **`experiment_runner.py`**: Manages experiment execution and statistics collection
- **`plotting.py`**: Provides visualization and plotting functionality
- **`sliding_window_decoder.py`**: Implements the custom decoder for sinter
- **`noise_model.py`**: Contains noise model implementations
- **`threshold_experiment.py`**: Main entry point that orchestrates the workflow

This modular design makes the codebase easier to maintain, test, and extend.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Install Dependencies

Install the required Python packages using the requirements file:

```bash
cd surface_code_experiment
pip install -r requirements.txt
```

Or install packages individually:

```bash
pip install stim pymatching sinter numpy matplotlib
```

The requirements file specifies minimum versions for compatibility:
- `stim>=1.11.0` - Quantum circuit simulator
- `pymatching>=2.0.0` - Minimum-weight perfect matching decoder
- `sinter>=1.11.0` - Statistical sampling and threshold analysis
- `numpy>=1.20.0` - Numerical computing
- `matplotlib>=3.3.0` - Plotting library

### Verify Installation

You can verify the installation by running:

```bash
python -c "import stim, pymatching, sinter; print('All packages installed successfully')"
```

## Usage

### Basic Threshold Experiment

Run a threshold experiment with default parameters:

```bash
python surface_code_experiment/experiments/threshold_experiment.py
```

This will:
1. Generate surface code circuits for each (L, error_rate) combination
2. Apply the standard depolarizing noise model
3. Decode using sliding window decoding
4. Collect statistics using sinter
5. Save results to `results/` directory
6. Generate and display a threshold plot

### Customized Experiments

#### Specify Code Distances and Error Rates

```bash
python surface_code_experiment/experiments/threshold_experiment.py \
    --L 5 7 9 11 \
    --error-rates 0.001 0.005 0.01 0.015 0.02
```

#### Adjust Number of Rounds

```bash
python surface_code_experiment/experiments/threshold_experiment.py \
    --rounds 500
```

#### Compare with Standard PyMatching

To compare sliding window decoding with standard PyMatching:

```bash
python surface_code_experiment/experiments/threshold_experiment.py \
    --compare
```

This will run both decoders and plot them together for comparison.

#### Parallel Processing

Adjust the number of parallel workers:

```bash
python surface_code_experiment/experiments/threshold_experiment.py \
    --workers 20
```

#### Complete Example

A complete example with all options:

```bash
python surface_code_experiment/experiments/threshold_experiment.py \
    --L 7 11 15 \
    --error-rates 0.001 0.005 0.008 0.01 0.02 0.03 \
    --rounds 1000 \
    --workers 10 \
    --max-shots 1000000 \
    --max-errors 5000 \
    --compare
```

#### Additional Options

Skip plotting or saving if you only need one:

```bash
# Only save results, don't plot
python surface_code_experiment/experiments/threshold_experiment.py --no-plot

# Only plot, don't save results
python surface_code_experiment/experiments/threshold_experiment.py --no-save
```

### Command-Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--L` | int (list) | From config | Code distances (L) to test |
| `--error-rates` | float (list) | From config | Physical error rates to test |
| `--rounds` | int | 1000 | Number of measurement rounds (tau) |
| `--workers` | int | 10 | Number of parallel workers for sinter |
| `--max-shots` | int | 100,000,000 | Maximum shots per task |
| `--max-errors` | int | 5000 | Maximum errors before stopping a task |
| `--compare` | flag | False | Compare with standard pymatching decoder |
| `--no-sliding-window` | flag | False | Disable sliding window decoding |
| `--no-plot` | flag | False | Skip plotting (only save results) |
| `--no-save` | flag | False | Skip saving results (only plot) |

## Configuration

Edit `config/experiment_config.py` to set default parameters:

```python
# Code distances to test
L_VALUES = [7, 11, 15]

# Number of measurement rounds (tau)
TAU_ROUNDS = 1000

# Sliding window decoding parameters
N_SLIDING_WINDOW = 100  # Window size for sliding window decoding
N_OVERLAP = 50        # Overlap between consecutive windows

# Physical error rates to test
ERROR_RATES = [0.001, 0.005, 0.008, 0.01, 0.02, 0.03, 0.05]
```

### Parameter Descriptions

- **L_VALUES**: List of code distances. Larger L means better error correction but more qubits.
- **TAU_ROUNDS**: Total number of measurement rounds in the memory experiment.
- **N_SLIDING_WINDOW**: Size of each decoding window. Each window contains `N_SLIDING_WINDOW` rounds.
- **N_OVERLAP**: Overlap between consecutive windows. Ensures continuity in decoding.
- **ERROR_RATES**: Physical error rates to test. These are the probabilities of errors per gate/measurement.

## Sliding Window Decoding Algorithm

### How It Works

The sliding window decoder processes long syndrome histories by:

1. **Window Creation**: The full syndrome history (tau rounds) is divided into overlapping windows:
   - Window 1: Rounds 0 to N_SLIDING_WINDOW
   - Window 2: Rounds (N_SLIDING_WINDOW - N_OVERLAP) to (2*N_SLIDING_WINDOW - N_OVERLAP)
   - Window 3: Rounds (2*N_SLIDING_WINDOW - 2*N_OVERLAP) to (3*N_SLIDING_WINDOW - 2*N_OVERLAP)
   - And so on...

2. **Independent Decoding**: Each window is decoded independently using PyMatching, which performs minimum-weight perfect matching on the detector error model.

3. **Accumulation**: Logical observable predictions from each window are XORed together:
   ```
   accumulated_predictions = predictions_window1 ⊕ predictions_window2 ⊕ ...
   ```

4. **Error Detection**: The accumulated predictions are compared with actual logical observables to determine if a logical error occurred.

### Example

With `N_SLIDING_WINDOW=100` and `N_OVERLAP=50`:
- Window 1: Rounds 0-100
- Window 2: Rounds 50-150
- Window 3: Rounds 100-200
- Window 4: Rounds 150-250
- ...

Each window overlaps with the previous one by 50 rounds, ensuring continuity.

### Advantages

- **Scalability**: Can handle very long memory experiments (thousands of rounds)
- **Efficiency**: Each window is decoded independently, allowing parallelization
- **Flexibility**: Window size and overlap can be tuned for different scenarios

## Noise Model

The package uses a **standard depolarizing noise model** implemented in `src/noise_model.py`. This model applies noise to various circuit operations:

- **Single-qubit gates (R, RX)**: Depolarizing noise after the gate
- **Two-qubit gates (CNOT/CX)**: Two-qubit depolarizing noise
- **Measurements (M, MR, MRX)**: Measurement errors before and after measurement
- **Nested repeat blocks**: Noise is applied recursively

The noise model is applied to the noiseless circuit generated by Stim before creating the detector error model.

## Results

### Output Files

Results are saved in the `results/` directory:

- **Statistics files** (`*.pkl`): Pickle files containing `sinter.TaskStats` objects with:
  - Number of shots
  - Number of errors
  - Logical error rate
  - Metadata (L, error_rate, rounds, etc.)

- **Figures** (`results/figures/*.svg`): Threshold plots showing:
  - Logical error rate vs. physical error rate
  - Separate curves for each code distance
  - Comparison between decoders (if `--compare` is used)

### Interpreting Results

The threshold plot shows:
- **X-axis**: Physical error rate (p)
- **Y-axis**: Logical error rate per round
- **Curves**: One for each code distance (L)

A threshold is indicated where curves for different L values cross. Below the threshold, larger codes perform better. Above the threshold, smaller codes perform better.

### Loading Results

To load and analyze saved results:

```python
import pickle
import matplotlib.pyplot as plt
import sinter

# Load results
with open('results/threshold_stats_n100_overlap50_20240101_120000.pkl', 'rb') as f:
    stats = pickle.load(f)

# Plot results
fig, ax = plt.subplots(1, 1)
sinter.plot_error_rate(
    ax=ax,
    stats=stats,
    x_func=lambda stat: stat.json_metadata['error_rate'],
    group_func=lambda stat: f"L={stat.json_metadata['L']}",
)
plt.show()
```

## Programmatic Usage

The modular design allows you to use individual components in your own scripts:

### Using Individual Modules

#### Task Creation

```python
from surface_code_experiment.src.tasks import create_surface_code_tasks

# Create tasks for experiments
tasks = create_surface_code_tasks(
    L_values=[7, 11, 15],
    error_rates=[0.001, 0.01],
    num_rounds=1000,
    use_sliding_window=True,
)
```

#### Running Experiments

```python
from surface_code_experiment.src.experiment_runner import run_threshold_experiment

# Run experiments and collect statistics
stats = run_threshold_experiment(
    L_values=[7, 11, 15],
    error_rates=[0.001, 0.01],
    num_rounds=1000,
    num_workers=10,
    max_shots=1000000,
    use_sliding_window=True,
    compare_with_pymatching=False,
)
```

#### Plotting Results

```python
from surface_code_experiment.src.plotting import plot_threshold

# Plot threshold results
plot_threshold(
    stats=stats,
    use_sliding_window=True,
    save_figure=True,
    show_figure=True,
)
```

### Using the Custom Decoder

The sliding window decoder can be used directly with sinter:

```python
from surface_code_experiment.src.sliding_window_decoder import SlidingWindowDecoder
from surface_code_experiment.src.tasks import create_surface_code_tasks
import sinter

# Create decoder
decoder = SlidingWindowDecoder(
    n_sliding_window=100,    # Window size
    n_overlap=50,          # Overlap
    num_rounds=None        # Will infer from DEM
)

# Create tasks using the utility function
tasks = create_surface_code_tasks(
    L_values=[7, 11, 15],
    error_rates=[0.001, 0.01],
    num_rounds=1000,
)

# Run experiments
custom_decoders = {'sliding_window': decoder}
stats = sinter.collect(
    tasks=tasks,
    decoders=['sliding_window'],
    custom_decoders=custom_decoders,
    max_shots=1000000,
    print_progress=True,
)
```

## Troubleshooting

### Import Errors

If you encounter `ModuleNotFoundError`:

1. Ensure all dependencies are installed: `pip install stim pymatching sinter numpy matplotlib`
2. Make sure you're running from the correct directory
3. Check that the `surface_code_experiment` package is in your Python path

### Memory Issues

For very large experiments:
- Reduce `--max-shots`
- Reduce `--rounds`
- Use fewer parallel workers (`--workers`)

### Slow Performance

- Increase `--workers` for more parallelization
- Reduce `N_SLIDING_WINDOW` for faster window decoding
- Reduce `TAU_ROUNDS` for shorter experiments

### Decoder Errors

If the decoder fails to infer the number of rounds:
- Explicitly specify `num_rounds` when creating `SlidingWindowDecoder`
- Check that the detector error model has a consistent structure

## Implementation Details

### Module Responsibilities

#### `tasks.py`
- Generates noiseless surface code circuits using `stim.Circuit.generated()`
- Applies noise models to circuits
- Creates detector error models (DEMs) with decomposed errors
- Constructs `sinter.Task` objects with appropriate metadata

#### `experiment_runner.py`
- Sets up decoders (sliding window and/or standard pymatching)
- Manages parallel execution using sinter's worker system
- Collects statistics and handles experiment progress
- Validates decoder configuration

#### `plotting.py`
- Creates publication-quality threshold plots
- Handles figure saving and display options
- Configures plot styling (log-log scale, grid, labels)
- Generates timestamped filenames

### Sliding Window Decoder

The `SlidingWindowDecoder` class implements the `sinter.Decoder` interface:

- **`compile_decoder_for_dem()`**: Compiles the decoder for a specific detector error model
- **`decode_via_files()`**: Fallback method for file-based decoding
- **`SlidingWindowCompiledDecoder.decode_shots_bit_packed()`**: Performs the actual decoding on bit-packed data

The decoder:
1. Unpacks bit-packed detection events
2. Reshapes data into (num_shots, num_rounds, num_detectors_per_round)
3. For each shot, creates overlapping windows
4. Decodes each window independently
5. Accumulates predictions by XORing
6. Packs results back to bit-packed format

### Bit-Packed Data

Sinter uses bit-packed data for efficiency:
- Detection events: 1 bit per detector
- Observable predictions: 1 bit per observable
- Data is packed into bytes (8 bits per byte)

## References

- **Stim**: https://github.com/quantumlib/Stim
- **PyMatching**: https://github.com/oscarhiggott/PyMatching
- **Sinter**: https://github.com/quantumlib/Stim/tree/main/glue/sample
- **Surface Codes**: Quantum error-correcting codes for fault-tolerant quantum computation

## License

[Add your license information here]

## Contributing

[Add contribution guidelines if applicable]

## Contact

[Add contact information if desired]
