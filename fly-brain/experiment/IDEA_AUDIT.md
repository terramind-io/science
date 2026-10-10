# Audit of four paper ideas (10 Oct 2026)

Four search agents audited prior work and feasibility, one per idea, using live fetches on 10 Oct 2026. Unless marked "we verified", records below are **as reported by those agents and not re-fetched by us**. Most of the closest work is GitHub repos, Zenodo deposits and preprints, not peer-reviewed. Nothing here is cleared for publication.

## Idea 1. Map versus simulation: appears open, and it grew into a sharper question

**Question:** what does simulating the brain add over reading the wiring map, when scored against real flies?

- **Not found:** any paper, preprint or repo scoring a no-simulation predictor against the Shiu model on real-fly results.
- **Shiu et al. shipped the simplest such predictor and never analysed it.** Supplementary Table 3 has a "Shortest Path" column (steps from each cell type to MN9). **We verified** from the supplement: 13 of the 14 real-fly positives are within 2 steps; ranking the 106 types by step count alone gives AUROC 0.771, against 0.853 for the simulation's 50 Hz rates and 0.804 for our 3-step path score. A yes/no rule "within 2 steps" is poor (13 hits, 42 false alarms, accuracy 0.594), so the comparison is about ranking, not about that rule.
- **Shiu's own argument** (Discussion): graph methods "measure traversal length, rather than a measure of activation, they are unlikely to be useful for predicting what neurons contribute most to a given circuit." Asserted, not tested. They also state: "Excluding our optogenetic split-GAL4 experiments (Fig. 2), in which the vast majority of cell types did not elicit MN9 activation, the accuracy of the model is 84%".
- **Closest prior work:** suifei/flywire-fly-lab (GitHub, HEAD `776442e`, 22 Sep 2026): wiring metrics against the simulation's own knockout effects (not real flies), concludes the model must be run. Fly.exe "cell-type-only" control (still a simulation; 0.7972 vs 0.8077, "almost no power"). Bates et al. 2026 (doi:10.1038/s41586-026-10735-w) linear "influence" score, not scored against behaviour or against the Shiu model. Yin et al. 2025 (doi:10.1101/2025.09.29.679410), Pospisil et al. 2024 (doi:10.1038/s41586-024-07982-0), Xie et al. 2025 (arXiv:2512.06934), Asis 2026 (doi:10.5281/zenodo.23120920).
- **Related fact from the idea-3 audit (not yet verified by us):** about 10 of the 14 positives were already published as positives before the simulation (mainly Shiu, Sterne et al. 2022, doi:10.7554/elife.79887; Flood et al. 2013, doi:10.1038/nature12208; Marella et al. 2012, doi:10.1016/j.neuron.2011.12.032). The Nature paper itself says "four of these neurons had been shown previously to be sufficient for proboscis extension". The exact count needs Shiu 2022 Figure 1D read by us.
- **Objections a specialist will raise:** (1) our path score is itself a crude rate model, so the claim is "a far cruder model does about as well", not "no simulation"; (2) 14 positives cannot show equivalence; (3) the screen is the easy case and the paper claims the simulation's value for interactions and silencing; (4) we chose k = 3 on the test set; (5) noisy labels; (6) this is criticism of a Nature paper, so the authors should see it first.
- **Held-out data available:** 58 non-screen test cases in Shiu's supplement (sugar/water responders and silencing, bitter and Ir94e interactions, grooming), small and overlapping; the male map's 99 types; external screens (Cande et al. 2018, doi:10.7554/eLife.34275, descending neurons) not yet checked for usable tables.
- **Search gaps:** bioRxiv full text blocked; several papers read as abstracts only; Google Scholar, SSRN, OSF, conference abstracts not searched.

## Idea 2. Replication census: appears open, and far bigger than we thought

- **Not found:** any census or systematic comparison of independent re-runs. flybench and Fugsukjit are their own runs; cobanov/awesome-fly is a list ("These are source reviews, not independent reproductions").
- **Scale (from GitHub search, README-level):** about 720 non-fork repos cite the model in their README (575 created in Sep 2026); 97 state an MN9 firing rate; 33 of those were read in context; an estimated 70–75 hold a real sugar → MN9 number (estimate, not a count). The search probably covers half or less of public GitHub.
- **Preliminary pattern (self-reported, nothing re-run):** female v630 runs at 100 Hz cluster at 66–68 Hz, matching the reference; male-map weight corrections disagree widely (0.15 to 0.65 of the published value, or "no gain works").
- **What makes it a paper:** inclusion rules and an extraction codebook frozen in advance; pinned commits; two independent extractors; de-duplication of copies and same-author repos; **re-running a stratified sample ourselves**; stating it is a retrospective census, not a prospective many-analysts study; fairness rules (no ranking of individuals, contact authors, correction window).
- **Method precedents (DOIs confirmed via Crossref by the agent):** Silberzahn et al. 2018 (10.1177/2515245917747646); Botvinik-Nezer et al. 2020 (10.1038/s41586-020-2314-9); Trisovic et al. 2022 (10.1038/s41597-022-01143-6); Pimentel et al. 2019 (10.1109/MSR.2019.00077).
- **Draft data:** `census_draft/` (README-level extraction, unverified).

## Idea 3. Language model versus the simulation: do not run as framed

- The head-to-head was not found, but the ground truth is public (bioRxiv 2 May 2023; the supplement; the authors' repo ships the names), most positives predate the simulation, and "always no" scores 0.868 against the simulation's 0.953.
- Closest prior work: Yin & Cardona 2026, arXiv:2608.00059 (LLM plus connectivity infers cell-type function, with dummy-name controls); Luo et al. 2024, BrainBench, doi:10.1038/s41562-024-02046-9.
- A leak-proof version needs new real-fly data published after the model's training cut-off; none of useful size was found.

## Idea 4. Viewers versus the model: a game, not a study

- A bet mechanic already exists in RaphaelSR/fly-brain-bench (no data collected, simulated outcomes). Lay-forecasting precedents exist (Hoogeveen et al. 2020, doi:10.1177/2515245920919667).
- Unsound as "who won": the sample is 106 items with 14 positives however many people play; accuracy is dominated by the 87% base rate; answers are public and shown after each guess.
- Collecting public guesses for a paper needs consent, an ethics exemption obtained beforehand, and care with identifiers and minors. Strictly a follow-up to the video.

## Correction to an agent claim

One agent wrote that a two-step rule "nearly ties the model". We checked: as a yes/no rule it scores 0.594 accuracy. It is close only as a ranking (AUROC 0.771 vs 0.853).
