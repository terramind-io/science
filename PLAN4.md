# Pre-registration 4: the fly simulation as an instinct function

**Registered:** 10 Oct 2026, before any run below. Tracked as GROW-119. **Status:** our own analysis, not peer-reviewed.
Part B (a courtship check) will be added to this file as an amendment, before its own run, once its test cases are compiled from the literature.

## The idea and its stated limit

We package the Shiu et al. 2024 simulation as a function with a fixed interface: a situation described **only in the fly's own senses** goes in, and a fixed-format yes/no answer comes out. We test the answers against real-fly results. We make no claim that this function can answer anything other than a fly's questions; translating other situations into fly senses is outside the scope.

## What we have already seen (declared)

- The paper's Supplementary Table 4: with stimulus rates the authors chose "to elicit 40 Hz MN9 firing, or reduce 40 Hz MN9 to 1 Hz" (sugar about 62 Hz, bitter 94 Hz, water 216 Hz, Ir94e 116 Hz), their simulation gives MN9 about 41 Hz for sugar alone, 1.3 Hz for sugar plus bitter and 1.1 Hz for sugar plus Ir94e.
- The paper's Supplementary Table 7A: with all antennal neurons at 100 Hz, aBN1 fires at about 24 Hz and aDN1 and aDN2 at about 3 Hz.
- Our own run: sugar at 100 Hz gives MN9 67.5 Hz; scrambled wiring gives 0 of 100.
- The real-fly counts in Supplementary Table 9A and the paper's text on grooming (below).
- We have **not** run any mixed stimulus at the uniform rates fixed here, nor the antennal subsets.

## The function (fixed now)

- **Connectome and model:** FlyWire v630 with the published parameters (the connectome the paper validated on). 30 trials of 1 s per situation; seeds fixed in code.
- **Senses (inputs),** as neuron lists named in the paper's supplement: sweet (21 "sugar" neurons), bitter (21), water (18), Ir94e (18), antennal touch (all neurons named JO_* in Supplementary Table 7A), and its two subsets JO-CE (names beginning JO_C or JO_E) and JO-F (names beginning JO_F).
- **Intensity:** every active sense is driven at **100 Hz**. "Strong sweet" is 200 Hz. These are uniform so that no rate is tuned to an outcome.
- **Outputs:**
  - *extend* reads MN9 (`720575940660219265`).
  - *groom* reads the antennal grooming command neurons; the value is the highest mean rate among aBN1 (`720575940630907434`), aDN1 (`720575940616185531`) and aDN2 (`720575940629806974`). For cases G2 and G3 the paper's experiment measured aBN1, so those cases read aBN1 alone.
- **Decision rule:** the answer is **yes if the readout's mean rate over the 30 trials is at least 5 Hz**, otherwise no. Alongside each answer we report the mean rate and the fraction of trials with any spike.
- **Sensitivity (reported, not used for the verdict):** thresholds of above 0 Hz and 10 Hz; suppressor senses at 50 and 200 Hz; and the paper's own tuned rates (as a reproduction of its Table 4).

## Scored cases (real-fly truth fixed now)

| ID | Situation | Output | Real flies | Source |
|---|---|---|---|---|
| F1 | sweet | extend | yes (26 of 30 and 24 of 26 with light off) | Supp. Table 9A |
| F2 | sweet + bitter | extend | no (3 of 30) | Supp. Table 9A |
| F3 | sweet + Ir94e | extend | no (3 of 26) | Supp. Table 9A |
| F4 | strong sweet + bitter | extend | no (5 of 30) | Supp. Table 9A (1 M sucrose) |
| F5 | strong sweet + Ir94e | extend | yes (20 of 26) | Supp. Table 9A (1 M sucrose) |
| F6 | water | extend | yes (control flies extend to water, e.g. 30 of 40) | Supp. Table 9B |
| G1 | antennal touch (all) | groom | yes ("Optogenetic activation of both JO-CE and JO-F neurons is sufficient to trigger antennal grooming") | paper text |
| G2 | antennal touch, JO-CE only | aBN1 active | yes ("JO-CE activated aBN1 robustly") | paper text, Fig. 5h |
| G3 | antennal touch, JO-F only | aBN1 active | no ("but JO-F neurons did not") | paper text, Fig. 5h |

A real-fly "yes" is a majority of flies responding, or the paper's stated outcome. Mapping "1 M sucrose" to 200 Hz and "50 mM" to 100 Hz is our assumption; the paper gives no such mapping.

**Reported but not scored** (no real-fly number in this supplement): nothing active; bitter alone; Ir94e alone; water + bitter; sweet + water; and two cross-checks, antennal touch read at *extend* and sweet read at *groom*.

## Scrambled-wiring control

For each of 10 scrambles (the signed weights permuted across the existing connections, as in our first experiment), the five cases whose real answer is yes (F1, F5, F6, G1, G2) are run for 3 trials each.

## Decision rules (fixed now)

| | Statement | Supported if | Not supported if |
|---|---|---|---|
| **I1** | The instinct function answers like real flies | at least 7 of the 9 scored cases match | 4 or fewer match |
| **I2** | The answers come from the wiring | under scrambled wiring, fewer than 10% of the 50 (case, scramble) pairs answer yes | 50% or more answer yes |

Anything in between is inconclusive. Every case is reported individually, including the ones that fail.

## Limits to state wherever this is used

No hunger or thirst state (real feeding depends on it); yes/no answers only (output strength does not track how many flies respond, see `PAPER_SCOPING.md`); one connectome; only instincts the original paper tested; nine cases, most of them the paper's own experiments, so this is largely a reproduction under uniform settings and not new biology.

---

## Amendment B (10 Oct 2026, before any courtship computation): a second-circuit check on the male map

**Registered before any path score was computed on courtship cell types.** Part A's primary run had finished at this point (6 of 9 cases matched); nothing in Part A is changed by this amendment.

### Purpose and credit

The paper's main map-only result (PLAN3, M1) was tested on feeding only. This asks whether the same kind of path score points the right way in a second circuit: courtship song in the male. It is a **confirmation**, not a first: the FLYCNS project reports that signed path products point the right way for five P1/pC1 groups on the male map, and Berg et al. traced the song pathway. We have seen those statements; we have computed nothing ourselves on these cell types.

### Question for every case

"Does artificially activating cell type X in an **isolated male** produce courtship song?" Real-fly answers come from published activation experiments, compiled with a verbatim quote for each case in `inputs/courtship_cases_literature.csv` (compiled by a search agent on 10 Oct from full texts or, where marked, abstracts and preprints; not re-fetched by us).

### Predictor (fixed now)

The path score of PLAN3 on the male CNS connectivity table (signed synapse counts, no rescaling): place 1 on every neuron of the cell type, multiply by the signed connection matrix and clip negatives to zero, **four** times, and sum what arrives at the readout over the four steps. Four steps and not three because the route from brain neurons to wing motor neurons is longer than the feeding route; three and five steps are reported as sensitivity only.

**Readout:** the wing-control motor neurons named in the male annotation: hg1, hg2, hg3, hg4, i1, i2, b3, ps1, tp1, tp2, tpn and MNwm35 (24 neurons). b1 and b2 are left out because the song-circuit paper reports no strong connections to them; the large power-muscle motor neurons are left out because song is produced by the control muscles.

### Scored cases (fixed now)

| Tier | Cell type(s) in the male table | Real flies |
|---|---|---|
| YES | TN1a (all TN1a_ subtypes) | sine song |
| YES | dMS2 | sine song |
| YES | dMS9 | brief song |
| YES | pC1_4a + pC1_4b + pC1_12b (the "P1a" line) | song, variable |
| YES | pC1_13a + pC1_14a + pC1_14b | song |
| YES | pC1_17a + pC1_17b | transient pulse song |
| YES | pC1_19 | sine song |
| NO (direct) | pC1x_a + pC1x_b + pC1x_d | no song |
| NO (direct) | pC1_10b + pC1_10c + pC1_10d | close interactions, not song |
| NO (direct) | mAL (every type whose name begins mAL) | suppresses courtship |
| NO (direct) | vPR9 (all subtypes) | reduces song |
| NO (indirect) | MDN | backward walking |
| NO (indirect) | DNg07 + DNg08 | head grooming |
| NO (indirect) | DNa01 + DNa02 | locomotion |
| NO (indirect) | DNp29 + DNg10 + DNg13 | grooming and reaching |
| NO (indirect) | LC16 | backward walking |

"Indirect" means the paper reports a different behaviour and does not state "no song"; those five are a second tier. pIP10, pMP2 and dPR1 (song command and premotor neurons) are reported as positive controls and not scored. Cases the literature leaves mixed (vPR6, vMS12, pC1_1a/2a/2b/15a–c, LC10) are reported and not scored.

### Scores and decision rule (fixed now)

AUROC of the path score for YES against NO (ties as half), on the 11 primary cases (7 YES, 4 direct NO) and on all 16.

| | Statement | Supported if | Not supported if |
|---|---|---|---|
| **K1** | The map-only path score points the right way for courtship song | AUROC at least 0.80 on the 11 primary cases **and** at least 0.75 on all 16 | AUROC 0.60 or below on the primary cases |

Otherwise inconclusive. Reported alongside, without a verdict: every case's score; the same AUROC with the signed weights scrambled across connections (20 scrambles); three- and five-step versions; and the mAL case restricted to its inhibitory neurons.

### Limits to state

Eleven primary cases from about six independent sources (the seven P1/pC1 cases come from one preprint and one assay); real-fly outcomes for several cell types depend on context (a moving target, another fly); driver lines do not always isolate one cell type; a sign-aware score scores inhibitory cell types as zero by construction, so two of the four direct NO cases test sign handling more than route finding; one fly; no behaviour is simulated.
