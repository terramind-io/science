# fly-sim

Download a real *Drosophila* connectome, turn it into a spiking network, and
check the result against a published experiment.

The point is not a simulator that produces plausible-looking activity. It is a
pipeline whose output can be **falsified**: it reproduces the sugar-taste →
proboscis-extension circuit from Shiu et al. 2024 (*Nature*), so a mistake
anywhere between the download and the integrator shows up as a wrong number.

## Quick start

```bash
uv sync                                   # Python 3.13
uv run flysim download                    # ~59 MB, no account needed
uv run flysim info                        # 134,181 neurons / 2,700,513 connections
uv run flysim experiment sugar-mn9        # the reproduction, writes out/
```

Ad-hoc runs:

```bash
# drive one labelled population and see what responds
uv run flysim simulate --label 'Sugar Gustatory Receptor Neuron' --regex --rate 100

# look neurons up by any annotation column
uv run flysim find --label '\bMN9\b' --regex
uv run flysim find --sub-class proboscis_motor_neuron
```

## Live visual simulator

The local browser app combines a procedural 3D fruit fly, a live schematic
neural circuit, spike rasters, and membrane traces. It starts paused with a
small **synthetic demo circuit**, so no connectome download is needed.

From a source checkout (Node.js 22.12+ and Python 3.13+):

```bash
uv sync --extra visual
npm ci
npm run build
uv run flysim serve
```

Open **http://127.0.0.1:8000** and click **Start simulation**. Drag to orbit,
scroll to zoom, adjust the stimulus slider while running, and click a circuit
node (or use the neuron selector) to inspect it. Up to four displayed neurons
can record voltage. Annotation selectors use **exact matches**. Changing the
stimulus population clears the displayed history while preserving neural state.

- **Idle / Walk / Fly**, speed, and turning control illustrative body movement.
  These controls apply to Manual / Research mode. FlyWire and Male CNS support the
  experimental autonomous room described below; its physics are simplified.
- Proboscis extension is an **illustrative mapping**: the mean annotated MN9
  firing rate over the last 100 ms divided by 300 Hz, clamped to 0–100%.
  It is not a prediction of muscle force or extension angle. Missing MN9
  annotations disable this mapping; missing sugar labels disable the sugar preset.
- Pause freezes neural activity and body movement. Reset restores the seed,
  clears recordings, and returns the fly to its configured starting pose. The seed field
  applies on reset; the current stimulus population and rate are retained.
- The full loaded connectome is simulated. The schematic displays at most
  200 neurons and 1,000 connections, prioritizing MN9, stimulated neurons,
  and strong outgoing neighbors. Plots retain 10 simulated seconds; voltage
  displays sample every 1 ms, while integration remains at 0.1 ms.
- Simulation advances in 10 ms blocks on a background worker. The displayed
  simulation/wall-time ratio reports achieved speed; full networks may run
  slower than real time. Rendering never advances the numerical model itself.

Select **FlyWire** or **Male CNS** and use **Load** for a built cache, or
**Download & load** to explicitly download and prepare a dataset. Loading pauses
the session. The existing `flysim download`/`info` commands and `FLYSIM_CACHE`
setting also work. Dataset downloads can be large, particularly Male CNS;
the interface shows loading and recoverable failure states. Demo behavior
must not be interpreted as reproduction of the published experiment.

One server owns one shared session. Closing the last connected browser pauses
it. Reconnecting restores recent history without automatically resuming.
Slow clients are disconnected rather than silently losing spike frames.
Keep the default loopback binding for local use; no account/authentication or
remote hosting is provided. `--host` and `--port` override the listen address.
The interface targets desktop browsers and supports reduced motion.

Frontend development: run `uv run flysim serve` and `npm run dev` in separate
terminals; Vite proxies `/api` to port 8000. Production assets are served locally,
without CDN requests. Build the frontend **before** `uv build` when packaging
the visual app; the generated assets are included in wheels and are ignored by Git.

Validation:

```bash
uv run --extra visual pytest -m 'not slow'
npm run build
npx playwright install chromium
npm run test:browser
```

The offline tests cover chunk/batch numerical equivalence, live control changes,
bounded history, session recovery, dataset failures, and desktop browser flows.
The existing download-dependent scientific reproduction remains a separate
`pytest -m slow` check. Browser tests save a desktop screenshot under `test-results/`.

## Datasets

Both are public bulk downloads under CC-BY 4.0 — no login, no API token — and
both arrive through the same `Connectome` interface, so everything downstream
is dataset-agnostic.

| `--dataset` | volume | neurons | connections (≥5 syn) | synapses |
|---|---|---:|---:|---:|
| `flywire` | FAFB snapshot 783, adult **female brain** | 134,181 | 2,700,513 | 34.2 M |
| `male-cns` | Male CNS v1.0, **male brain + optic lobes + VNC** | 165,122 | 6,235,682 | 89.7 M |

`male-cns` (published September 2026) carries the ventral nerve cord with the
neck connective intact, so sensory input, central processing and leg/wing motor
output are all in one graph. Its flat connectome covers every EM segment —
152 M rows over 1.8 M bodies — so the loader streams it in Arrow batches and
keeps only edges between traced neurons.

Two things about the FlyWire dump that are easy to get wrong, and that this
loader handles: it has **one row per (pre, post, neuropil)**, so a pair
synapsing in several neuropils appears several times and must be summed; and
the widely quoted "127,978 neurons / 2,613,129 connections" describe
materialisation 630, which the analysis papers used, not snapshot 783.

## The model

Leaky integrate-and-fire with an exponential synapse, exactly as specified in
Shiu et al. 2024:

```
dv/dt = (g - (v - V_rest)) / tau_m
dg/dt = -g / tau_syn
```

| parameter | value | source |
|---|---|---|
| `V_rest` = `V_reset` | −52 mV | Kakaria & de Bivort 2017 |
| `V_threshold` | −45 mV | " |
| `tau_m` = R·C = 10 MΩ × 0.002 µF | 20 ms | " |
| `t_refractory` | 2.2 ms | Kakaria & de Bivort 2017; Lazar et al. 2021 |
| `tau_syn` | 5 ms | Jürgensen et al. 2021 |
| `t_delay` | 1.8 ms | Paul et al. 2015 |
| `w_syn` | 0.275 mV / synapse | the model's **only free parameter** |

Connection weight is `syn_count × sign(pre) × w_syn`. The sign is per neuron,
not per synapse: a neuron is inhibitory when more than half its presynaptic
sites are predicted GABAergic or glutamatergic (glutamate is inhibitory in the
fly). For `male-cns` histamine joins that set, since the volume includes the
photoreceptors and `ort`/`HisCl1` are chloride channels.

### Performance

A whole-brain second — 134k neurons, 2.7M connections, 10,000 steps at
dt = 0.1 ms — takes about **9 s on one CPU core**. Propagation is a gather of
the spiking neurons' CSR rows summed with `np.bincount`, so each step costs the
out-degree of the neurons that actually fired rather than the 2.7M-entry matrix
product a dense `W.T @ spikes` would pay.

## What is verified

`uv run pytest` covers the integrator against the closed-form solution of its
own ODEs: a single PSP matches the analytic

```
u(t) = g0 · tau_syn/(tau_syn − tau_m) · (e^(−t/tau_syn) − e^(−t/tau_m))
```

to within 0.1% at the peak and 1% across the whole waveform; spikes reset to `V_reset` and hold for exactly
2.2 ms, and a silent network never fires.

`uv run pytest -m slow` runs the reproduction itself. Driving the 23 labelled
sugar GRNs of one hemisphere at 10-200 Hz, 10 trials each, and reading out the
MN9 pair (MN9 stays silent below ~50 Hz and saturates near 295 Hz):

| check | paper | measured |
|---|---|---|
| MN9 rate rises monotonically with GRN drive | yes | Spearman ρ = 0.996 |
| **contralateral** MN9 > ipsilateral (Fig. 2C) | yes | ratio 1.32 |
| MN9 at 100 Hz drive ≈ 80% of maximum | 0.80 | 0.68 |

The first two reproduce cleanly. The third lands near, not on, the published
value, and the reason is the population rather than the pipeline: `w_syn` was
calibrated on materialisation 630, and on snapshot 783 the 23 neurons carrying
an explicit "Sugar GRN" label give 0.68 while the broader 67-neuron
`sugar/water` subclass gives 0.95 — the paper's 0.80 sits between them. The
test asserts `0.6 ≤ fraction ≤ 0.9`, which catches a broken pipeline without
pretending to a precision the annotations do not support.

Both populations are found through FlyWire's community labels rather than
hard-coded ids. MN9 was labelled by Philip Shiu (Kristin Scott Lab), first
author of the paper being reproduced; the sugar GRNs carry the Engert et al.
2022 / Shiu, Sterne et al. 2022 annotation the model itself used.

## What this model does *not* do

Inherited from the paper and deliberately preserved so results stay comparable:

- **Basal firing rate is 0 Hz.** A direct consequence is that inhibition onto
  an otherwise silent neuron does nothing. Absolute firing rates are therefore
  not meaningful — read *changes*, not values.
- **One sign per neuron.** No co-transmission, no receptor diversity;
  dopaminergic and serotonergic neurons are modelled poorly.
- **No gap junctions** — they cannot be identified in EM.
- **No neuropeptides or neuromodulation.**
- **Synapse count is the only proxy for synaptic strength**, and morphology,
  dendritic compartments and receptor dynamics are ignored entirely.
- One animal, one moment. A connectome is a necessary condition for
  understanding a brain, not a sufficient one.

## Layout

```
src/flysim/
  datasets/       base.py (Connectome + protocol), flywire.py, malecns.py, cache.py
  graph.py        transmitter signs, CSR assembly, built-graph cache
  lif.py          the simulator
  experiments/    sugar_mn9.py -- the reproduction
  plotting.py     rasters and dose-response curves
  cli.py          flysim download | info | find | simulate | experiment
```

Raw downloads and built graphs are cached under `~/.cache/flysim`
(override with `FLYSIM_CACHE`).

## Sources

- Shiu et al. 2024, *A Drosophila computational brain model reveals sensorimotor
  processing*, Nature — [preprint](https://www.biorxiv.org/content/10.1101/2023.05.02.539144)
- Dorkenwald et al. 2024, *Neuronal wiring diagram of an adult brain*, Nature —
  [FlyWire Codex](https://codex.flywire.ai/)
- Janelia FlyEM / MRC LMB 2026, *Sexual dimorphism in the complete Drosophila
  male central nervous system connectome*, Cell —
  [MaleCNS](https://male-cns.janelia.org/)

Both connectomes are CC-BY 4.0; cite them if you use this.

## Experimental connectome-driven room

Load **FlyWire** (cached snapshot 783) or **Male CNS** (v1.0 brain + VNC) to enter the furnished room in
**Autonomous** mode, then press **Start simulation**. The synthetic demo retains
its original research controls. Choose **Manual room** to inspect
body mechanics using Idle / Walk / Fly, or **Research / original experiment**
to use the original stimulus experiment. Autonomous mode rejects direct neural
stimulation and manual body commands. An incomplete population profile rejects
Start and leaves the research interface available.

The cutaway room has a table, chair, window and partially peeled banana. While
paused, choose Table / Floor / Airborne, edit Banana X/Z or disable odor, then
press **Apply room / reset**. Reset preserves this arrangement and resets the
neural RNG, neural state, body, decoder filters, hysteresis and bounded trail.
The overview camera stays fixed; Fly-follow tracks the body. Odor overlay shows
illustrative concentration contours on the tabletop. Distances are scene units,
not millimeters. Altitude measures the feet above the room floor; the tabletop
is at 2 units. The rendered fly is intentionally enlarged relative to furniture.

### Neural and physical interfaces

The batch LIF defaults and connectome weights are unchanged. Each 10 ms block:

1. `embodied/environment.py` samples the two antennae, local obstacle proximity
   and exposed-food contact at the current pose.
2. `embodied/controller.py` encodes these samples as Poisson sensory drive and
   the existing engine advances **all** neurons and synapses.
3. Population spike counts become mean per-neuron firing rates, exponentially
   filtered with a 100 ms time constant. The motor decoder receives only counts
   and surface-support state. It has no access to food coordinates or odor.
4. Bounded body commands drive simple gravity, vertical drag, surface support,
   wall, ceiling, table and chair collisions. Horizontal movement is an
   overdamped speed command; there is no learned or scripted navigation policy.

`embodied/profile.json` records the versioned gains, thresholds, declared
background populations and source references. Resolved metadata includes exact
64-bit neuron IDs **as strings**, dataset provenance and a SHA-256 identity of
the profile/population manifest; it is streamed in `/api/session` and reconnect
snapshots. The manifest is not a checksum of raw dataset files.

Male CNS uses the separate `embodied/male_cns_profile.json`. The existing
traced/minimum-five-synapse cache contains 165,122 neurons and 6,235,682
connections. Native L/R annotations map to left/right interface keys without
altering the cache. The profile resolves 381 bilateral VNC leg motor neurons
(`vnc_motor`, subclasses `fl`/`ml`/`hl`) and 67 wing motor neurons (`wm`).
Walking speed and steering are multiplied by `min(1, mean leg motor Hz / 10)`;
flight speed, turning and power use `min(1, mean wing motor Hz / 50)`.
These are conservative activity gates, not calibrated muscle forces or a gait
generator: VNC activity alone does not command locomotion. Male CNS walking
steering uses a negative left-minus-right sign because increasing scene heading
turns right. All descending gains below otherwise match the initial FlyWire
interface. Takeoff and landing remain descending readout hypotheses.

Male CNS sugar input is **unavailable**. LB3 cross-matches contain sugar/water
candidates without a verified sugar-specific subset; sugar-labeled central
interneurons are not substituted for sensory GRNs. Contact remains a geometric
measurement, and MN9 still drives the proboscis. The UI reports this limitation.
Unknown-side odor neurons are excluded from bilateral inputs; every included
ID is saved in the manifest. Missing required sensory, descending or VNC motor
populations reject the autonomous profile.

**Male CNS measured result** (`artifacts/male-cns/REPORT.md`): the frozen
profile (50 Hz sensory ceiling, 5 Hz background, chosen by the declared
calibration ranking) achieved **0/20 autonomous contacts** in two-second
held-out trials, **0/20 with odor off**, no powered flight and zero horizontal
travel from table or floor starts; the only displacement was passive drift
while falling from airborne starts. DNp09 stayed silent under odor input.
DNg02 fired at ~10 Hz but at the same rate with odor off, so that activity is
background-driven and its decoded power never reached the flight threshold.
Failed stage: the odor-to-forward-walking readout. Direct descending-neuron
stimulation (`body-probes.json`) still produces walking, steering, takeoff,
powered flight, flight turning and landing through the VNC gates, so the
missing link is sensory-to-descending recruitment, not the body interface.
`validate` confirmed deterministic full-state replay, motor silencing, odor
ablation and contact ablation on the full 165,122-neuron graph
(`causal-checks.json`). Reliable food-seeking is **not** established for either
dataset; no engineered fallback was added.

| Interface | Initial hypothesis / illustrative mapping |
| --- | --- |
| Food odor | `exp(-distance / 2)` at each antenna; same-side ORN_DM1 and ORN_VA2. Generic food-odor proxy, not measured banana chemistry. |
| Looming | LC4, each side: `clip(speed / obstacle_distance / 4, 0, 1)`, using short horizontal rays through scene colliders. This is a simplified visual interface, not retinal rendering. |
| Sugar | Annotated sugar GRNs driven only at exposed banana capsule contact in Autonomous. No background sugar drive. |
| Walking | Mean bilateral DNp09 above 5 Hz × 0.025 units/s/Hz, clamped 0–3 units/s. |
| Walking steering | Left-minus-right DNa02 × 0.03 rad/s/Hz, clamped ±3 rad/s; sign is a decoder hypothesis. |
| Flight power | Mean DNg02_* × 0.02, clamped 0–2; lift = power × 6 units/s². Horizontal flight speed uses the same rate gain, clamped 0–3. DNg02 asymmetry does not steer. |
| Flight steering | Left-minus-right DNp03 × 0.03 rad/s/Hz, clamped ±3. |
| Takeoff | Either bilateral-mean DNp02 or DNp11 crosses 30 Hz; latch clears below 10 Hz. One 2.5 units/s launch impulse per latch activation while supported. |
| Landing posture | Either bilateral-mean DNp07 or DNp10 crosses 30 Hz; clears below 10 Hz. Suppresses lift; landing requires actual surface contact. |
| Physics | Gravity 6 units/s²; vertical drag coefficient 1.5/s; room boundary ±5.4 and ceiling 4.8; AABB furniture colliders streamed from the backend. |
| Proboscis | Existing MN9 rate / 300 Hz animation. Food contact is reported separately; contact alone does not prove feeding or successful navigation. |

The odor choice follows [Semmelhack & Wang (2009)](https://www.nature.com/articles/nature07983).
The descending populations are experimentally motivated candidates; their
conversion into these exact body commands is a hypothesis, not an established
biophysical model. Source links for each population are in the profile.

### Calibration and evidence

Run against the cached full connectome:

```bash
.venv/bin/python -m flysim.embodied.evaluate --out artifacts/embodied \
  --probe-seconds 0.2 --trial-seconds 2
.venv/bin/python -m flysim.embodied.diagnostics

# Separate evidence directory and profile for Male CNS
.venv/bin/python -m flysim.embodied.evaluate --dataset male-cns \
  --out artifacts/male-cns --probe-seconds 0.2 --trial-seconds 2 --workers 4
.venv/bin/python -m flysim.embodied.diagnostics --dataset male-cns \
  --out artifacts/male-cns/body-probes.json
.venv/bin/python -m flysim.embodied.report artifacts/male-cns
.venv/bin/python -m flysim.embodied.validate artifacts/male-cns
```

The evaluator saves direct-output probes, sensory-to-output probes, all 12
sensory/background candidates (25/50/100/200 Hz × 0/1/5 Hz), a frozen profile,
isolated checks, and 20 held-out placements/poses/seeds paired with odor-off
controls. Candidate ranking is deterministic: contacts, then bounded distance
minus collision penalty, then lower input rates. Held-out outcomes never tune
the profile. These are short two-second trials, and failures are retained.
The separate body probes deliberately stimulate descending neurons and must
never be interpreted as autonomous behavior. Extend the trial duration for
longer-horizon research; full-connectome real-time execution is not required.

`artifacts/embodied/REPORT.md` records the measured outcome and limitations.
The included two-second evaluation yielded **1/20 contacts (5%)**, versus
**0/20 with odor off**. That contact came from turning near the banana with zero
horizontal travel. DNp09 and DNg02 remained silent; reliable food-seeking was
not achieved. The bundled frozen profile uses a 25 Hz sensory ceiling and
0 Hz background. The UI shows this identity-matched evidence.
Use `--resume --workers 4` to resume independent calibration and held-out trials, and
`.venv/bin/python -m flysim.embodied.report <output-directory>` to summarize a completed run.
A profile may be described as reliably food-seeking only after at least 16/20
held-out autonomous contacts. Stationary or unsuccessful behavior remains visible;
there is no fallback policy. Tests cover deterministic replay, support/collision,
takeoff and landing hysteresis, odor/contact removal, motor-readout silencing,
and reset/reconnect. Browser tests run on an isolated localhost port 8765.
The `validate` command also checks replay of full-connectome voltages,
conductances and counts, motor silencing, and odor/contact ablation against the
saved frozen profile. It saves `causal-checks.json`, explicitly distinguishing
unavailable Male CNS sugar input from a validated sugar-contact response.
