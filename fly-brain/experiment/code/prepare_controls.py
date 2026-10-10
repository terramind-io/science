"""Specificity-control stimulus draws (PLAN2 amendment 2): class-matched random gustatory neurons,
head (brain-entering) gustatory neurons only, same side and same count as the sugar-set stimulus, excluding the stimulus types (LB3b/LB3c/LB3d/LB4b). 10 fixed draws."""
import json
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]
S = json.load(open(ROOT / 'inputs/stimuli.json'))
EXCL = {'LB3b', 'LB3c', 'LB3d', 'LB4b'}
rng = np.random.default_rng(20261009)
fw = pd.read_csv(ROOT / 'data/flywire/neuron_annotations.tsv', sep='\t', usecols=['root_id', 'cell_class', 'cell_type', 'side'], low_memory=False)
comp783 = set(pd.read_csv(ROOT / 'vendor/Drosophila_brain_model/Completeness_783.csv', index_col=0).index)
fpool = fw[(fw.cell_class == 'gustatory') & (fw.side == S['flywire783']['grn_side']) & (~fw.cell_type.isin(EXCL)) & fw.root_id.isin(comp783)].root_id.astype('int64').tolist()
ann = pd.read_feather(ROOT / 'data/malecns/body-annotations-male-cns-v1.0-minconf-0.5.feather')
mcomp = set(pd.read_csv(ROOT / 'inputs/malecns_completeness.csv', index_col=0).index)
mpool = ann[(ann.superclass == 'cb_sensory') & (ann['class'] == 'gustatory') & (ann.rootSide == 'L') & (~ann.type.isin(EXCL)) & ann.bodyId.isin(mcomp)].bodyId.astype('int64').tolist()
nf, nm = len(S['flywire783']['stim_typeset']), len(S['malecns']['stim_typeset_L'])
out = {'female_pool_n': len(fpool), 'male_pool_n': len(mpool), 'n_female': nf, 'n_male': nm,
       'female_draws': [sorted(int(x) for x in rng.choice(fpool, nf, replace=False)) for _ in range(10)],
       'male_draws': [sorted(int(x) for x in rng.choice(mpool, nm, replace=False)) for _ in range(10)]}
json.dump(out, open(ROOT / 'inputs/controls.json', 'w'), indent=1)
print({k: v for k, v in out.items() if not k.endswith('draws')})
