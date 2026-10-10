# FLY-UI — embodied whole-brain emulation of *Drosophila*

Research aim: a small-scale test of the "Uploaded Intelligence" idea from Pantheon. If you copy a complete nervous system (brain and nerve cord, synapse by synapse from real connectome data) into a simulated body, does the animal's behavior emerge? And where it doesn't, what's missing that the wiring diagram alone can't supply?

The pipeline is scan (connectome) → emulate (spiking brain) → embody (virtual body and world).
The brain and body run in a closed loop in real time.

## Current status (2026-10-09)

| Part | State | Basis |
|---|---|---|
| Brain | FlyWire v783 (139,255 neurons) as Shiu et al. LIF, with conductance synapses, spontaneous activity, adaptation, homeostasis, hunger neuromodulation, and graded APL / patchy AL LNs. Sugar → MN9 and other Shiu benchmarks reproduced. | measured wiring; literature and assumed physiology (see sections below) |
| Nerve cord | BANC VNC (22,681 resident neurons) joined to the brain: 161,320 neurons and 15.73M edges in total. 12,791 VNC interneurons and 371 leg motor neurons are rate units (Pugliese et al. 2025 model) with spike-frequency adaptation (since 2026-10-09); the escape circuit (giant-fibre-coupled GFC1–4, TTMn, PSI, flight motor neurons) spikes. The interneuron rate units have homeostasis (1 Hz set point, learned with the fly upright); leg motor neurons have none. | measured wiring; literature model; set points approximate |
| Eyes and vision | 1,709-facet compound eyes → FlyVis + graded optic lobe → VPNs | measured / literature |
| Taste, smell, wind | per-neuron sense organs on the NeuroMechFly body | measured mapping; approximate response curves |
| Legs | 391 real leg motor neurons → muscles → joint torques; 915 leg proprioceptors feed back (FeCO claw/hook/club, hair plates, campaniform sensilla; incl. 34 FeCO afferents identified from shape and wiring). Hair-plate and FeCO direction tuning from wiring. Load sensing is weak in the middle and hind legs: BANC annotates only 2 campaniform neurons per leg there (data gap, unresolved by MANC or shape/wiring). | measured mapping; assumed mechanics (calibration ledger) |
| Walking | Walking CPG reproduced exactly offline. Offline, the tuned descending mix (DNg100 + DNb08 + DNa02 + DNg97) gives swing/stance anti-phase in 5 of 6 legs at 4.2 Hz. Live on the kinematic body (2026-10-05): with wiring-derived claw/hook tuning and presynaptic gating, 4 of 6 legs switch stance/swing (1.4–3.8 cycles/s); left front and right middle stay planted; best free-walking speed 0.29 mm/s (real 10–30). **Not walking yet.** On the physical body (2026-10-09) the fly stands but does not step; see "Physics". | see "Neuromuscular legs" and the 2026-10-08/09 sections |
| Escape | giant fibre → TTMn follows 1:1 (gap junction, 16 mV). After the upright homeostasis warm-up, 1 escape (start-up) in 20 s at rest; before, the GF fired spontaneously at 0.4–0.8 Hz (tonic LC4 plus DNp70 bursts). | literature + calibrated |
| Physics | One body: `--physics=mujoco` runs the live FlyWire+BANC brain and the 1,709-facet eyes on the physical NeuroMechFly body in MuJoCo (FlyGym 2.1.0, true scale, 1.02 mg, friction 1.0, pad adhesion). The brain's 391 leg and 16 neck motor neurons drive it; 915 leg and 70 neck proprioceptors are fed back from the physics (incl. 33 FeCO afferents identified from shape and wiring). Every segment, including the head carrying the eyes, takes the MuJoCo pose (mapping check: max deviation 5×10⁻⁶). Head yaw/roll is driven by the real neck motor neurons, so the eyes move with a physical head. The brain still runs at 1.00× real time (15–17 fps vs 25 without physics). **Standing (latest, 2026-10-09):** with rate-unit adaptation the left/right latch behind the lean is gone (pools nearly symmetric when held level). Set down gradually, the fly carries its own weight for about 1 s, then a spontaneous ~3 Hz left/right premotor oscillation throws it over. (Before adaptation it held at 0.62–0.72 mm but leaned.) **No walking yet**, live or offline (closed-loop descending-mix search: best 1.2 mm/s vs 0.5 mm/s drift with no drive). | literature model + assumed (ledger) |
| Neck and head | 16 annotated neck motor neurons (ADNM yaw, DProN roll) drive the MuJoCo head; 70 neck proprioceptors (prosternal organ, neck chordotonal) feed back. 27 neck motor neurons have no axis annotation (data gap). | axes measured; direction and range assumed |
| Chemical signalling, memory/learning | not yet; designed and fact-checked in HANDOFF 5b/5c (back burner) | — |
| Leg sugar → PER | known gap (see Phase 5b) | — |

Sources and papers with DOI links: [REFERENCES.md](REFERENCES.md). Everything below is in chronological order. Dated sections describe the state at that date; this table is the current summary.

## Run

1. Both connectomes are already built in `data/`. To rebuild, use the project's own Python environment:
   ```bash
   .venv/Scripts/python tools/build_connectome.py flywire
   ```
   ```bash
   .venv/Scripts/python tools/build_connectome.py synthetic
   ```
2. Open the folder in Godot 4.6 (`F:\GODOT4.6`) and press Play. It needs the
   Forward+ renderer, because the brain runs in a compute shader.
   - The **real FlyWire brain** loads by default.
   - Add `-- --connectome=synthetic` to load the hand-designed stand-in instead.

Controls:
- **L** loom a predator
- **W** wind
- **F** / click: food
- **B** bitter/aversive patch
- **T** move the sun
- **C** camera
- **V** show/hide the brain view
- **1/2/3** time scale
- **R** reset the fly
- **O** optogenetic drive of P9/DNp09 (the forward-walking command neuron)

Test harness (arguments go after `--`):
- `--log` print a report every second
- `--pops` include per-population rates in that report
- `--auto` scripted wind and predator events
- `--threat_at=N` frame at which the predator launches
- `--start=x,z` and `--yaw=a` fly start position and heading
- `--frames=N` quit after N frames
- `--shot=screenshots/x.png` save a screenshot before quitting
- `--connectome=flywire|synthetic` choose the brain
- `--physiology=0` turn off spontaneous activity and adaptation (pure Shiu et al.)
- `--phys_ablate=noise,mu,adapt,homeo` turn off parts of the intrinsic physiology
- `--homeostasis` learn homeostatic offsets during the run (from zero) and save them at the end; use it with `--clean_air`. `--homeostasis=continue` starts from the saved offsets. With `--physics=mujoco` the result is saved only if the fly stayed upright (thorax ≥ 0.5 mm, up-axis ≥ 0.5 after 2 s); learn with `--mj_tether=1` first, then free standing.
- `--clean_air` no odour, wind or taste stimuli
- `--opto` start with P9 optogenetics on
- `--record=recordings/run.csv` write body state plus every population's firing rate every 100 ms of emulated time
- `--probe=groups.json --probe_out=out.csv` per-frame activity of chosen neurons (plus leg joint angles, stance and foot height when the legs are on; with `--physics=mujoco` also head yaw/roll, thorax height and thorax up-axis)
- `--act_tau=5` time constant (ms) of the activity readout (default 60; use 5 at `--fixed-fps 120` for rhythms)
- `--synapses=current` Shiu et al.'s current-like synapses instead of the default conductance synapses
- `--drive=i,j:Hz;k:Hz` Poisson drive on chosen model neurons (e.g. descending neurons)
- `--silence=i,j` and `--release_gain=i,j:g` set chosen neurons' transmitter release (diagnostics)
- `--sugar_release=x` force the sugar-GRN release gain (otherwise set by hunger)
- `--legs=0` cosmetic legs instead of the neuromuscular model; `--legs_log`, `--legs_lift_test` leg diagnostics
- `--locomotion=legs` the body moves only by its stance feet on the kinematic body (default: descending-neuron rate kinematics)
- `--proprio=0` cut the leg proprioceptors off from the brain (diagnostic)
- `--physics=mujoco` the physical body: starts `tools/body_server.py` (needs `.venv-flygym`; localhost only) and moves the fly by MuJoCo physics. Options: `--pad_fmax=10` pad strength in µN per leg; `--mj_port=47830`; `--mj_rigid_head=1` diagnostic (head held on the thorax); `--mj_tether=1` thorax held level at standing height (use for `--homeostasis` warm-ups: learn only while upright); `--mj_release=s` set the fly down standing (tether ramped off over 0.5 s from s); `--mj_sensors=kinds` keep only these leg afferent kinds (diagnostic)

Always add Godot's `--quit-after` as a watchdog. On this PC also use `--disable-vsync --fixed-fps 30` (windowed Godot freezes on vsync), and never run two GPU Godot instances at once.

Offline tools for the physical body (run with `.venv-flygym/Scripts/python`): `tools/nmf_closed_loop.py` (nerve-cord rate model + MuJoCo body), `tools/body_server_test.py` (protocol check), `tools/reflex_probe.py`, `tools/dn_mix_closed_loop.py`.

## What is in it

| Layer | File | Notes |
|---|---|---|
| Connectome builder | `tools/build_connectome.py` | Synthetic stand-in, or the real FlyWire v783 connectome |
| Brain emulator | `shaders/lif.glsl`, `scripts/fly_brain.gd` | Leaky integrate-and-fire neurons with Shiu et al. 2024 parameters (plus conductance synapses, intrinsic physiology, graded and rate units: see later sections). Integration step 0.5 ms; synapses stored in sparse row format with fixed-point atomic adds. About 35 ms of GPU time per frame for 161,320 neurons with FlyVis and the graded optic lobe on an RTX 2080 (about 25 fps; 15–17 fps with the MuJoCo body). |
| Legs | `scripts/fly_legs.gd`, `tools/build_leg_map.py` | Neuromuscular legs and proprioceptors (Phase 6); client of the MuJoCo body server |
| Physical body | `tools/nmf_body.py`, `tools/body_server.py`, `tools/vnc_body_model.py` | NeuroMechFly in MuJoCo (FlyGym 2.1.0, `.venv-flygym`): leg and neck torques, pad adhesion, tether, proprioceptor rates; served to Godot over localhost |
| Neck | `tools/build_neck_map.py`, `tools/neck_sensor_tuning.py` | Neck motor neurons → head axes; neck proprioceptor tuning |
| Sensory identification | `tools/classify_leg_sensory.py`, `tools/manc_leg_sensory_check.py` | Leg sensory neurons identified from shape and wiring; MANC cross-check |
| Taste | `scripts/fly_taste.gd` | Per-neuron taste organs (Phase 3) |
| Body, senses, motor | `scripts/fly.gd` | See the sensory and motor lists below |
| World, HUD, brain view | `scripts/main.gd`, `shaders/neuron_view.gdshader` | Every neuron is drawn as a point at its position, coloured by neuropil and brightened by recent spiking |

Senses in `scripts/fly.gd`:
- **Eyes:** 2 × 6 sectors, each with a contrast-adapted tonic channel and a darkening-transient channel.
- **Antennae:** olfactory receptor neurons with adaptation.
- **Johnston's organ:** wind.
- **Taste:** sweet and bitter taste receptor neurons.
- **Sun compass.**

Motor outputs (descending neurons → behaviour; walking is still driven this way by default; the body moves by its own legs with `--locomotion=legs` on the kinematic body or with `--physics=mujoco`):
- P9 → walk forward
- DNa02 → turn
- MDN → walk backward
- Giant fibre → TTMn → escape takeoff (scripted flight; with `--physics=mujoco` it is counted but not executed: no jump/flight model)
- MN9 → proboscis extension and feeding

Behaviours verified in test runs:
- Feeding on sugar, which lowers hunger.
- Giant-fibre escape from a looming object, with no false escapes while walking or turning (thanks to the efference copy). (Verified with the early sector-vision model; with facet vision and the graded optic lobe, loom-triggered escape is not reliable yet, see the loom tests below.)
- Wind-driven turning.
- Spontaneous meandering.
- Local search in food odour.
- A heading "bump" in the central complex that tracks the sun.

Odour-guided approach works only partly. The fly stays in the plume and circles near the food, but it does not reliably land on it.

## Downloaded data (`data/raw/`)

| File | Source | What it is |
|---|---|---|
| `Completeness_783.csv`, `Connectivity_783.parquet` | github.com/philshiu/Drosophila_brain_model | FlyWire v783: 138,639 proofread neurons, 15,091,983 connections, 54.5M synapses, signed by predicted transmitter |
| `model.py`, `utils.py`, `example.ipynb`, `figures.ipynb`, `sez_neurons.pickle`, `environment*.yml` | same | Shiu et al. 2024 reference model. MN9 = root 720575940660219265. The pickle holds data only and was checked before loading. |
| `annot_Supplemental_file1..5` | github.com/flyconnectome/flywire_annotations | Schlegel et al. 2024: super class, class, subclass, cell type, side, soma and anchor positions, neurotransmitter; plus hemilineages and hemibrain matches |
| `cell_stats.csv.gz`, `column_assignment.csv.gz`, `visual_neuron_types.csv.gz` | FlyWire / Codex | neuron sizes, optic-lobe column assignment (Matsliah et al. 2024), visual types |
| `banc/` | BANC (Bates et al. 2025; Codex release 888, Harvard Dataverse doi:10.7910/DVN/8TFGGB) | nerve-cord neurons, connections, SWC skeletons |
| `pugliese/` | Zenodo 22260924, github smpuglie/Pugliese_2026 | VNC CPG model data (weights, surface areas) |
| `manc/` | Janelia FlyEM export bucket (MANC v1.0) | neuron properties, used for the leg load-sensor cross-check |
| `door/` | github.com/Dahaniel/DoOR.data | odorant response and spontaneous-rate tables |
| `eyemap_T4/` | github.com/reiserlab/eyemap_T4 (GPL-3.0) | micro-CT compound-eye map (Zhao et al. 2025) |
| `neck/` | github.com/flyconnectome/2023neckconnective | neck connective tables (Stürner et al. 2025) |

Sources, commits and checksums: `tools/fetch_data.py`. Raw data is git-ignored.

## Real-brain mode: what maps to what

| Input or output | Real FlyWire neurons |
|---|---|
| Eyes, tonic channel | R7/R8 photoreceptors plus lamina neuron L3 |
| Eyes, darkening transient | Lamina neuron L2 |
| Eyes, brightening transient | Lamina neuron L1 |
| Food odour | Receptor neurons of glomeruli DM1, DM2, DM4, DP1m, VA2, VM2 |
| Aversive odour | Receptor neurons of glomeruli V (CO2) and DA2 (geosmin) |
| Wind | Johnston's organ wind/gravity neurons |
| Taste | Sugar and bitter taste neurons, by side |
| Motor outputs | DNa02 (turning), DNp09 (forward), MDN (backward), DNp01 (giant fibre), MN9 = CB0701 (proboscis) |

- The eyes are split into sectors using real neuron positions: lamina upright, medulla inverted by the optic chiasm. **This retinotopic mapping is approximate.**
- Input groups are also ready but not yet driven by anything in the world: water taste, temperature (hot/cold), humidity (moist/dry), hearing, ocelli, and the dorsal rim area.
- **Model fidelity:** matches Shiu et al. 2024 — leaky integrate-and-fire neurons, 0.275 mV per synapse, 1.8 ms synaptic delay, synaptic input reset on spike, Poisson sensory drive of 68.75 mV. One difference: the time step is 0.5 ms instead of their 0.1 ms, so it can run in real time.
- **Body calibration:** how descending-neuron rates map to body movement is in the `motor` block of `data/connectome_flywire.json`. Edit it freely.

## First findings with the real brain (2026-09-30; historical, several since addressed)

- **No spontaneous walking.** Nothing in the wiring activates DNp09 without an internal-state drive. With P9 optogenetics the fly walks.
- **Left turn bias.** DNa02_L fires at about 60–120 Hz while DNa02_R stays silent, even with no odour present. The fly circles left.
- **No looming escape.** LPLC2 and the giant fibre stay silent to the looming predator. The simplified lamina drive probably doesn't produce the direction-selective motion signals (T4/T5 cells) that loom detection needs. (Addressed in part later by the FlyVis and graded optic lobe; see those sections.)
- **APL runs at 300+ Hz.** In reality APL is a non-spiking, graded neuron. (Fixed 2026-10-04: APL is now a graded neuron.)
- **EPG (compass) neurons are silent.** Nothing drives the ring-neuron and sun-compass pathway yet.

## Important honesty notes

- **The synthetic connectome** (`--connectome=synthetic`) It uses FlyWire's neuron count and the real neuropils and pathways, but the synapse-level wiring was written by hand to produce these behaviours. It is **not** an upload of a real fly.
- **The real brain** is the actual FlyWire wiring. It still runs a simplified neuron model and uses a hand-built body.
- **What no connectome contains.** A UI in the Pantheon sense would need all of the following, and none of them is in a wiring diagram:
  - learning and synaptic plasticity (still missing; plan in HANDOFF 5c)
  - neuromodulators (dopamine, octopamine): only hunger → sugar-pathway release is modelled so far (plan in HANDOFF 5b)
  - receptor identity per synapse (only per cell type, from transcriptomics)
  - gap junctions and synaptic delays: delays modelled; gap junctions only for the documented giant-fibre ones
  - dendritic nonlinearities (still missing; graded and conductance neurons are a partial step)
  - the ventral nerve cord (the fly's "spinal cord"): now added from BANC, a different fly than FlyWire's brain
  - the brain's current state (what makes it a particular individual): still missing

## Anatomical body and compound eyes (Blender, in progress)

Built by scripts that run inside Blender (`tools/blender/`) and plain Python (`tools/`). Open `blender/fly_body.blend`.

| Part | Source | Basis |
|---|---|---|
| Body meshes (69 segments) | NeuroMechFly v2 / FlyGym (Apache-2.0), micro-CT of one adult female, `assets/flygym/` | measured (left side); right side mirrored = approximate |
| Body frames and joint axes | FlyGym `rigging.yaml` → `data/flygym_rig.json` (`tools/flygym_rig_to_json.py`) | measured |
| Standing pose | FlyGym `pose/neutral/pitch_roll_yaw.yaml` | literature |
| Ommatidia (1,709: 852 right, 857 left) | Zhao et al. 2025 *Nature* micro-CT eye (`data/raw/eyemap_T4/`, reiserlab/eyemap_T4) | optical axes measured |
| Facet → FlyWire column | Zhao's lens↔Mi1 map of the FAFB eye + FlyWire Codex column assignment (Matsliah et al. 2024) | right eye measured; left eye approximate (mirrored lattice) |
| R1–6 → cartridge | FlyWire v783 connectivity: each R1–6 goes to the column of its strongest L1–L3 targets (5,749 of 7,172 placed) | measured |
| Yellow / pale | none in FlyWire; random 70/30 | approximate |
| Dorsal rim area | Zhao's DRA Mi1 columns | right measured, left mirrored |
| Facet positions on the body | micro-CT lenses fitted onto the NeuroMechFly eye mesh (scale 0.956, rotation 3.8°, median residual 4 µm) | approximate |

Outputs:
- `data/ommatidia.json`: per facet: side, hex (p,q), column_id, optical axis, DRA, subtype, `basis`, and the FlyWire root IDs of its column (R7, R8, L1–L5, C2, C3, T1–T3, Mi1/4/9, Tm1/2/3/4/9/20/21, T4a–d, T5a–d, R1–6).
- `data/ommatidia_placement.json`: facet position and axis in the head frame (mm).

Checks:
- The Codex (p,q) ↔ Zhao (i,j) link was verified two independent ways (lattice overlap 770/779; photoreceptor-less edge columns 40/56).
- The median interommatidial angle comes out at 4.8° (right) and 4.7° (left); the literature value is about 4.5–5°.
- A typical column holds one neuron of each of the 31 columnar types plus exactly 6 R1–6 (neural superposition).

Caveats:
- The eye micro-CT, the FlyWire brain and the NeuroMechFly body come from three different flies.
- Only the right optic lobe's column map is tied to measured eye data.
- Rebuild with `.venv/Scripts/python tools/build_eye_map.py`, then run `tools/blender/build_body.py` and `tools/blender/place_ommatidia.py` in Blender.

## Compound-eye vision in Godot (facet vision, default with the FlyWire brain)

The fly in Godot is the NeuroMechFly micro-CT body (`assets/fly/fly.glb`, exported from `blender/fly_body.blend`). Every segment is a named node (`c_head`, `lf_tibia`, `l_arista`, …) where further sense organs can be attached. (2026-09-30: leg and wing motion was cosmetic. Since 2026-10-05 the legs are driven by the real leg motor neurons, and with `--physics=mujoco` every segment, including the head carrying the eye cameras, takes its pose from the MuJoCo body.)

Pipeline:
1. **Cube map.** Six 90° cameras (48 px per face) form a cube map. It is locked to the `c_head` node, centred between the eyes. The fly's own body is on render layer 2 and hidden from these cameras.
2. **Facet sampling.** `shaders/eye.glsl` samples each of the 1,709 measured ommatidia with a 5° Gaussian acceptance cone. Photoreceptor adaptation is Weber-like, with τ = 1 s.
3. **Photoreceptor drive.** The shader writes a Poisson rate into the per-neuron input buffer (new binding 14 in `lif.glsl`) for every real FlyWire R1–6, R7 and R8 of that facet's column (8,062 neurons). The kernel and receptor lists come from `data/eye_drive.json` (`tools/build_eye_drive.py`).
4. **Transmitter sign.** Photoreceptor output synapses are set **inhibitory (histamine)** in `tools/build_connectome.py`. FlyWire's transmitter predictor has no histamine class. basis: literature.
5. **Lamina resting bias.** Lamina L1–L5 get a resting bias of `--lamina_bias` (default 9 mV). They are graded cells in reality. basis: approximate.
6. **Columnar resting bias.** Other columnar optic-lobe types (Mi, Tm, C, T1–T5) can get `--columnar_bias=mV` (default 0). basis: approximate, free parameter.

Other approximations:
- RGB render with blue standing in for UV.
- One viewpoint for both eyes.
- Graded photoreceptors are represented as spike rates.
- The fly body casts no shadow (its 0.3 mm self-shadow flickered in the shadow map).

New arguments:
- `--vision=facets|sectors` (sectors is the old 2 × 6 model)
- `--lamina_bias`, `--columnar_bias`
- `--tethered`: body held in place; giant-fibre spikes are counted as escapes
- `--threat_angle=deg`: 0 = head-on, 90 = from the left
- `--eye_dump=file.csv`: per-facet luminance; plot it with `tools/plot_eye_view.py`
- `--probe=data/loom_probe.json`: per-column traces (`tools/make_loom_probe.py`)
- `--cam_dist`: camera distance

### Loom test (2026-09-30)

Run with `tools/run_loom_test.py --bias 0 5 6 6.5`. It records `recordings/loom_*.csv` / `*_summary.csv`, and per-column probes to `recordings/probe_b*.csv`.

- **Stimulus:** fly tethered; a dark sphere (radius 0.7 cm) launched from 9 cm to the fly's left at 7 cm/s.
- **Result:** no escape in any condition. LPLC2, LC4 and DNp01 (giant fibre) stay at 0 Hz.

Where the signal goes, in the 12 columns that view the predator (the control columns ahead stay flat):

| Stage | bias 0 mV | bias 6.5 mV | Real-fly expectation |
|---|---|---|---|
| R1–6 | 35 → 9 Hz | same | photoreceptors respond to darkening ✔ |
| L1 / L2 | 5 → 22 / 3 → 16 Hz | same | depolarize to darkening ✔ |
| Tm1 / Tm2 / Tm9 (OFF) | 0 → 3 / 1 / 0 | 2 → 20 / 20 / 7 | OFF cells excited ✔ (only with bias) |
| Mi1 / Tm3 (ON) | 0 | 8 → 3 / 2 → 1 | suppressed by a dark object ✔ (only with bias) |
| T5 (OFF motion) | 0 | 0 → up to 7 (T5d), 4 (T5c) | responds to a dark edge ✔ weak |
| T4 (ON motion) | 0 | ≈0 | little response ✔ |
| LPLC2 → DNp01 | 0 | 0 | should fire → escape ✘ |

Interpretation:
- The measured eye and the real wiring give the correct ON/OFF polarity at every stage up to T5.
- The signal is lost in two places:
  1. **At the first medulla synapse.** Lamina input delivers only about 0.6–1.5 mV of mean depolarization to Tm/Mi cells, against a 7 mV spike threshold. In reality these are graded, non-spiking synapses, which a spiking LIF model with the Shiu et al. parameters cannot represent.
  2. **At T5 → LPLC2.** A few weak, non-direction-selective T5 spikes don't reach LPLC2's threshold. Direction selectivity needs cell-type-specific time constants (delays between Tm9 and Tm1/Tm2), and this model gives every synapse the same 1.8 ms delay and 5 ms time constant.
- **Likely next steps:**
  - Run the optic lobe as a graded (rate) network with cell-type time constants (FlyVis, Lappalainen et al. 2024 is the data-driven source of those parameters), feeding LPLC2/LC4 into the spiking central brain.
  - Or add per-type time constants to the LIF shader.

## Graded optic lobe: FlyVis hybrid (default)

The optic lobe can now run as the **FlyVis** graded network (Lappalainen et al. 2024, *Nature*; github.com/TuragaLab/flyvis, MIT), pretrained model `flow/0000/000`. It runs on the GPU in `shaders/flyvis.glsl`: one instance per eye, each with 65 cell types and 45,669 cells.

What FlyVis supplies:
- **Connectivity** is measured, but from FIB-25/FIB-19 medulla data averaged into per-type filters, not from FlyWire.
- **Resting potentials, time constants and synapse strengths** are model-fitted: they were trained so the network computes optic flow.
- **Export check:** the exported network matches FlyVis's own simulator to 1×10⁻⁶ (`tools/flyvis/export_flyvis.py`). FlyVis is exactly convolutional, so 2,355 shared filter entries reproduce all 1,513,231 synapse groups.

How it connects to the rest of the model:
- **Input:** each FlyVis column reads its facet's luminance. The lattice is laid onto each measured eye (`tools/flyvis/map_eye_lattice.py`) and oriented so the model's T4/T5 preferred directions match biology (Maisak et al. 2013).
  - Remaining direction errors are 2–10° for most subtypes; T5d is 25–30° and T4c is 40–44°, which reflects FlyVis's own tuning.
  - 712 of 721 columns (right eye) and 674 (left) sit on a real facet.
- **Output:** every FlyVis cell whose type is in FlyWire's column map drives the real FlyWire neuron(s) of that type in that column, as a Poisson rate: `gain × (relu(V) − relu(V_grey))`, with `--flyvis_gain`, default 60 Hz/unit, approximate. That covers 28 types and **37,627 FlyWire neurons** (L1–L5, C2, C3, T1–T3, Mi1/4/9, Tm1/2/3/4/9/20, T4a–d, T5a–d).
- **Downstream:** everything beyond those cells (LPLC2, LC4, the giant fibre and the rest of the central brain) remains the spiking FlyWire LIF model.
- **Options:** `--optic_lobe=lif` switches back to the spiking-only optic lobe.

Rebuild:
1. `.venv/Scripts/python tools/flyvis/export_flyvis.py`
2. `.venv/Scripts/python tools/flyvis/map_eye_lattice.py`
3. `.venv/Scripts/python tools/flyvis/export_godot.py`

`tools/flyvis/_env.py` patches a Windows file-locking bug in FlyVis's storage library (datamate) at runtime.

Cost: about 20% more GPU time per simulated step. It runs in real time at about 27 fps.

### Loom test with the FlyVis optic lobe

Fly tethered; predator from the left. Records are in `recordings/loom_flyvis_g*`; the figure is `screenshots/flyvis_loom_g120.png`.

| | gain 60 | gain 120 | gain 240 |
|---|---|---|---|
| Columns facing the predator: T4a/b/c/d, T5a/d peak | — | 62 / 53 / 34 / 16, 28 / 22 Hz (from 0–1) | higher |
| Control columns | flat | flat | flat |
| LPLC2 | 0 | 0 | 0 |
| LC4 | not loom-specific | brief peak 18 Hz at the very end, tonic about 10 Hz | tonic about 23 Hz |
| Giant fibre (DNp01) | none | 1 false alarm (also in the no-predator control) | false alarms in the control |

- **Result:** with graded dynamics, the real eye geometry produces a strong, loom-specific, all-direction (expanding) T4/T5 response in exactly the columns that see the predator. Under the purely spiking optic lobe this signal was absent.
- **Where it stops:** the transmission from **T4/T5 → LPLC2** in the spiking FlyWire model.
  - Each LPLC2 has about 890 input synapses, with only about 30–40 per T4/T5 subtype, spread across a wide receptive field.
  - Its largest input, **Tm5f (67 synapses per cell), isn't in FlyVis** and stays silent.
  - It receives inhibition from PVLP011 (−46 per cell).
  - The estimated loom-driven depolarization is about 4 mV, against a 7 mV threshold.
- **Raising the gain doesn't help:** it only adds tonic LC4 drive and false giant-fibre spikes.
- **What would plausibly fix it:**
  - Graded or dendritic integration in LPLC2 itself; real LPLC2 dendrites combine layer-specific outward motion non-linearly.
  - Including Tm5f/TmY inputs.
  - Per-type LIF parameters.
  - None of these are in a wiring diagram.

## Graded optic lobe beyond FlyVis, and two-compartment visual projection neurons (default)

FlyVis now covers 47 cell types (46,229 FlyWire neurons). Twenty types that FlyWire's column map lacks were placed by connectivity, using `tools/flyvis/assign_columns.py`. That method recovers 83% of known columns exactly and 96% to within one column.

Every other FlyWire optic-lobe neuron is a **graded unit**: about 31,600 of them (LPi, Tm5f, Y, TmY, Li, Dm, Pm, Lawf, lobula-plate tangential cells, …). So is the **dendrite of every visual projection neuron**: 8,038 of them (LPLC2, LC4, LPLC1, LC6, LC12, …). Code is in `tools/graded/` and `shaders/graded.glsl`.

How the graded units are defined:
- **Dynamics:** the same equations as FlyVis.
- **Connectivity:** FlyWire synapse counts, with signs from the predicted transmitter. basis: measured.
- **Synapse strength:** FlyVis's fitted per-synapse strength for the presynaptic type, adjusted three ways:
  - scaled by FlyVis's own rule that cells with many inputs have weaker synapses (strength ∝ total inputs^−0.38);
  - converted from FIB-25 to FlyWire synapse counts (κ = 0.87);
  - multiplied by one global factor (α = 0.42) so the recurrent graded block has the same largest real eigenvalue (0.89) as FlyVis's fitted network, which keeps it stable.
  - basis: model-derived.
- **Resting level:** set so each unit sits at threshold under uniform grey light. basis: approximate.

How the graded part connects to the spiking brain:
- **Projection neurons are two-compartment.** The graded dendrite drives the spiking FlyWire soma as a bias current of c × V. The default c = 19 mV per unit is the mean-field equivalent of the spiking model's own synapses (`--vpn_c`). Their axonal outputs (to the giant fibre and so on) are ordinary spiking FlyWire synapses.
- **No double counting:** the spiking model's optic-lobe-internal synapses are silenced (7.7 million edges, in `data/lif_w_graded.bin`).
- **Switches:** `--graded=0` turns this off; `--optic_lobe=lif` gives the spiking-only optic lobe.

Rebuild everything with `bash tools/rebuild_vision.sh flow/0000/000`.

### Validation against physiology (offline, `tools/graded/validate.py`)

**Choosing the FlyVis model.** All 50 pretrained FlyVis models were screened on established T4/T5 physiology, without reference to any loom result (`tools/flyvis/screen_ensemble.py`, `pd_check.py`). The two criteria:
- strong direction selectivity with a weak response to stationary flashes;
- T4 and T5 of the same subtype preferring the same direction (Maisak et al. 2013).

How the candidates fared:
- Several high-scoring models (021, 022, 036) **violate the T4/T5 co-tuning constraint**; for example, 021's T5c and T5d are reversed.
- Models 000 and 005 pass both criteria.
- On the stimulus suite (below), **000 matches more of Klapoetke's LPLC2 tests**, so it is the default.

**Wiring check, independent of FlyVis** (`tools/graded/radial_test.py`). FlyWire T4/T5 → LPLC2 wiring is driven with an idealized radial-motion pattern. **All 102 right LPLC2 cells prefer outward motion, by a median factor of 25**, which reproduces Klapoetke et al.'s anatomical result in our eye geometry.

**Response tests** (model 000; peak population response relative to the loom):

| Stimulus | LPLC2 | Expected (Klapoetke 2017) |
|---|---|---|
| dark loom | 1.00 | strong |
| receding disc | 0.40 | ≈0 ✔ (reduced) |
| inward cross | 0.23 | ≈0 ✔ |
| wide-field translation | 0.36 | ≈0 ✔ (reduced) |
| outward cross | 0.39 | strong ✘ (weak) |
| luminance-matched dimming | 1.47 | ≈0 ✘ |

- **LC4** is silent to the dark loom and responds to brightening. In this FlyVis model, LC4's main input (T2) is a pure ON cell; real LC4 responds to dark looms (Ache et al. 2019).
- **Where the remaining failures come from:** FlyVis T4/T5 output. In model 000, T5 responds to stationary darkening almost as much as to motion. Across the whole eye, the T5 subtypes are unevenly tuned (in model 005, T5a dominates every OFF edge).
- **Bottom line:** the connectome wiring is radially correct. The motion inputs from any single FlyVis model aren't clean enough to reproduce the full selectivity.

### In-world loom test

Fly tethered, predator from the left (`tools/run_loom_test.py --optic graded --vpn_c 19 38 76 --control`):

| Coupling c | LPLC2 (approached side) | LC4 | Giant fibre |
|---|---|---|---|
| 19 mV/unit | peak 0.8 Hz, loom only (control 0) | tonic 5–8 Hz | silent |
| 38 mV/unit | peak 3.8 Hz, loom only | tonic 23–34 Hz | only a start-up transient, also in the control |
| 76 mV/unit | 8–13 Hz, loom only | tonic 50–75 Hz | fires every ~2 s, also in the control (false alarms) |

- **LPLC2** is loom-specific for the first time and scales with c.
- **No loom-triggered escape** occurs without false alarms. LC4 is tonically driven by the bright arena (an ON-cell artifact inherited from FlyVis T2), and it reaches the giant fibre before LPLC2 does.
- **Most likely improvements:**
  - an ensemble average of several co-tuned FlyVis models, as Lappalainen et al. recommend for predictions;
  - the newer whole-optic-lobe connectome-constrained models trained on FlyWire or the male CNS (not done here).

## Core brain fidelity: matched to Shiu et al. exactly (2026-10-03)

`tools/reference_lif.py` is an exact re-implementation of the Shiu et al. 2024 Brian2 model (`data/raw/model.py`): 0.1 ms step, exact linear integration, Poisson input into the membrane voltage, no refractory period for stimulated neurons. It revealed that our old GPU scheme under-drove the brain badly. Poisson input went into the synaptic conductance and was Euler-integrated, so at 100 Hz sugar input MN9 reached 30 Hz instead of 75.

`shaders/lif.glsl` now uses Shiu's semantics: exact integration, Poisson kicks to the voltage, stimulated neurons non-refractory, synaptic input reset on spike. The only remaining difference is the 0.5 ms step (needed for real time), which also rounds the 1.8 ms delay to 2.0 ms.

Benchmark (Shiu et al. Fig. 1): Shiu's 20 "sugar" GRNs (v783 IDs) stimulated at f Hz, MN9 rate R/L in Hz.

| f | exact reference (0.1 ms) | Godot GPU (0.5 ms) |
|---|---|---|
| 40 | 2.3 / 2.0 | 3 / 4 |
| 60 | 29 / 23 | 23 / 25 |
| 80 | 61 / 47 | 56 / 42 |
| 100 | 75 / 53 | 87 / 56 |
| 150 | 100 / 65 | 107 / 58 |

The two agree to within about 15%, which is about the size of the trial-to-trial spread.

**Note:** loom and vision results recorded before this date used the old scheme. Re-run them before comparing.

## Taste organs and the feeding motor system (Phase 3)

Data and tools:
- **Taste neurons:** `tools/build_taste.py` → `data/taste_neurons.csv`, `data/taste_organs.json`. Every FlyWire gustatory neuron (407) is assigned an organ, side, modality and sensor.
- **Sensor placement:** `tools/blender/place_taste.py` puts the sensors on the body: 62 labellar taste bristles (L/I/S rows), 73 taste pegs, 30 leg-tarsus sensors and 1 pharyngeal sensor.
- **Physics:** in `scripts/fly_taste.gd`, a sensor reads chemistry only when it physically touches a patch. Each neuron fires by its modality's dose–response, from literature ranges in `data/grn_response.json` (basis: approximate).
- **GPU input:** rates go straight into the brain through `shaders/sensor.glsl`.

Where each piece comes from:

| Item | Source | Basis |
|---|---|---|
| Labellar bristle types and modality | Tastekin et al. 2026 types (flywire_annotations v3.2.0) | measured |
| Leg neurons LgAG1–9 | LgAG2 = sugar (Gr61a match), LgAG1 = bitter (Gr33a); other types aversive / unknown cluster; leg of origin (fore vs mid/hind) from the male CNS (Tastekin et al. 2026) | literature |
| Pharyngeal neurons PhG1–16 | PhG1 = sugar-like (Gr64e); PhG3/4 = water; PhG2 and the aversive cluster = putative aversive (Tastekin et al. 2026, Suppl. Table 2 → `data/tastekin2026_flywire_types.tsv`) | literature |
| Taste pegs | no ligand known → not driven | — |
| Neuron → individual bristle, positions on the labellum | dealt by co-expression rules | approximate |
| Feeding motor neurons, 24 types (MN1–13, CEM, MNx) | Tastekin et al. 2026 Suppl. Table 2; muscle roles from McKellar et al. 2016 | measured / literature |
| Proboscis kinematics | MN9 vs MN1 → rostrum; MN4a (+MN6) vs MN1 → haustellum; MN8 → labellum spreading (exposes pegs); MN11/12 → cibarial pump. Activation = rate/(rate+30 Hz), 60 ms time constant | approximate |
| Labellum–substrate contact | rostrum ≥ 0.7 and haustellum ≥ 0.5 extended; pegs also need spreading ≥ 0.3. NeuroMechFly's neutral pose stands taller than a feeding fly, and posture isn't simulated | approximate |
| Ingestion | labellum on sucrose and the pump active | — |

### Findings

1. **Sugar alone evokes a full, coordinated feeding motor program from the wiring.** With Shiu's sugar set at 100 Hz:
   - MN9 (rostrum protraction) 50–80 Hz
   - MN4a (haustellum extension) 26 Hz
   - MN6 (labellar extension) 19–34 Hz
   - MN8 (labellar spreading) 21–76 Hz
   - MN11D (cibarial pump) 165–175 Hz
   - **MN1 (the retractor) silent**

   Nothing about this coordination was programmed.
2. **Shiu et al.'s 21 "sugar" neurons are mixed, and all on one side.** Re-typed with v3.2.0, they are 9 sugar, 2 sugar/low-salt, 5 high-salt/heavy-metal and 4 putative-attractive neurons, one is missing from v783, and every one is annotated `side = left`. Stimulated alone (`tools/decompose_shiu_sugar.py`), the 9 sugar neurons give MN9 34 Hz at 100 Hz input. The high-salt and putative-attractive subsets also drive MN9 at 200 Hz.
3. **Left and right labellar taste neurons are not equivalent in FlyWire v783.** Right-annotated labellar neurons have about **half the reconstructed output synapses** (median 127 vs 240, in every type), and their full sugar set drives MN9 to 0 Hz even at 100 Hz. The full left sugar set drives MN9 at 64 Hz at 60 Hz input (`tools/sugar_sides.py`). This points to incomplete reconstruction of one labellar nerve, not real biology.
4. **No proboscis extension from leg sugar, on the sucrose patch or in the bench test.**
   - On a 200 mM sucrose patch, all 12 leg sugar neurons (LgAG2) fire at about 32 Hz. MN9 stays at 0.
   - Even at 200 Hz, LgAG2 gives MN9 only about 2 Hz.
   - In real flies tarsal sugar reliably triggers extension, mostly via leg taste neurons that stay in the **ventral nerve cord**, which FlyWire doesn't contain. Only the ascending subset reaches the brain.
   - So in this model the fly cannot start feeding from its legs. That's a missing-data result: the nerve cord (MANC/BANC) is needed to close the loop.

Bench: `tools/run_taste_bench.py --set shiu|sugar|leg_sugar|bitter`.

## Mirrored right labellar taste neurons (on by default)

**The problem.** In FlyWire v783, right-annotated labellar taste neurons have about half the output synapses of the left ones:

| Class | Neurons L/R | Median output synapses L/R |
|---|---|---|
| Labellar bristles | 108 / 105 | 240 / 127 |
| Taste pegs | 37 / 36 | 149 / 74 |

Their cable is only about 14% shorter, but their synapse density is 43% lower (364 vs 634 per mm). Labial mechanosensory neurons in the same nerve, and the pharyngeal and leg taste neurons, are symmetric. Engert et al. 2022 report EM-volume misalignments that prevented labellar taste-neuron reconstruction in FAFB's left hemisphere. That is the side FlyWire labels right, because FAFB was imaged as a mirror image.

**The fix** (`tools/mirror_grn.py` → `data/grn_mirror_patch.parquet`; turn it off with `FLY_NO_MIRROR=1`):
- Each right taste neuron is topped up to the left-side mean for its type.
- Each type keeps its own pattern of same-side vs opposite-side partners, copied from the left. Bitter neurons reach the midline ring; sugar, water and salt neurons stay on their own side (Engert et al. 2022).
- Synapses are added only to the mirror-image partner neurons (same type, opposite side), in proportion to the synapses those partners already receive.
- Measured synapses are never removed.
- Taste-to-taste contacts are added once, from the presynaptic side.

Result: about 14,500 output and 2,000 input synapses added; the right-side median goes from 101 to 221 synapses (left: 204). basis: approximate.

**Functional check** (reference model, `tools/sugar_sides.py --mirror`). MN9 R/L in Hz:

| Sugar set | Neurons | 60 Hz input | 100 Hz input |
|---|---|---|---|
| left | 33 | 64 / 40 | 96 / 51 |
| right, before | 24 | 0 / 0 | 0 / 0 |
| right, after | 24 | 21 / 26 | 44 / 61 |

The opposite-side preference flips as a mirror image should. The right side stays weaker because FlyWire types fewer of its neurons as sugar.

## Spontaneous activity, adaptation and homeostasis (Phase 5, 2026-10-03, on by default)

Shiu et al.'s model is silent without input and has no adaptation. Real fly neurons fire spontaneously and adapt. Added per neuron (`shaders/lif.glsl`, `tools/build_physiology.py`, rules in `data/physiology_rules.json`):
- **Membrane noise:** Ornstein–Uhlenbeck, σ = 2 mV, τ = 5 ms. basis: approximate (Gouwens & Wilson 2009).
- **Resting offset μ:** calibrated so the isolated neuron fires at its cell class's measured spontaneous rate. Values and basis:

  | Cell class | Rate | Basis |
  |---|---|---|
  | ORNs | per receptor, from DoOR spike recordings (median 10 Hz) | measured (Münch & Galizia 2016; Hallem & Carlson 2006) |
  | PNs | 4 Hz | Wilson et al. 2004 |
  | Kenyon cells | 0.2 Hz | Turner et al. 2008 |
  | MBONs | 6 Hz | Hige et al. 2015 |
  | Giant fibre, escape/flight motor neurons, APL | silent | |
  | Everything else | about 1 Hz | approximate |

- **Spike-frequency adaptation:** AdEx-style current, τ_w = 300 ms. Its step is calibrated to a per-class adaptation index; Kenyon cells adapt strongly (0.3), motor neurons weakly (0.85). basis: approximate (Nagel & Wilson 2011).
- **Homeostatic intrinsic plasticity:**
  - A 60 s warm-up (`--homeostasis --clean_air`) learns a per-neuron offset that brings each neuron in the network to its target rate. It is saved to `data/homeostasis_offsets.bin` and loaded automatically.
  - Offsets (2026-10-03 warm-up): 5th–95th percentile −3.4 to +0.5 mV.
  - Since 2026-10-09 the offsets are learned on the physical body with the fly upright (tethered, then free standing), and also cover the nerve-cord interneuron rate units. Offsets are applied only to neurons with a homeostatic target. See the 2026-10-09 sections.
- **Synapse signs by Dale's principle:** each neuron's transmitter is `known_nt`, else FlyWire's neuron-level `top_nt` (Eckstein et al. 2024).
  - ACh is excitatory; GABA, glutamate and histamine are inhibitory.
  - Dopamine, serotonin, octopamine and tyramine have no fast effect.
  - Shiu et al.'s per-connection signs counted monoamines as excitatory. `FLY_SIGNS=shiu` restores them.

Two wiring corrections were needed to make this hold up:
1. **No spike-driving inputs onto sensory afferents.**
   - ORNs, GRNs and mechanoreceptors start their spikes in the periphery. FlyWire/BANC synapses onto their axon terminals (ORN–ORN, LN → ORN, GABA → GRN) act presynaptically on release (Olsen & Wilson 2008; Root et al. 2008), so 185,359 such edges were removed (`FLY_AFFERENT_INPUTS=1` keeps them).
   - Presynaptic gain control itself is not modelled.
2. **Input-resistance correction for giant integrators only.**
   - Shiu's 0.275 mV per synapse is kept for neurons with up to 6,000 input synapses, the range of the circuits Shiu et al. validated (MN9 has 5.6–5.9k).
   - Above that, a passive-membrane correction w × (6000 / N_inputs) is applied. It affects about 0.5% of neurons, mostly multiglomerular antennal-lobe local neurons (9–17k inputs) and APL.
   - Without it those cells saturate on spontaneous ORN input (local neurons 61 Hz, APL 70–96 Hz, even with homeostasis).
   - The FlyVis power law over all neurons (γ = 0.38) also tames them but weakens sugar → MN9 about 5× by scaling down the premotor hubs (CB0553, CB0493, DNge062).
   - No single power law fits both benchmarks (it would need γ > 1), hence the threshold. basis: biophysics + approximate threshold; `FLY_SIZE_NREF`, `FLY_SIZE_GAMMA`.

Also changed:
- The old 5 Hz (ORN) and 10 Hz (Johnston's organ) Poisson baselines are dropped when physiology is loaded, since they would double-count spontaneous activity.
- `--clean_air` turns off odour, wind and taste stimuli for resting calibration, like in-vivo recordings in clean air.

Results:
- **Resting rates** (clean air, no vision, 10 s; `tools/run_rest_test.sh`): measured against target.

  | Population | Measured | Target |
  |---|---|---|
  | ORNs | 12.4 | 10 |
  | PNs | 4.5 | 4 |
  | AL local neurons | 4.7 | 2 |
  | Kenyon cells | 0.1 | 0.2 |
  | MBONs | 4.7 | 6 |
  | DANs | 1.9 | 2 |
  | LH local neurons | 1.1 | 3 |
  | LH centrifugal | 1.9 | 3 |
  | APL | 0 | 0 |
  | MN9 | 0.2 | 0.5 |

  - Rates are averages over cell types.
  - Per neuron, AL local neurons have median 0 Hz and 13% above 10 Hz. The fastest are the serotonergic lLN2T_b (~100 Hz), which have no fast output here.
- **Global runaway:** gone. Bilateral 200 Hz sugar leaves APL at 0, AL local neurons at about 2 Hz and Kenyon cells at 0.1 Hz.
- **Sugar → MN9:** bilateral labellar sugar at 30/60/100/200 Hz gives MN9_R 8/14/20/38 Hz and MN9_L 5/7/11/20 Hz, rising steadily with input.
  - Shiu's exact model gives about 29/75/116 Hz at 60/100/200 Hz.
  - Much of that comes from a recurrent pharyngeal premotor loop (CB4055 / CB0910 / CB0707 / CB0708) that ignites to about 100 Hz in Shiu's model. With bilateral input it ignites 8,002 neurons at ≥ 15 Hz. With adaptation that loop stays moderate, so our MN9 is lower. Which is closer to the real fly is not settled by data; MN9 has not been recorded in Hz.
- **Giant fibre:** opto at 100 Hz drives TTMn at 44–57 Hz through the gap junction (8 mV coupling then; 16 mV and 1:1 following since 2026-10-09). Escape still works.
- **Leg sugar** (embodied, standing on the food patch): MN9 rises from 0.2 to 2.8 Hz but there is no visible PER. Real flies extend the proboscis to tarsal sugar, so the leg → PER route is still too weak (open issue).
- **Ablations** (`--phys_ablate=noise,mu,adapt,homeo`, γ = 0.38 build, 100 Hz bilateral sugar, MN9_R):

  | Configuration | MN9_R |
  |---|---|
  | All physiology on | 2 Hz |
  | No homeostasis | 18 Hz |
  | No adaptation | 18 Hz |
  | Neither | 36 Hz |
  | No noise | 0 Hz |
  | Physiology off | 0 Hz |

  Noise lets weak synaptic drive reach threshold.

Diagnostics: `tools/diag_sugar_path.py` compares the reference sugar pathway neuron by neuron with the embodied brain.

Note on running Godot: on this PC windowed Godot started freezing on vsync (2026-10-03, even with an empty project). All test scripts now launch it with `--disable-vsync --fixed-fps 30`, which gives about 33 ms of simulation per frame, as before.

## Leg sugar → proboscis extension (Phase 5b, in progress, 2026-10-03)

The circuit, from the literature:
- Tastekin et al. 2026, Fig. 9B: the appetitive leg taste type **LgLG4** (nerve cord, Gr64f) → ascending neuron **AN01B004** (FlyWire AN_GNG_162) → **Bract** descending neurons and Sink & Synch → **Roundup** → **MN9**.
- The direct leg-to-brain type **LgAG2** joins the same targets.

New tools and data:
- **Named feeding neurons in v783** (`data/tables/named_feeding_neurons.csv`):
  - Source: FlyWire Codex community labels.
  - Cross-checked by soma position against the CATMAID skeletons (`tools/data_named_feeding.py`, which agreed on every neuron both methods resolved).
  - Names → types: G2N-1 = CB0616, Clavicle = AN_GNG_30 (an ascending neuron), Fdg = CB0038, Rattle = CB0499, Roundup = CB0553, Rounddown = DNge080, Bract1/2 = DNge174/DNge173, Sink & Synch = CB0434, Foxglove = CB0890, Bluebell = DNg60, and others.
- **Better brain/nerve-cord joining** (`tools/build_vnc.py`):
  - Cell types come as left/right homolog sets. The FlyWire→BANC type correspondence learned from confident matches is used to pair the remaining members within each type.
  - +127 ascending and +53 sensory ascending neurons are now joined (1,266/1,736 and 181/581), e.g. the left Dandelion (AN_GNG_68 = AN13B002).
- **Presynaptic release gain** (`lif.glsl` binding 20, `FlyBrain.set_release_gain`): neuromodulation of transmitter release.
  - Hunger now raises release at the sites the literature identifies (`tools/build_hunger.py` → `data/hunger_targets.json`), with gain = 1 + hunger (×1.8 when hungry):
    - all 370 sugar GRNs: dopamine via DopEcR (Inagaki et al. 2012)
    - G2N-1 and Clavicle: the only hunger-modulated central nodes found by Shiu, Sterne et al. 2022 (Fig. 4)
  - basis: sites from the literature, gain approximate. Benchmarks keep gain 1; `--sugar_release=X` forces it.
  - `--silence=i,j,...` sets chosen neurons' release to 0, for ablation diagnostics.

Findings:

| Test | Result |
|---|---|
| All 293 nerve-cord leg sugar GRNs at 100 Hz → AN01B004 | 4–44 Hz |
| → Bract2 (DNge173), Roundup (CB0553) | 1–2 Hz |
| → MN9 | ≤ 2 Hz |
| Shiu et al.'s exact model, AN01B004 driven directly | needs ~200 Hz for MN9 18 Hz |
| Leg sugar also activates | glutamatergic DNxl094 (583 synapses back onto AN01B004) and GABAergic DNg103: negative feedback |
| Sugar-GRN release ×2 / ×4, labellar (30 Hz bilateral) | MN9 5 → 13 → 20 Hz |
| Sugar-GRN release ×2 / ×4, leg | ≤ 4 Hz |
| Embodied, standing on 200 mM sucrose, hungry (GRNs + G2N-1 + Clavicle ×1.8) | MN9 1–2 Hz, proboscis peaks at 0.28 only briefly |
| Labellar sugar 30 Hz bilateral, fed → hungry | MN9 5 → 18 Hz (strong hunger effect, as in Shiu et al. 2022) |
| Leg 100 Hz with DNxl094, DNg103 and IN09A001 silenced | MN9 ≤ 1.4 Hz (feedback is not the block) |

- AN01B004 provides only 2–8% of Bract1/2's inputs (241 and 146 synapses).
- The leg route needs about 7 hops to reach the feeding motor neurons, 2 more than the labellum (Tastekin et al.).
- Sensory hunger gain explains the labellar effect of starvation but not tarsal PER. The missing gain is central.
- Both of Shiu et al.'s hunger nodes are on the labellar route: Clavicle's inputs are labellar LB3 GRNs, not leg GRNs.
- Conclusion so far: with Shiu-calibrated synapse weights, the connectome's leg arc is too weak in the feed-forward direction to trigger PER on its own, even with the literature hunger mechanisms. This is either a model limitation (point neurons, uniform weight per synapse, glutamate always inhibitory) or a missing hunger mechanism on the leg relay.

### Testing the model assumptions on the leg route (option 1, 2026-10-03)

**Glutamate sign** (`FLY_GLU_SIGN`, diagnostic). Rest values are without homeostasis:

| Variant | Leg 100 Hz → MN9 | Rest MN9 | Labellar 100 Hz → MN9 |
|---|---|---|---|
| −1 (inhibitory, current) | 9 | 6.5 | 51 |
| 0 (no fast effect) | 21 | 9.8 | 51 |
| +1 (excitatory) | 7 | 2.4 | 8 |
| Shiu per-connection signs | 6 | 3.6 | 29 |

- With its own homeostatic warm-up, glutamate-neutral is worse: labellar 30 Hz → MN9 0.9 Hz, leg ≈ 0.
- Homeostasis lowers the whole network's excitability to compensate for the missing inhibition.
- Conclusion: the glutamate sign does not explain the leg gap.

**Strength at the leg relay** (`--release_gain` on the 8 AN01B004 / AN_GNG_162, hungry):

| AN01B004 release | Leg 100 Hz → MN9 (R) |
|---|---|
| ×1 | 3.7 |
| ×2 | 3.4 |
| ×4 | 7.1 |
| ×8 | 29 |

- Leg PER would need roughly 8× stronger synapses at this one relay, which is implausible as the only cause.

**The actual block is the resting state of the feeding motor chain** (`tools/diag_rest_drive.py`).
- Homeostatic offsets:

  | Neuron | Offset |
  |---|---|
  | MN9 | −26 to −28 mV |
  | AN01B004 | down to −30 mV |
  | Roundup | −10 to −12 mV |
  | Rounddown | −6 to −7 mV |
  | Bract2 | about −6 mV |
  | Network median | 0 mV |

- Without homeostasis, MN9 fires about 6 Hz at rest, although its net input is inhibitory:
  - inhibitory CB0862 and CB0903 at 7–11 Hz
  - excitatory DNge062 and Roundup at about 4 Hz
- With current-based synapses, this balanced bombardment produces large voltage fluctuations, so MN9 fires from noise. Homeostasis cancels that with an unphysiologically large hyperpolarization, which buries weak inputs. The strong labellar route still gets through; the 7-hop leg route does not.
- Real intrinsic plasticity shifts excitability by a few mV, and real synapses are conductance-based: inhibition shunts and excitation saturates near its reversal potential, which shrinks such fluctuations.

## Conductance-based synapses (default since 2026-10-03)

The model:
- **Driving forces:** each synapse now acts through a conductance with a driving force (`shaders/lif.glsl` `cond`).
  - E_exc = 0 mV (nicotinic ACh; measured)
  - E_inh = −75 mV (Cl⁻ channels: GABA-A/Rdl, GluCl, histamine-gated; approximate)
- **Calibration:** weights keep Shiu et al.'s 0.275 mV per synapse, normalised at mid-subthreshold, v_n = (v_rest + v_th)/2 = −48.5 mV, where his weight was fitted to behaviour. So inside the operating range a synapse has Shiu's effect. Excitation saturates toward 0 mV; inhibition shunts and reverses at −75 mV.
- **Integration:** exact exponential relaxation with the total conductance, using midpoint conductances over each 0.5 ms step.
- **Switches:** `--synapses=current` restores Shiu's current-like synapses. Each synapse model has its own homeostasis file (`data/homeostasis_offsets.bin`; `..._current.bin`).

Validation in the pure Shiu setting (no intrinsic physiology), 20 right sugar GRNs → MN9 R/L:

| Input | Exact reference, current | Reference, conductance (`tools/reference_lif.py` `cond`) | GPU, conductance |
|---|---|---|---|
| 100 Hz | 75 / 53 | 69.5 / 52 | 69.3 / 50.5 |
| 200 Hz | 116 / 72 | 121 / 82 | 119 / 78 |

- Normalising at rest (−52 mV) instead gives only 23 / 16 at 100 Hz.

With physiology and a fresh homeostatic warm-up:

| Check | Result |
|---|---|
| Resting rates | ORN 12.4, PN 4.8, AL local neurons 5.3, Kenyon cells 0.1, MBON 5.2, APL 0 |
| Bilateral sugar 30 / 100 / 200 Hz → MN9_R | 3.4 / 23 / 32 Hz |
| Same, hungry, at 30 Hz | 19 Hz |
| Giant fibre 100 Hz → TTMn | 51 Hz |

- AN01B004's offsets shrank from up to −30 mV to between +0.1 and −6.6 mV.
- MN9 still needs −28 to −30 mV, Roundup −9 to −11, Bract2 −6.
- Leg sugar still does not reach MN9: ≤ 1.6 Hz, and in the embodied hungry fly 1.1 Hz.
- So the large resting drive onto the feeding motor chain is not only a current-synapse artefact. It comes from the network's spontaneous activity converging on MN9: about 1 Hz assumed for every uncharacterised central neuron, with thousands of inputs.

### Where the leg-route gain is lost (2026-10-03)

**Driving each stage directly** (`--drive=indices:Hz`, no other input), MN9 R response:

| Driven stage | Reference (Shiu, no physiology) 30 / 100 Hz | This model 30 / 100 Hz |
|---|---|---|
| Roundup (CB0553) | 68 / 148 | 21 / 88 |
| Bract (DNge173/174) | 19 / 58 | 0.5 / 6.7 |
| AN01B004 (AN_GNG_162) | 5 / 52 | 4 / 20 |
| G2N-1 (CB0616) | 0 / 54 | 1 / 9 |

- Bract and G2N-1 are each sufficient for PER in real flies (Shiu, Sterne et al. 2022).
- In this model the interneuron stages lose 3–8× gain compared with Shiu's model. The cause is the intrinsic-physiology layer, chiefly the large negative homeostatic offsets on the feeding chain (MN9 about −29 mV, Roundup about −10, Bract2 about −6).
- These neurons are tonically driven at rest by the spontaneous network, and homeostasis holds them at their low set points.

**Variants tested** (each with its own 60 s warm-up):

| Variant | Result |
|---|---|
| Default rate 1 → 0.3 → 0.1 Hz (uncharacterised neurons) | MN9 offset −29 → −18 → −12 mV; leg route unchanged (≤ 0.5 Hz) |
| Homeostasis capped at ±5 mV | AL runs away (local neurons 75 Hz, PNs 26 Hz); Bract → MN9 2× stronger; leg route still ≈ 3 Hz |
| No default adaptation | Homeostasis re-balances; Bract → MN9 weaker (3.9 Hz); leg route ≈ 0 |

- The main build keeps a 1 Hz default rate, adaptation index 0.6, and the −40/+15 mV homeostasis range.

Summary: the leg route works in Shiu's raw model when its interneurons are driven, but leg GRNs cannot drive them hard enough (AN01B004 reaches 0–44 Hz). In the model with physiology, every stage is also damped. The real fly is quiet at rest but highly excitable along this chain. A noisy point-LIF homeostatically pinned to fixed set points cannot be both.

## Non-spiking (graded) neurons (2026-10-04, on by default)

- **Which neurons:** APL (2; Papadopoulou et al. 2011; Amin et al. 2020) and the patchy antennal-lobe local neurons lLN2P_a/b/c (34; Schenk & Gaudry 2023 eNeuro; R32F10 patchy LNs, Sizemore et al. 2023). Both are non-spiking in recordings.
- **Dynamics:**
  - These neurons never spike, reset or go refractory; their membrane integrates continuously, with membrane noise.
  - They release transmitter stochastically at f(v) = r_max / (1 + exp(−(v + 45)/2)), with r_max = 100 Hz. The release curve is approximate.
  - Implementation: `shaders/lif.glsl` binding 23, `data/graded_release.bin`, rule `graded` in `data/physiology_rules.json`.
- **Excluded:** graded neurons have no resting-rate target, adaptation or homeostasis.

Results after a fresh warm-up:
- **lLN2P:** release about 57 events/s at rest (near the top of the curve; they integrate ORN/PN input without spike resets).
- **APL:** tonic graded inhibition at about 5 events/s (previously forced silent). Kenyon cells 0.2 Hz; PNs 3.4 Hz (was 4.8).
- **Unchanged:** sugar → MN9 (bilateral 100 Hz → 23/11 Hz) and giant fibre → TTMn (52 Hz).
- **Not fixed:**
  - The spiking AL hubs il3LN6 and lLN2F_b still sit at the −40 mV homeostasis clamp.
  - They are spiking types (Seki et al. 2010 type I), so making lLN2P graded could not tame them.
  - The leg route is unchanged.

## Neuromuscular legs (Phase 6, in progress, 2026-10-05)

**Motor side** (`tools/build_leg_map.py` → `data/leg_motor_map.json`):
- All 391 BANC leg motor neurons are assigned, from their muscle-target annotations, to six joint degrees of freedom per leg: coxa protraction and adduction, trochanter, femur rotation, tibia, tarsus.
- `scripts/fly_legs.gd`:
  - Firing rate → muscle activation: a = r/(r + 30 Hz), filtered with 30 ms.
  - The agonist and antagonist pools set a joint equilibrium angle, and the NeuroMechFly skeleton joints relax to it with a 30 ms time constant.
  - Ranges and time constants are approximate.
- These replace the cosmetic leg swing (`--legs=0` restores it).

**Sensory side:** 886 proprioceptors (915 since the 2026-10-09 re-labels) drive their real BANC neurons every frame:
- femoral chordotonal organ claw (tibia position, flexion- and extension-tuned)
- hook (movement direction)
- club (movement or vibration)
- hair plates (coxa and trochanter angle near the joint limits)
- campaniform sensilla (muscle-force strain proxy)

Tuning is approximate (Tuthill & Wilson 2016; Mamiya et al. 2018).

**Walking rhythm (CPG): reproduced offline, partly live**

Target: Pugliese et al. 2025 bioRxiv. Driving DNg100 produces a leg motor rhythm via E1 = IN17A001 → E2 = INXXX466 → I1/I2 (IN16B036 / IN19A007) → E1.

1. **Exact reproduction of their model** (`tools/pugliese_repro.py`):
   - Inputs: their BANC front-leg subnetwork, weights and surface areas (`data/raw/pugliese`: Zenodo 22260924 and github smpuglie/Pugliese_2026 @10e7661, CC-BY-4.0).
   - Result: leg motor neuron rhythm 0.5–0.66 at 12.5–17.5 Hz.
   - With our weights and signs swapped in on their neurons: 0.65 at 13.8 Hz. Our synapse data are fine.
2. **Their rate model on our whole BANC nerve cord** (`tools/vnc_rate_model.py`, 25,227 neurons, stimulating the right-soma DNg100 135733, whose axon targets the left legs):

   | Size normalisation | Result |
   |---|---|
   | Measured surface area | E1/E2/I2 and motor neurons rhythmic, 0.96–0.98 at 14 Hz |
   | (synapses/median)^0.60 | rhythmic, 1.0 at 16 Hz |
   | None | runaway, no rhythm |

   - Size normalisation (larger neurons less excitable) is required.
3. **Ported to the live GPU brain:**
   - The 12,827 nerve-cord interneurons are now rate units, parameters mapped from the paper:
     - gain 21.82 Hz/mV ÷ size; threshold 0.344 mV × size above rest; r_max 200 Hz
     - size = surface area where measured, else synapses^0.60 (fit r = 0.90)
     - no noise, offset, adaptation or homeostasis
   - Transmission is smooth: quanta of weight/20 (`RATE_Q`).
   - Motor neurons, ANs, DNs and sensory neurons stay spiking.
   - Result: the CPG interneurons E1/E2/E3 now oscillate together, but weakly (0.25–0.37 at 3–5 Hz). Frequency does not yet rise with drive, and the leg motor neurons do not yet follow.
   - Remaining differences from the offline model: spiking motor neurons with homeostasis, the 5 ms synaptic filter and 1.8 ms delay, conductance synapses, and tonic input from brain, ascending and sensory neurons.
   - Validation with rate units:

     | Check | Result |
     |---|---|
     | Resting rates | unchanged |
     | Bilateral sugar 100 Hz → MN9 | 20 / 12 Hz |
     | Giant fibre → TTMn | 52 Hz |
     | Speed | 50 fps |

### CPG tuning steps (2026-10-05)

Offline, adding the live model's synaptic kinetics to their rate model (`RM_TAU_SYN=5`, `RM_DELAY=1.8`) slows the rhythm from 14 to about 4 Hz but keeps it (0.83). The slow live rhythm therefore comes from synaptic timing.

Live tests:
- **Conductance synapses on the rate units halve the rhythm.** So rate units now take linear, current-based input (excitation minus inhibition) as in the published model, while the spiking brain keeps conductance synapses (`shaders/lif.glsl`). With this, the live CPG is strong: E1/E2/I1/I2 at 0.57–0.61, 6.3 Hz.
- **Spiking leg motor neurons do not follow the rhythm** (≤ 0.25). Leg motor neurons are now firing-rate units too, as in Pugliese et al.; this is an abstraction, since real MNs spike. TTMn keeps its spiking escape rule.
- **The legs do not step yet.** Joint excursions under DNg100 drive are 0.003–0.09 rad, at 2–3 Hz, with no tripod phase pattern (`tools/analyze_gait.py`).
- **Per motor neuron, left front leg, DNg100 300 Hz** (`recordings/mn_lf.csv`):
  - Only 7 of 69 motor neurons are active, consistent with Pugliese et al. ("DNg100 typically recruited 2–10 leg MNs").
  - The active ones are strongly modulated (s.d. ≈ mean).
  - They are all one in-phase stance-like synergy (coxa retraction, trochanter extension, tibia flexion); the antagonists stay silent.
  - The muscle model averages activation over the whole pool, so 2 of 6 active neurons barely move the joint.
  - The gap has therefore moved to the biomechanics. Small insect legs moving in air need little force, and passive joint torques dominate (Hooper et al. 2009 J Neurosci). The "fraction recruited → fraction of range" muscle model is too crude.
- **Torque-based leg mechanics (`fly_legs.gd`):**
  - Motor-unit forces now add up.
  - Each fully active motor neuron gives 0.4 rad of excursion against passive stiffness (`DTHETA_MN`, approximate calibration).
  - Joint limits are soft (tanh), and the joint is overdamped with passive return (Hooper et al. 2009).
- **Result, tethered** (`screenshots/gait_dng100.png`):
  - With DNg100 driven, the legs move continuously and rhythmically: 4–20 Hz joint power 3–4× rest, peaking at about 5 Hz on several legs.
  - Swing in the 3.5–9 Hz band is 0.12–0.21 rad peak-to-peak (rest 0.01–0.06); total excursions reach 0.75 rad.
  - Real stepping is about 1–1.5 rad at 7–15 Hz with a tripod pattern. Not yet reached: amplitude is about a sixth of real, the rhythm is slower and irregular, and there is no inter-leg tripod coordination.
- **Next:** antagonist (swing-phase) recruitment, inter-leg coupling, and proprioceptive feedback while stepping.

### Swing/stance, coordination and free walking (2026-10-05)

1. **Free walking** (`--locomotion=legs`, `FlyLegs.odometry`):
   - Model: stance feet (foot height ≤ rest + 5% of reach, body frame) grip the ground without slipping, and the body moves by minus their mean motion (translation and yaw). It is a kinematic contact model without physics forces.
   - Result: with DNg100 driven, the legs move the body (4.9 mm path in 6.8 s, 5× rest) but the net displacement stays ≈ 0 (≤ 0.06 mm/s; real flies walk 10–30 mm/s). Feet push back and forth without a clean swing phase.
2. **Swing/stance recruitment:**
   - Offline, their model with our synaptic kinetics recruits 20 front-left motor neurons in two clusters about 180° apart: swing (promotors, trochanter and tibia flexors, tarsus depressors) and stance (remotors, trochanter extensors).
   - The stance cluster appears only if unmeasured neurons are given the median size. With the data-based size estimate (area ∝ synapses^0.60, r = 0.90; normalised by the median of the paper's measured subnetwork) only the swing cluster remains, at 7.1 Hz offline and 8 Hz live. Live and offline therefore agree.
   - Live, the right-soma DNg100 (which drives the left legs) gives swing-cluster rhythm at 8 Hz, in the real 7–15 Hz range. Any substantial left-soma DNg100 drive switches the left front leg to a slow, stance-dominated pattern.
   - In insects, stance is reinforced by load feedback from campaniform sensilla (Zill et al. 2004). BANC wiring from leg campaniform sensilla to the motor pools is mixed: direct excitation of retractors and trochanter motor neurons, but net inhibitory 2-hop pathways.
   - Ground load now drives the campaniform neurons in stance (`LOAD_HZ`, approximate). It does not yet produce propulsive stepping.
3. **Inter-leg coordination** (tethered, bilateral DNg100 150 Hz; CTr phase in the 4–9 Hz band):

   | Leg pair | Phase difference | Consistency |
   |---|---|---|
   | Left front vs left middle | −160° | 0.52 |
   | Left middle vs left hind | 178° | 0.51 |
   | Left front vs right front | −153° | 0.5 |
   | Left front vs right middle | none consistent | 0.03 |

   - Ipsilateral neighbours and the front legs alternate, as in a tripod gait. The cross-body tripod partner is not yet locked in phase.

### Real neuron sizes, descending-neuron screen, combinations (2026-10-05)

**Neuron sizes** (`tools/build_banc_cable.py` → `data/vnc/banc_cable_length.csv`):
- Cable length of all 114,999 BANC skeletons, computed from the SWC files of Bates et al. 2025 (Harvard Dataverse doi:10.7910/DVN/8TFGGB, `neuron_skeletons.zip`, md5 f7d16e8e…, CC-BY-4.0; user approved the 215.6 MB download). Codex's BANC attribute table has empty morphology columns.
- Surface area predicted from cable length: log area = 1.037 log cable + 1.179, r = 0.947 on 4,286 neurons with measured area.
- Coverage: 19,368 of 22,681 VNC residents.
- Size priority for rate units: measured area > cable-predicted > synapse-count estimate, normalised by the median of Pugliese et al.'s measured subnetwork.
- With these sizes, right DNg100 alone recruits a swing burst (promotors, trochanter flexors) and one remotor in anti-phase (−178°) at 7.1 Hz.

**Descending-neuron screen** (offline, each neuron alone; left front leg):

| Neuron(s) | Recruits | Rhythm |
|---|---|---|
| DNb08 left-soma (98130, 131703) | swing | 12 Hz, 0.99–1.0 |
| DNb08 right-soma 47118 | stance | 11 Hz, 0.21 |
| DNa02 left 92992 | stance | 10 Hz, 0.46 (24 Hz mean) |
| Right DNg100 | both | 7 Hz, 0.8 |
| DNp09, MDN, DNb02, DNp42 | little or nothing | — |

**Combinations** (offline):
- Right DNg100 + left DNa02: coxa remotors (−90° to −129°) and promotors plus trochanter flexors (≈ +155°) alternate at 7.1 Hz. This is the first swing/stance alternation in the motor output.

**Live free walking** (bilateral DNg100 ± DNa02 ± DNb08, ground-load feedback on):
- Net 0.08–0.21 mm/s, against 10–30 mm/s in real flies. Propulsive stepping is not yet achieved.

**Foot friction / physics contact:**
- The current contact model is no-slip (effectively infinite friction). Realistic friction and adhesion need a force-based physics body; NeuroMechFly does this in MuJoCo.
- 2026-10-08: that body is now installed. FlyGym 2.1.0 runs in a separate environment, because it pins mujoco < 3.10:

  ```
  py -3.13 -m venv .venv-flygym
  .venv-flygym/Scripts/python -m pip install -r requirements-flygym.txt
  .venv-flygym/Scripts/python tools/flygym_smoke.py
  ```

  FlyGym downloads about 14 MB of meshes on first use. Our tools point `FLYGYM_ASSET_CACHE_DIR` at `assets/flygym_cache` (git-ignored).
  - Smoke test: a free NeuroMechFly with default contact (sliding friction 1.0) and leg adhesion, legs held at the neutral pose, stays upright for 0.5 s. All 6 legs are in ground contact, and the lowest segment is at 0.06 mm.
  - Porting the MN → joint torque output onto this body: done 2026-10-08 (offline) and 2026-10-09 (live, `--physics=mujoco`); see the sections below.

### Descending-mix search and live test (2026-10-05)

**Search** (`tools/dn_mix_search.py`, offline, 381 mixes of walking DNs, symmetric left/right). Score per leg: swing pool and stance pool both modulated, phase near 180°, frequency 7–15 Hz; plus tripod coordination.
- Best mix: DNg100 + DNb08 + DNa02 + DNg97 = 4 : 1 : 1 : 1.
  - Left middle −178°, right front 160°, right middle 168°, right hind 172°, left front −98°.
  - Frequency 4.2 Hz (left front 8.3 Hz).
- Stronger DNg100 raises the frequency (7.5–8.3 Hz in some mixes) or tripod coordination (up to 0.33), but no mix reaches both.

**Live free walking** with this mix (live rates 200 / 50 / 50 / 50 Hz):
- 0.27 mm/s net, the best so far.
- Stance fraction: left front 0.98, left middle 0.00, left hind 0.24, right front 0.95, right middle 1.00, right hind 0.81.
- Only the hind legs switch between stance and swing (2–2.3 cycles/s).

**Without proprioceptive input** (`--proprio=0`):
- The left legs cycle (left front 1.8, left middle 4.7, left hind 4.8 cycles/s).
- The right legs stay planted (0.96–1.0).
- So the proprioceptive loop, with approximate tuning and no walking-state gating, locks the left middle leg in swing. The right legs are held in stance by a left/right asymmetry in tonic drive; whether that comes from DN sidedness or from the brain/nerve-cord joining is still to be tested.

### Left/right posture lock and proprioceptor fixes (2026-10-05)

**Posture lock** (`recordings/legpools.csv`, tuned descending mix, proprioception off):
- The left middle coxa promotors fire at 154 Hz, holding the leg up and forward. They are excited by IN17A052 (128 Hz), right-soma DNg100 and DNa02.
- The right middle promotors are silent, inhibited by IN21A001 (104 Hz). Instead the right middle retractors fire at 58 Hz.
- Left and right middle legs are anti-phase in a tripod, so this looks like a frozen tripod: the CPG settles into one phase and stops advancing.
- Some motor-neuron fragments are present (femur reductors with only 37–78 input synapses and 0.5–0.8 mm of cable). They are tiny and therefore hyper-excitable as rate units.

**Proprioceptor fixes:**
1. **Claw/hook tuning from wiring** (`tools/build_leg_map.py` → `feco_tuning`). Lee et al. 2025 (Nat Commun): flexion-encoding claw/hook axons excite tibia extensor and inhibit flexor motor neurons; extension-encoding axons do the reverse.
   - Each BANC claw/hook neuron is classified by its signed 1+2-hop drive: claw 98 flexion / 56 extension; hook 74 / 51.
   - This replaces the arbitrary alternation. MANC type names (SNpp50/51, SNpp39/41) align only loosely.
2. **Presynaptic inhibition** (Dallmann et al. 2025 Nature): movement-encoding (hook, club) afferents are suppressed during self-generated movement by GABAergic presynaptic inhibition.
   - 352 hook/club axons have inhibitory BANC inputs onto their terminals. These synapses are removed from the spiking graph and are now used to scale each axon's release live (mean gain about 0.67 while walking).

**Result, live free walking** (tuned mix):
- 0.29 mm/s.
- Left middle no longer locked up (stance 0.79).
- Left middle, left hind, right front and right hind switch stance/swing at 1.8, 3.8, 1.4 and 2.9 cycles/s.
- Left front and right middle stay planted.

### Musculoskeletal validation of the motor map (2026-10-05, MuJoCo)

`tools/msk_muscle_test.py` → `data/tables/msk_muscle_effects.csv`:
- **Model:** the Hill-type musculoskeletal front-leg model in the FlyGym assets (`assets/flygym/model/musculoskeletal`, converted from OpenSim with MyoConverter, Apache-2.0). It has 15 named muscles that match BANC motor-neuron types one-to-one, with fitted joint stiffness 0.4 and damping 0.02. It runs in MuJoCo 3.14 (`pip install mujoco` in `.venv`).
- **Method:** its STL meshes are not shipped, so mesh geometry is stripped (explicit inertials keep the mass). Each muscle is fully activated alone for 0.5 s, and the change of every joint is measured against the passive (unactivated) state.
- **Confirms our joint and direction mapping:**

  | Joint | Agonists | Antagonists |
  |---|---|---|
  | Trochanter | flexors −0.38 to −0.73 rad | extensors +0.48 to +1.31 |
  | Tibia | flexor +0.71 | extensor −0.98 |
  | Coxa | promotors −0.22 / −0.74 (pitch) | remotor/abductor +0.65 |

- **Simplification in our model:** the coxa rotators act mainly about coxa yaw and roll, which our single protraction DoF lumps together.
- **2026-10-08 cross-check with meshes:** FlyGym 2.1.0 bundles the full FlyMimic model (Ozdil et al. 2026) with meshes. `tools/flygym_smoke.py` gives the same tibia result (flexor +0.708 rad, extensor −0.976 rad), so stripping the meshes did not bias the table.
- **Scale:** full-muscle excursions of 0.5–1.3 rad agree in magnitude with `DTHETA_MN` = 0.4 rad per motor neuron (2–6 motor neurons per muscle).

### MuJoCo body in closed loop with the nerve cord (2026-10-08, offline)

This step moves the body from our kinematic Godot legs to a physical body. The goal is one body at true scale, with the brain, eyes and nerve cord all wired to it. Posture and walking should come out of the network and physics, with no scripted standing or walking functions.

- **Setup** (`.venv-flygym/Scripts/python tools/nmf_closed_loop.py`; shared model in `tools/vnc_body_model.py`; network exported by `.venv/Scripts/python tools/export_vnc_rate_net.py`):
  - **Body:** the NeuroMechFly body in MuJoCo (FlyGym 2.1.0, full biological skeleton with 126 joint DoFs, head included). Units are mm, g and s; mass 1.024 mg, weight 10.05 µN.
  - **Nerve cord:** the full VNC rate model (25,227 neurons, 818,619 edges; Pugliese et al. equations, 5 ms synapse, 1.8 ms delay), stepped every 0.2 ms with two MuJoCo steps of 0.1 ms. It runs at about 1/12 real time.
  - **Motor side:** each degree of freedom gets torque = K·lim·tanh(0.4·(A_pos − A_neg)/lim), set against a passive spring K = 10 µN·mm/rad whose rest angle is the neutral pose. This reproduces the Godot model's equilibrium when the leg is unloaded. Coxa yaw, tarsal, head and abdomen joints are passive.
  - **Adhesion:** on while a foot touches the ground and its trochanter drive is not lifting it.
  - **Proprioceptors:** the same rules as `fly_legs.gd`. Campaniform sensilla now read the measured ground reaction force of their own leg instead of the old muscle-activation proxy.
- **Load-sensor runaway found and fixed.** The Godot proxy (25 Hz × summed muscle activation) feeds muscle activity back to the muscles. In a physical body it ran away: with no descending drive and only campaniform input, the hind-leg swing pools reached 460–620 Hz and legs lifted off.
- **Reflex sign probe** (`tools/reflex_probe.py`, `recordings/reflex_probe.csv`): a joint state is imposed on one leg with no drive, and the torque the motor neurons produce is read.
  - **Femur–tibia:** the claw/hook/club wiring gives **resistance reflexes** in 22 of 24 tests (6 legs × ±position, ±velocity), as measured in flies.
  - **Hair plates:** the old rule fired at either joint limit and gave **positive feedback at the trochanter in all 6 legs**. This was the cause of the "legs lock up" postures.
- **Hair-plate direction from wiring** (`tools/hair_plate_tuning.py` → `data/hair_plate_tuning.json`): each of the 206 hair-plate afferents was driven alone through the network. It is tuned to fire at the joint limit its output pushes away from: limit detectors with negative feedback (Pratt et al. 2024).
  - **Joint:** trochanter where BANC annotates it (26 neurons, front legs only), otherwise coxa (assumed).
  - **Result:** 124 afferents got a direction; the other 82 act too weakly at rest and keep the either-limit rule.
  - **Probe after the change:** coxa bends are resisted in 5 of 6 legs and trochanter bends in both front legs. The middle and hind legs have no annotated trochanter hair plates.
- **Result (2 s runs, last 1.5 s; `recordings/nmf_closed_loop_*.csv`):**

  | Run | Thorax height | Forward speed | Legs |
  |---|---|---|---|
  | No leg sensors, walking drive | 0.59 mm (body sags) | +0.11 mm/s | feet shuffle, motor neurons 3–20 Hz |
  | Sensors on, no descending drive | 1.76 mm (stands) | 0.03 mm/s | front/middle legs in stance tone (stance pools 400–1,400 Hz); hind legs oscillate at 9–10 touchdowns/s |
  | Sensors on, walking drive (4:1:1:1) | 1.75 mm | −0.18 mm/s | almost the same as no drive |
  | Same, drive doubled | 1.65 mm | −0.06 mm/s | front-leg swing silenced, hind legs oscillate |
  | Sensors on, adhesion off | 0.51–0.52 mm (falls) | — | load signal ≈ 0, stance support lost |

- **What this means:**
  - Standing against gravity now **emerges from the connectome's reflex arcs**: resistance reflexes plus load feedback, with no hand-written posture controller. (2026-10-09 correction below: only with strong adhesion; the fly is not yet balanced.)
  - Walking does not. The descending command, tuned open-loop, is too weak against the reflex tone, and in real flies walking also changes reflex gains.
  - With adhesion on, the campaniform sensilla saturate (mean 140 Hz), because the 40 µN adhesion pull is about 4× body weight and the contact force includes it. Their response curve needs a physical calibration.
- **Next:**
  - Campaniform response from cuticle strain (graded, not saturating).
  - Re-run the descending-mix search in closed loop with the body.
  - Couple this physics body to the live Godot brain and eyes. Godot will pose its body and head from MuJoCo every frame, so the 1,709 facets stay physically on the head and keep their wiring.

### Load sensing from cuticle strain; adhesion and balance (2026-10-09)

- **Campaniform sensilla now read cuticle strain from the physics.**
  - **What is measured:** the bending moment carried through each femur base. MuJoCo `cfrc_int` gives the force and torque the coxa transmits to the femur subtree (weight, ground contact, adhesion, inertia); the part perpendicular to the femur axis is the bending moment.
  - **Unit:** M_REF = (body weight / 3) × leg length.
  - **Response:** rate = 150 Hz × x / (x + 1), graded instead of hard-capped.
  - **Basis:** the shape and M_REF are assumed. That campaniform sensilla encode strain is from Zill et al. 2004.
- **FlyGym's adhesion is not physical as a constant.** The MuJoCo adhesion actuator pulls the foot into the ground with a constant force for as long as it touches. Real pads resist being pulled off; they don't press the foot down.
  - At the NeuroMechFly default of 40 µN per leg (4× body weight), planted feet carry 37–45 µN, the strain reads 10–13 × M_REF, and the load sensors saturate.
  - I found no measured *Drosophila* adhesion force. Stick-insect toe pads reach up to about 0.8 × body weight.
- **Passive checks** (no neurons):
  - Without adhesion, the body rests on its joint springs at 0.71 mm with all feet down.
  - With 40 µN adhesion, it rests at 1.08 mm.
- **Closed loop, sensors on, no descending drive** (`recordings/nmf_closed_loop_nodrive_adh*.csv`):

  | Adhesion per leg | Result |
  |---|---|
  | 0 or 2 µN | Reflexes push the body up to 1.56 mm by 0.3 s. Support is uneven: the front legs lose contact. The fly tips over (thorax 0.50 mm, no feet on the ground). |
  | 10 µN (about 1× body weight) | Stays upright at 1.74 mm. Load sensors average 73 Hz (not saturated). Hind legs step in place at 10–17 touchdowns/s. |
  | 40 µN (FlyGym default) | Upright at 1.70 mm. Load sensors saturated. |

- **Honest status:**
  - The wiring produces active support; the reflexes do lift the body.
  - **It does not yet balance.** Without strong adhesion the uneven push tips the fly over.
  - Standing at 10 µN depends on an adhesion value that is assumed.
- **Next:**
  1. Find the source of the left/right and front/hind tone asymmetry: the right front leg's resting trochanter torque is −6.4 µN·mm versus −0.1 on the left front, and the hind legs oscillate even with no drive.
  2. Model adhesion physically: resist detachment only, with a measured or bounded force.
  3. Run the descending-mix search in closed loop.
  4. Couple the body to Godot.

### One body: the live brain and eyes on the MuJoCo body; tone asymmetry; pad adhesion; closed-loop search (2026-10-09)

**1. Uneven resting tone: a data gap, not biology** (`tools/tone_asymmetry.py`). The nerve cord was settled at the neutral pose with no drive and one afferent kind on at a time.
- **Claw:** the right front leg gets a trochanter torque of −5.5 µN·mm; the left front gets 0.
- **Campaniform:** under an equal load, front-leg coxa and hind-leg trochanter torques point in **opposite directions** on the left and right sides.
- **Cause: the BANC sensory annotations are incomplete.**
  - Campaniform-sensillum neurons are annotated as 27 and 24 in the front legs, but only 2 per middle or hind leg. Real legs have dozens each.
  - The middle and hind legs instead have 34–58 "hair plate" neurons, of the same cell types (SNpp45, SNpp52) as the front-leg campaniform sensilla.
  - Claw counts differ between sides: left middle 34, right middle 13.
- These cannot be split without inventing labels, so they stay as they are and go on the **"missing for 1:1" list**.

**2. Physical adhesion** (`tools/nmf_body.py`, `--adhesion pad`, now the default).
- **Model:** per leg, a MuJoCo connect constraint to the touchdown point. It carries only what the leg loads it with; it breaks above `pad_fmax` or when the leg actively lifts (peeling). It never pulls a foot down.
- **Passive body:** stands at 0.76 mm.
- **With the reflex network:** at 2 or 5 µN the fly falls (0.53–0.58 mm); at 10 µN (about body weight) it stays upright (100% of the time) at 0.68 mm, about passive height. The earlier 1.7 mm "stand" depended on FlyGym's constant 40 µN pull.

**3. Descending-mix search in closed loop** (`tools/dn_mix_closed_loop.py`, `recordings/dn_mix_closed_loop.csv`): 42 trials, each 2 s of physics, with DNg100, DNb08, DNa02, DNg97 and DNp09 at 0–800.
- **Best:** 1.23 mm/s (DNg100 : DNb08 : DNa02 : DNg97 = 400 : 400 : 800 : 200).
- **No-drive control:** drifts at 0.46 mm/s. Real flies walk at 10–30 mm/s.
- At most 4 legs step, never in a tripod.
- 2 trials ran out of MuJoCo constraint memory (the arena is now 64 MB).
- **Conclusion:** no descending mix of the nerve cord alone produces walking. Tuning further would only fit noise. The nerve-cord-only loop lacks the brain's tonic descending input and walking-state reflex modulation, which is why the live coupling (4) came next.

**4. One body, live** (`--physics=mujoco`; `tools/body_server.py`, client in `scripts/fly_legs.gd`; protocol test `tools/body_server_test.py`, which passes).
- **What happens:**
  - Godot starts the server.
  - Each brain update, Godot sends the brain's 391 leg-motor-neuron rates.
  - MuJoCo advances by exactly the brain's simulated time.
  - Godot receives all 69 segment poses and the 886 proprioceptor rates, and keeps presynaptic gating in the brain.
  - Heading and planar position move the fly node; everything else sits on the segment nodes.
- **Verified:** the MuJoCo neutral pose, mapped to Godot, reproduces every segment's rest transform to within 5×10⁻⁶. Units, axes, rotations and neutral pose are identical, so the eye cameras and facets sit on the physical head.
- **Speed:** the brain stays at 1.00× real time (15–17 fps vs 25 without physics). The physics alone runs at 0.6× real time.
- **Escapes:**
  - Over 20 s the jump motor neuron TTMn spikes 6–7 times in physics mode, versus 1 (the start-up transient) without physics. The giant fibre stays at 0 Hz.
  - Holding the head rigid does not change it. Cutting the leg proprioceptors (`--proprio=0`) brings it back to 1.
  - So leg sensory input reaches TTMn inside the nerve cord. TTMn drives the middle-leg tergotrochanter muscle, which is itself a leg muscle.
  - The escape counter treats every TTMn spike as a jump command. In physics mode the jump is counted but not executed (no jump model yet).
- **Not driven by the physics yet:** the proboscis (PER animation), the wings, and the neck motor neurons (head held by a passive spring). The MuJoCo floor is flat, and the Godot arena objects are not in the physics.

### Neck motor neurons drive the physical head; TTMn traced (2026-10-09)

**Neck** (`tools/build_neck_map.py` → `data/neck_motor_map.json`; `Neck` in `tools/vnc_body_model.py`; neck actuators in `tools/nmf_body.py`):
- **Motor neurons and axes, from BANC annotations:**
  - Yaw: ADNM1/2.
  - Roll: DProN1–4, plus DProN5 for roll only (its pitch direction is not annotated).
- **Side:** taken from the nerve the axon leaves through. One ADNM soma lies on the opposite side from its nerve.
- **Direction:** each motor neuron turns or rolls the head toward its own side. This is assumed.
- **Muscle model:** the same activation-to-torque rule as the legs, with a range of 0.35 rad (about 20°, assumed).
- **Axis mapping:** FlyGym's head-joint names are not biological axes (its "roll" joint turns about the vertical axis). The mapping is set and checked kinematically.
- **Test** (`tools/body_server_test.py`, passes): the left-yaw motor neurons at 150 Hz turn the head +0.335 rad left, with no roll.
- **Sensors** (`tools/neck_sensor_tuning.py` → `data/neck_sensor_tuning.json`): 31 prosternal-organ hair plates (SNpp19, head position) and 39 neck chordotonal neurons (speed).
  - Axis and direction come from the same signed 1+2-hop wiring criterion as the leg claw/hook sensors.
  - Prosternal: 15 roll afferents on the left and 11 on the right tuned to each direction; 5 yaw afferents.
  - Chordotonal: 21 of the 39 have no path to the annotated neck motor neurons inside the nerve cord.
  - A full-network test was rejected: the left DProN1 has only 231 annotated input synapses against 1,438 on the right, a reconstruction asymmetry, so every afferent appeared to roll the head right.
- **Live** (20 s, `recordings/probe_neck_ttmn_live.csv`): the neck motor neurons fire sporadically (up to 13–16 Hz) and move the head within ±0.14 rad yaw and ±0.18 rad roll. The eyes ride on it.
- **Not mapped (data gap):** DProN6–9, and the 20 brain neck motor neurons of the cervical nerve. Neither dataset gives their axis.

**TTMn** (the jump motor neuron; `recordings/probe_ttmn_r_inputs_live.csv`, `probe_gfc2_inputs_*.csv`):
- **In physics mode, only the right TTMn fires,** tonically at 4.7 Hz (up to 37 Hz) in 93% of frames. A real TTMn is silent at rest.
- **The giant fibre is not involved** (0 Hz).
- **Where the excitation comes from** (synapse·Hz, live):
  - About 11,300 of the 16,900 total comes from two right **GFC2** interneurons (giant-fibre-coupled), firing at 138 and 150 Hz. Without physics they fire at about 3 Hz.
  - GFC2 itself is driven by leg premotor interneurons recruited by the physical proprioceptive input: IN04B036 (14,500), IN04B100 (7,600), IN20A.22A001/003 (6,300) and IN04B049 (3,000).
  - GFC2 also gets recurrent GFC2→GFC2 excitation (9,400), which can hold the loop on.
- **Open questions:**
  - Whether real GFC2 is recruited by leg input this way. Its rate-unit model has no adaptation, which may let the recurrent loop latch.
  - How strong the TTM muscle is. Only qualitative takeoff data was found (Card & Dickinson 2008, doi:10.1242/jeb.012682), so TTMn stays an ordinary member of the middle-leg trochanter-extensor pool.
  - In physics mode, TTMn spikes are counted as escapes but not executed.

### Escape circuit: GFC latch removed, GF→TTMn 1:1 restored, spontaneous giant-fibre spikes traced (2026-10-09)

1. **GFC1–4 now spike.** The giant-fibre-coupled interneurons (36 neurons, `data/physiology_rules.json`) were Pugliese rate units, which have no adaptation, and GFC2 latched at 140–150 Hz. They are now spiking, with the default sparse baseline and spike-frequency adaptation (assumed).
   - **Physics mode, at rest:** GFC2 averages 6 Hz, and TTMn is silent with no escapes in 20 s, where it fired 6–7 times before.
   - `recordings/probe_escape_*.csv`; the physiology rebuild was first checked to be byte-identical before the rule was added.
2. **GF→TTMn coupling raised from 8 to 16 mV** (`data/vnc/electrical_synapses.json`, connectome metadata; GF→PSI too).
   - The 8 mV value assumed the standard resting potential. But the quiescent escape motor neurons rest 8 mV lower (their physiology rule), so TTMn followed only 0.29 of GF spikes.
   - At 16 mV, a GF driven at 53 Hz gives TTMn 0.92 spikes per GF spike, matching the measured 1:1 following (Tanouye & Wyman 1980). Basis: calibrated to that measurement.
3. **The giant fibre fires spontaneously** (`recordings/probe_gf_inputs_live.csv`, `gf_inputs_weights.csv`). Now that TTMn follows it, this is what remains of the "escapes".
   - **Rate at rest:** 0.84 Hz in physics mode (13 onsets in 20 s) and 0.44 Hz on the kinematic body (3 escapes in 20 s; these are the take-offs seen in the default mode). A real GF is silent at rest.
   - **Tonic drive:** LC4 loom detectors at 8.8 Hz with the scene standing still (805 synapses; 7,100 synapse·Hz).
   - **Trigger:** DNp70, whose rate doubles from 3.2 to 6.2 Hz in the 100 ms before each GF onset (587 synapses).
   - **Next to examine:** why LC4 is tonically active in a static scene, and what drives DNp70.

### Why the live fly sinks; homeostasis must be learned upright (2026-10-09)

- **Support pools, live** (`recordings/probe_support_live.csv`, `--physics=mujoco`, 20 s):
  - Only the middle legs drive their trochanter depressors: right middle 45–70 Hz, left middle 3–14 Hz.
  - Front and hind legs have about 0 Hz depressor drive. Right front and both hind legs drive levators (10–38 Hz).
  - The thorax sinks from 1.1 mm (1 s) to 0.6 mm (8 s), then rests on the belly at 0.45 mm (passive standing height 0.76 mm). The uneven middle-leg push is the sideways lean seen live.
  - This points to the missing load feedback: BANC annotates only 2 campaniform neurons per middle or hind leg (data gap above).
- **Homeostasis re-learned on the physical body was rejected.**
  - A 60 s `--homeostasis --clean_air` warm-up in physics mode lowered spontaneous GF firing (1 escape in 20 s instead of 6; GF 0.36 Hz).
  - But the fly fell on its back during the warm-up, so the offsets were learned for a fly flailing on its back. Neurons at the −40 mV floor rose from 494 to 947, and the fly fell over again.
  - The 2026-10-05 offsets are restored. **Rule:** homeostatic offsets must be learned while the fly is upright and behaving normally.
- **Spontaneous GF firing, upstream:** AVLP500 (visual + central input onto DNp70) sits at the −40 mV homeostatic floor and still fires 77–100 Hz. 494 neurons are at that floor in the current offsets.

### Leg load sensors: MANC cross-check (2026-10-09)

`tools/manc_leg_sensory_check.py` checks the gap against MANC v1.0 (male nerve cord, Janelia public export, CC BY 4.0; source and checksum in `tools/fetch_data.py`).
- **MANC v1.0 does not fill the gap.** Per leg segment it types the FeCO (claw/hook/club), the trochanteral campaniform field (TrCS, only 2–4 per leg) and, in the front leg only, 19 hair plates. The other 79 / 107 / 120 proprioceptors per segment carry only the generic "proprioceptive" label.
- **BANC** annotates 81 / 81 / 107 "hair plate" neurons in front / middle / hind legs, but campaniform sensilla only 51 / 4 / 4. That is far more hair-plate neurons than real legs carry, so many of them are probably unlabelled campaniform sensilla. No public table says which.
- **Not used:** the newer MANC v1.2.1 annotations need a neuPrint account (owner's decision), and the FANC leg reconstructions need CAVE access.
- **Option without new data:** classify the unlabelled neurons by axon morphology. Use the BANC skeletons already downloaded, with the labelled front-leg campaniform and hair-plate axons as serially homologous references. Results would be labelled inferred.

### Leg sensory neurons identified from shape and wiring (2026-10-09)

`tools/classify_leg_sensory.py` → `data/leg_sensory_inferred.csv` (every call with probabilities), `data/leg_sensory_relabel.json` (validated re-labels only), `recordings/leg_sensory_cv.txt`.

**Descriptors**, built from BANC v626:
- **Morphology:** each leg neuromere's axon cloud (left legs mirrored) is registered onto the front-right one with ICP; median residual 0.05–0.10 of the neuromere radius.
- **Wiring:** synapse shares split by partner hemilineage, and separately by partner cell type. 380 interneuron types repeat in all three leg segments.
- **Classifier:** logistic regression per descriptor, trained on labelled leg sensory neurons.

**Validation:**

| Descriptor | 5-fold CV | Front-left → front-right | Front → middle/hind |
|---|---|---|---|
| Morphology | 0.81 | 0.78 | 0.29 |
| Wiring by hemilineage | 0.81 | 0.64 | 0.79 |
| Wiring by cell type | 0.86 | 0.78 | 0.81 |

- **Acceptance rule:** two independent descriptors agree, each with p ≥ 0.8. Trained on front legs and tested on labelled middle/hind neurons, it is **95% correct** (morphology + wiring: 84 accepted; two wiring views: 417 accepted).

**The load-sensor gap is not resolved.**
- Campaniform vs hair plate (front legs, where BANC labels both): morphology 0.71 (= the majority-class baseline), wiring by hemilineage 0.60, wiring by cell type 0.72 (baseline 0.63).
- No middle/hind "hair plate" can be shown to be a campaniform sensillum. BANC's front-leg labels may themselves be partly noisy.
- 85 of the 154 middle/hind hair plates also have no skeleton in the v626 archive.

**Validated re-labels** (FeCO, bristle and taste classes; used in `tools/build_leg_map.py`):
- 34 new FeCO afferents, from 20 orphan neurons, 11 untyped chordotonal neurons and 3 BANC "hair plates" (2 claw, 1 hook). Their claw/hook tuning comes from wiring as before.
- 1 "hair plate" is a bristle.
- Orphans: 47 are bristles, 5 taste and 2 tactile-taste. These are stored for wiring touch and taste later.
- **Leg-map change:** the six legs gain 33 FeCO afferents and lose 4 hair plates; the motor side is unchanged. 985 proprioceptors are now fed back (886 leg before).

**Effect live** (`--physics=mujoco`, 20 s; repeated runs are identical, so the comparison is exact):
- Right-middle depressor pool: 41 → 7 Hz. Thorax mean: 0.57 → 0.49 mm.
- Neither version stands; push-down tone is missing in four of six legs either way.
- The re-label is kept, because the data is more accurate. It shows that standing does not come from adding sensors alone.

### Why the front/hind legs did not push down: a hot nerve cord; homeostasis for rate units, learned upright (2026-10-09)

1. **Depressor inputs traced live** (`recordings/probe_dep_inputs_live.csv`, `dep_inputs_weights.csv`):
   - Front- and hind-leg depressor pools received −170k to −246k synapse·Hz of inhibition, against +16k to +94k of excitation. The inhibition came from interneurons of hemilineages 13A, 16B and 08A firing tonically at 50–150 Hz.
   - The nerve-cord rate units (13,162 neurons) had no homeostasis, and the population ran at about 110 Hz.
   - Pool thresholds do not differ between legs (0.50–0.69 mV), so neuron size is not the cause.
2. **Stale-offset bug fixed** (`scripts/fly_brain.gd`). 371 leg motor neurons still carried homeostatic offsets (mean −1.2 mV, down to −14 mV) learned when they were spiking. At a rate unit's 21.8 Hz/mV, that silenced some of them. Offsets are now applied only to neurons that have a homeostatic target.
3. **Rate units now get homeostasis**, like every spiking brain neuron: set point 1 Hz for nerve-cord interneurons (the model's default sparse baseline) and 0.5 Hz for leg motor neurons (the motor rule). Basis: mechanism literature; set points approximate.
4. **Learned upright.** A tether (`--mj_tether=1`, calibration only) holds the thorax level at neutral-pose height with all feet on the ground (1.03 mm). The 60 s warm-up ran in that state.
   - Rate-unit offsets: median +0.07 mV, 5–95% −3.5…+0.4 mV, none at the −40 mV floor. Brain neurons at the floor: 531 (494 before).
5. **Free standing, 20 s** (`recordings/probe_support_homeo.csv`):

   | | Before | After |
   |---|---|---|
   | Thorax height | sank to 0.45 mm | holds at 0.62–0.72 mm (mean 0.66) |
   | Middle-leg depressors | low | left 45 Hz, right 103 Hz |
   | Right-hind depressor | 0 | 6 Hz |
   | Escapes in 20 s | 6 | 1 (start-up) |

   - **Still wrong:** front legs and left hind have no depressor drive. The body sits below its passive height (0.76 mm). The right/left middle-leg imbalance remains (the lean).
   - Some nerve-cord populations still average about 100 Hz once standing free, so the set points are not fully held outside the tethered state.

### Two-stage upright calibration; no set point for motor neurons (2026-10-09, in progress)

- **`--homeostasis=continue`** keeps learning from the saved offsets. Warm-ups in physics mode are saved only if the fly stayed upright: thorax at least 0.5 mm and up-axis at least 0.5 after 2 s. Otherwise "NOT saved" is printed.
- **Stage 2** (free standing, continuing from the tethered offsets) was saved, but its test removed nearly all depressor drive. Thorax 0.78 mm; hind levators 69–76 Hz.
  - The 0.5 Hz homeostatic set point for leg motor neurons was the cause. A standing fly needs tonic motor output, so leg motor neurons now have **no set point**; only the 12,791 interneuron rate units do.
- **Re-calibration without the motor set point was refused by the upright guard.** The tether's rotational hold was too weak (the fly twisted, up-axis −0.39) and the fly flipped when free.
  - The tether's rotational stiffness is now 100 µN·mm/rad (critically damped). It holds level against strong opposite leg torques (up-axis 0.996).
  - Probe CSVs now also record `thorax_up`.
- **Current offsets:** `data/homeostasis_offsets.bin` is the stage-2 file. Motor-neuron offsets in it are ignored (no set point).
- **Next:** repeat the tethered and free-standing warm-ups with the stiffer tether, then the free-standing test, now with orientation logged.

### Where the left/right lean comes from (2026-10-09)

Two-stage calibration with motor neurons free of a set point:
- **Stage 1** (tethered, from zero) was saved.
- **Stage 2** (free standing) was refused by the upright guard: the fly flipped (up-axis −0.99).

With the stage-1 offsets, the free fly rolls 35–55° (up-axis 0.58–0.80). Right front and right middle tibia extensors drive (53 and 131 Hz), while the left front leg is held up (levator 53 Hz). Tests (`recordings/probe_support_*.csv`):

| Test | Result |
|---|---|
| All 1,299 descending neurons silenced | Same asymmetry, so not the brain's commands |
| Descending neurons silenced **and** leg proprioceptors off | Symmetric (left/right differences 0–12 Hz); upright at 1.30 mm |
| Leave one afferent kind out | Club afferents carry most of it (differences shrink about 3×); no single kind removes it |
| Fly held level by the tether | Same asymmetry (right-middle tibia extensors 127 vs 20 Hz), so static, not a roll that amplifies itself |
| Leg motor-neuron input completeness (left front/middle have 45%/32% fewer input synapses than the right) corrected, `FLY_MN_COMPLETENESS=1` | No change (196 motor neurons scaled up, median ×1.38): silent pools have no input to scale. Hypothesis rejected; the option is kept but off |
| Front tibia-extensor inputs traced (`recordings/probe_tibext_inputs_live.csv`) | Same interneuron types on both sides, opposite states: left IN13A063/IN13A014/IN08A005 (inhibitory) at 95–99 Hz vs 0 Hz on the right; right IN04B034/038/031, IN03A065 (excitatory) at 14–184 Hz vs 0 Hz on the left |

**Conclusion:** each side's premotor network locks into a different stable state, driven by the sensory input. The interneurons sit at about 100 Hz despite their 1 Hz set point. Pugliese rate units have no spike-frequency adaptation, so recurrent loops can latch, as GFC2 did. **Next:** give the nerve-cord rate units the brain's adaptation (AdEx-style current, τ_w 300 ms).

Also fixed: `--mj_sensors` diagnostic (afferent kinds to keep). An empty argument from Godot is now no longer passed, since Windows dropped it and the server failed to start.

### Adaptation for nerve-cord rate units; size-principle motor force; gradual set-down (2026-10-09)

1. **Spike-frequency adaptation for all 13,162 rate units** (`shaders/lif.glsl`, `tools/build_physiology.py`), as the spiking neurons already have.
   - An adaptation current with τ_w = 300 ms is subtracted from the input. Rate units have no membrane noise, so it uses that state slot.
   - It grows by b per released spike-equivalent, with b = (1/AI − 1)/(g τ_w), so that a step settles at AI × the onset rate. AI is 0.6 for interneurons (the brain default) and 0.85 for leg motor neurons (the motor rule). Median b is 0.076 mV.
   - Basis: mechanism literature; indices approximate.
   - **Effect:** nerve-cord populations drop from 70–100 Hz to 7–26 Hz.
   - **Effect, held level by the tether:** left/right pools are now nearly symmetric. Depressors front 5.0/4.9 Hz, middle 6.7/7.7 Hz; middle tibia extensors 34/29 Hz. Front tibia extensors 1.3/10.7 Hz remain uneven. The opposite-state latch is gone.
2. **Size-principle motor force** (`tools/build_leg_map.py`, default; `FLY_MN_FORCE_UNIFORM=1` restores equal force). Each motor neuron's force is proportional to its surface area (cable-predicted), normalised within its pool so the pool's total force is unchanged (Azevedo et al. 2020: small, early-recruited leg motor neurons give small forces).
3. **Gradual set-down** (`--mj_release=s`): the fly is held standing by the tether, which is then ramped off over 0.5 s.
   - An instant release acted as a catapult. The legs had been pushing against the tether, and the thorax jumped from 1.06 to 1.7 mm.
4. **Free standing after a 2 s set-down** (`recordings/probe_support_ramp.csv`):
   - The fly carries its own weight and stays level for about 1 s.
   - Then the left and right middle-leg tibia extensors **alternate in large bursts at about 3 Hz** (67/40 → 9/95 → 30/2 → 54/50 → 49/6 Hz) with no walking command. This throws the body up and over (4 s: on its back).
   - **Interpretation:** adaptation plus reciprocal inhibition makes the nerve cord's premotor network oscillate at rest (a half-centre rhythm). It is uncoordinated and strong enough to unbalance the body. Real flies keep the walking CPG quiet while standing.
5. **Calibration state:**
   - Stage 1 (tethered, with adaptation) was saved.
   - Stage 2 (free standing) was refused by the upright guard (the fly went over).
   - A completeness correction for left leg motor neurons (`FLY_MN_COMPLETENESS=1`) was tested and rejected (see above); off.

## Calibration ledger (motor side): what is data, what is set by hand

Kept so that any walking result can state exactly how much came from the connectome and how much from hand-set values. Basis: **measured** = from data; **literature** = published model or parameter; **assumed** = an approximate value I chose; **tuned** = adjusted while looking at walking. Only the descending command mix has been tuned to walking; everything else is measured, literature or assumed.

| Item | Value | Basis | Walking depends on it? |
|---|---|---|---|
| Wiring: BANC VNC synapses, signs (Dale), DN/AN joining | — | measured | yes |
| VNC transmitter predictions | used as given; some motor neurons have implausible predictions (e.g. TTMn octopamine / GABA); motor output uses rates, not signs | measured (predicted) | no |
| Motor neuron → muscle → joint DoF | BANC annotations | measured | yes |
| VNC interneuron dynamics | Pugliese et al. rate model (τ 20 ms, gain, θ, f_cap 200 Hz, W × 0.03) | literature | yes |
| Neuron size for rate units | measured area / cable-predicted (r = 0.947) / synapse fit | measured + fit | yes (stance recruitment depends on it) |
| Leg motor neurons as rate units (not spiking) | abstraction, as Pugliese et al. | literature model | yes (spiking MNs did not follow the CPG) |
| Rate units take linear (current) input; brain uses conductances | as the published model | literature model | yes (conductance halved the rhythm) |
| Synaptic filter 5 ms, delay 1.8 ms | Shiu et al. values | literature | yes (sets the 4–8 Hz frequency) |
| Muscle activation: R_HALF 30 Hz, τ 30 ms | — | assumed | yes |
| DTHETA_MN 0.4 rad per motor neuron | — | assumed | yes (amplitude) |
| Joint range and τ_joint 30 ms | NeuroMechFly-like ranges | assumed | yes |
| Stance rule: foot ≤ rest + 5% of reach | no-slip contact | assumed | yes |
| LOAD_HZ 40 Hz campaniform ground load (kinematic body only) | — | assumed | kinematic body only |
| Claw/hook flexion vs extension tuning | per neuron from its wiring: signed 1+2-hop drive to tibia extensor vs flexor MNs (Lee et al. 2025 criterion) | measured wiring + literature | yes |
| Presynaptic inhibition of hook/club afferents | release × 1/(1 + Σ syn·rate / I_HALF) using BANC inhibitory inputs onto each terminal (Dallmann et al. 2025); I_HALF = 500 syn·Hz | wiring measured; I_HALF assumed | yes |
| Proprioceptor tuning curve shapes (claw sigmoid width, hook/club gains, hair plate limits) | — | assumed | yes |
| MuJoCo joint spring K (springref = neutral pose) | 10 µN·mm/rad (FlyGym default); damping K × 30 ms | assumed (FlyGym default) | yes |
| MuJoCo torque per motor neuron | K × 0.4 rad (same equilibrium as DTHETA_MN), tanh-limited to the joint range | assumed | yes |
| Tarsal adhesion | pad bond (default since 2026-10-09): connect constraint at touchdown, breaks above `pad_fmax` = 10 µN per leg or when the leg actively levates; FlyGym's constant-pull actuator (`--adhesion auto`, 40 µN) kept for comparison | mechanics approximate; pad_fmax assumed (no Drosophila measurement found; stick-insect pads ≤ 0.8 × body weight) | yes (falls below about 1× body weight per leg) |
| Campaniform rate in MuJoCo | 150 Hz × x/(x+1), x = bending moment at the femur base / ((W/3) × leg length), from MuJoCo `cfrc_int` (2026-10-09; before: 120 Hz × ground force / W) | strain physics from the simulation; response shape and reference assumed | yes |
| Hair-plate joint and limit direction | joint from BANC annotation (trochanter) or coxa (assumed); direction = the limit its network output opposes (Pratt et al. 2024 limit detectors) | measured wiring + literature function | yes |
| Neck motor neurons → head yaw/roll | ADNM1/2 yaw, DProN1–5 roll (BANC); motor-neuron side from its nerve; ipsilateral rotation; range 0.35 rad | axes measured (annotation); direction and range assumed | head/eye stabilisation |
| Neck proprioceptor axis/direction | signed 1+2-hop wiring onto the neck pools; prosternal = negative feedback (Preuss & Hengstenberg 1992) | measured wiring + literature function | head/eye stabilisation |
| Rate-unit homeostasis | interneurons: set point 1 Hz (the default sparse baseline); leg motor neurons: none (a 0.5 Hz set point removed the tonic depressor drive). Learned upright: 60 s tethered (`--mj_tether=1`), then 60 s free standing (`--homeostasis=continue`) | mechanism literature; set points approximate | yes (without it the nerve cord ran at ~110 Hz and inhibition silenced the depressors) |
| Homeostatic offsets applied only to neurons with a set point | stale offsets (e.g. 371 leg motor neurons, learned when they were spiking) are ignored | — (bug fix 2026-10-09) | yes |
| Rate-unit spike-frequency adaptation | AdEx-style, τ_w 300 ms, index 0.6 (interneurons) / 0.85 (leg motor neurons), b = (1/AI − 1)/(g τ_w) | mechanism literature; indices approximate | yes (removes latching; creates a resting oscillation) |
| Motor-unit force ∝ motor-neuron size | weight × area / pool mean area | principle literature (Azevedo et al. 2020); sizes measured; proportionality assumed | yes |
| Set-down | tether held until `--mj_release` s, ramped off over 0.5 s | assumed (initial condition) | standing tests |
| Leg sensory re-labels | 34 FeCO afferents added, 4 hair plates corrected, from morphology + wiring (`data/leg_sensory_relabel.json`; acceptance rule 95% precise on labelled middle/hind neurons) | inferred from data | yes |
| Thorax tether (calibration only) | thorax held level at neutral-pose height with all feet down (1.03 mm); 2000 µN/mm, 100 µN·mm/rad, critically damped | assumed (calibration device, not physiology) | only during warm-ups |
| Giant-fibre electrical coupling (GF→TTMn, GF→PSI) | 16 mV (one GF spike lifts the quiescent motor neuron from its resting offset just over threshold) | calibrated to measured 1:1 following | escape |
| GFC1–4 dynamics | spiking with adaptation (not rate units) | assumed | escape (rate units latched) |
| Descending command (which DNs, how strong) | DNg100 : DNb08 : DNa02 : DNg97 = 4 : 1 : 1 : 1 (offline amplitude 400/100/100/100; live 200 Hz / 50 / 50 / 50 Hz), from a 300-trial random search plus an 81-point refinement (`tools/dn_mix_search.py`, `recordings/dn_mix_search.csv`, `dn_mix_refine.csv`) | **tuned** | yes |

**Free-walking diagnosis (2026-10-05)** (`stance_<leg>` and `foot_h_<leg>` columns in probe CSVs):
- All six feet are never down together (0% of the time).
- Instead, legs sit in tonic postures. Left middle is held up 98–100% of the time; left front and right middle are planted 98–100%.
- Foot-lift test (`--legs_lift_test`): trochanter flexion lifts the foot (+0.23 to +0.28 of reach per 0.3 rad), so the swing group can lift. Coxa protraction is horizontal only, and tibia flexion lowers the foot slightly.
- Conclusion: each leg's tonic bias exceeds its rhythmic modulation. Next to check: proprioceptive phase-transition mechanisms.

## Former limitation: a global antennal-lobe / mushroom-body runaway (fixed 2026-10-03, see "Spontaneous activity, adaptation and homeostasis")

Strong, sustained bilateral sugar input (both labellar sugar sets at 100 Hz) drives the Shiu et al. spiking model into a self-sustaining global state:
- APL about 435 Hz
- antennal-lobe local neurons about 200 Hz
- mushroom-body input neurons (MBIN) about 330 Hz
- Kenyon cells about 60 Hz
- MN9 silenced

It happens in their exact model at 0.1 ms (`tools/reference_lif.py`), with or without the mirror patch (the patch delays it from 0.4 to 1.4 s), and with APL's output removed. Their published 1-second trials mostly end before it fully shows.

The ignition path, at 10 ms resolution:
1. ALIN (taste input to the antennal lobe) at 280 ms
2. antennal-lobe local neurons at 340 ms
3. the whole antennal lobe, lateral horn and mushroom body within 20 ms after that

Real antennal lobes have spike-frequency adaptation, gap junctions and non-spiking local neurons (Seki et al. 2010), and none of these is in the model. That is the next fidelity fix for the central brain.

## Ventral nerve cord (Phase 4): BANC joined to the FlyWire brain

`tools/build_vnc.py` takes the nerve cord from **BANC**, the brain-and-nerve-cord connectome (Bates et al. 2025; female, one animal; Codex release 888, `data/raw/banc/`). It joins it to the FlyWire brain through the neck, as in the real animal.

**How the two datasets are joined:**

| Neuron group | Method | Result |
|---|---|---|
| Descending neurons | name + side; within a group, paired by brain-input similarity | 1,125 / 1,299 matched |
| Ascending neurons | similarity of brain connectivity (partner cell types; BANC uses FlyWire type names for 89% of brain neurons), optimal assignment | 1,139 / 1,736 matched (median cosine 0.65) |
| Sensory-ascending neurons | same method | 128 / 581 matched |

**Checks on the matching:**
- Run blind on descending neurons, the similarity matcher picks the right type 81% of the time.
- **95%** of matched ascending pairs, and 88% of descending pairs, agree on predicted transmitter, consistently across the similarity range.

**Added nerve-cord neurons: 22,832** (first build; the current build has 22,681 resident nerve-cord neurons)

| Class | Neurons |
|---|---|
| Interneurons | 12,827 |
| Sensory (leg/wing/haltere/abdomen chordotonal, campaniform, hair-plate, bristle and taste neurons) | 7,436 |
| Motor (leg, wing, haltere, neck, abdominal) | 699 |
| Unmatched ascending | 650 |

Only BANC synapses inside nerve-cord neuropils are used (818,000 connections, 7.5 million synapses); the brain stays FlyWire's. Total model size at that build: 161,471 neurons, 15.9 million connections (current build: **161,320 neurons, 15.73 million connections**). Turn the nerve cord off with `FLY_NO_VNC=1`.

**Electrical synapses** (`data/vnc/electrical_synapses.json`):
- Connectomes record chemical synapses only. The giant fibre's gap junctions onto TTMn (jump motor neuron) and PSI are documented (ShakB; Allen et al. 2006; Tanouye & Wyman 1980). They are modelled as true voltage coupling: one spike → +8 mV on the partner's membrane at the next 0.5 ms step (`lif.glsl` mode 2). Since 2026-10-09: +16 mV, because the quiescent escape motor neurons rest 8 mV lower; TTMn then follows the giant fibre 0.92:1 at 53 Hz.
- With the giant fibre driven at about 100–115 Hz, TTMn follows at 0.73–0.85 of its spikes and PSI at 0.70–0.79. PSI drives the DLM flight-muscle motor neurons through 397 chemical synapses.
- The escape take-off is now executed when **TTMn** fires (`vnc_jump_ttmn`); with the MuJoCo body it is counted but not executed.

**Leg taste through the nerve cord:**
- 701 BANC leg taste neurons are placed on the tarsi of their actual leg. Modality comes from BANC receptor labels: 211 sugar (Gr5a/Gr64f), 82 sugar/low-salt, 9 bitter and 398 pheromone (ppk23/25, Ir52).
- On a sucrose patch, the leg sugar neurons fire at 30 Hz, their ascending targets at 42 Hz, and those neurons' brain targets at 7 Hz. **MN9 stays at 0**, so there is still no proboscis extension from the legs.
- Anatomically, leg sugar neurons put 8,865 of their nerve-cord synapses onto FlyWire-matched ascending neurons. Those are mostly **GABAergic** in both datasets, and so are their main brain targets (DNg103, VESa1_P02). The route to the feeding circuit appears to be **disinhibitory**.
- The Shiu et al. model has no spontaneous activity, so silencing an already-silent inhibitory neuron has no effect.

**What was needed next, all central-brain physiology rather than wiring:**
- spontaneous / resting activity (added 2026-10-03);
- spike-frequency adaptation (added 2026-10-03);
- non-spiking neurons (added 2026-10-04).

The antennal-lobe/mushroom-body runaway (above) points to the same missing properties.

Leg motor neurons are annotated by muscle and joint action (for example `flex_femur_tibia_joint`), and so are leg proprioceptors. Connecting these to the body's joints was done in Phase 6 (2026-10-05) and on the MuJoCo body (2026-10-08/09).

Performance with everything on (brain + nerve cord + FlyVis + graded optic lobe + taste): about 25 fps, close to real time; 15–17 fps with the MuJoCo body (brain still at 1.00× real time).

## License

- **Code:** Apache License 2.0 ([LICENSE](LICENSE)).
- **Documentation and figures:** CC BY 4.0. **Data derived from FlyWire:** CC BY-NC 4.0 (non-commercial), as FlyWire's public release requires. **Eye-map-derived files:** GPL-3.0. Details: [LICENSE-DATA.md](LICENSE-DATA.md).
- **Third-party datasets, models and assets** keep their own licenses and must be cited: see [THIRD_PARTY.md](THIRD_PARTY.md).
- **All sources and publications, with links, and each provider's citation rules:** [REFERENCES.md](REFERENCES.md) ("How to cite").
- **Citation:** see [CITATION.cff](CITATION.cff).
