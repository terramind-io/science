# Flylab: digital fly and Pong

Live digital fly: https://jingsong-wang.github.io/fruit-fly/brain/
Original Pong: https://jingsong-wang.github.io/fruit-fly/

## Digital fly / Experiment 002

An interactive 3D feeding arena using **127,400 individual neurons and all 14,687,178 weighted connection rows** from the Shiu et al. FlyWire 630 model. The row count is not a count of individual synapses. This uses that paper's public dataset, not the newer MaleCNS dataset.

Food contact drives the author's 21 sugar sensory neurons with independent 100 Hz Poisson inputs. The stimulus button supplies 150 Hz for two model seconds. Neural MN9 output controls mouth extension and food consumption. Walking towards food, the conversion from spike rate to food uptake, and six-legged movement are engineered. This is a kinematic body, not a NeuroMechFly physics simulation or a complete biological twin.

The full signed connectivity is converted losslessly to outgoing CSR. Browser Web Workers simulate simplified leaky integrate-and-fire neurons at 0.1 ms steps: resting/reset voltage −52 mV, threshold −45 mV, membrane/synapse time constants 20/5 ms, delay 1.8 ms, refractory period 2.2 ms (zero for stimulated sensory neurons), synaptic gain 0.275 mV, and Poisson jump 68.75 mV. Subthreshold integration is exact for these linear equations; state is frozen during refractory periods. Sparse scheduling drops tails below 1e-9 mV. These browser dynamics are a port, not certified identical to the authors' Brian2 implementation. No model training is performed.

Source: [Shiu et al., Nature 2024](https://doi.org/10.1038/s41586-024-07763-9), [author code and data](https://github.com/philshiu/Drosophila_brain_model), pinned to commit `91bdd1e7dcf193f3e7ca5a8933497fcef63b7960`. Source checksums, original cell IDs, conversion hash, model parameters, and MIT license are included under `dist/brain/data/`. Three.js 0.180.0 is MIT licensed under `dist/brain/vendor/`.

Controls: click the arena to add sugar, apply sensory stimulation, cut input, silence MN9, pause/reset, switch camera, run independent three-condition validation, and export a JSON recording. Each visitor runs their own simulation locally; no shared always-on animal or server is provided. Downloads approximately 49 MB on first load. Requires a modern WebGL browser with Web Workers and DecompressionStream. Desktop is recommended. Speed depends on the device; the interface reports measured model time / wall time rather than assuming real-time execution. Background tabs pause automatically.

### Build and validation

Requires Node 24 and Python 3.12. Install `numpy==2.2.6 pyarrow==25.0.1`, then:

```sh
python scripts/build-brain.py --download
node --test tests/*.test.mjs
node scripts/benchmark-brain.mjs
node server.mjs
```

Open `http://127.0.0.1:4173/brain/`. Set `PORT` to override the local port. Large generated graph and vendor JavaScript files are not committed; CI downloads pinned dependencies, verifies source checksums, builds the graph, runs behavioral checks, and deploys the compressed data with the site.

Local seed-42 full-graph checks (one model second each) produced MN9 0 spikes with no input, 88 with 100 Hz sugar, 109 with 150 Hz sugar, and 0 with 150 Hz sugar plus MN9 silencing. These are model sanity checks, not evidence of biological accuracy. Unit tests also compare sparse/dense scheduling on a small graph and ensure food cannot be consumed without motor output. The browser validation uses 100 Hz for both sugar conditions. Strong-input local benchmarks took approximately 1.2–2.8 wall seconds per model second; a live session including inactive periods ran around 0.8×. Performance is not guaranteed on other devices.

## Pong / Experiment 001

Local browser demo using a reduced public Drosophila visual connectivity graph. Run `node server.mjs`, then open http://127.0.0.1:4173. No installation or GPU required. Run `node --test tests/core.test.mjs` for controller and deterministic physics checks.

## GitHub Pages

The `Test and deploy Flylab` workflow tests the controller, validates JavaScript, and publishes only `dist/`. Enable **Settings → Pages → Source → GitHub Actions** once. Pushes to `main` automatically update the site. The browser runs the simulation; the local Node server is not needed online. All application assets use relative URLs, supporting a repository subpath.

## Model and boundaries

Source: TuragaLab/flyvis, `flyvis/connectome/fib25-fib19_v2.2.json`, retrieved 2026-09-16; main commit observed: `92b3845cc426dd309a1a0e1b3890156c42e14021`. Original paper: https://doi.org/10.1038/s41586-024-07939-3.

65 named type entries, 605 connection rules. Sum spatial-offset synapse counts, apply alpha signs, normalize each target's absolute incoming weights. Discard geometry. Run two copies of a leaky tanh rate network. These are type populations, not 130 reconstructed individual neurons. Engineered vertical ball-minus-paddle error drives R1–R8; this is not a retinal simulation. A non-photoreceptor linear readout is trained with normalized SGD on synthetic error/desired-action pairs. This is interface calibration, not biological learning. No direct ball-position bypass is used by the neural readout.

Shuffled baseline permutes target labels over edges, retaining the weight list and target counts (not target strengths). It gets the same calibration procedure. Random action baseline samples every four fixed steps. Right paddle auto-returns the ball. Fair comparison runs 120 simulated seconds per mode, seed 42, difficulty 1, inputs enabled, separate from the live session. Single-seed demo results are not scientific evidence of a topology advantage.

The network view shows real model state in a schematic layout; traces show mean absolute activity in each channel. The model is NOT MaleCNS, NOT full-brain emulation, and NOT a reproduction of flyvis dynamics or published trained models.

Controls: Space to pause; select manual mode and use arrows/W/S or drag on the arena. Export records session settings/results in JSON. Simulation remains local. Optional Google Fonts can be blocked without affecting functionality.
