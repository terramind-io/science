# Bottlenecks of the Fly Brain

Max-flow / min-cut analysis of the male *Drosophila* CNS connectome, validated with in-silico ablation in a spiking (LIF) simulation.

**Question:** which neurons are structural bottlenecks between a sensory modality and the descending neurons that drive movement, and does silencing them hurt the motor response more than silencing the same number of random or high-centrality neurons?

## Status

- [x] 0. Setup
- [x] 1. Ingestion
- [x] 2. Graph and EDA
- [x] 3. Source and sink sets
- [x] 4. Max-flow / min-cut
- [x] 5. Simulation and ablation
- [ ] 6. Visualization
- [ ] 7. Streamlit app
- [ ] 8. Write-up

## Setup

Requires Python 3.12.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env   # then paste your neuPrint token
```

Get the token from https://neuprint.janelia.org/account (log in with Google).

## Layout

```
data/raw/        cached neuPrint pulls (parquet), gitignored
data/processed/  cleaned graph, source/sink sets, results
src/             pipeline modules
app/             Streamlit app (reads data/processed only)
notebooks/       EDA only
reports/         figures and write-up
```

## Data

Connectome from neuPrint (Janelia FlyEM, Cambridge, Google Connectomics), dataset `male-cns:v1.0`
(last database edit 2026-03-28, segment property update 2026-06-08).

```powershell
python src/inspect_schema.py --dataset male-cns:v1.0   # read-only schema probe
python src/ingest.py --dataset male-cns:v1.0           # cached pull; --refresh to re-pull, --report for counts only
```

The full pull takes about 10 minutes. It writes `neurons.parquet` (11 MB) and `edges/` (163 MB) to `data/raw/male-cns_v1.0/`.

| | pulled | published |
|---|---|---|
| `:Neuron` nodes | 176,422 | |
| neurons with `superclass` | 166,700 | ~166,700 |
| neuron→neuron edges | 25,862,574 | |
| synapses (sum of `weight`) | 125,024,863 | ~125M |
| synapses (sum of `weightHP`) | 107,079,478 | |

Edges kept at each synapse threshold: ≥3: 10.6M (105.0M synapses), ≥5: 6.3M (90.3M), ≥10: 2.8M (67.5M).

## Graph

```powershell
python src/graph.py --dataset male-cns:v1.0   # builds data/processed/male-cns_v1.0/
python src/eda.py --dataset male-cns:v1.0     # writes eda.json there
```

174,386 neurons with at least one edge and 25,862,452 edges (122 self-loops dropped). `weightHR` equals `weight` on every edge, so it is not kept. The whole graph loads as a sparse matrix in about 1 s and takes 208 MB. At ≥5 synapses it takes 51 MB.

**Neurotransmitter sign** (`consensusNt`, by presynaptic neuron): acetylcholine = excitatory; GABA, glutamate and histamine = inhibitory; dopamine, serotonin, octopamine and unclear = no sign. That gives a known sign for 93.9% of neurons. 59% of synapses are cholinergic, and those form the excitatory subgraph. These are predictions, not measurements. Median prediction confidence is 0.96 for ACh, 0.86 for GABA and 0.81 for glutamate. `consensusNt` agrees with the per-neuron `predictedNt` for 88.4% of neurons. Glutamate is inhibitory at most central synapses but not all.

Caveat for the excitatory subgraph: all 6,093 photoreceptors (`ol_sensory`) are histaminergic, so an ACh-only graph has no edges leaving the visual sensory set.

## Source and sink sets

```powershell
python src/sets.py --dataset male-cns:v1.0   # writes sets.parquet and sets_report.json (with Neuroglancer spot-check links)
```

Sources come from the `class` / `subclass` / `superclass` annotations (definitions in `src/sets.py`). Sinks are the 1,314 neurons with `superclass == descending_neuron`; motor neurons (815) are kept as an alternative readout.

| modality | neurons | output synapses | share going directly to DNs | median hops to DNs |
|---|---|---|---|---|
| vision (photoreceptors) | 6,086 | 684,494 | 0.0% | 3 |
| olfaction (ORNs) | 2,639 | 1,364,154 | 0.04% | 2 |
| taste, head | 275 | 169,010 | 3.4% | 2 |
| taste, legs/wings | 1,153 | 540,333 | 2.1% | 2 |
| Johnston's organ | 512 | 231,113 | 15.9% | 2 |
| head mechanosensory (all) | 1,652 | 576,636 | 21.5% | 2 |
| touch, body | 2,558 | 1,395,875 | 1.6% | 2 |
| proprioception | 1,454 | 1,005,570 | 1.7% | 2 |
| hygrosensation | 66 | 55,757 | 1.0% | 2 |
| thermosensation | 25 | 50,522 | 0.9% | 2 |

From every modality, all 1,314 descending neurons can be reached.

## Max-flow / min-cut

```powershell
python -m pytest tests -q                    # solvers vs known cuts and vs networkx
python src/flow.py --dataset male-cns:v1.0   # ~25 min, mostly the 50 random ablations per pathway
python src/viz.py --dataset male-cns:v1.0    # reports/bottleneck_3d.html (interactive 3D; includes simulation results)
```

**Solvers.** OR-Tools, scipy (Dinic) and igraph give identical flow values. On the full graph OR-Tools and scipy take 1–5 s per cut and igraph about 5× longer. OR-Tools is the default.

**Finding 1: cutting to all descending neurons says nothing.** The minimum node cut between a modality and all 1,314 descending neurons is just its first relay layer:

| modality | node cut, full graph | share of the cut that is a direct partner of the sensory neurons |
|---|---|---|
| taste, head | 1,399 | 100% |
| olfaction | 1,142 | 99% |
| Johnston's organ | 2,200 | 100% |
| vision | 12,454 | 7% (the cut sits 2–4 hops deep, at the optic-lobe output) |

The CNS is shallow (median 2 hops from any sense to a descending neuron) and fans out immediately.

**Main analysis: single identified targets.** Node cut with unit capacity, on edges that carry ≥1% of the postsynaptic neuron's input. Direct source→target synapses are excluded.

| pathway | cut (full graph) | cut (≥1% input) | synapse flow left on the full graph after removing k cut neurons | same k, path betweenness | same k, random on-path (n=50) |
|---|---|---|---|---|---|
| photoreceptors → giant fiber (DNp01) | 1,267 (LPLC2 185, LC4 126) | 21 | 83% | 94% | 99.99% ± 0.04 |
| head taste → MN9 (proboscis) | 355 | 34 | 24% | 64% | 99.98% ± 0.16 |

PageRank and out-strength top-k remove nothing (100% left).

- **The full-graph cut for vision → giant fiber is dominated by LPLC2 and LC4.** These are the visual projection neurons known experimentally to drive looming escape through the giant fiber.
- **Robustness.** Synapse thresholds barely matter: at ≥1% input, the cut at ≥3, ≥5 and ≥10 synapses has Jaccard 1.0 (taste at ≥10: 0.94). The input-share threshold matters more. Against the ≥1% cut, the ≥0.5% cut has Jaccard 0.34 (vision) and 0.57 (taste). At ≥2%, vision no longer reaches the giant fiber at all.

**Caveat.** A per-edge input-share filter breaks pathways built from many small inputs that converge. For example, an LPLC2 cell has a median of 553 presynaptic partners, only 3 of which provide ≥1% of its input. None of the 33,409 T4/T5→LPLC2 edges reaches 1%, although T4/T5 together provide at least a fifth of LPLC2's input. That is why LPLC2/LC4 appear in the full-graph cut but not in the ≥1% cut. A cell-type-level graph (summing edges per type pair) is the natural next step.


## Simulation and ablation

```powershell
python src/sim.py --dataset male-cns:v1.0 --screen   # which head taste types drive MN9 on their own (~6 min)
python src/sim.py --dataset male-cns:v1.0            # controls + ablations, 30 trials x 1 s each (~80 min on 4 cores)
```

**Model.** A leaky integrate-and-fire model of all 174,386 neurons, using the equations and parameters of Shiu et al. 2024 (`philshiu/Drosophila_brain_model`, `model.py`): v_0 = v_rst = −52 mV, v_th = −45 mV, τ_m = 20 ms, τ_syn = 5 ms, refractory 2.2 ms, delay 1.8 ms, 0.275 mV per synapse, Poisson drive at 150 Hz with weight ×250, and 30 trials of 1 s at dt = 0.1 ms.
- **Implementation.** Brian2 needs a C compiler on Windows, so the model is re-implemented with numba. The linear v/g system is integrated exactly.
- **Signs** come from `consensusNt`: ACh excitatory; GABA, glutamate and histamine inhibitory; everything else 0.
- **Silencing** removes a neuron's output synapses, as in the original.
- **Tests.** `tests/test_sim.py` checks the model on small networks: silence without input, the Poisson-driven rate, relay through a strong synapse, blocking by silencing, no relay through weak or inhibitory synapses, synaptic delay and seed reproducibility.

**Stimulus.** Driving all 275 head gustatory neurons leaves MN9 silent (0 Hz). The labels in the data do not say which types are sugar-sensing, so each type was stimulated on its own. 8 of 37 types drive MN9 to ≥10 Hz (`data/processed/.../sim/source_screen.csv`): dorsal_tpGRN, LB2a, PhG13, claw_tpGRN, LB3d, LB3c, PhG1c and PhG10. These 121 neurons are the stimulus. Their minimum cut to MN9 is the same 34 neurons as for all head taste neurons (Jaccard 1.0).

Only the taste pathway is simulated. Photoreceptors are histaminergic, and a sign-only model can express that only as inhibition.

**Result.** MN9 rate is the mean of the two MN9 cells over 30 trials. Every silencing condition silences k = 34 neurons.

| condition | MN9 rate | vs intact |
|---|---|---|
| no stimulus | 0.0 Hz | |
| intact (seed 1 / seed 2) | 107.7 ± 11.4 / 105.4 ± 10.7 Hz | 100% |
| **min cut silenced** | **0.38 ± 0.21 Hz** | **0.4%** |
| path betweenness top-34 silenced | 44.3 ± 1.9 Hz | 41% |
| PageRank top-34 silenced | 107.8 ± 4.0 Hz | 100% |
| out-strength top-34 silenced | 118.0 ± 5.0 Hz | 110% |
| random on-path, 20 sets | 107.3 ± 0.7 Hz (range 105.7–108.6) | 100% |

The minimum cut was found from graph structure alone. Silencing it almost abolishes MN9 firing, while the strongest structural baseline cuts it by about 60% and random sets do nothing.

Caveats:
- **The random baseline is weak** (34 cells out of ~164k on-path neurons), so the meaningful comparison is with path betweenness.
- **The stimulus types were chosen with the same model**, but the cut was not.
- **Out-strength silencing raises MN9 firing**, presumably by removing inhibitory hubs.
