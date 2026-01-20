# Statistical Reliability is Independent of Decoding Method

## Key Principle

**Statistical reliability (confidence in error rate estimates) does NOT depend on the decoding method or window size.**

## What Affects Statistical Reliability

Statistical reliability depends ONLY on:
1. **Number of errors collected** (`MAX_ERRORS`)
2. **Number of shots collected** (`MAX_SHOTS`)
3. **The actual error rate** (affects how quickly errors are collected)

## What Does NOT Affect Statistical Reliability

- `n_sliding_window` (window size)
- `n_overlap` (overlap between windows)
- Decoding method (sliding window vs full PyMatching)
- Number of windows used

## Why This Is True

1. **Error Counting**: Sinter counts errors as "did the decoder prediction match the actual observable?" - **one error per shot**, regardless of how many windows were used.

2. **Statistical Confidence**: For a binomial distribution, confidence intervals depend on:
   - Number of errors observed
   - Number of shots taken
   - The error rate estimate
   
   They do NOT depend on how the decoder works internally.

3. **Decoding Accuracy vs Statistical Reliability**:
   - **Decoding accuracy**: How well the decoder corrects errors (affected by `n_sliding_window`)
   - **Statistical reliability**: How confident we are in our error rate estimate (NOT affected by `n_sliding_window`)

## Code Verification

The functions `calculate_max_errors()` and `calculate_max_shots()` in `experiment_config.py`:
- Only take `error_rate` and `tau_rounds` as parameters
- Do NOT use `n_sliding_window` or `n_overlap`
- Are called in `tasks.py` with only `error_rate` and `num_rounds`

## Example

For `error_rate=0.007`, `tau_rounds=80`:
- `MAX_ERRORS = 97,999` (regardless of `n_sliding_window`)
- `MAX_SHOTS = 9,799,900` (regardless of `n_sliding_window`)

Changing `n_sliding_window` from 20 to 100:
- ✅ Does NOT change `MAX_ERRORS` or `MAX_SHOTS`
- ✅ Does NOT change statistical reliability
- ⚠️ May change decoding accuracy (how well errors are corrected)
- ⚠️ May change the measured error rate (due to different decoding accuracy)

## If You See Different Statistical Reliability

If you observe that statistical reliability seems to depend on `n_sliding_window`, this is likely due to:

1. **Different error rates**: Smaller windows may give different (less accurate) error rate estimates, but the statistical confidence in those estimates is the same.

2. **Different number of errors collected**: If the experiment stops at different times, you may have collected different numbers of errors. Check `stat.errors` and `stat.shots` in the results.

3. **Confusion between accuracy and reliability**: 
   - Lower decoding accuracy → different error rate estimate
   - But statistical reliability (confidence in that estimate) is the same if you collected the same number of errors

## Conclusion

The code is correct: `n_sliding_window` does NOT affect statistical reliability. Statistical reliability depends only on the number of errors and shots collected, which is controlled by `MAX_ERRORS` and `MAX_SHOTS`, which are independent of `n_sliding_window`.
