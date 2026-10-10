# Pre-registration: same simulation, different fly

**Registered:** 9 Oct 2026, before any simulation with a stimulus was run. The only run before this file was written was `BENCH_mcns_nostim`: male CNS, no stimulus, 100 ms, used for timing only. With no input it carries no information about any hypothesis below.
**Tracked as:** GROW-109 · **Video:** 01 (fly brain) · **Status:** our own analysis, not peer-reviewed.

## Question

Shiu et al. 2024 (*Nature*, doi:10.1038/s41586-024-07763-9) built a leaky integrate-and-fire model of one female fly brain (FlyWire v630). In it, activating sugar-sensing taste neurons drives MN9, the motor neuron that lifts the proboscis to feed. With shuffled wiring, it doesn't.

**Does that prediction survive a different fly?** We run the *same model, unchanged*, on the male CNS v1.0 connectome (Berg et al. 2026, *Cell*, doi:10.1016/j.cell.2026.08.015). That's a different individual and a different sex, mapped with a different microscope and pipeline. The question is whether sugar input still drives MN9, and whether shuffled wiring still kills it.

## Materials (fixed before results)

| Item | Detail |
|---|---|
| Model | `vendor/Drosophila_brain_model/model.py`, Shiu et al.'s MIT-licensed repo at commit `91bdd1e7dcf193f3e7ca5a8933497fcef63b7960`, **unmodified**. All parameters at their defaults (w_syn 0.275 mV, 1,000 ms trials). Stimulus is Poisson input at **100 Hz**, the rate the paper uses for its shuffle test. |
| FlyWire v630 | The repo's own files `2023_03_23_completeness_630_final.csv` and `2023_03_23_connectivity_630_final.parquet` (127,400 neurons) |
| FlyWire v783 | The repo's own `Completeness_783.csv` and `Connectivity_783.parquet`. Cell types come from `flyconnectome/flywire_annotations` Supplemental_file1. |
| Male CNS v1.0 | `body-annotations`, `body-neurotransmitters` and `connectome-weights` (minconf 0.5) from male-cns.janelia.org (CC-BY). SHA-256 hashes are in `data/malecns/SHA256SUMS`. Converted to Shiu's format by `code/prepare_inputs.py`, which gives **165,122 neurons and 25,563,096 edges**. |
| Readout | MN9. In FlyWire it is `CB0701`, the type the male CNS annotations themselves give as MN9's `flywireType`. FlyWire v630/v783 contralateral MN9 is `720575940660219265`, the ID used in the paper's notebooks. Male CNS: `16949` (MN9_R) for left-side input, `10331` (MN9_L) for right-side input. |

### Stimulus sets (built from annotations only; see `inputs/stimuli.json`)

| Set | Definition | n |
|---|---|---|
| `fw630 shiu` | Shiu et al.'s exact 21 GRN IDs | 21 |
| `fw783 typeset` | All FlyWire GRNs of types LB3b, LB3c, LB3d and LB4b on the side of Shiu's GRNs (FlyWire `side` = left). These are the types that make up Shiu's 21 in the current annotations. | 52 |
| `mcns typesetL` | The same four types, male CNS, `rootSide` = L | 32 |
| `fw783 sugaronly` / `mcns sugaronlyL` | Only LB3b and LB3c, the annotated sugar and sugar/low-salt classes | 33 / 17 |
| `mcns typesetR` | The four types on the right side, read out at MN9_L | 36 |

**Pre-results observation** (from annotation tables, no simulation): in today's FlyWire annotations, Shiu's 21 "sugar" GRNs break down as follows. 20 of 21 IDs are still present in v783.

| Type | Count | FlyWire subclass |
|---|---|---|
| LB3c | 9 | sugar |
| LB3b | 2 | sugar/low_salt |
| LB4b | 4 | putative_attractive |
| LB3d | 5 | high_salt/heavy_metal |

Annotations have been refined since the paper, and this is why we also run the type-defined and sugar-only sets.

## Conditions

| ID | Dataset | Stimulus | Trials | Wiring |
|---|---|---|---|---|
| E1 | FlyWire v630 | Shiu 21 | 30 | real |
| E2 | FlyWire v630 | Shiu 21 | 100 | **shuffled**, one independent permutation per trial |
| E3a | FlyWire v783 | typeset | 30 | real |
| E3b | Male CNS | typesetL | 30 | real |
| E4 | Male CNS | typesetL | 100 | **shuffled** |
| S1a / S1b | FlyWire v783 / male CNS | sugar-only | 30 / 30 | real |
| S2 | Male CNS | typesetR → MN9_L | 30 | real |

**Shuffle procedure:** the signed weights (synapse count × sign) are randomly permuted across the existing edges. The graph topology and the global weight distribution stay the same. The paper says weights were "shuffled randomly (while maintaining the global connectivity weight distribution)" and gives no further procedure, so this is our reading of it.

**Seeds:** fixed per trial (stored in each result's `.json`) for both the Brian2 Poisson input and the permutation.

## Definitions

- **MN9 active in a trial:** at least 1 MN9 spike in the 1,000 ms trial.
- **Rate:** spikes divided by 1 s, averaged over trials. Reported as mean ± s.d.

## Hypotheses and decision rules (fixed now)

| | Hypothesis | Supported if | Not supported if | Otherwise |
|---|---|---|---|---|
| **H1** (replication) | E1: Shiu's model on Shiu's data drives contralateral MN9 | MN9 active in ≥29/30 trials **and** mean rate within ±25% of the authors' archived run `vendor/.../results/example/sugarR_100Hz.parquet` (same ID, same rate) | MN9 active in ≤15/30 | inconclusive |
| **H2** (shuffle replication) | E2: shuffled wiring kills it | MN9 active in ≤5/100 shuffles **and** Fisher's exact test vs E1 has p < 0.001 | ≥20/100 | inconclusive |
| **H3** (transfer: the headline) | E3b: the same model on the male CNS drives contralateral MN9 | active in ≥27/30 trials | active in ≤3/30 | partial (reported as such) |
| **H4** (shuffle in the male fly) | E4 | ≤5/100 **and** Fisher p < 0.001 vs E3b | ≥20/100 | inconclusive |
| **D1** (does the whole response transfer?) | Type-level correlation of responses, E3a vs E3b | Spearman ρ (real vs real) exceeds ρ (E3a vs E4-pooled shuffled) by ≥ 0.2 | difference ≤ 0 | weak |

**D1 method.** For each neuron, take the mean rate over trials. Collapse to types using FlyWire `cell_type` on one side and male CNS `flywireType` on the other (the male dataset's own cross-match). Keep types present in both datasets that fire in at least one of the two conditions being compared. Compute Spearman ρ across those types. Also report the overlap (Jaccard) of the top-50 most active types. Stimulated GRNs are excluded.

**Secondary (descriptive, no decision rule):**
- S1 (sugar-only stimulus in both flies)
- S2 (other side of the male fly)
- MN9 rate in the female vs male flies

## Known deviations from the paper (declared up front)

1. Brian2 2.7.1 with Cython 3.0.12 and Python 3.11. The paper's environment specifies Brian2 2.5.1.
2. **Male CNS sign rule:** a neuron is inhibitory if its neuron-level `predicted_nt` is GABA or glutamate. The paper's rule is ">50% of presynaptic sites predicted GABA or Glu". This is close, but not identical. All other transmitters, including histamine and unknowns, are excitatory, as in the paper.
3. **Male CNS inclusion:** bodies with `status == 'Traced'` only, and no self-loops.
4. **Shuffle procedure:** as above (our interpretation).
5. **Side naming:** FlyWire's `side` field calls Shiu's GRNs "left", while the paper's notebooks call them "sugarR". We follow the data tables and always read the contralateral MN9.

## What goes in the video regardless of outcome

- A **replication** result for H1 and H2, and a **transfer** result for H3, H4 and D1.
- If H3 fails, that becomes the story ("the model of one fly doesn't transfer to another"). We'd report it without re-tuning parameters.
- **No post-hoc changes.** Any extra analysis we add after seeing results is labelled *exploratory*.
