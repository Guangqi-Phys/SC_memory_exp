# surface_code_experiment/config/experiment_config.py

# Default code distances for threshold experiments
L_VALUES = [29, 31, 33]

# Number of measurement rounds (tau)
TAU_ROUNDS = 3

# Sliding window decoding parameters
N_SLIDING_WINDOW = 3  # Window size (n_sliding_window) for sliding window decoding
N_OVERLAP = 0  # Overlap between consecutive windows

# Number of parallel workers for pymatching/sinter
NUM_WORKERS = 10  # Number of parallel workers for sinter.collect

# Window parallelization for sliding window decoder
# Controls how many CPU cores to use for parallelizing window decoding within each shot
# Set to 1 to disable parallelization (uses batch processing only)
# Set to >1 to use multiprocessing for window parallelization
# Recommended: 1-4 (batch processing is usually faster, but multiprocessing can help for many windows)
WINDOW_PARALLEL_WORKERS = 1  # Number of workers for window parallelization (1 = batch only, >1 = multiprocessing)

# Default error rates for threshold experiments
ERROR_RATES = [0.001,0.003,0.005,0.007,0.009,0.01]


# Adaptive MAX_ERRORS and MAX_SHOTS based on error_rate and tau_round
# Baseline: error_rate=0.001 (0.1%), tau_rounds=10, with 100,000 errors and 10,000,000 shots
# MAX_ERRORS scales LINEARLY with both error_rate and tau_rounds
# MAX_SHOTS scales DOWN with error_rate and tau_rounds (errors collected faster)
BASELINE_ROUNDS = 1
BASELINE_ERROR_RATE = 0.001  # 0.1% - reference error rate
BASELINE_MAX_ERRORS = 1_000  # Baseline errors (scales with error_rate × tau_rounds)
BASELINE_MAX_SHOTS = 100_000_000  # Baseline shots (will be reduced for large error rates/rounds)

def calculate_max_errors(error_rate: float, tau_rounds: int) -> int:
    """
    Calculate MAX_ERRORS based on error_rate and tau_rounds.
    
    IMPORTANT NOTE: This uses PHYSICAL error rate as a proxy for LOGICAL error rate.
    The actual logical error rate per shot can be much higher (approaching 1) when:
    - Physical error rate is high (e.g., 0.009)
    - Number of rounds is large (e.g., 100)
    
    Strategy: Scale MAX_ERRORS LINEARLY with both error_rate AND tau_rounds, with a cap.
    - Higher physical error rates → higher logical error rates → need more errors
    - More rounds → higher shot error rate → need more errors
    - BUT: Cap MAX_ERRORS to prevent excessive collection when logical rate is very high
    
    Rationale:
    - Large tau_rounds increases shot error rate (more opportunities for errors)
    - High shot error rates benefit from more errors for better statistical confidence
    - However, when logical error rate approaches 1, we're near the boundary where:
      a) Precision is naturally better (relative precision formula: sqrt((1-p)/n) → 0 as p→1)
      b) Perfect precision isn't necessary (we already know it's "very high")
      c) Per-round conversion makes high shot rates manageable
    
    The decoding method (sliding window vs full decoding) affects DECODING ACCURACY
    (how well errors are corrected), but NOT STATISTICAL RELIABILITY (confidence in the estimate).
    Each shot produces one error count (logical error = decoder prediction != actual observable),
    regardless of how many windows were used in decoding.
    
    Args:
        error_rate: Physical error rate (e.g., 0.001, 0.01)
        tau_rounds: Number of measurement rounds
    
    Returns:
        Maximum number of errors to collect (scales linearly with error_rate and tau_rounds, capped)
    """
    # Scale LINEARLY with error_rate: 2x error_rate → 2x MAX_ERRORS
    error_rate_scale = error_rate / BASELINE_ERROR_RATE
    
    # Scale LINEARLY with tau_rounds: 2x rounds → 2x MAX_ERRORS
    # Rationale: More rounds → higher shot error rate → need more errors for confidence
    # 
    # IMPORTANT: Statistical uncertainty is calculated in SHOT ERROR RATE space, not per-round space.
    # - We measure: logical_error_rate_per_shot = errors / shots
    # - Uncertainty formula: Relative Precision = 2 × z × sqrt((1-p_shot) / n)
    # - Where p_shot is the shot error rate (what we actually measure)
    # - Per-round conversion happens AFTER uncertainty calculation (just for display)
    # 
    # Therefore, MAX_ERRORS should be based on SHOT error rate considerations:
    # - More rounds → higher shot error rate (more opportunities for errors)
    # - Higher shot error rate → we want good precision in shot space
    # - More errors → better precision in shot space
    # - So scaling with rounds is CORRECT (not just a practical compromise)
    tau_scale = 1
    
    max_errors = int(BASELINE_MAX_ERRORS * error_rate_scale * tau_scale)
    
    # Ensure minimum (at least BASELINE_MAX_ERRORS errors for any configuration)
    max_errors = max(BASELINE_MAX_ERRORS, max_errors)
    
    # CAP: When logical error rate is very high (near 1), we don't need extremely large MAX_ERRORS
    # Reason:
    # 1. Per-round conversion makes high shot rates manageable (e.g., 0.9 shot rate → ~0.02 per-round)
    # 2. Relative precision is naturally better near p=1 (formula: sqrt((1-p)/n) → 0)
    # 3. Practical: prevents experiments from running forever
    # 4. We're already near the boundary - perfect precision isn't necessary
    MAX_ERRORS_CAP = 100_000  # Cap at 100k errors
    
    return min(max_errors, MAX_ERRORS_CAP)

def calculate_max_shots(error_rate: float, tau_rounds: int) -> int:
    """
    Calculate MAX_SHOTS based on error_rate and tau_rounds.
    
    Strategy: Make MAX_SHOTS SMALLER for large error rates or large tau_rounds.
    - Large error rates: Collect errors quickly, so fewer shots needed
    - Large tau_rounds: Shot error rate increases, so collect errors faster
    
    Scaling:
    - Scale DOWN with error_rate: Large rates need fewer shots (errors collected faster)
    - Scale DOWN with tau_rounds: More rounds → higher shot error rate → errors collected faster
    
    Args:
        error_rate: Physical error rate (e.g., 0.001, 0.01)
        tau_rounds: Number of measurement rounds
    
    Returns:
        Maximum number of shots to run for this error_rate and tau_rounds
    """
    # Scale DOWN with error_rate: large rates collect errors faster
    # At error_rate=0.009, you collect errors ~9x faster than at 0.001
    # Use square root scaling for a reasonable compromise
    error_rate_scale = (BASELINE_ERROR_RATE / error_rate)
    
    # Scale DOWN with tau_rounds: more rounds → higher shot error rate → errors collected faster
    # Use square root scaling (not linear) to avoid too aggressive reduction
    tau_scale = (BASELINE_ROUNDS / tau_rounds) ** 0.5
    # tau_scale = 1

    
    # Combine scales: both reduce MAX_SHOTS for large error rates/rounds
    max_shots = int(BASELINE_MAX_SHOTS * error_rate_scale * tau_scale)
    
    # Ensure minimum: at least enough shots to potentially collect errors
    # Estimate: need at least 100× max_errors shots (for very low error rates)
    min_shots = max(1_000_000, BASELINE_MAX_ERRORS * 100)
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

