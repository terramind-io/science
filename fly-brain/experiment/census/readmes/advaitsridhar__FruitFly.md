# Virtual Fly

A whole-nervous-system fruit fly you can play with. It simulates the complete wiring diagram of a
male fruit fly's central nervous system (every neuron in its brain, optic lobes and nerve cord:
176,422 neurons, 6.3 million connections) and connects it to a little fly in a petri dish that
sees, smells, tastes, hears, feels the wind, learns, courts, and runs away.

It needs Python and one library (NumPy). There is nothing to train, and nothing runs in the cloud.

![The fly eating sugar while its brain map lights up](docs/preview.png)

```
fly_game.py        play: a local web server with the arena, the senses and the body
fly_brain.py       experiment: run the validated protocols, poke neurons, trace wiring routes
my_first_fly.py    the smallest possible experiment (start here if you want to write code)
virtual_fly/       the code (docs/ARCHITECTURE.md is the map)
docs/SCIENCE.md    what was measured on the real connectome, and why the kit is built the way it is
docs/API.md        the game's HTTP API, for driving the fly from your own program
tests/             a test suite that runs on a small synthetic connectome (no download needed)
data/              the connectome, downloaded automatically the first time (23 MB)
```

---

## 1. What this is

On **3 September 2026**, HHMI Janelia, the University of Cambridge and Google Research published the
first complete connectome of a male fruit fly's central nervous system, "MaleCNS v1.0", in *Cell*.
Within a day people were wiring it into Minecraft, Doom, Beat Saber and a car simulator. The
neuroscientists' reality check was that most of those demos never closed a real
sensation-to-action loop: they fed noise into the network and mapped a few neurons to buttons.

This kit is built around the honest version, following Shiu et al. (*Nature*, 2024): specific
sensory inputs, the real wiring, specific output neurons, and every hand-built part labelled.
Compared with the small starter it grew from, it adds:

| | what it does | comes out of the wiring? |
|---|---|---|
| **A retina** | two compound eyes render what the fly sees; looming, small moving objects and wide-field motion are computed from the images, and the connectome's own T4/T5 motion-detector columns are driven facet by facet | the escape (LC4/LPLC2 → giant fibre), the chase (LC10a → DNa02) and the optomotor reflex (T4/T5 → HS → DNp15/DNa02) are wiring; the retina and feature computations are hand-built |
| **Smell** | odour sources release turbulent plumes carried by the wind; each odour drives its own set of glomeruli | a sparse, odour-specific Kenyon-cell code (7-9 % of cells) and MBON responses are wiring |
| **Learning** | dopamine-gated depression of Kenyon-cell → MBON synapses, the fly's actual learning rule; pair an odour with sugar, bitter or shock and its preference changes | which synapses are plastic and which dopamine neurons gate which MBON come from the wiring; bitter → punishment dopamine is wiring; sugar → reward dopamine is injected (labelled); the rule's constants are hand-chosen |
| **A second fly** | a scripted female to chase, tap and sing to; or, with `--partner female`, a second *simulated* brain (FlyWire's female) in the dish, each fly sensing the other only through the world: sight, his song on her Johnston's organ, a foreleg's touch, bumping | the chase and the song (pC1 → pIP10 → wing motor neurons) are wiring, and so is everything her sensory neurons do next; the scripted female's behaviour, the contact-to-pC1 arousal and each channel between two simulated flies (its rate, range and units) are hand-built and labelled (`docs/SCIENCE.md` section 10) |
| **Wind, sound, touch** | Johnston's organ senses wind direction and sound; a clap can make the fly jump | sound → giant fibre and wind → grooming are wiring; heading upwind is hand-built |
| **Internal state** | hunger and thirst rise with time and change what the fly tastes; hunger also changes what it does (thirst cannot: the fly never drinks by itself, because in this wiring water alone does not reach MN9, the proboscis motor neuron; zapping MN9 on a water drop does make it drink) | hand-built |
| **A better model** | short-term synaptic depression, background noise, per-population output modulation, threshold heterogeneity, checkpoints, spike recording, rate monitors, a `--fast` 1 ms step; the integrator is the starter's (identical spikes), or the same step as compiled numba kernels when numba is installed (about twice as fast, still identical spikes) | the mechanisms are documented physiology; the parameters are chosen by hand |
| **Tools** | a pathway tracer ("how does the eye reach the steering neurons?"), lesion scans, dose-response sweeps, seeds, JSON export, scenarios (conditioning protocols, courtship, plume following, escape), a 3-D brain map, an event log, session recording | analysis, not model |
| **Genetics** | the neurons that express *fruitless* and *doublesex* (the genes that make a male brain male) and the male-specific and dimorphic ones, as populations to silence, activate or watch; the transmitter genes behind every neuron's sign; a lookup of which real driver lines label a population and which neurons a line labels (NeuronBridge); five genetic experiments | the expression labels are the MaleCNS annotation read from the data; the lookups are Janelia's; nothing is hand-built, but only two transcription factors and the transmitter identity are known here |
| **The genome as a recipe** | grow a new fly from the connectome's cell-type wiring rules alone (same neurons, new wiring) and see which reflexes survive; a bottleneck dial squeezes the rules; seeds are individuals | the rules are learned from the data; growth is random within them; 9 of 11 validated reflexes survive type-level rules, none survive class-level rules |
| **What the literature says** | every cell type joined to its class in the FlyBase anatomy ontology (Virtual Fly Brain): `fbbt:lobula columnar neuron` or `fbbt:dopaminergic neuron` as populations, an ontology search in the Neuron lab, a neuron's popover says what its type is (definition, lineage, peptides, curated transmitter, a VFB link); with the parts list on, the literature's transmitter wins over the prediction for the modulators and the tone's sign on each target follows the receptors its type expresses in the adult scRNA-seq atlases | the join is by name (offline, checked against VFB's own MaleCNS names); the transmitters are the ontology's curated assertions; the receptor fractions are Fly Cell Atlas and other atlases as VFB serves them; the rule that turns receptors into a sign is the kit's |
| **The genes as a parts list** | a switch that gives each neuron the machine its genes make: the dopamine, octopamine and serotonin neurons leave slow tones on their targets (all their receptors are slow; 2,146 neurons with the literature's transmitters, the default, of which 976 lose their fast synapses and 1,170, mostly the Mi15 cells, also release a fast transmitter and keep them; the connectome's own prediction names 979), and 43,000 optic-lobe cells that do not spike in real flies release transmitter in proportion to their depolarisation; three tone gauges; a per-type table for thresholds | which neurons make which transmitter is the data; that these three act slowly and that those cell types are graded is the literature (cited in `parts.py`); the strength and time constant of each tone are chosen by hand; all 16 validated experiments pass |

Everything on screen says which of the two it is; the **"What's real here?"** button lists it all.

## 2. Setup

**Quick start** (macOS / Linux; on Windows, use the commands for cmd in step 3 below and `py`
instead of `python3`):

```
git clone https://github.com/advaitsridhar/FruitFly.git
cd FruitFly
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install numpy numba
python3 fly_game.py
```

The first start downloads the 23 MB connectome into `data/` and opens the game in your browser;
later starts are instant. The two `.venv` lines give the kit its own virtual environment (Debian,
Ubuntu and Homebrew Pythons refuse `pip install` outside one); in a new terminal, activate it again first.
Already have a clone? `git pull origin main` brings it up to date.

Step by step:

1. Install **Python 3.10 or newer** from [python.org](https://www.python.org/downloads/) (3.10-3.12
   if you want the optional physics body). On Windows, tick **"Add python.exe to PATH"** in the installer.
2. Get the code: `git clone https://github.com/advaitsridhar/FruitFly.git` (or download and unzip
   it from GitHub), then open a terminal in the `FruitFly` folder (Windows: click the File Explorer
   address bar, type `cmd`, press Enter).
3. Make a virtual environment (the kit's own set of packages, in the folder `.venv`), then install
   NumPy into it, and numba for the compiled brain integrator (optional, about twice as fast, same spikes).
   Windows (cmd):
   ```
   py -m venv .venv
   .venv\Scripts\activate
   py -m pip install numpy numba
   ```
   macOS / Linux:
   ```
   python3 -m venv .venv
   . .venv/bin/activate
   python3 -m pip install numpy numba
   ```
   In every new terminal, run the second line again (in the `FruitFly` folder) before steps 4 and 5.
   On Debian or Ubuntu, `python3 -m venv` may first need `sudo apt install python3-venv`.
4. Check the brain works (downloads the data the first time, then runs the validated experiments):
   ```
   py fly_brain.py --profile game
   ```
5. Play:
   ```
   py fly_game.py
   ```
   Your browser opens the game. Keep the terminal window open; press `Ctrl+C` in it to quit.

On macOS or Linux, use `python3` instead of `py`. To install the package with its console scripts
and the test tools (in the virtual environment): `py -m pip install -e ".[dev]"` then `fly-game`,
`fly-brain`, `pytest`. The page's own tests in a browser (`tests/test_browser.py`) need one more extra, `py -m pip install -e ".[browser]"`,
and a one-time browser download, `py -m playwright install chromium` (about 150 MB; on Linux also `py -m playwright install-deps`,
which asks for sudo); they run only with `VF_BROWSER_TESTS=1` set. A plain `pip install .` (or `pip install git+https://github.com/advaitsridhar/FruitFly.git`,
without a clone) works too: that copy carries the four small data files inside the package and
downloads the connectome to `~/.cache/virtual-fly` instead of `data/`. `FLY_DATA_DIR` sets another folder
for everything the kit downloads or builds, in an installed copy and in a checkout alike (a checkout then
downloads into that folder rather than using `data/`).

**The female fly** (`--female`, and `--partner female`, which puts her in the dish with the male) needs one
more package, `py -m pip install pyarrow`, and the first run with either flag downloads about 130 MB (FlyWire's
connectivity table and annotations) and builds a 45 MB file: in `data/` in a checkout, in `~/.cache/virtual-fly` in an installed copy, or in `FLY_DATA_DIR` when that is set.

**A female with a nerve cord** (`--fly banc`, and `--partner banc` in the two-fly game) is BANC, one adult female's brain and
ventral nerve cord (Bates et al. 2026, Nature; the data deposit on Harvard Dataverse, doi:10.7910/DVN/7WTH1N, CC BY 4.0),
fetched once (0.44 GB, pinned by checksum) and built in under a minute (`docs/SCIENCE.md` section 14). FlyWire stays the
default female.

**The physics body** (`--body physics`, optional) needs Python 3.12-3.14 (flygym 2.1 installs on no other) and
about 400 MB of packages; in a virtual environment made with such a Python: `py -m pip install -e ".[physics]"`
(flygym 2.1.0 with MuJoCo 3.9; docs/SCIENCE.md section 6.7). One physics fly runs at real time, two at about half.

**The GPU brain** (`--backend cupy`, optional; Windows and Linux with an NVIDIA GPU, no CUDA toolkit to install) runs
the same model, spike for spike, on the graphics card through CuPy (`docs/SCIENCE.md` section 11). Install CuPy for
your driver generation, with the kit's NumPy and numba pinned so nothing else moves. With a driver of the R580 series
or newer (CUDA 13; `nvidia-smi` shows the version) on a Turing card or newer:

    py -m pip freeze | findstr /R "^numpy== ^numba== ^llvmlite==" > constraints.txt
    py -m pip install -c constraints.txt cupy-cuda13x "cuda-toolkit[nvrtc,cudart]==13.*"

(macOS / Linux: `python3 -m pip freeze | grep -E '^(numpy|numba|llvmlite)==' > constraints.txt`, then the same
`install` line with `python3 -m pip`; macOS has no CUDA, so the GPU brain is Windows and Linux only.) With a driver of
the R525-R579 series: `cupy-cuda12x "cuda-toolkit[nvrtc,cudart]==12.*"` instead. About 70 MB of wheels, under
NVIDIA's own licence; the first run compiles the kernels (a few seconds, cached in `~/.cupy/kernel_cache`). Then
`py fly_game.py --partner female --backend cupy` (the terminal says "Brain integrator: the GPU (CuPy)") or
`py fly_brain.py --backend cupy`. Measured here (an RTX 4070 Laptop GPU, `docs/SCIENCE.md` 11.3): one busy brain steps
about twice as fast as numba on one core (the male 8x real time against 4x, the female 7x against 5x; with the parts list
on 6x and 4x against 2x), spike for spike the same. GAME_SPEED_README_PLACEHOLDER

**If something goes wrong**

| Problem | Fix |
|---|---|
| `'py' is not recognized` | Python isn't on PATH: re-run the installer and tick "Add python.exe to PATH" (or use `python`). |
| `Activate.ps1 cannot be loaded because running scripts is disabled on this system` | That terminal is PowerShell, which blocks the activation script. Use cmd as in step 2, or allow your own scripts once with `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` and activate again. |
| `error: externally-managed-environment` | Your system's Python (Ubuntu 23.04+, Debian 12+, Homebrew) installs packages only into a virtual environment: make and activate one as in step 3 (if `python3 -m venv` says ensurepip is not available: `sudo apt install python3-venv`). |
| `No module named 'numpy'` | The virtual environment isn't active in this terminal: in the `FruitFly` folder run `.venv\Scripts\activate` (macOS / Linux: `. .venv/bin/activate`), or install NumPy as in step 3 if you haven't. |
| Download fails with a certificate error (macOS) | Run "Install Certificates.command" in your Python folder in Applications. |
| Download blocked by a firewall | Download [the file](https://raw.githubusercontent.com/blendi-remade/fly-brain-minecraft/6cfa30175003ef25da68a237d5eda958f8047b82/src/main/resources/connectome/malecns-v1.0.flyb.gz) in your browser and put it in `data/` as it is (named `malecns-v1.0.flyb.gz`, not unpacked); the error message gives the exact path. |
| "Could not find a free port" | Run the same command again with `--port 9000` added (the message names the ports it tried; if 9000 was among them, any other number from 1024 to 65535) |
| `--backend cupy` stops with "the cupy backend needs ..." | CuPy is not installed in this virtual environment, or no NVIDIA GPU (or driver) is visible: install it as in "The GPU brain" above, or leave out `--backend` (the CPU gives the same spikes). On Windows, WSL2 works too when the Windows NVIDIA driver is current. |
| The game says it's running below real time | Your computer is simulating 176k neurons slower than real time; the fly's world slows down to keep up. First make sure numba is installed (`py -m pip install numba`; the terminal says "Brain integrator: compiled (numba)" at start-up): with it, a 4-core laptop-class machine manages about 1.5x real time with a busy brain, without it about 0.7x. Then close other programs, or start it with `py fly_game.py --fast` (a 1 ms time step, about twice as fast again; every classic experiment still passes). With `--body physics` about 0.1x is normal, and about 0.08x with a partner (two bodies in one world): the physics body (MuJoCo) sets that pace, not your computer (`docs/SCIENCE.md` sections 6.7 and 13). |
| The 3-D brain map goes dark while its yaw counter keeps ticking | Your browser took the graphics (WebGL) context away, for instance after a GPU driver reset, sleep and resume, or too many WebGL tabs (Firefox drops the least recently used one past 16). The page now asks for it back and redraws the map when it returns, and says "graphics reset, restoring…" in the map meanwhile; if it says to reload, reload the tab. A flat map with the note that WebGL is unavailable means the browser refused WebGL altogether (check its graphics settings). |

## 3. How it works (the whole idea)

```
  things in the dish ──(senses: hand-built)──> sensory neurons
                                                     │
                                          the connectome: 176,422 neurons,
                                          6.3 million connections (nobody designed this part)
                                          + the mushroom body's learning rule
                                                     │
  the fly moves <──(body: hand-built)── descending neurons ("command" cables from brain to body)
```

1. **The wiring diagram.** For every pair of connected neurons, the connectome says how many synapses
   link them. This kit keeps the 6.3 million connections with 5 or more synapses (90 million synapses).
2. **Every neuron is the same simple unit.** Its voltage leaks back toward rest, jumps up or down when
   an input neuron fires, and when it crosses a threshold it fires a spike and resets ("leaky
   integrate-and-fire"). A spike from a neuron that uses acetylcholine pushes its targets up; one
   using GABA or glutamate pushes them down. The kick is proportional to the synapse count. These
   are the exact equations and parameters of Shiu et al. 2024 (0.275 mV per synapse, 20 ms leak,
   1.8 ms delay), with a gain of 0.65 because the male connectome has more synapses per neuron.
3. **Senses.** To make the fly taste sugar, the program makes the real sugar-sensing neuron types
   (`LB3b`, `LB3c`, ...) fire at random at about 120 spikes per second, as the paper does. To make it
   see, it renders two compound eyes and drives the real motion detectors and feature detectors
   from the images. To make it smell, it samples the plume at the antennae and drives the receptor
   neurons of the odour's glomeruli.
4. **Actions.** The program listens to descending neurons, the ~1,300 neurons that carry commands
   from the brain to the body, and turns their firing into movement: `MN9` extends the proboscis,
   a burst from `DNp01` (the giant fibre) triggers an escape jump, `DNa02` left vs right steers, `DNp15` carries
   the optomotor reflex, `MDN` walks backward, `pIP10` sings, and so on.
5. **Learning.** Every connection from a Kenyon cell onto a mushroom body output neuron (33,496 of
   them, carrying 402,850 synapses; one learned weight each) weakens when the Kenyon cell was active
   shortly before dopamine arrived in that MBON's compartment. Punishment dopamine (PPL1) waters the
   approach-promoting MBONs, reward dopamine (PAM) the avoidance-promoting ones, so odour + punishment
   makes the fly avoid the odour and odour + reward makes it approach. Which dopamine neurons gate
   which MBON is read from the wiring.

With no input, the brain is completely silent: every spike you see traces back to something the fly
sensed, something you zapped, or the faint background noise if you switch it on.

## 4. What it does, and how it was checked

`py fly_brain.py` runs the classic experiments and compares them with published results. These are
the numbers from this kit, every neuron simulated, nothing tuned for these tests (seed 0; the
"pure" profile is the paper's model, the "game" profile is what the game runs):

| Experiment | Neuron listened to | pure | game | Expected |
|---|---|---|---|---|
| No input | the whole brain | 0 | 0 | silence |
| Sugar on the mouthparts | MN9, proboscis motor neuron | 69 Hz | 50 Hz | 30-90 Hz |
| Bitter taste | Scapula (bitter relay) / MN9 | 287 / 0 Hz | 222 / 0 Hz | relay fires, MN9 silent |
| Sugar and bitter together | MN9 | 0 Hz | 0 Hz | bitter wins |
| Something looming on the right | DNp01 giant fibre / TTMn jump motor neuron | 343 / 68 Hz | 295 / 60 Hz | 250-400 / 40-100 Hz |
| Dust on the antennae | aDN1 / aDN2 grooming neurons (`DNg62` / `DNge078`) | 192 / 139 Hz | 142 / 105 Hz | 100-260 / 80-200 Hz |
| 1 s after bitter or dust stops | the whole brain | runaway loop | calm after bitter; a small loop after dust | calm |

A readout passes when its mean over five seeds is in range, allowing max(1 Hz, 15 %) above the top
(`docs/SCIENCE.md` section 2); `fly_brain.py` writes that margin after the range, as in `0-5(+1) Hz`,
whenever a mean or a seed needed it.

Scanning hundreds of sensory cell types on the real connectome (the experiments are in
`docs/SCIENCE.md`) found what else the wiring supports, and what it does not:

- **Vision.** Driving the connectome's own T4/T5 motion detectors, column by column from the
  retina, gives a direction-selective optomotor reflex: front-to-back motion on the right eye makes
  the right HS cells fire, and through them `DNp15` and `DNa02` on the right, so the fly turns with
  a rotating striped drum. The same input reaches the looming detector `LPLC2` only weakly and
  `LC10a` (small objects) not at all, so those are computed from the retinal image and injected.
- **Smell and learning.** Once the antennal lobe is calm, an odour that excites four or five
  glomeruli activates 7-9 % of Kenyon cells, the same cells every time and different cells for
  different odours (overlap 0.00-0.02 between odours with no shared glomerulus, 0.9 across random
  seeds). Halving the Kenyon-cell connections onto the punishment-side MBONs cuts their odour response
  (MBON14 38 → 6 Hz for the "Smell of vinegar" test mixture, four of the game's five vinegar glomeruli,
  and 44 → 9 Hz for the game's own vinegar; game profile, the mean of five seeds), and the game's other
  odours hardly reach MBON14 to begin with (0-2 Hz; `docs/SCIENCE.md` section 4.6). Bitter taste fires the
  PPL1 punishment dopamine neurons (PPL101 at about 80 Hz); sugar never reaches the PAM reward neurons in
  this model, so eating sugar drives them directly (all but PAM-γ3, which sugar suppresses in real
  flies), and the game says so.
- **Courtship.** `pC1` at 60 Hz drives `pIP10` at 80 Hz and the wing motor neurons of song. The
  tarsal taste neurons that should carry the female's pheromone to `pC1` are about eight times too
  weak in this model, so tapping the female fires them (wiring) *and* drives `pC1` directly
  (hand-built, labelled).
- **Hearing and wind.** Johnston's organ B neurons at 100 Hz drive the giant fibre at 65 Hz: a
  clap makes the fly jump. The wind-sensing C/E neurons drive grooming and backing at rates above
  ~30 Hz and no steering neuron at any rate, so wind is kept weak and heading upwind is hand-built.
- **Brakes.** The paper's model locks into runaway firing after bitter, dust or any odour. Mild
  fatigue plus blocking the output of the 420 antennal-lobe local neurons (many are non-spiking in
  real flies) ends it while keeping every readout in range. Textbook short-term synaptic depression
  starves the calibrated sensory drive instead, so it is offered only as the `brakes` profile.

## 5. Things to try

**Make room for the fly.** The **Panels** menu in the header hides the side panels altogether
(keyboard `H`: the dish takes the whole width, and the toolbar rows stop wrapping so it grows
taller too), or ticks exactly the panels you want. Every panel can be dragged by its title, with
the mouse or a finger: up or down to reorder the sidebar, or out of the sidebar to float it
anywhere on the screen (hover a title for its buttons: ⧉ pops it out over the dish, ⇤ docks it
again, × hides it; ▲ ▼ in the menu reorder by keyboard). The arrangement is remembered by your
browser; "Reset the layout" puts everything back. Zoom is what uses the extra width: the mouse
wheel over the dish, the 🔍 button or `+` / `−` zoom in on the fly (the view follows it).

**In the game** there is a checklist: feed it, offer bitter food, lure it, scare it, dust it, watch
it bump a wall, drop an odour, teach it, add a female, turn on the wind, clap, spin the drum, zap
MDN, silence MN9 (the checklist stays when you ask for a new fly). A fed fly eats in bouts of a few
seconds: under steady sugar MN9 tires, the proboscis goes in, and it starts again only now and then
(`docs/SCIENCE.md` 6.5). The **scenarios** run whole protocols for you: appetitive conditioning (odour +
sugar, then a preference test), aversive conditioning (odour + shock), courtship, following a
plume upwind, and three hand swoops. The **Neuron lab** zaps, silences or scales any cell type by
name and adds it to the readouts; the **Pathway explorer** asks the wiring how one population
reaches another and highlights the route in the 3-D brain map, with a one-click lesion of each
relay. The **Learning** panel shows every MBON's remaining synaptic strength and the learned bias
for the odour being smelled. **Record** saves the session (and, optionally, every spike).

**Switch to the female fly.** `py fly_game.py --female` and `py fly_brain.py --female` run the same
kit on FlyWire, the whole female brain the published model was built on (Dorkenwald et al. 2024), with
the published model's wiring: every connection, and 0.275 mV per synapse. Each neuron's sign (excitatory
or inhibitory) comes from FlyWire's current transmitter prediction, which differs from the published
model's own table on 1.2 % of connections, mostly uncertain calls in the optic lobe; it matches the
literature better, and the model's signs change no result (`docs/SCIENCE.md` section 9.1). The experiments and senses
find her cells under the male names (`MN9` is FlyWire's `CB0701`, and so on; `--find` marks those names as aliases). Cells she doesn't have
come out as n/a, never as 0 Hz: she has no nerve cord, and no male-specific cells such as pIP10. Sugar
drives her MN9 and, in the published model's profile (`fly_brain.py --female`), bitter wins over it, as
in the paper; in the game profile MN9 still fires about 7 Hz with both (13 Hz with the parts list on),
against 72 Hz with sugar alone. The parts list, the physics body and the
background re-test run on her too; `docs/SCIENCE.md` section 9.5 compares each with the male. Most readouts differ from the male's, and
`docs/SCIENCE.md` section 9 says why most of those differences are not yet sex differences.

**Two simulated flies.** `py fly_game.py --partner female` puts the male and FlyWire's female in one dish, each brain in its own process (2.7-2.9x real time in two runs on a 16-core laptop, `docs/SCIENCE.md` 10.2; 3.6x with `--backend cupy` on its GPU, section 11.3; `--fast` if yours is slower). Nothing links the two brains but the world: she sees him as a small dark thing, hears his song through her Johnston's organ (at up to 70 Hz on her sound cells, the loudest steady drive that does not startle *him*), tastes him when a foreleg lands, and the two bodies bump. `--social seen,song` keeps only those channels; `--partner male` gives him a male rival; `--female --partner male` gives her a male. A fly menu in the page's header picks which fly the panels, the retina and the brain map follow, and the checklist gains pair items (he saw her, sang, tapped; she heard, saw him, was tapped); the Scenarios card gains "Courtship, two brains", 90 s of both flies with the numbers logged at the end. Her decision neurons (`DNp37`, the vaginal plate opening command; `DNp13`, ovipositor extrusion; `vpoEN`, `pC2l`, `SAG`) are shown as watches, never as a verdict: in this data his song reaches her hearing and her giant fibre but not those neurons (`docs/SCIENCE.md` 10.3). `py fly_brain.py --female --pair-experiments` runs the pair experiments, whose ranges are provisional and measured, not validated.

**The dish in 3-D.** The 🧊 3-D button beside the zoom (or `D`) shows the dish as a three.js scene with both flies as
NeuroMechFly's meshes; right-drag orbits the camera, the wheel zooms, and the camera menu follows the fly in focus or looks
from the side. It is an animation, not physics: the legs replay NeuroMechFly's recorded stride at the drawn body's gait phase,
both flies wear the female body model, and the flies are drawn at about three times real size, as the badge on the canvas
and "What's real here?" say (`docs/SCIENCE.md` section 12). Nothing of it loads until the button is pressed; without WebGL2
the page stays in 2-D and says so.

**Two physics flies.** `py fly_game.py --partner female --body physics` puts both flies into one MuJoCo world as NeuroMechFly
bodies, each driven by its own brain, able to touch each other: the tap is a physical contact with its force, both flies are
drawn at real size, and the pair runs at about half real time on a laptop since v3.0 (flygym 2.1; a tenth before; the page
says so).
The single physics fly is the same body (`docs/SCIENCE.md` section 13). The page's "Save replay" switch writes the run to
`recordings/`, and `py tools/render_replay.py recordings/<id>` turns a physics replay into a 1080p MP4 at real speed with MuJoCo's
own renderer (`--camera overhead`, `follow` or `side`; section 13.4). `--physics-levers LIST` switches on the measured speed levers
of section 13.5 (on flygym 2.1 the model already has what the adopted ones asked for, so none is on by default).

**In code**, start with `my_first_fly.py`: poke, wait, listen, in three lines. Then:

| Command (macOS / Linux: `python3` instead of `py`) | What it does |
|---|---|
| `py fly_brain.py --find LC10` | Search cell types by name |
| `py fly_brain.py --stim "MDN:60" --watch "MDN,DNp09"` | Zap a type, listen to others |
| `py fly_brain.py --stim "LC4/R,LPLC2/R:150"` | No --watch: shows the most active types |
| `py fly_brain.py --trace LC10a/L DNa02/L` | The strongest wiring routes, with signs |
| `py fly_brain.py --inputs MN9 --outputs GNG232` | Strongest partners of a population |
| `py fly_brain.py --sweep "LB3b,LB3c:0:200:9" --watch MN9` | A dose-response curve |
| `py fly_brain.py --lesion Sugar --readout MN9` | Which relays does sugar → MN9 need? |
| `py fly_brain.py --profile game --json out.json` | Five seeds each (the default): mean ± sd, saved |
| `py fly_brain.py --silence GNG087 --only bitter` | Knock out the bitter relay |
| `py fly_brain.py --stim "prefix:JO-B:100" --record spikes.npz` | Every spike, with neuPrint IDs |
| `py fly_game.py --partner female` | Two simulated brains in one dish (the male and FlyWire's female) |
| `py fly_game.py --partner female --body physics` | The same pair as two NeuroMechFly bodies in one MuJoCo world, able to touch (about half real time) |
| `py fly_brain.py --fly banc` | A third connectome: BANC, a female with a whole ventral nerve cord (built on first use from its public deposit, `docs/SCIENCE.md` section 14) |
| `py tools/render_replay.py recordings/<id> --camera follow` | A saved physics replay as a 1080p MP4 at real speed, rendered by MuJoCo (overhead, follow or side camera) |
| `py fly_brain.py --female --pair-experiments` | Her song, pC1, pC2l, cVA and SAG routes, measured (provisional ranges) |
| `py fly_game.py --pure` | The paper's model, seizures and all |
| `py fly_game.py --noise 5:15` | Spontaneous activity (parts list off; docs/SCIENCE.md 3.4) |

```python
from virtual_fly import load_connectome, trace
from virtual_fly.settings import build_brain

brain = build_brain(load_connectome(), "game")          # what the game runs, plasticity included
for path in trace(brain.conn, "LC10a/L", "DNa02/L"):    # ask the wiring diagram
    print(path.describe())
brain.stimulate("ORN_DM1,ORN_DM4,ORN_VM7d,ORN_DP1m", 80) # the smell of vinegar ...
brain.stimulate("prefix:PPL1", 80)                       # ... paired with punishment
brain.run(2000)
print(brain.plasticity.summary()["MBON11"])              # its Kenyon-cell synapses are weaker now
```

Every neuron keeps its official ID, so you can look anything up at
[neuPrint](https://neuprint.janelia.org/?dataset=male-cns%3Av1.0) (dataset `male-cns:v1.0`); the
game's brain map links straight to it.

**From another program.** While `fly_game.py` runs it serves the fly as JSON: `GET /api/state` (or
the `/api/stream` event stream) returns the fly's position, heading, behaviour, senses, neuron
rates and learning state, and `POST /api/action` accepts commands such as
`{"type": "zap", "spec": "MDN", "hz": 60}`, `{"type": "drop", "kind": "vinegar", "x": 10, "y": 5, "food": "sugar"}`
or `{"type": "stripes", "count": 16, "drum_speed": 1.5}`; a command it cannot carry out gets
`{"ok": false, "error": ...}` back. `docs/API.md` has the whole contract; anything that can make HTTP
requests (a game engine, a notebook, a robot) can drive a fly from it. The server listens on this
computer only unless you start it with `--host 0.0.0.0`, and then anyone on your network can drive the fly.

**Genetics.** The Genetics card lists the neurons annotated as expressing *fruitless* (4,858) and
*doublesex* (412), the male-specific and sexually dimorphic ones, and the transmitter genes behind
every neuron's sign, each linked to its FlyBase report. Silence the fruitless neurons, then add a
female: no chase and no song, as in *fruitless* mutants, while feeding and escape work as before
(`python fly_brain.py --profile game --only genetic` runs the five genetic experiments). Type a
published driver line such as `SS02385` and the kit asks Janelia's NeuronBridge which of these
neurons it labels, so a real line can be zapped or silenced here; or ask which lines label a
population. `python fly_brain.py --genes`, `--lines pIP10` and `--driver MB112C` do the same
from the terminal. The selectors are `gene:fru`, `gene:dsx`, `gene:both`, `gene:VGlut` and so on,
and `dimorphism:male` / `dimorphism:dimorphic`.

**The genome as a recipe.** The Genome card grows a new fly from this connectome's cell-type
wiring rules (which types connect, how often, how strongly) with every neuron-to-neuron
connection drawn afresh, then runs the eleven validated experiments on it and lists which
reflexes survive. Nine of eleven do; a fly grown from class-level rules keeps none (only the two
no-response controls still pass), and the bottleneck levels squeeze the type rules through a
low-rank code. Change the seed for another individual, and "Real wiring" brings the original back.
`python fly_brain.py --profile game --genome-sweep` prints the same table from the terminal (the
default pure profile runs only the six classic experiments), `--grow type` runs any experiment on a
grown fly, and `python fly_game.py --grow type` starts the game with one. The science and the numbers are in
`docs/SCIENCE.md`, section 7.

**The genes as a parts list.** The published model gives every neuron the same machine; the
"Parts list" switch on the Genome card gives each the one its genes make. Dopamine, octopamine and
serotonin have no fast receptors in the fly, so their neurons leave a *tone* on their targets that
lingers for seconds and raises how strongly those targets respond to everything else (three gauges
show the tones; a loud sound, for instance, raises the octopamine tone that sharpens the motion
cells), and those that release no fast transmitter as well stop making fast synaptic potentials. The
connectome's own prediction names 979 such neurons; with the literature's transmitters (the default,
see "What the literature says" below) the Genome card counts 2,146, of which 976 lose their fast
synapses and 1,170 (1,151 of them Mi15 cells) release a fast transmitter as well and keep them.
Photoreceptors, the lamina cells, the medulla inputs to T4/T5, T4/T5 and the HS/VS cells do not
spike in real flies, so here they transmit graded signals below the spike threshold. APL, the mushroom body's inhibitory
feedback neuron, releases locally: onto the Kenyon cells and output neurons of a lobe that is
quieter than the rest it releases less, as in the real fly (Amin et al. 2020), and dopamine turns
it down through its Dop2R receptor. A tone acts only through receptors the kit has evidence for
(the target's single-cell atlas cluster, or a fact from the literature such as octopamine sharpening
the VS motion cells, of which the octopamine neurons reach one in this wiring); a target with neither
feels none. That rule closed a leak of song past the
silenced fruitless neurons (`python fly_brain.py --profile game --one-sign-rule` brings back the old rule, under which
every tone raised every target's gain; the game always uses the new one). The reflexes are re-tested on
the switch (the eleven the Genome card lists; all 16 validated experiments pass in `fly_brain.py
--profile game --parts`, none of them fragile; `python fly_brain.py --profile game --global-apl` puts APL back to one cell releasing
the same everywhere). Every
re-test runs each experiment five times on a fly with nothing learned carried over between runs, in a
separate low-priority process so the game keeps its speed, and a reflex that passes on average but
misses on some run gets an amber mark ("fragile"). `python fly_brain.py --profile game --parts` runs any experiment
that way, `--part "class:Kenyon_Cell:theta=10"` overrides a type's threshold, and
`python fly_game.py --parts` starts the game with the parts on. The parts cost about half as much
brain time again, so under heavy stimulation the game runs at 0.8-0.9 of real time on a laptop with
the compiled integrator; `--fast` restores it. With the parts on, the header's brain counter says
events/s: the graded cells' release quanta count with the spikes (hover it for the split). Section 8
of `docs/SCIENCE.md` has the tables.

**What the literature says (Virtual Fly Brain).** Each cell type is joined to its class in the
FlyBase anatomy ontology, so `fbbt:lobula columnar neuron`, `fbbt:adult descending neuron` or
`fbbt:dopaminergic neuron` name a population by what it *is* (the Neuron lab has a search box for
the classes), and clicking a neuron on the brain map now says what its type is: the definition, the
anatomical parents (each a click away as a population), the lineage, the peptides, the transmitter
the literature has established and a link to Virtual Fly Brain. `rx:Dop2R` names the types whose
adult single-cell cluster expresses a receptor. With the parts list on, the literature's word wins
over the prediction where the parts model cares (Mi15 gains a dopamine tone, the DPM neuron is
GABA + serotonin, "unclear" predictions with a curated transmitter get it), and the tone's sign on
each target follows the receptors its type expresses (Gi-coupled ones lower the gain). The Genetics
card lists where the literature and the prediction disagree. `python fly_brain.py --profile game --curated all`
lets the literature win over confident fast predictions too (their signs flip, and types it calls
purely modulatory lose their fast synapses), and `python fly_game.py --curated all` makes the
Genome card's switch use that policy; section 8.1 of `docs/SCIENCE.md` has the numbers and the
survival table.

## 6. Honest limitations

These are the things the critics point at, so it's worth knowing them:

- **Every neuron is identical** unless the parts list is on, and even then only three
  transmitters' slow action, five cell-type groups' graded signalling and a threshold table
  separate them. Real neurons differ in size, threshold, timing and chemistry. The absolute
  firing rates shouldn't be trusted, only which neurons respond. (`--jitter` adds threshold
  heterogeneity if you want to see how fragile the numbers are.)
- **Runaway loops.** In the paper's pure model, bitter taste, dust and smells set off a seizure in
  the antennal lobe that never stops. The game's fixes are documented above; `--pure` shows the
  model without them. A small loop between `DNg33` and a few serotonin neurons can still keep
  firing after strong stimuli; it doesn't move the body.
- **Dopamine is treated as a slow modulator.** The data label dopamine neurons excitatory; in the
  game their spikes gate plasticity but their fast synapses are muted, otherwise bitter taste would
  drive the MBONs directly. With the parts list on, octopamine and serotonin neurons are treated
  the same way and all three leave a slow tone; its sign on a target follows the receptors the
  target's cell type expresses only where an adult single-cell cluster exists (mostly the mushroom
  body and the optic lobe) or the literature has measured it; everywhere else a tone does nothing.
- **The mushroom body's inhibition hangs on two neurons.** APL and DPM are modelled as spiking
  points that inhibit each other, and whichever wins sets the inhibition of the whole mushroom
  body. With the parts list on, DPM wins during an odour, and about twice as many Kenyon cells
  respond as real flies use (about 15 % against 5-10 %). Sections 8.2 and 8.6 of `docs/SCIENCE.md`
  have the details; giving the cells their measured resting rates does not fix it.
- **The brain doesn't always settle.** With the parts list on, the graded optic-lobe cells can keep
  releasing after a strong stimulus (the model's graded cells release nothing at rest and never
  adapt), and over a long quiet session the brain drifts into a busy state, with the occasional
  escape jump. Section 3.5 of `docs/SCIENCE.md` traces it.
- **No spontaneous activity**, unless you switch on the (hand-built) background noise. The
  "walking urge", hunger, thirst and odour-guided steering are hand-built and can be switched off.
- **Vision is computed, not grown.** The retina, the feature detectors and the correlator are our
  code; only the T4/T5 columns onward are the fly's. The photoreceptor-to-motion-detector
  circuit (L1/L2, Mi1, Tm3...) is in the data but has no resting activity to modulate in this model.
- **The odour code is odd in places.** Kenyon-cell subtypes are recruited unlike real flies (γ-main
  cells hardly at all), single glomeruli barely reach the mushroom body, and an odour leaves the
  central-complex heading circuit ringing for a second or two after it stops.
- **The body is a drawing** unless you ask for the optional physics body (`--body physics`, Python 3.12-3.14
  only: NeuroMechFly v2 legs in MuJoCo through flygym 2.1, at real time for one fly; docs/SCIENCE.md section 6.7).
  The drawn body's speeds and turn rates are chosen by hand.
  The decoder's weights are hand-chosen too, but it measures and shows which motor pools each
  descending neuron reaches in the wiring.
- **No hormones, no electrical synapses, no development,** one fly's brain, one seed unless you ask
  for more. Nothing here is conscious. It is a wiring diagram with the simplest possible physics,
  and it still does a surprising number of fly things.
- **Two flies court through hand-built senses.** With `--partner female` both brains are real, but every
  channel between them (how far a song carries, how loud it is, what a touch fires, how the bodies bump) is
  a labelled encoder, and in this data his song does not reach her song-tuned neurons at all
  (`docs/SCIENCE.md` 10.3), so what she does next to him comes mostly from her hand-built walking urge.
  The pair experiments' ranges are measured, not validated.

## 7. Where to go next

- **Add a sense or a behaviour.** Find the neurons (with `--find`, `--stim`, `--trace` or on
  neuPrint), add an encoder in `virtual_fly/senses/`, a readout in `game.py`'s `READOUTS`, and a
  line in the decoder. Scanning inputs and watching `DNa02` is exactly how the lure was found;
  scanning T4/T5 columns is how the optomotor reflex was found.
- **A real body:** [FlyGym / NeuroMechFly](https://github.com/NeLy-EPFL/flygym) and
  [flybody](https://github.com/TuragaLab/flybody) are physics-simulated fly bodies (MuJoCo).
- **Real vision:** [flyvis](https://github.com/TuragaLab/flyvis) has connectome-based models of the
  fly's visual system that compute motion from photoreceptors up.
- **More projects:** [awesome-fly](https://github.com/cobanov/awesome-fly) lists dozens; the
  explainer ["Deconstructing viral fly sims"](https://www.neuroai.science/p/are-flies-playing-beat-saber)
  is the best overview of what works and what doesn't.

## 8. Credits and data licence

- **Connectome:** Berg S, Beckett IR, Costa M, Schlegel P, Januszewski M, et al. *Sexual dimorphism in
  the complete Drosophila male central nervous system connectome.* Cell 189(18):5504-5526 (2026),
  [doi:10.1016/j.cell.2026.08.015](https://doi.org/10.1016/j.cell.2026.08.015). HHMI Janelia FlyEM,
  University of Cambridge / MRC LMB, Google Research. Licensed
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Project site:
  [male-cns.janelia.org](https://male-cns.janelia.org/).
- **The female fly:** FlyWire connectome, release 783: Dorkenwald S et al. *Neuronal wiring diagram of
  an adult brain.* Nature 634:124-138 (2024), [doi:10.1038/s41586-024-07558-y](https://doi.org/10.1038/s41586-024-07558-y);
  annotations Schlegel P et al., Nature 634:139-152 (2024), [doi:10.1038/s41586-024-07686-5](https://doi.org/10.1038/s41586-024-07686-5),
  extended with Berg et al. ([flyconnectome/flywire_annotations](https://github.com/flyconnectome/flywire_annotations));
  connectivity table from the published model's repository ([philshiu/Drosophila_brain_model](https://github.com/philshiu/Drosophila_brain_model), MIT).
  Both files are fetched from their sources on your machine (pinned, checked by SHA-256) and are not
  redistributed here; see each source for its terms.
- **Neuron model:** Shiu PK, et al. *A Drosophila computational brain model reveals sensorimotor
  processing.* Nature 634:210-219 (2024), [doi:10.1038/s41586-024-07763-9](https://doi.org/10.1038/s41586-024-07763-9).
- **Learning rule:** Aso Y et al., eLife 2014 (MBON valence, compartments); Hige T et al., Neuron
  2015 and Handler A et al., Cell 2019 (dopamine-gated depression). **Vision:** Klapoetke NC et al.,
  Nature 2017 (LPLC2); Ache JM et al., Neuron 2019 (LC4); Ribeiro IMA et al., Cell 2018 (LC10a);
  Maisak MS et al., Nature 2013 (T4/T5 directions); Kim AJ, Fitzgerald JK, Maimon G, Nat Neurosci
  2015 (efference copy). **Other senses:** Hampel S et al., eLife 2015 (grooming); Suver MP et al.,
  Neuron 2019 (wind); Nagel KI, Wilson RI, Nat Neurosci 2011 (olfactory adaptation). Full list in
  `docs/SCIENCE.md`.
- **Data file and calibration:** the compact connectome file (connections with 5+ synapses, fetched
  from neuPrint), the gain of 0.65, the Kenyon-cell input scaling and many of the sensory and motor
  neuron choices come from [fly-brain-minecraft](https://github.com/blendi-remade/fly-brain-minecraft)
  by blendi-remade (code MIT, data CC BY 4.0). The download is pinned to one version and checked
  with a SHA-256 hash.
- **Anatomy ontology and Virtual Fly Brain:** the FlyBase anatomy ontology (FBbt; Costa M et al.,
  J Biomed Semantics 2013), release 2026-07-09, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/),
  and Virtual Fly Brain (Court R et al., Front Physiol 2023; [virtualflybrain.org](https://virtualflybrain.org)),
  whose MaleCNS name synonyms (Berg et al. 2025) and single-cell RNA-seq expression tables (Fly Cell
  Atlas, Li H et al., Science 2022; Davie K et al., Cell 2018; and the other data sets named in
  `data/vfb_receptors.json.gz`, all CC BY 4.0) were read once through the VFB connector and shipped
  as the files in `data/`.
- **The 3-D view:** [three.js](https://threejs.org) 0.186.1 (MIT, copyright 2010-2026 three.js authors), vendored under
  `virtual_fly/web/vendor/three/` with its licence and the hashes of every file (`VERSION.txt`), loaded only when the 3-D view
  is switched on. The fly meshes are NeuroMechFly v2's (Wang-Chen S, Stimpfling VA, Lam TKC, Özdil PG, Genoud L, Hurtak F,
  Ramdya P. *NeuroMechFly v2: simulating embodied sensorimotor control in adult Drosophila.* Nature Methods 21:2353-2362 (2024),
  [doi:10.1038/s41592-024-02497-y](https://doi.org/10.1038/s41592-024-02497-y); [NeLy-EPFL/flygym](https://github.com/NeLy-EPFL/flygym),
  Apache-2.0), converted to glTF and decimated for the browser by `tools/build_fly_model.py`, shipped under
  `virtual_fly/web/models/` with the licence text (`LICENSE-NeuroMechFly.txt`) and a notice of the changes (`NOTICE-NeuroMechFly.txt`).
- **This kit's code** is yours to use and change however you like.
