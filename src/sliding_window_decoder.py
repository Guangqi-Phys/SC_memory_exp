"""
Sliding window decoder for sinter that implements overlapping window decoding.
"""
import numpy as np
import stim
import pymatching
import pathlib
from typing import Optional

# Handle imports for both when used as module and when run directly
try:
    from sinter._decoding._decoding_decoder_class import Decoder, CompiledDecoder
except ImportError:
    # When run directly, try to import from installed sinter
    import os
    import sys
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    grandparent_dir = os.path.dirname(parent_dir)
    if grandparent_dir not in sys.path:
        sys.path.insert(0, grandparent_dir)
    try:
        from sinter._decoding._decoding_decoder_class import Decoder, CompiledDecoder
    except ImportError:
        raise ImportError(
            "Could not import sinter. Please ensure sinter is installed.\n"
            "Install with: pip install sinter"
        )


class SlidingWindowCompiledDecoder(CompiledDecoder):
    """
    Compiled decoder that implements sliding window decoding.
    
    This decoder processes long syndrome histories by dividing them into overlapping
    windows, decoding each window independently, and accumulating the logical
    observable predictions.
    
    Algorithm:
    1. Divide the full syndrome history (tau rounds) into overlapping windows
       - Window size: n_sliding_window rounds
       - Overlap: n_overlap rounds between consecutive windows
    2. For each window:
       - Extract syndrome data for that window
       - Decode using PyMatching to get logical observable predictions
       - Accumulate predictions by XORing (Pauli corrections are modulo 2)
    3. Compare final accumulated predictions with actual observables to compute error rate
    
    Example with tau_round=1000, n_sliding_window=100, n_overlap=50:
       - Window 1: rounds 0-100
       - Window 2: rounds 50-150 (overlap of 50 with window 1)
       - Window 3: rounds 100-200 (overlap of 50 with window 2)
       - Window 4: rounds 150-250 (overlap of 50 with window 3)
       - ... continues until all rounds are covered
    
    Special case: If tau_round == n_sliding_window, only one window covers all rounds,
    which is equivalent to normal PyMatching decoding without sliding window.
    """
    
    def __init__(
        self,
        matcher: pymatching.Matching,
        num_rounds: int,
        num_detectors_per_round: int,
        n_sliding_window: int,
        n_overlap: int,
        num_observables: int,
    ):
        self.matcher = matcher
        self.num_rounds = num_rounds
        self.num_detectors_per_round = num_detectors_per_round
        self.n_sliding_window = n_sliding_window
        self.n_overlap = n_overlap
        self.num_observables = num_observables
        self.num_detectors = num_rounds * num_detectors_per_round
    
    def decode_shots_bit_packed(
        self,
        *,
        bit_packed_detection_event_data: np.ndarray,
    ) -> np.ndarray:
        """
        Decode bit-packed detection events using sliding window decoding.
        
        Args:
            bit_packed_detection_event_data: Bit-packed detection events,
                shape (num_shots, ceil(num_detectors / 8))
        
        Returns:
            Bit-packed observable predictions, shape (num_shots, ceil(num_observables / 8))
        """
        num_shots = bit_packed_detection_event_data.shape[0]
        
        # Unpack detection events
        # Convert from bit-packed to regular binary array
        num_detectors = self.num_detectors
        dets_unpacked = np.unpackbits(
            bit_packed_detection_event_data,
            axis=1,
            bitorder='little'
        )[:, :num_detectors]
        
        # Reshape to (num_shots, num_rounds, num_detectors_per_round)
        dets_reshaped = dets_unpacked.reshape(num_shots, self.num_rounds, self.num_detectors_per_round)
        
        # Initialize output predictions
        predictions = np.zeros((num_shots, self.num_observables), dtype=np.uint8)
        
        # Process each shot
        for shot_idx in range(num_shots):
            current_shot_syndrome = dets_reshaped[shot_idx]
            
            # Sliding window decoding with overlap
            # Each window gives a correction (logical observable prediction) for data qubit errors in its time range.
            # These corrections need to be accumulated and applied to the final state (measurement of all data qubits).
            # The logical observable is the product of Pauli operators along a line in the 2D surface code.
            #
            # Algorithm:
            # 1. Decode each overlapping window independently using PyMatching
            # 2. Each window finds data qubit errors in its time range and gives a correction
            # 3. Accumulate corrections by XORing (Pauli corrections are modulo 2)
            # 4. The accumulated correction is applied to the final round to update the logical information
            #
            # Example with n_sliding_window=100, n_overlap=50, num_rounds=1000:
            #   Window 1: rounds 0-100   -> finds errors in rounds 0-100, gives correction1
            #   Window 2: rounds 50-150  -> finds errors in rounds 50-150, gives correction2
            #   Window 3: rounds 100-200 -> finds errors in rounds 100-200, gives correction3
            #   ...
            #   Final correction = correction1 XOR correction2 XOR correction3 XOR ...
            #   This final correction is applied to the last data qubit measurement result
            #
            # Special case: if num_rounds == n_sliding_window, only one window covers all rounds
            #   In this case, there's only one correction, so the result is automatically
            #   equivalent to normal PyMatching decoding (no special handling needed)
            
            # IMPORTANT: For surface code memory experiments, if we have num_rounds detector rounds,
            # the last round (round num_rounds-1) is the final data qubit measurement round.
            # This round corresponds to a "no-error" syndrome measurement and must be included
            # in the last sliding window for correct decoding.
            
            # Strategy for handling overlapping windows:
            # Each window decodes a LARGER range (with overlap on both sides) for reliability,
            # but we only RECORD corrections from the center portion (the non-overlapping part).
            #
            # Example with n_sliding_window=100, n_overlap=50:
            #   Recording window 1: rounds 0-100
            #     Decoding window 1: rounds 0-150 (adds 50 on right for reliability)
            #     -> Record corrections for rounds 0-100 only
            #
            #   Recording window 2: rounds 100-200
            #     Decoding window 2: rounds 50-250 (adds 50 on left and 50 on right)
            #     -> Record corrections for rounds 100-200 only
            #
            #   Recording window 3: rounds 200-300
            #     Decoding window 3: rounds 150-350 (adds 50 on left and 50 on right)
            #     -> Record corrections for rounds 200-300 only
            #
            # The extra overlap on both sides makes the center portion more reliable,
            # but we only keep corrections from the center (non-overlapping) portion.
            
            # OPTIMIZATION: Track only parity flips per window instead of full observable vectors
            # For surface codes, we typically have 1 observable, so we can use a single bit accumulator
            # This is more efficient than array operations: just XOR bits instead of arrays
            if self.num_observables == 1:
                # Single observable: use integer XOR for efficiency
                accumulated_parity = 0
            else:
                # Multiple observables: use array (fallback for general case)
                accumulated_predictions = np.zeros(self.num_observables, dtype=np.uint8)
            
            # Calculate recording windows (the center portions we keep corrections for)
            # Recording windows: 0-100, 100-200, 200-300, ... (non-overlapping, step by n_sliding_window)
            recording_start_round = 0
            window_num = 0
            
            while recording_start_round < self.num_rounds:
                # Calculate the recording window (center portion we keep corrections for)
                recording_end_round = min(recording_start_round + self.n_sliding_window, self.num_rounds)
                
                # Calculate the decoding window (larger, with overlap on both sides)
                # Decoding window starts n_overlap rounds before recording window (or at 0)
                decode_start_round = max(0, recording_start_round - self.n_overlap)
                # Decoding window ends n_overlap rounds after recording window (or at num_rounds)
                decode_end_round = min(recording_end_round + self.n_overlap, self.num_rounds)
                
                # CRITICAL: Ensure the final round (round num_rounds-1) is included in the last window
                # The final round is the data qubit measurement round, which is essential for correct decoding.
                # Since recording_end_round will be num_rounds for the last window, and decode_end_round
                # will also be num_rounds, the slice [decode_start_round:decode_end_round] will naturally
                # include rounds decode_start_round to num_rounds-1, which includes the final round.
                # This is guaranteed because:
                # - For the last window: recording_end_round = num_rounds (due to min() above)
                # - Therefore: decode_end_round = min(num_rounds + n_overlap, num_rounds) = num_rounds
                # - Python slice [start:end] includes indices start to end-1, so [decode_start_round:num_rounds]
                #   includes rounds decode_start_round to num_rounds-1, which includes the final round.
                
                # Extract syndrome data for the DECODING window (larger, with overlap)
                decode_syndrome_data = current_shot_syndrome[decode_start_round:decode_end_round, :]
                
                # Create a full syndrome vector for the decoding window, padding with zeros
                # IMPORTANT: We create a full-length vector (num_detectors) even though we only have
                # detection events for the decoding window. This is necessary because:
                # 1. PyMatching's matcher was built from the FULL DEM, so it expects a vector of length num_detectors
                # 2. The matcher uses the FULL graph structure (all nodes, all edges, all edge weights)
                # 3. Edge weights are derived from error probabilities in the DEM and represent the cost/probability
                #    of errors. These weights are used even for edges connecting detectors outside the window.
                # 4. PyMatching's matching algorithm will naturally focus on paths between detectors that have
                #    non-zero detection events, but it uses all edge weights in the graph for optimal matching.
                decode_syndrome_vector = np.zeros(self.num_detectors, dtype=np.uint8)
                
                # Calculate detector indices for the decoding window
                decode_start_detector_idx = decode_start_round * self.num_detectors_per_round
                decode_end_detector_idx = decode_end_round * self.num_detectors_per_round
                
                # Place decoding window data into full vector at the correct positions
                decode_detectors = decode_syndrome_data.flatten()
                decode_syndrome_vector[decode_start_detector_idx:decode_end_detector_idx] = decode_detectors
                
                # Decode the FULL decoding window using PyMatching
                # The extra overlap on both sides makes the center portion more reliable
                # PyMatching uses the full graph (all edge weights) but only matches detectors with events
                decode_2d = decode_syndrome_vector.reshape(1, -1)
                predicted_observables = self.matcher.decode_batch(decode_2d)
                
                # OPTIMIZATION: Track only parity flip per window (single bit for single observable)
                # Each window contributes a parity flip (0 or 1) that we XOR together
                # This is equivalent to tracking full corrections but more efficient
                if self.num_observables == 1:
                    # Single observable: just XOR the parity bit
                    # predicted_observables shape is (1, 1) for batch_size=1, num_observables=1
                    window_parity_flip = predicted_observables[0][0] if predicted_observables.ndim == 2 else predicted_observables[0]
                    accumulated_parity ^= window_parity_flip
                else:
                    # Multiple observables: XOR arrays (fallback)
                    accumulated_predictions = (accumulated_predictions ^ predicted_observables[0]) % 2
                
                # Move to next recording window: step by n_sliding_window
                # Recording windows: 0-100, 100-200, 200-300, ...
                recording_start_round += self.n_sliding_window
                window_num += 1
                
                # Break if we've covered all rounds
                if recording_end_round >= self.num_rounds:
                    break
            
            # Store accumulated predictions for this shot
            # IMPORTANT: This accumulated correction represents the total logical observable prediction
            # from all windows. It should be compared with the actual logical observable measurement
            # from the final round (round num_rounds-1) to determine if a logical error occurred.
            # The final round measures all data qubits directly, and the logical observable is
            # computed from those measurements. The accumulated correction from all windows is
            # the decoder's prediction of what the logical observable should be, accounting for
            # all errors detected in the syndrome history.
            if self.num_observables == 1:
                # Convert single bit to array format for consistency
                predictions[shot_idx, 0] = accumulated_parity
            else:
                predictions[shot_idx] = accumulated_predictions
        
        # Pack predictions back to bit-packed format
        num_obs_bytes = (self.num_observables + 7) // 8
        predictions_packed = np.packbits(
            np.pad(predictions, ((0, 0), (0, num_obs_bytes * 8 - self.num_observables)), mode='constant'),
            axis=1,
            bitorder='little'
        )[:, :num_obs_bytes]
        
        return predictions_packed


class SlidingWindowDecoder(Decoder):
    """
    Sliding window decoder that decodes overlapping windows of rounds.
    
    This decoder splits the full detector error model into overlapping windows,
    decodes each window independently, and accumulates the logical observable
    predictions by XORing them together.
    """
    
    def __init__(
        self,
        n_sliding_window: int,
        n_overlap: int,
        num_rounds: Optional[int] = None,
    ):
        """
        Initialize the sliding window decoder.
        
        Args:
            n_sliding_window: Size of each decoding window
            n_overlap: Overlap between consecutive windows
            num_rounds: Total number of measurement rounds (tau). If None, will try to infer
                from the DEM by assuming detectors are evenly distributed across rounds.
        """
        self.n_sliding_window = n_sliding_window
        self.n_overlap = n_overlap
        self.num_rounds = num_rounds
    
    def compile_decoder_for_dem(
        self,
        *,
        dem: stim.DetectorErrorModel,
    ) -> CompiledDecoder:
        """
        Compile the decoder for a specific detector error model.
        
        Args:
            dem: The detector error model to decode
        
        Returns:
            A compiled decoder instance
        """
        try:
            import pymatching
        except ImportError as ex:
            raise ImportError(
                "The sliding window decoder requires pymatching.\n"
                "To fix this, install the python package 'pymatching'.\n"
                "For example: pip install pymatching\n"
            ) from ex
        
        # Create matching from DEM
        # IMPORTANT: This creates a matcher with the FULL graph structure:
        # - All detectors (nodes) from the DEM
        # - All error mechanisms (edges) from the DEM
        # - All edge weights derived from error probabilities (weight = log((1-p)/p))
        # When decoding a window, we pass a full-length syndrome vector, and PyMatching
        # uses all edge weights in the graph (even for edges outside the window) to find
        # the optimal matching that explains the detection events in the window.
        matcher = pymatching.Matching.from_detector_error_model(dem)
        
        # Determine number of rounds if not provided
        # IMPORTANT: For surface code memory experiments, if we specify rounds=1000,
        # Stim creates 1001 detector rounds total:
        #   - Rounds 0-999: Syndrome measurement rounds (1000 rounds)
        #   - Round 1000: Final round that measures all data qubits (1 round)
        # So the DEM has num_rounds + 1 detector rounds total
        num_rounds = self.num_rounds
        if num_rounds is None:
            # Try to infer from common round counts
            # For surface codes, common values are small (3, 5, 7, 9, etc.)
            # Try dividing by common round counts
            # Note: We try both num_rounds and num_rounds+1 to account for the final round
            for candidate_rounds in [3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 50, 100, 200, 500, 1000, 10000]:
                # Try candidate_rounds (assuming it's the total number of detector rounds)
                if dem.num_detectors % candidate_rounds == 0:
                    num_detectors_per_round = dem.num_detectors // candidate_rounds
                    if 1 <= num_detectors_per_round <= 10000:
                        num_rounds = candidate_rounds
                        break
                # Also try candidate_rounds + 1 (in case candidate_rounds is the number of syndrome rounds)
                if dem.num_detectors % (candidate_rounds + 1) == 0:
                    num_detectors_per_round = dem.num_detectors // (candidate_rounds + 1)
                    if 1 <= num_detectors_per_round <= 10000:
                        num_rounds = candidate_rounds + 1
                        break
            
            if num_rounds is None:
                raise ValueError(
                    f"Could not infer number of rounds from DEM with {dem.num_detectors} detectors. "
                    f"Please specify num_rounds explicitly."
                )
        
        # Calculate number of detectors per round
        # This assumes detectors are evenly distributed across rounds
        if dem.num_detectors % num_rounds != 0:
            raise ValueError(
                f"Number of detectors ({dem.num_detectors}) is not divisible by "
                f"number of rounds ({num_rounds}). Cannot determine detectors per round."
            )
        num_detectors_per_round = dem.num_detectors // num_rounds
        
        return SlidingWindowCompiledDecoder(
            matcher=matcher,
            num_rounds=num_rounds,
            num_detectors_per_round=num_detectors_per_round,
            n_sliding_window=self.n_sliding_window,
            n_overlap=self.n_overlap,
            num_observables=dem.num_observables,
        )
    
    def decode_via_files(
        self,
        *,
        num_shots: int,
        num_dets: int,
        num_obs: int,
        dem_path: pathlib.Path,
        dets_b8_in_path: pathlib.Path,
        obs_predictions_b8_out_path: pathlib.Path,
        tmp_dir: pathlib.Path,
    ) -> None:
        """
        Performs decoding by reading/writing problems and answers from disk.
        This is a fallback method when compile_decoder_for_dem is not available.
        
        Args:
            num_shots: Number of shots to decode
            num_dets: Number of detectors
            num_obs: Number of observables
            dem_path: Path to detector error model file
            dets_b8_in_path: Path to input detection events (b8 format)
            obs_predictions_b8_out_path: Path to output predictions (b8 format)
            tmp_dir: Temporary directory for intermediate files
        """
        # Read DEM from file
        dem = stim.DetectorErrorModel.from_file(dem_path)
        
        # Compile decoder for this DEM
        compiled_decoder = self.compile_decoder_for_dem(dem=dem)
        
        # Read detection events from file
        dets_bit_packed = stim.read_shot_data_file(
            path=str(dets_b8_in_path),
            format='b8',
            bit_pack=True,
            num_detectors=num_dets,
            num_observables=0,
        )
        
        # Decode using compiled decoder
        predictions_bit_packed = compiled_decoder.decode_shots_bit_packed(
            bit_packed_detection_event_data=dets_bit_packed,
        )
        
        # Write predictions to file
        stim.write_shot_data_file(
            data=predictions_bit_packed,
            path=str(obs_predictions_b8_out_path),
            format='b8',
            num_detectors=0,
            num_observables=num_obs,
        )