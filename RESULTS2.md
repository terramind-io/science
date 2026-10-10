# Results 2: does the male-fly model predict real flies? (interim)

**Status:** our own analysis, not peer-reviewed. Pre-registered in `PLAN2.md` (commit `846197c`, Amendment 1 `2b65326`, Amendment 2 `8e876d6`), all before any of these runs.

**Interim:** the male default-setting screen (T1) and the robustness checks are still running on the laptop (`results/plan2/rest_local.log`). Until they finish, no transfer verdict can be called "robust", and nothing here is cleared for publication.

Numbers come from:
- `results/plan2/score_2a.json` (`code/score_2a.py`)
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
| **T2** | Male model at density-matched weights (×0.561) is about as accurate as the female | See table below: accuracy 0.919 vs 0.949 (within the 0.05 margin), 8 hits (≥ 7 required) | **Supported** (robustness pending) |
| **T3** | Male model at flymsg's setting (×0.698) is about as accurate as the female | Accuracy 0.879 vs 0.949 (outside the 0.05 margin, inside the 0.15 margin), 9 hits | **Partial** |
| **T1** | Male model at default weights | Running on the laptop | pending |
| Robustness | T-verdicts hold at weights ×0.7 and ×1.3, and at 10 Hz and 200 Hz | Running on the laptop | pending |

## The 2A screen: 99 cell types present in both flies, 13 of them positive in real flies

| Model | Hits | False alarms | Misses | Correct rejections | Accuracy (95% CI) | Precision | Recall |
|---|---|---|---|---|---|---|---|
| Female, same type-mapping as the male (2A_F783T) | 9 | 1 | 4 | 85 | 0.949 (0.899–0.990) | 0.90 | 0.69 |
| Male, ×0.561 (2A_Ms) | 8 | 3 | 5 | 83 | 0.919 (0.859–0.970) | 0.73 | 0.62 |
| Male, ×0.698 (2A_M698) | 9 | 8 | 4 | 78 | 0.879 (0.808–0.939) | 0.53 | 0.69 |
| "Always predict no" baseline | 0 | 0 | 13 | 86 | 0.869 | — | 0 |

- The female model with the paper's own neuron lists gives the same 9 / 1 / 4 / 85 on these 99 types.
- The male and female models agree on 97.0% of types at ×0.561 and 92.9% at ×0.698.
- Confidence intervals are bootstrap intervals over cell types (10,000 resamples, seed 0).

**Exploratory (not pre-registered):** a one-sided Fisher's exact test of predicted vs observed gives p = 4.0 × 10⁻⁹ (female), 1.1 × 10⁻⁶ (male ×0.561) and 7.2 × 10⁻⁶ (male ×0.698). All three models' predictions are associated with what real flies did.

**What the per-type table shows (exploratory):**
- **The same cell types carry the result in both flies.** The female model's 9 hits (roundup, bract, Fdg, diatom, G2N_1, clavicle, rattle, sink_sync and FMIn) are exactly the male model's 9 hits at ×0.698. At ×0.561 the male model has the same list minus FMIn, which fires only weakly in the female too (0.5 Hz).
- **Both flies' models miss the same four:** usnea, phantom, tentacular and marge fire 0 Hz in every model. Three of these are the misses the paper itself discusses (types predicted inhibitory or neuromodulatory).
- **The male model's extra errors are false alarms that grow with the weight setting.** At ×0.561: kitty (also the female model's one false alarm), puddle and seagull. At ×0.698 five more appear: mime, justice, gnome, foxglove and peahen. Five of the eight fire below 1 Hz.

## Caveats

- **Accuracy alone is a weak measure here,** because 87% of types are negative. The male ×0.561 model's accuracy interval (0.859–0.970) includes the "always no" baseline (0.869). The evidence that it carries real signal is the hit count (8 of 13 with 3 false alarms) and the exploratory Fisher test, not the accuracy figure.
- **The two male settings trade off.** ×0.561 scores better on this screen but fails the sugar → MN9 test (2/10 trials). ×0.698 passes the sugar test and specificity but makes more false alarms here. No single setting is best on everything we measured.
- **Male readout is MN9_L only** (MN9_R is flagged "RT Hard to trace"). 7 of 106 types could not be mapped to the male dataset and are excluded from all rows above.
- **Fly, sex and mapping pipeline remain confounded** (see RESULTS.md C2).
- **Type mapping broadens the stimulus:** each type is mapped to all neurons of its FlyWire cell type(s). On these 99 types this made no difference to the female scores.
- **Prior work:** see `PRIOR_WORK.md`. Fugsukjit scored a re-implementation against this table on FlyWire only. We found no one who had scored a male-connectome model against it (one search, 9 Oct; must be re-checked before any release).

## Provenance

- Laptop: `2A_F` (V0), 2B, 2C, SPEC.
- Cloud (12 jobs, ids `job-17916001…`, 9 Oct 22:42 ET, commit `8ba20f4`): `2A_F783T`, `2A_Ms`, `2A_M698`, four shards each. Every cloud machine re-downloaded the public data, passed the SHA-256 checks and rebuilt inputs byte-identical to ours. Each shard's returned file equals the copy printed in its job log (12/12). Coverage: 101 / 99 / 99 types, 30 trials each, no duplicates.
- Cloud cost for these 12 jobs: 409,500 credits.
