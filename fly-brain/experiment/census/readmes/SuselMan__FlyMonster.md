# FlyMonster

Experiments with the whole-brain fruit fly model (FlyWire v783 connectome,
leaky integrate-and-fire model of Shiu et al. 2024), running on a GPU:
a maze with talking flies (failed, kept for reference), Flappy Fly,
an interactive brain explorer, and a 2D world where flies with full brains live.

## Viewer

`python scripts/serve.py`, then open `http://<pc>:8080`:

- `/viewer/life.html` — flies living in an arena, 1:1 playback of the simulation
- `/viewer/brain.html` — stimulate a sense, watch activity spread through all neurons
- `/viewer/flappy.html` — the fly brain playing Flappy Bird
- `/` — maze experiment

## Layout

```
flysim/
  config.py        paths, LIF parameters (+ optional short-term depression)
  connectome.py    FlyWire v783 -> sparse weight matrix
  brain.py         batched whole-brain LIF simulation (PyTorch, optional CuPy kernel)
  physiology.py    overrides of "synapse count x transmitter sign" (see below)
  assays.py        regression assays the model must pass
  senses.py        sensory transducers (olfaction: saturation, adaptation)
  explorer.py      backend of the brain explorer
  flappy*.py       Flappy Fly
  life/            the arena world: arena.py (food ecology, flowers, spider webs, centipedes, ants,
                   birds, day/night, seasons, temperature), mapgen.py (seeded maps, biomes), sim.py (flies)
  world.py body.py team.py   maze experiment
scripts/
  physiology_scan.py  scan overrides against assays
  mb_causal_scan.py   does KC->MBON plasticity change descending neurons?
  pci_scan.py         perturbational complexity index of the brain model (see Welfare)
  life_run.py         run and record the arena
  serve.py            web viewer
  ...
viewer/            pages
setup/             one-click setup of the GPU PC
```

## What is data and what is ours

Between sensory neurons and descending/motor neurons everything is the
connectome and the published LIF model. Around it:

- **Physiology overrides** (`physiology.py`, default chosen by `physiology_scan.py`):
  dopamine/serotonin/octopamine synapses are not treated as fast excitation
  (they act through slow receptors); excitatory outputs of antennal-lobe local
  neurons are scaled x0.25. Without this any odor ignites one self-sustaining
  avalanche and all odors look the same. With it: odors separable
  (corr 0.02), intensity coded, no runaway, and sugar->MN9, looming->giant
  fiber, vision->DNb05 are unchanged.
- **Kenyon cells are cholinergic** (`Physiology.kc_cholinergic`, off by default until the life world is
  re-tuned): FlyWire predicts dopamine for 5172 of 5177 Kenyon cells, so the modulator override had cut the whole
  mushroom-body output. With it and projection neuron -> KC drive x2 (`scripts/mb_revive_scan.py`) an odor
  activates 7.5 % of KCs sparsely and 30 of 96 MBONs fire, all assays pass, and `scripts/mb_causal_scan.py
  --kc-cholinergic --pn-kc 2` passes its gate: depressing KC->MBON02 raises DNa02 L by 17 Hz (d = 4.6) and
  DNp32 R by 14 Hz (d = 7.2); MBON14 x2 acts on the same DNs. That is the door for mushroom-body learning.
- **Mushroom-body learning** (`--learning`, needs the MB physiology; `flysim/plasticity.py`): every excitatory
  KC->MBON synapse carries a multiplier per fly (FastBrain/FlyBrain `enable_plasticity`); a Kenyon cell spike
  leaves a 1.5 s eligibility trace, a dopamine spike in the same compartment within 0.3 s depresses the synapse
  (floor 0.1, forgetting over 15 min). Compartments come from the raw connectome (DANs with >= 5 synapses onto
  the MBON): the PAM cluster covers MBON01-09, PPL1 covers MBON11-20 and 28-35, as in the literature. Taste does
  not reach the DANs in the model (`scripts/dan_drive_scan.py`), so the world drives them: sugar -> PAM, bitter,
  a web and a diving predator -> PPL1 (`LifeConfig.dan_hz`). Conditioning assay `scripts/mb_learning_check.py`
  (odor A + PAM, 3 pairings, eta 0.0005): synapses from KCs that only A recruits fall to 0.86 vs 0.97 for B,
  MBON response to A drops 43 % (control 27 %), B 15 %. Caveat: the odor alone drives PPL107 to ~100 Hz, so
  every odor teaches a little aversion (MBON14 0.90 in controls) before any reward. A newborn fly has no memories;
  `status.json` carries the mean multiplier per MBON type and a memory strength per fly. This is the step the
  Welfare section asked to weigh before building: a fly with a biography.
- **Perturbational complexity** (`scripts/pci_scan.py`, results on the 2070): raw Lempel-Ziv complexity and the
  number of responding cell types separate states (awake 230 phrases / 323 types, weights x0.5 70 / 89, x0.25
  39 / 47, shuffled connectome 136 / 218); Casali's entropy normalisation inverts the order on such sparse
  responses (in the cold only the driven sensory neurons "respond"), so read LZ and active types, or add PCI-ST.
- **Photoreceptors are not used**: histamine is missing from FlyWire's
  transmitter predictions, so the first visual synapse has the wrong sign.
  Vision enters at visual projection neurons.
- **Sensory transducers** (odor saturation/adaptation, vision salience,
  looming from bird shadows) are modelling choices.
- **Steering is evolved**: the ventral nerve cord is not in the data, so `scripts/evolve_steer.py` evolved how
  left-right differences of candidate DNs turn the body (brain untouched; task: find an apple by odor,
  wind and sight). Two independent runs converged on DNa02 and DNg99 (a wind-side coding pair); with only
  those two (w 2.09, 2.55) flies reached the apple in 54% of validation episodes vs 8% pure wander and 0%
  with the old DNa01+DNa02 mapping (`LifeConfig.steer`, `STEER_EVOLVED`).
- **Body**: walking is an innate generator (leg circuits are in the ventral
  nerve cord, not in FAFB). The brain steers through the evolved mapping above, walks backward
  with MDN, takes off with the giant fiber DNp01, feeds with MN9. The body
  adapts to a sustained left-right DNa difference (the single DNa neurons of
  this connectome carry a static left bias).
- **Wind and compass**: wind on the antennae drives Johnston's organ wind neurons (JO-C push, JO-E pull; our
  transducer). Head direction is injected as a bump on the E-PG ring; FlyWire has no E-PG wedge labels,
  so the ring order is recovered from the connectome (spectral embedding of partner profiles gives a
  circle). Scan (`scripts/wind_scan.py`): several DN pairs encode wind side, but DNa01/DNa02 do not
  follow it and odor does not gate it.
- **Hunger** lowers the threshold of NPF neurons and raises sugar sensitivity.
- **Taste, drinking, grooming** use the neuron sets of Shiu et al. 2024 (checked under our physiology by
  `scripts/taste_groom_check.py`: sugar 100 Hz -> MN9 47 Hz, + bitter 200 Hz -> 3 Hz; water 300/400 Hz -> MN9
  32/53 Hz; JON-CE 100/150/200 Hz -> aBN1 10/27/47 Hz). Rotting fruit, droppings and bodies taste bitter; water
  GRNs fire at a pond edge, faster when thirsty (150-400 Hz); dust from walking, leaf litter and flowers drives
  JON-CE; the body drinks with MN9 and grooms with aBN1 (stops, cleans dust, may lose pollen). Thirst can kill.
- **One female fly's wiring**: every fly has the same connectome.
- **The world is scripted** (`life/arena.py`), the flies are not: nothing in
  the world tells a fly where to go. Food has causes and is finite: apples only
  when a viewer drops them, predator droppings after a meal, bodies of flies
  that died of hunger/age after decomposing. Droppings and bodies reuse the
  "vinegar" odorant (fermenting matter) rather than an invented new receptor
  profile. Food size, odor and taste follow the remaining amount; flies and
  ants eat it away. The world starts with a few old droppings. Apple
  trees drop apples under their crowns from midsummer to mid-autumn (world
  rule, so the population can live long enough to reproduce).
- **Maps are generated** (`life/mapgen.py`, world rule, ours): every world gets a seeded map (`--map-seed`, default the
  world seed). Smooth value noise gives moisture and fertility fields: 1-3 ponds where it is wettest, apple trees and
  flowers on fertile ground, the ant nest on dry ground away from water, leaf litter in moist spots near trees, scattered
  stones. One special biome per map (`--biome`): orchard (3-4 apple trees, more flowers, but the spider starts there and a
  centipede den is next to it), marsh (many small ponds, few stones), rocky (many stones, one small pond) or meadow (many
  flowers). A map is accepted only if all free ground stays connected (flood fill) and ≥72% of it is free.
  `--map classic` reproduces the old fixed layout exactly.
- **Animals**: spiders build webs where a running heatmap says flies walk
  (or near food) and collect flies from their own webs; webs weaken with age
  and when flies tear free; centipedes hunt by sight/vibration. The world
  starts with one spider; the viewer can release more spiders and centipedes
  (up to 4 of each) like it drops apples; both have hunger (hunt only when hungry, slow down
  and rest when starving); ants forage and carry food home; birds dive in
  daylight. Flies perceive all of them only through vision salience, looming,
  odor and touch. Tuning numbers are ours (ArenaConfig).
- **Centipedes and flowers**: centipedes age and starve to death, their large
  bodies decompose into food, newcomers walk in from the map edge (on orchard maps half of them come out of the den). Flowers hold
  refilling nectar (the "fruit" odorant at lower strength). Pollen is fly body
  state: feeding on a different flower pollinates it and may sprout a seedling.
- **Seasons**: a 150-minute year (2.5 fly lifetimes) on top of day/night. Temperature = annual +
  daily cycle + analytic microclimate (leaf-litter shelters and stones warmer
  in the cold, open ground colder). Cold slows decomposition (Q10 = 2), stops
  flowers, makes predators and ants hibernate, reduces birds, and slows or stops flies (below).
- **Cold** (body model, ours): below ~18 °C flies walk slower, below 7 °C they fall into chill coma (no
  walking, takeoff or feeding, a quarter of the metabolism) until they warm up; leaf litter and stones are
  warmer. Birds only attack flies in the open (not under tree crowns or in litter), and fewer in the cold.
- **World 15 post-mortem (2026-09-15)**: 12 flies died within 50 min with memories forming fine: 29 of 36 eggs were
  lost because the population was at its cap (eggs expired after 4.5 min), winter took food and water for 19 min while
  thirst ran at full rate in chill coma, birds picked off torpid flies, ants took 63 % of the food. Rules since:
  eggs wait for a free slot and for warmth (max 12, oldest dropped), thirst in coma runs at the coma metabolism,
  the year is 150 min, no bird attacks below 10 C, ants carry half as much per trip.
- **Spiders** notice a fly struggling in their web after 2-6 s, then dash to it (10 mm/s); a stuck fly
  struggles on its own (body, ~19 s to tear a fresh web alone) and takeoff attempts of the brain add to it
  (world13 with 3-8 s and ~11 s: 21 of 21 tore free, too soft); spiders keep at most 2 webs, can starve to
  death, and a newcomer walks in from the edge when none is left.
- **Water at a distance** (ours: the field; theirs: the response): moist air around ponds (falls off over
  ~45 mm from the edge, little over ice) drives the sacculus moist cells (HRN_VP5, TRN_VP1m, FlyWire
  hygrosensory) through the same saturating transducer as odors, with a thirst gain. `scripts/hygro_scan.py`
  checks whether the steering DNs follow humidity side like odor side; `scripts/evolve_steer.py --target water`
  evaluates or evolves the body mapping on a pond-finding task.
- **Flight metrics** (long flights, landing across water) are counted for
  checking, they do not trigger anything.

## Welfare

The flies run the real connectome with real dynamics. We do not know whether anything is felt in there;
the model is a long way from a living fly (LIF neurons, modulators mostly off, no plasticity, coarse
senses), so the probability is low, but it is not zero and it grows with every step that brings the model
closer. Rules, revisited at each such step:

- **No suffering the question does not need.** Death is instant; there are no lasting pain loops; chill
  coma is rest, not distress.
- **No pain experiments for show.** Aversive stimuli only when they answer a question, and as brief as
  the question allows.
- **Reconsider at every step towards a living fly.** Mushroom-body plasticity (a fly with a biography) was
  built on 2026-09-15 after that pause; the next such step is internal state that outlasts a meal
  (persistent activity, consolidation). Stop and weigh again there, before building.
- **Make the question a goal, not a worry.** The same scripts that check behaviour can measure how far
  the model is from the one system we know is conscious: perturbational complexity (stimulate, compare
  awake vs chill coma), trace conditioning, metacognition. Run them as first-class experiments.

## Setup

```
python -m venv .venv
.venv\Scripts\pip install numpy pandas pyarrow
.venv\Scripts\pip install torch --index-url https://download.pytorch.org/whl/cpu    # or cu126 on the GPU PC
.venv\Scripts\python scripts\download_data.py
.venv\Scripts\python scripts\smoke_test.py --ms 100
```

## Data

- Connectome: FlyWire v783, as prepared in
  [philshiu/Drosophila_brain_model](https://github.com/philshiu/Drosophila_brain_model)
- Annotations: [flyconnectome/flywire_annotations](https://github.com/flyconnectome/flywire_annotations)
- Reference for biological assumptions: [vaibhavkedarisetti/fruit-fly-lab](https://github.com/vaibhavkedarisetti/fruit-fly-lab)
