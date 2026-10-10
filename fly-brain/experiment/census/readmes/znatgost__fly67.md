# FLY67 🪰

**A whole fruit fly brain — all 138,639 neurons and 15.1 million connections of the FlyWire connectome — simulated live in your browser tab and wired to a virtual fly.**

No server, no Python, no GPU cluster. A spiking model of the entire adult *Drosophila* brain runs in a Web Worker, faster than real time, every spike is drawn in 3D, and the brain drives a 3D fly in a 3D arena. Put sugar under the fly's proboscis and watch the signal travel from taste neurons to the motor neuron that extends it. Swing a shadow at it and watch the Giant Fiber fire and the fly take off.

![FLY67 demo](docs/demo.gif)

<img src="docs/brain3d.gif" width="49%" alt="the brain, all 138,639 neurons, turning in 3D"> <img src="docs/sixseven.gif" width="49%" alt="the 3D fly doing six seven">

**[▶ Live demo](https://znatgost.github.io/fly67/)** · [video (mp4)](docs/demo.mp4) · [screenshot](docs/screenshot.png)

---

## What happens on screen

| You do | The connectome does (nothing hand-wired) | The fly does |
|---|---|---|
| Put a sugar drop under it | sugar GRNs → SEZ interneurons → **MN9** (proboscis motor neuron) | extends the proboscis and feeds |
| Lace the sugar with bitter | bitter GRNs recruit inhibition, MN9 drops ~14× (52 → 3.7 Hz) | stops feeding |
| Puff air on an antenna | Johnston's organ (JO-C/E) → aBN1 → **aDN1** | grooms its antennae |
| Bring a looming shadow from the left | LC4 / LPLC2 → **Giant Fiber** (DNp01), **right DNa02**, MDN | turns away / takes off |
| Silence the Giant Fiber, then threaten | GF output synapses cut; the steering pathway (DNa02) still responds | turns away instead of taking off |
| Wait ~20 s, or press *Six seven* | — (scripted easter egg, see below) | does the **6-7** meme with its front legs, with a close-up |
| Anything in the *Optogenetics lab* | activate (Poisson drive, like CsChrimson) or silence (like Kir2.1) any of 8,840 cell types | whatever the brain decides |

The "turn away" result is emergent: looming on the **left** eye recruits the **right** DNa02 steering neuron and vice versa, straight out of the wiring diagram. `npm run circuits` checks every row of this table against the full brain on each CI run.

## Six seven 🤲

<img src="docs/sixseven.gif" width="480" alt="the fly doing the 6-7 meme">

Every ~15–25 s of simulated time the fly stops, turns to the middle of the arena, rears up and pumps its front legs — *six… seven* — while the camera swoops to a front close-up. **This one is a scripted animation, not a connectome output**: the brain has no "6-7 circuit", and this dataset has no leg motor neurons. It's labelled as such in the UI log.

## Validation

FLY67 is a from-scratch JavaScript re-implementation of the leaky integrate-and-fire model of
[Shiu et al., *Nature* 2024](https://www.nature.com/articles/s41586-024-07763-9). It was checked
against the authors' own Brian2 code ([philshiu/Drosophila_brain_model](https://github.com/philshiu/Drosophila_brain_model)) on the same connectome (FlyWire v630), stimulating the 21 right labellar sugar neurons:

| Experiment | Reference | Pearson r, all neurons | top-20 responders shared | MN9 rate (ref → FLY67) |
|---|---|---|---|---|
| sugar 150 Hz | Brian2 2.9, authors' `model.py` | **0.9996** | 20 / 20 | 84.1 → 83.5 Hz |
| sugar 100 Hz | Brian2 2.9, authors' `model.py` | **0.9994** | 19 / 20 | 66.0 → 68.6 Hz |
| sugar 100 Hz | results shipped with the paper repo | **0.9997** | 20 / 20 | 67.0 → 68.6 Hz |

Details: [`validation/report.json`](validation/report.json). One subtlety that matters: in Brian2, `g` is declared `(unless refractory)`, which silently discards synaptic input arriving during the refractory period (a *conditional write*). Missing it inflates downstream rates by ~50 %; FLY67 reproduces it.

## How it's fast enough

- **Lazy exact integration.** Sub-threshold LIF dynamics are linear, so for every neuron FLY67 keeps a cheap upper bound on the highest voltage it can still reach without new input: `max(u, 0) + max(g, 0) · Cmax`. Neurons that provably can't fire are **not stepped at all**; when a spike reaches them, their state is advanced analytically (`u·Aₖ + g·Cₖ`, `g·Bₖ`) from lookup tables. Only a few hundred "hot" neurons out of 138k are integrated each 0.1 ms step.
  Result: **spike-for-spike identical** to stepping every neuron (`validation/lazy_vs_dense.mjs`), **8–12× faster**, 15–20× real time in Node for the sugar experiment.
- **Compact connectome.** CSR by presynaptic neuron, delta-coded postsynaptic indices, zig-zag signed synapse counts, all LEB128 varints: 15.1 M edges → 42 MB → **31 MB gzipped**, decoded with the browser's native `DecompressionStream` in ~1 s.
- **One draw call.** 138,639 points in WebGL2 with additive glow; spikes decay on the CPU and stream to the GPU each frame.
- **3D arena.** A procedurally built, fully articulated fly (18 leg joints, wings, compound eyes) posed every frame from the same state the brain drives — no assets, ~580 KB of three.js.

## Architecture

```
index.html
src/
  engine.js      LIF engine (Shiu et al. 2024 parameters), lazy exact updates, zero dependencies, Node + browser
  worker.js      runs the brain in real time, streams spikes and motor-neuron counts to the UI
  neurons.js     neuron table: FlyWire IDs, positions, super class, cell type, side, transmitter
  circuits.js    which neurons are sensors (GRNs, JO, LC4/LPLC2) and which are read out (MN9, GF, aDN1, P9, DNa02, MDN)
  arena.js       the world: drops, air puffs, looming objects → sensor rates; motor rates → body kinematics (+ 2D fallback view)
  arena3d.js     three.js view: articulated 3D fly (tripod gait, grooming, proboscis, wings, flight), follow/overview camera
  vendor/        three.js r186, tree-shaken to the classes used (tools/build_three.sh)
  brain-view.js  WebGL2 point cloud, picking, inspector
  app.js         UI, experiments, optogenetics lab; `window.fly67` scripting hook
tools/
  build_data.py  FlyWire parquet/TSV → data/*.bin.gz
  data-node.mjs  loads data/ in Node (joins the connectome parts)
  probe.mjs      command-line lab: `node tools/probe.mjs --on "type:LC4:100" --off "type:DNp01"`
  capture.py     deterministic GIF/MP4 recorder (steps the brain frame by frame, 1x playback on any machine)
validation/      comparison with Brian2, lazy-vs-dense equivalence, behaviour checks
test/            unit tests (node --test)
```

## What is real and what is not

Being honest about this is the point of the project.

**Real**
- The wiring: every neuron and every neuron-to-neuron connection of FlyWire v783 as packaged by Shiu et al. (15.1 M pairs, down to single synapses), with synapse counts as weights and excitatory/inhibitory signs from predicted neurotransmitters (Eckstein et al. 2024).
- The neuron model and its parameters, exactly as in Shiu et al. 2024, validated above.
- Every path from sensory neuron to motor/descending neuron. MN9, Giant Fiber, aDN1, DNa02 and MDN firing are outputs of the simulation, not scripts.

**Simplified / hand-made**
- **Neurons are point LIF units** with a single global synaptic weight — no dendrites, gap junctions, neuromodulation or plasticity. This model predicts many experiments well and gets others wrong.
- **Sensory input is coarse.** A sugar drop drives the known sugar GRNs at a fixed Poisson rate; a looming shadow drives the LC4 and LPLC2 populations of one eye. The retina and optic lobe are simulated but are not fed images.
- **There is no body, ventral nerve cord or leg motor system in the connectome.** The 3D body is animated, not physically simulated. The arena turns descending-neuron rates into movement with a few gains (`MOTOR_GAIN` in `arena.js`), following published roles: P9 = forward (+ ipsilateral turn), DNa02 = ipsilateral steering, MDN = backward, GF = takeoff, aDN1 = antennal grooming, MN9 = proboscis extension.
- **The "walking drive" is external.** Walking is started by Poisson stimulation of P9 (DNp09), as in an optogenetics experiment. Experiments that need the fly still set it to 0.
- It is **not** an uploaded mind and the fly is not conscious. It's a wiring diagram with a simple spiking rule — which is exactly why it's remarkable how much it gets right.

## Run it

```bash
git clone https://github.com/znatgost/fly67 && cd fly67
npm start                 # any static server works: python3 -m http.server
# open http://localhost:8080
```

The compressed connectome is in `data/` (33 MB, stored as two parts under 25 MB so the repo can be uploaded through the GitHub website). Needs a browser with WebGL2 and `DecompressionStream` (Chrome/Edge/Firefox/Safari 16.4+) and ~400 MB RAM.

```bash
npm test                  # unit tests incl. lazy == dense equivalence on a random network
npm run circuits          # behaviour checks on the full v783 brain
node tools/probe.mjs --on "type:LC4:120" --off "type:DNp01" --ms 1000   # your own experiment
```

Rebuild the data / rerun the Brian2 comparison:

```bash
npm run build-data                           # clones the source repos (~200 MB) and packs data/
python3 tools/build_data.py --v630           # + the v630 graph used by validation
node validation/validate.mjs 30
node validation/lazy_vs_dense.mjs
cd sources/Drosophila_brain_model && python ../../validation/run_brian2.py 8   # needs brian2
```

## Credits and licenses

Code: MIT © Ruben ([@znatgost](https://github.com/znatgost)).

Data (CC-BY 4.0, please cite if you use this):
- Dorkenwald et al. *Neuronal wiring diagram of an adult brain.* Nature 2024 — FlyWire connectome
- Schlegel et al. *Whole-brain annotation and multi-connectome cell typing of Drosophila.* Nature 2024 — cell types, positions ([flywire_annotations](https://github.com/flyconnectome/flywire_annotations))
- Shiu et al. *A Drosophila computational brain model reveals sensorimotor processing.* Nature 2024 — model, parameters, GRN/JON neuron lists ([Drosophila_brain_model](https://github.com/philshiu/Drosophila_brain_model))
- Eckstein et al. *Neurotransmitter classification from electron microscopy images at synaptic sites in Drosophila melanogaster.* Cell 2024

Behavioural roles of the read-out neurons: Bidaye et al. 2014 (MDN), Bidaye et al. 2020 (P9), Rayshubskiy et al. 2020 / Yang et al. 2024 (DNa02), von Reyn et al. 2014 (Giant Fiber), Hampel et al. 2015 (aDN1), Gordon & Scott 2009 (MN9).

Not affiliated with FlyWire, Janelia, Google or the authors above.
