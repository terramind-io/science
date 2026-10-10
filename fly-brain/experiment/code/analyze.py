"""Evaluate the pre-registered hypotheses in PLAN.md from results/*.parquet. Writes results/summary.json."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import fisher_exact, spearmanr

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / 'results'
S = json.load(open(ROOT / 'inputs' / 'stimuli.json'))
V = ROOT / 'vendor' / 'Drosophila_brain_model'
MN9 = {'fw630': S['flywire630']['mn9_contra'], 'fw783': S['flywire783']['mn9_contra'],
       'mcnsL': S['malecns']['mn9']['R'], 'mcnsR': S['malecns']['mn9']['L']}


def load(name):
    p = R / f'{name}.parquet'
    if not p.exists():
        return None, None
    return pd.read_parquet(p), json.load(open(p.with_suffix('.json')))


def mn9_stats(df, meta, nid):
    per = df[df.neuron_id == nid].set_index('trial').n_spikes.reindex(range(meta['n_trials']), fill_value=0)
    return {'active_trials': int((per > 0).sum()), 'n_trials': meta['n_trials'],
            'rate_mean_hz': round(float(per.mean()), 2), 'rate_sd_hz': round(float(per.std(ddof=0)), 2),
            'per_trial': per.tolist()}


def verdict(sup, nsup):
    return 'supported' if sup else ('not supported' if nsup else 'inconclusive')


def type_rates(df, meta, types, stim):
    m = df[~df.neuron_id.isin(stim)].groupby('neuron_id').n_spikes.sum() / meta['n_trials']
    t = types.reindex(m.index).dropna()
    return m.loc[t.index].groupby(t.values).mean()


out = {}
# H1
e1, m1 = load('E1_fw630_shiu_real')
if e1 is not None:
    s = mn9_stats(e1, m1, MN9['fw630'])
    arch = pd.read_parquet(V / 'results' / 'example' / 'sugarR_100Hz.parquet')
    a_tr = arch.trial.max() + 1
    a = arch[arch.flywire_id == MN9['fw630']].groupby('trial').size().reindex(range(a_tr), fill_value=0)
    s['archived_rate_mean_hz'] = round(float(a.mean()), 2)
    s['archived_active_trials'] = f'{int((a > 0).sum())}/{a_tr}'
    rel = abs(s['rate_mean_hz'] - a.mean()) / a.mean()
    s['rel_diff_vs_archived'] = round(float(rel), 3)
    s['verdict'] = verdict(s['active_trials'] >= 29 and rel <= 0.25, s['active_trials'] <= 15)
    out['H1'] = s
# H2
e2, m2 = load('E2_fw630_shiu_shuffled')
if e2 is not None and e1 is not None:
    s = mn9_stats(e2, m2, MN9['fw630'])
    p = fisher_exact([[out['H1']['active_trials'], 30 - out['H1']['active_trials']], [s['active_trials'], 100 - s['active_trials']]])[1]
    s['fisher_p_vs_E1'] = float(p)
    s['verdict'] = verdict(s['active_trials'] <= 5 and p < 1e-3, s['active_trials'] >= 20)
    out['H2'] = s
# H3, H4
e3b, m3b = load('E3_mcns_typesetL_real')
if e3b is not None:
    s = mn9_stats(e3b, m3b, MN9['mcnsL'])
    s['ipsilateral'] = {k: v for k, v in mn9_stats(e3b, m3b, MN9['mcnsR']).items() if k != 'per_trial'}
    s['verdict'] = 'supported' if s['active_trials'] >= 27 else ('not supported' if s['active_trials'] <= 3 else 'partial')
    out['H3'] = s
e4, m4 = load('E4_mcns_typesetL_shuffled')
if e4 is not None and e3b is not None:
    s = mn9_stats(e4, m4, MN9['mcnsL'])
    p = fisher_exact([[out['H3']['active_trials'], 30 - out['H3']['active_trials']], [s['active_trials'], 100 - s['active_trials']]])[1]
    s['fisher_p_vs_E3b'] = float(p)
    s['verdict'] = verdict(s['active_trials'] <= 5 and p < 1e-3, s['active_trials'] >= 20)
    out['H4'] = s
# D1
e3a, m3a = load('E3_fw783_typeset_real')
if e3a is not None and e3b is not None and e4 is not None:
    fw = pd.read_csv(ROOT / 'data' / 'flywire' / 'neuron_annotations.tsv', sep='\t', usecols=['root_id', 'cell_type'], low_memory=False)
    fwt = fw.dropna().set_index('root_id').cell_type
    mc = pd.read_csv(ROOT / 'inputs' / 'malecns_neurons.csv', usecols=['bodyId', 'flywireType']).dropna().set_index('bodyId').flywireType
    shared = set(fwt.unique()) & set(mc.unique())
    fa = type_rates(e3a, m3a, fwt, S['flywire783']['stim_typeset'])
    mb = type_rates(e3b, m3b, mc, S['malecns']['stim_typeset_L'])
    ms = type_rates(e4, m4, mc, S['malecns']['stim_typeset_L'])

    def comp(x, y):
        keys = sorted(t for t in shared if x.get(t, 0) > 0 or y.get(t, 0) > 0)
        xv = np.array([x.get(t, 0) for t in keys]); yv = np.array([y.get(t, 0) for t in keys])
        top = lambda s: set(s[s.index.isin(shared)].sort_values(ascending=False).index[:50])
        j = len(top(x) & top(y)) / len(top(x) | top(y))
        return {'n_types': len(keys), 'spearman_rho': round(float(spearmanr(xv, yv)[0]), 3), 'top50_jaccard': round(j, 3)}
    real, shuf = comp(fa, mb), comp(fa, ms)
    d = real['spearman_rho'] - shuf['spearman_rho']
    out['D1'] = {'real_vs_real': real, 'real_vs_shuffled': shuf, 'rho_difference': round(d, 3),
                 'verdict': 'supported' if d >= 0.2 else ('not supported' if d <= 0 else 'weak')}
    out['D1']['top20_types_female'] = fa[fa.index.isin(shared)].sort_values(ascending=False).head(20).round(2).to_dict()
    out['D1']['top20_types_male'] = mb[mb.index.isin(shared)].sort_values(ascending=False).head(20).round(2).to_dict()
# secondary
sec = {}
for name, key in [('E3_fw783_typeset_real', 'fw783'), ('S1_fw783_sugaronly_real', 'fw783'),
                  ('S1_mcns_sugaronlyL_real', 'mcnsL'), ('S2_mcns_typesetR_real', 'mcnsR')]:
    d_, m_ = load(name)
    if d_ is not None:
        s = mn9_stats(d_, m_, MN9[key]); s.pop('per_trial'); sec[name] = s
out['secondary'] = sec
json.dump(out, open(R / 'summary.json', 'w'), indent=1)
print(json.dumps({k: (v if k == 'secondary' else {kk: vv for kk, vv in v.items() if kk not in ('per_trial', 'top20_types_female', 'top20_types_male')}) for k, v in out.items()}, indent=1))
