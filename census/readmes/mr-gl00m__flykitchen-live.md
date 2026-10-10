# FLY-KITCHEN

Put a real, mapped fruit-fly brain inside a physics sim and watch it react to the world.

There are two things in this repo, and they are not the same:

| | what drives the fly | is it the real fly brain? |
|---|---|---|
| **`fly_live.py`** | the FlyWire v783 connectome: 138,639 real neurons, 15 M real synapses | **yes** |
| **`train_fly.py`** | a small random LIF net evolved by a genetic algorithm | no |

If you are here for "does the mapped fly brain work when you embody it," that is `fly_live.py`.

## The mapped brain, embodied (`fly_live.py`)

The FlyWire connectome (in `fly_brain_local/`) is a wiring diagram of an entire adult
Drosophila brain, from Shiu et al., *A leaky integrate-and-fire computational model based on
the connectome of the entire adult Drosophila brain*. Their headline validated result: drive
the sugar-sensing gustatory neurons and the network routes that signal, through the
subesophageal zone, to **MN9, the proboscis motor neuron**. The fly "decides" to extend its
proboscis and feed. They checked it against live flies.

`fly_live.py` puts that brain in a closed sensorimotor loop with a MuJoCo body. Every control tick:

1. **sense** the sim measures how near the fly is to a sugar droplet
2. **drive** that nearness sets the Poisson firing rate of the real sugar-sensing neurons
3. **think** the connectome steps forward; the signal cascades sugar → SEZ → MN9
4. **act** MN9's firing rate triggers feeding; the body steers toward the droplet and eats

No genetic algorithm, no behavioral rules. When you watch the fly home in on sugar and feed,
you are watching a real fly brain react to a virtual world through the same circuit a real fly
uses.

### What is biology and what is a bridge

Kept honest, because it matters:

* **sugar neurons → ... → MN9** is the real mapped connectome, unaltered. This is the science.
* **droplet nearness → sugar-neuron firing rate** is a bridge: the sim's "how much sugar is here."
* **finding the droplet** (locomotion) is a bridge, not the connectome. The v783 map is
  brain-only (no ventral nerve cord), so leg and wing output is not in the data. The fly walks
  by tropotaxis: two virtual taste antennae, steer toward the stronger side. The connectome's
  job in the loop is the sensorimotor decision, sugar to proboscis, and that part is real.

## Setup

Uses [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

### Connectome data

The big connectivity file `Connectivity_783.parquet` (~97 MB) is **not in this repo**, because it
is over GitHub's file-size limit. `Completeness_783.csv` and `sez_neurons.pickle` are included; you
only need to fetch the one parquet. See
[`fly_brain_local/fly_brain/CONNECTIVITY_DATA.md`](fly_brain_local/fly_brain/CONNECTIVITY_DATA.md)
for where to get it, then drop it into `fly_brain_local/fly_brain/`.

Bake the connectome into a fast cache. Once per machine, takes a few seconds, writes ~130 MB
to `cache/` (gitignored):

```bash
uv run build_connectome.py
```

Sanity-check that the port is faithful. This stimulates the sugar neurons and confirms MN9
fires, reproducing the paper's result, and benchmarks the stepper:

```bash
uv run validate_connectome.py
# PASS: sugar drives MN9 (0.00 -> 94.41 Hz). The mapped pathway fires as in the paper.
# [speed] ~1.2x biological realtime at dt=1.0ms
```

## Run the live fly

```bash
uv run fly_live.py                # serves the viewer on ws://localhost:8766
uv run fly_live.py --headless     # no browser; prints the loop to the terminal
```

Then open **`fly-live.html`** in a browser (double-click, or drag into Chrome/Edge/Firefox) and
click **Run**. The panel shows the MN9 proboscis meter, the sugar drive into the connectome, how
many of the 138,639 neurons are active, and an event log of every feed. The fly wanders, catches
the scent, homes in, and MN9 fires as it eats.

Headless is the fastest way to confirm it works without a browser:

```
bio_t   mode  dist  drive    MN9 active energy  feeds
  3.0   home  0.32  115.9   65.4    325   0.94  0
  4.0   feed  0.17  138.2  100.6    351   1.00  0   <FEED
  ...
[done] 70s biological in 73s wall (0.96x realtime); 10 droplets eaten
```

The whole connectome runs at roughly real time on CPU (the near-silent baseline makes the
sparse synaptic step cheap; it only lights up when the fly senses food).

## The GA experiment (`train_fly.py`)

The original piece: a population of flies with *random* recurrent LIF brains learns to survive a
kitchen (eat the apple, huddle in the stove's warm zone, feed at the trash) by evolution over
synaptic weights alone. This is a nice emergence demo, but the brains are toys, not the mapped
connectome. Kept because it is fun and self-contained.

```bash
uv run train_fly.py               # serves the GA viewer on ws://localhost:8765
```

Open `fly-kitchen-live.html`, click Run. Details of the GA, the kitchen, and the controls are the
same as before; see the code. Champion brains export to `tests/*.json`, cross-compatible with the
standalone JS sim in `archive/fly-kitchen.html`.

## Files

```
fly_live.py            ← embody the real connectome (run this)
fly-live.html          ← viewer for fly_live.py  (ws://localhost:8766)
connectome_brain.py    ← the mapped brain as a live LIF stepper
build_connectome.py    ← one-time: bake FlyWire v783 into cache/
validate_connectome.py ← proves the port reproduces sugar → MN9

train_fly.py           ← the older GA experiment (random brains)
fly-kitchen-live.html  ← viewer for train_fly.py (ws://localhost:8765)

fly_brain_local/       ← the FlyWire v783 connectome data + the paper's Brian2 model
archive/               ← earlier standalone browser iterations
```

## Extending

* **A different behavior**: the sugar → MN9 pathway is just the validated one. Any neuron set with
  a known FlyWire ID can be a sensory input (`ConnectomeBrain.set_drive`) or a motor readout
  (`ConnectomeBrain.rate_of`). `cache/meta_783.json` already resolves 100+ named SEZ groups.
* **Full biophysics**: `connectome_brain.py` reproduces the paper's LIF dynamics in NumPy/scipy so
  it can step inside a live loop. For offline batch experiments the paper's Brian2 model is in
  `fly_brain_local/fly_brain/model.py`.

## License

MIT. See [LICENSE](LICENSE).
