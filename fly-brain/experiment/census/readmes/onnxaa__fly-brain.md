# Fly Brain 🪰 — whole-brain *Drosophila* in code

> Real FlyWire connectome, frozen data-only: **138,639 neurons / 15,091,983
> synapses**. Learns, sleeps, sees, smells. Python API + 1:1 superfast C++
> twin (16× load, 8× train).
> `github.com/onnxaa/fly-brain` — CC BY-NC 4.0 (non-commercial).

**Core rule (`pure` mode, the default): 100% of topology, Dale signs and |w|
come from the data.** Only protocol constants are free (stimulus drive, KC
top-k 5%, DAN anti-Hebb 0.85, thresholds). Anything that breaks the rule lives
in the explicitly opt-in **X zone** and is logged in a deviation ledger.

> **Data license: CC BY-NC 4.0 — non-commercial use only.**

## What this is

- `fly_api.py` — the whole thing behind one class, `FlyBrainAPI(mode="mb"|"full")`.
  `mb` = mushroom-body circuit (6,289 neurons, ~50 steps/s, interactive).
  `full` = entire brain (~1 s/step, ~1 GB RAM, needs the parquet).
- A behavior readout stack (odor preference, tropotaxis steering, motor/lateral
  readouts), a plasticity stack (reward/punishment, protective DAN, SHY sleep,
  autonomous sleep, circadian TTFL, optional short-term depression via
  set_std() - OFF by default, protocol not data), and a validation battery (~20 assay scripts
  with `PASS-` verdicts, numbers in `results/`).

## How it works

**Forward.** Pure diffusion over the real graph, no learned parameters:
`a = ReLU(Σw·a_pre / fan_in − thr) + drive`, 1–2 hops for mushroom-body
readouts, up to 4 for deep (descending/motor) readouts. Fan-in scaling
(`fan_abs.npz`) keeps total drive bounded — this is why shallow paths are stable
and very deep chains attenuate (documented limit, worked around with spiking).

**Smell (real).** 6 odors from the DoOR 2.0 consensus matrix (691×78, inhibition
kept), mapped ORN→glomerulus via `door_mappings.csv`, broadcast to 2,279 ORNs
(`door_real.py` → `door_odors.npz`). Geosmin CAS corrected to 16423-19-1.

**Learning.** `train(reward/punish)` = whole-graph R-Hebb (±2% + renorm) plus
DAN anti-Hebb LTD on KC→MBON (Huang 2024: PAM/slab-avoid for reward, PPL1 for
punishment). `gated=True` (default) scales depression by KC uniqueness against
registered codes (`x_remember`) — shared memory protected (conflict retention
117%), with zero codes it is bit-identical to the legacy slab.

**Memory.** `sleep()` = SHY homeostatic downscaling toward baseline; `forgetting
curve +2.61→+0.83`, identity drift 0.03%. `enable_auto_sleep()` = Borbély
two-process (pressure from KC activity + light zeitgeber, hysteresis bouts,
drive gating ×0.2). `enable_clock()` + `tick_clock(hours)` = artificial Goldbeter
TTFL (free-run 23h, LD entrainment); only biochemistry outside the connectome,
fed into the correct M (s-LNv/l-LNv) vs E (LNd/DN1) neurons. **Clock time flows
only through `tick_clock`** — behavior steps never advance it.

**Vision.** `image=` drives R1-6/R7/R8 photoreceptors (10,582 cells) — each R
samples the input at its own receptive field from real pos_x/pos_y
(rank-normalized, bilinear + Gaussian RF, any HxW, no pixel grid); downstream
ME/LO/LC/DN run through the real graph. No lens/ommatidial optics model.
Motion (Reichardt) is readout-only, never
injected. Spiking seeing in `see_lif.py`: graded early vision (38,871
non-spiking cells, tonic release) + full-brain LIF — flash drives LC 0→21Hz
and DNs; loom recruits DNp01 2x over recede.

**Activation.** Two rate modes: `relu` (default, fast legacy `max(0,x)`) and
`lif` (`set_activation("lif")`, saturating LIF-shaped
`SAT*(1-exp(-x/SAT))`, Shiu `t_mbr/t_rfc` behind the shape; exact log-form
rejected — measured to crush contrast on fan-scaled drives). Weak-drive
numbers match within ~2% (all validations transfer); strong drives saturate
(5x overload: MB 723→198); learning direction preserved. Spike timing stays
in `see_lif.py`/Brian.

**Spike mode (3rd).** `set_activation("spike", Tms=200, seed=7, wdrv=68.75,
ainc=4, rmax=150, adapt=0.2, burn=50)` — full LIF sim 1:1 with `test_lif.py`
v2 (g-reset, 2-step refractory/delay, signed weights, spiking APL x4, graded
early vision + tonic release, sensory adaptation, SFA, onset burn-in); same
dict in Hz. mb works (halves: ALPN 65Hz, KC ~15%, MB d=+3.5Hz). Full runs
(~1min/200ms) with an honest envelope: strong sustained drives ignite
recurrent loops (geosmin: ALPN ~100Hz, KC ~77%, MBON ~130Hz saturate), weak
drives die — a bistable cliff, not a bug (APL cache verified, inhibition
genuinely overwhelmed: ORN→ALPN feedforward too weak at physiological rates
while ALPN-loop feedback too strong once firing). Knobs tame it partially
(SFA: MBON 137→15Hz). Full-brain spike gain control (STD/LN co-tuning) is
open work — no reference data exists (Shiu validated MB only).

**Spikes.** `test_lif.py` = NumPy port of the Brian/Shiu equations (g-reset,
refractory, delay, signed weights, spiking APL): KC 5.1% vs Brian 6.5%.
`loom_lif.py` runs the same dynamics on the full 138k brain (~100 s/500 ms):
sugar→MN9 60Hz, loom→DNp01/DNp04, conflict suppression 100%.

**Growth (X zone).** `x_grow_assoc` (any modality pool → any target),
`x_neurogenesis` (interference-gated), `x_prune_kc`, `x_add/cut_edge`,
`x_report()` ledger. 10k-neuron tranche protocol keeps 97% of learning
performance; touch modality goes from unlearnable (d=0) to learned.

## Purpose

A testable platform for: associative learning curves, reversal, hard/easy
discrimination, extinction, generalization vs DoOR similarity, mixture
tradeoffs, odor-vs-threat conflict (LC4/LPLC2 drive → escape synergy + MN9
suppression), lateral tropotaxis (`turn_olf`), sleep/forgetting, circadian
gating, and continual growth — all against a frozen-data identity check
(topology, Dale 100%, weight drift <5%).

## Use

```python
from fly_api import FlyBrainAPI
mb = FlyBrainAPI(mode="mb")
mb.step(odor="A")["MB_pref"]; mb.train(odor="A", reward=1.0)

fly = FlyBrainAPI(mode="full"); fly.enable_scaling()
o = fly.step(odor="ethyl_hexanoate", odor_left="geosmin", image=img, mech=v)
fly.train(odor="ethyl_hexanoate", reward=1.0)
fly.save_weights("w.npz")
```

```python
# female whole-CNS (BANC) and male whole-CNS (MCNS): intact brain->VNC
banc = FlyBrainAPI(mode="banc")   # 150k neurons / 11M edges
male = FlyBrainAPI(mode="mcns")   # 165k neurons / 25.6M edges
o = male.step(odor="geosmin", image=img, mech=v)
o["BANC_leg_L"], o["BANC_wing"]   # intact motor readouts, one animal

# deep vision: active scaling keeps Exc chains alive (default static)
male.set_scaling("active"); male.set_hops(4)
o = male.step(image=img)          # DN/legs respond, lateralized

# spikes: own APL/graded sets per dataset (mcns pre-calibrated SFA)
male.set_activation("spike"); o = male.step(odor="geosmin")  # Hz dict

# EB ring attractor (banc validated, mcns functional/EXPERIMENTAL)
banc.set_state(0.5)
o = banc.step(cx_cue=cue50)      # landmark -> CX_bump lands (+/-6 ranks)
o = banc.step()                  # dark: bump holds (CX_bump/CX_bump_amp)
o = banc.step(angvel=3.0)        # velocity walks bump, correct sign

# same in spikes (deterministic tonic regime recipe)
banc.set_activation("spike")
banc.set_cx_gain(spk=2.0, spk_inh=2.5, std_u=0.08, bg=0.0, plat=1.0, tonic=0.06)
```

Learning is real synapses now: `train(odor, reward/punish)` drives PAM/PPL
(`dan_rew/dan_pun` US pathway) and the measured DAN activity GATES KC->MBON
depression (Handler/Hige compartment logic, self-calibrated; `dan_block`
control gives zero learning; sleep tags protect fresh traces 95% vs 59%).
Inputs combine freely: `odor` (DoOR name / 'A'/'B' / vector), `odor_left/right`,
`image` (full/banc retinotopic, mcns homology+eye-split), `mech`,
`mech_left/right`, `alpn` (full only), `dan_rew/dan_pun`, tastes
`sugar/bitter/water/ir94e` (full split; banc/mcns single GRN pool).
Outputs: `MB_pref/app/avo`, `MBON`, `KC_active`, modality means,
`ALPN_L/R`, `ORN_L/R`, `MECH_L/R`, `turn_olf`, `DN_L/R`, `turn`, `motor_pref`,
`EFFERENT(1481)` (full), `BANC_motor/leg_L/R/wing/neck` (banc/mcns),
`EI_sum`, sleep/clock state. Vision polarity `vpol`: `lum` (default, raw
drive incl. real R7/R8->L histamine inhibition), `on`/`off` (clean labeled
lines: L1 increments / L2 decrements only, bg=0.5 — R cross-talk deliberately
excluded, scales are incommensurate; C++ `--vpol 0/1/2`, bit-parity).

## Validation (measured)

Topology N/E exact; Dale 100%; drift 0.12%, corr 0.99. DoOR→ALPN sim-vs-1hop
corr 0.60–0.94. Acquisition d −5.65→+7.89; reversal crosses zero in 1–2 trials;
30-trial rewire holds at +20.86 with 0.06% drift. Lesions, retina symmetry,
tropotaxis 0.20→0.90 all PASS. Full numbers: `results/*.txt`,
checkpoints: `weights_registry.json`.

## MCNS (real MALE whole-CNS, one animal) ⭐ newest

`FlyBrainAPI(mode="mcns")` runs the MCNS v1.0 connectome (Berg et al., Cell
2026): **165,122 traced neurons / 25,563,096 edges**, brain + VNC in ONE male
animal with intact neck connective. Frozen topology + Dale from per-body NT
consensus (ACh=+1, GABA/glutamate/histamine=-1, monoamines=+1 protocol).
KC 4064 / MBON 97 (61,210 KC→MBON) / DAN PAM+PPL1; valence approach 75 +
avoid 27 ported from FAFB by MBON type name; DoOR 6 odors via `ORN_<glom>`;
motor leg (Pro/Meso/MetaLN 161/158 L/R), wing 34, neck (CvN) 4.

Measured (`test_mcns.py` PASS, ~2 s/step): geosmin MB=-4.38 vs ethyl -10.87,
reward d=+1.51 / punish d=-0.90, mech→DESC 0.18/0.15 → legs 0.049/0.058 +
wing 0.070 + neck 0.083 (intact chain). Build: `build_mcns.py` (streams
151M-row weights, feeders git-ignored). No vision front-end / clock / C++
twin yet (v2).

## BANC (real female whole-CNS, one animal)

`FlyBrainAPI(mode="banc")` runs the BANC v888 connectome (Bates/Phelps/Kim/Yang,
Nature 2026): **150,808 proofread non-glia neurons / 11,036,557 edges**,
brain + VNC in ONE female animal with intact neck connective — no cross-sex
bridge. Frozen topology + Dale from BANC NT (ACh=+1, GABA/glutamate/histamine=-1,
monoamines=+1 protocol). KC 4130 / MBON 102 (14,681 KC→MBON edges) / DAN split
PAM/PPL1; valence approach 71/71 + avoid 30/25 ported from FAFB via `fafb_match`;
DoOR 6 odors via `ORN_<glom>` suffix (same consensus); motor leg/wing/neck pools.

Measured (`test_banc.py` PASS, 0.5 s/step): ethyl MB=1.116 vs geosmin 0.053,
reward d=+0.023 / punish d=-0.031 (right directions), mech→DESC 0.07/0.10 →
legs 0.048/0.044 + wing 0.058 (intact chain). Odor→legs ≈ 0 (deep chain,
same limit as FAFB DN-turn). Build: `build_banc.py` (streams 11.75M rows,
feeders git-ignored). No vision front-end / clock / C++ twin yet (v2).
Male MCNS v1.0 exists (166.7k, Sept 2026) but its 1–3 GB bulk files don't fit
this machine (1.7 GB free) — queued after disk upgrade.

## VNC (real, MANC v1.2.1)

Full mode + `fly.enable_vnc()` appends the real male nerve cord
(Takemura/Marin/Cheong et al., eLife 2024): **23,650 neurons / 5,303,770
edges / ~31M synapses**, frozen topology + Dale from MANC NT predictions
(ACh=+1, GABA/glutamate=-1 central). Brain DESC drive 499/1322 VNC
descending neurons via a type-matched bridge (196 shared DN types, 2033
pairs — X-zone protocol, coverage 500/1299 brain DESC). New readouts:
`VNC_leg_L/R`, `VNC_wing`, `VNC_neck`, `VNC_motor`, `VNC_desc_mean`.

Measured (`test_vnc.py` PASS): mech→DESC 0.87→VNC_desc 0.035→leg 0.0014,
mech_L lateralizes DN_L 0.064 > DN_R 0.028. Odor→DESC is ~0 in rate mode
(olfactory→neck chain too deep for fan-scaled diffusion — same documented
limit as DN-turn). Build: `build_vnc.py` (feeders git-ignored, re-download
from the public bucket). VNC weights frozen (no train/sleep plasticity v1);
C++ twin has no VNC yet.

## Limits

No lens/ommatidial optics (point sample + Gaussian RF only); motion readout-only, not injected; VNC real but brain↔VNC is cross-sex/cross-animal (FAFB female → MANC male, type-level bridge 38%) and odor→motor still needs the deep chain; DN-turn at
noise floor (steer via `MB_pref`/`turn_olf`); full spiking is NumPy-only
(~100 s/500 ms); rate mode loses deep chains; no forgetting without
sleep; molecular clock/TTFL outside data; DNa02 steering needs LAL drive.
