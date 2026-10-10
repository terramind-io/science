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
