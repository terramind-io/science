# Results 3: what the wiring map tells you, what the simulation adds, and what happened when the internet re-ran it

**Status:** our own analysis, not peer-reviewed. Pre-registered in `PLAN3.md` (commit `abb98a0`) before these runs; the predictors were fixed in the plan's text, and the code that implements them was committed with the results. An independent audit recomputed everything from the raw files with its own code on 10 Oct: every number reproduced, and its corrections to our wording and its caveats are folded in below. Not cleared for publication: a prior-work re-check and contact with the original authors are still to come.

Numbers: `results/plan3/3A.json` and `3A_per_type.csv` (`code/run_3a.py`); `results/plan3/3B.json` and `census/resolved.csv` (`code/score_3b.py`).

## 3A in one paragraph

The wiring map on its own carries real information about which cell types make a fly extend its mouth: a simple three-step path score ranks them above chance on both confirmation sets, comfortably on the female map and narrowly on the male one. The spiking simulation does measurably better than the map-only score on the female map, and better on the harder silencing cases (13 of 18 correct against 8 of 18). So both statements hold: much of the answer is in the wiring, and simulating it adds something real.

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
- **Step count (P1), as the plan required:** its interval includes 0.5 on both confirmation sets, so M1 is not supported for step count. The simulation is ahead of it by 0.270 (0.121–0.411) on v783 and 0.280 (0.135–0.428) on the male map.
- **Where the simulation's edge comes from (from the audit, exploratory):** on v783 the four real positives that the path score gives zero are also zero in the simulation. The difference is in the negatives: 1 negative type fires in the simulation, against 23 with a non-zero path score. The simulation is the more selective of the two.
- Many path scores are exactly zero (69 of 101 types on v783, 56 of 99 on the male map); ties count as half in the ranking score.
- Sensitivity only (not used for verdicts): 2-step, 4-step and excitatory-only path scores give 0.706 / 0.780 / 0.754 on v783 and 0.731 / 0.730 / 0.754 on the male map.

## The harder case: silencing (18 cases)

Real flies were tested with one cell type switched off, under sugar (9 types) and water (9 types). "Required" means the flies extended less.

| | Correct of 18 |
|---|---|
| Simulation (the paper's published silencing ratios, their 20% rule) | 13 |
| Path score, 3 steps (pre-registered) | 8 |
| Path score, 4 steps (sensitivity only) | 10 |

Zorro is excluded from both conditions because its neurons are not in the authors' cell-type file, which leaves 18 of the planned 20 cases. (The audit found Zorro's neurons listed elsewhere in the supplement; with them the count is 15 of 20 against 9 of 20.)

How strong this is: the two predictors disagree on 5 cases and the simulation is right on all 5 (an exact sign test gives p ≈ 0.06, from the audit). The path score calls only 4 cases "required", and its 8 of 18 is what always answering "not required" would score. The verdict holds under the alternative label readings the audit tried (12 vs 7, 14 vs 9, and 12 of 18 for the simulation if one disputed water case is scored against it).

## Step count: our version does not match the paper's column

The plan said to check our step counts against the paper's "Shortest Path" column and to report both if fewer than 90% matched. **Only 56 of 106 types match (53%).** In 45 mismatches ours is shorter, and in 5 the paper lists no path where we find one. The audit found the likely reason, and we re-ran it ourselves: counting only connections of 5 or more synapses reproduces the paper's column for 104 of 106 types (99 of the 101 with a number, plus all 5 with no path), and that step count ranks the types at 0.761 (`3A.json`, `P1_exploratory_5plus_synapses`). We did not find the method stated in the paper. Both versions:
- **Ours** (every listed connection is a step): nearly uninformative, 0.51–0.60, because almost every type is within 2 steps of MN9.
- **The paper's column** (v630 only): 0.771 on the 106 types.

So "count the steps" is informative only when weak connections are left out. We do not use step count in any claim.

## Background fact, verified from the literature (not part of the pre-registered test)

Of the 14 cell types that are positive in the screen, **10 had already been published as triggering proboscis extension** before the simulation paper's preprint (2 May 2023): eight in Shiu, Sterne et al. 2022 (doi:10.7554/eLife.79887), Fdg in Flood et al. 2013 (doi:10.1038/nature12208) and TH-VUM in Marella et al. 2012 (doi:10.1016/j.neuron.2011.12.032). The paper's own Supplementary Table 3 marks these ten with "See also" notes. For the other four (diatom, tentacular, sink_sync, marge) no earlier report was found. Caveats: the earlier papers scored proboscis extension in general, and the screen re-scored a specific movement with new flies; the first preprint version could not be opened to confirm the table was in it. Source: a search agent's fetches of the eLife API and source data on 10 Oct 2026; we have not re-fetched them ourselves.

## Limits

- **Same real-fly labels throughout.** The two confirmation sets test other maps and a broader choice of neurons against the same real-fly screen. They are not new fly experiments.
- **Only the male map is a new brain.** FlyWire v783 is a later version of the same female brain as the v630 development data; 52 of its 101 types use identical neuron lists and the path scores correlate at 0.92 between the two (audit). The male result is the independent one, and there M1 holds narrowly (lower bound 0.511; 0.511–0.516 across bootstrap seeds).
- **13 or 14 positive cases.** Intervals are wide. The v783 difference excludes zero under a paired bootstrap; the male difference does not.
- **The path score is a crude rate calculation,** not "no model at all". We chose its form (signed, 3 steps) on the v630 data, which is why v630 is reported as exploratory.
- **Silencing set is small** (18 cases, 11 cell types, sugar and water overlapping), and the simulation ratios are the paper's published values, not our re-run.
- **One readout on the male map** (MN9_L), as before.

---

# 3B. A census of independent re-runs

**What this is:** a retrospective census of public GitHub projects, read from their READMEs as saved on 10 Oct 2026. We ran nobody's code. Every number below is what a project says about its own run. The search covers an unknown share of GitHub (a search agent's guess: half or less), so every count is a lower bound.

## 3B in one paragraph

We found 97 projects whose README states a firing rate for the feeding neuron, and 72 of them report their own measurement of it under sugar. Of the 8 that state the paper's exact case, 6 report a number within 5 Hz of the paper's. Of the 7 that report what happens to that neuron when the wiring is scrambled, 6 report it silent. For the male fly there is no agreed correction: 14 projects state one, from 0.124 to 0.8, though 10 of them sit between 0.5 and 0.65 and about five of those look like independent calibrations.

## Pre-registered verdicts

| | Statement | Result | Verdict |
|---|---|---|---|
| **R1** | Re-runs of the paper's headline case agree with the paper | 8 projects state FlyWire v630 and 100 Hz; 6 report MN9 within 5 Hz of the paper's 67.0 Hz (75%; the bar was 80%). Values: 67.0, 67.07, 67.3, 68.4, 68.6, 70, 80.6, 88. | **Inconclusive** (just under the bar; depends on how two projects are coded, see below) |
| **R2** | The scrambled-wiring control holds up | 7 projects report an outcome for MN9; 6 report it silent, the seventh reports graded partial rewiring ("30% kills it") | **Supported** |
| **R3** | There is no agreed correction for the male map | 14 projects state a correction factor, from 0.124 to 0.8 (largest is 6.5× the smallest; the bar was 2×) | **Supported** |

**R1, the readings (from the audit).** The plan's rule had a second clause, "or state they reproduce the paper's shipped sugar result", which we did not define tightly enough in advance. The table above uses the strict first clause only. Other readings:
- adding projects that compare their own number with the paper's 67.0 Hz: 8 of 11 (73%), inconclusive;
- adding projects that claim a reproduction at 100 Hz on a female map: 10 of 15 (67%), inconclusive;
- every project that claims a reproduction at any setting: 16 of 39 (41%), which compares unlike settings and is not a fair test.

**R1 also depends on one coding choice.** Two projects (qp-hiro/flybrain, counted, 80.6 Hz; AkashaCorporation/FlyBrain, not counted, 81.0 Hz) both imply v630 without stating it in so many words. Counting both gives 6 of 9 (67%, inconclusive); counting neither gives 6 of 7 (86%, which would have met the bar). We leave the verdict at inconclusive.
- The three outside the band all report higher values (80.6, 81.0, 88); two of them (81.0 and 88) are single-trial runs by their own description.
- Our own run of this case gives 67.5 Hz (`RESULTS.md`, H1); the authors' shipped result is 67.0 Hz.

**R3, what the spread looks like (descriptive, with the audit's corrections):**
- 10 of the 14 corrections fall between 0.5 and 0.65 and the median is 0.57, close to the 0.581 scaling reported with the male map itself (Berg et al.) and to our own type-matched 0.561. Five of those ten sit exactly on the band's edges.
- **They are not ten independent results.** All four 0.65 values trace to one project (blendi-remade/fly-brain-minecraft); the two 0.556 values come from synapse-density arithmetic, not from tuning a response; one value adds a mechanism. About five look like independent calibrations: 0.65, 0.545, 0.582, 0.596 and arguably 0.5.
- The outliers are 0.124, 0.35, 0.42 and 0.8, and they were tuned to different targets (for example whole-brain rates, or the point where activity stops sustaining itself).
- **The verdict rests on the extremes.** Without 0.124 and 0.8 the largest is 1.86× the smallest, which would be inconclusive.
- The plan did not restrict R3 to included projects. Two excluded projects also state a factor (0.455 and 0.5); with them there are 16, 11 in the band, median 0.556, same verdict.
- Separately: one project says it used the published weight unchanged on the male map and three more simply state 0.275 mV there (coded by one extractor only); two say no single factor works.

## The census in numbers

| | Count |
|---|---|
| Projects in the frozen frame (README has "MN9" and a Hz value) | 97 |
| Included (own measured MN9 rate under sugar) | 72 |
| Excluded | 25 |
| Included, by map of the headline number | FlyWire v783: 33; male CNS: 18; FlyWire v630: 13; not stated or unclear: 8 |

**Two independent extractors** agreed on inclusion for 90 of 97 projects (93%). Among the 72 both included, the MN9 value matched as written in 62; the other 10 differ only in form (one recorded both MN9 cells or a different symbol) and match on the first listed value. We resolved the 7 inclusion disagreements from the quoted lines, all towards exclusion: two report only sugar-plus-bitter rates, two numbers are expected values or sample output, two do not name MN9 on the line with the number, and one uses a taste set chosen by connectivity. Each resolution is logged in `3B.json`.

**Other coding notes from the audit:** one extractor recorded a further scrambled-wiring report with no MN9 rate ("the fly does not feed"); we left it out of R2, and counting it as not silent would give 6 of 8 (75%, inconclusive). One included project (lingmulongtai/tsuyulabo) is doubtful: its own engine on a small extract, with no claim to use the paper's parameters. A few included projects add mechanisms or run in a closed loop. One excluded project (Flymagotchi, 68.0 Hz) is very probably the headline case but its table does not name MN9.

**Descriptives promised in the plan** (`results/plan3/3B_descriptives.json`): of the 72 included, 64 have a first commit in Sep 2026, 6 in Oct, and 1 each in Jun and Jul; licences are MIT 28, none detected 28, unclassified 12, GPL-3.0 3, Apache-2.0 1. Dates and licences come from the search agent's GitHub API pull, not re-fetched by us.

**R1 under a consistent coding (added after the audit):** counting both projects that name the v630 data file gives 6 of 9 (67%). Three of those nine values (70, 81.0 and 88) are single short runs by their authors' own description.

**Not run:** the plan called for our own re-check of any complete setting (map, stimulus set, rate) reported by at least 3 projects for which we had no reference. Only one setting met that bar, the paper's own (v630, the 21 sugar neurons, 100 Hz), and we already have that reference. So no new simulation was needed.

## Limits

- **Self-reported.** A README number may not match what the committed code produces. We did not run any of it.
- **Not independent teams.** Many projects appeared within weeks of each other, some share code or follow the same posts, and many look AI-assisted. Agreement between them is weaker evidence than agreement between isolated labs.
- **README only.** Projects that keep results in other files are missed or under-read. Three we know from our notes (Fugsukjit, flymsg, Fly.exe) are outside the frame. (flybench is in the frame and included, contrary to what the plan text said.)
- **Outside the headline case, settings differ too much to compare.** On FlyWire v783 at 100 Hz, nine projects report 15.7 to 190 Hz, with different or unstated taste-neuron sets.
- **Coverage unknown.** GitHub search caps results; other hosts were not searched.
- **R1 sits on 8 projects** (9 under the consistent coding), with single short runs among them (88 is a spike count from one seed; 70 is one 500 ms trial; 81.0, in the wider set, is a single trial).
- **R2 mixes maps and settings** (two on the male map, one at 150 Hz, one heavily modified), and is 7 of the 72 projects.
- **Fairness:** no project is ranked or called a failure here. Before anything is published, named projects are contacted.
