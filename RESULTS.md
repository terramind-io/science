# Results: same simulation, different fly

**Status:** our own analysis, not peer-reviewed. Pre-registered in `PLAN.md` (git `f6e8c13`, 9 Oct 2026 09:22 ET) before any stimulated run. All numbers below come from `results/summary.json` (`code/analyze.py`) and `results/exploratory.json` (`code/explore.py`). Every condition ran through `run_compute` (local jobs `job-1791552194643-87dc7039`, `job-1791552348329-0fb15612`, `job-1791555076914-99665cd2`, `job-1791555893905-fefe7dac`).

## Verdicts on the pre-registered hypotheses

| | Hypothesis | Result | Verdict |
|---|---|---|---|
| **H1** | Shiu et al.'s model on Shiu's data (FlyWire v630, their 21 GRNs, 100 Hz) drives contralateral MN9 | MN9 active in **30/30** trials, **67.5 ± 4.8 Hz**. The authors' archived run of the same condition gives 67.0 Hz (30/30), a 0.7% difference. | **Supported** |
| **H2** | Shuffled wiring abolishes it | **0/100** shuffled connectomes drove MN9. Fisher's exact test vs H1: p = 3.8 × 10⁻³⁰. The paper reports 1/100. | **Supported** |
| **H3** | The unchanged model on the **male CNS** drives contralateral MN9 | MN9 active in **30/30** trials, **28.7 ± 5.9 Hz** | **Supported** (see caveat C1) |
| **H4** | Shuffled wiring abolishes it in the male CNS | **1/100** shuffled connectomes drove MN9 (mean 0.01 Hz). Fisher's exact test vs H3: p = 1.2 × 10⁻²⁸. | **Supported** |
| **D1** | The *whole* response pattern transfers (type-level) | Spearman ρ, female vs male real = **0.110** (3,804 types; top-50 overlap 0.031). Female vs male shuffled = 0.150 (1,360 types; overlap 0.205). Difference = −0.04, below the ≥ 0.2 bar. | **Not supported** |

**Secondary conditions (descriptive, no decision rule).** MN9 was active in 30/30 trials in every one:

| Condition | MN9 rate |
|---|---|
| Female, type-defined stimulus (52 GRNs) | 99.1 ± 5.3 Hz |
| Female, sugar-only stimulus | 73.0 ± 3.7 Hz |
| Male, sugar-only stimulus | 16.8 ± 7.5 Hz |
| Male, right-side stimulus → MN9_L | 138.1 ± 26.3 Hz |

![MN9 per trial](results/figures/fig1_mn9_real_vs_shuffled.png)
*Fig 1.* Spikes in the opposite-side MN9 per 1 s trial at 100 Hz input. Female uses Shiu et al.'s 21 GRNs on FlyWire v630; male uses the 32 left-side GRNs of the same four types in the male CNS. Shuffled means signed weights permuted across existing edges, with a new permutation each trial.

## Exploratory analyses (post hoc, NOT pre-registered)

**X1. Activity spread.** The same stimulus spreads far wider in the male network.

| Condition | Neurons firing per trial | Spikes per trial |
|---|---|---|
| Female (type-defined) | 442 | 17,721 |
| Male | 12,378 | 593,811 |
| Male, sugar-only | 14,870 | 789,137 |

That is about 28× more neurons firing and 33× more spikes. The male top responders are memory and navigation cell types (MBONs, APL, DPM, ExR ring neurons, PEN), not the feeding-circuit types that top the female list. This is why D1 fails.

**X3. Likely cause: the two maps count synapses differently.** Under our conversion:

| | Male CNS | FlyWire v783 |
|---|---|---|
| Synapses | 124.0M | 54.5M |
| Edges | 25.6M | 15.1M |
| Synapses per neuron | 751 | 393 |
| Inhibitory neurons | 29.5% | 30.0% |
| Synapse-weighted inhibition | 37.4% | 40.4% |

Shiu's single free parameter (w_syn) was tuned on FlyWire counts, so every male connection hits about 1.9× harder.

**X4. Test of that cause.** We scaled w_syn by 393/751 = 0.523 (30 trials):

- **The runaway stops:** 112 neurons fire per trial, against 12,378 at default weights.
- **The response pattern moves toward the female's:** ρ = 0.287, top-50 overlap = 0.351. The top types are now shared feeding-circuit types (CB0248, AN_GNG_30, CB0118, CB0366, DNge031, CB0499).
- **But MN9 goes silent:** 0/30 trials.

At default weights MN9 fires but the brain runs away. At density-matched weights the circuit looks right but MN9 doesn't fire. **We found no single setting that gives both.** We only tested two settings. A planned 0.6–0.9 sweep (X5) was not run: its approval request timed out.

**X2. The "reversed laterality" is an MN9_L bias, not a reversal.** In the male, MN9_L fires strongly whichever side is stimulated (111.8 Hz from left input, 138.1 Hz from right input), and MN9_R stays weak (28.7 and 28.8 Hz). The female shows the paper's pattern: opposite side 99.1 Hz, same side 75.2 Hz. Why the two male MN9s differ was not investigated. Candidates are a real left-right difference in this animal, or reconstruction differences between the two cells.

![Activity spread](results/figures/fig2_activity_spread.png)
![MN9 sides](results/figures/fig3_mn9_sides.png)

**Shuffle sanity check (`code/check_shuffle.py`):** on FlyWire v630, one permutation changed 84.8% of 14,687,178 edge weights. The sorted weight list and its sum were identical before and after, and the inhibitory fraction (40.08%) was unchanged. The unchanged 15% are edges where the permutation landed on an equal value; most weights are 1–3 synapses.

## Caveats

- **C1. The H3 pass may not be "for the right reason".** In the male network MN9 fires inside a brain-wide storm (X1). Under density-matched weights (X4) the circuit looks right but MN9 is silent. So "the prediction transfers" holds only in the narrow pre-registered sense: MN9 fires with real wiring and not with shuffled wiring. It does **not** mean the male model reproduces the female's mechanism.
- **C2. Different fly, different sex and different pipeline are confounded.** The male CNS used different imaging (FIB-SEM vs serial-section TEM), synapse detection and neurotransmitter prediction. Our design cannot separate biology from measurement.
- **C3. Our sign rule for the male differs slightly from the paper's** (neuron-level top neurotransmitter vs > 50% of sites; see PLAN deviations). 14,365 male neurons with "unclear" predicted transmitter and 502 with none were treated as excitatory, following the paper's rule that everything that isn't GABA or glutamate is excitatory. This may contribute to X1.
- **C4. Software and settings.** Brian2 2.7.1 instead of 2.5.1; one stimulus rate (100 Hz); 1 s trials.
- **C5. Stimulus definitions changed over time.** In today's FlyWire annotations, Shiu's 21 "sugar" GRNs include 5 typed LB3d (high-salt/heavy-metal) and 4 LB4b (putative attractive). Our type-defined stimuli follow the paper's composition; our sugar-only stimuli use LB3b and LB3c only.

## One-paragraph summary (for the video and description)

We reran Shiu et al.'s whole-brain fly model with their own code and data and got their result to within 1% (67.5 vs 67.0 Hz). Shuffling the wiring killed it, 0 of 100. Then we ran the same model, unchanged, on the 2026 male fly connectome. The feeding neuron still fired in 30 of 30 trials, and shuffled wiring killed it again: 1 of 100. But the rest of the male brain didn't behave like the female's. Activity snowballed to about 28× more neurons, lighting up memory and navigation centres. The male map counts about twice as many synapses per neuron, so the model's one tuning knob, set for the first fly, is too strong for the second. Turning it down fixed the snowball, and the taste circuit started to look like the female's, but then the feeding neuron went quiet. Same model, different map, and no single setting we tried gets both right. This is our own unreviewed analysis.

## Reproduce

```
cd video-01-fly-brain/experiment
uv venv --python 3.11 .venv && uv pip install --python .venv/bin/python brian2==2.7.1 "numpy<2.1" pandas pyarrow joblib matplotlib scipy "cython<3.1"
git clone https://github.com/philshiu/Drosophila_brain_model vendor/Drosophila_brain_model   # commit 91bdd1e
# male CNS v1.0 tables -> data/malecns (URLs in PLAN.md; SHA-256 in data/malecns/SHA256SUMS)
# FlyWire annotations -> data/flywire/neuron_annotations.tsv (flyconnectome/flywire_annotations, Supplemental_file1)
.venv/bin/python code/prepare_inputs.py
for c in E1_fw630_shiu_real E2_fw630_shiu_shuffled E3_fw783_typeset_real E3_mcns_typesetL_real E4_mcns_typesetL_shuffled S1_fw783_sugaronly_real S1_mcns_sugaronlyL_real S2_mcns_typesetR_real X4_mcns_typesetL_wscaled; do .venv/bin/python code/run_sim.py $c 4; done
.venv/bin/python code/analyze.py && .venv/bin/python code/explore.py && .venv/bin/python code/figures.py
```

## Open items

- [x] X4 analysis folded into `code/explore.py`, and the full re-run reproduces every number above.
- [ ] Optional: the X5 w_syn sweep (0.6–0.9), which looks for a setting where MN9 fires without runaway.
- [ ] Before the code goes public: add our own README and LICENSE (MIT, matching the vendored model), and push the repo, without the data or vendor folders, to GitHub. Link it in the description.
