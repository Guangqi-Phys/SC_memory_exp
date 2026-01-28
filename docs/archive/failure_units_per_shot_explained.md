# Understanding `failure_units_per_shot_func`

## What It Does

`failure_units_per_shot_func` tells sinter **how many "failure units" are in each shot**, so it can convert from **shot error rate** to **per-unit error rate**.

## Key Concepts

### What is a "Failure Unit"?

A **failure unit** is whatever you want to measure the error rate for. Common examples:
- **Rounds**: For surface code memory experiments, the unit is "one round"
- **Gates**: For gate-level experiments, the unit might be "one gate"
- **Time steps**: For time-dependent experiments, the unit might be "one time step"

### What is "Per Shot"?

- **Shot error rate**: The probability that a shot (one complete execution) has a logical error
- **Per-unit error rate**: The probability that a single unit (e.g., one round) has an error

## The Problem

**Sinter measures shot error rate**, but you might want to **display per-round error rate**.

**Example**:
- You run a circuit with 100 rounds
- 63% of shots have logical errors → **shot error rate = 0.63**
- But what's the **per-round error rate**? (Not 0.63/100 = 0.0063, because the relationship is nonlinear!)

## The Solution: `failure_units_per_shot_func`

This function tells sinter: **"Each shot contains N failure units"**

For surface code memory experiments:
```python
failure_units_per_shot_func=lambda stat: stat.json_metadata.get('num_rounds', 100)
```

This says: "Each shot has `num_rounds` rounds (failure units)"

## The Conversion Formula

Sinter uses this formula to convert shot error rate to per-unit error rate:

```
P_unit = 0.5 - 0.5 * (1 - 2 * P_shot)^(1/units_per_shot)
```

Where:
- `P_shot` = shot error rate (e.g., 0.63 = 63%)
- `units_per_shot` = number of failure units per shot (e.g., 100 rounds)
- `P_unit` = per-unit error rate (e.g., per-round error rate)

## Example

### Scenario
- Circuit has **100 rounds** per shot
- **63% of shots** have logical errors → `P_shot = 0.63`

### Calculation

```python
units_per_shot = 100
P_shot = 0.63

P_unit = 0.5 - 0.5 * (1 - 2 * 0.63)^(1/100)
       = 0.5 - 0.5 * (1 - 1.26)^(1/100)
       = 0.5 - 0.5 * (-0.26)^(1/100)
       = 0.5 - 0.5 * (complex number)  # This is why the formula is more complex
```

Actually, for `P_shot < 0.5`, the formula simplifies. The key insight is that the conversion is **nonlinear**.

### Why Nonlinear?

Because errors accumulate across rounds:
- Round 1: Small chance of error
- Round 2: Small chance of error
- ...
- Round 100: Small chance of error
- **Shot error** = "Did ANY round have an error?" (OR of all rounds)

The relationship is:
```
P_shot = 1 - (1 - P_unit)^units_per_shot
```

Solving for `P_unit`:
```
P_unit = 1 - (1 - P_shot)^(1/units_per_shot)
```

But sinter uses a different formula that handles edge cases better.

## In Your Code

In `plotting.py`:

```python
sinter.plot_error_rate(
    ax=ax,
    stats=stats,
    failure_units_per_shot_func=lambda stat: stat.json_metadata.get('num_rounds', stat.json_metadata.get('r', 1)),
    # ...
)
```

This tells sinter:
- **Each shot has `num_rounds` rounds** (failure units)
- Convert shot error rate → per-round error rate
- Display per-round error rate on the plot

## What Values Are Available?

The Python expression has access to:

- **`metadata`**: The parsed `json_metadata` dictionary
- **`m`**: Shorthand for `metadata.get("key", None)`
- **`decoder`**: The decoder name (e.g., "sliding_window")
- **`strong_id`**: Cryptographic hash of the problem
- **`stat`**: The full `sinter.TaskStats` object

### Example Expressions

```python
# Simple: Use metadata field
failure_units_per_shot_func=lambda stat: stat.json_metadata['num_rounds']

# With shorthand
failure_units_per_shot_func=lambda stat: m.r  # m is shorthand for metadata

# With fallback
failure_units_per_shot_func=lambda stat: stat.json_metadata.get('num_rounds', 100)

# Complex: Calculate from other fields
failure_units_per_shot_func=lambda stat: stat.json_metadata['distance'] * 3
```

## Why This Matters

### Without `failure_units_per_shot_func`

If you don't specify this:
- Plot shows **shot error rate** (e.g., 0.63 = 63%)
- This is the probability that a shot (all 100 rounds) has an error
- Hard to compare across different numbers of rounds

### With `failure_units_per_shot_func`

If you specify this:
- Plot shows **per-round error rate** (e.g., 0.01 = 1% per round)
- This is the probability that a single round has an error
- Easy to compare across different numbers of rounds
- More meaningful for understanding code performance

## Summary

1. **`failure_units_per_shot_func`** tells sinter how many failure units (e.g., rounds) are in each shot
2. **Sinter uses this** to convert shot error rate → per-unit error rate
3. **The conversion is nonlinear** because errors accumulate across units
4. **In your code**, you set it to `num_rounds` to display per-round error rates
5. **The formula** handles the nonlinear relationship correctly

This is why your plot shows "Logical Error Rate per Round" instead of "Logical Error Rate per Shot"!
