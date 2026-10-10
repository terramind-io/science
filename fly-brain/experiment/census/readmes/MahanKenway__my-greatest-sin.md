# My Greatest Sin

> **A dual-species connectome observation bench for separating source data, explicit modelling, and honest uncertainty.**

**My Greatest Sin** is a browser-first React, Babylon.js and TypeScript project for studying bounded sensorimotor hypotheses around adult *Drosophila* FlyWire data and the *C. elegans* connectome. It is not a claim that a living animal, awareness, whole-body control, or biologically validated walking has been recreated.

## Scientific status

| System | Source topology | What currently executes | What remains modelled or blocked |
|---|---:|---|---|
| *C. elegans* | 279 neurons / 6,261 edges | Checksum-verified source topology runs in the browser | Sensor routing, motor grouping and the body wave are `MODELLED MAPPING` |
| FlyWire v783 | 139,255 proofread roots / 16,847,997 connection rows | Official data, CSR derivatives, site-level sign extraction and bounded offline corridors are verified outside the repository | `GameWorld` remains **0 N / 0 E** until a valid WebGPU run and separate scientific validation pass |
| Fly body | Apache-2.0 source derivative with real presentation pivots | Garden presentation and isolated mouthpart rig | Gait, wings, root movement and all displayed body output remain modelled; no FlyWire result controls them |

The current browser exposes `navigator.gpu`, but the target environment rejects `requestAdapter()`. The application therefore blocks real FlyWire execution rather than inventing a full-graph CPU fallback, a timing value, neural activity, or body command.

The site-level sign/weight LIF panel is a **readiness and settings surface**, not evidence of a dispatched full-brain model. Its release-783 sign derivative records 94,640 excitatory, 44,011 inhibitory and **604 unclassified** proofread neurons after the documented `cleft_score ≥ 50` source rule. Those unresolved signs block any full signed-LIF dispatch before device allocation; they are never silently assigned a sign. The panel’s 0.05–0.50 mV weight and 0–500 input-scale controls are explicitly `MODELLED` settings for a future gated experiment and do not drive FlyBody, walking, wings, or `GameWorld`. The UI keeps counters, a compact budget and bounded charts rather than rendering 139,255 nodes or 16,847,997 edges. [3] [6]

## Public deployment and scoped completion

The public static release is available at **[my-greatest-sin.pages.dev](https://my-greatest-sin.pages.dev/)**. Cloudflare Pages deploys the self-contained `gh-pages` artifact. The artifact contains the application, presentation assets, both specimen bodies, and the five checksum-verified chunks required to hydrate the C. elegans source topology; it does not distribute the large FlyWire v783 pack.

The public controls are operable with buttons or keyboard: `Space` toggles pause, `1` selects FlyWire staged, `2` selects C. elegans live, `R` resets the active specimen, and `D` toggles the demo. Keyboard shortcuts ignore form controls and do not create a new simulation policy. Cosmetic animation respects `prefers-reduced-motion`.

For C. elegans, the **DECODER READOUT CHECK** provides `NONE`, `MASK DB`, and `MASK VB`. It masks only the selected DB/VB contribution after source activity is read and before the disclosed motor decoder maps it to the display body. It does not modify the source topology, neuron state, body policy, or constitute biological ablation.

## Bounded CPU validation, not a full-graph fallback

The HUD provides one separate **CPU OFFLINE SUBGRAPH VALIDATION** control for a checksum-verified sugar corridor stored outside the repository. It fetches only **1,115 nodes / 13,346 signed edges**, verifies SHA-256 `237e23b3f2ea9a32cc9650aadc376b348f0d98ecdcd9c24242c4a54cd1322c67`, enforces hard browser caps of 2,000 nodes and 25,000 edges, and performs four signed structural-propagation steps. The readout is deliberately **not LIF**, a firing rate, an animal measurement, a WebGPU benchmark, or a FlyBody command.

With the live UI’s modelled sugar input open at 150 Hz, the current pack produced an MN9 structural score of `0.0016`; with the same input-ablation control closed, it produced `0.0000`. These observations validate only checksum delivery and bounded structural propagation. `GameWorld` stays at **0 N / 0 E** for FlyWire and the body remains display gait.

## What has been validated

The project stores raw FlyWire v783 files and derived binary packs **outside this repository**. Downloaded official inputs, chunk manifests, site-level transmitter predictions, annotation releases and output reports carry checksums and provenance. JavaScript FlyWire root IDs remain strings or `BigInt`; they are never converted to unsafe `Number` values.

Three bounded, offline LIF investigations use official v783 structure, site-level neuron signs and the published Shiu model constants. They are scientific **structural-model validations**, not animal recordings or full-brain results.

| Input population | Bounded corridor to MN9 | Offline outcome | Interpretation boundary |
|---|---:|---|---|
| Right labellar sugar GRNs | 1,115 nodes / 13,346 edges | Modelled MN9 response rises across the protocol; input-ablation is zero | Modelled Poisson input and Forward-Euler solver; not a FlyBody command |
| Right labellar water GRNs | 961 nodes / 11,231 edges | Distinct modelled MN9 response; input-ablation is zero | Same bounded approximation; not water perception or drinking |
| Right Johnston-organ JO-A mechanoreceptors | 787 nodes / 5,741 edges | MN9 is zero at all tested rates | A limited negative result for this selected auditory/mechanosensory corridor only |

The selected **sugar-GRN → MN9 / proboscis** pilot is the first embodiment target because its feeding circuit has a better documented FlyWire boundary than descending-neuron-dependent locomotion. Food encoding and MN9-to-mouthpart conversion are visibly labelled `MODELLED SENSOR INPUT` and `MODELLED MOTOR DECODER`; walking, wings and root movement are excluded by design.

## Architecture

```text
Official FlyWire v783 / pinned annotations
        │  checksums + version pinning
        ▼
External binary DFLY packs and site-level artifacts
        │
        ├── Browser: integrity-gated WebGPU benchmark → currently adapter-blocked
        └── Offline/server research: bounded signed corridor → LIF protocol → raw reports
                                                            │
                                                            └── never feeds FlyBody automatically
```

The production UI is static. A future server-side path should keep large immutable columns in object storage, run experiments in a GPU worker, record seeds/checksums/versions through a small API, and return only experiment results to the UI. A relational database such as Neon may catalogue runs and metadata; it is not a GPU simulator.

## Run locally

Use Node.js 22 and pnpm.

```bash
pnpm install --frozen-lockfile
pnpm check
pnpm test
pnpm dev
```

For a production bundle:

```bash
pnpm build
pnpm preview
```

The app can be opened in a modern browser. WebGPU must provide a genuine adapter before any official FlyWire GPU execution is allowed. The UI always displays whether a result is source-derived, modelled, staged, blocked or a synthetic numerical fixture.

## Data workflow

Do not place raw FlyWire data in `client/public`, the project tree, or Git history. The project provides external-only processing tools under [`scripts/data-processing`](scripts/data-processing), including:

| Tool | Purpose |
|---|---|
| `download_flywire_v783_official.sh` | Resumable official connectivity download with published MD5 verification |
| `download_flywire_v783_site_level.sh` | Official site-level table containing cleft scores and transmitter predictions |
| `build_flywire_v783_pack.py` | Builds checksum-bearing CSR packs outside the repository |
| `build_flywire_v783_neuron_signs.py` | Derives neuron-level excitatory/inhibitory signs from site-level data under the documented rule |
| `extract_sugar_mn9_four_hop_corridor.py` | Extracts bounded source-structural corridors to MN9 |
| `build_bounded_cpu_corridor_pack.py` | Converts one signed, bounded corridor into the CPU-only JSON contract with hard caps and provenance |
| `run_sugar_mn9_offline_subgraph_lif.py` | Runs a seeded offline LIF protocol without touching `GameWorld` |
| `run_v783_corridor_brian2cuda.py` | CUDA-only prototype using the reference Brian2 equations; it has no CPU fallback |

Every experimental report must retain the source release, annotation revision, input checksum, code revision, random seed, trial count and explicit modelling assumptions.

## Research roadmap

The next credible milestones are annotation-pinned labellar/pharyngeal mechanoreceptors, a separately documented olfactory population, a GPU worker run using Brian2CUDA on compatible NVIDIA hardware, and an independent comparison against the reference Brian2 integration. The literature-defined cibarial md-C pathway stays **blocked** until an authenticated, version-aligned root-ID crosswalk can link md-C and its correct MN11/MN12 targets to v783; it must not be substituted with broad pharyngeal candidates or routed to MN9. Full-body locomotion remains a later and harder question because relevant descending-neuron pathways are incomplete in FlyWire.

See the project records for detail:

- [`docs/FLYWIRE_ACTIVATION_PATH.md`](docs/FLYWIRE_ACTIVATION_PATH.md) — end-to-end v783 activation gates.
- [`docs/FLYWIRE_LIF_MODEL_BOUNDARY.md`](docs/FLYWIRE_LIF_MODEL_BOUNDARY.md) — LIF assumptions, transmitter signs and corridor results.
- [`docs/FLYWIRE_SITE_LEVEL_LIF_READINESS.md`](docs/FLYWIRE_SITE_LEVEL_LIF_READINESS.md) — sign coverage, settings contract, buffer budget and the full-dispatch gate.
- [`docs/FLYWIRE_SENSORY_EXPANSION.md`](docs/FLYWIRE_SENSORY_EXPANSION.md) — source versus modelled sensory expansion.
- [`docs/GITHUB_FLYWIRE_OPTIONS.md`](docs/GITHUB_FLYWIRE_OPTIONS.md) — reviewed query and GPU/server options.
- [`docs/BRIAN2CUDA_NVIDIA_RUNBOOK.md`](docs/BRIAN2CUDA_NVIDIA_RUNBOOK.md) — pinned NVIDIA/Colab smoke-test path and its hardware gates.
- [`docs/MD_C_CROSSWALK_SEARCH.md`](docs/MD_C_CROSSWALK_SEARCH.md) — multi-source md-C/MN11/MN12 search and exact crosswalk blocker.
- [`ASSETS.md`](ASSETS.md) — asset, license and scientific-boundary manifest.

## Attribution and licences

Original project code is licensed under the repository licence. FlyWire data, public annotations, reference models and presentation assets retain their own terms; they are not relicensed by this repository. Use release-specific citation guidance and preserve every source’s licence before sharing an experiment or derivative.

## References

[1]: https://doi.org/10.1038/s41586-024-07558-y "Dorkenwald et al. (2024), Neuronal wiring diagram of an adult brain"

[2]: https://doi.org/10.1038/s41586-024-07686-5 "Schlegel et al. (2024), Whole-brain annotation and multi-connectome cell typing of Drosophila"

[3]: https://pmc.ncbi.nlm.nih.gov/articles/PMC11446845/ "Shiu et al. (2024), A Drosophila computational brain model reveals sensorimotor processing"

[4]: https://github.com/flyconnectome/flywire_annotations "FlyWire systematic annotations for release 783"

[5]: https://github.com/navis-org/fafbseg-py "fafbseg-py"

[6]: https://zenodo.org/records/10676866 "FlyWire Whole-brain Connectome Connectivity Data, release 783"
