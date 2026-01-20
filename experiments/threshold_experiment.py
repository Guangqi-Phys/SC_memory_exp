"""
Threshold experiment script for surface code memory experiments.

This script provides a command-line interface for running threshold experiments
with sliding window decoding. It orchestrates task creation, experiment execution,
result saving, and visualization.

Usage:
    python threshold_experiment.py [OPTIONS]

Example:
    python threshold_experiment.py --L 7 11 15 --error-rates 0.001 0.01 --rounds 1000
"""
import sys
import os
import pickle
from datetime import datetime
import argparse

# Add parent directories to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
grandparent_dir = os.path.dirname(parent_dir)
if grandparent_dir not in sys.path:
    sys.path.insert(0, grandparent_dir)

from surface_code_experiment.src.experiment_runner import run_threshold_experiment
from surface_code_experiment.src.plotting import plot_threshold
from surface_code_experiment.config.experiment_config import (
    L_VALUES,
    TAU_ROUNDS,
    N_SLIDING_WINDOW,
    N_OVERLAP,
    ERROR_RATES,
    MAX_SHOTS,
    MAX_ERRORS,
)


def save_results(
    stats,
    results_dir: str = "surface_code_experiment/results",
) -> str:
    """
    Save experiment results to a pickle file.
    
    Args:
        stats: List of TaskStats to save
        results_dir: Directory to save results
    
    Returns:
        Path to saved results file
    """
    os.makedirs(results_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_filename = f'threshold_stats_n{N_SLIDING_WINDOW}_overlap{N_OVERLAP}_{timestamp}.pkl'
    results_path = os.path.join(results_dir, results_filename)
    
    with open(results_path, 'wb') as f:
        pickle.dump(stats, f)
    
    print(f"Results saved to {results_path}")
    return results_path


def main():
    """Main entry point for threshold experiment script."""
    parser = argparse.ArgumentParser(
        description="Run surface code threshold experiment with sliding window decoding",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
  Examples:
  # Run with default parameters
  python threshold_experiment.py

  # Run with custom code distances and error rates
  python threshold_experiment.py --L 7 11 15 --error-rates 0.001 0.01 0.02

  # Compare sliding window with standard pymatching
  python threshold_experiment.py --compare

  # Run with more workers for faster execution
  python threshold_experiment.py --workers 20
        """
    )
    
    parser.add_argument(
        '--L',
        type=int,
        nargs='+',
        default=L_VALUES,
        help='Code distances to test (default: from config)'
    )
    parser.add_argument(
        '--error-rates',
        type=float,
        nargs='+',
        default=ERROR_RATES,
        help='Physical error rates to test (default: from config)'
    )
    parser.add_argument(
        '--rounds',
        type=int,
        default=TAU_ROUNDS,
        help=f'Number of measurement rounds (tau) (default: {TAU_ROUNDS})'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=10,
        help='Number of parallel workers for sinter (default: 10)'
    )
    parser.add_argument(
        '--max-shots',
        type=int,
        default=MAX_SHOTS,
        help=f'Maximum shots per task (default: {MAX_SHOTS:,})'
    )
    parser.add_argument(
        '--max-errors',
        type=int,
        default=MAX_ERRORS,
        help=f'Maximum errors before stopping a task (default: {MAX_ERRORS:,})'
    )
    parser.add_argument(
        '--compare',
        action='store_true',
        help='Compare sliding window decoding with standard pymatching'
    )
    parser.add_argument(
        '--no-sliding-window',
        action='store_true',
        help='Disable sliding window decoding (use standard pymatching only)'
    )
    parser.add_argument(
        '--no-plot',
        action='store_true',
        help='Skip plotting (only save results)'
    )
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Skip saving results (only plot)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.no_sliding_window and not args.compare:
        parser.error("--no-sliding-window requires --compare to be set, or use --compare alone")
    
    # Run experiment
    print("=" * 60)
    print("Surface Code Threshold Experiment")
    print("=" * 60)
    print(f"Code distances: {args.L}")
    print(f"Error rates: {args.error_rates}")
    print(f"Rounds: {args.rounds}")
    print(f"Workers: {args.workers}")
    print("=" * 60)
    
    stats = run_threshold_experiment(
        L_values=args.L,
        error_rates=args.error_rates,
        num_rounds=args.rounds,
        num_workers=args.workers,
        max_shots=args.max_shots,
        max_errors=args.max_errors,
        use_sliding_window=not args.no_sliding_window,
        compare_with_pymatching=args.compare,
    )
    
    # Save results
    if not args.no_save:
        save_results(stats)
    
    # Plot results
    if not args.no_plot:
        plot_threshold(
            stats,
            use_sliding_window=not args.no_sliding_window,
            show_figure=True,
        )
    
    print("\nExperiment completed successfully!")


if __name__ == "__main__":
    main()
