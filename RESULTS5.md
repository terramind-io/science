# Results 5: does the wiring map carry a male's song to the female's "yes" neurons?

**Status:** our own analysis, not peer-reviewed. Pre-specified in `PLAN5.md` (commit `3a7ca53`, 10 October 2026, before the scores were computed). Numbers: `results/plan5/song.json` (`code/run_song.py`). Not independently re-computed and not cleared for publication.

## Verdicts

| | Statement | Result | Verdict |
|---|---|---|---|
| **L1** | The map carries the song to the acceptance neurons | vpoEN at the 61st percentile after three steps; vpoDN at the 55th after four (bar: both at or above the 90th) | **Inconclusive** |
| **L2** | The route is specific to hearing | The antennal touch neurons reach both targets more strongly (83rd and 84th percentile); the sugar neurons reach vpoEN more strongly (77th) and vpoDN slightly more (59th) | **Not supported** |

## What the map shows

- FlyWire v783, 387 neurons labelled auditory, 4 vpoEN, 2 vpoDN.
- A route exists. One direct connection runs from a hearing neuron to a vpoEN neuron, so something arrives at vpoEN after one step and at vpoDN after two. The four vpoEN neurons connect to the two vpoDN neurons through 8 connections (169 synapses, excitatory).
- It is thin. What arrives at vpoEN stops growing after step two (0, 98, 922 and 1,835 for the four neurons) and at vpoDN after step three (51 and 14,021). After three steps 66,355 other neurons have received something, and about four in ten of them have received more than vpoEN.
- It is not specific. Starting from the 145 antennal touch neurons, or from the 20 sugar neurons, the same targets rank as high or higher.

## Reading

On this map, read with this rule, the hearing neurons are not wired to the acceptance neurons more strongly than unrelated senses are. This agrees with the simulation staying silent when the hearing neurons are switched on (our exploratory lab runs; and, before us, opifor/femaleflybrain's pre-registered result that "courtship song entering the female's ear does not reach vpoDN"). It does not show the real circuit is absent: Wang et al. (https://doi.org/10.1038/s41586-020-2972-7) found it in real flies. Both the model and our score treat a song as "all hearing neurons on", with no rhythm or pitch.

## Limits

One fly. Percentile rank is our yardstick. One connection rule. No new simulation; the simulation side has not been repeated in Brian2. The percentiles fall as more steps are added (vpoEN: 62, 84, 61, 44, 31 for one to five steps), so the choice of step matters; the rule fixed three and four in advance.
