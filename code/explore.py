"""EXPLORATORY (post-hoc, not pre-registered): activity spread, MN9 laterality, sign-rule inputs."""
import json
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]; R = ROOT / 'results'
S = json.load(open(ROOT / 'inputs' / 'stimuli.json'))
out = {}
def rates(name):
    d = pd.read_parquet(R / f'{name}.parquet'); n = json.load(open(R / f'{name}.json'))['n_trials']
    return d.groupby('neuron_id').n_spikes.sum() / n, d, n
# X1 activity spread
for name in ['E1_fw630_shiu_real', 'E3_fw783_typeset_real', 'E3_mcns_typesetL_real', 'S1_mcns_sugaronlyL_real', 'E4_mcns_typesetL_shuffled', 'E2_fw630_shiu_shuffled']:
    r, d, n = rates(name)
    out.setdefault('X1_spread', {})[name] = {'neurons_firing_mean_per_trial': round(d.groupby('trial').size().mean(), 1),
        'neurons_ge_10hz': int((r >= 10).sum()), 'total_spikes_per_trial': round(d.n_spikes.sum() / n, 1)}
# X2 laterality
def mn9(name, nid):
    r, _, _ = rates(name); return round(float(r.get(nid, 0.0)), 2)
f = S['flywire783']; m = S['malecns']['mn9']
out['X2_laterality'] = {
    'fw783_typeset(left GRNs)': {'MN9_contra': mn9('E3_fw783_typeset_real', f['mn9_contra']), 'MN9_ipsi': mn9('E3_fw783_typeset_real', f['mn9_ipsi'])},
    'fw783_sugaronly(left GRNs)': {'MN9_contra': mn9('S1_fw783_sugaronly_real', f['mn9_contra']), 'MN9_ipsi': mn9('S1_fw783_sugaronly_real', f['mn9_ipsi'])},
    'mcns_typesetL': {'MN9_R(contra)': mn9('E3_mcns_typesetL_real', m['R']), 'MN9_L(ipsi)': mn9('E3_mcns_typesetL_real', m['L'])},
    'mcns_typesetR': {'MN9_L(contra)': mn9('S2_mcns_typesetR_real', m['L']), 'MN9_R(ipsi)': mn9('S2_mcns_typesetR_real', m['R'])},
    'mcns_sugaronlyL': {'MN9_R(contra)': mn9('S1_mcns_sugaronlyL_real', m['R']), 'MN9_L(ipsi)': mn9('S1_mcns_sugaronlyL_real', m['L'])},
}
# X3 model-construction differences
mc = pd.read_csv(ROOT / 'inputs' / 'malecns_neurons.csv')
out['X3_male_inputs'] = {'n_neurons': len(mc), 'predicted_nt_missing_frac': round(float(mc.predicted_nt.isna().mean()), 4),
    'nt_counts': mc.predicted_nt.value_counts(dropna=False).to_dict(), 'inhibitory_neuron_frac': round(float((mc.sign < 0).mean()), 4)}
fwc = pd.read_parquet(ROOT / 'vendor/Drosophila_brain_model/Connectivity_783.parquet', columns=['Presynaptic_ID', 'Excitatory', 'Connectivity'])
mcc = pd.read_parquet(ROOT / 'inputs/malecns_connectivity.parquet', columns=['Presynaptic_ID', 'Excitatory', 'Connectivity'])
for k, c in [('fw783', fwc), ('mcns', mcc)]:
    out.setdefault('X3_network', {})[k] = {'edges': len(c), 'synapses_total': int(c.Connectivity.sum()),
        'inhibitory_neuron_frac': round(float((c.groupby('Presynaptic_ID').Excitatory.first() < 0).mean()), 4),
        'inhibitory_synapse_frac': round(float(c.Connectivity[c.Excitatory < 0].sum() / c.Connectivity.sum()), 4)}

# X4 (exploratory): male CNS with w_syn x (FlyWire/male synapses per neuron)
from scipy.stats import spearmanr
if (R / 'X4_mcns_typesetL_wscaled.parquet').exists():
    rx, dx, kx = rates('X4_mcns_typesetL_wscaled')
    mm = S['malecns']['mn9']
    per = lambda nid: dx[dx.neuron_id == nid].set_index('trial').n_spikes.reindex(range(kx), fill_value=0)
    r_, l_ = per(mm['R']), per(mm['L'])
    fwt = pd.read_csv(ROOT / 'data' / 'flywire' / 'neuron_annotations.tsv', sep='\t', usecols=['root_id', 'cell_type'], low_memory=False).dropna().set_index('root_id').cell_type
    mct = mc[['bodyId', 'flywireType']].dropna().set_index('bodyId').flywireType
    shared = set(fwt.unique()) & set(mct.unique())
    def tr(name, types, stim):
        rr, _, _ = rates(name); rr = rr[~rr.index.isin(stim)]; tt = types.reindex(rr.index).dropna()
        return rr.loc[tt.index].groupby(tt.values).mean()
    fa = tr('E3_fw783_typeset_real', fwt, S['flywire783']['stim_typeset']); mb = tr('X4_mcns_typesetL_wscaled', mct, S['malecns']['stim_typeset_L'])
    keys = sorted(t for t in shared if fa.get(t, 0) > 0 or mb.get(t, 0) > 0)
    top = lambda s: set(s[s.index.isin(shared)].sort_values(ascending=False).index[:50])
    out['X4_wscaled'] = {
        'w_syn_multiplier': json.load(open(R / 'X4_mcns_typesetL_wscaled.json'))['w_syn_multiplier'],
        'MN9_R_contra': {'active': int((r_ > 0).sum()), 'mean': round(float(r_.mean()), 2), 'sd': round(float(r_.std(ddof=0)), 2)},
        'MN9_L_ipsi': {'active': int((l_ > 0).sum()), 'mean': round(float(l_.mean()), 2)},
        'neurons_firing_mean_per_trial': round(dx.groupby('trial').size().mean(), 1),
        'total_spikes_per_trial': round(dx.n_spikes.sum() / kx, 1),
        'D1_style_vs_female': {'n_types': len(keys), 'spearman_rho': round(float(spearmanr([fa.get(t, 0) for t in keys], [mb.get(t, 0) for t in keys])[0]), 3),
                               'top50_jaccard': round(len(top(fa) & top(mb)) / len(top(fa) | top(mb)), 3)},
        'top10_male_types': mb[mb.index.isin(shared)].sort_values(ascending=False).head(10).round(1).to_dict()}
json.dump(out, open(R / 'exploratory.json', 'w'), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))

# ---- Audit additions (9 Oct, post hoc; all EXPLORATORY) ----
import numpy as np
from scipy.stats import spearmanr
ann = pd.read_feather(ROOT / 'data' / 'malecns' / 'body-annotations-male-cns-v1.0-minconf-0.5.feather')
cf = pd.read_parquet(ROOT / 'vendor/Drosophila_brain_model/Connectivity_783.parquet', columns=['Presynaptic_ID', 'Postsynaptic_ID', 'Connectivity'])
cm = pd.read_parquet(ROOT / 'inputs/malecns_connectivity.parquet', columns=['Presynaptic_ID', 'Postsynaptic_ID', 'Connectivity'])
inf, inm = cf.groupby('Postsynaptic_ID').Connectivity.sum(), cm.groupby('Postsynaptic_ID').Connectivity.sum()
outf, outm = cf.groupby('Presynaptic_ID').Connectivity.sum(), cm.groupby('Presynaptic_ID').Connectivity.sum()
fwa = pd.read_csv(ROOT / 'data/flywire/neuron_annotations.tsv', sep='\t', usecols=['root_id', 'cell_type', 'side'], low_memory=False)
# A1: MN9 reconstruction completeness
out['A1_mn9_inputs'] = {
    **{f'female_{s}_{i}': int(inf.get(i, 0)) for i, s in fwa[fwa.cell_type == 'CB0701'][['root_id', 'side']].values},
    **{f'male_{r.instance}_{r.bodyId}': {'input_synapses': int(inm.get(r.bodyId, 0)), 'statusLabel': r.statusLabel}
       for r in ann[ann.type == 'MN9'].itertuples()}}
# A2: stimulus-excluded spread
stims = {'E3_fw783_typeset_real': S['flywire783']['stim_typeset'], 'E3_mcns_typesetL_real': S['malecns']['stim_typeset_L'],
         'X4_mcns_typesetL_wscaled': S['malecns']['stim_typeset_L'], 'E1_fw630_shiu_real': S['flywire630']['stim_shiu']}
out['A2_spread_excluding_stimulated'] = {}
for name, st in stims.items():
    if (R / f'{name}.parquet').exists():
        _, d, n = rates(name); d = d[~d.neuron_id.isin(st)]
        out['A2_spread_excluding_stimulated'][name] = round(d.groupby('trial').size().reindex(range(n), fill_value=0).mean(), 1)
# A3: type-matched synaptic input per neuron, male / female
ft = fwa.dropna(subset=['cell_type']).set_index('root_id').cell_type
mt = mc.dropna(subset=['flywireType']).set_index('bodyId').flywireType
a_ = pd.DataFrame({'i': inf.reindex(ft.index).fillna(0), 'o': outf.reindex(ft.index).fillna(0), 't': ft}).groupby('t').mean()
b_ = pd.DataFrame({'i': inm.reindex(mt.index).fillna(0), 'o': outm.reindex(mt.index).fillna(0), 't': mt}).groupby('t').mean()
j = a_.join(b_, lsuffix='_f', rsuffix='_m', how='inner'); j = j[(j.i_f > 50) & (j.i_m > 50)]
lr = np.log2(j.i_m / j.i_f)
brain = set(ann[~ann.superclass.astype(str).str.startswith('vnc')].bodyId)
mb_ids = [b for b in mc.bodyId if b in brain]
out['A3_synapse_density'] = {'type_matched_n_types': int(len(j)), 'median_input_ratio_male_over_female': round(float(2 ** lr.median()), 3),
    'iqr': [round(float(2 ** q), 2) for q in lr.quantile([.25, .75])],
    'synapses_per_edge': {'fw783': round(float(cf.Connectivity.mean()), 2), 'mcns': round(float(cm.Connectivity.mean()), 2)},
    'input_synapses_per_neuron_all': {'fw783': round(float(cf.Connectivity.sum() / len(pd.read_csv(ROOT / 'vendor/Drosophila_brain_model/Completeness_783.csv'))), 1),
                                      'mcns': round(float(cm.Connectivity.sum() / len(mc)), 1)},
    'mcns_brain_only_input_per_neuron': round(float(inm.reindex(mb_ids).fillna(0).sum() / len(mb_ids)), 1)}
# A4: X4 vs real on a FIXED type set (types active in the female condition)
def trates(name, types, st):
    rr, _, _ = rates(name); rr = rr[~rr.index.isin(st)]; tt = types.reindex(rr.index).dropna(); return rr.loc[tt.index].groupby(tt.values).mean()
shared = set(ft.unique()) & set(mt.unique())
fa = trates('E3_fw783_typeset_real', ft, S['flywire783']['stim_typeset'])
keys = sorted(t for t in shared if fa.get(t, 0) > 0)
res = {}
for name in ['E3_mcns_typesetL_real', 'X4_mcns_typesetL_wscaled', 'E4_mcns_typesetL_shuffled']:
    mb = trates(name, mt, S['malecns']['stim_typeset_L'])
    res[name] = round(float(spearmanr([fa.get(t, 0) for t in keys], [mb.get(t, 0) for t in keys])[0]), 3)
out['A4_rho_on_female_active_types'] = {'n_types': len(keys), **res}
json.dump(out, open(R / 'exploratory.json', 'w'), indent=1, default=str)
print(json.dumps({k: out[k] for k in out if k.startswith('A')}, indent=1, default=str))
# A5: well-traced male MN9_L as readout (real vs shuffled), since MN9_R is flagged "RT Hard to trace"
from scipy.stats import fisher_exact
def mn9_active(name, nid):
    _, d, n = rates(name); s = d[d.neuron_id == nid].set_index('trial').n_spikes.reindex(range(n), fill_value=0)
    return int((s > 0).sum()), n, round(float(s.mean()), 2)
L = S['malecns']['mn9']['L']
a5 = {c: mn9_active(c, L) for c in ['E3_mcns_typesetL_real', 'E4_mcns_typesetL_shuffled', 'S2_mcns_typesetR_real', 'S1_mcns_sugaronlyL_real', 'X4_mcns_typesetL_wscaled']}
r, s = a5['E3_mcns_typesetL_real'], a5['E4_mcns_typesetL_shuffled']
out['A5_male_MN9L_readout'] = {k: {'active': v[0], 'n': v[1], 'rate_hz': v[2]} for k, v in a5.items()}
out['A5_male_MN9L_readout']['fisher_p_real_vs_shuffled'] = float(fisher_exact([[r[0], r[1] - r[0]], [s[0], s[1] - s[0]]])[1])
json.dump(out, open(R / 'exploratory.json', 'w'), indent=1, default=str)
