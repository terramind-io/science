# flypoke

Poke a neuron in the fruit fly brain and watch what fires.

`flypoke` is a small, dependency-light leaky integrate-and-fire (LIF) simulation of
the **entire adult *Drosophila* brain** built directly on the public
[FlyWire](https://flywire.ai) connectome (release 783, ~139,000 neurons,
~2.7 million synaptic connections). It runs on a laptop CPU in seconds per
trial, no GPU or Brian2 required.

The model reproduces the headline result of
[Shiu et al. 2024, *Nature*](https://doi.org/10.1038/s41586-024-07763-9):
driving the fly's sugar-sensing taste neurons is enough to activate the
proboscis motor neuron **MN9** that extends the proboscis to feed, and
co-activating bitter-sensing neurons suppresses it. Nothing about feeding is
encoded in the model; it falls out of the wiring diagram alone.

## Quick start

```bash
git clone https://github.com/vshapenko/flypoke
cd flypoke
uv sync                      # or: pip install -e .
uv run flypoke download      # ~850 MB from Zenodo + GitHub (one time)
uv run flypoke feeding       # the sugar -> MN9 experiment
```

The first simulation builds and caches the sparse weight matrix (about a
minute). After that, a 1-second trial of the whole brain takes a few seconds.

## What it does

```
$ flypoke poke --stim "cell_sub_class=sugar/water" --rate 150 --trials 5 \
                --watch "cell_sub_class=ingestion_motor_neuron"
```

Stimulated neurons are driven with independent Poisson spike trains. Spikes
propagate through the signed connectome with a 1.8 ms delay; each synapse
adds 0.275 mV of exponentially decaying input, positive for cholinergic,
dopaminergic, serotonergic and octopaminergic presynaptic neurons, negative
for GABAergic and glutamatergic ones. The command prints the most active
downstream neurons with their FlyWire annotations (cell class, type, side,
transmitter), a breakdown by super class, and any neurons you ask to watch.

Neurons are selected by annotation columns from Schlegel et al. 2024
(`super_class`, `cell_class`, `cell_sub_class`, `cell_type`,
`hemibrain_type`, `side`, `top_nt`, ...) or by explicit root ids:

```
--stim "cell_sub_class=sugar/water,side=left"        # AND of clauses
--stim "cell_class=olfactory|gustatory"               # OR within a clause
--stim "root_id=720575940624963786,720575940630233916"
--silence "cell_type=CB0701"                          # cut a neuron's outputs
```

Use `flypoke find bitter` to discover selector values.

## Results

`flypoke feeding` drives the 129 sugar/water gustatory receptor neurons, the
65 bitter ones, or both, at 150 Hz for 1 s (5 trials, seed 0), on a
2023 laptop CPU in about 40 s total:

| condition       | MN9 right (Hz) | MN9 left (Hz) | all 28 ingestion MNs, mean (Hz) | other neurons above 1 Hz |
|-----------------|---------------:|--------------:|--------------------------------:|-------------------------:|
| sugar           |          150.0 |         111.6 |                            56.2 |                      439 |
| bitter          |            0.0 |           0.0 |                             0.0 |                      529 |
| sugar + bitter  |           14.4 |           8.8 |                            40.4 |                      419 |

Sugar input alone drives MN9 at about 150 Hz (Shiu et al. report ~120-150 Hz
at this stimulation rate in release 630). Bitter input alone reaches 529
neurons but no ingestion motor neuron. Adding bitter to sugar cuts MN9 by
an order of magnitude, the connectome-level signature of bitter suppressing
feeding.

`flypoke poke --stim "cell_sub_class=sugar/water"` shows the pathway. Of
139,248 neurons, 439 fire; almost all are in the central brain, descending
neurons and motor neurons, and the most active are the ingestion motor
neurons themselves, two levels downstream of the sensory input:

```
 rate_hz  root_id             super_class  cell_class          cell_sub_class          cell_type  side   top_nt
   235.8  720575940618165019  motor        brain_motor_neuron  ingestion_motor_neuron  CB0700     left   acetylcholine
   231.0  720575940630868793  motor        brain_motor_neuron  ingestion_motor_neuron  CB0700     right  glutamate
   223.4  720575940622695448  central                                                  CB0248     right  gaba
   213.8  720575940627383685  central                                                  CB0248     left   gaba
   211.4  720575940655014049  ascending    AN                  AN_GNG                  AN_GNG_30  left   acetylcholine
   206.8  720575940629888530  central                                                  CB0192     left   acetylcholine
   203.4  720575940629778554  motor        brain_motor_neuron  ingestion_motor_neuron  MNx01      right  glutamate
   195.2  720575940616103218  central                                                  CB0062     left   gaba
   192.8  720575940640589171  descending                                               DNge031    left   gaba
   190.8  720575940632648612  central                                                  CB0008     left   gaba

 super_class          n   mean Hz  max Hz
 central            322      43.9   223.4
 descending          69      44.5   192.8
 motor               26      98.2   235.8
 ascending           10      79.9   211.4
 visual_centrifugal   7       8.6    15.6
 sensory              5      52.2    71.4
```

For scale, poking all 2,282 olfactory receptor neurons at once lights up
7,753 neurons across the central brain, descending neurons and even the
optic lobes (`flypoke poke --stim "cell_class=olfactory" --trials 2`).

Full per-neuron rate tables can be written with `--out results/x.csv`. Rates
above are single-model numbers with no free parameters fitted to this data.

## Model

Constants and equations are those of Shiu et al. 2024
([code](https://github.com/philshiu/Drosophila_brain_model)):

| parameter | value |
|---|---|
| resting / reset potential | -52 mV |
| threshold | -45 mV |
| membrane time constant | 20 ms |
| synaptic time constant | 5 ms |
| refractory period | 2.2 ms |
| synaptic delay | 1.8 ms |
| weight per synapse | 0.275 mV |
| minimum synapses per connection | 5 |
| integration step | 0.1 ms |

Differences from the original: integration is exponential Euler in NumPy
rather than Brian2's exact linear solver, and stimulated neurons emit their
Poisson spikes directly instead of receiving a supra-threshold Poisson input
(equivalent, since in the original every Poisson event forces a spike).
Transmitter signs come from the per-neuron `top_nt` prediction in the
annotation table. The model uses release 783; Shiu et al. used release 630,
so root ids and exact rates differ slightly.

## Data

* Dorkenwald et al. 2024, *Nature* 634:124-138. Neuronal wiring diagram of an adult brain.
  Connection table from [Zenodo 10676866](https://doi.org/10.5281/zenodo.10676866).
* Schlegel et al. 2024, *Nature* 634:139-152. Whole-brain annotation and multi-connectome cell typing.
  Annotations from [flyconnectome/flywire_annotations](https://github.com/flyconnectome/flywire_annotations).
* Eckstein et al. 2024, *Cell* 187:2574-2594. Neurotransmitter classification from EM.
* Shiu et al. 2024, *Nature* 634:210-219. A *Drosophila* computational brain model reveals sensorimotor processing.

FlyWire data are released under CC BY 4.0. Set `FLYPOKE_DATA` to keep the
data somewhere other than `./data`.

## License

MIT
