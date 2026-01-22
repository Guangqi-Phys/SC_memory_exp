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
import json
import time
from datetime import datetime
import argparse
import resource

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


def save_experiment_summary(
    stats,
    start_time: float,
    end_time: float,
    start_cpu_time: float,
    end_cpu_time: float,
    config: dict,
    results_dir: str = "surface_code_experiment/results",
) -> str:
    """
    Save experiment summary including timing and statistics to a text/JSON file.
    
    Args:
        stats: List of TaskStats from the experiment
        start_time: Wall clock start time (from time.time())
        end_time: Wall clock end time (from time.time())
        start_cpu_time: CPU time start (from resource.getrusage())
        end_cpu_time: CPU time end (from resource.getrusage())
        config: Dictionary with experiment configuration
        results_dir: Directory to save results
    
    Returns:
        Path to saved summary file
    """
    os.makedirs(results_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    summary_filename = f'experiment_summary_n{N_SLIDING_WINDOW}_overlap{N_OVERLAP}_{timestamp}.txt'
    summary_path = os.path.join(results_dir, summary_filename)
    
    # Calculate timing information
    wall_time = end_time - start_time
    cpu_time = end_cpu_time - start_cpu_time
    cpu_time_user = cpu_time  # User CPU time
    cpu_time_sys = resource.getrusage(resource.RUSAGE_SELF).ru_stime - start_cpu_time
    
    # Calculate summary statistics
    total_shots = sum(stat.shots for stat in stats)
    total_errors = sum(stat.errors for stat in stats)
    total_tasks = len(stats)
    
    # Calculate per-task statistics
    task_stats = []
    for stat in stats:
        task_info = {
            'L': stat.json_metadata.get('L', 'N/A'),
            'error_rate': stat.json_metadata.get('error_rate', 'N/A'),
            'decoder': stat.decoder,
            'shots': stat.shots,
            'errors': stat.errors,
            'seconds': stat.seconds,
            'shots_per_second': stat.shots / stat.seconds if stat.seconds > 0 else 0,
        }
        task_stats.append(task_info)
    
    # Prepare summary data
    summary = {
        'experiment_info': {
            'timestamp': datetime.now().isoformat(),
            'experiment_type': 'Surface Code Threshold Experiment',
        },
        'configuration': config,
        'timing': {
            'wall_time_seconds': wall_time,
            'wall_time_formatted': f"{int(wall_time // 3600)}h {int((wall_time % 3600) // 60)}m {wall_time % 60:.2f}s",
            'cpu_time_user_seconds': cpu_time_user,
            'cpu_time_sys_seconds': cpu_time_sys,
            'cpu_time_total_seconds': cpu_time_user + cpu_time_sys,
            'cpu_time_formatted': f"{int((cpu_time_user + cpu_time_sys) // 3600)}h {int(((cpu_time_user + cpu_time_sys) % 3600) // 60)}m {(cpu_time_user + cpu_time_sys) % 60:.2f}s",
            'cpu_utilization_percent': ((cpu_time_user + cpu_time_sys) / wall_time * 100) if wall_time > 0 else 0,
        },
        'summary_statistics': {
            'total_tasks': total_tasks,
            'total_shots': total_shots,
            'total_errors': total_errors,
            'total_seconds': sum(stat.seconds for stat in stats),
            'average_shots_per_task': total_shots / total_tasks if total_tasks > 0 else 0,
            'average_errors_per_task': total_errors / total_tasks if total_tasks > 0 else 0,
            'overall_shots_per_second': total_shots / wall_time if wall_time > 0 else 0,
        },
        'per_task_statistics': task_stats,
    }
    
    # Write human-readable text file
    with open(summary_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("Surface Code Threshold Experiment Summary\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("Experiment Information:\n")
        f.write(f"  Timestamp: {summary['experiment_info']['timestamp']}\n")
        f.write(f"  Type: {summary['experiment_info']['experiment_type']}\n\n")
        
        f.write("Configuration:\n")
        for key, value in config.items():
            f.write(f"  {key}: {value}\n")
        f.write("\n")
        
        f.write("Timing Information:\n")
        f.write(f"  Wall Time: {summary['timing']['wall_time_formatted']} ({summary['timing']['wall_time_seconds']:.2f} seconds)\n")
        f.write(f"  CPU Time (User): {summary['timing']['cpu_time_user_seconds']:.2f} seconds\n")
        f.write(f"  CPU Time (System): {summary['timing']['cpu_time_sys_seconds']:.2f} seconds\n")
        f.write(f"  CPU Time (Total): {summary['timing']['cpu_time_formatted']} ({summary['timing']['cpu_time_total_seconds']:.2f} seconds)\n")
        f.write(f"  CPU Utilization: {summary['timing']['cpu_utilization_percent']:.1f}%\n")
        f.write("\n")
        
        f.write("Summary Statistics:\n")
        f.write(f"  Total Tasks: {summary['summary_statistics']['total_tasks']}\n")
        f.write(f"  Total Shots: {summary['summary_statistics']['total_shots']:,}\n")
        f.write(f"  Total Errors: {summary['summary_statistics']['total_errors']:,}\n")
        f.write(f"  Total Computation Time: {summary['summary_statistics']['total_seconds']:.2f} seconds\n")
        f.write(f"  Average Shots per Task: {summary['summary_statistics']['average_shots_per_task']:,.0f}\n")
        f.write(f"  Average Errors per Task: {summary['summary_statistics']['average_errors_per_task']:,.0f}\n")
        f.write(f"  Overall Throughput: {summary['summary_statistics']['overall_shots_per_second']:,.0f} shots/second\n")
        f.write("\n")
        
        f.write("Per-Task Statistics:\n")
        f.write("-" * 80 + "\n")
        for i, task in enumerate(task_stats, 1):
            f.write(f"Task {i}:\n")
            f.write(f"  L: {task['L']}, Error Rate: {task['error_rate']}, Decoder: {task['decoder']}\n")
            f.write(f"  Shots: {task['shots']:,}, Errors: {task['errors']:,}\n")
            f.write(f"  Time: {task['seconds']:.2f}s, Throughput: {task['shots_per_second']:,.0f} shots/s\n")
            f.write("\n")
        
        f.write("=" * 80 + "\n")
    
    # Also save as JSON for programmatic access
    json_path = summary_path.replace('.txt', '.json')
    with open(json_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Experiment summary saved to {summary_path}")
    print(f"Experiment summary (JSON) saved to {json_path}")
    return summary_path


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
    
    # Record start time
    start_time = time.time()
    start_cpu_time = resource.getrusage(resource.RUSAGE_SELF).ru_utime
    
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
    
    # Record end time
    end_time = time.time()
    end_cpu_time = resource.getrusage(resource.RUSAGE_SELF).ru_utime
    
    # Prepare configuration dictionary
    config = {
        'L_values': args.L,
        'error_rates': args.error_rates,
        'num_rounds': args.rounds,
        'num_workers': args.workers,
        'max_shots': args.max_shots,
        'max_errors': args.max_errors,
        'use_sliding_window': not args.no_sliding_window,
        'compare_with_pymatching': args.compare,
        'n_sliding_window': N_SLIDING_WINDOW,
        'n_overlap': N_OVERLAP,
    }
    
    # Save results
    if not args.no_save:
        save_results(stats)
        # Save experiment summary with timing information
        save_experiment_summary(
            stats=stats,
            start_time=start_time,
            end_time=end_time,
            start_cpu_time=start_cpu_time,
            end_cpu_time=end_cpu_time,
            config=config,
        )
    
    # Plot results
    if not args.no_plot:
        plot_threshold(
            stats,
            use_sliding_window=not args.no_sliding_window,
            show_figure=True,
        )
    
    # Print timing summary
    wall_time = end_time - start_time
    cpu_time = end_cpu_time - start_cpu_time
    print("\n" + "=" * 60)
    print("Experiment Timing Summary")
    print("=" * 60)
    print(f"Wall Time: {int(wall_time // 3600)}h {int((wall_time % 3600) // 60)}m {wall_time % 60:.2f}s")
    print(f"CPU Time: {int(cpu_time // 3600)}h {int((cpu_time % 3600) // 60)}m {cpu_time % 60:.2f}s")
    print(f"CPU Utilization: {(cpu_time / wall_time * 100):.1f}%")
    print("=" * 60)
    print("\nExperiment completed successfully!")


if __name__ == "__main__":
    main()
