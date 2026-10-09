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
json.dump(out, open(R / 'exploratory.json', 'w'), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
