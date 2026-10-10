# dino-fly

**A real fruit-fly brain plays Chrome Dino.** The complete adult *Drosophila* connectome (FlyWire: 138,639 neurons,
15 million connections) runs as a spiking neural network on a laptop GPU. A cactus is shown to the fly the way
neuroscientists show looming objects to real flies; when the fly's own escape neuron — the Giant Fiber — fires, the
dino jumps.

**What makes it different:** there is **no neural network on top of the brain**. No YOLO, no policy net, no trained
readout. Connectome weights are frozen as reconstructed. The only learning mechanism is the fly's own:
dopamine-gated plasticity at Kenyon cell → mushroom-body output neuron synapses. The game→neurons and neurons→action
mappings are fixed, hand-written and documented, and every number below comes from a script in this repo — including
the ones that are unflattering.

**Play it:** <https://flybrain-dino.vercel.app> (race the fly's recorded runs — or play with your body through the
laptop camera; the live brain is online only while Tair's laptop is).
**Read the research log:** [`docs/RESEARCH.md`](docs/RESEARCH.md).

## 30-second version of the results

All numbers: `docs/RESEARCH.md`, rendered from `brain/experiments/results/*.json`.

1. **Our engine *is* the published model.** On the real connectome our PyTorch engine and Brian2 (the simulator the
   model was published in, Shiu et al., *Nature* 2024) produce *identical spike trains* given identical input
   (≈ 10,000 spikes per trial, zero mismatches). The paper's sugar → MN9 curve is reproduced with 0.9 Hz RMSE.
2. **Looming reaches the escape neuron.** Driving the LPLC2 / LC4 looming detectors makes the Giant Fiber fire; the
   two Giant Fibers rank #1 and #6 of 1,299 descending neurons by response probability, and the same drive into the
   wrong cell types (LC6 / LPLC1) reaches it in only 5 % of trials. Unlike in real flies, the model's response grows
   with *slower* looms — a mismatch we report rather than tune away.
3. **The naive fly plays — badly but really.** Score 83 vs. 40 for never jumping, on 200 held-out seeds. When it
   jumps it clears the obstacle 99 % of the time; it mostly dies by *not* jumping. A Giant-Fiber-ablated fly, a
   jump-rate-matched random agent and 25 degree-preserving shuffles of the connectome all score at or near the floor.
4. **…and the honest part:** a bare threshold on our own hand-written transducer, with no brain at all, scores 281.
   In this phase the brain is a noisy threshold; the wiring is necessary (shuffles fail, and surprisingly the
   *direct* looming→Giant-Fiber synapses alone are not enough — the indirect pathways carry the jump), but it is not
   yet *adding* skill.
5. **The fly's own learning rule does not make it play better — and we know why.** With dopamine-gated KC→MBON
   plasticity acting only through the real wiring (H1, pre-registered, 100 held-out seeds), the score goes from 88.6
   to 85.6 after the first generation and then never moves again: later generations — and a control with rewards
   delivered at random moments — play all 100 held-out games *identically*. On the way there: no direct
   MBON→Giant-Fiber synapse exists (10 of 35 MBON types can suppress the Giant Fiber, none excites it); every way of
   feeding visual context into the mushroom body through visual projection neurons either fires the Giant Fiber by
   itself or abolishes its looming response (24 configurations), so the context had to enter at the Kenyon cells — a
   flagged deviation from our own rule; and the published model can *ignite*: after some crashes a third of all
   Kenyon cells fire in self-sustained volleys (dopamine is a fast excitatory transmitter in it and nothing adapts).
6. **A number we refuse to call learning.** Under the second hypothesis (H2: mushroom-body output sets the looming
   gain — a documented model assumption, still no learned layer) the held-out score goes from 90.6 to 160.3 in one
   generation. But rewards delivered at *random* moments end at exactly the same 160.3 (99 of 100 games identical):
   any dopamine depresses the only MBONs the context reaches, the gain ratchets to its ceiling of 2 G, and 2 G happens
   to play better. By the criteria fixed before the run — beat generation 0 *and* beat shuffled dopamine — the verdict
   is **no learning effect**. The research log says what would make it a real test.

## How it works

```
game state ─► looming transducer ─► LPLC2 / LC4 Poisson drive ─► whole-brain LIF (frozen FlyWire 783)
     ▲            (θ, θ̇ of the nearest obstacle; fixed)                        │
     └──────── JUMP ◄── motor transducer ◄── Giant Fiber (DNp01) spike ◄──────┘
```

- `brain/` — Python: connectome loader, our own Brian2-faithful event-driven LIF engine (exact "active set":
  only neurons that ever received input are updated), fixed transducers, KC→MBON plasticity, experiments, worker.
- `packages/dino-core` — deterministic all-integer game engine (TypeScript, source of truth) with a byte-identical
  Python port; `packages/dino-render` — own pixel art; `packages/protocol` — JSON-Schema message protocol.
- `apps/web` — play vs. the fly, live brain map, leaderboard, research page; `apps/api` — scores validated by
  deterministic replay, leaderboard, ghosts, worker hub (Postgres).
- `firmware/` — ESP32 stats display and XIAO ESP32S3 camera *(compile; kept for later, not needed to play — body
  control runs in the browser on the laptop camera)*.
- `docs/` — [ARCHITECTURE](docs/ARCHITECTURE.md) · [RESEARCH](docs/RESEARCH.md) · [NEURONS](docs/NEURONS.md) ·
  [DECISIONS](docs/DECISIONS.md) (incl. open questions and the forking-paths log) · [PROTOCOL](docs/PROTOCOL.md) ·
  [HARDWARE](docs/HARDWARE.md) · [DEPLOY](docs/DEPLOY.md) · [PROGRESS](docs/PROGRESS.md).

## Run it

```bash
# brain (uv; NVIDIA GPU for the real connectome, CPU is enough for the tests)
cd brain && uv sync --extra gpu            # or --extra cpu
uv run --no-sync pytest                    # synthetic 1k-neuron connectome, no data needed
uv run --no-sync flybrain download-data    # ~330 MB, pinned URLs + SHA-256
uv run --no-sync python -m experiments.sugar_mn9
uv run --no-sync flybrain worker           # the fly plays live on ws://localhost:8765

# game, web app, API
pnpm install && pnpm test
pnpm --filter @dino-fly/web dev            # http://localhost:5173  → Play / Brain / Lab
```

Full local + cloud setup: [`docs/DEPLOY.md`](docs/DEPLOY.md).

## Status

| Phase | State |
|---|---|
| 0 Skeleton, engine, correctness, benchmark | done |
| 1 Innate escape, game engine, naive play vs. controls | done |
| 2 Web dashboard, live brain map, worker | done (brain map v1 is group-level) |
| 3 API, DB, replay validation, leaderboard | done locally; web deployed; **Railway API deploy blocked** (see DEPLOY.md) |
| 4 Learning (KC→MBON plasticity) | measured, pre-registered: H1 (real wiring only) → no learning effect; H2 (model assumption) → score 90.6 → 160.3 but identical with shuffled dopamine → no learning effect; open decisions D13, D17 |
| 5 Crowd teaching | **collecting**: every validated human run is stored; training a new generation from them is a deliberate manual step (D21) |
| 6 Hardware | optional (D22): body control runs in the browser on the laptop camera. ESP32 firmware compiles but is **not part of the product** |
| 7–8 Stretch, MaleCNS, v1.0 write-up | not started |

## How to cite / credits

See [`CITATION.cff`](CITATION.cff) and [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md). Built on the FlyWire connectome
(Dorkenwald et al. 2024; Schlegel et al. 2024; CC BY 4.0) and the whole-brain model of Shiu et al., *Nature* 634:210–219
(2024). Game feel after the Chromium offline game (BSD); own implementation and art. Code: MIT © Tair Kaldybayev.
