# flywire-sim — faire tourner le cerveau d'une mouche (FlyWire v783)

Objectif final : un jeu / simulation 3D (PC & Mac) où une mouche est pilotée par une simulation de
son vrai cerveau. **Étape 1 (ce dépôt)** : installer et faire tourner le cerveau seul, à partir
uniquement des données officielles publiées par les chercheurs du projet FlyWire.

## C'est quoi FlyWire ?

FlyWire (Princeton, Seung & Murthy labs + consortium international) est le premier **connectome
complet** du cerveau d'un animal adulte complexe : une drosophile femelle (*Drosophila
melanogaster*, jeu de données EM « FAFB »).

- 139 255 neurones reconstruits et vérifiés (proofread) manuellement (~33 années-personnes).
- ~50 millions de synapses chimiques détectées automatiquement, dont ~34 M dans les 2,7 M de
  connexions neurone→neurone qui comptent ≥ 5 synapses (seuil recommandé par les auteurs).
- Pour chaque neurone, un **neurotransmetteur dominant prédit** depuis les images EM
  (acétylcholine ≈ excitateur ; GABA, glutamate ≈ inhibiteurs ; dopamine, sérotonine, octopamine
  = modulateurs).
- Des annotations hiérarchiques : flux (afférent / intrinsèque / efférent), super-classe
  (sensoriel, central, optique, descendant, moteur…), classe, type cellulaire, côté, nerf.

Publications de référence (Nature, oct. 2024) :
- Dorkenwald *et al.*, « Neuronal wiring diagram of an adult brain » — le connectome (v783).
- Schlegel *et al.*, « Whole-brain annotation and multi-connectome cell typing… » — les annotations.
- Eckstein, Bates *et al.* (Cell 2024) — prédiction des neurotransmetteurs.

Important : le connectome ne contient **pas** de « poids » appris. Il contient la structure
(qui est connecté à qui, avec combien de synapses, et quel neurotransmetteur). C'est nous qui
choisissons un modèle de neurone et qui en déduisons des poids : `poids = signe(NT) × nb_synapses`.

## Données utilisées (sources officielles uniquement)

| Fichier | Source | Contenu |
|---|---|---|
| `codex783/neurons.csv.gz` | Codex (Princeton), bucket public `gs://flywire-data/codex/data/fafb/783/` | 139 255 neurones, NT dominant + probabilités |
| `codex783/connections.csv.gz` | idem | connexions pre→post par neuropile, ≥ 5 synapses, `syn_count`, NT |
| `codex783/classification.csv.gz` | idem (annotations Schlegel *et al.*) | flow, super_class, class, sub_class, side, nerve |
| `codex783/labels.csv.gz` | idem | labels communautaires (ex. « Motor neuron 9; MN9 » par P. Shiu, Scott lab) |
| `codex783/names, consolidated_cell_types, coordinates, …` | idem | noms, types cellulaires, positions |
| `Supplemental_file1_neuron_annotations.tsv` | dépôt `flyconnectome/flywire_annotations` (Schlegel *et al.*) | annotations systématiques, `top_nt` par neurone |
| `proofread_connections_783.feather` (optionnel, 850 Mo) | Zenodo 10676866, FlyWire Consortium | toutes les connexions proofread **sans seuil**, moyennes NT par paire |

Aucun code de simulation tiers n'est réutilisé : le réseau et le simulateur sont écrits ici
(numpy / scipy).

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
scripts/download_data.sh                     # ~80 Mo (ajouter WITH_ZENODO_CONNECTIONS=1 pour le feather)
PYTHONPATH=. .venv/bin/python scripts/build_network.py          # matrice sparse signée 139k × 139k (5 s)
PYTHONPATH=. .venv/bin/python scripts/run_sugar_experiment.py   # 1 s de cerveau en ~5 s
PYTHONPATH=. .venv/bin/python scripts/run_controls.py
```

## Le modèle

`flywire_sim/network.py` : matrice `W[post, pre] = signe(pre) × syn_count`, format CSC, 2,7 M
d'entrées. Le signe vient du NT dominant du neurone présynaptique (GABA / glutamate → −1, sinon +1 ;
les ~20 k neurones sans NT dans Codex sont complétés par le `top_nt` de Schlegel *et al.*).

`flywire_sim/lif.py` : neurones **leaky integrate-and-fire** (le modèle biologiquement plausible le
plus simple), vectorisés sur tout le cerveau :

```
dv/dt = (g − (v − V_rest)) / τ_m        V_rest = V_reset = −52 mV, V_seuil = −45 mV, τ_m = 20 ms
dg/dt = −g / τ_syn                      τ_syn = 5 ms, délai 1,8 ms, réfractaire 2,2 ms
spike de j  →  g_i += W[i, j] × w_syn    w_syn = 0,275 mV (seul paramètre libre)
```

Ces constantes sont celles de l'électrophysiologie de la drosophile (publiées, réutilisées telles
quelles). Pas d'activité spontanée : le cerveau est silencieux tant qu'on ne stimule pas d'entrée
sensorielle. Un stimulus = forcer des neurones à émettre des spikes selon un processus de Poisson
(équivalent d'une activation optogénétique).

Coût : 139 255 neurones × 10 000 pas (dt = 0,1 ms) ≈ **4–5 s de calcul par seconde simulée** sur
un CPU (pas de GPU nécessaire).

## Premier résultat : le circuit « sucre → extension du proboscis »

On active à 100 Hz les 23 neurones gustatifs « sucre » du labellum gauche (labels officiels) et on
regarde ce qui s'allume dans le cerveau, notamment **MN9**, le motoneurone qui soulève le rostre
(extension du proboscis = la mouche « sort sa langue » pour manger) :

- 460 neurones actifs sur 139 255, presque tous dans le ganglion sous-œsophagien (GNG = centre
  gustatif/moteur de la tête) ;
- MN9 gauche ≈ 157 Hz, MN9 droit ≈ 218 Hz, et les autres motoneurones d'ingestion / proboscis
  (MN10, CB0700, MNx01…) sont activés ;
- contrôles : aucun stimulus → 0 spike ; 23 neurones centraux au hasard ou GRN « amer » → MN9 muet.

Autrement dit, la structure brute du connectome + un modèle de neurone minimal suffit à reproduire
une transformation sensorimotrice complète : goût sucré → commande motrice d'alimentation.

![raster](results/sugar_left_100Hz_seed0.png)

Limites à garder en tête : rates absolus non calibrés, pas de modulation (dopamine…), pas de
synapses électriques, pas d'états internes (faim), le côté contra > ipsi n'est pas attendu
biologiquement (à creuser : conventions gauche/droite de l'imagerie FAFB, qui est en miroir).

## Étape 2 : le corps (v0, `flywire_sim/body/`)

Conception détaillée dans `docs/conception_corps.md`. En résumé :

- **Système nerveux** : réseau **hybride** (`flywire_sim/hybrid.py`) = un cerveau + le ganglion ventral du
  **MANC v1.2.1** (mâle, Janelia, export officiel Codex, `flywire_sim/manc.py`), reliés par des neurones
  descendants / ascendants appariés par type cellulaire et côté ; aucune connexion inventée, chaque synapse
  vient d'un des deux exports. Deux cerveaux au choix (`--brain`) :
  - `fafb` (**défaut recommandé**, `flywire_sim/fafb.py`) : **FAFB v783** (femelle, cerveau complet, export
    officiel Codex), 161 350 neurones, 1 570 fusions (`docs/calibration.md` § 8). Les types de DN portent la
    nomenclature commune ; les AN et afférents ascendants du FAFB ont leurs propres noms, appariés au MANC
    via les annotations du BANC qui portent les deux nomenclatures (`bridge_type`), jamais par fonction.
  - `banc` : **BANC v888** (femelle, `flywire_sim/banc.py`) sans ses neurones de la moelle, 156 735 neurones,
    2 949 fusions (§ 7) ; son export sous-estime l'inhibition reçue par les DN, d'où une boucle
    moelle → cerveau → moelle qui a motivé le passage au FAFB.
  Dans les deux cas : deux animaux différents, ce n'est pas le connectome d'une seule mouche. Les motoneurones
  des pattes du MANC sont annotés muscle par muscle ; les neurones sensoriels du MANC (et, pour le FAFB, ceux
  de la tête) reçoivent organe et fonction par transfert des annotations BANC (même type cellulaire).
- **Corps MuJoCo** (`body/model.py`) : MJCF généré par nous (arbre cinématique, 82 DoF, muscles,
  adhésion tarsale, capteurs, collisions), **sans ailes** ; formes, masses et positions d'articulations
  issues d'un **scan micro-CT** d'une femelle adulte (maillages NeuroMechFly, Apache-2.0,
  `body/meshes/`). Unités mm/g/s, pas de 0,1 ms.
- **Muscles** (`body/muscles.py`) : 330 des 396 motoneurones de patte du MANC sont reliés chacun à
  l'actionneur portant le nom de leur muscle (66 n'ont pas de muscle nommé dans l'export) ; chaque spike
  produit une secousse (twitch).
- **Sens** (`body/senses.py`) : angles, vitesses, charge et contacts des pattes → 3 650 neurones
  sensoriels de patte du MANC (hair plates, organes chordotonaux claw/hook/club, campaniformes,
  soies tactiles, soies gustatives) en spikes Poisson ; les sens de la tête sont ceux du cerveau choisi
  (`docs/capteurs.md` ; pour le FAFB, § 8.2 de `docs/calibration.md` liste les canaux vides).
- **Boucle fermée** (`body/sim.py`) : capteurs → spikes → un pas de LIF → spikes MN → muscles →
  un pas de MuJoCo.

```bash
PYTHONPATH=. .venv/bin/python scripts/body_stand_test.py        # debout sous gravité + images
PYTHONPATH=. .venv/bin/python scripts/body_muscle_test.py --video   # tripode scripté (sans cerveau)
PYTHONPATH=. .venv/bin/python scripts/body_brain_loop.py --brain fafb --duration 200 --video  # cerveau FAFB + moelle MANC + corps
PYTHONPATH=. .venv/bin/python scripts/hybrid_regimes.py --brain fafb   # réseau seul : repos, DNg100, coupures
PYTHONPATH=. .venv/bin/pytest tests
```

État : elle tient debout ; les muscles scriptés la font avancer ; tous les afférents annotés du BANC
sont branchés au corps (`docs/capteurs.md`). Régime `banc.CALIBRATED_V2` (`docs/calibration.md` § 5 :
paramètres de Shiu 2024, signes GABA/glutamate/histamine vérifiés, afférents clampés, synapses
eLN → PN électriques atténuées, dépression ORN → PN) : avec tous les capteurs actifs le cerveau reste
stable (fond ~0 Hz hors lobe antennaire, cellules de Kenyon muettes au repos) et les neurones descendants
« marche » recrutaient les motoneurones de patte faiblement (1–3 Hz) avec la moelle BANC, sous-complète
(`docs/calibration.md` § 6). Avec la moelle MANC, DNg100 → MN de patte atteint la référence (11 Hz,
19–24 % des MN), mais sous le cerveau BANC une boucle moelle → ascendants → cerveau → descendants
s'auto-entretient (§ 7 : déficit d'inhibition sur les DN dans l'export BANC). Avec le cerveau **FAFB v783**
(§ 8) cette boucle disparaît (DN 2 Hz au lieu de 11, MN d'aile 15 Hz au lieu de 108 avec le corps) et
repos / DNg100 / « marche » redeviennent distinguables sur les MN de patte (2,7 / 3,7 / 10,7 Hz) — mais les
six pattes restent en appui (aucune alternance, déplacement 0,1 mm) : **elle ne marche pas encore**
(`scripts/body_brain_loop.py`, `scripts/banc_walk_analysis.py`). L'enquête du chantier moteur (§ 9) montre que cette « référence » de 11 Hz était un état auto-entretenu de
la moelle (400 interneurones saturés à > 100 Hz, activité qui monte après l'arrêt de DNg100) : avec les **volumes
officiels** des neurones (`flywire_sim/size.py`, loi 1/volume, Kazama & Wilson 2008) l'attracteur disparaît en
moelle isolée mais revient dès que les afférents de patte tirent, car le LIF à courant n'a aucun mécanisme
limitant la fréquence — c'est le prochain verrou, avant les classes de MN et la dynamique musculaire.
