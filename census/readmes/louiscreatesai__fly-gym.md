# Fly Gym

A simulated fruit fly doing gym stuff, forever.

**Try it in your browser:** https://louiscreatesai.github.io/fly-gym/

It works on a phone too. Tap **Brain** to open the brain panel.

| Scene | What happens | What the brain panel replays |
|---|---|---|
| Leg day | The fly has six legs, so leg day is triple leg day. It leg-presses with all six while the plates keep stacking. | Descending neurons MDN + DNb05 + DNa03 driven at 300 Hz. All three leg pairs light up in the nerve cord. |
| Sisyphus | It pushes a sugar cube uphill and never reaches the top. Flies taste with their feet, so it tastes the sugar the whole time. | Sugar taste neurons driven at 150 Hz. MN9, the feeding motor neuron, fires. |
| Pre-workout | One dry scoop and the treadmill never stops speeding up. | P9 walking neurons driven at 40, 80, 160 and 320 Hz as the speed climbs. No caffeine is modeled. |
| Blackjack | The fly brain makes every hit or stand call. | Sugar taste neurons at 150 Hz (the win) plus bitter taste neurons at a rate that grows with the hand total (the risk). If MN9, the feeding motor neuron, still fires above half its sugar-only rate, the fly hits. The rule was fixed before any run. The result: it only hits on 4 and stands on everything from 5 to 21. |

## Run it yourself

It is a static web page, so there is no install and no build step. You only need Python.

1. Download the repo (green **Code** button, then **Download ZIP**, and unzip it) or run `git clone https://github.com/louiscreatesai/fly-gym.git`.
2. Double-click **Start Fly Gym.bat** on Windows, or **start.command** on Mac. It serves the folder on http://localhost:5600 and opens it in your browser.

Or do it by hand: `python -m http.server 8000` in the folder, then open http://localhost:8000.

Don't double-click index.html itself: browsers block 3D pages opened straight from a folder. If you do, the page tells you what to do instead.

Controls: the buttons on the workout card switch cameras, pause and restart. Drag to rotate. On a keyboard: `R` restarts, `1` `2` `3` switch cameras, `Space` pauses, `F` goes full screen, `H` hides the panels, `C` toggles the pop-up labels and `P` shows the fps.

## How the brain panel works

- **The model:** a leaky integrate-and-fire model of every neuron in the fruit fly's brain and nerve cord (166,700 neurons, 25.6 million connections), wired by the Janelia MaleCNS v1.0 connectome, following the method of Shiu et al. 2024.
- **The runs:** we drove specific sensory or descending neurons for 1 second, as listed in the table above, and saved every spike.
- **The panel:** it replays one trial of that run at 0.35x speed. Every flash, raster dot, count and bar comes from those saved spikes, and the panel names exactly which neurons were stimulated.

It is a model of the wiring, not a living fly and not a copy of a mind. The gym numbers (day 9,999, infinite reps) are jokes.

The 3D fly is NeuroMechFly, a model built from a micro-CT scan of a real fly. It is posed with inverse kinematics, and the treadmill scene uses a real recorded step cycle.

## Credits

- Body: NeuroMechFly v2 (Wang-Chen et al. 2024; Lobato-Rios et al. 2022), meshes from [flygym](https://github.com/NeLy-EPFL/flygym), Apache-2.0.
- Connectome: Janelia MaleCNS v1.0 (Berg et al. 2026), CC BY 4.0.
- Brain model: Shiu et al. 2024, *A Drosophila computational brain model reveals sensorimotor processing*, Nature 634, 210-219.
- 3D engine: [three.js](https://threejs.org), MIT. Font: Inter, SIL Open Font License 1.1.

Details and licence texts are in [THIRD_PARTY.md](THIRD_PARTY.md) and [licenses/](licenses/). The Fly Gym code itself is MIT ([LICENSE](LICENSE)).
