# PSP Fly Arena

Connectome-constrained fruit-fly brain driving a fly sprite in a 2D arena on a PSP-2000.
Design: docs/superpowers/specs/2026-09-15-psp-fly-arena-design.md

## What is in the fly's brain

Every neuron is a leaky integrate-and-fire unit stepped at 1 ms (Shiu et al. 2024 constants:
v_rest = v_reset = −52 mV, v_th = −45 mV, τ_m 20 ms, τ_syn 5 ms, 2 ms refractory), except the
optic lobe, which runs the graded flyvis model at 5 ms. Synaptic weights from the connectome are
0.275 mV × synapse count, sign from the predicted transmitter (ACH/DA/SER/OCT +, GABA/GLUT −).
Firing rates are 50 ms exponential averages of spikes.

| Circuit | Source | Neurons / synapses | What it does in the arena |
|---|---|---|---|
| Walking "noise brain" | hand-wired (`src/sim/noise_brain.c`) | 6 / 5 | Two 25 Hz Poisson sources drive DNa02_L and DNa02_R (mutual inhibition); a 3 Hz source drives DNp09. Rate(DNa02_L) − rate(DNa02_R) sets angular velocity, DNp09 above 20 Hz stops walking. Produces wandering with saccade-like turns. |
| Sugar pathway | FlyWire v783 (`src/data/sugar_net.c`) | 2,774 / 91,598 | The 23 sugar gustatory neurons (`data/ids/sugar_grn.txt`), everything within 2 synaptic hops downstream of them (≥ 5 synapses, capped at 3,000), and the two proboscis motor neurons MN9 with their inputs. Sugar under the fly → GRNs fire at 200 Hz → MN9. Mean MN9 rate > 20 Hz = **feeding**: the body freezes and the spot depletes at 0.1/s. Weights are scaled by 0.45 (at 1.0 the network is bistable and MN9 never switches off). |
| Compass | FlyWire v783 (`src/data/compass_net.c`) | 151 (+3 sources) / 4,412 | EPG 47, PEN_a 20 + PEN_b 22 (split 21 left / 21 right), PEG 20, Δ7 42, with EPGs assigned to 16 wedges by spectral ordering. Extracted and kept, but **not active on the device**: under uniform weight scaling it is either silent or fully saturated and never holds a heading bump (see `docs/notes/phase3-validation.md`). |
| Heading ring (fallback) | hand-set (`src/sim/ring.c`) | 16 rate units | A cosine-kernel ring attractor seeded at wedge 0 and shifted by the body's angular velocity. This is what the HUD compass ring shows. |
| Path integrator | hand-set, Stone et al. 2017 structure (`src/sim/pathint.c`) | 16 rate units | Accumulates speed × heading bump. Re-zeroed when feeding starts; when the sugar is gone it steers the fly back toward the remembered spot with a gain that decays over 60 s (**local search**). |
| Optic lobe | pretrained flyvis "flow" network, equatorial hex row, one copy per eye (`src/data/optic_net.c`) | 3,950 graded units / 49,960 | 65 cell types (R1–R8, L1–L5, Mi, Tm, T4a–d, T5a–d, …). A 70-ray 1D retina (5° per cell) feeds the photoreceptors; T4a/T4b back-flow is read out as looming and L2 frontal contrast as fixation. Wired in, but on this one-row crop the steering signal is too weak to change behaviour (see `docs/notes/phase4-validation.md`). |

Everything that connects a circuit to the body — DN rates → turning, MN9 → feeding, sugar → GRN drive,
angular velocity → ring shift, the whole path integrator, the retina model and the vision readouts —
is hand-set, not emergent; the spec lists them in §6.

## What you see

- The fly (dark triangle, blue head dot) walks at 15 mm/s in a 40 × 18.3 mm arena and turns when
  the noise brain says so. Walls are tactile: it slides along them until it turns away.
- Drop sugar (Cross) in its path: when its centre enters the pale disc it stops, the feeding square in
  the HUD lights, `FEED` and the MN9 rate appear in the text line, and the disc shrinks and vanishes
  after about 10 s. Then it wanders again, biased for a minute toward where the sugar was.
- Posts (Triangle) are obstacles it cannot enter. It does not yet steer around them visually.
- HUD band: grey retina strip (70 luminance samples, live once Phase 4 Task 8 lands), the heading
  ring with the bump, the feeding square, and a green frame-time bar (100 px = 16.7 ms).

## Controls

Analog stick moves the crosshair (30 mm/s). Cross: sugar. Triangle: post. Circle: remove nearest
object within 3 mm. Square: toggle the text line. L / R: world speed 0.25 / 0.5 / 1.0. Start: pause.
Select: reset. Home: exit. In PPSSPP: `I/J/K/L` = stick, `Z` Cross, `S` Triangle, `X` Circle,
`A` Square, `Q`/`W` triggers, `Space` Start, `V` Select.

## Status

Phases 1–3 are tagged (`phase-1-done` … `phase-3-done`). Phase 4 is stopped at its behavioural
validation: the retina and optic row run, but looming avoidance and post fixation do not emerge from
the one-row crop. Validation records for every phase are under `docs/notes/`.

## Build (PSP)
    export PSPDEV=$HOME/pspdev PATH=$HOME/pspdev/bin:$PATH
    make            # -> EBOOT.PBP

## Run in emulator
PPSSPP from Homebrew installs as `PPSSPPSDL.app` on this machine:
    open -a PPSSPPSDL EBOOT.PBP

## Deploy to PSP-2000
Connect USB, enable USB mode on the PSP, then:
    mkdir -p /Volumes/PSP/PSP/GAME/FlyArena && cp EBOOT.PBP /Volumes/PSP/PSP/GAME/FlyArena/

## Host tests and validations
    make -f Makefile.host test                       # all unit tests
    .venv/bin/pytest tools/tests -q                  # extraction tools
    make -f Makefile.host headless-sugar W=0.45      # MN9 on/off sugar
    make -f Makefile.host headless-compass W=1.0 G=60 S=1
    make -f Makefile.host headless-search RING=1 W=1.0
    make -f Makefile.host headless-vision
