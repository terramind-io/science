# Flybrain

**Every neuron of a fruit fly's brain, switched on.**

Flybrain simulates all **138,639 neurons** and **15.1 million connections** of the adult *Drosophila* brain. Stimulate any cell type and watch the signal spread, from taste or vision to the neurons that move the body. There's a 3D lab, a plain-language command center, and a Python simulator that runs on a laptop.

Built by [Dhruv Agrawat](https://github.com/dhruvagrawat).

<!-- Add your Vercel URL here once deployed: **Live site →** https://flybrain.vercel.app -->

## What's inside

- **Eight apps** where the fly's own neurons take control, live in the browser: Fly Food Critic, Smell-o-vision, Fly Brain Surgeon, Flappy Fly, Twitch Plays Fly Brain, Fly Brain Radio, Is It Really the Fly? and Fly Gangs. Each has an autopilot and a scrambled-wiring control.
- **The lab.** A WebGL map of every neuron at its real position, replaying experiments spike by spike. Brain output readout (feeding, escape, walking), population chart, spike raster, neuron table, experiment log and run comparison.
- **Command center.** Press <kbd>⌘K</kbd> and type `stimulate sugar at 200 hz, silence CB0248, run`.
- **Animated explainers.** A live neuron you drive with sliders, and a toy circuit you can lesion by clicking.
- **Simulator.** A NumPy + Numba reimplementation of the Shiu et al. (2024) whole-brain model: one simulated second in ~9 s on one CPU core.
- **Docs.** Guides, model details, API reference, [roadmap](ROADMAP.md), [changelog](CHANGELOG.md) and a [lab notebook](NOTEBOOK.md) of experiment results.

## Quick start

```bash
git clone https://github.com/dhruvagrawat/fly-brain-sim && cd fly-brain-sim
pip install -r requirements.txt
python -m flybrain fetch            # ~140 MB of connectome data, once
python -m flybrain serve            # the lab at http://127.0.0.1:8050
```

Or straight from the terminal:

```bash
python -m flybrain run --stim sugar --rate 200 --trials 10
python -m flybrain run --stim looming --silence DNp01
```

Stimulating sugar-taste neurons activates ~430 neurons and drives the feeding motor neuron MN9 at ~115 Hz, reproducing the paper's key result.

### Web app

```bash
cd web && npm install
npm run dev        # develop on :3000
npm run build      # static site in web/out/, which `flybrain serve` also serves
```

Deploys to Vercel with no settings: import the repo at [vercel.com/new](https://vercel.com/new). The hosted site replays recorded experiments and can connect to a local `flybrain serve` for live runs.

## Repository

```text
flybrain/        Python simulator, CLI and local server
scripts/         export recorded experiments, build + validate app circuit packs, OG images
web/             Next.js site: landing page, lab, docs (content/docs/*.md)
CHANGELOG.md     what changed
ROADMAP.md       what's next: virtual body, training, the male brain
NOTEBOOK.md      experiment results
```

## Credits

Flybrain is my project. The science underneath comes from:

- **FlyWire connectome.** Dorkenwald et al., *Nature* 2024. Cell types and positions: Schlegel et al., *Nature* 2024.
- **Whole-brain model and packaged data.** Shiu et al., *Nature* 2024 · [philshiu/Drosophila_brain_model](https://github.com/philshiu/Drosophila_brain_model) (MIT).

Full citations are in [the docs](web/content/docs/credits.md). Connectome data is downloaded at runtime and not redistributed. Please cite the original papers if you use this in research.
