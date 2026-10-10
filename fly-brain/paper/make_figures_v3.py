"""Figures for draft 3, drawn only from experiment/results/plan3 and plan4 JSON/CSV files."""
import json, csv, math, collections
from pathlib import Path
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
E = Path(__file__).resolve().parents[1] / 'experiment/results'
A = json.load(open(E / 'plan3/3A.json')); B = json.load(open(E / 'plan3/3B.json')); D = json.load(open(E / 'plan3/3B_descriptives.json')); X = json.load(open(E / 'plan3/3A_review_checks.json'))
I = json.load(open(E / 'plan4/instinct.json')); C = list(csv.DictReader(open(E / 'plan4/courtship_cases.csv')))
INK, MUTED, ACC, BG, LINE = '#0a0a0a', '#8a8880', '#0034ff', '#ffffff', '#c4c1b3'
plt.rcParams.update({'font.family': 'sans-serif', 'font.size': 9, 'axes.spines.top': False, 'axes.spines.right': False, 'axes.edgecolor': INK, 'figure.facecolor': BG, 'axes.facecolor': BG})
# Figure 1: (a) ranking by predictor; (b) simulation minus path score
sets = [('C2_v783', 'P3_2A_F783T', 'FlyWire v783', False), ('C1_male', 'P3_2A_Ms', 'Male CNS', False), ('DEV_v630_exploratory', 'P3_paperST3', 'FlyWire v630\n(development)', True)]
preds = [('P1_steps', 'Step count, every connection', MUTED), ('P2_path3', 'Path score, 3 steps (map only)', INK), (None, 'Spiking simulation', ACC)]
fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.4, 3.4), gridspec_kw={'width_ratios': [2.3, 1], 'wspace': 0.45})
for i, (s, simkey, lab, dev) in enumerate(sets):
    for j, (k, name, col) in enumerate(preds):
        r = A[s][k or simkey]; x = i + (j - 1) * 0.24
        ax.errorbar(x, r['auroc'], yerr=[[r['auroc'] - r['ci95'][0]], [r['ci95'][1] - r['auroc']]], fmt='o', color=col, ms=6, capsize=3, lw=1.3, mfc=BG if dev else col, label=name if i == 0 else None)
        ax.text(x, r['ci95'][1] + 0.015, f"{r['auroc']:.2f}", ha='center', va='bottom', fontsize=8, color=col)
    r = A[s][simkey]; d, ci = r['diff_P3_minus_P2'], r['diff_P3_minus_P2_ci95']
    bx.errorbar(d, 2 - i, xerr=[[d - ci[0]], [ci[1] - d]], fmt='o', color=INK, ms=6, capsize=3, lw=1.3, mfc=BG if dev else INK)
    bx.text(ci[1] + 0.01, 2 - i, f"{d:.2f}", va='center', fontsize=8)
ax.axhline(0.5, color=LINE, lw=1, ls='--'); ax.text(2.42, 0.505, 'chance', color=MUTED, fontsize=8, ha='right')
ax.set_xticks(range(3)); ax.set_xticklabels([s[2] for s in sets], fontsize=8); ax.set_ylim(0.35, 1.07); ax.set_ylabel('Ranking against real flies (AUROC)')
ax.legend(frameon=False, loc='lower left', fontsize=7, ncol=3, bbox_to_anchor=(-0.02, 1.0), columnspacing=1.0, handletextpad=0.3); fig.text(0.01, 0.95, 'a', fontsize=10, fontweight='bold'); fig.text(0.70, 0.95, 'b', fontsize=10, fontweight='bold')
bx.axvline(0, color=LINE, lw=1, ls='--'); bx.set_yticks([2, 1, 0]); bx.set_yticklabels(['v783', 'male', 'v630\n(dev.)'], fontsize=8); bx.set_ylim(-0.6, 2.6); bx.set_xlim(-0.1, 0.3)
bx.set_xlabel('Simulation minus path score')
fig.tight_layout(); fig.savefig('figures/v3_fig1_ranking.png', dpi=200, bbox_inches='tight'); fig.savefig('figures/v3_fig1_ranking.svg', bbox_inches='tight'); plt.close(fig)
# Figure 2: survey
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 3.1), gridspec_kw={'width_ratios': [1, 1.25]})
v = sorted(D['R1_consistent_rule']['values'].values()); single = {88.0, 70.0, 81.0}
a1.axhspan(62, 72, color='#e2e0da', lw=0); a1.axhline(67.0, color=ACC, lw=1.2)
a1.scatter([i for i, x in enumerate(v) if x not in single], [x for x in v if x not in single], color=INK, s=26, zorder=3, label='mean of repeated runs, or not stated')
a1.scatter([i for i, x in enumerate(v) if x in single], [x for x in v if x in single], facecolors=BG, edgecolors=INK, s=26, zorder=3, label='single-trial run')
a1.legend(frameon=False, fontsize=7, loc='upper left'); a1.set_xticks([]); a1.set_xlabel('Projects, sorted by reported value'); a1.set_ylim(55, 97); a1.set_ylabel('Reported MN9 rate (Hz)')
a1.text(-0.3, 57, "line: authors' shipped run, 67.0 Hz; band: ±5 Hz", color=MUTED, fontsize=7); a1.set_title('a', loc='left', fontsize=10, fontweight='bold', x=-0.2)
f = sorted(B['R3']['values'].values()); c = collections.Counter(); ys = []
for x in f: ys.append(c[x]); c[x] += 1
der = [(x, y) for x, y in zip(f, ys) if x == 0.65 and y > 0]; own = [(x, y) for x, y in zip(f, ys) if not (x == 0.65 and y > 0)]
a2.axvline(0.561, color=ACC, lw=1); a2.axvline(0.581, color=MUTED, lw=1); a2.axvline(1.0, color=LINE, lw=1, ls='--')
a2.scatter(*zip(*own), color=INK, s=26, zorder=3, label='stated correction'); a2.scatter(*zip(*der), facecolors=BG, edgecolors=INK, s=26, zorder=3, label='taken from another project')
a2.legend(frameon=False, fontsize=7, loc='upper left'); a2.set_yticks([]); a2.set_ylim(-1.2, 5.5); a2.set_xlim(0, 1.08)
a2.text(0.02, -0.9, 'lines: 0.561 (ours), 0.581 (male-map preprint), 1.0 (published weight)', color=MUTED, fontsize=6.5)
a2.set_xlabel('Weight correction on the male connectome'); a2.set_title('b', loc='left', fontsize=10, fontweight='bold', x=-0.05)
fig.tight_layout(); fig.savefig('figures/v3_fig2_survey.png', dpi=200, bbox_inches='tight'); fig.savefig('figures/v3_fig2_survey.svg', bbox_inches='tight'); plt.close(fig)
# Figure S1: instinct function
fig, a1 = plt.subplots(figsize=(5.6, 3.3))
lab = {'F1': 'sweet', 'F2': 'sweet + bitter', 'F3': 'sweet + Ir94e', 'F4': 'strong sweet + bitter', 'F5': 'strong sweet + Ir94e', 'F6': 'water', 'G1': 'antennal touch (grooming neurons)', 'G2': 'touch, JO-CE (aBN1)', 'G3': 'touch, JO-F (aBN1)'}
ks = list(lab); y = list(range(len(ks)))[::-1]
for yy, k in zip(y, ks):
    cc = I['cases'][k]; a1.barh(yy, cc['mean_rate_hz'], color=INK if cc['match'] else BG, edgecolor=INK, height=0.6)
    if cc['mean_rate_hz'] == 0: a1.text(0.8, yy, '0', va='center', fontsize=7, color=INK)
    a1.text(max(cc['mean_rate_hz'], 5) + 3, yy, f"real flies: {cc['real_flies']}", va='center', fontsize=7, color=MUTED)
a1.axvline(5, color=ACC, lw=1.2); a1.text(6, len(ks) - 0.4, 'yes at 5 Hz or more', color=ACC, fontsize=7)
a1.set_yticks(y); a1.set_yticklabels([lab[k] for k in ks], fontsize=8); a1.set_xlabel('Readout firing rate (Hz); MN9 unless stated'); a1.set_xlim(0, 112); a1.set_ylim(-0.6, len(ks) + 0.2)
fig.tight_layout(); fig.savefig('figures/v3_figS1_instinct.png', dpi=200, bbox_inches='tight'); fig.savefig('figures/v3_figS1_instinct.svg', bbox_inches='tight'); plt.close(fig)
# Figure S2: courtship
fig, a2 = plt.subplots(figsize=(5.2, 3.6))
rows = [r for r in C if r['tier'] in ('primary', 'indirect', 'control')]; rows.sort(key=lambda r: -float(r['score_4']) / float(r['n_neurons']))
for i, r in enumerate(rows):
    v = float(r['score_4']) / float(r['n_neurons']); x = math.log10(v) if v > 0 else 6.6; yy = len(rows) - 1 - i
    if r['tier'] == 'control': a2.scatter(x, yy, s=30, marker='s', color=ACC, zorder=3)
    else: a2.scatter(x, yy, s=28, zorder=3, facecolors=INK if r['truth'] == 'YES' else BG, edgecolors=INK if r['tier'] == 'primary' else MUTED)
    a2.text(x + 0.1, yy, r['case'] + (' (score 0)' if v == 0 else ''), fontsize=6.5, va='center', color=INK if r['tier'] != 'indirect' else MUTED)
a2.set_yticks([]); a2.set_xlabel('Path score per neuron to wing motor neurons (log10 scale)'); a2.set_xlim(6.4, 13.2)
fig.tight_layout(); fig.savefig('figures/v3_figS2_courtship.png', dpi=200, bbox_inches='tight'); fig.savefig('figures/v3_figS2_courtship.svg', bbox_inches='tight'); plt.close(fig)
print('ok')
