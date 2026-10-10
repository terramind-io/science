# flypair

N connectome-simulated fruit flies (leaky integrate-and-fire on real connectomes) coupled
through a shared 2-D virtual world: each fly's motor output becomes the others' sensory input.
Config-driven: new interaction scenarios are YAML files, no code changes.

**Status: M1–M6 implemented** (tiny + MaleCNS + FlyWire loaders, batched LIF brain, group
registry, world/channels, six scenarios, three controls + coupling metric, rasters/rates/MP4,
optional LLM dub, Colab notebook). M7 (interactive steering) is deferred by design; only the
`InputSource` seam exists.

## What this is, honestly

- **Leaky integrate-and-fire on synapse counts only.** Neuron and synapse constants are Shiu et
  al. 2024's (`flypair/constants.py`, verified against `model.py` in their repo): v_rest −52 mV,
  threshold −45 mV, τ_m 20 ms, τ_syn 5 ms, refractory 2.2 ms, delay 1.8 ms, 0.275 mV per synapse,
  dt 0.1 ms, Poisson inputs at 68.75 mV straight onto v. The same constants are reused unchanged
  on MaleCNS, which they were never fit to.
- **No neuromodulation, no plasticity, no persistent internal state, no graded potentials.**
  Every neuron is the same point neuron. Sign comes from predicted neurotransmitter only.
- **World → sensory encoders and motor → movement decoders are hand-designed** and listed in
  full below. Their gains are guesses chosen so that things happen, not measurements.
- **Behaviours must be compared against the `shuffled` and `playback` controls** (and
  `open_loop`) before claiming the wiring explains anything. The coupling metric printout does
  exactly that comparison.
- Sensory groups are driven by Poisson spikes at a commanded rate; the Shiu input weight makes
  every input draw a spike, so "rate in" = "rate out" for those neurons.

## Layout

```
flypair/constants.py      Shiu constants + exact Brian2 'linear' update coefficients
flypair/connectome/       base (common format, cache), tiny, malecns, flywire, (controls.shuffle)
flypair/groups.py         registry: groups/<connectome>.yaml -> indices; loud failure on 0 matches
flypair/brain.py          batched LIF (torch, CSR spmm or event-driven gather, auto-benchmarked)
flypair/inputs.py         InputSource seam: BrainSource (default), RecordedSource (playback), ScriptedSource
flypair/world.py          arena, poses, emitters, MotorDecoder
flypair/channels.py       declarative source->target sensory channels
flypair/scenario.py       YAML validation + closed-loop runner (one Brain per connectome, batch = flies)
flypair/controls.py       shuffled connectome, run_controls;  metrics.py  xcorr + TE-lite
flypair/record.py plots.py video.py video3d.py dub.py sanity.py cli.py
viewer/index.html         three.js 3D viewer (procedural fly), also used headlessly by video3d.py
groups/{tiny,malecns,flywire}.yaml   scenarios/*.yaml   tests/   flypair_colab.ipynb   PLAN.md
```

## Connectomes

| name | data | sex / regions | neurons | notes |
|---|---|---|---|---|
| `malecns` | MaleCNS v1.0 flat-connectome feathers (Janelia FlyEM, CC-BY 4.0), URLs from fly.ai | male, brain + VNC | 166,700 | real wing/leg/proboscis motor neurons; sign = presynaptic `consensus_nt` (gaba/glutamate/histamine → −1, else +1, fly.ai convention; `unknown_nt="drop"` for the mlx convention) |
| `flywire` | `Connectivity_783.parquet` + `Completeness_783.csv` from the Shiu repo (pre-signed) + Schlegel et al. 2024 annotation TSV | female, **brain only** | 138,639 | no VNC → outputs read from descending neurons (DNa02, DNp01, MDN, DNp09/DNg100, DNp13, vpoDN) and MN9 (a brain motor neuron, cell_type CB0701). Side labels are mirrored w.r.t. Shiu's naming. |
| `tiny` | synthetic | any | 1,880 | fake annotations covering every group; for tests/CI only |

Common format: signed CSR float32 `W[post, pre]` = signed synapse counts; neuron table with
`id, type, class, side, nt` + extra annotation columns; cached to `cache/<name>/W.npz`,
`neurons.parquet`, `meta.json`. Builds stream the 1 GB MaleCNS edge table in batches.

**Never build or load a real connectome on the 8 GB laptop.** Local work = `tiny` only.

## Group registry (what resolved, what did not)

Checked against the real annotation tables on 2026-09-17 (full table in `PLAN.md`):

| group | malecns | flywire |
|---|---|---|
| sugar_grn | LB3b/LB3c (34; `_R` = 17) | LB3 side L (64, contains Shiu's 21) |
| bitter_grn | **unresolved** (no receptor/modality label) | **unresolved** |
| gr32a | **unresolved** (not annotated anywhere) | **unresolved** |
| ppk23 | `receptorType == putative_ppk23` (269, VNC leg GRNs) | **unresolved** (no VNC) |
| or67d (ORN_DA1) | 204 | 126 |
| jo_ab | 138 | 358 |
| lc10a / lplc2 | 275 / 185 | 234 / 210 |
| visual (L1/L2) | 3,555 | 3,288 |
| p1 | pC1 × male-specific (148) | pC1a-e (10, female) |
| mal / vab3 / asp / vpoen / aipg | 159 / 6 / 46 / 4 / 56 | 107 / **unresolved** / 57 / 4 / 23 |
| pip10 / wing_mn | 2 / 66 | **unresolved** (male-only / no VNC) |
| dnp01 / dna01 / dna02 / forward_dn (DNp09+DNg100) / mdn | 2/2/2/4/4 | 2/2/2/4/4 |
| mn9 | 2 | 2 (CB0701) |
| aggression_dn | **unresolved** | **unresolved** |
| vpodn / dnp13 | **unresolved** (male) / 2 | 2 (DNp37) / 2 |

Channels whose target group is unresolved on a fly's connectome are skipped with a warning
(`on_unresolved: fail` makes it an error). So on MaleCNS the male-pheromone → Gr32a channel is
skipped; the "brake removed" scenario silences **mAL** instead.

## Encoders (world → sensory), all of them

Default channels (`flypair/channels.py: DEFAULT_CHANNELS`); each yields a Poisson rate (Hz) for
the target group of every *other* fly, summed and clipped:

| channel | source quantity | target | Hz = gain × source × falloff(d) | gating |
|---|---|---|---|---|
| song_to_jo | song_intensity (0–1) | jo_ab L/R | 120 × s × exp(−d/15 mm) | 360°, L/R by bearing |
| body_to_lc10a | angular size of the other fly (deg) | lc10a L/R | 4 × deg | 180° FOV, L/R |
| looming_to_lplc2 | d(angular size)/dt, positive part (deg/s) | lplc2 L/R | 1.5 × deg/s | 240° FOV, L/R |
| male_pheromone_to_gr32a | pheromone_male (1 if male) | gr32a | 80 within 3 mm contact | skipped where unresolved |
| male_pheromone_to_or67d | pheromone_male | or67d L/R | 60 × exp(−d/5 mm) | 360°, L/R |
| female_pheromone_to_ppk23 | pheromone_female | ppk23 | 80 within 3 mm contact | |

Any channel can be added in YAML, including non-biological ones (`source: "rate:mn9"` →
`target: sugar_grn`), with `gain, falloff {none|exp|inverse_square|linear|contact}, fov_deg,
split_lr, delay_ms, clip_hz, from, to`.

## Decoders (motor → movement), all of them

`flypair/world.py: MotorDecoder` (rates = mean Hz per neuron per 20 ms world tick, EMA 60 ms):

- speed = 0.25 mm/s per Hz × rate(forward_dn = DNp09+DNg100), max 25 mm/s
- turn = 8 deg/s per Hz × (rate(dna02_L) − rate(dna02_R)), positive = left, max 500 deg/s
- if rate(mdn) > 20 Hz: speed = −0.2 × rate(mdn) (backward)
- if rate(dnp01) > 30 Hz (unsmoothed): jump 6 mm away from the nearest fly, flash, 300 ms refractory
- song_intensity = clip(rate(pip10) / 40 Hz, 0, 1); falls back to wing_mn if pIP10 is unresolved; 0 if neither
- pheromone emitters are fixed by `sex` (male: pheromone_male = 1; female: pheromone_female = 1)

Flies are clamped inside a circular arena (radius 20 mm by default).

## Scenarios (`scenarios/`)

1. `male_male_intact` — two MaleCNS males, default channels
2. `male_male_brake_removed` — same, `silence: [mal]` in both
3. `courtship_chain` — four brake-removed males in a ring
4. `male_female` — MaleCNS male + FlyWire female; vpoDN vs DNp13 recorded as accept/reject
5. `clone_mirror` — identical seeds, point-symmetric start; the run must mirror exactly (tested)
6. `custom_template` — every option, commented

Controls (`controls:` list or `--controls`): `open_loop` (channels off), `playback` (fly A
replayed from the live recording, no brain; B live), `shuffled` (degree-preserving rewiring of W
— each presynaptic neuron keeps its out-degree and signed counts, in-degrees preserved; idea
from drosophila-brain-mlx). `flypair.metrics.coupling_report` prints max cross-correlation and a
linear "transfer-entropy-lite" between the flies' P1 / song rates for live vs each control.

## Running

Local (tiny only):
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[test]"
pytest -q
flypair run male_male_intact --override-connectome tiny --duration-ms 800 --controls --video
```

Colab: open `flypair_colab.ipynb` (Runtime ▸ Change runtime type ▸ **T4 GPU**), set `REPO_URL`
in cell 1, run all. Cells: (1) clone + install, (2) optional Drive cache, (3) build MaleCNS /
FlyWire with RAM + timing, (4) group report, (5) sugar→MN9 sanity check + CPU/GPU benchmark
(picks the faster), (6) scenario, (7) controls + metric, (8) figures + MP4 inline + download,
(9) optional dub (needs `ANTHROPIC_API_KEY` in Colab secrets; output watermarked
"LLM dub — not fly output"; strictly post-hoc).

Outputs per run: `runs/<name>/run.parquet` (+ `run.json`) with per-tick poses, emitters,
`rate_<group>` and `drive_<group>` columns; `spikes.parquet` for raster groups; `meta.json` with
every constant, channel and decoder used; `rasters.png`, `rates.png`, `trajectories.png`, `arena.mp4`.

## Local web UI

```bash
pip install -e ".[web,video3d]"
flypair web            # -> http://localhost:8000
```
Dashboard: pick a scenario, connectome (`tiny` locally; `malecns`/`flywire` only if their
`cache/<name>/` folder was copied from Colab), duration and controls; watch progress; then the
3D viewer, rate/raster/trajectory figures, coupling metrics and the scenario YAML, per run.
Runs land in `runs/`. The app never builds a connectome.

## 3D viewer + video

`viewer/index.html` is a single-file three.js page with a procedural fruit fly (red compound
eyes, antennae, striped abdomen, six legs with a tripod gait scaled by speed, wings that extend
~75° on the side facing the nearest fly and vibrate with song intensity, halteres), a song ring,
an escape flash, per-fly rate bars, orbit / top / follow cameras, a timeline scrubber and an
in-browser ⏺ record button (WebM). Open it in any browser and drop `runs/<name>/run3d.json` on
it. `flypair.video3d.render3d(run, "arena3d.mp4", camera="follow:A")` renders the same page
headlessly (Playwright + Chromium → ffmpeg); notebook cell 8b does this on Colab. The 2D
matplotlib MP4 (`arena.mp4`) is still produced by cell 8. The fly model is hand-built (no
external asset; fly.ai's `wiz.fbx` is a monkey wizard, not a fly).

## Sanity check reference

Shiu et al.'s shipped results (`results/example/*.parquet`, 30 trials × 1 s, 21 right sugar GRNs):
MN9 = **67.0 Hz at 100 Hz drive**, 93.3 Hz at 150 Hz. Cell 5 reproduces this on `flywire`
using their exact IDs. On `malecns` (LB3b_R/LB3c_R → MN9) there is no published number; mlx
reports MN9_L ≈ 53 Hz, MN9_R ≈ 0.2 Hz at 100 Hz. Whatever you measure, it is printed, not asserted.

## Unverified / caveats

- Not yet executed on Colab from this machine (no real connectome may be loaded locally); the
  loaders' neuron-table + registry halves were verified against the real annotation files, and the
  edge-building code follows fly.ai/mlx line by line. First Colab run may surface issues: report the
  cell output.
- Expected speed (unmeasured): T4 ≈ 20–60 s wall per biological second for two 166k-neuron flies;
  Colab CPU several times slower. The notebook prints steps/s.
- Motor gains were tuned on `tiny` only; on real connectomes the descending neurons may be
  silent or saturated. Adjust `motor:` in the scenario YAML.
- One of Shiu's 21 sugar GRN IDs has no row in the Schlegel annotation TSV (20/21 resolve by type).
- Gr32a, bitter GRNs, aggression DNs, vAB3 (FlyWire), ppk23 (FlyWire), vpoDN (MaleCNS), pIP10 and
  wing MNs (FlyWire) are unresolved — see table above.

## Tests (`pytest`, tiny only)
LIF f-I, refractory ceiling, 18-tick delay, inhibitory sign, spmm==gather; batch-of-2 == two runs;
silence mask; gain override; registry loud failure; clone_mirror symmetry; gain 0 == open loop;
playback replays A exactly; shuffled preserves degrees; scripted brainless source; YAML schema errors.

## References
Shiu et al. 2024 Nature (philshiu/Drosophila_brain_model) · MaleCNS v1.0 (Janelia FlyEM) ·
Schlegel et al. 2024 (flyconnectome/flywire_annotations) · alextitonis/fly.ai ·
Kisame76/drosophila-brain-mlx · cobanov/awesome-fly.
