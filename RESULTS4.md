# Results 4: the simulation as an instinct function, and a courtship check

**Status:** our own analysis, not peer-reviewed. Pre-registered in `PLAN4.md`: Part A in commit `d91f86c`, Amendment B in commit `3ad7cd8` (its case table in `f37ad65`), each before its own run. Not cleared for publication.

Numbers: `results/plan4/instinct.json` (`code/score_instinct.py`) and `results/plan4/courtship.json`, `courtship_cases.csv` (`code/run_courtship.py`).

## Part A. The instinct function

A situation described only in the fly's own senses goes in; a yes/no answer comes out. Every active sense is driven at the same level (100 Hz; "strong sweet" 200 Hz), and the answer is yes when the readout neuron fires at 5 Hz or more on average over 30 trials. FlyWire v630, published parameters.

### Pre-registered verdicts

| | Statement | Result | Verdict |
|---|---|---|---|
| **I1** | The function answers like real flies | 6 of 9 cases match (7 needed) | **Inconclusive** |
| **I2** | The answers come from the wiring | Under scrambled wiring, 9 of 50 (case, scramble) pairs still answer yes (18%; the bar was under 10%) | **Inconclusive** |

### The nine cases

| Case | Situation | Readout | Rate (Hz) | Answer | Real flies | Match |
|---|---|---|---|---|---|---|
| F1 | sweet | MN9 | 69.0 | yes | yes (26 of 30) | yes |
| F2 | sweet + bitter | MN9 | 4.3 | no | no (3 of 30) | yes |
| F3 | sweet + Ir94e | MN9 | 16.1 | yes | no (3 of 26) | **no** |
| F4 | strong sweet + bitter | MN9 | 56.0 | yes | no (5 of 30) | **no** |
| F5 | strong sweet + Ir94e | MN9 | 79.2 | yes | yes (20 of 26) | yes |
| F6 | water | MN9 | 0.0 | no | yes | **no** |
| G1 | antennal touch | grooming neurons | 23.9 | yes | yes | yes |
| G2 | touch, JO-CE only | aBN1 | 25.5 | yes | yes | yes |
| G3 | touch, JO-F only | aBN1 | 0.9 | no | no | yes |

### What the misses have in common

In all three, the function gets the **direction** right and the **yes/no** wrong, because the answer depends on how strongly each sense is driven:

- **F3:** Ir94e does suppress the sweet response (69 Hz down to 16 Hz), but not below the 5 Hz bar. At twice the Ir94e drive it does (3.3 Hz).
- **F4:** bitter does suppress the strong sweet response (92 Hz down to 56 Hz), but not enough. At twice the bitter drive it nearly does (9.2 Hz).
- **F6:** water alone at 100 Hz does not reach MN9 at all. At the rate the paper used (216 Hz) it does (36.8 Hz).

With the paper's own tuned rates we reproduce its Table 4: sugar alone 39.3 Hz, sugar + bitter 0.03 Hz, sugar + Ir94e 0.27 Hz, water 36.8 Hz, water + bitter 9.9 Hz. So the simulation carries these instincts, but a single uniform "loudness" for every sense is not enough to turn them into correct yes/no answers. Each sense needs its own scale, and the model has no principled way to set it.

Other readings of the threshold (reported, not used for the verdict): any firing above 0 Hz gives 4 of 9; 10 Hz gives 6 of 9.

### Scrambled wiring

| Case | Scrambles answering yes (of 10) |
|---|---|
| F1 sweet | 0 |
| F5 strong sweet + Ir94e | 0 |
| F6 water | 0 |
| G1 antennal touch | 6 |
| G2 touch, JO-CE | 3 |

The feeding answers vanish when the connection strengths are scrambled. The grooming answers often survive. The scramble keeps every connection and only swaps strengths, and the antennal neurons connect to the grooming neuron aBN1 directly (the paper counts 103 and 78 synapses from the two subsets), so a one-step route remains. The grooming cases here are a one-step relay, and this control cannot show that they depend on the specific strengths.

### Unscored situations and cross-checks

- Nothing active, bitter alone, Ir94e alone, water + bitter: MN9 silent (0 Hz).
- Sweet + water: 86.2 Hz, above sweet alone (69.0 Hz).
- Antennal touch read at the feeding neuron: 0 Hz. Sweet read at the grooming neurons: 0 Hz. The two instincts do not leak into each other.

### What the independent audit added (10 Oct)

Every number above was reproduced from the raw files with separate code. The audit's points:

- **Only five of the nine cases were open questions for us.** We had declared knowing the sweet and antennal-touch results. We had also read the paper's statement that its model predicts JO-CE drives aBN1 and JO-F does not, and its Supplementary Table 8 gives the simulated values, so G2 and G3 were effectively known as well; we had not listed that. Of the five truly open cases (F2 to F6), **2 matched**.
- **Our own assumption decides the verdict.** Mapping 1 M sucrose to 200 Hz is what makes F4 fail. Had "strong sweet" been 100 Hz, F4 would equal F2 and the count would be 7 of 9. F5's match is uninformative, since sweet plus Ir94e answers yes at almost every level tried.
- **F2 passes narrowly:** 4.3 Hz against a 5 Hz bar (bootstrap interval over trials 3.4 to 5.2 Hz).
- **Threshold:** the count is 5 for thresholds of 1 to 4.3 Hz, 6 from 4.3 to 16.1 Hz, and 7 from 16.2 to 23.8 Hz. It is never 4 or fewer in that range.
- **G1's real-fly "yes" is an inference.** The paper says each antennal population is sufficient to trigger grooming; it does not report activating all of them together.
- **Scrambled wiring, explained and checked.** The connectivity file has 36 direct connections (148 synapses, all excitatory) from the antennal neurons onto aBN1, and none from any taste neuron onto MN9. Across the ten scrambles, the summed direct strength onto aBN1 orders the grooming rates. (The paper's text gives 103 and 78 synapses for the two subsets; the file we use has 77 and 69.)
- **Tuned-rate reproduction.** At the paper's rates we get 39.3 / 0.03 / 0.27 / 36.8 / 9.9 Hz against the paper's 40.8 / 1.3 / 1.1 / 40.4 / 10.1 Hz.
- **Antennal neurons:** we use the 146 named in the supplement; the paper's text says 147.
- **Process:** the scoring script was written after the primary run (it applies the plan's rule as written); the three code changes after the plan were crash fixes and sharding.

### Limits

No hunger or thirst state. Yes/no answers only. One connectome. The mapping of "1 M sucrose" to 200 Hz is our assumption. Eight of the nine cases are the original paper's own experiments, so this is a reproduction under uniform settings, not new biology. Real bitter taste also acts at the sensory neuron itself, which no wiring-map model includes.

## Part B. A second-circuit check: courtship song on the male map

**Question for each case:** does activating this cell type in an isolated male produce song? Real-fly answers come from published activation experiments (`inputs/courtship_cases_literature.csv`). **Predictor:** the map-only path score, four steps, from the cell type to 24 wing-control motor neurons, on the male CNS.

### Pre-registered verdict

| | Statement | Result | Verdict |
|---|---|---|---|
| **K1** | The path score points the right way for courtship song | AUROC 0.821 on the 11 primary cases (bar 0.80) and 0.794 on all 16 (bar 0.75) | **Supported** by the rule; weak as evidence (see the audit notes) |

- With scrambled connection strengths (20 scrambles) the AUROC is 0.25–0.43 on the primary cases; none reaches the real value.
- Sensitivity: three steps give 0.786 and 0.778; five steps give 0.750 and 0.698. The verdict holds only at the pre-registered four steps.
- The song command and premotor neurons used as positive controls (pIP10, pMP2, dPR1) score among the highest values.
- Restricting mAL to its inhibitory neurons leaves the result unchanged (0.821).

### Where it is right and wrong

- All four highest-scoring primary cases are P1/pC1 groups; three of them sing in real flies.
- **Miss:** pC1x_a/b/d scores high but does not sing in real flies.
- **Miss:** dMS2 sings in real flies but scores low.
- vPR9 scores exactly zero and mAL low because they are inhibitory; a sign-aware score gives that by construction.
- Among the indirect negatives, LC16 scores high. It has 182 neurons, and the score is not normalised by the number of neurons.

### What the independent audit added (10 Oct)

Every number was reproduced with separate code. The verdict follows the rule, but the audit shows how little it rests on:

- **Sign handling carries the result.** Without the two inhibitory cell types (vPR9 and mAL) the primary AUROC is 0.643 on 9 cases, which would be inconclusive. A score that ignores sign gives 0.500. What the test shows is mostly that a sign-aware score sets inhibitory cell types to zero, not that it finds the song route among excitatory ones.
- **One pair decides it.** 23 of 28 YES/NO pairs are ordered correctly; 22 would fail. Leaving out any one of five cases turns the verdict inconclusive (leave-one-out range 0.762 to 0.952). An exact permutation test gives p = 0.055 on the primary cases and 0.027 on all 16.
- **Only four steps pass,** of three, four and five.
- **Three of the four direct NO labels are our reading, not the papers' words.** The vPR9 result is from courting males and the mAL result from a male with a female, not isolated males. The pC1_10b–d label rests on "predominantly promote close interactions", which does not say "no song"; the same sentence covers three other P1 groups that we set aside as mixed, and scoring those as NO as well gives 0.735.
- **Group size is not inflating it.** Normalising the score per neuron gives 0.821 and 0.857. Under scrambling the score follows group size and the NO groups are larger, which is why the scrambled AUROC sits near 0.3; per-neuron scrambles centre near 0.5.
- **Sources:** the 11 primary cases come from three sources, not six (six holds for all 16). There are six P1/pC1 cases, not seven as the plan's limits said.
- **Positive controls** rank 2nd, 4th and 5th of 25 raw, and 1st to 3rd per neuron.
- **Housekeeping:** the plan amendment was committed about 20 seconds before the first result file; two commit messages are swapped (the amendment text is in `3ad7cd8`, the case table in `f37ad65`). An unscored case (pC1_2a,2b) picked up one extra neuron through a name prefix.

**Our reading:** K1 passes the rule we set, and we report it as such. As evidence that the wiring map points to the song pathway, it is weak.

### Limits

Eleven primary cases from three sources (the P1/pC1 and nerve-cord cases from two preprint versions, read by a search agent and not by us). Real-fly outcomes for several cell types depend on context. The score is a sum over all neurons of a type, so larger cell types score higher. Two of the four direct NO cases test sign handling more than route finding. One fly. This confirms on our own terms what the FLYCNS project and Berg et al. had already indicated; it is not a first.

## Prior work to credit for Part A (search of 10 Oct)

Felix471/ask-the-fly (four taste levels in, a four-state feeding label out, both sexes); roblitz-spec/fly-instinct ("Instinct Engine"); Cho's flybench (reflex tasks including bitter suppression, with scrambled-wiring controls); Fugsukjit's benchmark (pre-registered sugar + bitter, sugar + Ir94e, water and antennal tests; his water test also failed at default drive); opifor/femaleflybrain; joshuabradley012/brainfly (male map). None was found scoring a yes/no answer against the real-fly counts for mixed stimuli. Ours is a confirmation with a stricter scoring.

## Cloud runs

Scrambled-wiring and sensitivity runs: 7 cloud jobs (batch `plan4-instinct-cloud-2`, 10 Oct), about 31,000 credits, all on files with the same SHA-256 as the laptop's (`results/plan4/local_sha256.txt`; job logs). A first batch failed during setup on the wrong machine image (about 4,400 credits). The primary run was done on the laptop before Agrim asked for no more local runs.
