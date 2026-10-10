# Do Fly Brains *actually* think in MORGAN style spectral MoE??? Probably not, but here is what I did find...
![Fly Connectome Render](./Images/Connectome.png)
### Testing a *biologically inspired* graph model that is efficient and interpretable. Non linear too.
[Summary here! ^v^ Click to skip the jargon...](./RESULTS.md)
## But why..?
While waiting on my SWAEV AI model training runs to finish I've been scrolling instagram and been seeing a lot of goofy projects related to mapping the fly brain to trade stock, or importing it to Minecraft and training it on those tasks. Resulting in a digital fly doing silly things. Seeing a fly play beat saber made me question what the hell is this all about? Are people using the actual biophysical neurological replica of a fly brain and forcing it to learn these novel tasks... or maybe the answer is more simpler. I have found that for most of these project it is in fact more boring than it seems :(

My understanding is this all stems from researchers that mapped out all the pathways in a fly's brain. Huge respect. That is awesome and the dedication is insane. Releasing this in form of a graph of all the connections is the basis that these projects go off of. Mapping perceptrons onto the nodes of the graph in place of biological neurons is the methods they are using to bring the brain "to life". So the architecture of the graph serving as an actual fly in these projects is kinda a stretch to me. I mean its just altering the structure of a neural network... the rest is just standard dense neural network and transformer practice. This is true at least for these goofy applications of the fly brain structure. I have found that there are researchers genuinely creating novel neural network architectures to mimic and capture the biophysicalities of the fly. Sick. I love applying biophysics to neural networks to make them make more sense and learn more about biology. Here are some cool stuff I did find:

+ **FlyGM (Fly-connectomic Graph Model)** -> *Zehao Jin, Yaoye Zhu, Chen Zhang, Yanan Sui* (**Tsinghua / Georgia Tech**).

+ **BPU (Biological Processing Unit)** -> *Siyu Yu, Zihan Qin, Tingshan Liu, Beiya Xu, R. Jacob Vogelstein, Jason Brown, Joshua T. Vogelstein* (**Johns Hopkins**). 

+ **Shiu et al. LIF model** -> *Philip Shiu, Gabriella Sterne, Salil Bidaye* (**UC Berkeley → Eon Systems**). 

+ **Lappalainen et al. connectome-constrained network** -> *Janne K. Lappalainen, Fabian D. Tschopp, Sridhama Prakhya, Mason McGill, Aljoscha Nern, Kazunori Shinomiya, Shin-ya Takemura, Eyal Gruntman, Jakob H. Macke, Srinivas C. Turaga* (**Tübingen / Janelia / Stanford**).

+ **KCNet** -> *Jinyung Hong, Theodore P. Pavlic* (**Arizona State**).

+ **Eon Systems embodied fly** -> *Eon Systems team* (building on *Shiu et al.* + *Lappalainen et al.* + *NeuroMechFly*). 

Also important to mention that my idea of connecting spectral graph neural networks (GNN) with mixture of experts (MoE) GNNs is already formalised as MORGAN (**M**ixture **o**f **R**outed **G**r**a**ph **N**etworks) by Lihui Liu and Yuchen Yan, published at AAAI 2026. Huge thanks to this work. Additionally, I will be implementing my own contributions onto this design.

*After this dive I decided to add in my own efforts. I am bored and my curiousity had spiked!*

## My approach.
So the source of it all is the FlyWire connectome. It is essentially a complete wiring diagram of an adult Drosophila brain (YAY I worked on fruitfly dna before!). Entailing "roughly 140,000 neurons and 50 million synaptic connections". Neurons as nodes and synaptic connections just refers to the wires between these nodes. 

*Now that I have done the due diligence of prerequisite research. Time to start applying my domain.*

MoE design is the non-negotiable for me... I mean it's an absolute fact that different parts of our brains specialise in certain actions.

+ MoE LLMs HAVE been proven to be lightweight in inference and also have superb performance. Stuff like some the Qwen models... For a biology inspired NN this makes sense I think. 

+ MORGAN splits a graph onto an MoE framework and parts the graph spectrum into frequency bands. It assigns a specialized "expert" network to each band. A gating function then dynamically combines these experts based on the input's spectral characteristics (so how the graph was broken down aka laplacian eigenvalues). 

Additionally I will be adding cosine dampening to the architecture. The fly brain is a dynamical system. "Neural circuits exhibit oscillatory activity". A damped cosine kernel is a more faithful mathematical description of these biological processes than an MLP. I am also adding it because I can. It's a gap in this space of research and adding the dimension of temporal time dynamics is cool. The equation for a cosine dampened by eulers number (very nice differentiation) is...

$$cos(ωt + φ) · e^(αt)$$

Off course we are working with a graph of a fly's brain, so the build starts off with a directed graph **G** for **G** **=** **(V,E)**. Now **V** is the set of neurons in the brain and **E** is the set of synaptic connections in said neurons. [Click for more messy math!](./Images/scan.pdf)

The FlyWire connectome is a lot of graph. Before anything *spectral* or *expert* happens I need to carve out a piece that's small enough to actually train on and still meaningful as a computation. My crappy dl380p cant handle all that. First constraint done...

## 1.

*A circuit and not the whole brain...*
<hr/>

I think the feeding circuit will be the best to test. **Shiu et al** showed this thing predicts the "proboscis extension". The MN9 motor neuron was something I will keep no matter what. So I kept neurons that sit on short paths from the taste neurons (sugar, bitter, water, Ir94e... 88 total) to MN9. "Short" meaning within **k** hops downstream of a taste neuron and within **k** hops upstream of MN9. Just wiring... the teacher can't leak into the structure. OK.

TBH I only expected a few thousand neurons at **k = 2**. Well I got 5,516, which blew past my 5,000 cap. I decided to keep the taste neurons and MN9 no matter what, then prefer neurons on shorter "taste-to-MN9 paths", break ties by total synaptic strength.

So the final circuit is 5,000 neurons, 548,286 edges, 40.1% inhibitory. Median out-degree 93, median in-degree 85. Roughly bell shaped on a log axis, with in-degree having the fatter low-degree tail. All five checks passed (size in range, all 88 taste neurons present, both MN9 neurons present, a directed path from taste to each MN9 and no isolated neurons). `runs/r1_subcircuit/20260929-113520`

![1](./figures/r1_degree_distribution.png)

Cool. I have a graph.

## 2. 

*A GPU fly that agrees with the real fly...*
<hr/>

Shiu's model is a leaky integrate-and-fire spiking network written in Brian2. It runs on CPU. Pointless for generating 12,000 trials of training data. So I rewrote the whole thing in PyTorch to run batched on a 3060

First things first... does my GPU fly agree with Shiu's fly? The port had to match Brian2 spike-for-spike on a 50-neuron toy network first (it did), and then I ran the original Brian2 code side by side with my port on the whole 127,400-neuron brain: sugar neurons at 50-200 Hz and sugar at 100 Hz with bitter at 0-200 Hz, 30 trials each.

**The MN9 dose-response numbers (port vs Brian2, mean ± 2 SE):**

![1](./Images/first.jpg)

Every dose is within 2 standard errors of the difference. Bitter suppresses MN9 in both (from ~67 Hz down to 3.5/4.5 Hz at 100 Hz bitter, essentially silent at 200 Hz). Across 346 active neurons, rates correlate at r = 0.9995. Even excluding the 21 Poisson-driven sugar neurons, r = 0.9996 on the 325 neurons that only fire because of the network.

![2](./figures/r2_teacher_validation.png)

The port runs at 6,354 trials/hour at batch 256, so the 3000-condition × 4-trial dataset took about 1.9 hrs. The Brian2 reference took 1793 s with 30 processes.

We passed on all three checks (MN9 dose response, bitter suppression, network-wide rates r > 0.9). `runs/r2_teacher_validation/20260929-130111`.

**PLEASE READ!!!!**

*Brian2 validation covered only the 346 neurons active under sugar at 100 Hz. Of those, at least 330 are in my 5,000-neuron circuit, against the ~1,330 circuit neurons that are ever active in the dataset. So the comparison touched roughly a quarter of the circuit's active neurons. The teacher's accuracy on the near silent majority is unvalidated. Also, the Brian2 comparison drove only sugar_R and bitter at constant drive for the full second... the dataset drives all five taste channels with a 500 ms on / 500 ms off step, supervised in 20 ms bins. The off-period and the 20 ms bin structure are validated only by the 50-neuron test, not at whole-brain scale. And sugar_L, water and Ir94e were never compared against Brian2 at all.*

*So "validated teacher" means "validated on the part of the circuit that was active under one specific stimulus".*

## 3.

*The dataset*
<hr/>

3000 taste cocktails × 4 trials, 50 bins of 20 ms, 5000 neurons = 3 GB. Generated in 1.95 hours.

**73.4% of the circuit never fired at all.** Those get excluded from R² later. Only ~1,330 of 5,000 neurons carry any signal, and 90.4% fire below 1 Hz on average. Median neuron rate: 0.0 Hz. MN9 during stimulus: 10th/50th/90th percentile 0.0 / 5.0 / 72.5 Hz.

That low median is consistent with bitter-heavy cocktails silencing MN9. The numbers alone don't prove that mechanism. Also the 3 GB is mostly zeros.

Also also...the GPU simulator is not bit-reproducible. The drift measured during validation was about 0.2 Hz on an MN9 mean of ~90 Hz... which is well inside the ~1 Hz standard error. For training all good but not fine if you want to reproduce my exact bytes.

## 4.

*The MORGAN Part*
<hr/>

This is where the "spectral" in "spectral MoE" comes in haha. Two Laplacians on the 5,000-neuron circuit...

+ A signed symmetric one, which throws away direction (which way a synapse points).
+ A signed magnetic one, which keeps direction as a complex phase **(q = 0.25)**.

Full eigendecomposition of each, then chop the spectrum into 4 bands with equal numbers of modes, one per future expert.

The math says eigenvalues must be in [0, 2]. They are. But the spectrum is nowhere near touching the bounds. Symmetric μ ∈ [0.299, 1.6265], magnetic μ ∈ [0.434, 1.5412]. Orthonormality error ~5e-06 against a 1e-3 tolerance. Most modes pile up around μ = 1... the two middle bands are tiny slivers (symmetric band 2 is 0.9438 to 1.0039, band 3 is 1.0039 to 1.0627). About 3,300 of 5,000 symmetric modes (3,100 magnetic) are packed between 0.9 and 1.1.

![3](./figures/r3_spectra.png)

So "low frequency" here is not a smooth near zero mode. There is no eigenvalue anywhere near 0. The band 1/2 and 3/4 boundaries fall inside a dense... nearly degenerate cluster, so the middle band split is somewhat arbitrary. Nudge a boundary and different modes swap between bands 2 and 3.

Why try magnetic at all? 40,566 of 76,672 reciprocal connections have opposite signs (one side excites, the other inhibits)... those cancel when you symmetrize. That's 53% of all reciprocal pairs. The magnetic version keeps direction instead of cancelling it. But this run does not show that the magnetic version helps. Nothing here tests whether the magnetic basis recovers the information the symmetric one cancels. Also at the resolution of the localization figure the two bases look nearly identical. Test later!

The localization figure (log2 of a band's mean energy in a hop group, versus a mode spread evenly over all neurons) says less than I hoped :( . Most neurons are two hops from the taste neurons (4,309 of 5,000) and two hops from MN9 (4,648 of 5,000)... for those the enrichment is within ±0.02 in every band... the bulk of the circuit is unremarkable. All the action is in the small groups. Taste neurons themselves (88) are enriched in band 3 and depleted in band 1. Near MN9, the outer bands (1 and 4) put about 2× the uniform energy on the 2 MN9 neurons themselves, while the two middle bands nearly avoid them (6-7× below uniform). But that's two specific neurons, and I'm not generalizing it to "output neurons" or anything broader...

![4](./figures/r3_band_localization.png)

We passed (both eigenvalue ranges inside [0, 2], both orthonormal). `runs/r3_spectrum/20260929-185738`

## 5.

*Baselines*
<hr/>

Alright. 5 models with same data, split and loss

+ `mean`: predict each neuron's average response. The floor.
+ `mlp`: stimulus in, 5,000 rates out, no graph.
+ `chebgru`: Chebyshev graph convolution feeding a GRU.
+ `moe_single` and `moe_linear`: spectral mixture-of-experts variants using the magnetic basis from Step 4 above.

Three seeds each. The check... the per-neuron-mean floor must score below 0.8 normalised R², otherwise a trivial predictor already lives at the ceiling and everything downstream is meaningless.

**Normalised R² on held-out stimuli (3 seeds each):**

![2](./Images/second.jpg)

The graph-free MLP beats every graph model. On the normalised statistic, the graph models are not just worse than the MLP but far worse than predicting each neuron's mean...

But this isn't the full picture in my opinion. 
**Here's the fuller picture (seed 0, observed-active neurons, held-out stimuli):**

![3](./Images/third.jpg)

Reading across the table... the mean is dragged far below zero...neurons that are nearly silent have tiny absolute errors but also tiny variance, so their per-neuron R² explodes negative, a handful of those swamp the average. The median neuron tells a more calm story... the graph models sit roughly level with the per-neuron mean (-0.03, -0.05, -0.18 against +0.04), while the MLP is clearly ahead at 0.37. Also pooled R², which asks whether the model captured the population structure at all, has every model above the floor (0.77 to 0.90 against 0.458).

![5](./figures/r4_baselines.png)

So the graph models do learn something real about which neurons respond and roughly how much. What they lose is condition-by-condition, per-neuron detail... and a few near-silent neurons turn that loss into huge negative numbers. MN9, the output I care about most, shows the same ordering. Trace R² for the two MN9 neurons is mlp 0.83/0.75, chebgru 0.66/0.59, moe_linear ~0.00, moe_single ~-0.05.

The parameter counts are the story behind the table. The MLP has 27.5 million. The graph models have 425, 323 and 2,513. The graph models are node-agnostic by design... no per-neuron parameters at all, one shared mechanism applied over the connectome. That's exactly what will make the held-out-neuron test and the rewiring control meaningful later... it's also exactly why they cannot memorise per-neuron responses the way the MLP can. Part of the MLP's win is memorisation of 5,000 individual response profiles. I should not read it as "the MLP found better structure."

Honestly, almost every graph model hit the 40-epoch cap and was still improving. Best epoch 39 or 40 of 40 for all three moe_linear and all three moe_single seeds and for chebgru seeds 0 and 1. The MLP converged (best epochs 34/33/31). The 40-epoch cap is a compute trim of mine. So "this architecture underperforms an MLP" is currently tied to "this architecture was undertrained". Paired comparisons among the models remain valid since every model got the same budget... the absolute conclusion is not.

The check passed... the mean predictor scores 0.145, well under 0.8, so the task discriminates between models. `runs/p2_r4_baselines/20260930-185745`

Learning rate detour... because it was a real decision. The first pilot (3 rates, 6 epochs, 300 conditions) picked 3e-3 for every family by final val loss. That's the edge of the grid, and val loss and normalised R² disagreed about the best rate. So I killed the sweep and ran an extended pilot (5 rates, 15 epochs). The two criteria then agreed and chose 3e-2 for the MoE and chebgru families. I overrode that to 1e-2... 3e-2 was again the grid edge, the gain over 1e-2 was marginal, the MLP collapsed at 3e-2, then the real runs take ~7× more steps at the peak rate than the pilot. I traded a few percent of val loss for safety. The MLP kept its own interior optimum of 3e-3.

## 5 ½. ???

*I was wrong about silent neurons :(*
<hr/>

Step 4's runs trained on `ever_active`... the 1,062 neurons that spike at least once somewhere in the dataset. The alternative, `all_observed`, trains on all 4,018 observed neurons including the ones that are silent throughout. I had assumed the silent neurons would flatten the signal and make training worse. **So I ran a two-arm A/B on moe_full, three seeds each:**

![4](./Images/fourth.jpg)

A difference of 5.43 against a pooled seed spread of 1.68. My assumption was wrong... by a lot! Training on the silent neurons helps a great deal. I assume it is because "stay quiet" is most of what this circuit does. I guess a model that is never asked to learn it spends its capacity badly.

**So I ran it back, the whole baseline set under `all_observed` now (12 runs, 21 h 54 m):**

![5](./Images/fifth.jpg)

The mean predictor scores identically under both masks (0.14491 to five figures). This is the check I wanted. Every graph model improved very nicely and chebgru's seed-2 instability vanished... its three seeds now sit in a 0.36-wide band instead of a 2.4-wide one. The ordering did not change at all. The MLP still wins... every graph model is still far below the mean-predictor floor. A better loss mask made the graph models much less bad without making them good.

Under `all_observed`, every graph model stopped at best epoch 38, 39 or 40 out of 40, in every seed, with early-stopping patience never firing, while the MLP converged at 30 to 34. The budget binds the architectures I am testing and does not bind the one they are losing to.

`runs/p2_baselines_all_observed/20261002-143604`

## 6.

*The MoE Level*
<hr/>

This step is what the whole project was built for. My 4 dampedwave experts, one per frequency band, an input-dependent router, two layers with a nonlinearity between them. This is getting exciting!

Two questions I have. Checked by the rule I place before seeing any of it... a difference counts only if the mean paired difference across seeds beats twice the seed-to-seed spread and every seed agrees on the sign. Gotta make Rules to check my hypothesising. This da real science.

+ Rule 1 (non-collapse): does moe_full beat moe_linear? If not, the architecture is an expensive linear filter.
+ Rule 2 (specialisation): in at least 2 of 3 seeds, do two experts in some layer have channel-median timescales differing by 2× or more?

![6](./Images/sixth.jpg)

**Results of Rule 1:**

The full model beat its linear ablation in all three seeds (never worse) and still cannot claim it, because seed 1 came in at -0.48 while seed 0 came in at -2.95... and that spread swallows it. The interpretation I think is "suggestive and underpowered at three seeds" not "no effect". The rule is there precisely so I cannot hype myself past it after the fact. I have no claim.

**Results of Rule 2:**

It **passes**. Max timescale ratios of 1.67 / 2.11 / 9.48, so two of three seeds clear 2×. I have to read 9.48 with caution however...

![6](./figures/r5_expert_kernels.png)

In seed 2, layer 2, band 1 is the only expert in these runs that landed overdamped. Its reported `timescale_ms` of 7 ms is `bin_ms / γ`, which is a decay time only in the underdamped/critically damped regimes... the blue curve is visibly the slowest decaying expert, not a 7 ms one. The 7 ms also comes from a bad median... the channel γ values are `[0.22, 0.26, 0.34, 1.31, 4.26, 4.61, 6.32, 7.11]`, so the median 2.78 sits in an empty gap. And `1/median(γ)` vs `median(1/γ)` gives 9.48 vs 6.82... not quoting 9.48×.

Seed 1’s 2.11× (36 vs 76 ms, both underdamped) looked clean but isn’t. In layer 2, the check puts weight 1.000 on expert 3, the only expert that moved from init... experts 0-2 stayed near 0.3 and never trained. So the ratio is one trained expert against three frozen ones. Check weight scales the gradient. With no load balancing loss, once the check saturates the others stop learning. Rule 2 therefore cannot distinguish specialization from frozen at init. That is a flaw in the rule.

Everything else is normal... 30-81 ms, underdamped, settling within 400 ms... per-channel timescales inside a live expert range from about 16 to 93 ms.

**The router is the negative finding...**

![Where the router sends its weight, per seed and per layer](./figures/r5_gates.png)

So at max, the router learned a stimulus-present/absent detector...but mostly learned nothing. I don't think this is a bug (pun intended!) and I guess I had a hint istarting out... the stimulus space is five-dimensional (five taste channels), the conditions are static steps and the experts all converged on similar kinematics anyway. A router with four near-identical things to route between, locked on five numbers, has very little to do. This is the task I built... nothing about mixtures of experts. My bad.

**Rule 1 (does it avoid collapsing to linear?)** NAH: +0.61/+3.17/+2.37, mean 2.046 against a 2σ threshold of 2.616. Positive in every seed, not separable from seed noise.

**Rule 2 (do experts specialise in timescale?)** YEAH: 2 of 3 seeds at 2.11× and 9.48×, with the problem of how I measured it.

AND the thing that overshadows both... the headline model scores -1.59 mean normalised R² against a mean-predictor floor of 0.145, while stopping at best epoch 38/39/40 of 40 with patience never firing. I am not going to interpret "the spectral MoE loses to predicting each neuron's average" until I know what the epoch cap cost.

`runs/p2_r5_moe/20261003-124145`

I suppose what is next is the control that decides whether any of this is about the fly. A rewired connectome with identical degrees and signs. A direction-blind symmetric basis, both retrained from scratch. If the graph models do just as well on a rewired graph, then the connectome structure isn't doing the work. If they don't, then maybe there's something there. This will hopefully work or at least bring me some useful info.

## 7.

*The connectome matters*
<hr/>

OK, the control is done. Last time I said the rewiring and symmetric-basis controls would decide whether any of this is actually about the fly. They did. The answer is...a partly yes?... not in the way I expected. **I tried 2 controls and one dissection, all on the full model:**

+ Rewire the connectome. Shuffle the edges while keeping every neuron's in-degree, out-degree, excitatory/inhibitory counts and weight multiset exactly as they were. Rebuild the eigenbasis from scratch. Retrain. One fresh rewiring per seed, three seeds. If a graph with the same statistics but not the same structure does just as well, the structure was never the point.

+ Throw direction away. Swap the direction-aware magnetic Laplacian for the symmetric one, keeping the real graph. Three seeds.

+ Switch each frequency band off at test time on the trained seed-0 model and see which neurons notice, grouped by how many hops they sit from the taste inputs.

Well I expected the real graph to win. 53% of reciprocal connections in this subcircuit carry opposite signs and symmetrisation destroys that. I expected direction to matter for the same reason.

What actually happened though...


![7](./Images/seventh.jpg)

![7](./figures/r6_controls.png)

Does the connectome matter? Yeah. The specific wiring of this circuit carries signal that a degree and sign matched random graph does not. The model IS using it.

**Four problems though...**

+ Reciprocity is not preserved by the swap procedure. So the gap says "something beyond degree and sign", not specifically "reciprocal sign structure". The control is a null for all of that at once, not a dissection of it.

+ Unweighted in- and out-degree are preserved exactly and weighted out-strength is preserved because weights travel with their source edge... but weighted in-strength is not.

+ `swaps_per_edge=10` counts attempted swaps. Ones that would make a self-loop or a duplicate edge are skipped. So the realised displacement is the number that matters... 0.9448 / 0.9445 / 0.9444, measured on the real graph per seed.

+ A fresh rewiring is drawn per seed, so the three rewired runs differ in both initialisation and graph. This is intentional. For me one fixed rewiring would merge "this particular graph is easy" with "rewired graphs are easy".

+ Lastly, 1 thing I should not cover. All three arms are far below the mean-predictor floor of 0.145, which is why that dashed line is on the figure. Real beating rewired here means less bad, not good. It is still a real result... destroying the structure makes the model four to five times worse in normalised terms... but nobody should read the left-hand bar as a working model to be honest.

**But does direction matter..?** This failed in a weird way. Magnetic minus symmetric is -1.31 / +0.94 / -0.29, mean -0.22 with mixed signs. No claim either way and if anything the direction-blind symmetric basis is slightly ahead (-1.37 against -1.59). I built the signed magnetic Laplacian specifically because 53% of reciprocal pairs disagree in sign and that argument predicted a gap that is just simply not there. Either the model never learned to use the phase information or at this scale the symmetrised graph retains everything the model is capable of exploiting. I cannot separate those two with the runs I have right now. Maybe this is a future test.

**Now the brutal dissection :(**

![8](./figures/r6_knockouts.png)

Switching bands 2, 3 and 4 off moves the predictions by somewhere between 5e-10 and 2.4e-7!? That is float noise. The three flat lines sit on top of each other at zero, which is why I had to dash them to see them at all. This is Part 6's check collapse showing up as mechanism. In seed 0 the router sends all its weight to band 1 in both layers. The three of the four experts aren't even underused...but inert. A quarter of the architecture is doing all of the work and the rest is what I can only describe as fancy decoration.

Band 1... the only live expert... has mean knockout effect -2.05 at one hop from the input, which first looked like deleting the only working expert improves predictions. However the median there is +0.199. Nearly walked into the Part 5 trap... a few near-silent, low-variance neurons produce huge negative per-neuron R², dragging the mean below zero while the typical neuron is fine. Band 1 helps the median neuron at every hop (+0.025, +0.199, +0.045)... most neurons a little, a small tail destroyed at one hop. Highkey embarrassing to catch in my own analysis after writing that warning. Counts 88 / 194 / 564 are observed-active neurons at each hop (summing to the 846 scored)... the circuit has 88 / 603 / 4,309 neurons at those distances.

OK this is what I think is going on...Part 6 concluded the router never learned to route. This shows the cost. With three experts inert, `moe_full` is what I can describe as a single-expert model with a wasted parameter budget. Exactly consistent with Rule 1 failing to separate it from `moe_linear` AND with `moe_single` being within noise of it. The architecture's central idea that different frequency bands want different damped kernels and a router should pick between them never even engaged on this task.

**Conclusions conclusions conclusions...** Connectome matters (5.46 against 3.76). Direction doesn't (-0.22, mixed signs). Band specialisation is not used at inference (3 out of 4 are useless up to no good). Seed 2's second layer does spread across all four. Not true for every seed? 

`runs/p2_r6_controls/20261003-130247` rewiring in `runs/p2_rewired/20261003-124855`. Both figures were redrawn from the saved metrics with `scripts/part7_controls.py --replot`... no retraining. The controls figure gained the floor line. The knockout figure gained a zero line and per-band line styles. The 3 inert experts would be invisible underneath one another so yeah.

## 8. A conclusion

*Failure*
<hr/>

Here's what I know in the end. 

![9](./figures/summary_table.png)

+ **MoE vs ablations**... `moe_full` beat `moe_linear` in all three seeds (+0.61 / +3.17 / +2.37)... but the mean difference, 2.046, didn't clear twice the seed spread, 2.617. My commited rule 1 is not met. Against `moe_single` and `chebgru`, signs were mixed. Three seeds was too little resolution.

+ **Specialisation and router**... rule 2 passes only on its letter. Two seeds show a 2×+ timescale ratio... but the checked layers compare one trained expert against three frozen ones. Not really fair tbh. Seed 2’s 9.48× becomes 6.82× under an equally defensible reading. Another flaw in my rule. The router is input-independent in every seed. R6 knockouts change seed-0 predictions only at 1e-7... three of four experts are inert. The architecture’s purpose never even engaged.

+ **The fly connectome**... Rewiring while preserving in-degree, out-degree, sign counts and weight multiset... displacing 94.4% of edges... costs 5.46 normalised R², clearing the 3.76 threshold with the same sign in all seeds. Direction doesn't matter... magnetic and symmetric bases are within noise, with symmetric nominally ahead despite 52.9% of reciprocal pairs disagreeing in sign. This is my only win.

+ **Undertraining cap**... Nearly every model hit the 40epoch cap. A 120epoch probe (seed 0) gained 0.43 for three times the compute (-2.947 to -2.517), with validation loss 0.2237 -> 0.1976 and best epoch 114/120. The gap to the mean-predictor floor is 2.66. Undertraining was real, worth roughly 0.4. HOWEVER it does not explain a 2.7 shortfall. The cosine schedule stretches with the cap, so the probe measures “what a 120-epoch budget buys”. The 40-epoch flat tails are the schedule hitting zero. The probe is one seed, the worst of three.

In the end the connectome matters. That I know. The spectral MoE, _as I built it_, is a different story. The router never had anything to route. I do not reject spectral MoE by principle... just spectral MoE on this task, stimulus space, scale and budget. These variables. I built a bad task and I admit it. Maybe a part 2 will be due or someone else can continue my work.

*...and I'll still be here. Prolly still waiting on those damned SWAEV runs.*
