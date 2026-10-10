# Audit 5: the courtship beat and Supplementary Note 2

**Audited:** `paper/courtship_note_draft.md` (A, video beat; B, Supplementary Note 2).
**Date:** 10 October 2026. **Auditor:** independent, read-only. Nothing in the project was changed except this file.
**What was run:** my own re-computation of the map-only scores (new code, written without `run_song.py`; one core, no simulation), and a re-computation of the simulation summaries from the per-trial counts in the two JSON files. No Brian2 run, no browser-engine run, no network.
**What was not checked:** the browser-engine numbers were not re-run (see item 22); the Wang et al. paper body was not read (abstract only, as saved); the opifor repository's code and records were not read (saved README only); the README copy carries no commit id, so I cannot tie it to the cited commit `0d22f65`.

## Overall verdict

Every number in the draft that can be recomputed reproduces exactly. The problems are in the wording, not the arithmetic:

1. **The beat's third line and the note's "confirms" rest on an unfinished result.** The reference-implementation song run (C1) has not completed. What exists is an exploratory browser-engine table with no saved run output, and another project's sentence that its own authors have since narrowed.
2. **The beat implies a cause the evidence does not support** (no rhythm, therefore silence). The note itself says "We make no claim about why the first link fails".
3. **The "touch" control is not an unrelated sense.** All 145 control neurons are Johnston's-organ neurons, the same organ as the 387 hearing neurons.
4. **opifor's README narrows its own hearing results** to "a stress test of this front end, not a measurement of the female's hearing". The draft quotes the headline sentence without that.
5. **The "route" from hearing to vpoEN is one connection of one synapse.** The draft does not say so.

Recommendation: the beat should not be recorded as drafted. Either hold it until C1 is scored, or use the narrowed wording in "Required changes".

## Verdict table

### Pre-specification and records

| # | Claim (draft wording) | Source checked | Verdict | Fix |
|---|---|---|---|---|
| 1 | "The plan was committed before these scores were computed (`PLAN5.md`, commit `3a7ca53`)" | `git log`: `3a7ca53` 16:37:30, results `5053535` 16:38:24. File creation times: `PLAN5.md` 16:37:30, `code/run_song.py` 16:37:50, `results/plan5/song.json` 16:37:54 | PASS, with a note | The order holds. The margin is 20 seconds between the plan commit and the script file, and 24 seconds to the result file. Git cannot rule out an earlier uncommitted trial run; I found no trace of one. The plan itself declares that the set sizes and the simulation outcome were already known. No change needed. |
| 2 | "rules fixed in an amendment (commit `d047d48`) after L1 and L2 were scored" | `d047d48` 16:42:49, after `5053535` (16:38:24); `sim_vpoEN.json` and `sim_pC1.json` created 17:07:24, committed in `7d3c23c` 17:07:54 | PASS | None. |
| 3 | "**C2 confirmed**" presented as a test | Amendment A: "Already known: the browser-engine values ... about 35 Hz with vpoEN on at 100 Hz ... These are confirmations of expected values, not open tests." | NEEDS CHANGE | Add after the C2 rule: "The expected value was already known from our browser runs (about 35 Hz), so C2 is a repeat in the reference implementation, not an open test." |
| 4 | "30 one-second trials at 100 Hz" | `run_song_sim.py`: `N_TRIALS = 30`, `r_poi = 100 Hz`, `t_run = 1000 ms`; both JSON files have 30 trials, 30 distinct seeds | PASS | The JSON files carry no commit id or batch id; the link to cloud batch `plan5-song-brian2-b` is only stated in `RESULTS5.md`. Not a draft error. |
| 5 | "10 pC1" taken "from the FlyWire annotation table" | 10 neurons with `hemibrain_type` pC1a to pC1e (2 each); `inputs/song_sets.json` matches my own selection exactly for all four sets | PASS, with a note | The pC1 selection rule is not written in `PLAN5.md` (the amendment says "by the rules above", and no pC1 rule is above). State it in the note: "10 pC1 (types pC1a to pC1e)". |

### Map-only numbers (all recomputed independently)

| # | Claim | Draft | Recomputed | Verdict | Fix |
|---|---|---|---|---|---|
| 6 | Hearing neurons | 387 | 387 | PASS | |
| 7 | vpoEN, vpoDN | 4, 2 | 4, 2 | PASS | |
| 8 | Touch control, sugar control | 145, 20 | 145 (0 overlap with hearing removed), 20 | PASS | See item 16 for what the 145 are. |
| 9 | "one hearing neuron connects directly to a vpoEN neuron" | 1 | 1 connection, **1 synapse** | NEEDS CHANGE | "one hearing neuron connects directly to a vpoEN neuron, through a single synapse". |
| 10 | "8 connections (169 synapses, excitatory)" | 8, 169, excitatory | 8 connections, 169 synapses, all 8 with positive sign | PASS | |
| 11 | vpoEN from hearing at three steps | 61st | 61.21 | PASS | |
| 12 | vpoDN from hearing at four steps | 55th | 55.06 | PASS | |
| 13 | Touch: "83rd and 84th" | 83, 84 | 83.45, 84.25 | PASS | |
| 14 | Sugar: "77th and 59th" | 77, 59 | 76.65, 59.10 | PASS | The 59 depends on how ties are ranked; see robustness (c). |
| 15 | "vpoEN: 62, 84, 61, 44 and 31 for one to five steps" | as stated | 62.08, 84.40, 61.21, 44.48, 31.31 | PASS (numbers) / NEEDS CHANGE (wording) | "it falls as steps are added" is not what the series does: it rises from 62 to 84, then falls. Replace with: "it depends on the number of steps (vpoEN: 62, 84, 61, 44 and 31 for one to five steps; vpoDN: 50, 69, 77, 55 and 38)". |
| 16 | L1 inconclusive, L2 not supported | | Same verdicts under the plan's rules | PASS | |

### Wording about the map

| # | Claim | Source checked | Verdict | Fix |
|---|---|---|---|---|
| 17 | "the hearing neurons are not wired to the acceptance neurons more strongly than **unrelated senses** are" | The 145 "touch" neurons (`meta.json` `actions.antenna`) are all Johnston's-organ neurons: 78 annotated `wind_gravity`, 60 `grooming`, 7 with no sub-class (types JO-C, JO-D, JO-E, JO-F, JO-mz). The hearing set is also Johnston's organ (JO-A, JO-B and others) | **FAIL** | "... not ranked higher from the hearing neurons than from two comparison sets: the wind- and touch-sensing neurons of the same antennal organ, and the sugar-taste neurons." Do not call the antennal set unrelated. |
| 18 | "145 antennal touch neurons" | as above | NEEDS CHANGE | "145 antennal wind, gravity and touch neurons (Johnston's organ, the set used for the antennal-grooming test)". |
| 19 | "A route exists ... It is weak and not specific." | Recomputed: one of the four vpoEN neurons receives exactly zero from the hearing set at every step up to five; the direct link is one synapse | PASS, with the fix in item 9 | |
| 20 | Title: "does a male's **song** reach the female's acceptance neurons?" | The input is all 387 auditory-labelled neurons switched on together | NEEDS CHANGE | "A courtship check: does switching on the hearing neurons reach the female's acceptance neurons?" |

### Simulation

| # | Claim | Source checked | Verdict | Fix |
|---|---|---|---|---|
| 21 | "With the vpoEN neurons on, vpoDN fires at 36.2 Hz, in 30 of 30 trials"; "with the pC1 neurons on, at 81.7 Hz" | Recomputed from per-trial counts: 36.18 Hz (the two neurons: 47.3 and 25.1 Hz; trial means 29.5 to 41.0), 30 of 30 trials; pC1: 81.65 Hz (91.8 and 71.5), 30 of 30 | PASS | Optional: say the pC1 run was also at 100 Hz, since the browser figure in the README (105 Hz) is at 150 Hz. |
| 22 | "vpoEN and vpoDN stayed at 0 Hz in our browser implementation of the model (10 runs at each of five rates from 40 to 200 Hz; exploratory)" | `explore_courtship.mjs`: `n = 10`, rates `[40, 80, 120, 160, 200]`. `playground/README.md` table: "Hearing neurons at 40 to 200 Hz: 0 Hz, 0 Hz, 0 Hz" | PASS on consistency / **not verifiable as a record** | The script only prints to the console. No output file or log of this run exists in the project; the README table is the only record. Under "every journey claim must be backed by our own records", save the script's output to a result file and commit it before this number is published. Also: `PLAN5.md` says "20 to 200 Hz"; the script has no 20 Hz setting. The draft's "40 to 200" is the correct one. |
| 23 | "**C1 is not yet scored**" | No `sim_song.json` exists | PASS | Keep. |
| 24 | "The simulation side of this note confirms that." | C1 is unscored. The only song-condition runs are the exploratory browser runs. opifor used a synthesised song through its own auditory front end in its own reimplementation; ours is every auditory neuron at one rate. These are different inputs | **FAIL** | "Our exploratory browser runs point the same way; the run in the reference implementation has not completed, so this note does not yet confirm it." |

### Source claims

| # | Claim | Source checked | Verdict | Fix |
|---|---|---|---|---|
| 25 | "A female fly signals her willingness to mate by opening her vaginal plates" | Abstract, verbatim | PASS | |
| 26 | "in response to the male's courtship song" | Abstract: "occurs in response to the male courtship song and is dependent on the mating status of the female" | PASS | The second half is dropped; acceptable because pC1 and mating status are named in the next sentence. |
| 27 | "controlled by a pair of female-specific descending neurons (vpoDN)" | Abstract: "VPO is controlled by a pair of female-specific descending neurons (vpoDNs)" | PASS | |
| 28 | "receive excitatory input from auditory neurons tuned to specific features of the song (vpoEN)" | Abstract: "receive excitatory input from auditory neurons (vpoENs), which are tuned to specific features of the D. melanogaster song" | PASS | |
| 29 | "pC1 neurons, which encode her mating status" | Abstract: "pC1 neurons, which encode the mating status of the female" | PASS | |
| 30 | opifor quote: "courtship song entering the female's ear does not reach vpoDN" | README lines 23 to 24, verbatim (across a line break) | PASS | |
| 31 | "from pre-registered runs at the published parameters" | README: "Every experiment here is pre-registered before any simulation runs"; "What has held so far, at Shiu's parameters: ... What has not held: courtship song ..." | PASS on the words / NEEDS CHANGE on what is left out | Three things the same README says and the draft omits: (a) the simulator is "an independent reimplementation" of the model, not the authors' code; (b) the song was synthesised and passed through an auditory front end, so it is not our "all hearing neurons on"; (c) a scope note dated 2026-09-16: "Every hearing result recorded so far ... is therefore a stress test of this front end, not a measurement of the female's hearing. The records stand as run; their claims are narrowed to that." Quoting the headline without (c) misstates the project's current position. Replacement in "Required changes". |
| 32 | Reference [28] cites commit `0d22f65` | The saved README has no commit id; `census/frame.csv` records only the URL | NOT VERIFIABLE | Confirm the saved copy is from that commit, or cite the date the README was saved. |
| 33 | "In the model a song is the hearing neurons firing at a steady rate with no temporal structure" | `model.py` `poi()`: each stimulated neuron gets `PoissonInput(N=1, rate=r_poi, weight=w_syn*f_poi)` and its refractory period set to zero. One constant rate for all of them, random timing. The published code has no time-varying input and nothing called a song | NEEDS CHANGE | "Steady" suggests regular firing; the input is random. And "in the model a song is" suggests the model defines a song; it does not. Replace with: "In our runs the stand-in for a song is every hearing neuron receiving random input at one constant average rate (the model's standard stimulation), with no pulse rhythm or pitch." |
| 34 | Reference 32: "Wang K, Wang F, Forknall N et al. (2021). Neural circuit mechanisms of sexual receptivity in Drosophila females. *Nature* 589, 577–581. https://doi.org/10.1038/s41586-020-2972-7" | Crossref JSON: authors Wang Kaiyu, Wang Fei, Forknall Nora (then Yang, Patrick, Parekh, Dickson); title identical; Nature; volume 589; page 577-581; print date 28 Jan 2021; DOI identical | PASS | The number 32 is free in v1.5 (31 references). Note that `draft_v3.md` used 32 for Rubin et al.; make sure the note is merged into v1.5 numbering. |
| 35 | "The path-score rule of Section 2.2" | v1.5 Section 2.2, P2: signed matrix, clip negatives, sum over steps | PASS | The existing note in v1.5 is titled "Supplementary Note"; it becomes Note 1. |
| 36 | "We found no map-only score in that project's README; we did not read its code or records." | README searched: no map-only score | PASS | Keep. It makes no novelty claim, which is right given the code was not read. |

### Video beat (A), sentence by sentence

| # | Sentence | Verdict | Reason and fix |
|---|---|---|---|
| A1 | "We tried one more thing. In a real fly, a female answers a male's courtship song by opening her vaginal plates. That is how she says yes. [S44]" | PASS | Matches the abstract ("signals her willingness to mate by opening her vaginal plates"; "occurs in response to the male courtship song"). |
| A2 | "The pair of neurons that gives that command is in the map, and in the model it works: switch on the song-tuned neurons that feed it, and it fires. [E11]" | PASS, with tag fixes | True: two neurons annotated vpoDN (type DNp37, marked female-specific, one per side); 36.2 Hz in 30 of 30 Brian2 trials. "Is in the map" rests on the FlyWire annotation table, which needs its own source tag. `E11` is not defined in `research-bible.md`. Safer: "... and in the model that last step works: switch on the four song-tuned neurons that feed it, and it fires." |
| A3 | "But switch on her hearing neurons, which is the only way this model can "play" a song, and nothing arrives. [E12, S45]" | **FAIL as drafted** | (i) Not adequately supported without C1. The support is an exploratory browser run with no saved output, plus a README sentence its authors narrowed. The project rule is that an uncertain result is described as unfinished, not as a finding. (ii) "the only way this model can play a song" is too strong: opifor fed a synthesised song through a front end into the same kind of model. It is the only way the published code stimulates neurons. (iii) "nothing arrives" contradicts the note, where the map score does arrive (a route exists). What stayed silent is the spiking output of vpoEN and vpoDN. (iv) `E12` and `S45` are not defined anywhere I could find. Safe wording below. |
| A4 | "In the model a song is just "hearing neurons on", with no rhythm. In the real fly, those song-tuned neurons respond to specific features of his song. [S2, S44]" | NEEDS CHANGE | Second sentence: PASS (abstract). First sentence: true of our input, but [S2] (the Shiu paper) is the wrong source; the source is the code (`model.py`). Say "our stand-in for a song", not "in the model a song is". |
| A5 | "The wiring for yes is there. The tune is not something this model can hear." | **FAIL (implied causation)** | Placed after A4, this tells the viewer the silence is caused by the missing rhythm. Nothing tests that. The note says "We make no claim about why the first link fails", and the map result points at least as much to thin wiring from the hearing set (one synapse) as to rhythm. opifor's README also notes a relay known to be "graded and largely electrical, which a spike-only chemical model cannot represent". Also "the wiring for yes" is shown only for the last link. Safe wording below. |
| A6 | On-screen credit: "First reported by opifor, femaleflybrain (GitHub)" | NEEDS CHANGE | "First" is a priority claim nobody checked (the plan itself names a second project, flypair, reading vpoDN). And what opifor reported was a different input, since narrowed. Use: "Reported earlier, with a synthesised song, by opifor: femaleflybrain (GitHub)". |

## Recomputed numbers

Own code, inputs as specified. Model network: 138,639 neurons, 15,091,983 connections, no duplicate pairs. Percentile = 100 x average rank / number of non-source neurons.

**Set sizes:** hearing 387, vpoEN 4, vpoDN 2, touch control 145 (overlap with hearing: 0), sugar control 20. No target neuron is in any source set.

**Direct connections:** hearing to vpoEN: 1 connection, 1 synapse, excitatory. vpoEN to vpoDN: 8 connections, 169 synapses, all excitatory (55, 41, 33, 22, 8, 6, 2, 2). Touch to vpoEN: 0. Sugar to vpoEN: 0.

**Mean percentile by number of steps (k):**

| Source | Target | k=1 | k=2 | k=3 | k=4 | k=5 |
|---|---|---|---|---|---|---|
| Hearing (387) | vpoEN | 62.08 | 84.40 | **61.21** | 44.48 | 31.31 |
| Hearing (387) | vpoDN | 49.65 | 68.72 | 76.66 | **55.06** | 38.23 |
| Touch (145) | vpoEN | 49.58 | 98.96 | **83.45** | 61.47 | 42.65 |
| Touch (145) | vpoDN | 49.58 | 67.55 | 97.12 | **84.25** | 55.38 |
| Sugar (20) | vpoEN | 49.90 | 47.35 | **76.65** | 60.85 | 44.79 |
| Sugar (20) | vpoDN | 49.90 | 71.82 | 66.49 | **59.10** | 53.23 |

Bold cells are the ones the plan's rules use. All six agree with `song.json` and with the draft to the reported precision. The vpoEN series 62, 84, 61, 44, 31 matches.

**Raw arrival from hearing:** vpoEN 0, 98, 922, 1,835 (unchanged from step two onward); vpoDN 51 and 14,021 (unchanged from step three onward). Matches `RESULTS5.md`.

**Simulation (from per-trial counts):** vpoEN on: vpoDN 36.18 Hz, 30 of 30 trials with a spike (both neurons spike in all 30). pC1 on: vpoDN 81.65 Hz, 30 of 30; vpoEN 0 Hz in 30 of 30.

**Discrepancies with the draft's numbers: none.**

## Robustness the authors did not report

**(a) Per target neuron, hearing against the antennal set.** L2's failure survives. The antennal set gives a higher percentile than the hearing set for every one of the six target neurons:

| Target neuron | Hearing | Touch (antennal) | Sugar |
|---|---|---|---|
| vpoEN 1, k=3 | 26.00 | 71.17 | 91.32 |
| vpoEN 2, k=3 | 64.08 | 77.57 | 88.07 |
| vpoEN 3, k=3 | 75.42 | 99.72 | 37.61 |
| vpoEN 4, k=3 | 79.33 | 85.33 | 89.62 |
| vpoDN 1, k=4 | 46.98 | 71.18 | 26.87 |
| vpoDN 2, k=4 | 63.15 | 97.31 | 91.33 |

Touch beats hearing on 6 of 6. Sugar beats hearing on 4 of 6 (3 of 4 vpoEN, 1 of 2 vpoDN). The raw arrival per source neuron points the same way (vpoEN at k=3: hearing 1.8, touch 1,916, sugar 24). The touch comparison is carried largely by one vpoEN neuron (raw value 1,107,937) but does not depend on it: the other three are also higher.

Caveat that matters for the wording: all 145 "touch" neurons are Johnston's-organ neurons, so this comparison is within one organ. Sugar is the only unrelated sense tested, and its result is mixed per neuron.

**(b) Median instead of mean.**

| | Hearing | Touch | Sugar |
|---|---|---|---|
| vpoEN, k=3, median of 4 | 69.75 | 81.45 | 88.84 |
| vpoDN, k=4 (median of 2 = mean) | 55.06 | 84.25 | 59.10 |

L1 stays inconclusive (between 50 and 90). L2 stays not supported.

**(c) Ties at zero.** A large share of non-source neurons have received exactly nothing, and they all share one average rank:

| Source | Zero at k=3 | Zero at k=4 |
|---|---|---|
| Hearing | 52.00% | 40.98% |
| Touch | 54.17% | 41.47% |
| Sugar | 75.23% | 53.73% |

Consequences:
- One vpoEN neuron receives zero from the hearing set at every step up to five. Its "26th percentile" at k=3 is only the midpoint of the tied block. Counting only neurons strictly below, the hearing vpoEN mean at k=3 is 54.7, not 61.2. L1 is still inconclusive.
- The hearing value of 62 at k=1 is one single-synapse connection plus tied zeros (three neurons at 49.65, one at 99.36).
- **The sugar-to-vpoDN figure of 59 is tie-dependent.** One of the two vpoDN neurons receives zero from sugar. With average ranks sugar gives 59.10 against hearing's 55.06; counting strictly-below, sugar gives 45.66 against 55.06, and the order flips. With "at or below" it is 72.53 against 55.07. The plan fixed average ranks in advance, so the reported number is the right one, but "sugar reaches vpoDN more" should not be leaned on.
- The touch result does not depend on ties (83.4 and 84.2 under strict counting).

L2's verdict needs only one control to beat hearing on both targets; touch does so under every variant I tried.

## Overclaims, tone and the word "song"

- **Overclaims:** items 17, 24, A3, A5, A6 above. Also "the last link of the published circuit works in the model" is fine, but "The wiring for yes is there" (A5) stretches one link into the whole circuit.
- **Tone toward opifor:** nothing reads as a takedown. The risk runs the other way: the draft uses their sentence as support while leaving out their own scope note. Being generous here means quoting the narrowed claim. The on-screen "First reported by" is kind but unverified.
- **Tone toward the model:** "The tune is not something this model can hear" is acceptable in tone; the problem is the causal implication, not the framing.
- **"Song" used for "all auditory-labelled neurons on":** the note's title; A3 ("play a song"); A4 and the Reading ("In the model a song is ..."). The 387 neurons include 20 typed JO-unclear, 17 JO-CA1/CA2, 8 JO-mz and 1 JO-FV alongside JO-A and JO-B, so "hearing neurons" should be introduced once as "every neuron the map labels auditory". The Limits paragraph already says this; the title and the beat should match it.
- **Undefined tags:** `S45`, `E11`, `E12` are not in `research-bible.md` or `sources/README.md`. `S44` is defined. `[S2]` on A4 points to the Shiu paper, which is not the source for that sentence.

## Required changes

1. **Beat line 3 (A3).** Do not record as drafted. Preferred: hold the beat until C1 is scored in Brian2. If it must go earlier, use: "But when we switched on every hearing neuron in her brain, in our browser version of the model, those neurons stayed silent." On screen: "Browser version of the model; exploratory. Run in the authors' code not finished." If that label is not acceptable on screen, the line fails the "publish only what we are certain of" rule and should be cut.
2. **Beat lines 4 and 5 (A4, A5).** Replace with: "Our stand-in for a song was crude: every hearing neuron on at once, with no rhythm. In a real fly, those song-tuned neurons respond to specific features of his song. So the last step of yes is in the wiring. How a song gets that far, this simple model doesn't show us, and we don't yet know why."
3. **On-screen credit (A6).** "Reported earlier, with a synthesised song, by opifor: femaleflybrain (GitHub)". Drop "First".
4. **Prior work paragraph.** Replace with: "The femaleflybrain project, an independent reimplementation of the model with pre-registered experiments, reports at the published parameters that "courtship song entering the female's ear does not reach vpoDN" [28]. Its README has since narrowed every hearing result to "a stress test of this front end, not a measurement of the female's hearing", because its auditory front end is uncalibrated. Its input was a synthesised song; ours is every auditory neuron at one rate. Our exploratory browser runs point the same way; our run in the reference implementation has not completed, so we do not yet confirm it."
5. **Reading.** Replace "than unrelated senses are" with "than from two comparison sets: the wind- and touch-sensing neurons of the same antennal organ, and the sugar-taste neurons". Replace the song sentence with item 33's wording. Replace "why the first link fails" with "why vpoEN stayed silent in our exploratory runs".
6. **Method.** "145 antennal wind, gravity and touch neurons (Johnston's organ)". Add the C2 "not an open test" sentence (item 3). Name the pC1 types.
7. **Results.** Add "through a single synapse" to the direct hearing-to-vpoEN connection.
8. **Limits.** Fix "it falls as steps are added" (item 15). Add: "About half of all neurons receive nothing after three steps (52%) and share one rank; one of the four vpoEN neurons is among them. The sugar comparison for vpoDN (59 against 55) reverses under a stricter tie rule; the antennal comparison does not." Add: "The antennal comparison set comes from the same organ as the hearing set."
9. **Title of the note.** "does switching on the hearing neurons reach the female's acceptance neurons?"
10. **Records.** Save the output of `explore_courtship.mjs` to a committed result file before the 0 Hz figure is published. Define `S45`, `E11`, `E12`. Correct "20 to 200 Hz" in `PLAN5.md` by a dated note (do not edit the pre-specified text silently). Confirm the saved opifor README matches commit `0d22f65`.
