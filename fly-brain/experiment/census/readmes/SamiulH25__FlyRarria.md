# FlyRarria

A living Terraria companion driven by real fruit-fly brain circuits. Cosmetic pet, emergent personality, bond levels, evolving look.

## Status

v0.1.0: pet follows/teleports, world sampling -> `SensoryFrame` -> LIF brain -> `MotorDecoder` steering, bond persistence, `/fly` readout.

The brain is the whole male CNS: all 176,422 neurons and 25,862,574 connections (125,024,863 synapses) of male-cns:v1.0, from `Circuits/male-cns.connectome.gz`. It loads in the background when the mote is summoned (~0.7 s, ~190 MB; the HUD reads `loading` meanwhile) and steps on up to 12 threads: ~7 ms per 50 ms brain tick on average, ~30 ms at worst on an 8-core Ryzen 7 5700X. `/fly stats` shows the step time and how close to real time the brain runs. Without that file the pet runs the extracted circuits (`Circuits/*.json`, 7,805 neurons), and without those it falls back to documented `[reflex]` following. No fake brain activity is ever displayed.

Model: Shiu et al. 2024 LIF, plus three things the whole CNS needs (the extracted circuits leave out the loops they fix). Dopamine, octopamine and serotonin have no fast synaptic effect. Kenyon cell -> Kenyon cell synapses inhibit (mAChR-B lateral inhibition, Manoim et al. 2022). Short-term depression (U 0.05, 300 ms recovery; Poisson-driven sensory neurons exempt) at gain 0.8. Without them one taste or smell latched every Kenyon cell and the antennal lobe at ~60k spikes a step for good. One excitatory antennal-lobe loop (lLN1_bc, lLN2T/X) still holds ~5k spikes a step after chemosensory input; the behaviours below read through it.

Verified headlessly on the whole CNS (the C# brain driven with scripted frames, plus `tools/bench.py --connectome` 5/5): loom -> ESCAPE (DNp01 ~180 Hz), sugar -> FEED (MN9 26-41 Hz; 27/30 ticks when hungry), a full mote mostly refuses (MN9 6-17 Hz), bitter suppresses feeding, touch/rain/owner damage/strong wind -> GROOM, chase left/right -> FOLLOW with matching yaw, and all of it still works during the antennal-lobe latch. Hunger (bond `fed`, decays 1.5/min while the pet is out) scales sugar-neuron gain (0.2 full, 1.0 at the default, up to 1.5 hungry), so the circuit makes the call. Food *seeking* isn't decoded: food odor moves no readout. STARTLE and MDN/DNp09 forward-backward movement are handled in `Steer` but don't fire (any loom spikes DNp01 first), and SONG never fires.

The engine only steps neurons that could spike and splits them across threads in blocks of the synaptic delay; spikes are identical to stepping every neuron on one thread (checked spike for spike against a dense reference at 1-16 threads).

## Layout

- `Brain/` — engine-independent LIF core: `Connectome` (graph + sign rules), `ConnectomeFile`, `CircuitLoader`, `LifNetwork` (`Params.WholeCns` / `Params.Shiu2024`), `SensoryFrame`, `SensoryEncoders`, `MotorDecoder`, `PopulationIndex`, `ScopeLayout`
- `Circuits/` — `male-cns.connectome.gz`, the whole male CNS the game runs (via `tools/extract_connectome.py`); extracted circuit JSON, the fallback (via `tools/extract_circuits.py`, neuPrint male-cns:v1.0); `scope_shape.json`, the neuroscope outline
- `Content/Pets/` — `MoteProjectile` / `MoteBuff` / `MoteItem`
- `Content/Bond/` — bond levels + hunger persistence
- `Content/Debug/` — `/fly stats|senses|scope`; the neuroscope overlay (`N` or `/fly scope`) draws the real brain and VNC silhouette (male-cns neuropil meshes, brain seen from behind) with every neuron where it sits in the fly (soma, or synapse centroid for sensory neurons), lights the ones spiking, and traces their strongest synapses (orange excitatory, blue inhibitory), with live input drives and decoder readout rates labelled
- `tools/` — circuit and whole-connectome extractors, neuroscope silhouette baker (`scope_shape.py`) + headless bench

## Build

Requires tModLoader (Terraria 1.4.5) + .NET 8 SDK (`mise use dotnet@8`). Copy/clone (or symlink) into the tModLoader `ModSources/` folder and build via Workshop -> Develop Mods. `dotnet build` alone cannot resolve `tModLoader.targets` — that import only exists under a tModLoader install.

## Circuits

```
python3 -m venv .venv && .venv/bin/pip install requests numpy scipy
.venv/bin/python tools/extract_circuits.py --out Circuits/   # anonymous neuPrint, ~30 s
.venv/bin/python tools/scope_shape.py                         # neuroscope brain outline, ~10 s
.venv/bin/python tools/bench.py --circuits Circuits/         # all five must PASS
```

Whole connectome (`Circuits/male-cns.connectome.gz`, 51.8 MB):

```
.venv/bin/pip install pyarrow
.venv/bin/python tools/extract_connectome.py   # 1 GB Janelia export + neuPrint, cached in .cache/; ~2 min cached, longer first time
.venv/bin/python tools/bench.py --connectome Circuits/male-cns.connectome.gz   # all five must PASS; ~40 s, ~1.6 GB RAM
```

It writes nothing unless its totals equal neuPrint's own count and every neuron and connection in the circuit JSON matches. The format is documented in the script's docstring.

Circuits are seed types plus bridge interneurons (seed -> x -> seed; `feed` uses two hops, since its one-hop sugar -> MN9 bridges are mostly inhibitory). See the docstring in `tools/extract_circuits.py` for seeds, the side encoding, and neuPrint API quirks.

## Sources

- Berg et al., male CNS connectome v1.0 (Janelia/Google/Cambridge)
- Shiu et al. 2024, Drosophila computational brain model (LIF params)
- Manoim et al. 2022, lateral axonic inhibition between Kenyon cells via mAChR-B
- blendi-remade/fly-brain-minecraft (architecture reference: sensors/encoders/decoder split, validation protocol)

## Duo runbook

1. Extract circuits — done (see Circuits above). Seed names follow male-cns:v1.0:
   `P1` isn't a type there (pC1 covers it); wind/touch/bristle drives use
   `JO-C*`/`JO-E*`, `JO-FV`, `BM_InOm` — best-guess equivalents, worth a check.
2. `tools/bench.py` — 5/5 PASS on both the circuits (gain 0.65) and the whole
   CNS (`--connectome`, gain 0.8 with depression). Keep `tools/bench.py`,
   `Brain/LifNetwork.cs` and the sign rules in `Brain/Connectome.cs` in lockstep
   (both report rates from every spike in the window).
3. Build the mod in tModLoader — `Circuits/*` ship as loose .tmod files (tML's
   compiler ignores `<EmbeddedResource>`; `FlyRarria.Load` caches them).
   In-game: `/fly stats` should read `[brain] 176,422 neurons`.
4. Playtest: offer food (sugar->FEED), sprint at it (loom->ESCAPE), rain
   (groom), night at bond 4 (head perch). Tune `MotorDecoder.Thresholds`
   (`FeedMn9Hz` is 35: on the whole CNS sugar gives MN9 ~26-41Hz, hungry ~40Hz,
   full ~6-17Hz) and `LifNetwork.Params.WholeCns`.
5. Open: make SONG reachable; the antennal-lobe latch after odors.
