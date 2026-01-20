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
from surface_code_experiment.config.experiment_config import MAX_SHOTS, MAX_ERRORS

if __name__ == '__main__':
    surface_code_tasks = []
    for d in [3, 5, 7]:
        for noise in [0.001, 0.003, 0.005, 0.008, 0.009, 0.01, 0.015]:
            # Generate noiseless surface code circuit
            circuit = stim.Circuit.generated(
                "surface_code:rotated_memory_z",
                rounds=d * 3,
                distance=d,
            )
            
            # Get the full qubit set from the circuit
            full_qubit_set = list(range(circuit.num_qubits))
            
            # Apply standard depolarizing noise model
            noisy_circuit = standard_depolarizing_noise_model(
                circuit=circuit,
                full_qubit_set=full_qubit_set,
                probability=noise,
            )
            
            # Create detector error model with decomposed errors for graph-like structure
            dem = noisy_circuit.detector_error_model(decompose_errors=True)
            
            # Create task
            surface_code_tasks.append(
                sinter.Task(
                    circuit=noisy_circuit,
                    detector_error_model=dem,
                    json_metadata={'d': d, 'r': d * 3, 'p': noise},
                )
            )

    collected_surface_code_stats: List[sinter.TaskStats] = sinter.collect(
        num_workers=10,
        tasks=surface_code_tasks,
        decoders=['pymatching'],
        max_shots=MAX_SHOTS,
        max_errors=MAX_ERRORS,
        print_progress=True,
    )

    fig, ax = plt.subplots(1, 1)
    sinter.plot_error_rate(
        ax=ax,
        stats=collected_surface_code_stats,
        x_func=lambda stat: stat.json_metadata['p'],
        group_func=lambda stat: stat.json_metadata['d'],
        failure_units_per_shot_func=lambda stat: stat.json_metadata['r'],
    )
    ax.set_ylim(1e-5, 1e-1)
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
