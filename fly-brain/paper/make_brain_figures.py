"""Preview brain figures for the paper (not yet in the paper). Everything drawn is computed here from the FlyWire v783 model
network (Shiu's Completeness_783.csv + Connectivity_783.parquet), FlyWire annotation positions, and inputs/sez_screen.json.
Run: ../experiment/.venv/bin/python make_brain_figures.py [cell_type]"""
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
from scipy import sparse
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
ROOT = Path(__file__).resolve().parent; EXP = ROOT.parent / 'experiment'; V = EXP / 'vendor/Drosophila_brain_model'
OUT = ROOT / 'final/figures_preview'; OUT.mkdir(parents=True, exist_ok=True)
TYPE = sys.argv[1] if len(sys.argv) > 1 else 'Fdg'; MN9 = 720575940660219265
INK, ACC, MUTED, DOT, WARM = '#0a0a0a', '#0034ff', '#7d7a72', '#c9c7c0', '#d9480f'
plt.rcParams.update({'font.family': 'STIX Two Text', 'font.size': 9, 'savefig.dpi': 300, 'savefig.bbox': 'tight', 'figure.facecolor': 'white'})

c = pd.read_csv(V / 'Completeness_783.csv', index_col=0); e = pd.read_parquet(V / 'Connectivity_783.parquet')
ids = c.index.values; idx = {k: i for i, k in enumerate(ids)}; n = len(ids)
W = sparse.csr_matrix((e['Excitatory x Connectivity'].values.astype(float), (e['Postsynaptic_Index'].values, e['Presynaptic_Index'].values)), shape=(n, n))
ann = pd.read_csv(EXP / 'data/flywire/neuron_annotations.tsv', sep='\t', low_memory=False).drop_duplicates('root_id').set_index('root_id').reindex(ids)
X = ann.pos_x.values * 4 / 1000; Y = ann.pos_y.values * 4 / 1000; has = ~np.isnan(X)   # micrometres, frontal view
SEZ = json.load(open(EXP / 'inputs/sez_screen.json')); src = [idx[i] for i in SEZ[TYPE]['female783_typed_ids'] if i in idx]; m = idx[MN9]
x0 = np.zeros(n); x0[src] = 1
x1 = np.maximum(W @ x0, 0); x2 = np.maximum(W @ x1, 0); x3 = np.maximum(W @ x2, 0)
wm = np.asarray(W[m].todense()).ravel()               # weight of each neuron's direct connection onto MN9
score = x1[m] + x2[m] + x3[m]
r2 = np.where((x1 > 0) & (wm > 0))[0]                 # neurons that receive from the type and excite MN9 directly: two-step routes
r3 = np.where((x2 > 0) & (wm > 0))[0]                 # neurons delivering excitation to MN9 at step three
info = {'type': TYPE, 'n_source': len(src), 'n_with_position': int(has.sum()), 'n_neurons': n, 'arrive_step1': float(x1[m]), 'arrive_step2': float(x2[m]), 'arrive_step3': float(x3[m]),
        'path_score': float(score), 'n_active_after': [int((x1 > 0).sum()), int((x2 > 0).sum()), int((x3 > 0).sum())], 'n_two_step_relays': len(r2), 'n_step3_deliverers': len(r3),
        'source_have_pos': int(has[src].sum()), 'mn9_has_pos': bool(has[m]), 'relays_have_pos': int(has[r2].sum())}
json.dump(info, open(OUT / f'brain_{TYPE}.json', 'w'), indent=1); print(info)

def cloud(ax, s=0.25, col=DOT, a=0.55):
    ax.scatter(X[has], Y[has], s=s, color=col, alpha=a, lw=0, rasterized=True); ax.invert_yaxis(); ax.set_aspect('equal'); ax.axis('off')

# ---- Preview A: the map, the cell type, the two-step routes and MN9
fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 2.35), gridspec_kw={'width_ratios': [1.25, 1], 'wspace': 0.03})
cloud(a)
segs = [[(X[s_], Y[s_]), (X[r], Y[r])] for r in r2 if has[r] for s_ in src if W[r, s_] > 0 and has[s_]] + [[(X[r], Y[r]), (X[m], Y[m])] for r in r2 if has[r]]
for ax in (a, b):
    ax.add_collection(LineCollection(segs, colors=INK, lw=0.35 if ax is a else 0.5, alpha=0.5, zorder=3))
    ax.scatter(X[r2], Y[r2], s=7 if ax is a else 16, color=INK, lw=0, zorder=4, label=f'relay neurons ({len(r2)})')
    ax.scatter(X[src], Y[src], s=26 if ax is a else 60, color=WARM, lw=0, zorder=5, label=f'{TYPE} ({len(src)} neurons)')
    ax.scatter([X[m]], [Y[m]], s=30 if ax is a else 70, color=ACC, lw=0, zorder=6, label='MN9, the feeding motor neuron')
pts = np.array([[X[i], Y[i]] for i in list(r2) + src + [m] if has[i]]); pad = 14
cloud(b, s=1.2, a=0.7); b.set_xlim(pts[:, 0].min() - pad, pts[:, 0].max() + pad); b.set_ylim(pts[:, 1].max() + pad, pts[:, 1].min() - pad)
x_, y_ = b.get_xlim(), b.get_ylim(); a.plot([x_[0], x_[1], x_[1], x_[0], x_[0]], [y_[0], y_[0], y_[1], y_[1], y_[0]], color=MUTED, lw=0.6)
a.plot([X[has].min(), X[has].min() + 100], [Y[has].max() + 8] * 2, color=INK, lw=1); a.text(X[has].min() + 50, Y[has].max() + 14, '100 µm', ha='center', va='top', fontsize=7.5)
h, l = b.get_legend_handles_labels(); fig.legend(h[::-1], l[::-1], frameon=False, loc='lower center', ncol=3, fontsize=8, bbox_to_anchor=(0.5, -0.02), handletextpad=0.2, columnspacing=1.4)
fig.text(0.13, 0.86, '(a)', fontsize=10); fig.text(0.56, 0.86, '(b)', fontsize=10)
fig.savefig(OUT / f'previewA_routes_{TYPE}.png'); plt.close(fig)

# ---- Preview B: how far the map-only signal has spread after each step
fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.25), gridspec_kw={'wspace': 0.02})
for k, (ax, x) in enumerate(zip(axs, (x1, x2, x3)), 1):
    cloud(ax, s=0.12, a=0.5); on = np.where((x > 0) & has)[0]; v = np.log10(1 + x[on]); o = np.argsort(v)
    ax.scatter(X[on][o], Y[on][o], s=0.5 + 2.2 * v[o] / v.max(), c=v[o], cmap='Blues', vmin=-0.35 * v.max(), vmax=v.max(), lw=0, rasterized=True, zorder=3)
    ax.scatter(X[src], Y[src], s=14, color=WARM, lw=0, zorder=5); ax.scatter([X[m]], [Y[m]], s=22, facecolors='none', edgecolors=INK, lw=0.9, zorder=6)
    ax.set_title(f'after step {k}: {int((x > 0).sum()):,} neurons', fontsize=8.5, pad=2)
fig.savefig(OUT / f'previewB_spread_{TYPE}.png'); plt.close(fig)
