"""
Plotting utilities for surface code threshold experiments.

This module provides functions to visualize threshold experiment results,
including threshold plots and error rate comparisons.
"""
import os
from typing import List
from datetime import datetime
import matplotlib.pyplot as plt
import sinter

from surface_code_experiment.config.experiment_config import (
    N_SLIDING_WINDOW,
    N_OVERLAP,
)


def plot_threshold(
    stats: List[sinter.TaskStats],
    output_dir: str = "surface_code_experiment/results",
    figures_dir: str = "surface_code_experiment/results/figures",
    use_sliding_window: bool = True,
    save_figure: bool = True,
    show_figure: bool = True,
) -> str:
    """
    Plot threshold results from surface code experiments.
    
    Creates a threshold plot showing logical error rate vs. physical error rate
    for different code distances. The plot uses log-log scaling and includes
    appropriate labels and legends.
    
    Args:
        stats: List of TaskStats from sinter containing experiment results
        output_dir: Directory for output files (unused, kept for compatibility)
        figures_dir: Directory to save figure files
        use_sliding_window: Whether sliding window decoding was used (affects title)
        save_figure: Whether to save the figure to disk
        show_figure: Whether to display the figure
    
    Returns:
        Path to saved figure file (if saved), or empty string
    
    Example:
        >>> stats = [...]  # List of TaskStats
        >>> fig_path = plot_threshold(stats, save_figure=True, show_figure=False)
        >>> os.path.exists(fig_path)
        True
    """
    # Create figures directory if it doesn't exist
    os.makedirs(figures_dir, exist_ok=True)
    
    # Create figure and axis
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    
    # Plot error rates using sinter's built-in plotting function
    # highlight_max_likelihood_factor controls uncertainty region width:
    # - 5:  Very tight confidence interval (~90% confidence)
    # - 10: Tighter confidence interval (good balance, recommended)
    # - 20: ~95% confidence interval (standard, but can appear wide on log scale)
    # - 100: Very wide confidence (exploratory)
    # - 1000: Extremely wide (too wide, not recommended)
    # See docs/reducing_uncertainty.md for explanation
    # Note: With 9000 errors, statistical precision is good (~1-2% relative),
    #       but the visual width on log scale depends on this factor
    sinter.plot_error_rate(
        ax=ax,
        stats=stats,
        x_func=lambda stat: stat.json_metadata.get('error_rate', stat.json_metadata.get('p', 0)),
        group_func=lambda stat: f"L={stat.json_metadata.get('L', stat.json_metadata.get('d', '?'))}",
        failure_units_per_shot_func=lambda stat: stat.json_metadata.get('num_rounds', stat.json_metadata.get('r', 1)),
        # highlight_max_likelihood_factor=1,  # Tighter than 20, better for log-scale plots (was 20, was 1000)
    )
    
    # Set plot limits and scale
    ax.set_ylim(1e-5, 1)
    ax.set_xlim(0.001, 0.01)
    ax.loglog()
    
    # Add grid
    ax.grid(which='major', alpha=0.3)
    ax.grid(which='minor', alpha=0.1)
    
    # Extract total round number from stats (should be consistent across all stats)
    num_rounds = None
    if stats:
        num_rounds = stats[0].json_metadata.get('num_rounds', stats[0].json_metadata.get('r', None))
    
    # Set title and labels
    title = "Surface Code Threshold"
    if num_rounds is not None:
        title += f" (τ = {num_rounds} rounds)"
    if use_sliding_window:
        title += f" [Sliding window size = {N_SLIDING_WINDOW}, overlap={N_OVERLAP}]"
    ax.set_title(title)
    ax.set_xlabel("Physical Error Rate")
    ax.set_ylabel("Logical Error Rate per Round")
    ax.legend()
    
    # Set high DPI for publication-quality figures
    fig.set_dpi(300)
    
    # Save figure if requested
    filepath = ""
    if save_figure:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'threshold_sliding_window_n{N_SLIDING_WINDOW}_overlap{N_OVERLAP}_{timestamp}.svg'
        filepath = os.path.join(figures_dir, filename)
        plt.savefig(filepath, bbox_inches='tight', format='svg')
        print(f"Figure saved to {filepath}")
    
    # Show figure if requested
    if show_figure:
        plt.show()
    else:
        plt.close(fig)
    
    return filepath
