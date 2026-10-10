# Fly brain granularity sweep

How much detail does a whole-brain fly model need to still produce a known behavior?
Starting point: Shiu et al. 2024, *Nature* 634:210–219 (LIF model of the FlyWire v630 connectome).
Behavior: sugar GRN activation → proboscis motor neuron MN9 firing.

Status: complete, tagged `v1.0`. Write-up: `docs/technical_note.md`. Original brief: `docs/brief.md`. Lab log: `NOTES.md`.

## Layout

```
docs/brief.md                    the experiment as specified before any code was written
docs/technical_note.md           the write-up
docs/upstream.md                 what was downloaded, from where, at which commit
NOTES.md                         lab log: surprises, dead ends, decisions, in date order
external/                        authors' repo and the annotation table; not tracked (see Setup)
src/sim.py                       seeded wrapper around the authors' Brian2 model; builds from in-memory tables
src/neurons.py                   FlyWire IDs copied from the authors' figures.ipynb
src/behaviors.py                 the two behaviors: stimulated set, readout, reference Hz, curve Hz
src/fidelity.py                  primary, symmetric and curve-shape fidelity scores
src/knobs.py                     degrade(model, knob, level, seed, active_idx) -> (model, PerturbationReport)
scripts/run_baseline.py          Phase 0: Fig 1 sugar sweep + Fig 3A bitter control
scripts/run_baseline_grooming.py Phase 3 baseline: Fig 5 JON -> aDN1 checks
scripts/run_sweep.py             every knob x level x seed -> results/[grooming/]{knob}.csv
scripts/run_combo.py             the combined cheaper model (prune + quantize + dt)
scripts/plot_sweep.py            per-knob and combined plots, {knob}.summary.csv, cliffs.csv
scripts/sensitivity_map.py       per-neuron effect sizes from the random-knob draws
scripts/verify_sensitivity.py    single-neuron sign flips of the top-ranked neurons
scripts/compare_behaviors.py     sugar vs grooming figure and cliff table
scripts/reproduce.sh             every run above, in order
results/                         CSVs, per-level JSONL, PNGs, reference.json, cost.json; results/logs/ holds the run logs
tests/                           pytest; `-m slow` for full-network integration tests
```

## Setup

```
uv venv --python 3.10 .venv
uv pip install --python .venv/bin/python -r requirements.txt
git clone https://github.com/philshiu/Drosophila_brain_model external/Drosophila_brain_model
git -C external/Drosophila_brain_model checkout 91bdd1e
mkdir -p external/annotations         # cell-type table for the merge knob (Schlegel et al. 2024, v1.1.0 = v630 IDs)
curl -L -o external/annotations/Supplemental_file1_annotations_v1.1.0.tsv \
  https://raw.githubusercontent.com/flyconnectome/flywire_annotations/v1.1.0/supplemental_files/Supplemental_file1_annotations.tsv
.venv/bin/python -m pytest            # fast tests
.venv/bin/python -m pytest -m slow    # full-network tests (~2 min)
.venv/bin/python scripts/run_baseline.py --n-seeds 30 --n-jobs 8
```

`scripts/reproduce.sh` lists every run in this repository in order (about 9 hours on an Apple M4 laptop).

## Guessed / defaulted parameters (not stated in paper or repo)

| parameter | value used | source of value | why it is a guess |
|---|---|---|---|
| integration timestep `dt` | 0.1 ms | Brian2 `defaultclock` default | paper and repo never set it; authors ran with the default |
| Poisson input weight factor `f_poi` | 250 | repo `model.py` comment ("sufficient to cause spiking") | not in paper Methods |
| codegen target | numpy | our choice (faster here than cython) | affects speed only, not results |
| per-trial seeds | 1000+k | our choice | authors' runs are unseeded |

## Fidelity definition

`fidelity = clip(MN9_rate(model @ 100 Hz sugar) / MN9_rate(baseline @ 100 Hz sugar), 0, 1)`,
MN9 = FlyWire 720575940660219265 (the contralateral MN9 the authors read out), mean over seeds.
100 Hz is the paper's calibration point for its single free parameter W_syn.

## Baseline reproduction (Phase 0)

Run 2026-09-11/12 on an Apple M4 laptop, FlyWire v630, 30 seeds per condition (seeds 1000–1029), 1000 ms trials.

![Fig 1 sugar sweep](results/baseline/fig1_sugar_sweep.png)
![Fig 3A bitter control](results/baseline/fig3_bitter_control.png)

| check | paper | ours | status |
|---|---|---|---|
| neurons active at 10 Hz sugar (any of 30 trials) | 45 | 42 | match |
| neurons active at 200 Hz sugar (any of 30 trials) | 455 | 447 | match |
| MN9 fires in every simulation at 100 Hz sugar | 100% | 30/30 | match |
| contralateral MN9 > ipsilateral MN9 (Fig 1c) | yes | yes, at every freq ≥ 40 Hz | match |
| 100 Hz sugar ≈ 80% of maximal MN9 | "roughly 80%" | 67.0 / 92.5 Hz at 200 Hz = 72% | approximate; "maximal" is not defined numerically in the paper |
| bitter co-activation suppresses MN9 (Fig 3b) | yes | 100 Hz sugar: 69 → 47 → 4 → 0 Hz at bitter 0/40/100/200 Hz | match |
| bitter reduces ~40 Hz MN9 to ≤1 Hz (Fig 3f) | yes | 60 Hz sugar (37 Hz MN9) + 100 Hz bitter → 0 Hz | match |

MN9 readout rate vs sugar GRN rate (mean ± s.d. over 30 seeds, Hz): 10: 0; 20: 0; 30: 0.1; 40: 6.6±3.0; 50: 20.7±6.0;
60: 37.6±6.0; 70: 50.0±5.2; 80: 56.7±5.8; 90: 64.1±5.4; **100: 67.0±4.1**; 120: 76.0±5.1; 150: 83.0±5.4; 200: 92.5±5.3.
Full table: `results/baseline/fig1_sugar_sweep.csv`. Bitter grid: `results/baseline/fig3_bitter_control.csv`.

What did not match exactly: nothing numerically checkable disagreed, but the authors' per-frequency MN9 rates are only
available as figure bars or inside a 4.5 GB archive we have not downloaded, so the Fig 1 curve is checked against the
counts and qualitative claims in the text, not against their CSVs. The authors' runs are unseeded, so a bit-exact match
is not possible in any case.

**Fidelity reference**: `results/baseline/reference.json` records MN9 = 67.0 Hz at 100 Hz sugar (30 seeds). The
baseline scores fidelity 1.0 by construction (tested in `tests/test_fidelity.py`).

## Compute cost (baseline, per 1000 ms trial)

| quantity | value |
|---|---|
| neurons | 127,400 |
| connections (pre→post pairs) | 14,687,178 |
| synapses (sum of per-pair counts) | 52,793,639 |
| timestep | 0.1 ms → 10,000 steps |
| wall-clock, single process | 8.4 s |
| wall-clock throughput, 8 workers | 5.3 s/trial (memory-bandwidth bound; 6 GB peak) |
| estimated ops = neurons × steps + Σ_spikes out-degree | 1.28 × 10⁹ (at 100 Hz sugar; 1.274 × 10⁹ is the neuron term) |

Note the op count is dominated by the neuron-update term; the spike-driven synapse term is < 0.2% at baseline because
only ~360 of 127,400 neurons are active. Knobs that remove neurons (cell-type merging) or steps (dt) will move this
number; pruning and quantization will not, unless the estimator is changed to count stored synapses. Flagged for Phase 1.

## Sweep results (Phase 2, five knobs)

5 seeds per level (1000–1004), FlyWire v630, 1000 ms trials. Primary fidelity = MN9 rate at 100 Hz sugar / 67.0 Hz,
clipped to [0, 1]. Curve fidelity = 1 − RMSE over 40/60/100/150/200 Hz ÷ RMS of the baseline curve. Noise floor:
the untouched model with these 5 seeds scores 0.997 primary and 0.974 curve.

### Cliffs

| knob | first level below 0.9 (primary) | first level below 0.5 (primary) | curve < 0.9 | curve < 0.5 |
|---|---|---|---|---|
| **signflip** (fraction of neurons E/I-flipped) | p = 0.03 | p = 0.10 | p = 0.01 | p = 0.10 |
| **shuffle** (fraction of connections rewired, degree-preserving; null) | p = 0.10 | p = 0.30 | p = 0.10 | p = 0.30 |
| **quantize** (distinct synapse-count values N) | N = 4 | N = 4 | N = 4 | N = 2 |
| **prune** (drop connections with < T synapses) | T = 7 (0.89) | T = 20 | T = 7 | T = 20 |
| **dt** (integration step) | 6.4 ms (0.43) | 6.4 ms | 3.2 ms | n/a (curve not run at 6.4 ms) |

Which knob breaks first: **sign randomization**. Flipping 3% of neurons (1 in 33) halves the behavior; 10% kills it.
Rewiring is next: 10% of connections rewired with degrees preserved costs 15%, 30% kills it. Weight precision is
robust down to 8 distinct values and collapses at 4. Pruning is remarkably tolerant: keeping only connections with
≥ 5 synapses (18% of connections) still scores 0.96, ≥ 10 synapses (7%) scores 0.89, and the cliff is between 10 and
20. Timestep is the most tolerant knob: at 3.2 ms (32× coarser, 31× fewer ops) primary is still 0.94 and only
the curve shape degrades (0.82); the cliff arrives at 6.4 ms (0.43).

### Per-knob curves

![quantize](results/quantize.png) ![prune](results/prune.png)
![dt](results/dt.png) ![shuffle](results/shuffle.png)
![signflip](results/signflip.png)

### Fidelity vs cost, all knobs

![vs ops](results/combined_fidelity_vs_ops.png)
![vs bytes](results/combined_fidelity_vs_bytes.png)

Only dt moves the estimated-ops axis (clock-driven simulator: 99.8% of ops are neuron updates). Only prune and
quantize move the stored-bytes axis. Prune reaches 0.89 fidelity at 10× fewer stored bytes and 0.96 at 5× fewer.

### Shuffle vs sign-flip on a shared denominator

The two randomisation knobs are parameterised differently (fraction of connections rewired vs fraction of neurons
flipped). `results/{knob}.summary.csv` column `frac_connections_changed` puts both on the same axis: the fraction
of the 14.7 M (pre, post) pairs whose signed weight changed. `results/shuffle_vs_signflip_by_connections.png`
overlays them. Sign-flipping a neuron changes every one of its outgoing connections, so p = 0.03 of neurons is a
larger fraction of connections than p = 0.03 rewired; see the plot for the comparison at equal connection counts.

**Transmitter sign is predicted, not measured.** In this model every neuron is exclusively excitatory or inhibitory,
with the sign taken from a machine-learning neurotransmitter prediction on electron-microscopy synapse images
(Eckstein et al. 2024), thresholded per neuron by majority vote across its presynaptic sites. The sign-flip knob
therefore probes sensitivity to errors in that prediction as much as to biology.

### Perturbation accounting

Every level ≥ 1 of every knob perturbed all or nearly all of the 410 baseline-active neurons (minimum 370/410, for
signflip p = 0.01, where 4 of the 410 active neurons were themselves flipped). No curve in this sweep is flat because
the pathway was untouched; the flat stretches (quantize N = 64…8, dt 0.2…1.6 ms, prune T = 2…5) are genuine
robustness. Full per-level numbers, including the fractional weight change on inputs to active neurons, are in
`results/{knob}.summary.csv`.

### Fine cliff pass, dt extension, symmetric score (added after Phase 2 review)

Prune and signflip were re-run at intermediate levels; dt was extended to 6.4 ms for the primary score only
(the 200 Hz curve point would have a Poisson probability per step above 1). A third score, **symmetric fidelity**
= 1 − |rate/reference − 1|, penalises overshoot; it is computed from stored rates and never needed a rerun.

| knob | primary trajectory (level → fidelity) | cliff (primary < 0.5) |
|---|---|---|
| prune | T=5 0.96 · T=7 0.89 · T=10 0.89 · T=12 0.77 · T=15 0.72 · T=20 0.28 | between T=15 and T=20 (3.8% and 2.4% of connections) |
| signflip | p=.01 1.00 · .015 0.96 · .02 1.00 · .03 0.64 · .05 0.99 · .07 0.85 · .10 0.20 | between p=0.07 and 0.10, but see the draw caveat |
| dt | 1.6 ms 1.00 · 3.2 ms 0.94 · 6.4 ms 0.43 | between 3.2 and 6.4 ms (64× coarser than the authors' 0.1 ms) |

Symmetric score changes only where MN9 overshot: signflip p=0.01 drops from 1.00 to 0.75 (84 Hz), dt 0.8 ms from
1.00 to 0.90 (74 Hz), quantize N=16 from 1.00 to 0.93. No cliff position moves.

### Random knobs with one independent draw per seed

Each signflip/shuffle level in the main sweep used a single random draw of *which* neurons to flip or rewire,
shared by the five simulation seeds. The non-monotonic signflip trajectory (0.64 at 3% then 0.99 at 5%) was draw
variance, not level dependence. `results/{knob}_draws.csv` reruns both knobs with an independent draw per seed
(`--draws-per-seed`); mean over the five draws, with the min–max spread across draws:

| level | signflip, 1 draw | signflip, 5 draws (min–max) | shuffle, 1 draw | shuffle, 5 draws (min–max) |
|---|---|---|---|---|
| 1% | 1.00 | 1.00 (0.88–1.00) | 1.00 | 1.00 (1.00–1.00) |
| 1.5% | 0.96 | 0.99 (**0.18**–1.00) | | |
| 2% | 1.00 | 0.93 (0.55–1.00) | | |
| 3% | 0.64 | 0.84 (0.49–1.00) | 0.96 | 1.00 (1.00–1.00) |
| 5% | 0.99 | 0.49 (0.15–0.64) | | |
| 7% | 0.85 | 0.73 (0.28–1.00) | | |
| 10% | 0.20 | 0.61 (0.06–0.85) | 0.85 | 0.73 (0.28–1.00) |
| 30% | 0.00 | 0.11 (0.00–0.28) | 0.00 | 0.22 (0.00–0.55) |

Two conclusions. The draw-averaged cliffs are later than the single-draw ones (signflip < 0.5 at 5% rather than
10%... the 5% and 10% means are within draw noise of each other; shuffle < 0.5 at 30% either way). And the spread
is enormous: one draw at 1.5% sign-flipped neurons scored 0.18 while another scored 1.00. Fidelity of this
behavior depends on whether the draw hits a handful of specific neurons, not on the fraction perturbed. The
per-draw results are the honest version of these two curves; the single-draw curves are kept for the record.
Plots: `results/signflip_draws.png`, `results/shuffle_draws.png`, `results/shuffle_vs_signflip_by_connections_draws.png`.

### Combined degradation

prune T=5 → quantize N=8 → dt 1.6 ms, applied in that order, 5 seeds (`results/combo.json`).

| | baseline | combined | ratio |
|---|---|---|---|
| fidelity (primary / symmetric / curve) | 1.00 / 1.00 / 0.97 | 0.90 / 0.90 / 0.84 | |
| MN9 at 100 Hz sugar | 67.0 Hz | 60.0 Hz (56–66 across seeds) | |
| stored connections | 14.69 M | 2.61 M | 0.18 |
| stored bytes | 150 MB | 25 MB | 0.17 |
| estimated ops / trial | 1.28 × 10⁹ | 8.0 × 10⁷ | 0.063 |
| wall-clock / trial | 5.3 s | 0.6 s | 0.11 |

The three individually "free" degradations cost about 10% of fidelity together, for a 16× cheaper model in ops
and 6× smaller in storage. The losses are roughly additive (individually 0.96, 0.99, 1.00 primary; curve 0.90,
0.96, 0.95).

### Cell-type merging (sixth knob), summed vs averaged

Two variants. `merge` sums synapse counts over parallel connections (as the brief specifies). `merge_mean` divides a merged
node's *incoming* counts by its member count so the node receives what a typical member received, and keeps
*outgoing* counts summed so one spike stands for every member's spike (population-node style).

| merged | active merged | merge (sum) | merge_mean | curve, sum / mean |
|---|---|---|---|---|
| ≤ 75% | 0 | 0.997 | 0.997 | 0.974 / 0.974 |
| 90% | 75 | 0.928 | 0.591 | 0.875 / 0.698 |
| 95% | 226 | 0.893 | 0.707 | 0.763 / 0.729 |
| 99% | 332 | 0.794 | 0.645 | 0.807 / 0.651 |
| 100% | 334 | 0.794 | 0.663 | 0.793 / 0.654 |

Summing props the merged model up: at 90% merged the summed variant keeps 0.93 and the averaged variant 0.59.
The 21% loss under summing was therefore the *net* of a gain increase and a loss of identity; averaging exposes
the identity loss on its own, about 35–40%. Neither variant crosses 0.5.

### Cell-type merging (sixth knob), details

Types from Schlegel et al. 2024 (release v1.1.0, FlyWire v630 IDs; 127,322 of 127,400 model neurons mapped; 23,194
neurons in 1,770 types with ≥ 2 members are mergeable). Merge = collapse each type into one node, sum synapse counts
over parallel connections, majority sign, drop the orphaned members. Stimulated neurons and readouts are never
merged. Levels are the fraction of mergeable neurons merged, **largest types first** as the brief specifies. Deterministic.

| merged | types | neurons removed | of the 410 active: perturbed / merged | primary | curve |
|---|---|---|---|---|---|
| 10% | 1 (R1-6) | 2,425 | 0 / 0 | 0.997 | 0.974 |
| 25% | 4 | 7,029 | 0 / 0 | 0.997 | 0.974 |
| 50% | 9 | 12,354 | 17 / 0 | 0.997 | 0.974 |
| 75% | 28 | 17,396 | 158 / 0 | 0.997 | 0.974 |
| 90% | 611 | 20,265 | 410 / 75 | 0.928 | 0.875 |
| 95% | 1,191 | 20,845 | 410 / 226 | 0.893 | 0.763 |
| 99% | 1,655 | 21,309 | 410 / 332 | 0.794 | 0.807 |
| 100% | 1,770 | 21,424 | 410 / 334 | 0.794 | 0.793 |

Largest-first means the first 75% of merging is entirely optic-lobe and mushroom-body types (R1-6, KCab, Mi1, T4/T5…)
and the sugar pathway is untouched: fidelity is bit-identical to baseline through 75%, and the perturbation log says
why. The pathway's own collapse happens between 75% and 100%, and even with 334 of the 410 active neurons merged into
type nodes (their summed input weights changed by 126%) MN9 still reaches 0.79 of its baseline rate. **No merge level
drops below 0.5.** The curve score shows what summing does: at full merge MN9 fires *more* at low sugar rates (40 Hz:
7 → 21 Hz) and *less* at high rates (200 Hz: 91 → 77 Hz), because a merged node receives the sum of its members'
inputs and saturates. Compute: merging removes 17% of neurons and 12% of stored connections; est_ops drops 17%.

Caveats: (1) 2,037 members disagree with their merged node's majority sign (recorded per level). (2) A type-count
ordering other than largest-first would place the pathway's collapse at a different nominal level; the per-level
"active merged" column is the invariant to compare against. (3) 18% of neurons carry a cell type in this release,
but 82% of the active pathway does, so coverage is not the limiting factor for this behavior.

### Per-neuron sensitivity map (from the per-seed draws; no new sweep)

Every signflip and shuffle draw was regenerated deterministically and expressed as a vector over the 410 active
neurons (silent neurons cannot matter). Per-neuron effect sizes were fitted by non-negative least squares,
loss ~ draws × β, over the unsaturated draws (`scripts/sensitivity_map.py`; `results/sensitivity/`). The
signflip map is well identified (38 usable draws, residual 0.2% of total). The shuffle map is **not**: rewiring
touches nearly every active neuron in every draw (top entries hit in 25 of 30), so its ranks are reported but not used.

![cumulative](results/sensitivity/signflip_cumulative.png)

**13 neurons carry 80% of the attributed sign-flip loss.** Their identities were then checked directly by flipping
each of the top 20 alone (3 seeds, `results/sensitivity/verify_sugar.csv`):

| rank | FlyWire ID | type | library name | single flip → fidelity |
|---|---|---|---|---|
| 1 | 720575940630683385 | CB0801 | | 0.99 |
| 2 | 720575940619588568 | | | 1.00 |
| 3 | 720575940607272649 | CB0553 | **roundup** | **0.53** |
| 4 | 720575940610232274 | CB0110 | gnome | 1.00 |
| 7 | 720575940632047890 | CB0393 | | **0.65** |
| 8 | 720575940612888178 | CB0911 (motor) | | **0.90** |
| 9 | 720575940612648106 | DNge202 | fudog | 1.00 |
| 11 | 720575940623211725 | CB0553 | **roundup** | **0.30** |
| top-5 together | | | | 0.57 |
| top-10 together | | | | 0.14 |
| top-20 together | | | | 0.01 |

Four neurons are individually critical: both **roundup** neurons (a known sugar-circuit interneuron from the authors'
split-GAL4 library, ref. Sterne et al. 2021), one CB0393 interneuron and one CB0911 motor neuron. The other nine of
the 13 matter jointly: flipping the top 10 together removes 86% of the behavior although most of them do nothing
alone. gnome and fudog, both named sugar-circuit neurons, sit in that joint tier.

**Restating the two random knobs.** Sign-flip and rewiring fidelity are not functions of the fraction perturbed.
They are functions of whether the draw hit roundup (either copy), CB0393 or CB0911, and secondarily of how many of
the joint tier it hit. At 1.5% of neurons flipped, four draws missed all of them and scored 1.0; one draw hit one and
scored 0.18. The per-draw plots (`results/signflip_draws.png`, `results/shuffle_draws.png`) show every draw as a point
for this reason.

**Must-match list for the male transfer test** (`results/sensitivity/must_match_sugar.csv`): tier A = the four
individually critical neurons; tier B = the remaining nine of the 80%-of-loss set; tier C = the shuffle map's top five,
low confidence. A male-brain model that reproduces sugar → MN9 must at minimum reproduce the sign and connectivity of
tier A; tier B is the next test.

### Things the primary score misses

Sign-flipping 1% of neurons raised MN9 to 84 Hz at 100 Hz sugar (baseline 67). The primary ratio clips this to 1.0;
the curve score sees it (0.82, RMSE 12 Hz). Same at quantize N = 16 and dt 0.2–0.8 ms: rates drift up by 3–7 Hz.
The primary score, as defined, cannot distinguish "same" from "more". Both are recorded.

## Phase 3: antennal grooming baseline (JON → aDN1)

Stimulus: the 146 Johnston's organ neurons the authors list (JO-CE 70, JO-F 60, JO-D/m 16; the paper says 147).
Readout: aDN1 (FlyWire 720575940616185531, the authors' `id_DN1_1`). Reference stimulation: 140 Hz JON, the
frequency the paper uses for its aDN1 silencing analysis (Fig 5d–f). 30 seeds (1000–1029), v630.

![grooming sweep](results/baseline_grooming/fig5b_jon_sweep.png)
![silencing](results/baseline_grooming/fig5d_silencing.png) ![subtype](results/baseline_grooming/fig5g_abn1_by_subtype.png)

| check | paper | ours |
|---|---|---|
| aBN1, aDN1, aDN2 respond to JON activation (Fig 5b) | yes | yes; all three in the top-300 responders at 220 Hz (ranks 173, 253, 252) |
| silencing aBN1 reduces aDN1 by > 20% at 140 Hz JON (Fig 5d–f) | yes | 100% (16.2 → 0.0 Hz) |
| silencing aDN2 reduces aDN1 by > 20% at 140 Hz JON (Fig 5d–f) | yes | 37% (16.2 → 10.2 Hz) |
| JO-CE drives aBN1 robustly, JO-F does not (Fig 5g) | yes | at 140 Hz: JO-CE 46.6 Hz, JO-F 1.3 Hz; at 220 Hz: 72.9 vs 4.3 Hz |

aDN1 rate vs JON rate (mean ± s.d., Hz): 20–60: 0; 80: 0.6±0.8; 100: 3.6±1.8; 120: 8.7±2.0; **140: 16.2±1.7**;
150: 20.3±2.0; 160: 23.4±1.5; 180: 29.3±1.5; 200: 34.2±1.2; 220: 37.8±1.1. aDN1 and aDN2 track each other almost
exactly at every frequency. Full table: `results/baseline_grooming/fig5b_jon_sweep.csv`.

What did not match: nothing checkable disagreed. The paper gives no aDN1 rate values in the text; the checks above
are the qualitative and threshold claims it makes. 

**Differences from the sugar behavior that matter for the sweep**

- **Low readout rate and late threshold.** aDN1 fires at 16 Hz at the reference (MN9: 67 Hz) and is silent below
  ~80 Hz JON. The primary ratio therefore has ~1 Hz resolution per 6% of fidelity, and the sugar curve frequencies
  (40, 60 Hz) carry no information here. Curve-shape frequencies are now per behavior: grooming uses
  100/140/180/220 Hz (`src/behaviors.py`; `results/baseline_grooming/reference_curve.json`).
- **A single bottleneck neuron.** Silencing aBN1 alone zeroes aDN1. Any degradation that happens to hit aBN1's
  inputs or sign will look like a cliff; the perturbation log records whether aBN1 was touched.
- **Larger active set.** 619 neurons fire in any of 30 trials at 140 Hz JON (sugar at 100 Hz: 410).

## Phase 3: grooming sweep (JON → aDN1) and the cross-behavior comparison

Same knobs, same levels, same seeds, 5 seeds per level; primary = aDN1 rate at 140 Hz JON / 16.2 Hz; curve over
100/140/180/220 Hz. Noise floor with 5 seeds: 0.986 primary, 0.969 curve (aDN1 at 16 Hz has ~6% resolution per spike).
The two random knobs were run with one independent draw per seed only (`results/grooming/{knob}_draws.csv`).

![compare](results/compare_behaviors.png)

### Where the cliffs land (first level with fidelity below threshold; `results/compare_cliffs.csv`)

| knob | sugar < 0.9 | sugar < 0.5 | grooming < 0.9 | grooming < 0.5 |
|---|---|---|---|---|
| quantize (N values) | 4 | 4 | 64 | 2 (non-monotonic: N=16 0.58, N=8 0.69, N=4 1.00*) |
| prune (T synapses) | 7 | 15–20 | 2 | 5 |
| dt (ms) | 6.4 | 6.4 | 0.2 | 1.6 |
| merge (sum) | 0.95 | never | 0.95 | never |
| merge_mean | 0.90 | never | 0.90 | never (overshoots; symmetric < 0.5 at 0.95) |

\* N=4 gives aDN1 24 Hz against a 16 Hz reference; primary clips to 1.0, symmetric is 0.53, curve 0.77.

**The cliffs do not land in the same place.** For the three deterministic "resolution" knobs the grooming circuit
breaks far earlier than the feeding circuit:

- **Timestep**: sugar tolerates 3.2 ms (0.94); grooming is at 0.65 by 0.8 ms and 0.26 by 1.6 ms. aDN1 sits on a
  steep part of its input curve at the reference, so anything that shifts effective drive by a few percent moves it a
  lot, and a coarser step shifts the 1.8 ms delay and 2.2 ms refractory period by whole steps.
- **Pruning**: sugar keeps 0.89 with only ≥ 10-synapse connections; grooming is at 0.49 with ≥ 5 and 0.31 with ≥ 10.
  The JON → aBN1 → aDN1 pathway runs through many weak connections (the paper's own count: JO-CE → aBN1 is 103
  synapses spread over 70 neurons, i.e. ~1.5 per connection).
- **Quantization**: sugar is flat down to 8 values; grooming loses 10% at 64 values and 42% at 16.
- **Merging** is the exception: both behaviors survive full merging (0.79 sugar, 0.92 grooming) and neither crosses 0.5.
  Grooming is *more* tolerant of losing neuron identity than sugar, probably because aDN1's drive is concentrated in
  aBN1, a single neuron per hemisphere that has no type-mates to be merged with.

In the terms of the brief: **the amount of detail a whole-brain model needs depends on the
behavior read out from it.** A model coarse enough to be 16× cheaper still produces sugar → MN9 at 0.90, and the
same model would produce JON → aDN1 at well under 0.5 (dt 1.6 ms alone puts it at 0.26).

### Random knobs on grooming (one independent draw per seed)

| level | signflip sugar (min–max over draws) | signflip grooming | shuffle sugar | shuffle grooming |
|---|---|---|---|---|
| 1% | 1.00 (0.88–1.00) | 0.92 (0.68–1.00) | 1.00 (1.00–1.00) | 0.90 (0.62–1.00) |
| 2% | 0.93 (0.55–1.00) | 1.00 (**0.06**–1.00) | | |
| 3% | 0.84 (0.49–1.00) | 0.92 (0.68–1.00) | 1.00 (1.00–1.00) | 0.80 (**0.06**–1.00) |
| 5% | 0.49 (0.15–0.64) | 0.99 (**0.00**–1.00) | | |
| 7% | 0.73 (0.28–1.00) | 0.38 (0.00–1.00) | | |
| 10% | 0.61 (0.06–0.85) | 1.00 (0.25–1.00) | 0.73 (0.28–1.00) | 0.89 (0.55–1.00) |
| 30% | 0.11 (0.00–0.28) | 0.06 (0.00–0.31) | 0.22 (0.00–0.55) | 0.28 (0.00–1.00) |

The grooming primary means are *higher* than sugar's at most levels, and they are misleading: aDN1 overshoots
under many draws (primary clips to 1.0; the symmetric score at 1.5% is 0.60 and at 10% is 0.64) and the spread is
even more bimodal than for sugar. At 2% of neurons sign-flipped, four draws scored ≥ 0.96 and one scored 0.06; at
5%, four scored 1.00 and one scored 0.00. Grooming's active set is larger (619) but the pathway is narrower: the
draws that fail are the ones that hit aBN1 or its immediate inputs, consistent with the silencing result in the
baseline (aBN1 alone → 0). The same statement as for sugar holds, with a smaller must-hit set: **these two knobs
measure whether a draw hits specific neurons, not how much of the network is perturbed.** Per-draw plots:
`results/grooming/signflip_draws.png`, `results/grooming/shuffle_draws.png`.

### Summary of the cross-behavior comparison

The resolution knobs (timestep, pruning, quantization) have cliffs an order of magnitude earlier for antennal
grooming than for feeding. The identity knobs (merging) do not cliff for either. The randomisation knobs are
governed by a handful of specific neurons in both behaviors, and which neurons differ (roundup/CB0393/CB0911 for
sugar; aBN1 for grooming). A single "how much detail is enough" number does not exist for this brain model; the
answer is per circuit, and the circuit with the lower-rate, later-threshold readout needs more of everything.

## Follow-ups

See `NOTES.md`. The ones that would change conclusions: (1) 20 draws per level for the random knobs, or a full
single-neuron flip screen of the active set (410 or 619 sims), to replace the bimodal 5-draw spreads with a per-neuron
map for both behaviors; (2) the grooming sensitivity map (`scripts/sensitivity_map.py --behavior grooming`, not run);
(3) the MaleCNS transfer test using `results/sensitivity/must_match_sugar.csv` as the acceptance list.
