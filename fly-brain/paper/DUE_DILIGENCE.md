# Due diligence log for the paper (10 Oct 2026)

Status of every check behind `draft_v1.md` and `draft_v2.md`. Draft 2 adds the instinct function and the courtship check; their checks are in "Draft 2 additions" at the end. "Done" means we did it ourselves and the record is in the repository.

## Done

| Check | Result | Record |
|---|---|---|
| Plan committed before results | Plan `abb98a0` (10:34) precedes results `a00789a` (10:41) and `e3e080b` (10:52) | `experiment/` git log |
| Independent re-computation of all 3A and 3B numbers | All point estimates reproduced; intervals within 0.006 | audit summarised in `experiment/RESULTS3.md` |
| Audit's corrections applied | Two overstatements and one miscount corrected in the write-up (commit `1e069c3`); the dropped row fixed in code and result file (commit `e02b454`) | `experiment/` git log |
| Step-count explanation, re-checked by us | Counting only connections of 5+ synapses matches the paper's column for 104 of 106 types (56 of 106 with every connection); AUROC 0.761. Recomputed again by the fact-check. | `experiment/results/plan3/3A.json` (`P1_exploratory_5plus_synapses`), regenerated after fixing a dropped row |
| Headline-case coding made consistent | Two projects name the v630 data file without writing the version; counting both gives 6 of 9, neither 6 of 7, as first scored 6 of 8. Verdict inconclusive in every case. | `experiment/results/plan3/3B_descriptives.json` |
| Census descriptives promised in the plan | First commit of the 72 included: 64 in Sep 2026, 6 in Oct, 1 each in Jun and Jul. Licences: MIT 28, none detected 28, unclassified 12, GPL-3.0 3, Apache-2.0 1. Exclusion reasons tallied. | `3B_descriptives.json` (dates and licences come from the search agent's GitHub API pull of 10 Oct, not re-fetched by us) |
| Citation metadata from fetched records | 18 Crossref records (17 used; Sterne 2021 is unused) and 2 DataCite records fetched 10 Oct; reference list generated from them | `paper/refs/` |
| Corresponding author address | Taken from the printed paper text | `sources/text/S2_Shiu2024_brain_model.txt`, line 74 |
| v783 neuron count in the model | 138,639 (the draft first said 139,255, which is the dataset figure; corrected) | `Completeness_783.csv` |
| Ten of 14 screen positives previously published | Confirmed against the "See also" notes in Supplementary Table 3 by the audit; source data of the earlier papers read by a search agent, not by us | `experiment/RESULTS3.md` "Background fact" |

| Prior-work re-check on both claims, 10 Oct | Both still appear open. Tracked projects unchanged (flywire-fly-lab `776442e`, Fly.exe `cc25411`, Fugsukjit `c4ef087`, flymsg `cb3ed70`, flybench `3052ce5`). bioRxiv 1 Sep–10 Oct scanned by title and abstract (9,135 records). Closest new item: moiz-lakkadkutta/flyconn (`53d1715`, pushed 10 Oct), created 29 Sep, which per its documents compares route signs with simulated effects, not with real flies; its code was not read, and the draft's description of it rests on this report alone. Gaps: Zenodo keyword search failed; Google Scholar, SSRN and OSF not searched. | search agent's report, 10 Oct; summary here |
| Shortest Path legend | Read by us from the supplement file: "The “shortest path” specifies the minimum number of synapses separating neurons in the split-GAL4 and MN9." No threshold stated. | `sources/papers/S2_supplementary/S2_Shiu2024_MOESM2_ESM.xlsx` (text box) |
| The 0.581 scaling factor | Found in the preprint text only (lines 1607–1610); the draft now cites the preprint | `sources/text/S3pre_Berg2025_maleCNS_preprint.txt` |
| Public contact routes for credited projects | The 14 repositories checked exist with issues enabled, and no email is printed in any README or citation file. Not yet checked: AkashaCorporation/FlyBrain and moiz-lakkadkutta/flyconn, which also appear in `emails.md`. One owner (ameerul-muminin) lists an email on a public profile. | search agent's report, 10 Oct |

## Open before release

1. **Repeat the prior-work search on the day of release,** including Zenodo, and read flyconn's code.
2. **Original authors see the draft** (email 1 in `emails.md`), with five questions: the Shortest Path method, the status of previously published cell types, the antennal neuron and synapse counts, the sucrose-to-rate mapping, and the silencing labels.
3. **Credited and named projects are contacted** (emails 2–4), with a correction window.
4. **Berg et al. scaling factor 0.581:** check whether the published *Cell* version states it; we hold only the preprint text and the PubMed abstract.
5. **Licence for redistributing FlyWire-derived tables** (CC BY on Zenodo, CC BY-NC on flywire.ai; unresolved since the playground research). The result files contain neuron ids and derived scores.
6. **Public repository and archive DOI** (GitHub and Zenodo, per GROW-111 and GROW-103).
7. **Authorship, affiliation and a statement on how the work was produced.** Decision for Agrim.
8. **Blind fact-check of the final text** against the result files. A first pass on draft v1 found 17 mismatches, 11 overstatements and 12 omissions; all were addressed in the revised draft (see "Fact-check of draft v1" below). A second pass on the revised text found one substantive error (67.0 Hz is the authors' shipped example run, not a number in the paper, whose Supplementary Table 1A lists 65.7 Hz; we verified this in the spreadsheet), plus smaller mismatches, all corrected. The text as it stands after those corrections has not been checked a third time.
9. **Census data table:** release with repository names (then contact all 97) or with names removed.

## Known weak points a reviewer will raise

- 13–14 positive cases; wide intervals; the male-map result for M1 is narrow.
- The path score's form was chosen on v630 and v783 is the same brain.
- The silencing comparison rests on five discordant cases.
- Census numbers are self-reported README text; projects are not independent.
- The first census rule (R1) was not defined tightly enough in advance; all readings are shown.
- The census rules were written after a rough view of the data, and the simulation outputs had been scored against the screen before the plan.
- Extraction and audits were done by AI agents, not human reviewers.

## Fact-check of draft v1 (10 Oct)

A separate agent checked every statement in the first draft against the result files, the anchor paper's text, the citation records and the git history, and recomputed the step-count figures. Main corrections made in response:
- "Independent" removed as a description of the census projects (title, abstract, figure caption).
- Abstract now says the headline-case agreement fell short of the pre-registered bar, that the male-map finding is "no agreed correction", and that the female test set is a later version of the same female connectome (the body adds that it is the same brain as the development data).
- Methods now state what was already known before the plan (simulation outputs scored; pilot; draft census pattern), that our own runner and Brian 2 version 2.7.1 were used, the male sign rule, and that extraction and audits were done by AI agents.
- Three, not two, of the nine headline values are single short runs.
- The journey section now lists all three audits and describes their corrections accurately.
- Omitted results added: other male weights, step-count differences, tied zeros, Zorro and label sensitivity, the alternative readings of R1, details of R2 and R3.
- Reference fixes: Goodman DFM; code authors Shiu and Spiller; Zenodo records for references 13 and 15 saved.
- Result file `3A.json` regenerated (it still held the pre-audit 56 of 105).

## Draft 2 additions (10 Oct)

| Check | Result | Record |
|---|---|---|
| Plans committed before runs | Instinct plan `d91f86c` (12:33) before its run (results 12:52). Courtship amendment `3ad7cd8` (12:56:15) before the first result file (12:56:35). | `experiment/` git log |
| Prior work, instinct idea | Partly done by others: ask-the-fly, fly-instinct, flybench, Fugsukjit, femaleflybrain, brainfly. None found scoring yes/no answers against real-fly counts for mixed stimuli. Credited in draft 2. | search agent's report, 10 Oct; `experiment/RESULTS4.md` |
| Courtship ground truth | 28 literature rows with verbatim quotes, compiled by a search agent; several sources read as abstracts or preprints. Not re-read by us. | `experiment/inputs/courtship_cases_literature.csv` |
| Independent audit of both results | All numbers reproduced. Findings folded into `RESULTS4.md` and draft 2: only 5 of 9 instinct cases were open (2 matched); our sucrose-to-rate assumption decides that verdict; the courtship pass rests on sign handling and on one pair. | `experiment/RESULTS4.md` "What the independent audit added" |
| Cloud runs used the same files as the laptop | SHA-256 of the connectivity table, neuron list, supplement and runner identical in all 7 job logs | `experiment/results/plan4/local_sha256.txt` |
| New citations from fetched records | 11 Crossref records for references 26–32, 37 and 38 (and the two preprint versions) | `paper/refs/` |

**Open for draft 2, in addition to the list above:**
- Read the published versions of references 26 and 27 and the sources behind the courtship labels ourselves.
- Contact routes for the five newly credited projects.
- Fact-check of draft 2's new sections: one pass done on 10 Oct. It found 7 mismatches (one wrong count of inconclusive verdicts; one figure, 0.735, that our result file did not yet support; wording in five places), 9 overstatements (among them the title and "gets the direction of every effect right") and 17 omissions, mostly audit caveats missing from the manuscript. All were addressed. The text after those corrections has not been checked again.
- brainfly is now credited in draft 2 (reference 39); its commit hash was read by a search agent.
- Commit hashes for references 33–36 were read by a search agent, not by us.

## Final critical pass: draft 2 to draft 3 (10 Oct)

**Licence decision (Agrim, 10 Oct):** the project is non-commercial, so FlyWire's CC BY-NC 4.0 terms allow the use. Draft 3's data statement says FlyWire-derived tables are shared for non-commercial use with attribution. One thing to keep in view: this covers the paper and data release; if a video using FlyWire-derived renders is monetised or used to promote a product, "non-commercial" could be questioned. Rendering from the male CNS data (CC BY) avoids the question.

**Checks run on draft 2:** a referee-style review and a full-text fact-check, each by a separate AI agent run, plus our own read.
- Fact-check: every number in Sections 2 and 3 reproduced from the raw files. One substantive error (the draft said the plan had not listed a value that it had listed), five wording mismatches, three quotation slips, and a list of statements with no local record.
- Review: recommended narrowing the paper to the map-only baseline and the survey; cutting the courtship check; moving the instinct function to a supplementary note; rewording "the simulation adds measurable value"; reporting both constant-guess baselines for silencing; replacing "pre-registered" with a dated "pre-specified"; and a full statement of how the work was produced.

**What draft 3 does:** narrows the main text; moves the instinct function and courtship check to Supplementary Notes 1 and 2; adds a table of what was known before each rule; adds exploratory checks (`experiment/results/plan3/3A_review_checks.json`: rank tests, stratified intervals, seed check for the difference, both silencing baselines, thresholded map scores); renames the census a survey and gives the roughly 720-repository count as unverified; adds Section 8 on how the work was produced; renumbers references; redraws the figures (`paper/make_figures_v3.py`).

**New result from the pass (exploratory):** leaving out connections under five synapses raises the path score to 0.81 on v783 and 0.74 on the male CNS, and narrows the simulation's lead on v783 to 0.03 (interval 0.007 to 0.068).

**Not yet done, and required before release:**
1. Agrim's decisions marked [DECISION] in draft 3: authors and roles, what a human verified, courtship note in or out, title.
2. A fact-check of draft 3 as it stands (it has not been checked since the rewrite).
3. A person reads: flyconn's code; Tastekin et al. and Guan et al. (listed in `PRIOR_WORK.md`, unread); the courtship sources if Note 2 stays; the published text of the male-connectome paper for 0.581.
4. Credit owed per `PRIOR_WORK.md` and not yet in the draft: Fugsukjit's male calibration (0.547), Silva Santos, Avetisyan, Aldunate Rodríguez. Each needs verifying before it is cited.
5. Model names and versions for Section 8.
6. Emails sent and answered; public repository and DOI; prior-work search repeated on release day.

## Version 1.0 release candidate (10 Oct)

Files: `paper/final/wiring-only-baseline-v1.0.md` and `.pdf` (14 pages; built from the Markdown by `paper/build_pdf_html.py` and headless Chrome), figures in `paper/final/figures/`.

**Fact-check of draft 3 before this version:** no wrong result number; 11 wording or provenance mismatches (for example the trial standard deviation quoted from the wrong run, "types" for "cases", and "seven minutes before the scores were computed" where the record supports "results committed seven minutes later"), 8 internal disagreements, figure-caption gaps and leftover markers. All addressed in v1.0. The v1.0 text itself has not been checked after those edits.

**Defaults taken because Agrim did not answer the four questions (the prompt timed out); each is his to change:**
- Author line: "Agrim, Terramind".
- Courtship note: cut, under the "if uncertain, cut it" rule (labels compiled by an agent from preprints and abstracts, unread by a person). The full note remains in `paper/draft_v3.md` and its results in `experiment/RESULTS4.md`.
- Section 8 states that the author directed and reviewed and did not re-derive results or re-read sources by hand. This is what our records show; he should confirm it is true.
- Title: "A wiring-only baseline for a whole-brain fly simulation, and a survey of its public re-runs".
- No model names are given in Section 8.

**This is a release candidate, not a published paper.** Still required before public release: Agrim confirms the defaults above; emails to the original authors and named projects sent and answered; a person reads the sources listed under "Final critical pass"; repository made public with a DOI; prior-work search repeated on the day.

## Version 1.1 (10 October 2026, ~15:00)

Files: `paper/final/is-the-map-all-you-need-v1.1.md`, `.html`, `.pdf` (14 pages). Version 1.0 is kept beside it.

**Changes Agrim asked for:**
- Authors: Terramind first, then Agrim. Section 8 names Agrim as the person directing the work and says "the authors take responsibility".
- Title: "Is the Map All You Need? A Wiring-Only Baseline for a Whole-Brain Fly Simulation". The survey is no longer in the title; it is still in the abstract and Section 4.
- Layout: paper-style PDF from `paper/build_paper_pdf.py` (centred front matter, indented abstract with a run-in label, serif justified text, ruled tables, page numbers).
- Figures: six main figures and Figure S1 from `paper/make_figures_v4.py`, all drawn from the result files except Figure 1, which is a sketch and is labelled as illustrative.
- A tools line in Section 8: "Researched with Terramind Science, in Nucleus."

**Checks done:** every page of the PDF was viewed; the counts shown in Figures 5 and 6 were checked against the text (14 corrections; 9 headline values; 1+1+0+64+6 = 72; 33+18+13+8 = 72). Two legends that overlapped data, a merged Table 1 caption and a reference note run into reference 31 were fixed.

**Not done:** no independent fact-check of the v1.1 text has been run since the edits (new captions and figure references). No result number was changed. All release gates listed under version 1.0 still apply.

## Version 1.2 (10 October 2026, late afternoon)

Files: `paper/final/what-the-flys-wiring-map-predicts-v1.2.md`, `.html`, `.pdf` (14 pages). Versions 1.0 and 1.1 are kept beside it.

**Changes, all decided by Agrim:**
- Title: "What the Fly's Wiring Map Predicts Without a Simulation", with no subtitle.
- Author block: Terramind with https://terramind.org; Agrim with agrim@terramind.com. A correspondence line was added to the acknowledgements.
- Front page: a plain link to the project page, https://terramind.org/fly-brain/ (returned HTTP 200 on 10 October 2026, as did /fly-brain/lab/). No short links inside the PDF, per the cross-linking rule.
- Abstract: the second sentence now reads "For that one behaviour, the feeding response, we ask how much of the prediction is already in the wiring map, before any simulation is run", so the scope the title leaves open is stated.

**Not added, because the destinations are not live:** a link to the video, the code repository and its DOI, and a papers index (https://terramind.org/papers/ returned 404). Add them at release.

**Not done:** an independent fact-check of the text since v1.0; a check of each repository's rules on an organisation as first author. All release gates listed under version 1.0 still apply.

## Version 1.3 (10 October 2026, evening)

Files: `paper/final/what-the-flys-wiring-map-predicts-v1.3.md`, `.html`, `.pdf` (15 pages).

**Change, approved by Agrim from previews:** two figures drawn from the FlyWire v783 model network by `paper/make_brain_figures.py` replace the hand-drawn sketch. Figure 1: routes from Fdg to MN9 (2 source neurons, 20 relay neurons). Figure 2: the map-only signal after steps one to three (402, 5,782, 21,267 neurons; 0, 4,708 and 17,916,312 arriving at MN9). The earlier Figures 2-6 are now 3-7.

**Checks:** the script's path score for Fdg (17,921,020) equals `P2_path3` for Fdg in `experiment/results/plan3/3A_per_type.csv`; every caption number is in `paper/final/figures_preview/brain_Fdg.json`; Fdg's real-fly result (8 of 10) is `observed_rate` 0.8 in `experiment/inputs/sez_screen.json`; figure references were renumbered by script and listed.

**Not done:** an independent fact-check of the text since v1.0. `paper/` is still not under version control, so the figure script has no commit. The repository is not public, so the paper carries no code link.
