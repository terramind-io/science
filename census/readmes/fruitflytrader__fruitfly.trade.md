![fruitfly.trade](assets/logo/readme-banner-1600x400.png)

# fruitfly.trade

A whole male *Drosophila* nervous system, simulated spike by spike, whose own spikes choose
memecoin trades on Robinhood Chain.

The connectome is MaleCNS v1.0 (**166,700 neurons, 25,582,938 edges, 124,177,617 synaptic
contacts**), run as a leaky integrate-and-fire network at 0.1 ms resolution. Market numbers
become Poisson drive on small taste populations. When the feeding command neurons (Fdg) fire,
that is a BUY. When the moonwalker descending neurons (MDN) fire, that is a SELL.

**No language model is in the loop.** Nothing in the decision path prompts a model, embeds a
token, or asks for a sentiment score. An observation becomes spike rates, 25.6 million
synapses propagate them, and two motor populations answer. Language models helped write this
code. None of them is inside the fly.

## The honest summary

- **The simulation is faithful and it validates.** The compiled graph matches independently
  reported counts. At the calibrated input (4 mV, 200 Hz), sugar gustatory neurons drive MN9
  (proboscis extension) in 9 of 9 repeated runs. That is the validation criterion Shiu et al.
  2024 used, reproduced on a different connectome with an independent kernel. Ignition at
  4 mV is stochastic: the whole brain ignited in 7 of 9 sugar runs, and the two quiet runs were
  silent rather than sparse.
- **The motor decoders are measured and selective.** In 9 repeated 500 ms sugar runs, both Fdg
  cells fired every time and MDN never fired. MDN's own presynaptic drivers fired all four MDN
  cells in 9 of 9 runs (median 18.5 Hz), with one stray Fdg spike across all nine. MN9 fires for
  sugar too, but once the brain ignites it also fires for MDN's drivers and for a smell, so BUY
  reads Fdg alone and SELL reads MDN.
- **Decisions need strong input.** In the 200 ms window the fly decides in, no input from 25 to
  100 Hz produced a BUY or a SELL on any seed. Sugar at 200 Hz produced a BUY in 3 of 6 seeds;
  MDN's drivers produced a SELL in 6 of 6 at 175 Hz and above.
- **Mushroom-body learning does not work, and we know why.** A single glomerulus either
  ignites all 4,064 Kenyon cells or propagates nothing, and two different odors give
  identical Kenyon-cell sets (Jaccard 1.000). We tested four causes and refuted all four:
  missing APL inhibition, input strength, global weight scale, and synaptic time constant.
  Every scalar dial gives the same step function. So there is no odor code, no conditioning,
  and no claim that the fly learns.
- **No profitable trading has been demonstrated.** None, offline or live. On a 0.005 ETH
  position, fixed costs come to about 43 to 48 percent per round trip before slippage, most of it
  Axiom's flat 0.001 ETH priority fee.

Because the odor code failed, the connectome is treated as a **fixed nonlinear filter**.
Every one of its 25,582,938 weights is left as reported. Evolution strategies, run offline,
train only a small gain vector on the sensory side and the decoder thresholds.

Details: [`docs/MODEL.md`](docs/MODEL.md) (equations, parameters, departures from Shiu),
[`docs/FINDINGS.md`](docs/FINDINGS.md) (every measurement and sweep),
[`docs/AXIOM.md`](docs/AXIOM.md) (venue, filters, costs, terms of service).

## Measured versus assumed

| Measured on the real graph | Assumed, and flagged |
|---|---|
| Graph counts against an independent report | That extending the proboscis means "buy" and walking backward means "sell". These are our labels on measured circuits. |
| 4 mV into the synaptic variable is the working input, and even there ignition is stochastic (7 of 9 sugar runs); 8 mV ignites the brain | That a market signal can reach MDN's drivers at all. Those drivers are visual and ascending pathways, not taste pathways. |
| Sugar fires Fdg in 9 of 9 repeated runs and never fires MDN | That the offline market simulator resembles the venue. It is not calibrated against held-out on-chain data. |
| MDN's drivers fire MDN in 9 of 9 repeated runs; Fdg gave one stray spike across all 9 | That monoamine and unresolved-transmitter cells act as fast excitation (see MODEL.md, D4) |
| The odor code fails, and four candidate causes are refuted | That the encoder calibration, fitted to simulated coins, carries over to real Pulse coins (fruitfly/resources/encoder_calibration.json) |

## How to run

The simulation and training stack runs offline. The one exception is `fruitfly/axiom.py`: it
attaches to a Chrome window a person has already logged into Axiom and reads Pulse. By default
it runs dry: it logs and screenshots what it would do, and never clicks a buy button, a sell
percentage or a sell confirmation (it does switch a coin page to its Sell tab, which places no
order). Built with
`live=True` and a `fruitfly.risk.RiskGate` that keeps a persistent ledger, and allowed by that
gate at the moment of the click, it clicks Buy and Sell, which spends from that logged-in wallet. It
refuses to click when the row or coin page no longer shows the coin the brain chose, and the
daily loss cap counts ETH in unconfirmed positions as already lost. Nothing in this
repository reads, stores or signs with a private key.

**Prerequisites**

- Python 3.11 or newer.
- A stable Rust toolchain with `cargo`.
- The three MaleCNS v1.0 files from <https://male-cns.janelia.org/download/> (CC BY 4.0), saved
  in one folder: `body-annotations-male-cns-v1.0-minconf-0.5.feather`,
  `body-neurotransmitters-male-cns-v1.0.feather` and
  `connectome-weights-male-cns-v1.0-minconf-0.5.feather`.

**Build and validate** (bash; on Windows use Git Bash or translate the variable syntax)

```
python -m venv .venv
. .venv/bin/activate                                   # Windows: .venv\Scripts\activate
pip install -e ".[test,tools]"
export FRUITFLY_CACHE=/path/to/malecns-v1.0            # the folder holding the three .feather files

python tools/compile_connectome.py                     # signed CSR + meta.json into $FRUITFLY_CACHE/compiled
KERNEL=$(python tools/build_kernel.py --quiet | tail -1)        # builds kernel/, prints the library path
cargo build --release --manifest-path kernel_live/Cargo.toml    # per-neuron input rates, see below
python tools/probe_decoders.py --kernel "$KERNEL" --w-input 4 --ms 500   # sugar -> MN9 validation
python -m pytest
```

Build `kernel_live` as well. Without it, `Simulation` (default `rates="auto"`) silently uses the
legacy `union_max` input mode, which drives every stimulated group at the highest requested
rate and reproduces the superseded behaviour in which the fly held on every decision (see
`docs/MODEL.md`, D7). If the library lives elsewhere, set `FRUITFLY_LIVE_KERNEL`.

Pass `--w-input 4`. `probe_decoders.py` defaults to Shiu's 68.75 mV input, and applied to the
synaptic variable that ignites the whole brain (see `docs/MODEL.md`, section 4).

Most tests load the compiled graph and the built kernels, so run `pytest` after the steps above.

```python
from fruitfly.config import Paths, LifParams, TradeConfig
from fruitfly.connectome import Connectome
from fruitfly.kernel import Simulation
from fruitfly.senses import SensoryEncoder
from fruitfly.motor import MotorDecoder
from fruitfly.market import MarketSim
from fruitfly.train import train_es

conn = Connectome.load(Paths())
sim = Simulation(conn, LifParams(), Paths().kernel)
obs = MarketSim(TradeConfig(), seed=1).reset(n_coins=8)[0]
res = sim.run(SensoryEncoder(conn).encode(obs), ms=500.0, seed=1)
print(MotorDecoder(conn).decide(res, holding=False))

theta = train_es(steps=50, popsize=16, sigma=0.1, lr=0.05, seed=0)   # offline only
```

Export the variables in `.env.example` in your shell; nothing reads `.env` automatically. No
private key belongs in them. The Axiom adapter needs `pip install -e ".[browser]"`; read
`docs/AXIOM.md` before using it.

## Built on

- **MaleCNS v1.0**, the male *Drosophila* central nervous system connectome from HHMI Janelia
  FlyEM with the University of Cambridge, MRC Laboratory of Molecular Biology and Google
  Research ([dataset](https://male-cns.janelia.org/); Berg et al., *Cell* 2026,
  [doi:10.1016/j.cell.2026.08.015](https://doi.org/10.1016/j.cell.2026.08.015)), used under
  [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
- **Shiu et al. 2024** (*Nature*,
  [doi:10.1038/s41586-024-07763-9](https://doi.org/10.1038/s41586-024-07763-9)): the whole-brain
  leaky integrate-and-fire model, its parameters, and the sugar-to-MN9 validation reproduced here.
- **Lappalainen et al. 2024** (flyvis; *Nature*,
  [doi:10.1038/s41586-024-07939-3](https://doi.org/10.1038/s41586-024-07939-3)): the precedent
  for fitting efficacies on fixed wiring.

## License and data

Code is MIT (see `LICENSE`).

The raw MaleCNS v1.0 files are not included. These derived files are, adapted from them (subset
at min-confidence 0.5, grouped by cell type, soma positions quantised to uint16) and shared under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), not under the MIT licence:

- `research/probe_cells.json`, `research/interface_cells.json`, `research/mdn_drivers.json` and
  `research/orn_glomeruli.json`
- `research/reports/connectome_schema.md`
- `site/data/points_u16.bin`, `site/data/points_class_u8.bin` and `site/data/points_meta.json`
- `site/data/research/wiring.json`

Source: the MaleCNS collaboration (HHMI Janelia FlyEM, University of Cambridge, MRC Laboratory
of Molecular Biology, Google Research), <https://male-cns.janelia.org/>; Berg et al., *Cell*,
2026, <https://doi.org/10.1016/j.cell.2026.08.015>. See `CITATION.cff` and
`docs/BIBLIOGRAPHY.md` for full attribution.

fruitfly.trade is an independent project. It is not affiliated with, endorsed by, or officially
connected with Robinhood Markets, Inc., Axiom, pons, HHMI Janelia, the University of Cambridge,
MRC LMB or Google.

This is not financial advice, not a strategy, and not evidence that a fly brain can trade or
learn.
