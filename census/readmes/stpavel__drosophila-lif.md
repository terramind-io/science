# drosophila-lif

**A real fruit-fly brain circuit, running live in JavaScript.**

2 546 neurons and ~680 000 synapses taken from the [FlyWire](https://flywire.ai) whole-brain connectome of *Drosophila melanogaster*, simulated as spiking leaky integrate-and-fire neurons in real time — in the browser or in Node, with zero dependencies.

Smell on the left antenna → the fly steers left. Sugar on the legs of a hungry fly → the proboscis motor neuron **MN9** fires. A startle → the **giant fiber** escape neuron fires. These responses come from the real wiring, not from hand-written rules.

```js
import { DrosophilaBrain } from 'drosophila-lif';

const brain = await new DrosophilaBrain().load('data/flywire-subgraph.bin');

brain.setInput({ odorLeft: 0.8, odorRight: 0.1, taste: 0, hunger: 1, ethanol: 0 });
brain.step(16);                        // advance 16 ms (call every animation frame)

const out = brain.getOutputs();
out.steering      // < 0 turn left, > 0 turn right
out.proboscisMN9  // Hz — "drink or not" (≈0 sated … ≈280 starved)
out.giantFiber    // Hz — escape command after brain.startle()
```

Live demo: open `examples/index.html` through any static server (`npx serve .`).

## What is inside

| | |
|---|---|
| `src/drosophila-lif.js` | the whole library, ~10 KB, no DOM |
| `data/flywire-subgraph.bin` | 164 KB gzipped subgraph: neurons, groups, CSR synapse matrix, frontal-view positions |
| `tools/build_subgraph.py` | how the subgraph was cut out of FlyWire v783 (reproducible) |
| `examples/index.html` | interactive demo with sliders |
| `test/smoke.mjs` | `npm test` — checks the three behaviours below |

**Circuits included:** olfactory receptor neurons of fermentation-sensitive glomeruli (DM1, DM2, DM4, VA2, DP1m) for each antenna → antennal-lobe projection & local neurons → lateral horn, mushroom body (Kenyon cells, APL, MBONs, PAM dopamine neurons), central complex; sugar gustatory receptor neurons → every neuron active on the sugar→MN9 pathway in the full-brain model → MN9; giant fiber (DNp01); steering descending neurons DNa01/DNa02; a sample of optic-lobe neurons.

**Neuron model** (Shiu et al., Nature 2024): `dv/dt = (−v + g)/τm`, `dg/dt = −g/τs`, a presynaptic spike adds `synapses × 0.275 mV × sign` to the target, sign from the predicted neurotransmitter. τm = 20 ms, τs = 5 ms, threshold 7 mV, refractory 2.2 ms, dt = 0.5 ms.

## Verified behaviour (`npm test`)

```
sugar → MN9: hungry 282 Hz, sated 14 Hz, no taste 0 Hz
odor steering: left odor −39.5, right odor +32.5
startle → giant fiber 47 Hz
```

## Honest limitations

This is a **subgraph** of a **simplified** neuron model, tuned to be stable when cut out of the whole brain. Please read before you tweet "the fly brain in 10 KB":

- **2 546 of ~140 000 neurons.** Neurons that were silent under these stimuli in the full-brain model are left out.
- **Added spike-frequency adaptation** in the antennal lobe, lateral horn and mushroom body. Without it the isolated antennal lobe excites itself. Real neurons do adapt, but the strength is a tuning choice.
- **Steering** is read mostly from the left/right contrast of sensory and antennal-lobe activity. In this model the DNa01/DNa02 steering neurons do not respond to odor side reliably, so they are not used for steering.
- **Ethanol** is phenomenological: a global scaling of excitatory/inhibitory weights and threshold, not a receptor-level model.
- **Hunger** scales sugar-receptor drive (starved flies are more sensitive to sugar), the magnitude is ours.
- Only motor *commands* come out. Legs, wings and bodies are up to you.

## Credits and citations

- Connectome: **FlyWire** — Dorkenwald et al., *Neuronal wiring diagram of an adult brain*, Nature 634 (2024), [doi:10.1038/s41586-024-07558-y](https://doi.org/10.1038/s41586-024-07558-y); Schlegel et al., *Whole-brain annotation and multi-connectome cell typing of Drosophila*, Nature 634 (2024), [doi:10.1038/s41586-024-07686-5](https://doi.org/10.1038/s41586-024-07686-5).
- Model: Shiu et al., *A Drosophila computational brain model reveals sensorimotor processing*, Nature 634 (2024), [doi:10.1038/s41586-024-07763-9](https://doi.org/10.1038/s41586-024-07763-9); connectivity table from [philshiu/Drosophila_brain_model](https://github.com/philshiu/Drosophila_brain_model) (MIT).

## License

Code: **MIT** (see `LICENSE`). Data file: derived from FlyWire — see **`DATA_LICENSE.md`**.

---

### По-русски

Кусок настоящего мозга дрозофилы (2 546 нейронов, ~680 тыс. синапсов из коннектома FlyWire) в виде спайковой модели на чистом JavaScript. На вход — запах слева/справа, вкус, голод, этанол; на выход — руль, нейрон хоботка MN9 и нейрон побега giant fiber. Работает в реальном времени в браузере.

Сделано в (https://nalivatorplus.ru): там этот мозг решает, сколько налить — активность MN9 превращается в миллилитры.
