# Fly Brain Lab

Forschungs-Sandbox: Das vollständige Konnektom einer Fruchtfliege läuft als Spiking-Netz,
steuert einen physikalisch simulierten Fliegenkörper in MuJoCo, und ein LLM fährt als
automatisierter Experimentator Versuchsreihen: Hypothese, Eingriff, Simulation, Auswertung.

> **Ein Konnektom ist ein statischer Schaltplan, kein lebendes Gehirn.** Hier laufen echte
> Verdrahtung (MaleCNS v1.0 bzw. FlyWire v783), ein LIF-Modell (Shiu et al. 2024),
> **handgebaute** Sinnes-Encoder, eine **handgesetzte** Ausleseschicht und **abstrahierte**
> Bewegungsprimitive zusammen. Ergebnisse sind Hypothesen über den Schaltplan plus diese
> Annahmen, keine Aussagen über echte Fliegen. Jede Annahme steht in
> [`docs/assumptions.md`](docs/assumptions.md).

## Stand und wichtigste Ergebnisse (MaleCNS v1.0, 166.700 Neuronen)

Alle Zahlen: Mittelwert über Seeds, jeweils mit eigener Shuffle-Kontrolle. Vollständige Tabellen,
Tests und Run-IDs in [`docs/results.md`](docs/results.md).

| Frage | Ergebnis | Lesart |
|---|---|---|
| Läuft das Gehirn korrekt? (Shiu-Befund, FlyWire) | Zucker-GRNs → MN9: **78,7 Hz** (Engine, n = 30) vs. **77,5 Hz** (Brian2-Referenz, n = 6), Shuffle 0 Hz; Raten aller 418 antwortenden Neuronen r = 0,999 | Engine reproduziert das Referenzmodell |
| Looming-Flucht (M3) | Abheben **12/12** intakt, **0/12** Shuffle, **0/12** Giant Fiber stillgelegt, **3/12** LPLC2+LC4 stillgelegt | Flucht hängt im Modell an der echten Verdrahtung LPLC2/LC4 → DNp01 |
| Spinne (M4) | Überleben **12/12** intakt, **0/12** Shuffle, **0/12** GF-Lesion, **1/12** LPLC2+LC4-Lesion | dito; die Spinne ist leicht zu entkommen (nur Bodenjäger) |
| Sprungrichtung | handgesetzt **108°** Fehler, trainiert (Ridge auf alle DNs) **48°** (p = 0,005); offline CV 54° intakt vs. 69° Shuffle vs. 90° Zufall | Richtungsinformation steckt in den DNs, braucht aber eine **trainierte** Ausleseschicht |
| Zero-g mit Luft (M6) | Roll-Regelkreis VS → DNp20/DNb06 aktiv und korrigierend (Korrelation 0,55 vs. 0 im Shuffle), Drehrate aber nicht signifikant kleiner (3,98 vs. 4,38 rad/s, p = 0,7 Holm); Drift 1 g: 107 cm, 0 g: 205 cm | Verdrahtung liefert korrigierende Kommandos, die Stabilisierung macht aber die Physik (Flapping-Dämpfung) |
| Lichtwahl (M7) | 5/12 wählen einen Arm, davon 1/5 den hellen | keine Phototaxis im Modell |
| Futtersuche (M7) | 0/8 erreichen die Duftquelle | keine Duft-Navigation; Duft aktiviert ~75 % der Kenyon-Zellen (fehlendes Sparse Coding, B-8) |

Ehrliche Kurzfassung: Der Giant-Fiber-Reflex ist ein robuster, verdrahtungsabhängiger Effekt.
Komplexere Verhalten (Phototaxis, Duft-Navigation, aktive Flugstabilisierung) entstehen aus
Konnektom + LIF + diesen Encodern **nicht** von selbst. Das ist ein Befund, kein Bug. Der
Abhebezeitpunkt (8° Reizgröße, ~260 ms vor Kollision) wird von den Encoder-Schwellen bestimmt
und ist nicht an Physiologie angepasst.


## Architektur

```
Umwelt (MuJoCo, CGS-Einheiten: Luft, Gravitation, Spinne, Licht, Duft, Hindernisse)
   │  Zustand: Pose, Geschwindigkeit, Objekte, Lichtquellen, Duftfeld
   ▼
Sinnes-Encoder  (engineered)              sensory/encoders.py
   Looming → LPLC2/LC4 · optischer Fluss → HS/VS · Licht → R1–R6
   Duft → ORN DM1/DM2/DM4/VM2 · Schwerkraft/Wind → Johnston-Organ JO-C/E
   ▼  Poisson-Raten auf identifizierte Neuronen
Gehirn: Konnektom als LIF-Netz (dt 0,1 ms)  brain/lif.py  (Brian2-äquivalent, numba)
   ▼  Spikes der Descending Neurons
Ausleseschicht (handgesetzt, optional trainiert)  motor/readout.py
   DNp01 → Abheben · DNp02/11 → Sprungrichtung · DNp09/MDN → vor/zurück
   DNa02/01 → Lenken · DNg02 → Flugschub/Rollen
   ▼  MotorCommand
Bewegungsprimitive → Kraft/Moment am Thorax   body/fly.py  (simple | flybody)
   ▲
   │ Experiment-API: Lesion, Rewiring, Shuffle, Sinnes-Ablation, Gravitation, Seeds
LLM-Experimentator (Claude, nur über Tools)  agent/
   list_neuron_groups · describe_scenarios · run_experiment · get_metrics · compare · submit_report
```

Physik und Gehirn laufen beide mit Δt = 0,1 ms. Sinnesraten und Motorkommando werden jede
Millisekunde neu berechnet.

### Was ist echt, was ist gebaut?

| Teil | Herkunft |
|---|---|
| Neuronen, Synapsenzahlen, Neurotransmitter-Vorzeichen | **Konnektom** (MaleCNS v1.0 / FlyWire v783) |
| Neuronendynamik (LIF, Konstanten) | Shiu et al. 2024; `w_syn` pro Datensatz kalibriert |
| Welche Neuronen welchen Reiz bekommen (Looming, Fluss, Licht, Duft, JO) | **engineered** (Annahmen A-8 bis A-13) |
| DN → Motorkommando | **handgesetzt** (A-14); optional trainierte Sprungrichtung |
| Muskeln, Gelenke, Flügelaerodynamik | **abstrahiert** als Bewegungsprimitive (A-15 bis A-17) |
| Körpergeometrie, Masse, Luftwiderstand | MuJoCo-Fluidmodell; Körper `simple` oder flybody (starr) |

## Schnellstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[llm,dev]"

flylab download                 # MaleCNS v1.0 (~570 MB) + FlyWire v783 (~110 MB)
flylab download --flybody       # optional: anatomischer flybody-Körper
flylab sanity                   # Neuronen-/Synapsenzahl gegen die Release-Zahlen prüfen
pytest -q                        # Tests; ohne Daten laufen alle außer den Release-Zählchecks (Toy-Konnektom)
```

### Experimente

```bash
# Looming-Flucht, 12 Seeds, automatisch mit Shuffle-Kontrolle
flylab run looming --trials 12 --seed 1 --label intact --plot

# Lesion: Giant Fiber stilllegen
flylab run looming --trials 12 --seed 1 --lesion giant_fiber --label "GF lesion"

# Spinne mit stillgelegten Looming-Detektoren
flylab run spider --trials 12 --lesion looming_vpn

# Schwerelosigkeit (Luft bleibt), Johnston-Organ abgeschaltet
flylab run zerog --gravity 0 --ablate jo

# Rewiring: LPLC2 → Giant Fiber halbieren
flylab run looming --rewiring '[{op: scale, pre: lplc2, post: giant_fiber, factor: 0.5}]'

# beliebige Config überschreiben
flylab run looming --set scenario_cfg.speed=50 --set body.kind=flybody

flylab compare <run_a> <run_b>          # Welch-t / Mann-Whitney / Fisher, Bootstrap-CI, Holm
flylab groups DNa                        # Neuronengruppen und Zelltypen suchen
flylab runs                              # alle Runs
```

Jeder Run landet in `runs/<run_id>/` mit `config.json` (vollständige Config, Seeds, Git-Commit,
Paketversionen), `trials.csv` (berechnete Metriken pro Trial), `summary.json` (Mittelwert, SD,
SEM, Median, Bootstrap-95%-KI, n), `events.json` und Trajektorien der ersten Trials.

### LLM-Experimentator

```bash
export ANTHROPIC_API_KEY=...
flylab agent "Hängt die Überlebenszeit gegen die Spinne an LC4 oder an LPLC2?" --budget 100
```

Das LLM (Standard: `claude-opus-5-5`, adaptive thinking, effort `high`) bekommt nur Werkzeuge:

| Tool | Zweck |
|---|---|
| `list_neuron_groups(query)` | Gruppen und Zelltypen suchen |
| `describe_scenarios()` | Szenarien, Parameter, Metrik-Definitionen |
| `run_experiment(scenario, label, n_trials, seed, gravity, lesion, rewiring, ablate_senses, scenario_overrides)` | Simulation, **immer** mit Shuffle-Kontrolle; Trial-Budget wird erzwungen |
| `get_metrics(run_id)` | berechnete Zahlen pro Trial und aggregiert |
| `compare(run_a, run_b)` | Statistik |
| `submit_report(...)` | Bericht; wird **maschinell geprüft** |

Regeln, die der Code erzwingt (nicht nur der Prompt): Jede Zahl in einem Berichtstext muss in
einem vorherigen Tool-Ergebnis vorkommen (auf die geschriebene Genauigkeit gerundet). Jede
Kernaussage zitiert `run_id + Metrik + Statistik`, und der Wert wird gegen `summary.json`
geprüft. Ohne Kontroll-Run wird der Bericht abgelehnt. Ein fester Block mit Modellgrenzen wird
immer angehängt. Abgelehnte Berichte gehen mit der Fehlerliste zurück an das LLM.

Ohne API-Key: `flylab study giant-fiber` fährt einen festen Versuchsplan über dieselben Tools
und dieselbe Berichtsprüfung.

## Szenarien und Metriken

| Szenario | Aufbau | Metriken (berechnet in `env/scenarios.py`) |
|---|---|---|
| `looming` | Dunkle Kugel nähert sich der stehenden Fliege (r/v = 20 ms), zufälliger Azimut | takeoff, time_before_collision_ms, theta_at_takeoff_deg, escape_dir_error_deg |
| `spider` | Geskriptete Spinne: schleicht mit 6 cm/s, sprintet mit 30 cm/s ab 3 cm | survived, survival_time_s, escape_latency_ms, escape_dir_error_deg, min_distance_cm |
| `foraging` | Duftquelle 4 cm entfernt (Gaußsche Wolke), ein Hindernis, tonischer Laufantrieb | reached, time_to_goal_s, path_efficiency, final_distance_cm, landed |
| `lightchoice` | T-Labyrinth, helle Seite zufällig | chose, chose_bright, chose_left, choice_time_s |
| `zerog` | Freiflug, Gravitation einstellbar, Luft unverändert, Startdrehung 4 rad/s | drift_cm, mean_tilt_deg, upright_fraction, mean_angspeed_rad_s, control_effort, tumbled |

Alle Szenarien loggen zusätzlich `gf_spikes`, `n_active_neurons` und `mean_rate_active_hz`.

## Validierung

| Prüfung | Ergebnis | Datei |
|---|---|---|
| Neuronen-/Synapsenzahl MaleCNS v1.0 | 166.700 Neuronen (Release: ~166.700), 124,03 Mio. Synapsen (Release: ~125 Mio.) | `flylab sanity` |
| Neuronen-/Synapsenzahl FlyWire v783 | 138.639 / 54.492.922 (exakt wie Shiu-Referenz) | `flylab sanity` |
| Engine ≡ Brian2 | identische Spike-Zeiten bei identischem Input | `tests/test_brian2_equivalence.py` |
| Shiu-Befund Zucker-GRN → MN9 (FlyWire) | siehe unten | `docs/validation/m1_results.json`, `m1_validation.png` |

Details und Abbildung: [`docs/results.md`](docs/results.md). Beim Vergleich mit Brian2 fiel eine
Abweichung von ~25 % auf: Brian2 verwirft synaptischen Input an refraktäre Neuronen. Die Engine
macht das jetzt genauso (Test sichert es ab).

## Projektstruktur

```
src/flybrainlab/
  connectome/   loaders.py (MaleCNS, FlyWire) · model.py · groups.py · interventions.py
  brain/        lif.py (Engine) · brian2_ref.py (Referenz)
  sensory/      encoders.py
  motor/        readout.py
  body/         fly.py · assets/simple_fly.xml
  env/          world.py · scenarios.py
  experiments/  runner.py · store.py · stats.py
  agent/        tools.py · llm.py · report.py · scripted.py
  viz/          plots.py
  loop.py · cli.py · download.py · provenance.py
configs/        default.yaml · scenarios/*.yaml · groups/<dataset>.yaml · readouts/
scripts/        validate_m1.py · calibrate_wsyn.py · reference_experiments.py · fit_escape_readout.py
docs/           assumptions.md · data_and_licenses.md · reference_review.md · results.md · validation/
runs/           Run-Ausgaben (nicht versioniert; Beispiele unter runs/examples/)
notebooks/      quickstart.ipynb
tests/
```

## Meilensteine

| | Meilenstein | Stand |
|---|---|---|
| M0 | Setup, Daten laden, Zahlen prüfen | ✅ beide Datensätze, Sanity-Checks gegen Release |
| M1 | Gehirn läuft, bekannter Befund | ✅ Zucker → MN9 reproduziert, Brian2-äquivalent; MaleCNS kalibriert |
| M2 | Körper in MuJoCo, Gravitation und Luft als Parameter | ✅ `simple` + flybody (starr), Bewegungsprimitive |
| M3 | Schleife Sinne → Gehirn → DN → Körper, Looming-Flucht | ✅ analytischer Looming-Encoder statt FlyVis (siehe Roadmap) |
| M4 | Spinne, Metriken, Shuffle | ✅ geskriptete Spinne |
| M5 | LLM-Loop mit Tools und Berichten | ✅ Tool-Schicht, Berichtsprüfung, skriptbarer Offline-Experimentator; Live-Lauf braucht API-Key |
| M6 | Zero-g, Sinnesorgan-Ablationen | ✅ Gravitation, JO-Ablation, HS/VS-Lesion, Böen; Duftdiffusion ohne Konvektion offen |
| M7 | RL-Spinne, Futtersuche, Lichtwahl, Visualisierung | ◐ Futtersuche, Lichtwahl, Plots, trainierte Sprungrichtung; RL-Spinne offen |

### Roadmap (offen)

1. **FlyVis-Adapter:** Kamerabilder → FlyVis → T4/T5 → Projektion auf LPLC2/LC4/LC-Typen statt des analytischen Encoders.
2. **Retinotopie** aus den MaleCNS-Spalten-Pins (`malecns-v1.0-optic-lobe-column-pins`) statt zufälliger Rezeptivfelder.
3. **Gelenksteuerung:** VNC-Motoneuronen (in MaleCNS vorhanden) → flybody-Gelenke statt Primitiven.
4. **RL-Spinne** (Policy gegen die Konnektom-Fliege) und Duftdiffusion in Schwerelosigkeit.
5. Physiologische Kalibrierung der Looming-Schwellen (Abhebewinkel vs. r/v-Daten).

## Grenzen (Kurzfassung)

- Keine Plastizität, Neuromodulation, Gap Junctions, Spontanaktivität oder zelltypspezifische
  Membranparameter. `w_syn` ist frei (FlyWire 0,275 mV, MaleCNS 0,15 mV kalibriert).
- Hemmung von stillen Neuronen wirkt nicht (siehe Photorezeptoren, A-11). Die
  Pilzkörper-Aktivität ist bei Duftreizen viel zu dicht (B-8).
- Sinnes-Encoder und Ausleseschicht sind gebaut. Shuffle-Kontrollen zeigen, welcher Teil eines
  Verhaltens an der Verdrahtung hängt. Was im Shuffle bleibt, kommt aus Encoder, Readout oder Physik.
- Gelenke und Flügel werden nicht vom Konnektom gesteuert. MuJoCos Fluidmodell ist quasi-stationär.

## Lizenzen und Zitate

Code-Lizenz: noch nicht festgelegt (vor Veröffentlichung eine `LICENSE` hinzufügen). Daten haben eigene Lizenzen (FlyWire CC BY-NC 4.0, MaleCNS CC BY 4.0,
flybody Apache-2.0). Details und Zitierpflichten: [`docs/data_and_licenses.md`](docs/data_and_licenses.md).
