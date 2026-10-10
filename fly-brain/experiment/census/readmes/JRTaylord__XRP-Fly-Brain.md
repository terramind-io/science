# XRP Fly Brain

Drive a [SparkFun XRP robot](https://www.sparkfun.com/experiential-robotics-platform-xrp) with a
spiking simulation of a complete adult *Drosophila* connectome. Two datasets are supported, in
the same runtime format:

- **Male CNS v1.0** (Janelia FlyEM/Google, *Cell* 2026 — released Sept 2026): 166,691 neurons,
  ~125M synapses, covering the **entire central nervous system** — brain *and* ventral nerve
  cord, so real leg motor neurons are simulated. Preferred when present.
- **FlyWire v783** (Dorkenwald et al. & Schlegel et al., *Nature* 2024): 139,255 neurons,
  ~2.7M connections; adult female brain only. This is the dataset the Shiu et al. model was
  validated on.

The robot program is a normal **WPILib (2026) Java** project. It runs on this PC in WPILib
simulation; the built-in XRP client transmits motor commands to the robot over WiFi and streams
sensor values back (UDP to `192.168.42.1`). A background thread runs a leaky integrate-and-fire
(LIF) simulation of the connectome in real time. Each 20 ms robot loop:

```
XRP sensors ──► Poisson firing of sensory neurons ──► 139k-neuron LIF simulation
                                                            │
XRP motors ◄── arcade drive ◄── firing rates of descending (motor) neurons
```

## Sensor → neuron → motor mapping

| Robot signal | Fly neurons stimulated | Fly circuit consequence | Robot behavior |
|---|---|---|---|
| Reflectance sensors (dark floor) | Sugar gustatory receptor neurons (left/right) | Proboscis extension (feeding) | Stop on "food" |
| Rangefinder (obstacle approaching) | LC4 + LPLC2 looming detectors (both eyes) | Giant-fiber escape (a jump) | Back away |
| User button | Bitter gustatory receptor neurons | Aversion | Suppress forward drive |

Motor readout (mean firing rate per neuron, smoothed ~200 ms):

| Group | Fly cell type | Effect |
|---|---|---|
| `fwd` | DNp09 (forward-walking command DN) | forward speed + |
| `bwd` | MDN "moonwalker" (backward walking) | forward speed − |
| `escape` | DNp01 (giant fiber) + DNp02, DNp04, DNp11 — the looming detectors' DN targets | forward speed − (retreat) |
| `turn_left` / `turn_right` | DNa01 + DNa02 left / right (ipsilateral steering DNs) | arcade-drive rotation |
| `feed` | MN9 proboscis-extension motor neurons (male CNS only) | forward speed × (1 − feeding): stop to eat |
| `legmn_left` / `legmn_right` | VNC leg motor neurons (male CNS only) | forward speed + (male CNS) |

The model brain is silent with no sensory input, so the robot adds a constant `idleSpeed` cruise
and, while the steering neurons are quiet, a slow random walk on heading (`wanderTurnMax`,
`wanderPeriodSec`) so it meanders until a sensor drives a neuron. Set both to 0 for a robot that
moves only when neurons fire.

### Setting up the table

The two reflectance sensors under the XRP's nose are IR line sensors: they read near 0 on a
light, matte surface and near 1 on black. Dark is "sugar", so lay **black tape (or black paper)
on a light table** - a patch is a food source, a line is a sugar trail that the left/right
sensors sample separately. Anything the rangefinder sees closer than 0.3 m is a looming
predator: walls, boxes, a hand.

## The model

Parameters follow Shiu et al. 2024, *"A Drosophila computational brain model reveals sensorimotor
processing"* (Nature 634:210–219; code: [philshiu/Drosophila_brain_model](https://github.com/philshiu/Drosophila_brain_model)):

- `dv/dt = (v_rest − v + g)/τ_mem`, `dg/dt = −g/τ_syn`
- v_rest = v_reset = −52 mV, threshold −45 mV, τ_mem = 20 ms, τ_syn = 5 ms,
  refractory 2.2 ms, synaptic delay 1.8 ms
- Each synapse contributes 0.275 mV × synapse count; sign from the presynaptic neuron's
  predicted neurotransmitter (ACh +, GABA −, glutamate − via GluCl; aminergic treated as +)
- A spike resets v and clears the accumulated synaptic drive g (as in the reference Brian2
  code; v and g are frozen during the refractory period)
- Sensory input = forced Poisson spiking of the target group (10–200 Hz), as in the paper

Two additions beyond the paper, both needed for a brain that has to run for hours rather than
one second: **spike-frequency adaptation** (1 mV of hyperpolarization per own spike, decaying
with τ = 300 ms) and **synapse-density normalization** (the 0.275 mV weight was fitted on
FlyWire's 245 synapses/neuron and tolerates up to 300; the male CNS export reports 538, so its
weight is scaled to 0.153 mV). Without them either connectome ignites after its first stimulus into a permanent
reverberating state - the central complex in FlyWire, the antennal lobe in the male CNS - with
thousands of neurons pinned at the refractory ceiling and the left DNa02 firing forever. Both
are `LifEngine.Params` fields, overridable without a rebuild via `-Dflybrain.<field>=` or
`FLYBRAIN_<FIELD>=` (e.g. `-Dflybrain.adaptMvPerSpike=0 -Dflybrain.calibrationSynapsesPerNeuron=0`
for the pure reference model).

Prior art in the same spirit: the OpenWorm *C. elegans* connectome on a Lego robot
(Busbice 2014), and [flywire-arduino](https://github.com/mhdsilva/flywire-arduino) (LC4/LPLC2→GF
escape subcircuit on an Arduino servo).

## Prerequisites

- WPILib 2026 (installed at `C:\Users\Public\wpilib\2026`)
- An XRP with recent [XRP-WPILib firmware](https://docs.wpilib.org/en/stable/docs/xrp-robot/getting-to-know-xrp.html)

## Quick start (no download needed)

The repo ships with a tiny hand-wired reflex network (`data/sample/`, 18 neurons) in the same file
format as the full brain, so everything runs out of the box:

```powershell
.\gradlew simulateJava
```

1. Power the XRP; join its WiFi network (`XRP-xxxx`, password `xrp-wpilib`). The simulator
   connects to the robot at `192.168.42.1` automatically (`HALSIMXRP_HOST` in `build.gradle`).
2. In the Sim GUI, set **Teleoperated** mode.
3. Watch `Brain/*` values on the dashboard (NetworkTables): sim time, realtime factor, spike
   counts, per-group firing rates.

Without an XRP on the network the program still runs; the XRP client just retries in the
background — useful for testing the brain itself.

## Running the real fly brain

**Male CNS v1.0** (newest; ~570 MB of Feather flat files from the public
`gs://flyem-male-cns` bucket, no account needed; CC-BY 4.0):

```powershell
.\gradlew downloadMaleCns
```

This converts the per-body annotations + neurotransmitter predictions + traced-only edge list
into `data/malecns/` (edges thresholded at ≥5 synapses → ~6.3M connections, matching the FlyWire
export's convention). Sensory/motor groups come from the v1.0 cell types: LC4/LPLC2 looming
detectors, DNa01/DNa02/DNp09/MDN/DNp01/02/04/11 descending neurons, labellar GRNs LB3b/LB3c (sugar, Gr64f) and
LB1a–d (bitter, Gr33a), plus front/middle/hind leg motor neurons per side.

**FlyWire v783** (~53 MB, no account needed; CC-BY 4.0):

```powershell
.\gradlew downloadConnectome
```

This fetches `neurons`, `classification`, `consolidated_cell_types`, `labels`, and `connections`
from the Codex data bucket (`storage.googleapis.com/flywire-data/codex/data/fafb/783/`), then
writes `data/flywire/{neurons.csv.gz, connections.csv.gz, groups.csv}` — including the
sensory/motor groups resolved from cell-type annotations (LC4, LPLC2, DNa01/02, DNp09, MDN,
DNp01/02/04/11) and
community labels (sugar/bitter GRNs).

On the next `simulateJava`, the robot loads the best available dataset automatically
(`malecns` → `flywire` → `sample`; loading takes a little while — watch the console and the
`Brain/loaded` dashboard flag). Override with the `FLYBRAIN_DATASET` environment variable or
`-Dflybrain.dataset=` (a directory name under `data/`).

## Tuning

Sanity-check any dataset offline with `.\gradlew benchBrain` (`-Dflybrain.dataset=flywire` to
pick another dataset, `-Dflybrain.bench.sugarHz=` / `loomHz=` to change stimulus strength). It
runs a baseline → sugar (both, left, right) → looming (strong, weak) → recovery protocol and
prints per-group and per-neuron readout rates, active-neuron counts, the most active cell types
in each phase, and achieved speed. The recovery phases must end at 0 spikes - that is the check
that the brain comes back to rest. Both real brains are silent at baseline (as in Shiu et al.),
activate ~1-2k neurons under looming, and run at ~1× real time idle, ~0.3-0.5× when excited (the
pacing loop degrades gracefully - the brain runs in slow motion; watch `Brain/realtimeFactor`).
Set `LifEngine.Params.timeScale` below 1.0 to make that explicit.

Male CNS readouts under the bench protocol (Hz per neuron): looming at 200 Hz drives the
`escape` group to ~270 Hz (all eight DNs, giant fiber included) and at 60 Hz to ~140 Hz, with
the steering pools essentially silent, so the robot backs straight up. DNp09 and MDN never fire.
Sugar at 150 Hz activates only ~250 neurons of the gnathal (feeding) circuit, barely reaches
the MN9 proboscis motor neuron (~0.5 Hz), and touches no walking readout - see the quirks below.
The protocol also fires sugar + looming + bitter together and then checks recovery: at a milder
normalization (weight 0.179 mV) that combination ignites the antennal lobe permanently, which
is why the default is the stricter one.

Motor gains are live-tunable **Preferences** (NetworkTables → `Preferences/FlyBrain/*` in the Sim
GUI): `fwdGainPerHz` (DN command drive), `legGainPerHz` (mean leg-motor-pool drive — the main
mover on the male CNS, where sugar input produces ~18 Hz in the leg MN pools while DNp09 itself
stays near-silent), `escapeGainPerHz` (reverse drive from the giant-fiber escape group — this is
what makes the robot retreat from the rangefinder's obstacle), `feedStopPerHz` (how completely
proboscis-motor activity halts the robot on food), `idleSpeed` (baseline cruise),
`turnMax`, `turnMinActivityHz`, and the wander pair `wanderTurnMax`/`wanderPeriodSec`. Steering
uses the bounded left/right
asymmetry `(L−R)/(L+R)` of the DNa01+DNa02 steering pools because tiny readout groups saturate
near the 450 Hz refractory limit. Sensor→stimulus constants live at the top of
[`Robot.java`](src/main/java/frc/robot/Robot.java).

Known dataset quirks: FlyWire's community labels only annotate sugar GRNs on the left
hemisphere, so the converter mirrors them to the right channel; the male CNS labellar GRNs are
properly lateralized. Where the steering readouts respond at all they show a left bias even
under symmetric input (FlyWire: sugar drives the left DNa02 alone, ~25 Hz) - the two sides
receive near-mirror-image input, so this is a winner-take-all outcome of the mutually inhibitory
steering circuit, not a data error. Looming drives the giant-fiber escape circuit (the `escape`
readout) and not MDN - a real fly's escape is a jump, which a two-wheeled robot can't do, so the
robot backs away instead. Sugar does not drive walking in either real brain: a fly's response
to sugar is to stop and extend its proboscis (sugar → MN9), so the robot's food response is to
stop, via the `feed` readout — but at the coupling that keeps the male CNS stable that pathway
only just reaches MN9, so on the real brain a dark patch currently does very little. To make
food matter, raise `kSugarMaxHz` in `Robot.java` or try `-Dflybrain.calibrationSynapsesPerNeuron=350`
(stronger feeding response, but the brain can then lock up after a strong combined stimulus —
watch `Brain/totalSpikes` climbing with no input). Line-following via the sugar channels works
only on the hand-wired sample network.

## Project layout

```
src/main/java/frc/robot/        Robot program (TimedRobot + XRP drivetrain/sensors)
src/main/java/frc/flybrain/     Connectome loader + LIF engine + FlyBrain facade
src/main/java/frc/flybrain/tools/  FlyWire downloader/converter (gradlew downloadConnectome)
data/sample/                    18-neuron hand-wired reflex network (runs out of the box)
data/flywire/                   Full connectome (created by downloadConnectome; gitignored)
```

## Data citation

Male CNS connectome: *Sexual dimorphism in the complete Drosophila male central nervous system
connectome*, Cell (2026). Data CC-BY 4.0 via [male-cns.janelia.org](https://male-cns.janelia.org/).
Sugar/bitter GRN identities from the companion gustatory connectome paper (Cell 2026).

FlyWire connectome: Dorkenwald et al., *Neuronal wiring diagram of an adult brain*, Nature 634
(2024); Schlegel et al., *Whole-brain annotation and multi-connectome cell typing of Drosophila*,
Nature 634 (2024). Data CC-BY 4.0 via [Codex](https://codex.flywire.ai).
