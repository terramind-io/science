# Pre-registration 3: two new questions

**Registered:** 10 Oct 2026, before any run below. Tracked as GROW-115. **Status:** our own analysis, not peer-reviewed.
**Framing (AGENTS.md "Tone"):** we report what the results show. Limits are stated plainly. Verdict rules below are neutral and fixed now; the wording of the write-up does not change them.

## What we have already seen (declared)

- **Exploratory pilot** (`code/explore_pathcount.py`, commit `44c22ee`): on FlyWire v630 with the paper's own neuron lists, a 3-step signed path score ranked the 106 cell types at AUROC 0.804 against real flies; the paper's simulated 50 Hz rates gave 0.853. Eight variants were tried (1–4 steps, signed or excitatory-only). We chose "signed, 3 steps" from these.
- The paper's own "Shortest Path" column (Supplementary Table 3) gives AUROC 0.771 on the same 106 types.
- **Draft census** (`census_draft/`): a search agent's README-level extraction. We have seen its rough pattern (female v630 numbers near 67 Hz; male weight factors spread from 0.15 to 0.65).
- Because of the above, the v630 106-type result is **development data** and is reported as exploratory. The confirmation sets below have not been scored with any map-only predictor.

---

## 3A. How much of the fly's feeding behaviour is already written in the wiring map?

### Predictors (all fixed now)

| ID | Predictor | Definition |
|---|---|---|
| P0 | Always "no" | Baseline |
| P1 | Step count | Fewest synaptic steps from any neuron of the cell type to the feeding motor neuron MN9, on the model's connectivity table (every listed connection counts as one step). Fewer steps = higher score; no path = lowest. |
| P2 | Path score | Start with 1 on every neuron of the type. Multiply by the signed connection table, clip negatives to zero, three times. Score = sum of what arrives at MN9 over the three steps. (This is a crude rate calculation, not a spiking simulation; we say so.) |
| P3 | Simulation | Mean MN9 firing rate from the spiking simulation at 50 Hz activation, 30 trials (already run in PLAN2). |

Sensitivity only (never used for a verdict): P2 with 2 and 4 steps, and excitatory-only.

**Validity check for P1:** our step counts on v630 are compared with the paper's "Shortest Path" column. We report the match count. If fewer than 90% of types match exactly, both versions are reported.

### Confirmation sets

| Set | Map | Cell types | Stimulated neurons | MN9 readout | Simulation comparator |
|---|---|---|---|---|---|
| C1 | Male CNS v1.0 | 99 | `male_ids` | MN9_L `10331` | `2A_Ms` (×0.561); also `2A_M698`, `2A_M` reported |
| C2 | FlyWire v783 | 101 | `female783_typed_ids` | `720575940660219265` | `2A_F783T` |
| C3 | FlyWire v630 | 20 silencing cases | see below | `720575940660219265` | the paper's published silencing ratios |

Truth for C1 and C2 is the same real-fly screen as before (positive if the observed rate is above 0). **So C1 and C2 test a new map and a new neuron selection against the same real-fly labels; they are not new fly experiments.** We say this wherever the result is used.

**C3, the harder case (silencing).** The paper argues the simulation earns its keep on cases like this. From Supplementary Tables 2 and 5: for 10 named cell types under sugar and 10 under water, real flies were tested with that type silenced ("required for proboscis extension": yes/no). Labels are taken from those tables; for Fdg under sugar we use "No" (Shiu, Sterne et al. 2022), which is the reading that reproduces the paper's own count of 6 of 10 correct. MN9 itself is excluded.
- **Simulation prediction (the paper's):** required if the published MN9 ratio after silencing is below 0.8 (their 20% rule).
- **Map prediction:** P2 from the taste neurons (the paper's sugar set; the water set named in Supplementary Table 6) to MN9, computed with and without the cell type's outgoing connections. Required if the ratio is below 0.8.
- If the P2 baseline from the taste neurons to MN9 is zero at 3 steps, C3 is reported as "not computable at 3 steps" and the 4-step sensitivity result is shown, labelled as such.
- A cell type whose neurons we cannot identify from `sez_neurons.pickle` is excluded and listed.

### Scores

For C1 and C2: AUROC of each predictor against real flies, with a bootstrap 95% interval over cell types (10,000 resamples, seed 0), and the paired bootstrap interval of the difference (P3 − P2) and (P3 − P1). Also the agreement between P2 and the simulation's yes/no calls (AUROC of P2 against "simulation fired").
For C3: number correct out of 20 for each predictor, and the list of cases where they differ.

### Decision rules (fixed now)

| | Statement | Supported if | Not supported if |
|---|---|---|---|
| **M1** | The map alone carries real signal | On **both** C1 and C2, the lower end of P2's AUROC interval is above 0.5 | On either set the interval includes 0.5 |
| **M2** | On this screen the map-only score is not distinguishable from the simulation | On **both** C1 and C2, the interval of (P3 − P2) includes 0 **and** the point difference is at most 0.10 | On either set the interval of (P3 − P2) lies wholly above 0 (simulation clearly better) |
| **M3** | The simulation does better on the harder silencing cases | The simulation is correct on at least 3 more of the 20 cases than P2 | P2 is correct on as many or more cases than the simulation |

Anything in between is **inconclusive**. M2 "supported" means *this test cannot tell them apart* (13 positive cases), not that they are equal; the write-up must say that. M1 is also reported for P1.

---

## 3B. A census of independent re-runs

**Design:** a retrospective census of public repositories, not a prospective many-analysts study. We run nobody else's code. We read what each project reports and, where its settings are stated, compare with what the published model gives under those settings using our own validated runner.

### Frame (frozen)

`census/frame.csv`: the 97 GitHub repositories whose README contained a line with both "MN9" and a Hz value in the search snapshot of 10 Oct 2026, with README copies in `census/readmes/`. The search covers an unknown fraction of public GitHub (our agent's guess: half or less), so every count is a lower bound. Projects known from our notes whose numbers sit outside the README (Fugsukjit, flymsg, Fly.exe, flybench) are listed separately and not counted in the frame.

### Inclusion (frozen)

A repository is **included** if its README reports a firing rate of MN9 that the project itself measured, from a Shiu-type integrate-and-fire model on a fly connectome, under sugar taste-neuron activation. **Excluded:** lines that are thresholds, stimulus rates, interface examples or numbers quoted from the paper or from another project; verbatim copies of another repository; a second repository by the same owner reporting the same run (keep the earliest first commit).

### Extraction codebook (frozen)

For each repository: include (yes/no, reason); connectome for the headline number (v630 / v783 / male CNS / BANC / other / not stated); stimulus set (paper's 21 sugar neurons / other / not stated); stimulation rate in Hz (or not stated); MN9 rate in Hz as reported; the reference value they compare against, if any; shuffled or rewired wiring outcome for MN9 (silent / reduced / not reported, with numbers); male-map weight correction (factor relative to the published 0.275 mV, or not reported); whether they state they reproduce the paper; the exact quoted line for every number. "Not stated" is used whenever the README does not say; nothing is inferred.

**Two independent extractors** work from the same README copies without seeing each other's output or the draft census. We report agreement on inclusion and on the MN9 rate (exact match). Disagreements are resolved by us from the quoted lines, and the resolution is logged.

### Outcomes (fixed now)

| | Statement | Supported if | Not supported if |
|---|---|---|---|
| **R1** | Independent re-runs of the paper's headline case agree with the paper | Among included repositories that state FlyWire v630 and 100 Hz (or state they reproduce the paper's shipped sugar result), at least 80% report MN9 within ±5 Hz of the paper's 67.0 Hz, with at least 5 such repositories | Fewer than 50% do. Fewer than 5 such repositories = not assessable. |
| **R2** | The shuffled-wiring control holds up | Among included repositories reporting a shuffle or rewiring outcome for MN9, at least 80% report MN9 silent or reduced by at least 90% | Fewer than 50% do. Fewer than 5 = not assessable. |
| **R3** | There is no agreed correction for the male map | Among repositories reporting a male-map weight factor, the largest is at least twice the smallest | The largest is within 1.25× of the smallest. Fewer than 4 = not assessable. |

Descriptive, no verdict: number included and excluded with reasons; connectomes used; first-commit dates by month; licences.

**Our own re-check:** for any complete setting (connectome, stimulus set, rate) reported by at least 3 included repositories for which we do not already have a reference run, we run our validated runner under that setting (30 trials) and report it next to the reported values.

### Fairness rules

No ranking of individuals and no "failed" labels. Results are reported in aggregate; a project is named only to credit a specific contribution or as the source of a quoted number. Token or coin projects are excluded from naming. Before anything is published, named authors are contacted with a correction window.

## Publication gate

Unchanged from AGENTS.md "Credibility comes first": independent audit of results, prior-work re-check before release, and the original authors see 3A before it goes out.
