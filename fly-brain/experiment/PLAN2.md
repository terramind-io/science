# Pre-registration 2: follow-up experiments

**Registered:** 9 Oct 2026, after the PLAN.md results and their audit (RESULTS.md) and before any of the runs below.
**Tracked as:** GROW-109 follow-up · **Status:** our own analysis, not peer-reviewed.

These follow-ups answer the two gaps the first experiment left open:
1. Is the male model as **accurate against real-fly experiments** as the female model? Firing is not the same as being right.
2. Is the male runaway really caused by the extra synaptic input, and is there a setting where the model works in both flies?

## Ground truth

Shiu et al. 2024 Supplementary Table 3 is saved as `../sources/papers/S2_supplementary/S2_Shiu2024_MOESM2_ESM.xlsx`, sheet "Sup Table 3 Predicted MN9 vs. o". For each of 106 cell types in the feeding region (the SEZ), it gives:
- the **observed** fraction of real flies that lifted their proboscis when that cell type was switched on with light (column "MN9 Optogenetic Activation Rate"; a type counts as positive if this is above 0)
- the female model's MN9 rates

Before registering this plan we checked the scoring rule against the table (`code/` run of 9 Oct). **"MN9_Left > 0 Hz at 50 Hz activation"** reproduces the paper's headline exactly: 11 predicted, 10 true positives, 4 false negatives, 91 true negatives, accuracy 0.953. MN9_Left is FlyWire `720575940660219265`.

## Experiment 2A: does the male model predict real flies as well? (headline)

**Stimulus.** For each SEZ cell type, every neuron of that type is activated with Poisson input at **50 Hz**, 30 trials of 1 s. That's 106 types.
- **Female:** the neuron IDs come from `vendor/.../sez_neurons.pickle`, the paper's own lists.
- **Male:** each type's v630 IDs are mapped to FlyWire v783 `cell_type` (annotation table). We then activate all male CNS neurons whose `flywireType` matches any of those types, on both sides. If no male neuron matches, the type is recorded as **unmappable** and excluded from male scoring. We report how many were excluded.

**Readout.**
- Female: MN9_Left as above.
- Male: **MN9_L (`10331`)**. MN9_R is excluded because the dataset flags it "RT Hard to trace" (RESULTS.md A1).
- A type is **predicted positive** if mean MN9 rate > 0 Hz.

**Conditions.**

| ID | Network | w_syn | Purpose |
|---|---|---|---|
| 2A-F | FlyWire v630 | 1.0 (default) | Validate our faster runner (see Method). It must reproduce ST3. |
| 2A-M | Male CNS | 1.0 (default) | Transfer as-is |
| 2A-Ms | Male CNS | **0.561** = 1/1.782, the type-matched density ratio from RESULTS.md A3 | Transfer with synapse density matched |

**Scores** (against observed ST3 outcomes, over mappable types): accuracy, true/false positives and negatives, and Cohen's κ against the female model's predictions. Each gets a bootstrap 95% CI over types (10,000 resamples, seed 0).

**Decision rules (fixed now):**

| | Hypothesis | Supported if | Not supported if |
|---|---|---|---|
| **V0** (runner validity) | 2A-F reproduces the paper's own predictions | The classification at 50 Hz matches ST3 for ≥ 104 of 106 types **and** Pearson r ≥ 0.95 between our and ST3's MN9_Left rates | Otherwise. 2A-M and 2A-Ms are then reported only as exploratory. |
| **T1** (transfer at default weights) | The male model is about as accurate as the female model | Male accuracy ≥ female accuracy − 0.05 on the same mappable types, **and** male true positives ≥ 7 of the observed positives that are mappable | Male accuracy < female − 0.15, **or** male true positives ≤ 3 |
| **T2** (transfer at matched density) | Same as T1, for 2A-Ms | same thresholds | same thresholds |

Anything in between counts as **partial**. Accuracy alone is misleading here because about 87% of types are negative: a model that predicts "never fires" scores about 0.87. So we also report that trivial baseline, and true positives carry weight in the decision.

## Experiment 2B: does synapse density cause the runaway?

Stimulus is the same as E3: type-defined sugar-set GRNs at 100 Hz, 10 trials per condition. Readouts:
- the number of non-stimulated neurons firing per trial
- MN9 rate (female: contralateral `720575940660219265`; male: MN9_L)

| ID | Network | w_syn multiplier |
|---|---|---|
| 2B-F178 | FlyWire v783 | **1.782**, giving the female the male map's density |
| 2B-M{0.561, 0.65, 0.75, 0.85} | Male CNS | the stated multipliers |

The default-weight (1.0) and 0.523 male points already exist (E3b, X4).

**Decision rules:**
- **R1 (density causes runaway):** supported if 2B-F178 has ≥ 10× the non-stimulated neurons firing of female default (E3a: 390). Not supported if < 2×.
- **R2 (a working window exists):** supported if any male multiplier gives **both** MN9_L active in ≥ 9/10 trials **and** non-stimulated firing neurons ≤ 3× the female default (≤ 1,170). Not supported if none does. This is a search over 4 settings, and we report it as such.

## Experiment 2C: is the runaway caused by the extra tissue?

**2C:** a male CNS network restricted to brain neurons only (superclass not starting with `vnc`), default w_syn, the same stimulus as E3b, 10 trials. Readout: non-stimulated neurons firing.
- **R3:** if spread stays ≥ 10× the female default, the extra nerve-cord tissue is ruled out as the main cause. If it drops to < 3×, the nerve cord is implicated.

## Method change (declared)

**Faster runner (`code/run_screen.py`).** Instead of rebuilding the network for every trial, each worker builds it once. Stimulation comes from a `PoissonGroup` with one-to-one synapses adding w_syn × 250 to v (the same weight and target as Shiu's `PoissonInput`). Rates are set per trial, along with zero refractory time for the stimulated neurons, as in the original. The network is restored to a stored initial state before every trial.

This is mathematically the same input process. **V0 is the test that it reproduces the paper.** As a second check, the runner must reproduce E1's MN9 rate (67.5 Hz) within 2 s.e.m. before 2A runs.

## Reporting

Every verdict is reported, including failures. Anything added after seeing results is labelled exploratory. The video and paper say "our own analysis, not peer-reviewed".

## Amendment 1 (9 Oct 2026, before any 2A/2B/2C run)

A prior-work check found flymsg (GitHub `cb3ed70`). Its default setting, w_syn 0.192 = 0.275/1.43, uses the lower interquartile bound of its density ratio and reports sugar → MN9_L without runaway. To test that directly, **2B adds a male multiplier of 0.698** (= 0.192/0.275). Adding this point doesn't change R2's decision rule; R2 is now evaluated over 5 settings, and we report it as such. No other change.

## Amendment 2 (9 Oct 2026, before any 2A/2B/2C/new run): controls and robustness

Agrim asked for the paper to be as robust as possible. All of the following is fixed before any of these runs.

**A. A fair female comparator for 2A (`2A_F783T`).** The male stimulus sets are built by mapping each SEZ type to *all* neurons of its FlyWire cell type(s). The paper's own lists (used in 2A-F) are narrower. To separate "different fly" from "different neuron selection", we add 2A_F783T: FlyWire v783, the **same type-mapping procedure** as the male, 50 Hz, 30 trials, readout MN9 `720575940660219265`. **T1 and T2 are now judged against 2A_F783T.** 2A-F (the paper's own lists) stays as the check that we reproduce the paper (V0).

**B. Male at flymsg's setting (`2A_M698`).** Male CNS, w_syn × 0.698, otherwise identical to 2A-M. It is scored with T1/T2's rules and reported as **T3**.

**C. Specificity control (`SPEC_*`).** The question is whether sugar input is special, or whether any head taste input drives MN9.
- **Stimulus:** 10 fixed random draws (`inputs/controls.json`, seed 20261009) of head gustatory neurons on the stimulus side, excluding the stimulus types (LB3b/c/d, LB4b). Each draw has the same number of neurons as the sugar-set stimulus: 52 in the female (pool of 154), 32 in the male (pool of 106).
- **Run:** 100 Hz, 10 trials per draw.
- **Networks:** female v783 (×1.0), and male at ×1.0, ×0.561 and ×0.698.
- **Readouts:** female MN9 `720575940660219265`; male MN9_L.
- **Sp (fixed now):** at each setting, the sugar-set response is **specific** if the mean sugar MN9 rate is **≥ 3× the mean control rate + 2 Hz** **and** sugar drives MN9 in ≥ 90% of trials. Sugar rates come from E3a, E3b and 2B_M0.561 / 2B_M0.698. Otherwise it is **not specific**.

**D. Robustness of 2A (`ROB_*`).** On 2A_F783T and 2A_Ms (×0.561), 10 trials each:
- 50 Hz with w_syn ×0.7 and ×1.3 of that network's setting (Shiu's ±30% check)
- 10 Hz and 200 Hz at the network's setting

We report accuracy and true positives for each. A transfer conclusion (T1/T2) counts as **robust** only if its verdict is the same across all four.

**E. Order of runs:** 2B → 2C → SPEC → 2A (F, F783T, Ms, M698, M) → ROB. Every job is resumable. The approximate total is about 14 h of local compute.

**F. Publication gate (from AGENTS.md):** nothing is published unless the results meet the "Credibility comes first" bar *and* the prior-work search (PRIOR_WORK.md) finds the main contribution not already done. If it was done, we credit it and the paper doesn't go ahead.
