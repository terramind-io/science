# flybrain_robot

FlyWire whole-brain connectome (v783, 139k neurons, 15M connections) running as a spiking LIF network,
closed-loop with NeuroMechFly (MuJoCo fly body). Wind hits the antennae, the connectome routes it to
descending neurons, their spikes steer the legs.

```
wind -> JO-C/E antennal neurons (Poisson) -> 139k-neuron LIF brain -> descending neuron spikes -> decoder -> CPG legs -> heading -> wind
```

## Setup

```bash
pip install -r requirements.txt
./setup_data.sh                 # ~135 MB; first run builds data/csr_783.npz (~120 MB)
export MUJOCO_GL=egl            # headless. use osmesa if no GPU/EGL
python validate_sugar.py        # expect: sugar 0 Hz -> MN9 0 Hz, sugar 100 Hz -> MN9 ~65-80 Hz (seed-dependent)
```

## Run

```bash
python run_closed_loop.py --wind left --seconds 3            # left|right|front|back|none
python run_closed_loop.py --wind left --seconds 3 --render   # adds outputs/wind_left.mp4
python annotate_video.py outputs/wind_left                   # overlays wind arrow + decoded steering
python plot_run.py outputs/wind_*.npz                        # outputs/summary.png
python probe_pathways.py                                     # which sensory inputs reach locomotor DNs
```

Cost on 1 CPU: brain ~4-7 s wall per brain-second, physics ~30 s per sim-second. Physics dominates.

## Files

| file | role |
|---|---|
| connectome.py | load connectome, CSR cache, cell type / side -> index lookup |
| brain.py | numba event-driven LIF, Shiu et al. 2024 equations + params. optional adaptive threshold (off by default) |
| sensors.py | wind direction -> left/right JO-C/E Poisson rates |
| decoder.py | DN population rates -> [left, right] CPG drive, per-side calibration |
| body.py | NeuroMechFly + HybridTurningController (flygym 1.2.1) |
| run_closed_loop.py | main loop, 10 ms decision step |
| validate_sugar.py | engine check vs published model |
| probe_pathways.py | sensory -> DN mapping |
| plot_run.py | trajectories + signals |
| annotate_video.py | wind arrow + steering bar on the rendered mp4 |

## Results (3 s runs, seed 0, fly spawns facing +x)

| wind from | start angle to wind | reaches +/-20 deg of upwind | last 1 s: mean, sd | notes |
|---|---|---|---|---|
| left | +90 | 0.47 s | -0.6, 6.5 deg | turns left |
| right | -90 | 0.39 s | +0.9, 7.5 deg | turns right |
| back | 180 | 0.95 s | +0.6, 7.0 deg | U-turn; turn direction at exactly 180 deg is set by spike noise; went right here, left in an unseeded earlier run |
| none | n/a | n/a | n/a | JO silent, steering DNs silent, drive fixed [1,1]. Heading still drifts +56 deg (left) over 42 mm: body/CPG asymmetry, not the brain. The brain-driven loop cancels this drift when wind is on |

Decoded turn is noisy (frequently hits the +/-0.8 clip); the body's inertia smooths it. All four .npz files and
summary.png are from the current code.

## RL: learn the motor readout from a frozen spiking whole brain

Question: with the published LIF brain frozen, which descending neurons (DNs) does reward select for steering?
This replaces the hand-picked steering DNs in decoder.py with a readout learned from all 932 DN groups (cell_type x side).

```bash
python validate_fast.py                     # FastBrain vs brain.py: identical spike counts on both tests
python rl_train.py --episodes 250 --lr 0.03 --seed 0 --out outputs/rl       # ~13 min on 1 CPU
python rl_eval.py outputs/rl                # 12 held-out wind directions: zero vs hand decoder vs RL; weights CSV + plot
python rl_mujoco.py --wind left --render    # transfer to NeuroMechFly (MuJoCo)
python rl_compare.py outputs/rl outputs/rl_seed1   # do weights replicate across seeds?
python rl_train.py ... --bias_lo 0 --bias_hi 0.5   # drift randomization (for the sim-to-sim offset)
```

| file | role |
|---|---|
| brain_fast.py | active-set LIF. eps=1e-6 bit-identical to brain.py; eps=1e-2 (used for RL) matched exactly on the 1 s tests, ~2.7x faster; eps=5e-2 changed 314 neurons |
| rl_env.py | frozen brain + JO encoder + unicycle body fit to the MuJoCo runs. Policy sees DN rates only |
| rl_train.py | REINFORCE with Gaussian exploration = node-perturbation three-factor rule (reward-prediction error x exploration noise x DN rate). Privileged critic (wind angle) for the baseline only |
| rl_eval.py / rl_mujoco.py / rl_compare.py | evaluation, MuJoCo transfer, cross-seed replication |

### Results, seed 0 (outputs/rl)

| readout (surrogate body, 12 held-out winds, last 1 s) | mean cos(upwind) | worst wind |
|---|---|---|
| zero (brain ignored) | +0.036 | -0.967 |
| hand decoder (decoder.py) | +0.892 | +0.370 |
| RL readout | +0.931 | +0.873 |

- 149 of 932 DN groups fired during training; RL can only weight those.
- Hemisphere level: left DN groups sum +8.9 (70% push a left turn), right DN groups sum -9.8 (67% push a right turn),
  i.e. reward recovered ipsilateral steering. DNa02 gets the ipsilateral sign on both sides (+0.13 / -0.12).
- Hand-decoder assumption not supported: DNg29 left gets the wrong sign (-0.45), DNb05 ~0. Top weights are DNp06 left
  and many DNge types. Weight-level claims are NOT safe, see replication below.
- MuJoCo transfer: wind left -> settles +15.8 +/- 8.7 deg off upwind; wind right -> +15.2 +/- 11.0 deg.
  Hand decoder in MuJoCo: ~1 deg. So a ~15 deg sim-to-sim offset, likely surrogate drift mismatch
  (fit +12 deg/s vs +19 deg/s seen in the MuJoCo no-wind run). --bias_lo/--bias_hi is the intended fix; not yet shown to work.

### Replication: FAILED so far

Same config, seed 1: mean return ~0 through episode 111 (seed 0 had taken off by episode ~60).
Drift-randomized run, seed 2: also ~0 through episode 110. Both runs were cut off by the session, not finished.
So the seed-0 result is one lucky seed until shown otherwise. Likely cause (hypothesis, not tested): Adam's per-coordinate
normalization moves all ~149 correlated DN weights by ~lr per step regardless of signal, so noise dominates.
Things to try: plain SGD with global gradient-norm clipping, batching 4-8 episodes per update, fewer features
(e.g. only DNs whose rate differs L vs R), 3+ seeds before reading any weight.

### Prior work (checked Sep 2026, not exhaustive)
- Eon Systems (Mar 2026): FlyWire LIF (Shiu et al.) + NeuroMechFly, DN readout. Essentially the base pipeline here.
- FlyGM (Tsinghua, arXiv 2602.17997, Feb 2026): connectome as a trainable graph network, RL on flybody.
- NeuroMechFly v2 (Wang-Chen et al. 2024): RL navigation controllers + connectome-constrained visual model.
Difference here: the published spiking model stays frozen; only the DN readout is learned by a reward rule.
No claim of novelty beyond that.

## flybody (TuragaLab) vs flygym (NeuroMechFly): both, in two environments

Answer to the obvious question: the closed loops above run on **flygym / NeuroMechFly v2**, not flybody. flygym ships a
CPG walking controller, so a 2-number descending drive is enough to make the fly walk. flybody has no leg CPG: its
walking policies are trained by imitation of reference data, so "brain -> legs" there needs either that reference dataset
or a gait controller of your own. flybody's flight side does ship a wing-beat pattern generator (WPG) with a built-in
approximate pattern, which is why the flybody work here is a flight preparation.

The two packages pin incompatible numpy (flygym >=2.0, flybody ==1.26.4), so they cannot share one environment:

```bash
# environment A (everything above): flygym 1.2.1, numpy>=2, numba>=0.67, dm_control (latest), mujoco 3.13
pip install -r requirements.txt
# environment B (flybody): numpy==1.26.4, numba==0.60.0, mujoco 3.9, dm_control, flybody
python -m venv venv_flybody
git clone https://github.com/TuragaLab/flybody.git
venv_flybody/bin/pip install "numpy==1.26.4" "numba==0.60.0" pandas pyarrow dm_control mediapy h5py
venv_flybody/bin/pip install -e ./flybody
```

The brain (numpy + numba + pandas only) runs in both. Verified in environment B: `flight_imitation()` 12-dim action,
`walk_on_ball()` 59-dim action, both step headless with EGL at ~300 steps/s.

### flybody_rig.py: tethered flight arena (PARTIALLY WORKING, do not trust yet)

The classic closed-loop flight-arena preparation: fly rigidly tethered (walker attached with no free joint), wings beaten
by flybody's WPG, steering by stroke-amplitude asymmetry, yaw torque read off the tether and integrated into a virtual
heading that is fed back to the antennae. No flight stabilization policy needed, nothing falls over.

What works: the rig builds, wings beat, and torque responds to the turn command. Two real bugs were found and fixed
while testing: wing actuators take normalized [-1, 1] units (raw WPG angles up to 1.4 rad were being clipped, which
destroyed the modulation), and the torque average must be locked to a whole number of wing beats or the stroke cycle
aliases it.

What does NOT work yet, measured (k_amp=0.25, 60 decision steps, mean of last 30):

| turn command | mean yaw torque | sd |
|---|---|---|
| -0.80 | -58 | 5.7 |
| -0.40 | +82 | 59 |
| 0.00 | +162 | 3.2 |
| +0.40 | -365 | 22 |
| +0.80 | -1843 | 0.7 |

Monotone (and steep) from -0.4 to +0.8, but the -0.8 point breaks the ordering and there is a large torque bias at
turn=0. So the tether torque is not yet a trustworthy steering readout and the closed loop is NOT wired up to it.
Next things to check: whether MuJoCo's ellipsoid fluid model is actually active on the wings outside flybody's task
wrapper (the task may set flow parameters or a control callback this rig skips), and whether cfrc_ext on the thorax is
the right channel versus an explicit torque sensor at the tether.

## The male CNS connectome: the piece that would make this genuinely new

Every result here stops at descending neurons, because FlyWire v783 is a brain only: no ventral nerve cord, so no leg
motor neurons. The gait comes from a CPG, not from the connectome. The male CNS connectome (neuPrint `male-cns:v1.0`,
Berg et al., Cell 2026, 176k neurons including the nerve cord) does contain the leg motor neurons, which is what would
let the loop run brain -> VNC -> motor neurons -> MuJoCo muscles, with no CPG anywhere. As far as I can tell that has
not been done: fly-brain-minecraft decodes descending neurons into mob commands with no physics, flybody uses trained
policies, and the work here uses a CPG.

neuprint.janelia.org is blocked from my sandbox (`host_not_allowed`), so I could not fetch that dataset or write code
against its real schema. `blendi-remade/fly-brain-minecraft/tools/fetch_neuprint.py` is a working reference fetcher
(anonymous Cypher access, no token) if you want to pull it on your machine. Adapting it means: same CSR format as
connectome.py, `superclass:vnc_motor` neurons as the output layer, and a motor-neuron-rate to muscle-activation map onto
flygym's or flybody's actuators.

## Model

- Neurons: dv/dt = (v0 - v + g)/20ms, dg/dt = -g/5ms, v0 = v_reset = -52 mV, v_th = -45 mV, refractory 2.2 ms, delay 1.8 ms, dt 0.1 ms, exact integration.
- Synapses: w = 0.275 mV x signed synapse count. Sign from predicted neurotransmitter (as packaged by Shiu et al.).
- Input: Poisson kicks of 68.75 mV (forces a spike) at the given rate.

## What is biology, what is glue

| part | status |
|---|---|
| connectome, neuron model | published (FlyWire; Shiu et al. 2024) |
| JO-C/E as wind sensors | published (Yorozu et al. 2009) |
| JO -> DN routing | computed by the connectome model, not tuned |
| wind -> JO rate encoding | glue: r = 20 + 180*max(0, sin(angle)) Hz, same rate for all neurons on a side |
| DNb05/DNb06/DNg29 as ipsilateral steering DNs | ASSUMPTION. Their steering role is not established. DNa01/DNa02 (known steering) are barely recruited by JO |
| per-side calibration | glue. Right JO->DN pathway is ~2.8x stronger than left in this model |
| forward speed | glue. DNp09 (P9) and MDN never fire from wind input, so speed is a constant baseline |
| leg control | flygym CPG + stumbling/retraction rules, not a VNC connectome |

## Known failure: odor/taste input

Driving any olfactory or gustatory population triggers a self-sustaining ~10k-neuron attractor (mostly
Kenyon cells). The output is identical regardless of which side is stimulated and it persists after
stimulus offset. Not fixed by: pruning KC-KC and ORN-ORN edges, zeroing DA/5-HT/OA outputs, adaptive
threshold (d_a 1-3 mV), or scaling all weights to 0.5x. So odor taxis does not work through this model as-is.

## Why not Janelia hemibrain

The hemibrain misses the SEZ/GNG, where most descending neurons and JO targets live, so it cannot close
this loop. It also needs a neuPrint token. Janelia's MANC (nerve cord) is the logical replacement for the
CPG leg controller.

## Next

- Replace the CPG with a MANC-based VNC model.
- Fit the wind -> JO encoding to recorded JO responses.
- Solve the olfactory attractor (e.g. APL-KC inhibition, conductance-based synapses).
