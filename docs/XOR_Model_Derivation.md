# Mathematical Derivation of Shot-to-Per-Round Error Rate Conversion

## The XOR Model

The conversion formula is based on the assumption that **errors accumulate across rounds via XOR** (exclusive OR), not simple addition.

### Key Insight: XOR Probability Formula

For N independent Bernoulli trials (rounds), each with probability `p` of "flipping", the probability that the **XOR of all N rounds equals 1** (i.e., odd number of flips) is:

```
P(XOR = 1) = (1 - (1 - 2p)^N) / 2
```

This is a well-known result in probability theory.

### The "Randomize Rate" Concept

The code uses a concept called **"randomize_rate"** which represents the probability of "randomization" or "flipping" per round. The relationship is:

```
randomize_rate = 2 × per_round_error_rate
```

Why the factor of 2? This comes from the XOR formula structure.

### Forward Direction: Per-Round → Shot Error Rate

If we have:
- `p_round` = per-round error rate
- `N` = number of rounds

Then the shot error rate is:

```
shot_error_rate = (1 - (1 - 2×p_round)^N) / 2
```

Or equivalently, using `randomize_rate = 2 × p_round`:

```
shot_error_rate = (1 - (1 - randomize_rate)^N) / 2
```

### Reverse Direction: Shot Error Rate → Per-Round (What the Code Does)

Given `shot_error_rate` and `N`, we need to solve for `p_round`.

Starting from:
```
shot_error_rate = (1 - (1 - randomize_rate)^N) / 2
```

Solving for `randomize_rate`:

```
2 × shot_error_rate = 1 - (1 - randomize_rate)^N
(1 - randomize_rate)^N = 1 - 2 × shot_error_rate
1 - randomize_rate = (1 - 2 × shot_error_rate)^(1/N)
randomize_rate = 1 - (1 - 2 × shot_error_rate)^(1/N)
```

Then the per-round error rate is:

```
p_round = randomize_rate / 2
        = [1 - (1 - 2 × shot_error_rate)^(1/N)] / 2
```

### The Code Implementation

This matches exactly what the code does:

```python
randomize_rate = 2 * shot_error_rate                    # Step 1: Multiply by 2
round_randomize_rate = 1 - (1 - randomize_rate)^(1 / N)  # Step 2: Solve for per-round randomize_rate
round_error_rate = round_randomize_rate / 2              # Step 3: Convert back to error rate
```

Wait, there's a subtlety here. Let me check the code more carefully...

Actually, looking at the code:
```python
randomize_rate = 2 * shot_error_rate
round_randomize_rate = 1 - (1 - randomize_rate)^(1 / pieces)
round_error_rate = round_randomize_rate / 2
```

This is solving:
- `randomize_rate = 2 × shot_error_rate` (this is the "target randomize rate" for the shot)
- `round_randomize_rate = 1 - (1 - randomize_rate)^(1/N)` (per-round randomize rate)
- `round_error_rate = round_randomize_rate / 2` (convert back to error rate)

But this doesn't quite match the XOR formula directly. Let me reconsider...

### Alternative Interpretation: Depolarizing Channel Model

The "randomize_rate" might refer to a **depolarizing channel** model where:
- With probability `randomize_rate`, the state is completely randomized (depolarized)
- The error rate is half of the randomize rate (because randomization can flip to either state)

In this model:
- Shot fails if there's an odd number of rounds with randomization
- P(odd randomizations in N rounds) = (1 - (1 - 2×randomize_rate)^N) / 2

If `shot_error_rate` is the probability of failure:
```
shot_error_rate = (1 - (1 - 2×randomize_rate)^N) / 2
2×shot_error_rate = 1 - (1 - 2×randomize_rate)^N
(1 - 2×randomize_rate)^N = 1 - 2×shot_error_rate
1 - 2×randomize_rate = (1 - 2×shot_error_rate)^(1/N)
2×randomize_rate = 1 - (1 - 2×shot_error_rate)^(1/N)
randomize_rate = [1 - (1 - 2×shot_error_rate)^(1/N)] / 2
```

And since `error_rate = randomize_rate / 2` (in the depolarizing model, error is half of randomization):
```
error_rate = randomize_rate / 2 = [1 - (1 - 2×shot_error_rate)^(1/N)] / 4
```

Hmm, this still doesn't match. Let me look at the code again more carefully...

### Correct Interpretation

Looking at the code step by step:

```python
randomize_rate = 2 * shot_error_rate
```

This sets `randomize_rate = 2 × shot_error_rate`. This is treating `shot_error_rate` as if it came from a model where:
```
shot_error_rate = randomize_rate / 2
```

But that's the reverse! The code is working backwards. Let me think...

Actually, I think the model is:
- Each round has a "randomize rate" `r` (probability of randomization)
- The shot error rate (probability of logical error) is: `shot_error_rate = (1 - (1 - 2r)^N) / 2`
- Given `shot_error_rate`, we want to find `r` such that this holds

From the XOR formula:
```
shot_error_rate = (1 - (1 - 2r)^N) / 2
2 × shot_error_rate = 1 - (1 - 2r)^N
(1 - 2r)^N = 1 - 2 × shot_error_rate
1 - 2r = (1 - 2 × shot_error_rate)^(1/N)
2r = 1 - (1 - 2 × shot_error_rate)^(1/N)
r = [1 - (1 - 2 × shot_error_rate)^(1/N)] / 2
```

And the per-round error rate is `r` (the randomize rate IS the error rate in this model, or `r/2` depending on interpretation).

But the code does:
```python
randomize_rate = 2 * shot_error_rate  # This is 2 × shot_error_rate
round_randomize_rate = 1 - (1 - randomize_rate)^(1/N)  # This is 1 - (1 - 2×shot_error_rate)^(1/N)
round_error_rate = round_randomize_rate / 2  # This is [1 - (1 - 2×shot_error_rate)^(1/N)] / 2
```

So the final answer is:
```
round_error_rate = [1 - (1 - 2×shot_error_rate)^(1/N)] / 2
```

This matches the XOR formula derivation! The code is correct.

## Summary

The formula uses the **XOR probability model**:
- Errors across rounds combine via XOR (odd number of errors = failure)
- The XOR probability formula: `P(XOR=1) = (1 - (1-2p)^N) / 2`
- The code inverts this formula to go from shot error rate to per-round error rate
- The "randomize_rate" is an intermediate variable: `randomize_rate = 2 × shot_error_rate`
- The final per-round error rate is: `[1 - (1 - 2×shot_error_rate)^(1/N)] / 2`

This is **not** simple division because errors accumulate nonlinearly via XOR, not linearly via addition.
