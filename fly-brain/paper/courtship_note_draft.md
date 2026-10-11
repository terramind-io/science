# Courtship beat and paper note (after the independent audit of 10 October 2026, `experiment/AUDIT5.md`)

Status (11 October): C1 is confirmed. The video beat is in `research-bible.md` §0.1 and the note below is in the paper from version 1.6.

## A. Video beat

> We tried one more thing. In a real fly, a female answers a male's courtship song by opening her vaginal plates. That is how she says yes. [S44]
> The pair of neurons that gives that command is in the map, and in the model it works: switch on the song-tuned neurons that feed it, and it fires. [E11]
> But when we switched on all 387 sound-sensing neurons the map labels, the song-tuned neurons and the yes neurons all stayed silent. [E12]
> Our stand-in for a song was crude: every sound-sensing neuron on at once, with no rhythm. [E13] In a real fly, those song-tuned neurons respond to specific features of his song. [S44]
> So the last step of yes is in the wiring. How a song gets that far, this simple model doesn't show us, and we don't yet know why.

On-screen credit: "Reported earlier, with a synthesised song, by opifor: femaleflybrain (GitHub)".

## B. Paper

## Supplementary Note 2. A courtship check: does switching on the hearing neurons reach the female's acceptance neurons?

**Question.** A female fly signals her willingness to mate by opening her vaginal plates, in response to the male's courtship song. Wang et al. report that this is controlled by a pair of female-specific descending neurons (vpoDN), which receive excitatory input from auditory neurons tuned to specific features of the song (vpoEN) and from pC1 neurons, which encode her mating status [32]. We ask whether the map, and the simulation, carry a signal from the hearing neurons to vpoDN.

**Prior work.** The femaleflybrain project, an independent reimplementation of the model, states from pre-registered runs at the published parameters that "courtship song entering the female's ear does not reach vpoDN" [28]. Its input was a synthesised song passed through its own auditory front end, and its README now describes every hearing result so far as "a stress test of this front end, not a measurement of the female's hearing". Our test is not the same as theirs: we switch every hearing neuron on at one rate. Under that input our runs in the reference implementation agree with the direction of their report. We found no map-only score in that project's README; we did not read its code or records.

**Method.** FlyWire v783. Sets from the FlyWire annotation table: the 387 neurons with sub-class "auditory" (hearing neurons), 4 vpoEN, 2 vpoDN and 10 pC1 (cell types pC1a to pC1e). *Map.* The path-score rule of Section 2.2, started from the hearing neurons; each neuron outside the source set is ranked by what has arrived after k steps, as a percentile among all such neurons. Rule L1: supported if vpoEN (mean of 4) at three steps and vpoDN (mean of 2) at four steps are both at or above the 90th percentile; not supported if either is below the 50th. Rule L2 (specific to hearing): supported if both percentiles are higher than from each of two comparison sets, 145 antennal wind, gravity and touch neurons (Johnston's organ, the same organ as the hearing neurons) and 20 sugar-taste neurons. The plan was committed before these scores were computed (`PLAN5.md`, commit `3a7ca53`). *Simulation.* The model of [1] in Brian 2, 30 one-second trials at 100 Hz, with rules fixed in an amendment (commit `d047d48`) after L1 and L2 were scored: C1, vpoDN below 1 Hz with the hearing neurons on; C2, vpoDN at 5 Hz or more with the vpoEN neurons on.

**Results.** *Map.* A route exists: one hearing neuron connects directly to a vpoEN neuron through a single synapse, and the vpoEN neurons connect to the vpoDN neurons through 8 connections (169 synapses, excitatory). It is weak and not specific. From the hearing neurons, vpoEN is at the 61st percentile after three steps and vpoDN at the 55th after four (**L1 inconclusive**). From the wind, gravity and touch neurons the same targets are at the 83rd and 84th percentiles, and from the sugar neurons at the 77th and 59th (**L2 not supported**). *Simulation.* With the vpoEN neurons on, vpoDN fires at 36.2 Hz, in 30 of 30 trials (**C2 confirmed**; our browser runs had already given about 35 Hz, so this was not an open test); with the pC1 neurons on, at 81.7 Hz. With the hearing neurons on, vpoEN and vpoDN fired no spike in any of the 30 trials (**C1 confirmed**). This too was expected: in our browser implementation of the model both had stayed at 0 Hz with the hearing neurons on (10 runs at each of five rates from 40 to 200 Hz; exploratory).

**Reading.** On this map, read with this rule, the hearing neurons are not wired to the acceptance neurons more strongly than two comparison sets are: the wind- and touch-sensing neurons of the same antennal organ, and the sugar-taste neurons. The last link of the published circuit works in the model. In our runs the stand-in for a song is every hearing neuron receiving random input at one constant average rate (the model's standard stimulation), with no pulse rhythm or pitch; in real flies vpoEN are tuned to specific features of the song [32]. We make no claim about why vpoEN stays silent.

**Limits.** One fly. Percentile rank among all neurons is our yardstick, and it depends on the number of steps (vpoEN: 62, 84, 61, 44 and 31 for one to five steps); the rule fixed three and four in advance. Many neurons tie at zero (52% after three steps and 41% after four, from the hearing neurons), and one of the four vpoEN neurons receives nothing at any step up to five. The touch comparison does not depend on how ties are counted; the sugar comparison for vpoDN (59th against 55th) does. The hearing set is every neuron the map labels auditory, switched on together. The map-only numbers were re-computed by a separate automated run with its own code (`experiment/AUDIT5.md`).

Reference to add: 32. Wang K, Wang F, Forknall N et al. (2021). Neural circuit mechanisms of sexual receptivity in Drosophila females. *Nature* 589, 577–581. https://doi.org/10.1038/s41586-020-2972-7
