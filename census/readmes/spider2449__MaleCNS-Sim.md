# MaleCNS-Sim

MaleCNS-Sim is a reusable, reproducible, stateful connectome-simulation runtime.
Applications can prepare a resolved projection once, advance independent states
incrementally, inject explicit stimuli, consume detached results, and embed the
runtime in engineered closed-loop systems. Start with the
[runtime guide and synthetic examples](docs/runtime/USER_GUIDE.md).

It provides deterministic CPU reference and optional CUDA float64
Leaky Integrate-and-Fire engines, a resumable CPU runtime and a local experiment
workbench. The fixed synthetic Arena uses engineered sensory/motor coupling;
biological coupling is not validated. It is not a complete brain simulation,
an executable-brain claim, a biological fly behavior simulator, or a FlyGym,
NeuroMechFly, MuJoCo or learning-system integration.

## Current stage

MaleCNS-Sim **v0.3.0 is RELEASED**. The annotated `v0.3.0` tag peels to
`a1a6651163840a982799b1fa82c1904e67f84660`; current `master` also contains
later application/runtime engineering and documentation commits. See the
[Task 021 closure](docs/plans/2026-09-30-task-021-v0.3-post-release-closure.md).

The stable CPU public runtime is implemented under A023-A. Start with the
[runtime guide and synthetic examples](docs/runtime/USER_GUIDE.md).
The **0.4.0 application/runtime candidate is not published**; package
metadata is 0.4.0. Candidate-specific Windows/GPU and artifact evidence is tracked
in the [A025 result](docs/plans/2026-10-08-application-a025-release-candidate-result.md). See the [candidate notes](docs/releases/0.4.0-preparation.md)
and [artifact release gate](docs/runtime/RELEASE_GATE.md). This engineering scope
does not reopen the historical scientific v0.4 roadmap.

The v0.3 scientific scope is complete under Task 018B Decision A. The
prospectively preregistered Task 018A asks an independent anatomical question:
the full curated graph gives MN9_L 6,012 incoming synapses and MN9_R 556.
The 5,456 gap decomposes into shared-partner difference +4,281, LEFT-only
+1,315, and signed RIGHT-only -140. Its primary classification is
`SHARED_PARTNER_DIFFERENCE_LARGEST`. The `min_synapses=5` sensitivity is
`LEFT_ONLY_INPUT_LARGEST` and does not replace the primary result. This is
connectomic accounting, not a functional or biological mechanism claim. The
full Task 017 preregistered matrix was completed and all variants were
technically valid; its `NOT_ROBUST` result is a successful negative robustness
result under the frozen Task 016 criteria. Task 017Q remains deferred. Task 011 remains the baseline
temporal mechanism audit. The validated state covers the curated MaleCNS v1.0
graph, explicit sign policies, reference LIF dynamics, the Shiu v630 reference
reproduction, Task 008 dynamics, Task 009 structural analysis, Task 010
frozen-candidate perturbations, and the completed v0.3 robustness study. See
the [authoritative research checkpoint](docs/MALECNS_RESEARCH_CHECKPOINT.md)
and [Task 018A execution report](docs/plans/2026-09-30-task-018a-mn9-anatomical-asymmetry-execution.md).
The byte-identical Task 018A execution artifact is tracked at
[`artifacts/task018/execution-result.json`](artifacts/task018/execution-result.json)
for inspection from a fresh clone; the original ignored local output remains
at `data/derived/task018-results.json`. Running `scripts/run_task018.py`
requires the manifest-matching raw data and performs scientific analysis; it
is not needed to inspect the tracked result.
Task 018B closes the current v0.3 scientific scope and recommends release
preparation; see the [Task 018B decision record](docs/plans/2026-09-30-task-018b-mn9-anatomical-asymmetry-closure.md).

The intended pipeline is:

```text
MaleCNS data
→ normalization
→ sparse directed graph
→ signed anatomical projection
→ reference LIF dynamics
→ validated reference dynamics
```

Task 005 adds the CPU reference dynamics layer. It uses the published Shiu
equations with an exact linear state update, explicit `dt=0.1 ms`, integer
1.8 ms delayed sparse events, explicit refractory handling, deterministic
spike schedules, and seeded reference-style Poisson input. It consumes only
resolved Task 004 signed edges and reports excluded unresolved edge counts and
weights. This is a numerical reference and bounded engineering substrate, not
a reproduction of the Shiu FlyWire network or a biological validation.

Task 002 validated MaleCNS v1.0 locally from the three official Feather
files. The measured full segment graph contains 88,404,403 node IDs and
151,856,684 edges; the `min_synapses=5` graph contains 7,622,864 edges.
Both CSR builds are deterministic, and source neurotransmitter predictions
are preserved as metadata without assigning biological sign. See the
[Task 002 validation record](docs/plans/task-002-malecns-v1-real-data-validation-and-provenance.md)
and the local provenance manifest at `data/provenance/male-cns-v1.0.json`.

Task 003 projected the raw segment graph onto the publication-defined curated
neuron identity set: 166,700 curated IDs, 25,582,938 full neuron-level edges,
and 6,242,118 edges at `min_synapses=5`. The full graph has 217 isolated
curated IDs; the thresholded graph has 864. The curated graph, not the raw
88-million-segment graph, is the intended future simulation substrate. See the
[Task 003 validation record](docs/plans/2026-09-20-task-003-curated-neuron-level-connectome-projection.md).

Task 004 adds explicit MaleCNS neurotransmitter resolution and named sign
policies without changing the unsigned anatomical graph. The curated set has
163,523 resolved neurotransmitter identities and 3,177 unresolved identities
under the consensus-first policy. The Shiu-compatible policy signs 97.7988% of
full curated anatomical weight and 97.9549% of `min_synapses=5` weight; the
conservative policy signs 79.8927% and 81.2499%, respectively. Signed counts
are derived data, not functional synaptic weights. See the
[Task 004 validation record](docs/plans/2026-09-20-task-004-neurotransmitter-sign-policy-and-signed-connectome.md).

Task 006 reproduces the Shiu et al. FlyWire v630 sugar-to-MN9 experiment as a
separate reference-data validation. Against the official stored
`sugarR_100Hz.parquet`, the local 30-trial run measured MN9 mean firing rates
of 67.0667 Hz versus 67.0333 Hz, with all trials active; the original signed
`Excitatory x Connectivity` column times 0.275 mV was used directly. The
frequency curve was measured at 10, 25, 50, 100, 150, and 200 Hz, and rose
from 0 Hz at 10/25 Hz to 93.1333 Hz at 200 Hz. This validates engine behavior
on the historical v630 graph only; it does not map FlyWire IDs to MaleCNS v1.0
IDs. See the [Task 006 validation record](docs/plans/2026-09-20-task-006-shiu-v630-sugar-mn9-reproduction.md)
and [its provenance manifest](data/provenance/shiu-2024-v630.json).

Task 007 establishes a provenance-pinned homolog mapping boundary without
running a MaleCNS experiment. Twenty historical sugar roots have later
FlyWire `LB3`/`sugar/water` type evidence and one remains unresolved; their
MaleCNS `flywireType=LB3` mapping contains 87 type-level candidates. The
evidence-backed right-side MaleCNS input population contains 43 gustatory
`MxLbN` bodies, with 42 Task 004-resolved NT records and one unresolved NT
record. FlyWire MN9 type `CB0701` maps to MaleCNS `type=MN9` bodies `10331`
and `16949` at `TYPE_LEVEL`; neither is silently selected. Structural checks
found no direct sugar-to-MN9 edge and shortest curated paths of two hops to
both candidates. This is an identity result, not a firing or behavioral
claim. See the [Task 007 mapping record](docs/plans/2026-09-20-task-007-malecns-sugar-mn9-homolog-mapping.md)
and [its compact evidence summaries](data/provenance/task007-mapping-summary.json).

The complete release gate, including scientific nonclaims, fingerprints,
environment, and reproduction commands, is in the
[MaleCNS release gate](docs/MALECNS_RELEASE_GATE.md). The authoritative
scientific state is in the
[research checkpoint](docs/MALECNS_RESEARCH_CHECKPOINT.md).

## Application workbench

The local connectome simulation workbench provides experiment validation,
execution status, schematic subgraphs, recorded playback, controlled model-output
comparison and explicit R0–V7 robustness evidence without a default aggregate
verdict. Start with `uv run malecns-workbench` after installation and open the
newly printed local session URL. Real experiments require registered local data.
See the [application user guide](docs/application/USER_GUIDE.md),
[architecture](docs/application/ARCHITECTURE.md), and
[application reproducibility record](docs/application/REPRODUCIBILITY.md).

## Installation

Python 3.12 or newer and `uv` are required. For local CPU setup:

```powershell
uv sync --frozen --group dev
```

GPU support is optional; see the [reproducibility and recovery guide](docs/REPRODUCIBILITY.md)
for its setup and preflight boundary.

## Tests

For application/runtime zero-payload release certification, use the separately
authorized [candidate gate](docs/runtime/RELEASE_GATE.md). The generic commands
below are ordinary local development checks: they can read tracked scientific
evidence and do not establish zero protected-payload access. A023's split
integrity acceptance does not turn protected I1 into PASS.

Validation is local. After setup, run the data-free tests, package build, and
tracked-integrity check:

```powershell
uv run pytest
uv run python -m compileall src scripts tests
uv build
uv run python scripts/check_tracked_integrity.py
git diff --check
```

On a clean CPU clone,
the raw-data and CUDA tests skip through their existing environment checks.
The full-graph test remains opt-in with `MALECNS_TASK007C_REAL=1` and is not
enabled by these commands. These checks cover locked CPU installation, data-free
tests, compilation, build, and offline tracked integrity. They do not
certify raw-data integration, GPU/CUDA/CuPy execution, CPU/GPU parity, external
Task 017 checkpoint restore, Task 017Q cross-machine certification, scientific
endpoint reproduction, or Windows behavior.

## Reproducing the validated analyses

Place the exact raw files named by
[`data/provenance/male-cns-v1.0.json`](data/provenance/male-cns-v1.0.json)
under `data/raw/male-cns/v1.0`, then verify them:

```powershell
uv run malecns-sim data verify `
  --manifest data/provenance/male-cns-v1.0.json `
  --root data/raw/male-cns/v1.0
```

The validated Task 008 run prepares and caches the full curated graph and the
separate `min_synapses=5` sensitivity graph:

```powershell
uv run python scripts/run_task008.py
```

This script requests CUDA and writes ignored cache/result files under
`data/derived/`. Task 009, 010, and 011 are then run in order:

```powershell
uv run python scripts/run_task009.py
uv run python scripts/run_task010.py
uv run python scripts/run_task011.py
```

Task 010 and Task 011 load and validate the full Task 008 cache. Task 006 has
no standalone runner in this repository; its pinned Shiu v630 inputs, API
entry points, and nonclaims are documented in the
[release gate](docs/MALECNS_RELEASE_GATE.md) and the
[Task 006 plan](docs/plans/2026-09-20-task-006-shiu-v630-sugar-mn9-reproduction.md).
The repository does not claim a one-command reproduction for Task 006.

## Local data inspection and benchmarking

Task 001 uses an explicit CSV/TSV adapter boundary because the exact public
MaleCNS v1.0 schema has not been verified in this repository. The default
column names are canonical internal names, not invented claims about the
external dataset. Map a verified source schema with CLI options such as
`--neuron-id-column` and `--synapse-column`.

```powershell
malecns-sim inspect --neurons neurons.csv --edges edges.csv --min-synapses 5
malecns-sim benchmark --neurons neurons.csv --edges edges.csv --min-synapses 5
```

The benchmark reports measured graph construction and propagation times.
Sparse storage values are measured sizes of CSR arrays and are estimates of
the complete in-memory object because Python and allocator overhead are not
included. No real-data benchmark is claimed until a documented MaleCNS data
release is successfully loaded and inspected.

## Scientific limitations

Neuron and edge metadata are preserved where supplied, including
neurotransmitter predictions and classifications. Model signs are explicit
policy assumptions and edge weights remain anatomical synapse counts; signed
counts are not functional synaptic weights. The LIF model is a deterministic
reference model, not a complete biological neuron model, and the simulation
does not provide biological causality, behavioral validation, receptor-level
physiology, or an embodied fly environment.

Raw source data and normalized records are separate concepts. Raw or derived
connectome files should remain outside Git.

See [the Task 001 plan](docs/plans/task-001-malecns-data-ingestion-and-executable-graph.md)
and [the adapter boundary](docs/data-adapter.md) for assumptions and known
unknowns.
