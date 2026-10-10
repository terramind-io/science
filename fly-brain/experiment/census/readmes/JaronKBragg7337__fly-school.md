# Fly School

A simulated male fruit-fly brain (MaleCNS v1.0, 165,122 neurons run as leaky integrate-and-fire cells) taught Morse
timing with its own learning rule, on school hours, with exams. Live: **https://www.heartbeatobservatory.com/school/**

This repository is written so that a person — or an AI handed this page — can rebuild the whole thing and get the same
numbers. Every constant is marked **CHOSEN** (ours, swappable) or **MEASURED** (from the data or the run). If something
below is not enough to rebuild from, that is a bug in this README; open an issue.

## Credits, in the order the work happened

- **The brain:** Male CNS connectome v1.0, HHMI Janelia FlyEM + Cambridge Connectomics + Google Research, CC-BY 4.0.
  Dataset released 2026-06-08; paper 2026-09-03. Files from `storage.googleapis.com/flyem-male-cns/v1.0/`.
- **The runtime** (`runtime/`): cloned from **fruitflydev/flycoinrh** (MIT), which follows Shiu et al. 2024 (Nature)
  for the LIF model and sign convention, and includes the mushroom-body learning circuit (`mushroom.py`,
  `calibration.py`, `mb_sides.py`). We changed nothing in these five files for the school; they are copied here so
  the exact code that ran is in one place. LICENSE and NOTICE are theirs.
- **The exam** (`exams/morse_grade1.py`): written by ChatGPT (Fly-Lab-2, 2026-09-14) at Jaron Bragg's design;
  env overrides and the axon-gate/leg-drive options added by Claude Code (2026-09-16/17).
- **The axo-axonic fork** (`axon/`): Claude Code, 2026-09-17, from Ceballos et al., iScience 2026-04-22 (PMC13126034).
- **The school** (`school/school.py`): Claude Code, 2026-09-17, at Jaron's rules (persistent fly, school hours,
  shifts, life source).
- **The site pages:** github.com/JaronKBragg7337/heartbeat-observatory, `/school/` and `/live-systems/flies/school/`.
- **Jaron Bragg** — the design, every rule, every "that's not honest, fix it." Codex, Grok and a local Qwen worked on
  neighbouring parts of the same project; each is credited in the project ledger where it worked.

## 1. Rebuild the brain (once, ~10 minutes, ~1.1 GB download)

```
pip install -r runtime/requirements.txt
# fetch the three flat-connectome tables (CC-BY, no account) into runtime/data/:
#   https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/connectome-weights.feather
#   https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/body-neurotransmitters.feather
#   https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/body-annotations.feather
python runtime/build_graph.py      # -> runtime/build/graph.npz   (165,122 neurons, 10,228,000 signed edges)
python runtime/mb_sides.py         # -> runtime/build/mb_sides.json (which dopamine cluster innervates each MBON)
```

The LIF cell (`runtime/flysim.py`, MEASURED in Shiu et al., CHOSEN here by inheritance): v_rest −52 mV, v_thresh −45,
v_reset −52, τ_m 20 ms, refractory 2.2 ms, dt 0.2 ms, 0.275 mV per synaptic contact, ACh excitatory, GABA/Glu
inhibitory, monoamines zero fast weight. Calibration `pn05_apl10_kc03` (CHOSEN by the runtime's author; see
`calibration.py`) scales PN/APL/KC types so the mushroom body is sparse.

## 2. The learning rule (the only weights that change)

`runtime/mushroom.py`: Kenyon-cell → MBON synapses only (MEASURED site, 44,042 synapses on this graph). Direction:
**depression** under dopamine (Hige 2015, Cohn 2015), never potentiation. Which MBONs get reward vs punishment
dopamine: counted from PAM vs PPL1 synapses onto each MBON type (`mb_sides.json`). CHOSEN constants: learning rate
0.06, floor 0.25, eligibility trace ×0.55 per `observe()` call (~6 observations stay eligible), forgetting half-life
6 h wall-clock (Tully & Quinn 1985, "mostly gone within a day").

## 3. Grade 1 — the Morse exam (`exams/morse_grade1.py`)

CHOSEN protocol. Input: the 50 neurons whose type name starts with `JO-A` (annotated auditory Johnston's organ cells;
the real organ has ~480–720 — we drive the 50 that are typed). Carrier 120 Hz Poisson while sound is on. Dot 20 ms,
dash 60 ms, gap 40 ms, pre 20 ms, tail 40 ms. Output: the two `DNa01` descending neurons, spikes counted in 10 ms
bins; a bin with ≥1 spike is "on"; runs of on-bins <40 ms = dot, ≥40 ms = dash. Membrane reset every trial; MB
weights persist. **Teach:** 24 epochs × (`.`, `-`); exact decode → dopamine +1 (reward side), else −1 (punish side).
**Exam:** `.-` and `-.` — never taught as pairs — six cold trials each, before and after, no dopamine. Seeds are
SHA-256 of (base seed, phase, pattern, rep), so every trial is reproducible.

```
set MORSE_SEEDS=73,7337          # or any list
python exams/morse_grade1.py     # -> results/morse_grade1.json (every trial, every DNa01 bin)
```
Options: `MORSE_GAP_MS`, `MORSE_DOT_MS`, `MORSE_DASH_MS`; `MORSE_BRAIN=axon` (fork below); `MORSE_LEG_HZ=5` (tonic
drive on 3,899 leg sensory neurons). Paths at the top of the file point at one machine; set `LAB` and `RUNTIME`.

### Report card (MEASURED; the JSON for every row is in `results/`)

| row | fly | change | `.-` pre→post | `-.` pre→post | reading |
|---|---|---|---|---|---|
| 1 | fly-v1 (seeds 73, 7337) | — | 0/12 → 2/12 | 0 → 0 | one seed produced it; the other did not |
| 2 | fly-v1 (101, 202, 303) | — | 1/18 → 1/18 | 0 → 0 | not reproduced; `.-` occurs untrained |
| 3 | fly-v1 (10 seeds) | — | 0/60 → 4/60 | 0 → 0 | pooled 15 seeds: 1/90 → 7/90 (~1 in 13), p≈0.03 two-sided |
| 4 | fly-v1, gap 100 ms | echo test | 4/30 → 3/30 | 0 → 0 | `.-` appears **untrained** at the wide gap: a DNa01 output bias, not a lesson |
| 5 | fly-v1-axon | INVALID | — | — | the gate was loaded but never wired into the exam kernel (identical to v1 per seed was the tell) |
| 6 | fly-v1 + 5 Hz leg drive | control | 0/30 → 0/30 | 0 → 0 | flat leg noise erases the exam |
| 7 | fly-v1-axon + 5 Hz legs | gate wired in | 2/30 → 1/30 | 0 → 0 | the axo-axonic gate is real and does not produce `-.` |

Verdict so far: **not a pass.** `-.` has never appeared in 252 cold trials. The asymmetry is upstream of DNa01's axon:
its brain-side inputs during a dash, and/or the single-compartment LIF cell (which cannot ramp down).

## 4. The axo-axonic fork (`axon/`)

Ceballos et al. 2026 charted inputs onto the *axons* of descending neurons that "veto, amplify, or synchronize" spikes.
`dn_axon_inputs.py` streams the 124-M-row per-synapse table (`syn-partners-traced.feather`, 2.97 GB) and classifies
each synapse onto a DN as **axonal** if the postsynaptic ROI is in the VNC (CHOSEN token list in the file) — MEASURED:
4.59 M DN inputs, 290,602 axonal (6.3%); DNa01 1,135 (4.4%). Sanity check that reproduces the paper's validated example:
DNp01's top axonal presynaptic type is AN08B098 (399 synapses). `flysim_axon.py`: axonal edges do not touch the target's
voltage; they set an output **gate** on the target, `gate = clip(1 + 0.05·mV, 0, 3)`, τ 5 ms (CHOSEN). With no axonal
flags the class is spike-identical to the base runtime (verified).

## 5. The school (`school/school.py`) — one fly, persistent, on hours

Run it and leave it running (on Windows we register it as a scheduled task; any supervisor works):

```
set SCHOOL_FLY=school-1             # pupil name; its memory file is mb_<name>.npz and is never deleted
set SCHOOL_HOURS=9-12,13-16         # CHOSEN, local time; lessons only in these hours
set SCHOOL_NIGHT=22-7               # CHOSEN; sleeping (one silent trial / 5 min)
set SCHOOL_INHERIT=                 # optional: start from another pupil's memory file (same graph only)
python school/school.py
```
A **lesson** = teach 12 × (`.`, `-`) with dopamine ±1 → exam (`.-`, `-.`) × 6 cold → rest (2 silent trials, so "what the
fly does on its own" is measured — in this runtime: nothing, 0 spikes). Lesson 0 = a baseline exam. The **morning
exam** is the first exam of each school day, before any teaching: with a 6 h half-life and ~17 h without lessons,
~14% of the previous day's depression survives, so it measures what stuck (spaced vs massed training). **Free time:**
a silent trial per minute and a meal every 3 h — a clock event (fed_at, hunger), deliberately *not* dopamine, because
sugar with nothing recent in the eligibility trace changes no weight and counting it would lie. **Year:** if the
process finds the last sign of life ≥3 h old (the machine was off), it archives the report card and starts year n+1;
the memory carries with the forgetting applied. Publishing: one `fly_live` row per pupil (overwritten every trial) and
one `fly_school` row per trial (`supabase/2026-09-17-fly_school.sql`); local mirrors `report-card.json`, `*.state.json`.

**First MEASURED thing the persistent fly showed (2026-09-17, first hour):** under continuous ±1 dopamine the memory
saturates in one lesson — 41,096 of 44,042 KC→MBON synapses depressed after 24 dopamine events, mean gain 1.0 → 0.54,
sitting at ~0.28 (floor 0.25) an hour later. Everything depressed = no contrast. That is the CHOSEN rule (lr 0.06,
floor 0.25, −1 on every miss), not the connectome. Planned competing mechanisms, each as a new pupil beside the control:
smaller lr / higher floor; dopamine only on *change*; longer rest. `VERSIONS.md` is the freeze-and-fork ledger.

## 6. What is chosen vs measured — the short list

CHOSEN: LIF constants (inherited), calibration, Morse timings and the 40 ms split, the reward mapping, learning rate /
floor / trace / half-life, school hours, meal interval, the gate formula, the VNC-ROI rule for "axonal".
MEASURED: the wiring, the sign of every synapse, which neurons are JO-A / DNa01 / KC / MBON, the PAM/PPL1 side of each
MBON, every spike, every decode, every score, the axonal-input counts.

## 7. Rebuild check

You have rebuilt it when `python exams/morse_grade1.py` with `MORSE_SEEDS=73` reproduces row 1's seed-73 decodes in
`results/morse_grade1.json` (`.-` pre-test `['..', '.', '.', '.', '.', '.']`, post-test `['.-', '.', '.', '.', '.', '.-']`). Float summation order can differ
between BLAS builds; if it does, the pooled counts in row 3 are the check instead.

---
Code in `school/`, `exams/`, `axon/`: MIT (Jaron Bragg, 2026). `runtime/`: MIT, © fruitflydev. Connectome: CC-BY 4.0,
© HHMI Janelia FlyEM et al. — keep the attribution; it is the whole reason any of this is real.

## 8. What one night on the persistent fly found (2026-09-17, rows 8–14; every file in `results/`, scripts in `exams/`)

1. **The graded neuron could not speak.** `exams/dn_readout_scan.py`: DNa01 says a dash 0/30 times untrained. 117 DN
   types / 275 cells can say all four rhythms untrained. (`results/dn_readout_scan.json`)
2. **On readouts that can speak, training moves nothing.** Four readouts × 5 seeds: `.-` 29→26/120, `-.` 7→3/120.
   (`results/morse_grade1_readout_*.json`)
3. **The mushroom body does not reach a production exam.** `exams/mb_reach_test.py`: cutting MB output entirely leaves
   every readout's accuracy unchanged (36 trials × 3 conditions). (`results/mb_reach_test.json`)
4. **Its own exam — valence — fails too,** because dot and dash are the same Kenyon cells (Jaccard 0.97; ~65% of KCs fire
   for any sound). `exams/morse_valence.py`. (`results/morse_valence.json`)
5. **Root cause: whole-brain ignition** under the stock gain (25–35 Hz/cell for any sustained input).
6. **Fix, measured:** `exams/gain_sweep.py` on 3 seeds — every weight × 0.35 → 2–2.9 Hz/cell, KC 7–11% active (the real
   fly range), descending neurons alive and duration-sensitive. **This is `fly-v2`** (`versions/fly-v2/MANIFEST.md`; build
   it by scaling `graph.npz["data"]` by 0.35). (`results/gain_sweep*.json`)
7. **The body.** `body/body_loop.py` (flybody + MuJoCo 3.13, own venv): 328 leg motor neurons → 59 actuators by muscle
   name; 3,915 leg sensory cells ← touch / joint speed; same 0.2 ms step. On v1 the fly seizes at any touch; on v2 it
   stands (4–6 Hz/cell, five or six legs down, ball still). (`results/body_loop_*.json`)

Rebuild check for this section: `SWEEP=0.35 SWEEP_SEED=73 python exams/gain_sweep.py` → `hz_per_cell` ≈ 2.0, `kc_frac_active` ≈ 0.07.

## 9. Walking — borrowed, declared (2026-09-17 02:10)

No connectome-only model walks; every public embodied fly brain (FlyGM, Fly.exe, lulzx/fly-brain, NeuroMechFly v2) puts a
stepping generator between descending-neuron rates and the legs, and says so. We do the same: `body/gait.py` is a port of
**lulzx/fly-brain's** generator (lulzx, MIT) — `gait.mineplix.json`, two-harmonic joint curves fitted to 100 FlySuite
real-fly walks, tripod, 10 Hz — commanded by our brain's own DN rates (`BODY_MODE=descending`). Measured on fly-v2:
silent, the fly steps intermittently at the walking threshold; a 120 Hz tone makes MDN fire and it backs up and turns
(`results/body_loop_v2_gait_s0.json`, `_s120.json`). lulzx also reports 7.4% active Kenyon cells in their fitted regime;
our 0.35× gives 7.3%. Their raw-muscle mode "cannot stand"; ours stands on v2 (2 s, on a ball — small, checkable).

## 10. Grade 0 — does each organ do its job? (2026-09-17 02:45)

Before any lesson: sense in, the literature's named output read, no learning (`exams/grade0_organs.py`). Pass = output
≥ max(1 Hz, 2× baseline) and brain < 10 Hz/cell. **fly-v1: 7 of 7 organs ignite the whole brain. fly-v2: 7 of 7 pass** —
taste → proboscis MN9 (20 Hz); loom → giant fibre (253 Hz); wind → MDN (11.5 Hz); song → pIP10/DNp13; odour → 6.3% Kenyon
cells + steering DNa02; hind-leg touch → DNa01/MDN; front-leg touch → grooming DNs (weak, 1–2 Hz). `results/grade0_v1.json`,
`grade0_v2.json`. Identity lesson on v2 (`exams/identity_lesson.py`): two odours are distinct (KC overlap 0.10–0.21) but
the population valence readout did not learn a preference in 12 pairings (0/5 seeds) — next: compartment-specific readout.

## 11. Grade 0b — the organ check on the corrected answer key (2026-09-17 03:00)

A literature answer key (assembled with ChatGPT; Shiu 2024, Ache 2019, Zhou 2015, Turner 2008, the 2026 MaleCNS gustatory
typing) removed three unsupported rows from section 10 and named the right cells. `exams/grade0b_organs.py`, fly-v2:
sweet LB3b+LB3c → MN9 (6.7 Hz) PASS · **bitter + sweet → MN9 1.7 Hz, the veto sign Shiu reports** PASS · water LB3a → MN9 0
FAIL · loom: LPLC2 → GF/DNp04/DNp06, LC4 → DNp02/DNp04 — the feature specificity the key predicts — PASS · JO-A → GF 0 FAIL ·
JO-B → AMMC PASS (weak key) · DM1 odour → DM1 PN 297 Hz but Kenyon cells 2.8% (target 5–10%) FAIL · antennal → grooming DNs
PASS (weak key). **v2: 7 pass / 3 fail / 1 not testable. v1: 0 pass, 11 ignite.** Neighbour numbers (lulzx/fly-brain, nine
fitted globals, conductance synapses): sugar → MN9 59 Hz, KC 7.4%. That recipe is the fly-v3 candidate. `results/grade0b_*.json`.

## 12. The communication loop — attempted, predeclared, NOT established (2026-09-17 03:15–03:59)

`exams/comm_protocol.md` holds two predeclared tests; `exams/comm_loop.py` runs them; every pilot and test JSON is in
`results/`. Test 1 (answer = MDN, 8 fresh seeds) failed all criteria. Test 2 (answer = MBON21+26, 8 fresh seeds) failed all
criteria. What held: the MBON side table (Aso 2014), symbol delivery through sensory neurons only, two-odour discrimination
when the pair is chosen well, and dopamine-gated depression at the intended synapses in the intended direction. What did not:
any answer channel selecting reproducibly by symbol after learning. Root cause, measured: the Kenyon-cell code shares
0.4–0.7 of its cells across most odour pairs (`results/glom_scan_v3.json`), and a per-KC homeostasis attempt (`versions/fly-v4`)
decorrelates it only by making it unreliable. The next step is a mushroom-body calibration search with the objective written
in the project ledger. Nothing was redefined after a result.

## 13. Calibration search → fly-v5 → test 3 (2026-09-17 04:05–04:30). Failed. Where the loop stands.

`exams/mb_calib_search.py` (96 random candidates; `results/mb_calib/`) found one calibration meeting the predeclared
mushroom-body targets — reliability 0.69, overlap 0.06, 4.6% Kenyon cells — by raising APL inhibition ×6 (`versions/fly-v5`).
On it, a rewarded odour's avoid-side MBON output fell 21–31% while a control odour's did not (stage 2, one seed). The
predeclared test 3 on 8 fresh seeds: the drop is 5–20% and per-trial replies are at chance — failed. Three predeclared
tests (24 seeds) failed tonight; none was redefined. The gap is quantitative: the learned change is about a fifth of the
trial-to-trial variability at the readout. Next: a calibration whose objective includes the learned readout, many seeds.

Test 4 (block-level reply, 8 fresh seeds): failed — 0/8. Four predeclared tests, 32 seeds, none redefined. Communication not established; see `exams/comm_protocol.md` for every predeclaration and the ledger for the next step.

## 14. The readout was pinned (2026-09-17 morning): fly-v6, fly-v7, tests 5–7

Instrumenting a trained fly showed the lesson landing (KC→MBON synapses at gain 0.26; KC drive −60%) while the MBONs did not
move: APL inhibition and weak KC→MBON synapses pinned the readout. fly-v6 puts the APL gain on APL→KC edges only; fly-v7 sets
KC→MBON edges ×24 (`versions/fly-v7`). Grade 0b on v7: 9 pass / 1 fail / 1 not testable — core reflexes intact. Test 7 (one-sided,
24 pairings, 24 reps, 8 fresh seeds): the rewarded odour's avoid-side MBON output fell in 7/8 flies (z −2.9 to −6.4) — but the
control odour fell 3–10% too, so the predeclared specificity criterion failed; the punished odour did not move. Seven predeclared
tests, none redefined. Open question: why the control inherits part of the lesson. `results/comm_loop_test{5,6,7}_s*.json`.

## 15. Antennal lobe corrected (fly-v9), fly-v10, test 8 (2026-09-17 10:25)

The lLN1/lLN2 antennal-lobe local neurons are marked cholinergic by the transmitter table; in the fly they are GABAergic lateral
inhibition. With that sign fixed (`versions/fly-v9`), one odour activates 23–35 PN types instead of 154–164. A shared-weights bug
(pupils in one process inheriting each other's memory — found in Grok's review) is fixed too. Calibration round 2 on v9 then
gave a 32–50% learned drop in every fly (`versions/fly-v10`). Grade 0b on v10: core reflexes hold. Test 8 (8 fresh seeds, the
wiring-chosen top-5 reward-side compartments): the rewarded odour's output fell 40% in 8/8 flies (z −13 to −22) — but the
never-paired control fell 15% and the punished odour 30%, so the predeclared specificity criterion failed. Eight predeclared
tests, none redefined. The remaining leak is Kenyon-cell reliability (0.29–0.47 in these flies). `results/comm_loop_test8_s*.json`.

## 16. Test 9 — the first predeclared communication test to pass; reproduced (2026-09-17 11:02–11:42)

ChatGPT chat's review found three more leaks: the calibration had been searched with odour A alone while the tests trained A and
B; the control odour's rate was matched to one probe trial; and the block statistic ignored the post-training variance. Test 9
(`exams/comm_protocol.md`, predeclared 10:50) therefore trains A only, replays identical sensory realisations before and after
(paired differences), freezes the answer population to five reward-side compartments (MBON09/01/05/03/06) and skips the equaliser.
Result on 8 fresh seeds: rewarded odour A → APPROACH in 8/8 (paired z −13.6 to −23.2, output down 45–49%); never-paired odour C →
NONE in 8/8 (1–4%). Grade 0b on fly-v10 identical before and after. Reproduction on 8 new seeds (8181–8888): 8/8 and 8/8 again.
Frozen as `versions/comm-loop-1` (SHA-256 of graph, calibration, side table, code). The reproduction's *motor* line (paired z on
DNa13+DNa03+MDN with 24 realisations) was mis-sized for such small counts and failed even though the direction was right in
16/16 flies — reported as failed, not redefined. `results/comm_loop_test9_s*.json`, `results/comm_loop_repro_8181-8888.json`.

## 17. Test 10 / 10b — the motor stage passes its own predeclared bar (2026-09-17 12:33)

Same frozen protocol, 48 matched realisations per odour, criteria fixed at 11:50 before either batch ran: rel_Y(A) > 0 in ≥ 7/8,
mean ≥ 0.15, A > C in ≥ 7/8, |mean rel_Y(C)| ≤ 0.15, plus the MB lines unchanged. Test 10 (9191–9898): MB 8/8 + 8/8; descending
sum down for A in 8/8 (mean 0.229), C mean 0.048. Test 10b (10101–10808): 8/8 + 8/8; A 8/8 (mean 0.214), C mean 0.014. Decoded
reply GO-TOWARD in 16/16. Grade 0b after: every verdict and read identical. Caveat: C barely drives these descending neurons
(1–5 Hz vs A's 90–111 Hz), so single-fly rel_Y(C) is noisy; the A effect is not. `results/comm_loop_test10*_s*.json`,
`results/comm_loop_test10_pooled.json`, `results/grade0b_v10calib_post10.json`.

One fact that is easy to miss in the sections above: the learning rule has had an aversive side from the start — PPL1-dopamine
depression of the punishment-side KC→MBON synapses (side table verified against Aso 2014), and tests 1–8 trained odour B + punishment
beside odour A + reward. B's aversive lesson leaked into the network used to judge A, and dropping it is part of why test 9 passed.
So aversive learning exists and was measured; it has not yet been run as the *primary* symbol on the frozen stack.

With that, the nine-item goal predeclared on 2026-09-17 is met on every item, on its own bars, and reproduced from clean
processes. In Grok chat's words it is **Goal A: a decoded endogenous reply from one fly on a frozen test.** It is not two flies
talking through a world (Goal B). Section 18 starts that.

## 18. GPU kernel (verified bit-for-bit) and Gate 1 — a sender's song reaches a receiver's ear through a world (2026-09-17 12:26)

`gpu/flysim_gpu.py`: the same LIF maths batched over flies with one sparse matmul per step (torch 2.6 + CUDA, RTX 4060). Verified
against the CPU kernel on five organ rows: every one of 165,122 neurons' spike counts identical (`results/gpu_verify.json`).
0.5 s per fly in a batch of 8 (CPU ≈ 7 s).

Grok chat (reading this repo, 2026-09-17) set the bar for communication: a sender changes a physical field in a shared world, the
receiver gets it only through its own sensory neurons, a mute lesion and a scramble are the controls, and the fly's own channels
(song, cVA, CO2) replace Morse. Gate 1 (`world/gate1_protocol.md`, predeclared 12:25): two separate processes (`world/sender.py`,
`world/receiver.py`) on the frozen fly-v10 stack; the only shared thing is a song on/off schedule that `world/world.py` writes from
the sender's wing motor neuron spikes. Sender: pIP10 (2 cells, 100 Hz) → dPR1 / TN1a / vPR9 song-pattern neurons 72–100 Hz → pulse-
song wing motor neurons hg1/ps1/i1/i2 at 54–100 Hz (silent sender: 0). Receiver: JO-A driven at 120 Hz only while the schedule
says song → AMMC 2.7–4.6 Hz live vs 0 muted, 8/8; mute identical to a zero world and scramble identical to live (whole spike
vectors equal), 8/8; no ignition. PASS on every criterion, 168 s. Limits stated in the protocol: the model has no spontaneous
activity, so mute = 0 Hz makes the 2× line easy; the world rule is binary (no pulse-song rhythm yet); 100 Hz on pIP10 is chosen,
not fitted. It is a wire test. Gates 2–4 (cVA / CO2 on the receiver; state-gated emission; learned coupling) are next.
`results/gate1/gate1_summary.json`.

Credits for this stretch: Grok chat (the four-gate design, the mute/scramble controls, the song channel, the shared-weights bug);
ChatGPT chat (the A-only calibration mismatch, the one-trial equaliser, the block statistic, the literature answer key); Claude
Code (the runs, the kernel, the writing); Jaron (the rule that nothing is cancelled out — the chemistry lead is logged, not dropped).

## 19. Gate 3 — the sender's learned state reaches a receiver through a world; passed and reproduced (2026-09-17 12:40–15:30)

Grok chat's Gate 3: train the sender only, and the receiver — which never smells the taught odour — must track the sender's state
through a physical channel, with a mute lesion as the control. The pilot showed the mushroom-body lesson does not reach the song
circuit consistently, so song was dropped as the channel (`world/gate3_pilot.py`). The lesson does reach MDN, the backward-walking
neurons (test 10). A male carries cVA on his cuticle; a nearby male is smelled through Or67d → DA1. So the world (`world/gate3_world.py`,
declared 1-D physics) turns the sender's MDN rate into how far it backs away from the odour source, and into the cVA concentration
at the receiver, which drives the receiver's 204 ORN_DA1 neurons. Sender (`world/gate3_sender.py`) and receiver
(`world/gate3_receiver.py`) are separate processes; the world file is the only bridge; the receiver's ORN_DA2/VM5d spike counts are
checked to be zero every trial.

Six declarations, all in `world/gate3_protocol.md` with their results: 3 failed (a learning-rate transcription error; an under-powered
z line and a ratio-of-small-numbers control line; then twice the "mute bit-identical" line, because the GPU sparse matmul flips one
borderline spike about once per 800 trials and the network cascades from it — `results/gate3/gate3c/determinism.txt`). Every
scientific line passed 8/8 in 3c, 3d, 3e and 3f. **Gate 3e passed every line 8/8; Gate 3f, the reproduction on fresh seeds, passed
every line 8/8.** Across 3e+3f: sender MDN down 17–33% for the rewarded odour in 16/16, control odour within 1 Hz; cVA at the
receiver up in 16/16; the receiver's DA1 projection neurons up ~20% (≈105 → ≈126 Hz), paired z 2.9–6.0, in 16/16; control odour
flat (|change| ≤ 0.6%); mute clean; no ignition. Decoded reply at the receiver: "SENDER-CAME-CLOSER" 16/16. Grade 0b after: every
verdict and read identical to before.

What it is not: the sender does not decide to signal — it backs away less and the pheromone it already carries does the rest; the
walking is a declared kinematic rule, not the MuJoCo body; the receiver's readout is a projection-neuron rate, not a behaviour;
Gate 4 (two senders, one receiver; persistence across a school day) is not started. `results/gate3/*/gate3_summary.json`,
`results/grade0b_v10calib_post_gate3.json`, hashes in `versions/comm-loop-1/MANIFEST.md`.

## 20. Gate 4 — the round trip; the reply arrives, but does not yet carry the lesson (2026-09-17 19:35 → 2026-09-18 00:57)

Jaron's bar, stated plainly on the evening of the 17th: something learned goes out, something comes back, and the next move depends on
what came back. Gate 3 is half of that. Gate 4 (`world/gate4_protocol.md`, predeclared before the run) asks for the other half:
fly A learns odour A; its backing-away changes what B smells; B's wings (cVA → wing motor neurons, graded, 32 cells) push air at A's
antenna; A's antennal mechanosensors reach A's walking neurons even while A is smelling the odour (the cVA channel cannot — the
restored lateral inhibition silences a faint odour behind a strong one, as in the real fly). Two separate brain objects, A trained,
B frozen and leak-checked; a 1-D world of distance, pheromone and air; three one-second bouts; 8 pairs × 96 paired realisations;
LIVE vs YOKED (B's wing output replayed from the untrained pairing) vs MUTE; the never-paired odour as the control loop.

Result: learning enters the world 8/8 (the pair ends 11–14 mm closer); **A hears B's reply 8/8** (A's walking neurons 13–16 Hz with
the air arriving, 31–38 Hz with it cut, z −9 to −12); control flat; no leak; B's weights untouched. But the line that mattered —
does B's reply depend on what A learned — failed: pooled Δ −0.65 Hz, z −1.34 against a bar of −3, sign right in 6/8. The reply is
loud and it is the same reply whether or not A learned. Verdict FAIL as declared; no reproduction; nothing re-declared.
`results/gate4/gate4_summary.json`.

That is the measured gap, at a named link, and it is the most useful line in this file for anyone who wants to take the work
further: the native wiring carries a lesson one way strongly and hears a reply strongly, but nothing in the fly persists between
bouts except its position, so the reply cannot mean anything to it. What the model lacks is not another channel; it is state —
something to need, something to lose, something to expect (decisions/OPEN-QUESTIONS Q-019, Q-020). That is where this repo hands off.

Credits for the two-fly stretch: Grok chat (the four gates, mute/scramble, "the fail is the finding"); ChatGPT chat (the return-path
tightening — no scripted rule, LIVE/YOKED/MUTE — and the "something to lose, need, expect" framing); DeepSeek (stakes and contrast);
Claude Code (kernel, world, runs, writing); Jaron (the bar, the three things, and the rule that nothing is cancelled out).
