"""
Task creation utilities for surface code threshold experiments.

This module provides functions to create sinter tasks for surface code experiments
with various noise models and configurations.
"""
from typing import List
import stim
import sinter

from surface_code_experiment.src.noise_model import standard_depolarizing_noise_model
from surface_code_experiment.config.experiment_config import (
    N_SLIDING_WINDOW,
    N_OVERLAP,
    calculate_max_errors,
    calculate_max_shots,
)


# def get_data_qubits_from_circuit(circuit: stim.Circuit) -> List[int]:
#     """
#     Extract data qubit indices from a Stim surface code circuit.
    
#     For rotated surface codes, data qubits are identified by their coordinates:
#     - Data qubits have coordinates where both x and y are odd integers
#     - Measurement qubits have coordinates where x and/or y are even integers
    
#     Args:
#         circuit: A Stim circuit (typically generated with surface_code:rotated_memory_z)
    
#     Returns:
#         List of data qubit indices
#     """
#     # Get qubit coordinates from the circuit
#     qubit_coords = circuit.get_final_qubit_coords()
    
#     data_qubits = []
#     for qubit_idx, coords in qubit_coords.items():
#         # For rotated surface codes, data qubits have coordinates where
#         # both x and y are odd integers (1, 3, 5, 7, ...)
#         # Measurement qubits have at least one even coordinate (0, 2, 4, 6, ...)
#         # Example from Stim docs: data qubits at (1,1), (3,1), (5,1), etc.
#         #                   measurement qubits at (2,0), (2,2), (4,2), etc.
#         if len(coords) >= 2:
#             x, y = coords[0], coords[1]
#             # Check if both coordinates are odd integers (data qubits)
#             # Convert to int and check modulo 2
#             x_int = int(round(x))
#             y_int = int(round(y))
#             if x_int % 2 == 1 and y_int % 2 == 1:
#                 data_qubits.append(qubit_idx)
#         elif len(coords) == 1:
#             # Single coordinate: if it's odd, likely a data qubit
#             # (less common, but handle it)
#             x = coords[0]
#             x_int = int(round(x))
#             if x_int % 2 == 1:
#                 data_qubits.append(qubit_idx)
    
#     # If no coordinates found or pattern doesn't match, fall back to heuristic:
#     # For rotated surface codes, data qubits are typically the first L^2 qubits
#     # But this is unreliable, so we prefer coordinate-based identification
#     if not data_qubits and qubit_coords:
#         # Fallback: assume all qubits are data qubits (conservative but incorrect)
#         # This should not happen if circuit has QUBIT_COORDS
#         data_qubits = list(range(circuit.num_qubits))
    
#     return sorted(data_qubits)


def create_surface_code_tasks(
    L_values: List[int],
    error_rates: List[float],
    num_rounds: int,
    use_sliding_window: bool = True,
) -> List[sinter.Task]:
    """
    Create sinter tasks for surface code threshold experiments.
    
    This function generates surface code circuits for each combination of code distance
    and error rate, applies the standard depolarizing noise model, and creates sinter
    tasks with appropriate metadata.
    
    Args:
        L_values: List of code distances (L) to test
        error_rates: List of physical error rates to test
        num_rounds: Number of measurement rounds (tau)
        use_sliding_window: Whether to include sliding window decoding parameters in metadata
    
    Returns:
        List of sinter.Task objects ready for execution
    
    Example:
        >>> tasks = create_surface_code_tasks(
        ...     L_values=[7, 11],
        ...     error_rates=[0.001, 0.01],
        ...     num_rounds=1000,
        ... )
        >>> len(tasks)
        4
    """
    tasks = []
    
    for L in L_values:
        for error_rate in error_rates:
            # Generate noiseless surface code circuit
            circuit = stim.Circuit.generated(
                "surface_code:rotated_memory_z",
                distance=L,
                rounds=num_rounds,
            )
            
            
            # Get the full qubit set from the circuit (includes both data and measurement qubits)
            # Note: list(range(circuit.num_qubits)) includes ALL qubits (data + ancilla),
            # so we use the extracted data_qubits when we need only data qubits
            full_qubit_set = list(range(circuit.num_qubits))
            
            # # Apply standard depolarizing noise model
            noisy_circuit = standard_depolarizing_noise_model(
                circuit=circuit,
                full_qubit_set=full_qubit_set,
                probability=error_rate,
            )
            
            # Create detector error model with decomposed errors for graph-like structure
            dem = noisy_circuit.detector_error_model(decompose_errors=True)
            
            # Create metadata for tracking experiment parameters
            metadata = {
                'L': L,
                'error_rate': error_rate,
                'num_rounds': num_rounds,
            }
            
            # Add sliding window parameters to metadata if applicable
            if use_sliding_window:
                metadata['n_sliding_window'] = N_SLIDING_WINDOW
                metadata['n_overlap'] = N_OVERLAP
            
            # Calculate adaptive max_errors and max_shots based on error_rate and num_rounds
            # Lower error rates need fewer errors for good statistical confidence
            # Higher error rates (especially with many rounds) need more errors
            max_errors = calculate_max_errors(error_rate, num_rounds)
            max_shots = calculate_max_shots(error_rate, num_rounds)
            
            # Create and append sinter task with adaptive collection options
            tasks.append(
                sinter.Task(
                    circuit=noisy_circuit,
                    detector_error_model=dem,
                    json_metadata=metadata,
                    collection_options=sinter.CollectionOptions(
                        max_shots=max_shots,
                        max_errors=max_errors,
                    ),
                )
            )
    
    return tasks
