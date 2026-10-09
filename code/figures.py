"""Figures for RESULTS.md, drawn only from results/*.parquet and results/*.json."""
import json
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT = Path(__file__).resolve().parents[1]; R = ROOT / 'results'; F = R / 'figures'
S = json.load(open(ROOT / 'inputs' / 'stimuli.json'))
INK, MUTED, BORDER, ACCENT, BG = '#0a0a0a', '#8a8880', '#d8d6c9', '#0034ff', '#edece8'
plt.rcParams.update({'font.family': 'Helvetica', 'axes.edgecolor': INK, 'axes.labelcolor': INK, 'xtick.color': INK,
                     'ytick.color': INK, 'figure.facecolor': BG, 'axes.facecolor': BG, 'axes.spines.top': False, 'axes.spines.right': False})
def per_trial(name, nid):
    d = pd.read_parquet(R / f'{name}.parquet'); n = json.load(open(R / f'{name}.json'))['n_trials']
    return d[d.neuron_id == nid].set_index('trial').n_spikes.reindex(range(n), fill_value=0).values
mn = S['malecns']['mn9']
# Fig 1: MN9 per trial, real vs shuffled, both flies
fig, ax = plt.subplots(figsize=(7, 3.6))
groups = [('Female (FlyWire)\nreal wiring', per_trial('E1_fw630_shiu_real', S['flywire630']['mn9_contra']), INK),
          ('Female\nshuffled', per_trial('E2_fw630_shiu_shuffled', S['flywire630']['mn9_contra']), MUTED),
          ('Male (MaleCNS)\nreal wiring', per_trial('E3_mcns_typesetL_real', mn['R']), ACCENT),
          ('Male\nshuffled', per_trial('E4_mcns_typesetL_shuffled', mn['R']), MUTED)]
rng = np.random.default_rng(0)
for i, (lab, v, c) in enumerate(groups):
    ax.scatter(i + rng.uniform(-0.18, 0.18, len(v)), v, s=10, color=c, alpha=0.8, linewidths=0)
    ax.text(i, max(v.max(), 5) + 6, f'{(v > 0).sum()}/{len(v)} trials', ha='center', fontsize=9, color=INK)
ax.set_xticks(range(4)); ax.set_xticklabels([g[0] for g in groups], fontsize=9)
ax.set_ylabel('MN9 spikes per 1 s trial (opposite side)'); ax.set_ylim(-4, 95)
ax.set_title('Sugar-taste input to feeding motor neuron MN9, 100 Hz', fontsize=11, loc='left')
fig.tight_layout(); fig.savefig(F / 'fig1_mn9_real_vs_shuffled.png', dpi=200); plt.close(fig)
# Fig 2: activity spread
ex = json.load(open(R / 'exploratory.json'))
names = [('Female', ex['X1_spread']['E3_fw783_typeset_real']['neurons_firing_mean_per_trial'], INK),
         ('Male, default weights', ex['X1_spread']['E3_mcns_typesetL_real']['neurons_firing_mean_per_trial'], ACCENT),
         ('Male, weights × 0.52\n(exploratory)', ex['X4_wscaled']['neurons_firing_mean_per_trial'], MUTED)]
fig, ax = plt.subplots(figsize=(7, 3.2))
ax.barh(range(3), [n[1] for n in names], color=[n[2] for n in names])
for i, n in enumerate(names): ax.text(n[1] * 1.15, i, f'{n[1]:,.0f}', va='center', fontsize=9)
ax.set_xscale('log'); ax.set_yticks(range(3)); ax.set_yticklabels([n[0] for n in names], fontsize=9); ax.invert_yaxis()
ax.set_xlabel('Neurons firing per trial (mean, log scale)')
ax.set_title('Same stimulus, how far does activity spread?', fontsize=11, loc='left')
fig.tight_layout(); fig.savefig(F / 'fig2_activity_spread.png', dpi=200); plt.close(fig)
# Fig 3: MN9 left/right
lat = ex['X2_laterality']
rows = [('Female, left input', lat['fw783_typeset(left GRNs)']['MN9_ipsi'], lat['fw783_typeset(left GRNs)']['MN9_contra']),
        ('Male, left input', lat['mcns_typesetL']['MN9_L(ipsi)'], lat['mcns_typesetL']['MN9_R(contra)']),
        ('Male, right input', lat['mcns_typesetR']['MN9_R(ipsi)'], lat['mcns_typesetR']['MN9_L(contra)'])]
fig, ax = plt.subplots(figsize=(7, 3.2)); x = np.arange(3)
ax.bar(x - 0.18, [r[1] for r in rows], 0.36, color=MUTED, label='same-side MN9')
ax.bar(x + 0.18, [r[2] for r in rows], 0.36, color=INK, label='opposite-side MN9')
ax.set_xticks(x); ax.set_xticklabels([r[0] for r in rows], fontsize=9); ax.set_ylabel('MN9 rate (Hz)')
ax.legend(frameon=False, fontsize=9); ax.set_title('Which MN9 fires? (exploratory)', fontsize=11, loc='left')
fig.tight_layout(); fig.savefig(F / 'fig3_mn9_sides.png', dpi=200); plt.close(fig)
print('ok', sorted(p.name for p in F.iterdir()))
