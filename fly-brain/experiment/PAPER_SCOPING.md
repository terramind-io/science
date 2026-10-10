# Scoping two further papers (10 Oct 2026)

Agrim asked for two more papers (the fly as a Jev-like decision model; courtship), or a consolidation. Before any experiment, two search agents mapped prior work and what our data can support. Records below are as reported by those agents from live fetches on 10 Oct unless marked "ours"; most GitHub items are not peer-reviewed.

## Recommendation

**One paper, not three.** Neither new idea has a result that can carry a paper. Splitting thin material across papers and building a paper around an analogy are both poor practice; one paper should answer one question with one body of evidence.

- **Decision-model idea:** at most a short section in the existing paper, without the product name. Jev stays in the video as framing.
- **Courtship:** an explainer Short from published work. One narrow descriptive question may be open, but it cannot be checked against behaviour and three papers must be read in full first.

## Decision-model idea (Jev)

- **What could be tested:** whether the simulation's output strength predicts the fraction of real flies that respond. Shiu et al. state it as an assumption: "Although the exact correlation between MN9 firing rate and rostrum lifting is not known, we assume that increased MN9 firing rates correspond with increased rostrum lifting probability."
- **Exploratory look (ours, `inputs/sez_screen.json`, left MN9 at 50 Hz):** rank correlation with the observed fraction is 0.79 across all 106 types but 0.15 within the 14 positive types. Examples: usnea 10 of 10 flies at 0 Hz simulated; FMIn 10 of 10 at 0.37 Hz; sink_sync 2 of 10 at 22 Hz; roundup 10 of 10 at 79.5 Hz. The simulation behaves like a two-level predictor (fires or not), not a graded one.
- **Why not a paper:** about 14 informative cell types at 10 flies each; no real-fly outcome for any second readout; no dose-response table in the supplement.
- **Jev itself:** released in limited early access on 15 Sep 2026 (The Register, 16 Sep; Wikipedia). Three typed answers: Noul (yes/no probability), Choice, Score. TypeSafe publishes no calibration measurement and no architecture. Independent preprints dispute the calibration of its yes/no output (arXiv:2609.37647; arXiv:2610.11392). Pairing a fly brain with Jev is already common on GitHub (for example EnesYilmazcode/FlyJevPong). A product name in a paper title is the norm only when the product is the object of study.
- **Hunger:** real feeding decisions depend on internal state, which the wiring map leaves out (Inagaki et al. 2012, doi:10.1016/j.cell.2011.12.022). Any "state in, decision out" claim has to say so.

## Courtship

- **Already done by the male-map paper and its companions:** the male song pathway is traced; an edge-by-edge male/female comparison is reported (6.3% of male and 1.3% of female central-brain connections differ, per the preprint); worked examples show the same sensory neurons routed to sex-specific targets. A companion paper covers the 48 P1/pC1 cell types (Rubin et al. 2026, doi:10.1016/j.cub.2026.08.013).
- **Simulation versions exist in public repos:** IONOFIELD/FLYCNS (male; simulation and a signed path score against real-fly pC1 results), opifor/femaleflybrain (both sexes, pre-registered), flymsg, flybench.
- **Ground truth:** about 10–12 usable real-fly cases, nearly all single-sex and overlapping, mostly used by those repos. Not enough for a quantitative paper.
- **Structural limit:** the female map is brain-only, so song or wing output cannot be read out in the female.
- **Possibly open (conditional):** where the female relatives of the male "decide to court" neurons send their wires, compared with the male, map-only. Not testable against behaviour. Do not start before reading Rubin et al. 2026, Deutsch et al. 2025 (doi:10.1101/2025.06.10.658788) and the published Berg et al. text.
- **Fact-sheet flag:** cell-type counts differ between the preprint (7,205 shared, 114 differing, 262 male-only, 69 female-only) and the published abstract (8,069 / 138 / 289 / 71). Use the published figures.

## Search gaps

bioRxiv full text blocked; the Cell and Current Biology full texts not read; OpenAlex budget exhausted for the courtship map; Zenodo, Google Scholar, SSRN and OSF not searched; GitHub by repository search only.
