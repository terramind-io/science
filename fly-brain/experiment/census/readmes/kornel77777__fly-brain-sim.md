# fly-brain-sim

Visualize and simulate the whole-brain connectome of adult *Drosophila melanogaster*
using the FlyWire FAFB v783 release. 

Basically: ~140,000 neurons and tens of millions of synapses, mapped in full, and
you get to fly around inside them in your browser.

So far this repository has the data
foundation (download scripts, a reproducible DuckDB build, validation tests) and
a 3D web viewer. 

Shout out to the FlyWire Consortium!!! (the Seung and Murthy labs at Princeton, the Jefferis lab at Cambridge, and the citizen scientists)

<p align="center">
  <img src="docs/fly-brain-pic.png" alt="The viewer: brain regions as translucent outlines with one example neuron per cell type, coloured by super class" width="820">
</p>

## Setup

Requires [uv](https://docs.astral.sh/uv/) (it installs Python 3.12 for you) and,
for the viewer, Node.js 20 or newer.

```bash
uv sync
npm --prefix web install
```

## Getting the data

Nothing under `data/` is tracked by git. There are two kinds of input.

### 1. Files from FlyWire Codex (download manually)

Codex downloads require a FlyWire account.

1. Sign in at <https://codex.flywire.ai> and open the download page
   (<https://codex.flywire.ai/api/download>).
2. Choose data version **783** and download these tables (all `.csv.gz`):
   - Neurons, Classification, Names, Consolidated Cell Types, Cell Stats
   - Connections (Princeton synapses), **twice**: once thresholded
     (neuron pairs with at least 5 synapses) and once without a threshold
   - Coordinates, Labels, Processed Labels, Visual Neuron Types,
     Column Assignment, Connectivity Tags
   - For the viewer: the skeletons, **LOD1 Healed** (~14 GB zip), and the
     Princeton synapse table (~2.7 GB). The synapse table is needed for the brain
     region shapes and synapse locations; without it the viewer shows neurons only.
3. Put them all in one folder, e.g. `~/Downloads/flywire`, and run:

```bash
uv run python scripts/import_codex.py ~/Downloads/flywire
```

The browser's file names don't matter. Each file is identified by its CSV
header (the skeleton zip by its `<root_id>.swc` entries), and the two connection
tables are told apart by their contents. 
Files are copied into `data/raw/codex/`
under canonical names such as `neurons.csv.gz`. Files over 1 GB (skeletons,
synapse table) are symlinked instead, so keep the originals where they are. The
skeletons are read straight from the zip; there is no need to unpack 33 GB!

### 2. Files from GitHub (scripted)

```bash
uv run python scripts/fetch_external.py
```

This downloads into `data/raw/external/`, pinned to fixed commits:

| file | from |
|---|---|
| `Connectivity_783.parquet`, `Completeness_783.csv` | [philshiu/Drosophila_brain_model](https://github.com/philshiu/Drosophila_brain_model) |
| `Supplemental_file1_neuron_annotations.tsv` | [flyconnectome/flywire_annotations](https://github.com/flyconnectome/flywire_annotations) |

Existing files are skipped, so feel free to re-run. The annotation file
is pinned to the last revision whose root IDs are exactly those of v783. Later
revisions (v3.0, October 2025 onward) swap in a few non-783 IDs.

## Building the database

```bash
uv run python scripts/build_db.py
```

This builds `data/processed/flywire_783.duckdb` from scratch and
replaces any existing copy. Root IDs are 18-digit integers and are always read
as `BIGINT`, never as floats, which would silently change them.

| table | contents |
|---|---|
| `neurons` | one row per neuron: Codex neurons + classification + name + cell type + cell stats |
| `annotations` | Schlegel et al. neuron annotations |
| `connections` | Codex connections, pairs with ≥ 5 synapses, one row per (pre, post, neuropil) |
| `connections_no_threshold` | the same without a threshold |
| `shiu_neurons`, `shiu_connections` | the Shiu et al. model's neuron index and signed weights |
| `coordinates`, `labels`, `processed_labels`, `visual_neuron_types`, `column_assignment`, `connectivity_tags` | other Codex per-neuron tables |
| `build_info` | source file and row count for each table |

Column names are normalised across sources: `root_id`, `pre_root_id`,
`post_root_id`, `syn_count`, `cell_type`, and `x_nm`/`y_nm`/`z_nm` for positions.

For the viewer, three more build steps:

```bash
uv run python scripts/build_synapses.py   # ~20 s, 2.1 GB
uv run python scripts/build_regions.py    # ~2 s, needs the synapse database
uv run python scripts/build_overview.py   # ~40 s, needs the skeleton zip
```

`build_synapses.py` loads the synapse table into its own database,
`data/processed/synapses_783.duckdb`. `build_overview.py` simplifies all 139,255
skeletons (727M nodes) into one whole-brain buffer of about 4.8M vertices
(30 MB gzipped) in `data/processed/overview/`. It prunes side branches shorter
than 20 µm, then keeps branch points, tips and a node every 20 µm of cable.

`build_regions.py` turns the 78 neuropils (brain regions) into smooth outline
meshes. FlyWire labels every synapse with its neuropil, so each region's shape
comes from where its synapses are: they are binned into 4 µm voxels, cleaned up,
and turned into a surface with marching cubes. It also works out each region's
main cell types and the regions it exchanges the most signal with. A neuron's
*home region* is the neuropil holding most of its synapses (tables
`neuron_neuropils` and `neuron_home_neuropil` in the main database).

## Viewer

```bash
npm --prefix web run build
uv run python scripts/serve.py
```

Then open <http://127.0.0.1:8000>. For frontend development, run the API with
`scripts/serve.py` and, in another terminal, `npm --prefix web run dev`, then open
<http://localhost:5173>; the dev server proxies `/api` to the API.

- **Levels of detail:** "Regions" shows only the brain regions; Sketch (the
  default) adds one example neuron per cell type and side, about 17,000 neurons;
  *All neurons* shows all 139,255.
- **Brain regions:** hover to name a region, click to read what it does and see
  its main cell types and where its signals come from and go to. The "Brain
  regions" tab lists them all, grouped by system.
- **Colors:** by super class, brain region, neurotransmitter, side, hemilineage,
  cell type and more, with a short explanation of each. Click a legend entry to
  highlight that group.
- **Search and inspect:** find neurons by cell type, name, community label (for
  example "MN9") or root ID, or click one in the view. The selected neuron is shown
  at full resolution with its details. The URL (`#neuron=<root_id>`) links to it.
- **Connectivity:** upstream partners in cyan and downstream in orange, brighter
  for stronger connections (you might want to raise the opacity to make it more
  noticeable), with a minimum synapse count. Other neurons are dimmed
  to a faint silhouette.
- **Synapses:** input and output synapse locations of the selected neuron.
- **Stimulate:** switch on a group of neurons and watch activity spread, slowed
  down: firing neurons glow on a heat scale and brain regions glow with the
  activity inside them. Choose a preset (sweet taste, bitter taste, pheromone
  smell, hearing), or the neuron, cell type or region you have selected. Each
  preset reports its key neurons, e.g. whether the feeding motor neuron MN9 fires
  (it does for sweet, not for bitter). Short explanations cover how the model
  works and its limits.

The view is anatomical: in the front (anterior) view dorsal is up and the fly's
right is on your left. FlyWire coordinates are left-handed (x → fly's right,
y → ventral, z → posterior), so the viewer mirrors them; see `web/src/scene/frame.ts`.

## Simulation

`fly_brain_sim.sim` re-implements the whole-brain leaky integrate-and-fire model
of Shiu et al. 2024 ([code](https://github.com/philshiu/Drosophila_brain_model)),
using numba instead of Brian2 and their v783 connectivity file
(`shiu_connections`). The equations, parameters and update order are theirs:

- each neuron's voltage leaks toward −52 mV (time constant 20 ms) and it fires
  when it crosses −45 mV, then is reset and refractory for 2.2 ms;
- a spike reaches each target 1.8 ms later and adds 0.275 mV × the number of
  synapses to its input, which decays with a 5 ms time constant. The input is
  negative if the sender is predicted to release GABA or glutamate;
- stimulated neurons receive random (Poisson) input, 150 Hz by default, strong
  enough to make them fire.

It runs one trial at a time (about 1 s of compute per simulated second for a
typical stimulus); Shiu et al. average 30.

**Validation** (`tests/test_sim.py`): stimulating the 20 sugar-sensing neurons
from their example (v630 IDs, 20 of the 21 unchanged in v783) makes the
proboscis motor neuron MN9 fire at about 100 Hz, and about 380 neurons become
active, matching their "about 400". Small synthetic networks check delays,
refractoriness, inhibition and silencing.

**Limitation:** the model treats the 293,762 Kenyon cell to Kenyon cell
connections in the mushroom body as excitatory. Once activity reaches the
mushroom body, it spreads through them and saturates (in the bitter and
pheromone presets Kenyon cells fire over a third of all spikes). In the real
brain, feedback inhibition keeps Kenyon cell activity sparse. Results report
`kenyon_cell_share` so this can be recognised.

API: `GET /api/sim/presets` and `POST /api/sim/run` with a target (a preset, a
list of root IDs, a cell type, or a region's neurons, capped at 300), a
stimulation rate and a duration.

## Checks and docs

```bash
uv run pytest
npm --prefix web test
uv run python scripts/inspect_raw.py
```

`pytest` validates the built database, the synapse database, the overview
buffers and the API. Tests for the optional pieces are skipped if they haven't
been built. `npm test` covers the frontend's decoders and colour logic.
`inspect_raw.py` profiles every raw file and regenerates
[docs/data_dictionary.md](docs/data_dictionary.md).

Things worth knowing about the data (each is covered by a test):

- The Codex figure of 3,732,460 connections counts neuron **pairs**. The
  thresholded file has 5,342,446 rows because a pair gets one row per neuropil.
- The Shiu model covers 138,639 of the 139,255 neurons. The 616 left out are
  almost all sensory afferents.
- Shiu's connectivity is based on a different synapse table from the Codex
  "Princeton" connections: 54.5M vs 76.9M synapses. Neuron IDs line up, but pair
  weights are not interchangeable.
- The Codex connections are the synapse table grouped by (pre, post, neuropil),
  without autapses, with synapses outside any neuropil labelled `UNASGD`. The one
  exception is 212 synapses (44 groups, mostly from one R7 photoreceptor) that
  are missing from the connection table.

## Data sources and license

The code in this repository is released under the [MIT License](LICENSE). No
FlyWire data is included; it is downloaded separately and keeps its own license.

FlyWire connectome data is released under
[CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) and may only
be used for **non-commercial** purposes. Please cite:

- Dorkenwald, S. et al. Neuronal wiring diagram of an adult brain.
  *Nature* 634, 124–138 (2024). <https://doi.org/10.1038/s41586-024-07558-y>
- Schlegel, P. et al. Whole-brain annotation and multi-connectome cell typing
  of *Drosophila*. *Nature* 634, 139–152 (2024).
  <https://doi.org/10.1038/s41586-024-07686-5>
- Shiu, P. K. et al. A *Drosophila* computational brain model reveals
  sensorimotor processing. *Nature* 634, 210–219 (2024).
  <https://doi.org/10.1038/s41586-024-07763-9>
