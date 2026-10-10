# 🪰 FlySchool: Bio-Neural Classroom Simulator

Laboratório de neuroeducação e vida artificial: alunas e professora são moscas *Drosophila melanogaster*
virtuais governadas por **redes neurais de espículas (LIF)** que aprendem por **STDP modulado por dopamina**
em uma escola 3D (sala de aula, pátio/refeitório, banheiro, descanso e arena de prova).

**Stack:** Next.js 15 (App Router) · TypeScript · Tailwind CSS 4 · Three.js / @react-three/fiber / drei · Recharts · jsPDF · Zustand

## Rodando

```bash
npm install
npm run dev          # http://localhost:3000
npm run build        # build de produção (Vercel)
npm run sim:headless # simula 3 dias sem renderização e imprime a curva de aprendizado
```
## Arquitetura

| Módulo | Responsabilidade |
|---|---|
| `src/core/FlyConnectome.ts` | SNN LIF (dt = 5 ms), 96 neurônios, CSR, STDP competitivo + dopamina, STM/LTM, escalonamento sináptico |
| `src/core/FlyAgent.ts` | Sensores → correntes, seleção de ação, acumulador de evidência (MBON → placa), cinemática DNg, homeostase |
| `src/core/SchoolDirector.ts` | Relógio, campainha, cronograma, rotina didática do professor (estímulo, glicose, rajada de ar, estrobo, feromônio) |
| `src/core/ExamSystem.ts` | Provas A–E sem reforço: tempo de decisão, rota, acerto, estado interno |
| `src/core/Analytics.ts` | Curvas, matriz individual, perfis, correlação ponto-bisserial, eficácia por método |
| `src/core/ReportGenerator.ts` | Relatório PDF (gráficos rasterizados em canvas offscreen) |
| `src/core/SimulationEngine.ts` | Orquestração, população, crises, estratégias |
| `src/components/3d/SchoolScene.tsx` | Cenário 3D, lousas e placas com texturas dinâmicas |
| `src/components/3d/FlyAgentView.tsx` | Malha procedural da mosca (marcha em tripé, asas, probóscide) |
| `src/components/ui/BrainGraphModal.tsx` | Grafo force-directed estilo Obsidian, heatmap KC→MBON, raster |
| `src/components/ui/AnalyticsDashboard.tsx` | Dashboard Recharts + botão de relatório |
| `src/components/ui/GodPanel.tsx` | População, crises, métodos de ensino, editor de estratégias, parâmetros da prova |

O motor (`src/core`) não depende de React/Three e roda headless (`scripts/headless.ts`).
No navegador, o engine fica acessível no console como `window.flyschool`.

## Modelo neural (resumo)

```
Lousa ─► 16 colunas visuais ─► 40 Kenyon cells (esparsas, APL) ─► 5 MBONs (placas A–E) ─► decisão
                    ▲ ganho atencional (CX)                ▲ ΔW = η·(PAM − PPL1)·traço(i,j)
Fome/Sede/Fadiga/Bexiga ─► neurônios de ação (WTA) ─► DNg (caminhar, girar, voar, probóscide, permanecer)
```

* **Crédito de escolha:** cópia eferente da placa escolhida + LTD heterossináptica pela média dos MBONs.
* **Memória:** W = W_curto (decai τ = 420 s e consolida τ = 300 s) + W_longo; consolidação extra no sono noturno.
* **Resultado típico** (18 alunas, método apetitivo): prova sobe de ~30–40% no dia 1 para ~55–60% no dia 3–5 (acaso = 20%), com forte variação individual.

## Dois motores neurais

### 1. Conectoma reduzido (padrão · até 40 moscas)
96 neurônios construídos à mão com classes celulares do FlyWire (Kenyon cells, APL, MBONs, PAM, PPL1,
PFL3, DNa02, Giant Fiber, Gr5a, Gr28b, Or67d…). Pesos calibrados, não medidos.

### 2. FlyWire completo (God Panel → "Motor neural" · 1–4 moscas)
Cada aluna roda **o cérebro inteiro**: 138.639 neurônios e 15,1 milhões de conexões do FlyWire v783,
num Web Worker próprio (~110 MB de RAM, 1 núcleo).

* **Modelo:** LIF de Shiu et al. (Nature 2024) com os mesmos parâmetros (v₀ −52 mV, limiar −45 mV,
  τm 20 ms, τsyn 5 ms, w = nº sinapses × sinal × 0,275 mV, entradas Poisson), dt = 1 ms, integração só
  dos neurônios ativos.
* **Validação:** os 21 receptores de açúcar do artigo a 200 Hz fazem o MN9 (probóscide) disparar ~50 Hz;
  PFL3 de um lado ativa o DNa02 contralateral.
* **Interface sensório-motora (neurônios anotados reais):** açúcar/água, feromônio, vento (órgão de
  Johnston), calor, ocelos, fotorreceptores R1-6/R7/R8 (retinotopia 4×4), ORNs por glomérulo, PFL3 → DNa02
  (direção), MN9 (alimentação), DNp01/Giant Fiber (fuga), neurônios endócrinos (DH44, IPC, ITP, DH31, dFB)
  para estados internos.
* **Memória:** as 62.261 sinapses reais KC→MBON são plásticas (regra de três fatores com covariância,
  dopamina do compartimento = DANs que inervam cada MBON, escala sináptica por MBON). Os 96 MBONs são
  lidos em 5 pools (placas A–E).

Limitações medidas e explicitadas na UI:
* Fotorreceptores são histaminérgicos (sinal inibitório) e não propagam num LIF puro → a lousa chega às
  KCs como **marcador odorífero** (pares de glomérulos escolhidos por baixa sobreposição medida,
  `scripts/build-odor-codes.ts`).
* Com os parâmetros originais, estímulos olfativos levam a atividade global (~80% das KCs). O preset
  "Balanceado" adiciona ganho inibitório ×5, adaptação de 1 mV e **APL graduado** (o APL real é
  não-espicante) — ajustáveis no God Panel; o preset "Shiu et al. original" reproduz o modelo publicado.
* A seleção de programa (atenção, fome, banheiro, social) é um modelo de utilidade homeostática fora do conectoma.
* **Resultado medido:** o pareamento odor + dopamina potencia fortemente o pool alvo (4 → 38 Hz em
  5 pareamentos), mas generaliza para outros odores. Na tarefa de 5 estímulos → 5 placas, 100 ensaios
  ficaram no acaso (20–26%; uma execução chegou a 50% na primeira metade e regrediu). Neste regime os
  códigos de KC são muito sobrepostos (similaridade 0,73–0,94). Reproduza com `scripts/fullbrain-learning.ts`,
  `fullbrain-pairing.ts` e `fullbrain-overlap.ts`.

Regerar o pacote de dados (requer os arquivos brutos em `data/flywire-raw/`, fora do git):

```bash
node --max-old-space-size=8192 scripts/build-flywire.mjs
npx tsx scripts/build-odor-codes.ts
```

Dados: FlyWire v783 (CC-BY 4.0) e Shiu et al. 2024 (MIT) — citações em `public/flywire/ATTRIBUTION.txt`.

Moscas aprendem associações *estímulo → placa recompensada*; rótulos como "3 + 1" são interpretação humana.
