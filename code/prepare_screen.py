"""Build inputs/sez_screen.json: SEZ cell types (Shiu et al. ST3) with female v630 IDs, male CNS IDs, observed outcome."""
import json, pickle
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sez = pickle.load(open(ROOT / 'vendor/Drosophila_brain_model/sez_neurons.pickle', 'rb'))
st3 = pd.read_excel(ROOT / '../sources/papers/S2_supplementary/S2_Shiu2024_MOESM2_ESM.xlsx', 'Sup Table 3 Predicted MN9 vs. o', header=0)
st3 = st3.rename(columns={st3.columns[0]: 'type'}).dropna(subset=['type'])
st3['key'] = st3.type.str.lower().str.strip()
fw = pd.read_csv(ROOT / 'data/flywire/neuron_annotations.tsv', sep='\t', usecols=['root_id', 'cell_type'], low_memory=False).set_index('root_id').cell_type
mc = pd.read_csv(ROOT / 'inputs/malecns_neurons.csv')
mc_types = mc.dropna(subset=['flywireType'])
comp630 = set(pd.read_csv(ROOT / 'vendor/Drosophila_brain_model/2023_03_23_completeness_630_final.csv', index_col=0).index)
out, unmatched = {}, []
for name, ids in sez.items():
    row = st3[st3.key == name.lower().strip()]
    if row.empty: unmatched.append(name); continue
    r = row.iloc[0]
    fwtypes = sorted(set(fw.reindex(ids).dropna()))
    male = mc_types[mc_types.flywireType.isin(fwtypes)].bodyId.astype(int).tolist()
    out[name] = {'female_ids': [int(i) for i in ids if i in comp630], 'flywire_types': fwtypes, 'male_ids': male,
                 'observed_rate': float(r['MN9 Optogenetic Activation Rate']),
                 'st3_50hz_left': float(r['50 Hz MN9_Left']), 'st3_50hz_right': float(r['50 Hz MN9_Right'])}
json.dump(out, open(ROOT / 'inputs/sez_screen.json', 'w'), indent=1)
print('types', len(out), 'unmatched to ST3', unmatched, '| male-mappable', sum(1 for v in out.values() if v['male_ids']),
      '| observed positive', sum(v['observed_rate'] > 0 for v in out.values()),
      '| observed positive & male-mappable', sum(v['observed_rate'] > 0 and bool(v['male_ids']) for v in out.values()))
