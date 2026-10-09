# Prior-work search: cross-connectome transfer of the Shiu et al. 2024 LIF model

Search date: 2026-10-09. Every item below has an id/URL that was retrieved during the search. Nothing here is peer reviewed unless it says so; most hits are Zenodo deposits and GitHub repos from Sep–Oct 2026.

## Coverage and limits

- **Citing works, OpenAlex:** all 98 works citing Shiu 2024 (W4403062868) were pulled with cursor paging and every title was screened. The bioRxiv preprint DOI 10.1101/2023.05.02.539144 resolves in OpenAlex to the same record (W4403062868), so it has no separate citation list.
- **Citing works, Semantic Scholar:** all 94 citing records were screened. 27 of them were not in the OpenAlex set, so about 125 unique citing works were screened in total. Abstracts were read for about 30.
- **Keyword searches:** about 16 OpenAlex title/abstract searches (2024-06 onward), one Europe PMC full-text query and the bioRxiv tool. The bioRxiv tool returned only irrelevant recent items.
- **Sources I could not reach:** the arXiv API did not respond and the Zenodo API returned 403. arXiv was covered only through OpenAlex and Semantic Scholar. For Zenodo I used OpenAlex abstracts and the Zenodo web page.
- **GitHub:** about 10 searches. I read the READMEs, and where relevant the docs and pre-registration files, of 14 repos, and scanned two "awesome" lists.
- **Gaps:**
  - Citation indexes lag. Deposits from the last 1–2 weeks are probably under-counted, and new MaleCNS simulation repos appear daily.
  - Google Scholar was not searched.
  - I did not access the full text of the published Berg et al. 2026 *Cell* version. I grepped the local preprint text only.
  - I did **not** independently verify the Berg "0.581" scaling factor quoted in the brief.

## Relevant works

| # | Work (author, date, id) | What it did | Overlap |
|---|---|---|---|
| 1 | Fugsukjit V., "Benchmarking a whole-brain connectome model of Drosophila against experimental data…", Zenodo preprint, 2026-09-29, doi:10.5281/zenodo.23025559; code: github.com/vichienFF/flybrain-connectome-benchmark | Pre-registered NumPy re-implementation of Shiu, validated against Brian2. Scored against Shiu's Supp. Table 3 (104 of the 106 types, with pSG1 and Usnea excluded): balanced accuracy 0.879 **on FlyWire v783 only**. Also scored 17 GtACR1 silencing tests from Supp. Tables 2/5. **Male CNS v1.0:** the unchanged model ran away (about 20,700 neurons active, MN9 181 Hz). Attributed to about 1.8× synapses per cell (692 vs 391 inputs). w_syn rescaled by k = 0.547, then DNge031 and Roundup knockouts tested in the male. | (a) full; (b) mostly full (no shuffled control found); (c) full; (d) **partial: FlyWire only**; (e) partial |
| 2 | Avetisyan S., GitHub issue "Sugar→MN9 path: input synapse counts in BANC v888 ~0.35× FAFB v783", 2026-09-15, github.com/sjcabs/fly_connectome_data_tutorial/issues/4 | Shiu model unchanged on FAFB v783, MaleCNS **v0.9** and BANC v888. Sugar→MN9: 76.7 / 68.9 / 17.8 Hz. Traces the BANC deficit to synapse counts per cell (0.39× FAFB). Global and per-type rescaling tests. | (b) partial (v0.9, no runaway in that setup); (e) full |
| 3 | Silva Santos A.M., "cerebro: exact fast whole-brain Drosophila LIF model, audit and FlyWire vs BANC comparison", Zenodo 2026-09-28, doi:10.5281/zenodo.23005090; github.com/amthedev/cerebro-mosca | Exact Shiu engine. FlyWire vs BANC, matched type by type across 7 BANC versions, with noise and hemisphere controls. Between flies ρ ≤ 0.32. BANC has fewer synapses per neuron and blows up at about 1.4× weight. Per-type calibration restores sugar→MN9. | (a) full; (c) analogous (BANC); (e) full |
| 4 | Mazza G., flymsg, github.com/gianlucamazza/flymsg | Shiu engine checked against Brian2 (r ≥ 0.998). Male median 1.81× synapses over 7,327 matched types. w_syn density-scaled. Same model on male and female for sugar→MN9 and other pathways. Controls use random similar neurons, not shuffled wiring. | (a) full; (b) partial; (c) full; (e) full |
| 5 | Cho B. (brandoncho369), flybench, doi:10.5281/zenodo.22886374; github.com/brandoncho369/flybench | 36 pre-registered tasks on FlyWire v783 and MaleCNS v1.0, with **shuffled-wiring controls on every task**, including sugar→MN9. Global-gain sweeps: on MaleCNS no gain does taste and vision together, and at 0.65 "the network never quiets". No Supp. Table 3 / split-GAL4 screen (grep of README, FINDINGS and LEADERBOARD). | (b) full incl. shuffle; (c) partial; (e) full |
| 6 | Kisame76, drosophila-brain-mlx, github.com/Kisame76/drosophila-brain-mlx | MLX port of Shiu, run on FlyWire v630 and MaleCNS v1.0. Degree-preserving shuffle: MN9 silent on the shuffled copy. The README shows the shuffle demo on v630. | (a) full; (b) partial |
| 7 | Aldunate Rodríguez F.J., "Embodied whole-CNS emulation of Drosophila…", Zenodo 2026-09-27, doi:10.5281/zenodo.23004436 | LIF on MaleCNS v1.0 plus NeuroMechFly. Reproduces the published implementation (r = 0.999). Sugar-evoked feeding emerges. Degree-preserving shuffle control. Weight scaling not stated in the abstract. | (a) full; (b) partial |
| 8 | Smarygin A.A., "Persistent position-specific bump activity… cross-connectome replication…", Zenodo 2026-10-01, doi:10.5281/zenodo.23085647 | Central-complex LIF bump on MaleCNS, replicated on FlyWire v783, with a degree-preserving null. | (e) full (different circuit) |
| 9 | Wang Y., "Packaging choices change connectome-simulation outcomes…", Zenodo 2026-09-27, doi:10.5281/zenodo.22998483 | One LIF core on FlyWire v783 and MaleCNS. A glutamate sign flip switches whole-brain runaway regimes. Weight-scheme dependence. | (c) related; (e) partial |
| 10 | Shibusawa R., "Approximate graph-fibration symmetry in connectome-constrained neural networks", SSRN doi:10.2139/ssrn.7537393; code doi:10.5281/zenodo.22846083 | Independent LIF with Shiu constants on MaleCNS v1.0 and FlyWire v783, with shuffle interventions. | (e) partial |
| 11 | An D., "How sparse can a fly-brain model be?…", bioRxiv 2026-09-24, doi:10.64898/2026.09.19.752860 | Shiu model on FlyWire. Sugar→MN9 under degree-preserving rewiring and weight shuffling: output abolished. | (b) shuffle control, FlyWire only |
| 12 | Pugliese S.M. et al., "Connectome simulations identify a central pattern generator circuit for fly walking", bioRxiv 2025-09-12, doi:10.1101/2025.09.12.675944 | VNC simulations. Walking circuit found in four connectome datasets. Experimental optogenetic confirmation of one predicted descending pathway. | (e) full (VNC) |
| 13 | Guan I.Y.N. et al., "How much of fly walking is written in the wiring?", arXiv:2609.38665, 2026-09-29 | Two independent connectomes, each compared against six families of rewired networks, with pre-registered criteria. | (e) full (VNC) |
| 14 | Scheffer L.K., "Synapse Detection Efficiency in EM Drosophila Connectomics", bioRxiv 2025-10-19, doi:10.1101/2025.10.16.682869 | FIB-SEM volumes (male CNS among them) show more human-visible synapses than SS-TEM, "typically by more than 40%". | (c) explains density gap |
| 15 | Smarygin A.A., "Neurotransmitter sign and source-column errors… MaleCNS v1.0", doi:10.5281/zenodo.22975836 | Audit of NT-to-sign mapping in MaleCNS simulation pipelines. | (b)/(c) confound to control |
| 16 | Bates A.S. et al., BANC, *Nature* 2026, doi:10.1038/s41586-026-10735-w (PMC13518251) | Full text grepped: uses a **linear rate model**, not the Shiu LIF. | none |
| 17 | Berg S. et al., male CNS preprint, doi:10.1101/2025.10.09.680999 (local text S3pre) | Cites Shiu only as future work ("in silico may be used…"). No simulation found. | none (published *Cell* version not checked) |
| 18 | Tastekin I. et al., gustatory connectome, bioRxiv doi:10.1101/2025.08.25.671814 (*Cell* doi:10.1016/j.cell.2026.08.016) | Male CNS taste pathways to MN9 via "effective connectivity" scores. No LIF found in the preprint text. | none / context |
| 19 | spider2449/MaleCNS-Sim (github.com/spider2449/MaleCNS-Sim) | Reproduces Shiu v630 sugar→MN9. MaleCNS engine. Reports MN9_L/MN9_R input asymmetry (6,012 vs 556). | (a) |

Screened and judged not relevant (application, game or learning repos, reviews, unrelated circuits) include the roughly 60 MaleCNS demo repos on github.com/townie/awesome-fruit-fly, Lappalainen 2024, Li et al. 2026 (doi:10.64898/2026.08.21.745055, FlyWire only), and Cho et al. arXiv:2610.10014 (trained, not LIF).

## Verdict per contribution

- **(a) Reproducing Shiu with their code: ALREADY DONE**, many times. Fugsukjit, flymsg (Mazza), cerebro (Silva Santos), Aldunate Rodríguez, Kisame76 and MaleCNS-Sim all report it. It belongs in Methods as a sanity check. It is not a contribution.

- **(b) Unchanged model on Male CNS v1.0, sugar→MN9, with a shuffled-wiring control: ALREADY DONE.**
  - Unchanged model on MaleCNS v1.0: Fugsukjit (Zenodo 23025559 / malecns/REPLICATE_PLAN.md).
  - MaleCNS sugar→MN9 with shuffled-wiring controls: flybench (Cho), across gains.
  - Degree-preserving shuffle on MaleCNS: Aldunate Rodríguez.
  - Unchanged model on MaleCNS v0.9: Avetisyan.

  At most ours would be a confirmation.

- **(c) Runaway at default weights, explained by synapse density: ALREADY DONE.**
  - Fugsukjit reported exactly this: about 20,700 active neurons, explained by about 1.8× synapses per cell, then recalibrated w_syn.
  - flymsg reports 1.81× and density-scales w_syn.
  - flybench reports that MaleCNS at gain 0.65 "never quiets".
  - Scheffer gives the imaging-method explanation (FIB-SEM sees >40% more synapses).

  **Caution:** Avetisyan got MN9 68.9 Hz with *no* reported runaway on MaleCNS v0.9 (Lee-lab edgelist, 27 right sugar GRNs, 150 Hz). Whether runaway happens depends on version, stimulus set and sign table. A claim of "runaway at default weights" must state those conditions.

- **(d) Scoring the transferred male-CNS model against Shiu's Supp. Table 3 split-GAL4 screen: PARTIALLY DONE. The male-CNS scoring itself was not found.**
  - Fugsukjit scored Table 3 (104 types, balanced accuracy 0.879) on **FlyWire only**. He explicitly calls that a replication of Shiu's own comparison.
  - His male-CNS runs covered only DNge031, Roundup and Usnea knockouts, not Table 3. This is confirmed from his BENCHMARK_V2_PLAN.md (models D0/D0U/D2, all FlyWire) and REVISION_PLAN.md.
  - flybench, flymsg and cerebro do not use the split-GAL4 screen.
  - Novelty is therefore narrow and fragile. Fugsukjit already has the Table-3 neuron mapping (`literature/shiu2024_supp/sez_neurons_783.json`), a calibrated male model, and commits as recent as 2026-10-06. Re-check his repo and Zenodo immediately before any release.
  - If we proceed, credit Fugsukjit for the FlyWire Table-3 benchmark, the male runaway and the k-calibration, and frame ours as extending his benchmark to a second connectome.

- **(e) Comparing LIF/connectome model predictions across connectomes: ALREADY DONE** in several forms:
  - FlyWire vs BANC, type by type: Silva Santos.
  - FAFB / MaleCNS / BANC sugar→MN9: Avetisyan.
  - Male vs female: flymsg.
  - Two-connectome benchmark: flybench.
  - CX bump on MaleCNS and FlyWire: Smarygin.
  - VNC walking: Pugliese et al. and Guan et al.

  None of these scores cross-connectome predictions against the Table-3 behavioural screen. That gap is the same one as (d).

## Bottom line

Only (d) survives, and only in a narrow form: "the Shiu split-GAL4 sufficiency benchmark, re-scored on a second, independently reconstructed connectome". Everything else, (a), (b), (c) and the general idea in (e), has named prior work from the last six weeks, all of it non-peer-reviewed. Per AGENTS.md, any write-up must credit Fugsukjit, Mazza (flymsg), Cho (flybench), Silva Santos (cerebro), Avetisyan and Aldunate Rodríguez by name, and call (b) and (c) confirmations.
