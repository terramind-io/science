# Dopamine Trading Fly

A fruit fly gets $100,000 of paper money and up to 50x leverage on live BTCUSDT.
Wins make it jump and lever up. Losses make it writhe and cut leverage. Stress wears its body down until it dies.
Next to it, a simulated connectome of the whole fly brain (138,639 neurons) lights up: sugar taste neurons on a win, bitter taste neurons on a loss.

It is a toy. No orders are ever sent anywhere.

## What is real and what is made up

| part | status |
|---|---|
| Fly body | Real anatomy and physics: NeuroMechFly body model via [flygym](https://github.com/NeLy-EPFL/flygym), simulated in MuJoCo |
| Walking, jumping, writhing | Scripted. Leg rhythms plus assist forces, not neural control |
| Market data | Real. Binance public spot ticker, 1s candles and order book, no API key |
| Trading decisions | Invented rules (below). **The brain does not make the trades** |
| Brain wiring | Real. FlyWire v783 connectivity, the dataset used by [Shiu et al. 2024](https://github.com/philshiu/Drosophila_brain_model) |
| Brain activity | Simulated with the same leaky integrate-and-fire equations and parameters as Shiu et al., reimplemented in numpy |
| Win = sugar, loss = bitter | My choice of input mapping |

## Rules

- Start with $100,000 at 5x. Each position is held 12 seconds (3 in fast mode), then closed.
- Win: leverage times 1.5 (max 50x), dopamine up, it tends to repeat the same side.
- Loss: leverage divided by 1.5 (min 1x), stress up, health down, it tends to flip sides.
- A trade that nets zero or less counts as a loss.
- Fees (toggle): 0.05% of position size per side, an assumed taker rate.
- Death: health reaches zero, or price touches the liquidation price.

The page shows win rate, reward to risk, profit factor, expectancy per trade, max drawdown and fees paid.

## Run it

Tested on macOS with Python 3.14. flygym needs Python 3.12 to 3.14.

```bash
git clone https://github.com/tyun122189/dopamine-trading-fly
cd dopamine-trading-fly
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python get_data.py      # about 136 MB of connectome data
.venv/bin/python fly.py
```

Open http://localhost:8790 and press START.

Binance's public API is not reachable from every region. If prices never load, that is the likely reason.

## Brain model

- 138,639 neurons, 15,091,983 connection rows from `Connectivity_783.parquet`.
- Parameters from the original `model.py`: resting and reset potential -52 mV, threshold -45 mV, membrane time constant 20 ms, synaptic time constant 5 ms, refractory period 2.2 ms, synaptic delay 1.8 ms, 0.275 mV per synapse, 150 Hz Poisson input.
- Integrated with a 0.1 ms Euler step, event-driven synaptic delivery.
- Runs in its own process. After each trade it stimulates 500 ms of taste input and runs until activity dies out, which takes a few seconds of wall time (about 5x slower than real time on the machine it was built on). Between events it does no work.

Validation: the original example notebook lists 21 sugar neurons, 20 of which exist in v783. Stimulating those 20 at 150 Hz for 1 s drove MN9, the feeding motor neuron the paper uses, to 99 spikes in that second in this reimplementation.

Known issue: across five test runs with bitter input, three activated about 180 to 190 neurons, one 961, and one 10,751. This has not been compared against the original Brian2 implementation, so the spread may be a difference in this reimplementation.

Neuron positions and region groups come from the FlyWire annotation table. Each dot on the brain map is one neuron at its annotated position, front view.

## Credits

- Brain model and connectivity: Shiu et al. 2024, [philshiu/Drosophila_brain_model](https://github.com/philshiu/Drosophila_brain_model) (MIT).
- FlyWire connectome and annotations: [flyconnectome/flywire_annotations](https://github.com/flyconnectome/flywire_annotations). Per that repository, cite Berg et al. (2025), Schlegel et al. (2024), Matsliah et al. (2024) and Dorkenwald et al. (2024).
- Fly body: [NeuroMechFly / flygym](https://github.com/NeLy-EPFL/flygym) (Apache-2.0).
- Physics: [MuJoCo](https://github.com/google-deepmind/mujoco) (Apache-2.0).

Connectome data is not included in this repository. `get_data.py` downloads it from the sources above.

## Not financial advice

Paper trading on public data, for fun. The fly has no edge, and with fees on its expected result per trade is negative.
