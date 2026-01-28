# Plotting and Uncertainty

Complete guide to understanding plots, uncertainty regions, and how to reduce uncertainty.

## Table of Contents
1. [Reducing Uncertainty in Plots](#reducing-uncertainty-in-plots)
2. [Why Uncertainty Region Position Changes](#why-uncertainty-region-position-changes)
3. [Zero Errors and High Uncertainty](#zero-errors-and-high-uncertainty)
4. [High Uncertainty When Shot Error Rate > 0.5](#high-uncertainty-when-shot-error-rate--05)
5. [Shot Errors vs Per-Round Errors](#shot-errors-vs-per-round-errors)
6. [Understanding failure_units_per_shot_func](#understanding-failure_units_per_shot_func)

---

## Reducing Uncertainty in Plots

### The Problem

Even with 9000 errors collected for `error_rate=0.009`, the uncertainty region appears very large. This is due to two factors:

1. **`highlight_max_likelihood_factor=1000` is too large**
2. **Singularity near p_shot = 0.5**: the shot→per-round map has dp_round/dp_shot → ∞ as p_shot → 0.5, so any uncertainty in shot space is massively amplified in per-round space when shot rate is near 0.5 (e.g. high error rate or many rounds). See [Singularity_Near_Half_Shot_Rate.md](Singularity_Near_Half_Shot_Rate.md).

### Solution: Reduce `highlight_max_likelihood_factor`

#### Current Setting

```python
highlight_max_likelihood_factor=1000  # Too large!
```

This means the uncertainty region includes hypotheses that are up to **1000× less likely** than the maximum likelihood hypothesis. This is extremely wide!

#### Recommended Values

| Value | Interpretation | Use Case |
|-------|---------------|----------|
| **5** | Very tight confidence (~90%) | For tight bounds on log-scale plots |
| **10** | Tighter confidence interval | **Recommended for log-scale plots** |
| **20** | ~95% confidence interval | Standard, but can appear wide on log scale |
| **100** | Very wide confidence | For exploratory analysis |
| **1000** | Extremely wide | Too wide for publication |

#### Fix

Change `highlight_max_likelihood_factor` to a smaller value:

```python
sinter.plot_error_rate(
    ax=ax,
    stats=stats,
    x_func=lambda stat: stat.json_metadata.get('error_rate', stat.json_metadata.get('p', 0)),
    group_func=lambda stat: f"L={stat.json_metadata.get('L', stat.json_metadata.get('d', '?'))}",
    failure_units_per_shot_func=lambda stat: stat.json_metadata.get('num_rounds', stat.json_metadata.get('r', 1)),
    highlight_max_likelihood_factor=10,  # Tighter - better for log-scale plots
)
```

### Why 9000 Errors Still Shows Large Uncertainty?

**9000 errors is actually statistically sufficient!** The issue is visual:

1. **Log scale amplifies visual width**: On a log-scale plot, even small absolute uncertainties look large
2. **Singularity near p_shot = 0.5**: When shot rate is near 0.5 (e.g. high physical error or many rounds), the shot→per-round conversion has a singularity (dp_round/dp_shot → ∞), so per-round uncertainty blows up. See [Singularity_Near_Half_Shot_Rate.md](Singularity_Near_Half_Shot_Rate.md).
3. **`highlight_max_likelihood_factor`**: This controls the visual width, not just statistical precision

**With 9000 errors:**
- Statistical precision: ~1-2% relative precision in shot space (excellent!)
- Visual width: Depends on `highlight_max_likelihood_factor` and log scale

**Solution**: Reduce `highlight_max_likelihood_factor` to 10 (or even 5) for tighter visual bounds.

### Optional: Collect More Errors

If you want even better precision:

```python
BASELINE_MAX_ERRORS = 2000  # Instead of 1000
```

This gives:
- `error_rate=0.009`: `MAX_ERRORS = 18,000`
- Better statistical precision (~2.9% relative precision)

---

## Why Uncertainty Region Position Changes

### Observation

After changing `highlight_max_likelihood_factor` from 1000 to 20, the uncertainty region moved from **below** the line to **above** the line. This is due to how the shot→per-round map (and its **singularity near p_shot = 0.5**, where dp_round/dp_shot → ∞) interacts with different confidence interval widths.

### The Shot→Per-Round Map and Singularity Near 0.5

The conversion from shot error rate to per-round error rate is **nonlinear**, and has a **singularity at p_shot = 0.5** (dp_round/dp_shot → ∞):

```python
round_error_rate = 0.5 - 0.5 * (1 - 2 * shot_error_rate)^(1/pieces)
```

This transformation:
- Is **concave** (curved downward) for small error rates
- Compresses higher values more than lower values
- Does **not preserve symmetry** of confidence intervals

### How `highlight_max_likelihood_factor` Affects Position

**With `highlight_max_likelihood_factor=1000` (very wide)**:
- Confidence interval is very wide in shot space
- Upper bound is much higher than best estimate
- After transformation: Upper bound gets compressed **more** than lower bound
- Result: Uncertainty region appears **below** the line

**With `highlight_max_likelihood_factor=20` (narrower)**:
- Confidence interval is narrower in shot space
- Upper and lower bounds are closer to best estimate
- After transformation: The asymmetry pattern changes
- Result: Uncertainty region can appear **above** the line

### Why the Position Changes

The position (above vs below) depends on:

1. **The error rate range**: Different error rates have different transformation curves
2. **The confidence interval width**: Wider intervals transform differently than narrow ones
3. **The number of rounds**: More rounds amplify the transformation effect
4. **The actual data**: The true error rate and collected errors affect the confidence interval shape

### Is This Correct?

**Yes, this is mathematically correct!**

The uncertainty region represents the **confidence interval in per-round error rate space**. The nonlinear transformation correctly converts the confidence interval, but:
- It doesn't preserve symmetry
- The position (above/below) can vary
- This is expected behavior

### Visual Explanation

#### Wide Confidence Interval (factor=1000)

```
Shot Space:
  low:  0.05  ────────────────
  best: 0.10  ────────●───────
  high: 0.15  ────────────────

After Transformation (100 rounds):
  low:  0.0005  ────────────────
  best: 0.0010  ────────●───────
  high: 0.0015  ────────────────
  
But the transformation compresses the upper bound MORE:
  Visual result: Region appears BELOW the line
```

#### Narrow Confidence Interval (factor=20)

```
Shot Space:
  low:  0.095  ────────────────
  best: 0.100  ────────●───────
  high: 0.105  ────────────────

After Transformation (100 rounds):
  low:  0.00095  ────────────────
  best: 0.00100  ────────●───────
  high: 0.00105  ────────────────
  
With narrower bounds, the asymmetry pattern changes:
  Visual result: Region can appear ABOVE the line
```

### The Key Point

**The position (above/below) is not meaningful** - what matters is:
- ✅ The **line** represents the best estimate (maximum likelihood)
- ✅ The **shaded region** represents the confidence interval
- ✅ Both are correctly calculated in per-round error rate space

The fact that the region appears above or below is just a consequence of the nonlinear transformation, not an error.

---

## Zero Errors and High Uncertainty

### The Problem

When you observe **0 errors** out of many shots (e.g., 50,000,000 shots), the logical error rate is extremely low, but the **statistical uncertainty is high** in the plot. This seems contradictory - why is uncertainty high when the error rate is so convincingly low?

### The Answer: Confidence Intervals for Zero Events

#### What "0 errors" Means

When you observe 0 errors out of N shots:
- **Best estimate**: Error rate = 0
- **But you can't distinguish between**:
  - True error rate = 0 (perfect decoder)
  - True error rate is just very small (e.g., 1×10⁻⁹)

#### How Confidence Intervals Work

Sinter uses `fit_binomial` to calculate confidence intervals based on **Bayesian inference**:

1. **Maximum likelihood estimate**: With 0 errors, the best estimate is `p = 0`
2. **Confidence interval**: Finds the range of probabilities that are "compatible" with the data
3. **Upper bound**: Even with 0 errors, there's an upper bound on what the true error rate could be

#### Example: 0 Errors Out of 50,000,000 Shots

For 0 errors with `max_likelihood_factor = 1000` (default):
- **Shot error rate**: 0 (best estimate)
- **Upper bound**: Approximately `3.7 × 10⁻⁸` (roughly 3/50M, similar to "rule of 3")
- **Per-round error rate** (with 100 rounds): Upper bound ≈ `3.7 × 10⁻¹⁰` per round

The **uncertainty region** in the plot shows this upper bound, which is why it appears high even though you observed 0 errors.

### The "Rule of 3"

A simple approximation for 0 errors:
- **Upper bound (95% confidence)** ≈ `3 / N`
- For 50M shots: `3 / 50,000,000 ≈ 6 × 10⁻⁸` shot error rate
- Per-round (100 rounds): `≈ 6 × 10⁻¹⁰` per round

This matches what you see in the plots - the uncertainty region extends up to this upper bound.

### Why This is Correct Behavior

The high uncertainty for 0 errors is **statistically correct**:
1. **You can't prove a negative**: 0 errors doesn't prove error rate = 0
2. **Uncertainty reflects ignorance**: The wide interval correctly shows you don't know if the rate is 0 or just very small
3. **One error changes everything**: Once you see 1 error, you get a much tighter upper bound

---

## High Uncertainty When Shot Error Rate > 0.5

When shot error rate is near or above 0.5, the plotted uncertainty region in **per-round** space often looks very wide, even if you collected many errors. Two effects combine:

### 1. Binomial uncertainty is largest at p = 0.5

The variance of the binomial proportion is **p(1−p)/n**, which is **maximized at p = 0.5** (value 0.25/n). So:

- For the same number of shots, the confidence interval in **shot error rate** is widest when p_shot ≈ 0.5.
- `fit_binomial` returns [low, high] in shot space; that interval is naturally wider when the true rate is near 0.5.

### 2. Conversion singularity: dp_round/dp_shot → ∞ at p_shot = 0.5

The XOR-model relation is **p_shot = (1 − (1−2·p_round)^N) / 2**. This curve has a **maximum at p_round = 0.5**, where p_shot = 0.5. So:

- **dp_shot/dp_round = 0** at p_round = 0.5.
- The **inverse** (shot → per-round) therefore has **dp_round/dp_shot → ∞** as p_shot → 0.5.

Any fixed interval in shot rate near 0.5 (e.g. [0.48, 0.52]) maps to a **very large** interval in per-round rate. For **p_shot > 0.5**, sinter uses the “high” branch (p_round > 0.5), but the derivative is still huge near the boundary, so small changes in p_shot produce large changes in p_round.

### Net effect

1. **Shot space**: The [low, high] interval from `fit_binomial` is wider when p_shot ≈ 0.5.
2. **Per-round space**: That interval is then passed through `shot_error_rate_to_piece_error_rate`. Near p_shot = 0.5 the map is singular, so the converted interval becomes very wide.

So **high per-round uncertainty when shot rate > 0.5 is expected**: it comes from binomial variance being largest near 0.5 and from the **singularity near p_shot = 0.5** (dp_round/dp_shot → ∞), which amplifies any shot-space uncertainty in per-round space. Reducing `highlight_max_likelihood_factor` tightens the *shot-space* interval that gets converted, but cannot remove this singularity. For very high shot rates, consider plotting in shot space or limiting the physical parameter range so that shot rates stay below ~0.5 where possible.

### Does increasing max_errors or max_shots help?

**Yes.** More data narrows the confidence interval in **shot space**, and that narrower interval is then converted to per-round space. So:

- **Increasing `max_errors`** (and thus total shots when you hit that cap) → smaller variance in the binomial estimate → narrower [low, high] in shot space → narrower (though still amplified) band in per-round space.
- **Increasing `max_shots`** → same effect when you’re in a high-error regime and stop by `max_errors`; when you stop by `max_shots`, more shots still improve precision.

**But** near p_shot = 0.5 the amplification is so strong that you need a **very** narrow shot-space interval to get a “reasonable” per-round interval. So you may need a large increase in data (e.g. 10× or more errors/shots) to see a modest tightening of the per-round band. The benefit is real but diminishing as you approach 0.5.

### Practical options

| Strategy | When it helps |
|----------|----------------|
| **Increase `max_errors` / `max_shots`** | Always helps; biggest effect when p_shot is not too close to 0.5. Near 0.5, use large values (e.g. 100k+ errors) if you need tighter per-round bands. |
| **Use smaller `highlight_max_likelihood_factor`** (e.g. 5–10) | Shrinks the shot-space interval that gets converted, so per-round bands get tighter. You already do this; going below 5 trades rigor for narrowness. |
| **Avoid p_shot > 0.5** | Best way to avoid the singularity: use lower physical error rate `p`, fewer rounds, or smaller code size so shot rate stays below ~0.4–0.5. |
| **Plot in shot space for high-rate points** | For (d, p) where p_shot > 0.5, plot “Logical error rate per shot” instead of “per round” so the audience sees the direct statistic without the singular conversion. |
| **Restrict the plotted (p, d) range** | Omit or grey out points where p_shot > 0.5 if the goal is a clean per-round threshold plot. |

So: **yes, increase `max_errors` (and `max_shots` if you’re not yet limited by `max_errors`)**—it does help. For points that still sit near or above p_shot = 0.5, combine that with “avoid the regime” or “plot in shot space” where appropriate.

**Formal scaling and numbers:** The singularity and the scaling of required sample size with ε, N, and target per-round width Δ are derived in [Singularity_Near_Half_Shot_Rate.md](Singularity_Near_Half_Shot_Rate.md). Summary: \(dp_{\mathrm{round}}/dp_{\mathrm{shot}} = (1/N)(2\varepsilon)^{1/N - 1}\) with ε = |p_shot − 0.5|, and required shots (or max_errors) scale like \(1/((\Delta N)^2 \varepsilon^2)\). That doc also gives an approximate table (e.g. for N=100, ε=0.01, Δ=1%: order 10⁴ shots / ~5×10³ errors; for ε=0.001, order 10⁶ errors).

---

## Shot Errors vs Per-Round Errors

### The Issue

There's an important distinction:

1. **What we collect**: **Shot errors** (logical errors per shot)
   - `MAX_ERRORS` counts the number of shots that have logical errors
   - Each shot produces 0 or 1 logical error
   - This is what `sinter` measures

2. **What we display**: **Per-round error rate** (logical error rate per round)
   - The plot shows "Logical Error Rate per Round"
   - This is **converted** from shot error rate using:
     ```python
     per_round_rate = shot_error_rate_to_piece_error_rate(shot_rate, pieces=tau_rounds)
     ```

### The Problem

**Increasing `MAX_ERRORS` collects more shot errors, but:**
- The shot→per-round map has a **singularity near p_shot = 0.5** (dp_round/dp_shot → ∞), so any shot-space uncertainty is hugely amplified in per-round space when shot rate is near 0.5
- For high shot error rates (e.g. many rounds or high physical p), shot rate is often near 0.5, so per-round uncertainty blows up even with good shot-space precision
- See [Singularity_Near_Half_Shot_Rate.md](Singularity_Near_Half_Shot_Rate.md) for the math and required sample sizes

### Why This Happens

#### Example: High Shot Error Rate

For `tau_rounds = 100` and per-round rate = 0.01:
- Shot error rate ≈ 0.63 (63% of shots have errors)
- With 9,000 errors: Need ~14,286 shots
- Statistical precision in shot space: ~1.5% relative

But after conversion to per-round space:
- Per-round rate ≈ 0.01
- Precision in per-round space is **much worse** than in shot space because p_shot ≈ 0.63 is **near 0.5**, where the map has a singularity (dp_round/dp_shot → ∞)

#### The Singularity Near p_shot = 0.5

The conversion formula is:
```
per_round_rate = 0.5 - 0.5 * (1 - 2 * shot_rate)^(1/tau_rounds)
```

The derivative dp_round/dp_shot tends to **∞** as p_shot → 0.5. So:
- Near p_shot = 0.5, small changes in shot rate → huge changes in per-round rate
- Any shot-space confidence interval maps to a very wide per-round interval there
- That is why "nonlinear" is not enough—the **singularity near 0.5** is what makes uncertainty explode

### The Solution

**Keep Current Approach (Recommended)**:
- We're correctly measuring shot errors (what `sinter` does)
- We're correctly converting to per-round for display
- Keep `MAX_ERRORS` scaling with rounds (your insight was correct!)
- But understand that precision improvements are limited for high shot error rates
- The conversion is mathematically correct; the large per-round uncertainty when shot rate is high comes from the **singularity near p_shot = 0.5** (see [Singularity_Near_Half_Shot_Rate.md](Singularity_Near_Half_Shot_Rate.md))

---

## Understanding failure_units_per_shot_func

### What It Does

`failure_units_per_shot_func` tells sinter **how many "failure units" are in each shot**, so it can convert from **shot error rate** to **per-unit error rate**.

### Key Concepts

#### What is a "Failure Unit"?

A **failure unit** is whatever you want to measure the error rate for. Common examples:
- **Rounds**: For surface code memory experiments, the unit is "one round"
- **Gates**: For gate-level experiments, the unit might be "one gate"
- **Time steps**: For time-dependent experiments, the unit might be "one time step"

#### What is "Per Shot"?

- **Shot error rate**: The probability that a shot (one complete execution) has a logical error
- **Per-unit error rate**: The probability that a single unit (e.g., one round) has an error

### The Problem

**Sinter measures shot error rate**, but you might want to **display per-round error rate**.

**Example**:
- You run a circuit with 100 rounds
- 63% of shots have logical errors → **shot error rate = 0.63**
- But what's the **per-round error rate**? (Not 0.63/100 = 0.0063, because the relationship is nonlinear!)

### The Solution: `failure_units_per_shot_func`

This function tells sinter: **"Each shot contains N failure units"**

For surface code memory experiments:
```python
failure_units_per_shot_func=lambda stat: stat.json_metadata.get('num_rounds', stat.json_metadata.get('r', 1))
```

This says: "Each shot has `num_rounds` rounds (failure units)"

### The Conversion Formula

Sinter uses this formula to convert shot error rate to per-unit error rate:

```
P_unit = 0.5 - 0.5 * (1 - 2 * P_shot)^(1/units_per_shot)
```

Where:
- `P_shot` = shot error rate (e.g., 0.63 = 63%)
- `units_per_shot` = number of failure units per shot (e.g., 100 rounds)
- `P_unit` = per-unit error rate (e.g., per-round error rate)

### Why Nonlinear?

Because errors accumulate across rounds:
- Round 1: Small chance of error
- Round 2: Small chance of error
- ...
- Round 100: Small chance of error
- **Shot error** = "Did ANY round have an error?" (OR of all rounds)

The relationship is:
```
P_shot = 1 - (1 - P_round)^rounds
```

If `P_round = 0.01` (1% per round) and `rounds = 100`:
- `P_shot = 1 - (1 - 0.01)^100 ≈ 0.63` (63% shot error rate)

So 1% per round → 63% shot error rate, not 100%!

### In Your Code

```python
failure_units_per_shot_func=lambda stat: stat.json_metadata.get('num_rounds', stat.json_metadata.get('r', 1))
```

This:
1. Extracts `num_rounds` from metadata (e.g., 100)
2. Tells sinter: "Each shot has 100 rounds"
3. Sinter converts shot error rate → per-round error rate
4. Plot shows "Logical Error Rate per Round" instead of "per Shot"

### What Values Are Available?

The Python expression can use:
- **`metadata`**: The parsed `json_metadata` dictionary
- **`m`**: Shorthand for `metadata.get("key", None)`
- **`decoder`**: Decoder name (e.g., "sliding_window")
- **`stat`**: Full `sinter.TaskStats` object

---

## Summary

1. **Reduce `highlight_max_likelihood_factor`** to 10 (or 5) for tighter uncertainty regions
2. **Uncertainty region position** (above/below) is a visual artifact of the shot→per-round map—it's correct
3. **Large uncertainty when shot rate ≈ 0.5** is due to the **singularity near p_shot = 0.5** (dp_round/dp_shot → ∞), not just “nonlinearity”; see [Singularity_Near_Half_Shot_Rate.md](Singularity_Near_Half_Shot_Rate.md)
4. **Zero errors** lead to high uncertainty because you can't prove the rate is exactly 0
5. **Shot errors vs per-round errors**: We measure shot errors, display per-round (converted)
6. **`failure_units_per_shot_func`** tells sinter how many rounds per shot for conversion
