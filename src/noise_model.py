import numpy as np
import stim

def standard_depolarizing_noise_model(
        circuit: stim.Circuit, 
        full_qubit_set: list, 
        probability: float) -> stim.Circuit:
    """
    Applies a standard depolarizing noise model to a Stim circuit.
    
    This noise model simulates common quantum errors including:
    - Depolarizing noise on single-qubit gates
    - Depolarizing noise on two-qubit gates
    - Measurement errors
    - State preparation errors
    
    Args:
        circuit (stim.Circuit): The input quantum circuit
        probability (float): Base error probability for all noise operations
        
    Returns:
        stim.Circuit: A new circuit with noise operations inserted
    """
    n = circuit.num_qubits
    result = stim.Circuit()
    
    for instruction in circuit:
        # Handle nested repeat blocks recursively
        if isinstance(instruction, stim.CircuitRepeatBlock):
            result.append(stim.CircuitRepeatBlock(
                repeat_count=instruction.repeat_count,
                body=standard_depolarizing_noise_model(instruction.body_copy(), full_qubit_set=full_qubit_set,
                                                        probability=probability)))
        # Add Z errors after R gates (rotation around Z axis)
        elif instruction.name == 'R':
            result.append(instruction)
            result.append('Z_ERROR', instruction.targets_copy(), probability)
            result.append('DEPOLARIZE1', list(set(full_qubit_set) - set(instruction.targets_copy())), probability)
        # Add X errors after RX gates (rotation around X axis)
        elif instruction.name == 'RX':
            result.append(instruction)
            result.append('X_ERROR', instruction.targets_copy(), probability)
            result.append('DEPOLARIZE1', list(set(full_qubit_set) - set(instruction.targets_copy())), probability)
        # Add measurement errors: Z error before measurement and depolarizing after
        elif instruction.name == 'M':
            result.append('Z_error', instruction.targets_copy(), probability)
            result.append(instruction)
            result.append('Z_error', instruction.targets_copy(), probability)
            result.append('DEPOLARIZE1', list(set(full_qubit_set) - set(instruction.targets_copy())), probability)
        # Add two-qubit depolarizing noise after CNOT gates
        elif instruction.name == 'CX':
            result.append(instruction)
            result.append('DEPOLARIZE2', instruction.targets_copy(), probability)
            result.append('DEPOLARIZE1', list(set(full_qubit_set) - set(instruction.targets_copy())), probability)
        # Add measurement errors for MR gates (measure and reset)
        elif instruction.name == 'MR':
            result.append('Z_error', instruction.targets_copy(), probability)
            result.append(instruction)
            result.append('Z_error', instruction.targets_copy(), probability)
            result.append('DEPOLARIZE1', list(set(full_qubit_set) - set(instruction.targets_copy())), probability)
        # Add measurement errors for MRX gates (measure and reset with X rotation)
        elif instruction.name == 'MRX':
            result.append('X_error', instruction.targets_copy(), probability)
            result.append(instruction)
            result.append('X_error', instruction.targets_copy(), probability)
            result.append('DEPOLARIZE1', list(set(full_qubit_set) - set(instruction.targets_copy())), probability)
        # Pass through other instructions unchanged
        else:
            result.append(instruction)
    return result

def si1000_noise_model(
        circuit: stim.Circuit, 
        full_qubit_set: list, 
        probability: float) -> stim.Circuit:
    """
    Applies the SI1000 noise model to a Stim circuit.
    
    This is a specialized noise model with different error rates for different operations:
    - Higher error rates for measurement operations (5x base probability)
    - Lower error rates for two-qubit gates (1/10x base probability)
    - Double error rates for rotation gates (2x base probability)
    
    Args:
        circuit (stim.Circuit): The input quantum circuit
        probability (float): Base error probability for all noise operations
        
    Returns:
        stim.Circuit: A new circuit with noise operations inserted
    """
    n = circuit.num_qubits
    result = stim.Circuit()
    
    for instruction in circuit:
        # Handle nested repeat blocks recursively
        if isinstance(instruction, stim.CircuitRepeatBlock):
            result.append(stim.CircuitRepeatBlock(
                repeat_count=instruction.repeat_count,
                body=si1000_noise_model(instruction.body_copy(), full_qubit_set = full_qubit_set,
                                                        probability=probability)))
        # Add Z errors after R gates with double probability
        elif instruction.name == 'R':
            result.append(instruction)
            result.append('Z_ERROR', instruction.targets_copy(), 2*probability)
            result.append('DEPOLARIZE1', list(set(full_qubit_set) - set(instruction.targets_copy())), 2*probability)
        # Add X errors after RX gates with double probability
        elif instruction.name == 'RX':
            result.append(instruction)
            result.append('X_ERROR', instruction.targets_copy(), 2*probability)
            result.append('DEPOLARIZE1', list(set(full_qubit_set) - set(instruction.targets_copy())), 2*probability)
        # Add measurement errors with 5x probability before and 1x after
        elif instruction.name == 'M':
            result.append('Z_error', instruction.targets_copy(), 5*probability)
            result.append(instruction)
            result.append('Z_error', instruction.targets_copy(), probability)
            result.append('DEPOLARIZE1', list(set(full_qubit_set) - set(instruction.targets_copy())), 2*probability)
        # Add reduced depolarizing noise after CNOT gates
        elif instruction.name == 'CX':
            result.append(instruction)
            result.append('DEPOLARIZE2', instruction.targets_copy(), probability)
            result.append('DEPOLARIZE1', list(set(full_qubit_set) - set(instruction.targets_copy())), probability/10)
        # Add measurement errors for MR gates with 5x probability before and 1x after
        elif instruction.name == 'MR':
            result.append('Z_error', instruction.targets_copy(), 5*probability)
            result.append(instruction)
            result.append('Z_error', instruction.targets_copy(), probability)
            result.append('DEPOLARIZE1', list(set(full_qubit_set) - set(instruction.targets_copy())), 2*probability)
        # Add measurement errors for MRX gates with 5x probability before and 1x after
        elif instruction.name == 'MRX':
            result.append('X_error', instruction.targets_copy(), 5*probability)
            result.append(instruction)
            result.append('X_error', instruction.targets_copy(), probability)
            result.append('DEPOLARIZE1', list(set(full_qubit_set) - set(instruction.targets_copy())), 2*probability)
        # Pass through other instructions unchanged
        else:
            result.append(instruction)
    return result

def simple_stim_noise_model(
        circuit: stim.Circuit,
        data_qubits: list,
        noise: float) -> stim.Circuit:
    """
    Applies Stim's standard noise model parameters to a circuit.
    
    This noise model applies the same noise parameters used by Stim's circuit generation:
    - after_clifford_depolarization: Depolarizing noise after Clifford gates
    - after_reset_flip_probability: Flip errors after reset operations
    - before_measure_flip_probability: Flip errors before measurements
    - before_round_data_depolarization: Depolarizing noise on data qubits before each round
    
    Args:
        circuit (stim.Circuit): The input quantum circuit
        data_qubits (list): List of data qubit indices for before_round_data_depolarization
        noise (float): Error probability for all noise operations
        
    Returns:
        stim.Circuit: A new circuit with noise operations inserted
    """
    # Single-qubit Clifford gates (apply DEPOLARIZE1)
    single_qubit_cliffords = {
        'H', 'S', 'S_DAG', 'SQRT_X', 'SQRT_X_DAG', 'SQRT_Y', 'SQRT_Y_DAG',
        'SQRT_Z', 'SQRT_Z_DAG', 'X', 'Y', 'Z',
        'C_XYZ', 'C_ZYX', 'C_NXYZ', 'C_NZYX', 'C_XNYZ', 'C_XYNZ', 'C_ZNYX', 'C_ZYNX',
        'H_XY', 'H_XZ', 'H_YZ', 'H_NXY', 'H_NXZ', 'H_NYZ'
    }
    
    # Two-qubit Clifford gates (apply DEPOLARIZE2)
    two_qubit_cliffords = {
        'CX', 'CNOT', 'CZ', 'CY', 'ISWAP', 'ISWAP_DAG', 'SWAP',
        'CXSWAP', 'CZSWAP', 'SWAPCX', 'SWAPCZ',
        'SQRT_XX', 'SQRT_XX_DAG', 'SQRT_YY', 'SQRT_YY_DAG', 'SQRT_ZZ', 'SQRT_ZZ_DAG',
        'XCX', 'XCY', 'XCZ', 'YCX', 'YCY', 'YCZ', 'ZCX', 'ZCY', 'ZCZ',
        'II'
    }
    
    result = stim.Circuit()
    
    for instruction in circuit:
        # Handle nested repeat blocks recursively
        if isinstance(instruction, stim.CircuitRepeatBlock):
            result.append(stim.CircuitRepeatBlock(
                repeat_count=instruction.repeat_count,
                body=simple_stim_noise_model(
                    instruction.body_copy(),
                    data_qubits=data_qubits,
                    noise=noise
                )
            ))
        # Apply before_round_data_depolarization before TICK
        elif instruction.name == 'TICK':
            if noise > 0:
                result.append('DEPOLARIZE1', data_qubits, noise)
            result.append(instruction)
        # Apply after_clifford_depolarization after single-qubit Cliffords
        elif instruction.name in single_qubit_cliffords:
            result.append(instruction)
            if noise > 0:
                result.append('DEPOLARIZE1', instruction.targets_copy(), noise)
        # Apply after_clifford_depolarization after two-qubit Cliffords
        elif instruction.name in two_qubit_cliffords:
            result.append(instruction)
            if noise > 0:
                result.append('DEPOLARIZE2', instruction.targets_copy(), noise)
        # Apply after_reset_flip_probability after reset operations
        elif instruction.name == 'R':
            result.append(instruction)
            if noise > 0:
                # R is Z-basis reset: apply X_ERROR
                result.append('X_ERROR', instruction.targets_copy(), noise)
        elif instruction.name == 'RX':
            result.append(instruction)
            if noise > 0:
                # RX is X-basis reset: apply Z_ERROR
                result.append('Z_ERROR', instruction.targets_copy(), noise)
        elif instruction.name == 'RY':
            result.append(instruction)
            if noise > 0:
                # RY is Y-basis reset: apply X_ERROR (same as R)
                result.append('X_ERROR', instruction.targets_copy(), noise)
        # Apply before_measure_flip_probability before measurements
        elif instruction.name == 'M':
            if noise > 0:
                # M is Z-basis measurement: apply X_ERROR before
                result.append('X_ERROR', instruction.targets_copy(), noise)
            result.append(instruction)
        elif instruction.name == 'MX':
            if noise > 0:
                # MX is X-basis measurement: apply Z_ERROR before
                result.append('Z_ERROR', instruction.targets_copy(), noise)
            result.append(instruction)
        elif instruction.name == 'MY':
            if noise > 0:
                # MY is Y-basis measurement: apply X_ERROR before
                result.append('X_ERROR', instruction.targets_copy(), noise)
            result.append(instruction)
        # Handle MR (measure and reset) - apply before_measure_flip_probability and after_reset_flip_probability
        elif instruction.name == 'MR':
            if noise > 0:
                # MR is Z-basis: X_ERROR before measurement
                result.append('X_ERROR', instruction.targets_copy(), noise)
            result.append(instruction)
            if noise > 0:
                # After reset: X_ERROR (Z-basis reset)
                result.append('X_ERROR', instruction.targets_copy(), noise)
        elif instruction.name == 'MRX':
            if noise > 0:
                # MRX is X-basis: Z_ERROR before measurement
                result.append('Z_ERROR', instruction.targets_copy(), noise)
            result.append(instruction)
            if noise > 0:
                # After reset: Z_ERROR (X-basis reset)
                result.append('Z_ERROR', instruction.targets_copy(), noise)
        elif instruction.name == 'MRY':
            if noise > 0:
                # MRY is Y-basis: X_ERROR before measurement
                result.append('X_ERROR', instruction.targets_copy(), noise)
            result.append(instruction)
            if noise > 0:
                # After reset: X_ERROR (Y-basis reset, same as R)
                result.append('X_ERROR', instruction.targets_copy(), noise)
        # Pass through other instructions unchanged
        else:
            result.append(instruction)
    
    return result

# def with_dephasing_before_ticks(
#         circuit: stim.Circuit, 
#         *, 
#         probability: float) -> stim.Circuit:
#     """
#     Applies dephasing noise before each TICK instruction in a Stim circuit.
    
#     This noise model simulates time-dependent dephasing by adding Z errors
#     to all qubits before each TICK instruction, which represents a unit of time
#     in the circuit.
    
#     Args:
#         circuit (stim.Circuit): The input quantum circuit
#         probability (float): Error probability for the dephasing noise
        
#     Returns:
#         stim.Circuit: A new circuit with dephasing noise inserted before TICKs
#     """
#     n = circuit.num_qubits
#     result = stim.Circuit()
    
#     for instruction in circuit:
#         # Handle nested repeat blocks recursively
#         if isinstance(instruction, stim.CircuitRepeatBlock):
#             result.append(stim.CircuitRepeatBlock(
#                 repeat_count=instruction.repeat_count,
#                 body=with_dephasing_before_ticks(instruction.body_copy(),
#                                                  probability=probability)))
#         # Add Z errors to all qubits before each TICK
#         elif instruction.name == 'TICK':
#             result.append('Z_ERROR', range(n), probability)
#             result.append(instruction)
#         # Pass through other instructions unchanged
#         else:
#             result.append(instruction)
#     return result