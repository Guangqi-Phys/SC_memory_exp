# Why More Rounds Can Worsen Shot Error Rate (Even When the Decoder Works)

## The puzzle

You might expect: *“If the decoder can correct errors when rounds are small, it should also fix errors when rounds are large.”*  

In practice we see: when rounds are **large** (and/or physical error rate is high), shot error rate often goes toward **0.5** — the logical outcome looks like a coin flip. So it seems the decoder “stops working” for large rounds. Why?

## Short answer

The decoder **does** correct errors in every round. The issue is not that it “stops working,” but that **each round adds new, independent noise**. The logical bit you care about is the **parity over all rounds** (XOR). So:

- **Few rounds** → few independent “logical error this round?” events → shot failure rate can stay small.
- **Many rounds** → many independent events → even a **small** per-round logical error rate accumulates, and in the limit shot failure rate → **0.5**.

So “more rounds” means more independent chances for a logical flip. The decoder keeps the **per-round** logical error rate low (when below threshold), but it cannot remove the **accumulation** over rounds. That accumulation is why shot error rate goes to 0.5 as rounds grow.

---

## 1. Each round adds new noise

Important point: **every round is a new layer of gates and measurements, with new physical errors.**

- The decoder does not get to “fix everything and then stop.”
- After round 1, you have some syndrome and some residual logical effect. In round 2, **new** physical errors happen, new syndrome is produced, and the decoder uses rounds 1+2 together. In round 3, again **new** errors, and so on.
- So “more rounds” = more layers of **independent** physical noise.

The decoder’s job is to turn that syndrome into a best guess for the **total** logical error so far. It can do that well (low logical error **per round**) when physical noise is below threshold, but it cannot make extra rounds add zero noise.

---

## 2. The logical observable is parity (XOR) over rounds

In a **memory experiment** (e.g. rotated surface code memory), the stabilizer measurements don’t reveal the logical bit directly. What you get from the decoder is whether the **logical Z** has flipped an **odd** or **even** number of times over the **whole** circuit.

- **Odd number of logical flips** → shot **fails** (wrong logical outcome).
- **Even number** → shot **succeeds**.

So the effective “logical coin” is:

- **Round 1:** with probability `p_round`, flip; else don’t.
- **Round 2:** again, independently, with probability `p_round`, flip; else don’t.
- …
- **Round N:** same, independently.

The decoder sets how big `p_round` is (small below threshold, large above), but it does **not** change the fact that each round is an independent “flip or not” with that probability. The **shot** fails if the **total** number of flips is odd.

So we’re really asking: *“In N independent rounds, each with probability `p_round` of a logical flip, what is the probability of an **odd** number of flips?”*  

That is exactly the XOR model:

\[
P(\text{shot fails}) = \frac{1 - (1 - 2\,p_{\mathrm{round}})^N}{2}.
\]

When \(N \to \infty\) and \(p_{\mathrm{round}} > 0\), this tends to **1/2**. So as you add more and more rounds, you add more and more independent “flips,” and the parity becomes 50–50. The decoder does not “forget” how to correct; the **accumulation** of many small per-round error rates is what drives shot error rate to 0.5.

---

## 3. Why “decoder works for few rounds but not for many” is not contradictory

- **Few rounds (e.g. N = 5):**  
  Even if \(p_{\mathrm{round}} = 0.01\), the chance of an odd number of flips is still small. So shot error rate can be low, and the decoder “seems to work great.”

- **Many rounds (e.g. N = 100):**  
  You have 100 independent “flip or not” events. Even with \(p_{\mathrm{round}} = 0.01\), the parity over 100 rounds is close to random, so shot error rate ≈ 0.5.

So the decoder **is** working in both cases (it keeps \(p_{\mathrm{round}}\) small when below threshold). The difference is:

- **Small N:** Few independent flips → shot outcome still biased toward “even number of flips.”
- **Large N:** Many independent flips → parity approaches 50–50, so shot error rate → 0.5.

So it’s not that “the decoder can’t reveal the logical information when rounds are large.” It’s that the **question** we ask (“odd or even total flips over N rounds?”) becomes a 50–50 outcome when N is large and \(p_{\mathrm{round}} > 0\), no matter how good the decoder is at keeping \(p_{\mathrm{round}}\) small.

---

## 4. Above threshold (high physical error rate)

When the **physical** error rate is **above** the code’s threshold:

- The decoder cannot correct well. So **per-round** logical error rate \(p_{\mathrm{round}}\) is large (e.g. close to 0.5).
- Then even a **small** number of rounds is enough to make shot error rate ≈ 0.5, because each round is almost a random flip.

So for “high error rate + many rounds,” you see shot error rate → 0.5 for two reasons:

1. **Above threshold:** \(p_{\mathrm{round}}\) is large, so parity randomizes quickly.
2. **Below threshold but many rounds:** \(p_{\mathrm{round}}\) is small, but **accumulation** over many rounds still drives shot error rate → 0.5.

In both cases, “more rounds” means more independent logical-error events, so the parity (and hence the shot error rate) moves toward 0.5.

---

## 5. Summary

| Your intuition | What’s actually going on |
|----------------|---------------------------|
| “Decoder fixes errors when rounds are small → it should fix when rounds are large.” | The decoder **does** correct each round (keeps \(p_{\mathrm{round}}\) small when below threshold). “More rounds” doesn’t make it stop; it adds **more independent** rounds, each with a small chance of a logical flip. |
| “Decoder cannot reveal logical info when rounds are large.” | The decoder *does* produce a logical answer. The issue is that the **observable** is “odd vs even number of flips over N rounds.” With many rounds and \(p_{\mathrm{round}} > 0\), that parity becomes 50–50, so the **statistic** (shot error rate) tends to 0.5. |
| “If it corrects when N is small, it should correct when N is large.” | Correcting **each round** is not the same as making the **total parity over N rounds** non-random. More rounds = more independent flips = parity → 0.5. |

So: **the decoder is not “failing” when rounds are large; the logical bit is the parity over many independent rounds, and that parity tends to 0.5 as N grows.**  
That is why shot error rate often goes to 0.5 for large rounds (or high physical error rate), and why the “decoder works for small N but not large N” is really about **accumulation over rounds**, not the decoder forgetting how to decode.

See [XOR_Model_Formula_Derivation.md](XOR_Model_Formula_Derivation.md) for the formula and [Singularity_Near_Half_Shot_Rate.md](Singularity_Near_Half_Shot_Rate.md) for why that makes per-round uncertainty explode near p_shot = 0.5.
