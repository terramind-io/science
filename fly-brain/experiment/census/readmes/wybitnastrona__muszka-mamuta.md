# MUSZKA-MAMUTA

<p align="center">
  <img src="assets/preview.svg" alt="MUSZKA-MAMUTA: Drosophila jedząca twaróg waniliowy, atlas som MaleCNS" width="760">
</p>

Symulacja w przeglądarce: *Drosophila melanogaster* z mózgiem LIF na grafie
MaleCNS v1.0 je **kreatynę** (puszka KFD, miarka, bieżnia lab) w
nieskończoność. Scena kuchenna, HUD z boku, przełącznik widoków. To
**zmodyfikowana** wersja szablonu
[fly-connectome-template](https://github.com/cobanov/fly-connectome-template)
autorstwa [Merta Cobanova](https://github.com/cobanov).

**Wystarczy jeden** `npm run dev`. Nie uruchamiaj dodatkowych serwerów Vite.

---

## Co jest zmierzone, a co autorskie

Z szuflady **Metody** w HUD:

**ZMIERZONE (MaleCNS v1.0, CC BY 4.0):** graf połączeń i wagi; 271
gustatorycznych neuronów ssawki (`class == "gustatory"` AND `subclass` ∈
{labellar bristle, taste peg, pharyngeal sensillum}); MN9 bodyId **10331** i
**16949**; znaki synaps z predykcji neuroprzekaźników; role napędu ze
pomiaru (`docs/DATA-PIPELINE.md`). MaleCNS **nie ma** adnotacji receptorów
słodki/gorzki (zero trafień Gr64f / Gr5a / Gr66a).

**AUTORSKIE:** parametry LIF (cytowania w `src/brain/params.ts`), model głodu
i hemolimfy, chemia pokarmu (`CREATINE_KFD`, aa 0,85, słodycz 0,05; twaróg
waniliowy zostaje fixture'em testowym), skala
renderu 6× (15 mm na ekranie), rig proceduralny, miarka, bieżnia, chód dwunożny,
każdy klip ruchu, lot, czyszczenie, sen, gag-i,
mapowanie MN9 Hz → czas pompy. Konektom steruje **tylko bramką żerowania**
(kanał gustatoryczny → MN9). `ActivityFrame` jest jednokierunkowy: ciało
i proszek go czytają, nigdy do niego nie zapisują. MaleCNS **nie ma** adnotacji
kreatyny / Ir76b (0 trafień). Puszka KFD: wysokość 142 mm zmierzona, Ø z
aspectu packshotu, wrap z artworku na czarnym plastiku, kopiec proszku 3D
(1/3 H). Miarka, bieżnia i chód dwunożny są autorskie.

**OGRANICZENIA:** charakter pobudzający vs hamujący jest wnioskowany, nie
zmierzony. Cały kanał gustatoryczny napędza MN9 słabiej niż pojedyncze seedy
(hamowanie boczne / normalizacja) — to zmierzona własność obwodu.

---

## Wynik negatywny: `path_sign`

`path_sign` (znak najsilniejszej ścieżki ≤ 4 hopów od seeda do MN9) **został
przetestowany i odrzucony**. Nie jest etykietą słodki/gorzki i nie jest efektem
netto. `validate_per.ts` (2026-09-16, ziarno 1, 100 Hz / 500 ms):

| Bodziec | MN9 |
| --- | ---: |
| wszystkie `gust_labellar` (223) | **32 Hz** |
| podzbiór `path_sign = −1` (107) | **52 Hz** |

Podzbiór −1 napędzał MN9 **mocniej**, nie słabiej. Pole zostaje w metadanych
jako `path_sign_deprecated`. Model go nie używa.

## Nieaddytywność (po kalibracji tonicznej 0,25 Hz)

Toniczne 2 Hz na 271 seedach dawało MN9 **29 Hz** (żerowanie, nie spoczynek).
Kalibracja: `BACKGROUND_RATE_HZ = 0.25` → spoczynek MN9 **3,75 Hz** (okno
2000 ms).

| Pomiar | Wartość |
| --- | ---: |
| cały kanał labellar/peg (223), 100 Hz / 500 ms | MN9 **28 Hz**, wzrost **+24,25 Hz** |
| najsilniejszy pojedynczy seed `Δ` | **+137,25 Hz** |
| `gust_drive` (91) | MN9 **87 Hz** (wzrost +83,25 Hz) |
| `gust_suppress` (90) | MN9 **22 Hz** (wzrost +18,25 Hz) |
| luka drive − suppress | **65 Hz** |

Wzrost całego kanału jest **daleko poniżej** maksimum pojedynczego seeda —
zgodne z hamowaniem bocznym / normalizacją w wyciętym obwodzie.

---

## Uruchomienie

Node.js **22.18+**:

```sh
npm ci
npm run dev
```

Otwórz URL Vite (127.0.0.1). **Jeden** proces deweloperski wystarczy.
LIF startuje sam po wczytaniu atlasu. HUD jest po polsku; przycisk **EN**
przełącza język. `?reel=1` zostawia slogan + raster. `?record=1` nagrywa
pętlę 1080×1920 VP9/WebM (kamera Reel, slogan skomponowany w klatce).

```sh
npm test
npm run check:assets
npm run validate:circuit
npm run soak
npm run build
npm run preview
```

Statyczny hosting: `dist/`. `vite` ma `base: './'`, więc działa pod
podścieżką. Na Cloudflare Pages: build `npm run build`, katalog `dist`.
`graph.bin` jest skompresowany (MMG1, ~13 MB), poniżej limitu 25 MB/plik.

Nagranie WebM → MP4: `scripts/webm2mp4.sh wejście.webm` (ffmpeg, H.264,
yuv420p, 30 fps, `+faststart`).

---

## Potok zasobów

1. `scripts/data-prep/inspect_malecns.py` — seedy z adnotacji (nie z nazw genów).
2. `scripts/data-prep/extract_feeding_circuit.py` — 20k feeding-gate carve, CSR.
   `write_csr` (nieskompresowany, audyt w `data/derived/`) oraz
   `write_csr_compressed` (publiczny `graph.bin`).
3. `npm run compress:graph` — float16 + delty varint, jeśli przebudowujesz bin.
4. `npm run calibrate:background` — toniczny 0,25 Hz.
5. `npm run measure:drive` — `deltaMn9Hz` i tercyle ról.
6. `npm run validate:circuit` — musi drukować **PASS**.
7. Tekstury kuchni: `scripts/textures/build_textures.py --in assets/photos --out assets/textures`
   (wycięcie opakowania, tile twarogu, normal/roughness, `textures.json`).
8. Atlas som i Flybody: `public/data/brain-atlas/`, `public/data/flybody/`
   (`npm run check:assets`).

Szczegóły: `docs/DATA-PIPELINE.md`, `docs/METABOLISM.md`, `docs/BODY-MODEL.md`,
`docs/QA.md`.

---

## Atrybucja i licencje

Zbudowane na [fly-connectome-template](https://github.com/cobanov/fly-connectome-template)
autorstwa [Merta Cobanova](https://github.com/cobanov). Ta wersja **jest
zmodyfikowana**. Kredyt UI: `src/components/Attribution.tsx` (nie usuwać).

- **MaleCNS v1.0** — CC BY 4.0, FlyEM / HHMI Janelia, University of Cambridge,
  MRC Laboratory of Molecular Biology, Google Research.
  <https://male-cns.janelia.org/>
- **Flybody** — Apache-2.0, Turaga Lab.
  <https://github.com/TuragaLab/flybody>
- Szablon: [Cobanov Template Attribution License 1.0](LICENSE).

Literatura behawioralna (parametry ruchu, nie neurony w tym buildzie):

- van Breugel F, Dickinson MH (2012) *J Exp Biol* — lądowanie / τ.
- Card G, Dickinson MH (2008) *J Exp Biol* — takeoff typ 1 vs 2.
- Seeds AM et al. (2014) *eLife* — hierarchia czyszczenia.
- Murphy KR et al. (2016) *eLife* — sen po słodkim posiłku.
- Chen E, Seeds AM (2025) — hierarchia czyszczenia (cytowanie, nie IDs).
- Shiu et al., *Nature* 2024 — LIF sugar GRN → MN9 (tu: cały kanał gustatoryczny).

---
---

# MUSZKA-MAMUTA (English)

A browser simulation: *Drosophila melanogaster* with a MaleCNS v1.0-driven
spiking brain eats a wedge of Polish farmer’s cheese (**vanilla twaróg**)
forever. Kitchen table, side HUD, view switcher. This is a **modified**
fork of [fly-connectome-template](https://github.com/cobanov/fly-connectome-template)
by [Mert Cobanov](https://github.com/cobanov).

**One** `npm run dev` is enough. Do not start extra Vite processes.

## Measured vs authored

From the in-app **Methods** drawer:

**MEASURED (MaleCNS v1.0, CC BY 4.0):** connection graph and weights; 271
proboscis gustatory neurons (`class == "gustatory"` AND subclass in
{labellar bristle, taste peg, pharyngeal sensillum}); MN9 bodyId **10331**
and **16949**; synapse signs from neurotransmitter predictions; drive roles
from measurement (`docs/DATA-PIPELINE.md`). MaleCNS has **no** sugar/bitter
receptor annotations (no Gr64f / Gr5a / Gr66a).

**AUTHORED:** LIF parameters (`src/brain/params.ts` citations), hunger and
hemolymph, food chemistry (`TWAROG_MAMUTA_WANILIOWY`, sweet 0.75), 6× render
scale (15 mm on screen), procedural rig, every motion clip, flight, grooming, sleep, gags,
MN9-rate → pump mapping. The connectome drives **only the feeding gate**
(gustatory channel → MN9). `ActivityFrame` is one-way: body and food consume
it; they never write into it.

**LIMITATIONS:** excitatory vs inhibitory character is inferred, not measured.
The whole gustatory channel drives MN9 less than single seeds do (lateral
inhibition / normalisation) — a measured circuit property.

## Negative result: `path_sign`

`path_sign` (sign of the strongest ≤4-hop walk from a seed to MN9) was
**tested and rejected**. It is not a sweet/bitter label and not a net effect.
`validate_per.ts` (2026-09-16, seed 1, 100 Hz / 500 ms):

| Stimulus | MN9 |
| --- | ---: |
| all `gust_labellar` (223) | **32 Hz** |
| `path_sign = −1` subset (107) | **52 Hz** |

The −1 subset drove MN9 **harder**, not weaker. Metadata keeps
`path_sign_deprecated`. The model does not use it.

## Non-additivity (after 0.25 Hz tonic calibration)

2 Hz tonic on all 271 seeds put MN9 at **29 Hz** (feeding, not rest).
Calibrated `BACKGROUND_RATE_HZ = 0.25` → MN9 rest **3.75 Hz** (2000 ms window).

| Measurement | Value |
| --- | ---: |
| whole labellar/peg channel (223), 100 Hz / 500 ms | MN9 **28 Hz**, rise **+24.25 Hz** |
| strongest single-seed `Δ` | **+137.25 Hz** |
| `gust_drive` (91) | MN9 **87 Hz** (rise +83.25 Hz) |
| `gust_suppress` (90) | MN9 **22 Hz** (rise +18.25 Hz) |
| drive − suppress gap | **65 Hz** |

Whole-channel rise is far below the max single-seed delta.

## Setup

Node.js **22.18+**:

```sh
npm ci
npm run dev
```

Open the Vite URL. **A single** dev server is enough. Live LIF starts after
the atlas loads. UI is Polish first; **EN** toggles English. `?reel=1` leaves
slogan + raster. `?record=1` records a 1080×1920 VP9/WebM loop (Reel camera,
slogan composited).

```sh
npm test && npm run check:assets && npm run validate:circuit && npm run soak
npm run build && npm run preview
```

Serve `dist/` on any static host. `base: './'` so subpaths work. Cloudflare
Pages: build `npm run build`, output `dist`. Shipped `graph.bin` is MMG1
(~13 MB), under the 25 MB per-file limit.

WebM → MP4: `scripts/webm2mp4.sh input.webm` (ffmpeg, H.264, yuv420p, 30 fps,
`+faststart`).

## Asset pipeline

1. `scripts/data-prep/inspect_malecns.py` — seeds from annotations.
2. `scripts/data-prep/extract_feeding_circuit.py` — 20k feeding-gate carve, CSR.
   Keep `write_csr` (uncompressed audit in `data/derived/`) and
   `write_csr_compressed` (public `graph.bin`).
3. `npm run compress:graph` if you rebuild the bin.
4. `npm run calibrate:background` — 0.25 Hz tonic.
5. `npm run measure:drive` — `deltaMn9Hz` terciles.
6. `npm run validate:circuit` must print **PASS**.
7. Kitchen textures: `scripts/textures/build_textures.py --in assets/photos --out assets/textures`
   (packaging cutout, curd tile, normal/roughness, `textures.json`).
8. Soma atlas and Flybody under `public/data/` (`npm run check:assets`).

See `docs/DATA-PIPELINE.md`, `docs/METABOLISM.md`, `docs/BODY-MODEL.md`,
`docs/QA.md`.

## Credits and licences

Built with [fly-connectome-template](https://github.com/cobanov/fly-connectome-template)
by [Mert Cobanov](https://github.com/cobanov). **This version is modified.**
Keep `src/components/Attribution.tsx` visible and linked.

- **MaleCNS v1.0** — CC BY 4.0, FlyEM / HHMI Janelia, University of Cambridge,
  MRC LMB, Google Research. <https://male-cns.janelia.org/>
- **Flybody** — Apache-2.0. <https://github.com/TuragaLab/flybody>
- Template: [Cobanov Template Attribution License 1.0](LICENSE).

Behavioural literature (motion parameters; not neuron IDs in this build):
van Breugel & Dickinson 2012; Card & Dickinson 2008; Seeds et al. 2014;
Murphy et al. 2016; Chen & Seeds 2025; Shiu et al. Nature 2024 (LIF feeding
gate ground truth).
