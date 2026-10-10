# Results 3: what the wiring map tells you, what the simulation adds, and what happened when the internet re-ran it

**Status:** our own analysis, not peer-reviewed. Pre-registered in `PLAN3.md` (commit `abb98a0`) before these runs. Not cleared for publication: the independent audit, a prior-work re-check and contact with the original authors are still to come.

Numbers: `results/plan3/3A.json` and `3A_per_type.csv` (`code/run_3a.py`); `results/plan3/3B.json` and `census/resolved.csv` (`code/score_3b.py`).

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

---

# 3B. A census of independent re-runs

**What this is:** a retrospective census of public GitHub projects, read from their READMEs as saved on 10 Oct 2026. We ran nobody's code. Every number below is what a project says about its own run. The search covers an unknown share of GitHub (a search agent's guess: half or less), so every count is a lower bound.

## 3B in one paragraph

We found 97 projects whose README states a firing rate for the feeding neuron, and 72 of them report their own measurement of it under sugar. Where people ran the paper's exact case, most landed on the paper's number. Where they scrambled the wiring, the response vanished. And for the male fly, where the published settings don't work as they are, most people independently arrived at a similar correction.

## Pre-registered verdicts

| | Statement | Result | Verdict |
|---|---|---|---|
| **R1** | Re-runs of the paper's headline case agree with the paper | 8 projects state FlyWire v630 and 100 Hz; 6 report MN9 within 5 Hz of the paper's 67.0 Hz (75%; the bar was 80%). Values: 67.0, 67.07, 67.3, 68.4, 68.6, 70, 80.6, 88. | **Inconclusive** (just under the bar) |
| **R2** | The scrambled-wiring control holds up | 7 projects report an outcome for MN9; 6 report it silent, the seventh reports graded partial rewiring ("30% kills it") | **Supported** |
| **R3** | There is no agreed correction for the male map | 14 projects state a correction factor, from 0.124 to 0.8 (largest is 6.5× the smallest; the bar was 2×) | **Supported** |

**R1, wider reading (declared after extraction, not the pre-registered one):** adding three projects that compare their own number with the paper's 67.0 Hz without stating v630 and 100 Hz in the same place gives 8 of 11 within 5 Hz (73%). Same verdict.
- The three outside the band all report higher values (80.6, 81.0, 88); two of them are single-trial runs by their own description.
- Our own run of this case gives 67.5 Hz (`RESULTS.md`, H1); the authors' shipped result is 67.0 Hz.

**R3, what the spread looks like (descriptive):** although the range is wide, **10 of the 14 corrections fall between 0.5 and 0.65**, and the median is 0.57. That is close to the 0.581 scaling reported with the male map itself (Berg et al. 2026) and to our own type-matched 0.561. The outliers are 0.124, 0.35, 0.42 and 0.8. Two of the 14 (0.5 and 0.8) come from models with an added mechanism, and one 0.65 is adopted from another project, so the values are not all independent. Separately, four projects state they used the published weight unchanged on the male map, and two state that no single factor works.

## The census in numbers

| | Count |
|---|---|
| Projects in the frozen frame (README has "MN9" and a Hz value) | 97 |
| Included (own measured MN9 rate under sugar) | 72 |
| Excluded | 25 |
| Included, by map of the headline number | FlyWire v783: 33; male CNS: 18; FlyWire v630: 13; not stated or unclear: 8 |

**Two independent extractors** agreed on inclusion for 90 of 97 projects (93%). Among the 72 both included, the MN9 value matched as written in 62; the other 10 differ only in form (one recorded both MN9 cells or a different symbol) and match on the first listed value. We resolved the 7 inclusion disagreements from the quoted lines, all towards exclusion: two report only sugar-plus-bitter rates, two numbers are expected values or sample output, two do not name MN9 on the line with the number, and one uses a taste set chosen by connectivity. Each resolution is logged in `3B.json`.

**Not run:** the plan called for our own re-check of any complete setting (map, stimulus set, rate) reported by at least 3 projects for which we had no reference. Only one setting met that bar, the paper's own (v630, the 21 sugar neurons, 100 Hz), and we already have that reference. So no new simulation was needed.

## Limits

- **Self-reported.** A README number may not match what the committed code produces. We did not run any of it.
- **Not independent teams.** Many projects appeared within weeks of each other, some share code or follow the same posts, and many look AI-assisted. Agreement between them is weaker evidence than agreement between isolated labs.
- **README only.** Projects that keep results in other files are missed or under-read. Four we know from our notes (Fugsukjit, flymsg, Fly.exe, flybench's leaderboard) are outside the frame.
- **Outside the headline case, settings differ too much to compare.** On FlyWire v783 at 100 Hz, nine projects report 15.7 to 190 Hz, with different or unstated taste-neuron sets.
- **Coverage unknown.** GitHub search caps results; other hosts were not searched.
- **R1 sits on 8 projects.** One more inside the band would have met the bar.
- **Fairness:** no project is ranked or called a failure here. Before anything is published, named projects are contacted.
