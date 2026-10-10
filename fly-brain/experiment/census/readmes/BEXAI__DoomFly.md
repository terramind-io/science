# DoomFly — a fly brain double-doomscrolls an iPhone Duo

A 50 s vertical (1080 × 1920, 60 fps) video in which a simulated fruit-fly brain — the complete
**MaleCNS v1.0 connectome** (166,700 neurons, 6.24 M connections) running as a
leaky-integrate-and-fire spiking network — sits on an open foldable phone mock-up and
scrolls two feeds at once: **left eye → left panel, right eye → right panel; front-left leg
swipes the left feed, front-right leg swipes the right feed**. A picture-in-picture shows
the real neurons firing.

Nothing in the video is scripted. Every swipe is emitted by a fixed, unfitted rule over the
spikes of real MaleCNS neurons: *a swipe happens when the descending-neuron population bursts,
and it goes to the side whose medulla saw the change.* What is chosen by hand, and what is
not, is stated in [§6](#6-what-is-and-is-not-learned-or-fitted).

Deliverables: the video `out/final.mp4` and its sources `out/events_final_v2.jsonl` +
`out/spikes_final_v2.npz` are **generated locally** by the commands in §8 (media and logs are
git-ignored; the video was shared directly). The repository carries the code, this README and
`docs/`: verified data notes, every test result as JSON, the episode statistics, and figures.

---

## 1. Pipeline

```
data/raw/*.feather ──► src/build_graph.py ──► data/graph/{W.npz, ids.npy, sets.json, eye_map.npz, positions.npy, groups.npy}
                                                        │
 src/feeds.py  (two synthetic feeds, 1335×1878 each,    │
                autoplaying cards)                       ▼
      │ luminance grid per panel (24×18)        src/sim.py  (LIF, dt = 2 ms, scipy CSC, STD)
      ▼                                                 │
 src/encoder.py  (retinotopic L1/L2 Poisson drive) ──►  brain.step() ×8 = one 16 ms control step
                                                        │ spike counts: DNs, medulla L/R, leg MNs
                                                        ▼
                                                src/decoder.py  (burst rule → swipe L / R)
                                                        │ feed.swipe()
                                                        ▼
 src/run_episode.py  logs out/events_<tag>.jsonl + out/spikes_<tag>.npz  ──►  src/render.py  ──►  out/final.mp4
 src/validate.py     Tests A–C (Shiu benchmark, runaway, wiring shuffle)
 src/analyze_episode.py  swipe statistics + figure for any episode;  src/side_eval.py  open-loop side test
```

Everything ran offline on 4 CPU cores / 15 GB RAM, no GPU. A 50 s episode simulates in
60–80 s (19–26 ms per 16 ms control step, depending on activity) and renders in ~140 s (22 fps).

## 2. Data

MaleCNS v1.0 flat connectome (CC-BY 4.0), three files, ~1.1 GB
(`src/download.py`, bucket `gs://flyem-male-cns/v1.0/connectome-data/flat-connectome/`):

| file | used for |
|---|---|
| `body-annotations-male-cns-v1.0-minconf-0.5.feather` | bodyId, type, superclass, class, subclass, somaSide / rootSide, somaNeuromere, `assignedOlHex1/2` (optic-lobe column coordinates), `somaLocation` |
| `body-neurotransmitters-male-cns-v1.0.feather` | `consensus_nt` per body (synister predictions, Eckstein, Bates et al. 2024) |
| `connectome-weights-male-cns-v1.0-minconf-0.5.feather` | 151.9 M `body_pre, body_post, weight` rows |

Column-level notes with printed value counts: `docs/RESEARCH_DATA.md`.
Reference-implementation notes (Shiu constants, sign conventions, licences): `docs/RESEARCH_REFS.md`.

### Graph build (`src/build_graph.py`)

| choice | value |
|---|---|
| neurons kept | every body with a non-null `superclass` → **166,700** |
| edges kept | synapse count ≥ 5, both ends kept, 33 self-edges dropped → **6,242,085 edges, 89,859,938 synapses** |
| sign | presynaptic `consensus_nt`: ACh, DA, OA, 5-HT → +1; GABA, glutamate (GluCl, Liu & Wilson 2013), histamine → −1; unclear/missing (3,177 cells) → +1 |
| inhibitory edge fraction | **37.2 %** |
| NT counts | ACh 103,720 · Glu 29,302 · GABA 22,069 · His 7,891 · unclear 2,999 · DA 392 · OA 101 · 5-HT 48 · missing 178 |
| side | `somaSide` → `rootSide` (sensory cells) → `instance` suffix `_L/_R` |
| soma positions | `somaLocation` × 8 nm for 139,662 cells; 26,236 more filled by the mean of synaptic partners (4 rounds); 802 unknown |

These match the community builds: hotocoo/malecns reports 166,700 neurons and 6,242,118 edges
(89.86 M synapses); the 33-edge difference is exactly the self-edges dropped here.

### Neuron sets (`data/graph/sets.json`)

| role | selection | L | R |
|---|---|---|---|
| eye input, ON | type `L1` (lamina) with hex column coords | 875 | 892 |
| eye input, OFF | type `L2` | 874 | 893 |
| medulla (side evidence) | types `Mi1`, `Tm1`, `Tm2`, `Tm9`, `L5` — direct targets of L1/L2 | 4,429 | 4,445 |
| optic lobe | superclass `ol_intrinsic` | 44,607 | 44,796 |
| visual projection neurons | superclass `visual_projection` | 4,589 | 4,612 |
| **descending neurons (swipe trigger)** | superclass `descending_neuron` | 656 | 648 (+10 midline) = **1,314** |
| front-leg motor neurons | superclass `vnc_motor` & subclass `fl` (T1) | 68 | 67 |
| all motor neurons | `vnc_motor` + `cb_motor` | 815 | |
| sugar GRNs (proxy) | labellar bristle types `LB3a-d` | 78 | |
| bitter GRNs (proxy) | labellar bristle types `LB1a-e` | 56 | |
| MN9 | type `MN9` (bodyIds 10331 L, 16949 R) | 2 | |
| PAM / PPL1 / KC / MBON | for Phase 2 (unused) | 316 / 16 / 4,064 / 97 | |

Caveats found in the data: the left eye is under-reconstructed (R1–R6 photoreceptors 1,112 L vs
2,265 R; `L3`/`C2`/`Tm4` have column coordinates only on the right), so drive is injected at
**L1/L2 only** (complete on both sides: 1,749 cells left, 1,785 right) and never at photoreceptors
(histamine sign trap) or L3. MaleCNS has **no sugar/bitter GRN label**; the LB3/LB1 split is a
connectivity proxy (strongest two-hop path to MN9), so Test A is reported with that caveat.

## 3. Neuron model (`src/sim.py`)

Shiu et al. (Nature 2024) LIF constants, verified line-by-line against
`philshiu/Drosophila_brain_model` and `hotocoo/malecns` (`docs/RESEARCH_REFS.md` §1):

| constant | value |
|---|---|
| V_rest = V_reset | −52 mV |
| V_threshold | −45 mV |
| refractory | 2.2 ms (→ 1 step at dt = 2 ms; a cell can fire again two steps after a spike, i.e. a 250 Hz ceiling) |
| membrane τ | 20 ms |
| synaptic τ (exponential) | 5 ms |
| synaptic weight | 0.275 mV per synapse, integrated (τ_m/τ_s pre-compensation as hotocoo; the peak PSP of one synapse at dt = 2 ms is ≈ 0.15 mV) |
| synaptic delay | 1.8 ms (→ 1 step) |
| dt / control step | 2 ms / 16 ms (8 substeps) |
| **`weight_scale`** | **0.5**, set by the closed-loop probes with depression (§5.2); Test B without depression recommends 0.4 |
| spike-frequency adaptation | 0.6 mV, τ 120 ms (hotocoo's addition; 0 = pure Shiu) |
| **short-term depression** (Tsodyks–Markram, one resource per presynaptic neuron) | **U = 0.15 per spike, recovery 480 ms** (TheMrRaGe/flybrain measured U = 0.08, τ 480 ms; it must be global). The resource is depleted at spike time and weights delivery one step later, so a rested cell transmits 0.85 of its weight; the effective gain of a first spike is therefore 0.5 × 0.85 ≈ 0.43 |

Sensory input follows Shiu: driven cells are forced to spike as Poisson processes at the
requested rate; everything downstream is the wiring. The step is a sparse column gather on the
CSC matrix (only columns of neurons that spiked are touched): 1–20 ms per 2 ms step on 4 cores.

## 4. Eyes and legs

**Feeds (`src/feeds.py`).** Two deterministic synthetic feeds (seeded card generators, no text
glyphs, no logos, no real posts). Image cards and "novel" high-contrast cards **autoplay**: like
muted clips they cut to a new brightness level about once a second (period and phase fixed per
card, ±80 % for image cards, ±60 % for novel cards). Between cuts the frame is static. This is the
ambient stimulus — a property of the content, not of the brain. A swipe flicks the feed by 0.55
screen heights with an ease-out over 350 ms. The renderer replays the feeds from the seeds and
autoplay parameters recorded in the episode's meta line, so no frames are stored.

**Encoder (`src/encoder.py`).** Each panel → 24 × 18 luminance grid. The ~875 L1 and ~875 L2
columns of each eye carry MaleCNS hex coordinates (`assignedOlHex1/2`); axial → cartesian
(x = h1 − h2/2, y = h2·√3/2 gives an upright 1.15:1 ellipse), PCA-upright, normalised, binned
(≈ 2.5 columns per populated grid cell). Temporal contrast c = (I − I_bg)/(I_bg + 0.05) against a
250 ms adapting background; c > 0 drives that column's **L1** (ON), c < 0 its **L2** (OFF),
rate = clip(6·|c|, 0, 1) × 150 Hz. Static frames go silent within ~1 s; a swipe gives a ~110 Hz burst.

**Decoder (`src/decoder.py`, mode `burst`, no fit).** Two population signals, both real neurons:
1. *Trigger*: an 80 ms trace of the spike rate of all **1,314 descending neurons**. When it exceeds
   **1.5 Hz per cell** (baseline is 0), a swipe is emitted (≥ 400 ms per panel, ≥ 300 ms globally,
   none in the first second).
2. *Side*: an 800 ms trace of the per-cell rate of the **left vs right medulla** (Mi1/Tm1/Tm2/Tm9/L5,
   one synapse downstream of the driven lamina cells). The panel of the more active medulla is swiped.

Two other readouts were built and rejected, and are kept in the code for the record:
`direct` (front-leg motor-neuron pool z-score — the legs fire on every burst but bilaterally, so it
cannot pick a panel) and `ridge` (hotocoo-style linear readout fitted to a teacher — see §5.4).

## 5. Results

All numbers below are printed from `docs/validate_results.json`, `docs/episodes/*.json`,
`docs/probes/*.json` and `docs/ridge_fit_diag.json`. An earlier set of runs drove the right eye's
L3 cells as well (a code default; the left eye has no L3 columns); that asymmetry was found in
audit and removed, and every episode number below is from the corrected L1/L2-only runs.

### 5.1 Test A — Shiu benchmark (sugar → MN9), `src/validate.py`

Tests A–C run **without** short-term depression (it was added after them, for the closed loop);
the depression regime is characterised by the closed-loop probes in §5.2.

78 sugar-proxy GRNs at 150 Hz for 1 s; MN9 rate (Hz per cell) during the drive; baseline 0 Hz.

| weight_scale | sugar | sugar + bitter | bitter | population rate | state |
|---|---|---|---|---|---|
| 1.0 (pure Shiu) | 106.5 | 101.5 | 67.0 | 22 Hz, 24 % of neurons | runaway |
| 0.5 | 186.5 | 76.0 | 114.5 | 13.7 Hz | runaway |
| 0.3 | 147.0 | 89.5 | 23.0 | 8 Hz plateau | latched |
| 0.15 | 107.5 | 0.0 | 0.0 | 2.7 Hz | latched at 3 Hz after drive |
| 0.15 + adapt 0.6 | 13.5 | 0.0 | 0.0 | 0.95 Hz | 0.9 Hz after drive (below the 1 Hz latch criterion) |

Bitter suppresses MN9 at every scale, most cleanly at 0.15 (108 → 0 Hz). Absolute MN9 rates
are physiological only with adaptation. The sugar/bitter sets are proxies (§2), so this is a
consistency check, not a reproduction of Shiu's exact experiment. Figure: `docs/figures/validate_A_mn9.png`.

### 5.2 Test B — runaway, silence, and the operating point

* No input, 1 s: **0 spikes** at every configuration (no noise term).
* Left-eye drive (all 1,770 left L1+L2 cells at 60 Hz, 1.5 s), no depression: population rate
  26 Hz at scale 1.0, 15.6 Hz at 0.5 (both latched, persisting after the drive stops); ≤ 1.2 Hz and
  dying instantly at ≤ 0.4. The cliff is between 0.4 and 0.5. But at ≤ 0.4 **nothing leaves the
  optic lobe** (VPN 0.02 Hz, DN < 0.01 Hz, motor 0).
* Closed-loop probes (8 s, swipes as stimulus; `docs/probes/closed_loop_probes.json`): at 0.2 the
  activity stays in the optic lobe; at 0.25–0.3 the network latches after the first swipe into a
  3–4 Hz self-sustained state in which descending activity is constant (≈ 120 DN spikes per step
  before and after a swipe alike) and input-blind.
* **With global short-term depression** (U = 0.15) at scale 0.5 (+ adapt 0.6): no latch;
  descending neurons are silent between events and burst on each visual onset (62 DN spikes per
  step in the 300 ms after a swipe vs 8 before; 0 in quiet periods). U = 0.08 at 0.5 still latched
  (162 vs 131). This is the operating point used everywhere below. Mean population rate in the
  50 s episodes: 0.33–0.67 Hz; DN rate at swipe 7.9–10.7 Hz per cell vs 0.5–0.9 Hz one second earlier.

Figure: `docs/figures/validate_B_lateral.png`.

### 5.3 Test C — it is the wiring

*Lateralisation under left-eye drive* (`validate.py`, scale 0.4): optic-lobe rate L 2.16 vs R 0.01 Hz,
index +0.99 on the real graph; on the wiring-shuffled graph (same weights and signs, postsynaptic
targets permuted) L 41.6 vs R 46.6 Hz, index −0.06, and the shuffled graph runs away (53 Hz) where the
real one is quiet.

*Open-loop side test* (`src/side_eval.py`; scripted swipes, 15 s left-only then 15 s right-only, the
decoder only logs what it would do; `docs/episodes/side_eval_open_loop.txt`):

| graph | left block | right block | overall |
|---|---|---|---|
| **real wiring** | 10 / 11 | 13 / 13 | **23 / 24 = 96 %** |
| shuffled wiring | 1 / 18 | 13 / 13 | 14 / 31 = 45 % |

*Closed loop on the shuffled graph* (`docs/episodes/episode_v2_shuffled.json`): it still bursts
(35 swipes), but every one of them goes right (0 L / 35 R, posts 0 / 55): the shuffled brain can be
startled but does not know which eye saw the change.

### 5.4 The fitted readout is a negative result

A ridge readout from 2 × 2,129 DN + MN traces (fast 80 ms, slow 800 ms) to a teacher that swiped
each panel at random 1–1.8 s intervals (100 s, 138 teacher swipes, λ chosen on held-out blocks)
reaches held-out correlation **0.02 (L) / 0.06 (R)** (`docs/ridge_fit_diag.json`; run before the L3
fix, not repeated). The descending/motor state does not encode "how long ago was this panel still",
so this readout was dropped rather than tuned.

### 5.5 The episode (`docs/episodes/episode_v2_s1.json`, video)

Six 50 s runs at the operating point, differing only in the Poisson seed:

| seed | swipes | L / R | longest quiet gap | side = eye that saw the onset¹ | DN at swipe vs 1 s before | mean rate |
|---|---|---|---|---|---|---|
| 0 | 27 | 9 / 18 | 5.4 s | 67 % | 8.6 / 0.8 Hz | 0.67 Hz |
| **1 (video)** | **28** | **14 / 14** | **5.2 s** | **96 %** | 7.9 / 0.6 Hz | 0.62 Hz |
| 2 | 27 | 2 / 25 | 6.0 s | 81 % | 9.3 / 0.5 Hz | 0.57 Hz |
| 3 | 17 | 1 / 16 | 11.7 s | 76 % | 10.1 / 0.5 Hz | 0.49 Hz |
| 4 | 9 | 0 / 9 | 28.1 s | 89 % | 8.1 / 0.7 Hz | 0.35 Hz |
| 5 | 9 | 0 / 9 | 33.4 s | 100 % | 10.7 / 0.9 Hz | 0.33 Hz |

¹ fraction of swipes whose panel had the larger eye drive in the preceding 256 ms (ties do not
count); confounded in closed loop because the swipe itself is the strongest onset, hence the
open-loop test in §5.3.

Seed 1 was chosen for the video because it covers both panels evenly with no long pause; the
dynamics are the same in all six (bursts locked to onsets, swipe chains of 2–3 at 0.4 s spacing,
then habituation until the next autoplay cut ignites a burst). Most seeds still favour the right
panel: whichever panel ignites first gets swiped, swipes are the strongest onsets, and the right
optic lobe of this reconstruction ignites bursts more readily. Video episode: 28 swipes (14 L / 14 R),
20 / 23 posts consumed, 5.1 M spikes, 0.62 Hz mean rate, front-leg MNs fire 60 (L) / 40 (R)
spikes in the 0.5 s after a swipe. Figure: `docs/figures/episode_v2_s1.png`.

## 6. What is and is not learned or fitted

- **Not fitted / not scripted:** the wiring (every synapse count and sign is MaleCNS), the neuron
  model, the retinotopic input map (real hex column coordinates), which cells are driven (L1/L2),
  which cells are read (all descending neurons; medulla per side), the swipe rule.
- **Chosen by hand (and reported):** `weight_scale` 0.5, adaptation 0.6 mV, STD U 0.15 / 480 ms,
  encoder gain 6 and 150 Hz cap, DN threshold 1.5 Hz, side-trace 0.8 s, refractory 0.4 s / 0.3 s
  and 1 s warm-up, autoplay amplitude and rate, the seed shown.
- **Fitted:** nothing in the video pipeline. (The ridge readout in §5.4 was fitted and rejected.)
- **Stimulus design:** the feeds autoplay. Without any change on the screens the brain is silent
  (Test B), so the loop needs content that moves, exactly like real feeds.
- **Never claimed:** awareness, intent, or that a fly would do this. It is a static wiring diagram
  driven by LIF dynamics with a fixed population readout.

## 7. Video (`src/render.py`)

Pure OpenCV/numpy compositing at 1080 × 1920, 60 fps (≈ 20 fps render): a dark navy floor with a
glowing perspective grid, the open two-panel device and the fly perched head-up over the hinge.
The device is the photoreal open Duo supplied by the author (`assets/duo_reference.jpg`), turned
into a sprite by `src/build_device_sprite.py`: the screens in the photo are located by RANSAC line
fits to the bezel edges (RMS 0.2–0.4 px), cut out as rounded quads, and the device is stored as a
premultiplied RGBA matte (`assets/duo_sprite.png`) with the two screen quads, the hinge line and
the corner radius in `assets/duo_sprite.json`. At render time the two feed rasters are
perspective-warped into those quads (INTER_AREA shrink, then a homography per screen), so the feeds
sit behind the real bezels with the photo's foreshortening. The screen content of the photo is
never shown: the panels carry only our own synthetic feeds (**no logo, no real UI**).
`--device procedural` restores the flat two-panel mock-up (crease, titanium bevel, drop shadow). The fly is a photoreal render supplied by the author
(`assets/fly_reference.jpg`), turned into a sprite by `src/build_fly_sprite.py`: a soft alpha matte
from the black background that keeps the wings translucent, the front legs removed by inpainting,
and eye / leg anchors recorded in `assets/fly_sprite.json`. The front legs are drawn procedurally
from those anchors with two-bone inverse kinematics, matched to the photo's leg colours and widths,
and the front-left / front-right leg flicks on each swipe. `--fly procedural` restores the earlier
fully procedural 2.5D-shaded fly. The 460 × 460 PiP is a depth-weighted, bloomed point cloud of the 165,898 soma positions
(optic lobes amber, central brain and VNC cool blue, descending neurons green, front-leg MNs
magenta; the volume's x axis is mirrored so the fly's left lobe is on the viewer's left, like the
head-up fly) with a slow ±12° yaw, lit frame-accurately by the spike file. HUD: the
descending-neuron rate per side against its 1.5 Hz threshold, posts consumed L / R, swipes,
spikes/s with a sparkline; title card (0–4 s), stats card (38–46 s), attribution card (46–50 s).
Feed frames are replayed deterministically from the swipe times and meta line in the events log,
in the feed mode the episode was run with (`feed_mode` / `clips_dir` in the meta line).

**Feed modes (`src/feeds.py`).** `cards` (the published results): synthetic post cards with a
1 Hz autoplay hard cut. `reels` (`--feed-mode reels`): a full-screen short-video feed. Each swipe
snaps to the next clip; the clip pool is every `*.mp4` in `assets/clips/` (decoded once to
270 × 480, looped), and the visible frame is a deterministic function of the feed seed, the time
and the swipe count, so the renderer replays exactly what the eyes saw. Ten original 5 s clips
(neon dance, ocean drone, pottery wheel, latte art, skateboard, cat, city time-lapse, an abstract
flash clip flagged as *novel*, a sunset hyperlapse and a puppy) were generated for this repo
with a text-to-video model and are listed with their download URLs in `assets/clips/manifest.json`;
`python3 src/fetch_clips.py` downloads them (they are not committed, ~2 MB each). No third-party
footage is used. Without the clips the reels feed shows moving synthetic placeholders (same
scrolling mechanics, plain colour-field clips), which is what the rendering here used.

## 8. Reproduce

```bash
cd ~/Projects && git clone https://github.com/BEXAI/DoomFly.git && cd DoomFly
python3 -m venv .venv && source .venv/bin/activate
pip install numpy scipy pandas pyarrow pillow opencv-python-headless matplotlib tqdm imageio imageio-ffmpeg certifi
python3 src/download.py                                  # ~1.1 GB
python3 src/build_graph.py                               # ~3 min, peaks ~8 GB RAM
# build_graph.py reads data/graph/sets_draft.json (bodyId sets derived from the annotations, see docs/RESEARCH_DATA.md);
# that file and columns.json are committed, everything else under data/ is generated.
python3 src/validate.py --quick                          # Tests A-C -> out/validate_results.json + figures
python3 src/run_episode.py --duration 50 --seed 1 --tag final_v2                      # the episode (burst mode is the default)
python3 src/run_episode.py --duration 50 --tag v2_shuffled --shuffle 0 --no-spikes    # wiring-shuffled control
python3 src/run_episode.py --duration 30 --tag v2_side_real --no-spikes --scripted L:15,R:15 --teacher-gap 1.2 2.0             # open-loop side test
python3 src/run_episode.py --duration 30 --tag v2_side_shuf --no-spikes --scripted L:15,R:15 --teacher-gap 1.2 2.0 --shuffle 0
python3 src/side_eval.py v2_side_real v2_side_shuf
python3 src/analyze_episode.py final_v2 v2_shuffled      # figures + JSON
python3 src/render.py --events out/events_final_v2.jsonl --spikes out/spikes_final_v2.npz \
        --positions data/graph/positions.npy --groups data/graph/groups.npy --out out/final.mp4
# reels variant: pre-generated short clips on both screens (fetch the clips first, or placeholders are used)
python3 src/fetch_clips.py                                                             # assets/clips/*.mp4
python3 src/run_episode.py --duration 50 --seed 1 --tag reels_s1 --feed-mode reels
python3 src/analyze_episode.py reels_s1
python3 src/render.py --events out/events_reels_s1.jsonl --spikes out/spikes_reels_s1.npz --stats out/summary_reels_s1.json --out out/final_reels.mp4
# sprites (already committed): python3 src/build_fly_sprite.py ; python3 src/build_device_sprite.py
# optional, the rejected ridge readout of §5.4:
python3 src/run_episode.py --mode teacher --duration 100 --teacher-gap 1.0 1.8 --no-spikes --out-dir out/calib
python3 src/decoder.py fit out/calib/calib.npz out/calib/readout.npz
```

## 9. Phase 2 — the fly is free to ignore the phone (`src/arena.py`, `src/run_arena.py`)

The fixed-position loop above cannot show *choice*: the fly is glued to the hinge. Phase 2 puts
the same brain in a dark 400 × 400 mm box with one open Duo lying flat in the middle and lets it
walk. Design contract: `docs/ARENA_DESIGN.md`.

**Body.** A correlated random walk that is identical in every condition (12 mm/s, Ornstein–Uhlenbeck
heading noise σ 1.2 rad/s, τ 0.5 s, wall reflection) is *modulated* by the brain: forward speed
adds 6 mm/s per Hz of descending-neuron population rate; turning adds 3 rad/s × the normalised
right-minus-left rate of the DNa descending neurons (26 per side; ipsilateral turn as for DNa02).
Rates are Hz per cell of the 1,304 sided descending neurons (the same count the burst decoder
uses); the heading noise is integrated with the exact Ornstein–Uhlenbeck update so its standard
deviation is 1.2 rad/s at any step size. When the descending trace is below 0.05 Hz per cell and
the fly stands on the phone, the base speed drops to 3 mm/s ("standing on the screen"); the
population is bursty, so a connected fly is slow for most of its time on the phone.
The fly is drawn at 10× scale (30 mm body, 22 mm front-leg reach) so that "over a panel" is a
meaningful event; the README states this scale wherever it matters.

**Eye.** A panoramic eye replaces the two fixed panels: a 2 mm luminance map of the room (floor
0.03, walls 0.06, bezel 0.15, the two live feeds pasted onto their 79 × 111 mm panels) sampled by
each eye as a 24 × 18 grid of log-spaced distance (5–300 mm, nearest row lowest in the visual
field) × 10° azimuth bins over that eye's hemifield. The grid feeds the unchanged retinotopic
encoder onto the same L1/L2 lamina cells, with the nearest row mapped onto the ventral retina.

**Swipes.** The same burst rule, but a swipe is applied only if that side's front-leg tip is over a
panel; otherwise it is logged as blocked. Side evidence is near zero in the arena (both eyes see
similar scenes), so which panel gets swiped is close to a coin flip decided by the brain.

**Reward and plasticity.** When a novel card appears on a panel while the fly stands on the phone,
the 316 PAM dopamine neurons are driven at 100 Hz for 300 ms. A dopamine-gated depression rule
(Tsodyks-style eligibility trace on each Kenyon cell, τ 1 s; every KC→MBON synapse of a recently
active KC is depressed in proportion to the dopamine its MBON compartment receives *through the
wiring*, floor 0.2 × w₀, no recovery) acts on the 33,496 KC→MBON edges of the connectome.
Conditions, five seeds each, 120 s:

| condition | wiring | brain → body | swipes | dopamine |
|---|---|---|---|---|
| `real` | MaleCNS | yes | contact-gated | off |
| `dopamine` | MaleCNS | yes | contact-gated | reward → PAM + plasticity |
| `shuffled` | wiring-shuffled | yes | contact-gated | off |
| `random` | MaleCNS (logged only) | **no** (baseline walk) | never applied | off |

The `random` body ignores all three descending rates (`Body(connected=False)`): no speed
modulation, no steering and no standing-still rule, so it is the pure baseline walker (an earlier
version kept the standing rule, which alone inflated the control's time on the phone). Each run
draws its brain and body random streams from `SeedSequence(seed).spawn(2)`, so a condition changes
only the wiring or the coupling, never the noise.

Two caveats found while building it, both properties of the model rather than bugs: under the Shiu
sign convention dopamine neurons are excitatory, so a PAM pulse recruits most Kenyon cells and the
depression is only ~7× stimulus-specific rather than clean; and spontaneous PAM spikes cause a slow
weight drift (w/w₀ ≈ 0.998 over 120 s without any reward). Uniform visual drive of the kind used in Test B does
not reach the mushroom body at all; patterned drive at the encoder's full range does (KC ≈ 2 Hz,
MBON ≈ 8 Hz), so the analysis reports the mushroom-body rates actually reached.

### 9.1 Results (`docs/arena/arena_summary.json`, five seeds × 120 s per condition)

| condition | time on phone | within reach | visits | swipes applied | swipes blocked | 1st half → 2nd half | final KC→MBON w/w₀ |
|---|---|---|---|---|---|---|---|
| real | 15 % [3, 34] | 16 % | 1.4 | 9.2 | 28.6 | 7 % → 22 % | 1.000 |
| dopamine | 12 % [1, 31] | 15 % | 1.2 | 7.6 | 29.2 | 22 % → 3 % | 0.990 [0.980, 0.998] |
| shuffled | 0 % [0, 0] | 1 % | 0.0 | 0.2 | 33.2 | 0 % → 0 % | 1.000 |
| random walker | 7 % [0, 19] | 8 % | 1.0 | 0 (never applied) | 31.2 | 12 % → 1 % | 1.000 |

Brackets are 95 % bootstrap intervals across seeds. Dopamine minus real, paired by seed:
−2.4 percentage points of time on the phone [−29.9, +25.6], −0.2 visits [−1.8, +1.2], learning
(second-half minus first-half) −34 points [−79, +4], final w/w₀ −0.010 [−0.020, −0.002]; exact
sign-flip p = 0.63 (time on phone) and 0.38 (learning). Real vs random walker: +7.9 points,
exact permutation p = 0.48. Real vs shuffled: +14.6 points, p = 0.048 (252 permutations, smallest
attainable p = 0.008). Mean distance to the phone centre: real and dopamine 140 mm, random walker
157 mm, shuffled 159 mm. Visits last 20 s on average with the real wiring (dopamine 22 s) against
7 s for the random walker, whose visits are just transits.

**Honest reading.** With five seeds nothing between the brain-connected conditions is significant,
and the distributions are heavy-tailed: one run per condition (real seed 4, 54 %; dopamine seed 3,
50 %) supplies most of the time on the phone, while three of the five real runs and two of the five
dopamine runs touch it for less than 6 s. The "learning" columns are those single runs — seed 4 of
the real condition found the phone in its second half, seed 3 of the dopamine condition in its
first — so first-half / second-half comparisons mean nothing at this n. What does hold up: the
brain-connected fly stays closer to the phone than the plain random walker (140 mm vs 157 mm), is
within reach twice as often (16 % vs 8 %) and, once on it, stays for 20 s instead of 7 s, because
the swipe-triggering descending bursts also set the walking speed and the quiet phases between
them slow it to the standing speed. That is "attracted to motion" behaviour of the wiring, not a
preference, and it is not significant here (p = 0.48).

The shuffled control is informative in a different way. With the same 89.9 million synapses
rewired at random, the descending output no longer depends on what the eyes see: every shuffled
seed shows the same tonic descending rate (0.37 Hz per cell in all five runs, against 0.30–0.50 Hz
varying with the visual input in the real runs) and the same left–right DNa imbalance
(0.92 vs 0.82 Hz), i.e. a constant speed and a constant 0.2 rad/s turning bias. The fly circles the
room along the walls, is within reach of the phone 1 % of the time and never steps on it. The only
significant contrast in the table, real vs shuffled (p = 0.048), therefore says that with the real
wiring the descending neurons follow the visual input; it does not say the fly wants the phone.

Dopamine did not change behaviour. KC→MBON weights moved by 1.0 % on average (2.9 % in the run
with six rewards), and most of that is reward-independent drift: the rule fires on every PAM spike
and PAM cells fire spontaneously at 0.05–0.10 Hz, so runs with no reward still end at
w/w₀ ≈ 0.998. The mushroom body is nearly silent throughout (KC 0.25 Hz, MBON 1.1 Hz), so a few
rewards cannot move it far. Novel-card approach could not be measured: 0–1 novel cuts per run
happened while the fly was off the phone.

What would make this a real experiment rather than a pilot: (1) a DN → *stop-and-orient* mapping
(or a data-driven one from DNp09 / DNa-type walking and halting neurons) instead of DN → speed;
(2) 20+ seeds per condition, since single runs dominate every mean above; (3) a modulatory
(non-spiking-effect) treatment of dopamine synapses with a reward gate, so a PAM pulse rewards the
active Kenyon cells specifically instead of drifting on spontaneous PAM spikes; (4) longer runs,
because learning needs rewards and rewards need visits. The code supports all four; none was tuned
here.

Figures: `docs/figures/arena_trajectories.png`, `arena_time_on_phone.png`, `arena_distance.png`,
`arena_w_ratio.png`. Video: `python3 src/render_arena.py --events out/arena_dopamine_s3.jsonl
--spikes out/arena_dopamine_s3_spikes.npz` (the most eventful dopamine run: one 60 s visit,
25 swipes, 6 rewards, 50 % of the time on the phone, w/w₀ 0.971).

### 9.2 Train first, then set it free (`--pin-on-phone`, `--forced-swipe-s`, `--save-weights`, condition `trained`)

The question behind this protocol: if the fly is *made* to scroll for ten minutes with dopamine
on, does it then choose the phone more often than an untrained fly? Two phases, same brain.

**Training (10 min of brain time).** The body is pinned on the hinge at the centre of the phone,
facing up, so the front-left leg is over the left panel and the front-right leg over the right
one. Every 2 s a swipe is forced on alternating panels (logged with `forced: true`); the brain's
own descending bursts still swipe as well. Plasticity is on (`dopamine` condition) and every
novel post that appears while the fly is on the phone, which is always, drives the 316 PAM
neurons for 300 ms. At the end the 33,496 KC→MBON weights are written to a file
(`Brain.export_plastic_weights`). Nothing else is carried over: membrane potentials, synaptic
depression and traces start fresh in the test, so the *only* trace of the training is the
learned weights. Training seed 100, separate from the test seeds.

**Test (120 s, five seeds).** Condition `trained` = the `real` condition (real wiring, brain
steers, contact-gated swipes, no dopamine) with the trained weights loaded before the run
(`Brain.import_weights`) and plasticity frozen. Start pose, heading noise and feeds are the same
seeds 0–4 as the published sweep, so `trained` vs `real` is a paired comparison in which the
only difference is the learned weights. An "exposure without dopamine" control needs no run: with
plasticity off the ten minutes leave no trace in the model, so that control *is* the `real` row.

```bash
python3 src/run_arena.py --condition dopamine --seed 100 --duration 600 --pin-on-phone --forced-swipe-s 2 \
        --save-weights out/train/trained_w.npz --tag arena_train_pinned_s100 --out-dir out/train
for sd in 0 1 2 3 4; do python3 src/run_arena.py --condition trained --seed $sd --duration 120 --load-weights out/train/trained_w.npz; done
python3 src/analyze_arena.py            # adds the `trained` row and the trained − real paired comparison
```

**Training outcome (`docs/arena/arena_train_pinned_s100_summary.json`).** In 600 s on the phone the
fly received 299 forced swipes and made 236 of its own, saw 165 novel posts, i.e. 165 dopamine
rewards, and its KC→MBON weights fell to **0.63 w₀** on average, with the most active edges at the
0.2 floor. The training did what it was meant to: the mushroom-body output changed. In the free
test the trained flies' MBON rate is 0.83 Hz against 1.12 Hz with the untrained wiring (−26 %),
with the same visual input statistics.

**Test outcome (five seeds, 120 s, `trained` vs `real`, same seeds):**

| condition | time on phone | within reach | visits | swipes applied | mean visit | MBON Hz |
|---|---|---|---|---|---|---|
| real | 15 % [3, 34] | 16 % | 1.4 | 9.2 | 20 s | 1.12 |
| trained | 10 % [0, 22] | 11 % | 1.2 | 4.6 | 11 s | 0.83 |

| seed | 0 | 1 | 2 | 3 | 4 |
|---|---|---|---|---|---|
| real, time on phone | 0 % | 9.5 % | 4.8 % | 4.4 % | 54 % |
| trained, time on phone | 0 % | 30 % | 0 % | 22 % | 0 % |

Paired trained minus real: −4.3 points of time on the phone [−30, +15], −0.2 visits, exact
sign-flip p = 0.88; unpaired permutation p = 0.75. Two seeds went up (1 and 3), one stayed at
zero, two went down (seed 4 lost its 60 s visit entirely, because the trained brain steered
differently in the first seconds and never came near the phone).

**Honest reading.** Ten minutes of forced, rewarded scrolling trained the synapses but not the
behaviour. The fly did not come back for the phone more often; if anything it spent less time on
it. The reason is structural and worth stating plainly: in this model the mushroom-body output
neurons have no strong route to the descending neurons that set walking speed and turning. The
MBONs changed their firing by a quarter, but the descending population that drives the body is
dominated by the visual pathways, which the training did not touch. In a real fly, MBON activity
biases approach and avoidance through downstream neuromodulatory and central-complex circuits;
here the same anatomical connections exist in the wiring, but under a uniform LIF model with
depression-only plasticity they do not carry enough weight to change where the fly walks. So the
answer to "does it choose the phone after being made to use it" is **no**, and the experiment says
why: we know how to change what the fly's memory centre says about the phone, and we can see it
change; we do not have a motor pathway through which that memory can express a preference.

What would test the idea properly: a modulatory (non-spiking) treatment of dopamine so the
depression is stimulus-specific; a validated MBON → descending-neuron readout (or the central
complex's role in goal-directed steering) instead of DN rate alone; 20+ seeds; and a
counter-balanced control in which the same 600 s of forced scrolling pairs dopamine with the
*absence* of the phone.

Figures: `docs/figures/arena_trajectories.png` (five panels), `arena_time_on_phone.png`.

## 10. Attribution (CC-BY)

> Connectome: MaleCNS v1.0 — HHMI Janelia FlyEM Project Team, the Cambridge Drosophila
> Connectomics Group (University of Cambridge / MRC Laboratory of Molecular Biology), and Google
> Research Connectomics. CC-BY 4.0. https://male-cns.janelia.org/ — Berg et al., "Sexual dimorphism
> in the complete connectome of the Drosophila male central nervous system," *Cell* (2026),
> doi:10.1016/j.cell.2026.08.015. Neurotransmitter predictions: Eckstein, Bates et al. (2024) /
> funkelab. Neuron model after Shiu et al., *Nature* (2024). Simulation design informed by
> hotocoo/malecns and TheMrRaGe/flybrain (re-implemented; those repositories carry no licence file,
> so no code was copied). iPhone Duo is a trademark of Apple Inc.; the device shown is a mock-up;
> feeds are synthetic and contain no real posts, apps or logos.

Suggested caption: *A real fruit-fly connectome (MaleCNS v1.0, 166,700 neurons) simulated as a
spiking network, doomscrolling two feeds at once — one per eye, one per leg. Every swipe is a
burst of the fly's own descending neurons, sent to the side whose eye saw the change. Nothing
scripted, nothing fitted. Data CC-BY Janelia FlyEM · Cambridge · Google.*

