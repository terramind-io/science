# FlyBrain

**Command-driven simulation of a Drosophila brain connectome.**

By **[Batuhan Ayrıbaş](https://batuhanayribas.com)** · Rootcastle Engineering & Innovation

[Get started](#quick-start) · [Commands](docs/COMMANDS.md) · [Architecture](docs/ARCHITECTURE.md) · [Validation](docs/VALIDATION.md) · [Research provenance](#research-provenance)

FlyBrain turns a published computational fruit-fly brain model into a persistent, interactive command console. Type `sugar`, `water`, `bitter`, or `antenna`; the program stimulates the corresponding source-defined neurons, advances the actual Brian2 network, and reports the spikes and circuit readouts it calculates.

The application uses **all 127,400 neurons and 14,687,178 directed connection records** in the upstream FlyWire v630 dataset. Those weighted records represent **52,793,639 anatomical synapses**. It does not replace the connectome with a demonstration network. The small synthetic graphs in `tests/` are exclusively test fixtures.

This is a numerical neural-circuit simulation. Commands are translated into experimental stimuli by software; the model does not understand language, acquire consciousness, learn commands, or simulate a complete moving fly. Its measured outputs are neuron firing counts and rates.

## Quick start

Use **Python 3.11–3.13**. The locally validated runtime is Python 3.12 on Linux. Windows and macOS launchers are included; their native execution is not claimed as locally tested.

```bash
git clone https://github.com/rootcastleco/fly-brain.git
cd fly-brain
python launch.py
```

On systems where Python is named `python3`, use `python3 launch.py`. On Windows, you can also double-click **`BASLAT.bat`**. On macOS/Linux, run **`bash baslat.command`**.

The launcher creates an isolated `.venv`, installs pinned runtime dependencies, downloads approximately **86 MiB** of source data from a fixed upstream commit, verifies each file's SHA-256 digest, and prepares a local compressed graph of approximately **48 MiB**. Subsequent runs use the local data and work offline. No API key, hosted model, GPU, or account is needed to run the simulation.

The default NumPy backend requires no C/C++ compiler. Allow several seconds to load the whole network and several more seconds per stimulus; simulated milliseconds are different from wall-clock time. Use an 8 GB or larger machine as a practical starting point; this is a planning recommendation, not a measured minimum.

### Your first experiment

At the `flybrain>` prompt, enter:

```text
reset 42
sugar 150 200
wait 500
water 200 200
save
exit
```

The two numeric arguments are **input frequency in Hz** and **simulation duration in ms**. Omitting them uses 150 Hz and 500 ms. Turkish commands also work: `şeker`, `su`, `acı`, `anten`, `bekle`, `sıfırla`, and `çıkış`.

Example output measured with a fresh seed of 42:

```text
Response: The MN9 circuit readout associated with proboscis extension is active.
  307 active neurons; 2,431 spikes; 1,842 spikes outside directly stimulated neurons.
  MN9_a: 75.0 Hz  |  MN9_b: 45.0 Hz  |  DN1: 0.0 Hz  |  DN2: 0.0 Hz
```

This example corresponds to `reset 42` followed immediately by `sugar 150 200`. Earlier commands consume random numbers and can change a later response even when no external stimulus was applied. Reset before comparing independent conditions.

### Run in a notebook

[Open the interactive quickstart in Google Colab](https://colab.research.google.com/github/rootcastleco/fly-brain/blob/main/notebooks/Quickstart.ipynb), or open the same notebook in Jupyter. It installs the dependencies, prepares the full graph, creates one persistent brain, and lets you run individual commands or an interactive prompt. Hosted runtime speed and available memory vary.

## What you can control

| Command | Experiment |
| --- | --- |
| `sugar 150 200` | Stimulate the 21 right-side sugar sensory neurons |
| `sugar_left 150 200` | Stimulate the 10 left-side sugar sensory neurons |
| `water 200 200` | Stimulate 18 water sensory neurons |
| `bitter 200 200` | Stimulate 21 bitter sensory neurons |
| `antenna 150 200` | Stimulate 146 source-listed Johnston's organ neurons |
| `mix sugar=100 bitter=200 duration=500` | Apply two sensory inputs simultaneously |
| `stimulate 720575940624963786 150 200` | Address an exact FlyWire neuron ID |
| `silence sugar` | Disable outgoing transmission from the sugar group |
| `reconnect sugar` | Restore the group's outgoing transmission |
| `wait 500` | Observe the network without new external input |
| `reset 42` | Restore neural state, pending events, model time, and seed |
| `status`, `groups`, `help`, `save` | Inspect the session or export measurements |

Rates are limited to **0–260 Hz**, and one command advances **10–1,000 ms**, in multiples of the 0.1 ms timestep. These are application limits, not claims about biological limits. At most eight non-overlapping input targets can be combined.

See [the command reference](docs/COMMANDS.md) for aliases, output semantics, exact IDs, and reproducible command sequences.

## Measured responses

The following are **single-trial software acceptance results**, using seed 42 and the complete v630 graph. Each sensory condition starts from reset. They are not confidence intervals, new biological validation, or a reproduction of every figure in the source paper.

| Condition | Input | Duration | Active neurons | Total spikes | MN9_a / MN9_b | DN1 / DN2 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| No stimulus | 0 Hz | 200 ms | 0 | 0 | 0 / 0 Hz | 0 / 0 Hz |
| Sugar | 150 Hz | 200 ms | 307 | 2,431 | 75 / 45 Hz | 0 / 0 Hz |
| Water | 200 Hz | 200 ms | 202 | 1,527 | 35 / 20 Hz | 0 / 0 Hz |
| Bitter | 200 Hz | 200 ms | 79 | 1,204 | 0 / 0 Hz | 0 / 0 Hz |
| Antenna | 150 Hz | 200 ms | 421 | 5,676 | 0 / 0 Hz | 10 / 15 Hz |
| Sugar | 100 Hz | 500 ms | 339 | 4,978 | 70 / 46 Hz | 0 / 0 Hz |
| Sugar + bitter | 100 + 200 Hz | 500 ms | 162 | 5,182 | 0 / 0 Hz | 0 / 0 Hz |
| Sugar outputs disconnected | 150 Hz | 200 ms | 21 | 589 | 0 / 0 Hz | 0 / 0 Hz |

The final condition is an important causal software check: directly stimulated sensory neurons still fire, but their activity no longer propagates into the rest of the network. `silence` blocks outgoing transmission; it does not clamp the neuron's internal voltage or erase pending activity elsewhere.

Raw measurements, dataset identity, backend versions, and timings are in [`validation/full_results.json`](validation/full_results.json). The acceptance script checks all 11 recorded conditions/invariants. Details and limits are in [the validation report](docs/VALIDATION.md).

## How the model works

The dynamics follow the upstream leaky integrate-and-fire model, implemented in Brian2:

$$\frac{dv}{dt}=\frac{v_0-v+g}{\tau_m},\qquad \frac{dg}{dt}=-\frac{g}{\tau_s}.$$

A neuron spikes when its membrane potential exceeds the threshold. The model resets its membrane potential and synaptic drive, applies the refractory period, and delivers weighted effects to connected neurons after the configured delay.

| Parameter | Value |
| --- | ---: |
| Resting / reset potential | −52 mV |
| Spiking threshold | −45 mV |
| Membrane time constant | 20 ms |
| Synaptic decay time constant | 5 ms |
| Refractory period | 2.2 ms |
| Synaptic transmission delay | 1.8 ms |
| Weight per signed anatomical synapse | 0.275 mV |
| External input scale | 250 × synaptic weight |
| Numerical timestep | 0.1 ms |

The input targets use the upstream zero-refractory convention, including targets explicitly configured at zero input rate. Other neurons retain the model's normal refractory period.

FlyBrain adds a persistent session, dynamic stimulus rates, strict command validation, source verification, output gating, and bounded reporting. It preserves all graph rows and the original neuron ordering. Its `PoissonGroup` implementation has the same independent, per-timestep Bernoulli input law as the source's `PoissonInput` with `N=1`, but consumes random numbers differently. **Equal seeds across the two implementations do not imply identical stochastic trajectories.**

The adapted membrane and synaptic dynamics have also been checked against the actual upstream `model.py` with identical deterministic spike input, including inhibitory transmission and disconnected output. The voltage/conductance traces agreed within the test's numerical tolerance, and spike indices and times matched exactly. See [architecture and equivalence details](docs/ARCHITECTURE.md).

## Automation and Python use

Run commands without entering the interactive console:

```bash
python launch.py --command "reset 42" --command "sugar 150 200" --json --export results/sugar.json
```

`--command` can be repeated. Commands execute in order on one persistent brain. `--json` writes one JSON object per command to standard output; setup progress may also appear on first launch, so use the prepared environment directly for a pure JSON pipeline:

```bash
python launch.py --setup-only
.venv/bin/python -m flybrain --command "sugar 150 200" --json
```

On Windows, the environment executable is `.venv\Scripts\python.exe`.

```python
from flybrain.data import load_connectome
from flybrain.engine import Brain
from flybrain.session import Session

brain = Brain(load_connectome(), seed=42)
session = Session(brain)
response = session.execute("sugar 150 200")
print(response["result"]["readouts"])
session.execute("wait 500")
session.export()  # New JSON file; existing files are never overwritten.
```

One `Brain` instance must be owned by one thread, and only one brain should run in a process because Brian2 preferences and random state are process-level resources. Use separate processes for independent experiments.

## Reproducibility and testing

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python -m tools.validate_full --output results/full-validation.json
```

Prepare the graph with `python launch.py --setup-only` first if it is not present. When using a virtual environment, run all commands with that environment's Python.

The ordinary suite includes parser rejection cases, exact 64-bit ID handling, data corruption rejection, transmission gating, state continuity, reset/replay, and export protection. Two additional differential tests require a pinned upstream checkout:

```bash
git clone https://github.com/philshiu/Drosophila_brain_model.git ../Drosophila_brain_model
git -C ../Drosophila_brain_model checkout 91bdd1e7dcf193f3e7ca5a8933497fcef63b7960
FLYBRAIN_UPSTREAM=../Drosophila_brain_model python -m pytest -q
```

The snapshot of local test evidence is documented in [VALIDATION.md](docs/VALIDATION.md). Tests against tiny synthetic graphs establish software behavior; the separate full-graph checks establish that the real dataset loads and responds.

## Data, resource use, and recovery

- Source downloads are pinned to a commit and checked against committed SHA-256 hashes. The runtime cache is generated locally and excluded from Git.
- The runtime uses non-pickle NumPy arrays and verifies the local cache before building the network. The entire graph remains in memory; this is not an embedded-device runtime.
- Spike counts are recorded for each command. Full spike timestamps are deliberately not retained by this interface. The session retains the last 100 events, and a normal result directory accepts at most 100 automatically named session exports.
- Commands do not execute Python, shell commands, or network requests. The simulator starts no HTTP service and sends no telemetry.
- `reset` restores the initial model snapshot, including delayed-event queues. It clears transmission blocks and resets the random generator. This is a session reset, not a durable checkpoint/resume feature.
- If setup is interrupted, rerun `python launch.py`. To rebuild a corrupt cache, use `python launch.py --rebuild-data --setup-only`.

See [SECURITY.md](SECURITY.md) for the trust boundary and [CONTRIBUTING.md](CONTRIBUTING.md) for extension and change-validation rules.

## Research provenance

This repository is an engineering adaptation of **[philshiu/Drosophila_brain_model](https://github.com/philshiu/Drosophila_brain_model)**, originally authored by **Philip Shiu and Nico Spiller**, and accompanying the research by Shiu and colleagues:

> Shiu et al. *A Drosophila computational brain model reveals sensorimotor processing*. Nature (2024). [DOI: 10.1038/s41586-024-07763-9](https://doi.org/10.1038/s41586-024-07763-9).

Pinned source revision: **`91bdd1e7dcf193f3e7ca5a8933497fcef63b7960`**. The source neuron lists are extracted from `figures.ipynb` using literal parsing, without executing notebook cells or loading pickle files. The original v630 identifiers are used consistently; v783 data is not mixed into this release.

Batuhan Ayrıbaş's contribution is the interactive application, reproducible setup, command adapter, validation, and documentation. The connectome reconstruction and scientific model remain credited to their original authors. Read [THIRD_PARTY_LICENSES.txt](THIRD_PARTY_LICENSES.txt) and [CITATION.cff](CITATION.cff).

## License and author

The application is distributed under the repository's [MIT license](LICENSE). Upstream copyright and license notices are retained separately.

**Batuhan Ayrıbaş** · [batuhanayribas.com](https://batuhanayribas.com) · [GitHub / rootcastleco](https://github.com/rootcastleco)
