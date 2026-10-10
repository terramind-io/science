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
