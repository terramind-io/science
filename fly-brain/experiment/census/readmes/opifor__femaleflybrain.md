# flybench

An open bench for whole-brain simulation of fruit fly connectomes, built to
put a male and a female brain in the same model and the same world.

The simulator is an independent reimplementation of the leaky
integrate-and-fire model of Shiu et al. (2024). It reproduces their
benchmarks on the female brain: the sugar to MN9 dose response, bitter and
Ir94e suppression, the JO-CE to aBN1 response, and the water to MN9 dose
response once the input matched the paper's doses (see
`records/shiu_benchmarks_v1_report.md` and `records/water_dose_v1_report.md`). The same bench loads
the MaleCNS male, the FlyWire FAFB female and the FlyWire BANC female from
their public releases. No connectome data are bundled.

Every experiment here is pre-registered before any simulation runs. The
pre-registration text is stored verbatim and hashed into the record, seeds
are fixed and shared across conditions, and results that did not hold are
reported the same way as results that did.

What has held so far, at Shiu's parameters: the male's song command chain
works (P1 drives pIP10, the song pathway), and the female's reproductive
state gates her answer (a mated state silences pC1 and vpoDN, the "no"
readout). What has not held: courtship song entering the female's ear does
not reach vpoDN, and scent or vision entering the male leaves the mapped P1
population almost silent, at any dose we tried. Scent does raise pIP10, the
male's song command neuron, and a pre-registered lesion test shows that route
bypasses P1 (see `records/male_route_v1_report.md`). So the
picture is not "nothing travels deep": some routes transmit, the ones the
physiology says should carry courtship signals do not, and the sensory front
ends (ear bands, eye geometry) are themselves uncalibrated. That is the open
question this bench exists to work on. Pre-registrations
are in `experiments/`, results in `records/`.

The rest of this file is the technical reference.

A small NumPy/SciPy simulator for signed connectome networks, with an optional
Torch backend. No connectome data are bundled. Parameters and equations follow
Shiu et al. (2024); see NOTICE and the source-line citations in sim/params.py.

The default `kernel="shiu"` integrates exactly between grid events:

```text
dv/dt = (v_rest - v + g) / tau_m
dg/dt = -g / tau_s
```

Voltage is in mV and time in ms. A spike adds signed synapse count times
0.275 mV to g after 1.8 ms. Both v and g freeze during the 2.2 ms refractory
period; incoming writes during that period are discarded. Spikes require
v > -45 mV and reset v to -52 mV and g to zero. The membrane and synaptic
time constants are 20 and 5 ms. dt is 0.1 ms by default, or 0.2 ms.

`kernel="jump"` is a comparison-only model: each spike adds its weight
directly to the postsynaptic voltage without filtering or delay. It is not
the Shiu synaptic model.

Each step integrates, applies drive, detects spikes, delivers network events,
then resets. Spike timestamps label the grid step; delayed g increments start
affecting voltage on the next integration. Jump increments occur immediately
in the delivery phase; threshold detection follows on the next step.

`Drive(..., mode="poisson")` uses the reference's N=1 grid Poisson input:
a Bernoulli draw with probability rate*dt/1000, a 250*w_syn voltage pulse,
and zero refractory period for driven neurons. `mode="bernoulli"` instead
sets eligible targets above threshold and preserves their refractory period.
Both allow at most one input per target per step and reject rates above grid
capacity. Inhibition can prevent delivery. Every result reports requested,
sampled, and delivered drive Hz per target; delivered means a sampled input
matched an actual spike. Total output rates also include network spikes.

```python
from scipy.sparse import csr_matrix
from flybench.sim import Simulator, Drive

network = Simulator(csr_matrix([[0, 100], [-10, 0]]),
                    drive=Drive((0,), 150), groups={"output": (1,)})
first = network.run(500, seed=7, spike_log=True)
second = network.run(500, state=first.state, spike_log=True)
print(second.group_rates_hz)
```

CSR rows are presynaptic neurons, columns are postsynaptic neurons, and values
are signed synapse counts. Results contain per-call counts and rates, group
counts and mean Hz per group neuron, overall mean Hz per neuron, and optional
(absolute time in ms, neuron index) spike tuples. State is mutated in place and
contains v, g, refractory eligibility steps, delay ring and cursor, absolute
step, and RNG. Resume with the same simulator; retain logs before continuation.

Install with `python -m pip install -e ".[test]"`, or `".[test,gpu]"` for Torch.
`flybench.sim.lif_gpu.Simulator` defaults to CUDA and also accepts `device="cpu"`.
It uses float64, the same host RNG, and ordered CSR updates for parity.
`run_batch(duration_ms, seeds=[7, 11])` returns independent seeded trials;
`states=[...]` resumes them. Trials are scheduled serially; this backend favors
reproducibility over throughput and synchronizes with the host each step.

Run `python -m pytest -q -p no:cacheprovider tests`.
CUDA checks skip when CUDA is unavailable. To verify failure propagation, set
`FLYBENCH_FAIL_PROBE=1` and run only `tests/test_lif.py::test_harness_failure_probe`;
the expected result is one failure and exit code 1. Unset it for acceptance.

## Graphs

Build signed CSR graphs from official local exports with `flybench.graph`.
Install the graph readers separately: `python -m pip install pandas pyarrow`.
NumPy and SciPy are already project dependencies. No data are downloaded by
the builders. All three datasets are CC-BY 4.0; credit their original authors.

Download the indicated release, preserving these local filenames:

| Dataset | Official download source | Required local files |
| --- | --- | --- |
| MaleCNS v1.0 | [Janelia release](https://male-cns.janelia.org/download/) | `connectome-weights.feather`, `body-annotations.feather`, `body-neurotransmitters.feather` |
| FlyWire FAFB v783 | [Codex downloads](https://codex.flywire.ai/api/download?dataset=fafb) | `neurons.csv.gz`, `classification.csv.gz`, `consolidated_cell_types.csv.gz`; Shiu: `Connectivity_783.parquet`, `Completeness_783.csv`; Codex alternative: `connections_princeton.csv.gz` |
| BANC v888 | [BANC Codex](https://codex.flywire.ai/banc), [static data archive](https://doi.org/10.7910/DVN/7WTH1N) | `banc_888_edgelist_simple_v3.feather`, `banc_888_meta.feather` |

Janelia's release filenames are
`connectome-weights-male-cns-v1.0-minconf-0.5.feather`,
`body-annotations-male-cns-v1.0-minconf-0.5.feather`, and
`body-neurotransmitters-male-cns-v1.0.feather`; rename local copies as above.
The release's `minconf-0.5` is an upstream synapse confidence setting, distinct
from this builder's `min_syn`. Codex annotations can change; preserve the
downloaded files and their hashes for reproducibility.

Shiu data are distributed with the [paper's model repository](https://github.com/philshiu/Drosophila_brain_model).
Place its two data files alongside Codex annotations or pass `--shiu-data /data/shiu`.

Point `--data` directly at the directory holding each dataset's files:

```sh
python -m flybench.graph.male --data /data/male --out build/graph_male.npz
python -m flybench.graph.female --data /data/female --out build/graph_female.npz
python -m flybench.graph.banc --data /data/banc --out build/graph_banc.npz
```

Omit `--data` to use `FLYBENCH_DATA`. Python APIs expose
`build(data_dir, out, min_syn=1, **options)`; pass `None` for `data_dir` to use the environment.
Use `--min-syn 2` or `3` to explicitly filter weak connections after aggregating
duplicate pairs. The default retains every positive-count pair within the
documented annotation population, including connections with zero signed weight.
MaleCNS's raw file also contains millions of unannotated segments: those are
outside this graph population, and their excluded edges/synapses are reported
in metadata. MaleCNS defaults to `--status Traced` (multiple values/repeated flags supported).
BANC selects proofread OR roughly_proofread, excluding NOT_A_NEURON/GLIA/TOO_SMALL/UNROOTED
statuses and glia superclass. FAFB defaults to `--source shiu`; `--source codex`
uses the upstream >=5-synapse export. There is no type, self-loop or sign filter.

```python
from flybench.graph import load, where
from scipy.sparse import csr_matrix

graph = load("build/graph_female.npz")
n = len(graph["body_id"])
weights = csr_matrix((graph["data"], graph["indices"], graph["indptr"]), shape=(n, n))
left_dn = where(graph, type_re=r"^DN", side="L")
```

Rows are presynaptic; `count` retains raw synapse counts and `data` is
`sign[src] * count`. The simulator applies `w_syn`. Default rule `shiu2024` version 1 assigns ACh and dopamine/serotonin/octopamine +1,
GABA/glutamate -1, other/unknown NT 0. `--sign-rule monoamine-zero` sets the
monoamines to zero. FAFB Shiu instead preserves parquet `Excitatory` signs under
`shiu2024-parquet` version 1, rejects conflicts, and records nodes without
outgoing sign evidence as 0. Its signs can differ from current Codex NT labels.
The [schema and measured results](docs/graph-schema.md) document population
differences, missing evidence, NT confidence, source hashes and measurements.
Run synthetic tests with `python -m pytest -q -p no:cacheprovider tests/test_graph.py`;
the three commands above are the separate real-data runs.

## Fast backend

`flybench.sim.fast.Simulator` preserves the reference's `Drive`, `State`, and
`Result` contract and NumPy seed stream. It delivers all spikes in a step with
one float64 SciPy CSR multiplication: `scaled_weights.T @ fired`. The target
CSR is built once, with signed synapse values scaled before reduction. Both
the delayed Shiu filter and immediate `kernel="jump"` are supported, including
refractory freezing, discarded arrivals, and all three drive statistics.
Aggregation changes floating-point addition order, particularly for jump
voltage updates; arbitrary networks near threshold are not guaranteed to
remain bitwise identical to the reference.

```python
from flybench.sim.fast import Simulator, Drive

sim = Simulator(weights, drive=Drive((0, 1), 100))
first = sim.run(50, seed=7, spike_log=True)
second = sim.run(50, state=first.state, spike_log=True)
```

`flybench.sim.fast_gpu.Simulator` uses Torch sparse CSR multiplication and
float32 by default (`dtype=torch.float64` is also supported). It accepts
`device="cuda"` or `device="cpu"`. A single `run` keeps the reference's shapes;
`run_batch` computes independent trials together as dense columns:

```python
from flybench.sim.fast_gpu import Simulator

sim = Simulator(weights, drive=Drive((0, 1), 100), device="cuda")
head = sim.run_batch(50, seeds=[7, 11, 19])
tail = sim.run_batch(50, state=head.state)
```

Batch voltage, conductance, refractory steps, and neuron result arrays have
shape `[n, B]`; the delay ring has shape `[delay_steps + 1, n, B]`. Total and
group statistics have shape `[B]`, and optional spikes are a list of B logs.
Each seed initializes an independent CPU Torch generator. Drive samples are
generated in bounded 256-step chunks and transferred together; streams are
unchanged by batch membership or continuation. No NumPy RNG drives this
backend. For paired CPU/CUDA experiments use `fast.Simulator(..., rng="torch")`;
the default NumPy stream and Torch stream intentionally differ. There is no
per-spike delivery loop or per-step host synchronization when logging is off.
Enabling spike logs transfers indices to the host each step.

Parity tests use a seeded 200-neuron graph with 5% connection probability,
signed counts, and 20 driven targets at 400 Hz. They cover both kernels and
drive modes, exact CPU/reference spike logs, paired Torch/CPU first-50-ms logs,
total spike counts within 1%, independent batch columns, continuation, delay,
inhibition, refractory freezing, and input validation. Run:

```text
python -m pytest -q -p no:cacheprovider tests/test_fast.py
python -m pytest -q -p no:cacheprovider tests/test_lif.py
```

The opt-in `FLYBENCH_FAIL_PROBE=1` test in either file must fail with exit 1.
On the measured system, fast tests reported 31 passed and 1 skipped; reference
tests reported 18 passed and 1 skipped. Skips are the opt-in failure probes,
not CUDA tests. The joint failure-probe run reported 2 failed with exit 1.
The four CPU/reference cases matched all 27,686 spike timestamps. All eight
paired CUDA/CPU cases matched first-50-ms spike logs and had 0% total-count
difference (55,560 spikes per backend across the eight 100-ms trials).

The synthetic benchmark is executable without writing output files:

```text
python -m flybench.sim.fast --backend cpu
python -m flybench.sim.fast --backend cuda
python -m flybench.sim.fast --backend cuda --batch 4
```

The default graph has 140,000 neurons and 350 random destination draws per
source. Duplicate destinations are coalesced and zero entries removed, leaving
48,939,021 edges. Graph seed is 20240916; absolute synapse counts are uniformly
1 through 100, with 20% negative draws. The first 1,000 neurons receive 100 Hz
grid Poisson input. Each trial simulates 1,000 ms at dt=0.1 ms from rest, with
seed 72 (consecutive seeds for a batch), Shiu filtering, and spike logging off.
This strongly recurrent synthetic graph produces substantially more than
40 Hz/neuron; it is a throughput workload, not a calibrated connectome model.
CPU and CUDA use their respective default RNG streams in this timing test.

Measurements on 2026-09-16: Windows, AMD Ryzen 9 7950X3D, NVIDIA RTX 4090,
Python 3.12, NumPy 2.4.2, SciPy 1.17.1, Torch 2.6.0+cu124. Setup and one warm-up
step are excluded from run time. Process peak working set includes graph setup
and runtime libraries; CUDA memory reports peak allocated tensor memory and
is separate from host memory. Times are measured wall times, not estimates.

| Backend | Trials | Run seconds | Seconds / trial-second | Host peak MiB | CUDA peak MiB | Mean Hz/neuron |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| CPU float64 | 1 | 532.850 | 532.850 | 1495.80 | n/a | 336.75 |
| CUDA float32 | 1 | 12.505 | 12.505 | 2460.75 | 391.74 | 336.72 |
| CUDA float32 | 4 | 26.857 | 6.714 | 2461.12 | 459.04 | 345.58 |

Seconds per trial-second divides wall time by simulated duration times B.
The four-trial row simulates one second in every column; rates range from
336.35 to 372.61 Hz/neuron. Setup took 2.130 s (CPU), 3.813 s (CUDA B=1), and
3.734 s (CUDA B=4). Peak CUDA reserved memory was 396 and 472 MiB respectively.

## Dictionary

Build source-labelled neuron groups with
`python -m flybench.dictionary.build --data build --out build`.
The three `dictionary_<dataset>.json` reports record selectors, measured counts,
body-ID examples, side/NT distributions, confidence and literature sources.
`flybench.dictionary.groups(dataset, graph=graph)` returns indices for the
simulator's `groups=` parameter; `drive_targets(dataset, name, graph=graph)`
returns a selected drive population and rejects absent groups. Without a loaded
graph, use `data_dir=`, `FLYBENCH_DATA`, or the default `build/` graph directory.
See [the measured dictionary and matching limitations](docs/dictionary.md),
including explicit absent groups and the conservative MaleCNS P1 proxy.
Run `python -m pytest -q -p no:cacheprovider tests/test_dictionary.py`.

## Experiments

Scope note on the ear (2026-09-16): the auditory front end in `flybench/ear.py`
is a windowed energy mapping with an engineering rate ceiling (`JO_MAX_HZ`),
not a calibrated transducer. That ceiling has no biological source, the band
assignment does not follow the JO subtype literature, and the AMMC-B1 relay is
known to be graded and largely electrical, which a spike-only chemical model
cannot represent. Every hearing result recorded so far (`female_no_v1` song
conditions, `female_hearing_v1`, `courtship_v1` hearing readouts) is therefore
a stress test of this front end, not a measurement of the female's hearing.
The records stand as run; their claims are narrowed to that. A replacement
front end will be pre-registered before any new hearing number is produced.

Scope note on the eye (2026-09-17): `flybench/eye.py` spreads sorted body IDs
across the field at zero elevation, so its "retina" is a rank order, not a
coordinate. `flybench/retinotopy.py` and `flybench/eye2.py` join the published
FAFB v783 column assignments (hex p,q per cell) to the graph and provide a
causal graded front end with a declared, uncalibrated angle convention; no
network drive exists yet and no visual physiology target is in the ledger.
See [docs/eye.md](docs/eye.md) and `records/eye_v2_e1_report.md`.

The [shiu_benchmarks_v1 controls](experiments/shiu_benchmarks_v1.md) reproduce feeding and grooming directions with explicit [results and drive audits](records/shiu_benchmarks_v1_report.md).

The [female_hearing_v1 hearing ladder](experiments/female_hearing_v1.md) separates dose calibration, frozen choices and held-out tests; see the [experiment guide](docs/experiments.md#female_hearing_v1).

Run the preregistered female-only experiment with
`python -m flybench.experiment.runner --quick`, then
`python -m flybench.experiment.runner` for ten paired seeds per condition.
The [protocol](experiments/female_no_v1.md) fixes song synthesis, auditory
transduction, reproductive-state input and predictions before simulation.
The [experiment guide](docs/experiments.md) describes records, validation,
and interpretation. Full JSON and its generated report are written to
`records/female_no_v1_experiment.json` and `records/female_no_v1_report.md`.
## World

The two-body world connects geometry-only scent, silhouette vision, and sound
to independent persistent brains using the fast GPU backend. Motor commands
update a planar arena; records keep sensory evidence, neural readouts, movement,
and contact separate. See [world assumptions and usage](docs/world.md).
Run python -m pytest -q -p no:cacheprovider tests/test_world.py for synthetic acceptance.
The [courtship_v1 protocol](experiments/courtship_v1.md) preregisters paired two-fly world trials with live and muted male song.
The [male_decides_v1 sensory dose ladder](experiments/male_decides_v1.md) freezes male smell, vision and P1 doses before [held-out tests](records/male_decides_v1_report.md).

## Ask your own question

Start with one input group, one intervention and one readout against baseline.
Choose `male` (MaleCNS), `female` (FAFB) or `banc` (BANC); build and load its
graph as above. The [dictionary](docs/dictionary.md) lists selectors and limits.
`flybench.dictionary.groups("female", graph=graph)` supplies readout indices;
`drive_targets("female", "ORN", graph=graph)` from the same module selects an
input. Absent groups are empty, not biological absences; drive_targets rejects
absent and read-only groups. Use indices from the same graph throughout.
For your own group, replace the case-sensitive `type_re` in this example:

```python
from flybench.graph import where
cells = where(graph, type_re=r"^ORN_DA1$", side="L")
```

`^` and `$` bound the type name; side and superclass filters combine with AND.
Pass selected indices through `Simulator(..., groups={"readout": cells})`.
For input, `Drive(targets, 100, mode="poisson")` requests 100 Hz per target;
compare requested, sampled and delivered drive with output firing rates.
For a lesion, `flybench.experiment.male_route.lesion_outgoing(graph, cells)`
returns a graph copy with those outgoing edge counts and weights zeroed;
incoming edges from other rows remain. Construct the simulator from that copy.
For graded input, `flybench.sim.release.GradedRelease(source_rows, flux)` is
passed as `release=`: flux is spike-equivalents/ms over absolute time steps.
It replaces those rows' spike output, not their integration; see the
[diagnostic hook contract](docs/release-hook.md), not an electrical-synapse model.
Keep model parameters, weight scale and calibration fixed across comparisons;
any gain or calibration change is a separate experimental choice.
For auditory questions, the ear is not calibrated (see the scope note above).
These results are neuronal readouts in an isolated brain simulation, not behaviour.

The repo practice is to write `experiments/<name>.md` first (a new protocol),
record its SHA256, then run. A useful plan fixes selectors, conditions, doses,
seeds, windows and the decision rule; [water](experiments/water_dose_v1.md) and
[direction](experiments/direction_probe_v1.md) are small examples. Execution is
implemented in Python, as in `flybench/experiment/protocol.py` and
`flybench/experiment/runner.py`; a Markdown file alone does not define a runner.

Read group means as Hz per cell. The [experiment guide](docs/experiments.md)
uses twenty 50 ms windows, each with ten 5 ms calls carrying state forward;
discard four warm-up windows. Start each condition from rest with paired seeds,
average measured windows per seed, then report paired differences as mean
plus/minus SE (sample SD of differences divided by sqrt(number of seeds)).
Ignition is the fraction of measured seed-windows above 30 network Hz/neuron.

For example, does water drive MN9? With the protocol's FAFB Shiu graph, CUDA
and matching benchmark graph/engine hashes, run quick then full:

```sh
python -m flybench.experiment.water_dose --quick
python -m flybench.experiment.water_dose
```

The [existing record](records/water_dose_v1_report.md) reads [200,1000) ms,
with full seeds 0-9. Water100 gives MN9_ref 0.000 +/- 0.000 Hz; water160 gives
13.250 +/- 2.060 Hz. The paired water160-minus-baseline difference is also
13.250 +/- 2.060 Hz, passing its registered mean > 2 SE rule. This supports
transfer at that dose in this model; silence at 100 Hz does not establish absence.
