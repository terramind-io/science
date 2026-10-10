"""PLAN4 Amendment B: map-only path score for courtship song on the male CNS. Writes results/plan4/courtship.json.
After the audit: the unscored pC1_2a,2b case uses exact names (a prefix had also matched a composite type), and exploratory fragility figures are recorded."""
import json
from pathlib import Path
import numpy as np, pandas as pd
from scipy import sparse
from scipy.stats import mannwhitneyu
ROOT = Path(__file__).resolve().parents[1]; I = ROOT / 'inputs'; OUT = ROOT / 'results' / 'plan4'; OUT.mkdir(parents=True, exist_ok=True)
comp = pd.read_csv(I / 'malecns_completeness.csv', index_col=0); e = pd.read_parquet(I / 'malecns_connectivity.parquet')
idx = {int(k): i for i, k in enumerate(comp.index)}; n = len(idx)
rows, cols, w = e['Postsynaptic_Index'].values, e['Presynaptic_Index'].values, e['Excitatory x Connectivity'].values.astype(float)
W = sparse.csr_matrix((w, (rows, cols)), shape=(n, n))
ann = pd.read_csv(I / 'malecns_neurons.csv'); ann['type'] = ann['type'].astype(str)
def ids(exact=(), prefix=()):
    m = ann['type'].isin(exact) | ann['type'].map(lambda t: any(str(t).startswith(p) for p in prefix))
    return [idx[int(b)] for b in ann.loc[m, 'bodyId'] if int(b) in idx], ann.loc[m]
MN = ['hg1 MN', 'hg2 MN', 'hg3 MN', 'hg4 MN', 'i1 MN', 'i2 MN', 'b3 MN', 'ps1 MN', 'tp1 MN', 'tp2 MN', 'tpn MN', 'MNwm35']
ro, _ = ids(exact=MN)
CASES = [('TN1a', 'YES', 'primary', dict(prefix=['TN1a_'])), ('dMS2', 'YES', 'primary', dict(exact=['dMS2'])), ('dMS9', 'YES', 'primary', dict(exact=['dMS9'])),
         ('P1a (pC1_4a,4b,12b)', 'YES', 'primary', dict(exact=['pC1_4a', 'pC1_4b', 'pC1_12b'])), ('pC1_13a,14a,14b', 'YES', 'primary', dict(exact=['pC1_13a', 'pC1_14a', 'pC1_14b'])),
         ('pC1_17a,17b', 'YES', 'primary', dict(exact=['pC1_17a', 'pC1_17b'])), ('pC1_19', 'YES', 'primary', dict(exact=['pC1_19'])),
         ('pC1x_a,b,d', 'NO', 'primary', dict(exact=['pC1x_a', 'pC1x_b', 'pC1x_d'])), ('pC1_10b,c,d', 'NO', 'primary', dict(exact=['pC1_10b', 'pC1_10c', 'pC1_10d'])),
         ('mAL', 'NO', 'primary', dict(prefix=['mAL'])), ('vPR9', 'NO', 'primary', dict(prefix=['vPR9_'])),
         ('MDN', 'NO', 'indirect', dict(exact=['MDN'])), ('DNg07,DNg08', 'NO', 'indirect', dict(exact=['DNg07', 'DNg08'])), ('DNa01,DNa02', 'NO', 'indirect', dict(exact=['DNa01', 'DNa02'])),
         ('DNp29,DNg10,DNg13', 'NO', 'indirect', dict(exact=['DNp29', 'DNg10', 'DNg13'])), ('LC16', 'NO', 'indirect', dict(exact=['LC16'])),
         ('pIP10', 'control', 'control', dict(exact=['pIP10'])), ('pMP2', 'control', 'control', dict(exact=['pMP2'])), ('dPR1', 'control', 'control', dict(exact=['dPR1'])),
         ('vPR6', 'mixed', 'unscored', dict(exact=['vPR6'])), ('vMS12', 'mixed', 'unscored', dict(prefix=['vMS12'])), ('pC1_1a', 'mixed', 'unscored', dict(exact=['pC1_1a'])),
         ('pC1_2a,2b', 'mixed', 'unscored', dict(exact=['pC1_2a', 'pC1_2b'])), ('pC1_15a,b,c', 'mixed', 'unscored', dict(exact=['pC1_15a', 'pC1_15b', 'pC1_15c'])), ('LC10', 'mixed', 'unscored', dict(prefix=['LC10']))]
def score(Wm, src, hops):
    x = np.zeros(n); x[src] = 1; tot = 0.0
    for _ in range(hops): x = np.maximum(Wm @ x, 0); tot += x[ro].sum()
    return float(tot)
def auroc(s, l):
    s = np.asarray(s, float); l = np.asarray(l, bool); return float(mannwhitneyu(s[l], s[~l]).statistic / (l.sum() * (~l).sum()))
tab = []
for name, truth, tier, sel in CASES:
    src, a = ids(**sel); tab.append({'case': name, 'truth': truth, 'tier': tier, 'n_neurons': len(src), 'frac_inhibitory': round(float((a['sign'] < 0).mean()), 2) if len(a) else None,
                                     **{f'score_{h}': score(W, src, h) for h in (3, 4, 5)}})
T = pd.DataFrame(tab); T.to_csv(OUT / 'courtship_cases.csv', index=False)
P = T[T.tier == 'primary']; A = T[T.tier.isin(['primary', 'indirect'])]
out = {'n_readout_neurons': len(ro), 'primary': {'n_yes': int((P.truth == 'YES').sum()), 'n_no': int((P.truth == 'NO').sum())}, 'all': {'n_yes': int((A.truth == 'YES').sum()), 'n_no': int((A.truth == 'NO').sum())}}
for h in (3, 4, 5):
    out[f'auroc_{h}steps'] = {'primary': round(auroc(P[f'score_{h}'], P.truth == 'YES'), 3), 'all16': round(auroc(A[f'score_{h}'], A.truth == 'YES'), 3)}
a4 = out['auroc_4steps']; out['K1'] = 'supported' if a4['primary'] >= 0.80 and a4['all16'] >= 0.75 else ('not supported' if a4['primary'] <= 0.60 else 'inconclusive')
# mAL restricted to inhibitory neurons (sensitivity)
src_inh = [idx[int(b)] for b in ann.loc[ann['type'].str.startswith('mAL') & (ann['sign'] < 0), 'bodyId'] if int(b) in idx]
P2 = P.copy(); P2.loc[P2.case == 'mAL', 'score_4'] = score(W, src_inh, 4); out['sensitivity_mAL_inhibitory_only'] = {'n_neurons': len(src_inh), 'mAL_score_4': float(P2.loc[P2.case == 'mAL', 'score_4'].iloc[0]), 'auroc_primary': round(auroc(P2['score_4'], P2.truth == 'YES'), 3)}
# scrambled signed weights across existing connections (20 scrambles)
sh = []
srcs = {r.case: ids(**dict(CASES)[r.case] if False else next(c[3] for c in CASES if c[0] == r.case))[0] for r in A.itertuples()}
for s in range(20):
    Ws = sparse.csr_matrix((np.random.default_rng(9000 + s).permutation(w), (rows, cols)), shape=(n, n))
    sc = {c: score(Ws, src, 4) for c, src in srcs.items()}
    sh.append({'primary': auroc([sc[c] for c in P.case], P.truth == 'YES'), 'all16': auroc([sc[c] for c in A.case], A.truth == 'YES')})
S = pd.DataFrame(sh); out['scrambled_4steps'] = {k: {'mean': round(float(S[k].mean()), 3), 'min': round(float(S[k].min()), 3), 'max': round(float(S[k].max()), 3), 'n_at_or_above_real': int((S[k] >= a4[k]).sum())} for k in ('primary', 'all16')}
# exploratory, added after the audit: fragility figures
yes = P[P.truth == 'YES'].score_4.values; no = P[P.truth == 'NO'].score_4.values
out['exploratory_after_audit'] = {'pairs_correct': int(sum(y > x for y in yes for x in no)), 'pairs_total': int(len(yes) * len(no)),
    'primary_without_inhibitory_types': round(auroc(P[~P.case.isin(['mAL', 'vPR9'])].score_4, P[~P.case.isin(['mAL', 'vPR9'])].truth == 'YES'), 3),
    'primary_plus_three_mixed_P1_as_NO': round(auroc(list(P.score_4) + list(T[T.case.isin(['pC1_1a', 'pC1_2a,2b', 'pC1_15a,b,c'])].score_4), list(P.truth == 'YES') + [False] * 3), 3),
    'per_neuron': {'primary': round(auroc(P.score_4 / P.n_neurons, P.truth == 'YES'), 3), 'all16': round(auroc(A.score_4 / A.n_neurons, A.truth == 'YES'), 3)},
    'leave_one_out_primary': [round(float(min(v)), 3), round(float(max(v)), 3)] if (v := [auroc(P.drop(i).score_4, P.drop(i).truth == 'YES') for i in P.index]) else None}
json.dump(out, open(OUT / 'courtship.json', 'w'), indent=1); print(T.to_string()); print(json.dumps(out, indent=1))
