"""Build model inputs (completeness + signed connectivity) and stimulus/readout ID lists.

Outputs, all in ../inputs:
  flywire630_*  : Shiu et al. 2024's own files (copied paths only; not modified)
  flywire783_*  : Shiu repo's v783 files (used as-is)
  malecns_completeness.csv / malecns_connectivity.parquet : male CNS v1.0 in Shiu's format
  stimuli.json  : neuron ID lists per condition, built from annotation tables only
"""
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
V = ROOT / 'vendor' / 'Drosophila_brain_model'
D = ROOT / 'data'
OUT = ROOT / 'inputs'

# ---- Shiu et al. 2024 exact stimulus (example.ipynb / figures.ipynb) ----
SHIU_SUGAR = [720575940624963786, 720575940630233916, 720575940637568838, 720575940638202345, 720575940617000768,
              720575940630797113, 720575940632889389, 720575940621754367, 720575940621502051, 720575940640649691,
              720575940639332736, 720575940616885538, 720575940639198653, 720575940620900446, 720575940617937543,
              720575940632425919, 720575940633143833, 720575940612670570, 720575940628853239, 720575940629176663,
              720575940611875570]
SHIU_MN9 = 720575940660219265  # contralateral MN9 for sugarR in the paper's notebooks

TYPES_SHIU_SET = ['LB3b', 'LB3c', 'LB3d', 'LB4b']   # type composition of Shiu's 21 GRNs (FlyWire v783 annotations)
TYPES_SUGAR_ONLY = ['LB3b', 'LB3c']                  # annotated sugar / sugar-low_salt classes


def flywire783():
    fw = pd.read_csv(D / 'flywire' / 'neuron_annotations.tsv', sep='\t', low_memory=False)
    comp = pd.read_csv(V / 'Completeness_783.csv', index_col=0)
    fw = fw[fw.root_id.isin(comp.index)]
    shiu = fw[fw.root_id.isin(SHIU_SUGAR)]
    side = shiu.side.mode()[0]                                   # FlyWire 'side' of Shiu's GRNs
    other = {'left': 'right', 'right': 'left'}[side]
    mn9 = fw[fw.cell_type == 'CB0701']                           # MN9 == FlyWire CB0701 (male CNS flywireType)
    def grn(types, s):
        return fw[(fw.cell_type.isin(types)) & (fw.side == s)].root_id.astype('int64').tolist()
    return {
        'shiu_composition': shiu.cell_type.value_counts().to_dict(),
        'shiu_subclass': shiu.cell_sub_class.value_counts().to_dict(),
        'grn_side': side,
        'mn9_contra': int(mn9[mn9.side == other].root_id.iloc[0]),
        'mn9_ipsi': int(mn9[mn9.side == side].root_id.iloc[0]),
        'stim_typeset': grn(TYPES_SHIU_SET, side),
        'stim_sugaronly': grn(TYPES_SUGAR_ONLY, side),
    }


def malecns():
    a = pd.read_feather(D / 'malecns' / 'body-annotations-male-cns-v1.0-minconf-0.5.feather')
    nt = pd.read_feather(D / 'malecns' / 'body-neurotransmitters-male-cns-v1.0.feather')
    keep = a[a.status == 'Traced'].copy()
    keep = keep.merge(nt[['body', 'predicted_nt']], left_on='bodyId', right_on='body', how='left')
    # Shiu rule: GABA or glutamate -> inhibitory; everything else (incl. unknown) -> excitatory
    keep['sign'] = keep.predicted_nt.isin(['gaba', 'glutamate']).map({True: -1, False: 1})
    keep = keep.sort_values('bodyId').reset_index(drop=True)
    ids = keep.bodyId.astype('int64')
    idx = pd.Series(range(len(ids)), index=ids.values)
    sign = pd.Series(keep.sign.values, index=ids.values)

    w = pd.read_feather(D / 'malecns' / 'connectome-weights-male-cns-v1.0-minconf-0.5.feather')
    w = w[w.body_pre.isin(idx.index) & w.body_post.isin(idx.index) & (w.body_pre != w.body_post) & (w.weight > 0)]
    con = pd.DataFrame({
        'Presynaptic_ID': w.body_pre.values, 'Postsynaptic_ID': w.body_post.values,
        'Presynaptic_Index': idx.loc[w.body_pre.values].values, 'Postsynaptic_Index': idx.loc[w.body_post.values].values,
        'Connectivity': w.weight.values, 'Excitatory': sign.loc[w.body_pre.values].values,
    })
    con['Excitatory x Connectivity'] = con.Connectivity * con.Excitatory
    con.to_parquet(OUT / 'malecns_connectivity.parquet')
    pd.DataFrame({'Completed': True}, index=ids.rename('bodyId')).to_csv(OUT / 'malecns_completeness.csv')

    def grn(types, s):
        return keep[keep.type.isin(types) & (keep.rootSide == s)].bodyId.astype('int64').tolist()
    mn9 = keep[keep.type == 'MN9'].set_index('somaSide').bodyId
    keep[['bodyId', 'type', 'flywireType', 'instance', 'superclass', 'predicted_nt', 'sign']].to_csv(OUT / 'malecns_neurons.csv', index=False)
    return {
        'n_neurons': int(len(keep)), 'n_edges': int(len(con)),
        'frac_inhibitory_edges': float((con.Excitatory < 0).mean()),
        'mn9': {k: int(v) for k, v in mn9.items()},
        'stim_typeset_L': grn(TYPES_SHIU_SET, 'L'), 'stim_typeset_R': grn(TYPES_SHIU_SET, 'R'),
        'stim_sugaronly_L': grn(TYPES_SUGAR_ONLY, 'L'),
    }


if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    out = {'flywire630': {'stim_shiu': SHIU_SUGAR, 'mn9_contra': SHIU_MN9},
           'flywire783': flywire783(), 'malecns': malecns()}
    json.dump(out, open(OUT / 'stimuli.json', 'w'), indent=1)
    summ = {k: {kk: (len(vv) if isinstance(vv, list) else vv) for kk, vv in v.items()} for k, v in out.items()}
    print(json.dumps(summ, indent=1))
