# bosco

A simulated male fruit fly (MaleCNS v1.0 connectome) running as an
autonomous Bluesky account, `bosco.proto.cool`.  The question is whether a
fly-brain policy over a constrained action set can hold its own against the
bottom of the feed.  See `CLAUDE.md` for the rules and `EXPERIMENT.md` for
the pre-registration.  This file documents the model as built.

## Pipeline

```
poller -> encoder -> kernel (C, ctypes) -> plasticity -> readout -> poster
                 \_______ SQLite ledger + stimulus log (features only) _______/
```

- `src/bosco/data.py`, `populations.py` — raw feathers, named populations.
- `src/bosco/model.py` — pruned network as CSR; v1 wiring rules.
- `kernel/lif.c`, `src/bosco/kernel.py` — deterministic LIF kernel.
- `src/bosco/encoder.py` — (DID, VADER, mention) → sensory drive. `docs/encoder.md`.
- `src/bosco/sim.py` — episodes from rest; `plasticity.py` — mushroom body.
- `src/bosco/readout.py` — DN/MN populations → behaviour → action.
- `src/bosco/agent.py` — one event → one episode → one ledger row.
- `src/bosco/bsky.py` — Bluesky loop; `cli.py` — `bosco poke|replay|run ...`.

## Modeling decisions

Every number below has a gate report under `docs/`.

1. **Neuron set** (`model.CB_SUPERCLASSES`): 40,939 traced central-brain
   bodies: cb_intrinsic/sensory/motor/endocrine/efferent, plus descending
   and ascending neurons.  Optic lobes dropped (no visual input until
   2026-09-15; since then a hand-built retina drives the visual Kenyon cells
   directly, decision 47).  VNC dropped; descending neurons are the readout.
   8.49 M edges, 45.7 M synapses.
2. **LIF parameters** are Shiu et al. 2024 verbatim (`config/model_v1.yaml`),
   except the per-synapse weight, which Shiu calibrate per connectome:
   "W_syn such that activation of sugar GRNs at 100 Hz resulted in roughly
   80% of maximal MN9 firing".  Same criterion on MaleCNS gives
   **w_syn = 0.16 mV** (`docs/phase2-wsyn-calibration.md`).
3. **Synaptic sign** from the MaleCNS consensus NT prediction, Shiu's
   convention: ACh and monoamines excitatory, GABA/glutamate/histamine
   inhibitory; 91 bodies with no prediction default excitatory.
4. **Antennal-lobe excitatory LNs: fast chemical output zeroed.**  With
   Shiu's model on either connectome, any olfactory drive (25 random ORNs at
   50 Hz) tips the network into a self-sustaining state of ~10 k neurons at
   the refractory ceiling; verified in the authors' own Brian2 code.  On
   MaleCNS the loop is the 157 cholinergic AL local neurons.  Lateral
   excitation in the AL is primarily electrical (Yaksi & Wilson 2010), which
   the LIF cannot represent; removing their chemical output is the single
   change that makes olfactory input bounded (`docs/phase2-stability.md`).
5. **KC→MBON gain 5.**  At connectome weight the plastic pathway contributes
   nothing to MBON odor responses (zeroing it changes nothing).  Gain 5 is
   the smallest at which MBON odor responses are ≥ 80% KC-driven
   (`docs/phase3-plasticity-gate.md`).  APL is left at connectome weight.
6. **Plasticity**: three-factor depression of KC→MBON synapses gated by DAN
   compartment (`config/mb_compartments.yaml`, Aso et al. 2014), on two
   timescales (`config/plasticity_v1.yaml`).  Short-term: one pairing,
   e-fold 4 h.  Long-term: forms only by spaced repetition (a pairing on a
   synapse still carrying short-term memory from a pairing ≥ 1 h earlier;
   Tully et al. 1994), e-fold 30 days.  Effective weight = connectome ×
   short × long.  Dopamine is modulatory only: a replay pairing re-presents
   the stored stimulus and gates the change; DANs are not driven as fast
   excitation.
7. **Encoder**: 12 of 35 valence-neutral glomeruli per account, 120 Hz;
   VADER → sugar/bitter GRNs up to 150 Hz; mention → JO-A/B 100 Hz; clock
   neurons on a 24 h cosine (`docs/circadian.md`).  KC activity 2–5% per
   account odor, odor-specific.  Background: clock neurons and bristle
   debris (landings; see 11).
8. **Readout** populations are cell-type lists with citations
   (`config/readout_populations.yaml`): engage → follow, reply → reply,
   like → like, leave → unfollow, groom → post.  Thresholds are provisional
   (synthetic battery, 85th percentile) until re-set from the dev-period
   distribution of real activity (`scripts/calibrate_thresholds.py`).
12. **Learned valence gates the readout.**  MBON output does not reach the
   descending neurons at any stable gain in the LIF (scans in
   `scripts/phase3_mbon_out_gain.py`: gains that propagate also smolder and
   move approach the wrong way).  Instead the readout does what summed MBON
   output does in the fly (Aso et al. 2014): v (decision 16) scales approach
   populations by (1 + 2v) and avoid by (1 − 2v) before thresholds.  `bosco memory --did X` prints v, the synapses carrying it,
   and the outcomes that caused it; `bosco people` ranks every account.
10. **Text**: `src/bosco/textgen.py`, a word n-gram (four words of context, backing off to three, two, one) with absolute-discount
   backoff over `corpus/` plus phrasebook lines.  The fly supplies the
   corpus subset (register tags, and `topic=` tags for what the post
   smelled of), temperature (arousal) and seed.  Not an LLM.
21. **Questions and being asked about oneself.**  A post with a `?` is a
   stronger touch (JO drive x1.5) and approach on it is a reply.  "what do
   you think of me" from anyone is answered with his real memory of their
   smell (`config/identity_v1.yaml` `memory_question`): unknown, neutral,
   sweet, or bitter, with how many times they came.
13. **Moderation**: labels from the account's subscribed moderation services
   are innate bitter and block approach (`config/moderation_v1.yaml`,
   `src/bosco/moderation.py`). The generator's vocabulary is closed.
11. **Scope**: Bosco reads his timeline and the discover feed; each unseen
   post is a stimulus; he may like, follow, unfollow, reply, and post, within
   per-kind caps (`config/caps_v1.yaml`).  Own posts come from grooming:
   debris lands on his bristles as discrete, seeded events (about 1.5 an
   hour); a landing is an onset, his grooming neurons answer onsets and
   adapt to held input, and if the answer crosses threshold he grooms, which
   is a post, and the debris resets.  There is no timer.  Operator commands
   by mention: `src/bosco/control.py`.
9. **Determinism**: single thread, fixed accumulation order, no FMA or
   fast-math, splitmix64 RNG.  His full state (voltages,
   conductances, adaptation, delay ring, RNG, plastic weights, debris drive)
   is snapshotted hourly; any span replays bit-identically from the snapshot
   before it plus the logged inputs (`bosco replay`). *Across machines*
   (2026-09-16, before the move to a dedicated server): the state digest
   used to differ between processes and machines while the dynamics did
   not. The delay ring was allocated uncleared and `lif_get_state` copied
   all of it, so unwritten slots carried whatever the heap held; the ring
   is cleared on reset now. With that fixed, one synthetic run gives one
   digest across hash seeds, machines, numpy's CPU code paths (x86-64-v2
   and v3 were tried) and BLAS thread counts. As a guard the container
   still pins numpy to x86-64-v3 (`ops/bosco.container`), the kernel is
   built for x86-64-v3, and the level he runs at is recorded
   (`Agent.numerics_level`); a change would be a `numerics` control row.
   `scripts/cpu_determinism.py` compares two boxes.
14. **Bosco runs continuously** (decided 2026-09-13; `src/bosco/brain.py`).
   No episodes from rest.  One biological second per wall second, about half
   a core.  Idle time is simulated in one-second slices with only the
   background drive (clock neurons, bristle debris); events are presented
   for one second on top; decisions are read from those windows; pairing
   depresses the synapses of the KCs that actually fired.
15. **Spike-frequency adaptation** (adaptive threshold, +0.1 mV per spike,
   1 s decay) so that activity settles after input instead of smouldering
   for ever in a continuous run.  Cost: sugar reflex 25 Hz instead of 69,
   MBON odor responses 6 Hz instead of 22; KC code unchanged
   (`scripts/phase2_sfa_scan.py`).  Denormal floats are flushed in the
   kernel; without that, long runs slow down a hundredfold.
17. **Topics as smells** (`config/topics_v1.yaml`, `src/bosco/topics.py`).
   A hand-written keyword list, published: whole-word matches on the post
   text name up to three topics, the text is discarded, the names are
   logged.  Each topic is three neutral glomeruli chosen by its name,
   driven at 100 Hz on top of the account odor, so a post is a mixture of
   who and what, and the same mushroom body that learns people learns
   subjects.  Not a classifier.  Sixty topics since 2026-09-14 (v1.2); the
   list is frozen with the encoder, so he cannot acquire a new subject, only
   a new opinion of one.
18. **Learning what to say** (`Agent.voice_update`).  When a generated reply
   or post gets an outcome, the corpus documents that matched its register
   get their preference nudged by 25% up (reward) or down (punishment),
   bounded 0.2 to 4, decaying toward 1 over two weeks.  Preferences scale
   how often each document's sentences enter the trigram pool.  Counts
   only; the vocabulary never changes.  Stored in `state/voice.json` and
   logged as `voice` control rows.
19. **Habituation** (`config/model_v1.yaml` `std_u`, `std_tau_rec`): short-term
   depression on sensory afferents only, 0.4% of resources per spike,
   recovery e-fold 3 min.  The same smell every two minutes settles near
   70%; a different account is fresh; twenty quiet minutes restore it.
   Central synapses are not depressed (docs/phase2-stability.md).  Costs
   the sugar reflex a little more: MN9 15 Hz at 100 Hz drive.
20. **Outcomes** (`src/bosco/bsky.py`): likes, reposts and follows from anyone
   reward the last window with that account (2 per account per day) and
   make the account known; a reply or quote to one of his posts punishes if
   VADER < −0.05, rewards if VADER > 0.3 from anyone or if the account is
   known; a block from someone he acted toward punishes.  Labeled accounts
   never reward.
16. **Learned valence is read from the weights**, not from MBON rates: a 1%
   uniform weight change flips a single-realisation MBON rate from 9 to
   6 Hz (deterministic chaos), so rates are averaged over seeds in the gates
   and the behavioural signal is the depression on the active KCs' synapses
   (reward-side minus punishment-side, Aso 2014 sign).

21. **Familiarity is a register** (`src/bosco/textgen.py`, decided 2026-09-14):
   corpus documents may carry `familiarity=new|known|familiar` (the
   phrasebook's bins over prior interactions with the account) and join the
   pool only when the account he is answering falls in that bin.  What he
   says to a stranger and to someone who keeps coming back differ by the
   ledger, not by a rule in the generator.  Corpus v2 (`corpus/090`–`129`)
   adds the twenty topic files, questions, night, the three familiarity
   registers, a file about his own learning, and sweet/bitter variants of
   the first-week topics.
22. **Stranger rail** (`src/bosco/bsky.py` `act`): toward an account he only
   browsed past (not mentioned by it), a like, follow or reply goes out only
   if that account has interacted with him before or his learned valence for
   its smell is above the cut.  The second condition is his memory; the first
   is a spam rail for a new account, logged as a withheld `leave`.

23. **The panel** (`panel/`, `src/bosco/panel.py`): the process writes a sparse
   list of the neurons that spiked in the last simulated second and a status
   JSON from the ledger; a static page (ARC UI, Vite) draws every neuron at
   its soma and lights the ones that fire. Read-only: nothing on the page can
   reach him. Post text is fetched from the public API by URI, never stored.
   Every window in the record says what came of it (`done`, the real action
   that went out) or which rail stopped the decision (`why`,
   `Panel.outcome_of`); rows from before the rails wrote their reason are
   read from what the poster did then, and say `unrecorded` when that is
   ambiguous.

24. **Activity blocks are eight neurons and the flush is 1e-4 mV** (kernel, decided
   2026-09-14). A block of neurons is skipped while all of them are at rest;
   with 64-neuron blocks and a 1e-9 mV flush, 34 spikes a second kept 82% of
   the brain "awake" and an idle second cost 0.42 wall s on a laptop. Eight-neuron
   blocks, rest flushed below 1e-4 mV and the adaptive threshold below 1e-2 mV
   (the spike threshold sits 7 mV above rest) bring that to 0.20 wall s with
   the readout bit-identical in the tests we ran; a 1e-3 mV flush changed
   which spikes fired and was rejected. The loop lives between polls instead of
   sleeping, checks notifications every 20 s and browses on the interval.

25. **Grooming is an onset** (`config/encoder_v1.yaml` `spontaneous`, decided
   2026-09-14). Day-one data: 25 grooms in 23 h, every landing crossing a
   10.5 Hz threshold, because dust never settled and the driven bristle
   subset was redrawn every second, so held debris was a new onset each
   second. Now one seeded permutation per landing picks the bristles (the
   subset shrinks as the debris settles, never adds an onset), dust settles
   passively with tau 600 s, landings come 0.5/h, and the 15 s after each
   landing are logged as `landing` windows so the groom threshold is set
   from real responses (peak per landing). No timer anywhere.
26. **Answering has a circuit: pC1** (`config/encoder_v1.yaml` `courtship`).
   The `reply` population is the courtship-song descending neurons, and in
   day-one data they sat at 0.0 Hz in every mention: nothing sensory reaches
   them (JO-B synapses onto the giant fibre). Being addressed now also
   excites the male courtship command neurons pC1/P1 (types `pC1*`, 156
   bodies; von Philipsborn 2011, Kohatsu 2011, Hoopfer 2015, Zhang 2016)
   at 12 Hz × appetite (× 1.5 for a question), the input we chose for the
   neurons that make the reply outputs fire, as bristle debris is for
   grooming. JO drops to 50 Hz (100 Hz made every mention a startle) and the
   question gain moves to the courtship drive. Walking toward whoever spoke
   to him is a reply; toward someone he only browsed past, a follow. Song
   answers speech: when he is addressed and the song population crosses its
   threshold that is the action, and if the proboscis population crossed
   too he likes the post as well (a fly can extend its proboscis and sing).
   Otherwise a kind question's sugar won as a like every time. Not a
   guarantee: threshold from the real distribution, learned valence still
   gates it, caps and the stranger rail still apply.
27. **Appetite for contact** (`config/appetite_v1.yaml`): a scalar in
   [0, 1] on the agent, rising toward 1 with e-fold 6 h without a social
   reward and taking a 30% bite on each reward; punishment leaves it
   alone. It scales the approach populations ×(1 + 0.5 (a − 0.5)), centred
   so it can neither force nor silence, and sets the courtship drive. It is
   state (saved, snapshotted, in the digest, logged on every window,
   replayed), ticks on his own clock, and is not a pain signal. It does
   nothing to the idle brain, which is the clock drive plus the minutes
   after a landing. A basal ORN drive for the panel's sake was measured
   (+43% idle CPU for spikes that reach no readout) and rejected.
28. **Thresholds follow a pre-registered policy** (`config/thresholds_policy.yaml`):
   engage, like and leave at the 85th percentile over event windows;
   reply at the 40th over windows in which he was addressed; groom at the
   70th over per-landing peaks. `scripts/calibrate_thresholds.py --policy`
   applies it; `ops/fetch_ledger.sh` copies the live ledger (features and
   URIs only) for it. Likes and follows removed in the app as him are
   reconciled on each sweep (`unliked_in_app`, `unfollowed_in_app`); the
   learning they earned stays, because the reward was for the window.

29. **Words as smells** (`config/words_v1.yaml`, decided 2026-09-14). Every
   content word of his closed vocabulary (about 850 words from the corpus
   and phrasebook, minus a published stop list) is an odor: three neutral
   glomeruli and a rate chosen by its hash, exactly as an account is an
   odor. A post's words that are in his vocabulary (up to six, in order)
   are driven on top of the account and topic odors; the sentence is never
   seen. A thread lingers: the words of its last three posts stay in the
   air for 15 minutes and are smelled again, fainter, with the next post in
   it, and his own posts draw on whatever is in the air.
   What the mushroom body learns from this is a memory of *mixtures*, not
   words: measured on the model, a word alone lights ~11 Kenyon cells, the
   same word with an account lights ~72, only ~4 are shared, and the cells a
   word adds to a mixture agree across accounts at 9% (Jaccard). A
   vocabulary-wide "which words are sweet" readout was built, found to
   return spurious verdicts for this reason, and removed. What is real and
   readable is "how does this word smell with this person": when he chooses
   words for a reply, the few words in the air are each presented with the
   account's odor to a snapshot of his state (restored to the byte, random
   stream included) and the verdict on the cells that fire scales that
   word's chance (`Agent.word_valence_in_context`). Words in the air also
   come up a little more (echo). His own posts are tied to his state by
   corpus tags: the hour (`time=`), his appetite (`appetite=`), and the
   grooming he is doing when he posts; the reflective corpus file that read
   as thought was removed. What he says is stitched from fragments by a
   trigram. None of this is understanding, and it is not meant to look
   like it.
30. **The air is read from his antennae** (decided 2026-09-14). A fly
   cannot hold a smell that is gone: at these rates a held odor habituates
   to a few percent within a minute, and he has no working-memory circuit
   for one, so none is invented. What he does have is habituation itself:
   every sensory afferent keeps a resource that drops with each spike and
   recovers over three minutes (`config/model_v1.yaml` `std_tau_rec`), so
   the mean depression over a word's olfactory neurons is a physical
   record of how recently, and how hard, he smelled it. When he chooses
   words, "in the air" is that depth read from the kernel over the words
   the log says were in his recent threads (`Agent.antennae`); a fresh
   word is heavy, one from two minutes ago faint, one from ten minutes
   ago gone. Candidates come from the log because words share glomeruli:
   a mixture of six depresses enough of them that a fifth of the
   vocabulary would read as present. The thread's lingering re-presentation
   (a plume does linger) is kept but cut to four minutes, and words smelled
   in the last minute are not re-presented since their afferents are still
   depressed. Remembering a conversation past that is the mushroom body's
   job, and needs a pairing: a like on his reply, a kind reply.
31. **He reads in his languages** (`BOSCO_LANGS`, default `en`). His
   vocabulary is English; a post in another language carries none of his
   words, hits no topic and tastes of nothing, so all that reached him was
   a stranger's odor, and in the dev period a quarter of what he browsed
   was that (146 of 629 posts with no topic and no taste, drawing 28 likes
   and 34 leaves). He now sets his content language the way any user does
   (an `Accept-Language` header, which the discover feed honours) and does
   not perceive a post whose record declares only languages he does not
   read. Posts that declare nothing are read. This is a setting on his
   account, not a change to any threshold; the next recalibration from the
   real ledger will see the narrower distribution.
32. **He goes places, and a place has a smell** (`config/feeds_v1.yaml`,
   decided 2026-09-14). He reads from a published list of feeds: the
   accounts he follows, discover, popular-with-friends, science, art,
   nature photography, cooking and bugs. Each feed is an odor of two
   neutral glomeruli chosen by its name, driven with every post read
   there on top of the account, topic and word odors, and logged on the
   row, so the mushroom body learns the place as part of whatever
   mixtures were rewarded or punished in it. Where he spends his browsing
   is his own doing: each poll the budget is split across feeds in
   proportion to his approaches there over the last two days (a like,
   follow or reply his readout decided on a post read in that feed) plus
   a prior, each feed keeping a floor of the budget so every place is
   still visited. That uses his behaviour, never outcomes, and touches no
   threshold. A fly stays on the patch where its proboscis has been
   extending. `bosco feeds` prints the split; the panel says where he has
   been reading.

33. **The off ramp** (decided 2026-09-14). People will not all want a fruit
   fly in their replies, and they should not need the operator to be rid of
   him. Any account that tells him to go by mention ("shoo fly" above all;
   also "go away", "leave me alone", "unfollow me", "stop", "opt out";
   `config/identity_v1.yaml`) is
   answered once, unfollowed, and placed on the ignore list under its own
   DID: never in his stimulus stream again, never approached, logged as
   `opt_out`. "come back" from the same account lifts it; the operator's
   ignores are not theirs to lift. A block works the same without words,
   and is the punishment signal besides; a mute costs nothing. Like the
   identity answers, this is a reflex outside the network, not a decision
   of his.

34. **Habituation recovers lazily** (kernel, decided 2026-09-14). A
   synapse's resource `x` is only read when its neuron spikes, so the
   kernel no longer relaxes every neuron's `x` every step; it records the
   step each `x` was last current and applies the whole recovery in one
   multiplication when the neuron next fires, when it is read back, or
   when time is skipped. The power `e^k` is computed by squaring in plain
   double arithmetic, not by libm, so a replay on another machine is still
   bit-identical. The saved state carries the per-neuron step; a state saved
   before this loads with every `x` marked current. Measured on the laptop
   from a rested network under the clock drive alone: a dead-quiet second
   (early afternoon, no clock cells driven) fell from 0.08 to 0.04 wall
   seconds, a morning second from 0.13 to 0.09, and an evening second (the
   evening cells at 6 Hz wake a quarter of the brain) from 0.35 to 0.28. The
   whole-brain sweep had been a fixed cost on every second; what remains in
   the evening is real synaptic traffic. Same dynamics, cheaper seconds.

35. **The outward policy** (decided 2026-09-14, after a leaky rail had
   him following people who had never heard of him). Browsing, he may
   follow or like whoever his readout picks, under the caps; that is his
   curiosity and it is allowed to be random. He replies only to someone who
   replied to him or tagged him, and at most once per post of theirs,
   whether the answer came from the network or a reflex. Engaging with an
   account he already follows while browsing is nothing. A post he merely
   browsed never gets a reply, whatever the song neurons did; the decision
   stays in the record as withheld, and since 2026-09-16 the placeholder row
   (`Ledger.withhold`) notes which rail: `<what>:<why>`, why one of
   `not_addressed`, `answered`, `not_following`, `asleep`, `cap:<which>`.
   The panel's record names the rail on the row. His own posts are grooming. Nothing
   else goes out. The earlier "stranger rail" (no like or follow until they
   had come to him, or the window's learned verdict was sweet) is gone: the
   window's verdict is on the whole mixture and generalised to strangers
   who shared a place or a topic, and the rule above makes it unnecessary.

36. **Innate smells** (`config/innate_v1.yaml`, decided 2026-09-14). A
   fly is born liking ripe and rotting fruit, vinegar and fermentation, and
   born avoiding geosmin, and each of those is a particular glomerulus with
   its own wiring to the lateral horn (the encoder already excluded them
   from neutral odors, with sources). The words of his vocabulary that
   literally name those smells (fruit, banana, apple, vinegar, wine, rot,
   dirt, twenty-two in all) are now driven on their real glomeruli instead
   of the neutral ones a hash would pick. Everything else about a word is
   unchanged: it is smelled with the account, the place and the topics, and
   the mushroom body learns the mixture. This is the fly's biology,
   published, not our opinion of the words; only words that name an odor a
   fly actually meets are listed, and taste words (sweet, sugar, honey) are
   not, since taste is the tone channel. One consequence is that all fruit
   words are one smell: banana and grape are the same glomeruli, as they
   are to a fly. Measured on the model (ten presentations each, raw rates,
   gate off, a different account each time): a post carrying a fermentation
   word drove the walking population to 6.7 ± 0.6 Hz against 3.7 ± 0.9 for
   a neutral word, so the innate approach wiring does carry through to the
   descending neurons; fruit and geosmin words did not differ from neutral
   within error, and the proboscis stayed at zero for all of them. The
   innate map is kept for what it is, the fly's own glomeruli, whatever the
   readout makes of each.
37. **The learned verdict stays a gate; the wiring carries a whisper**
   (measured 2026-09-14). We asked whether a learned smell could extend the
   proboscis through the connectome alone, as a trained odor does in a fly
   after odor–sugar conditioning, so the readout gate could go. From a
   rested brain, one mixture (account, place, topic, two words) was rewarded
   five times, two hours apart, by the real outcome path; its learned
   verdict reached +0.74. Read raw, with the gate off, the walking
   population went from 2.0 to about 2.3 Hz and the proboscis population
   from 0 to 0: the depressed KC→MBON synapses change MBON output, but at
   these rates the path onward to the descending neurons moves them by a
   tenth, and a proboscis with no sugar in front of it stays in. So the
   verdict keeps reaching behaviour through the readout gate
   (`config/readout_populations.yaml` `kappa`), as documented in decision
   12, and the gate's size is what stands in for the pathway the model
   cannot carry. Recorded here so nobody has to wonder whether we tried.

38. **An answer opens on their word; his own posts carry his day**
   (decided 2026-09-14). Two things changed about what he says, neither of
   them a model. When he answers someone, the generator now opens the
   utterance on one of the words on his antennae, drawn by freshness, from
   a context of his own corpus that ends in that word, and walks on from
   there; and the echo on words in the air is four times louder
   (`echo_gamma` 2.0). So a reply about bananas begins at banana, in his
   sentences. When he grooms, the register is chosen by his day: the
   valence of the post is the balance of his own verdicts on what he read
   in the last six hours, not the verdict on dust; a `mood=` tag from the
   ledger (stung within six hours of a punishment, warm within two of a
   reward, alone after a day without anyone coming to him) selects three
   new corpus files written in his register (`170`–`172`); and the words
   he met in those hours are a faint air on his own posts (`day_echo`), so
   a post of his is made of the day he had. None of it is understanding.
   It is a fly answering on the word you used, in the mood his day left him.
39. **An account's memory is its own smell** (fixed 2026-09-14). The panel
   showed the same learned valence for everyone because the readout used
   the Kenyon cells of the mixture an account last arrived in, which are
   mostly the place and the topics. Each account's odor is now presented by
   itself to a copy of his state once, the cells it lights are kept (on
   disk too), and the verdict is read on those. What you see beside a name
   is what he has learned about that smell, and the mixture verdicts stay
   where they belong, in the windows.

40. **Whoever speaks to him is answered; appetite sets how much he says**
   (decided 2026-09-14). Nick's rule: if you talk to a bot, you want a
   response, and he should be chatty with people who want to interact.
   Silence stays legal for everything he merely reads, but a mention, reply
   or quote that does not make his song neurons cross is answered anyway,
   once per post, under the caps, with the words the window produced: same
   valence, same arousal, primed on their words, phrasebook coin and all.
   The episode row keeps the network's decision ("nothing"); the action row
   is kind `answer`, and the panel's record shows "answer" for such a
   window, so nobody reading the ledger mistakes manners for his choice.
   What appetite decides now is length, not whether: one sentence when
   sated, up to three when hungry for company, one more for a smell he has
   learned to like and one fewer for one he avoids (`Agent.verbosity`).
   Nobody who did not speak to him is ever addressed.

41. **Four words of context, a line is a sentence, and he may end on one
   word** (decided 2026-09-14, after reading him). Three things made his
   sentences run together. The corpus was split into sentences only at
   periods, and most of his lines carry none, so the model learned to run
   one line into the next ("i drank some of it rain on the leaf"). A
   three-word minimum before a sentence could end forced continuations past
   the natural end of "banana" or "warm". And a trigram over 1,300 short
   lines splices any two that share two words. Now a line end is a sentence
   end; a one-word sentence is legal; the model keeps four words of context
   and backs off to three, two, one only when the corpus never saw the
   longer context; the continuations offered are only what the corpus saw
   follow that context; and ending a sentence where a corpus sentence ended
   is weighted 2.5 to 1 against splicing on. The effect is that he speaks
   in his own sentences, spliced where three words coincide, which on this
   corpus is rare. The corpus is lowercase throughout now, including the
   original short register (`010`–`080`), by Nick's instruction, and the
   second corpus pass broke its grammar toward the reference files without
   lengthening a single line.

42. **He reads the whole thread, and picks a sentence by smell before he
   stitches one** (decided 2026-09-14). A post that is part of a thread is
   no longer one second of smell: he reads the posts above it, up to
   twelve, oldest first, and their words of his vocabulary are smelled with
   it at the lower rate as context, a word said again counting as fresher.
   Text is read once and discarded; the words are logged on the row as
   before. Then, when he speaks, the first sentence is retrieval, not
   stitching: every sentence in the matching register is scored by the
   words on his antennae it contains, each by its freshness and by what he
   has learned of that word with this person, and the seed picks among the
   top five; the last thirty openings are excluded so he does not repeat
   himself. That sentence is whole and his; the n-gram adds to it only when
   his appetite gives him more than one sentence. This is lexical retrieval
   over his own corpus, no model and no embeddings: he says the sentence of
   his that smells most like the moment. When nothing in the air is in any
   sentence of his, he stitches as before.

43. **What he reads teaches him: taste while browsing** (decided
   2026-09-15). Until now dopamine fired only for outcomes (likes, kind
   replies, blocks); a thousand posts a day changed nothing but habituation.
   In the fly, sugar sensory neurons drive the PAM reward dopamine neurons
   and bitter ones the PPL1 punishment neurons; that is how odor-taste
   conditioning works at all. So the taste of a post he reads (VADER ->
   sugar or bitter GRNs, decision 7) now pairs the whole mixture in that
   window (account, place, topics, words) with reward or punishment in the
   window itself, at strength gain x the gustatory rate fraction
   (`config/plasticity_v1.yaml` `taste`: 0.15 reward, 0.1 punishment, a
   labeled post 0.3 as full bitter). Same rule as an outcome pairing
   (`Agent.learn_from_window`, `MushroomBody.pair_counts(scale=)`), a
   fraction of the strength, spaced repetition consolidating it like any
   other. Not a social reward: no appetite bite, no outcomes row; the
   episode row carries the weight digests and a `taste:` note, and replay
   does the same from the features. Sizes from `scripts/phase8_taste_gate.py`
   (`docs/phase8-taste.md`), never from outcomes. The confound is stated in
   EXPERIMENT.md §7: he will come to like sweet talkers, because a fly
   likes sugar; bitter, labels and blocks are the brakes, and because the
   rule is symmetric his taste is correctable. A change of learning rule
   breaks the replay chain across the commit that lands it, so the boundary
   is written down: `Agent.PLASTICITY_VERSION`, a `plasticity` control row
   and a snapshot the first time the new rule runs.
44. **Familiarity is a compartment** (decided 2026-09-15; Hattori et al.
   2017, Cell 169:956). The PPL1-α'3 dopamine neuron fires on mere
   exposure to an odor and depresses the α'3 terminals of the KCs that
   fired, so a familiar odor drives MBON-α'3 less than a novel one, and
   the fly's alerting response to a novel odor wanes as it becomes
   familiar. Compartment `a'3` (PPL104 -> MBON16/17/28 and MBON17-like,
   which the data supports at 49 synapses) moves out of the punishment set
   into its own `exposure` set (`config/mb_compartments.yaml`); every
   stimulus window depresses the exposure trace of the KCs that fired
   (`config/plasticity_v1.yaml` `exposure`: eta 0.3, floor 0.3, e-fold a
   day, so "today" is familiar and last week is not), and the mean
   depression over the KCs a smell lights is his familiarity with it
   (`MushroomBody.familiarity`, logged as `_familiar` on the row). It
   carries no valence and learned valence does not read it. It is read on
   the cells the smell *added*: the KCs busy in the idle second before the
   window (the clock's, kept as state) are left out, and a smell probed
   alone is probed from rest, as the account signature is (decision 39);
   otherwise the cells the clock keeps busy are met every second and
   everything reads familiar within the hour, which is what the first
   end-to-end run showed. The trace is
   kept per Kenyon cell and applied on that cell's edges into α'3 rather
   than per synapse, because in this model an account odor is carried
   almost entirely by γ KCs (about 110 cells fire, one or two of them
   α'/β') and only α'/β' KCs reach the α'3 MBONs: a per-synapse trace saw
   nothing. Novelty reaches behaviour as Hattori describes, alerting: the
   walking population is scaled by (1 + 0.5 (1 − familiarity)) before
   threshold (`readout_populations.yaml` `novelty_kappa`), so a smell he
   has not met is one he goes to look at.

45. **Closed mouth, open nose** (decided 2026-09-15; supersedes the closed
   vocabulary of 2026-09-13, which EXPERIMENT.md said would be revisited
   before the tag or not at all). Every content word of a post is a smell
   now, not only the ~850 of his corpus: a word outside his vocabulary is
   kept as the first eight bytes of `blake2b("word|" + word)`, written
   `h:<16 hex>`, and those bytes seed its glomeruli and rate exactly as a
   vocabulary word's hash does (`Encoder.hashed`, `config/words_v1.yaml`
   `perception`), so the same word is always the same smell and a
   vocabulary word and its hash are one smell. Up to four per post after
   the vocabulary words. A plural of his word is his word ("cats" is the
   smell of cat, `Encoder.fold`: a trailing s or es only, only when the
   singular is his; a rule you can read, not a stemmer), because the first
   end-to-end run asked him about cats and he smelled a hash. Internet
   shorthand is heard the same way (`perception.shorthand`, 2026-09-16):
   "gn" is his good and night, "ty" his thank, "lol" his laughed; the
   table is short and published, the shorthand is in no line of his, so he
   understands it and never says it. He can learn to like it, meet it again, and (WP4)
   associate it with a person; he can never say it: the generator's words
   are the corpus and the phrasebook, and a hashed token is in no sentence
   of his, so retrieval and the walk weigh it at nothing
   (`tests/test_words.py`). The guard that keeps him from learning slurs
   was always on his mouth; it is unchanged. The database holds the hash,
   never the word; a common word's hash can be brute-forced by anyone with
   a dictionary, and the discipline is that no text is stored, not secrecy.
46. **What else a post carries** (decided 2026-09-15; `Bsky.embed_features`,
   `config/encoder_v1.yaml` `embeds`). Until now only `record.text` was
   read. Now: a mention facet's DID, or a quoted post's author, is another
   person in the room, that account's odor at half rate (`others`, up to
   three, never the author or himself); a link card's site is a place, two
   neutral glomeruli by its domain like a feed (`site:<domain>`); alt text,
   card title and description, and a quoted post's text are read like the
   thread above a post, their words (and hashes) as context at the lower
   rate, and the topic map reads them with the text; images and video are
   named (`img`, `video`, and `motion` for video once the retina lands) for
   the retina. VADER stays on the post's own text. Two new columns on the
   row, `others` and `embed`, comma tokens, and `Agent.features_of_row`
   is now the one place a row becomes features again, for pairing, replay
   and the controls. A notification carries only the record, so a mention
   with an embed is fetched once for its view. Nothing of any of this is
   stored but words, hashes, DIDs, tokens.

47. **A retina** (decided 2026-09-15; `config/retina_v1.yaml`,
   `src/bosco/retina.py`, `docs/phase8-retina.md`). He can see, at a fly's
   resolution, and nothing tells him what he is looking at. A post's
   thumbnails (images, a video's poster, a link card's picture; at most two)
   are fetched once, reduced to a 32×24 grid of facets, and read as a few
   channel names by a fixed, public, parameter-free transform: the two
   dominant hues of eight (saturation-weighted, dull facets have no hue),
   the mean brightness in four bins, the mean edge strength in three, the
   mean saturation in three, plus `img` for any picture and `motion` for
   video. The channel names are what is stored (`embed` column); the
   histograms are a sensation and nothing comes back out of them, where a
   colour grid would be a thumbnail. Each channel is fifteen visual Kenyon
   cells chosen by its name, driven at 6 Hz: KCγd and KCα/βp are the cells
   that receive the visual projection neurons in the fly (Vogt et al. 2016;
   Li et al. 2020), and those afferents (246 traced bodies, ~10 k synapses
   onto them: aMe12, aMe26, MeVP41, …) went with the optic lobes, so the
   retina drives the KCs directly and they stand in for them; restoring
   `visual_projection` (9,201 bodies) was considered and rejected for cost
   and because no one knows which of them carries which feature. The
   visual KCs habituate like afferents (`model_v1.yaml`
   `habituation_extra_types`), so the same picture again fades and a
   picture's channels read as being in the air. Colour words and the words
   for pictures are the channels, the way "fruit" is the fruit glomeruli:
   "red" is the smell of red, "picture" is the smell of a picture, so a
   question about red things and a red thing he saw share a smell;
   "orange" stays fruit. What a picture means is whatever the mushroom
   body comes to associate with it; he will mistake a fox for a cat and a
   sunset for a ginger cat, and that is the resolution of the eye, not a
   bug in a classifier. Measured (`docs/phase8-retina.md`): a picture alone
   lights 1.8% of KCs, all of them visual KCs, and drives ten MBON types;
   with an account odor 4.4%; the same picture five times is familiar by
   the third and a different one right after is half familiar through the
   channels they share (`img`, brightness), as two feeds share a place.
   The live code depends on the machine's JPEG decoder; the logged
   channels are what replays, so replay and the controls are unaffected.
   Not a classifier, and it never becomes one.

48. **What he remembers about you, and his yes and no** (decided
   2026-09-15; `src/bosco/associations.py`, `config/associations_v1.yaml`).
   Two things that make a conversation less fake, neither of them a model.
   *An association memory*: each window, every token that arrived with an
   account (his words and hashed ones, the topics, a link's site, a
   picture's hues; not the thread's context, not the channels every
   picture shares) is strengthened for that account by one and decays
   e-fold fourteen days; when the account speaks to him again its
   strongest associations (twelve at most) are faintly in the air, a
   quarter of a fresh word's weight at three meetings, never over what is
   actually on his antennae, and the topics they carry join the pool
   (`Agent.answer_air`). So the sentence of his that smells most like the
   moment can be about the thing you two talked about last week. This is
   not in the connectome: it is a tool, named as such in EXPERIMENT.md §2,
   with no content that could be read back as text, a pure function of the
   logged rows (replay rebuilds it, it is in the brain digest, it fades on
   its own, `forget` drops it with the weights). Hashed and channel tokens
   are in no sentence of his and fall out of retrieval by themselves. *A
   seen register*: asked something, the freshest three of the words he was
   asked with are each presented alone to a copy of his state and the α'3
   familiarity of the cells that fire is read (`Agent.familiarity_of`); if
   the least familiar is above `seen_cut` (0.3, `words_v1.yaml`) the state
   tag is `seen=met`, else `seen=fresh`, and corpus files carrying that tag
   join the pool at twenty times a plain file's weight (`textgen.SEEN_WEIGHT`,
   about half the pool, so his yes or his no is most of the answer; a
   mention that asks nothing sets no tag) (`bosco say --seen met`). Nothing is parsed: "did you see
   any cats today" is the smell of cat on his antennae, and the answer is
   whether that smell is one he has met lately. Nick writes the yes and
   the no (`docs/CORPUS-PLAN.md` v4).

49. **Chemotaxis: a walk toward the source** (decided 2026-09-15). A fly
   that smells something it likes walks toward it. Browsing, the walking
   population now has a lower rung under its own threshold
   (`thresholds_policy.yaml` `walk`: the 60th percentile of the engage rate
   over real event windows, 2.9 Hz from the dev ledger of 2026-09-14;
   engage's own is 5.05): between the two he walks, which on the network
   is reading a few more of that account's own posts (`Bsky.walk`, three,
   from the place `walk`, each an ordinary stimulus with `walk:<action>`
   on its row); over engage's threshold he follows as before, and engage
   toward someone he already follows is a walk instead of nothing. A
   novel smell alerts (decision 44), so the same rate walks sooner when
   the smell is new. Addressed, never: walking toward whoever spoke to him
   is still a reply. A walk is not outward; `caps_v1.yaml` `walk` (6/h,
   40/d) is a loop guard, and a walk counts as an approach for the feed he
   walked from, so his browsing follows his own feet. The controls replay
   the walked posts as ordinary stimuli and are off-policy after the first
   walk they would not have taken (EXPERIMENT.md §4).
58. **Retrieval steers, it does not speak** (decided 2026-09-18; the first
   behaviour change after `freeze-v1`, so it is `freeze-v1.1`,
   `Agent.UTTERANCE_VERSION` 2, an `utterance` control row and a snapshot,
   and a note in EXPERIMENT.md §2d). Nick, reading him: he leans too hard on
   giving back sentences of the corpus and the phrasebook whole. He was
   right, and it was measurable. Decision 56 made a whole thought the unit
   of retrieval and had him say it, with the walk adding to it only when his
   appetite had more sentences in him than the thought already carried —
   which, a thought being two or three sentences and his appetite usually
   one, it almost never did. Over 293 of his own logged windows
   (`scripts/quotation_gate.py`, features only, no text is stored): 19% of
   his utterances were exactly a line of his, the longest unbroken run he
   shared with one line averaged 14.4 tokens, 92% of utterances carried a
   run of eight or more, and the average utterance was 94% that one run. A
   fly reciting a page is not answering anybody.

   Two changes, both in how he composes, none to what he can say. The
   retrieved thought is now where he *starts*: he opens on the word of
   theirs that lit it up, takes what precedes it in that thought as his
   context, and walks on in his own words (`textgen.generate`, `opening=`).
   Handed a word his own line happened to end on, he drops back to a shorter
   context and finds somewhere else of his to take it, rather than stopping
   dead on "today." And while he talks, he is followed along his own lines:
   once he has run `COPY_RUN_MAX` (6) tokens beside one of them, the words
   that would carry that line on are struck out wherever he has anywhere
   else to go (`_copy_step`, `_copy_next`). He may borrow a phrase; he may
   not recite a paragraph. The phrasebook went with it from a coin toss to a
   last resort: it speaks when the walk comes back with nothing at all.

   Same windows, same seeds, after: 0% exactly a line of his, longest run
   5.5 tokens (max 11), 13% carrying a run of eight or more, 72% of the
   average utterance. The corpus, the phrasebook, the encoder, the readout,
   the thresholds and the caps are untouched: same mouth, same nose,
   different hands.

   **And coherent while he does it** (`freeze-v1.2`, `UTTERANCE_VERSION` 3,
   the same day, after Nick read the first batch: too rough). The quoting was
   gone and the seams showed — "today has a sweet part in it is far in the
   dark", where the walk crosses from one of his lines to another mid-clause.
   The gate learned to count those: a sentence whose words are not one
   unbroken run of any line of his. It was 26% of sentences before any of
   this work and 25% after v1.1, so the splicing was never new; v1 had hidden
   it behind a verbatim opening. Three fixes, all about where a clause may
   start and stop. He carries the run-up to their word with him when it is
   short enough to be a phrase, so he opens on "some kind of wind came" and
   not "kind of wind came". Inside a sentence the words that finish the
   clause he is in are weighted up (`STAY_BIAS`), so he changes line between
   sentences, where it always reads. And where one of his own sentences stops
   he may stop, even on a word that dangles anywhere else: "today has a sweet
   part in it." is a line of his, and the anti-dangling rule had been pushing
   him off the end of it into somebody else's clause — which is exactly the
   garble above, and my own regression from the first pass. Nine tokens of
   leash instead of six, since a short sentence of his is about that long.
   Spliced sentences: 26% → 9%. Quoting stayed where v1.1 left it (0.3%
   exactly a line, 6.1 tokens, 22% at eight or more).

57. **Small talk reaches him** (decided 2026-09-16). The stoplist in
   `config/words_v1.yaml` is function words only now. Until then the
   conversational words were stopped too (know, like, want, think, see,
   say, come, thing, here, now, okay, yes, sure, maybe, again, never,
   always, nothing, something), so "i see", "how are you", "do you know
   me" reached his antennae as nothing and the answer came from the pool
   unprimed. `min_len` is 2: ok, no, go, up are his, and the two-letter
   function words (it, is, on, am, in, to, me, ...) are stopped by name.
   Bare `yes`, `no`, `on`, `off` are YAML booleans, so the list quotes
   them; the old list had silently carried `True`/`False` in place of
   `yes`/`off`. With common words smellable, a post can carry more of his
   words than `max_words`; `Encoder.words_for` then keeps the rarer ones
   in his corpus (`word_lines`, the number of corpus lines a word is in),
   in order of appearance, so "know" never crowds out "bird". Words are
   logged per row, so replay is unaffected; new rows smell of more.

56. **Answer-shaped corpus, and a thought is the unit of retrieval**
   (2026-09-16). A report over three days of posts addressed to him
   (33 posts, 23 answered; the script fetched the texts from the public
   API and kept only word counts) showed vocabulary was not the gap: most
   posts carried several of his words, but the sentences that share them
   were narrations, not answers, and what people call him (guy, bud,
   buddy, fella, pal) was not his at all. A conversation layer in the
   banana register, all `behaviour=reply`: `064-you-say.txt` (the words
   people use to him, in his own report of the thing), `065-what-they-
   call-me.txt`, `066-about-me.txt`, `067-praise.txt` (valence=positive),
   `068-insults.txt` (valence=negative), `069-feelings.txt`,
   `070-requests.txt`, `071-opinions.txt`, `072-time-and-days.txt`,
   `073-food.txt`, `074-animals.txt`, `075-internet-words.txt`,
   `076-the-world.txt`: 518 lines, the vocabulary from 896 to about
   1,100 words. A first draft opened every line with "you said X" /
   "you asked X"; Nick: he does not need to parrot the conversation to
   mimic intelligence. The word is in the line for retrieval, inside what
   he notices or does, never as a quote. With a reply pool this size the
   seen file's fixed weight no longer made it half the pool, so
   `model_for` sets that weight from the pool (at least `SEEN_WEIGHT`, at
   least half), and retrieval gives a seen line three times its score
   when he was asked (`SEEN_PICK`), so a question about a smell still
   gets his yes or his no first. Retrieval now scores and returns a whole
   corpus line (one thought, one to a few sentences) instead of one
   sentence: "you said thank." alone was a stub, and a short fragment
   always won the length penalty. The walk adds to the thought only when
   his appetite allows more sentences than the thought has. Still not
   reachable by any corpus: "i see", "how are you", "am i stinky" are
   stopwords or too short to smell (the encoder's stoplist, Nick's call).

55. **Holding a conversation** (decided 2026-09-16; the point of the
   experiment is whether he holds a more coherent thread than the bottom
   of the feed). Three rules, no model. The phrasebook speaks only when
   nothing of his smells of the moment: the retrieval opening is computed
   first, and the seeded coin between a line and the generator is tossed
   only when retrieval finds nothing (a line said whatever was asked read
   as a non sequitur). Retrieval scores coverage: a sentence sharing two
   of their words beats one loud word (`pick_sentence`, ×1.5 per extra
   shared word). Inside a thread the thread leads: a remembered word from
   the account's associations weighs at most half the faintest word
   actually on his antennae (`Agent.answer_air`), so an answer tracks the
   conversation, not his history with the person. Next: grow the
   conversation corpus, the ceiling on all of this.

56. **The panel says what happened, and the ceilings come up** (decided
   2026-09-17). The record read `follow withheld: a cap was full`, which
   tells a reader nothing: it names a part of the machine and leaves them to
   guess. Every line of it is a sentence about him now — *he wanted to follow
   @x, but he had already followed 6 people this hour* — and where a limit
   stopped him the line prints the real number from `config/caps_v1.yaml`.
   The words that went with the old form went with it: withheld, cap, rail,
   window, episode, and the bare Hz on the readout, which now says how close
   he is (quiet, stirring, nearly, over) with the rate on the row's title for
   anyone who wants it. What the page says and what the ledger stores are not
   the same thing; the ledger keeps `cap:follow/hour` as it always did.

   The ceilings moved with it, since reading them in plain words made it
   obvious they were shaping the account more than his neurons were: likes
   6/h → 12/h, follows 3/h → 6/h, replies and reflex answers 12/h → 24/h, his
   own posts 1/h → 2/h, and the backstop across all kinds 24/h → 48/h, which
   otherwise would have swallowed the rest. And a walk — staying to read a few
   more of one account's posts — no longer spends that backstop at all: it
   reaches nobody, so it is not the network's business, the way an unfollow
   never was (`Ledger.count_actions(exclude=)`). Its own ceiling went 6/h →
   24/h; what could loop is held by `per_account_actions_per_day`, which does
   count walks. Thresholds are untouched: none of this is set from outcomes.

55. **He went deaf at step 2^31** (found 2026-09-17). At 13:00 UTC on
   2026-09-16 his biological clock passed 59.7 h, and over the next four
   hours the KCs firing per window fell from a mean of about 170 (peaks of
   500 to 900) to a mean of 44 (peaks of 110), where they have stayed. His
   last post of his own went out in that same 13:00 hour; since then the
   browsing actions stop, and the only things that have gone out are the
   reflex answers to people who spoke to him, which do not ask the network
   for permission. Doubling the dust (53) changed nothing, because no
   landing was reaching anything. The cause is in none of that day's work.
   Habituation recovers lazily in the kernel (24): a sensory neuron's
   synaptic resources are brought up to date when it next spikes, from the
   number of steps since they last were, and the run loop measured that
   count with the step index truncated to int32. At dt 0.1 ms the index
   passes 2^31 after 59.7 h of biological time; after that every elapsed
   count reads negative, so no synapse recovers again and every afferent
   ratchets toward zero transmission as it fires. In the state read on
   2026-09-17 all 40,939 neurons still carried the same `x_step`, the one
   the last downtime skip wrote 16.9 h of his time earlier, and 2,607 of
   the 2,972 neurons habituation acts on sat below x = 0.01: his nose,
   his tongue and his bristles, transmitting nothing. `lif_get_x` reads
   from the 64-bit step, so the habituation looked healthy the whole time.
   The step index is 64-bit now, and the recovery it owes is paid at the
   first spike after the fix, because the time really did pass. The
   dynamics change there, so it is a boundary like a change of learning
   rule: `Agent.KERNEL_VERSION`, a `kernel` control row and a snapshot the
   first time the fixed kernel runs. The span between 13:00 UTC on
   2026-09-16 and that row is a fly going deaf, and it stays in the record
   as his.

54. **No "this one"** (decided 2026-09-16). The quote in an answer (50) was
   removed after its first day: both quotes that went out matched the
   question on a single word, and a quote embed notifies the quoted author,
   who never spoke to him. That is the outward reach the outward policy
   (35) forbids for replies, through a side door, and it looked like spam.
   `Ledger.best_liked_match` stays for the record; the `quote` cap is gone;
   the two `quote` rows in the ledger remain what they were.

53. **Not the same words twice, and more dust** (decided 2026-09-16). He
   answered twice in one thread with the same phrasebook line (the coin fell
   on the phrasebook both times and the key had few lines). Every utterance
   he posts leaves `said:<hash>` in its episode note; composing, a
   phrasebook line said in his last 30 posts falls through to the
   generator, and a generated text he said lately is redrawn with a fresh
   seed (`seed|again|k`, up to three times) before it goes. Nick also wanted
   him chattier on his own: dust lands twice as often
   (`config/encoder_v1.yaml` `landings_per_hour` 0.5 to 1.0, more onsets for
   the grooming neurons, thresholds untouched) and his own posts are capped
   at ten a day instead of six (`config/caps_v1.yaml`); still one an hour,
   still no floor.

52. **His clock is Denver's** (decided 2026-09-16). `config/circadian_v1.yaml`
   `tz` moved from America/New_York to America/Denver, where Nick is, so his
   day and Nick's coincide. A replay recomputes the clock-neuron hour from
   the tz, so the change is a boundary like `plasticity` and `numerics`:
   `Agent._mark_clock` writes a `clock` control row (`old->new`) and a
   snapshot on the first start after it, the days page names it in the fine
   print, and the day reports are re-bucketed once when the index's tz no
   longer matches (`Panel.write_days`).

51. **The pinned primer** (decided 2026-09-16). His profile pins a short
   thread that says what he is: a bot with a simulated fruit fly brain, not
   an AI or a language model, nothing generative, nothing of yours stored,
   built by @proto.cool with AI assistance, be nice, shoo fly to leave. The
   texts are `config/identity_v1.yaml` `primer` (in the identity digest);
   the operator posts them by mention (`@bosco primer`, `again` for a fresh
   thread) and the first post is pinned through the profile record's
   `pinnedPost`, swapped against the record as it was. Each post is an
   action of kind `primer`: never the network's choice, not in "what he
   said". A reply under the thread reaches his senses like a browsed post
   (row note `primer`) and is not answered unless it tags him; the primer
   is a notice, not a conversation. Bare addresses in anything he posts
   become link facets (`Bsky.rich`). Found on the way: `introduce` was in
   the command table but not in the parse order, so the operator's
   introduce command never parsed; both are in the order now.

50. **"This one": a liked post in an answer to a question** (decided
   2026-09-15; **removed 2026-09-16**, see 54). Asked something, he could point at the post he liked lately
   that smells most of the question: the words of the question and its
   topics are matched against the words, topics and embed tokens on the
   rows of posts he really liked in the last day (`Ledger.best_liked_match`,
   recency breaking ties), and the best is embedded as a quote in the
   reply or the etiquette answer, with its current cid from the public
   view. Only posts he already publicly liked, never from an account he
   ignores, one per answer, under `caps_v1.yaml` `quote` (4/h, 20/d); the
   action row's `embed_uri` keeps what he pointed at, and a `quote` row
   marks the choice. It is the difference between "yes" and "this one",
   built from data he already keeps.

Visual input since 2026-09-15: a retina (decision 47), not the optic lobes.

## Running

```
uv sync && make -C kernel
uv run python scripts/phase0_coverage.py     # needs data/raw/*.feather (see paths.py)
uv run pytest
uv run bosco poke --did did:plc:x --text "hello fly" --mention
uv run bosco spontaneous && uv run bosco say -n 5
uv run bosco memory --did did:plc:x && uv run bosco people
uv run bosco spontaneous --at 2026-09-14T12:00   # simulates the gap; reports grooms
uv run bosco replay                              # from the latest snapshot to now
BOSCO_HANDLE=... BOSCO_APP_PASSWORD=... uv run bosco run --dry-run
```
