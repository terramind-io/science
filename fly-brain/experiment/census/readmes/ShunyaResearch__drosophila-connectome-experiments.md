# Drosophila Connectome Experiments

A [Brian2](https://brian2.readthedocs.io/) leaky integrate-and-fire (LIF) model of the
[FlyWire](https://codex.flywire.ai/) *Drosophila* connectome — the **brain** half of a
connectome → body pipeline whose other half is [NeuroMechFly v2](https://neuromechfly.org/).

The LIF model is a reimplementation of **Shiu et al., *Nature* 634:210–219 (2024)**, following
the reference code at [`philshiu/Drosophila_brain_model`](https://github.com/philshiu/Drosophila_brain_model)
(vendored under `data/dbm/`).

```
src/
  lif_model.py            the model: parameters, connectome loading, network construction
  neurons.py              named neuron sets (21 sugar GRNs, MN9, SEZ cell types)
  run_sugar_milestone.py  milestone 1 experiment
data/dbm/                 vendored connectome (FlyWire v630 + v783 parquet) + reference impl
results/                  spike parquet + firing-rate CSV + log, one set per run
```

## The model

Per neuron, integrated only outside the refractory period:

```
dv/dt = (v_0 - v + g) / t_mbr     : volt
dg/dt = -g / tau                  : volt
```

Spike when `v > v_th`; reset `v = v_rst; g = 0 mV`; then refractory for `rfc`. A presynaptic
spike does `g += w` after a fixed delay `t_dly`, with `w = (synapse count) × (NT sign) × w_syn`
— synapse count from the FlyWire connectivity table, sign from the predicted neurotransmitter
(ACh → +1, GABA/Glu → −1). External ("optogenetic") drive is a `PoissonInput` onto `v`.

| symbol | value | meaning | source |
|---|---|---|---|
| `v_0`, `v_rst` | −52 mV | resting / reset potential | Kakaria & de Bivort 2017 |
| `v_th` | −45 mV | spike threshold | Kakaria & de Bivort 2017 |
| `t_mbr` | 20 ms | membrane time constant (C·R) | Kakaria & de Bivort 2017 |
| `tau` | 5 ms | synaptic decay | Jürgensen et al. 2021 |
| `t_rfc` | 2.2 ms | refractory period | Lazar et al. 2021 |
| `t_dly` | 1.8 ms | synaptic transmission delay | Paul et al. 2015 |
| `w_syn` | 0.275 mV | voltage step per synapse | free parameter, fit in Shiu et al. 2024 |
| `dt` | 0.1 ms | integration step (`method='exact'`) | — |

Connectome sizes as loaded: **v630** — 127,400 neurons, 14,687,178 edges (the materialisation
the paper used); **v783** — 138,639 neurons, 15,091,983 edges.

## Findings

### Milestone 1 — sugar activation drives the feeding motor neuron MN9

Reproduces the feeding experiment of Shiu et al. Drive the 21 right-hemisphere sugar-sensing
gustatory receptor neurons (Gr64f class) with Poisson input and check that **MN9** — the
proboscis motor neuron for pharyngeal pumping — fires, against an otherwise identical
unstimulated control.

```bash
python3 src/run_sugar_milestone.py --dataset 630 --n-run 30 --rate 150 --n-proc 5
```

**Result (v630, 150 Hz, 30 trials × 1 s):**

| | firing rate |
|---|---|
| MN9, sugar-stimulated | **83.47 ± 4.60 Hz** |
| MN9, unstimulated control | **0.00 Hz** |
| neurons active, sugar condition | 431 (21 stimulated + 410 downstream) |
| neurons active, control | 0 |
| total spikes recorded | 409,883 |

**Interpretation.**

- **The circuit works end to end.** Stimulating a sensory population 410 synaptic partners
  away from MN9 reliably drives the motor neuron. The sugar → feeding pathway is present and
  functional in the connectome-constrained LIF network, matching the paper's optogenetically
  validated result.
- **Every spike is causal.** The network is completely silent in the control condition
  (0 active neurons, 0 Hz everywhere). There is no background activity, no self-sustaining
  loop — so all 409,883 spikes in the stimulated condition are directly attributable to the
  sugar drive. This is a clean stimulus–response assay with zero baseline to subtract.
- **The stimulated neurons track their drive.** The 21 sugar GRNs fire at 140–154 Hz under
  150 Hz Poisson input (they are given zero refractory period so the imposed rate is not
  clipped); the highest-rate downstream neurons sit just below them (~110–140 Hz), consistent
  with strong monosynaptic relay before divergence dilutes the signal.
- **Cost.** ~112 s wall time (75 s stimulated + 37 s control) on 5 CPU cores, ~3 GB per
  worker, no GPU. A whole-brain spiking model is tractable on a laptop.

**Outputs** (tag = `630_150Hz_30trials`):

- `results/spikes_sugar_<tag>.parquet` — one row per spike (`t`, `trial`, `flywire_id`, `exp_name`)
- `results/rates_sugar_<tag>.csv` — mean ± sd firing rate per neuron per condition, with cell-type names
- `results/milestone1.log` — full run log

### What has *not* been tested yet

- **v783.** Milestone 1 runs only on v630, because one of the 21 published sugar root ids does
  not resolve in the v783 materialisation (FlyWire root ids change between snapshots). A v783
  run needs the sugar set re-identified by annotation rather than by hard-coded id.
- **Inhibition / silencing.** `lif_model.silence()` (zeroing a neuron's outgoing synapses) is
  implemented but no experiment exercises it.
- **Any body coupling.** Nothing in this repo touches NeuroMechFly yet — see TODO.
- **Rate sensitivity.** Only 150 Hz drive has been run; the paper sweeps rate.

## Requirements

`brian2` (tested 2.9.0), `pandas`, `pyarrow`, `numpy`, `joblib`. A working C compiler is needed
for Brian2's Cython code generation; without it the model still runs, far more slowly. Each
parallel worker holds a full copy of the network (~3 GB), so size `--n-proc` to RAM.

---

## References

**Simulator**

- Stimberg M, Brette R, Goodman DFM (2019). *Brian 2, an intuitive and efficient neural
  simulator.* eLife 8:e47314. doi:[10.7554/eLife.47314](https://doi.org/10.7554/eLife.47314)
- Brian 2 documentation — <https://brian2.readthedocs.io/>
- Nowotny T, Goodman DFM, Stimberg M (2020). *Brian2GeNN: accelerating spiking neural network
  simulations with graphics hardware.* Sci Rep 10:410. — GPU backend option.
- Alevi D, et al. (2022). *Brian2CUDA: Flexible and Efficient Simulation of Spiking Neural
  Network Models on GPUs.* Front Neuroinform 16:883700. — GPU backend option.

**Connectome**

- Dorkenwald S, et al. (2024). *Neuronal wiring diagram of an adult brain.* Nature
  634(8032):124–138. doi:[10.1038/s41586-024-07558-y](https://doi.org/10.1038/s41586-024-07558-y)
- Schlegel P, et al. (2024). *Whole-brain annotation and multi-connectome cell typing of
  Drosophila.* Nature 634(8032):139–152.
  doi:[10.1038/s41586-024-07686-5](https://doi.org/10.1038/s41586-024-07686-5) —
  cell-type / class annotations used to pick stimulation and readout populations.
- Eckstein N, et al. (2024). *Neurotransmitter classification from electron microscopy images
  at synaptic sites in Drosophila melanogaster.* Cell 187(10):2574–2594.
  doi:[10.1016/j.cell.2024.03.016](https://doi.org/10.1016/j.cell.2024.03.016) — per-neuron
  neurotransmitter → synapse sign.
- Codex: FlyWire — <https://codex.flywire.ai/> · bulk downloads
  <https://codex.flywire.ai/api/download>

**LIF model reproduced here**

- Shiu PK, et al. (2024). *A Drosophila computational brain model reveals sensorimotor
  processing.* Nature 634(8032):210–219.
  doi:[10.1038/s41586-024-07763-9](https://doi.org/10.1038/s41586-024-07763-9) —
  **the model this project implements.**
- Shiu PK, et al. (2023). Preprint: *A leaky integrate-and-fire computational model based on
  the connectome of the entire adult Drosophila brain…* bioRxiv 2023.05.02.539144.
  doi:[10.1101/2023.05.02.539144](https://doi.org/10.1101/2023.05.02.539144) — explicit
  equations and parameter table.
- `philshiu/Drosophila_brain_model` — <https://github.com/philshiu/Drosophila_brain_model> —
  reference Brian2 implementation + bundled connectivity, vendored under `data/dbm/`.

**LIF parameter provenance**

- Kakaria KS, de Bivort BL (2017). *Ring Attractor Dynamics Emerge from a Spiking Model of the
  Entire Protocerebral Bridge.* Front Behav Neurosci 11:8.
  doi:[10.3389/fnbeh.2017.00008](https://doi.org/10.3389/fnbeh.2017.00008) — `v_0`, `v_rst`,
  `v_th`, `t_mbr`.
- Jürgensen A-M, et al. (2021). *A neuromorphic model of olfactory processing and sparse
  coding in the Drosophila larva brain.* Neuromorphic Comput. Eng. 1:024007.
  doi:[10.1088/2634-4386/ac3ba6](https://doi.org/10.1088/2634-4386/ac3ba6) — `tau`.
- Lazar AA, et al. (2021). *Accelerating with FlyBrainLab the discovery of the functional
  logic of the Drosophila brain…* eLife 10:e62362.
  doi:[10.7554/eLife.62362](https://doi.org/10.7554/eLife.62362) — `t_rfc`.
- Paul MM, et al. (2015). *Bruchpilot and Synaptotagmin collaborate to drive rapid glutamate
  release and active zone differentiation.* Front Cell Neurosci 9:29.
  doi:[10.3389/fncel.2015.00029](https://doi.org/10.3389/fncel.2015.00029) — `t_dly`.

**Body (target for coupling)**

- Wang-Chen S, et al. (2024). *NeuroMechFly v2: simulating embodied sensorimotor control in
  adult Drosophila.* Nat Methods 21(12):2353–2362.
  doi:[10.1038/s41592-024-02497-y](https://doi.org/10.1038/s41592-024-02497-y)
- Lobato-Rios V, et al. (2022). *NeuroMechFly, a neuromechanical model of adult Drosophila
  melanogaster.* Nat Methods 19:620–627.
  doi:[10.1038/s41592-022-01466-7](https://doi.org/10.1038/s41592-022-01466-7) — morphology:
  65 segments, 122 DoF.
- flygym — <https://github.com/NeLy-EPFL/flygym/> · docs <https://neuromechfly.org/> ·
  `pip install "flygym[examples]"`

**Related connectome-simulation work**

- Lappalainen JK, et al. (2024). *Connectome-constrained networks predict neural activity
  across the fly visual system.* Nature 634:1132–1140.
  doi:[10.1038/s41586-024-07939-3](https://doi.org/10.1038/s41586-024-07939-3) ·
  flyvis <https://github.com/TuragaLab/flyvis> — candidate visual front-end.
- *Neuromorphic Simulation of Drosophila Melanogaster Brain Connectome on Loihi 2.*
  arXiv:2508.16792.
- `JNLiew/flylif_orientation_maps` — <https://github.com/JNLiew/flylif_orientation_maps> —
  FlyWire + LIF, oriented stimuli → optic-lobe orientation maps.

---

## TODO

**Model / experiments**

- [ ] Port milestone 1 to **v783**: select the sugar GRNs and MN9 by FlyWire annotation
  (cell type / class from Schlegel et al.) instead of hard-coded root ids, so the experiment
  is materialisation-independent.
- [ ] **Rate sweep**: run the sugar → MN9 assay across drive rates (e.g. 50–300 Hz) and plot
  the MN9 input–output curve; compare against Shiu et al.
- [ ] **Silencing controls**: use `lif_model.silence()` to knock out candidate relay
  interneurons between the sugar GRNs and MN9 and confirm MN9 drive drops — identifies the
  necessary pathway, not just a sufficient one.
- [ ] Second behavioural circuit as an independent check (e.g. antennal grooming: drive
  bristle mechanosensory neurons → neck/leg descending neurons).
- [ ] Cross-check total edge counts and NT-sign assignment against Codex directly, not only
  the vendored parquet.
- [ ] Switch to `set_device('cpp_standalone')` or a GPU backend (Brian2GeNN / Brian2CUDA) for
  the longer sweeps.

**NeuroMechFly coupling** (the point of the project)

- [ ] Install `flygym`; stand up a minimal closed loop that steps Brian2 and NeuroMechFly in
  lock-step (run the network in `dt_phys`-sized chunks inside the gym loop).
- [ ] **Sensory encoding** (body → brain): map NeuroMechFly ommatidia intensities and
  antennal odor concentration to Poisson rates on the corresponding FlyWire sensory neurons
  (R1–R8 / L1–L5, ORNs). Consider `flyvis` as a drop-in visual front-end.
- [ ] **Motor decoding** (brain → body): low-pass the spike trains of a chosen **descending
  neuron** population into joint targets / CPG parameters, and feed them as the `action` to
  `nmf.step()`.
- [ ] Handle the brain-only limitation: FlyWire has no VNC, so leg motor neurons are absent.
  Read out at descending neurons and drive legs with a hand-built CPG (NeuroMechFly v1 style),
  or stitch in the MANC / male VNC connectome at the descending/ascending interface.
- [ ] First embodied milestone: odor-gated turning — odor on one antenna biases descending
  activity, body turns toward the source.

**Repo**

- [ ] `git init`, pin exact dependency versions (`requirements.txt` / `environment.yml`).
- [ ] Move the large parquet files out of the repo (or Git LFS) and add a fetch script from
  Codex.
- [ ] Restore the `citations/` set (`SOURCES.md`, `PARAMETERS.md`, `THEORY.md`,
  `references.bib`) if provenance detail beyond this README is needed.
