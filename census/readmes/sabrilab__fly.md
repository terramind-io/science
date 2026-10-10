# Le cerveau d'une mouche — dans son corps, et en marche

Le **cerveau entier d'une mouche du vinaigre**, en 3D dans le navigateur : 138 639 neurones
à leur vraie position anatomique, **logés dans le vrai corps de l'animal**, avec le modèle
qui les fait fonctionner et de quoi lancer ses propres expériences.

C'est le modèle repris par **Eon Systems** pour sa démo de « mouche incarnée » de mars 2026,
remis à plat, vérifié, et rendu explorable — limites comprises.

---

## Ce que c'est, en une minute

| Brique | Origine |
|---|---|
| **Le câblage** — 138 639 neurones, 15 091 983 connexions, 54,5 M de synapses | connectome **FlyWire** v783, Dorkenwald et al., *Nature* 2024 |
| **Le signe** — chaque neurone est excitateur ou inhibiteur | prédiction de neurotransmetteur, Eckstein et al. |
| **Les positions 3D et les types cellulaires** | annotations de Schlegel et al. 2024 |
| **La dynamique** — intègre-et-tire à fuite (LIF) | **Shiu et al.**, *Nature* 2024 |
| **Le corps** — 67 segments, 102 articulations, scan aux rayons X | **flybody**, Google DeepMind + HHMI Janelia |
| **L'implémentation de référence** | [eonsystemspbc/fly-brain](https://github.com/eonsystemspbc/fly-brain) |

Tous les neurones sont **identiques** : seul le câblage les différencie. Il n'y a
**qu'un seul paramètre libre** dans tout le système — 0,275 mV par synapse, calibré une
fois pour toutes. Tout le reste sort de l'anatomie.

**Ce que le modèle n'est pas** : pas de plasticité, pas d'apprentissage, pas de
neuromodulation, pas d'états internes. Aucun souvenir d'aucune mouche n'est dedans.
Ce n'est pas un « upload » : c'est un plan de câblage mis sous tension.

---

## Le bac à sable : la boucle complète

Un second mode où la mouche **vit**, dans une petite arène. La boucle est fermée pour de vrai :

```
monde → neurones sensoriels → cerveau LIF (Web Worker) → neurones descendants → corps → monde
```

Vous posez des choses autour d'elle et vous regardez son cerveau réagir :

| Commande | Ce qui entre dans le cerveau | Ce qui en ressort |
|---|---|---|
| **Lui donner du sucre** | GRN sucrés au contact | MN9 → la trompe se déploie (mesuré : 100 Hz) |
| **Y ajouter de l'amer** | GRN amers en plus | MN9 retombe à **0** — elle refuse |
| **Lancer une menace** | LC4, proportionnel à la **vitesse d'expansion angulaire** | Giant Fiber → décollage |
| **Laisser un prédateur** | des menaces qui la poursuivent et corrigent leur trajectoire | elle décolle régulièrement |
| **Lui poser une poussière** | organe de Johnston | aDN1 → toilettage |
| **Lâcher une odeur de moisi** | Or56a | DNa02 → virage |

L'arène fait **165 mm**, soit environ 55 longueurs de mouche.

Trois choses valent d'être signalées.

**La latéralisation, là où elle existe.** Les populations sensorielles sont séparées en moitié
gauche et moitié droite quand c'est possible, et stimulées séparément selon d'où vient le
stimulus : l'asymétrie motrice qui en résulte sort alors du connectome. C'est le cas de **LC4**
(54 neurones à gauche, 50 à droite) et des deux **P9**. Ce n'est en revanche **pas** le cas des
GRN sucrés ni de l'organe de Johnston : les listes de Shiu et al. sont entièrement d'un seul
côté, et le code ne prétend pas le contraire — il utilise alors la population entière.

**Ce qui doit être ajouté à la main, et pourquoi.** Le déséquilibre entre le P9 gauche et le P9
droit fait bien tourner le connectome — mais **d'un seul côté** : seul DNa02 gauche répond. Elle
ne saurait donc que spiraler. L'errance dans les deux sens est ajoutée au contrôleur, au même
titre que la traduction d'un taux de décharge en vitesse ou en angle de braquage.

**Le temps de réaction est mesuré, pas affiché en dur.** L'application chronomètre le délai
entre le début de l'expansion visuelle et la première décharge de la fibre géante. Valeurs
observées : **environ 110 ms**, dans la fourchette biologique de 20 à 200 ms.

**Le temps du monde avance au rythme du cerveau.** Une milliseconde simulée dans le connectome
= une milliseconde dans l'arène. Le cerveau tournant à ~0,5× le temps réel, tout se déroule au
ralenti — à peu près comme une mouche nous perçoit.

### Ce qu'elle voit

Une incrustation montre la scène depuis sa tête, en très grand angle, ramenée à la trame
hexagonale des ommatidies (~750 par œil) et corrigée pour sa réponse spectrale : elle voit
l'ultraviolet, le bleu et le vert, et elle est presque aveugle au rouge.

### Ce que la vision révèle — et pourquoi plus de la moitié du cerveau ne tourne pas

Le curseur **« brancher ses yeux »** injecte l'image de son propre œil dans ses cellules de
lamina (L1/L2), de façon rétinotopique. Le résultat est spectaculaire et négatif :

- son lobe optique s'allume, on passe de **1 000 à plus de 30 000 neurones actifs** ;
- et **rien** n'arrive à ses neurones descendants.

Vérifié hors navigateur, sur le **graphe complet** : stimuler les 3 288 cellules L1/L2 à 30 Hz
pendant 0,4 s active **0 des 12 246 neurones T4/T5** et **aucun** descendant. Ce n'est donc pas
un effet de l'élagage.

Deux raisons, toutes deux structurelles :

1. Chez la drosophile, les neurones visuels précoces — photorécepteurs, cellules monopolaires
   de la lamina, une grande partie de la médulla — **ne produisent pas de potentiels d'action**.
   Ils communiquent par potentiels gradués. Un modèle intègre-et-tire, qui ne transmet que des
   décharges, ne peut pas les faire fonctionner.
2. L1 est classé glutamatergique, donc **inhibiteur** dans ce modèle : son poids sortant total
   est de **−427 370**, contre **+764 346** pour L2. L'un éteint ce que l'autre allume.

**C'est exactement pour cette raison qu'Eon Systems a dû brancher un second modèle, entièrement
séparé — le réseau de Lappalainen et al. — rien que pour la vision.** L'application le montre
plutôt que de le masquer.

### La bulle au-dessus de sa tête

Elle ne dit pas ce que la mouche « pense » — elle n'a rien à penser. Elle dit **ce que fait son
cerveau**, avec les chiffres réels : « mes LC4 déchargent à 210 Hz », « MN9 est retombé à 0 Hz,
ce blocage n'est écrit nulle part ». Y compris quand il ne fait rien : *« Rien n'entre. Mon
cerveau n'a aucune activité spontanée : sans stimulus, il est parfaitement muet. »*

Chaque état porte aussi un émoji — 🚶 🍯 🤢 👁️ ⚡ 🪽 🧼 🪨 😴 — pour se lire d'un coup d'œil.
Ce ne sont pas des émotions : elle n'en a pas. C'est l'état de son cerveau, résumé.

C'est d'ailleurs pourquoi le bac à sable ajoute une **pulsion d'exploration** réglable : sans
cette impulsion écrite à la main, la mouche resterait immobile pour toujours.

### Le monde vit sans vous

Prédateur actif d'emblée, rafales de vent qui secouent ses antennes, nourriture qui apparaît,
22 cailloux qu'elle percute et contourne. Observée une minute sans la moindre intervention :
**5 décollages**, des repas, des virages, des chocs, et un temps de réaction mesuré à 96 ms.

---

## Ce que l'application permet

- **Une visite guidée en 9 étapes**, sans jargon, qui part de « voici une mouche » et
  finit par ce que le modèle ne sait pas faire.
- **Trois échelles** : la mouche entière, la tête, le cerveau. Le corps est rendu en
  silhouette sombre translucide — on voit à travers où le cerveau est logé.
- **Le corps bouge, piloté par les neurones** : MN9 déploie la trompe, aDN1 fait passer les
  pattes avant sur les antennes, P9 lance la marche en trépied, la fibre géante ouvre les
  ailes. Voir la mise en garde plus bas — c'est le point important.
- **Naviguer** dans le volume : les deux lobes optiques, le cerveau central, les entrées
  sensorielles, chacun à sa place.
- **Rejouer sept expériences** précalculées et regarder le signal se propager, neurone par
  neurone, milliseconde par milliseconde.
- **Lancer ses propres stimulations en direct** : le modèle LIF tourne dans le navigateur
  (Web Worker), à ~0,4–1× le temps réel selon la machine.
- **Cliquer un neurone** : type cellulaire, neurotransmetteur, côté, lien vers FlyWire Codex,
  et ses partenaires synaptiques les plus forts, tracés en 3D.
- **Éteindre une population** (silencing) et voir ce qui disparaît en aval.

---

## Les résultats, et pourquoi ils comptent

Simulations de 1 s, graphe complet, graine fixée. `Hz` = taux du neurone descendant nommé.

| Expérience | Spikes | Neurones actifs | Sortie motrice | Lecture |
|---|---:|---:|---|---|
| **Repos** (rien) | 0 | 0 | — | le modèle est **silencieux** sans entrée : pas d'activité spontanée |
| **Sucre** (23 GRN, 200 Hz) | 17 485 | 412 | MN9 95 / 67 Hz | la trompe se déploie → **manger** |
| **Amer** (42 GRN, 200 Hz) | 12 489 | 138 | — | voie aversive, MN9 muet |
| **Sucre + amer** | 21 630 | 319 | **MN9 à 0** | l'amer **supprime totalement** la réponse alimentaire |
| **LC4** (looming, 200 Hz) | 38 603 | 656 | Giant Fiber 139 / 130 Hz | objet qui fonce → **fuite** |
| **JO** (antenne, 300 Hz) | 83 572 | 890 | aDN1 53 Hz | vibration → **toilettage** |
| **Or56a** (géosmine, 250 Hz) | 459 173 | 8 393 | DNa02 47 Hz | odeur aversive → **virage** |

La ligne **sucre + amer** est le résultat phare de Shiu et al. : la suppression du
comportement alimentaire par l'amer **émerge du câblage seul**, elle n'a été programmée
nulle part.

À noter aussi : sur une stimulation sucrée, **412 neurones sur 138 639** s'activent. Le
modèle n'est jamais « allumé » en entier — on regarde une voie précise s'illuminer.

---

## Le corps, et la mise en garde qui va avec

Le corps vient de **flybody** (Google DeepMind + HHMI Janelia) : un modèle MuJoCo obtenu par
tomographie aux rayons X d'une vraie mouche, avec 67 segments et 102 articulations. Le même
modèle que celui utilisé par Eon.

Le recalage cerveau ↔ corps n'a pas été fait à l'œil. Il est déduit de repères anatomiques :

- **côté** — les neurones annotés `left` sont à x = −206 µm, ceux annotés `right` à +208 µm ;
- **avant** — les neurones Or56a, dont les corps cellulaires sont dans l'antenne, sont à
  z = −149 µm, l'extrême du volume.

D'où le repère du cerveau (+x = droite, +y = dorsal, +z = postérieur), celui du corps
(+x = avant, +y = gauche, +z = dorsal), et la transformation qui va de l'un à l'autre.

**Ce qu'il faut comprendre du mouvement.** Le cerveau simulé ne calcule pas les mouvements.
Il produit un taux de décharge sur une poignée de neurones descendants, et chaque taux
déclenche ici une **animation écrite à la main**. C'est exactement ce que fait la démo
d'Eon : 7 neurones descendants branchés sur des contrôleurs pré-entraînés, là où une vraie
mouche en possède plus de 1 300. La raison est structurelle : FlyWire ne couvre que le
cerveau, pas la chaîne nerveuse ventrale où siègent les motoneurones des pattes. Le modèle
ne *peut pas* produire la marche.

L'application le dit à l'écran plutôt que de le cacher — c'est le plus instructif.

---

## Validation

Le simulateur de ce dépôt (`pipeline/lif.py`, numpy) est une **réimplémentation
indépendante**, écrite en suivant pas à pas la référence PyTorch d'Eon
(`code/run_pytorch.py`), elle-même validée chez eux contre Brian2 CPU.

Contrôle sur l'expérience de référence d'Eon — *Sugar GRNs (200 Hz)*, 21 neurones, 1 s, 1 essai :

| | spikes | neurones actifs |
|---|---:|---:|
| **Référence Eon** (Brian2 CPU, médiane de 5 tours) | 16 708 | 388 |
| **Ce dépôt** (graines 0 / 1 / 2) | 16 508 / 17 582 / 16 954 | 400 / 402 / 413 |

L'écart reste dans la dispersion d'essai à essai du modèle lui-même (l'entrée est un
processus de Poisson). Reproduire : `python pipeline/validate.py`.

---

## Sur téléphone

L'application s'adapte : les panneaux deviennent des feuilles coulissantes avec une barre
d'onglets (Agir · Cerveau · Sa vue · Visite), la barre haute se réduit, les zones sûres de
l'écran sont respectées, et les cibles tactiles font au moins 44 px.

Côté rendu, trois choses changent automatiquement sur un appareil tactile : la densité de
pixels est plafonnée, le décor est allégé (320 brins d'herbe au lieu de 900, 14 cailloux au
lieu de 22), le corps n'est plus rendu sur ses deux faces, et la vue de son œil n'est calculée
qu'une image sur deux. Le survol est désactivé — le pointage parcourt les 138 639 points, c'est
trop cher au doigt.

Surtout, la finesse **s'ajuste toute seule** : le temps d'image réel est mesuré en continu et la
densité de pixels monte ou descend en conséquence. Aucune supposition sur la puissance de
l'appareil.

Le champ de vision est calculé à l'horizontale plutôt qu'à la verticale, sinon un écran tenu
debout écrase la scène ; et la caméra recule proportionnellement en portrait.

---

## Reproduire les données

```bash
pip install -r pipeline/requirements.txt
./pipeline/fetch_data.sh          # annotations FlyWire + dépôt d'Eon
python pipeline/build_atlas.py    # -> web/data/positions.bin, attrs.bin, atlas.json…
python pipeline/run_experiments.py # -> web/data/sims/*.bin
python pipeline/build_edges.py    # -> web/data/graph.bin
python pipeline/build_body.py     # -> web/data/body.bin  (corps, 4 Mo)
python pipeline/validate.py       # contrôle contre les chiffres publiés d'Eon
```

Servir l'application : `python -m http.server 8099 -d web`, puis <http://localhost:8099>.

---

## Créer sa propre expérience

Tout passe par `pipeline/neuron_sets.py` et `pipeline/run_experiments.py`.

```python
from lif import Connectome, simulate

steps, neurons = simulate(
    conn,                                   # le connectome
    [(sucre_idx, 200.0), (amer_idx, 150.0)],# groupes stimulés (indices, Hz)
    duration_s=1.0,
    silenced=interneurone_idx,              # extinction, pour tester la nécessité
    seed=0,
)
```

Les cinq protocoles qui marchent bien avec ce modèle :

1. **Dose-réponse** — balayer la fréquence de stimulation, tracer la réponse d'un descendant.
2. **Compétition** — deux entrées antagonistes, mesurer la suppression.
3. **Lésion** — répéter en éteignant un interneurone candidat : la sortie disparaît-elle ?
4. **Criblage** — un type cellulaire à la fois, classer par effet.
5. **Latéralisation** — stimuler un seul côté, vérifier la préférence controlatérale.

Pièges à connaître :

- **Les IDs dépendent de la version du connectome** : seulement 106 220 IDs sont communs
  entre v630 et v783. Un ID venu d'ailleurs peut ne pas exister ici.
- **Stimuler n'est pas physiologique** : l'entrée de Poisson force la décharge et annule le
  réfractaire. C'est de l'optogénétique, pas un stimulus naturel.
- **Toujours plusieurs essais** (`n_run` ≥ 20) : l'entrée est stochastique.
- Nouveaux IDs de neurones : [FlyWire Codex](https://codex.flywire.ai), recherche par type
  cellulaire, neurotransmetteur ou hémisphère.

---

## Structure

```
pipeline/            reconstruction des données (Python)
  lif.py               le simulateur LIF — le cœur, 190 lignes
  neuron_sets.py       populations sensorielles et neurones descendants nommés
  build_atlas.py       annotations + connectome -> binaires 3D
  run_experiments.py   lance les expériences -> trains de spikes
  build_edges.py       graphe élagué pour le navigateur + mesure du coût de l'élagage
  build_body.py        modèle MuJoCo du corps -> maillages compacts + arbre articulé
  validate.py          contrôle contre les chiffres publiés d'Eon
web/                 l'application (statique, sans étape de build)
  js/scene.js          rendu Three.js du nuage de points
  js/fly-body.js       corps articulé, coque sombre translucide, recalage anatomique
  js/motor.js          neurones descendants -> articulations (animations assumées)
  js/world.js          le bac à sable : arène, objets, sens, physique du vol
  js/sandbox.js        boucle monde <-> cerveau, mesure du temps de réaction, narration
  js/pov.js            ce qu'elle voit, à la résolution des ommatidies
  js/sim-worker.js     le même modèle LIF, en JavaScript, dans un Web Worker
  js/app.js            interface, lecture temporelle, sélection
  data/                binaires générés (24 Mo)
```

Le graphe expédié au navigateur est élagué à `|synapses| ≥ 5` : 2 700 513 connexions,
62,7 % du poids synaptique, 16,8 Mo. Coût mesuré sur l'expérience sucre : **91 % des
neurones actifs et 85 % des spikes conservés**. Les expériences précalculées, elles,
utilisent le **graphe complet**.

---

## Sources

- Connectome : [FlyWire](https://flywire.ai) · Dorkenwald et al., *Nature* 2024
- Modèle LIF : [Shiu et al., *Nature* 2024](https://www.nature.com/articles/s41586-024-07763-9)
- Annotations : [Schlegel et al. 2024](https://github.com/flyconnectome/flywire_annotations)
- Implémentation de référence : [eonsystemspbc/fly-brain](https://github.com/eonsystemspbc/fly-brain)
- Corps : [flybody](https://github.com/eonsystemspbc/flybody), Google DeepMind + HHMI Janelia
- Démo « mouche incarnée » : [Eon Systems](https://eon.systems/updates/embodied-brain-emulation) ·
  la lecture critique : [Carboncopies](https://carboncopies.org/Blog/Posts/FruitFlyNotUploaded/Post/)

Le code de Shiu et al. repris dans `pipeline/` est sous licence MIT en amont ;
flybody est sous licence Apache 2.0 ; Three.js (`web/vendor/`) est sous licence MIT.
