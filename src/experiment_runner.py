"""
Experiment runner for surface code threshold experiments.

This module provides functions to run threshold experiments using sliding window
decoding and collect statistics using sinter.
"""
from typing import List
import sinter

from surface_code_experiment.src.sliding_window_decoder import SlidingWindowDecoder
from surface_code_experiment.src.tasks import create_surface_code_tasks
from surface_code_experiment.config.experiment_config import (
    N_SLIDING_WINDOW,
    N_OVERLAP,
    MAX_SHOTS,
    MAX_ERRORS,
)


def run_threshold_experiment(
    L_values: List[int],
    error_rates: List[float],
    num_rounds: int,
    num_workers: int = 10,
    max_shots: int = MAX_SHOTS,
    max_errors: int = MAX_ERRORS,
    use_sliding_window: bool = True,
    compare_with_pymatching: bool = False,
) -> List[sinter.TaskStats]:
    """
    Run threshold experiment with sliding window decoding.
    
    This function creates tasks, sets up decoders (sliding window and/or standard
    pymatching), and collects statistics using sinter's parallel collection system.
    
    Args:
        L_values: List of code distances to test
        error_rates: List of physical error rates to test
        num_rounds: Number of measurement rounds (tau)
        num_workers: Number of parallel workers for sinter.collect
        max_shots: Maximum number of shots per task before stopping
        max_errors: Maximum number of errors before stopping a task
        use_sliding_window: Whether to use sliding window decoding
        compare_with_pymatching: Whether to also run standard pymatching for comparison
    
    Returns:
        List of TaskStats from sinter containing experiment results
    
    Raises:
        ValueError: If no decoders are specified
    
    Example:
        >>> stats = run_threshold_experiment(
        ...     L_values=[7, 11],
        ...     error_rates=[0.001, 0.01],
        ...     num_rounds=1000,
        ...     num_workers=4,
        ...     max_shots=10000,
        ... )
        >>> len(stats) > 0
        True
    """
    # Create tasks for all (L, error_rate) combinations
    tasks = create_surface_code_tasks(L_values, error_rates, num_rounds, use_sliding_window)
    
    # Setup decoders
    decoders = []
    custom_decoders = {}
    
    if use_sliding_window:
        custom_decoders['sliding_window'] = SlidingWindowDecoder(
            n_sliding_window=N_SLIDING_WINDOW,
            n_overlap=N_OVERLAP,
            num_rounds=None,  # Will infer from DEM
        )
        decoders.append('sliding_window')
    
    if compare_with_pymatching:
        decoders.append('pymatching')
    
    if not decoders:
        raise ValueError("At least one decoder must be specified")
    
    # Print experiment configuration
    print(f"Running threshold experiment with {len(tasks)} tasks...")
    print(f"Decoders: {decoders}")
    
    # Check if tasks have per-task collection_options (adaptive max_errors/max_shots)
    # If so, tasks will use their own limits; global max_shots/max_errors are fallbacks
    has_per_task_options = any(
        task.collection_options is not None and 
        (task.collection_options.max_shots is not None or task.collection_options.max_errors is not None)
        for task in tasks
    )
    
    if has_per_task_options:
        print(f"Using adaptive MAX_ERRORS/MAX_SHOTS per task (based on error_rate and tau_rounds)")
        # Find the maximum per-task limits to use as global limits
        # This ensures:
        # 1. Per-task options take precedence (min(global, per_task) = per_task when per_task < global)
        # 2. Status message shows "shots_left" and "errors_left" instead of "shots_taken" and "errors_seen"
        # 3. Display shows correct remaining counts (using max of all per-task limits)
        max_per_task_shots = max(
            (task.collection_options.max_shots for task in tasks 
             if task.collection_options is not None and task.collection_options.max_shots is not None),
            default=max_shots
        )
        max_per_task_errors = max(
            (task.collection_options.max_errors for task in tasks 
             if task.collection_options is not None and task.collection_options.max_errors is not None),
            default=max_errors
        )
        global_max_shots = max_per_task_shots
        global_max_errors = max_per_task_errors
    else:
        print(f"Using global MAX_ERRORS = {max_errors}, MAX_SHOTS = {max_shots}")
        global_max_shots = max_shots
        global_max_errors = max_errors
    
    # MAX_ERRORS is the maximum number of logical errors (shot errors) to collect
    # IMPORTANT: This is per shot, NOT per sliding window.
    # The sliding window decoder processes all windows for each shot and produces
    # one prediction per shot. Sinter compares this with the actual observable
    # to determine if there's a logical error (one error count per shot).
    if use_sliding_window:
        print(f"Sliding window parameters: n_sliding_window={N_SLIDING_WINDOW}, overlap={N_OVERLAP}")
    
    # Collect statistics using sinter
    # Note: If tasks have collection_options, sinter will use min(global, per_task) for each task
    stats = sinter.collect(
        num_workers=num_workers,
        tasks=tasks,
        decoders=decoders,
        custom_decoders=custom_decoders if custom_decoders else None,
        max_shots=global_max_shots,
        max_errors=global_max_errors,
        print_progress=True,
    )
    
    return stats
