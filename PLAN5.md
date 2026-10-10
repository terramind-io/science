# Plan 5: does the wiring map carry a male's song to the female's "yes" neurons?

**Status:** our own analysis, not peer-reviewed. Written on 10 October 2026 and committed before any map-only score from the hearing neurons was computed.

## Why

Agrim asked for a courtship test for the video and the paper: when a male sings, what happens in the female's brain? In real flies a female signals that she accepts a male by opening her vaginal plates, in response to his song. Wang et al. (Nature 2021, https://doi.org/10.1038/s41586-020-2972-7) report that this is controlled by a pair of female-specific descending neurons (vpoDN), which receive excitatory input from song-tuned auditory neurons (vpoEN) and from pC1 neurons.

## What we already know (declared)

- **Our own exploratory runs in the lab's JavaScript engine** (`playground/tools/explore_courtship.mjs`, FlyWire v783, 10 runs per setting): with the 387 auditory neurons switched on at 20 to 200 Hz, vpoEN and vpoDN stay at 0 Hz. Switching vpoEN on directly makes vpoDN fire, and so does switching pC1 on.
- **Prior work, found in our survey:** the README of opifor/femaleflybrain states, from pre-registered experiments at the published parameters, that "courtship song entering the female's ear does not reach vpoDN". tobasummandal/flypair pairs a male and a female model and reads vpoDN as "accept". The simulation result is theirs first; ours is a confirmation.
- **Not known to us:** any map-only score from the hearing neurons to vpoEN or vpoDN. None has been computed.

## Question

The paper's theme is what the map predicts without a simulation. Here the simulation stays silent. Does the map itself contain a route from the ear to the acceptance neurons?

## Data and sets

FlyWire v783 model network (Shiu's `Completeness_783.csv` and `Connectivity_783.parquet`, unchanged). Sets from the FlyWire annotation table:
- **Hearing neurons:** `cell_sub_class` = "auditory" (387 in the model).
- **vpoEN:** `hemibrain_type` = "vpoEN" (4). **vpoDN:** `hemibrain_type` = "vpoDN" (2).
- **Controls:** the antennal touch set used by the lab (`meta.json` `actions.antenna`), with any neuron also in the hearing set removed; and the lab's sugar set (`presets.sugar_paper21`).

## Method

The paper's path score rule, unchanged: place 1 on every source neuron, multiply by the signed connection matrix and clip negatives to zero at each step. For every neuron outside the source set, the score after k steps is the sum of what has arrived over steps 1 to k. Each neuron gets a percentile rank among all non-source neurons (ties share the average rank).

## Tests and rules

- **L1, the map carries the song to the acceptance neurons.** Supported if the mean percentile of the 4 vpoEN neurons at k = 3 and the mean percentile of the 2 vpoDN neurons at k = 4 are both at or above 90. Not supported if either is below 50. Otherwise inconclusive.
- **L2, the route is specific to hearing.** Supported if both percentiles in L1 are higher from the hearing neurons than from each of the two control sets. Not supported if either control gives a higher percentile for both targets. Otherwise inconclusive.

Reported but not used for a verdict: the first step at which anything positive arrives at each target, the percentiles at k one lower and one higher, and the raw values.

## Limits, stated in advance

One fly. Percentile rank among all neurons is our choice of yardstick. The hearing set is every neuron the map labels auditory, switched on together, which is not what a song does. A route on the map says nothing about timing or tuning. No new simulation is run in this plan; the simulation side rests on the exploratory runs and the prior work above, and has not been repeated in the reference implementation (Brian2).

## Amendment A: repeat the simulation in the reference implementation (added 10 October 2026, after L1 and L2 were scored, before any Brian2 song run)

Agrim wants the courtship result in the video, so the simulation side has to stand on the authors' own code, not only on our browser engine and another project's report.

**Runs:** Shiu et al.'s Brian2 model, unmodified (commit `91bdd1e`), FlyWire v783, published parameters, 30 one-second trials per condition at 100 Hz (`code/run_song_sim.py`, sets in `inputs/song_sets.json`, built from the annotation table by the rules above):
1. **Song:** the 387 hearing neurons on.
2. **vpoEN:** the 4 vpoEN neurons on.
3. **pC1:** the 10 pC1 neurons on.

**Rules.**
- **C1, the acceptance neurons stay silent under song:** confirmed if the mean vpoDN rate under condition 1 is below 1 Hz; not confirmed if it is 5 Hz or more; otherwise inconclusive.
- **C2, the last link works:** confirmed if the mean vpoDN rate under condition 2 is 5 Hz or more; not confirmed if below 1 Hz; otherwise inconclusive.
- Condition 3 is reported without a rule.

**Already known:** the browser-engine values listed at the top (vpoDN 0 Hz under song; about 35 Hz with vpoEN on at 100 Hz; about 105 Hz with pC1 on at 150 Hz), and opifor's report. These are confirmations of expected values, not open tests.

