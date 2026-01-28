# What is a Shot in Stim?

## Answer: A Shot = One Sample

**Yes, a shot in Stim is one sample.** They are the same thing.

## Definition

A **shot** is one complete execution/simulation of the circuit. Each shot produces:
- One set of measurement results
- One set of detection events
- One set of observable values

## Examples

### Command Line

```bash
stim sample --shots 5 --in circuit.stim
```

This produces **5 shots** = **5 samples** of the circuit.

### Python API

```python
import stim

circuit = stim.Circuit('''
    H 0
    CNOT 0 1
    M 0 1
''')

sampler = circuit.compile_sampler()
results = sampler.sample(shots=10)  # 10 shots = 10 samples
# Shape: (10, 2) - 10 shots, 2 measurements per shot
```

## What Each Shot Contains

For a surface code memory experiment with `tau_rounds = 100`:

**One shot** contains:
- All measurement results from all 100 rounds
- All detection events from all 100 rounds
- The final logical observable values

**Multiple shots** = multiple independent executions:
- Shot 1: Complete execution with its own noise, measurements, etc.
- Shot 2: Another complete execution (independent)
- Shot 3: Another complete execution (independent)
- ...

## In Your Experiment

When you run:
```python
sinter.collect(..., max_shots=10000, max_errors=1000)
```

This means:
- **max_shots = 10000**: Run the circuit 10,000 times (10,000 shots = 10,000 samples)
- **max_errors = 1000**: Stop after collecting 1,000 logical errors

Each shot:
- Executes the full circuit (all `tau_rounds` rounds)
- Produces one logical error result (0 or 1)
- Is independent of other shots

## Summary

- ✅ **Shot = Sample** (they're the same thing)
- ✅ One shot = one complete execution of the circuit
- ✅ Multiple shots = multiple independent executions
- ✅ Each shot produces one logical error result (0 or 1)
- ✅ `MAX_ERRORS` counts the number of shots that have logical errors
- ✅ `MAX_SHOTS` is the maximum number of times to run the circuit

## Terminology

In Stim and quantum computing literature:
- **Shot**: One execution/sample of the circuit
- **Sample**: Same as shot (used interchangeably)
- **Trial**: Sometimes used synonymously with shot

All refer to one complete run of the circuit from start to finish.
