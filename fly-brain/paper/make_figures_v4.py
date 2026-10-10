"""Figures for version 1.1 (paper layout). Drawn only from experiment/results/plan3 and plan4 files, except Figure 1, which is a schematic."""
import json, csv, math, collections
from pathlib import Path
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle
E = Path(__file__).resolve().parents[1] / 'experiment/results'; OUT = Path(__file__).resolve().parent / 'final/figures'; OUT.mkdir(parents=True, exist_ok=True)
A = json.load(open(E / 'plan3/3A.json')); B = json.load(open(E / 'plan3/3B.json')); D = json.load(open(E / 'plan3/3B_descriptives.json')); X = json.load(open(E / 'plan3/3A_review_checks.json'))
I = json.load(open(E / 'plan4/instinct.json')); T = list(csv.DictReader(open(E / 'plan3/3A_per_type.csv')))
INK, MUTED, ACC, BG, LINE, SOFT = '#0a0a0a', '#77756d', '#0034ff', '#ffffff', '#c4c1b3', '#e6e4dd'
plt.rcParams.update({'font.family': 'serif', 'font.serif': ['STIX Two Text', 'STIXGeneral', 'Times New Roman', 'DejaVu Serif'], 'mathtext.fontset': 'stix', 'font.size': 9,
                     'axes.spines.top': False, 'axes.spines.right': False, 'axes.edgecolor': INK, 'axes.linewidth': 0.7, 'figure.facecolor': BG, 'axes.facecolor': BG, 'xtick.major.width': 0.7, 'ytick.major.width': 0.7})
def save(fig, name): fig.savefig(OUT / f'{name}.png', dpi=220, bbox_inches='tight'); fig.savefig(OUT / f'{name}.svg', bbox_inches='tight'); plt.close(fig)

# ---- Figure 1: schematic of the three predictors (illustrative, not data)
fig, ax = plt.subplots(figsize=(7.0, 2.5)); ax.set_xlim(0, 10); ax.set_ylim(0, 3.6); ax.axis('off')
cols = [1.0, 3.2, 5.4, 7.6]; ys = {0: [1.8], 1: [2.8, 1.8, 0.8], 2: [2.8, 1.8, 0.8], 3: [1.8]}
def node(x, y, fc=BG, ec=INK, r=0.2): ax.add_patch(Circle((x, y), r, fc=fc, ec=ec, lw=1.0, zorder=3))
def arrow(p, q, col=INK, ls='-', lw=1.1): ax.add_patch(FancyArrowPatch(p, q, arrowstyle='-|>', mutation_scale=9, color=col, lw=lw, ls=ls, shrinkA=7, shrinkB=7, zorder=2))
node(cols[0], 1.8, fc=INK)
for c in (1, 2):
    for y in ys[c]: node(cols[c], y)
node(cols[3], 1.8, fc=ACC, ec=ACC)
for y in ys[1]: arrow((cols[0], 1.8), (cols[1], y))
arrow((cols[1], 2.8), (cols[2], 2.8)); arrow((cols[1], 2.8), (cols[2], 1.8)); arrow((cols[1], 1.8), (cols[2], 1.8), col=MUTED, ls=(0, (3, 2))); arrow((cols[1], 0.8), (cols[2], 0.8))
arrow((cols[2], 2.8), (cols[3], 1.8)); arrow((cols[2], 1.8), (cols[3], 1.8)); arrow((cols[2], 0.8), (cols[3], 1.8), col=MUTED, ls=(0, (3, 2)))
ax.text(cols[0], 0.2, 'activated\ncell type', ha='center', va='center', fontsize=8.5); ax.text(cols[3], 0.2, 'MN9\n(extends the proboscis)', ha='center', va='center', fontsize=8.5, color=ACC)
for k, c in enumerate(cols[1:], 1): ax.text((cols[k - 1] + c) / 2, 3.45, f'step {k}', ha='center', fontsize=8.5, color=MUTED)
ax.plot([8.55, 9.05], [2.9, 2.9], color=INK, lw=1.1); ax.text(9.15, 2.9, 'excitatory', va='center', fontsize=8)
ax.plot([8.55, 9.05], [2.5, 2.5], color=MUTED, lw=1.1, ls=(0, (3, 2))); ax.text(9.15, 2.5, 'inhibitory', va='center', fontsize=8, color=MUTED)
ax.text(8.55, 1.75, 'Step count: fewest steps\nPath score: signed weights,\n  negatives clipped, summed\nSimulation: spiking neurons', fontsize=7.6, va='center', linespacing=1.35)
save(fig, 'fig1_predictors')

# ---- Figure 2: ranking and paired difference
sets = [('C2_v783', 'P3_2A_F783T', 'FlyWire v783', False), ('C1_male', 'P3_2A_Ms', 'Male CNS', False), ('DEV_v630_exploratory', 'P3_paperST3', 'FlyWire v630\n(development)', True)]
preds = [('P1_steps', 'Step count, every connection', MUTED), ('P2_path3', 'Path score, 3 steps (map only)', INK), (None, 'Spiking simulation', ACC)]
fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.0, 3.1), gridspec_kw={'width_ratios': [2.3, 1], 'wspace': 0.42})
for i, (s, simkey, lab, dev) in enumerate(sets):
    for j, (k, name, col) in enumerate(preds):
        r = A[s][k or simkey]; x = i + (j - 1) * 0.24
        ax.errorbar(x, r['auroc'], yerr=[[r['auroc'] - r['ci95'][0]], [r['ci95'][1] - r['auroc']]], fmt='o', color=col, ms=5.5, capsize=3, lw=1.1, mfc=BG if dev else col, label=name if i == 0 else None)
        ax.text(x, r['ci95'][1] + 0.015, f"{r['auroc']:.2f}", ha='center', va='bottom', fontsize=8, color=col)
    r = A[s][simkey]; d, ci = r['diff_P3_minus_P2'], r['diff_P3_minus_P2_ci95']
    bx.errorbar(d, 2 - i, xerr=[[d - ci[0]], [ci[1] - d]], fmt='o', color=INK, ms=5.5, capsize=3, lw=1.1, mfc=BG if dev else INK); bx.text(ci[1] + 0.012, 2 - i, f"{d:.2f}", va='center', fontsize=8)
ax.axhline(0.5, color=LINE, lw=0.9, ls='--'); ax.text(2.42, 0.508, 'chance', color=MUTED, fontsize=8, ha='right')
ax.set_xticks(range(3)); ax.set_xticklabels([s[2] for s in sets]); ax.set_ylim(0.35, 1.07); ax.set_ylabel('Ranking against real flies (AUROC)')
fig.legend(*ax.get_legend_handles_labels(), frameon=False, loc='upper center', fontsize=7.5, ncol=3, bbox_to_anchor=(0.5, 1.09), columnspacing=1.0, handletextpad=0.2)
bx.axvline(0, color=LINE, lw=0.9, ls='--'); bx.set_yticks([2, 1, 0]); bx.set_yticklabels(['v783', 'male', 'v630\n(dev.)']); bx.set_ylim(-0.6, 2.6); bx.set_xlim(-0.1, 0.3); bx.set_xlabel('Simulation minus path score')
fig.text(0.02, 0.95, '(a)', fontsize=10, fontweight='bold'); fig.text(0.68, 0.95, '(b)', fontsize=10, fontweight='bold'); save(fig, 'fig2_ranking')

# ---- Figure 3: every cell type, path score against simulated rate
fig, axs = plt.subplots(1, 2, figsize=(7.0, 3.0), sharey=True, gridspec_kw={'wspace': 0.08})
for a, (sname, simcol, title) in zip(axs, (('C2_v783', 'P3_2A_F783T', 'FlyWire v783'), ('C1_male', 'P3_2A_Ms', 'Male CNS'))):
    rows = [r for r in T if r['set'] == sname]
    px = np.array([math.log10(1 + float(r['P2_path3'])) for r in rows]); sy = np.array([float(r[simcol]) for r in rows]); pos = np.array([r['observed_positive'].lower() == 'true' for r in rows])
    rng = np.random.default_rng(1); jx = np.where(px == 0, rng.uniform(-0.25, 0.25, len(px)), 0); jy = np.where(sy == 0, rng.uniform(-0.035, 0.035, len(sy)), 0)
    yy = np.log10(1 + sy) + jy
    a.scatter(px[~pos] + jx[~pos], yy[~pos], s=16, facecolors=BG, edgecolors=MUTED, lw=0.8, label='no response in real flies')
    a.scatter(px[pos] + jx[pos], yy[pos], s=22, color=ACC, zorder=3, label='real flies extend')
    a.set_title(title, fontsize=9.5); a.set_xlabel('Path score, $\\log_{10}(1+\\mathrm{score})$'); a.set_yticks([0, math.log10(2), math.log10(11), math.log10(101)]); a.set_yticklabels(['0', '1', '10', '100'])
    a.text(0.02, 0.97, f"{int(((px == 0) & (sy == 0)).sum())} types at zero on both", transform=a.transAxes, fontsize=7.5, color=MUTED, va='top')
axs[0].set_ylabel('Simulated MN9 rate (Hz)'); h, l = axs[1].get_legend_handles_labels(); fig.legend(h, l, frameon=False, fontsize=8, loc='upper center', ncol=2, bbox_to_anchor=(0.5, 1.06)); save(fig, 'fig3_scatter')

# ---- Figure 4: silencing, and the effect of leaving out weak connections
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.0, 2.9), gridspec_kw={'width_ratios': [1, 1.35], 'wspace': 0.35})
c3 = A['C3_silencing']; s = X['silencing']
labs = ['Simulation', 'Always\n"required"', 'Path\nscore', 'Always "not\nrequired"']; vals = [c3['sim_correct'], s['always_required_correct'], c3['map_correct_3steps'], s['always_not_required_correct']]
a1.bar(range(4), vals, color=[ACC, SOFT, INK, SOFT], edgecolor=[ACC, MUTED, INK, MUTED], width=0.62, lw=0.8)
for i, v in enumerate(vals): a1.text(i, v + 0.3, str(v), ha='center', fontsize=8.5)
a1.set_xticks(range(4)); a1.set_xticklabels(labs, fontsize=7.4); a1.set_ylim(0, 18); a1.set_yticks([0, 6, 12, 18]); a1.set_ylabel('Correct of 18 silencing cases')
th = X['thresholded_5plus_synapses']; order = [('C2_v783', 'FlyWire v783', 'P3_2A_F783T'), ('C1_male', 'Male CNS', 'P3_2A_Ms'), ('DEV_v630', 'FlyWire v630\n(development)', 'P3_paperST3')]
for i, (k, lab, simkey) in enumerate(order):
    key = 'DEV_v630_exploratory' if k == 'DEV_v630' else k
    base, thr, sim = A[key]['P2_path3']['auroc'], th[k]['path_score'], th[k]['simulation']
    a2.plot([i - 0.2, i], [base, thr], color=INK, lw=0.9); a2.scatter(i - 0.2, base, s=30, facecolors=BG, edgecolors=INK, zorder=3, label='path score, every connection' if i == 0 else None)
    a2.scatter(i, thr, s=30, color=INK, zorder=3, label='path score, 5+ synapses only' if i == 0 else None); a2.scatter(i + 0.2, sim, s=30, color=ACC, zorder=3, label='simulation' if i == 0 else None)
    for xx, v, col in ((i - 0.2, base, INK), (i, thr, INK), (i + 0.2, sim, ACC)): a2.text(xx, v + 0.012, f'{v:.2f}', ha='center', fontsize=7.5, color=col)
a2.set_xticks(range(3)); a2.set_xticklabels([o[1] for o in order], fontsize=8); a2.set_ylim(0.65, 0.92); a2.set_ylabel('AUROC'); a2.legend(frameon=False, fontsize=7.3, loc='upper center', ncol=3, bbox_to_anchor=(0.5, 1.14), columnspacing=0.8, handletextpad=0.1)
fig.text(0.02, 0.97, '(a)', fontsize=10, fontweight='bold'); fig.text(0.44, 0.97, '(b)', fontsize=10, fontweight='bold'); save(fig, 'fig4_silencing_threshold')

# ---- Figure 5: survey results
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.0, 2.9), gridspec_kw={'width_ratios': [1, 1.25], 'wspace': 0.22})
v = sorted(D['R1_consistent_rule']['values'].values()); single = {88.0, 70.0, 81.0}
a1.axhspan(62, 72, color=SOFT, lw=0); a1.axhline(67.0, color=ACC, lw=1.1)
a1.scatter([i for i, x in enumerate(v) if x not in single], [x for x in v if x not in single], color=INK, s=24, zorder=3, label='mean of repeated runs, or not stated')
a1.scatter([i for i, x in enumerate(v) if x in single], [x for x in v if x in single], facecolors=BG, edgecolors=INK, s=24, zorder=3, label='single-trial run')
a1.legend(frameon=False, fontsize=7.3, loc='upper left'); a1.set_xticks([]); a1.set_xlabel('Projects, sorted by reported value'); a1.set_ylim(55, 97); a1.set_ylabel('Reported MN9 rate (Hz)')
f = sorted(B['R3']['values'].values()); c = collections.Counter(); ys = []
for x in f: ys.append(c[x]); c[x] += 1
der = [(x, y) for x, y in zip(f, ys) if x == 0.65 and y > 0]; own = [(x, y) for x, y in zip(f, ys) if not (x == 0.65 and y > 0)]
a2.axvline(0.561, color=ACC, lw=1); a2.axvline(0.581, color=MUTED, lw=1); a2.axvline(1.0, color=LINE, lw=0.9, ls='--')
a2.scatter(*zip(*own), color=INK, s=24, zorder=3, label='stated correction'); a2.scatter(*zip(*der), facecolors=BG, edgecolors=INK, s=24, zorder=3, label='taken from another project')
a2.legend(frameon=False, fontsize=7.3, loc='lower left', ncol=2, bbox_to_anchor=(0.12, 0.98), columnspacing=1.0); a2.set_yticks([]); a2.set_ylim(-0.8, 5.5); a2.set_xlim(0, 1.08); a2.set_xlabel('Weight correction on the male connectome')
fig.text(0.02, 0.95, '(a)', fontsize=10, fontweight='bold'); fig.text(0.47, 0.95, '(b)', fontsize=10, fontweight='bold'); save(fig, 'fig5_survey')

# ---- Figure 6: who the surveyed projects are
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.0, 2.3), gridspec_kw={'wspace': 0.3})
m = D['first_commit_month_included']; months = ['2026-06', '2026-07', '2026-08', '2026-09', '2026-10']; mv = [m.get(k, 0) for k in months]
a1.bar(range(5), mv, color=INK, width=0.62)
for i, vv in enumerate(mv): a1.text(i, vv + 1.2, str(vv), ha='center', fontsize=8.5)
a1.set_xticks(range(5)); a1.set_xticklabels(['Jun', 'Jul', 'Aug', 'Sep', 'Oct\n(to the 10th)'], fontsize=8); a1.set_ylim(0, 74); a1.set_ylabel('Projects, by first commit (2026)')
cc = B['connectome_counts_included']; cv = [cc['v783'], cc['maleCNS'], cc['v630'], cc['not stated'] + cc['not stated | v630']]
a2.barh(range(4)[::-1], cv, color=[INK, INK, INK, SOFT], edgecolor=[INK, INK, INK, MUTED], height=0.6, lw=0.8)
for i, vv in zip(range(4)[::-1], cv): a2.text(vv + 0.6, i, str(vv), va='center', fontsize=8.5)
a2.set_yticks(range(4)[::-1]); a2.set_yticklabels(['FlyWire v783', 'Male CNS', 'FlyWire v630', 'not stated\nor unclear'], fontsize=8); a2.set_xlim(0, 38); a2.set_xlabel('Projects, by connectome of the headline number')
fig.text(0.02, 0.97, '(a)', fontsize=10, fontweight='bold'); fig.text(0.5, 0.97, '(b)', fontsize=10, fontweight='bold'); save(fig, 'fig6_projects')

# ---- Figure S1: instinct function
fig, a1 = plt.subplots(figsize=(5.6, 3.1))
lab = {'F1': 'sweet', 'F2': 'sweet + bitter', 'F3': 'sweet + Ir94e', 'F4': 'strong sweet + bitter', 'F5': 'strong sweet + Ir94e', 'F6': 'water', 'G1': 'antennal touch (grooming neurons)', 'G2': 'touch, JO-CE (aBN1)', 'G3': 'touch, JO-F (aBN1)'}
ks = list(lab); y = list(range(len(ks)))[::-1]
for yy, k in zip(y, ks):
    cc = I['cases'][k]; a1.barh(yy, cc['mean_rate_hz'], color=INK if cc['match'] else BG, edgecolor=INK, height=0.6, lw=0.8)
    if cc['mean_rate_hz'] == 0: a1.text(0.8, yy, '0', va='center', fontsize=7.5)
    a1.text(max(cc['mean_rate_hz'], 5) + 3, yy, f"real flies: {cc['real_flies']}", va='center', fontsize=7.5, color=MUTED)
a1.axvline(5, color=ACC, lw=1.1); a1.text(6, len(ks) - 0.4, 'yes at 5 Hz or more', color=ACC, fontsize=7.5)
a1.set_yticks(y); a1.set_yticklabels([lab[k] for k in ks], fontsize=8); a1.set_xlabel('Readout firing rate (Hz); MN9 unless stated'); a1.set_xlim(0, 112); a1.set_ylim(-0.6, len(ks) + 0.2)
save(fig, 'figS1_instinct'); print('ok')
