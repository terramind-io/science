# fly-loop

A closed-loop simulated *Drosophila*: a connectome-derived spiking brain driving a
biomechanical body, doing odour-driven walking.

**Brain** — FlyWire v783 leaky integrate-and-fire whole-brain model (Shiu et al.,
*Nature* 634:210–219, 2024), via [`eonsystemspbc/fly-brain`](https://github.com/eonsystemspbc/fly-brain).
**Body** — [FlyGym / NeuroMechFly v2](https://neuromechfly.org), pinned to **1.2.1**.
**Bridge** — written here. Nobody has released one.

Target hardware: **GTX 1080 Ti** (Pascal, `sm_61`, 11 GB) under WSL2 / Ubuntu 24.04.

---

## Read this first

### The seam: the connectome stops at the neck

**FlyWire covers the brain only.** The leg motor neurons live in the **ventral
nerve cord**, which this connectome does not include. Descending neurons are
therefore the **output boundary** of the connectome-derived part of this system.

Everything below them — the central pattern generator, leg coordination, joint
trajectories — is **hand-written**, ships with FlyGym, and is neither
connectome-derived nor learned.

```
odour (FlyGym physics)
  -> Poisson drive to 2,248 ORNs        [connectome-derived]
  -> 138,639-neuron LIF brain           [connectome-derived]
  -> DNa02 left/right firing rates      [connectome-derived]   <-- THE SEAM
  -> left/right rate asymmetry
  -> steering bias                      [HAND-TUNED, see docs/bridge-parameters.md]
  -> FlyGym CPG walking controller      [hand-written, ships with FlyGym]
  -> leg joint torques -> physics
```

Calling this an end-to-end connectome-driven fly would be false. Roughly the top
half is connectome-derived; the bottom half is a conventional robotics controller.

### The result, stated plainly

The loop runs, and the fly does steer toward the odour — but **the honest
headline is that the connectome's odour-to-steering signal is very weak**, and
one constant I chose is doing a lot of work.

Measured facts, all reproducible from this repo:

1. **Unilateral ORN drive does lateralise DNa02, ipsiversively** — matching
   Rayshubskiy et al. Separation between left-drive and right-drive conditions is
   **+14.5 Hz (3.7σ)**. DNa01's separation is 1.5σ, not usable.
2. **But DNa02 carries a large fixed left-bias pedestal** unrelated to stimulus
   side: driving the *right* ORNs still leaves the *left* DNa02 at 52 Hz while
   the right sits near zero. Calibration puts the pedestal at **+57.6 Hz** against
   a usable slope of only **+8.6 Hz per unit contrast** (R² = 0.73). The connectome
   review predicted this from LAL051, a glutamatergic DNa02 partner with 70 vs 130
   left/right synapses.
3. **Natural odour contrast is far too small to use.** The fly's antennae are
   ~0.3 mm apart; measured inter-antennal contrast is **±1.8%**, which the
   connectome would convert to ~0.26 Hz of DN differential against a **8–17 Hz
   Poisson noise floor**. The bridge amplifies contrast **~55×** to get a usable
   signal. The transduction is real; the stimulus is not natural.
4. **A single DNa02 pair cannot carry a clean steering signal** on behavioural
   timescales. Rate SD is √(r/T): ~12 Hz even at a 400 ms readout window, versus
   an 8.6 Hz signal. SNR stays of order 1, and the trajectories show it — a weak
   directional bias on a meandering walk, not clean taxis.

**Everything I guessed is enumerated in [`docs/bridge-parameters.md`](docs/bridge-parameters.md).**
The most important entry: at `contrast_gain = 12` the odour-dependence test came
back **negative**; at 55 it came back positive. That history is recorded there
rather than quietly overwritten.

### The statistical bottom line

At n=6 per cell, the intact fly's mirror difference is **+11.02 mm, 95% CI
[+0.36, +21.68], p = 0.044** — significant, but only just, with a CI whose lower
bound is nearly zero. Crossing the sensory wiring removes 96% of it (p = 0.95).
Silencing DNa02 removes all of it.

So: **a real but marginal odour-driven steering effect, carried by DNa02, on a
55×-amplified gradient.** Treat it as preliminary. It is not a robust result and
this README should not be read as claiming one.

### Other honest caveats

- **Symmetric drive does not walk straight.** FlyGym's `[1.0, 1.0]` drifts +10.3°.
  There is a baseline turning bias independent of anything we do.
- **The model has no valence machinery.** An odour's sign is imposed by us.
- **Absolute firing rates are not comparable to electrophysiology** — the Shiu
  model assumes zero basal firing. Only relative left-right differences are meaningful.
- **Shiu et al.'s published model was built on v630; this data is v783.** Root IDs
  are not portable (only ~76.6% overlap), which is why neuron identity is resolved
  from a checksummed v783 dump rather than hardcoded.
- **The DNa01/DNa02 literature is two papers from the same lab** (Wilson), using
  different methods. Not fully independent replication.

---

## Results by milestone

| | | |
|---|---|---|
| **M0** | WSL2 + CUDA 12.6 + torch cu126, GPU execution verified on Pascal | done |
| **M1** | Brain on GPU; sugar→proboscis reproduced; benchmarked | done |
| **M2** | FlyGym walking, odour readout, turning modulation, mp4 | done |
| **M3** | Auditable ORN / DNa01 / DNa02 root IDs from a pinned v783 dump | done |
| **M4** | Closed loop, decoupled rates, side-by-side video + DN raster | done |
| **M5** | Ablation: silence DNa02, test whether odour-dependence dies | done |
| **M6** | Optimisation pass + persistent multi-source world | done |

### M0 — the Pascal trap is real, but not where it is usually claimed

`sm_61` is **not in any official PyTorch wheel** and never has been. Both
`torch 2.6.0+cu126` and `2.14.0+cu126` report
`['sm_50','sm_60','sm_70','sm_75','sm_80','sm_86','sm_90']`. An
`assert "sm_61" in get_arch_list()` gate can never pass.

It works anyway because CUDA guarantees cubin compatibility across one minor
revision: the **`sm_60` cubin runs natively on `sm_61`**. Verified with `nvcc`,
PTX stripped so no JIT could mask it. Pin cu126 anyway — but because cu128+ and
CUDA 13.x drop the `sm_60` cubin that is carrying us, leaving only `compute_90`
PTX, and **PTX JITs forward only, never backward**. Details and the measured
compatibility matrix: [`docs/hardware-notes.md`](docs/hardware-notes.md).

### M1 — the paper's result reproduces

21 sugar GRNs @ 200 Hz, 1 s:

| | measured | upstream v783 band | |
|---|---|---|---|
| total spikes | **17,393** | 16,353–17,429 | ✅ |
| active neurons | **403** | 380–416 | ✅ |
| MN9 contralateral | **100 Hz** | must fire | ✅ |
| MN9 other CB0701 | **63 Hz** | — | ✅ |

The contralateral MN9 fires harder than the other — the asymmetry Shiu et al.
report for unilateral sugar GRN activation.

**Throughput: 115 ms of simulated brain time per second of wall clock** at
batch=1 (0.115× realtime, 0.87 ms/step, 1.45 GB VRAM).

**Batching is counterproductive on this GPU** — `batch=4` takes **8× longer in
absolute wall clock** than `batch=1` for the same simulated duration, because
`matmul(dense, sparse_csr.T)` has no efficient batched path. Aggregate throughput
*falls* from 115 to 58 sim-ms/s. Upstream benchmarks to batch=32; that does not
transfer to Pascal.

### M4 — why the full brain, not a subset

Measured, not assumed. At 115 sim-ms/wall-s and 1.45/11 GB VRAM, a 3 s episode
costs ~26 s of brain compute. A hop≤3 ORN→DN subset (~42,400 neurons) would buy
maybe 3× while discarding ~11% of DNa02's input synapses and introducing a second
model needing its own validation. **The measured numbers say we do not need that
trade.** Closed loop runs at 0.013× realtime overall — the brain is ~9× faster
than the full loop, so physics and per-exchange synchronisation dominate.

Rates are decoupled: physics and brain each advance at their own native 1e-4 s
step and exchange information at **200 Hz** (every 5 ms = 50 native steps each).

### M5 — the ablation passes, but read the caveat

Metric is the **mirror difference**: `mean net_y(source left) − mean net_y(source
right)`. An odour-driven fly goes left for a left source and right for a right
source, so this is large and positive. A fly driven by the bridge and the fixed
pedestal does the same thing regardless, so it is ~0. Three seeds per cell,
2 s episodes, calibration held **fixed** across conditions (re-calibrating per
condition would silently re-centre the silenced fly and hide the effect).

| condition | mirror delta | vs intact |
|---|---|---|
| intact | **+14.15 mm** (effect 1.61) | baseline |
| DNa02 silenced | **+0.00 mm** | **0%** |
| DNa01 silenced (specificity control) | **+22.54 mm** | 159% |

Silencing DNa02 abolishes odour-dependence; silencing DNa01 — which M4a showed is
*not* usable as a readout (1.5σ) — does not. By the stated criterion, it passes.

**The caveat you should not skip.** The silenced trajectories are
`[-4.57, -4.55, -4.69]` for *both* source positions — identical to two decimals.
That is not the effect fading; with DNa02 silenced the bias pins at −1.000, the
fly runs a fixed open-loop motor program, and deterministic physics does the rest.
Since the bridge reads **only** DNa02, removing it necessarily removes every path
from odour to motor. **This test could not have failed**, which makes it a
consistency check rather than evidence.

### M5b — the control that could fail

Cross the sensory wiring: the left antenna's odour drives the **right** ORN
population and vice versa. Nothing downstream changes — same connectome, same
DNa02 readout, same bridge constants, same calibration. The fly still walks and
still responds to odour, so this control *can* fail while producing behaviour.

If the connectome is genuinely transducing the lateralisation, DNa02's ipsiversive
response must now point the wrong way and the mirror difference must **invert**.

| | mirror delta | |
|---|---|---|
| intact | +14.15 mm | baseline |
| **crossed wiring** | **+0.28 mm** | **98% reduction** |

**Partial.** Crossing the wiring destroys the steering — which rules out the worst
case, that the bridge manufactures the behaviour on its own. But it does not
cleanly *invert* it, which is what strong evidence would look like. The crossed
condition's variance is large (`srcR = [21.31, −16.23, 14.99]`, pooled SD 14.24),
so at three seeds we cannot distinguish "abolished" from "inverted".

### M5c — the statistics, because n=3 was not enough

The M5 pass was reported at n=3 per cell. Run properly, that is
t = 1.98, df = 4, **p ≈ 0.12 — not significant.** An effect size of 1.61 says
nothing about how many samples produced it. M5c adds seeds 3–5 to both the intact
and crossed conditions (n=6) and runs a Welch t-test.

| condition | mirror delta | 95% CI | Welch t | p | |
|---|---|---|---|---|---|
| **intact** | **+11.02 mm** | [+0.36, +21.68] | +2.321 (df 9.5) | **0.044** | significant |
| **crossed wiring** | −0.41 mm | [−16.03, +15.21] | −0.059 (df 8.9) | 0.954 | n.s. |

Crossing the wiring removes **96%** of the effect.

**The result holds, but read the confidence interval.** p = 0.044 is marginal and
the lower bound of the CI is **+0.36 mm** — nearly zero. This is a real effect at
the level of "publishable as preliminary," not a robust one. It rests on n=6,
2 s episodes, and `contrast_gain = 55`.

**What the three tests establish together:** the steering depends on DNa02
(M5) *and* on the sensory wiring being correct (M5b/M5c). The second is the load-
bearing one, because unlike the silencing ablation it was free to fail — the fly
still walked and still responded to odour with the wiring crossed, and the
odour-dependence disappeared anyway. That is the strongest evidence here that the
connectome's lateralisation, not the bridge, is carrying the signal.

**What they do not establish:** the crossed condition *abolishes* the effect
rather than *inverting* it, so the sign is not confirmed to pass through the
connectome — only that correct wiring is necessary. Distinguishing those would
need more seeds or longer episodes.

---

### M6 — making it fast enough to live in, and a world to live in

**Every optimisation here is bit-exact and was verified before adoption.** The
gate is M1: `FastBrain` reproduces it *exactly* — 17,393 spikes, 403 active
neurons, the same numbers, not merely in band — and is step-for-step identical to
the reference over 500 steps at a fixed seed.

| change | measured | exact? |
|---|---|---|
| int32 CSR indices | 0.686 → 0.565 ms SpMV | 96/96 bit-identical |
| ring-buffer delay line | 0.0733 → 0.0110 ms | 60/60 identical |
| memoised `Fly.get_observation` | 3.306 → 2.743 ms/step | max\|Δ\| = 0.0 in qpos |
| render moved out of the loop | −158 ms/exchange | output unchanged |
| **closed loop** | **0.0137× → 0.0257×** | **1.88×** |

#### Profiling overturned the obvious hypotheses

Rendering is **43%** of the loop and physics **42%**; the brain is **14%**. So
even an infinitely fast brain buys 1.16×. `torch.roll` — the intuitive
suspect, copying 21 MB per timestep — is **1.2%**, and the per-step spike
recording is **0.3%**. Both were "obviously" the bottleneck and neither is.

Three measurement errors worth recording, since each looked like a result:

- The first render benchmark timed **skipped frames**. `Camera.render()`
  early-outs unless enough *simulated* time has passed (`camera.py:223`), so a
  tight loop of `render()` calls mostly measures the early-out. Per frame
  actually produced it is ~158 ms and **essentially independent of resolution**
  (155.6 ms at 320×240 vs 158.7 at 640×480).
  I then attributed that to dm_control overhead, on the strength of a bare
  `mujoco.Renderer` managing 7.7–10.2 ms. **That was also wrong** — the toy
  benchmark used a 3-geom box-and-plane model. On the actual 71-geom mesh fly,
  a bare `mujoco.Renderer` costs **163 ms/frame** too. The expense is the
  model's geometry, not dm_control and not rasterisation. Moving rendering off
  the critical path is still worth 43%; it just does not get cheaper offline,
  you only pay it for the frames you actually want.
- `solver iterations=1000` (vs MuJoCo's default 100) looked alarming.
  `solver_niter` is **2** — Newton converges in two. Irrelevant.
- The first two attempts at the observation patch were **silent no-ops**:
  patching the instance cannot intercept `super().get_observation()`, and
  patching `Simulation` misses `post_step`, which calls `Fly` directly.

#### Refused, deliberately

FlyGym registers **2,268 collision pairs of which only 1,182 are unique** —
`_init_self_contacts` de-duplicates on the *ordered* key `f"{geom1}_{geom2}"`,
so both (A,B) and (B,A) are added. Removing the 1,086 duplicates would cut
broad-phase work, but over 3,000 walking steps no duplicated pair was ever in
contact, so the saving is unproven — and if legs ever *do* touch, removing one
changes the contact force. That is a dynamics change, not an optimisation.
Worth reporting upstream.

#### The world

`LivingWorldArena`: a wind-shaped Gaussian plume over N sources, depletable
reserves with regrowth, and a **toroidal odour field by minimum image** — the fly
is never teleported, so there is no discontinuity in the brain's input and no
bound on lifetime. `OdorArena` already supports N sources × K dimensions; the
subclass exists only because `diffuse_func` receives a scalar distance and
therefore cannot express direction.

Two traps handled: mutating `peak_odor_intensity` is a **silent no-op**
(`get_olfaction` reads a cache built in `__init__`), and `calibrate_gain` pins the
plume's on-axis intensity to the old r⁻² value at a reference radius — without
it, swapping the field would quietly rescale `intensity_to_hz` and move the
result while looking like a pure environment change.

#### 60 s of fly life

Path 1112.6 mm, closest approach to FOOD_B **14.8 mm from a start 83 mm away**,
sensed odour up **10.4×**. Zero source visits — the feed radius is 3 mm.

The stronger evidence is within-run. Across 12,000 exchanges, the correlation
between inter-antennal odour contrast and steering bias is:

```
lag(exch)    0      60     100     140     200     300
   r      -0.036  +0.106  +0.182  +0.187  +0.029  -0.089
```

**Peak r = +0.187 at lag 140, p = 0.016** (rotation permutation — shuffling
would have manufactured a p-value, since both series are autocorrelated).

#### …and the null control says that is not enough

The odour-blind run (`--blind`) drives the ORNs with the same total rate and
**zero** left/right contrast, so odour information cannot reach the DNs. I
predicted its correlation "must be ~0 by construction". It is not:

| | peak \|r\| | at lag | p |
|---|---|---|---|
| intact | 0.187 | 140 | 0.016 |
| **blind** | **0.082** | 60 | 0.274 |

The pre-registered bar was *intact > 3× blind*. 0.187 < 3 × 0.082, so **this
fails, and the approach to FOOD_B should be read as drift, not taxis.**

The null exposed a confound I had not thought of, and my "structurally zero"
claim was simply wrong: **steering causes contrast.** Turning changes which
antenna faces the gradient, so bias → heading → contrast is a feedback path that
exists whether or not odour drives steering. Any correlation between bias and
contrast is therefore bidirectional by construction.

What remains suggestive but unproven: the intact fly's sensed odour rose
**10.4×** against the blind fly's **1.5×**, and the lag profiles differ in shape
(intact starts *negative* at lag 0 and rises to a delayed peak; blind starts
positive and stays flat). Both are n=1 per condition. Settling it needs
replicates, at ~39 min of wall clock each.

**What this is not.** The fly has no valence machinery: "aversive" is a sign
imposed in numpy, and depletion is arena bookkeeping the brain cannot perceive
except as concentration. This is a persistent environment, not foraging — and on
the current evidence, not demonstrated odour tracking either.

## Layout

```
brain.py              steppable wrapper around the v783 LIF model
bridge.py             THE BRIDGE -- every hand-tuned constant lives here
m1_sugar.py           M1 validation + benchmark
m2_body.py            M2 body, odour readout, turning, positive control
m3_neurons.py         M3 neuron identification -> neurons.v783.json
m4a_orn_dn.py         M4 go/no-go: does ORN drive lateralise the DNs?
m4_loop.py            M4 closed loop + mirrored odour-source test
m4_video.py           side-by-side video + trajectory figure
m5_ablation.py        M5 ablation with specificity control
neurons.v783.json     auditable root IDs, with source checksums
docs/hardware-notes.md      Pascal / CUDA / WSL2 findings
docs/bridge-parameters.md   every place I guessed
setup/                numbered, idempotent environment scripts
external/fly-brain/   upstream connectome model (git clone)
```

## Setup

```bash
# Windows, elevated -- enables virtualization, installs WSL2. Then REBOOT.
powershell -ExecutionPolicy Bypass -File setup/windows/enable-wsl.ps1

# inside WSL
sudo bash setup/01-base.sh          # user, wsl.conf, toolchain, GL/EGL
sudo bash setup/02-cuda.sh          # CUDA 12.6 + sm_61 compile-and-execute gate
bash setup/03-conda-torch.sh        # miniforge, torch cu126, Pascal gate
bash setup/07-flygym.sh             # flygym 1.2.1, re-verifies the gate
```

Then, in order: `m1_sugar.py`, `m2_body.py`, `m3_neurons.py`, `m4a_orn_dn.py`,
`m4_loop.py`, `m5_ablation.py`.

### If Valorant stops working

Enabling WSL2 turns on the Hyper-V hypervisor, which Riot Vanguard may reject.
You do **not** need to uninstall anything:

```powershell
setup/windows/toggle-hypervisor.ps1 -Mode Off    # gaming; reboot
setup/windows/toggle-hypervisor.ps1 -Mode Auto   # WSL2;   reboot
```

---

## Provenance

Connectome data is FlyWire v783 (Dorkenwald et al.; Schlegel et al.). The LIF
model follows Shiu et al., *Nature* 2024. Respect the upstream licences and
citation requirements of both.
