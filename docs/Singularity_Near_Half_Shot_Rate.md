# Singularity Near p_shot = 0.5 and Required Sample Size

Formal treatment of the shot→per-round conversion singularity and an estimate of how many `max_errors` / `max_shots` are needed to achieve a given per-round uncertainty when shot error rate is near 0.5.

**Quick takeaway:** Define ε = |p_shot − 0.5| and Δ = desired per-round CI half-width. Required shots scale as \(n \gtrsim 1\big/\bigl((\Delta\,N)^2\,\varepsilon^2\bigr)\). Near 0.5 (ε small) you need **much** more data: e.g. N=100, ε=0.01, Δ=1% ⇒ order **10⁴ shots** / **~5×10³ max_errors**; ε=0.001 ⇒ order **10⁶ max_errors**. See the table in §5 for numbers.

---

## 1. Forward and inverse maps

**Forward (XOR model, p_round ≤ 0.5):**
$$
p_{\mathrm{shot}} = \frac{1 - (1 - 2\,p_{\mathrm{round}})^N}{2}.
$$

**Inverse for p_shot ≤ 0.5:**
$$
p_{\mathrm{round}} = f(p_{\mathrm{shot}}) = \frac{1 - (1 - 2\,p_{\mathrm{shot}})^{1/N}}{2}.
$$

**Inverse for p_shot > 0.5** (sinter uses symmetry): \(p_{\mathrm{round}} = 1 - f(1 - p_{\mathrm{shot}})\), i.e. the “high” branch.

---

## 2. Formal singularity

### Derivative for p_shot ≤ 0.5

Let \(x = p_{\mathrm{shot}}\). Then
$$
f(x) = \frac{1 - (1 - 2x)^{1/N}}{2},\qquad
\frac{df}{dx} = \frac{1}{N}\,(1 - 2x)^{1/N - 1}.
$$

For \(N > 1\), the exponent \(1/N - 1\) is negative. As \(x \to 0.5^-\), \((1 - 2x) \to 0^+\), so \((1-2x)^{1/N - 1} \to +\infty\). Hence
$$
\boxed{\ \frac{dp_{\mathrm{round}}}{dp_{\mathrm{shot}}} \to +\infty \quad\text{as}\quad p_{\mathrm{shot}} \to 0.5^-\ \ }
\quad\text{(singularity from below).}
$$

### Derivative for p_shot > 0.5

Here \(p_{\mathrm{round}} = g(p_{\mathrm{shot}}) = \bigl(1 + (2\,p_{\mathrm{shot}} - 1)^{1/N}\bigr)/2\), so
$$
\frac{dg}{dx} = \frac{1}{N}\,(2x - 1)^{1/N - 1}.
$$
As \(x \to 0.5^+\), \((2x - 1) \to 0^+\), so again the derivative diverges:
$$
\boxed{\ \frac{dp_{\mathrm{round}}}{dp_{\mathrm{shot}}} \to +\infty \quad\text{as}\quad p_{\mathrm{shot}} \to 0.5^+\ \ }
\quad\text{(singularity from above).}
$$

### Leading-order scaling

Set **ε = |p_shot − 0.5|** (distance from 0.5). On both sides,
$$
\frac{dp_{\mathrm{round}}}{dp_{\mathrm{shot}}}
= \frac{1}{N}\,(2\varepsilon)^{1/N - 1}
= \frac{1}{N}\,(2\varepsilon)^{-(1 - 1/N)}.
$$

So near 0.5,
$$
\boxed{\ \frac{dp_{\mathrm{round}}}{dp_{\mathrm{shot}}}
\approx \frac{1}{N}\,(2\varepsilon)^{1/N - 1},\qquad \varepsilon = |p_{\mathrm{shot}} - 0.5|.\ }
$$

For small ε and \(N \geq 2\), \((2\varepsilon)^{1/N - 1}\) is large and grows as ε → 0. Example: \(N = 100\), ε = 0.01 → \((0.02)^{-0.99} \approx 50\) → derivative ≈ 0.5; ε = 0.001 → derivative ≈ 5.

---

## 3. How shot-space width maps to per-round width

Suppose the confidence interval in **shot** space has half-width \(\delta\) (so the interval is \(\approx [\hat{p}_{\mathrm{shot}} - \delta, \hat{p}_{\mathrm{shot}} + \delta]\)). After conversion, the half-width in **per-round** space is approximately
$$
\Delta_{\mathrm{round}} \approx \left|\frac{dp_{\mathrm{round}}}{dp_{\mathrm{shot}}}\right|\,\delta.
$$
So to get a per-round half-width of at most \(\Delta\), we need a shot-space half-width of at most
$$
\delta \;\lesssim\; \frac{\Delta}{dp_{\mathrm{round}}/dp_{\mathrm{shot}}}
\;=\; \frac{\Delta\,N}{(2\varepsilon)^{1/N - 1}}
\;=\; \Delta\,N\,(2\varepsilon)^{1 - 1/N}.
$$
As ε → 0, the required \(\delta \to 0\), so we need ever tighter precision in shot space.

---

## 4. Required number of shots (or errors)

Uncertainty in shot space is set by the binomial: with true rate \(p\) and \(n\) shots, the standard error of \(\hat{p}\) is \(\sqrt{p(1-p)/n}\). At \(p = 0.5\) this is \(0.5/\sqrt{n}\). A confidence interval with half-width \(\delta\) typically requires
$$
\delta \;\sim\; z\,\frac{0.5}{\sqrt{n}}
\quad\Rightarrow\quad
n \;\sim\; \frac{0.25\,z^2}{\delta^2}.
$$
(\(z \approx 1.96\) for 95%.) Sinter uses a likelihood-based interval rather than this normal approximation, but the scaling \(n \propto 1/\delta^2\) is the same.

Substitute \(\delta = \Delta\,N\,(2\varepsilon)^{1 - 1/N}\) to get the shots required for a given per-round half-width \(\Delta\) when we are at distance ε from 0.5:
$$
n \;\sim\; \frac{0.25\,z^2}{\bigl(\Delta\,N\,(2\varepsilon)^{1 - 1/N}\bigr)^2}
\;=\; \frac{0.25\,z^2}{(\Delta\,N)^2}\,(2\varepsilon)^{-2(1 - 1/N)}.
$$

For \(N \gg 1\), \(2(1 - 1/N) \approx 2\), so
$$
\boxed{\ n \;\sim\; \frac{C}{(\Delta\,N)^2\,\varepsilon^2}\ ,\qquad C = 0.25\,z^2\,2^{2(1 - 1/N)} \approx z^2.\ }
$$

So **required number of shots** scales as
$$
n \;\propto\; \frac{1}{\Delta^2\,N^2\,\varepsilon^2}.
$$
When p_shot ≈ 0.5 (ε small), \(n\) grows like \(1/\varepsilon^2\). To halve the distance ε, you need about 4× more shots.

**Errors:** If we stop by `max_errors`, then \(n_{\mathrm{errors}} \approx p_{\mathrm{shot}}\,n\). Near \(p_{\mathrm{shot}} = 0.5\), \(n_{\mathrm{errors}} \approx n/2\), so **required max_errors** scales the same way as \(n\) up to that factor:
$$
\boxed{\ \text{max\_errors (or shots)} \;\gtrsim\; \frac{K}{(\Delta\,N)^2\,\varepsilon^2}\ ;
\qquad \varepsilon = |p_{\mathrm{shot}} - 0.5|,\quad \Delta = \text{target per-round half-width}.\ }
$$
\(K\) depends on the confidence level and on whether you use a normal approximation or sinter’s likelihood factor; \(K \approx 1\) gives the right scaling for rough planning.

---

## 5. Practical estimates

Use **ε = |p_shot − 0.5|** and **Δ = desired half-width of the per-round interval** (e.g. 0.005 for ±0.5%). Then
$$
n \;\gtrsim\; \frac{1}{(\Delta\,N)^2\,\varepsilon^2}.
$$
Examples (with \(K=1\) and \(N=100\)):

| ε (distance from 0.5) | p_shot   | Δ = 0.01 (1%) | Δ = 0.005 (0.5%) | Δ = 0.002 (0.2%) |
|------------------------|----------|----------------|-------------------|-------------------|
| 0.10                   | 0.40/0.60| ~10²           | ~4×10²            | ~2.5×10³          |
| 0.05                   | 0.45/0.55| ~4×10²         | ~1.6×10³          | ~10⁴              |
| 0.02                   | 0.48/0.52| ~2.5×10³       | ~10⁴              | ~6×10⁴            |
| 0.01                   | 0.49/0.51| ~10⁴           | ~4×10⁴            | ~2.5×10⁵          |
| 0.005                  | 0.495/0.505 | ~4×10⁴      | ~1.6×10⁵          | ~10⁶              |
| 0.001                  | 0.499/0.501 | ~10⁶        | ~4×10⁶            | ~2.5×10⁷          |
| 0.000008               | 0.500008 / 0.499992 | ~1.6×10¹⁰ | ~6×10¹⁰       | ~2.5×10¹¹         |

Formula used: \(n \approx 1/\bigl((\Delta\,N)^2\,\varepsilon^2\bigr)\) with \(N=100\). For other \(N\), scale by \((100/N)^2\).

### If shot error rate is 0.500008

Then **ε = 0.000008**. You are effectively at the singularity: the derivative is huge and the required sample size is astronomical.

- **Derivative:** \(\frac{dp_{\mathrm{round}}}{dp_{\mathrm{shot}}} \approx \frac{1}{100}(0.000016)^{-0.99} \approx 630\). So a shot-space interval of width 0.001 becomes a per-round interval of width ~0.63.
- **Required shots for Δ = 1%:** \(n \gtrsim 1/\bigl((0.01\times 100)^2 \times (0.000008)^2\bigr) \approx 1.6\times 10^{10}\) (**~16 billion shots**).
- **Required max_errors:** ~**8×10⁹** (billions). Unrealistic in practice.

So for **p_shot = 0.500008** you should **not** expect tight per-round uncertainty from more data. Treat it as “at the singularity”: either **avoid** that (d, p) combination, **plot in shot space** for that point, or **accept a very wide band** in per-round space. Increasing `max_errors` / `max_shots` helps only on paper here; the scaling makes it impractical.

**Interpretation:**  
- ε = 0.05 (e.g. p_shot = 0.55): to get ±1% per-round width you need on the order of hundreds of shots (and roughly half that in errors when p_shot ≈ 0.5).  
- ε = 0.01 (p_shot = 0.51): need on the order of 10⁴ shots (thousands of errors).  
- ε = 0.001 (p_shot = 0.501): need on the order of 10⁶ shots (hundreds of thousands of errors) for ±1% per-round.

**Using `max_errors`:** When you stop by `max_errors`, total shots ≈ (max_errors) / p_shot. Near p_shot = 0.5, max_errors ≈ n/2. So the table above also gives the order of **required max_errors** for that ε and Δ: e.g. ε=0.01, Δ=1% ⇒ **max_errors ~ 5×10³**; ε=0.001, Δ=1% ⇒ **max_errors ~ 5×10⁵** (and 10⁶ is a safe target for “very close to 0.5”).

### Why large max_errors often lands you near p_shot = 0.5

There is a fundamental tension: **the (d, p, rounds) configurations where you actually reach a large `max_errors` are exactly those where shot error rate is close to 0.5.**

- For **many rounds** (or high physical p), the logical information of the surface code is likely destroyed over the circuit: errors accumulate, and the decoder fails about half the time. So shot error rate → 0.5.
- Those are also the regimes where you **collect errors fastest**, so you hit `max_errors` quickly and stop.
- So when you set a **large** `max_errors`, the tasks that reach it are typically the high-round or high-p ones—i.e. the ones where p_shot is already near 0.5 (ε small).
- That is precisely the **singular regime**: the points where you have the most data are the ones where the shot→per-round map blows up and per-round uncertainty is worst.

So “use a large max_errors to improve precision” does not fix the problem near 0.5: the regimes where you get lots of data are the regimes where the singularity makes per-round precision bad. The right lever is to **avoid** those regimes (fewer rounds, lower p, or smaller d so p_shot stays away from 0.5), or to **plot in shot space** for those points instead of insisting on tight per-round bands there.

---

## 6. Summary

1. **Singularity:**  
   \(dp_{\mathrm{round}}/dp_{\mathrm{shot}} = (1/N)(2\varepsilon)^{1/N - 1}\) with \(\varepsilon = |p_{\mathrm{shot}} - 0.5|\), and it tends to \(+\infty\) as ε → 0.

2. **Scaling of required sample size:**  
   \(n \;\gtrsim\; K\big/\bigl((\Delta\,N)^2\,\varepsilon^2\bigr)\) for per-round half-width Δ and distance ε from 0.5.

3. **Practical rule:**  
   Near p_shot = 0.5, require **much** larger `max_errors`/`max_shots` for a given per-round precision; avoid the regime (ε small) when possible, or accept wider bands / plot in shot space for those points.

See [Plotting_and_Uncertainty.md](Plotting_and_Uncertainty.md#high-uncertainty-when-shot-error-rate--05) for practical mitigation options.
