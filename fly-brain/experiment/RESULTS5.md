# Results 5: does the wiring map carry a male's song to the female's "yes" neurons?

**Status:** our own analysis, not peer-reviewed. Pre-specified in `PLAN5.md` (commit `3a7ca53`, 10 October 2026, before the scores were computed). Numbers: `results/plan5/song.json` (`code/run_song.py`). The map-only numbers were re-computed by a separate automated run with its own code (`AUDIT5.md`, 10 October 2026): every number matched. Not cleared for publication until C1 is scored.

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

## Amendment A: the simulation in the authors' own code (Brian2)

Rules fixed in `PLAN5.md` (commit `d047d48`) after L1 and L2 were scored and before these runs. FlyWire v783, published parameters, 30 one-second trials at 100 Hz. Numbers: `results/plan5/sim_vpoEN.json`, `sim_pC1.json` (cloud batch `plan5-song-brian2-b`).

| | Statement | Result | Verdict |
|---|---|---|---|
| **C1** | The acceptance neurons stay silent under song | 26 of the 30 trials are done (11 October): vpoDN and vpoEN fired no spike in any of them (`results/plan5/sim_song_summary.json`). Four trials (seeds 510000, 510006, 510018, 510024) are missing: they were cut off by time limits we set too short, not by anything seen in the model. The 30-trial mean is below 1 Hz unless those four average 7.5 Hz or more | **Not yet scored** (26 of 30, all silent) |
| **C2** | The last link works | With the 4 vpoEN neurons on, vpoDN fires at 36.2 Hz on average, in 30 of 30 trials (bar: 5 Hz) | **Confirmed** |

- With the 10 pC1 neurons on at 100 Hz, vpoDN fires at 81.7 Hz and vpoEN stays at 0 Hz (no rule set).
- Our browser engine gave 36.3 Hz for the vpoEN condition (10 runs), so the two implementations agree there.
- For song, what we have is the browser engine (vpoEN and vpoDN at 0 Hz with the hearing neurons at 40 to 200 Hz, 10 runs per setting, `playground/README.md`) and opifor's report. Neither is the reference implementation.

## Limits

One fly. Percentile rank is our yardstick. One connection rule. No new simulation; the simulation side has not been repeated in Brian2. The percentiles fall as more steps are added (vpoEN: 62, 84, 61, 44, 31 for one to five steps), so the choice of step matters; the rule fixed three and four in advance.

## Corrections and additions after the audit (`AUDIT5.md`, 10 October 2026)

- **"Unrelated senses" was wrong.** All 145 neurons of the touch comparison set are Johnston's-organ neurons (78 wind and gravity, 60 grooming, 7 unlabelled), the same antennal organ as the hearing set. The comparison is with neighbouring senses of that organ and with sugar taste.
- **Ties.** From the hearing neurons, 52% of other neurons have received nothing after three steps and 41% after four. One of the four vpoEN neurons receives nothing at any step up to five. The sugar comparison for vpoDN (59th against 55th percentile) reverses if ties are counted strictly; the touch comparison does not (touch is higher on 6 of 6 target neurons).
- **The direct hearing-to-vpoEN connection is a single synapse.**
- **Plan errata.** `PLAN5.md` says the lab's exploratory runs covered 20 to 200 Hz; the script runs 40 to 200 Hz (the 20 Hz figure is from the website fact-checker's own extra run). The plan does not write out the pC1 rule; it is cell types pC1a to pC1e (10 neurons).
- **opifor's result is not the same test as ours.** It used a synthesised song through its own auditory front end in an independent reimplementation, and its README (scope note dated 2026-09-16) narrows every hearing result to "a stress test of this front end, not a measurement of the female's hearing".
- **The plan-to-result margin is short** (plan committed 16:37:30, results 16:38:24), so the git record alone cannot exclude an earlier uncommitted run. There was none: the script was written after the plan commit.
- **Browser runs now have a saved output:** `playground/build/validation/courtship_explore.log`.

## How the song runs went (10 and 11 October)

Honest record, because it cost more than planned. Attempt 1: four workers per machine, out of memory within a minute. Attempt 2: two workers; the vpoEN and pC1 conditions finished, the song condition ran out of memory after 13 minutes. Fix: one process per trial and shards (commit `e6a8253`). Attempt 3 (11 October): three shards of ten; two finished (20 trials), one hung and was cancelled at 31 minutes. Attempt 4: its ten trials as two shards of five; one finished (5 trials), one hit a 30-minute limit. Attempt 5: the five remaining trials on one machine each with a 13-minute limit; a fresh machine needs about 12 minutes before its first trial completes, so only one finished. A sixth dispatch for the last four was not approved in time. Spend on these runs: roughly 390,000 credits.

