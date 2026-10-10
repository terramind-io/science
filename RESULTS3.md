# Results 3: what the wiring map tells you, and what the simulation adds

**Status:** our own analysis, not peer-reviewed. Pre-registered in `PLAN3.md` (commit `abb98a0`) before these runs. Not cleared for publication: the independent audit, a prior-work re-check and contact with the original authors are still to come.

Numbers: `results/plan3/3A.json` and `3A_per_type.csv` (`code/run_3a.py`).

## 3A in one paragraph

The wiring map on its own carries real information about which cell types make a fly extend its mouth: a simple three-step path score ranks them well above chance on two maps we had not tested it on. The spiking simulation does measurably better than the map-only score on the female map, and clearly better on the harder silencing cases (13 of 18 correct against 8 of 18). So both statements hold: much of the answer is in the wiring, and simulating it adds something real.

## Pre-registered verdicts

| | Statement | Result | Verdict |
|---|---|---|---|
| **M1** | The map alone carries real signal | Path score AUROC 0.780 (95% interval 0.608–0.932) on FlyWire v783 and 0.707 (0.511–0.889) on the male map; both intervals are above 0.5 | **Supported** |
| **M2** | On this screen the map-only score is not distinguishable from the simulation | On v783 the simulation is ahead by 0.063 (interval 0.019–0.119, excludes 0). On the male map the difference is 0.086 (−0.060 to 0.236, includes 0). | **Not supported**: the simulation is measurably better on v783 |
| **M3** | The simulation does better on the harder silencing cases | Simulation correct on 13 of 18, path score on 8 of 18 | **Supported** |

AUROC is a ranking score: 0.5 is guessing, 1 is perfect.

## The screen: ranking cell types against real flies

| Set | Types (positive) | Step count (ours) | Path score, 3 steps | Simulation | Simulation − path score |
|---|---|---|---|---|---|
| FlyWire v783, type-mapped lists (confirmation) | 101 (13) | 0.573 (0.479–0.685) | 0.780 (0.608–0.932) | 0.843 (0.702–0.962) | 0.063 (0.019–0.119) |
| Male CNS, ×0.561 simulation (confirmation) | 99 (13) | 0.513 (0.416–0.628) | 0.707 (0.511–0.889) | 0.793 (0.650–0.927) | 0.086 (−0.060–0.236) |
| FlyWire v630, paper's lists (development, exploratory) | 106 (14) | 0.600 (0.500–0.715) | 0.804 (0.631–0.949) | 0.853 (0.721–0.966) | 0.050 (0.012–0.096) |

- Male map with the other simulation settings: ×0.698 gives 0.823 (ahead of the path score by 0.116, interval 0.022–0.245); ×1.0 gives 0.770 (ahead by 0.063, interval −0.026–0.199).
- The path score and the simulation mostly agree on which types fire: the path score ranks the simulation's own yes/no calls at 0.963 (v783), 0.870 (male ×0.561) and 0.983 (v630).
- Sensitivity only (not used for verdicts): 2-step, 4-step and excitatory-only path scores give 0.706 / 0.780 / 0.754 on v783 and 0.731 / 0.730 / 0.754 on the male map.

## The harder case: silencing (18 cases)

Real flies were tested with one cell type switched off, under sugar (9 types) and water (9 types). "Required" means the flies extended less.

| | Correct of 18 |
|---|---|
| Simulation (the paper's published silencing ratios, their 20% rule) | 13 |
| Path score, 3 steps (pre-registered) | 8 |
| Path score, 4 steps (sensitivity only) | 10 |

Zorro is excluded from both conditions because its neurons are not in the authors' cell-type file, which leaves 18 of the planned 20 cases.

## Step count: our version does not match the paper's column

The plan said to check our step counts against the paper's "Shortest Path" column and to report both if fewer than 90% matched. **Only 56 of 105 types match (53%).** Ours are shorter in every mismatch, so the paper must have counted steps differently (for example over stronger connections only; the paper does not say). Both versions:
- **Ours** (every listed connection is a step): nearly uninformative, 0.51–0.60, because almost every type is within 2 steps of MN9.
- **The paper's column** (v630 only): 0.773 on the 105 types where both exist.

So "count the steps" works only with the paper's unstated way of counting. We do not use step count in any claim until that is understood.

## Background fact, verified from the literature (not part of the pre-registered test)

Of the 14 cell types that are positive in the screen, **10 had already been published as triggering proboscis extension** before the simulation paper's preprint (2 May 2023): eight in Shiu, Sterne et al. 2022 (doi:10.7554/eLife.79887), Fdg in Flood et al. 2013 (doi:10.1038/nature12208) and TH-VUM in Marella et al. 2012 (doi:10.1016/j.neuron.2011.12.032). The paper's own Supplementary Table 3 marks these ten with "See also" notes. For the other four (diatom, tentacular, sink_sync, marge) no earlier report was found. Caveats: the earlier papers scored proboscis extension in general, and the screen re-scored a specific movement with new flies; the first preprint version could not be opened to confirm the table was in it. Source: a search agent's fetches of the eLife API and source data on 10 Oct 2026; we have not re-fetched them ourselves.

## Limits

- **Same real-fly labels throughout.** The two confirmation sets test new maps and a broader choice of neurons against the same real-fly screen. They are not new fly experiments.
- **13 or 14 positive cases.** Intervals are wide. The v783 difference excludes zero under a paired bootstrap; the male difference does not.
- **The path score is a crude rate calculation,** not "no model at all". We chose its form (signed, 3 steps) on the v630 data, which is why v630 is reported as exploratory.
- **Silencing set is small** (18 cases, 10 cell types, sugar and water overlapping), and the simulation ratios are the paper's published values, not our re-run.
- **One readout on the male map** (MN9_L), as before.
