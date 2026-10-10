"""Figures for the draft, drawn only from experiment/results/plan3/*.json."""
import json
from pathlib import Path
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
R = Path(__file__).resolve().parents[1] / 'experiment/results/plan3'
A = json.load(open(R / '3A.json')); B = json.load(open(R / '3B.json')); D = json.load(open(R / '3B_descriptives.json'))
INK, MUTED, ACC, BG, LINE = '#0a0a0a', '#8a8880', '#0034ff', '#ffffff', '#c4c1b3'
plt.rcParams.update({'font.family': 'sans-serif', 'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False, 'axes.edgecolor': INK, 'figure.facecolor': BG, 'axes.facecolor': BG})
# Figure 1: ranking score by predictor and set
sets = [('C2_v783', 'P3_2A_F783T', 'FlyWire v783\n(101 types, 13 positive)'), ('C1_male', 'P3_2A_Ms', 'Male CNS\n(99 types, 13 positive)'), ('DEV_v630_exploratory', 'P3_paperST3', 'FlyWire v630, development\n(106 types, 14 positive)')]
preds = [('P1_steps', 'Step count (every connection)', MUTED), ('P2_path3', 'Path score (3 steps, map only)', INK), (None, 'Spiking simulation', ACC)]
fig, ax = plt.subplots(figsize=(7.0, 3.3))
for i, (s, simkey, lab) in enumerate(sets):
    for j, (k, name, col) in enumerate(preds):
        r = A[s][k or simkey]; x = i + (j - 1) * 0.24
        ax.errorbar(x, r['auroc'], yerr=[[r['auroc'] - r['ci95'][0]], [r['ci95'][1] - r['auroc']]], fmt='o', color=col, ms=6, capsize=3, lw=1.3, label=name if i == 0 else None)
        ax.text(x, r['ci95'][1] + 0.015, f"{r['auroc']:.2f}", ha='center', va='bottom', fontsize=8, color=col)
ax.axhline(0.5, color=LINE, lw=1, ls='--'); ax.text(2.42, 0.505, 'chance', color=MUTED, fontsize=8, ha='right')
ax.set_xticks(range(3)); ax.set_xticklabels([s[2] for s in sets]); ax.set_ylim(0.35, 1.05); ax.set_ylabel('Ranking score against real flies (AUROC)')
ax.legend(frameon=False, loc='lower left', fontsize=8, ncol=3, bbox_to_anchor=(0, 1.0))
fig.tight_layout(); fig.savefig('figures/fig1_ranking.png', dpi=200); fig.savefig('figures/fig1_ranking.svg'); plt.close(fig)
# Figure 2: census
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.0, 3.0), gridspec_kw={'width_ratios': [1, 1.25]})
v = sorted(D['R1_consistent_rule']['values'].values())
a1.axhspan(62, 72, color='#e2e0da', lw=0); a1.axhline(67.0, color=ACC, lw=1.2)
single = {88.0, 70.0, 81.0}  # single short runs by the projects' own description
a1.scatter([i for i, x in enumerate(v) if x not in single], [x for x in v if x not in single], color=INK, s=26, zorder=3, label='mean of repeated runs or not stated')
a1.scatter([i for i, x in enumerate(v) if x in single], [x for x in v if x in single], facecolors=BG, edgecolors=INK, s=26, zorder=3, label='single short run')
a1.legend(frameon=False, fontsize=7, loc='upper left'); a1.set_xticks([]); a1.set_ylim(55, 97)
a1.set_ylabel('Reported MN9 rate (Hz)'); a1.set_title('Headline case, 9 projects', fontsize=9, loc='left')
a1.text(len(v) - 0.6, 67.6, "authors' shipped run: 67.0 Hz", color=ACC, fontsize=8, ha='right', va='bottom'); a1.text(-0.3, 62.4, '±5 Hz band', color=MUTED, fontsize=8)
f = sorted(B['R3']['values'].values())
a2.axvspan(0.5, 0.65, color='#e2e0da', lw=0); a2.axvline(1.0, color=LINE, lw=1, ls='--')
import collections; c = collections.Counter(); ys = []
for x in f: ys.append(c[x]); c[x] += 1
der = [(x, y) for x, y in zip(f, ys) if x == 0.65 and y > 0]  # three 0.65 values derived from one project
own = [(x, y) for x, y in zip(f, ys) if not (x == 0.65 and y > 0)]
a2.scatter(*zip(*own), color=INK, s=26, zorder=3, label='stated correction'); a2.scatter(*zip(*der), facecolors=BG, edgecolors=INK, s=26, zorder=3, label='taken from another project')
a2.legend(frameon=False, fontsize=7, loc='upper left'); a2.set_yticks([]); a2.set_ylim(-1, 5.5); a2.set_xlim(0, 1.08)
a2.set_xlabel('Weight correction (1.0 = published weight)'); a2.set_title('Male-connectome corrections, 14 projects', fontsize=9, loc='left')
a2.text(0.575, -0.7, '0.5–0.65', color=MUTED, fontsize=8, ha='center')
fig.tight_layout(); fig.savefig('figures/fig2_census.png', dpi=200); fig.savefig('figures/fig2_census.svg'); plt.close(fig)
print('ok')

# Figure 3: instinct function and courtship check (from experiment/results/plan4)
R4 = Path(__file__).resolve().parents[1] / 'experiment/results/plan4'
I = json.load(open(R4 / 'instinct.json')); import csv
C = list(csv.DictReader(open(R4 / 'courtship_cases.csv')))
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.4), gridspec_kw={'width_ratios': [1.15, 1]})
lab = {'F1': 'sweet', 'F2': 'sweet + bitter', 'F3': 'sweet + Ir94e', 'F4': 'strong sweet + bitter', 'F5': 'strong sweet + Ir94e', 'F6': 'water', 'G1': 'antennal touch', 'G2': 'touch, JO-CE', 'G3': 'touch, JO-F'}
ks = list(lab); y = range(len(ks))[::-1]
for yy, k in zip(y, ks):
    c = I['cases'][k]; a1.barh(yy, c['mean_rate_hz'], color=INK if c['match'] else BG, edgecolor=INK, height=0.6)
    a1.text(max(c['mean_rate_hz'], 0) + 2, yy, f"real flies: {c['real_flies']}", va='center', fontsize=7, color=MUTED)
a1.axvline(5, color=ACC, lw=1.2); a1.text(6, len(ks) - 0.45, 'yes at 5 Hz or more', color=ACC, fontsize=7)
a1.set_yticks(list(y)); a1.set_yticklabels([lab[k] for k in ks], fontsize=8); a1.set_xlabel('Readout firing rate (Hz)'); a1.set_xlim(0, 110); a1.set_ylim(-0.6, len(ks) + 0.1)
a1.set_title('Instinct function: 6 of 9 match (filled)', fontsize=9, loc='left')
import math
rows = [r for r in C if r['tier'] in ('primary', 'indirect')]; rows.sort(key=lambda r: -float(r['score_4']))
for i, r in enumerate(rows):
    v = float(r['score_4']); x = math.log10(v) if v > 0 else 7.5
    a2.scatter(x, len(rows) - 1 - i, s=28, zorder=3, facecolors=INK if r['truth'] == 'YES' else BG, edgecolors=INK if r['tier'] == 'primary' or r['truth'] == 'YES' else MUTED)
    a2.text(x + 0.12, len(rows) - 1 - i, r['case'] + (' (score 0)' if v == 0 else ''), fontsize=6.5, va='center', color=INK if r['tier'] == 'primary' else MUTED)
a2.set_yticks([]); a2.set_xlabel('Path score to wing motor neurons (log10)'); a2.set_xlim(7.2, 14.2)
a2.set_title('Courtship song: filled = sings in real flies', fontsize=9, loc='left')
fig.tight_layout(); fig.savefig('figures/fig3_instinct_courtship.png', dpi=200); fig.savefig('figures/fig3_instinct_courtship.svg'); plt.close(fig)
print('fig3 ok')
