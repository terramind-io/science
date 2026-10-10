"""PLAN5: does the wiring map carry a male's song to the female's acceptance neurons? Pre-specified in PLAN5.md (commit 3a7ca53).
Writes results/plan5/song.json."""
import json
from pathlib import Path
import numpy as np, pandas as pd
from scipy import sparse
from scipy.stats import rankdata
ROOT = Path(__file__).resolve().parents[1]; V = ROOT / 'vendor/Drosophila_brain_model'; OUT = ROOT / 'results/plan5'; OUT.mkdir(parents=True, exist_ok=True)
c = pd.read_csv(V / 'Completeness_783.csv', index_col=0); e = pd.read_parquet(V / 'Connectivity_783.parquet'); ids = c.index.values; n = len(ids)
W = sparse.csr_matrix((e['Excitatory x Connectivity'].values.astype(float), (e['Postsynaptic_Index'].values, e['Presynaptic_Index'].values)), shape=(n, n))
ann = pd.read_csv(ROOT / 'data/flywire/neuron_annotations.tsv', sep='\t', low_memory=False).drop_duplicates('root_id').set_index('root_id').reindex(ids)
meta = json.load(open(ROOT.parent / 'playground/public/data/fw783/meta.json'))
hear = np.where(ann.cell_sub_class.values == 'auditory')[0]; en = np.where(ann.hemibrain_type.values == 'vpoEN')[0]; dn = np.where(ann.hemibrain_type.values == 'vpoDN')[0]
touch = np.array(sorted(set(meta['actions']['antenna']['idx']) - set(hear.tolist()))); sugar = np.array(meta['presets']['sugar_paper21']['idx'])
def run(src, kmax=5):
    x = np.zeros(n); x[src] = 1; cum = np.zeros(n); out = {}; mask = np.ones(n, bool); mask[src] = False
    for k in range(1, kmax + 1):
        x = np.maximum(W @ x, 0); cum = cum + x
        pct = np.full(n, np.nan); pct[mask] = 100 * (rankdata(cum[mask], method='average') - 1) / (mask.sum() - 1)
        out[k] = {'n_positive': int((cum[mask] > 0).sum()), 'vpoEN_pct': [round(float(v), 2) for v in pct[en]], 'vpoDN_pct': [round(float(v), 2) for v in pct[dn]],
                  'vpoEN_mean_pct': round(float(np.mean(pct[en])), 2), 'vpoDN_mean_pct': round(float(np.mean(pct[dn])), 2),
                  'vpoEN_value': [float(v) for v in cum[en]], 'vpoDN_value': [float(v) for v in cum[dn]], 'vpoEN_step_value': [float(v) for v in x[en]], 'vpoDN_step_value': [float(v) for v in x[dn]]}
    first = lambda key: next((k for k in out if any(v > 0 for v in out[k][key])), None)
    return {'n_source': int(len(src)), 'first_step_vpoEN': first('vpoEN_value'), 'first_step_vpoDN': first('vpoDN_value'), 'by_k': out}
R = {name: run(src) for name, src in (('hearing', hear), ('touch_control', touch), ('sugar_control', sugar))}
h = R['hearing']['by_k']; pe, pd_ = h[3]['vpoEN_mean_pct'], h[4]['vpoDN_mean_pct']
L1 = 'supported' if pe >= 90 and pd_ >= 90 else 'not supported' if pe < 50 or pd_ < 50 else 'inconclusive'
ce = {k: R[k]['by_k'][3]['vpoEN_mean_pct'] for k in ('touch_control', 'sugar_control')}; cd = {k: R[k]['by_k'][4]['vpoDN_mean_pct'] for k in ('touch_control', 'sugar_control')}
L2 = 'supported' if all(pe > v for v in ce.values()) and all(pd_ > v for v in cd.values()) else 'not supported' if any(ce[k] > pe and cd[k] > pd_ for k in ce) else 'inconclusive'
res = {'sets': {'hearing': int(len(hear)), 'vpoEN': int(len(en)), 'vpoDN': int(len(dn)), 'touch_control': int(len(touch)), 'touch_removed_overlap': int(len(meta['actions']['antenna']['idx']) - len(touch)), 'sugar_control': int(len(sugar)), 'n_neurons': n},
       'direct_hearing_to_vpoEN_connections': int((W[en][:, hear] != 0).sum()), 'direct_vpoEN_to_vpoDN_connections': int((W[dn][:, en] != 0).sum()), 'direct_vpoEN_to_vpoDN_weight': float(W[dn][:, en].sum()),
       'L1': {'vpoEN_mean_pct_k3': pe, 'vpoDN_mean_pct_k4': pd_, 'verdict': L1}, 'L2': {'vpoEN_k3_controls': ce, 'vpoDN_k4_controls': cd, 'verdict': L2}, 'runs': R}
json.dump(res, open(OUT / 'song.json', 'w'), indent=1)
print(json.dumps({k: res[k] for k in ('sets', 'direct_hearing_to_vpoEN_connections', 'direct_vpoEN_to_vpoDN_connections', 'direct_vpoEN_to_vpoDN_weight', 'L1', 'L2')}, indent=1))
for name in R:
    print(name, 'first EN/DN step', R[name]['first_step_vpoEN'], R[name]['first_step_vpoDN'], {k: (v['n_positive'], v['vpoEN_mean_pct'], v['vpoDN_mean_pct']) for k, v in R[name]['by_k'].items()})
print('hearing EN values by k', {k: v['vpoEN_value'] for k, v in h.items()}); print('hearing DN values by k', {k: v['vpoDN_value'] for k, v in h.items()})
