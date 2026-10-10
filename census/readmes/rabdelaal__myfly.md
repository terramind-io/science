# FlyChess — démo live : https://rabdelaal.github.io/myfly/

Élevez une mouche Tamagotchi dont le cerveau est une simulation du connectome de la drosophile mâle — et défiez-la aux échecs.

**Deux régimes :** la démo en ligne tourne **100 % dans le navigateur**
(cerveau synthétique 5 000 neurones en Web Worker, readout non entraîné —
même encodeur 788 features, parité bit-exacte avec le backend, testée dans
`frontend/`). Le **vrai MaleCNS** (183 490 neurones, readout, salons
multijoueurs, théâtre live, lésions) demande le backend local (ci-dessous) —
le frontend bascule tout seul, ou forcez avec `?api=http://localhost:8000`.

## Mode Tamagotchi

La mouche a quatre stats (**satiété, humeur, énergie, propreté**) qui décroissent avec le temps,
même serveur éteint (décroissance hors-ligne plafonnée à 48 h, état dans `backend/tamagotchi_state.json`).

- Chaque action de soin (nourrir, caresser, laver, dormir) est envoyée au **connectome** comme stimulus
  sensoriel : l'intensité de la réponse motrice donne la réaction de la mouche, visible dans la vue WebGL.
- **Les échecs sont son mini-jeu** : chaque coup la stimule (+humeur) mais la fatigue (-énergie, -satiété).
- Une mouche mal en point **joue mal** : du bruit proportionnel à son état est ajouté à l'évaluation
  de ses coups.
- Épuisée, elle s'endort toute seule (et refuse alors de jouer). Réveillez-la depuis l'onglet Mouche.

## 🎬 Cerveau en direct

Bouton **« 🎬 Cerveau en direct »** du panneau cerveau : plein écran, caméra en orbite automatique
autour des vraies positions du connectome, **1500 synapses les plus fortes dessinées en lignes**
(excitrices chaudes, inhibitrices froides) qui **s'allument quand leurs deux neurones tirent**.

- `backend/live.py` : un **cerveau persistant** (état neural conservé frame après frame — il « vit »)
  simule en continu avec un bruit sensoriel spontané dont l'amplitude suit l'humeur de la mouche ;
  endormie, son cerveau tombe presque au silence.
- Chaque action de soin ou coup d'échecs est **injectée comme stimulus visible** : on voit la bouffée
  se propager des sensoriels vers les moteurs, avec légende à l'écran.
- Flux WebSocket `/ws/live` à 30 fps (ralenti ×6,5 pour l'esthétique), HUD de fréquences par
  population (Hz) et octopamine en direct.
- La simulation ne tourne **que si quelqu'un regarde** : démarrage à l'arrivée du premier spectateur,
  arrêt à la dernière déconnexion (zéro CPU sinon).
- **Depuis la page principale** : bouton **⚡ Live** (flux continu dans le panneau cerveau),
  **🔊 Son** (clics Geiger des spikes), légende des populations par couleur, et paramètres d'URL :
  `?tab=chess` (ouvrir sur les échecs), `?theater=1` (ouvrir le théâtre directement).

## Architecture

- **Backend** : FastAPI + PyTorch, simulation LIF du connectome MaleCNS v1.0, module `tamagotchi.py`.
- **Frontend** : Vanilla JS + Three.js + WebGL custom (onglet Mouche / onglet Échecs).

## Sous le capot (partie neuronale)

- **Simulation batchée** : les ~20 coups candidats sont simulés en parallèle — les états neuronaux
  sont des tenseurs (n_neurones, B) partageant la même matrice creuse (`brain.py:run`).
- **Format sparse CSR** : ~16× plus rapide que COO pour `sparse.mm` sur CPU.
- **Octopamine** : le bien-être du Tamagotchi asservit un gain global d'excitabilité du cerveau
  (`brain.set_neuromod`), comme l'hormone d'excitation réelle des insectes. Une mouche mal en point
  joue aussi mal (bruit sur les scores).
- **WebSocket `/ws`** : les spikes du connectome sont streamés au fur et à mesure de la simulation
  (60 frames pendant que la mouche réfléchit), visibles en direct dans la vue WebGL.
- **Readout entraîné par règle locale à trois facteurs** (activité × erreur × récompense Stockfish),
  sans rétropropagation à travers la simulation (`train_readout.py`).

Coups de la mouche mesurés sur CPU (connectome synthétique 5 000 neurones) : ~1,9 s par coup
contre ~80 s avant optimisation (≈ ×40).

## Benchmark SpearVM / champions (spur-math, spear-kernels)

`backend/bench_spear.py` compare la baseline fly aux kernels « champions » AVX2 de
[SpearVM](https://pypi.org/project/spur-math/) (polynômes certifiés gelu/erf/tanh, matmul tuilé)
et aux [spear-kernels](https://www.npmjs.com/package/spear-kernels) (kernels closed-form découverts
par régression symbolique — dont `rc_circuit`, pertinent pour une membrane LIF).

Résultats mesurés sur cette machine (4 cœurs, i7 8e gen, numpy/OpenBLAS) — **pas d'intégration,
et c'est volontaire** :

| Opération | Baseline | Spear | Gain |
|---|---|---|---|
| Projection d'encodage (20×788→1500, f32) | 0,95 ms | 4,79 ms | ×0,20 |
| Projection échelle MaleCNS (→50 000) | 35,3 ms | 171 ms | ×0,21 |
| FFN fusionnée matmul+GELU (→4096) | 5,53 ms | 8,07 ms | ×0,69 |
| tanh 4M éléments | 15,3 ms | 25,7 ms | ×0,60 |
| LIF dense 5000² (torch.mm) | 16,3 ms | 17,7 ms | ×0,92 |
| **LIF sparse CSR (cœur du cerveau)** | **1,03 ms** | — (aucun kernel sparse) | — |

Deux conclusions : (1) les speedups ×15-34 annoncés sont mesurés **contre libm scalaire**, pas contre
numpy/OpenBLAS déjà vectorisé AVX2 ; (2) la voie f32 de `matmul_nt` est numériquement loseuse
(écart ~0,4 vs référence — la voie f64 est exacte mais plus lente). Le gain « champion » est
asymétrique et ne touche pas notre goulot (le sparse). Re-tester sur une machine sans OpenBLAS
ou avec AVX-512 si support ajouté.

## HTC-Core (produit scalaire ternaire 1.58-bit, sans multiplicateur)

Reproduction du papier de R. Abdel-Aal (même auteur que spear) : `tools/htc-core/htc_core.c`
(v2.0, compile avec `gcc -O3 -march=native`), `tools/htc-core/htc_v21.c` (v2.1 AVX2) et
`htc_flysize.c` (test à l'échelle du connectome) ; expérience sur le connectome :
`backend/bench_htc_fly.py`.

**v2.0 vérifié** : 1 000 000 / 1 000 000 essais bit-exact, défaut `a = −128` reproduit (Δ = 256).
Mais sur CPU : ×7,6 plus lent que le dot AVX2, bitmasks ×7 plus gourmands que notre sparse à
0,45 % de densité, et la quantification ternaire des poids (loi gamma) détruit la dynamique
(r = +0,10 / +0,51).

**v2.1 vérifié et validé** (`htc_v21.c`) : l'offset +128 bijectif éradique le défaut −128 —
**0 échec sur 500 000 vecteurs de [-128, 127]** (v2.0 : 73 607 échecs sur le même jeu), et le
kernel GEMV AVX2 pré-décompacté devient **plus rapide que la référence int8 auto-vectorisée** :

| Kernel (cette machine, gcc) | ns / 64 MACs | GMACs/s | Mémoire poids |
|---|---|---|---|
| Référence int8 auto-vecto | 5,41 | 11,8 | 8 bits/poids |
| HTC v2.0 scalaire (offset 127) | 105,0 | 0,6 | 16 bits/w |
| **HTC v2.1 pré-décompacté** | **5,07** | **12,6** | 16 bits/w |
| HTC v2.1 bitplane online | 6,14 | 10,4 | **2 bits/w** |

**Mais toujours pas pour la mouche** (`htc_flysize.c`, connectome 5056² paddé, batch 20) :
le GEMV dense bitplane prend 27,6 ms contre 4,5 ms pour notre torch sparse CSR (**×6,1**), et
6,4 Mo de bitplanes contre 0,91 Mo de sparse — à 0,45 % de densité, payer 25,6M MACs là où il y
a 113k synapses reste perdant, même avec un kernel 20× plus rapide que le v2.0. HTC v2.1 est le
bon outil pour des poids denses déjà ternaires (BitNet), pas pour du câblage biologique creux.

## Kernel LIF natif vérifié (la discipline HTC appliquée à notre noyau)

`backend/native/lif_kernel.c` — le pas LIF réécrit en C, avec le même protocole de vérification
que HTC-Core : **1 000 000 / 1 000 000 réseaux aléatoires bit-exact** contre une référence naïve
(`lif_verify.exe`), puis **300/300** contre la référence torch (`native_lif.verify_vs_torch`).
Leçon d'implémentation : il a fallu `-ffp-contract=off` — la contraction FMA de gcc changeait
l'arrondi entre kernel et référence, et le harness l'a attrapé.

- Intégré comme backend CPU par défaut de `brain.py` (repli torch automatique, GPU non supporté) ;
  écart dynamique mesuré sur un run complet : **0,0**.
- `bench_native.py` : pas LIF 1,06 ms, run 300 pas × batch 20 = 334 ms (torch : 391 ms).

## Expériences `rc_circuit` et int8 (`bench_rc_int8.py`)

- **Champion `rc_circuit` (intégration exacte du circuit RC) : résultat négatif.** Même à dt=1 ms,
  Euler et exact divergent (r = 0,68 — sensibilité chaotique du réseau récurrent), et à pas élargi
  (5/10 ms, gain recalibré) le classement des coups candidats est détruit (ρ ≈ 0, meilleur coup
  différent). Pas de réduction gratuite du pas de temps : la mouche reste en Euler 1 ms.
- **Encodage int8 symétrique : positif.** Clampé à [−127, +127] (jamais −128, le défaut formel
  de HTC-Core), erreur de quantification 0,0027, activité motrice préservée (r = 0,70). L'encodeur
  est prêt pour un futur accélérateur entier.
- **Bug corrigé au passage** : l'encodeur du moteur d'échecs n'avait pas de gain de stimulus —
  les courants restaient sub-seuil, aucun neurone ne spike pendant l'évaluation des coups et les
  scores étaient dus au bruit d'humeur. Correctif : `encoding.STIM_GAIN = 20` (calibré), vérifié
  (59/60 frames spikées, 20/20 scores distincts).

## Démarrage rapide (données synthétiques)

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (dans un autre terminal)
cd frontend
python -m http.server 3000
# Ouvrir http://localhost:3000
```

Le backend démarre avec un connectome synthétique de 5 000 neurones. Cliquez sur une pièce blanche
pour la sélectionner (les coups légaux sont surlignés), puis cliquez la case de destination.
Clic-glisser pour orbiter autour du plateau, molette pour zoomer.

## Utiliser le vrai connectome MaleCNS ✅ (branché)

Le backend charge automatiquement `data/malecns.npz` s'il existe — c'est le cas ici :
**183 490 neurones, 25 963 816 synapses** (MaleCNS v1.0, Janelia, CC-BY), avec les vraies
positions des soma, les neurotransmetteurs prédits (signe synaptique) et les superclasses
(15 950 sensoriels, 925 moteurs, 1 316 descendants).

```bash
# 1. Télécharger les données officielles (feather, ~1,15 Go)
cd data
curl -LO https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/body-annotations-male-cns-v1.0-minconf-0.5.feather
curl -LO https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/body-neurotransmitters-male-cns-v1.0.feather
curl -LO https://storage.googleapis.com/flyem-male-cns/v1.0/connectome-data/flat-connectome/connectome-weights-male-cns-v1.0-minconf-0.5.feather

# 2. Construire le .npz (lecture IPC memory-mappée, ~5 min)
cd ../scripts && python prepare_data.py

# 3. Relancer le backend : le vrai connectome se charge automatiquement
cd ../backend && uvicorn main:app --port 8000
```

Adaptations à l'échelle réelle (automatiques) :
- **Normalisation des poids** : dans MaleCNS, `weight` = nombre de synapses agrégées (médiane 2,
  max 2 591). Normalisée à |w| moyen = 1/20 (calibré empiriquement : réseau spontané vivant
  ~9 Hz sensoriel sans avalanche récurrente, degré moyen 141).
- **Échecs** : 8 candidats × 60 pas batchés → ~35 s par coup (183k neurones, 0 re-simulation : les frames du gagnant viennent du batch). Passer à 100 pas recrute mieux les moteurs (mesuré) mais change le vainqueur aussi souvent que le hasard des horizons — le readout devra être réentraîné à l'horizon choisi.
- **Cerveau en direct** : pas LIF mesuré au démarrage (73 ms) → 1 pas/frame à 10 fps.
- Le kernel C natif se désactive seul au-delà de 20M synapses (torch multi-thread gagne).

## Réplication du réflexe d'alimentation de Shiu et al. (Nature 2024) ✅

`backend/exp_feeding_reflex.py` — notre simulation reproduit le réflexe testé dans
[Shiu et al.](https://www.nature.com/articles/s41586-024-07763-9) : stimuler les GRN du goût
sucré (60 tpGRN pharyngées de nos annotations) à 100 Hz fait décharger les **vrais motoneurones
MN9** (2 neurones, `cb_motor`) à travers le connectome réel, avec leur modèle exact
(α-synapses τ = 5 ms, délai 1,8 ms, réfractaire 2,2 ms, V ∈ [−52, −45] mV, zéro décharge de base).

**Calibration du paramètre unique Wsyn** (critère Shiu : 80 % de la réponse motrice maximale) :

- Notre MaleCNS : **0,164 mV/synapse** — seuil net entre 0,10 et 0,175 mV
  (0 Hz → 229 Hz : l'all-or-none de la décision d'alimentation), saturation à ~244 Hz ;
- Shiu et al. (FlyWire, cerveau seulement) : **0,275 mV/synapse** ;
- Accord à ×0,6 sur le paramètre unique, entre deux connectomes et deux implémentations
  indépendantes. Écarts résiduels : périmètre (CNS complet vs cerveau), choix du set GRN,
  τ_m supposé, affectation des signes NT.

Courbe dose-réponse : `data/feeding_dose_response.npy`.

**Le Tamagotchi au complet tourne maintenant sur ce modèle** (`synapse_model="alpha"`, défaut ;
revenir à l'ancien : `FLY_SYNAPSE_MODEL=current`) :
- **α-synapses 3 équations** (décroissance τ = 5 ms, incrément w au spike, délai 1,8 ms),
  réfractaire absolu 2,2 ms, V ∈ [−52, −45] mV, poids = nb de synapses brutes × signe × Wsyn ;
- les stimuli externes sont convertis en **Poisson de spikes** (codage en fréquence) ;
- « 🍯 Nourrir » déclenche le **vrai réflexe** : drive Poisson 100 Hz sur les GRN sucrées →
  propagation → MN9 (visible en direct dans le théâtre) ;
- le bruit ambiant est recalibré pour ce régime (σ = 0,3 mV : le réseau amplifie ×37 tout
  drive de base, le repos reste paisible) ;
- vérifié en direct : 22 284 spikes en 3 s au repos (50,8 Hz sensoriels, moteurs 1,1 Hz),
  bouffée de 48 000 spikes au nourrissage.

## Lésions virtuelles : quelle partie du cerveau fait quoi ? ✅

`backend/exp_lesions.py` — silencie un groupe de neurones annotés (spikes forcés à zéro)
et mesure le déficit sur trois assays : le **réflexe d'alimentation** (assay validé ci-dessus),
l'**activité d'ambiance** (Poisson 2 Hz sur les 15 110 sensoriels) et la **discrimination
sensorimotrice** (4 sous-ensembles de 500 sensoriels stimulés → corrélation des 4 patterns
moteurs). Les 9 conditions sont simulées **en parallèle** (une colonne de batch chacune,
masque de lésion par colonne) — 29 min au lieu de ~4 h. Résultats (`data/lesion_results.json`,
Wsyn = 0,164, fenêtres 600–800 ms) :

| Condition lésée | n | Réflexe MN9 (Hz) | Déficit réflexe | Ambiance (Hz) |
|---|---|---|---|---|
| **intact (témoin)** | 0 | **201,2** | — | 145,8 |
| corps du champignon (MB) | 4 064 | 201,2 | 0 % | 139,1 |
| complexe central (CX) | 2 950 | 200,6 | 0,3 % | 140,5 |
| dimorphes mâle/femelle | 2 368 | 200,6 | 0,3 % | 143,3 |
| fruitless/doublesex | 5 012 | 200,0 | 0,6 % | 140,2 |
| **neurones descendants** | 1 314 | **138,1** | **31,4 %** | 143,9 |
| lobes optiques | 89 394 | 200,6 | 0,3 % | **56,8** |
| témoin aléatoire ~4k | 4 000 | 200,6 | 0,3 % | 140,6 |
| témoin aléatoire ~89k | 89 000 | 29,4 | 85,4 % | 46,8 |

Trois enseignements, tous cohérents avec la littérature :

1. **Le réflexe gustatif est un arc direct** : MB, CX, hotspots dimorphes et fru/dsx ne
   changent rien (≤ 0,6 %, niveau du témoin aléatoire 4k) — le goût sucré va des GRN aux
   MN9 sans passer par l'apprentissage (MB) ni l'intégration (CX). En revanche lésion des
   **1 314 neurones descendants = −31 %** : dans notre régime LIF, ce goulot anatomique
   porte une bonne partie de l'amplification récurrente du réflexe.
2. **Les lobes optiques = la moitié de la vitalité d'ambiance** (145,8 → 56,8 Hz) mais zéro
   rôle dans le goût — spécialisation modale nette.
3. **Redondance + diagnostic rank-1 confirmé indépendamment du readout** : lésion aléatoire
   de 89k neurones ⇒ −85 % (le réseau résiste) ; et la spécificité des patterns moteurs est
   **nulle même à cerveau intact** (les 4 sous-ensembles sensoriels produisent le même
   pattern moteur, corr ≈ 1) — le problème rank-1 du readout est bien une propriété du
   régime LIF global, pas d'un sous-circuit lésionnable.

Usage : `python exp_lesions.py` (29 min) ou `--quick` (smoke test ~9 min).

### ⚗️ Labo — les lésions dans le produit (onglet Labo de l'UI)

L'expérience ci-dessus est branchée sur le produit : un onglet **⚗️ Labo** permet de lésionner
une population en un clic et de la voir **grisée dans le cerveau WebGL** (panneau + théâtre,
qui continuent de vivre sans elle). La lésion s'applique au vrai cerveau de la mouche
(Tamagotchi + échecs + live) : `FlyBrain.set_lesion()` force zéro spike aux neurones ciblés
dans les trois backends (torch alpha/current, kernel C natif → repli torch).

- `backend/lab.py` : les 7 populations (MB, CX, dimorphes, fru/dsx, descendants, lobes
  optiques, témoin aléatoire ~4k) construites depuis le npz + feather ; déficits « prédits »
  servis depuis `data/lesion_results.json` ;
- `GET/POST /api/lab[/lesion|/clear|/test-reflex]` : statut, lésion, guérison, mesure ;
- **🧪 Tester le réflexe** : drive 100 Hz des GRN sucrées sur le cerveau réel, mesure MN9 sur
  600 ms (~1 min 30). Référence intacte mesurée une fois au démarrage (thread de fond,
  insensible à une lésion appliquée entre-temps).

Validation end-to-end (API réelle) : cerveau lésé « descendants » → **155,8 Hz, déficit
28,1 %** (l'expérience batchée prédisait 31,4 %) ; après « 🩹 Guérir » → **216,7 Hz,
déficit 0 %**, la référence est retrouvée exactement.

## Readout entraîné sur le vrai connectome — état et limites (honnêtes)

`train_readout.py` a été lancé sur le vrai connectome (Stockfish 19 comme récompense, règle
locale à trois facteurs, 200 positions en ~10 min avec `--steps 50`). Deux problèmes profonds
ont dû être résolus puis documentés :

1. **Divergence** : à pleine puissance synaptique, certaines positions déclenchent une bouffée
   récurrente qui fait exploser un readout linéaire (10³⁰ puis NaN). Correctif : décodage par
   **vecteur populationnel** (l'activité est normalisée en norme L2 — l'information porte sur la
   direction du pattern) + bornage des poids. Entraînement désormais stable (RMS ~0,4).
2. **Non-généralisation** : validé sur 25 positions fraîches, le readout entraîné ne prédit pas
   mieux Stockfish qu'un readout aléatoire (ρ ≈ 0,14 vs 0,19, n=25 ± 0,2). Cause racine mesurée :
   sous notre régime LIF simplifié, la réponse du connectome réel est quasi **rank-1** (un niveau
   d'activité global ; les moteurs ne recrutent pas, les descendants faiblement) — il n'y a pas
   encore d'information position-quality linéairement décodable.

Ce que ça implique : la mouche joue avec son vrai câblage biologique et un readout qui ne corrompt
rien, mais **elle ne joue pas « bien »** — ses coups reflètent la dynamique du réseau, pas une
évaluation échiquéenne. Pour y arriver, il faudrait : des synapses à dynamique réaliste (alpha,
dépression), une stimulation ciblant les vraies voies sensorielles (lemnissales/olfactives),
beaucoup plus de données d'entraînement, et idéalement un simulateur à noyaux dédiés (chAMP).
Le pipeline d'entraînement et de validation est prêt — c'est un problème de modélisation, plus
d'ingénierie de gamme de simulation.

## Avec Docker

```bash
docker-compose up --build
# Frontend : http://localhost:3000
# Backend : http://localhost:8000
```

## Mise à jour 16/09/2026 — backend natif α réparé

- Le CSC natif ignorait `weight_scale` (×15,8 manquant) et la variante int16 zérotait 99 % des synapses (poids normalisés ~0,05) : le « 0,7 ms/pas » venait d'un cerveau mort. Après fix : **1,7 ms/pas sur réseau vivant** (torch 56 ms), réflexe Shiu 130 Hz en natif, parité moteur torch ≈ OK (7,0 vs 7,9).
- Bench déterministe run-to-run (tirages Poisson figés, Stockfish 1 thread, val-set seedé) ; garde-fou anti-train-long (120 positions par défaut, `FLY_ALLOW_LONG_TRAIN=1` pour forcer) ; `--resume-from` pour les fine-tunes courts (120 pos ≈ 1 min en natif batch 1).
- Référence rho (looped `.best`, 3×15 pos, steps 100) : −0,10/−0,03/−0,11, stable — le readout reste à ré-entraîner, mais sur une métrique qui ne bouge plus au hasard.

## Honnêteté scientifique

- Le **wiring** (connexions, types, positions) est biologique (MaleCNS v1.0, CC-BY).
- Les **équations LIF** sont une simplification (pas de dynamique de canaux, pas de plasticité à court terme).
- L'**encodage** du plateau est arbitraire (projection aléatoire de features).
- Le **readout** est entraîné supervisément sur Stockfish.

Aucune information sur les échecs n'est stockée dans le connectome. Seuls les readouts (linéaire + looped) sont entraînés.

## Ressources

- MaleCNS : https://male-cns.janelia.org/
- connectome_interpreter : https://github.com/YijieYin/connectome_interpreter
- fly-escape (projet similaire) : https://github.com/dzhng/fly-escape
- doomfly (projet similaire) : https://github.com/davidakin/doomfly
