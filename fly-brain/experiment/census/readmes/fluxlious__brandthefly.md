# BrandTheFly

**How does a fly feel about your brand?** An experiment by [@fulutmd](https://x.com/fulutmd).

Live at **https://fluxlious.github.io/brandthefly/** (studio: [/studio.html](https://fluxlious.github.io/brandthefly/studio.html)).

Type a brand or upload a logo, watch it slide through a simulation of a real fruit fly brain (all 138,639 neurons of the FlyWire connectome), see what the fly does and how it feels about it, and get an 11-second clip to post. Everything runs in the visitor's browser; nothing is uploaded.

## What's in here

```
brandthefly/
├── docs/                         the website (GitHub Pages serves this folder)
│   ├── index.html                landing page: hero replay, fly moods, clip maker
│   ├── studio.html               Fly Brain Billboard: full studio (text/logo/senses, LED ticker, readouts, 9:16 clip frame)
│   ├── hero.json                 pre-simulated "NIKE" replay + output neuron rates (the big panel)
│   ├── badge.json                pre-simulated "BRANDTHEFLY" replay (the small brain at the top)
│   ├── counts.json idx.json      brain wiring (4.9M connections, compressed)
│   ├── w8.json wover.json        connection weights
│   ├── pos.json                  neuron positions (front view)
│   ├── groups.json               named neuron groups (steering, escape, feeding, dopamine…)
│   ├── preview.png               link preview image for X
│   └── .nojekyll
└── pipeline/                     how the data and replay were made
    ├── 00_download.sh            download raw data (Shiu et al. model + FlyWire annotations)
    ├── 01_convert_connectome.mjs parquet -> raw arrays (Node + hyparquet)
    ├── 02_positions.py           neuron positions
    ├── 03_groups.py              neuron groups
    ├── 04_validate_pruning.py    checks the pruned web network behaves like the full one
    ├── 05_export_web.py          writes the website data files into docs/
    ├── 06_hero_sim.py            simulates a sliding LED text through the brain
    ├── 07_pack_hero.py           packs that replay into docs/hero.json
    ├── 08_fly_mood_test.py       runs brands/shapes and prints appetite, curiosity, dopamine
    ├── 09_hero_sim_web.mjs       re-simulates the hero replay from docs/*.json alone (no raw download)
    ├── simlib.py                 the brain model (leaky integrate-and-fire, Shiu et al. parameters)
    ├── font57.json / .txt        5×7 LED dot-matrix font
    └── extras/name_snapshot/     scripts for the very first "CEM" brain snapshot (outputs not committed)
```

## Run the site locally

```bash
cd docs
python3 -m http.server 8000
# open http://localhost:8000  (and http://localhost:8000/studio.html)
```
Opening index.html directly as a file won't work; browsers block loading the data files that way.

## Put it live on GitHub Pages

```bash
git init -b main
git add .
git commit -m "BrandTheFly: first version"
gh repo create brandthefly --public --source=. --remote=origin --push
gh api -X POST repos/{owner}/brandthefly/pages -f "source[branch]=main" -f "source[path]=/docs"
```
Without `gh`: create an empty public repo on github.com, `git remote add origin https://github.com/<you>/brandthefly.git`, `git push -u origin main`, then Settings → Pages → Deploy from a branch → `main` → `/docs`.

Live after about a minute at `https://<you>.github.io/brandthefly/`. For the X preview image, change the two `preview.png` tags in `docs/index.html` to the full URL.

## Rebuild the data yourself

```bash
cd pipeline
./00_download.sh                       # ~120 MB
npm install                            # hyparquet
pip install -r requirements.txt
node 01_convert_connectome.mjs
python 02_positions.py
python 03_groups.py
python 04_validate_pruning.py          # optional, a few minutes
python 05_export_web.py                # -> ../docs/*.json
python 06_hero_sim.py "BRAND THE FLY"  # ~1 minute
python 07_pack_hero.py                 # -> ../docs/hero.json
python 08_fly_mood_test.py "CEM,PIZZA,sugar"
```
Steps 01–05 reproduce the site's data files byte for byte.

To change only the hero replay (the text, or where the LED band sits) you don't need the raw data:

```bash
cd pipeline
node 09_hero_sim_web.mjs "NIKE" 243                          # big replay -> ../docs/hero.json, ~40 s
node 09_hero_sim_web.mjs "BRANDTHEFLY" 243 ../docs/badge.json  # small brain at the top
```
It prints the fly-mood numbers for the run; paste them into `CONFIG.verdicts` in `docs/index.html`.

## How it works (and what's real)

- **Real:** the wiring (FlyWire connectome, connections with 3+ synapses kept for the web, 4.9M of 15.1M; checked against the full network), the neuron model and parameters from Shiu et al. 2024, and every neuron's position.
- **Stimulus:** neurons under your logo or LED dots get 300 Hz input while it passes over them. The fly's output neurons (1,299 descending neurons and the motor neurons) are never driven directly, so what the fly does has to come through the wiring.
- **The fly:** a 2D animation driven by output neurons: DNa01/DNa02 steering, MDN backward walking, giant fiber takeoff, MN9 proboscis, pharynx, antenna and neck motor neurons.
- **Fly moods:** playful names for real activity. Appetite = MN9 compared with a real sugar taste in the same model (146 Hz). Curiosity = antenna motor neurons. Buzz = neurons that fired. Dopamine critic = reward (PAM) vs punishment (PPL1) neurons.
- **Not real:** no animal is involved, and the fly has no actual opinion about brands.

## Credits

- Brain wiring: FlyWire connectome (Dorkenwald et al. 2024, Nature; Schlegel et al. 2024, Nature), CC BY 4.0.
- Neuron model: Shiu et al. 2024, Nature, [philshiu/Drosophila_brain_model](https://github.com/philshiu/Drosophila_brain_model) (MIT).
- Parquet reading: [hyparquet](https://github.com/hyparam/hyparquet) (MIT).

## License and attribution

Code (the site and the pipeline) is MIT, see `LICENSE`. The data files in `docs/` are derived from the [FlyWire](https://flywire.ai) connectome (CC BY 4.0; Dorkenwald et al. 2024, Schlegel et al. 2024). The neuron model follows [Shiu et al. 2024](https://github.com/philshiu/Drosophila_brain_model) (MIT). If you reuse the data files, keep that attribution.

The site counts visits anonymously with [GoatCounter](https://www.goatcounter.com) (no cookies, no personal data). Logos and brand names never leave the visitor's browser.
