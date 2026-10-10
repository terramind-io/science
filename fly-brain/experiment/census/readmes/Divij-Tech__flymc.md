# flymc — a fly connectome driving a Minecraft spider

The *Drosophila* whole-brain connectome (FlyWire, 139,255 neurons, 2.7M synaptic
connections) runs as a live leaky-integrate-and-fire spiking network on the GPU.
Its descending neurons steer a spider in Minecraft. Two processes, one loopback
socket.

```
Minecraft (Paper plugin)  --JSON/TCP-->  Python + PyTorch/CUDA
   world -> loom/left/right/food             139k-neuron LIF network
   forward/turn/jump/stop <- descending neurons
```

---

## What is real and what is invented

This matters more than anything else in this README.

**Measured data.** The wiring is real. Which neuron connects to which, and how
many synapses each connection has, come from the FlyWire electron-microscopy
reconstruction of an adult female fly brain (Codex snapshot 783). Nothing about
the graph structure is synthetic.

**Machine-learning predictions.** The neurotransmitter identity of each
presynaptic neuron is a prediction from a classifier, roughly 87% accurate. Our
excitatory/inhibitory sign comes entirely from that prediction, so about 1 in 8
edges probably has the wrong sign.

**Our modelling assumptions — the arbitrary part.**

| Choice | What we did | Why it is a guess |
|---|---|---|
| LIF dynamics | Shiu et al. 2024 parameters | Real neurons are not point LIF units |
| `W_SYN = 0.275 mV` | One flat weight for every synapse | Real synaptic strengths vary enormously |
| Sign mapping | ACH/DA/SER/OCT → +1, GABA/GLUT → −1 | A reasonable convention, not a measurement |
| Sensory transduction | Entity distance → Poisson rate on LC neurons | A fly's eye does not work like this |
| Motor mapping | DN firing rates → velocity and yaw | Pure invention (see below) |
| Latch watchdog | Reset the network when it sticks | Entirely ours, not biology |

**There is no ventral nerve cord.** FlyWire is the brain only. The leg motor
neurons and the central pattern generators that actually produce walking live in
the VNC, which is a separate dataset (MANC) that we do not use. So there is no
gait here and there cannot be one. What the descending neurons give us is
*intent* — startle, turn, freeze, escape — and we map that intent onto Minecraft
velocity by hand. Expect jittery and alien. That is the honest ceiling of this
design.

### The network does not settle

Worth knowing before you run it. Driven above roughly 50 Hz on any channel, this
network enters a **self-sustaining recurrent state that never decays**. Remove
the stimulus and ~7,800 neurons keep firing at a flat ~4.9 Hz indefinitely —
verified stable over 6+ seconds of simulated time, at every `dt` from 1.0 ms
down to the paper's 0.1 ms.

This is not a bug we failed to find. The network is genuinely silent from rest,
and the taste pathway reproduces correctly (below). It is a property of *this
model on the full connectome*: flat synaptic weights, no spike-frequency
adaptation, no neuromodulation, and a densely recurrent graph. There is nothing
in the model to switch a latched assembly back off.

Left alone the spider picks one behaviour and keeps it forever, which reads as
broken rather than alien. So the server has a **latch watchdog**: if every
sensory channel has been zero for 1500 ms and the brain is still above 0.05 Hz,
it resets the network. This is a reboot of the fly, it is our invention, it is
logged every time it fires, and you can turn it off:

```bash
flybrain serve --tune latch_watchdog_ms=0     # watch the raw behaviour
```

---

## Requirements

- NVIDIA GPU. Developed on an RTX 5070 (Blackwell, **sm_120**).
- **PyTorch cu128 or newer.** Older CUDA wheels have no sm_120 kernels and fail
  at *runtime*, not at install time. `torch` is deliberately not in
  `pyproject.toml` because it must come from the CUDA index:
  ```bash
  pip install torch --index-url https://download.pytorch.org/whl/cu128
  python -c "import torch; torch.zeros(1, device='cuda'); print(torch.cuda.get_device_capability())"
  ```
  That must print `(12, 0)` on a 5070 and must not raise.
- **Java 25** and a **Paper 26.1.x** server, for the plugin. Paper 26.1.2
  requires Java 25 as a minimum; the 1.21 line went out of support on
  2026-06-15. See "Choosing a Paper version" below if you need 1.21.11.

## Setup

```bash
cd flybrain
pip install -e .
python scripts/fetch_data.py      # ~60 MB, cached; skips files already present
pytest                            # 58 tests
```

---

## The data

`scripts/fetch_data.py` pulls the FlyWire Codex 783 snapshot from its public GCS
bucket. Five files, and the choice of files is not the obvious one:

| File | Why |
|---|---|
| `connections.csv.gz` | the edges: `pre_root_id, post_root_id, neuropil, syn_count, nt_type` |
| `classification_with_fw_and_hemibrain_types.csv.gz` | **not** plain `classification.csv.gz`, which lacks `cell_type` and `hemibrain_type` entirely |
| `consolidated_cell_types.csv.gz` | a third naming column; `LC4` is spelled differently here than in `cell_type` |
| `labels.csv.gz` | free-text community annotations — the **only** place `MN9` and the sugar GRNs are named |
| `names.csv.gz` | per-neuron names |

Two things the layout will catch you on:

- **`classification.csv.gz` has no cell types.** Its real header is
  `root_id,flow,super_class,class,sub_class,hemilineage,side,nerve`. Everything
  in milestone 4 needs the `_with_fw_and_hemibrain_types` variant instead.
- **`Gr64` and `MN9` do not appear in any structured type column.** The sugar
  GRNs are identifiable only from community label prose ("Putative Sugar
  Gustatory Receptor Neuron (GRN)"), and MN9 only as "Motor neuron 9; MN9".

Every CSV read goes through a schema check that lowercases headers and, on a
missing column, raises with the actual header list rather than guessing.

## The graph

```
neurons=139,255  edges=2,700,513  inhibitory=1,068,582 (39.6%)  nt_fallback=0  matrix=33.5 MB
```

Stored as `A[post, pre]` in CSR, so `A @ spikes` is every neuron's total
synaptic input in one sparse product. float32 values, int64 indices, handed to
`torch.sparse_csr_tensor` on CUDA. `root_id` is mapped to a dense index once;
no 18-digit id ever reaches the hot loop.

**Aggregate before thresholding.** Rows in `connections.csv.gz` are
per-neuropil, so one `(pre, post)` pair appears once per neuropil it passes
through. Codex applies its 5-synapse floor to the *pair total*: 1,159,840 raw
rows sit below 5 synapses, but no aggregated pair does. Filtering rows first —
the natural mistake — silently discards real synapses from connections that
should survive. Summing first makes the threshold a no-op on the stock file,
which is exactly the sign it is being applied correctly.

`nt_fallback=0`: every edge in this snapshot has a recognised neurotransmitter,
so nothing fell through to the excitatory default. The code still counts and
logs fallbacks, because a different snapshot may not be so tidy.

## The simulator

Leaky integrate-and-fire, parameters from Shiu et al. 2024 (Nature).

```
V_REST -52.0 mV   TAU_M   20.0 ms    V_THRESH -45.0 mV   T_REFRAC 2.2 ms
V_RESET -52.0 mV  TAU_SYN  5.0 ms    W_SYN    0.275 mV   T_DELAY  1.8 ms
```

`dt` defaults to 0.5 ms (`--dt` to change it; the paper uses 0.1 ms). The whole
step stays on-device: no `.item()`, no `.cpu()`, no host sync inside the loop.
Spikes propagate through a ring buffer `round(T_DELAY/dt)` steps deep.

One deviation from a literal reading of the spec, and it is deliberate:
**externally driven Poisson spikes are gated by the refractory mask.** Without
that gate a hard-driven neuron fires on every single step and reports rates of
1730 Hz, far past the 1/`T_REFRAC` ceiling of ~455 Hz. A refractory neuron
cannot spike, whatever is driving it.

### Verification: sugar makes the fly stick its tongue out

The headline result from the paper, reproduced here and covered by
`tests/test_lif.py`:

```
$ flybrain sim --stim food --hz 100 --ms 1000
baseline 200 ms with no drive: whole-brain mean 0.0000 Hz, max 0.000 Hz
stimulating food (n=23) at 100 Hz
   t=1000ms  MN9 = 190 Hz   brain mean 0.37 Hz   856 of 139,255 neurons active
```

Stimulating the 23 sugar gustatory receptor neurons drives **MN9**, the
proboscis extension motor neuron, from complete silence to ~190 Hz. That is the
in-silico version of a fly extending its proboscis at sugar, and it was
confirmed in live flies.

Two controls make that result mean something:

| Stimulus (100 Hz, 1 s) | MN9 | brain mean | active |
|---|---|---|---|
| 23 sugar GRNs | **190 Hz** | 0.37 Hz | 856 |
| 23 random sensory neurons | 0.0–5.8 Hz | 4.6 Hz | ~7,000 |
| 439 loom detectors | **0.00 Hz** | 1.2 Hz | 2,865 |

Random sensory drive produces an order of magnitude *more* total activity yet
leaves MN9 silent; loom drive leaves it at exactly zero. The response is
pathway-specific, not an artifact of exciting the brain. It holds across every
`dt` from 1.0 down to 0.1 ms.

The second invariant, also tested: **with zero drive the network is silent.**
Not near-silent — exactly 0.000 Hz. This model has no spontaneous activity, so
any baseline firing would mean a sign error or runaway excitation.

## Named populations

Selected by regex over the naming columns, unioned. `flybrain groups`:

```
  loom     n=  439   LPLC2, LC4, LC6            looming-object detectors
  left     n=  296   LC11, LC17, LC18 (left)    lateral motion
  right    n=  295   LC11, LC17, LC18 (right)   lateral motion
  food     n=   23   sugar GRNs                 label-matched; Gr64 absent from 783
  turn_l   n=    1   DNa02 (left)               steering
  turn_r   n=    1   DNa02 (right)              steering
  back     n=    4   MDN                        moonwalker, reverse
  stop     n=    4   DNp09                      freeze
  escape   n=    2   DNp01                      giant fiber, jump
  mn9      n=    2   MN9                        proboscis extension (verification)
```

A group resolving to zero neurons is a loud warning, because the mapping that
uses it would otherwise silently do nothing.

**Which columns get searched is per-selector, and that is load-bearing.**
Cell-type channels search only the structured type columns. The free-text
`label` column is opt-in, used only for `food` and `mn9` and always with a hard
`super_class` filter. The reason: curators routinely name a neuron's synaptic
*partners* in its label, so a bare `/DNp09/` across `label` matches 32 neurons —
most of them LCe04 visual neurons annotated
`LC122_L56-CL333.DNp09.AVLP538`. Restricted to type columns it matches the
correct 4. There is a regression test for this.

Explore before wiring anything up:

```bash
flybrain groups --search 'DNp0[19]'
flybrain groups --search 'sugar'
```

## Protocol

Newline-delimited JSON on `127.0.0.1:5005`.

```
->  {"loom":0.8,"left":0.2,"right":0.0,"food":0.0,"ms":50}
<-  {"forward":0.6,"turn":-0.3,"jump":false,"stop":false,"lag_ms":4.2}
```

Sensory values are 0..1, scaled to a maximum drive of 200 Hz. Motor outputs are
−1..1. `lag_ms` is the wall-clock cost of simulating the requested window, so
headroom is visible from the client.

Every gain and threshold is in the `Embodiment` dataclass at the top of
`server.py`, overridable without editing code:

```bash
flybrain serve --tune turn_gain=2.0 escape_ref_hz=80
```

Brain state lives on the service, not the connection, so a client can drop and
reconnect and the same fly is still there. Covered by a test.

### Calibration, and two channels that do nothing

Measured descending rates under 200 Hz single-channel drive, from a fresh brain:

| stimulus | turn_l | turn_r | back (MDN) | stop (DNp09) | escape (DNp01) | MN9 |
|---|---|---|---|---|---|---|
| none | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| food | 4.17 | 7.55 | 0.00 | 0.00 | 0.00 | **256.62** |
| loom | 109.57 | 1.31 | 0.48 | 0.02 | **88.52** | 0.00 |
| left | 238.37 | 178.10 | 0.12 | 0.04 | 0.23 | 0.00 |
| right | 261.39 | 4.22 | 0.16 | 0.06 | **143.72** | 0.00 |

The reference rates in `Embodiment` come from this table. Two honest findings:

- **MDN (`back`) and DNp09 (`stop`) stay at ~0 Hz for every sensory channel we
  have.** In the real fly they are driven largely by mechanosensory and bristle
  input; our visual and gustatory channels never reach them. Since `forward` is
  derived from exactly those two, it sits near `base_forward` in practice. The
  spider steers and startles convincingly; it rarely stops or reverses.
- **Lateral input is not cleanly lateralised.** Driving `left` raises *both*
  DNa02s (238 vs 178). `turn_l`/`turn_r` are a single neuron each, so their
  rates are noisy and near-binary. Turning works, but it is not a clean
  contralateral steering law.

## Minecraft plugin

```bash
cd plugin && ./gradlew build     # -> build/libs/flyspider-0.1.0.jar
```

Drop the jar in `plugins/`. Commands: `/flyspider` spawns the spider at you
(AI off, persistent, named "Drosophila"), `/flyspider status` shows the link
state and last motor command, `/flyspider stop` despawns and disconnects.

**The main server thread never touches the socket.** A dedicated I/O thread
owns the connection and does the blocking send/receive. The 1-tick task only
publishes a sensory snapshot into an `AtomicReference` and reads whatever motor
command is in another one. A motor command older than 1000 ms is treated as
stale and the spider simply stops moving. A stalled or dead brain degrades to a
motionless spider; it can never freeze the server. The I/O thread reconnects on
its own once a second.

Sensory derivation is main-thread only (entity and block lookups are not
thread-safe): looming from nearby living entities weighted by closeness and by
how directly ahead they are, plus a solid block within 3 blocks ahead;
left/right from the sign of the cross product between the facing vector and the
direction to each entity. Yaw is tracked by the plugin and applied with
`setRotation`, since vanilla AI is off. `forward` becomes horizontal velocity
with the existing Y preserved, and Y is set only on a jump.

Verified: compiles clean against `paper-api:1.21.4-R0.1-SNAPSHOT` with no
warnings, and loads and enables in a real Paper 1.21.4 server. The in-game
behaviour itself was not verified — that needs a human with a game client.

## Performance

`flybrain bench` reports steps/sec and simulated-ms per wall-ms across `dt`.

Per 50 ms window (one Minecraft tick) at `dt=0.5`, RTX 5070:

| | wall time | sim/wall |
|---|---|---|
| eager | ~20 ms | 2.4x |
| **CUDA graph** | **~12 ms** | **4.2x** |

Steps/sec was flat at ~4,800 across every `dt` before optimisation, which is the
signature of being **kernel-launch bound, not arithmetic bound** — the step is
~20 tiny kernels over 139k elements. So the fix was CUDA graphs: one full ring
cycle (`delay_steps` steps) captured as a single graph, replayed with one
launch, for a consistent 1.6x. All state is preallocated and written in place,
so changing the sensory drive between replays needs no re-capture.

Live loop test at the plugin's real cadence — 200 exchanges at 50 ms, sensory
input changing mid-run:

```
round-trip: mean 21.1  p95 24.7  max 28.7 ms
brain lag : mean 20.5  p95 24.2  max 28.3 ms
over the 50 ms budget: 0/200
```

Note these were measured while an unrelated `uvicorn image_api` process was
using ~40% of the same GPU. On an idle GPU the same window costs ~12 ms. Either
way it fits inside a tick, but the margin depends on what else you are running.

Remaining headroom if you need it: the spike vector is extremely sparse (~850 of
139k active), so a CSR product over all 2.7M non-zeros wastes nearly all of its
memory bandwidth. Gathering only the firing columns would be a large win, at the
cost of data-dependent shapes that CUDA graphs cannot capture.

## Headless replay

Debug the brain with no Minecraft attached. Runs the same `tick()` the socket
path uses, so what you see here is what the plugin gets:

```bash
flybrain replay --report-rates
```

Scripted stimuli — rest, sugar, loom, lateral motion, combinations, and a long
final rest so you can watch the latch (and the watchdog) for yourself.

## Layout

```
flybrain/
  scripts/fetch_data.py   download + verify, with real-header errors
  flybrain/graph.py       CSVs -> signed sparse CSR
  flybrain/lif.py         the simulator, CUDA graph capture
  flybrain/groups.py      named populations, per-selector column scoping
  flybrain/server.py      protocol, Embodiment tunables, latch watchdog, replay
  flybrain/cli.py         sim | serve | bench | groups | replay
  tests/                  58 tests
plugin/
  build.gradle.kts        paper-api 26.1.2 (Java 25), shaded, Gson provided by server
  src/main/java/dev/flymc/flyspider/FlySpider.java
```

## Out of scope

No learning or plasticity, no neuromodulation, no VNC, no multi-fly, no web
dashboard.

## Credits

- FlyWire connectome: Dorkenwald et al., Schlegel et al. (2024), Codex snapshot 783.
- LIF model and the sugar→MN9 result: Shiu, Sterne et al., *Nature* (2024).
