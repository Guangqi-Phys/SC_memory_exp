import sys
import os
import sinter
import stim
import matplotlib.pyplot as plt
from typing import List

# Add parent directories to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
grandparent_dir = os.path.dirname(parent_dir)
if grandparent_dir not in sys.path:
    sys.path.insert(0, grandparent_dir)

from surface_code_experiment.src.noise_model import standard_depolarizing_noise_model


if __name__ == '__main__':
    surface_code_tasks = []
    for d in [5,7]:
        for noise in [0.005, 0.01, 0.015]:
            # Generate noiseless surface code circuit
            noisy_circuit = stim.Circuit.generated(
                "surface_code:rotated_memory_z",
                rounds=100,
                distance=d,
                after_clifford_depolarization=noise,
                after_reset_flip_probability=noise,
                before_measure_flip_probability=noise,
                before_round_data_depolarization=noise,
            )
            
            # Get the full qubit set from the circuit
            # full_qubit_set = list(range(circuit.num_qubits))
            
            # # Apply standard depolarizing noise model
            # noisy_circuit = standard_depolarizing_noise_model(
            #     circuit=circuit,
            #     full_qubit_set=full_qubit_set,
            #     probability=noise,
            # )
            
            # Create detector error model with decomposed errors for graph-like structure
            dem = noisy_circuit.detector_error_model(decompose_errors=True)
            
            # Create task
            surface_code_tasks.append(
                sinter.Task(
                    circuit=noisy_circuit,
                    detector_error_model=dem,
                    json_metadata={'d': d, 'r': 100, 'p': noise},  # r should match rounds=100
                )
            )

    collected_surface_code_stats: List[sinter.TaskStats] = sinter.collect(
        num_workers=10,
        tasks=surface_code_tasks,
        decoders=['pymatching'],
        max_shots=100_000_000,
        max_errors=10_000,
        print_progress=True,
    )

    # Demonstrate the difference between simple division and actual conversion
    print("\n" + "="*80)
    print("DEMONSTRATION: Shot Error Rate → Per-Round Error Rate Conversion")
    print("="*80)
    print("The conversion is NONLINEAR, not simple division!\n")
    
    test_shot_rates = [0.01, 0.1, 0.5, 0.9]
    rounds = 100
    
    print(f"With {rounds} rounds:")
    print(f"{'Shot Error Rate':<20} {'Simple Division':<20} {'Actual Conversion':<20} {'Difference':<20}")
    print("-" * 80)
    for shot_rate in test_shot_rates:
        simple_division = shot_rate / rounds
        actual_conversion = sinter.shot_error_rate_to_piece_error_rate(
            shot_error_rate=shot_rate,
            pieces=rounds,
            values=1
        )
        difference = actual_conversion - simple_division
        print(f"{shot_rate:<20.6f} {simple_division:<20.8f} {actual_conversion:<20.8f} {difference:<20.8f}")
    print("="*80 + "\n")
    
    # Print diagnostic information about collected errors
    print("="*80)
    print("DIAGNOSTIC: Collected Statistics")
    print("="*80)
    import math
    z = 1.96  # 95% confidence
    
    for stat in collected_surface_code_stats:
        d = stat.json_metadata['d']
        p = stat.json_metadata['p']
        shots_used = stat.shots - stat.discards
        error_rate_shot = stat.errors / shots_used if shots_used > 0 else 0
        
        # Calculate relative precision in shot space
        if stat.errors > 0 and error_rate_shot > 0:
            # Relative precision = 2 × z × sqrt((1-p) / (n × p))
            # where n = number of shots, p = error rate
            # Or using errors: relative_precision = 2 × z × sqrt((1-p) / errors) when p is small
            # More accurate: use standard error = sqrt(p(1-p)/n) where n = shots
            if shots_used > 0:
                se = math.sqrt(error_rate_shot * (1 - error_rate_shot) / shots_used)
                relative_precision = 2 * z * se / error_rate_shot if error_rate_shot > 0 else float('inf')
            else:
                relative_precision = float('inf')
        else:
            relative_precision = float('inf')
        
        # Calculate per-round error rate using actual conversion
        rounds = stat.json_metadata['r']
        per_round_rate_actual = sinter.shot_error_rate_to_piece_error_rate(
            shot_error_rate=error_rate_shot,
            pieces=rounds,
            values=1
        ) if error_rate_shot > 0 else 0
        per_round_rate_simple = error_rate_shot / rounds if rounds > 0 else 0
        
        print(f"d={d}, p={p:.4f}: errors={stat.errors}, shots={stat.shots}, "
              f"discards={stat.discards}")
        print(f"  shot_error_rate={error_rate_shot:.6f}, "
              f"per_round_actual={per_round_rate_actual:.8f}, "
              f"per_round_simple_div={per_round_rate_simple:.8f}, "
              f"relative_precision={relative_precision*100:.2f}%")
    print("="*80)
    print("Note: When shot error rate is near 0.5, the shot→per-round conversion has a")
    print("      singularity (dp_round/dp_shot → ∞), so per-round uncertainty blows up")
    print("      even with good statistical precision in shot space. See Singularity_Near_Half_Shot_Rate.md.")
    print("="*80 + "\n")

    fig, ax = plt.subplots(1, 1)
    # Y-axis = logical error rate per round. Shot→per-round conversion uses sinter's XOR model
    # (sinter._probability_util.shot_error_rate_to_piece_error_rate). Passing
    # failure_units_per_shot_func=lambda stat: stat.json_metadata['r'] supplies rounds N,
    # so the plot uses p_round = (1-(1-2*p_shot)^(1/N))/2 for p_shot ≤ 0.5 and the symmetric
    # form for p_shot > 0.5. No extra conversion is needed—sinter does this inside plot_error_rate.
    #
    # Why uncertainty is very high when shot error rate > 0.5:
    # (1) Binomial: variance p*(1-p)/n is maximized at p=0.5, so the [low,high] interval in
    #     shot space is widest when p_shot ≈ 0.5.
    # (2) Conversion singularity: p_shot = (1-(1-2*p_round)^N)/2 has a maximum at p_round=0.5
    #     (where p_shot=0.5), so dp_round/dp_shot → ∞ as p_shot → 0.5. Any interval in
    #     p_shot near 0.5 maps to a huge interval in p_round. For p_shot > 0.5 we use the
    #     high branch (p_round > 0.5), but the derivative is still huge near the boundary.
    sinter.plot_error_rate(
        ax=ax,
        stats=collected_surface_code_stats,
        x_func=lambda stat: stat.json_metadata['p'],
        group_func=lambda stat: stat.json_metadata['d'],
        failure_units_per_shot_func=lambda stat: stat.json_metadata['r'],
        highlight_max_likelihood_factor=5,  # Very tight uncertainty bounds (default is 1000, which is too wide)
        # Try 5 for very tight bounds, 10 for tighter, 20 for standard
    )
    ax.set_ylim(1e-5, 1)
    ax.set_xlim(0.001, 0.015)
    ax.loglog()
    ax.set_title("Surface Code Error Rates per Round under Circuit Noise")
    ax.set_xlabel("Physical Error Rate")
    ax.set_ylabel("Logical Error Rate per Round")
    ax.grid(which='major')
    ax.grid(which='minor')
    ax.legend()
    fig.set_dpi(160)  # Show it bigger
    plt.show()
