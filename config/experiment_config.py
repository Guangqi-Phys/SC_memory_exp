# surface_code_experiment/config/experiment_config.py

# Default code distances for threshold experiments
L_VALUES = [27]

# Number of measurement rounds (tau)
TAU_ROUNDS = 5

# Sliding window decoding parameters
N_SLIDING_WINDOW = 5  # Window size (n_sliding_window) for sliding window decoding
N_OVERLAP = 0  # Overlap between consecutive windows

# Number of parallel workers for pymatching/sinter
NUM_WORKERS = 10  # Number of parallel workers for sinter.collect

# Default error rates for threshold experiments
ERROR_RATES = [0.003, 0.005, 0.007, 0.009]


# Adaptive MAX_ERRORS based on error_rate and tau_round
# At low error rates, fewer errors are needed for good statistical confidence
# At high error rates, more errors are needed (especially with many rounds)
# Baseline: 200 rounds, error_rate=0.01 (1%) with 50,000 errors
BASELINE_ROUNDS = 1
BASELINE_ERROR_RATE = 0.01  # 1% - reference error rate
BASELINE_MAX_ERRORS = 10_000
BASELINE_MAX_SHOTS = 1_000_000

def calculate_max_errors(error_rate: float, tau_rounds: int) -> int:
    """
    Calculate MAX_ERRORS based on error_rate and tau_rounds.
    
    Strategy:
    - Scale with tau_round: Linear scaling (power 1.0)
      - More rounds means more opportunities for errors, so we scale linearly
      - Statistical confidence depends on the number of errors collected, not on how error rate scales with rounds
    - Scale with error_rate: lower error rates need fewer errors for same confidence
    - Use square (power of 2) scaling for error_rate: at 0.001 we want ~1/100 the errors of 0.01
    
    IMPORTANT: This function does NOT depend on n_sliding_window or any decoding parameters.
    Statistical reliability (confidence in error rate estimate) depends ONLY on:
    - Number of errors collected (MAX_ERRORS)
    - Number of shots collected (MAX_SHOTS)
    - The actual error rate
    
    The decoding method (sliding window vs full decoding) affects DECODING ACCURACY
    (how well errors are corrected), but NOT STATISTICAL RELIABILITY (confidence in the estimate).
    Each shot produces one error count (logical error = decoder prediction != actual observable),
    regardless of how many windows were used in decoding.
    
    Args:
        error_rate: Physical error rate (e.g., 0.001, 0.01)
        tau_rounds: Number of measurement rounds
    
    Returns:
        Maximum number of errors to collect for this error_rate and tau_rounds
    """
    # Scaling with rounds: Should MAX_ERRORS scale with number of rounds?
    #
    # IMPORTANT: MAX_ERRORS is the maximum number of LOGICAL ERRORS (decoder failures) to collect.
    # Since we're measuring "logical error rate per round" = (errors / shots) / num_rounds,
    # the question is: do we need more errors for more rounds to maintain the same statistical confidence?
    #
    # Statistical reasoning:
    # - For the same relative precision in per-round error rate, you might need errors ∝ num_rounds^2
    # - However, with more rounds, shot error rate increases (you collect errors faster)
    # - For consistent statistical confidence regardless of rounds, you might NOT need scaling
    #
    # Options:
    # - tau_power = 0.0: No scaling - same number of errors regardless of rounds
    #   → Same statistical confidence in per-round estimate (if per-round rate is similar)
    # - tau_power = 1.0: Linear scaling - 2x rounds → 2x errors (current default)
    #   → Practical compromise: accounts for higher shot error rates with more rounds
    # - tau_power = 2.0: Quadratic scaling - 2x rounds → 4x errors
    #   → For same relative precision in per-round estimate
    #
    # Current choice (linear) is a practical compromise, but NOT strictly necessary.
    # If you want consistent statistical confidence regardless of rounds, use tau_power = 0.0.
    tau_power = 1.0  # Linear scaling: 2x rounds → 2x errors
    # Alternative: tau_power = 0.0  # No scaling: same errors regardless of rounds
    
    tau_scale = (tau_rounds / BASELINE_ROUNDS) ** tau_power
    # To disable scaling with rounds, uncomment:
    # tau_scale = 1.0
    
    # Scale with error_rate (lower rates need fewer errors)
    # Use square (power of 2) to get more aggressive scaling at low rates
    # At error_rate=0.001, we want ~1/100 the errors of error_rate=0.01
    # (0.001/0.01)^2 = 0.1^2 = 0.01 = 1/100
    # error_rate_scale = (error_rate / BASELINE_ERROR_RATE) ** 0.5
    error_rate_scale = 1.0
    
    # Combine scales
    max_errors = int(BASELINE_MAX_ERRORS * tau_scale * error_rate_scale)
    
    # Ensure minimum (at least 1,000 errors for any configuration)
    return max(1_000, max_errors)

def calculate_max_shots(error_rate: float, tau_rounds: int) -> int:
    """
    Calculate MAX_SHOTS based on error_rate and tau_rounds.
    
    IMPORTANT: MAX_SHOTS needs to scale INVERSELY with error_rate:
    - Small error rates (0.001): Need MANY shots to collect errors (errors are rare)
    - Large error rates (0.007): Collect errors quickly, so fewer shots needed
    
    Strategy:
    - Scale with MAX_ERRORS (proportional): More errors need more shots
    - Scale INVERSELY with error_rate: Small rates need more shots to collect errors
    
    Args:
        error_rate: Physical error rate (e.g., 0.001, 0.01)
        tau_rounds: Number of measurement rounds
    
    Returns:
        Maximum number of shots to run for this error_rate and tau_rounds
    """
    max_errors = calculate_max_errors(error_rate, tau_rounds)
    
    # Scale proportionally with MAX_ERRORS: more errors need more shots
    shots_from_errors = BASELINE_MAX_SHOTS * (max_errors / BASELINE_MAX_ERRORS)
    
    # Scale INVERSELY with error_rate: small rates need MORE shots to collect errors
    # At error_rate=0.001, you need ~10x more shots than at 0.01 to collect the same errors
    # Use square root scaling for a reasonable compromise (not too aggressive)
    error_rate_inverse_scale = (BASELINE_ERROR_RATE / error_rate) ** 0.5
    
    max_shots = int(shots_from_errors * error_rate_inverse_scale)
    
    # Ensure minimum: at least enough shots to potentially see errors
    min_shots = max(1_000_000, max_errors * 100)  # At least 100× max_errors
    return max(min_shots, max_shots)

# Default values (for backward compatibility and simple cases)
# These are calculated for the default TAU_ROUNDS and a moderate error rate (0.5%)
# 
# IMPORTANT: These defaults are ONLY used when:
# 1. NOT using per-task collection_options (has_per_task_options = False)
# 2. Calling functions without explicitly specifying max_shots/max_errors
#
# When using adaptive per-task options (the current default), each task gets its own
# max_errors/max_shots based on its error_rate and tau_rounds, so these defaults are
# NOT used for the actual stopping criteria. They may still be used as fallback values
# in some edge cases (e.g., when finding max_per_task_shots if no tasks have options).
#
# The choice of 0.005 (0.5%) is arbitrary - it's a moderate error rate that provides
# reasonable defaults for quick tests. For production runs, use adaptive per-task options.
MAX_ERRORS = calculate_max_errors(0.005, TAU_ROUNDS)  # Default for error_rate=0.005 (0.5%)
MAX_SHOTS = calculate_max_shots(0.005, TAU_ROUNDS)  # Default for error_rate=0.005 (0.5%)
# Maximum shots and errors for threshold experiments
# These are stopping criteria for statistical collection:
# - MAX_SHOTS: Hard limit on number of experimental runs (caps computation time)
# - MAX_ERRORS: Maximum number of logical errors (shot errors) to observe before stopping
#   IMPORTANT: This is the total number of shot errors, NOT per sliding window.
#   Each shot either has a logical error or doesn't (one prediction per shot).
#   The sliding window decoder processes all windows for a shot and produces ONE prediction per shot.
#   Sinter compares this prediction with the actual observable to determine if there's an error.
# Sinter stops when EITHER limit is reached.
#
# How to set them:
# - For statistical confidence, aim for 100-1000+ errors (more = better confidence)
# - Estimate: shots_needed ≈ MAX_ERRORS / expected_shot_error_rate
# - Example: If shot_error_rate = 0.01 (1%), then 50,000 errors needs ~5,000,000 shots
# - Note: shot_error_rate increases with tau_round (more rounds = more chances for errors)
#
# Important: MAX_ERRORS counts logical errors per shot, not per window.
# The sliding window decoder accumulates corrections from all windows and produces
# one prediction per shot, which is then compared with the actual observable.
#
# Why scale MAX_ERRORS with tau_round:
# - When tau_round increases, shot error rate increases (more rounds = more chances for errors)
# - At high shot error rates (>0.95), you need more independent samples for the same confidence
# - Statistical confidence interval width ∝ sqrt(p * (1-p) / n) where p=error_rate, n=samples
# - When p is close to 1, p*(1-p) is small, so you need more samples for same confidence
# - We use square root scaling: MAX_ERRORS ∝ sqrt(tau_round) as a reasonable approximation
#
# Why NOT scale by number of windows:
# - Errors are counted per shot (one prediction per shot), not per window
# - The number of windows is an internal decoder detail, not related to sample size
# - What matters is tau_round (affects shot error rate), not number of windows
#
# Adaptive MAX_ERRORS and MAX_SHOTS:
# The functions calculate_max_errors() and calculate_max_shots() automatically adjust
# based on error_rate and tau_rounds. Each task gets its own collection_options.
#
# Scaling strategy:
# 1. Scale with tau_rounds: Adaptive power based on error_rate
#    - Low error rates (<0.005): power 1.0 (linear) - shot error rate increases roughly linearly
#    - High error rates (>=0.005): power 1.5 (superlinear) - shot error rate increases superlinearly
#    This accounts for the fact that at high error rates, doubling rounds more than doubles shot error rate
# 2. Scale with error_rate: (error_rate / 0.01)^2 - lower rates need much fewer errors
#    - At error_rate=0.001: (0.001/0.01)^2 = 0.01 = 1/100 of baseline
#    - At error_rate=0.005: (0.005/0.01)^2 = 0.25 = 1/4 of baseline
#    - At error_rate=0.01:  (0.01/0.01)^2 = 1.0 = baseline
#
# Examples (tau_rounds = 40, baseline_rounds = 40, baseline_max_errors = 100,000):
# - error_rate = 0.001: MAX_ERRORS = 100,000 * (40/40)^1.0 * (0.001/0.01)^2 = 100,000 * 1.0 * 0.01 = 1,000
# - error_rate = 0.005: MAX_ERRORS = 100,000 * (40/40)^1.0 * (0.005/0.01)^2 = 100,000 * 1.0 * 0.25 = 25,000
# - error_rate = 0.01:  MAX_ERRORS = 100,000 * (40/40)^1.0 * (0.01/0.01)^2 = 100,000 * 1.0 * 1.0 = 100,000 (baseline)
# - error_rate = 0.007: MAX_ERRORS = 100,000 * (40/40)^1.5 * (0.007/0.01)^2 = 100,000 * 1.0 * 0.49 = 49,000
#
# Examples (tau_rounds = 80, baseline_rounds = 40):
# - error_rate = 0.001: MAX_ERRORS = 100,000 * (80/40)^1.0 * 0.01 = 100,000 * 2.0 * 0.01 = 2,000
# - error_rate = 0.005: MAX_ERRORS = 100,000 * (80/40)^1.0 * 0.25 = 100,000 * 2.0 * 0.25 = 50,000
# - error_rate = 0.01:  MAX_ERRORS = 100,000 * (80/40)^1.0 * 1.0 = 100,000 * 2.0 * 1.0 = 200,000
# - error_rate = 0.007: MAX_ERRORS = 100,000 * (80/40)^1.5 * 0.49 = 100,000 * 2.83 * 0.49 ≈ 138,592
#
# Note: At high error rates (>=0.005), tau_round scaling uses power 1.5 to account for
# superlinear increase in shot error rate. This ensures good statistical reliability even
# when doubling tau_rounds significantly increases shot error rate.
#
# Why adaptive scaling:
# - At low error rates (0.001): Fewer errors needed for good confidence, saves computation
# - At high error rates (0.01): More errors needed, especially with many rounds
# - Each task gets appropriate limits based on its error_rate and tau_rounds
#
# The default MAX_ERRORS and MAX_SHOTS above are for backward compatibility
# (calculated for error_rate=0.005, tau_rounds=TAU_ROUNDS)
#
# Other options:
# - Quick tests: MAX_ERRORS = 1,000, MAX_SHOTS = 100,000
# - Moderate confidence: MAX_ERRORS = 10,000, MAX_SHOTS = 1,000,000
# - Very high confidence: MAX_ERRORS = 100,000, MAX_SHOTS = 50,000,000

