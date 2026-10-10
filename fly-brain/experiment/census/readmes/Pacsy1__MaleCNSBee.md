# MaleCNS Bee

A Paper plugin that puts a **real fly brain** into a Minecraft bee.

Inside the jar is the complete central nervous system of an adult male *Drosophila melanogaster*, the
FlyEM **MaleCNS v1.0** connectome released by Janelia: **165,733 proofread neurons and 6,239,854
connections** (89.8 million synapses). The plugin runs that wiring diagram as a spiking neural network in
real time on its own thread. What the bee sees, smells, tastes, hears and feels is fed into the fly's
sensory neurons; the fly's descending neurons fly the bee. Nothing about the movement is scripted: the
bee goes where 165,733 simulated neurons send it.

Minecraft **26.2**, Paper. Drop the jar in `plugins/` and you are done. The connectome ships inside it,
nothing is downloaded at runtime.

## Download and verify

Get the jar from [Releases](https://github.com/Pacsy1/MaleCNSBee/releases/latest). Every release also
publishes `SHA256SUMS.txt`, so you can check that the file you have is exactly the file that was
published:

```powershell
# Windows
.\tools\verify.ps1
```

```sh
# Linux / macOS
./tools/verify.sh
```

Both fetch `SHA256SUMS.txt` from the release, hash your jar, print both values and exit non-zero on a
mismatch. By hand, if you prefer:

```powershell
(Get-FileHash .\MaleCNSBee-1.1.1.jar -Algorithm SHA256).Hash
```

```sh
sha256sum -c SHA256SUMS.txt
```

## Quick start

```
/malecns spawn
```

Then watch it. Useful things to try:

| Command | What it does |
| --- | --- |
| `/malecns spawn [x y z [world]]` | Spawn a bee with a brain (works from console too) |
| `/malecns stats` | Firing rates, sensory state, motor commands, busiest descending neurons |
| `/malecns watch` | Live read-out of the nervous system on your action bar |
| `/malecns list` | Every active bee, its position and simulation speed |
| `/malecns stim <cellType>[:L\|:R] [seconds] [Hz]` | Optogenetics: drive any of the 11,751 cell types |
| `/malecns remove [all]` | Remove the nearest bee, or all of them |

Permissions: `malecns.use` (read-only: list, stats, watch, about, top, neuron, pathway, probe; default true),
`malecns.admin` (everything that touches the bee or its brain; default op).

## The lab: testing it

These are the interesting part. Every one of them drives or reads the real connectome.

### Become a stimulus

| Command | What it does |
| --- | --- |
| `/malecns beodor <co2\|floral\|pheromone\|geosmin\|off>` | **You** become an odour source. `co2` is your breath on the fly's ORN_V neurons (the channel it uses to notice animals); `floral` makes you smell like a flower patch; `pheromone` hits cVA/Or47b, the male courtship channels; `geosmin` is mould, which flies avoid. Walk around the bee and watch `/malecns stats`. |
| `/malecns poke [left\|right\|both]` | Mechanical touch: 745 head bristle neurons on that side |
| `/malecns wind <0-1> [s]` | A gust on the Johnston's organ wind/gravity neurons |
| `/malecns sing [s]` | Courtship song played at it (JO-A/JO-B sound neurons) |
| `/malecns taste <sugar\|bitter> [s]` | Sugar or bitter on the labellum |
| `/malecns temp <hot\|cold> [s]` | Thermosensory neurons |

### Show it things (painted into its visual field, through the real optic lobe)

| Command | What it does |
| --- | --- |
| `/malecns loom [speed] [s]` | An object rushing at its face |
| `/malecns grating <deg/s> [s]` | A rotating striped drum, the classic optomotor stimulus |
| `/malecns flash <dark\|light>` | Whole-field flash |
| `/malecns blind [s]` | Blank field: it goes blind for a while |

### Neurons

| Command | What it does |
| --- | --- |
| `/malecns stim <type>[:L\|:R] [s] [Hz]` | Activate a cell type (sufficiency) |
| `/malecns silence <type>[:L\|:R] [s]` | Inactivate a cell type: they integrate inputs but cannot spike (necessity) |
| `/malecns probe <type> [s]` | Record from a cell type: per-second rate, left vs right |
| `/malecns top [n]` | Busiest cell types in the whole CNS right now |
| `/malecns neuron <type>` | Cell-type card: how many, which side, excitatory or inhibitory, synapse counts, strongest input and output partners |
| `/malecns pathway <from> <to>` | How two cell types are wired together: direct synapses and the strongest two-hop routes |
| `/malecns record [s]` | Writes a per-tick CSV of motor commands and descending-neuron rates to `plugins/MaleCNSBee/recordings/` |

### The rig

`/malecns tether` glues the bee in place. Brain and senses keep running, and it still turns on the spot,
like a fly in a flight simulator. Best way to run stimuli without it flying off. `/malecns bring`
teleports it to you without interrupting the simulation.

### Scripted experiments

`/malecns experiment <optomotor | looming | escape-necessity | sugar | song | blind>` runs a timed
sequence and prints the mean and peak firing rates it measured in each phase. Real output from the test
server (tethered bee, Paper 26.2):

```
Experiment: optomotor    Does wide-field motion drive the steering circuit like in a real fly?
  still:                HS left   0.0 Hz    HS right   0.0 Hz
  drum turning right:   HS left 145.5 Hz    HS right  19.3 Hz
  drum turning left:    HS left  19.2 Hz    HS right 124.7 Hz

Experiment: blind        How much of the CNS activity is the eyes?
  seeing a moving scene:  T4+T5 7.0 Hz   HS cells 69.9 Hz   whole CNS 2.4 Hz
  blind:                  T4+T5 0.1 Hz   HS cells  1.5 Hz   whole CNS 1.2 Hz
  seeing again:           T4+T5 6.6 Hz   HS cells 66.7 Hz   whole CNS 2.3 Hz

Experiment: sugar        Does sugar reach the proboscis motor neurons? (Shiu et al.'s test case)
  no sugar:               sugar GRNs  0.0 Hz   MN9 4.0 Hz (peak 30)
  sugar on the labellum:  sugar GRNs 59.1 Hz   MN9 5.8 Hz (peak 60)
```

The optomotor hemisphere swap is not coded anywhere; it falls out of the wiring. Blinding it halves
the activity of the entire central nervous system.

Note for console/RCON users: results that arrive after the command returns (experiments, `probe`,
`neuron`, `pathway`) also go to the server log, since a console sender cannot receive them later.

### Optogenetics worth trying

These all work through the real wiring, not through special cases in the plugin:

```
/malecns stim DNa02:L 3      # left steering descending neuron -> the bee turns left
/malecns stim DNa02:R 3      # ... and right
/malecns stim LPLC2 1        # looming detectors -> Giant Fiber -> escape jump
/malecns stim DNp01 1        # the Giant Fiber itself -> escape
/malecns stim MDN 2          # moonwalker descending neurons -> backs up
/malecns stim pIP10 2        # courtship song command neuron -> the bee sings
/malecns stim LB3a 3         # labellar sugar neurons -> proboscis motor neurons
```

Tab completion suggests cell types; any MaleCNS type name works (`T4a`, `KCg-m`, `EPG`, `ORN_DA1`, ...).

## How it works

### 1. The connectome (`tools/build_brain.py` → `malecns.bin.gz`, 18 MB)

Built from the public FlyEM MaleCNS v1.0 release (`gs://flyem-male-cns/v1.0/connectome-data/flat-connectome/`):

* every neuron with status *Traced* or *Anchor* (165,733 of them);
* every connection of **at least 5 synapses** between two of those neurons (the usual threshold in
  connectomics work): 6.24 M edges, stored as a delta-coded CSR graph;
* each neuron's sign from its predicted neurotransmitter: acetylcholine → excitatory, GABA / glutamate /
  histamine → inhibitory (35 % of neurons), following Shiu et al.;
* a **retinotopic eye map**: the optic lobe's column coordinates (`assignedOlHex1/2`) laid out over the
  fly's field of view, with the axes' orientation regressed from the physical positions of lamina
  somata. Neurons without column coordinates (T4/T5 motion detectors, LC/LPLC projection neurons) get a
  receptive-field direction propagated from their presynaptic partners.

### 2. The simulation (`brain/Brain.java`)

A leaky integrate-and-fire model of the whole CNS, following
[Shiu et al. 2024, *Nature*](https://www.nature.com/articles/s41586-024-07763-9) (the whole-brain model
built for the female FlyWire brain), with their parameters: resting −52 mV, threshold −45 mV,
τ_membrane 20 ms, τ_synapse 5 ms, 2.2 ms refractory, 1.8 ms axonal delay, **0.275 mV per synapse**, 1 ms
time step, Poisson-driven sensory neurons.

Two things had to be added that are not in that paper. With the *whole* CNS (brain **and** ventral nerve
cord) and a complete compound eye pushing input in continuously, the pure model ignites into brain-wide
saturated firing, with every neuron at hundreds of Hz. Two standard properties of real neurons tame it:

* **short-term synaptic depression** (Tsodyks–Markram, per presynaptic neuron: 30 % of the resource per
  spike, 200 ms recovery), and
* **spike-frequency adaptation** (+1.5 mV threshold per spike, 150 ms decay).

Those two numbers were chosen by measurement, not taste: stronger values calm the network further but
start to cost real responses (at 35 %/2 mV the sugar → proboscis pathway stops working), weaker ones
leave the antennal lobe saturated at 200 Hz.

Activity then settles into a responsive regime: 50–220 k spikes/s across the CNS, around 1 Hz average
rate, rising and falling with what the bee is looking at.

It runs on a dedicated thread, in real time, and never blocks the server. If the machine cannot keep up
the fly simply lives in slow motion (`/malecns stats` shows the factor).

### 3. Senses (`Senses.java`)

| Fly neurons | Driven by |
| --- | --- |
| L1–L3 (OFF), Mi1 (ON) | Luminance decrements/increments per eye column |
| T4a–d, T5a–d | Local motion, from a Hassenstein–Reichardt correlator over the sampled visual field (a→front-to-back, b→back-to-front, c→up, d→down, as in the real lobula plate) |
| ORN_DM1/DM2/DM3/DM4/DL5/VA2/VM7d | Flowers and beehives, per antenna, inverse-square with the odour on the correct side of the head |
| ORN_V (CO₂) | Players and mobs breathing nearby |
| ORN_DA1/VA1v/VA1d (pheromones) | Other bees |
| ORN_DA2 (geosmin) | Mycelium, podzol, mud, rooted dirt |
| LB3a/LB3c (sugar GRNs) | Tarsal contact with a flower |
| LB1a–d (bitter GRNs) | Cactus, wither rose, sweet berry bush |
| TRN_VP2 / VP3a/b, VP1m | Biome temperature, hot and cold |
| HRN_VP5/VP1d/VP1l, VP4 | Rain, nearby water, biome humidity |
| JO-C/JO-E (wind, gravity) | Airspeed and storms |
| JO-A/JO-B (sound) | Footsteps, other bees' wingbeats, another MaleCNS bee's courtship song |
| BM_InOm (head bristles) | Bumping into blocks, being punched (from the correct side), the home-radius wall |
| Tarsal sensory neurons | Standing on the ground |

The world is sampled by 377 ray casts per visual frame (10 frames/s by default), one grid of view
directions rotated with the bee's head; each of the 21,000 optic-lobe input neurons reads that grid at
its own receptive-field direction. Block brightness comes from the block's map colour and the light
level at the face it was hit on, faded towards the sky colour with distance.

Photoreceptors themselves are deliberately *not* driven: their histaminergic synapses are sign-inverting
and the real lamina is graded, not spiking, so in a signed LIF model driving R1–R6 would only silence
the lamina. Driving L1–L3 and Mi1 instead is the standard shortcut, and the motion pathway downstream of
them is entirely the connectome's.

### 4. Motor (`Motor.java`)

The model has no calibrated gain from spikes to muscle force, so every read-out channel is judged
against its own recent history (running mean and spread over ~15 s):

| Behaviour | Neurons |
| --- | --- |
| Turning | DNa01, DNa02, DNp15: left/right imbalance |
| Flight power, climb | DNg02 (wing stroke amplitude) |
| Forward drive | DNp09 (P9) |
| Backing up | MDN (moonwalker descending neurons) |
| Escape jump | DNp01 (the Giant Fiber) |
| Courtship song | pIP10: plays a note, and other MaleCNS bees hear it through their Johnston's organ |
| Drinking nectar | MN9 + MN11D/V (proboscis motor neurons), while tasting sugar |

That the optomotor and escape circuits work is not imposed anywhere: rotate the visual scene and the
HS cells and DNp15 swap hemispheres exactly as in a real fly; stimulate the looming detectors LPLC2/LC4
and the Giant Fiber fires at ~190 Hz, through 6.2 million real synapses.

## Configuration (`plugins/MaleCNSBee/config.yml`)

```yml
max-bees: 3               # each bee is a whole CNS: roughly half a CPU core
keep-chunks-loaded: true  # the bee keeps living when no one is around
home-radius: 96           # soft wall it can feel with its bristles; 0 = roam without limit
invulnerable: true        # players cannot kill it (it still feels punches)
show-activity-in-name: true
vision:
  interval-ticks: 2       # 10 visual frames per second
  max-distance: 20
motor:
  cruise-speed: 0.12
  max-turn-degrees-per-tick: 8
  climb-speed: 0.06
```

Bees survive restarts: the plugin remembers each bee's chunk in `bees.yml`, reloads it on startup and
gives the bee a fresh brain (a nervous system's state is not saved: it wakes up, it does not resume).

## Measured cost

On an i5-11400F, Paper 26.2, one bee: **1.0× real time** simulation (capped there on purpose), 1–3 ms
of server tick time, TPS 20.0. Three bees at once: ~0.8× real time each, ~6 ms per tick. Memory: ~90 MB
for the shared connectome plus ~7 MB per bee.

## Honest limits

* It is a fly's nervous system, not a bee's. The fly is the animal we have a connectome for.
* The retina and the elementary motion detectors are a phenomenological front end (see above); everything
  from L1/Mi1 and T4/T5 onwards is the measured connectome.
* Synapse signs are neurotransmitter *predictions*; connections below 5 synapses are dropped; synaptic
  depression and adaptation are added for stability and are not measured per cell type.
* Two things the experiments turned up that are worth knowing before you read too much into a result:
  the antennal lobe's local-neuron network **sustains its own activity** once any spontaneous input
  ignites it (ORN idle firing is therefore kept at 0.2 Hz, far below a real ORN's, or the lobe saturates);
  and a looming object drives the Giant Fiber to ~90 Hz peaks **without** measurably exciting LPLC2/LC4.
  Silencing those detectors barely changes it, so in this model the escape signal arrives by other routes
  (`/malecns experiment escape-necessity` is exactly that test, and it answers "no").
* An untrained connectome has no motivation and does not chemotaxis its way to flowers. It roams,
  reacts, startles, sings and occasionally feeds: the behaviour of a fly brain in a bee's body, not a
  game AI pretending to be one.

## Licence

* Plugin code: **GPL-3.0** (see `LICENSE`).
* The connectome in `src/main/resources/malecns.bin.gz`, and anything derived from it, stays under
  **CC BY 4.0** from Janelia's FlyEM project. Keep the attribution in `NOTICE.txt` with it.

## Credits

* Connectome data: **FlyEM MaleCNS v1.0**, Janelia Research Campus, [male-cns.janelia.org](https://male-cns.janelia.org/),
  licensed **CC BY 4.0**. See `NOTICE.txt` in the jar.
* Model: Shiu, Sterne, Spiller et al., *A Drosophila computational brain model reveals sensorimotor
  processing*, Nature 634 (2024).
* Cell-type identities for the taste circuits: the MaleCNS gustatory connectome paper (Cell, 2026).

## Rebuilding

```bash
mvn -o package                                   # needs JDK 25; jar lands in target/
python tools/build_brain.py src/main/resources/malecns.bin.gz   # regenerate the brain from the FlyEM release
```

`tools/build_brain.py` expects the four FlyEM feather files in a `data/` directory next to it
(annotations, neurotransmitters, connectome weights); it documents the exact file names.
