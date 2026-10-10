# Results 2: does the male-fly model predict real flies?

**Status:** our own analysis, not peer-reviewed. Pre-registered in `PLAN2.md` (commit `846197c`, Amendment 1 `2b65326`, Amendment 2 `8e876d6`), all before any of these runs.

**All pre-registered runs are finished (10 Oct 2026, 05:13 ET).** Headline: at default weights the male model fails (T1 not supported). At density-matched weights it passes the main test (T2 supported) but **fails the pre-registered robustness rule**, so T2 is **not robust**. Nothing here is cleared for publication.

**Publication gate (PLAN2 Amendment 2 F): not met.** The robustness rule failed, and a re-check of prior work on 10 Oct found that a male-connectome model had already been scored against this table (Fly.exe, see Prior work). No paper goes ahead on these results.

Numbers come from:
- `results/plan2/score_2a.json` (`code/score_2a.py`)
- `results/plan2/score_rob.json` (`code/score_rob.py`)
- `results/plan2/score_2a_check.json` and `2A_per_type_table.csv` (a separate recompute that agrees exactly)
- the per-job files in `results/plan2/`

## Ground truth

Shiu et al. 2024, Supplementary Table 3: for 106 feeding-region cell types, whether real flies extended the proboscis when that type was switched on with light. A type counts as positive if the observed rate is above 0. A model prediction is positive if the feeding motor neuron MN9 fires above 0 Hz at 50 Hz activation (30 trials).

## Pre-registered verdicts so far

| | Hypothesis | Result | Verdict |
|---|---|---|---|
| **V0** | Our faster runner reproduces the paper's own per-type predictions | 106/106 types classified the same as the paper's table; Pearson r = 0.9986 between our MN9 rates and theirs. Against real flies: 10 hits, 1 false alarm, 4 misses, accuracy 0.953, the paper's numbers. | **Supported** |
| **R1** | Extra synaptic input causes the runaway | Female model with weights ×1.782: 6,617 non-stimulated neurons fire, against 390 at default (17×) | **Supported** |
| **R2** | A working window exists for the male model | ×0.65: MN9_L 10/10 trials, 668 neurons firing. ×0.698: 10/10, 972. (Limit was ≤ 1,170.) Search over 5 settings. | **Supported** |
| **R3** | The nerve cord is the cause of the runaway | Brain-only male network still has 9,312 neurons firing (24× the female) | **Ruled out** |
| **Sp** | Sugar input is specific, compared with random head taste neurons | Female: 99.1 vs 7.6 Hz. Male ×1.0: 111.8 vs 11.0 Hz. Male ×0.698: 35.9 vs 0.5 Hz. Male ×0.561: sugar itself fires in only 2/10 trials. | **Specific** at female, male ×1.0 and male ×0.698. **Not specific** at male ×0.561. |
| **T2** | Male model at density-matched weights (×0.561) is about as accurate as the female | See table below: accuracy 0.919 vs 0.949 (within the 0.05 margin), 8 hits (≥ 7 required) | **Supported**, but **not robust** (see Robustness) |
| **T3** | Male model at flymsg's setting (×0.698) is about as accurate as the female | Accuracy 0.879 vs 0.949 (outside the 0.05 margin, inside the 0.15 margin), 9 hits | **Partial** |
| **T1** | Male model at default weights | 9 hits but 32 false alarms; accuracy 0.636 vs 0.949 (outside the 0.15 margin) | **Not supported** |
| Robustness | T2's verdict is the same at weights ×0.7 and ×1.3, and at 10 Hz and 200 Hz | Supported at ×1.3 and 200 Hz; partial at ×0.7 and 10 Hz (only 4 hits; 7 required) | **T2 not robust** |

## The 2A screen: 99 cell types present in both flies, 13 of them positive in real flies

| Model | Hits | False alarms | Misses | Correct rejections | Accuracy (95% CI) | Precision | Recall |
|---|---|---|---|---|---|---|---|
| Female, same type-mapping as the male (2A_F783T) | 9 | 1 | 4 | 85 | 0.949 (0.899–0.990) | 0.90 | 0.69 |
| Male, ×0.561 (2A_Ms) | 8 | 3 | 5 | 83 | 0.919 (0.859–0.970) | 0.73 | 0.62 |
| Male, ×0.698 (2A_M698) | 9 | 8 | 4 | 78 | 0.879 (0.808–0.939) | 0.53 | 0.69 |
| Male, ×1.0 default (2A_M) | 9 | 32 | 4 | 54 | 0.636 (0.545–0.727) | 0.22 | 0.69 |
| "Always predict no" baseline | 0 | 0 | 13 | 86 | 0.869 | — | 0 |

- The female model with the paper's own neuron lists gives the same 9 / 1 / 4 / 85 on these 99 types.
- The male and female models agree on 97.0% of types at ×0.561, 92.9% at ×0.698 and 68.7% at ×1.0.
- Confidence intervals are bootstrap intervals over cell types (10,000 resamples, seed 0).

**Exploratory (not pre-registered):** a one-sided Fisher's exact test of predicted vs observed gives p = 4.0 × 10⁻⁹ (female), 1.1 × 10⁻⁶ (male ×0.561) and 7.2 × 10⁻⁶ (male ×0.698). All three models' predictions are associated with what real flies did.

**What the per-type table shows (exploratory):**
- **The same cell types carry the result in both flies.** The female model's 9 hits (roundup, bract, Fdg, diatom, G2N_1, clavicle, rattle, sink_sync and FMIn) are exactly the male model's 9 hits at ×0.698. At ×0.561 the male model has the same list minus FMIn, which fires only weakly in the female too (0.5 Hz).
- **Both flies' models miss the same four:** usnea, phantom, tentacular and marge fire 0 Hz in every model. Three of these are the misses the paper itself discusses (types predicted inhibitory or neuromodulatory).
- **The male model's extra errors are false alarms that grow with the weight setting.** At ×0.561: kitty (also the female model's one false alarm), puddle and seagull. At ×0.698 five more appear: mime, justice, gnome, foxglove and peahen. Five of the eight fire below 1 Hz.

## Robustness (PLAN2 Amendment 2 D): 10 trials per type, same 99 types

In each condition the male run (based on ×0.561) is judged against the female run of the same condition, with T2's rules (male accuracy ≥ female − 0.05 **and** ≥ 7 hits).

| Condition | Female: hits / false alarms / accuracy | Male: hits / false alarms / accuracy | Male–female agreement | T2 verdict |
|---|---|---|---|---|
| Weights ×0.7, 50 Hz | 5 / 1 / 0.909 | 4 / 1 / 0.899 | 97.0% | partial |
| Weights ×1.3, 50 Hz | 9 / 5 / 0.909 | 9 / 9 / 0.869 | 89.9% | supported |
| 10 Hz | 5 / 1 / 0.909 | 4 / 1 / 0.899 | 94.9% | partial |
| 200 Hz | 9 / 5 / 0.909 | 9 / 7 / 0.889 | 93.9% | supported |

**Pre-registered conclusion: T2 is not robust,** because its verdict is not the same in all four conditions.

**Exploratory reading (not pre-registered, cannot rescue the verdict):**
- The two "partial" verdicts come from the absolute 7-hit threshold, which the *female* model also misses in those conditions (5 hits). Hit counts fall in both flies' models at weaker drive, but the hit lists are not the same (×0.7: female has Fdg and G2N_1 where the male has diatom; 10 Hz: female has Fdg, clavicle and sink_sync where the male has diatom and rattle).
- In every condition the male model's accuracy differs from the female's by at most 4 of 99 types.
- The benchmark is sensitive in both directions: at stronger drive (×1.3, 200 Hz) the female model's false alarms rise from 1 to 5 and its accuracy falls from 0.949 to 0.909.
- Every male robustness run is within 3 types of the "always no" baseline (0.869): 0.899, 0.869, 0.899 and 0.889. The female runs are all at 0.909.
- The rule does not say which female run is the comparator. We used the same-condition female run. Against the 30-trial female screen (0.949) all four male verdicts would be "partial". Either way T2 is not robust.

**How much rests on very weak firing (from the independent audit, exploratory):** the pre-registered rule counts any spike as a positive. With a stricter rule (mean rate ≥ 1 Hz), T2 stays supported (male 7 hits / 2 false alarms, 0.919 vs female 0.939), T3 becomes supported, T1 stays not supported and robustness still fails. T2 passes with 8 hits against a threshold of 7, and one of those hits (rattle) is 0.87 Hz. Some positives rest on a single trial: for example seagull (male ×0.561 false alarm) is 2 spikes in 2 of 30 trials, and TH_VUM (the female model's tenth hit in V0) is 1 spike in 1 of 30 trials. Because "any spike" depends on the number of trials, the 10-trial robustness runs are slightly less likely to call a positive than the 30-trial screens.

## Caveats

- **Accuracy alone is a weak measure here,** because 87% of types are negative. The male ×0.561 model's accuracy interval (0.859–0.970) includes the "always no" baseline (0.869). The evidence that it carries real signal is the hit count (8 of 13 with 3 false alarms) and the exploratory Fisher test, not the accuracy figure.
- **The two male settings trade off.** ×0.561 scores better on this screen but fails the sugar → MN9 test (2/10 trials). ×0.698 passes the sugar test and specificity but makes more false alarms here. No single setting is best on everything we measured.
- **Male readout is MN9_L only** (MN9_R is flagged "RT Hard to trace"). 7 of 106 types could not be mapped to the male dataset and are excluded from all rows above. One of the seven (TH_VUM) is positive in real flies, which is why 13 positives remain and not 14.
- **Fly, sex and mapping pipeline remain confounded** (see RESULTS.md C2).
- **Type mapping broadens the stimulus:** each type is mapped to all neurons of its FlyWire cell type(s). On these 99 types this made no difference to the female scores.
- **Not reported as planned:** PLAN2 promised Cohen's κ with a bootstrap interval and intervals for every score. We report raw agreement and an interval for accuracy only. The audit computed κ = 0.84 (×0.561), 0.70 (×0.698) and 0.27 (×1.0) against the female model. The runner pre-check passed (V1: 67.7 Hz against E1's 67.5 Hz).
- **The exploratory Fisher test** treats cell types as independent. For male ×1.0 it gives p = 0.031.

## Prior work (re-checked 10 Oct 2026)

**Someone had already scored a male-connectome model against this table, before we did.** The 9 Oct search missed it.

- **Fly.exe** (Ibtisam-Mohammad, GitHub, GPL-2.0), commit `cc25411e00f945e7330cb6f400372cce315c0802`, repo created 12 Sep 2026, last push 15 Sep 2026. File `docs/evidence/STAGE1_SHIU_FEEDING.md` scores a male CNS model against Shiu's Supplementary Table 3: 101 of 106 types mapped, 30 trials, on a 2,714-neuron sub-network of paths to MN9 (not the whole CNS). It reports 8 hits / 0 false alarms / 88 correct rejections / 5 misses for the real wiring and 0 hits for shuffled wiring. It also states that its own pre-registered pass rule was not met. We have not run its code or verified its numbers.
- Our male ×0.561 result (8 hits / 3 false alarms on 99 types, whole CNS) is therefore a **confirmation with a different method**, not a first.
- Fugsukjit (repo HEAD `c4ef087`, 6 Oct; Zenodo v1, one version), flymsg (HEAD `cb3ed70`) and flybench (v0.2.1): unchanged, no male scoring against this table.
- Earlier notes: `PRIOR_WORK.md`.

## Provenance

- Laptop: `2A_F` (V0), 2B, 2C, SPEC; and, overnight on 10 Oct (00:00–05:13 ET), the eight `ROB_*` jobs and `2A_M` (`code/run_rest_local.sh`, switched at 00:10 to three parallel chains with `code/run_rest_parallel.sh`; seeds are keyed on the item index, so worker count does not change results). Coverage: 99 or 101 types, 10 trials each for ROB, 30 for `2A_M`, no duplicates.
- Cloud (12 jobs, ids `job-17916001…`, 9 Oct 22:42 ET, commit `8ba20f4`): `2A_F783T`, `2A_Ms`, `2A_M698`, four shards each. Every cloud machine re-downloaded the public data, passed the SHA-256 checks and rebuilt inputs byte-identical to ours. Each shard's returned file equals the copy printed in its job log (12/12). Coverage: 101 / 99 / 99 types, 30 trials each, no duplicates.
- Cloud cost for these 12 jobs: 409,500 credits.
